# P478: deploy.py's text view, slice 2 (the spinner under deploy's silent waits): rows

Card: [P478 #656](https://github.com/xmejkal/spark/issues/656). Two plan rounds (round 1: the everyday-model lens and the
refuter; round 2: the refuter), then the build of slice 2. This file holds the acted, raised and rejected findings only
(rules.md). 2026-11-25.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `Event.wait` copied `Event.line`'s guard, so p507's anchor occurred twice | plan round 1, refuter 1 | acted | one guard, `Event._with_text`, whose TypeError names the kind. The anchor occurs once |
| 2 | One more line in `DeployService.verify` breaks R1 (40 lines) | plan round 1, refuter 2, lens 1 | acted | the WAIT is in `DeployFlowService.verify`, after BEGIN(`verify`) |
| 3 | Four test_board_start tests assert every event | plan round 1, refuter 3 | acted | named, with the RESET wait's line asserted at its start and after each not-counted line |
| 4 | A Ctrl-C during `join()` let a tick draw after the erase | plan round 1, refuter 4 | acted | `ThreadTicker.stop` joins whenever it holds a thread. test_spinner's interrupted-stop test, its mutation row |
| 5 | Test 13 had no way to inject a fake without a patch | plan round 1, refuter 5, lens 5 | acted | the outside builder sets `reporter.spinner`, a plain attribute |
| 6 | Test 12's NO_COLOR case decides Q2 early | plan round 1, refuter 6 | acted | marked Q2's (decided by the auto-mode council, delegated, the PO's to change) |
| 7 | `reading the board` and RESTART_NOTICE say the same read twice | plan round 1, refuter 7 | raised | P1052 #1544, the person words (RESTART_NOTICE is look.py's shared line) |
| 8 | The changed test's input `"end"` is P793's coming kind | plan round 1, lens 2 | acted | `"other"` |
| 9 | No golden test pins "no `\r`" under FORCE_COLOR | plan round 1, lens 3 | acted | test_view_reporter.TheSpinnerChoiceTest pins it on a pipe with FORCE_COLOR=1, and the claim is dropped |
| 10 | The pipe's text is not byte-equal | plan round 1, lens 4 | acted | said in the plan and the PR body: three `.txt` goldens gain four lines, no `.json` or `.stderr` golden changes |
| 11 | Three "line" words for the moving part | plan round 1, lens 7 | acted | round 2 named it the spinner (row 15) |
| 12 | `FakeLiveLine` is not needed | plan round 1, lens 8 | acted | dropped. The view's tests read the stream of a `TerminalSpinner` over `FakeTicker` |
| 13 | The plan said this Mac has no rich, from `python3 -I` | spark-main, the tech lead | acted | rich 15.0.0 imports without `-I`, as deploy.py runs. Q1 closed with no install |
| 14 | The plan said esptool shows its own progress during the erase | the tech lead | acted | one static line (esptool/cmds.py:2311-2321). D13's reason is corrected, and Q3 is decided: no slice 3 |
| 15 | "live" already means the bench's live try and grant, and "row" a port row in `wait_for_start` | plan round 2, refuter 1 | acted | `Spinner`, `NO_SPINNER`, `TerminalSpinner`, `core/spinner.py`, the role `spinner`; the word is in patterns-and-names.md |
| 16 | Nothing pins that `TerminalSpinner.stop` stops the ticker again after a stop that a Ctrl-C cut | plan round 2, refuter 2 | acted | `stop` always calls `ticker.stop()`; a test whose FakeTicker raises KeyboardInterrupt once, and a row with the spinner's own flag as the mutant |
| 17 | Python 3.10.0's join can hang after a Ctrl-C at the wrong moment (bpo-45274) | plan round 2, refuter 3 | acted | named in the PR's Risk 2; no time limit on the join (not reproduced in 200 trials) |
| 18 | A test that reads a constant as `module.NAME` fails test_self_confirmation | plan round 2, refuter 4 | acted | the tests assert literals |
| 19 | Text fixes: `DeployFlowService.verify`, test 14 through the flow, rows with context, two import lines change | plan round 2, refuter 5 | acted | test_deploy_json.TheWaitsTest runs the whole deploy; the rows' finds carry their comments, so each occurs once |
| 20 | `FakeTicker(interrupt=True)` raised at `start`, which stops the old ticker first | build | acted | a test sets `interrupt` after the start; `start` still always stops the old ticker, so no thread leaks |
| 21 | The plan put the wait's sentence in both deploy.py's EPILOG and `DETAILS` | build | rejected | dropped because both print in one `--help`, so the sentence would show twice; the EPILOG holds the text view's paragraph |
