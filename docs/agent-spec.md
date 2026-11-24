# Agent spec: weekly topic miner

| Part | Decision |
|---|---|
| Role | Research assistant that finds content topics and explains the evidence. Does not write final articles. |
| Tools | Read, Write, Bash (runs `python3 -m topicminer`), Glob, Grep. No web login, no posting, no email. |
| Input | A private data folder: brand profile, trade and competitor feeds, community CSV exports, keyword exports, `state/`. |
| Workflow | Collect (optional) → mine → compare with last run → check → short summary. Command: `python3 -m topicminer weekly`. |
| Memory | `state/last-run.json` (theme scores, top ideas, date) and `state/chosen-topics.csv` (ideas already picked). |
| Output | `<date>-topic-brief.md` (ranked ideas by funnel stage) and `<date>-what-changed.md` (what moved since last run). |
| Guardrails | Public data only; exports for LinkedIn, Quora, G2; robots.txt obeyed; no invented numbers; nothing published or sent. |
| Error handling | One failed source never stops the run. Failures are listed at the top of the note. A failed brief writes a "Weekly run failed" note and exits with code 1. |
| Human steps | Export from LinkedIn, Quora, G2 and keyword tools; choose topics; write in the brand's voice; approve the brand profile. |

## Three ways to use it
1. **Skill:** ask Claude Code "mine topics from this data folder". Uses `.claude/skills/topic-miner/SKILL.md`.
2. **Agent:** `.claude/agents/topic-miner.md`, plus a scheduled task using `prompts/weekly-run.md`.
3. **Copilot:** `copilot/agent-instructions.md`. Copilot cannot run Python or fetch feeds, so you paste the brief in and it does the judgment work only.
