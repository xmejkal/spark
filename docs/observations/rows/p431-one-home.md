# P431: one home for each fact, findings rows

Findings of P431 (#573), 2026-10-27, Prague: OC7, OC5 and OC6 of refactor plan v2, PR W2-1. From the wave 2 plan (two council rounds) and the build, which checked each claim of the plan in the code.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Must `boards.board_fact_problems` refuse a bare value at a fact position, so that a record never holds one? | plan | raised | not decided here. `read_value` keeps the lenient rule, as `fact_value` had it (`series_ohms` is byte-identical), and `firmware_pulls` counts only a finite positive number as the pull. The PO or a later card decides the records check — P776: waits on the PO: records check decision left to PO or a later card — P776: waits on the PO: records check decision left to PO or a later card |
