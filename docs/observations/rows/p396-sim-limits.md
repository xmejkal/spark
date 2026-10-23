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
| 6 | No test reached the full build's simulation stage, so a change at `check_spine.py:538` was guarded by nobody | round 2 (refuter) | acted | both paths call `sim_project.write_limits(sim_dir, design, board)`, which the tests cover |
| 7 | The P37 mutation anchor and two journey examples quoted "from the records (%d)" | round 2 (refuter) | acted | `tests/mutations/sprint-7-p37.json`, `docs/guide/journey.md` |
| 8 | `--json` carries limits only as text in `stages[].detail`, so Claude matches English to see a "not checked" | round 1 (architecture), round 2 (refuter) | raised | a later card: a structured `limits` list with a kind per line |
| 9 | A note from an earlier build stays when its limits vanish (`sim_project.py`, today too) | round 1 (architecture) | raised | a later card, not this one |
| 10 | Walk 2's copy also prints "no serial monitor is wired in the diagram" for the XIAO, though its run heard "ready" | the walk 2 check | raised | G18, its cause open (P400 refuter A5). No change here |
