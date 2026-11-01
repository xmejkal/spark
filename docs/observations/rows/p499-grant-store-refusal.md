# P499 grant store refusal: rows

What the P499 fix (card #684) found. The P496 refuter (PR #683) raised the bug, and the P496 reviewer two more points.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Every caller of the store catches StoreProblem | P496 refuter 3 | rejected | `grant.py`'s `main` caught neither OSError nor StoreProblem around `GrantService.issue`, which ends in `store.write_json`; it now catches StoreProblem beside `ToolProblem` and prints `grant.py: <why>`, exit 2; test |
| 2 | `_make_ready`'s chmod calls are covered by the new try | P496 reviewer 2 | rejected | they sat after it; the loop now runs inside the same try, so a chmod failure is the same refusal |
| 3 | The "folder spark may not write" case has a test | P496 reviewer 3 | acted | `test_a_folder_spark_may_not_write_is_refused_the_same_way` (a 0500 folder) |
| 4 | OSError belongs in grant.py's except too | plan check | rejected | the store turns its own OSErrors into StoreProblem since P496; catching OSError in grant.py would also swallow port and console errors that have their own stop lines |
