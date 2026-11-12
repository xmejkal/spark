# P389 PR 1: a board names its own LED, buttons and display, findings rows

Findings from building PR 1 of P389 (2026-10-25, Prague). The build checked each claim of the approved plan in the code.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The kept README is the T-Display's pin source | build | raised | its pinout column is headed V18, and the board's silkscreen reads V1.1. The fixture's display note says so. No kept source says the two are one revision — P776: waits on the PO: Silkscreen V1.1 versus README V18 needs the PO's look at the board — P776: waits on the PO: Silkscreen V1.1 versus README V18 needs the PO's look at the board |
| 2 | The T-Display buttons hold an `active_level` | build | raised | the walk record had none. The fixture gives 0 from its own note ("each pressing to GND", schematic). Nobody pressed them on the bench for this. The walk project's record is not changed — P776: waits on the PO: T-Display button active level needs a bench press — P776: waits on the PO: T-Display button active level needs a bench press |
| 3 | Only the fixture names a display today | build | raised | the walk project's own record gets the display after the merge, with the PO's yes — P776: waits on the PO: Writing the display into the walk project record waits for his yes — P776: waits on the PO: Writing the display into the walk project record waits for his yes |
