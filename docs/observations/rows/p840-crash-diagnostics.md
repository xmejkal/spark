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
| 6 | lines that `RequirementsBuildService.build` adds to its own list (`requirements_build.py:70-76`, the firmware line and the history line) are still lost if the service itself crashes partway, since they reach the core only when it returns | plan council | raised | a line on card P840's follow-up |
| 7 | two rows of older tables anchored on the lines this change moved: p655's `run_operation ignores effects_of` and p804's `the kept entries' lines never reach stderr` | build | acted | each anchored again on the same defect; `tools/mutate.py --anchors` refuses the same 20 rows as on main and no other |
