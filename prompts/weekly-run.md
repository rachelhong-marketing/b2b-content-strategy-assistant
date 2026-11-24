# Weekly run prompt

Paste this into a scheduled task (Claude desktop app scheduled tasks, or any scheduler that can start Claude Code). Replace the two paths.

```
Use the content-strategy-assistant agent. Data folder: /path/to/your/private-data. Collect config: /path/to/your/private-data/collect-config.json.
Run the weekly run, then give me: what changed since last week, the 3 best new ideas with evidence, anything with weak evidence, and what I need to export by hand this week.
If the citation log has results, add the tally. Do not publish or send anything.
```

Notes
- Scheduled tasks only run while the computer and the app are open. If the run is missed, run it by hand.
- Keep your data folder private. Do not commit it to the public repo.
- The agent cannot export from LinkedIn, Quora, G2 or keyword tools. Drop the new exports into the data folder before the run.
