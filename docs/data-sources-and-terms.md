# Where the data comes from, and what each source allows

Check each site's terms yourself before you collect anything. The notes below say how this tool is designed, not what is legal for you.

| Source | How you get it | What the tool uses | Notes |
|---|---|---|---|
| Trade publications (for example advertising and marketing news sites) | Their public feeds (RSS or Atom) | Headline, date, link, a short summary | Many articles are behind paywalls. The tool never reads full text. |
| Competitor websites | Their feeds or sitemaps | Page title (or a title guessed from the address), date, link | Compared with the last run to show what is new. Public information only. |
| Reddit | Export or paste posts and questions into a CSV | Title, short excerpt, date, link, an engagement number you trust | Reddit has an official programme with its own terms. |
| LinkedIn, Quora, G2 | You export or paste into a CSV | Same columns | These sites generally restrict automated collection, so the tool never reaches them. |
| Google Ads Keyword Planner | Export the keyword ideas as CSV | Monthly searches, competition, top-of-page bid | Volumes can be ranges such as "1K - 10K". The lower end is used. |
| Semrush | Export keywords as CSV | Volume, keyword difficulty, cost per click, your position and page | When two exports give a volume, the larger is used and both sources are named. |
| Your own analytics | Export your published pieces as CSV: `url, title, stage, publish_date, visits, conversions, promotion_spend, channel` | Visits, conversions, paid promotion | Your own data. Remove anything personal. Judged against your other pieces at the same funnel stage. |
| Google Trends | Export a term over time as CSV | Direction: up, flat or down (last third compared with first third) | Needs at least six data points per term. |

## Community CSV columns
`source,title,text,url,date,engagement`. Engagement is any number you trust: upvotes, reactions, helpful votes, comment counts. Rows with no engagement score low, so add a number if a post matters (for example the helpful-vote count on a G2 review).

## What is never done
- No logging in, no cookies, no bypassing paywalls.
- No storing full articles. Titles and short excerpts only.
- No guessing volumes, rankings or quotes. Gaps are marked [MISSING].
- `collect` obeys robots.txt, waits between requests and reads only the feeds and sitemaps you list. It has been tested with a stand-in fetcher, not against live sites.
