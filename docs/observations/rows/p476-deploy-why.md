# P476 each deploy stage says why: rows

When each of the five deploy stages starts, `deploy.py` prints one `why:` line from `PHASE_WHY` (`deploy_stages.py`). A small
Decorator, `WhyLineReporter` (`deploy_image.py`), adds it inside `StageTrackingReporter`. Card:
[P476 #652](https://github.com/xmejkal/spark/issues/652). Rows 1 to 3 are the refuter's plan check (Opus).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | four of the five sentences did not match the code | plan refuter | acted | the plan holds the corrected sentences, and `PHASE_WHY` uses them word for word |
| 2 | three exact test pins are missed: `test_deploy.py:118` and `:300`, `test_deploy_gate.py:413` | plan refuter | acted | all three hold the why lines, and the pin of a ready deploy in `test_deploy_gate.py` lists five |
| 3 | the docs that state what deploy prints: `deploy.py:3` and its `--help`, `commands/deploy.md`, `journey/bench.md`, `agents/json.md`, `deploy_image.py:4` | plan refuter | acted | each says the `why:` line; `deploy_image.py:4` no longer says "no golden changed" |
| 4 | exactly five BEGINs pass through the tracker, so a retry prints no second why | plan refuter | verified | a retry is a LINE, not a BEGIN |
| 5 | under `--json` every `.json` golden of a deploy keeps its stdout | build | verified | `SPARK_ACCEPT=deploy` added 17 `why:` lines in five files (`.txt`, `.stderr`) and changed no `.json` stdout |
| 6 | a refusal in the plan or the look prints only the whys of the stages it began | build | verified | `test_a_scenario_that_failed...` pins the plan's why alone, `test_no_board_on_usb...` pins plan and look |
