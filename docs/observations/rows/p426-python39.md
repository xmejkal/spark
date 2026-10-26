# P426: spark runs on Python 3.9 again, findings rows

Findings of P426 (2026-10-26, Prague, auto mode). Found by the plan council of P425.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Only `boards.py` needs Python 3.10 | build | acted | an `ast` search of `scripts/`, `tools/` and `tests/` found two annotations, `boards.py:341` and `:344` (`str | None`). Both are `Optional[str]` now. Every script imports under `/usr/bin/python3` 3.9.6 |
| 2 | The suite runs on 3.9 | build | acted | in a 3.9 venv with `littlefs-python`, 4 of 3237 failed: `test_no_magic_strings` reads `ast.MatchValue` and parses a `match` statement (3.10 only), and one `image_evidence` test expects 3.10's refusal of a deep expression, which 3.9 compiles. The first is guarded, the second skips with its reason. Now "Ran 3240 tests in 132.608s / OK (skipped=1)" on 3.9 |
| 3 | A guard keeps it so | build | acted | `tests/test_python_floor.py`: every script and tool parses with `feature_version=(3, 9)`, and no `X | Y` annotation runs without `from __future__ import annotations`. It fails on main, naming the two lines |
| 4 | The suite has a 3.9 run on every push | build | raised | it does not: the hook runs the developer's Python (3.10 here). The floor test catches syntax, not 3.10-only library calls. A 3.9 run before a release can join the release checklist |
