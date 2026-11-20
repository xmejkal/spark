# P953 PR 3: power and ground go through the rails, the first end marks a + or - rail and the others join it: rows

Card: [P953 #1359](https://github.com/xmejkal/spark/issues/1359). This file holds the acted, raised and rejected
findings only, then each test this PR changes with what it pinned before and what it pins now. The build ran on Opus;
the coordinator's answers decide where the plan was silent. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the rail seating picks one rail by the side of most ends, so on the walk the e-paper's VCC and GND (wires 5 and 9) run to the bottom rails under the e-paper while the top rails sit right above its header; 3V3_2 (wire 4) runs round the board until joined_pads lands ([P955 #1361](https://github.com/xmejkal/spark/issues/1361)) | the coordinator, from the walk's render | raised | [P959 #1373](https://github.com/xmejkal/spark/issues/1373) |
| 2 | the walk's render after PR 1 showed rail holes covered by a part body; a rail jumper must take a free hole | the coordinator's brief | acted | `rails.rail_holes_under`: the planner claims each rail hole a body covers or comes within half a pitch of; `test_each_rail_end_has_a_jumper_to_a_free_rail_hole` on the four drawn fixtures; mutation row "a rail hole under a part's body is left free" |
| 3 | the half board's rail holes lie off the router's grid (x 34 + 9.6 n, 1.6 px off a column), so a rail wire's leg slanted: `test_every_segment_is_straight...` failed on the XIAO's wires 7, 8 and 9 | the build, `test_wire_routing` | acted | `TrackRouting._along_the_holes`: the corner beside a hole takes the hole's x; a way with no corner gets two on the track next to its first hole. Every router rule test passes unchanged; `cut_short` 0 on every fixture; the walk takes 164447 states (limit 300000) |
| 4 | a rail jumper should take the rail hole nearest its end, not the rail's first free hole, and the reshuffle of ends by height must leave rail holes alone (they lie at one height) | the build | acted | `HoleLedger.claim_free_hole(group, by, x)`; `spacing.ends_toward_their_runs` skips column 0; mutation rows. `KeepMovesJumperPlacement` takes the nearest free hole too (the plan's risk: it took a rail group unchanged): the same hole as before in a row of holes, a near one on a rail |
| 5 | a third mark of one sign, a resistor leg on a rail, and a rail with no sign stay `not_drawn_yet`; the old "rails are not drawn yet" was half untrue (PR 1 rows, row 23) | the plan, PR 1 rows 22 and 23 | acted | `_refuse_what_is_not_drawn` says "a rail with no sign is not drawn yet" or "this breadboard has no rails"; the resistor's refusal names the resistor; `_seat_rails` raises "GND goes on a free - rail, and none is left" |
| 6 | the plan put `RailSeating` in `drawing.py`; it reached 635 lines (R1, 600) | the build, `test_architecture` | acted, with a change | the new module `rails.py` holds `RailSeating` (None when no rail is left; the planner raises), `rail_holes_under` and `hole_words`; it imports nothing of `drawing`. `drawing.py` is 597 |
| 7 | the plan's paragraph in `scripts.md` passes its budget (308), and the README's Build cell its 300 characters | the build, `test_docs` | acted, with a change | the rails paragraph is the section "Power and ground on the rails" of `breadboard-codes.md`; `scripts.md` names it in one line and adds `sign` to `WiringChange`. The Build cell is shortened to keep P512, P945 and P953 |
| 8 | about 30 existing tests not named in the plan pin the old power and ground rows | the build, at its first run | acted | the coordinator's yes (the PO approved rails by role): each is listed below, none weaker |
| 9 | three older mutation rows lost their `find`: P191 "a point with more ends than a row holds is not sent to a rail", P287 "a jumper that is not kept takes the planned holes without a claim", P691 "a full row is told as a full board" (twice) and "a rail is told as a planner fault" | the build, `tools/mutate.py --anchors` | acted | they follow the moved lines; 20 rows are refused, the same 20 as on main |

## The tests this PR changes

Each moved because power and ground now go through the rails: a power or ground point has one jumper per end to its
rail, so its steps, numbers, jumper counts and holes move. Each keeps every other fact it pinned.

| test | pinned before | pins now |
| --- | --- | --- |
| 6 goldens `breadboard-ok-{xiao,firebeetle,module,c6,rebuild,not-drawn}.txt` | the old rows; read in `git diff` | the rail steps, the rail nodes in the diagram, the point lines' `— power:` / `— ground:` sentence, the records' `sign`, the pictures. Rebuild: "Take out the black jumper from the row of LedRed5mm K to the GND rail." (board GND stays on the rail). The motor is still not drawn |
| `button-light/breadboard.expected.md`, `motor/breadboard.expected.md` | the old sheets | the same sheets with the rail steps (read in the diff) |
| `test_breadboard.TheMotorExampleTest.test_the_points_read_as_before_the_steps_came` | point 6 ends with the off-board supply | point 6 ends with the supply, then the power sentence |
| `test_breadboard.TheXiaoExampleTest.test_its_steps_read_as_built` | 9 steps | 10 steps; steps 5 and 6 and their holes unchanged |
| `test_breadboard_steps.ThePointRoleTest.test_the_role_reaches_each_step_and_each_drawn_jumper` | roles power, 4 signals, ground, 2 signals; jumpers {3 power, 8 ground} | power twice, ground twice; jumpers {3, 4 power, 9, 10 ground} |
| `test_breadboard_steps.ThePrintedLabelTest.test_the_step_says_the_printed_label` | step 4 says e-paper D/C | step 5 says it |
| `test_breadboard_layout.TheSheetNamesTheWireColorsTest.test_the_line_the_svg_and_the_record_agree` | 3 red ... 8 black ... 10 cyan | 3 and 4 red, 9 and 10 black, 12 cyan; the svg's red and black stay |
| `test_breadboard_layout.TheRecordBoardLayoutTest.test_four_jumpers_...` | 4 jumpers | `test_five_jumpers_and_the_same_bytes_twice`: 5; same bytes twice |
| `test_breadboard_layout.TheXiaoLayoutTest.test_the_drawing_keeps_the_bytes_wokwi_showed` | hash 4a35a5ed | hash 51af5c29: the three ground jumpers to bn.6, bn.14, bn.10; no part moved (read in the diff) |
| `test_breadboard_layout.TheSpaceBetweenPartsTest.test_all_end_holes_of_one_header_are_in_one_row_unless_taken` | {f: 8, g: 1}: VCC took two jumpers | {f: 8}: each pin's row holds one end |
| `test_breadboard_layout.TheSpaceBetweenPartsTest.test_two_jumpers_into_one_row_take_the_hole_toward_their_other_end` | the walk's two VCC jumpers, 7b.j-49b.g and 11t.a-49b.f | the same four holes handed the wrong way to `ends_toward_their_runs`, which gives 49b.g and 49b.f back; two rail jumpers keep their holes |
| `test_breadboard_layout.EachStepNamesItsHolesTest.test_the_e_paper_s_steps_name_their_holes_in_the_order_the_step_runs` | lines 1 to 4, 10 lines | lines 1 to 5 with the rail holes, 12 lines |
| `test_breadboard_layout.EachStepNamesItsHolesTest.test_a_hole_reads_letter_then_column_and_a_rail_keeps_its_name` | tp.3 reads "tp.3" | `..._and_a_rail_by_its_side_and_sign`: "top + rail, hole 3"; e41; a rail of no known name keeps its name |
| `test_breadboard_layout.WhatIsNotDrawnTest.test_a_rail_is_said_not_drawn` | "rails are not drawn yet" | `test_a_rail_with_no_sign_is_said_not_drawn`: "a rail with no sign is not drawn yet", code and subject |
| `test_breadboard_svg.TheSvgTest.test_each_jumper_runs_from_hole_center_to_hole_center_in_its_step_s_color` | the helper read a terminal hole only (an error on bn.6) | the helper reads a rail hole's centre from `data/wokwi-geometry.json` too; no case dropped |
| `test_breadboard_svg.TheSvgTest.test_the_bytes_are_the_ones_reviewed` | 5001ff44 | 7d080087, rendered and looked at |
| `test_breadboard_svg.TheRecordBoardSvgTest.test_the_picture_is_the_one_looked_at_on_2026_11_20` | ac835219 | 6638454c, rendered and looked at |
| `test_breadboard_svg.TheWireStyleTest.test_3v3_is_red_gnd_is_black_and_no_signal_is_either` | 3 red, 8 black | 3 and 4 red, 9 and 10 black; no signal red or black |
| `test_wire_routing.TheRoutesTest.test_the_walk_s_result_is_pinned` | dashed 7, 8, 9, 11 of 9 | dashed 6, 7, 10, 11 of 11 (all signals); the rail wires 3, 4, 5, 8, 9 keep the rules |
| `test_wire_routing.TheRoutesTest.test_the_xiao_s_wire_7_is_dashed_...` | wire 7 dashed | `test_the_xiao_s_wire_7_is_no_longer_dashed_as_ground_goes_to_the_rail`: 5 to 9, none dashed |
| `test_wire_routing.TheRoutesTest.test_the_other_fixtures_results_are_pinned` | button-light 7 dashed; e-paper 4, 8 | button-light none; e-paper 5, 11, 12 |
| `test_wire_routing.TheFallbackTest.test_a_walled_end_is_not_drawn_and_the_note_says_so` | the note names dashed wire 7 and walled wire 5 | the note names walled wire 5 only |
| `test_wire_routing.TheFallbackTest.test_a_dashed_wire_is_dashed_in_its_colour_only` | the XIAO's dashed 7, solid 5 | the walk's dashed 6, solid 3 (the XIAO has no dashed wire) |
| `test_breadboard_record` (7): `FirstBuildTest`, `RebuildTest` x2, `WriteOrderTest` steps; `DrawnJumpersTest` x2; `CheckSpineTest` x2 | 9 steps; drawn jumpers with 12t.a-17b.h and 17b.g-8b.j; 3 left after a person's move; changes 5 added + 1 rerouted (board GND to the LED's row) | 10 steps; drawn jumpers with 12t.a-bn.10, 17b.g-bn.14, 8b.j-bn.6; 4 left; 5 added (board GND stays on the rail), with "Run a black jumper from the row of LedRed5mm K to the GND rail." The rerouted line is pinned by `SignedRailTest` |
| `test_breadboard_keep_jumpers` (7) and `test_breadboard_keep` (1) | GND jumpers between rows 8b, 12t and 17b; 4 wires | the same moves on the rail jumpers: the LED's K jumper moved to the button's row is kept (12t.c-bn.14), follows the LED to 19b (19b.g-bn.14); a jumper not kept takes the nearest free rail hole beside a kept one (bn.7: bn.5 lies past the gap between blocks of five); a jumper moved to R1's row is named; a kept jumper stays at its place (8b.j-bn.8); 5 wires |
| `test_architecture.TheBreadboardAreaTest` | the area's modules | `rails` added |
