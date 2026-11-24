# P1092: a flash that does not finish writes a board log, and the flow says the board may be erased: rows

Card: [P1092 #1603](https://github.com/xmejkal/spark/issues/1603), a story. New logic: a plan, a plan council (one lens
on Sonnet, the refuter on Opus) and a second round (the refuter on Opus), then the build. This file holds the acted and
raised findings only (rules.md). 2026-11-24.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | F1: the new verdict must never reach main without the flow part, whose reader on main says "files read back" for it | plan council | acted | one PR: the bench part was built and pushed first, the flow part after P1062 merged, and the PR opened only then |
| 2 | F2: the log write never hides the flash's error | plan council | acted | `.get(reason, str(failed))`, `encoding="utf-8"`, `except (OSError, ValueError)`; a test for each: a folder that is a file, a writer that raises ValueError |
| 3 | F3: the `grant_ended` log sentence must not say "before the erase": the first erase ran | plan council | acted | "the yes ended before the erase's retry"; a test reads it in the log |
| 4 | F5: test 1 runs a failed erase and a failed write after a good erase | plan council | acted | two tests in `TheFlashNotFinishedTest` |
| 5 | F6: each mutation anchor occurs exactly once | plan council | acted | `--anchors`: 33 refused on the branch, the same 33 as on main |
| 6 | F7: the `board log:` line is a say() line, so three goldens change | plan council | acted | `deploy-could-not-run-flash-failed-grant.txt`, `.json` and `.json.stderr`; `.txt.stderr` is unchanged |
| 7 | F8 (1): a deploy that stops in the flash loop for another reason (a crash, Ctrl-C during esptool) writes no board log | plan council | raised | P1096 #1614. Every FlashError now writes the log, so `no_terminal` at the retry gets one too, with no cause (the builder's choice: the `.get` of F2 serves it; a test) |
| 8 | F8 (2): the look's "last deploy" sentence reads the store record, so it names the last finished deploy on a board that may be erased | plan council | raised | P1097 #1615 |
| 9 | F10: the log's name has second resolution, so a failed flash and a deploy in the same second write one file | plan council | acted | said in the PR body |
| 10 | F11: the log sentences live in `NOT_FINISHED_SENTENCES`, and `board_codes.CODES` stays as it is | second round | acted | `deploy_service.NOT_FINISHED_SENTENCES` |
| 11 | F12: row 3's mutant is `except KeyError`, and the ValueError test injects a log writer, with no `mock.patch` | second round | acted | `DeployService.write_log`, a class attribute that a test sets on the instance, so `__init__` keeps five parameters (R3) |
| 12 | F13: a TypeError or KeyError in the log write replaces the FlashError, on purpose | second round | acted | the docstring of `log_not_finished` says so; a test checks the `__context__` |
| 13 | F15: `data.image_sha256` is filled beside `data.board_log` | second round | acted | `reached["image_sha256"]`, its own row; the `.json` golden changes in two keys |
| 14 | the envelope's change refused row "the envelope names no image" of `p213b1-deploy-command.json` | the builder's `--anchors` | acted | re-anchored in place on the new line, with the same mutant |
| 15 | F4: the NOW adds "The board log says what failed.", as the problems NOW does | plan council | acted | `DEPLOY_NOT_FINISHED_NOW`; test 6 reads it |
| 16 | F14: the bench part's goldens do not change again after P1062 merges | second round | acted | after the merge of origin/main, `test_golden_bench` passes with no new golden |
| 17 | the plan's `read_back_of` (`in (SEEN, NOT_SEEN)`, else the cause) gives null for a not-finished log with no cause, as `no_terminal` at the retry, while its words say "nothing read back" | the builder | acted | `read_back_of` returns false for the verdict first; row #19 of `p1043-deploy-reader.json` keeps its line, so it needs no re-anchor, and a P1092 row guards the new line |
| 18 | test 11 belongs beside P1062's own `deployed_line` tests | the builder | acted | it is in `test_flow.TheDeployedLineTest`, not in `test_flow_page.py` |
