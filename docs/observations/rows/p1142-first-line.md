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
| 6 | "has a goal" is ruled twice: the idea strips a blank goal, `stamp_of` stamps it | the lens | acted | one `Brief.has_goal` for both; `test_a_blank_goal_gives_no_record_and_no_line` and two mutation rows |
| 7 | "no goal in the brief yet: Claude writes it from your words" under DONE reads as work to do | the lens and the refuter | acted | the fact only: "the brief holds no goal". The instruction stays in `IDEA_NOW` |
| 8 | no test pins "now is the idea" for a stale idea that holds a goal | the lens | acted | `test_a_stale_idea_with_a_goal_and_no_need_left_is_still_now` and a row that turns `!= OK` into `!= STALE` |
| 9 | the goal text goes into `data.phases`, `--json` and the page's developer fold, and `Privacy` masks paths and secrets only | the lens | acted | one sentence in `docs/guide/agents/flow.md`; no mask |
| 10 | the idea's mark on the page changes, so P1135's goldens can meet the same line | the lens | acted | the PR body names `tests/golden-design/flow-ok-page.txt` line 80 for the owner of P1135 #1670 |
| 11 | "`Brief.from_project` is the only reader of `.spark/project.json`" is too wide | the refuter | acted | the claim reads "the only reader of the brief in the flow"; `project_setup.py` reads it to write it and is not touched |
| 12 | the test line is 1603, not 1602 | the refuter | acted | the assertion was rewritten at its place |
| 13 | the fingerprint does not hold the brief, so a page made before the goal was written stays current | the refuter | raised | out of scope and older than this card. A card is proposed to spark-main (not filed by the builder) |
| 14 | "a goal and no needs" (the needs are now) breaks hand-written projects | the refuter | rejected | on `button-light` the needs status is `null`, so the rule never fires and NOW stays build; without it the first line asks for a goal that is set |
| 15 | moving the guide lines first breaks another reader of show's lines | the refuter | rejected | `run_request` builds its own lines; the flow's page, reading, wired-board, deploy, run-request, tabbed-page, journey and script tests pass |
