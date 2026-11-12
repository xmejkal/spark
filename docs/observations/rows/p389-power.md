# P389 PR 2: a board names its own charger, regulator, battery input and battery-level pin, findings rows

Findings from building PR 2 of P389 (2026-10-25, Prague). The build checked each claim of the approved plan in the code and in the kept sources.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | GPIO14 on the T-Display is a battery pin | plan, round 1 | raised | it is not. The schematic calls the net on MTMS/IO14 `PWR_EN`, and the kept README lists it as `ADC Power 14`. The fixture's `//power` says so and holds no entry for it. What `PWR_EN` switches (Q3 and D6 are near it) was not read — P776: waits on the PO: Needs the PO's reading of what PWR_EN switches on the T-Display schematic. — P776: waits on the PO: Needs the PO's reading of what PWR_EN switches on the T-Display schematic. |
