# P1270 (#1829): rewire and stale pin names: rows

Card: [P1270 #1829](https://github.com/xmejkal/spark/issues/1829). This file holds the acted, raised and rejected findings only. 2026-11-28.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Q1: a check record or a board log later than the sheet closes the rewire | the plan council | acted | `wired_board.rewire_count`, tested in `TheRewireCountTest` |
| 2 | Q2: firmware older than pins.py's names means the older record's `pin_map.names` differ from pins.py's | the plan council | acted | `PinMapUses.changed_since`, `checks_reading.pin_names_line`; a moved pin keeps its name and is not stale |
| 3 | Q3: the step's op is `check-firmware`, with one `OP_SCRIPTS` row | the plan council | raised | the architecture lens on Opus reviews the row in `core/renderers.py` |
| 4 | the `(FIRMWARE, STALE)` NOW sentence lives in `checks_reading`, since `flow_codes.py` has 599 of 600 lines | the architecture lens | raised | the card that splits `flow_codes.py` moves it |
| 5 | a `NOW_SENTENCES` table entry for that sentence | the architecture lens | rejected | dropped because the precedent is `(REQUIREMENTS, STALE)` and `DESIGN_*_NOW` |
| 6 | a rebuild of the same design asks again, with a new sheet mtime | the refuter | raised | a card: one more field in the wiring record, the time of the list's first sheet |
| 7 | a check record from before `names` gives no stale mark | the plan | acted | by design; the PR says to run `check_firmware.py` once after the merge |
| 8 | a check in the same second as the sheet closes nothing, so a test would flake | the second round | acted | the tests set the sheet's mtime back with `os.utime`, or the record's `at` |
| 9 | `now.changes` joins the JSON, so 14 expected `now` dicts gain `"changes": None` | the build | acted | amendment A1: each keeps its full-dict assertion |
| 10 | the p977 `two_jobs` mutation row named `beside_sheet`, which step 4a moved into a helper | the build | acted | amendment A2: the row mutates the same condition where it lives now; its mutant is caught by the same test |
