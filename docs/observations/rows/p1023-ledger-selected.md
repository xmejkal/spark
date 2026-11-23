# P1023: a change to a mutation table selects test_ledger: rows

Card: [P1023 #1495](https://github.com/xmejkal/spark/issues/1495). Plan: XS, one plan check by the refuter (Opus). This
file holds the acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `tests/mutations/` sat in `NO_TEST_OF_THEIR_OWN`, so a changed table selected no test, and P1021 and P1017 pushed the critical rows to 51 against the cap of 50 | main went red, 2026-11-23 | acted | the folder maps to `test_ledger`, as the converter's folder maps to `test_converter`; PR #1494 fixed main first |
| 2 | no mutation row anchors on the lines the change touches | the plan check, the refuter | verified | `tools/mutate.py --anchors tests/mutations/*.json`: 4561 mutation(s) in 390 table(s): 33 would be refused, the same 33 as main |
| 3 | `ledger.jsonl` sits in the same folder, and a sweep commit changes it | the plan check, the refuter | verified | `tests/test_ledger.py` reads the real ledger, so selecting it is right; the new test names both files |
| 4 | no other test reads the repository's tables | the plan check, the refuter | verified | `tests/test_mutate.py` builds its own tables in temp roots; `tests/test_orphans.py` leaves the folder out |
| 5 | `test_a_document_and_a_mutation_table_need_only_the_always_list` pinned the behaviour this card changes | the plan check, the refuter | acted | the table leaves that test, renamed `test_a_document_needs_only_the_always_list`; the card's Done-when changes what it pinned |
| 6 | the new test needs `test_ledger` in the fake test list, and adding it to the shared list moved another test's count | the build | acted | the new test passes its own list, `dict(TESTS, test_ledger="")`, so no other expectation moves |
| 7 | the docs step: `docs/guide/developing.md` does not list what each folder selects | the plan check, the refuter | rejected | the plan's condition is false, so no doc changes |
| 8 | the PR review found nothing to fix: a table or the ledger adds only `test_ledger`, other selections are the same on main and the branch, the anchors are 33, the row is caught | the PR review, the lens (Sonnet) and the refuter (Opus) | verified | the refuter ran `story_tests.select` on the real tree with the branch's and main's code |
| 9 | a PR that only deletes or renames a scripts file named by a critical row does not select `test_ledger` | the PR review, the refuter | rejected | older than this PR, and each PR's `tools/mutate.py --anchors` refuses a row whose file is gone, a count checked before every merge |
