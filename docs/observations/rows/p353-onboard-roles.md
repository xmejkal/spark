# P353 on-board roles in pins.py: findings rows

Findings from building P353 (2026-10-20, Prague). The plan is item 3 of the P351 plan (PR #449).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan says the FireBeetle record holds neither role, but it names `onboard_button` GPIO47, so its `pins.py` now gains `ONBOARD_BUTTON = 47` | implementer, plan claim | acted | `boards/firebeetle2-esp32s3.json` `pin_roles.onboard_button`, a true fact, kept |
| 2 | The on-board LED line put the record's note into a comment without the one-line cleaning, so a line break in a note could run as code | the suite, implementer | acted | `test_a_line_break_in_the_board_s_words_never_leaves_the_comment` failed for the new button line; `onboard_lines` cleans every note |
| 3 | A signal assigned to the board button's GPIO now sits beside an `ONBOARD_BUTTON` line with the same number | the suite | acted | both are true, the exactly-once test leaves the board's own names out |
| 4 | The LED level comes from the PO's bench only, the schematic was not read | implementer | raised | the record's note says so, the tech lead's P351 report names the bench result |
| 5 | A signal named `ONBOARD_LED_ON` was overwritten by the level line, so the firmware read the wrong pin | refuter | acted | the refuter's repro (GPIO17, then 0); `onboard_lines` refuses both names, test `test_a_signal_named_like_the_led_s_level_is_refused_not_shadowed` |
| 6 | `pins.py` kept only the first sentence of a note, so the XIAO's "held down at reset it enters the bootloader" and the FireBeetle's "cannot wake the chip" never reached the firmware | refuter | acted | the on-board lines write the whole note, test `test_the_board_s_whole_note_reaches_its_own_line` |
| 7 | `ONBOARD_BUTTON_ON` is written for a button record with `active_level`, but no doc named it | reviewer | acted | `commands/build.md`, `docs/guide/agents.md`, the `--help` text and the docstring name it |
| 8 | Mutation run 1: 11 planted, 9 caught. No test gave a role two GPIOs, and no test checked the button line without a level | mutation tester | acted | two tests added, the table kept as `tests/mutations/p353-onboard-roles.json` |
| 9 | `docs/guide/agents.md:226` says "It may also compile" | reviewer | rejected | older than this PR, not in its lines |
| 10 | Mutation run 2: 12 planted, 12 caught | tools/mutate.py --copy | verified | "every mutation was caught, and the suite is green with the files restored" |
