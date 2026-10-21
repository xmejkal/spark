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
| 106 | `mock.patch` 336 read as uses, but it counts lines: 350 uses on 336 lines | fact check (script) | acted | D8 and the progress table say lines |
| 107 | "Exit code" in 33 files had no scope: 149 files repository-wide | fact check (script) | acted | scope named: `scripts/`, the guides, the commands (28 + 4 + 1) |
| 108 | The bench move's 17 modules, 34 importers, 188 rows could not be reproduced: another file list gives 15, 19, 236 | fact check (script) | acted | a range, marked as an estimate |
| 109 | 110 plugin paths, 39 importers of outcomes, 11 OPTIONS rows, 6 item sites, design.py:377 and every other file:line reference | fact check (script) | verified | reproduced by grep and the script |
| 110 | Every name that exists nowhere in the repository is a proposed new name | fact check (by hand) | verified | 25 names, each introduced as new in the design |
| 111 | Six result shapes cross boundaries (`outcomes.py:49`, `check_all.py:72`, `check_spine.py:100`) | round 4 architect | acted | architecture/README.md contract, core.md: one `OperationResult` (named by the naming paper) |
| 112 | Five problem shapes, two with `code` (`parts.py:238`, `breadboard_keep.py:63`, `check_physics.py:93`) | round 4 architect | acted | core.md, checks.md: one `Finding` with severity |
| 113 | Collaborators are growing keyword lists (design 2.6, `deploy_service.py:78`) | round 4 architect | acted | core.md: one `OutsideWorld` with only declared effects (N4) |
| 114 | The rejected `Clock` exists as `DeployService(clock=)` and two Fakes | round 4 architect | acted | clock is an `OutsideWorld` field filled by `SystemClock` (`board_console.py:80`), no `Clock` class, one `FakeClock` (slice 5) |
| 115 | `Layers` duplicates `store.layers` (`store.py:73`) | round 4 architect | acted | records.md: `Records(kind)` over `store.records`. `RecordFolders` kept as the Value tests pass (N9) |
| 116 | Two validators and `REQUIRED_KEYS` (`boards.py:62`, `:340`) | round 4 architect | acted | records.md: `RecordSchema.findings(record)` |
| 117 | Three registry forms and a lambda Platform (`matching.py:222`, `check_all.py:285`, `firmware_platform.py:53`) | round 4 architect | acted | rule X3, N7: a dict keyed by the class attribute `name`. bench.md: `MicroPythonPlatform` |
| 118 | `description` and `epilog` are CLI text, not Operation fields | round 4 architect | acted | notes.md cut list. README.md help row: the CLI keeps its long text |
| 119 | No text-mode output in the design (`look.py:63`) | round 4 architect | acted | `OperationResult.lines`, rendered by `TextReport` |
| 120 | `SparkError.outcome` as an argument invites a wrong status (`assign_pins.py:46`) | round 4 architect | acted | N14: `status` is a class attribute |
| 121 | `pin_map_text` and `make_image` on a bench class add upward edges | round 4 architect | acted | N15, bench.md, design.md |
| 122 | Frontends are implied, not designed | round 4 architect | acted | README.md context diagram and sequence: CLI text, CLI `--json`, MCP later, all over `run_operation` |
| 123 | Backend choices live in four places (`tools.py:277`, `deploy.py:171`, `flash_image.py:89`, `store.py:46`) | round 4 architect | acted | records.md: one `Backends` (N5) |
| 124 | The write-up needs three levels with a class diagram per area | round 4 architect | acted | README.md and nine area pages |
| 125 | `Check.answer(design)` differs from the code's `run` (`check_all.py:72`) | round 4 architect | acted | checks.md: `Check.run(inputs) -> OperationResult` |
| 126 | `Backends` builds the platform and engine objects | round 4 architect | rejected | records cannot import bench or firmware. `Backends` holds choices (testability F3) |
| 127 | "door" clashes with CLI and interface | round 4 naming | acted | glossary.md: CLI, `run_cli` |
| 128 | "outcome" beside `status`, three values listed where the code prints four | round 4 naming | acted | glossary.md: status, four words (`outcomes.py:21-26`) |
| 129 | Bare `code` means an exit code and board source | round 4 naming | acted | glossary.md: `code` is a problem code only in new code |
| 130 | `verdict` has four meanings | round 4 naming | acted | glossary.md clashes: private functions renamed in moves, JSON keys stay |
| 131 | Five keys hold the person's text | round 4 naming | acted | glossary.md: new JSON uses only `sentence` and `why`. Rule C2 |
| 132 | `tool` and `check` both name the CLI in JSON | round 4 naming | acted | glossary.md: `tool` is the CLI that printed the envelope |
| 133 | Doctor and ready "checks" clash with `Check` | round 4 naming | acted | bench.md: `DoctorStep`, `ReadyProbe` in slice 5 |
| 134 | `stage`, `Step`, "record" and "facts" carry other meanings | round 4 naming | acted | `DeployPhase`, `WiringStep`, `WiringLog`, `RunLog`, `ReadingFile` |
| 135 | `Layers`, "catalog" and `parts.Answer` clash | round 4 naming | acted | `RecordFolders`, "operation registry", `OperationResult` |
| 136 | Coined check classes and ten exceptions without `Error` | round 4 naming | acted | checks.md renames, rule C1, in each area move |
| 137 | AGENTS.md:27 says "library module" and the docs cite `EsptoolBoardReader` (the class is `EsptoolReader`, `board_look.py:117`) | round 4 naming | raised | fix both docs in the PR that merges this design |
| 138 | Four exit aliases (`assign_pins.py:46`, `check_vendor_pins.py:44`) | round 4 naming | acted | rule C3, dropped in each area move |
| 139 | Public flags and keys keep their spelling, with a glossary | round 4 naming | acted | glossary.md section 3. Copy to developing.md in slice 2 |
| 140 | The paper cites `BoardCheckStrategy` and `CheckResult` at `board_doctor.py:54,74` in swapped order | synthesis fact check | verified | `CheckResult` is line 54, `BoardCheckStrategy` line 74. Cited correctly in bench.md |
| 141 | No rule limits nesting or parameters (`matching.py:68` takes 9) | round 4 human readability | acted | rules R2 and R3 |
| 142 | 60 lines is lax for new code | round 4 human readability | acted | rule R1: 40 in `spark/`, 60 for old scripts |
| 143 | Modules do not read top-down | round 4 human readability | acted | rule R4 |
| 144 | Comments tell incident history (`check_spine.py:371`, `:453`) | round 4 human readability | acted | rule R5, build.md moves the stories to their cards |
| 145 | `**collaborators` hides what an Operation uses | round 4 human readability | acted | one `OutsideWorld` instead of one Value per area (smaller) |
| 146 | `run(values)` reads arguments by string key | round 4 human readability | acted | N6: keyword parameters named for each `Argument.dest`, checked by one test |
| 147 | Three hops from CLI to logic | round 4 human readability | acted | README.md: each `Operation(...)` sits under its function, the CLI docstring names both |
| 148 | `parts.py`'s Operations make a 300-line table | round 4 human readability | acted | one-line `summary`, long text in the CLI. sourcing.md splits the Operations by area |
| 149 | Long sentences in control flow, two format styles | round 4 human readability | acted | rule R7 |
| 150 | "outcome" and "status" name one value | round 4 human readability | acted | status everywhere (glossary.md) |
| 151 | `parts`, `boards`, `build`, `design` and bench CLI names mean two or three things | round 4 AI readability | acted | N10, N11: the area is `sourcing`, modules keep prefixes, `design/loader.py` |
| 152 | `describe` and `render` overlap (`board_doctor.py:188`, `parts.py:1546`) | round 4 AI readability | acted | glossary.md: `render` is person text, `describe` the machine description, renamed per story |
| 153 | `drawer.py:187`, `:226` read `parts._parse` and `parts._problem` | round 4 AI readability | acted | rule U2 catches attribute access too |
| 154 | Import style unstated | round 4 AI readability | acted | rule U2: import modules, not names |
| 155 | No code map | round 4 AI readability | acted | slice 6: generated `docs/guide/map.md` |
| 156 | Test mode keyed on `sys.modules` (`store.py:40`, `:339`) | round 4 AI readability | acted | rule T4, removed in the records move |
| 157 | Codes and shared flags have no home | round 4 AI readability | acted | rule U3: `codes.py` per area, `COMMON_ARGUMENTS` in core |
| 158 | No one-entry `--describe` | round 4 AI readability | acted | slice 6: `--describe OP` |
| 159 | The chosen backend is invisible | round 4 AI readability | acted | envelope gains `backends` with `chosen_by` (records.md, N16) |
| 160 | 179 `sys.path` inserts in 78 test files | round 4 AI readability | raised | not checked here. A `tests/paths.py` helper is a card for slice 3a |
| 161 | A frontend is only a CLI over `run_operation` | round 4 AI readability | acted | README.md, rule X2, the parity test |
| 162 | Platform seam leaks through 8 tool lookups (`live.py:84`, `reach.py:79`, `grant.py:88`, `:95`, `board_look.py:296-297`, `board_doctor.py:160`, `:162`) | round 4 testability | acted | bench.md, slice 4: `make_port_finder`, `make_board_reader`, `FakePlatform` seam test |
| 163 | `tools.find` is patched about 39 times and `shutil.which` 29 (paper said 37) | round 4 testability | acted | slice 4: `ToolFinder`, `FakeToolFinder`. Counted by grep 2026-10-21 |
| 164 | Backends chosen in four places | round 4 testability | acted | records.md `Backends` holds choices, registries per area |
| 165 | MCP tool versions have no core adapter | round 4 testability | acted | N13: an MCP result enters as an input file |
| 166 | No proof that a CLI holds no logic | round 4 testability | acted | parity test in core.md, slice 3b |
| 167 | CLI code duplicated: `GrantService` built in 4 places, `--json` and `--project` declared in 14 files | round 4 testability | acted | bench.md, `COMMON_ARGUMENTS` |
| 168 | Fakes outside `fakes.py` and two clocks (`fakes.py:59`, `:88`) | round 4 testability | acted | slice 5 |
| 169 | Seven scripts call `subprocess` with no `run` to inject | round 4 testability | acted | each Adapter takes `run` in its area move (firmware.md, build.md, checks.md, breadboard.md) |
| 170 | `store.py:40` branches on unittest | round 4 testability | acted | rule T4. Slice 0 gives each child process its own `SPARK_HOME`, since the branch does not fire there. Reason corrected by row 212 |
| 171 | Suite 122 s with 44 s in three spots | round 4 testability | acted | slice 7: fast and slow lanes |
| 172 | Only 17% of tests test from the outside, slice 1a covers 3 of 24 CLIs | round 4 testability | acted | slice 0a, 0b, 0c: a golden per Operation and status, fake tools as processes |
| 173 | Areas can reach concrete Adapters and each other's internals | round 4 testability | acted | rules X1 and U1 |
| 174 | Cut seams that serve nothing yet | round 4 testability | acted | refactor-plan.md, what we will not do |
| 175 | 11 output shapes across CLIs | round 4 UX | acted | one envelope (rule C2), each CLI converted when its story or move comes |
| 176 | The message sits under 5 keys | round 4 UX | acted | `Finding.sentence`, rule C2 |
| 177 | `--json` prints plain text on could-not-run (`check_footprints.py:547`, `assign_pins.py:465`) | round 4 UX | acted | `run_cli` prints an envelope for every failure, slice 3b and each conversion |
| 178 | `look.py --bogus --json` prints usage text | round 4 UX | acted | core.md: a bad flag is an envelope, code `bad_argument` |
| 179 | A missing input exits 1 (`boards.py --get`, `parts.py --show`) | round 4 UX | raised | a card for the PO: a public exit code change, outside the refactor |
| 180 | `status` carries mismatch and per-module words | round 4 UX | raised | checks.md: unchanged in the move, a card per CLI's envelope conversion |
| 181 | `--keep` means two things | round 4 UX | raised | a card for the PO to rename one (glossary.md section 3) |
| 182 | The project, circuit, output and timeout are given in several ways | round 4 UX | acted | `COMMON_ARGUMENTS`, old spellings as hidden aliases |
| 183 | 12 `--json` and 11 `--project` help wordings, flags with no help | round 4 UX | acted | help lines live once in core, rule U3 |
| 184 | Exit codes in 8 of 23 helps, effects in prose | round 4 UX | acted | README.md: the generated three-line footer |
| 185 | The last line differs per CLI | round 4 UX | acted | README.md contract: one text order in `TextReport` |
| 186 | `tools.py --status` exits 2 for an unneeded tool and has no `--json` | round 4 UX | raised | convert with P92, outside this refactor |
| 187 | `boards.py` prints a home path | round 4 UX | acted | rule C4 marker test, `Privacy` in slice 3c |
| 188 | A `Frontend` Strategy with three subclasses | round 4 UX | rejected | a function plus two Renderers until MCP is the second frontend (rule T3) |
| 189 | Readability not ranked first | round 4 PO | acted | README.md: five goals in his order, Your call 1 |
| 190 | No reader index per area | round 4 PO | acted | each `operations.py` docstring is the index, `look` the worked example, the generated map |
| 191 | The design is too long to decide on | round 4 PO | acted | README.md at 170 lines, history to notes.md and design.md |
| 192 | Section 8 and the TL;DR say walk 1, which is done | round 4 PO | acted | Your call 3 asks against walk 2, due 2026-10-27 |
| 193 | The product bar is not stated | round 4 PO | acted | refactor-plan.md: codes and next steps for the bench come first (slice 1), for walk 2 |
| 194 | Slice 2 holds several things | round 4 PO | acted | slices 3a, 3b, 3c |
| 195 | 18 rules shown at once | round 4 PO | acted | rules grouped under five goals, the full table in notes.md |
| 196 | `Layers` does not say its role, and "door" is coined | round 4 PO | acted | `RecordFolders`, CLI |
| 197 | The PO's decisions are unordered | round 4 PO | acted | README.md Your call: four, in the paper's order |
| 198 | Goldens that spawn a CLI are not protected by the `store.py:40` test branch, which needs `unittest` imported | synthesis | acted | refactor-plan.md slice 0: each child gets its own `SPARK_HOME`. Reason corrected by row 212 |
| 199 | `check_spine.py` does not import any check module, so build has no edge to checks | synthesis | acted | README.md area map |
| 200 | `parts.py` holds 29 Operations by an `ast` count, not 30 | synthesis | acted | sourcing.md |
| 201 | The goal Operations of `parts.py` live in design, since `needs.py` imports `design`, `emit_board` and `emit_footprint` | synthesis | acted | design.md and sourcing.md. `parts.py` imports both areas' `OPERATIONS` |
| 202 | The tools role for the board engine already exists as `board-engine` (`data/tools.json:6`) | synthesis | acted | build.md uses it, no new role |
| 203 | Area pages run over the 130-line budget | synthesis | acted | notes.md N17: three diagrams each, prose within budget |
| 204 | The build design broke the `check_spine` golden: wrong stage order, a `BreadboardStage` that does not exist, a stop on any non-ok status (`check_spine.py:391-412`) | refuter round 4 | acted | build.md: today's order, six stages, `goes_on` keeps the schematic-notes rule, the sheet stays a `--keep` side output |
| 205 | The pages said goldens never change, yet slice 1 accepts them, `backends` had no slice, and per-area codes arrived in moves | refuter round 4 | acted | refactor-plan.md: a golden changes only in an output slice, never in a move. Each area has an output slice before its move (N18) |
| 206 | "A fix is a NextStep" turns today's string `fix` (`board_envelope.py:58`) into an object | refuter round 4 | acted | `fix` stays a string, `fix_step` is a new key (glossary.md, core.md, README.md, N3) |
| 207 | `deploy.main`'s five keywords (`tests/test_deploy_gate.py:108`) cannot pass through a 15-line CLI over `run_cli` | refuter round 4 | acted | `run_cli` gets one `outside=` override. Slice 3c changes the deploy tests' call lines and says why (N22) |
| 208 | Moving `footprint_stop` and `footprint_gaps` to design left `boards.py:592` and `parts.py:165` as upward edges | refuter round 4 | acted | `board-list` and `audit` move to design (N19) |
| 209 | `cost.py:69,77` and `run_scenario.py:249` read the environment outside records | refuter round 4 | acted | `OutsideWorld.environ` (N20). records.md says only records reads `os.environ` |
| 210 | A new platform touches firmware and design too, not only bench | refuter round 4 | acted | bench.md states the limit: an image builder and a pin map Renderer come with it |
| 211 | `Backends.for_project` defaulted to micropython, a backend named outside `operations.py` | refuter round 4 | acted | the default is bench's `DEFAULT_PLATFORM`. Backends names none |
| 212 | "store.py:40 does not protect a child process" is wrong: children inherit the scratch store (`store.py:35-39`) | refuter round 4 | rejected | the real gap: in a child `store.fetch` refuses `file:` URLs (`store.py:339`), so the 0c fetch goldens run through `main(argv)`. The wrong reason in rows 170 and 198 is corrected in refactor-plan.md |
| 213 | Slice 3a needs `mutate.py --retarget`, which no slice adds | refuter round 4 | acted | slice 2 adds `tools/mutate.py --retarget OLD NEW` |
| 214 | The area map lacked direct edges the pages declare, such as bench to design (`board_live.py:24`, `live.py:19`) | refuter round 4 | acted | rule U1 means reachability along the arrows. Each page names its direct imports (N21) |
| 215 | About 20 new names were not marked proposed | refuter round 4 | acted | each area page lists its new names, checked by grep. `FlasherContract` also does not exist and is marked |
| 216 | `run_cli` had two signatures, and README's sequence omitted `backends` | refuter round 4 | acted | core's signature in both pages |
| 217 | `DoctorStep` gave "step" a third meaning | refuter round 4 | acted | `DoctorProbe`, with "probe" in the glossary (N23) |
| 218 | `FakeOutside` and `FakePlatform` break the Fake naming rule, `<<Records>>` is not a role in the table | refuter round 4 | acted | `FakeOutsideWorld`, `FakeFirmwarePlatform`, the stereotype says proposed role. Slice 2 edits developing.md's table |
| 219 | No effect word covers running a tool, so `run` was never gated | refuter round 4 | acted | a `runs` effect gates `run` (core.md, C4) |
| 220 | The plan says walk 2 needs 0a and 1, but the PO was asked only about 0a | refuter round 4 | acted | README.md decision 3 covers slices 0a and 1 |
| 221 | "Five lambdas" in `FirmwarePlatform`: it is three lambdas and two classes (`firmware_platform.py:55-60`), and `make_shell_command` was missing | refuter round 4 | acted | bench.md text and class diagram fixed |
| 222 | Area pages ran 154 to 197 lines, mostly mermaid | refuter round 4 | acted | the file moves went to refactor-plan.md, redundant flowcharts and bare class lines dropped. Pages now 131 to 157 lines (N17) |
| 223 | Fake tool processes first on `PATH` find nothing: esptool and mpremote are `kind: python` rows found by `find_spec` (`data/tools.json:130-149`, `tools.py:164-165`) | planner, detailed plan | acted | S1 puts fake `esptool`, `mpremote` and `serial` modules first on the child's `PYTHONPATH` |
| 224 | `grant`, `live` and `reach` print a flat JSON line, not an envelope (`grant.py:63`, `live.py:68`, `reach.py:63`), so making them Operations with `JsonEnvelope` changes public keys | planner, detailed plan | acted | `FlatJsonLine` keeps today's line. An envelope for them is out of scope |
| 225 | `deploy` prints lines while the flash runs (`deploy.py:121-123`), so `lines` rendered at the end lose the progress | planner, detailed plan | acted | `OutsideWorld.show_line` (S5) |
| 226 | One `outside=` override cannot replace `tools.find`, which bench tests patch 19 times, because `Backends` is not in `OutsideWorld` | planner, detailed plan | acted | `run_cli` and each `main` take `backends=None` too (S5) |
| 227 | "`look.py` at most 40 lines" is false while its 24-line `EPILOG` (`look.py:15-38`) stays in the CLI | planner, detailed plan | acted | the limit is `look.main` at most 15 lines; R1's CLI limit counts code lines |
| 228 | "A fast lane under 60 s": moving `test_mutate` and `test_needs.py:1416` out of 122.2 s leaves about 87 s | planner, detailed plan | acted | S13's target is under 90 s |
| 229 | `requirements.json` has no `platform` key; no script reads one | planner, detailed plan | acted | `Backends.platform` is always `DEFAULT_PLATFORM` until a second platform exists |
| 230 | A fake `run` alone does not stand in for `ConsoleProbe`: it checks the port with `os.path.exists` (`board_console.py:89`) | planner, detailed plan | acted | S7's tests use a temp file as the port |
| 231 | `check_bom.py` (185 lines) and `download_mode.py` had no area in the moves; `converter_command` sits at `check_spine.py:208`, not `:509` | planner, detailed plan | acted | checks and bench tables, build table fixed |
