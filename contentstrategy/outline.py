"""Turn one chosen idea into a writing brief: question headline, answer-first structure, evidence, links, keywords.

It does not write the article. It gives the writer (you, or an AI assistant working in your voice) a structure that
answer engines and AI search tools can lift an answer from, and it leaves every unknown as [MISSING]."""
import re

from .util import has_phrase

QUESTIONS = {
    "TOFU": ["What should a B2B team know about {t}?", "Why does {t} become a problem?", "How do you spot {t} in your own data?", "What is the cost of {t}?"],
    "MOFU": ["What are the ways to handle {t}?", "How do you choose between them?", "What should you compare before you pick one?", "What does a good checklist for {t} include?"],
    "BOFU": ["What result can you expect from fixing {t}?", "What does it take to roll out?", "How long does it take and who needs to be involved?", "What proof should you ask any vendor for?"],
}


def slug(text, n=60):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s if len(s) <= n else s[:n].rsplit("-", 1)[0]


def find_idea(ideas, text):
    t = text.lower().strip()
    exact = [x for x in ideas if x["text"].lower().strip() == t]
    part = [x for x in ideas if t in x["text"].lower()]
    hit = exact or part
    if not hit:
        raise ValueError(f"no idea matches '{text}'")
    return max(hit, key=lambda x: x["score"])


def headline_as_question(text, theme, stage):
    t = text.strip().rstrip("?")
    t = t[0].upper() + t[1:]
    if re.match(r"(?i)^(what|why|how|when|who|which|should|can|does|do|is|are)\b", t):
        return t + "?"
    return f"{t}: what should a B2B team know?" if stage == "TOFU" else f"{t}: how do you decide?"


def related_pages(inventory, theme, brand):
    trig = brand["themes"].get(theme, {}).get("triggers", [])
    return [r for r in inventory if any(has_phrase((r.get("title") or ""), w) for w in trig)]


def build(idea, brand, inventory, as_of):
    stage, theme = idea["stage"], idea["theme"] or "[MISSING: no theme matched]"
    title = headline_as_question(idea["text"], theme, stage)
    camp = brand.get("campaign") or {}
    L = ["---", f"title: {title}", f"primary_question: {title}", f"funnel_stage: {stage}", f"theme: {theme}",
         f"campaign: {camp.get('name') or '[MISSING: no campaign set in the brand profile]'}",
         f"audience: {camp.get('audience') or ', '.join(brand['audiences'])}",
         "author: [MISSING: a real person's name and role]", "date: [MISSING: publish date, YYYY-MM-DD]", "updated: [MISSING: last updated, YYYY-MM-DD]",
         "original_angle: [MISSING: what do you know that other pages do not? A number, a customer example, or a decision rule]",
         "---", "", f"# {title}", "",
         "[MISSING: direct answer, 40 to 60 words. Answer the question in plain words before anything else. State the main fact, not a teaser.]", ""]
    for q in QUESTIONS[stage][:3]:
        L += [f"## {q.format(t=theme)}", "", "[MISSING: answer in 40 to 60 words first, then the detail, an example, or a table.]", ""]
    L += ["## Frequently asked questions", ""]
    for q in QUESTIONS[stage][3:] + ["Who should own this inside a B2B team?", "How often should you revisit it?"]:
        L += [f"### {q.format(t=theme)}", "", "[MISSING: answer in 80 words or fewer.]", ""]
    L += ["---", "", "## Writer's notes (delete before publishing)", "", f"Prepared as of {as_of}. Format suggested: {idea['format']}.", ""]
    if camp:
        L += ["**Campaign**", f"- Theme: {camp.get('theme', '[MISSING]')}", *[f"- Pillar: {p}" for p in camp["pillars"]], ""]
    L += ["**Evidence for this idea**"]
    if idea["kind"] == "keyword":
        d = idea["data"]
        L.append(f"- Keyword data for '{idea['text']}': volume {d['volume']}, difficulty {d['difficulty']}, source: your keyword export. Use the numbers as exported.")
    else:
        it = idea["item"]
        L.append(f"- {it['source']}: {it['title']} ({it['date'] or 'undated'}) {it['url'] or '[MISSING link]'}. Paraphrase, do not copy.")
    L += ["", "**Link to your own pages (internal links)**"]
    rel = related_pages(inventory, idea["theme"], brand) if idea["theme"] else []
    L += [f"- {r['title']} ({r.get('stage') or '?'}) {r['url']}" for r in rel[:5]] or ["- [MISSING] no published page on this theme yet. This piece would be the first."]
    L += ["", "**Answer-engine checklist** (run `aeo-check` when the draft is done)",
          "- Direct answer in the first paragraph, 40 to 60 words.",
          "- Question headings, each followed by a short answer, then detail.",
          "- At least 3 questions in the FAQ section, each answered in 80 words or fewer.",
          "- At least 2 outside sources linked, and one original element (your data, a customer example, a decision rule).",
          "- A list or table where it helps. A real author name and a visible date.",
          "- Spell out every acronym on first use. Use the brand and product names exactly the same way every time.",
          f"- Words to avoid: {', '.join(brand['avoid_words']) or 'none set'}.", ""]
    return "\n".join(L)
