# B2B Content Strategy Assistant

> **B2B Campaign Lifecycle Toolkit**, step 3 of 7
>
> [1. Position](https://github.com/rachelhong-marketing/b2b-product-marketing-agent) → [2. Plan](https://github.com/rachelhong-marketing/b2b-campaign-assistant) → **3. Content** → [4. Set up](https://github.com/rachelhong-marketing/b2b-paid-media-planner) → [5. Test](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) → [6. Report](https://github.com/rachelhong-marketing/b2b-campaign-reporting-agent) → [7. Prove](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool)

An AI assistant for B2B content strategy, in four jobs. It finds topics inside your campaign theme (from what your audience asks, what the press covers, what competitors publish and what people search for), ranks them by funnel stage with the evidence next to each one, helps write each piece in your voice, and checks that the piece is built for answer engine optimization (AEO, being quoted as the answer in search) and generative engine optimization (GEO, being cited by AI tools such as ChatGPT and Perplexity). It runs as a Claude Code skill and agent, with a small Python tool (standard library only) that does the counting and the checking.

All data here is made up. Fernhill Software is a fictional company. It sells the Fernhill Data Quality Platform, which finds and merges duplicate customer records across systems. The same company, product, buyers and competitors appear in the Campaign Assistant and the Product Marketing Agent.

## What you give it, and what you get back

### What you give it

| You provide | What it is | Where it usually comes from |
|---|---|---|
| Brand profile | Your audiences, content themes, words to avoid, competitors and website | You write it once. Step 1 and step 2 can supply much of it |
| Audience questions | What your buyers ask online | Reddit, LinkedIn, Quora, G2, exported or pasted as CSV |
| Industry news | Stories your buyers read | News feeds you list |
| Competitor pages | What competitors publish | Their feeds or sitemaps |
| Keywords | What people search for and how often | Google Keyword Planner, Semrush, Google Trends |
| Content inventory and performance (optional) | What you have published and how each page did | Your website and analytics |
| Campaign (optional) | The campaign theme and messages | The [Campaign Assistant](https://github.com/rachelhong-marketing/b2b-campaign-assistant) master brief |
| A finished draft (optional) | A piece you wrote, to check it | You |

### What you get back

| Output | What it looks like | Example |
|---|---|---|
| Topic brief | Ranked themes and content ideas for each funnel stage, each with its evidence and a suggested format | [Topic brief](docs/example-topic-brief.md) |
| Stage gaps | Where you are thin on top, middle or bottom of funnel content | [Topic brief](docs/example-topic-brief.md) |
| Competitor activity | New pages each competitor published and what they push | [Topic brief](docs/example-topic-brief.md) |
| Search fixes | Pages worth refreshing, and themes with demand and no page from you | [Topic brief](docs/example-topic-brief.md) |
| Writing brief | For one idea: question headline, direct-answer slot, question headings, FAQ, evidence, internal links | [Writing brief](docs/example-draft-brief.md) |
| Case study brief | Outline built from a real customer source file (approved, with permission), with every fact listed and every sentence left for you. The check fails any number not in the source | [Brief](docs/example-case-study-brief.md), [finished example](docs/example-case-study-finished.md) |
| Long-form guide outline | Chapters taken from your best-scoring ideas on one theme, in funnel order, with evidence for each | [Outline](docs/example-guide-outline.md) |
| Short social post brief | Opening line, three points, source and call to action, with the platform's character limit | [Brief](docs/example-social-post-brief.md) |
| AI search check | A pass or fail list for a finished blog draft | `aeo-check` |
| Format check | The same kind of pass or fail list for a case study, guide or social post | `format-check` |
| Structured data | Ready-to-paste article and FAQ markup | [Schema](docs/example-schema.json) |
| Citation report | A monthly count of whether AI tools quote you, from your manual test log | `citation-report` |

### What it writes, and what it doesn't

| Format | What the tool gives you | Who writes the words |
|---|---|---|
| Blog post or explainer | Writing brief, AEO and GEO check, structured data | You, or Claude working in your voice |
| Case study | Outline and a strict check. Needs a customer source file with the customer's permission and an approver. It never invents a customer, quote or number | You or Claude, from the facts in the source file |
| Long-form guide or ebook | Chapter outline and a check | You or Claude |
| Short social post | Brief with the character limit, and a check | You or Claude |

The Python tool writes no prose in any format. In Claude Code the skill has Claude fill each `[MISSING]` slot, then run the check. Each draft still needs a person's review. For ad and email copy, use the [Campaign Assistant](https://github.com/rachelhong-marketing/b2b-campaign-assistant).

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
| "Which topics fit our campaign and have worked before?" | Ideas ranked on campaign fit, your own past results, and search demand, with each idea's score parts shown |
| "Where can we improve for search?" | Pages ranking 11 to 20 worth refreshing, and themes with demand and no page from you |
| "Which topics could be an ebook?" | Themes with enough ideas across stages |
| "Turn this idea into a draft" | A writing brief: question headline, direct-answer slot, question headings, FAQ, evidence, internal links, campaign pillars |
| "Is this draft ready for AI search?" | A pass/fail list from `aeo-check`, plus ready-to-paste structured data from `schema` |
| "Are AI tools citing us?" | A monthly tally from a manual test log |

## From topic to published piece

```
1. mine          rank ideas by campaign relevance, past performance, search demand and four smaller factors
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

## Input details

| Input | Where it comes from |
|---|---|
| Brand profile | You write it once: audiences, themes with trigger phrases, words to avoid, domain, competitors |
| Trade news | Feeds you list |
| Competitors | Their feeds or sitemaps |
| Audience questions | CSV you export or paste from Reddit, LinkedIn, Quora, G2 |
| Keywords | Exports from Google Ads Keyword Planner, Semrush and Google Trends |
| Content inventory | A CSV of what you have published, with funnel stage. If you give only the performance file, the inventory is built from it |
| Content performance | A CSV from your analytics: `url, title, stage, publish_date, visits, conversions, promotion_spend, channel`. Use the conversion count that matters at that stage (downloads, leads or MQLs). Optional, but it is a quarter of the score |
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

| Theme | Score | Campaign | Past performance | Demand (monthly searches) | Trend | Sources | Competitors posted | You posted | Note |
|---|---|---|---|---|---|---|---|---|---|
| duplicate records | 82.7 | on campaign | 69 (5 pieces) | 6,590 | flat | example-martech-daily, example-revops-weekly, quora, reddit | 3 | 5 |  |
| customer data cleanup | 80.5 | on campaign | 59 (4 pieces) | 6,610 | flat | example-martech-daily, example-revops-weekly, linkedin, quora, reddit | 1 | 4 |  |
| trusted reporting | 37.5 | on campaign | 6 (3 pieces) | 1,220 | unknown | example-martech-daily, example-revops-weekly, quora, reddit | 0 | 3 |  |
| ai data readiness | 24.9 | off campaign | [MISSING] | 320 | up | example-martech-daily, example-revops-weekly, quora | 1 | 0 |  |

```
## Top of funnel (learning) (TOFU)

- **Why duplicate records quietly wreck your pipeline reports**, score 88.5, theme: duplicate records, suggested format: Blog post or explainer
  - Evidence: example-revops-weekly headline, 2026-10-06, https://revops-weekly.example/duplicate-records-pipeline; stage rule: TOFU (matched a rule)
  - Score parts: campaign 1.00 | performance 0.89 | demand 1.00 | ease 0.70 | audience 0.95 | trend 0.66 | gap 0.00
  - Past performance: same theme and stage, 2 pieces, 1 had paid promotion
```

## How ideas and themes are scored

Every topic idea, and every theme in the themes table, gets a score from 0 to 100 from the same seven factors. Each factor is scaled from 0 to 1.

| Factor | Weight | What it measures |
|---|---|---|
| Campaign relevance | 25% | How closely the idea fits your campaign. On-campaign theme = 0.6, plus up to 0.4 for words shared with the campaign theme or a pillar. Off-campaign ideas keep at most 15% of their brand fit. With no campaign set, it is the theme's brand fit |
| Past performance | 25% | How your published pieces on this theme did, compared only with your pieces at the same funnel stage. Top of funnel is judged on visits, middle and bottom of funnel on conversions |
| Search demand | 25% | Monthly searches for the keyword (or, for a question or headline, for the theme's keywords) |
| Ranking ease | 5% | Lower keyword difficulty scores higher; unknown scores in the middle |
| Audience signal | 10% | Questions people ask, engagement on audience posts and how often the theme comes up |
| Trend and freshness | 5% | Search interest going up, flat or down, and how recent the news or post is |
| Competitor gap | 5% | Competitors have covered it and you have not |

The weights are in `contentstrategy/scoring.py` and are meant as a starting point. Edit them to match what your team cares about.

- **Missing data is left out, not guessed.** If a factor has no data (for example no performance export), it is dropped, the others scale up, and the idea's "Score parts" line says what was left out.
- **Performance needs enough pieces.** An idea uses the average of your pieces on the same theme and stage if there are at least 2. If not, it uses the theme across all stages if there are at least 3. Otherwise it is [MISSING].
- **Paid promotion is flagged.** A piece that did well with ad budget behind it may not prove the topic is good, so the brief says how many of the pieces were promoted.
- **Compare ideas within a funnel stage.** Bottom-of-funnel searches are small by nature, so those ideas will score lower on demand than top-of-funnel ideas. The brief ranks them within each stage for that reason.
- **Scores compare options in one run.** They are not forecasts.

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
tests/                                50 tests
```

## The B2B Campaign Lifecycle Toolkit

Seven tools, one per step of a B2B campaign, from positioning to proving pipeline. Each works on its own; together they cover the whole cycle. All sample data is made up.

| Step | Tool | What it does |
|---|---|---|
| 1. Position | [B2B Product Marketing Agent](https://github.com/rachelhong-marketing/b2b-product-marketing-agent) | Assist the product marketer: draft ideal customer profile hypotheses from deals, target accounts and sales notes, plus persona guides, positioning and messaging pillars backed by approved proof. The product marketer decides. |
| 2. Plan | [B2B Campaign Assistant](https://github.com/rachelhong-marketing/b2b-campaign-assistant) | Turn the positioning into a campaign theme, write the campaign plan and master brief, then draft channel briefs, keywords, landing page and ad copy, all checked before launch. |
| 3. Content | **B2B Content Strategy Assistant** (this repo) | Pick content topics inside the campaign theme from audience questions, news, competitors and keyword data, outline and check each piece so search and AI answer tools can quote it, and log whether AI answers cite you. |
| 4. Set up | [B2B Paid Media Planner](https://github.com/rachelhong-marketing/b2b-paid-media-planner) | Plan channels and retargeting, then build and check tracking links before launch. |
| 5. Test | [B2B Campaign Test Planner](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) | Plan tests in waves, let the ad platform call the winner, check MQLs, and size tests when volume is small. |
| 6. Report | [B2B Campaign Reporting Agent](https://github.com/rachelhong-marketing/b2b-campaign-reporting-agent) | Consolidate ad platform and CRM data into one file, check every channel and funnel stage for gaps, and draft insights. |
| 7. Prove | [B2B Pipeline Attribution Tool](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool) | Check the CRM data can be trusted, then show sourced and influenced pipeline. |

### Which tool is for your role

Teams are organized by function, and the steps cut across them. Start here:

| If you are a... | Start with |
|---|---|
| Product marketer | [1. Product Marketing Agent](https://github.com/rachelhong-marketing/b2b-product-marketing-agent) |
| Demand gen or campaign manager | [2. Campaign Assistant](https://github.com/rachelhong-marketing/b2b-campaign-assistant), [4. Paid Media Planner](https://github.com/rachelhong-marketing/b2b-paid-media-planner), [5. Campaign Test Planner](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) |
| Content marketer | [3. Content Strategy Assistant](https://github.com/rachelhong-marketing/b2b-content-strategy-assistant) |
| Paid media manager | [4. Paid Media Planner](https://github.com/rachelhong-marketing/b2b-paid-media-planner), [5. Campaign Test Planner](https://github.com/rachelhong-marketing/b2b-campaign-test-planner) |
| Marketing operations or analytics | [5. Campaign Test Planner](https://github.com/rachelhong-marketing/b2b-campaign-test-planner), [6. Campaign Reporting Agent](https://github.com/rachelhong-marketing/b2b-campaign-reporting-agent), [7. Pipeline Attribution Tool](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool) |

## About the author

**Rachel Hong** has worked in B2B demand generation and marketing analytics for more than ten years, at marketing and advertising technology companies. She builds campaigns, reporting and the AI workflows that help marketing teams plan and measure them.

[LinkedIn](https://www.linkedin.com/in/rachelhongatbaruch/)

## License

MIT. See `LICENSE`.
