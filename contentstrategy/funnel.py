"""Sort a keyword or question into a funnel stage with simple, editable rules (rules/funnel-patterns.csv).

TOFU = top of funnel: the reader is learning about a problem.
MOFU = middle of funnel: the reader is comparing options or approaches.
BOFU = bottom of funnel: the reader is close to choosing and needs proof or a next step."""
import csv
import re
from pathlib import Path

DEFAULT_RULES = Path(__file__).resolve().parent.parent / "rules" / "funnel-patterns.csv"
STAGES = ("TOFU", "MOFU", "BOFU")
STAGE_NAMES = {"TOFU": "Top of funnel (learning)", "MOFU": "Middle of funnel (comparing)", "BOFU": "Bottom of funnel (deciding)"}
FORMATS = {"TOFU": "Blog post or explainer", "MOFU": "Guide, checklist, comparison or webinar", "BOFU": "Case study, ROI calculator or demo page"}


def load_rules(path=DEFAULT_RULES):
    rules = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rules.append((r["stage"].strip().upper(), re.compile(r["pattern"].strip(), re.I), float(r.get("weight") or 1)))
    return rules


def classify(text, rules):
    """Returns (stage, matched_pattern or ''). Highest total weight wins; ties go to the deeper stage."""
    score = {s: 0.0 for s in STAGES}
    hit = {}
    for stage, rx, w in rules:
        if rx.search(text or ""):
            score[stage] += w
            hit.setdefault(stage, rx.pattern)
    best = max(STAGES, key=lambda s: (score[s], STAGES.index(s)))
    if score[best] > 0:
        return best, hit.get(best, "")
    t = (text or "").strip().lower()
    if t.endswith("?") or re.match(r"^(how|why|what|when|should|can|is|are|do|does)\b", t):
        return "TOFU", "(default: question)"
    return "MOFU", "(default: no pattern matched)"
