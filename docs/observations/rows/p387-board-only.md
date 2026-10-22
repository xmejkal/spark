# P387 board_only from parts.py --requirements: findings rows

Findings from building P387 (2026-10-22, Prague). It closes prediction 4 of `p378-walk2-map.md`. The plan council ran two
rounds: two Sonnet 5.5 lenses, then one Opus 5.5 agent.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `plan_pick` counted one piece per pick, so one owned XIAO picked for `board` and `light` was refused ("1 owned — 2 picked here"). Walk 2 could not run | council round 2 (Opus) | verified, acted | reproduced by `test_the_board_picked_for_two_needs_takes_one_piece`. A board pick now counts once per project |
| 2 | Two older pick tests used a board for a "spare" need, so they expected two boards reserved | the suite | acted | they now use the part `x-silent`, which keeps what they test: the refusal count and one record over two entries |
| 3 | The writer and the reader used two spellings of `board_only` | council round 1 (architecture) | acted | `needs.BOARD_ONLY`, read by `check_spine.py` |
| 4 | Dropping `board_only` without a word hides a change the person made | council round 1 (edge cases) | acted | `board_only removed: the file lists parts` |
| 5 | `/spark:idea` had no route to pick the board for a need while P355 (#453) is open | council round 1 (edge cases) | acted | one sentence in `commands/idea.md` section C |
| 6 | A hand value such as `"yes"` is kept and fails at the build | council round 1 (edge cases) | rejected | the build names it already (`test_a_string_true_is_not_board_only`). This card only writes the key |
