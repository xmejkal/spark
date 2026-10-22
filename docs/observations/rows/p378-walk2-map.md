# P378 walk 2 map: rows

Rows from the P378 spike (#484), 2026-10-22 (Prague). One agent (Sonnet 5.5) wrote the map and the predictions.

| # | row | state |
| --- | --- | --- |
| 1 | `parts.py --requirements` never writes `board_only`, so a board-only idea ends `????` until the file is written by hand. | raised: walk 2 tests it (prediction 4) |
| 2 | The idea step offers no pick for the board's own button. P355 (#453) covers only the LED. | raised: widen P355 after the walk |
| 3 | The XIAO record has no `active_level` for `onboard_button`, so `pins.py` has no `ONBOARD_BUTTON_ON`. | raised: walk 2 measures it |
| 4 | A board-only build gives the PO no page to read at the wiring step. | raised |
| 5 | The sweep before the PR: claims 4, 7 and 8 checked in the code (they hold). Bold lead-ins removed. | acted |
