# P499 grant store refusal: rows

What the P499 fix (card #684) found. The P496 refuter (PR #683) raised the bug, and the P496 reviewer two more points.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Every caller of the store catches StoreProblem | P496 refuter 3 | rejected | `grant.py`'s `main` caught neither OSError nor StoreProblem around `GrantService.issue`, which ends in `store.write_json`; it now catches StoreProblem beside `ToolProblem` and prints `grant.py: <why>`, exit 2; test |
| 2 | `_make_ready`'s chmod calls are covered by the new try | P496 reviewer 2 | rejected | they sat after it; the loop now runs inside the same try, so a chmod failure is the same refusal; `test_a_folder_spark_may_not_tighten_is_refused_the_same_way` replaces `os.chmod` with one that refuses (main gave a raw PermissionError) |
| 3 | The "folder spark may not write" case has a test | P496 reviewer 3 | acted | `test_a_folder_spark_may_not_write_is_refused_the_same_way` (a 0500 folder: the mkdir fails, already caught since P496) |
| 4 | OSError belongs in grant.py's except too | plan check | rejected | the store turns its own OSErrors into StoreProblem since P496; catching OSError in grant.py would also swallow port and console errors that have their own stop lines |
| 5 | The 0500-folder test proves the moved chmod | PR reviewer 1, PR refuter 1 | rejected | it passed with main's store.py, because the mkdir fails first; a second test makes the chmod refuse |
| 6 | `for folder in {...} if private else ():` reads well | PR reviewer 2 | rejected | the condition hid in the loop header and a set has no order; `if private:` and a tuple |
| 7 | `--check --json` with a store that refuses says could-not-run | PR refuter 2 | raised | it answers `why: no grant`, exit 1, on main and here: a later card |
| 8 | Every writer of the store catches StoreProblem | PR refuter 4 | raised | `deploy_record_store.py:101` and `drawer.py:323` catch neither; the parts.py callers were not checked |
| 9 | The SPARK_HOME restore can use mock.patch.dict | PR reviewer 3 | rejected | tests/test_store.py sits at its T2 budget of 13 mock.patch |
