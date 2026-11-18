# P920: a registered project records its deploys (`bench.py register`, `bench.py record`): rows

Card: [P920 #1302](https://github.com/xmejkal/spark/issues/1302), a story, PR #1306. New logic: one lens on Sonnet and
one refuter on Opus read the branch. The refuter planted 44 faults by hand, and 7 escaped the tests. This file holds the
acted, raised and rejected findings only (rules.md). 2026-11-18.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `register` takes a blank `--tool` or `--origin`, so a recorded deploy reads as spark's own, with no "not by spark" and no "by" | the refuter (REF-1) and the lens (LENS-2) | acted | fixed: a blank, space-only or unprintable origin or tool is refused with the new code `blank_value`, before anything is written. A test and two mutation rows |
| 2 | when the launcher's write fails after the registration was written, the run says "Not registered." and the name is on disk | the lens (LENS-1) and the refuter (REF-2) | acted | fixed: the order stays. The stop says that the name is registered and the launcher was not written, `data` holds the registration with `launcher` null, and the fix runs the same command again. A test and a mutation row |
| 3 | the store stop of `register` has an empty fix | the lens (LENS-3) | acted | fixed: every stop of `register` names the next command. A test and a mutation row |
| 4 | the grouping reads `made_by` with no type check, so a hand-edited `made_by: [1]` makes `show` raise | the lens (LENS-4) | acted | fixed: one helper, `deploy_record_store.made_by_of`, for the last deploy and the grouping. A test and a mutation row |
| 5 | an unreadable `projects.json` ends `register` as a crash with PermissionError | the refuter (REF-3) | acted | fixed: `store.projects()` raises StoreError `file_refused` for an OSError. No existing test pins that path. A test and a mutation row |
| 6 | a folder in the place of `boards/<mac>.json` ends `record` as a crash at the rename | the refuter (REF-4) | acted | fixed: `append_deploy` refuses it with `not_a_board_record`, for spark's own deploys too. A test and a mutation row |
| 7 | the launcher passes the caller's environment on, so a caller with another `SPARK_HOME` or `XDG_DATA_HOME` reaches another store | the refuter (REF-5) | acted | fixed: the launcher sets its child's `SPARK_HOME` to the folder above its own, found at run time. Tests for another store, and for a store path with a space and a quote. The agents' page names `XDG_DATA_HOME` |
| 8 | `write_deploy` no longer writes a None board over the record's board, as main did | the lens (LENS-6) | acted | fixed: only an outside deploy keeps the record's board (`KEEP_BOARD`). A test of `write_deploy` and a mutation row |
| 9 | 7 hand faults escape: no lock in `register`, a registration that drops the other names, `OSError` removed from `_read_all`, `is_file` for `exists`, another Python in the launcher, and the raw time in the two maker sentences. Also: a taken name must not write the launcher | the refuter (REF-6) and the lens (LENS-5) | acted | fixed: a test for each. The lock test holds the store's lock in another thread and sees that `register` waits. 16 new mutation rows in all, 40 in the table |
| 10 | `agents/bench.md` says that each stop says "Nothing was written.", which is on stderr only for some codes, and leaves out a gone Python | the lens (LENS-7, LENS-8) | acted | fixed: the page says where each sentence is, and that no JSON also means that the Python which runs the launcher is gone |
| 11 | exit 1 for a refused name | the plan council | rejected | dropped because a refusal is a could-not-run with its code, as every store refusal is |
| 12 | the prefix "spark's last deploy here:" contradicts "not by spark" | the refuter (REF-7) | rejected | dropped because the plan's round 2 chose one prefix for every state |
| 13 | a 200 character name registers | the refuter | rejected | dropped because the name is a JSON key, and no file is named by it |
| 14 | show's `last` date is the stored text's first ten characters, not the machine's zone | the refuter | raised | a card, filed by the coordinator: P923, to be filed |
