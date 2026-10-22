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
| 7 | The review (Sonnet 5.5): no MVP marker on the `plan_pick` line, a long docstring line, no test for a board an older pick held twice, and journey.md said "every need picks the board" for a wider rule | review | acted | the marker, the wrap, `test_a_board_an_older_pick_held_twice_is_held_once_after_a_re_pick`, the journey wording |
| 8 | The refuter (Opus 5.5): a hand-written `"board_only": false` is rewritten to `true` when the board serves every need | refuter | rejected | `false` beside an empty parts list cannot build (`check_spine.py`, "the requirements name no parts"). The said line names the change |
| 9 | The refuter: a board drawer entry with no record, picked for two needs, still counts two pieces | refuter | rejected | a board with no board file cannot build, and `--requirements` refuses it (`_unfiled_boards`) |
| 10 | The refuter: a need that picks the board and a record-less speaker leaves the file `board_only: true`, with the speaker reserved, not placed | refuter | closed | the council chose this in round 1: a record-less pick is wired off the board, so the board alone is the build |
| 11 | The mutation run: 12 planted, 11 caught. The removal line said with no part listed escaped | mutation-tester | acted | `test_when_the_board_serves_every_need_the_file_says_board_only` reruns on the written file and asserts no removal line |
