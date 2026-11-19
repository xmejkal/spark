# P922: one lock for one store, whatever the process's environment: rows

Card: [P922 #1305](https://github.com/xmejkal/spark/issues/1305), from the plan council of P920. This file holds the
acted, raised and rejected findings only. The review: one plan check and one lens on Sonnet, and the refuter on Opus
(6 claims: 3 hold, 3 refuted). 2026-11-19.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the lock makes the store's folder, so a dry run or a refused write with a store inside a git tree leaves an empty folder | the plan check, finding 1 and 5 | acted | fixed: a folder that the lock's own `mkdir` made goes again when it is empty (`_remove_empty`), with a test |
| 2 | a home that is a file is a bare `OSError` and not the store's refusal | the plan check, finding 4 | acted | fixed: `store_not_writable`, with the words of `_make_ready` that a test of `grant.py` pins |
| 3 | six to eight processes on a store that does not exist leave the empty folders, 3 of 3 runs | the refuter, claim c | acted | fixed for the store's folder: only an own `mkdir` counts as made. A folder above it can still stay, see row 8 |
| 4 | the same race refuses a good home with `store_not_writable` in about 1% of the rounds (ENOENT, EEXIST, EINVAL) | the refuter, claim e | acted | fixed: `_hold_home` starts again, up to 100 times. A test with 6 processes and 150 rounds each: none is refused, no two are inside at once |
| 5 | a relative `SPARK_HOME` and a changed working folder inside the lock leave the made folder | the lens, question 1 | acted | fixed: the helper takes the whole path once |
| 6 | an error of `flock` leaves the folder open | the refuter, not checked | acted | fixed: `_take` closes it and raises |
| 7 | a store folder with mode 0300, and a missing home under a read-only folder, were let through by main's lock and are refused now | the refuter, claim f | rejected | dropped because spark reads its store's folders in every run, so a folder it cannot open is no store, and a home that cannot be made fails at the write on main too |
| 8 | an empty folder above the store can stay when several processes take a store that does not exist at one moment | the fix of row 3, seen in its test | rejected | dropped because the folder is empty, git does not show it, and a lock that covers the folders above needs a second lock. The docstring of `locked()` and the test say the limit |
| 9 | the start time 2 s ahead and the 0.5 s sleep can pass with no overlap on a loaded machine | the lens, question 3 | rejected | dropped because the tests then pass and do not fail falsely, and the mutation rows hold the two paths |
| 10 | `flock` on a folder is not probed on Linux and on a network drive | the lens and the refuter | rejected | dropped because no store is on a network drive today. The PR's body names the limit |
