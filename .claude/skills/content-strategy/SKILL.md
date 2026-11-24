---
name: content-strategy-assistant
description: B2B content strategy from topic to published piece. Finds topics inside a campaign theme (audience questions, trade news, competitor activity, keyword data), ranks them by funnel stage (top, middle, bottom), turns a chosen idea into a writing brief, helps write the piece in the brand voice, and checks it for answer engine optimization (AEO) and generative engine optimization (GEO) so search features and AI tools can quote and cite it. Use when someone wants blog or ebook topics, a content brainstorm, a competitor content check, SEO gaps, a draft written, or a draft checked for AI search.
---

# Content Strategy Assistant

Step 3 of the B2B Campaign Lifecycle Toolkit. It comes after the campaign assistant (theme, plan, master brief) and before paid media. You do the thinking and the writing in the brand's voice. The Python tool in this repo does the counting and the checking.

## Funnel stages (spell these out for the user)
- **Top of funnel (TOFU):** the reader is learning about a problem.
- **Middle of funnel (MOFU):** the reader is comparing options or approaches.
- **Bottom of funnel (BOFU):** the reader is close to choosing and needs proof or a next step.

## Part 1: Find topics

1. **Read the brand profile** (`sample-data/brand/brand-profile.json` is the template). Fill the `campaign` block from the campaign assistant's master brief (name, theme, audience, pillars, which themes it covers). If there is no campaign yet, say so and suggest running step 2 first; the tool still works without one. If the user has brand material, help draft the profile and show it for approval.
2. **Gather data. Never log in to anything, never bypass a paywall, never copy full articles.**
   - Trade publications and competitors: feeds and sitemaps. `python3 -m contentstrategy collect <config.json>` downloads them slowly and obeys robots.txt. Ask the user first, and tell them to check each site's terms.
   - Reddit, LinkedIn, Quora, G2: the user exports or pastes posts into a CSV (source, title, text, url, date, engagement). Only titles and short excerpts are used.
   - Keywords: the user exports from Google Ads Keyword Planner, Semrush and Google Trends. Use the numbers exactly as exported.
3. **Run it:** `python3 -m contentstrategy mine --data <folder> --out output/topic-brief.md`
4. **Add judgment.** Read the brief. For the top themes, link them to the campaign pillars and write one angle per funnel stage in the brand's voice. Flag ideas that conflict with the brand's tone, product claims or legal rules. Say which ideas are weak signals (one source type, or no keyword data), and which sit outside the campaign theme.
5. **Check it:** `python3 -m contentstrategy check output/topic-brief.md --brand <brand-profile.json>`

## Part 2: Write one piece

1. The user picks an idea. **Outline it:** `python3 -m contentstrategy outline --data <folder> --idea "<text>" --out-dir output/drafts`
2. **Fill every [MISSING] slot.** Rules for the draft:
   - Open with a direct answer of 20 to 70 words. Answer the question before anything else.
   - Use question headings. Start each section with a 15 to 70 word answer, then the detail.
   - Include a FAQ with at least 3 questions, each answered in 80 words or fewer.
   - Name and link at least 2 outside sources. Add one original element only the user can supply (their data, a customer example, a decision rule). Ask for it. Never invent a number, quote or customer.
   - Use a list or table where it helps. Use a real author name and real dates.
   - Spell out every acronym on first use. Use the brand and product names the same way every time. Follow the brand voice and avoid list.
   - Delete the "Writer's notes" block before publishing.
3. **Check it:** `python3 -m contentstrategy aeo-check <draft> --brand <brand-profile.json> --as-of <today>`. Fix every FAIL. Look at every WARN and decide. Run it again.
4. **Structured data:** `python3 -m contentstrategy schema <draft> --brand <brand-profile.json> --out <draft>.schema.json`. Tell the user to paste it into the page inside a script tag of type application/ld+json, and to correct the page address if the guessed one is wrong.
5. Show the whole updated draft after any change, not only the changed part.

## Part 3: Measure AI citations (monthly, manual)

- `python3 -m contentstrategy citation-sheet --data <folder>` adds the top buyer questions to `state/ai-citation-log.csv`, one row per AI tool.
- The user asks each question in each tool, then fills in `our_site_cited` (yes, mentioned, or no), `competitors_cited` and `date_tested`. Do not fill these in yourself and do not guess.
- `python3 -m contentstrategy citation-report --data <folder>` counts the results. Say plainly when there are too few tests to compare.

## Rules
- Every idea needs its evidence next to it: a link, or keyword data with its source. If something is missing, write [MISSING]. Never invent a volume, difficulty, ranking, citation or quote.
- AEO and GEO checks are common recommendations, not published rules. Never promise a ranking or a citation.
- Competitor activity is public information only. Do not copy their content. Use it to find gaps and angles.
- Scores compare ideas within one run. Do not present them as forecasts.
- Keep the user's own tone rules (words to avoid, plain language). Sound human, not polished.

## Weekly agent
For a recurring run, use the `content-strategy-assistant` agent (`.claude/agents/content-strategy-assistant.md`) and `python3 -m contentstrategy weekly --data <folder>`. It saves a what-changed note, remembers the last run in `<folder>/state/`, hides ideas listed in `state/chosen-topics.csv`, and adds the citation tally when the log has results.
