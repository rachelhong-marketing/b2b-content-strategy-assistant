"""Past performance of your own published pieces, from an analytics export.

File: <data>/content/content-performance.csv with columns url, title, stage, publish_date, visits, conversions, promotion_spend, channel.
Pieces are compared with others at the SAME funnel stage, so bottom-of-funnel pages are not beaten by top-of-funnel pages on raw visits:
top of funnel is judged on visits, middle and bottom of funnel on conversions (downloads, leads or MQLs, whatever you count at that stage).
A piece with promotion spend is flagged, because paid promotion can make a weak topic look strong."""
from pathlib import Path

from .util import minmax, read_csv_rows, to_number

MIN_SAME_STAGE = 2
MIN_SAME_THEME = 3


def load(data):
    p = Path(data) / "content" / "content-performance.csv"
    rows = read_csv_rows(p) if p.exists() else []
    out = []
    for r in rows:
        stage = (r.get("stage") or "").upper()
        if stage not in ("TOFU", "MOFU", "BOFU"):
            continue
        out.append(dict(url=r.get("url", ""), title=r.get("title", ""), stage=stage, date=r.get("publish_date", ""),
                        visits=to_number(r.get("visits")), conversions=to_number(r.get("conversions")),
                        spend=to_number(r.get("promotion_spend")) or 0.0, channel=r.get("channel", "")))
    metric = lambda x: x["visits"] if x["stage"] == "TOFU" else x["conversions"]
    for s in ("TOFU", "MOFU", "BOFU"):
        grp = [x for x in out if x["stage"] == s and metric(x) is not None]
        scaled = minmax({i: metric(x) for i, x in enumerate(grp)})
        for x in out:
            if x["stage"] == s:
                x["score"] = None
        for i, x in enumerate(grp):
            x["score"] = scaled[i]
    return out


def for_idea(perf, theme, stage, themes_for_fn, themes):
    """Returns dict(value, n, promoted, basis) or None. Prefers the same theme and stage, then the same theme at any stage."""
    if not perf or not theme:
        return None
    mine = [x for x in perf if x.get("score") is not None and theme in themes_for_fn(x["title"], themes)]
    same = [x for x in mine if x["stage"] == stage]
    if len(same) >= MIN_SAME_STAGE:
        use, basis = same, "same theme and stage"
    elif len(mine) >= MIN_SAME_THEME:
        use, basis = mine, "same theme, other stages included"
    else:
        return None
    return dict(value=sum(x["score"] for x in use) / len(use), n=len(use), promoted=sum(1 for x in use if x["spend"] > 0), basis=basis)


def note(info):
    if not info:
        return "[MISSING] too few past pieces on this theme"
    s = f"{info['basis']}, {info['n']} pieces"
    if info["promoted"]:
        s += f", {info['promoted']} had paid promotion"
    return s
