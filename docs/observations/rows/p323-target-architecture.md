# P323 target architecture: findings rows

The P323 architecture council (round 1 five lenses, an Opus refuter, round 2 tech lead, senior and PO assistant) found these, folded into [design.md](../../discovery/2026-10-19-p323-target-architecture/design.md).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | R1: `spark` as a package name clashes with another module | refuter | rejected | no clash found, `scripts/spark/` kept (D1) |
| 2 | R2: A shim breaks `mock.patch`, drops private names (65 test uses) and 7 mutation rows on `outcomes.py` | refuter | acted | D14, 5.3: no library shims, a move retargets importers, patches and rows |
| 3 | R3: Guard tests and `measure.py` read only `scripts/*.py` | refuter | acted | slice 1a switches them to `rglob` |
| 4 | R4: The build had no legal home: `check_spine` imports breadboard, simulation and setup | refuter | acted | `build` area on top, `setup` above `design` (2.1) |
| 5 | R5: `catalog.py` imported every area, so one broken area broke all doors | refuter | acted | D3: no catalog, each door imports its own area |
| 6 | R6: Operation did not fit `parts.py`'s table, and `op` and the name were two names | refuter | acted | D2, 2.4: argparse keywords, many Operations per door, name is `op` |
| 7 | R7: Slice 2 was not byte-identical and `run` injection was unstated | refuter | acted | only slice 1a before walk 1, `run_door` passes `run` (2.6) |
| 8 | R8: Acceptance criteria contradicted D8 and the ban list failed on the design | refuter | acted | AC 1 keeps S8 out, S12 bans exact name parts |
| 9 | R9: library, Operation and code each had two meanings | refuter | acted | role `Records`, Operation only a role, exit status apart from code |
| 10 | R10: Slice 2 built a catalog, Workspace and door class for one door | refuter | acted | one `run_door` helper, catalog and Workspace wait for need |
| 11 | T1: Area graph cycle: `project_image` and `run_scenario` import each other's areas, bench imports simulation | round 2 tech lead | acted | `project_image` in `simulation`, `DeployError` in `firmware/errors.py`, edge bench to simulation (2.1) |
| 12 | T2: A 40-line door cannot hold `parts.py`'s 30 Operations | round 2 tech lead | acted | the area's `operations.py` holds `OPERATIONS`, the door imports it (2.4) |
| 13 | T3: No board record has a `firmware` key | round 2 tech lead | acted | 2.5: `micropython_port` maps to `micropython` until a second platform |
| 14 | T4: `SimulationEngine` had the wrong role | round 2 tech lead | acted | Strategy with an Adapter subclass (2.5, diagram) |
| 15 | T5: The MCP switch was missing, and `tool_finder` cannot sit in `core` | round 2 tech lead | acted | MCP seam row (2.5), D5, D15 puts `tool_finder` in `records` |
| 16 | T6: One board per project contradicts the v0.13 promise in developing.md and journey.md | round 2 tech lead | acted | D12: the promise moves to P318, the design PR edits both lines |
| 17 | T7: Acceptance criteria missed seams | round 2 tech lead | acted | AC 6 lists seven seam tests |
| 18 | T8: Slice 1's unused `SparkError` would fail `test_orphans` | round 2 tech lead | acted | no code under `spark/` in slice 1, `SparkError` enters in slice 2 |
| 19 | T9: Name conflicts: SparkError fields, check meaning, role words missing, "under" versus "at most" | round 2 tech lead | acted | D9 fields fixed, check redefined, roles pointed to developing.md, "at most" |
| 20 | T10: Refactoring capacity after walk 1 | round 2 tech lead | acted | D13: per-story pay-down only until v0.13 |
| 21 | T11: A crash exit status | round 2 tech lead | acted | D9: `could-not-run`, code `crash`, exit 2, agents.md exit table updated |
| 22 | S1: The baseline format and rule scopes were unstated | round 2 senior | acted | section 3: sorted keys, `--lower`, a scope column |
| 23 | S2: S12 hit real names such as `command_for` and `is_library` | round 2 senior | acted | S12 narrowed to whole CamelCase words and four function words |
| 24 | S3: Slice 1 could not plant a cycle in a near-empty package | round 2 senior | acted | slice 1b: `ArchitectureCheck(root)` with temp-tree tests and a mutation table |
| 25 | S4: `run_door` needed `prog`, epilog, diagnostics, bad-argument handling and exit parity | round 2 senior | acted | 2.4, 2.6, slice 2 done-when |
| 26 | S5: `core` imports `outcomes`, which stayed flat | round 2 senior | acted | slice 2's first commit moves `outcomes` into `core` (39 importers, 7 rows) |
| 27 | S6: `parts.py`'s Operations are flags of an exclusive group, with shared options and data keys | round 2 senior | acted | 2.4: selector flags, `options=`, `data` field |
| 28 | S7: The bench move's real size was missing | round 2 senior | acted | 5.3: 17 modules, 34 importers, 188 rows, guard regexes |
| 29 | S8: Slice 1 was about 400 lines | round 2 senior | acted | split into 1a and 1b with sizes |
| 30 | P1: The TL;DR was jargon | round 2 PO assistant | acted | plain-English TL;DR |
| 31 | P2: No plain yes or no line | round 2 PO assistant | acted | "Your call" line under the TL;DR |
| 32 | P3: Progress showed only as jargon | round 2 PO assistant | acted | "Areas moved, known breaches left" headline in 5.4 |
| 33 | P4: The crash question was not the PO's | round 2 PO assistant | acted | decided by the council in D9 |
| 34 | P5: The PO's real question was missing | round 2 PO assistant | acted | section 8: slice 1a before or after walk 1 |
| 35 | P6: Undefined words | round 2 PO assistant | acted | section 4 defines Value, baseline, golden, registry, seam, AST test, stdlib, mutation row |
| 36 | P7: Reading time | round 2 PO assistant | acted | sections 1 to 7 marked reference |
