# P476 each deploy stage says why: rows

When each of the five deploy stages starts, `deploy.py` prints one `why:` line from `PHASE_WHY` (`deploy_stages.py`). A small
Decorator, `WhyLineReporter` (`deploy_image.py`), adds it inside `StageTrackingReporter`. Card:
[P476 #652](https://github.com/xmejkal/spark/issues/652). Rows 1 to 4 are the refuter's plan check (Opus); rows 7 to 12 are the review's.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | four of the five sentences did not match the code | plan refuter | acted | the plan holds the corrected sentences, and `PHASE_WHY` uses them word for word |
| 2 | three exact test pins are missed: `test_deploy.py:118` and `:300`, `test_deploy_gate.py:413` | plan refuter | acted | all three hold the why lines, and the pin of a ready deploy in `test_deploy_gate.py` lists five |
| 3 | the docs that state what deploy prints: `deploy.py:3` and its `--help`, `commands/deploy.md`, `journey/bench.md`, `agents/json.md`, `deploy_image.py:4` | plan refuter | acted | each says the `why:` line; `deploy_image.py:4` no longer says "no golden changed" |
| 4 | exactly five BEGINs pass through the tracker, so a retry prints no second why | plan refuter | verified | a retry is a LINE, not a BEGIN; the golden `deploy-could-not-run-flash-failed-grant` covers the retry and holds one flash why |
| 5 | under `--json` every `.json` golden of a deploy keeps its stdout | build | verified | `SPARK_ACCEPT=deploy` added 17 `why:` lines in five files (`.txt`, `.stderr`) and changed no `.json` stdout |
| 6 | a refusal in the plan or the look prints only the whys of the stages it began | build | verified | `test_a_scenario_that_failed...` pins the plan's why alone, `test_no_board_on_usb...` pins plan and look |
| 7 | `tests.test_map.TheCommittedMapTest` fails: `docs/guide/map.md` is stale | review | acted | `python3 tools/map.py --write`, committed |
| 8 | the look sentence said "the board's record", but the look reads the chip and flash size from the board | review | acted | the look sentence is now "spark reads the chip and flash size, so another chip or too little flash for the image is stopped" |
| 9 | the flash sentence named the C6 as a chip with no watchdog reset, which the code does not state | review | acted | the flash sentence says "with its watchdog where it has one" |
| 10 | the flash test checked "plain reset", a phrase of the dropped sentence | review | acted | the test is `test_the_flash_line_names_the_watchdog_restart` and checks "restarts the chip with its watchdog"; the mutation row "the flash why loses the watchdog" now plants "where it has one" and that test catches it |
| 11 | `commands/deploy.md` and `journey/bench.md` said the dry run prints the esptool commands, but it prints the plan's why first | review | acted | both say the plan's `why:` line first, then the esptool commands |
| 12 | the `why:` sentence opened the `--help` epilog, ahead of the safety rule | review | acted | it is the last paragraph of the epilog |
