# Agent spec: content strategy agent

| Part | Decision |
|---|---|
| Role | Finds content topics inside the campaign theme and explains the evidence. On request, outlines a chosen idea, drafts in the brand voice from facts the user supplies, and checks the draft for answer engine optimization (AEO) and generative engine optimization (GEO). Never publishes. |
| Tools | Read, Write, Bash (runs `python3 -m contentstrategy`), Glob, Grep. No web login, no posting, no email. |
| Input | A private data folder: brand profile (with the campaign block), trade and competitor feeds, community CSV exports, keyword exports, content performance export, `state/`. |
| Workflow | Collect (optional) → mine → compare with last run → check → short summary. Command: `python3 -m contentstrategy weekly`. |
| Memory | `state/last-run.json` (theme scores, top ideas, date), `state/chosen-topics.csv` (ideas already picked) and `state/ai-citation-log.csv` (manual AI citation tests). |
| Output | `<date>-topic-brief.md` (ranked ideas by funnel stage), `<date>-what-changed.md` (what moved since last run, plus the AI citation tally), and on request a writing brief, an `aeo-check` result and structured data. |
| Scoring | Seven factors: campaign relevance 25%, past performance 25%, search demand 25%, ranking ease 5%, audience signal 10%, trend and freshness 5%, competitor gap 5%. Missing factors are left out and shown. |
| Guardrails | Public data only; exports for LinkedIn, Quora, G2; robots.txt obeyed; no invented numbers; nothing published or sent. |
| Error handling | One failed source never stops the run. Failures are listed at the top of the note. A failed brief writes a "Weekly run failed" note and exits with code 1. |
| Human steps | Export from LinkedIn, Quora, G2 and keyword tools; choose topics; supply the original angle and real numbers; approve the draft; publish; run the monthly AI citation tests by hand. |

## Three ways to use it
1. **Skill:** ask Claude Code "mine topics from this data folder". Uses `.claude/skills/content-strategy/SKILL.md`.
2. **Agent:** `.claude/agents/content-strategy-assistant.md`, plus a scheduled task using `prompts/weekly-run.md`.
3. **Copilot:** `copilot/agent-instructions.md`. Copilot cannot run Python or fetch feeds, so you paste the brief in and it does the judgment work only.
