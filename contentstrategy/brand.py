"""Load the brand profile: who you sell to, what you want to be known for, how you sound, and who you compete with."""
import json

REQUIRED = ("brand", "domain", "audiences", "themes", "avoid_words", "competitors")


def load(path):
    with open(path, encoding="utf-8") as fh:
        b = json.load(fh)
    missing = [k for k in REQUIRED if k not in b]
    if missing:
        raise ValueError(f"brand profile is missing: {', '.join(missing)}")
    for name, t in b["themes"].items():
        if not t.get("triggers"):
            raise ValueError(f"theme '{name}' needs at least one trigger phrase")
        t.setdefault("fit", 0.5)
    b.setdefault("product", b["brand"])
    b.setdefault("known_acronyms", [])
    c = b.get("campaign")
    if c:
        unknown = [t for t in c.get("themes", []) if t not in b["themes"]]
        if unknown:
            raise ValueError(f"campaign themes not in the theme list: {', '.join(unknown)}")
        c.setdefault("pillars", [])
        c.setdefault("audience", "")
    return b
