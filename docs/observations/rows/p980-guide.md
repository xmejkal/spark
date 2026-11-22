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
