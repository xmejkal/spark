# P514 needs-drop (--needs-drop PROJECT NEED): rows

What the plan council's two rounds found, and what the build changed against the plan. Card:
[P514 #710](https://github.com/xmejkal/spark/issues/710). Plan: `~/.claude/plans/p514-needs-drop.md`.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | One data key for the drop, `dropped`; `released` and `written` keep `--pick`'s shape | round 1, lens | acted | `DropNeed.run`, the OPERATIONS row |
| 2 | The line numbers are the checked ones | round 1, lens | acted | the build re-checked each claim in the code (rows 14 to 17 are the ones that were off) |
| 3 | No outside builder in the new area: `_op_needs_drop` calls core's `build_outside_world(effects, Reporter())` | round 1, lens | acted | parts.py `_op_needs_drop` |
| 4 | `plan_holds` returns drawer changes (plus notes and problems, round 2); `known` is not a parameter | round 1, lens and refuter | acted | needs.py `plan_holds(name, after, entries)` |
| 5 | The area is `scripts/spark/idea/`, named for the idea stage | round 1, lens | acted | scripts/spark/idea/, patterns-and-names.md |
| 6 | One word: a hold is released; `_released` moves to needs.py as `released_holds` | round 1, lens | acted | needs.py, parts.py `_op_pick` |
| 7 | The missing-need sentence serves a retry and lists the ids | round 1, lens | acted | `NEED_UNKNOWN_SENTENCE`, tested with the literal |
| 8 | The requirements note is a `notes` entry and a line, compares the pick's record id, says who runs what | round 1, lens and refuter | acted | `needs.parts_left_listed`, two tests (an entry pick, a part another need keeps) |
| 9 | A crash's diagnostics go to stderr from `_op_needs_drop`; DropNeed wraps a StoreProblem | round 1, refuter | acted | `_op_needs_drop`, `DropNeed.run`, the no-JSON test |
| 10 | The codes live in an area table | round 1, refuter | acted | scripts/spark/idea/idea_codes.py (the file name changed: row 14) |
| 11 | `held_by` and another project's hold are tested on two entries | round 1, refuter | acted | two tests in TheNeedsDropTest |
| 12 | `plan_holds` returns `(changes, notes, problems)`; a missing need is a Finding with data, not a raise | round 2, refuter | acted | needs.py, `DropNeed.run` |
| 13 | The 17 mutation rows in the hold loop and 2 next to it still find their anchors | round 2, refuter | acted | `mutate.py --anchors` on the four tables: every anchor present, once |
| 14 | The area codes file is `spark/idea/codes.py` | the plan | raised, wrong | rule C1 wants one file name under scripts/, and `spark/core/codes.py` has it: renamed `idea_codes.py`, as `board_codes.py` is for the bench |
| 15 | `tools/mutate.py --check` | the plan | raised, wrong | the flag is `--anchors` |
| 16 | The hold code is needs.py:413-436 and :442-447 | the plan | raised, wrong | it was :417-440 and :448-452 on this main (the `wanted` counter belongs to it too); moved whole, the notes and problems spliced where they were |
| 17 | The area codes table is checked by nothing, because `code` never reaches parts.py's envelope | round 2, NIT | acted | said in the PR; the Finding carries the code for a core frontend |
| 18 | Step 1's red test and step 2's refactor cannot be pushed alone: the hook runs the suite, and the tests stay red until step 4 | the build | raised | commits 1 to 4 were pushed together |
| 19 | `<module>` of needs.py rose 769 to 811 and parts.py 2373 to 2384; `plan_pick` left the R1 list (`--accept` refuses a risen value) | the build | acted | `measure.py --rules --accept-new`, the reason is the moved loop and the new row and handler |
| 20 | A hold given by hand that no pick explains is released too by a drop, as `--pick` does | the build | raised | the plan releases what `plan_holds` lowers; a drop of an unrelated need also frees such a hold, and the dry run says so |
| 21 | docs/guide/agents.md gets one example | the plan | raised | every doc is at its line budget, so the example went on an existing line of scripts.md; agents.md has no natural place |
| 22 | The mutation table has 8 rows, and the write-order row needs a test | the build | acted | `test_a_drawer_that_refuses_the_write_leaves_the_needs_file_as_it_was_so_a_retry_finishes`, with a fake drawer through the constructor |
