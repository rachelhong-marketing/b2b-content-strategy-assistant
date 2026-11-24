"""Group everything under the brand's themes, score each theme, then turn the evidence into topic ideas by funnel stage."""
import re
from collections import Counter

from . import performance as perfmod, scoring
from .funnel import STAGES, FORMATS, classify
from .util import STOP, days_between, has_phrase, minmax, words

QUESTION_RX = re.compile(r"^(how|why|what|when|should|can|is|are|do|does|which|where)\b", re.I)
GENERIC = {"data", "customer", "customers", "one", "see", "many", "how", "new"}
RECENT_DAYS = 90



def is_question(title):
    t = (title or "").strip()
    return t.endswith("?") or bool(QUESTION_RX.match(t))


def _stems(text):
    return {w[:-1] if w.endswith("s") and len(w) > 3 else w for w in words(text) if w not in STOP and w not in GENERIC and len(w) > 2}


def campaign_relevance(theme, text, brand):
    """0..1. Without a campaign: the theme's brand fit. With one: 0.6 for an on-campaign theme, plus up to 0.4 for words in common
    with the campaign theme or a pillar. An idea outside the campaign themes keeps at most 15 percent of its brand fit."""
    fit = brand["themes"].get(theme, {}).get("fit", 0.0) if theme else 0.0
    c = brand.get("campaign")
    if not c:
        return fit
    if theme not in c.get("themes", []):
        return round(scoring.OFF_CAMPAIGN_FIT * fit, 2)
    mine = _stems(text)
    best = max((len(mine & _stems(t)) for t in [c.get("theme", "")] + list(c.get("pillars", []))), default=0)
    return round(0.6 + 0.4 * (1.0 if best >= 2 else 0.5 if best == 1 else 0.0), 2)


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


def theme_table(items, keywords, brand, as_of, inventory, perf=None):
    themes = brand["themes"]
    campaign_themes = (brand.get("campaign") or {}).get("themes")
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
        has_kw = bool(r["keywords"])
        camp = r["fit"] if campaign_themes is None else (1.0 if n in campaign_themes else round(scoring.OFF_CAMPAIGN_FIT * r["fit"], 2))
        pinfo = perfmod.for_idea(perf, n, None, themes_for, themes)
        parts = dict(campaign=camp, performance=pinfo["value"] if pinfo else None, demand=nd[n] if has_kw else None,
                     ease=(0.5 if x["kd"] is None else 1 - kds[n]) if has_kw else None,
                     audience=0.4 * nm[n] + 0.3 * ne[n] + 0.3 * x["qshare"], trend=trend_pts, gap=x["gap"])
        score, left_out = scoring.combine(parts)
        evidence = sorted(r["community"] + r["trade"], key=lambda it: (-it["engagement"], it["date"] or ""), reverse=False)[:3]
        weak = len(x["source_types"]) < 2 and not r["keywords"]
        out.append(dict(theme=n, score=score, components={k: (round(v, 2) if v is not None else None) for k, v in parts.items()}, left_out=left_out,
                        perf=pinfo, on_campaign=campaign_themes is None or n in campaign_themes, raw=x, trade=r["trade"], community=r["community"],
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


def ideas_by_stage(themetable, items, keywords, brand, rules, as_of, top=8, hide=(), perf=None):
    """Topic ideas from three kinds of evidence: keywords people search, questions people ask, headlines in the news.
    Each idea is placed in a funnel stage and scored with the same seven factors as the themes (see scoring.py).
    Factors that belong to the idea itself (its own search volume, its own engagement) are used where they exist;
    otherwise the factor comes from the idea's theme."""
    themes = brand["themes"]
    campaign_themes = set((brand.get("campaign") or {}).get("themes", []))
    tt = {t["theme"]: t for t in themetable}
    score_of = {n: t["score"] for n, t in tt.items()}
    vols = minmax({k: v["volume"] for k, v in keywords.items()})
    kds = minmax({k: v["difficulty"] for k, v in keywords.items()})
    recent_items = recent(items, as_of)
    comm = [it for it in recent_items if it["source_type"] == "community"]
    engs = minmax({i: it["engagement"] for i, it in enumerate(comm)})
    ideas, seen = [], set()

    def fresh_of(it):
        age = days_between(as_of, it["date"]) if it.get("date") else None
        return 0.3 if age is None else max(0.0, 1 - age / RECENT_DAYS)

    def add(kind, text, own, **extra):
        key = text.lower().strip()
        if key in seen:
            return
        seen.add(key)
        hidden = key in hide
        found = themes_for(text, themes)
        theme = max(found, key=lambda n: score_of.get(n, 0)) if found else ""
        stage, why = classify(text, rules)
        tc = tt.get(theme, {}).get("components", {})
        theme_trend = tc.get("trend")
        parts = dict(campaign=campaign_relevance(theme, text, brand), performance=None,
                     demand=own.get("demand", tc.get("demand")), ease=own.get("ease", tc.get("ease")),
                     audience=own.get("audience", tc.get("audience")),
                     trend=own["trend"](theme_trend) if "trend" in own else theme_trend, gap=tc.get("gap", 0.0) if theme else 0.0)
        info = perfmod.for_idea(perf, theme, stage, themes_for, themes)
        parts["performance"] = info["value"] if info else None
        score, left_out = scoring.combine(parts)
        on_campaign = not campaign_themes or theme in campaign_themes
        ideas.append(dict(kind=kind, text=text, stage=stage, matched=why, theme=theme, hidden=hidden, on_campaign=on_campaign,
                          score=score, parts=parts, left_out=left_out, perf=info, format=FORMATS[stage], **extra))

    for k, v in keywords.items():
        if v["volume"] is None:
            continue
        add("keyword", k, dict(demand=vols[k], ease=0.5 if v["difficulty"] is None else 1 - kds[k]), data=v)
    for i, it in enumerate(comm):
        fr = fresh_of(it)
        add("question", it["title"], dict(audience=0.7 * engs[i] + 0.3 * (1.0 if is_question(it["title"]) else 0.0),
                                          trend=lambda tt_, fr=fr: 0.5 * fr + 0.5 * (tt_ if tt_ is not None else 0.3)), item=it)
    for it in recent_items:
        if it["source_type"] == "trade":
            fr = fresh_of(it)
            add("headline", it["title"], dict(trend=lambda tt_, fr=fr: 0.5 * fr + 0.5 * (tt_ if tt_ is not None else 0.3)), item=it)
    by_stage = {s: sorted([x for x in ideas if x["stage"] == s and x["score"] >= 5 and not x["hidden"]], key=lambda x: -x["score"])[:top] for s in STAGES}
    return by_stage, ideas
