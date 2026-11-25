# P1057 PR 2 and P1055: an unnamed port's asleep fix, and `fix` on the line of grant, live and reach: rows

Cards: [P1057 #1554](https://github.com/xmejkal/spark/issues/1554) (slice 2) and [P1055 #1552](https://github.com/xmejkal/spark/issues/1552).
The plan was written on main 142656a9 on 2026-11-25 and had two council rounds: round 1 (the everyday lens on Sonnet, the
architecture lens and the refuter on Opus) and round 2 (one refuter on Opus, who built the plan in a scratch worktree).
The PO approved it on 2026-11-25: O1 "found", O2 null, O3 to O5 as recommended. This file holds the acted, raised and
rejected findings only. The PR review's rows follow the councils' in the same table.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | R1: nine key pins change, not four | council round 1, refuter | acted | test_grant.py :387, :391, :415, :431, test_live.py :90, :127, test_reach.py :96, test_json_contracts.py :258 and test_board_questions.py :387 gain `fix`, named in the P1055 commit. `tests.test_board_questions` joined the pre-push list |
| 2 | R2: the goldens cannot be accepted before the renderer exists | council round 1, refuter | acted | each card's tests and code are one commit; the seven goldens were written after the renderer and each gains only `"fix": null` |
| 3 | R3: the doctor roads of live and reach give no look step in `next` | council round 1, refuter | acted | both pass `next=board_envelope.asleep_next(fix, project.resolve())`. Rows 12 and 13 of `tests/mutations/p1055-asleep-json.json` |
| 4 | R4: D3 makes the help of look and deploy, commands/deploy.md and json.md untrue | council round 1, refuter | acted | fixed: the port off USB, named or found by spark |
| 5 | R5: bench.py record runs no doctor | council round 1, refuter | acted | the plan's picture says so; record_deploy.py passes `undoctored` |
| 6 | R6: two re-anchored p1049 rows keep names that D3 makes false | council round 1, refuter | acted | the re-anchored rows of `p1049-asleep-stops.json` name `doctor_said` and the renamed test |
| 7 | R7: an open question of other_board could take the asleep fix (Risk 6) | council round 1, refuter | rejected | GRANT, REACH and LIVE ask only `CANNOT_TELL` (known_board.py:154-166), so other_board stops with no question. Risk 6 dropped |
| 8 | R8: a test_lint failure on the refuter's copy | council round 1, refuter | acted | each module imports only what it uses; `tests.test_lint` ran before each commit |
| 9 | A1: the "first Finding with a fix" rule belongs on the result, not in a Renderer | council round 1, architecture lens | acted | `OperationResult.first_fix()` beside `status()`; `FlatJsonLineWithFix` only calls it. Rows 7 and 8 |
| 10 | A2: O3's reason and Risk 3 were wrong about masking | council round 1, architecture lens | acted | run_cli masks `data` and each Finding with the same kept texts before the renderer (cli.py:68, privacy.py:129-135); the plan says so |
| 11 | A4: the renderer's docs | council round 1, architecture lens | acted | renderers.py's docstring and patterns-and-names.md lines 23 and 29 name `FlatJsonLineWithFix` |
| 12 | A6: `doctor_said` built ButtonPlaces again | council round 1, architecture lens | acted | it takes `places` (5 parameters, the R3 limit) |
| 13 | A7: pin what happens to a `fix` key in `data` (with L3) | council round 1, architecture and everyday lens | acted | a test_core test pins that the result's fix overwrites it |
| 14 | L1: null has two meanings | council round 1, everyday lens | acted | json.md, live's EPILOG, grant's help and never-assume.md say that null means spark has no fix, not that nothing is wrong |
| 15 | L2: relay `fix` word for word | council round 1, everyday lens | acted | json.md and scripts.md say it; `doctor.next_step` stays `plug_in`, pinned by the doctor-road tests |
| 16 | L4: "it read no board and wrote nothing" may be false after a doctor road | council round 1, everyday lens | rejected | in live and reach mpremote never entered before the doctor ran, and in look and deploy esptool's read failed. The doctor-road tests pin `entered` false (reach) and `reset` null (live) |
| 17 | L5: json.md's `port_not_listed` row names only the named port | council round 1, everyday lens | acted | the row names live's found port and the doctor roads |
| 18 | L6: json.md's `board_not_read` row and a glossary entry for the port | council round 1, everyday lens | acted | "a port off USB, named or found by spark"; GLOSSARY.md has the named and the unnamed port, and keeps "pick" for parts |
| 19 | S1: mutation row 7 of the plan raises NameError instead of planting the old fix | council round 2, refuter | acted | row 6 of `p1055-asleep-json.json` replaces `self._findings(result, fix)` with the doctor's step |
| 20 | S2: the p430 row anchors on reach's `lines=[printable(line) ...]` line, which `next=` would break | council round 2, refuter | acted | reach's `next=` is on its own line, and the anchor line keeps its text |
| 21 | S3: json.md, scripts.md and never-assume.md are at their line budgets | council round 2, refuter | acted | words were added to existing lines only; `tests.test_docs` passes, and each table cell is under 300 characters |
| 22 | S4: three more texts are untrue after D3, and test_look.py:686 pins no look step for an unnamed port | council round 2, refuter | acted | look_at_board.py's comment, grant.py's help and run_live_code.py's DETAILS fixed; the assertion moved to `test_an_unnamed_port_not_listed_now_gets_the_asleep_fix_and_the_look_step` |
| 23 | the p1049 row "asleep_after_doctor ignores the named port" | the plan's mutation rows | acted | retired: D3 makes it the behaviour, and rows 1 to 3 guard the opening |
| 24 | the p1049 row "stop_said gives a port_not_listed stop the asleep fix with no named port" | the plan's mutation rows | acted | retired: D2 makes it the behaviour |
| 25 | PR 1's rows 7 and 8: a port spark found that leaves USB gets no asleep fix, and live's doctor keeps its plug_in step | `p1057-asleep-live-reach.md` | acted | fixed in this PR: `ASLEEP_UNNAMED_PORT_OPENING` and `doctor_said` |
| 26 | PR 1's row 9: json.md and scripts.md say live and reach give no asleep fix, and live's line holds no fix | `p1057-asleep-live-reach.md` | acted | fixed in this PR: the pages and `fix` on the line (P1055) |
| 27 | a script-level test of an unnamed port for deploy.py | the plan, Step 1 | raised | not written: deploy's fakes take one devs fixture. look.py's script test and the `stop_said` unit tests cover the road; destination: the PR review |
| 28 | A3 and A5: the round-1 report is not kept and the plan's table has no line for them, so their fate is unknown | council round 1, architecture lens | raised | not guessed; destination: the PR review |
