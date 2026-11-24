# B2B Content Strategy Assistant

> **B2B Campaign Lifecycle Toolkit**, step 3 of 7
>
> [1. Position](https://github.com/rachelhong-marketing/b2b-product-marketing-agent) → [2. Plan](https://github.com/rachelhong-marketing/b2b-campaign-assistant) → **3. Content** → [4. Set up](https://github.com/rachelhong-marketing/b2b-paid-media-planner) → [5. Test](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) → [6. Report](https://github.com/rachelhong-marketing/b2b-campaign-reporting-agent) → [7. Prove](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool)

An AI assistant for B2B content strategy, in four jobs. It finds topics inside your campaign theme (from what your audience asks, what the press covers, what competitors publish and what people search for), ranks them by funnel stage with the evidence next to each one, helps write each piece in your voice, and checks that the piece is built for answer engine optimization (AEO, being quoted as the answer in search) and generative engine optimization (GEO, being cited by AI tools such as ChatGPT and Perplexity). It runs as a Claude Code skill and agent, with a small Python tool (standard library only) that does the counting and the checking.

All data here is made up. Fernhill Software is a fictional company. It sells the Fernhill Data Quality Platform, which finds and merges duplicate customer records across systems. The same company, product, buyers and competitors appear in the Campaign Assistant and the Product Marketing Agent.

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
| "Turn this idea into a draft" | A writing brief: question headline, direct-answer slot, question headings, FAQ, evidence, internal links, campaign pillars |
| "Is this draft ready for AI search?" | A pass/fail list from `aeo-check`, plus ready-to-paste structured data from `schema` |
| "Are AI tools citing us?" | A monthly tally from a manual test log |

## From topic to published piece

```
1. mine          rank ideas inside the campaign theme (ideas outside it count for 60 percent)
2. outline       pick one idea, get the writing brief with [MISSING] slots
3. write         you, or an AI assistant working in your voice, fill the slots. The tool writes no prose.
4. aeo-check     FAIL = fix before publishing, WARN = look at it
5. schema        article and FAQ structured data (JSON-LD) from the finished draft
6. publish       your site, your process
7. citation-log  each month, test the same buyer questions in ChatGPT, Perplexity, Google AI Overviews, Claude and Microsoft Copilot; log the result; the report counts it
```

What `aeo-check` looks at: an opening answer of 20 to 70 words, question headings each followed by a short answer, a FAQ with at least 3 questions, at least 2 outside sources, a list or table, a named author and dates, acronyms spelled out, your words to avoid, one consistent brand name, and no leftover [MISSING] slots.

**What this does not promise.** No search engine or AI tool publishes its ranking or citation rules. These checks follow common recommendations and make a page easier to quote. They do not guarantee a ranking or a citation, so measure with the citation log. The log is manual on purpose: there is no reliable free source of citation counts, and a few tests move around a lot, so the report says when there are too few to compare.

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
| Campaign (optional) | The campaign theme, audience, messaging pillars and which brand themes it covers, from the [Campaign Assistant](https://github.com/rachelhong-marketing/b2b-campaign-assistant) master brief. It sits in the brand profile under `campaign` |

Details and limits for each source are in [docs/data-sources-and-terms.md](docs/data-sources-and-terms.md).

## Quick start

```bash
python3 -m contentstrategy mine --data sample-data --out output/topic-brief.md
python3 -m contentstrategy check output/topic-brief.md --brand sample-data/brand/brand-profile.json
python3 -m contentstrategy outline --data sample-data --idea "how to remove duplicate contacts" --out-dir output/drafts
python3 -m contentstrategy aeo-check sample-data/drafts/how-to-spot-duplicate-records.md --brand sample-data/brand/brand-profile.json
python3 -m contentstrategy schema sample-data/drafts/how-to-spot-duplicate-records.md --brand sample-data/brand/brand-profile.json
python3 -m contentstrategy citation-sheet --data sample-data
python3 -m contentstrategy citation-report --data sample-data
python3 -m contentstrategy classify "how to choose a data quality platform"
python3 -m unittest discover -s tests
```

## Example output

From the sample data (full file: [docs/example-topic-brief.md](docs/example-topic-brief.md)). The sample is the same fictional company, product, buyers, competitors and campaign as the [Campaign Assistant](https://github.com/rachelhong-marketing/b2b-campaign-assistant) and the [Product Marketing Agent](https://github.com/rachelhong-marketing/b2b-product-marketing-agent). The data is made up.

| Theme | Score | Demand (monthly searches) | Trend | Sources | Competitors posted | You posted | Note |
|---|---|---|---|---|---|---|---|
| duplicate records | 80.3 | 6,590 | flat | example-martech-daily, example-revops-weekly, quora, reddit | 3 | 2 |  |
| customer data cleanup | 80.1 | 6,610 | flat | example-martech-daily, example-revops-weekly, linkedin, quora, reddit | 1 | 2 |  |
| ai data readiness | 43.3 | 320 | up | example-martech-daily, example-revops-weekly, quora | 1 | 0 |  |
| trusted reporting | 38.0 | 1,220 | unknown | example-martech-daily, example-revops-weekly, quora, reddit | 0 | 0 |  |
| crm migration | 29.4 | 390 | unknown | example-revops-weekly, linkedin | 1 | 0 |  |

```
## Top of funnel (learning) (TOFU)

- **what is data hygiene**, score 89.0, theme: customer data cleanup, suggested format: Blog post or explainer
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

An idea's score is half its theme's score and half its own signal (search volume and ease for keywords, engagement for questions, freshness for headlines). The weights are in `contentstrategy/topics.py`.

## Three ways to use it

| Way | What you do | Files |
|---|---|---|
| Skill (on demand) | Ask Claude Code to mine topics, outline an idea, write it in your voice, then run the AEO and GEO checks | `.claude/skills/content-strategy/SKILL.md` |
| Agent (weekly) | Copy `.claude/agents/content-strategy-assistant.md` into your project, then schedule `prompts/weekly-run.md`. It compares with last week and remembers topics you chose | `.claude/agents/`, `prompts/`, `docs/agent-spec.md` |
| Copilot (judgment only) | Paste the brief into a Copilot agent; no code runs | `copilot/` |

Weekly command: `python3 -m contentstrategy weekly --data <folder> --out-dir output/weekly [--collect-config collect-config.json]`. Memory lives in `<folder>/state/`. Keep your own data folder private.

## Guardrails and limits

- **Evidence first.** Every idea has a link or keyword data next to it. Gaps are marked [MISSING]. The `check` command fails a brief without evidence or with words on your avoid list.
- **Weak signals are labeled** when a theme has one source type and no keyword data.
- **Rule-based, not magic.** Themes are matched by your trigger phrases and funnel stages by simple patterns, so it misses things you have not listed. Read the "possible new themes" section for gaps.
- **Titles only for competitor sitemaps.** Titles are guessed from addresses and marked as derived.
- **No scraping behind logins.** Community posts come from exports you make. See the data guide.
- **Scores are not forecasts.** They help a team decide what to read first.
- **`collect` is untested against live sites.** It was tested with a stand-in fetcher.
- **AEO and GEO checks are recommendations, not rules.** See "What this does not promise" above.
- **The tool writes no article text.** It builds the brief and checks the draft. A human (or an AI assistant working in the brand voice) writes it, and a human checks every claim and number.
- A human still chooses the angle, writes in the brand voice and checks every claim.

## Repo layout

```
.claude/skills/content-strategy/SKILL.md   the skill
.claude/agents/content-strategy-assistant.md         the weekly agent
prompts/weekly-run.md                 schedule prompt
copilot/                              Copilot instructions and setup
contentstrategy/                           sources, keywords, funnel, topics, competitors, report, check, collect, weekly,
                                      outline, aeo, schema, citations
rules/funnel-patterns.csv             funnel stage rules
sample-data/                          made-up brand and campaign, feeds, posts, keyword exports, competitor files,
                                      a finished draft, an AI citation log
docs/                                 data guide, example brief, example writing brief, example structured data, agent spec
tests/                                41 tests
```

## The B2B Campaign Lifecycle Toolkit

Seven tools, one per step of a B2B campaign, from positioning to proving pipeline. Each works on its own; together they cover the whole cycle. All sample data is made up.

| Step | Tool | What it does |
|---|---|---|
| 1. Position | [B2B Product Marketing Agent](https://github.com/rachelhong-marketing/b2b-product-marketing-agent) | Define who you sell to and what you say: ideal customer profile, positioning, messaging pillars and proof points, checked for gaps before any campaign starts. |
| 2. Plan | [B2B Campaign Assistant](https://github.com/rachelhong-marketing/b2b-campaign-assistant) | Turn the positioning into a campaign theme, write the campaign plan and master brief, then draft channel briefs, keywords, landing page and ad copy, all checked before launch. |
| 3. Content | **B2B Content Strategy Assistant** (this repo) | Pick content topics inside the campaign theme from audience questions, news, competitors and keyword data, outline and check each piece so search and AI answer tools can quote it, and log whether AI answers cite you. |
| 4. Set up | [B2B Paid Media Planner](https://github.com/rachelhong-marketing/b2b-paid-media-planner) | Plan channels and retargeting, then build and check tracking links before launch. |
| 5. Test | [B2B Campaign Test Planner](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) | Plan tests in waves, let the ad platform call the winner, check MQLs, and size tests when volume is small. |
| 6. Report | [B2B Campaign Reporting Agent](https://github.com/rachelhong-marketing/b2b-campaign-reporting-agent) | Consolidate ad platform and CRM data into one file, check every channel and funnel stage for gaps, and draft insights. |
| 7. Prove | [B2B Pipeline Attribution Tool](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool) | Check the CRM data can be trusted, then show sourced and influenced pipeline. |

## About the author

**Rachel Hong** has worked in B2B demand generation and marketing analytics for more than ten years, at marketing and advertising technology companies. She builds campaigns, reporting and the AI workflows that help marketing teams plan and measure them.

[LinkedIn](https://www.linkedin.com/in/rachelhongatbaruch/)

## License

MIT. See `LICENSE`.
