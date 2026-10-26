# P416: a last deploy the look could not check is unchecked, findings rows

Findings from the plan council, the build and the review of P416 (2026-10-26, Prague, auto mode).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Only the look's status and envelope need to change | plan | rejected | a deploy grant answered yes on `verdict == match`, so it erased while the last-deploy record could not be read (the gate test erased on main, exit 0). The grant now falls back to the typed yes, `WHY_LAST_DEPLOY_NOT_CHECKED` |
| 2 | The text look needs no new line | plan | rejected | a person reads "all fields match" and a token with exit 2 and no cause. The look prints "last deploy not checked: <why>: <fix>." |
| 3 | The golden harness can plant a store file | plan | acted | it could not: `Case.plant` writes (path, text) pairs into the run's store. New golden `look-could-not-run-last-deploy-not-checked.json` |
| 4 | The grant tests' fake look is neutral | build | acted | a `Mock`'s `last_deploy_not_checked()` returned a true-ish Mock, so 9 tests fell back to the terminal. The fake says False unless asked |
| 5 | A test may name the reason by its constant | build | rejected | `test_self_confirmation` forbids it: the test names "last deploy not checked" as text |
| 6 | deploy.py offers a grant only where one can cover the deploy | review, refuter | acted | it offered the grant line and `grant_argv` for a not-checked look. `board_grant.grant_may_cover` is the one predicate for both sites. A planted removal of its last-deploy term is caught |
| 7 | The no-MAC look's fix sentence helps | review | acted | it repeated the no-token item's words. It says to reconnect the board, and a test pins the two unchecked items |
| 8 | The fix sentence must not print a home path | review, refuter | rejected | the person must repair or remove that file, so the path is the help. Goldens mask it as `<store>`, and deploy.py already prints absolute project paths |
| 9 | `record_path` is the one place of the path | refuter | raised | the writer reads through it but writes with `store.write_json("boards", key)`, which builds the same path again. The same file, so harmless. The records move (wave 6) gives the store record one owner |
| 10 | The look's deploy step names a grant only where it can stand | refuter | raised | `yes_rule` says "(or a deploy grant stands)" whatever the look, as it did for warning looks before this PR. A later card can pass the report to `yes_rule` |
| 11 | The mutation run catches every planted defect | mutation-tester | acted | 11 planted, 11 caught, on b287d1c. One more row on the final predicate (row 6) |
| 12 | The live grant needs the same rule | refuter | rejected | a live grant neither erases nor reads the last deploy |
