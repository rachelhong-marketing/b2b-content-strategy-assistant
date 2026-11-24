"""A manual log of whether AI answers cite you. Nobody offers free, reliable citation counts, so you test a fixed list of
buyer questions by hand each month (ChatGPT, Perplexity, Google AI Overviews, Claude, Microsoft Copilot), write down what you see,
and this module counts it. Small samples move around a lot, so the report says when there are too few tests to compare."""
import csv
from collections import Counter, defaultdict
from pathlib import Path

ENGINES = ["ChatGPT", "Perplexity", "Google AI Overviews", "Claude", "Microsoft Copilot"]
FIELDS = ["date_tested", "question", "engine", "our_site_cited", "competitors_cited", "notes"]
CITED = {"yes": 1.0, "mentioned": 0.5, "no": 0.0}
MIN_TESTS = 20


def log_path(data):
    return Path(data) / "state" / "ai-citation-log.csv"


def read(data):
    p = log_path(data)
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def add_sheet(data, questions, engines=ENGINES):
    """Append blank rows for questions not in the log yet. Returns the number of rows added."""
    p = log_path(data)
    p.parent.mkdir(parents=True, exist_ok=True)
    rows = read(data)
    have = {(r["question"].lower(), r["engine"]) for r in rows}
    new = [dict(date_tested="", question=q, engine=e, our_site_cited="", competitors_cited="", notes="")
           for q in questions for e in engines if (q.lower(), e) not in have]
    with open(p, "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=FIELDS)
        wr.writeheader()
        wr.writerows(rows + new)
    return len(new)


def summary(data):
    """Lines of plain text. Only rows with a result in 'our_site_cited' (yes, mentioned or no) are counted."""
    rows = [r for r in read(data) if (r.get("our_site_cited") or "").strip().lower() in CITED]
    if not rows:
        return ["No tests logged yet. Run the questions in the log by hand and fill in the 'our_site_cited' column (yes, mentioned or no)."]
    L = [f"{len(rows)} tests logged. Scoring: yes = 1, mentioned (brand named, no link) = 0.5, no = 0.", ""]
    by_engine, by_month = defaultdict(list), defaultdict(list)
    comp = Counter()
    for r in rows:
        v = CITED[r["our_site_cited"].strip().lower()]
        by_engine[r["engine"]].append(v)
        by_month[(r["date_tested"] or "undated")[:7]].append(v)
        for c in (r.get("competitors_cited") or "").replace(";", ",").split(","):
            if c.strip():
                comp[c.strip().lower()] += 1
    L.append("By engine:")
    for e, v in sorted(by_engine.items()):
        L.append(f"- {e}: {100 * sum(v) / len(v):.0f}% over {len(v)} tests" + (" (too few tests to compare)" if len(v) < MIN_TESTS else ""))
    L += ["", "By month:"]
    for m, v in sorted(by_month.items()):
        L.append(f"- {m}: {100 * sum(v) / len(v):.0f}% over {len(v)} tests" + (" (too few tests to compare)" if len(v) < MIN_TESTS else ""))
    if comp:
        L += ["", "Competitors cited most: " + ", ".join(f"{c} ({n})" for c, n in comp.most_common(5))]
    never = sorted({r["question"] for r in rows} - {r["question"] for r in rows if CITED[r["our_site_cited"].strip().lower()] > 0})
    if never:
        L += ["", "Questions where you were never cited (candidates for a new or rewritten page):"] + [f"- {q}" for q in never[:10]]
    return L
