# P676 the wave 5 plan: rows

What the plan council found while Fable 5.1 wrote the wave 5 plan. Card:
[P676 #907](https://github.com/xmejkal/spark/issues/907). Plan: `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave5-plan.md`, whose Council section lists each change.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Wave 5 had no card and no plan, though the PO asked to finish the refactor | session | acted | P676 #907, this plan |
| 2 | The baseline holds 23 keys that the move touches, not 17 | refuter, round 1 | acted | the plan lists all 23 |
| 3 | "probe" is no role word, so the renames raised an R6 breach | refuter, round 1 | acted | role words in the docstrings, Adapter or Strategy in the diagram |
| 4 | Moving `board_codes` and `board_pads` into `bench/` makes import cycles through `spark/bench/__init__.py` | refuter, round 1 | acted | both leaves stay in `scripts/` until wave 6, an import-alone test per moved module |
| 5 | Four paths built from `__file__` and two path tests break after the move | refuter, rounds 1 and 2 | acted | named in W5-3a's fix list; `tests/test_boards.py` keeps its `board_pads.py` path, because the leaf stays in `scripts/` |
| 6 | W5-1 masked too little (lines, notes, events, repo and python) and named a field that does not exist | refuter, round 1 | acted | the masked places and the raw places named, the goal narrowed to "except a pasted line" |
| 7 | The counts were off (imports, files, doc files) | refuter, round 1 | acted | 182 import lines in 58 files, 170 doc files, rows recounted on W5-3a's base |
| 8 | The map was bloat by spark's bar | architecture lens | acted | trimmed to one class and `--write`. It stays, because the accepted plan names it |
| 9 | W5-3 mixed a move with renames and a fold | architecture lens | acted | split into W5-3a and W5-3b |
| 10 | `spark.bench.CLI_DIR` made a new cycle | refuter, round 2 | acted | dropped, each module builds its path inline |
| 11 | Masking reached pasted lines in a Finding sentence and an Event | refuter, round 2 | acted | `PASTED_CODES` and a raw Event, tested on two goldens |
| 12 | `~/` paths made the goldens depend on one machine | refuter, round 2 | acted | the scrub also replaces the `~/` forms |
| 13 | Folding `DeployPhase` into `board_envelope` makes a cycle | refuter, round 2 | acted | it stays in the leaf `deploy_stages.py` |
| 14 | Two PO questions: real paths in pasted lines, and how S11 meets the open #906 | Fable | raised | the plan's Open questions, with defaults: real paths, and S11 waits for his merge |
| 15 | Two mutation rows name `scripts/board_ready.py`, which no longer exists | Fable | raised | W5-3a reports them as a row in its rows file, as the plan says |
