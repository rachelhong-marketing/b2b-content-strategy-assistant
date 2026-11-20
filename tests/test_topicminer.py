import json
import tempfile
import unittest
from pathlib import Path

from topicminer import brand, check, collect, competitors, funnel, keywords, report, sources, topics, cli
from topicminer.util import to_number, parse_date

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "sample-data"


class Util(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(to_number("1,200"), 1200)
        self.assertEqual(to_number("1K – 10K"), 1000)
        self.assertEqual(to_number("100 - 1K"), 100)
        self.assertEqual(to_number("< 10"), 0)
        self.assertIsNone(to_number(""))

    def test_dates(self):
        self.assertEqual(parse_date("Tue, 06 Oct 2026 09:00:00 GMT"), "2026-10-06")
        self.assertEqual(parse_date("2026-10-07T10:00:00Z"), "2026-10-07")
        self.assertEqual(parse_date("not a date"), "")


class Sources(unittest.TestCase):
    def test_rss_and_atom(self):
        rss = sources.parse_feed((DATA / "trade" / "example-revops-weekly.xml").read_text(), "a", "trade")
        atom = sources.parse_feed((DATA / "trade" / "example-martech-daily.xml").read_text(), "b", "trade")
        self.assertEqual((len(rss), len(atom)), (8, 6))
        self.assertTrue(all(i["url"].startswith("https://") and i["date"] for i in rss + atom))

    def test_html_is_stripped_and_text_is_short(self):
        xml = "<rss><channel><item><title>T</title><link>https://x.example/a</link><description>&lt;p&gt;" + "word " * 200 + "&lt;/p&gt;</description></item></channel></rss>"
        it = sources.parse_feed(xml, "s", "trade")[0]
        self.assertNotIn("<", it["text"])
        self.assertLessEqual(len(it["text"]), 300)

    def test_sitemap_titles_are_marked_derived(self):
        items = sources.parse_sitemap((DATA / "competitors" / "cleanly-sitemap.xml").read_text(), "cleanly")
        self.assertTrue(all(i["title_derived"] for i in items))
        self.assertIn("crm migration data prep", [i["title"] for i in items])

    def test_community_csv(self):
        items = sources.read_community_csv(DATA / "community" / "reddit-export.csv")
        self.assertEqual(len(items), 10)
        self.assertEqual(items[3]["engagement"], 210)


class Keywords(unittest.TestCase):
    def test_google_ads_skips_preamble_and_reads_ranges(self):
        ga = keywords.read_google_ads(DATA / "keywords" / "google-ads-keyword-planner.csv")
        self.assertEqual(ga["duplicate records in crm"]["volume"], 1000)
        self.assertEqual(ga["duplicate records in crm"]["bid_high"], 5.40)

    def test_semrush(self):
        sr = keywords.read_semrush(DATA / "keywords" / "semrush-keywords.csv")
        self.assertEqual(sr["duplicate records in crm"]["position"], 14)
        self.assertIsNone(sr["data hygiene best practices"]["position"])

    def test_trends_direction(self):
        tr = keywords.read_trends(DATA / "keywords" / "trends.csv")
        self.assertEqual(tr["ai data readiness"]["direction"], "up")
        self.assertEqual(tr["duplicate records in crm"]["direction"], "flat")

    def test_merge_uses_larger_volume_and_keeps_both_sources(self):
        ga = keywords.read_google_ads(DATA / "keywords" / "google-ads-keyword-planner.csv")
        sr = keywords.read_semrush(DATA / "keywords" / "semrush-keywords.csv")
        m = keywords.merge(ga, sr, keywords.read_trends(DATA / "keywords" / "trends.csv"))
        k = m["duplicate records in crm"]
        self.assertEqual(k["volume"], 2400)
        self.assertEqual(sorted(k["sources"]), ["google ads", "semrush"])
        self.assertEqual(m["ai data readiness"]["trend"], "up")


class Funnel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = funnel.load_rules()

    def test_stages(self):
        self.assertEqual(funnel.classify("what is data hygiene", self.rules)[0], "TOFU")
        self.assertEqual(funnel.classify("tidybase vs fernhill", self.rules)[0], "MOFU")
        self.assertEqual(funnel.classify("data quality software pricing", self.rules)[0], "BOFU")

    def test_cost_alone_is_not_bottom_of_funnel(self):
        self.assertNotEqual(funnel.classify("the hidden cost of messy data", self.rules)[0], "BOFU")

    def test_question_default(self):
        stage, why = funnel.classify("Is a one-time cleanup worth it?", self.rules)
        self.assertEqual(stage, "TOFU")


class Mining(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "brief.md"
        cls.text, cls.items = cli.mine(DATA, cls.out)
        cls.brand = brand.load(DATA / "brand" / "brand-profile.json")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_top_theme_and_ordering(self):
        rows = [l for l in self.text.split("\n") if l.startswith("| ") and "---" not in l and "Theme" not in l][:6]
        self.assertTrue(rows[0].startswith("| duplicate records"))
        scores = [float(r.split("|")[2]) for r in rows]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_every_idea_has_evidence(self):
        self.assertEqual(check.check_brief(self.text, self.brand), [])

    def test_all_three_stages_have_ideas(self):
        for h in ("(TOFU)", "(MOFU)", "(BOFU)"):
            section = self.text.split(h)[1].split("## ")[0]
            self.assertIn("- **", section)

    def test_missing_data_is_marked_not_filled(self):
        self.assertIn("[MISSING]", self.text)   # e.g. difficulty for keywords only in Google Ads

    def test_gaps_and_refresh(self):
        self.assertIn("no published BOFU content", self.text)
        self.assertIn("position 18", self.text)

    def test_competitor_diff_against_snapshot(self):
        snap = competitors.load_snapshot(DATA / "competitors" / "snapshot.json")
        new = competitors.new_since(self.items, snap)
        self.assertEqual(len(new["tidybase"]["new"]), 2)
        self.assertFalse(new["tidybase"]["baseline"])
        self.assertEqual(len(new["cleanly"]["new"]), 3)

    def test_first_run_is_baseline(self):
        new = competitors.new_since(self.items, {})
        self.assertTrue(new["tidybase"]["baseline"])

    def test_no_keyword_data_still_works_and_says_so(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            for sub in ("brand", "trade", "community"):
                (d / sub).mkdir()
            (d / "brand" / "brand-profile.json").write_text((DATA / "brand" / "brand-profile.json").read_text())
            (d / "trade" / "x.xml").write_text((DATA / "trade" / "example-revops-weekly.xml").read_text())
            text, _ = cli.mine(d, d / "o.md")
            self.assertIn("no keyword exports were provided", text)
            self.assertIn("weak signal", text)


class Checks(unittest.TestCase):
    def test_check_catches_planted_problems(self):
        b = brand.load(DATA / "brand" / "brand-profile.json")
        bad = "## Data used\n\n## Top of funnel (learning) (TOFU)\n- **A revolutionary idea**, score 50\n- **Another idea**, score 40\n  - Evidence: reddit post, no link here\n\n## Ebook or pillar candidates\n\n## Competitor activity\n"
        probs = " | ".join(check.check_brief(bad, b))
        self.assertIn("revolutionary", probs)
        self.assertIn("no evidence line", probs)
        self.assertIn("no link", probs)


class Collect(unittest.TestCase):
    def test_robots_is_obeyed_and_files_saved(self):
        pages = {"https://ok.example/robots.txt": (404, ""), "https://ok.example/feed.xml": (200, "<rss/>"),
                 "https://no.example/robots.txt": (200, "User-agent: *\nDisallow: /"), "https://no.example/feed.xml": (200, "<rss/>"),
                 "https://err.example/robots.txt": (500, "")}
        fake = lambda u: pages.get(u, (404, ""))
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "c.json"
            cfg.write_text(json.dumps([{"name": "ok", "url": "https://ok.example/feed.xml"}, {"name": "no", "url": "https://no.example/feed.xml"},
                                       {"name": "err", "url": "https://err.example/feed.xml"}]))
            slept = []
            res = dict(collect.run(cfg, Path(d) / "out", fetcher=fake, sleep=slept.append, delay=3))
            self.assertTrue(res["ok"].startswith("saved"))
            self.assertTrue(res["no"].startswith("skipped"))
            self.assertTrue(res["err"].startswith("skipped"))
            self.assertTrue((Path(d) / "out" / "ok.xml").exists())
            self.assertFalse((Path(d) / "out" / "no.xml").exists())
            self.assertEqual(slept, [3, 3])


class Hygiene(unittest.TestCase):
    def test_no_real_company_names_or_personal_details(self):
        banned = ["epsilon", "walmart", "pubmatic", "neustar", "rachel", "@gmail"]
        for p in ROOT.rglob("*"):
            if p.is_file() and p.suffix in (".py", ".md", ".csv", ".json", ".xml") and "output" not in p.parts and "tests" not in p.parts and ".git" not in p.parts:
                low = p.read_text(encoding="utf-8", errors="ignore").lower()
                for w in banned:
                    if w in low and not (w == "rachel" and p.name in ("README.md", "LICENSE")):
                        self.fail(f"{w!r} found in {p.relative_to(ROOT)}")


if __name__ == "__main__":
    unittest.main()
