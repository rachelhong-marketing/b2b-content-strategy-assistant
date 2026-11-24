---
name: topic-miner
description: Find content topics worth writing about. Combines audience questions (Reddit, LinkedIn, Quora, G2 exports), industry news feeds, competitor activity and keyword data (Google Ads Keyword Planner, Semrush, Google Trends) with the brand's own voice and themes, then ranks topic ideas by funnel stage (top, middle, bottom). Use when someone wants blog or ebook topics, a content brainstorm, a competitor content check, or SEO gaps in their content.
---

# Topic Miner

Turns evidence into a ranked list of content topics by funnel stage. You do the thinking and the writing in the brand's voice. The Python tool in this repo does the counting.

## Funnel stages (spell these out for the user)
- **Top of funnel (TOFU):** the reader is learning about a problem.
- **Middle of funnel (MOFU):** the reader is comparing options or approaches.
- **Bottom of funnel (BOFU):** the reader is close to choosing and needs proof or a next step.

## Steps

1. **Read the brand profile** (`sample-data/brand/brand-profile.json` is the template). If the user has brand material (narrative, messaging pillars, product pages, content strategy, tone), help draft the profile from it: audiences, 4 to 8 themes with trigger phrases and a fit score, words to avoid, the domain, and competitors. Show it for approval.
2. **Gather data. Never log in to anything, never bypass a paywall, never copy full articles.**
   - Trade publications and competitors: feeds and sitemaps. `python3 -m topicminer collect <config.json>` downloads them slowly and obeys robots.txt. Ask the user first, and tell them to check each site's terms.
   - Reddit, LinkedIn, Quora, G2: the user exports or pastes posts into a CSV (source, title, text, url, date, engagement). Only titles and short excerpts are used.
   - Keywords: the user exports from Google Ads Keyword Planner, Semrush and Google Trends. Use the numbers exactly as exported.
3. **Run the miner:** `python3 -m topicminer mine --data <folder> --out output/topic-brief.md`
4. **Add judgment.** Read the brief. For the top themes, link them to the brand's messaging pillars and write one angle per funnel stage in the brand's voice. Flag ideas that conflict with the brand's tone, product claims or legal rules. Say which ideas are weak signals (one source type, or no keyword data).
5. **Check it:** `python3 -m topicminer check output/topic-brief.md --brand <brand-profile.json>`
6. **Hand over** a short brainstorm agenda: 2 or 3 themes, one idea per stage each, one ebook or pillar candidate, and the SEO fixes (page-two pages to refresh, themes with demand and no page).

## Weekly agent
For a recurring run, use the `topic-miner` agent (`.claude/agents/topic-miner.md`) and `python3 -m topicminer weekly --data <folder>`. It saves a what-changed note, remembers last run in `<folder>/state/`, and hides ideas listed in `state/chosen-topics.csv`.

## Rules
- Every idea needs its evidence next to it: a link, or keyword data with its source. If something is missing, write [MISSING]. Never invent a volume, difficulty, ranking or quote.
- Competitor activity is public information only. Do not copy their content. Use it to find gaps and angles.
- Scores compare ideas within one run. Do not present them as forecasts.
- When the user asks for a change, show the whole updated brief, not only the changed part.
- Keep the user's own tone rules (words to avoid, plain language). Spell out every acronym on first use.
