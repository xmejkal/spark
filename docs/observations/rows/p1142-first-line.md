# P1142: a done idea says its goal, and show's first line is the next step: rows

Card: [P1142 #1677](https://github.com/xmejkal/spark/issues/1677). Found in the PO's P829 walk, 2026-11-25: `flow.py show` listed
a done idea as to do, and its first line was not the next step. The plan council ran on 2026-11-26, about 09:28 to 09:38 CET
(one lens on Sonnet, the refuter on Opus). This file holds the acted, raised and rejected findings only. 2026-11-26.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `phase_readers.py` grows from 596 to 608 lines, and `test_architecture` R1 (600 lines) fails | the refuter, confirmed by a run | acted | the read of the brief is `Brief.read` in `records/brief.py`; `phase_readers.py` is 597 lines and `test_architecture` passes |
| 2 | `tests/test_needs_dropped.py` (`TheBriefStepTest`) goes red and the plan did not name it | the refuter, confirmed by a run | acted | its idea assertion `(None, "ok")` became `("ok", "ok")`, named in the PR body |
| 3 | `NEEDS_NOW` on the first line of `NOW_SENTENCES` breaks the anchor of a p1027 row | the refuter, `--anchors` | acted | the entry stands on its own line after `(NEEDS, STALE)`, as `(NEEDS, NOT_STARTED)` (the status the needs phase has with no need; the plan's `(NEEDS, None)` is a slip) |
| 4 | the move re-anchors exactly two p1027 rows | the refuter | acted | the two rows now point at `Brief.read` in `brief.py`; a third p1027 row (`stamp_of`) was re-anchored for `has_goal`; `tools/mutate.py --anchors` passes |
| 5 | a `must` that is not a list makes the idea say "cannot be read" and NOW ask for a goal the brief holds | the lens and the refuter, confirmed by a run | acted | a goal is said whatever `must` holds; `test_a_goal_is_said_whatever_must_holds` and `test_a_goal_with_no_needs_starts_with_the_needs_and_not_the_goal_question` |
| 6 | "has a goal" is ruled twice: the idea strips a blank goal, `stamp_of` stamps it | the lens | acted | `Brief.has_goal` is the idea's rule. The build used it in `stamp_of` too, and the review (row 17) took that back: the stamp sees every change of the goal's text, a blank goal too, and its docstring says so |
| 7 | "no goal in the brief yet: Claude writes it from your words" under DONE reads as work to do | the lens and the refuter | acted | the fact only: "the brief holds no goal". The instruction stays in `IDEA_NOW` |
| 8 | no test pins "now is the idea" for a stale idea that holds a goal | the lens | acted | `test_a_stale_idea_with_a_goal_and_no_need_left_is_still_now` pins it as a guard. A stale idea is open, so it is now before the needs rule is read; the row that turned `!= OK` into `!= STALE` was a duplicate of the `!= OK` row and is dropped (row 18) |
| 9 | the goal text goes into `data.phases`, `--json` and the page's developer fold, and `Privacy` masks paths and secrets only | the lens | acted | one sentence in `docs/guide/agents/flow.md`; no mask |
| 10 | the idea's mark on the page changes, so P1135's goldens can meet the same line | the lens | acted | the PR body names `tests/golden-design/flow-ok-page.txt` line 80 for the owner of P1135 #1670 |
| 11 | "`Brief.from_project` is the only reader of `.spark/project.json`" is too wide | the refuter | acted | the claim reads "the only reader of the brief in the flow"; `project_setup.py` reads it to write it and is not touched |
| 12 | the test line is 1603, not 1602 | the refuter | acted | the assertion was rewritten at its place |
| 13 | the fingerprint does not hold the brief, so a page made before the goal was written stays current | the refuter | raised | out of scope and older than this card: [P1195 #1743](https://github.com/xmejkal/spark/issues/1743) |
| 14 | "a goal and no needs" (the needs are now) breaks hand-written projects | the refuter | rejected | on `button-light` the needs status is `null`, so the rule never fires and NOW stays build; without it the first line asks for a goal that is set |
| 15 | moving the guide lines first breaks another reader of show's lines | the refuter | rejected | `run_request` builds its own lines; the flow's page, reading, wired-board, deploy, run-request, tabbed-page, journey and script tests pass |
| 16 | the review ran on the five commits: one lens on Sonnet, the refuter on Opus, 2026-11-26 | the review | acted | rows 17 to 21 |
| 17 | `has_goal` in `stamp_of` hides a goal blanked after the needs: the needs stay ok and NOW moves on, and a review under a blank goal leaves the idea stale | the refuter, confirmed by a run | acted | `stamp_of` keeps `brief.goal is None`; `test_a_goal_blanked_after_the_needs_makes_them_out_of_date` and its mutation row replace the blank-goal stamp test and row |
| 18 | the mutation row "only a stale idea gives way to the needs" names a test that does not catch it | the refuter, by a planted run | acted | the row makes the same change as the `!= OK` row (the ok idea stays now), so it is dropped |
| 19 | `Brief.read` and `Brief.has_goal` have no test of their own | the lens | acted | `test_read_gives_the_brief_and_why_it_cannot_be_read` and `test_has_goal_is_true_for_a_text_with_a_character_other_than_white_space` in `tests/test_brief.py` |
| 20 | the new `--help` sentences are lines of 184 and 248 characters | the lens | acted | the first paragraph of `flow.py`'s EPILOG is wrapped at 120 columns |
| 21 | a hand-written project says `DONE: idea` and also "the brief holds no goal" | the lens | rejected | the line states a fact, not work to do, and the first line is the next step; the card's done-when holds |
