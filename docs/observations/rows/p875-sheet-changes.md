# P875: the sheet keeps the list of changes since the last sheet spark wrote for another design: rows

Card: [P875 #1243](https://github.com/xmejkal/spark/issues/1243), a story. New logic: a plan check, a plan council (one
lens on Sonnet, the refuter on Fable, reproducing the bug) and a review of the PR. This file holds the acted and raised
findings only (rules.md). 2026-11-17.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | C1: no clock is passed down | plan council | acted | `write` keeps its signature; the Store takes `SystemClock`; tests set `at` in the record; a row says a carry-on never takes this build's time |
| 2 | C2: the four-argument calls of `from_build` must keep working | plan council | acted | `at` has a default of `None` |
| 3 | C3: fewest edits to existing tests | plan council | acted | `WiringLog.read` and `FILE_NAME` stay; only `write` moved to `WiringLogStore`, and one test changed its two calls (`test_breadboard_changes.py`, the write-whole-or-not-at-all test); `StagedFile.from_bytes` |
| 4 | C4: no `since` key on the `changed` entries | plan council | acted | `since` is on `WriteResult` and on the sheet's `wrote` entry only |
| 5 | C5: the helper of `test_breadboard_record.py` finds only the old heading | plan council, then the coordinator | acted | the heading with a base starts with other words, so `SECTION` and `section()` follow the card's Done-when 3 (the coordinator's ruling); no expected value changed |
| 6 | C6: a missing folder of `out` must name `out` | plan council | acted | `write` checks the folder before it stages; the golden `bad-out` is unchanged |
| 7 | C7: the order of the writes | plan council | acted | render every text, stage the record, write the sheet, commit the record, then the drawings; the stage is removed in a `finally`; a test with a folder at the sheet's name |
| 8 | C8: a leftover stage says P874's sentence | plan council | acted | `STAGE_IN_THE_WAY` moved to `build_record.py`, and `StageTakenError` says it, so `breadboard.py` says it too; `kept_files.py` lost a line |
| 9 | C9: words for a person | plan council | acted | the heading shows the time as `2026-11-17 10:32`; one line says to count from that sheet only if the person wired it |
| 10 | C10: tests and rows | plan council | acted | a test for a sheet that cannot be written; T2's list half, T7's list half and the A, B, A test are pins and have rows; the row "changes-never" of `p300-change-list.json` is re-anchored with the same meaning |
| 11 | C11: the goldens | plan council | acted | four record dumps gain `at` and `base`; `breadboard-ok-rebuild.txt` gets the new heading and the line; `golden_bench.scrub` hides the heading's time |
| 12 | C12 (i): the list and the `changed` entries repeat on every rebuild until another design, also after the person wired it (the PO's Q10) | plan council | raised | a card, filed by the coordinator before the merge |
| 13 | C12 (ii): a broken record, then B, B: the second B says "Nothing to change on the bench." with no base, as today | plan council | raised | a card, filed by the coordinator before the merge |
| 14 | C13: the docs | plan council | acted | `bench_changes.py`'s docstring, `commands/build.md`, `scripts.md`, `json.md`, `recorded-run.md`, `never-assume.md` and the help of `breadboard.py` say the base and the time |
