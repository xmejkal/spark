# P496 store path that is a file: rows

What the P496 fix (card #678) found. The P487 refuter (PR #675) raised the bug.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `init_project.py` writes its files when the store refuses | P487 refuter 5 | rejected | with SPARK_HOME on a file, `store._make_ready`'s mkdir raised FileExistsError, which `init_project.py:429-432` does not catch; init crashed and wrote nothing |
| 2 | The fix belongs in `init_project.py` | plan check | rejected | the store's own write path raises a bare OSError for every caller (`parts.py --step` too); `_make_ready` now raises StoreProblem with the way out ("point SPARK_HOME at a folder") |
| 3 | A test can set SPARK_HOME with `mock.patch.dict` | build | rejected | `tests/test_store.py` sits at its T2 budget of 13 `mock.patch`; the test sets the variable and restores it in a cleanup |
