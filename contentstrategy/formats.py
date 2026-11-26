"""Briefs and checks for three more formats: a customer case study, a long-form guide and a short social post.

Like the blog outline, none of these write the piece. Each gives the writer (you, or an AI assistant working in your
voice) a structure with every unknown left as [MISSING], and a check to run on the finished draft.

A case study is the strictest: it needs a real customer source file with an approver and a date, it never invents a
customer, quote or number, and its check fails any figure in the Results section that is not in that source file."""
import json
import re
from pathlib import Path

from .aeo import LINK, QWORD, parse, notes_stripped, sections, wc
from .outline import QUESTIONS, headline_as_question
from .util import has_phrase

LIMITS = {"linkedin": 3000, "x": 280, "facebook": 63206}
HOOK_MAX = 140
NUM = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")
STAGE_ORDER = {"TOFU": 0, "MOFU": 1, "BOFU": 2}


def _lint(body, brand, res):
    f = lambda m: res.append(("FAIL", m))
    if "[MISSING" in body:
        f("the draft still has [MISSING] placeholders")
    for word in brand.get("avoid_words", []):
        if has_phrase(body, word):
            f(f"brand voice: the word '{word}' is on your avoid list")
    known, seen = set(brand.get("known_acronyms", [])), set()
    for m in re.finditer(r"\b[A-Z]{2,6}\b", body):
        a = m.group(0)
        if a in known or a in seen:
            continue
        seen.add(a)
        before, after = body[max(0, m.start() - 1):m.start()], body[m.end():m.end() + 2]
        if not ((before == "(" and after.startswith(")")) or after == " ("):
            f(f"acronym '{a}' is not spelled out on first use")


def _fm_required(fm, keys, res):
    for k in keys:
        if not fm.get(k) or "[MISSING" in fm[k]:
            res.append(("FAIL", f"front matter '{k}' is empty or still [MISSING]"))


# ---------- case study ----------
SOURCE_KEYS = ("customer", "challenge", "what_they_did", "results", "approved_by", "approval_date", "customer_permission")


def load_case_source(path):
    src = json.loads(Path(path).read_text(encoding="utf-8"))
    miss = [k for k in SOURCE_KEYS if not src.get(k)]
    if miss:
        raise ValueError(f"case study source is missing: {', '.join(miss)}")
    if str(src["customer_permission"]).lower() not in ("yes", "true", "approved"):
        raise ValueError("customer_permission is not 'yes'; a case study needs the customer's written permission first")
    for r in src["results"]:
        if not r.get("claim") or not r.get("source"):
            raise ValueError("every result needs a claim and a source")
    return src


def build_case_study(src, brand, as_of):
    camp = brand.get("campaign") or {}
    L = ["---", "title: [MISSING: a headline that states the result, in the customer's words if possible]",
         f"customer: {src['customer']}", f"industry: {src.get('industry', '[MISSING]')}", f"company_size: {src.get('size', '[MISSING]')}",
         "funnel_stage: BOFU", f"campaign: {camp.get('name') or '[MISSING: no campaign set in the brand profile]'}",
         "author: [MISSING: a real person's name and role]", "date: [MISSING: publish date, YYYY-MM-DD]",
         f"approved_by: {src['approved_by']}", f"approval_date: {src['approval_date']}", "---", "",
         "# [MISSING: the headline again]", "",
         "[MISSING: a summary in 40 to 60 words: who the customer is, the problem, and the main result with its number.]", "",
         "## The challenge", "", "[MISSING: what was going wrong and what it cost, in the customer's terms.]", "",
         "## What they did", "", "[MISSING: the steps they took, in order, and how long each took.]", "",
         "## The results", "", "[MISSING: each result in one sentence with its number and time frame. Use only the figures in your source.]", "",
         "> [MISSING: the customer's quote, word for word]", ">", "> [MISSING: speaker name and title, as approved]", "",
         "## What to do next", "", "[MISSING: one next step for a reader in the same position, and a link to it.]", "",
         "---", "", "## Writer's notes (delete before publishing)", "", f"Prepared as of {as_of}.", "", "**Facts from your source file** (use these exactly, do not round or add)", "",
         f"- Customer: {src['customer']}" + (f", {src['industry']}" if src.get("industry") else "") + (f", {src['size']}" if src.get("size") else ""),
         f"- Challenge: {src['challenge']}"]
    steps = src["what_they_did"]
    L += [f"- Step: {s}" for s in (steps if isinstance(steps, list) else [steps])]
    L += [f"- Result: {r['claim']} (source: {r['source']}" + (f"; period: {r['period']}" if r.get("period") else "") + ")" for r in src["results"]]
    q = src.get("quote")
    L += [f"- Quote: \"{q['text']}\" by {q.get('speaker', '[MISSING]')}, {q.get('title', '')}" if q else "- Quote: [MISSING] none supplied. Ask the customer, do not write one.",
          f"- Approved by {src['approved_by']} on {src['approval_date']}; customer permission: {src['customer_permission']}", "",
          "**Do not**: invent a customer name, a quote or a number, round a figure up, or imply a result the source does not state.", ""]
    return "\n".join(L)


def check_case_study(text, brand, source_text=None):
    res = []
    fm, body = parse(text)
    body = notes_stripped(body)
    f = lambda m: res.append(("FAIL", m))
    w = lambda m: res.append(("WARN", m))
    _fm_required(fm, ("title", "customer", "author", "date", "approved_by", "approval_date"), res)
    secs = sections(body)
    heads = {s[1].lower() for s in secs if s[0] == 2}
    for need in ("the challenge", "what they did", "the results"):
        if need not in heads:
            f(f"no '## {need.title()}' section")
    results = " ".join(p for lvl, h, ps in secs if lvl == 2 and h.lower() == "the results" for p in ps)
    figs = NUM.findall(results)
    if "the results" in heads and not figs:
        f("the Results section has no number; state each result with its figure")
    if source_text is not None:
        for g in sorted(set(figs)):
            if g not in source_text:
                f(f"the figure '{g}' in Results is not in your source file")
    quote_lines = re.findall(r"(?m)^>\s*(\S.*)$", body)
    if not quote_lines:
        w("no customer quote; a quote in the customer's own words makes a case study more believable")
    elif len(quote_lines) < 2:
        w("the quote has no speaker name and title under it")
    n = wc(body)
    if n < 300 or n > 1500:
        w(f"{n} words; most case studies run 300 to 1,500")
    _lint(body, brand, res)
    return res


# ---------- long-form guide ----------
def build_guide(theme, ideas, brand, as_of, max_chapters=6):
    pool = [x for x in ideas if x["theme"] == theme]
    if not pool:
        raise ValueError(f"no ideas under theme '{theme}'")
    top = sorted(pool, key=lambda x: -x["score"])[:max_chapters]
    top.sort(key=lambda x: (STAGE_ORDER.get(x["stage"], 9), -x["score"]))
    camp = brand.get("campaign") or {}
    aud = camp.get("audience") or ", ".join(brand["audiences"])
    L = ["---", f"title: [MISSING: guide title. Working title: The {theme} guide for {aud}]", f"theme: {theme}", f"audience: {aud}",
         "funnel_stage: MOFU", f"campaign: {camp.get('name') or '[MISSING: no campaign set in the brand profile]'}",
         "author: [MISSING: a real person's name and role]", "date: [MISSING: publish date, YYYY-MM-DD]", "---", "",
         f"# [MISSING: guide title]", "",
         "[MISSING: introduction in 60 to 100 words: who this guide is for, the problem, and what they will be able to do by the end.]", ""]
    for i, x in enumerate(top, 1):
        q = headline_as_question(x["text"], theme, x["stage"])
        L += [f"## Chapter {i}: {q}", "", "[MISSING: answer in 40 to 60 words first, then the detail, an example, or a table.]", ""]
    L += ["## Checklist", "", "- [MISSING: one action per chapter, in the same order]", "",
          "## What to do next", "", "[MISSING: one next step and a link. A bottom of funnel piece, such as a case study or a demo page, fits here.]", "",
          "---", "", "## Writer's notes (delete before publishing)", "", f"Prepared as of {as_of}. Chapters come from the highest scoring ideas under the '{theme}' theme, in funnel order.", ""]
    for i, x in enumerate(top, 1):
        if x["kind"] == "keyword":
            d = x["data"]
            ev = f"keyword '{x['text']}', volume {d['volume']}, difficulty {d['difficulty']} (your keyword export)"
        else:
            it = x["item"]
            ev = f"{it['source']}: {it['title']} ({it['date'] or 'undated'}) {it['url'] or '[MISSING link]'}"
        L.append(f"- Chapter {i} ({x['stage']}, score {x['score']}): {ev}")
    L += ["", "**Checklist for the finished guide**: at least 5 chapters, every chapter opens with a short answer, at least 3 outside sources linked, one original element only you can supply (your data, a customer example, a decision rule), and every acronym spelled out.", ""]
    return "\n".join(L)


def check_guide(text, brand):
    res = []
    fm, body = parse(text)
    body = notes_stripped(body)
    w = lambda m: res.append(("WARN", m))
    _fm_required(fm, ("title", "author", "date"), res)
    secs = sections(body)
    chapters = [s for s in secs if s[0] == 2 and s[1].lower().startswith("chapter")]
    if len(chapters) < 5:
        res.append(("FAIL", f"{len(chapters)} chapters; a guide needs at least 5"))
    for lvl, head, paras in chapters:
        n = wc(paras[0]) if paras else 0
        if n < 15 or n > 70:
            w(f"under '{head[:50]}': the first paragraph is {n} words; open with a 15 to 70 word answer")
    if "checklist" not in {s[1].lower() for s in secs if s[0] == 2}:
        res.append(("FAIL", "no '## Checklist' section"))
    if len(set(LINK.findall(body))) < 3:
        w("fewer than 3 outside source links")
    n = wc(body)
    if n < 1500 or n > 6000:
        w(f"{n} words; most guides run 1,500 to 6,000")
    _lint(body, brand, res)
    return res


# ---------- short social post ----------
def build_social(idea, brand, as_of, platform="linkedin"):
    stage = idea["stage"]
    camp = brand.get("campaign") or {}
    q = headline_as_question(idea["text"], idea["theme"], stage)
    L = ["---", f"platform: {platform}", f"funnel_stage: {stage}", f"theme: {idea['theme'] or '[MISSING]'}", f"campaign: {camp.get('name') or '[MISSING: no campaign set]'}",
         "author: [MISSING: the person posting, with their role]", f"character_limit: {LIMITS[platform]}", "---", "",
         f"[MISSING: opening line, {HOOK_MAX} characters or fewer. A question or a specific number, not a teaser. Working idea: {q}]", "",
         "[MISSING: point one, one or two short sentences.]", "", "[MISSING: point two.]", "", "[MISSING: point three.]", "",
         "[MISSING: one source or example: where the fact comes from, with a link.]", "",
         "[MISSING: one question or next step for the reader.]", "", "[MISSING: up to 3 hashtags, or none.]", "",
         "---", "", "## Writer's notes (delete before publishing)", "", f"Prepared as of {as_of}. Format suggested for this stage: {idea['format']}.", ""]
    if camp:
        L += [*[f"- Pillar: {p}" for p in camp.get("pillars", [])], ""]
    if idea["kind"] == "keyword":
        d = idea["data"]
        L.append(f"- Evidence: keyword '{idea['text']}', volume {d['volume']}, difficulty {d['difficulty']} (your keyword export).")
    else:
        it = idea["item"]
        L.append(f"- Evidence: {it['source']}: {it['title']} ({it['date'] or 'undated'}) {it['url'] or '[MISSING link]'}. Paraphrase, do not copy.")
    L += ["", f"Posts run best with one idea, short lines, and a real person's voice. Words to avoid: {', '.join(brand['avoid_words']) or 'none set'}.", ""]
    return "\n".join(L)


def check_social(text, brand):
    res = []
    fm, body = parse(text)
    body = notes_stripped(body).strip()
    f = lambda m: res.append(("FAIL", m))
    w = lambda m: res.append(("WARN", m))
    _fm_required(fm, ("author",), res)
    plat = (fm.get("platform") or "linkedin").lower()
    limit = LIMITS.get(plat, 3000)
    if len(body) > limit:
        f(f"{len(body)} characters; {plat} allows {limit}")
    hook = body.splitlines()[0] if body else ""
    if "[MISSING" not in hook and len(hook) > HOOK_MAX:
        w(f"the opening line is {len(hook)} characters; feeds cut it off, so keep it to {HOOK_MAX} or fewer")
    tags = re.findall(r"#\w+", body)
    if len(tags) > 3:
        w(f"{len(tags)} hashtags; use 3 or fewer")
    if not LINK.search(body):
        w("no source link; name where the fact comes from")
    if "?" not in body:
        w("no question or call to the reader")
    _lint(body, brand, res)
    return res


def format_results(res):
    return "\n".join(f"{lvl}: {msg}" for lvl, msg in res) if res else "Draft OK"
