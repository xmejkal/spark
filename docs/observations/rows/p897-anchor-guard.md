# P897 PR 2: the push hook checks every mutation row's anchor: rows

Card: [P897 #1273](https://github.com/xmejkal/spark/issues/1273), PR 2 of 2 (the row repairs were PR 1,
[#1620](https://github.com/xmejkal/spark/pull/1620)). Rows 1 to 4 are the plan check's and the build's: where the plan
did not hold in the code, and what the build did.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Every open branch is refused at its next push until it merges main | the plan, section 6 | rejected | dropped because `tools/pre-push` runs each branch's own copy of `check_commit.py`: a branch meets the guard only after it merges main, where the rows are fixed. The risk is written nowhere |
| 2 | The guard reverses P208's decision of 2026-10-12, "The push gate no longer checks the old tables' anchors" | the plan, section 6 | raised | the PR is a draft and waits for the PO's yes. Destination: the PO's decision on the PR; W3 of 2026-11-08 made the rows current again, and P897's done-when asks for the gate |
| 3 | `mutate.anchors` and `mutate.unloadable` put `table[index]` before a row's name (plan, section 3, row 5 of the mutation rows) | the plan, section 3 | acted | `refused_rows` in `tools/check_commit.py` builds each row's name as `table[index] name` itself, so `mutate.py` and its tests stay as they are. The mutation row on that name is not written: the gate test asserts `t.json[0] add becomes sub` |
| 4 | The six rows of `tests/mutations/p897-row-anchors.json` are each caught by the test they name | the build | closed | each planted by hand in a scratch copy of the tree, with `tests.test_check_commit` run: rows 1, 2, 3, 4 and 6 fail one to three tests of `TheGateChecksTheMutationRowsTest`, row 5 errors the not-JSON test. `--anchors` on the file says every anchor present, once |
