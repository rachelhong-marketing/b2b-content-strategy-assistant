"""Build structured data (JSON-LD) for a finished draft: an Article and, if the draft has a FAQ, a FAQPage.
Paste the result into the page inside a script tag of type application/ld+json. It describes only what is in the draft."""
import json
import re

from . import aeo
from .outline import slug


def _plain(text):
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    t = re.sub(r"[*_`>]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def build(text, brand, url=None):
    fm, body = aeo.parse(text)
    body = aeo.notes_stripped(body)
    secs = aeo.sections(body)
    title = fm.get("title", "")
    url = url or fm.get("url") or f"https://{brand['domain']}/blog/{slug(title)}"
    author = fm.get("author", "")
    person = {"@type": "Person", "name": author.split(",")[0].strip()}
    if "," in author:
        person["jobTitle"] = author.split(",", 1)[1].strip()
    graph = [{"@type": "Article", "headline": title, "author": person, "datePublished": fm.get("date", ""),
              "dateModified": fm.get("updated", ""), "mainEntityOfPage": url, "publisher": {"@type": "Organization", "name": brand["brand"]},
              "about": fm.get("theme", "")}]
    pairs = aeo.faq_pairs(secs)
    if pairs:
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _plain(a)}} for q, a in pairs]})
    return {"@context": "https://schema.org", "@graph": graph}


def dumps(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)
