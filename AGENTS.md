# spark — for AI agents

spark is a Claude Code plugin for gadgets built from an ESP32 dev board and modules. From a requirements file it
generates a board that builds, with a Wokwi diagram generated from it (kept only with `--sim-dir`,
[P116](https://github.com/xmejkal/spark/issues/50)), and checks the board. Nothing yet writes the requirements file
from a vague idea with no parts named ([P76](https://github.com/xmejkal/spark/issues/5)), and no simulation runs unless
you run one. [What works today](README.md#what-works-today) gives each step's status.

**If you are an AI agent using spark, read [`docs/guide/agents.md`](docs/guide/agents.md) first.** It covers:

- the commands in Claude Code, and the scripts anywhere else;
- their JSON and exit codes;
- what never to assume. A `could-not-run` or a `skipped` is not a pass, and a `null` is not a value to fill in.

The rules under what never to assume apply to any work in this repository. To change spark itself, read
[`docs/guide/developing.md`](docs/guide/developing.md).
