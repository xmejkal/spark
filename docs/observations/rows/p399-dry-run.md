# P399 PR 2: run_scenario.py --dry-run: rows

Card: [P399 #515](https://github.com/xmejkal/spark/issues/515). The plan's rows are in `p399-scenario-ids.md`.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The parser could not move to its own function, because `test_architecture` lets the script hold only `main` | implementation | acted | `ARGUMENTS`, a table at module level, keeps `main` within its ratchet |
| 2 | `dry_run` returns the status and the lines | implementation | acted | `main` only prints, and the plan's `dry_run_lines` became `dry_run` |
| 3 | The counts in a dry run include the wait spark adds for `ready` | implementation | closed | the same as the log, from `ScenarioSteps.line()` |
| 4 | Walk 2's project: exit 0, its counts line as on the card with the log's order, and its 21 files unchanged | run on 2026-11-09 | closed | `step counts: expect-pin 0, set-control 0, wait-serial 1` |
