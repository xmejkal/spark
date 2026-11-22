# P980: the guide's done and now are true in two cases: rows

Card: [P980 #1414](https://github.com/xmejkal/spark/issues/1414). This file holds the findings of the plan check (the
refuter on Opus), 2026-11-22.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | "Hand-written" is not the only state with no needs: `--needs-drop` of the last need writes `{"needs": []}` and keeps requirements.json | plan check, refuter | acted | the label is `requirements (no needs or picks behind it)`, the constant `REQUIREMENTS_NO_PICKS`; flow.md names both states |
| 2 | `HAND_WRITTEN_MESSAGE` ("a hand-written project: requirements.json and no needs") has the same mislabel | plan check, refuter | raised | card [P984 #1428](https://github.com/xmejkal/spark/issues/1428) |
| 3 | The all-aside branch must come before the NEEDS branch in `now_phase`, or the p977-guide row "a fresh project starts at the needs, not the idea" loses its anchor | plan check, refuter | acted | placed before it; `--anchors` over all tables |
| 4 | flow.md said `done` names the phases before now, and `stands_at` can say requirements while `guide.now` says parts | plan check, refuter | acted | `docs/guide/agents/flow.md` says both |
| 5 | With every need aside the requirements offer stays on the page and a click is refused | plan check, refuter | raised | named in flow.md; a later card if it bites |
| 6 | With every need aside and a requirements phase that could not run, now hid the failure | PR refuter | acted | the redirect applies only when the requirements phase is not could-not-run; test and mutation row 5 |
| 7 | No test for `needs: []` (last need dropped, requirements.json kept) | PR refuter | acted | `test_a_project_whose_last_need_was_dropped_lists_no_needs_or_parts_as_done` |
| 8 | Names say hand-written, the label does not | PR lens | acted | `has_no_picks`, `no_picks`, docstring and flow.md reworded; `HAND_WRITTEN_MESSAGE` stays (P984) |
| 9 | `next(...)` in `now_phase` could raise StopIteration on a swapped phase list | PR lens | acted | `next(..., now)` |
| 10 | `ALL_ASIDE_NOW` too long | PR lens | acted | "Every need is set aside, so no pick can make the parts list. Tell Claude which need to bring back, then pick a part." |
| 11 | flow.md paragraph held two cases and "a later card may hide it" | PR lens | acted | two paragraphs; tells the agent not to run the requirements offer |
