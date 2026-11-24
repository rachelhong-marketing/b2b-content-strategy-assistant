# Copilot setup guide

1. In Microsoft Copilot Studio (or a Copilot agent builder), create a new agent named "Content topic reviewer".
2. Paste the text of `agent-instructions.md` into the instructions box.
3. Turn off web search and any connectors you do not need.
4. Each week: run the miner on your computer (Claude Code skill or agent), then paste `<date>-topic-brief.md` into the Copilot chat.
5. Test with `docs/example-topic-brief.md`: the agent should return 3 themes with one idea per funnel stage and keep every [MISSING] label.

What Copilot cannot do: run the Python tool, fetch feeds, remember last week's run. Use Claude Code for those parts.
