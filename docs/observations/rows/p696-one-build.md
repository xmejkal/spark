# P696: a run_scenario.py run builds the flash image once: rows

Card: [P696 #939](https://github.com/xmejkal/spark/issues/939), a bug (time, not output) under #94 (v0.13, one core), found by P685's
whole-branch review. Plan `~/.claude/plans/p696-one-build.md` (XS: one plan check on Sonnet, one PR refuter on Fable). This file
holds the acted, raised and rejected findings only (rules.md). 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a plain `start()` that returns the free checks' lines with the result prints them after the paid run; a person reads them late and a crash in the run loses them | plan check | acted | `start(say)`: `say` gets the lines before the run; `main`'s `say` prints them to stderr as before |
| 2 | a None sentence as the "refused before the run" signal is a null used as a value (never-assume) | plan check | acted | `StartResult(status, sentence, log, ran)`, a Result Value; `main` tests `ran` |
| 3 | `p130-wokwi-harness.json:101`'s bare find `self.log.unlink(missing_ok=True)` occurs twice once `start()` has its own unlink, and `mutate.py` refuses a find that is not unique; the plan named `:155` alone | plan check | acted | `:101` gains `run()`'s comment, `:155` is re-aimed on `start()`'s line with its own comment; `--anchors`: 3170 mutation(s) in 269 table(s), every anchor present, once |
| 4 | `run()` kept for the tests has nine callers (`test_run_scenario.py:398, 442, 541, 807, 864`, `golden_bench.py:155`, `test_journey_basic.py:267`, `test_deploy.py:96, 180`) | plan check | acted | its docstring says it is the tests' door and `start` the command's |
| 5 | `areas/firmware.md:60-70` and `:105-120` describe the target architecture (`run(engine)`, an engine Strategy), not today's code; adding `start`/`simulate` there is a design claim | plan check | rejected | dropped because the page is the target; nothing added |
| 6 | the `command()` helper built its `FakeToolFinder` in a local and kept nothing on `self` | plan check | acted | `self.finder` |
| 7 | the plan's line cites for `run` and `free_checks` were off (`:177-181`, `:231-236`) | plan check | acted | the plan |
| 8 | the count: a command asked the finder `littlefs` twice (one ask per build); the new test was red at two and is green at one | build | closed | `test_a_command_builds_the_image_once` |
| 9 | the four run-scenario goldens are byte-equal | build | closed | `tests.test_golden_firmware` OK, `git status --short tests/golden-firmware` empty |
| 10 | no step's status moves: the README's journey table and `tools/journey.py` stay | build | closed | nothing to edit |
