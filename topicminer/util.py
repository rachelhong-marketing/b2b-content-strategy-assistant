"""Small shared helpers. Standard library only."""
import csv
import re
from datetime import date, datetime
from email.utils import parsedate_to_datetime

STOP = set("""a an and are as at be by for from has have how i in is it its of on or our so that the their this to was we what when where which who why will with you your can do does should vs versus""".split())


def words(text):
    return re.findall(r"[a-z0-9']+", (text or "").lower())


def has_phrase(text, phrase):
    """Whole-word match, so 'dedupe' does not match inside another word."""
    return re.search(r"\b" + re.escape(phrase.lower()) + r"\b", (text or "").lower()) is not None


def to_number(value):
    """'1,200' -> 1200, '1K - 10K' -> 1000 (lower end), '< 10' -> 0, '' -> None."""
    if value is None:
        return None
    s = str(value).strip().lower().replace(",", "")
    if not s or s in ("n/a", "-", "--"):
        return None
    if "<" in s:
        return 0.0
    s = re.split(r"\s*[–—-]\s*", s)[0]
    m = re.match(r"^([0-9]*\.?[0-9]+)\s*([km]?)", s)
    if not m:
        return None
    n = float(m.group(1))
    return n * {"k": 1_000, "m": 1_000_000}.get(m.group(2), 1)


def parse_date(text):
    """Best-effort date to YYYY-MM-DD, or '' if unknown."""
    s = (text or "").strip()
    if not s:
        return ""
    for fn in (lambda x: parsedate_to_datetime(x).date(), lambda x: datetime.fromisoformat(x.replace("Z", "+00:00")).date(),
               lambda x: datetime.strptime(x[:10], "%Y-%m-%d").date()):
        try:
            return fn(s).isoformat()
        except Exception:
            continue
    return ""


def days_between(a, b):
    try:
        return (date.fromisoformat(a) - date.fromisoformat(b)).days
    except Exception:
        return None


def minmax(values):
    """Scale a dict of numbers to 0..1. All-equal input maps to 0."""
    vals = [v for v in values.values() if v is not None]
    if not vals:
        return {k: 0.0 for k in values}
    lo, hi = min(vals), max(vals)
    return {k: ((v - lo) / (hi - lo) if (v is not None and hi > lo) else 0.0) for k, v in values.items()}


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))
