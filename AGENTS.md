# spark — for AI agents

spark is a Claude Code plugin for gadgets built from an ESP32 dev board and modules. From a requirements file it
generates a board that builds, with a breadboard sheet, the pin map the firmware imports and a Wokwi diagram generated from it (each kept with
`--keep`, [P116](https://github.com/xmejkal/spark/issues/50), [P196](https://github.com/xmejkal/spark/issues/155)), and checks the board. `parts.py --requirements` writes the
requirements file from the parts picked for a goal's needs ([P97](https://github.com/xmejkal/spark/issues/18)), and no
simulation runs unless you run one. [What works today](README.md#what-works-today) gives each step's status.

**If you are an AI agent using spark, read [`docs/guide/agents.md`](docs/guide/agents.md) first.** It covers:

- the commands in Claude Code, and the scripts anywhere else;
- their JSON and exit codes;
- what never to assume. A `could-not-run` or a `skipped` is not a pass, and a `null` is not a value to fill in.

The rules under what never to assume apply to any work in this repository. To change spark itself, read
[`docs/guide/developing.md`](docs/guide/developing.md).

## Principles for changing spark

These are the PO's standing rules for work on spark itself. Where a decision is written down, its bullet links to it.

- Judge a change by one bar: does it move a basic project closer to a breadboard with working firmware? Every stage
  hands over to the next. Pause tooling that does not serve this bar. Measure progress by walking a real project end
  to end ([P100](https://github.com/xmejkal/spark/issues/6)).
- Spark exports facts, never behaviour. It writes only what it derives from a record it holds, and never thresholds,
  timings, state tables or drivers. The conversation writes the firmware ([the firmware decision](docs/archive/2026-10-01-firmware-and-tests.md)).
- One core, many interfaces. New code is a small class with one job in a library module, and `main()` only parses
  arguments and prints. The CLI (with `--json`), the agents and MCP call that code. An agent prompt never repeats
  its logic. When a fix touches a script, take the small refactor toward this shape if it makes the code simpler.
  The whole-repository change waits for [v2, #94](https://github.com/xmejkal/spark/issues/94).
- Records grow by need. A property enters when a check, a stage or the PO needs it, with its origin. Prefer checks
  that read facts in records to logic written per part ([P94](https://github.com/xmejkal/spark/issues/17)).
- Free, few and local. Use only free tools, one tool per job, and a local CLI before a web service or an MCP server.
  A spark setting lets a person switch a tool to its MCP version. A user installs nothing heavy, so KiCad stays
  optional. Name any cost and ask first.
- Spark is public, under MIT. Never commit a vendor file, because installing spark copies the whole repository.
  Never commit a home path or a photo with GPS data. Cite a source by its URL, printed version, page and sha256
  ([keeping sources](docs/archive/2026-10-01-keeping-sources.md)).
- Spark is the product. A spark change does not update the demo projects or regenerate the examples. Offer that to
  the PO after an epic. A fixture that tests spark is part of the change.
- Plans shrink with distance. Only Ready and the next slice are refined in detail. A later version is one epic with
  the PO's words and one sentence that says when it is done.
- Keep the journey current. A change to a step's status, note or date updates the README's "What works today"
  table and `tools/journey.py`'s picture in the same PR. `tests/test_journey.py` fails on a stale picture. The team
  also updates its Miro journey board in that PR.
