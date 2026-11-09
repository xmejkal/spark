# P399 PR 2: run_scenario.py --dry-run: rows

Card: [P399 #515](https://github.com/xmejkal/spark/issues/515). The plan's rows are in `p399-scenario-ids.md`.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The parser could not move to its own function, because `test_architecture` lets the script hold only `main` | implementation | acted | `ARGUMENTS`, a table at module level, keeps `main` within its ratchet |
| 2 | `dry_run` returns the status and the lines | implementation | acted | `main` only prints, and the plan's `dry_run_lines` became `dry_run` |
| 3 | The counts in a dry run include the wait spark adds for `ready` | implementation | closed | the same as the log, from `ScenarioSteps.line()` |
| 4 | Walk 2's project: exit 0, its counts line as on the card with the log's order, and its 21 files unchanged | run on 2026-11-09 | closed | `step counts: expect-pin 0, set-control 0, wait-serial 1` |
| 5 | A dry run exited 0 for a read-only unnamed `wokwi.toml`, an image name with no folder or that is a folder, and a file with no name and no marker, where a real run fails | PR refuter | acted | `image_in` refuses all of them, so the free checks are the same on both paths. The missing-folder crash was older than this card |
| 6 | The `try` around `write_image_name` in `run()` | implementation | closed | removed, because `image_in` now refuses a read-only file first |
| 7 | README's Simulate note changed, and `tools/journey.py` did not | PR refuter | acted | the note and the picture changed together |
| 8 | `ARGUMENTS` could be a `build_parser()` function | PR reviewer | rejected | `test_architecture` lets the script hold only `main` |
| 9 | The module docstring said this names the image, with no word on `--dry-run` | PR reviewer | acted | it says a real run names it, and describes `--dry-run` |
