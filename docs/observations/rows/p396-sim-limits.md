# P396 the board's own GPIOs as simulation limits: findings rows

Findings from building P396 (2026-10-23, Prague). The plan council ran two rounds: two Sonnet 5.5 lenses (technology and
tests, architecture and naming and UX), then one Opus 5.5 refuter.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | A FireBeetle build printed "not checked" for a board with no Wokwi definition, then was planned silent | round 1 (technology), round 2 (refuter) | acted | a record that names no definition says `onboard GPIOs: not checked: the board record names no Wokwi definition`. The card asks for that line, and the FireBeetle's GPIO21 and GPIO47 were not said before |
| 2 | Cutting `/* */` before parsing breaks a JSON string that holds `/*` | round 1 (technology) | acted | the cut runs only when strict JSON fails. `test_strict_json_with_a_comment_mark_inside_a_string_parses` |
| 3 | The "is this GPIO simulated" question in `sim_project` would force P397's pick to import firmware code (rule U1) | round 1 (architecture) | acted | `SimulatedPart.why_not_simulated` in `boards.py` |
| 4 | Three results of the reader (a part, None, a sentinel) where two do | round 2 (refuter) | acted | `onboard_limits` asks whether the record names a definition, and the reader returns a part or None |
| 5 | The planned sentence said "no scenario can press it", a claim about Wokwi, not about spark's records | round 2 (refuter) | acted | the card's words: "so spark knows no way for a scenario to press it", then "Test it on the board." |
| 6 | No test reached the full build's simulation stage, so a change at `check_spine.py:538` was guarded by nobody | round 2 (refuter), PR refuter | acted | the PR refuter dropped `board` at `:538`, and 2946 tests still passed. So `write_limits` now takes `board` with no default, and a call that drops it fails on the first full build. A test of `run()`'s simulation stage stays open, as it has been since P37 |
| 7 | The P37 mutation anchor and two journey examples quoted "from the records (%d)" | round 2 (refuter), PR review | acted | the anchor follows. The journey examples sit under `<!-- output: run 2026-10-11, spark 0.8.1 -->`, and a hand edit left a stray comma and made them claim output no run printed. They are restored as that run printed them |
| 8 | `--json` carries limits only as text in `stages[].detail`, so Claude matches English to see a "not checked" | round 1 (architecture), round 2 (refuter) | raised | a later card: a structured `limits` list with a kind per line |
| 9 | A note from an earlier build stays when its limits vanish (`sim_project.py`, today too) | round 1 (architecture) | raised | a later card, not this one |
| 10 | Walk 2's copy also prints "no serial monitor is wired in the diagram" for the XIAO, though its run heard "ready" | the walk 2 check | raised | G18, its cause open (P400 refuter A5). No change here |
| 11 | `read_simulated_part` raised on `documents` as a list and on a file nested 100000 deep, and a gpio of `"9"` raised in `onboard_limits` | PR refuter | verified, acted | `isinstance` guards, `RecursionError` caught, a gpio that is not an int is skipped. Four tests. `validate` still passes `gpio: ["9"]`, also for `assign_pins.onboard_lines`: a row for a later card |
| 12 | A file with `pins` as a list, or no `pins`, read as a definition with no pins, so it claimed "no pin on GPIO9" | PR refuter | verified, acted | it gives None, so the line says "not checked". The reason now names "or it does not parse". `[0-9]` replaces `\\d`, so a fullwidth digit is no GPIO |
| 13 | `onboard_limits` had no test for changed bytes | PR refuter | acted | `test_a_definition_whose_bytes_changed_says_not_checked` |
| 14 | A "not checked" in an ok stage has no word in `docs/guide/agents.md` | PR refuter | acted | one sentence beside the limits text: say it to the person, never read it as a pass |
| 15 | The `assign_pins.ONBOARD_NAMES` alias and its sameness test were extra code | PR review | acted | `assign_pins` reads `boards.ONBOARD_NAMES` |
| 16 | Tests compare the printed English sentences | PR review | rejected | the printed words are the output under test, and `tests/test_self_confirmation.py` requires literals there. The code decides by constants |
| 17 | The FireBeetle example at `commands/build.md:141` shows no limits, though a chip and the onboard roles give some | PR review | raised | older than this PR (the chip's stand-in line was missing before). A docs card |
| 18 | The glossary has no entry for the new words | PR review | rejected | `glossary.md:63-64` holds "Wokwi definition" and "limit" |
| 19 | Mutation run 1, on a tree before d78718b: 12 planted, 10 caught. `GPIO9x` counted as GPIO9, and only the first GPIO of a role was read | mutation run | acted | `test_only_a_whole_gpio_name_is_a_gpio`, `test_each_gpio_of_a_role_with_no_pin_is_its_own_limit`, each checked by planting the defect by hand |
| 20 | Mutation run 2, on 642ea03: 18 planted, 17 caught. A default for `board` in `write_limits` escaped | mutation run | acted | `test_the_board_cannot_be_left_out` |
| 21 | `onboard_limits` read `documents` as a table where the reader guards it, so a list said "store lacks" | prune sweep | acted | the same guard, and `test_documents_that_are_not_a_table_name_no_definition` |
