"""Check a finished brief: evidence next to every idea, no banned words, and no silent gaps."""
import re

from .util import has_phrase


def check_brief(text, brand):
    problems = []
    lines = text.split("\n")
    start = next((i for i, ln in enumerate(lines) if ln.startswith("## ") and "(TOFU)" in ln), None)
    end = next((i for i, ln in enumerate(lines) if ln.startswith("## Ebook or pillar")), len(lines))
    if start is None:
        problems.append("no funnel stage sections found")
        start = end = 0
    for w in brand.get("avoid_words", []):
        if has_phrase(text, w):
            problems.append(f"brand voice: the word '{w}' is on your avoid list")
    for i in range(start, end):
        ln = lines[i]
        if ln.startswith("- **"):
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if not re.match(r"\s+- (Evidence|Keyword data):", nxt):
                problems.append(f"no evidence line under: {ln[:70]}")
            elif "http" not in nxt and "Keyword data" not in nxt and "[MISSING" not in nxt:
                problems.append(f"evidence has no link: {ln[:70]}")
    for h in ("## Competitor activity", "## Data used"):
        if h not in text:
            problems.append(f"missing section: {h}")
    return problems
