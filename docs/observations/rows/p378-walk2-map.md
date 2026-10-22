# P378 walk 2 map: findings rows

Gaps from the P378 spike (#484), the map and predictions for walk 2 (2026-10-22, Prague). One agent (Sonnet 5.5)
wrote them. The journey map is the Miro frame
https://miro.com/app/board/uXjVEavQ4JQ=/?moveToWidget=3458764688085642382. Walk 2 tests each row.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `parts.py --requirements` never writes `board_only`, so a board-only idea ends `????` until the file is written by hand | spike, code | verified | `scripts/parts.py` has no `board_only`, prediction 4 |
| 2 | The idea step offers no pick for the board's own button. P355 (#453) covers only the LED | spike | raised | prediction 3, widen P355 after the walk |
| 3 | The XIAO record has no `active_level` for `onboard_button`, so `pins.py` has no `ONBOARD_BUTTON_ON` | spike, record | verified | `boards/xiao-esp32-c6.json` `onboard_button`, prediction 8 |
| 4 | A board-only build gives the PO no page to read at the wiring step | spike | raised | the map's step 8 |
| 5 | The sweep before the PR checked claims 1 and 3 in the code and removed bold lead-ins from the predictions | sweep | acted | this PR |
