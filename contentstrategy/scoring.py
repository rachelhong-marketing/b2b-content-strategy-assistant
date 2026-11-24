"""One scoring formula for themes and ideas. Seven factors, each scaled 0 to 1, each with a weight.

If a factor has no data (for example you gave no content performance export), it is left out and the rest are scaled up,
and the brief lists the missing factor. Scores compare options within one run. They are not forecasts."""

WEIGHTS = dict(campaign=0.25, performance=0.25, demand=0.25, ease=0.05, audience=0.10, trend=0.05, gap=0.05)
LABELS = dict(campaign="Campaign relevance", performance="Past performance", demand="Search demand", ease="Ranking ease",
              audience="Audience signal", trend="Trend and freshness", gap="Competitor gap")
OFF_CAMPAIGN_FIT = 0.15  # an idea outside the campaign themes keeps at most 15 percent of its brand fit as campaign relevance


def combine(parts):
    """parts: factor -> 0..1 or None. Returns (score 0..100, list of factors left out)."""
    use = {k: v for k, v in parts.items() if v is not None}
    total = sum(WEIGHTS[k] for k in use)
    if not total:
        return 0.0, list(WEIGHTS)
    return round(100 * sum(WEIGHTS[k] * v for k, v in use.items()) / total, 1), [k for k in WEIGHTS if k not in use]


def parts_line(parts):
    out = []
    for k in WEIGHTS:
        v = parts.get(k)
        out.append(f"{k} {v:.2f}" if v is not None else f"{k} [MISSING]")
    return " | ".join(out)
