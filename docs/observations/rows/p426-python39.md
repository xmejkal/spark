# P426: spark runs on Python 3.9 again, findings rows

Findings of P426 (2026-10-26, Prague, auto mode). Found by the plan council of P425.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The suite has a 3.9 run on every push | build | raised | it does not: the hook runs the developer's Python (3.10 here). The floor test catches syntax, not 3.10-only library calls. A 3.9 run before a release can join the release checklist — P776: waits on the PO: a release-time check the PO decides on — P776: waits on the PO: a release-time check the PO decides on |
| 2 | The floor test is complete | review | raised | best effort: a newer host (3.12's f-strings) or an `Alias = int | str` or `isinstance(x, int | str)` outside annotations slips past it. None exists in `scripts/` or `tools/` today. Row 4's 3.9 run before a release is the second net — P776: waits on the PO: a release-time check the PO decides on — P776: waits on the PO: a release-time check the PO decides on |
