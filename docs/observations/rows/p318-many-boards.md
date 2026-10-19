# P318 many boards: findings rows

The council of spike P318 (#402). Finding: [`finding.md`](../../discovery/2026-10-19-p318-many-boards/finding.md).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Every stage after the requirements file assumes one board in one project folder | code map | verified | the table in the finding, line numbers spot-checked by the refuter |
| 2 | Option C (one board per folder) needs no spark change, only the message fix and P319 | architect | acted | partly true: each folder needs init and its own `parts/` (refuter's run on a copy of rc-car) |
| 3 | Both rc-car boards walk the v0.10 journey | architect | acted | `remote/` builds to the end; `car/` stops at simulation, 3 parts have no `simulation` record |
| 4 | A folder with no `.spark/` builds with its parent's project, but `check_all --project .` does not walk up | refuter | acted | card P319 #403 |
| 5 | C costs nothing later | architect | acted | only if A keeps each board folder as the store's project (projects.json, history events) |
| 6 | Four line numbers in the table point inside the code, not at the name | refuter | acted | corrected |
| 7 | The sizes of A (about 10 files) and B (about 15) | architect | raised | estimates, not measured; the finding says so |
| 8 | The TL;DR, the table and row 5 disagree on the condition for "no rework"; `car/`'s stop reads as a spark failure | docs review, PR | acted | the condition is in all three; the stop is named a gap in rc-car's part records |
