"""Read keyword research exports: Google Ads Keyword Planner, Semrush and Google Trends. You export the files; this reads them.
Volumes are used exactly as exported. Nothing is estimated or filled in."""
import csv

from .util import to_number


def _rows(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.reader(fh))


def _header_index(rows, first_cells):
    for i, r in enumerate(rows):
        if r and r[0].strip().lower() in first_cells:
            return i
    raise ValueError(f"No header row found in file (looked for a first column named one of {sorted(first_cells)}).")


def read_google_ads(path):
    """Keyword Planner export. Preamble lines above the header are skipped."""
    rows = _rows(path)
    h = _header_index(rows, {"keyword"})
    head = [c.strip().lower() for c in rows[h]]
    def col(*names):
        for n in names:
            for i, c in enumerate(head):
                if c.startswith(n):
                    return i
        return None
    vi, ci, bi = col("avg. monthly searches", "avg monthly searches"), col("competition"), col("top of page bid (high")
    out = {}
    for r in rows[h + 1:]:
        if not r or not r[0].strip():
            continue
        k = r[0].strip().lower()
        out[k] = dict(keyword=k, volume=to_number(r[vi]) if vi is not None and vi < len(r) else None,
                      competition=(r[ci].strip() if ci is not None and ci < len(r) else ""),
                      bid_high=to_number(r[bi]) if bi is not None and bi < len(r) else None, source="google ads")
    return out


def read_semrush(path):
    rows = _rows(path)
    h = _header_index(rows, {"keyword"})
    head = [c.strip().lower() for c in rows[h]]
    def idx(name):
        return head.index(name) if name in head else None
    vi, ki, pi, ui, ci = idx("search volume"), idx("keyword difficulty"), idx("position"), idx("url"), idx("cpc")
    def get(r, i):
        return r[i] if i is not None and i < len(r) else None
    out = {}
    for r in rows[h + 1:]:
        if not r or not r[0].strip():
            continue
        k = r[0].strip().lower()
        out[k] = dict(keyword=k, volume=to_number(get(r, vi)), difficulty=to_number(get(r, ki)), position=to_number(get(r, pi)),
                      url=(get(r, ui) or "").strip(), cpc=to_number(get(r, ci)), source="semrush")
    return out


def read_trends(path):
    """Google Trends export: a Week/Month/Time column, then one column per term. Direction = last third vs first third."""
    rows = _rows(path)
    h = _header_index(rows, {"week", "month", "day", "time"})
    head = rows[h]
    out = {}
    for ci in range(1, len(head)):
        term = head[ci].split(":")[0].strip().lower()
        vals = [to_number(r[ci]) for r in rows[h + 1:] if len(r) > ci and r[ci].strip()]
        vals = [v for v in vals if v is not None]
        if len(vals) < 6:
            out[term] = dict(term=term, direction="unknown", change=None)
            continue
        n = max(1, len(vals) // 3)
        first, last = sum(vals[:n]) / n, sum(vals[-n:]) / n
        ratio = (last / first) if first else None
        direction = "unknown" if ratio is None else "up" if ratio > 1.15 else "down" if ratio < 0.85 else "flat"
        out[term] = dict(term=term, direction=direction, change=None if ratio is None else round(ratio - 1, 2))
    return out


def merge(google_ads=None, semrush=None, trends=None):
    """One record per keyword. Where two exports give a volume, the larger one is used and both source names are kept."""
    merged = {}
    for src in (google_ads or {}, semrush or {}):
        for k, v in src.items():
            m = merged.setdefault(k, dict(keyword=k, volume=None, difficulty=None, position=None, url="", cpc=None, bid_high=None, competition="", sources=[]))
            if v.get("volume") is not None and (m["volume"] is None or v["volume"] > m["volume"]):
                m["volume"] = v["volume"]
            for f in ("difficulty", "position", "cpc", "bid_high"):
                if v.get(f) is not None and m[f] is None:
                    m[f] = v[f]
            if v.get("url") and not m["url"]:
                m["url"] = v["url"]
            if v.get("competition") and not m["competition"]:
                m["competition"] = v["competition"]
            m["sources"].append(v["source"])
    for k, m in merged.items():
        t = (trends or {}).get(k)
        m["trend"] = t["direction"] if t else "unknown"
    return merged
