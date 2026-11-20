"""Read trade-publication feeds, competitor feeds and sitemaps, and community posts exported or pasted as CSV.

Nothing here logs in to anything. Community sites that restrict automated collection (LinkedIn, Quora, G2 and others)
come in as CSV files that you export or paste yourself. Check each site's terms before you collect anything."""
import re
import xml.etree.ElementTree as ET
from html import unescape
from urllib.parse import urlparse

from .util import parse_date, read_csv_rows

ATOM = "{http://www.w3.org/2005/Atom}"


def _clean(html):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html or ""))).strip()


def parse_feed(xml_text, source, source_type):
    """RSS 2.0 or Atom -> list of normalized items. Keeps titles and short summaries only, never full articles."""
    root = ET.fromstring(xml_text)
    out = []
    for it in root.iter("item"):
        out.append(dict(source=source, source_type=source_type, title=_clean(it.findtext("title")),
                        text=_clean(it.findtext("description"))[:300], url=(it.findtext("link") or "").strip(),
                        date=parse_date(it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date")), engagement=0.0))
    for en in root.iter(ATOM + "entry"):
        link = en.find(ATOM + "link")
        out.append(dict(source=source, source_type=source_type, title=_clean(en.findtext(ATOM + "title")),
                        text=_clean(en.findtext(ATOM + "summary"))[:300], url=(link.get("href") if link is not None else "") or "",
                        date=parse_date(en.findtext(ATOM + "updated") or en.findtext(ATOM + "published")), engagement=0.0))
    return [i for i in out if i["title"]]


def parse_sitemap(xml_text, source):
    """Sitemap -> items. The title is guessed from the last part of the address, so it is marked as derived."""
    root = ET.fromstring(xml_text)
    out = []
    for u in root.iter():
        if u.tag.endswith("}url") or u.tag == "url":
            loc = lastmod = ""
            for c in u:
                if c.tag.endswith("loc"):
                    loc = (c.text or "").strip()
                elif c.tag.endswith("lastmod"):
                    lastmod = c.text or ""
            slug = urlparse(loc).path.rstrip("/").split("/")[-1].replace("-", " ").strip()
            if slug:
                out.append(dict(source=source, source_type="competitor", title=slug, text="", url=loc, date=parse_date(lastmod),
                                engagement=0.0, title_derived=True))
    return out


def read_community_csv(path, default_source="community"):
    """Columns: source,title,text,url,date,engagement. Engagement is any number you trust (upvotes, reactions, comments)."""
    items = []
    for r in read_csv_rows(path):
        title = (r.get("title") or "").strip()
        if not title:
            continue
        try:
            eng = float(str(r.get("engagement") or 0).replace(",", ""))
        except ValueError:
            eng = 0.0
        items.append(dict(source=(r.get("source") or default_source).strip().lower(), source_type="community", title=title,
                          text=(r.get("text") or "").strip()[:300], url=(r.get("url") or "").strip(),
                          date=parse_date(r.get("date")), engagement=eng))
    return items
