# P407: a board with no footprint stops at the footprint stage, findings rows

Findings from the plan councils and the build of P407 (2026-10-25, Prague). The build checked each claim of the
approved plan in the code.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | With `--keep`, the build still writes `firmware/pins.py` on a footprint stop | plan | acted | true only when the pins can be placed: `keep_pins` writes nothing on `assign_pins.Impossible`. `NO_FOOTPRINT_HINT` says "if its pins can be placed, and the kept lines say which". `test_pins_that_cannot_be_placed_are_said_in_the_kept_lines` |
| 2 | The footprint check before `emit_board` keeps today's order of causes | plan, round 1 refuter | acted | it does not. Without `--keep`, a board with no header and an impossible pin assignment now shows only the footprint stop, and the pin cause shows after the footprint exists. With `--keep`, the kept `pins.py` line names it. Accepted for the MVP |
| 3 | A record with `footprint_export` and no header stopped under `schematic` | plan | rejected | it reached the old `footprint` stage with "no footprint could be generated". Only a record with no `footprint_export` (the T-Display walk) stopped under `schematic` |
| 4 | The `footprint` stage's own failure says why | build | raised | after this change it fails only when `emit_footprint.main` exits PROBLEMS (a header that disagrees with itself). Its detail is still "no footprint could be generated for <id>", and the reason goes to stderr. A later card |
| 5 | The `--keep` test fails on the old code | build | acted | it passed there: the old footprint stage also stopped a XIAO with no header, so the stage name alone proved nothing. The test now asserts the hint sentence too, and all four new spine tests fail on the old code |
| 6 | The `emit_board` guard had a test | plan, round 2 | acted | none: no test quoted "reference nothing". `test_a_board_that_cannot_give_a_footprint_is_could_not_run_naming_the_gap` covers a missing `footprint_export` and a missing `header_order` |
| 7 | The stage picture in `commands/build.md` needs a footprint stop | plan | rejected | the picture shows a passing run. The refusal table holds the new row, and a second picture would repeat it |
