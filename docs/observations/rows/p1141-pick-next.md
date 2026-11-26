# P1141: a next: line after a pick into a parts now, and --match and --needs read the picks: rows

Card: [P1141 #1676](https://github.com/xmejkal/spark/issues/1676). The PO's P829 walk of 2026-11-25, step 3 (walk
findings 3 and 4). The plan had two council rounds and the PO's approval on 2026-11-26, with the new words kept as
written. The reproduction ran on a scratch copy of the walk project and the store before the plan. This file holds the
acted, raised and rejected findings only. 2026-11-26.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a pick can still end with no `next:` line: the requirements phase at problems, or the needs phase stale, names no step | plan refuter (Opus), rounds 1 and 2 | raised | [P1181 #1725](https://github.com/xmejkal/spark/issues/1725) |
| 2 | `guide.now.needs` comes from the needs file, so a parts phase with problems or one that could not run would get a pick step | plan refuter (Opus), round 1 | acted | `parts_steps` names a step only for `not-started` or `partial`; a test with a need that has no `does` |
| 3 | `phase_readers.needs_holding` and `PickPlan.needs_picking` hold the pick-to-part rule twice, with two rules | plan refuter (Opus) round 1, plan lens (Sonnet) round 2 | acted | one rule, `PickPlan.picked_for`; `needs_holding` goes and `needs_picking` reads it; a test for an old entry pick of a record |
| 4 | a match on the key alone marks a record `led` and a drawer entry `led` both | plan refuter (Opus), round 2 | acted | `picked_for(key, kind)` compares `{kind: key}` after `as_record`; a test with both |
| 5 | the step functions have four signatures and the parts step would repeat `pick_step`'s NextStep | plan lens (Sonnet), round 2 | acted | `PHASE_STEPS`, one `(project, phase, guide)` function per phase; `offer_steps.picks_step` is the one shape of a pick's step |
| 6 | "free 1, this project holds 1" reads as two boards | plan lens (Sonnet), round 1 | acted | `free 1 (1 held by this project)`, the PO kept it |
| 7 | flow.md, scripts.md and json.md are at their line budgets | plan refuter (Opus), round 1 | acted | flow.md joins two lines for its new row; scripts.md and idea.md grow in place; json.md lists no candidate keys |
| 8 | eight mutation rows lose their anchors when the lines move | plan refuter (Opus), round 2 | acted | each re-anchored to its moved line with the same mutation; each still caught in a scratch copy |
| 9 | two new keys on every `--match` candidate double its pages (3 to 6 in the paging test) | the build | acted | `held_here` and `picked_for` appear only on a candidate the project holds or picks, as `stops_why` on a board that stops |
| 10 | three pick texts in `ThePicksTest` pin the text with no `next:` line | the build | acted | each now ends with the flow's parts step line, the line the card asks for |
| 11 | `test_an_unlisted_project_is_not_named_as_holding_its_own_board` read "held by" anywhere in the line | the build | acted | it reads `, held by` (a list of holders) and asserts `(1 held by this project)` |
| 12 | `test_a_review_right_after_the_drop_clears_the_idea_and_a_defining_write_does_not` pins `next == []` after the review, while its now is a parts phase with open needs | the build | acted | it asserts that the brief step goes and that the now's step is the parts pick |
| 13 | `free 3, held by alarm2 (1 held by this project)` reads as the other project's hold | PR lens (Sonnet) | acted | the own pieces come right after the free count, before `held by`; a test with both, and `test_a_match_names_who_holds_a_board_and_the_asking_project_is_left_out` reads the new order |
| 14 | flow.md's parts row says "more than one pick offer", but the step comes whenever the now names no offer, zero offers too | PR lens (Sonnet) | acted | "no one pick offer" |
| 15 | flow.md's paragraph above the table is one long line | PR lens (Sonnet) | rejected | flow.md is at its 400-line budget, and the new table row needs that line |
| 16 | `PHASE_STEPS` wraps `simulate_steps` in a lambda | PR lens (Sonnet) | acted | `simulate_steps(project, phase, guide=None)` takes the table's signature |
| 17 | `list_needs.picked_words` reads a pick's key itself | PR lens (Sonnet) | rejected | it is one line that only formats, and `needs.py` reads the same shape the same way in several places |
| 18 | `match` turns a candidate's kind None into "entry" before `picked_for` | PR lens (Sonnet) | rejected | in `picked_for` a kind of None means "any kind", the rule of `named_pick` and `needs_picking`; two meanings of None would be worse |
| 19 | `needs_picking` lost the need whose stored pick is a record's drawer entry: a refused hold names the stored key (`plan_holds`), which `picked_for` matched only as the record | PR refuter (Opus) | acted | with no kind, `picked_for` matches the key as stored or as its record; a test with the entry key |
| 20 | a drawer entry linked to a record whose file cannot be read is shown as its own candidate and never marked as picked | PR refuter (Opus) | rejected | a broken record file is a problem `--audit` names, and the entry's pieces still show as held here |
| 21 | with the stored-key arm, `named_pick` names a need whose old entry pick has a record id's key as its entry key, for another part | fix refuter (Opus) | acted | `named_pick` asks `picked_for(key, "part")`: its keys are part picks; a test with the collision |
| 22 | the `--match` line in every combination of own hold, other holders and counts; `simulate_steps` unchanged; no test bent | fix refuter (Opus) | verified | each rendered and read; `steps_of` is the only caller |
