# B2B Content Topic Miner

> **B2B Campaign Lifecycle Toolkit**, step 0 (Research)
>
> **0. Research** → [1. Plan](https://github.com/rachelhong-marketing/b2b-campaign-assistant) → [2. Set up](https://github.com/rachelhong-marketing/b2b-paid-media-planner) → [3. Test](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) → [4. Report](https://github.com/rachelhong-marketing/b2b-campaign-reporting-agent) → [5. Prove](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool)

An AI agent that finds content topics worth writing about. It combines what your audience asks, what the industry press is covering, what competitors publish, and what people search for, then ranks topic ideas by funnel stage with the evidence next to each one. It runs as a Claude Code skill, with a small Python tool (standard library only) that does the counting.

All data here is made up. Fernhill Software is a fictional company that sells software to clean up duplicate and messy customer records in a CRM.

## Why this exists

Content brainstorms usually start from opinions: what the team feels like writing, or what a competitor just posted. The evidence is scattered across Reddit threads, news feeds, keyword tools and competitor sites, and nobody has time to read all of it. This tool reads it for you, keeps the source next to every idea, and leaves the judgment and the writing to you.

## What it does

```
Brand profile (audiences, themes, voice, competitors)
        |
Audience questions + industry news + competitor pages + keyword exports
        |
   Group under your themes  -->  score each theme  -->  sort ideas by funnel stage
        |
Brainstorm brief: ranked themes, TOFU / MOFU / BOFU ideas with evidence,
ebook candidates, SEO fixes, competitor activity
```

| You ask | You get |
|---|---|
| "Find content topics for Q4" | A ranked list of themes and, for each funnel stage, topic ideas with evidence and a suggested format |
| "Where are we thin on bottom-of-funnel content?" | Stage gaps compared with your content inventory |
| "What did competitors publish since last time?" | New pages per competitor and the themes they push |
| "Where can we improve for search?" | Pages ranking 11 to 20 worth refreshing, and themes with demand and no page from you |
| "Which topics could be an ebook?" | Themes with enough ideas across stages |

The three funnel stages: **top of funnel (TOFU)** is learning about a problem, **middle of funnel (MOFU)** is comparing options, and **bottom of funnel (BOFU)** is close to choosing. Rules for sorting are in `rules/funnel-patterns.csv` and are easy to edit.

## Inputs

| Input | Where it comes from |
|---|---|
| Brand profile | You write it once: audiences, themes with trigger phrases, words to avoid, domain, competitors |
| Trade news | Feeds you list |
| Competitors | Their feeds or sitemaps |
| Audience questions | CSV you export or paste from Reddit, LinkedIn, Quora, G2 |
| Keywords | Exports from Google Ads Keyword Planner, Semrush and Google Trends |
| Content inventory | A CSV of what you have published, with funnel stage |

Details and limits for each source are in [docs/data-sources-and-terms.md](docs/data-sources-and-terms.md).

## Quick start

```bash
python3 -m topicminer mine --data sample-data --out output/topic-brief.md
python3 -m topicminer check output/topic-brief.md --brand sample-data/brand/brand-profile.json
python3 -m topicminer classify "how to choose a data quality platform"
python3 -m unittest discover -s tests
```

## Example output

From the sample data (full file: [docs/example-topic-brief.md](docs/example-topic-brief.md)):

| Theme | Score | Demand (monthly searches) | Trend | Sources | Competitors posted | You posted | Note |
| duplicate records | 80.3 | 6,590 | flat | example-martech-daily, example-revops-weekly, quora, reddit | 3 | 2 |  |
| crm data cleanup | 75.7 | 6,610 | flat | example-martech-daily, example-revops-weekly, linkedin, quora, reddit | 1 | 2 |  |
| ai data readiness | 43.3 | 320 | up | example-martech-daily, example-revops-weekly, quora | 1 | 0 |  |
| trusted reporting | 38.0 | 1,220 | unknown | example-martech-daily, example-revops-weekly, quora, reddit | 0 | 0 |  |
| crm migration | 29.4 | 390 | unknown | example-revops-weekly, linkedin | 1 | 0 |  |

```
## Top of funnel (learning) (TOFU)

- **what is data hygiene**, score 86.8, theme: crm data cleanup, suggested format: Blog post or explainer
  - Keyword data: volume 5,400, difficulty 35, cost per click $2.10 (Semrush), trend unknown (google ads, semrush); stage rule: TOFU (matched a rule)
- **how to remove duplicate contacts**, score 76.0, theme: duplicate records, suggested format: Blog post or explainer
  - Keyword data: volume 3,600, difficulty 41, cost per click $2.60 (Semrush), trend unknown (google ads, semrush); stage rule: TOFU (matched a rule)
```

## How a theme is scored

Each theme gets a score from 0 to 100, made of eight parts. Every part is scaled across the themes in the same run, so scores compare themes within a run only.

| Part | Weight | Meaning |
|---|---|---|
| Mentions | 20% | How many news items and posts mention the theme (competitor posts count half) |
| Demand | 20% | Total monthly searches for its keywords |
| Engagement | 10% | Upvotes, reactions and similar on audience posts |
| Ease | 10% | Lower keyword difficulty scores higher; unknown scores in the middle |
| Trend | 10% | Search interest going up, flat or down |
| Questions | 10% | Share of mentions that are real questions |
| Brand fit | 10% | The fit you set for the theme in the brand profile |
| Competitor gap | 10% | Competitors have covered it and you have not |

An idea's score is half its theme's score and half its own signal (search volume and ease for keywords, engagement for questions, freshness for headlines). The weights are in `topicminer/topics.py`.

## Guardrails and limits

- **Evidence first.** Every idea has a link or keyword data next to it. Gaps are marked [MISSING]. The `check` command fails a brief without evidence or with words on your avoid list.
- **Weak signals are labeled** when a theme has one source type and no keyword data.
- **Rule-based, not magic.** Themes are matched by your trigger phrases and funnel stages by simple patterns, so it misses things you have not listed. Read the "possible new themes" section for gaps.
- **Titles only for competitor sitemaps.** Titles are guessed from addresses and marked as derived.
- **No scraping behind logins.** Community posts come from exports you make. See the data guide.
- **Scores are not forecasts.** They help a team decide what to read first.
- **`collect` is untested against live sites.** It was tested with a stand-in fetcher.
- A human still chooses the angle, writes in the brand voice and checks every claim.

## Repo layout

```
.claude/skills/topic-miner/SKILL.md   the skill
topicminer/                           sources, keywords, funnel, topics, competitors, report, check, collect
rules/funnel-patterns.csv             funnel stage rules
sample-data/                          made-up brand, feeds, posts, keyword exports, competitor files
docs/                                 data guide and an example brief
tests/                                24 tests
```

## B2B Campaign Lifecycle Toolkit

| Step | Tool | What it does |
|---|---|---|
| 0. Research | **B2B Content Topic Miner** (this repo) | Find content topics from audience questions, news, competitors and keyword data, sorted by funnel stage. |
| 1. Plan | [B2B Campaign Assistant](https://github.com/rachelhong-marketing/b2b-campaign-assistant) | Brainstorm the campaign theme, write the campaign plan and master brief, then draft channel briefs, keywords, landing page and ad copy, all checked before launch. |
| 2. Set up | [B2B Paid Media Planner](https://github.com/rachelhong-marketing/b2b-paid-media-planner) | Plan channels and retargeting, then build and check tracking links before launch. |
| 3. Test | [B2B Campaign Test Planner](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) | Plan tests in waves, let the ad platform call the winner, check MQLs, and size tests when volume is small. |
| 4. Report | [B2B Campaign Reporting Agent](https://github.com/rachelhong-marketing/b2b-campaign-reporting-agent) | Consolidate ad platform and CRM data into one file, check every channel and funnel stage for gaps, and draft insights. |
| 5. Prove | [B2B Pipeline Attribution Tool](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool) | Check the CRM data can be trusted, then show sourced and influenced pipeline. |

## About the author

**Rachel Hong** has worked in B2B demand generation and marketing analytics for more than ten years, at marketing and advertising technology companies. She builds campaigns, reporting and the AI workflows that help marketing teams plan and measure them.

[LinkedIn](https://www.linkedin.com/in/rachelhongatbaruch/)

## License

MIT. See `LICENSE`.
