# P323 round 4: naming and consistency

> **TL;DR.** About twenty words carry two to five meanings each, in the design and in today's code. Fix the new names
> now, while they cost nothing: "door" becomes CLI, "outcome" becomes status, `Layers` becomes `RecordFolders`. Rename
> private classes in their area's move. Keep every public flag and JSON key, and give each one meaning in a glossary.

## 1. Glossary (one word, one meaning)

| Term | Meaning |
|---|---|
| CLI | a script in `scripts/` with a `main()`: parses, runs one operation, prints. One of spark's interfaces (AGENTS.md:27), beside agents and a later MCP server. Replaces "door". |
| operation | one named job a CLI runs, printed as `op` |
| area / module | one package folder under `scripts/spark/` / one Python file |
| status | `ok`, `problems`, `could-not-run`, and `skipped` for a check or stage not run (outcomes.py:21,26). Replaces "outcome"; the module keeps its name. |
| exit code | the number the process exits with, from `EXIT_FOR` (outcomes.py:31). Always two words. |
| code | a constant naming one problem or unchecked item, as `NotKeptResult` has (breadboard_keep.py:63). Never an exit number. |
| sentence / why | the text a person reads in a problem (outcomes.py:70) / in a step (outcomes.py:84) |
| record / fact / reading | a JSON file of facts with an origin (part, board, chip), never a log / one field of it / what a board said on USB (`BoardReading`), not a fact until a record holds it |
| library / store / project | the record folders spark ships / the person's `SPARK_HOME` / the gadget's folder |
| design / build | the netlist and pin map / the chain from requirements to design, sheet, diagram and checks |
| stage / step | one link of the build chain (`BuildStage`, JSON `stages`) / an action that may come next (JSON `next`) |
| platform | the firmware's language family, such as MicroPython (`FirmwarePlatform`) |
| board / port / image | the dev board, its record or the one on USB / its serial device (`--port`) / the flash image a simulation tested |
| check / tool | one `Check` subclass that grades a design, run by `check_all` / an outside program, one row in `data/tools.json` |

## 2. Clashes

| Word | Meanings found | Proposal |
|---|---|---|
| door / CLI / interface | design's "door"; "fat CLIs" (facts.md:6); "interfaces" (AGENTS.md:27) | CLI, `run_cli`. Free: no code holds it yet. |
| outcome / status | design 2.4 "outcome, printed as `status`"; code has `status_of`, `STATUS_FOR`, `LookReport.status`. Design 4 lists three values, code prints four. | status, `SparkError(status, code, fix)`, four values listed |
| code | problem code (design 2.4); bare `code` for the exit code (board_envelope.py:80,123); Python for the board (live.py:76, `BoardCodeError` board_connection.py:41) | bare `code` only for a problem code; `exit_code`, `source` in new code; flag stays |
| verdict | exit code (check_spine.py:582); status (check_all.py:492); match/warning/stop (board_look.py:178); ready/unknown (board_envelope.py:113) | private functions become `exit_code_of`, `overall_status`; JSON keys stay |
| person text | `sentence`, `why`, `reason` (check_all.py:82), `message` (emit_footprint.py:236), `detail` (check_spine.py:968) | new JSON uses only `sentence` and `why` |
| tool | outside program (tools.py:63); the envelope's `tool` names the CLI (outcomes.py:78); the `tools/` folder. Old output names the CLI as `tool` (check_physics.py:652) or `check` (check_spine.py:967). | define the key as "the CLI that printed this"; the envelope unifies it per CLI |
| check | `Check` (check_all.py:63); `BoardCheckStrategy`, `CheckResult` (board_doctor.py:54,74); `ReadyCheck` (ready_check.py:43); `grant.py --check`; `check_spine` is a build | `DoctorStep...` (doctor already says step), `ReadyProbe` beside `ConsoleProbe`, in the bench move |
| stage | build chain; deploy's `STAGE_*` (board_envelope.py:23); journey stages (facts.md:17) | build only; `DeployPhase` in code, JSON `stage` stays; "journey step" in prose |
| step | next action; wiring `Step` (breadboard_steps.py:34); a cost event (cost.py:84, parts.py:1637) | `WiringStep` in the breadboard move; the history field stays |
| record | fact file; `WiringRecord`, `RecordedStep` (breadboard_changes.py:39,103); design's `RunRecord` | `WiringLog`, `RunLog` |
| keep / kept | `check_spine --keep DIR` (:639); `parts --keep FILE`, `--kept` (parts.py:1595,1599); `breadboard_keep` | flags stay; new names say what is kept |
| facts | record fields; `FactsFile` holds a board's reading (board_facts.py:35) | `ReadingFile` in the bench move |
| port | serial device; MicroPython's build name `micropython_port` (flash_image.py:89) | key stays; prose says "MicroPython build" |
| board | dev board; `emit_board.py` writes the circuit; `Board` (check_physics.py:114) | `CircuitBoard`; script name stays |
| token | look's proof for `deploy --token` (board_look.py:231); the Wokwi CI secret | "Wokwi key" in prose |
| needs | a goal's needs (needs.py); a check's inputs (check_all.py:67) | `Check.inputs` |
| catalog / answer | `parts --catalog` (parts.py:1603) vs D3's "catalog"; `outcomes.answer` vs `parts.Answer` (parts.py:230) | "operation registry"; `OperationResult` in slice 2 |
| library | record folders (design 4); "library module" (AGENTS.md:27, developing.md:222) | the design PR edits AGENTS.md:27 too |
| Layers | design 2.3's folder Value; architecture layers (facts.md:11) | `RecordFolders` |
| finding | `Finding` twice (check_footprints.py:54, check_physics.py:93), `Failure` (compare_design.py:44), JSON `problems` | one `Problem` Value when checks move |

## 3. Vague or coined names

- Check classes `RulesVsNetlist`, `Physics`, `Buildability`, `VendorTruth`, `TheOrder` (check_all.py:121-264) become `RulesCheck`, `PhysicsCheck`, `BuildCheck`, `VendorPinsCheck`, `OrderCheck`.
- Ten exceptions lack `Error`: `Impossible`, `LookStop`, `NotDrawn`, `NotBuilt`, `CouldNotKeep`, `NoTranscript`, `UnknownMatcher`, `BadArgument`, `StoreProblem`, `ToolProblem`.
- developing.md and design 2.6 cite `EsptoolBoardReader`; the class is `EsptoolReader` (board_look.py:117).
- `EXIT_IMPOSSIBLE`, `EXIT_INVALID`, `EXIT_MISMATCH`, `EXIT_NOTHING_TO_DO` (assign_pins.py:46, boards.py:119, check_vendor_pins.py:44, init_project.py:44) name `EXIT_PROBLEMS` four more ways; outcomes.py:12 invites them.

## 4. Conventions

| Kind | Rule | Good | Bad |
|---|---|---|---|
| module | a noun for what it holds | `flasher.py`, `restricted_pins.py` | `board_facts.py` (holds readings) |
| class | role suffix from developing.md; subclass = what varies + base | `TerminalConsentStrategy` | `TheOrder`, `Impossible` |
| function | a verb; `why_` returns a reason or None; `require_` raises | `require_open_gate`, `status_of` | `verdict()` returning an exit code |
| flag | kebab-case noun of its value; unit in name or metavar; one meaning | `--project`, `--json` (14 CLIs each) | `--timeout` (s) beside `--timeout-ms`; `--keep` twice |
| JSON key | snake_case noun, one meaning across CLIs, only gains keys | `status`, `op`, `needs_yes` | `reason`, `message`, `detail` for `sentence` |
| code value | snake_case, named for the cause | `no_board`, `port_busy` | a sentence compared as text |
| exit code | the three `EXIT_*` names only; a child's exit names its program | `EXIT_FOR[status]` | `EXIT_NOTHING_TO_DO`; `EXIT_PORT_BUSY = 3` (board_console.py:37) |

## 5. What pays and what costs

- **Pays now, free:** names the design invents: CLI, status, `RecordFolders`, `OperationResult`, `WiringLog`, `RunLog`.
- **Pays in the area move:** private classes, exceptions and exit aliases. The move already edits every importer.
- **Costs more than it gives:** any flag, JSON key, record key or script name (`--circuit`, `--code`, `--keep`, `verdict`, `stage`, `tool`, `micropython_port`, `emit_board.py`). Pages and Claude read them, so define them instead.

## Rows

- "door" clashes with CLI and "interface": rename to CLI and `run_cli` in design.md.
- "outcome" beside `status`, and three values listed where code prints four: one word, status, four values.
- Bare `code` means an exit code and board source: `exit_code` and `source` in new code; `code` is a problem code.
- `verdict` has four meanings: rename the two private functions; JSON keys stay.
- Five keys hold the person's text: new JSON uses only `sentence` and `why`; the contract test lists allowed keys.
- `tool` and `check` both name the CLI in JSON: define `tool` in the glossary; the envelope unifies per CLI.
- Doctor and ready "checks" clash with `Check`: `DoctorStep`, `ReadyProbe` in the bench move.
- `stage`, `Step`, "record" and "facts" carry other meanings: `DeployPhase`, `WiringStep`, `WiringLog`, `RunLog`, `ReadingFile`.
- `Layers`, "catalog" and `parts.Answer` clash: `RecordFolders`, "operation registry", `OperationResult`.
- Coined check classes and ten exceptions without `Error`: rename in each area move (S7, S12-style test).
- AGENTS.md:27 says "library module" and the docs cite `EsptoolBoardReader`: fix both docs in the design PR.
- Four exit aliases: drop each when a story edits its file; edit outcomes.py:12.
- Public flags and keys keep their spelling: add section 1 as a glossary in developing.md beside the role table.
