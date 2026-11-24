"""Check a draft article for answer engine optimization (AEO) and generative engine optimization (GEO).

AEO is making content easy for search features and assistants to quote as the answer. GEO is making content easy for
AI tools to cite. Nobody publishes the real ranking rules, so these checks are common recommendations: an answer first,
question headings, short Q and A, named sources, an original element, a real author and a date. They raise the odds.
They are not guarantees. Measure the result with the citation log."""
import re
from datetime import date

from .util import has_phrase

QWORD = re.compile(r"(?i)^(what|why|how|when|who|which|should|can|does|do|is|are|will|where)\b")
LINK = re.compile(r"https?://[^\s)>\]]+")


def parse(text):
    """Returns (front matter dict, body text without front matter)."""
    fm, body = {}, text
    if text.startswith("---"):
        parts = text.split("\n---", 1)
        if len(parts) == 2:
            for ln in parts[0].splitlines()[1:]:
                if ":" in ln:
                    k, v = ln.split(":", 1)
                    fm[k.strip()] = v.strip()
            body = parts[1].lstrip("-").lstrip("\n")
    return fm, body


def notes_stripped(body):
    return body.split("\n## Writer's notes")[0]


def sections(body):
    """List of (level, heading, [paragraphs]) in order. Paragraphs are blank-line separated blocks."""
    out, cur = [], None
    for block in re.split(r"\n\s*\n", body):
        lines = block.strip().splitlines()
        if not lines:
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", lines[0])
        if m:
            cur = (len(m.group(1)), m.group(2).strip(), [])
            out.append(cur)
            rest = "\n".join(lines[1:]).strip()
            if rest:
                cur[2].append(rest)
        elif cur:
            cur[2].append(block.strip())
    return out


def wc(text):
    return len(re.findall(r"[A-Za-z0-9']+", re.sub(r"\[[^\]]*\]\([^)]*\)", " ", text)))


def faq_pairs(secs):
    pairs, on = [], False
    for lvl, head, paras in secs:
        if lvl == 2:
            on = bool(re.search(r"(?i)\b(faq|frequently asked|common questions)\b", head))
        elif lvl == 3 and on:
            pairs.append((head, paras[0] if paras else ""))
    return pairs


def check_draft(text, brand, as_of=None):
    """Returns a list of (level, message). level is 'FAIL' (fix before publishing) or 'WARN' (look at it)."""
    res = []
    fm, body = parse(text)
    body = notes_stripped(body)
    secs = sections(body)
    f = lambda m: res.append(("FAIL", m))
    w = lambda m: res.append(("WARN", m))
    for k in ("title", "author", "date", "original_angle", "primary_question"):
        if not fm.get(k) or "[MISSING" in fm[k]:
            f(f"front matter '{k}' is empty or still [MISSING]")
    if "[MISSING" in body:
        f("the draft still has [MISSING] placeholders")
    upd = fm.get("updated", "")
    if upd and "[MISSING" not in upd and as_of:
        try:
            if (date.fromisoformat(as_of) - date.fromisoformat(upd)).days > 365:
                w("last updated more than 12 months ago; refresh the facts and the date")
        except ValueError:
            w("'updated' is not a valid YYYY-MM-DD date")
    elif not upd or "[MISSING" in upd:
        f("front matter 'updated' is empty or still [MISSING]")
    h1 = [s for s in secs if s[0] == 1]
    if not h1:
        f("no H1 title heading")
    else:
        first = h1[0][2][0] if h1[0][2] else ""
        n = wc(first)
        if not 20 <= n <= 70:
            f(f"the first paragraph is {n} words; open with a direct answer of 20 to 70 words")
    qh = [s for s in secs if s[0] == 2 and QWORD.match(s[1]) and not re.search(r"(?i)faq|frequently", s[1])]
    if len(qh) < 2:
        w("fewer than 2 question headings; phrase section headings as the questions people ask")
    for lvl, head, paras in qh:
        n = wc(paras[0]) if paras else 0
        if n > 70 or n < 15:
            w(f"under '{head}': the first paragraph is {n} words; start with a 15 to 70 word answer")
    pairs = faq_pairs(secs)
    if not pairs:
        f("no FAQ section (a '## Frequently asked questions' heading with '###' questions)")
    elif len(pairs) < 3:
        w(f"only {len(pairs)} FAQ questions; aim for at least 3")
    for q, a in pairs:
        if wc(a) > 80:
            w(f"FAQ answer is over 80 words: {q[:60]}")
    if len(set(LINK.findall(body))) < 2:
        w("fewer than 2 outside source links; name and link where facts come from")
    if not re.search(r"(?m)^\s*([-*]|\d+\.)\s+\S", body) and "|---" not in body:
        w("no list or table; steps and comparisons are easier to quote in a list or table")
    n = wc(body)
    if n < 500 or n > 2200:
        w(f"{n} words; most useful pieces on one question run 500 to 2,200")
    for word in brand.get("avoid_words", []):
        if has_phrase(body, word):
            f(f"brand voice: the word '{word}' is on your avoid list")
    known = set(brand.get("known_acronyms", []))
    seen = set()
    for m in re.finditer(r"\b[A-Z]{2,6}\b", body):
        a = m.group(0)
        if a in known or a in seen:
            continue
        seen.add(a)
        before, after = body[max(0, m.start() - 1):m.start()], body[m.end():m.end() + 2]
        if not ((before == "(" and after.startswith(")")) or after == " ("):
            f(f"acronym '{a}' is not spelled out on first use")
    name = brand["brand"]
    variants = {m.group(0) for m in re.finditer(re.escape(name), body, re.I)}
    if not variants:
        w(f"the brand name '{name}' never appears; name it where it fits so assistants can tie the answer to you")
    elif variants != {name}:
        w(f"the brand name is written more than one way: {', '.join(sorted(variants))}")
    return res


def format_results(res):
    return "\n".join(f"{lvl}: {msg}" for lvl, msg in res) if res else "Draft OK"
