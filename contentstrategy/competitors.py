"""Track what competitors publish: what is new since the last run, and which themes they push."""
import json
from collections import Counter
from pathlib import Path

from .topics import themes_for


def load_snapshot(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else {}


def new_since(items, snapshot):
    """Competitor items whose address was not in the last snapshot. First run (no snapshot) marks everything as 'baseline'."""
    out = {}
    for it in items:
        if it["source_type"] != "competitor":
            continue
        known = snapshot.get(it["source"])
        if known is None:
            out.setdefault(it["source"], dict(baseline=True, new=[]))["new"].append(it)
        elif it["url"] not in known:
            out.setdefault(it["source"], dict(baseline=False, new=[]))["new"].append(it)
    return out


def snapshot_of(items):
    snap = {}
    for it in items:
        if it["source_type"] == "competitor" and it["url"]:
            snap.setdefault(it["source"], []).append(it["url"])
    return snap


def theme_counts(items, themes):
    c = {}
    for it in items:
        if it["source_type"] != "competitor":
            continue
        for n in themes_for(it["title"], themes):
            c.setdefault(it["source"], Counter())[n] += 1
    return c
