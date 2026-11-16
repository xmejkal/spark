# P459: the X2 rule counts every route to print, read or exit: rows

Card: [P459 #619](https://github.com/xmejkal/spark/issues/619), a chore: the card and the change, no plan. New logic: one
lens and the refuter on the PR. This file holds the acted, raised and rejected findings only (rules.md). 2026-11-16.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | five mutation rows of four tables find nothing: p190-serial, p468-serial-warning, p484-onboard-parts and p778-stages-agree-on-simulation, in `scripts/spark/build/build_service.py` and `tools/circuit-to-wokwi/cli.ts`, which this PR does not touch | build (`mutate.py --anchors` on every table) | raised | a comment on [P284 #331](https://github.com/xmejkal/spark/issues/331), the card for rows that find nothing |
| 2 | X2 reads names by file, not by scope: a local or a parameter named `input`, `exit`, `quit` or `print` counts (`def f(input): return input + 1`) | PR lens (Sonnet), PR refuter (Opus) | acted | the `OUTPUT_NAMES` comment names the limit; no such name in `scripts/spark/` today |
| 3 | `sys.__stdout__` and `sys.__stderr__` still escape, the likeliest by accident | PR lens, PR refuter | acted | both in `OUTPUT_NAMES`; the planted test reads `sys.__stderr__.flush()`; a mutation row |
| 4 | `getattr(builtins, "print")`, `__builtins__.print`, `os.fdopen(1)`, `from builtins import *` still escape | PR lens, PR refuter | rejected | dropped because each needs a deliberate dodge and the card names none; `scripts/spark/` holds no `from os|sys|builtins import` |
| 5 | `import builtins as b` is matched by a written name, while the from-branch uses `OUTPUT_MODULES` | PR lens | rejected | dropped because `import os as o` and `import sys as s` already resolve through `TRACKED` in `aliases_of`; only builtins is new |
| 6 | `T1:scripts/spark/build/build_service.py:file-write` fell from 7 to 6 on main, and a fallen value passes unseen | PR refuter | acted | `measure.py --rules --accept`: that one line changed |
| 7 | `planted()` never removes its `mkdtemp()` folders: 104 sit in TMPDIR | PR refuter | rejected | dropped because every test module imports `suite_temp` first, which points `tempfile` at one folder and removes it at exit; only a call from outside the suite leaves folders |
