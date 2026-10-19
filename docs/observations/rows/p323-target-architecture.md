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
| 37 | The platform key belongs on the project, not the board record (one XIAO runs MicroPython or Arduino) | round 3 extensions | acted | 2.5: key in requirements' `firmware`, default `micropython`, enters with the second platform |
| 38 | `FirmwarePlatform` covers only the deploy, the pin map and image are MicroPython too | round 3 extensions | acted | 2.5 row and class diagram add `pin_map_text` and `make_image`, built with the second platform |
| 39 | No MCU is not "nothing": `REQUIRED_KEYS` needs `chip` (`boards.py:62`), a missing board loads the active ESP32 (`boards.py:253`) | round 3 extensions | acted | D16: `no_board` instead of a silent default, seam test in AC 6, a no-MCU platform deferred |
| 40 | Check codes are listed in two places | round 3 extensions | acted | each `Check` declares `codes`, `check_all`'s are the union (2.4) |
| 41 | `SimulationEngine` with one `run` cannot swap Wokwi | round 3 extensions | acted | `prepare(design)` and `run(scenario)`, engine facts under `simulation.<engine>` later (2.5) |
| 42 | `run_door` mixes parse, run and print, so an MCP door would copy it | round 3 extensions | acted | `run_operation` split in slice 2 (2.6). `Argument.kind` waits for the MCP door (2.4). |
| 43 | An online store layer needs one sync Operation with the `network` effect | round 3 extensions | raised | for P178, no second case yet |
| 44 | The wiring page needs a `project` area above `build` | round 3 extensions | rejected | no slice needs it yet, deferred to P297 (section 7) |
| 45 | fab, copper and emit_footprint have no area, exports have no registry | round 3 extensions | acted | placed in `design` (2.1). `EXPORTERS` deferred until a second export. |
| 46 | The MCP Adapter seam is added before its need | round 3 simplicity | rejected | the PO named tool adapters with an MCP setting in #94. The row stays, the seam test uses a fake Adapter, no MCP client. |
| 47 | The Renderer seam test is not needed | round 3 simplicity | acted | dropped from AC 6, two Renderers already exist |
| 48 | The `firmware` key and the no-MCU row come too early | round 3 simplicity | acted | merged with 37 and 39 |
| 49 | Measure columns that stay 0 until v0.13 | round 3 simplicity | acted | 5.4: a column enters with its first slice |
| 50 | Two headline measures | round 3 simplicity | acted | one headline, "Known breaches left", Miro table from v0.13 |
| 51 | S8's `MagicMock` sentence bans nothing (0 files) | round 3 simplicity | acted | dropped |
| 52 | exit status and exit code (agents.md 9 lines) | round 3 simplicity | acted | "exit status" kept, agents.md edited in the design PR (section 7) |
| 53 | outcome, status and verdict | round 3 simplicity | acted | "outcome, printed as `status`". `verdict` rename raised for later. |
| 54 | library means record folders and a module kind | round 3 simplicity | acted | measure.py and developing.md:225 say "module" |
| 55 | step means `outcomes.step`, `BuildStep` and breadboard steps | round 3 simplicity | acted | `BuildStage` |
| 56 | `ArchitectureCheck` is not a `Check` | round 3 simplicity | acted | `ArchitectureRules` |
| 57 | gate means consent and merge criteria | round 3 simplicity | acted | 5.3 says "Done when" |
| 58 | Error scope clashes with developing.md:237 and :278 | round 3 simplicity | acted | the design PR edits both lines (section 7) |
| 59 | Value is a role word and a vocabulary row | round 3 simplicity | acted | defined once in the role list in section 4 |
| 60 | The summary says output is unchanged | round 3 simplicity | acted | TL;DR: output only gains keys, a crash exits 2 |
| 61 | S1 and S6 on `tests/` puts 482 test classes in the baseline | round 3 simplicity | acted | scope `scripts/` |
| 62 | D9 and S7 disagree on area subclasses | round 3 simplicity | acted | S7: directly or through its area's Error |
| 63 | S3 needs judgment | round 3 simplicity | acted | S3 is an AST rule on `subprocess`, `time.time`, `urllib`, `os.environ` |
| 64 | S13 needs judgment | round 3 simplicity | acted | S13: two subclasses or a Fake, checked by AST |
| 65 | S10's contract test names no file | round 3 simplicity | acted | one entry per `name` in `tests/test_json_contracts.py` |
| 66 | 10 areas can be 8 | round 3 simplicity | acted | D15: firmware holds simulation, build holds setup |
| 67 | A newcomer's first change touches four files | round 3 simplicity | acted | a five-line "add a flag" example in developing.md, slice 1b |
| 68 | Tool code sits in two areas | round 3 simplicity | acted | `records/tools` holds finder and install |
| 69 | Test shape per role is not written down | round 3 testing | acted | developing.md in slice 1b |
| 70 | Fakes can drift from their real class | round 3 testing | acted | S14 contract mixins, Fakes pass them |
| 71 | Contract tests have no shape | round 3 testing | acted | S14: contract classes land with each area, the `FirmwarePlatform` contract loops over every board record |
| 72 | A bulk golden update turns a bug into truth | round 3 testing | acted | slice 1a: one file per Operation and outcome, `--accept <op>` only |
| 73 | Hand-retargeted mutation rows can guard nothing | round 3 testing | acted | `mutate.py --retarget` in slice 2, "rows N, caught N" |
| 74 | Suite speed | round 3 testing | acted | parse once, suite seconds in measure, shard at 150 s |
| 75 | What only the bench proves is unstated | round 3 testing | acted | developing.md list in slice 1b |
| 76 | The architecture test must fail clearly | round 3 testing | acted | rule, file, line and reason, at most 20, `--lower` only lowers (section 3) |
| 77 | Stale patch targets pass and test nothing | round 3 testing | acted | S8: every patch target resolves to its defining module |
| 78 | Discovery needs two reads | round 3 Claude operator | acted | a generated `docs/guide/operations.md` in the plan order (5.1) |
| 79 | No "where am I" Operation | round 3 Claude operator | acted | `loop_status` second in the plan order, in `build` |
| 80 | Command pages still repeat logic | round 3 Claude operator | acted | `fix` steps with `op` and `argv`, build envelope in the plan order |
| 81 | Pages still parse text | round 3 Claude operator | acted | S10: every Operation a page calls has `--json` |
| 82 | Tokens: `check_all --all`, rules into code meanings | round 3 Claude operator | raised | behaviour changes, later card |
| 83 | No guard on walk-1 outputs before slice 2 | round 3 Claude operator | acted | slice 1a goldens of `check_spine`, `check_all`, `deploy --dry-run` |
| 84 | Missing codes, `image_stale` most | round 3 Claude operator | acted | starter codes in 2.4 |
| 85 | Person steps are not marked | round 3 Claude operator | acted | `needs_person` in `outcomes.step` |
| 86 | Nothing checks firmware imports the pin map | round 3 Claude operator | raised | a `firmware_pins` Check is a feature card |
| 87 | Gates are not tied to effects | round 3 safety | acted | S15 and `run_door`'s consent refusal, planted in slice 2 |
| 88 | A yes must never be an input | round 3 safety | acted | 2.6: the door's process picks `consent`, MCP fails closed |
| 89 | Grants must fail closed | round 3 safety | acted | 5.3: a corrupt or zoneless grant test lands with the bench move |
| 90 | Schema versions differ per reader | round 3 safety | acted | S17, `RecordSchema(kind, version, rules)` |
| 91 | Records read the environment in many places | round 3 safety | acted | one `Layers` Value, only `records` reads `SPARK_HOME` (S3) |
| 92 | File writes are spread out | round 3 safety | acted | S16: only `records` writes, through `write_file` or `FileWriter` |
| 93 | Dry run is a convention | round 3 safety | acted | 2.6: `run_door` swaps in recording Fakes, AC 9 |
| 94 | The Wokwi token could leak | round 3 safety | acted | `run_door` masks `account_env` values, S18 marker test |
| 95 | A `Clock` collaborator for aware times | round 3 safety | rejected | `board_grant` already refuses a zoneless time, no second need |
| 96 | Errors leak home paths | round 3 safety | acted | `run_door` shortens paths, traceback only with `--debug` (2.6, S18) |
| 97 | The area graph has upward edges and a firmware-bench cycle with today's imports, and `part_pictures` has no area | refuter round 2 | acted | 2.1: `FirmwarePlatform` in bench, `needs` in design, `part_pictures` in breadboard, graph re-derived by an `ast` scan. 5.3 lists the four upward edges left and the move that removes each. |
| 98 | The platform is chosen twice: `deploy.py:171` hard-codes MicroPython and `micropython_port` (`flash_image.py:89`) picks the build | refuter round 2 | acted | 2.5: the requirements' `platform` key is the only choice, `micropython_port` is a fact the platform reads |
| 99 | "firmware" names the area, the requirements key, the project folder and `check_spine --firmware` | refuter round 2 | acted | the requirements key is `platform` in design.md |
| 100 | `no_board` breaks `boards/active.json`, which `init_project --board` writes (`boards.py:253`, `boards/README.md:21`) | refuter round 2 | acted | D16, 5.1, AC 6: `no_board` only when neither names a board. Callers `live.py:91`, `check_all.py:406`, `emit_footprint.py:208`, `design.py:377` listed. |
| 101 | `run_door` breaks S3, the core rule and the Fakes' home | refuter round 2 | acted | 2.6: the door passes `shorten`, `secrets` and `writer`. Production versions live in `records`. |
| 102 | S14, S15 and S17 are not AST-checkable as written | refuter round 2 | acted | S14 checks `<Name>Contract` classes and inheritance, S15 direct imports of the erase Adapter, S17's last sentence dropped |
| 103 | Goldens hold a home path and tool versions, and a non-failing deploy golden needs a kept simulated project | refuter round 2 | acted | 5.2: a fixture under `tests/data/`, `<project>` for the root, versions normalised, 1a records only goldens that meet these rules. 1a grows to about 220 lines (section 8). |
| 104 | `status` is both the outcome's key and the exit status, "library shim" misuses library, `developing.md:225` is off by three | refuter round 2 | acted | section 4: "exit code" for the process, "module shim" in D14, 5.3 and 7, `developing.md:222`. Other "exit code" lines change in later slices. |
| 105 | Rows 89, 71 and 42 are acted but have no text in design.md | refuter round 2 | acted | text added in 5.3 (89), S14 (71) and 2.4 (42) |
