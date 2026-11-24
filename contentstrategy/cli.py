"""Command line: mine, check, classify, collect."""
import argparse
import json
import sys
from pathlib import Path

from . import brand as brandmod, check as checkmod, collect, competitors, funnel, keywords, performance, report, sources, topics
from .util import read_csv_rows


def _load_items(data):
    items, counts = [], {}
    d = data / "trade"
    for f in sorted(d.glob("*.xml")) if d.exists() else []:
        items += sources.parse_feed(f.read_text(encoding="utf-8"), f.stem, "trade")
    counts["Trade publication items"] = sum(1 for i in items if i["source_type"] == "trade")
    d = data / "community"
    n0 = len(items)
    for f in sorted(d.glob("*.csv")) if d.exists() else []:
        items += sources.read_community_csv(f, f.stem)
    counts["Community posts (exported or pasted)"] = len(items) - n0
    d = data / "competitors"
    n0 = len(items)
    for f in sorted(d.glob("*.xml")) if d.exists() else []:
        text = f.read_text(encoding="utf-8")
        name = f.stem.replace("-feed", "").replace("-sitemap", "")
        items += sources.parse_sitemap(text, name) if "<urlset" in text[:500] else sources.parse_feed(text, name, "competitor")
    counts["Competitor pages and posts"] = len(items) - n0
    return items, counts


def _load_keywords(data):
    d = data / "keywords"
    ga, sr, tr = {}, {}, {}
    for f in sorted(d.glob("*.csv")) if d.exists() else []:
        n = f.name.lower()
        if "trend" in n:
            tr.update(keywords.read_trends(f))
        elif "semrush" in n:
            sr.update(keywords.read_semrush(f))
        elif "google" in n or "planner" in n:
            ga.update(keywords.read_google_ads(f))
    merged = keywords.merge(ga, sr, tr)
    return merged, {"Google Ads Keyword Planner keywords": len(ga), "Semrush keywords": len(sr), "Google Trends terms": len(tr)}


def load_chosen(data):
    p = Path(data) / "state" / "chosen-topics.csv"
    return {r["text"].strip().lower() for r in read_csv_rows(p) if r.get("text")} if p.exists() else set()


def analyze(data, as_of=None, top=8):
    """Everything the brief and the other commands need, as one dict."""
    data = Path(data)
    b = brandmod.load(data / "brand" / "brand-profile.json")
    items, counts = _load_items(data)
    kws, kcounts = _load_keywords(data)
    counts.update(kcounts)
    inv_path = data / "content" / "content-inventory.csv"
    inventory = read_csv_rows(inv_path) if inv_path.exists() else []
    perf = performance.load(data)
    if not inventory and perf:
        inventory = [dict(url=x["url"], title=x["title"], stage=x["stage"], publish_date=x["date"]) for x in perf]
    counts["Your published content (inventory)"] = len(inventory)
    dates = [i["date"] for i in items if i["date"]]
    as_of = as_of or (max(dates) if dates else "")
    rules = funnel.load_rules()
    counts["Past performance of your published pieces (analytics export)"] = len(perf)
    table = topics.theme_table(items, kws, b, as_of, inventory, perf)
    chosen = load_chosen(data)
    by_stage, ideas = topics.ideas_by_stage(table, items, kws, b, rules, as_of, top, hide=chosen, perf=perf)
    counts["Ideas hidden because you already chose them"] = sum(1 for x in ideas if x["text"].lower().strip() in chosen) or "0 (none chosen yet)"
    ebooks = []
    for t in table:
        mine_ = [x for x in ideas if x["theme"] == t["theme"]]
        stages = {x["stage"] for x in mine_}
        if len(mine_) >= 5 and len(stages) >= 2 and t["score"] >= 40:
            ebooks.append(dict(theme=t["theme"], ideas=len(mine_), stages=len(stages), score=t["score"]))
    inv_stage = {s: sum(1 for r in inventory if (r.get("stage") or "").upper() == s) for s in funnel.STAGES}
    gaps = []
    for s in funnel.STAGES:
        if inventory and inv_stage[s] == 0:
            gaps.append(f"You have no published {s} content in the inventory.")
    thin = [t["theme"] for t in table if not t["own"] and t["raw"]["demand"] > 0]
    if thin:
        gaps.append("Themes with search demand and no page from you yet: " + ", ".join(thin))
    if not perf:
        gaps.append("[MISSING] no content performance export, so past performance was left out of every score and the other factors were scaled up.")
    if not any(not t["missing_keywords"] for t in table):
        gaps.append("[MISSING] no keyword exports were provided, so demand and difficulty could not be used.")
    domain = b["domain"].lower()
    refresh = sorted([k for k in kws.values() if k["position"] and 11 <= k["position"] <= 20 and domain in (k["url"] or "").lower()],
                     key=lambda k: -(k["volume"] or 0))
    snap = competitors.load_snapshot(data / "competitors" / "snapshot.json")
    comp_new = competitors.new_since(items, snap)
    text = report.build(b, as_of, counts, table, by_stage, topics.emerging_phrases(items, b["themes"]), comp_new,
                        competitors.theme_counts(items, b["themes"]), refresh, inv_stage, ebooks, gaps)
    return dict(text=text, items=items, ideas=ideas, brand=b, inventory=inventory, keywords=kws, as_of=as_of, table=table, by_stage=by_stage, performance=perf)


def mine(data, out, as_of=None, top=8):
    ctx = analyze(data, as_of, top)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(ctx["text"], encoding="utf-8")
    return ctx["text"], ctx["items"]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="contentstrategy", description="Turn audience questions, news, competitor activity and keyword data into ranked content topics by funnel stage.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mine", help="build the topic brief from a data folder")
    m.add_argument("--data", required=True)
    m.add_argument("--out", default="output/topic-brief.md")
    m.add_argument("--as-of")
    m.add_argument("--top", type=int, default=8)
    m.add_argument("--save-snapshot", action="store_true", help="remember today's competitor pages for the next run")
    c = sub.add_parser("check", help="check a finished brief")
    c.add_argument("brief")
    c.add_argument("--brand", required=True)
    w = sub.add_parser("weekly", help="the weekly run: collect, mine, compare with last week, remember")
    w.add_argument("--data", required=True)
    w.add_argument("--out-dir", default="output/weekly")
    w.add_argument("--collect-config")
    o = sub.add_parser("outline", help="turn one chosen idea into a writing brief")
    o.add_argument("--data", required=True)
    o.add_argument("--idea", required=True, help="the idea's text, or part of it")
    o.add_argument("--out-dir", default="output/drafts")
    o.add_argument("--as-of")
    k = sub.add_parser("aeo-check", help="check a draft for answer engine and AI search readiness")
    k.add_argument("draft")
    k.add_argument("--brand", required=True)
    k.add_argument("--as-of")
    s = sub.add_parser("schema", help="build JSON-LD structured data (Article and FAQPage) from a finished draft")
    s.add_argument("draft")
    s.add_argument("--brand", required=True)
    s.add_argument("--url")
    s.add_argument("--out")
    cs = sub.add_parser("citation-sheet", help="add buyer questions to the manual AI citation test log")
    cs.add_argument("--data", required=True)
    cs.add_argument("--max", type=int, default=10)
    cr = sub.add_parser("citation-report", help="summarize the AI citation test log")
    cr.add_argument("--data", required=True)
    f = sub.add_parser("classify", help="which funnel stage is this?")
    f.add_argument("text")
    g = sub.add_parser("collect", help="download feeds and sitemaps you list (obeys robots.txt)")
    g.add_argument("config")
    g.add_argument("--out", default="collected")
    a = ap.parse_args(argv)
    if a.cmd == "mine":
        text, items = mine(a.data, a.out, a.as_of, a.top)
        if a.save_snapshot:
            (Path(a.data) / "competitors" / "snapshot.json").write_text(json.dumps(competitors.snapshot_of(items), indent=1))
        print(f"Wrote {a.out} ({len(text.splitlines())} lines)")
    elif a.cmd == "weekly":
        from . import weekly
        res = weekly.run(a.data, a.out_dir, a.collect_config)
        print(Path(res["note"]).read_text())
        return 0 if res["ok"] else 1
    elif a.cmd == "outline":
        from . import outline as outlinemod
        ctx = analyze(a.data, a.as_of, top=50)
        idea = outlinemod.find_idea(ctx["ideas"], a.idea)
        text = outlinemod.build(idea, ctx["brand"], ctx["inventory"], ctx["as_of"])
        dest = Path(a.out_dir) / f"{outlinemod.slug(idea['text'])}-draft.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        print(f"Wrote {dest}")
    elif a.cmd == "aeo-check":
        from . import aeo
        res = aeo.check_draft(Path(a.draft).read_text(encoding="utf-8"), brandmod.load(a.brand), a.as_of)
        print(aeo.format_results(res))
        return 1 if any(l == "FAIL" for l, _ in res) else 0
    elif a.cmd == "schema":
        from . import schema as schemamod
        out = schemamod.dumps(schemamod.build(Path(a.draft).read_text(encoding="utf-8"), brandmod.load(a.brand), a.url))
        if a.out:
            Path(a.out).write_text(out, encoding="utf-8")
            print(f"Wrote {a.out}")
        else:
            print(out)
    elif a.cmd == "citation-sheet":
        from . import citations
        ctx = analyze(a.data, top=50)
        qs = [x["text"] for x in sorted(ctx["ideas"], key=lambda x: -x["score"]) if topics.is_question(x["text"]) and x["on_campaign"] and not x["hidden"]][: a.max]
        n = citations.add_sheet(a.data, qs)
        print(f"Added {n} test rows for {len(qs)} questions to {citations.log_path(a.data)}")
    elif a.cmd == "citation-report":
        from . import citations
        print("\n".join(citations.summary(a.data)))
    elif a.cmd == "check":
        probs = checkmod.check_brief(Path(a.brief).read_text(encoding="utf-8"), brandmod.load(a.brand))
        print("\n".join(probs) if probs else "Brief OK")
        return 1 if probs else 0
    elif a.cmd == "classify":
        stage, why = funnel.classify(a.text, funnel.load_rules())
        print(f"{stage}: {funnel.STAGE_NAMES[stage]} ({why})")
    else:
        for name, res in collect.run(a.config, a.out):
            print(f"{name}: {res}")
    return 0
