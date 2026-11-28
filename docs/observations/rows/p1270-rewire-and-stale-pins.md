# P1270 (#1829): rewire and stale pin names: rows

Card: [P1270 #1829](https://github.com/xmejkal/spark/issues/1829). This file holds the acted, raised and rejected findings only. 2026-11-28.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Q1: a check record or a board log later than the sheet closes the rewire | the plan council | acted | `wired_board.rewire_count`, tested in `TheRewireCountTest` |
| 2 | Q2: firmware older than pins.py's names means the older record's `pin_map.names` differ from pins.py's | the plan council | acted | `PinMapUses.changed_since`, `checks_reading.pin_names_line`; a moved pin keeps its name and is not stale |
| 3 | Q3: the step's op is `check-firmware`, with one `OP_SCRIPTS` row | the plan council | acted | the final architecture lens found the `OP_SCRIPTS` row right: a data row with no logic, as `run-scenario` and `build-board` are |
| 4 | the `(FIRMWARE, STALE)` NOW sentence lives in `checks_reading`, since `flow_codes.py` has 599 of 600 lines | the architecture lens | raised | P1364 https://github.com/xmejkal/spark/issues/1957, the card that splits `flow_codes.py`, moves it |
| 5 | a `NOW_SENTENCES` table entry for that sentence | the architecture lens | rejected | dropped because the precedent is `(REQUIREMENTS, STALE)` and `DESIGN_*_NOW` |
| 6 | a rebuild of the same design asks again, with a new sheet mtime | the refuter | raised | P1363 https://github.com/xmejkal/spark/issues/1956: the time of the list's first sheet in `wiring-record.json`. Until then show's help and flow.md say so |
| 7 | a check record from before `names` gives no stale mark | the plan | acted | by design; the PR says to run `check_firmware.py` once after the merge |
| 8 | a check in the same second as the sheet closes nothing, so a test would flake | the second round | acted | the tests set the sheet's mtime back with `os.utime`, or the record's `at` |
| 9 | `now.changes` joins the JSON, so 14 expected `now` dicts gain `"changes": None` | the build | acted | amendment A1: each keeps its full-dict assertion |
| 10 | the p977 `two_jobs` mutation row named `beside_sheet`, which step 4a moved into a helper | the build | acted | amendment A2: the row mutates the same condition where it lives now; its mutant is caught by the same test |
| 11 | the PO's cap of 50 critical mutation rows is full (52 with rows 1 and 7) | the hook | acted | the two p1270 rows lose their critical mark (amendment A3); new rows run in every sweep anyway |
| 12 | the guide's own claim in firmware-codes.md that an older record leaves the firmware with no status | the final architecture lens 1 | acted | the page says `stale` after a change of names (commit bc27913e) |
| 13 | flow.md's `with_wiring` and the `guide_of` docstring leave out the open rewire, `changes` and `board` | the final architecture lens 2 | acted | both name them (bc27913e) |
| 14 | spark-review's "out of date" is unconditional | the final architecture lens 3 | acted | it says after a change of pin names (bc27913e) |
| 15 | `ONE_CHANGE if count == 1` repeats `phase_readers.counted_words`, and `names_said` repeats the "A, B and C" join found in four other files | the final architecture lens 5 | raised | P1349 https://github.com/xmejkal/spark/issues/1935, one shared helper |
| 16 | `listed_count`'s docstring says it reads with the writer's own constants, though `sheet.py` writes the "### " and "- " marks as literals | the final architecture lens 6 | acted | the docstring is narrowed to the headings and the nothing line (bc27913e) |
| 17 | the `OP_SCRIPTS` row at 151 characters breaks the table's wrap | the final architecture lens 7 | rejected | dropped because renderers.py already holds lines of 121 to 124 characters; a style fix only (the refuter) |
| 18 | no mutation row for `firmware_steps`, the `(FIRMWARE, STALE)` branch of `who_and_sentence` and `is_after`'s strict `>` | the final architecture lens 8 | acted | three rows added, each caught by its test applied by hand |
| 19 | `with_wiring` finds the rewire by `now.status is None`, not by the fact `changes` | the final architecture lens 8 | rejected | dropped because `is_open` opens a breadboard with no status only through `changes`, and a test pins the page's open fold |
| 20 | REWIRE_NOW says "against the new pins.py" though a listed change may not touch pins.py's names | the final refuter 2 | acted | it says "against pins.py" (bc27913e) |
| 21 | two new tests pass on main's code (a moved pin keeps no status, a missing name on a current record stays problems) | the final refuter 3 | rejected | dropped because they are guards, not proofs of the new code |
