# P389 PR 1: a board names its own LED, buttons and display, findings rows

Findings from building PR 1 of P389 (2026-10-25, Prague). The build checked each claim of the approved plan in the code.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan adds the display to `PIN_ROLES` and `ONBOARD_ROLES` in its first commit | build | acted | the display row came in commit 4, where it first has an effect. Commits 1 to 3 change no behaviour, as the plan's commit order says |
| 2 | `parts.validate` gives "the same problem" for a fact that is no object | build | acted | it already did, through `type_problems`, before the fact loop ran. The wording of `provenance.fact_problems` matches it. `test_a_fact_that_is_no_object_is_caught` guards it |
| 3 | Each caller builds `where` with `%r` | build | acted | `boards.validate` does. `parts.validate` keeps `facts.%s`, so its messages do not change, and `type_problems` prints names raw too. A newline in a fact name of a part record still reaches the screen raw there |
| 4 | `boards.validate` read `role["note"].strip()` on any value | build | acted | a note that is no string raised in `boards.load`. It is now the "empty note" problem. `test_a_note_that_is_no_string_is_a_problem_not_a_crash` |
| 5 | The plan says `function_of` adds onboard functions "on both paths" | build | acted | read as both paths of a board (own `function`, and kind). A part record, `board=False`, gets none. `test_a_part_that_is_no_board_does_not_gain_the_board_s_parts` |
| 6 | The mutation tables' anchors hold | build | raised | 104 rows are refused on main already, and the push hook checks none of them (P208). This PR re-anchored the `p353-onboard-roles` table (2 refused on main, 7 more by this PR) and one row of `sprint-10-p96-1`. A sweep of the 100 others is for the council to decide |
| 7 | The kept README is the T-Display's pin source | build | raised | its pinout column is headed V18, and the board's silkscreen reads V1.1. The fixture's display note says so. No kept source says the two are one revision |
| 8 | The README's BUTTON1 and BUTTON2 name the buttons | build | acted | the README puts BUTTON1 on 35 and BUTTON2 on 0, the other way round from the schematic. The fixture uses the schematic's S1 on GPIO0 and S2 on GPIO35, and its note says so |
| 9 | The T-Display buttons hold an `active_level` | build | raised | the walk record had none. The fixture gives 0 from its own note ("each pressing to GND", schematic). Nobody pressed them on the bench for this. The walk project's record is not changed |
| 10 | Only the fixture names a display today | build | raised | the walk project's own record gets the display after the merge, with the PO's yes |
| 11 | A bad record never reaches `pin_module` | build | raised | `design.load` validates through `boards.load`, and `test_a_record_with_bad_labels_never_reaches_the_pin_map` proves it. A caller of `pin_module` with an unvalidated record that holds a label with a non-number would still raise in `%d` |
| 12 | The Idea step's status note changes | build | raised | the README row and `tools/journey.py` are unchanged, because the step stays "partly" and the offer is one small addition. `docs/guide/journey.md` has one more sentence. The council may want the row changed |
| 13 | The limits note's header said that every line comes from a part record or the Wokwi definition | build | acted | the display sentence comes from no record. The header now says "Most lines" and "The rest say what spark did not check or leaves out of the diagram." |
| 14 | A new test that reads a module constant passes `test_self_confirmation` | build | acted | `boards.ONBOARD_ROLES` and `boards.ONBOARD_DISPLAY` have entries in `MAY_READ`, each with its reason |
