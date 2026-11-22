# P1015: a need's condition orders its candidates, and the score stays as it is: rows

Card: [P1015 #1476](https://github.com/xmejkal/spark/issues/1476). Seen in the p934-display walk, where the need
`screen` (indicate / display screen, condition `e-paper`) put the owned e-paper third. The plan council of 2026-11-22:
round 1 a lens on Sonnet and the refuter on Opus on plan v1, round 2 the refuter on Opus on plan v2. This file holds the
acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | v1 (the condition's words join the scored words) drops the PO's picked dfr0664-tft-2in on p581-sound-joystick and walk4 from first (1.0) to second (0.143) | plan council round 1, refuter | acted | v2: the condition changes only the order, never the score. The comparison on the PO's 7 projects keeps dfr0664-tft-2in first at 1.0 on both (PR body) |
| 2 | v1 lowers scores on other needs, and `--match` hides more (reaction-game's xiao-esp32-c6-fresh 0.5 to 0.111) | plan council round 1, refuter | acted | v2 keeps every score: scores, the hidden set, the plausible set (P976) and `_other_choice` are the same on all 14 needs with a condition (PR body) |
| 3 | v1's win on the walk rests on the one-letter word `e` of "e-paper" | plan council round 1, refuter | acted | fixed: `matching.condition_words` keeps a hyphenated word whole and drops one-letter words; rows 5 and 6 of `tests/mutations/p1015-condition-order.json` |
| 4 | v1's citations and "the guard" were wrong | plan council round 1, lens and refuter | acted | fixed in plan v2 |
| 5 | v2 makes four texts untrue: docs/guide/agents/scripts.md:139 ("come in one order"), needs.py's `_rank` and `candidates` docstrings, offers.py's "both say the same way (P783)" | plan council round 2, refuter | acted | fixed, one sentence each; the order sentence of docs/guide/journey/idea.md is a new bullet after the matcher sentence, not in it |
| 6 | the condition "e paper" does not find an offer's "e-paper" | plan council round 2, refuter | acted | fixed: on an offer's side (`condition_words(text, parts=True)`) a hyphenated word gives its parts as well; "paper e" still gives 0. `test_condition_words_keep_a_hyphenated_word_and_drop_one_letter`, `test_condition_overlap_counts_functions_and_tags_only`; row 7 |
| 7 | the key is a raw count with few filler words dropped: "a push button" lifts a joystick with "push button" | plan council round 2, refuter | acted | stated as a limit where the order is described (commands/idea.md, docs/guide/journey/idea.md, the P211 design note, scripts.md); no tuning |
| 8 | the rank_key test has no owned drawer entry, so a mutation that puts the overlap before `id is None` (P991) escapes | plan council round 2, refuter | acted | fixed: `test_the_condition_overlap_orders_inside_a_group_and_lifts_nothing_into_a_better_one` has an owned entry at 1.0 with overlap 1 below both owned records; row 9 ("overlap before id is None") and row 3 ("about texts count") added; row 6 cites test 1 only |
| 9 | `rank_key`'s new line moved the anchor of P991's three rows and P211's "candidates: the score does not order" | the build, `mutate.py --anchors` | acted | fixed: re-anchored on the same defects in the line with `-overlap`, each planted by hand and caught; main and the branch refuse the same 33 rows |
