"""The weekly run: collect, mine, compare with last week, save a short 'what changed' note, and remember the run.

Memory lives in <data>/state/: last-run.json (themes, scores, top ideas, as-of date) and chosen-topics.csv (ideas you already picked).
Every step is wrapped, so one failed feed never stops the run. Failures are listed at the top of the note."""
import json
from datetime import date
from pathlib import Path

from . import collect, competitors
from .cli import _load_items, mine


def _top_ideas(text):
    """Idea headlines in a brief: the bold text of lines that start with '- **' inside the funnel sections."""
    out, on = [], False
    for ln in text.split("\n"):
        if ln.startswith("## ") and "(TOFU)" in ln:
            on = True
        elif ln.startswith("## Ebook"):
            on = False
        if on and ln.startswith("- **"):
            out.append(ln[4:].split("**")[0])
    return out


def _theme_scores(text):
    rows = {}
    for ln in text.split("\n"):
        if ln.startswith("| ") and "---" not in ln and "Theme" not in ln:
            p = [c.strip() for c in ln.strip("|").split("|")]
            try:
                rows[p[0]] = float(p[1])
            except (ValueError, IndexError):
                pass
    return rows


def run(data, out_dir, collect_config=None, as_of=None, today=None):
    data, out_dir = Path(data), Path(out_dir)
    state = data / "state"
    state.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    problems = []
    if collect_config:
        try:
            for name, res in collect.run(collect_config, data):
                if not res.startswith("saved"):
                    problems.append(f"{name}: {res}")
        except Exception as e:
            problems.append(f"collection failed: {e}")
    last_path = state / "last-run.json"
    last = json.loads(last_path.read_text()) if last_path.exists() else None
    brief_tmp = out_dir / "_latest.md"
    try:
        text, items = mine(data, brief_tmp, as_of)
    except Exception as e:
        note = out_dir / f"{(today or date.today()).isoformat()}-what-changed.md"
        note.write_text(f"# Weekly run failed\n\nThe topic brief could not be built: {e}\n\n" + "\n".join(f"- {p}" for p in problems))
        return dict(ok=False, note=str(note), problems=problems + [str(e)])
    stamp = next((l.split("as of ")[1].split(".")[0] for l in text.split("\n") if l.startswith("Prepared as of ")), "") or (today or date.today()).isoformat()
    brief = out_dir / f"{stamp}-topic-brief.md"
    brief_tmp.replace(brief)
    scores, ideas = _theme_scores(text), _top_ideas(text)
    snap_old = competitors.load_snapshot(data / "competitors" / "snapshot.json")
    comp_new = competitors.new_since(items, snap_old)
    L = [f"# What changed this week ({stamp})", ""]
    if problems:
        L += ["## Problems in this run", ""] + [f"- {p}" for p in problems] + [""]
    if last is None:
        L += ["First run: nothing to compare with yet. This brief is the baseline.", ""]
    else:
        L += [f"Compared with the run of {last['stamp']}.", "", "## Theme scores that moved 5 points or more", ""]
        moved = [(t, s - last["scores"].get(t, 0)) for t, s in scores.items() if abs(s - last["scores"].get(t, 0)) >= 5]
        L += [f"- {t}: {d:+.1f}" for t, d in sorted(moved, key=lambda x: -abs(x[1]))] or ["- None."]
        fresh = [i for i in ideas if i not in last["ideas"]]
        L += ["", "## New top ideas", ""] + [f"- {i}" for i in fresh[:10]] if fresh else ["", "## New top ideas", "", "- None."]
    L += ["", "## Competitor activity", ""]
    real_new = {k: v for k, v in comp_new.items() if not v["baseline"] and v["new"]}
    L += [f"- {k}: {len(v['new'])} new" for k, v in real_new.items()] or ["- Nothing new since the last run." if last else "- Baseline saved."]
    L += ["", f"Full brief: {brief.name}", ""]
    note = out_dir / f"{stamp}-what-changed.md"
    note.write_text("\n".join(L), encoding="utf-8")
    (data / "competitors" / "snapshot.json").write_text(json.dumps(competitors.snapshot_of(items), indent=1))
    last_path.write_text(json.dumps(dict(stamp=stamp, scores=scores, ideas=ideas), indent=1))
    return dict(ok=True, brief=str(brief), note=str(note), problems=problems)
