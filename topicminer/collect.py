"""Optional: download feeds and sitemaps you list in a config file. Slow on purpose, polite, and it obeys robots.txt.

It reads only feeds and sitemaps. It does not log in, does not use cookies and does not collect community posts.
Check each site's terms before you point it anywhere. This has been tested with a stand-in fetcher, not against live sites."""
import json
import time
import urllib.request
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

UA = "b2b-content-topic-miner/0.1 (personal research; contact: see repository)"
MAX_BYTES = 2_000_000


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(MAX_BYTES).decode("utf-8", "replace")
    except HTTPError as e:
        return e.code, ""


def allowed(url, fetcher=fetch):
    p = urlparse(url)
    status, body = fetcher(f"{p.scheme}://{p.netloc}/robots.txt")
    if status == 404:
        return True
    if status != 200:
        return False
    rp = RobotFileParser()
    rp.parse(body.splitlines())
    return rp.can_fetch(UA, url)


def run(config_path, outdir, fetcher=fetch, sleep=time.sleep, delay=3.0):
    """Config: a JSON list of {"name": "...", "url": "..."}. Returns a list of (name, result) lines."""
    cfg = json.loads(Path(config_path).read_text())
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for n, src in enumerate(cfg):
        if n:
            sleep(delay)
        name, url = src["name"], src["url"]
        if not allowed(url, fetcher):
            results.append((name, "skipped: robots.txt does not allow it, or could not be read"))
            continue
        status, body = fetcher(url)
        if status != 200 or not body.strip():
            results.append((name, f"failed: status {status}"))
            continue
        (out / f"{name}.xml").write_text(body, encoding="utf-8")
        results.append((name, f"saved {len(body):,} characters"))
    return results
