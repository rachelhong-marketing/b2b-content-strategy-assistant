import json
import tempfile
import unittest
from pathlib import Path

from contentstrategy import brand, check, collect, competitors, funnel, keywords, report, sources, topics, cli
from contentstrategy.util import to_number, parse_date

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
        items = sources.parse_sitemap((DATA / "competitors" / "datavault-sitemap.xml").read_text(), "datavault")
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
        self.assertEqual(funnel.classify("clearline vs fernhill", self.rules)[0], "MOFU")
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
        self.assertIn("Themes with search demand and no page from you yet", self.text)
        self.assertIn("position 18", self.text)

    def test_competitor_diff_against_snapshot(self):
        snap = competitors.load_snapshot(DATA / "competitors" / "snapshot.json")
        new = competitors.new_since(self.items, snap)
        self.assertEqual(len(new["clearline"]["new"]), 2)
        self.assertFalse(new["clearline"]["baseline"])
        self.assertEqual(len(new["datavault"]["new"]), 3)

    def test_first_run_is_baseline(self):
        new = competitors.new_since(self.items, {})
        self.assertTrue(new["clearline"]["baseline"])

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


class Weekly(unittest.TestCase):
    def _copy(self, d):
        import shutil
        dst = Path(d) / "data"
        shutil.copytree(DATA, dst)
        return dst

    def test_first_run_is_baseline_then_second_run_has_no_changes(self):
        from contentstrategy import weekly
        with tempfile.TemporaryDirectory() as d:
            data, out = self._copy(d), Path(d) / "out"
            r1 = weekly.run(data, out)
            self.assertTrue(r1["ok"])
            self.assertIn("First run", Path(r1["note"]).read_text())
            self.assertTrue((data / "state" / "last-run.json").exists())
            r2 = weekly.run(data, out)
            note = Path(r2["note"]).read_text()
            self.assertIn("Compared with the run of", note)
            self.assertIn("Nothing new since the last run", note)

    def test_new_competitor_post_shows_up(self):
        from contentstrategy import weekly
        with tempfile.TemporaryDirectory() as d:
            data, out = self._copy(d), Path(d) / "out"
            weekly.run(data, out)
            feed = data / "competitors" / "clearline-feed.xml"
            txt = feed.read_text()
            item = "<item><title>Brand new post about pipeline reporting</title><link>https://clearline.example/new</link><pubDate>Mon, 19 Oct 2026 09:00:00 GMT</pubDate></item>"
            feed.write_text(txt.replace("<item>", item + "<item>", 1))
            note = Path(weekly.run(data, out)["note"]).read_text()
            self.assertIn("clearline: 1 new", note)

    def test_chosen_topics_are_hidden(self):
        from contentstrategy import weekly
        with tempfile.TemporaryDirectory() as d:
            data, out = self._copy(d), Path(d) / "out"
            r = weekly.run(data, out)
            first = weekly._top_ideas(Path(r["brief"]).read_text())
            self.assertTrue(first)
            state = data / "state"
            state.mkdir(exist_ok=True)
            (state / "chosen-topics.csv").write_text("text\n" + first[0] + "\n")
            r2 = weekly.run(data, out)
            self.assertNotIn(first[0], weekly._top_ideas(Path(r2["brief"]).read_text()))

    def test_failure_is_reported_not_raised(self):
        from contentstrategy import weekly
        with tempfile.TemporaryDirectory() as d:
            data = self._copy(d)
            (data / "brand" / "brand-profile.json").write_text("not json")
            r = weekly.run(data, Path(d) / "out")
            self.assertFalse(r["ok"])
            self.assertIn("failed", Path(r["note"]).read_text())

    def test_collect_folder_option(self):
        pages = {"https://ok.example/robots.txt": (404, ""), "https://ok.example/feed.xml": (200, "<rss/>")}
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "c.json"
            cfg.write_text(json.dumps([{"name": "ok", "url": "https://ok.example/feed.xml", "folder": "trade"}]))
            collect.run(cfg, Path(d) / "out", fetcher=lambda u: pages.get(u, (404, "")), sleep=lambda s: None)
            self.assertTrue((Path(d) / "out" / "trade" / "ok.xml").exists())


class Aeo(unittest.TestCase):
    BRAND = brand.load(DATA / "brand" / "brand-profile.json")
    GOOD = (DATA / "drafts" / "how-to-spot-duplicate-records.md").read_text()

    def levels(self, text):
        from contentstrategy import aeo
        return aeo.check_draft(text, self.BRAND, "2026-10-23")

    def test_sample_draft_passes(self):
        self.assertEqual(self.levels(self.GOOD), [])

    def test_missing_placeholders_fail(self):
        res = self.levels(self.GOOD.replace("author: Sam Example, Head of Data Engineering", "author: [MISSING: name]"))
        self.assertTrue(any(l == "FAIL" and "author" in m for l, m in res))

    def test_acronym_must_be_spelled_out(self):
        res = self.levels(self.GOOD.replace("customer relationship management (CRM)", "CRM"))
        self.assertTrue(any("acronym 'CRM'" in m for l, m in res))

    def test_long_opening_answer_fails(self):
        first = self.GOOD.split("\n# ", 1)[1].split("\n\n", 2)[1]
        res = self.levels(self.GOOD.replace(first, "word " * 90))
        self.assertTrue(any("first paragraph" in m and l == "FAIL" for l, m in res))

    def test_avoid_word_and_brand_name_variants(self):
        res = self.levels(self.GOOD.replace("Fernhill Software built", "Fernhill software is revolutionary and built"))
        msgs = " ".join(m for _, m in res)
        self.assertIn("revolutionary", msgs)
        self.assertIn("more than one way", msgs)

    def test_no_faq_fails_and_stale_date_warns(self):
        res = self.levels(self.GOOD.split("## Frequently asked questions")[0].replace("updated: 2026-10-20", "updated: 2025-01-01"))
        self.assertTrue(any(l == "FAIL" and "FAQ" in m for l, m in res))
        self.assertTrue(any(l == "WARN" and "12 months" in m for l, m in res))


class Schema(unittest.TestCase):
    def test_article_and_faq_graph(self):
        from contentstrategy import schema
        g = schema.build((DATA / "drafts" / "how-to-spot-duplicate-records.md").read_text(), brand.load(DATA / "brand" / "brand-profile.json"))
        kinds = [n["@type"] for n in g["@graph"]]
        self.assertEqual(kinds, ["Article", "FAQPage"])
        self.assertEqual(len(g["@graph"][1]["mainEntity"]), 4)
        self.assertEqual(g["@graph"][0]["author"]["name"], "Sam Example")
        json.dumps(g)


class Outline(unittest.TestCase):
    def test_outline_is_a_valid_unfinished_draft(self):
        from contentstrategy import aeo, outline
        ctx = cli.analyze(DATA, top=50)
        idea = outline.find_idea(ctx["ideas"], "duplicate contacts")
        text = outline.build(idea, ctx["brand"], ctx["inventory"], ctx["as_of"])
        self.assertIn("title: ", text)
        self.assertIn("[MISSING", text)
        self.assertGreaterEqual(len(aeo.faq_pairs(aeo.sections(aeo.notes_stripped(aeo.parse(text)[1])))), 3)
        res = aeo.check_draft(text, ctx["brand"], ctx["as_of"])
        self.assertTrue(any("[MISSING]" in m for l, m in res))

    def test_unknown_idea_raises(self):
        from contentstrategy import outline
        with self.assertRaises(ValueError):
            outline.find_idea([], "nothing")


class Campaign(unittest.TestCase):
    def test_off_theme_ideas_are_scored_lower_and_labeled(self):
        ctx = cli.analyze(DATA, top=50)
        off = [x for x in ctx["ideas"] if not x["on_campaign"]]
        self.assertTrue(off)
        self.assertIn("outside the campaign theme", ctx["text"])
        b = brand.load(DATA / "brand" / "brand-profile.json")
        self.assertEqual(set(b["campaign"]["themes"]) - set(b["themes"]), set())

    def test_bad_campaign_theme_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            b = json.loads((DATA / "brand" / "brand-profile.json").read_text())
            b["campaign"]["themes"] = ["not a theme"]
            p = Path(d) / "b.json"
            p.write_text(json.dumps(b))
            with self.assertRaises(ValueError):
                brand.load(p)


class Citations(unittest.TestCase):
    def test_sheet_adds_rows_once_and_report_counts(self):
        from contentstrategy import citations
        with tempfile.TemporaryDirectory() as d:
            n1 = citations.add_sheet(d, ["Why are reports wrong?"])
            n2 = citations.add_sheet(d, ["Why are reports wrong?"])
            self.assertEqual((n1, n2), (5, 0))
            self.assertIn("No tests logged", citations.summary(d)[0])
        lines = "\n".join(citations.summary(DATA))
        self.assertIn("16 tests logged", lines)
        self.assertIn("too few tests to compare", lines)
        self.assertIn("clearline", lines)


class Scoring(unittest.TestCase):
    BRAND = brand.load(DATA / "brand" / "brand-profile.json")

    def test_weights_sum_to_one_and_demand_equals_performance(self):
        from contentstrategy import scoring
        self.assertAlmostEqual(sum(scoring.WEIGHTS.values()), 1.0)
        self.assertEqual(scoring.WEIGHTS["demand"], scoring.WEIGHTS["performance"])
        self.assertEqual(scoring.WEIGHTS["demand"], 0.25)

    def test_missing_factor_is_left_out_and_rest_scale_up(self):
        from contentstrategy import scoring
        full = dict(campaign=1.0, performance=1.0, demand=1.0, ease=1.0, audience=1.0, trend=1.0, gap=1.0)
        self.assertEqual(scoring.combine(full), (100.0, []))
        s, left = scoring.combine(dict(full, performance=None))
        self.assertEqual((s, left), (100.0, ["performance"]))
        s, left = scoring.combine(dict(full, performance=0.0))
        self.assertEqual(s, 75.0)
        self.assertEqual(scoring.combine({k: None for k in full})[0], 0.0)

    def test_campaign_relevance_is_graded(self):
        from contentstrategy import topics
        on_pillar = topics.campaign_relevance("duplicate records", "how to find duplicate records across systems", self.BRAND)
        on_theme_only = topics.campaign_relevance("duplicate records", "dedupe contacts quickly", self.BRAND)
        off = topics.campaign_relevance("lead routing", "lead routing rules", self.BRAND)
        self.assertGreater(on_pillar, on_theme_only)
        self.assertGreater(on_theme_only, off)
        self.assertEqual(on_theme_only, 0.6)
        self.assertLessEqual(off, 0.15)

    def test_no_campaign_falls_back_to_brand_fit(self):
        from contentstrategy import topics
        b = dict(self.BRAND)
        b.pop("campaign")
        self.assertEqual(topics.campaign_relevance("duplicate records", "anything", b), b["themes"]["duplicate records"]["fit"])


class Performance(unittest.TestCase):
    def test_pieces_are_scored_within_their_own_stage(self):
        from contentstrategy import performance
        perf = performance.load(DATA)
        by = {x["title"]: x for x in perf}
        # a middle-of-funnel page with few visits but the most conversions still tops its stage
        self.assertEqual(by["CRM data cleanup: where to start"]["score"], 1.0)
        self.assertEqual(by["Duplicate records in your CRM: how to spot them"]["score"], 1.0)
        # top of funnel is judged on visits, so a bottom-of-funnel page's low visits do not hurt it
        self.assertGreater(by["Customer story: a regional bank merges duplicate records"]["score"], 0.9)

    def test_promoted_pieces_are_counted(self):
        from contentstrategy import performance, topics
        perf = performance.load(DATA)
        b = brand.load(DATA / "brand" / "brand-profile.json")
        info = performance.for_idea(perf, "duplicate records", "TOFU", topics.themes_for, b["themes"])
        self.assertEqual(info["basis"], "same theme and stage")
        self.assertEqual(info["promoted"], 1)
        self.assertIn("paid promotion", performance.note(info))

    def test_too_few_pieces_means_missing_not_a_guess(self):
        from contentstrategy import performance, topics
        perf = performance.load(DATA)
        b = brand.load(DATA / "brand" / "brand-profile.json")
        self.assertIsNone(performance.for_idea(perf, "lead routing", "TOFU", topics.themes_for, b["themes"]))
        self.assertIsNone(performance.for_idea([], "duplicate records", "TOFU", topics.themes_for, b["themes"]))
        self.assertIn("[MISSING]", performance.note(None))

    def test_brief_without_performance_file_says_so_and_still_works(self):
        import shutil
        with tempfile.TemporaryDirectory() as d:
            data = Path(d) / "data"
            shutil.copytree(DATA, data)
            (data / "content" / "content-performance.csv").unlink()
            ctx = cli.analyze(data)
            self.assertIn("no content performance export", ctx["text"])
            self.assertTrue(all("performance" in x["left_out"] for x in ctx["ideas"]))
            self.assertEqual(check.check_brief(ctx["text"], ctx["brand"]), [])

    def test_brief_shows_score_parts_for_every_idea(self):
        ctx = cli.analyze(DATA)
        n_ideas = sum(len(v) for v in ctx["by_stage"].values())
        self.assertEqual(ctx["text"].count("  - Score parts:"), n_ideas)
        self.assertEqual(ctx["text"].count("  - Past performance:"), n_ideas)
        self.assertIn("campaign relevance 25%", ctx["text"])


class Hygiene(unittest.TestCase):
    def test_no_real_company_names_or_personal_details(self):
        banned = ["epsilon", "walmart", "pubmatic", "neustar", "rachel", "@gmail"]
        for p in ROOT.rglob("*"):
            rel = p.relative_to(ROOT).parts
            if p.is_file() and p.suffix in (".py", ".md", ".csv", ".json", ".xml") and "output" not in rel and "tests" not in rel and ".git" not in rel:
                low = p.read_text(encoding="utf-8", errors="ignore").lower()
                for w in banned:
                    if w in low and not (w == "rachel" and p.name in ("README.md", "LICENSE")):
                        self.fail(f"{w!r} found in {p.relative_to(ROOT)}")


if __name__ == "__main__":
    unittest.main()
