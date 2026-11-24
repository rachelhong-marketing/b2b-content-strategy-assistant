"""Group everything under the brand's themes, score each theme, then turn the evidence into topic ideas by funnel stage."""
import re
from collections import Counter

from .funnel import STAGES, FORMATS, classify
from .util import STOP, days_between, has_phrase, minmax, words

QUESTION_RX = re.compile(r"^(how|why|what|when|should|can|is|are|do|does|which|where)\b", re.I)
WEIGHTS = dict(mentions=0.20, engagement=0.10, demand=0.20, ease=0.10, trend=0.10, questions=0.10, fit=0.10, gap=0.10)
RECENT_DAYS = 90


OFF_CAMPAIGN = 0.6  # ideas outside the campaign themes count for 60 percent when a campaign is set


def is_question(title):
    t = (title or "").strip()
    return t.endswith("?") or bool(QUESTION_RX.match(t))


def themes_for(text, themes):
    return [n for n, t in themes.items() if any(has_phrase(text, tr) for tr in t["triggers"])]


def recent(items, as_of):
    """Keep items from the last 90 days. Items with no date are kept and counted as undated."""
    out = []
    for it in items:
        age = days_between(as_of, it["date"]) if it.get("date") else None
        if age is None or 0 <= age <= RECENT_DAYS:
            out.append(it)
    return out


def theme_table(items, keywords, brand, as_of, inventory):
    themes = brand["themes"]
    items = recent(items, as_of)
    rows = {n: dict(theme=n, trade=[], community=[], competitor=[], own=[], keywords=[], fit=t["fit"]) for n, t in themes.items()}
    for it in items:
        for n in themes_for(it["title"] + " " + it.get("text", ""), themes):
            rows[n][it["source_type"]].append(it)
    for inv in inventory:
        for n in themes_for(inv.get("title", ""), themes):
            rows[n]["own"].append(inv)
    for k in keywords.values():
        for n in themes_for(k["keyword"], themes):
            rows[n]["keywords"].append(k)
    raw = {}
    for n, r in rows.items():
        external = r["trade"] + r["community"]
        kws = r["keywords"]
        demand = sum(k["volume"] or 0 for k in kws)
        wk = [(k["volume"], k["difficulty"]) for k in kws if k["volume"] and k["difficulty"] is not None]
        kd = (sum(v * d for v, d in wk) / sum(v for v, _ in wk)) if wk else None
        up = sum(k["volume"] or 0 for k in kws if k["trend"] == "up")
        down = sum(k["volume"] or 0 for k in kws if k["trend"] == "down")
        trend = "up" if up > down else "down" if down > up else ("flat" if any(k["trend"] == "flat" for k in kws) else "unknown")
        qs = sum(1 for it in external if is_question(it["title"]))
        raw[n] = dict(mentions=len(external) + 0.5 * len(r["competitor"]), engagement=sum(it["engagement"] for it in r["community"]),
                      demand=demand, kd=kd, trend=trend, qshare=(qs / len(external)) if external else 0.0,
                      gap=1.0 if (len(r["competitor"]) >= 2 and not r["own"]) else 0.5 if (r["competitor"] and not r["own"]) else 0.0,
                      source_types=sorted({it["source"] for it in external}), questions=qs)
    nm, ne, nd = (minmax({n: raw[n][k] for n in raw}) for k in ("mentions", "engagement", "demand"))
    kds = minmax({n: raw[n]["kd"] for n in raw})
    out = []
    for n, r in rows.items():
        x = raw[n]
        trend_pts = {"up": 1.0, "flat": 0.5, "unknown": 0.3, "down": 0.0}[x["trend"]]
        ease = 0.5 if x["kd"] is None else 1 - kds[n]
        comp = dict(mentions=nm[n], engagement=ne[n], demand=nd[n], ease=ease, trend=trend_pts, questions=x["qshare"], fit=r["fit"], gap=x["gap"])
        score = round(100 * sum(WEIGHTS[k] * comp[k] for k in WEIGHTS), 1)
        evidence = sorted(r["community"] + r["trade"], key=lambda it: (-it["engagement"], it["date"] or ""), reverse=False)[:3]
        weak = len(x["source_types"]) < 2 and not r["keywords"]
        out.append(dict(theme=n, score=score, components={k: round(v, 2) for k, v in comp.items()}, raw=x, trade=r["trade"], community=r["community"],
                        competitor=r["competitor"], own=r["own"], keywords=r["keywords"], evidence=evidence, weak=weak,
                        missing_keywords=not r["keywords"]))
    out.sort(key=lambda t: -t["score"])
    return out


def emerging_phrases(items, themes, min_items=3, top=6):
    """Two-word phrases that show up in several headlines but belong to no theme yet: candidates for new themes."""
    df = Counter()
    for it in items:
        if themes_for(it["title"], themes):
            continue
        ws = [w for w in words(it["title"]) if w not in STOP and len(w) > 2]
        pairs = {" ".join(p) for p in zip(ws, ws[1:])}
        df.update(pairs)
    return [(p, c) for p, c in df.most_common(top * 3) if c >= min_items][:top]


def ideas_by_stage(themetable, items, keywords, brand, rules, as_of, top=8, hide=()):
    """Topic ideas from three kinds of evidence: keywords people search, questions people ask, headlines in the news.
    Each idea is placed in a funnel stage and scored: half from its theme's score, half from its own signal."""
    themes = brand["themes"]
    campaign_themes = set((brand.get("campaign") or {}).get("themes", []))
    score_of = {t["theme"]: t["score"] for t in themetable}
    vols = minmax({k: v["volume"] for k, v in keywords.items()})
    kds = minmax({k: v["difficulty"] for k, v in keywords.items()})
    recent_items = recent(items, as_of)
    comm = [it for it in recent_items if it["source_type"] == "community"]
    engs = minmax({i: it["engagement"] for i, it in enumerate(comm)})
    ideas, seen = [], set()

    def add(kind, text, signal, **extra):
        key = text.lower().strip()
        if key in seen:
            return
        seen.add(key)
        hidden = key in hide
        found = themes_for(text, themes)
        theme = max(found, key=lambda n: score_of.get(n, 0)) if found else ""
        stage, why = classify(text, rules)
        score = 0.5 * score_of.get(theme, 0.0) + 0.5 * 100 * signal
        on_campaign = not campaign_themes or theme in campaign_themes
        if not on_campaign:
            score *= OFF_CAMPAIGN
        ideas.append(dict(kind=kind, text=text, stage=stage, matched=why, theme=theme, hidden=hidden, on_campaign=on_campaign,
                          score=round(score, 1), format=FORMATS[stage], **extra))

    for k, v in keywords.items():
        if v["volume"] is None:
            continue
        ease = 0.5 if v["difficulty"] is None else 1 - kds[k]
        add("keyword", k, 0.6 * vols[k] + 0.4 * ease, data=v)
    for i, it in enumerate(comm):
        add("question", it["title"], 0.7 * engs[i] + 0.3 * (1.0 if is_question(it["title"]) else 0.0), item=it)
    for it in recent_items:
        if it["source_type"] == "trade":
            age = days_between(as_of, it["date"]) if it.get("date") else None
            fresh = 0.3 if age is None else max(0.0, 1 - age / RECENT_DAYS)
            add("headline", it["title"], 0.5 * fresh, item=it)
    by_stage = {s: sorted([x for x in ideas if x["stage"] == s and x["score"] >= 5 and not x["hidden"]], key=lambda x: -x["score"])[:top] for s in STAGES}
    return by_stage, ideas
