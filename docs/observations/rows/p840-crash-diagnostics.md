# P840: a crashed Operation keeps the diagnostics it gave the core: rows

Card: [P840 #1204](https://github.com/xmejkal/spark/issues/1204), raised by row 20 of
`docs/observations/rows/p804-build-and-checks-on-core.md`. One plan round (the architecture lens and the refuter on
Opus), then a build to the plan with the council's changes. This file holds the acted, raised and rejected findings
only. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | two tests in `test_needs` hand `run_operation` a builder that gives None, and DropNeed never reads `outside`: `None._replace` would crash one run and let the other pass without running DropNeed | plan council | acted | `_guarded_result` leaves a None world as None; `test_core.RunOperationTest.test_a_world_the_builder_gives_as_none_reaches_the_operation_as_none` and mutation row 3; the two tests are unchanged |
| 2 | the lines should be merged once, after the try, not once per end | plan council | acted | the try picks `result`, and one closing line merges; mutation rows 1 and 2 plant it |
| 3 | the rule needs saying once: `add_diagnostics` is for lines that must outlive a crash, and a line that only belongs to a normal answer goes in the result's `diagnostics` | plan council | acted | `outside.py`'s comment over the slots and `patterns-and-names.md`'s list of the slots |
| 4 | a direct `.run()` with a FakeOutsideWorld has no slot | plan council | acted | one line in FakeOutsideWorld's docstring: an AttributeError |
| 5 | `json.md`'s crash paragraph is scoped to `look.py` and `deploy.py` | plan council | acted | the sentence went to the build's keys (`### check_spine.py`): a crash prints nothing on stdout, exits 2, and stderr leads with the build's own lines; two lines of the missing-facts bullet that repeated the page paid for it, and the page stays at 425 lines |
| 6 | lines that `RequirementsBuildService.build` adds to its own list (`requirements_build.py:70-76`, the firmware line and the history line) are still lost if the service itself crashes partway, since they reach the core only when it returns; deploy's `_crashed` and bench.py's register and record steps keep their own diagnostics lists too | plan council, PR review | raised | card [P938 #1335](https://github.com/xmejkal/spark/issues/1335): the build service's and deploy's own crash-time lines through the slot |
| 7 | two rows of older tables anchored on the lines this change moved: p655's `run_operation ignores effects_of` and p804's `the kept entries' lines never reach stderr` | build | acted | each anchored again on the same defect; `tools/mutate.py --anchors` refuses the same 20 rows as on main and no other |
| 8 | the four new rows and the two anchored again must each fail a test | build | acted | each planted in a copy of the tracked tree (`PYTHONDONTWRITEBYTECODE=1`), running `test_core`, `test_check_spine` and `test_needs`: 6 planted, 6 caught |
| 9 | the raised row 6 needs a destination | PR review | acted | card P938, named in row 6 and in the PR |
| 10 | the crash sentence in `json.md` sat in the list of the build's keys, but it is no key, and the bullet "Refusals and crashes" speaks of a stage's crash | PR review | acted | the sentence moved into that bullet as "a crash of spark itself (not a stage)" |
| 11 | "a problem's four keys" hides the keys an agent reads | PR review | acted | `{subject, code, sentence, fix}` is back; "is never in `unchecked`", which the list's "top-level" and the codes table say, paid for it, and the page stays at 425 lines |
| 12 | the inline comment on `build_board.py`'s `add_diagnostics` line repeats the docstring and names only the history line | PR review | acted | dropped; mutation row 4 anchored again on the bare line |
| 13 | the patterns page should say the lines come first before the mask, and that `run_operation` fills the slot | PR review | acted | both said on lines 61 and 72; line 61 stays shorter than on main by cutting "the run's open list", which `data.open` names |
| 14 | "gather" is a second word for the slot | PR review | acted | the PR's title says "added", and `test_core`'s class is `Adding` |
| 15 | the None-world row leaves one drawer test green | PR review | rejected | `test_core` catches the row, and the weakness predates this PR |
| 16 | the trace's arguments now live only in `cli.py` | PR review | note | the patterns page says only that `trace` is called once |
