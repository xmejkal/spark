# P353 on-board roles in pins.py: findings rows

Findings from building P353 (2026-10-20, Prague). The plan is item 3 of the P351 plan (PR #449).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan says the FireBeetle record holds neither role, but it names `onboard_button` GPIO47, so its `pins.py` now gains `ONBOARD_BUTTON = 47` | implementer, plan claim | acted | `boards/firebeetle2-esp32s3.json` `pin_roles.onboard_button`, a true fact, kept |
| 2 | The on-board LED line put the record's note into a comment without the one-line cleaning, so a line break in a note could run as code | the suite, implementer | acted | `test_a_line_break_in_the_board_s_words_never_leaves_the_comment` failed for the new button line; `onboard_lines` cleans every note |
| 3 | A signal assigned to the board button's GPIO now sits beside an `ONBOARD_BUTTON` line with the same number | the suite | acted | both are true, the exactly-once test leaves the board's own names out |
| 4 | The LED level comes from the PO's bench only, the schematic was not read | implementer | raised | the record's note says so, the tech lead's P351 report names the bench result |
