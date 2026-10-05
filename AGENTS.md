# spark — for AI agents

spark is a Claude Code plugin that takes a gadget built from an ESP32 dev board and modules from an idea to a board
that builds, simulates and is checked.

**If you are an AI agent using spark, read [`docs/guide/agents.md`](docs/guide/agents.md) first.** It covers:

- the commands in Claude Code, and the scripts anywhere else;
- their JSON and exit codes;
- what never to assume. A `could-not-run` or a `skipped` is not a pass, and a `null` is not a value to fill in.

The rules there hold here. To change spark itself, read [`docs/guide/developing.md`](docs/guide/developing.md).
