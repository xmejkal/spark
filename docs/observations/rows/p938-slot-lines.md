# P938: the build service and deploy add their lines through the one slot: rows

Card: [P938 #1335](https://github.com/xmejkal/spark/issues/1335), raised by row 6 of
`docs/observations/rows/p840-crash-diagnostics.md`. One plan check (the architecture lens and the refuter on Opus),
then a build to the plan with its decisions, then the PR review (the architecture lens and the refuter on Opus). This
file holds the acted, raised and rejected findings only. 2026-11-20. A note of the PR review: a direct `run()` with no
`add_diagnostics` raises TypeError on a line, as `BuildBoard.run()` did on main.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the service is no Operation: it reaches the slot as one callable per call, `build(..., add_diagnostics=None)`, never the whole outside; a generator would make `BuildBoard` drive the run, and the constructor outlives one run | plan, plan check | acted | `requirements_build.py`; `BuildBoard` hands `outside.add_diagnostics` |
| 2 | dropping `RequirementsBuildResult.diagnostics` moves what two tests read | plan check | acted | `ARequirementsBuildServiceTest.run_with` returns the lines it gave the slot as `added` beside the run; `run.diagnostics` became `added` in the refused-file and the history tests, the same assertions; the timeout and crash tests only unpack |
| 3 | the slot is called only when there is a line, and the callable is not guarded, so a missing slot fails loudly as the core's does | plan check | acted | `if lines := ...: add_diagnostics(lines)` and the history line's own call |
| 4 | a crash test of the service needs a crash after a line without a new `mock.patch` (T2) | plan | acted | `RequirementsBuildService(note_built=None)`, looked up at call time as `_stages` does, so the patches of `part_facts.note_built` in `test_check_spine` still reach it; `test_a_crash_in_the_history_note_keeps_the_firmware_line_ahead_of_the_traceback`; mutation row 3 |
| 5 | deploy's three lines (the refusal, the look's stop, the closed gate) are each the last step before the run returns; only the result's assembly runs after them, and `_crashed`'s `flow.diagnostics` was always empty | plan | acted | the lines go to `outside.add_diagnostics`; `self.diagnostics`, `deploy_result`'s `diagnostics` and `_crashed`'s `flow.diagnostics +` are gone; `_crashed` stays for `board_state`, the finding and the look step |
| 6 | a flasher whose commands raise to crash the result's assembly is a contrived seam | plan check | acted | dropped; `test_a_refusal_and_a_closed_gate_give_their_line_to_the_slot_as_it_is_said` runs `DeployImage.run` with a slot of its own: the line is in the slot and none in the result; the goldens pin the byte order |
| 7 | the slot's rule says it is for lines that must outlive a crash, which a refusal line seemed not to be | plan, plan check | acted | said once, in `outside.py`'s comment and on the patterns page: a line said before work that can still fail goes in the slot, a line built into the final result in the result's `diagnostics` |
| 8 | a crash in the service after the work folder is made leaves the folder, as `BuildBoard`'s `finally` never gets it | plan | raised | card [P939 #1337](https://github.com/xmejkal/spark/issues/1337); the new test removes the folder by a `spark-spine-*` glob |
| 9 | bench.py's register and record keep their own diagnostics lists | P840's row 6 | rejected | their line is built into the final result (`register_project.py:80`, `record_deploy.py:84`), so by the slot's rule it stays there |
| 10 | seven rows of older tables anchored on the lines this change moved: p423's gate row, p508's two rows, p655's `board_envelope` row, p840's row 4 and p97-requirements-fix's two `note_built` rows | build | acted | each anchored again on the same defect; `tools/mutate.py --anchors` refuses the same 20 rows as on main and no other |
| 11 | the walrus name `gone` holds the sentence in a list, and the plan said `if line:` | PR review | acted | renamed `lines`; mutation row 1 anchored on it |
| 12 | `BuildBoard`'s docstring should say who gives the service's lines to the slot | PR review | acted | "(the service gives them to `outside.add_diagnostics`, so a crash later keeps them, P840, P938)" |
| 13 | row 9's reason should name where register's and record's line is built | PR review | acted | row 9 names `register_project.py:80` and `record_deploy.py:84` |
| 14 | the cut of "in the run's project" from the `find_tool` sentence loses a fact | PR review (refuter) | rejected | the same page states it at `ToolFinder(project).find`, line 66 (the lens checked it) |
