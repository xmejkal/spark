# P953 PR 4a: every jumper carries a pill with its step number and the two pads it joins, and the wires use the visual palette: rows

Card: [P953 #1359](https://github.com/xmejkal/spark/issues/1359). This file holds the acted, raised and rejected
findings only, then each test this PR changes with what it pinned before and what it pins now. The build ran on Opus;
revision 8 of the plan check splits PR 4 and keeps the word cyan. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `test_flow_page.TheBudgetTest.test_the_page_stays_within_its_budget` and `TheInlinePictureTest.test_each_jumper_step_and_each_part_of_the_built_fixture_is_in_the_page` are red at main 8efff4aa: they count 8 and 4 `data-step` groups, and PR 3's rails give 10 and 5 | the build, a run of the area's tests on a copy of main | raised | to the coordinator for a card: this PR changes neither test nor the jumper counts (the hook does not run `test_flow_page`) |
| 2 | a stub into a rail is too short to hold its pill on its wire (the walk's 3 and 8, the module's 9) | the build, the walk's render | acted | `PillLayout` tries, after every run, a pill across beside each piece, 2 px off its wire or its end dot, then one past an end along the last piece; `test_every_pill_finds_a_free_place_on_every_fixture` reads the layout's pills and checks each is free and on its wire or within 6 px of it |
| 3 | the plan names `PillLayout` a Strategy with a `pill_layout` argument; the renderer's `__init__` then takes 6 parameters (R3, 5) and no caller swaps it | the build, `test_architecture` | acted, with a change | `PillLayout` is a Service the renderer builds; the role table names it with the word pill |
| 4 | the plan renames cyan to teal | revision 8 | acted | the word stays cyan on the sheet and in Wokwi, drawn `#0b7fa8` (4.55:1 on white); no sheet or Wokwi byte moves |
| 5 | the cyan test read `sheet.JUMPER_COLORS` as its expectation | the build, `test_self_confirmation` | acted | the test reads the walk's golden sheet line "12 magenta, 13 cyan." and its picture's `#0b7fa8` |
| 6 | the pills paragraph pushed `scripts.md` (308) and the names table `patterns-and-names.md` (279) past their budgets | the build, `test_docs` | acted, with a change | the section "The pills and the wire colours" of `breadboard-codes.md`; `scripts.md` points to it in the same three lines; the role table's Service row names `PillLayout` and the pill |
| 7 | `TrackRouting.LEG_CLEARANCE` (2.5) says it is the white under-stroke's half width, which is now 2 | the build | acted | the comment says "more than" it; the value stays, so no route moves |
| 8 | two older mutation rows lost their `find`: P268 "a jumper in the wrong color" and P947 "the number sits at the corner, not mid-run" | the build, `tools/mutate.py --anchors` | acted | they follow the moved lines: the wrong colour's hex, and the pill at its run's start; 20 rows are refused, the same 20 as on main |
| 9 | `docs/guide/img/button-light-xiao-breadboard.svg` was no longer the XIAO golden's picture after PR 2 and PR 3 | the build | acted | drawn again from `breadboard-ok-xiao.txt`; the sentence above it in `recorded-run.md` says the pill and no lane |
| 10 | the walk-c6 fixture's golden shows the e-paper's frame picture, not the red demo screen of the walk's store | revision 9 | acted | said in the PR; the walk's render with the kept picture is the PO's look |
| 11 | the module golden's canvas grows 36 px upward: its GND stub's pill (9) sits past its rail end, turned | the build, the golden's diff | acted | read in the diff: the place left beside the stub touches wire 3 or wire 12, so the pill goes past the end |

## The tests this PR changes

Each moved because the picture draws the palette's hex and a pill in place of the bare number. Each keeps every other
fact it pinned.

- 5 goldens `breadboard-ok-{xiao,firebeetle,module,c6,rebuild}.txt`. Before: the wires in CSS words, 5 and 2.5 wide, end dots 3 with a 1 ring, a bold number per wire. Now: only their `breadboard.svg` lines move (read in `git diff`): the hex, 4 and 2.2, 3 and 0.8, a pill in each wire's group, and the canvas grown where a pill lies past the board (c6, module, xiao). Their sheets, Wokwi files and records are unchanged.
- `test_breadboard_svg.TheSvgTest.test_the_bytes_are_the_ones_reviewed`. Before: 7d080087. Now: a79ee2aa, rendered and looked at.
- `test_breadboard_svg.TheRecordBoardSvgTest.test_the_picture_is_the_one_looked_at_on_2026_11_20`. Before: 6638454c. Now: fb324bc3, rendered and looked at.
- `test_breadboard_svg.TheSvgTest.test_each_jumper_runs_from_hole_center_to_hole_center_in_its_step_s_color`. Before: the colour path's stroke is the jumper's colour word. Now: the word's hex; every centre unchanged.
- `test_breadboard_svg.TheWireStyleTest.test_3v3_is_red_gnd_is_black_and_no_signal_is_either`. Before: 3 and 4 "red", 9 and 10 "black". Now: `#d0202a` and `#20262b`; no signal is either.
- `test_breadboard_svg.TheJumperLanesTest.test_no_step_numbers_overlap`. Before: no two bold numbers overlap. Now: removed with its helper `number_boxes`, as the numbers are gone; `ThePillsTest.test_no_two_pill_boxes_touch` checks the pills on the same pictures and the four fixtures.
- `test_breadboard_svg.ThePillsTest.test_every_pill_finds_a_free_place_on_every_fixture` (new in this PR's first commit). Before: each pill on a piece of its wire. Now: each pill `free`, on a piece of its wire or within 6 px of it (row 2).
- `test_breadboard_layout.TheSheetNamesTheWireColorsTest.test_the_line_the_svg_and_the_record_agree`. Before: the svg holds `stroke="red"` and `stroke="black"`. Now: a red and a black wire, `#d0202a` and `#20262b` at 2.2; the sheet's line and the record's words unchanged.
