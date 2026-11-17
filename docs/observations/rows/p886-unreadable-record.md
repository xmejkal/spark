# P886: a build record with a wrong shape is one sentence, not a traceback: rows

Card: [P886 #1256](https://github.com/xmejkal/spark/issues/1256), an XS bug. One plan check (no council round) and a build
to the plan, with the coordinator's rulings. This file holds the acted and raised findings only (rules.md). 2026-11-17.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the fix is one function, `is_build_record`, in the one place that reads the record (`BuildRecordStore.read`); no reader and no class changes | plan check | acted | `scripts/spark/build/build_record.py` only; the error type, the code and the sentence are the old ones |
| 2 | `stages` of 0, "" or {} is now unreadable, and an unreadable record holds no sha256, so the build leaves `board.tsx` alone | plan check | acted | said in the PR; `test_an_unreadable_record_holds_no_sha256` |
| 3 | the one existing test that changes is the keep step's: the page is now written, so the "(TypeError)" line is gone for this record | plan check | acted | renamed `test_an_unreadable_record_still_gets_its_page_from_the_build`; `test_a_flow_page_that_raises_is_one_no_page_entry` keeps the keep step's own catch under test |
| 4 | `flow.py page` keeps exit 0 with the sentence in `page.html`, as for a record that is not JSON | the coordinator's ruling | acted | no change to `write_flow_page.py` |
| 5 | `missing_facts: 5` and `requirements: 5` crash the same way, so the same function refuses them | the coordinator's ruling | acted | a test and a mutation row each; both crashed on main when run |
