"""Write the brainstorm brief as markdown. Every idea carries its evidence; anything missing is marked [MISSING]."""
from .funnel import STAGES, STAGE_NAMES


def _num(v):
    return "[MISSING]" if v is None else f"{v:,.0f}"


def _kwline(d):
    parts = [f"volume {_num(d.get('volume'))}"]
    parts.append(f"difficulty {_num(d.get('difficulty'))}" if d.get("difficulty") is not None else "difficulty [MISSING]")
    if d.get("cpc") is not None:
        parts.append(f"cost per click ${d['cpc']:.2f} (Semrush)")
    elif d.get("bid_high") is not None:
        parts.append(f"top-of-page bid ${d['bid_high']:.2f} (Google Ads)")
    parts.append(f"trend {d.get('trend', 'unknown')}")
    return ", ".join(parts) + f" ({', '.join(d.get('sources', [])) or 'no source'})"


def idea_lines(x):
    stage_note = x["stage"] + (" (default rule)" if str(x["matched"]).startswith("(default") else " (matched a rule)")
    head = f"- **{x['text']}**, score {x['score']}, theme: {x['theme'] or 'none yet'}, suggested format: {x['format']}"
    if x["kind"] == "keyword":
        ev = f"  - Keyword data: {_kwline(x['data'])}; stage rule: {stage_note}"
    elif x["kind"] == "question":
        it = x["item"]
        ev = f"  - Evidence: {it['source']} post, engagement {it['engagement']:,.0f}, {it['date'] or 'undated'}, {it['url'] or '[MISSING link]'}; stage rule: {stage_note}"
    else:
        it = x["item"]
        ev = f"  - Evidence: {it['source']} headline, {it['date'] or 'undated'}, {it['url'] or '[MISSING link]'}; stage rule: {stage_note}"
    return [head, ev]


def build(brand, as_of, counts, themetable, by_stage, emerging, comp_new, comp_themes, refresh, inventory_stage, ebooks, gaps):
    L = [f"# Content topic brief: {brand['brand']}", "",
         f"Prepared as of {as_of}. Audiences: {', '.join(brand['audiences'])}.",
         "This is a starting point for a brainstorm, not a decision. Every idea below has its evidence next to it. Scores compare ideas within this run only.", "",
         "## Data used", ""]
    for k, v in counts.items():
        L.append(f"- {k}: {v if v else '[MISSING] none provided'}")
    L += ["", "## Themes ranked", "",
          "| Theme | Score | Demand (monthly searches) | Trend | Sources | Competitors posted | You posted | Note |", "|---|---|---|---|---|---|---|---|"]
    for t in themetable:
        note = []
        if t["weak"]:
            note.append("weak signal: one source type and no keyword data")
        if t["missing_keywords"]:
            note.append("keyword data [MISSING]")
        if t["raw"]["gap"] >= 1:
            note.append("competitors cover it, you do not")
        L.append(f"| {t['theme']} | {t['score']} | {_num(t['raw']['demand']) if not t['missing_keywords'] else '[MISSING]'} | {t['raw']['trend']} | "
                 f"{', '.join(t['raw']['source_types']) or 'none'} | {len(t['competitor'])} | {len(t['own'])} | {'; '.join(note)} |")
    for s in STAGES:
        L += ["", f"## {STAGE_NAMES[s]} ({s})", ""]
        ideas = by_stage.get(s, [])
        if not ideas:
            L.append("[MISSING] no ideas found for this stage. Add sources or keyword exports that cover it.")
        for x in ideas:
            L += idea_lines(x)
        L.append("")
        L.append(f"You currently have {inventory_stage.get(s, 0)} published piece(s) tagged {s} in your content inventory.")
    L += ["", "## Ebook or pillar candidates", ""]
    L += [f"- **{e['theme']}**: {e['ideas']} ideas across {e['stages']} funnel stage(s), theme score {e['score']}" for e in ebooks] or ["- None yet: no theme has enough ideas across stages."]
    L += ["", "## Where your content can improve (SEO)", ""]
    for g in gaps:
        L.append(f"- {g}")
    if refresh:
        L += ["", "Pages that rank on page two for a keyword (positions 11 to 20), worth refreshing:", ""]
        for r in refresh:
            L.append(f"- {r['keyword']}: position {_num(r['position'])}, volume {_num(r['volume'])}, {r['url']}")
    L += ["", "## Competitor activity", ""]
    if not comp_new:
        L.append("[MISSING] no competitor feeds or sitemaps provided.")
    for name, info in comp_new.items():
        tag = "baseline (first run, nothing to compare with)" if info["baseline"] else f"{len(info['new'])} new since last run"
        L.append(f"- **{name}**: {tag}")
        for it in info["new"][:5]:
            L.append(f"  - {it['title']}, {it['date'] or 'undated'}, {it['url']}")
        top = comp_themes.get(name)
        if top:
            L.append("  - Themes they push: " + ", ".join(f"{n} ({c})" for n, c in top.most_common(3)))
    L += ["", "## Possible new themes (phrases in several headlines that match no theme)", ""]
    L += [f"- {p} ({c} headlines)" for p, c in emerging] or ["- None found."]
    L += ["", "## What to do next", "",
          "1. Pick 2 or 3 themes and read the evidence behind each one.",
          "2. For each, choose one idea per funnel stage and write it in your brand voice.",
          "3. Check any claim or number against your own approved sources before you publish.", ""]
    return "\n".join(L)
