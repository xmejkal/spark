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
| 12 | C12 (i): the list and the `changed` entries repeat on every rebuild until another design, also after the person wired it (the PO's Q10) | plan council | raised | a line on P873 #1241 (the person's word as a witness) |
| 13 | C12 (ii): a broken record, then B, B: the second B says "Nothing to change on the bench." with no base, as today | plan council | raised | P894 #1268 |
| 14 | C13: the docs | plan council | acted | `bench_changes.py`'s docstring, `commands/build.md`, `scripts.md`, `json.md`, `recorded-run.md`, `never-assume.md` and the help of `breadboard.py` say the base and the time |
| 15 | M1: `recorded-run.md` showed the old heading as what a rebuild gets | PR lens | acted | one sentence says the recording is from 2026-10-18 and what the heading and the line are today |
| 16 | M2: the helper hides a stray paragraph under the first-design heading | PR refuter | acted | the first-design test asserts that the note is not in the sheet; a row prints it, and the test caught it once by hand |
| 17 | F1: an `at` the local zone cannot say (`9999-12-31T23:59:59+00:00`, `0001-01-01T00:00:00`) crashed every build | PR refuter | acted | `_time` says the time as the heading does, and `read` takes OverflowError as an unreadable record; a test and a row |
| 18 | F2: three guards no test caught: a record that is a link, a stage whose own write fails, a base with a garbage time | PR refuter | acted | a test and a row each (the stage test sets a file size limit, so it needs no mock) |
| 19 | F3: two rows had the same find and replace | PR refuter | acted | the p300 row "changes-never" stays; the p875 duplicate "the base is never listed" is dropped |
| 20 | W1 to W4: the words under the heading, the heading with no time, the docs, the names | PR lens | acted | the line names the time (or "that earlier sheet"); the heading says "(spark did not note when)"; `LAST_BUILD_HEADING`; the docs say `since` is absent when unknown |
| 21 | the sheet does not print its own time | PR lens | raised | P894 #1268 |
| 22 | the command line does not say the time beside its `change:` lines | PR lens | raised | P894 #1268 |
