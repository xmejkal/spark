# P323: spark's target architecture and code standard

Card [P323 #413](https://github.com/xmejkal/spark/issues/413), epic P158 [#94](https://github.com/xmejkal/spark/issues/94).
Built on [P322's facts](../2026-10-19-p322-code-architecture/facts.md). 2026-10-19.

## Council

- **Round 1** (papers in `council/`): architect, AI interface, standards, migration and tech lead, on the everyday
  model. The synthesis on Opus picked the smaller option at each split.
- **Refuter** (Opus): nine findings confirmed, one rejected. It removed library shims and the global catalog, added a
  `build` area, and fit `Argument` to `parts.py`.
- **Round 2**: tech lead (Opus) fixed the area graph cycle, the many-operation door, the platform key and the seam
  tests. Senior (Sonnet) made `run_door` and the baseline buildable. PO assistant (Sonnet) rewrote the top.
- **Round 3**: extensions and simplicity (Opus), testing, Claude operator and safety (Sonnet). It cut 10 areas to 8,
  split `run_operation` from `run_door`, put safety into rules, and added goldens to slice 1a.

> **TL;DR.** We move spark's logic out of the big scripts into one package, area by area. Each script keeps its name
> and flags. Its output only gains keys, and a crash exits 2. Each job gets one declared list of arguments and results,
> so the script, `--help` and Claude read the same thing. One automatic test enforces the code rules and only lets the
> list of known breaches shrink. Only step 1a, which records today's outputs and fixes the measure, could run before walk 1.

**Your call:** say yes to this design, and answer the one question in section 8.

**Summary.** spark keeps its scripts as doors and moves their logic into a package inside `scripts/`, so no plugin
path changes. Each job becomes an Operation in its area's `operations.py`, and the door, `--help` and `--describe` read
that list. Until v0.13 only the per-story pay-down runs, and the area moves are v0.13's work.

Sections 1 to 7 are reference. The TL;DR and section 8 are enough to decide.

## Refuter round

Nine findings were acted on: no library shims (R2), `rglob` guards (R3), a `build` area (R4), no global catalog (R5),
`Argument` fit to `parts.py` (R6), only slice 1a before walk 1 (R7), consistent criteria (R8), one meaning per word
(R9) and one small helper (R10). R1, a `spark` name clash, was rejected. Every row is in
`docs/observations/rows/p323-target-architecture.md`.

## Round 3

| Finding | What changed |
|---|---|
| The platform key and its scope | Key in requirements, default `micropython`. The platform owns the pin map and image too. |
| A missing board silently loads the active ESP32 (`boards.py:253`) | A requirements file with no board answers `no_board`. A no-MCU platform is deferred. |
| `run_door` mixes parse, run and print | `run_operation` split out in slice 2 |
| 10 areas | 8: simulation joins firmware, setup joins build, tool install joins records |
| Safety by convention | S14 to S18: effects need a gate, consent from the process, one writer, secrets masked, paths shortened, dry run in `run_door` |
| Records read the environment in many places | One `Layers` Value, versioned `RecordSchema` |
| Test gaps | Role test shapes, contract mixins, safe goldens, `--retarget`, patch guard |
| Claude's walk | Walk-1 goldens in 1a, `loop_status`, `operations.md`, starter codes, `needs_person` |
| Terms | exit status, outcome printed as `status`, `BuildStage`, `ArchitectureRules`, "Done when", library |
| Built too early | No Renderer or MCP-client seam test, measure columns enter when they move, no `MagicMock` line |

Rejected or deferred, with reasons in the rows file: a `project` area, an `EXPORTERS` registry, an online store layer,
a `Clock`, `check_all --all` and a `firmware_pins` check.

## 1. Decisions

| # | Decision | Choice | Why | From | Where lenses disagreed |
|---|---|---|---|---|---|
| D1 | Package home | `scripts/spark/` | `scripts/` is already on `sys.path` for doors and tests. The 110 plugin paths stay. | migration | Architect: top-level `spark/` |
| D2 | Operation | Role Operation: a frozen dataclass `Operation(name, summary, arguments, effects, codes, data, description, epilog, run)`. `name` is the envelope's `op`. | It generalises `parts.py`'s `OPERATIONS` table (line 1581). | architect, AI interface | AI lens: a typed `Input` dataclass |
| D3 | Wiring | No container, no `wiring.py`, no catalog. Each area's `operations.py` holds its `OPERATIONS` and builds its Services. Registries are dicts beside their base class. | A central import lets one broken area break all doors. | architect, tech lead, refuter | The catalog returns with an MCP door, as a list of area names imported one by one. |
| D4 | Adapters | An Adapter lives in the area of its Strategy. Only Adapters run outside programs. | `flasher.py` already does. | standards, migration | `adapters/` tree dropped. |
| D5 | MCP | A tool's MCP version is a setting (`kind: mcp` rows). An MCP door for spark comes last, on a trigger: a host with no shell, or P178. | It costs a process and tool definitions in every session. | all | none |
| D6 | Type checker | None. Public functions in `spark/` carry hints. | Free, few, local. | standards | none |
| D7 | Size limits | Function 60 lines, module 600, door file 40. | A ratchet, not a big bang. | standards, tech lead | none |
| D8 | `mock.patch` | None new except `os.environ`. A file's count never rises. | 336 today. | standards, migration | No sweep. |
| D9 | Errors | One `SparkError(outcome, code, fix)`, area subclasses ending in `Error`. A crash is `could-not-run`, code `crash`, exit 2. | `agents.md:501`: exit 2 is "it could not look". | standards, AI interface | none |
| D10 | Enforcement | One test, `tests/test_architecture.py` (class `ArchitectureRules`), with `tests/architecture_baseline.json`. | One tool, no hook edit. | standards, migration | `tools/check_style.py` merged in. |
| D11 | Roles | Add **Operation** and **Records** to developing.md's table. | `Command` and `Library` mean other things. | architect | Command, Library, Policy dropped. |
| D12 | Several MCUs | One board per project stays. The v0.13 promise in `developing.md:301` and `journey.md:875` moves to P318. This design's PR edits both. | No abstraction before its second case. | tech lead | `Project.targets` deferred. |
| D13 | Timing | Until v0.13, the per-story pay-down only. A story may pull its area forward. Area moves are v0.13's work. | AGENTS.md: the whole-repository change waits for v0.13. | tech lead | none |
| D14 | Moves | No shim for a library module. A move updates every importer in the same PR. | See R2. | refuter | Shims dropped. |
| D15 | Areas | 8 areas. Firmware holds simulation, build holds setup, records holds tools. | Removes two edges and a loop. | simplicity | 10 to 8. |
| D16 | No MCU | Small fix now: no silent default board. A no-MCU platform waits for a 555-style project. | The board contract requires `chip` and `wokwi_part_type` (`boards.py:62`). | extensions, simplicity | Extensions: `"board": null` now |

## 2. The target architecture (reference)

### 2.1 Layout and areas

```
scripts/                 the doors: same names and flags as today
  look.py ...            imports its area's OPERATIONS and calls run_door. At most 40 lines.
  spark/
    core/                outcomes, errors (SparkError), operation (Operation, Argument), door (run_operation, run_door)
    records/             store, Layers, tools (tool_finder, install), BoardRecords, PartRecords, RecordSchema
    parts/               drawer, needs, matching, cost, datasheets, requirements
    design/              design, restricted_pins, pin_assigner, netlist, board_emitter/, emit_footprint, fab, copper
    firmware/            FirmwarePlatform, flash_image, import_firmware, project_image, sim_project, run_scenario, SimulationEngine
    breadboard/          steps, drawing, keep, changes, match, tabbed_page
    checks/              Check, the five checks, physics, compare_design
    bench/               look, deploy, grant, doctor, live, reach, Flasher, BoardConnection, console
    build/               BuildService, one BuildStage per stage, init_project, ai_files, loop_status
```

```mermaid
flowchart TB
  subgraph Doors["Doors: scripts/*.py"]
    D1["look.py uses bench OPERATIONS"]
    D2["check_spine.py uses build OPERATIONS"]
  end
  subgraph Areas["Areas, each with operations.py"]
    BUILD[build] --> BB[breadboard]
    BUILD --> CHK[checks]
    BUILD --> FW[firmware]
    BENCH[bench] --> FW
    BB --> DES[design]
    CHK --> DES
    FW --> DES
    DES --> PARTS[parts]
    PARTS --> REC[records]
  end
  CORE["core: outcomes, errors, Operation, run_operation, run_door"]
  D1 --> BENCH
  D2 --> BUILD
  Doors --> CORE
  Areas --> CORE
```

### 2.2 The dependency rule

| Module | May import |
|---|---|
| a door in `scripts/` | its own area's `operations`, `spark.core` |
| an area | itself, the areas below it (reachable by the arrows), `core` |
| `core` | Python's built-ins only |

Only public names cross a module border. Nothing in `spark/` has a `main()`, calls `print` or `sys.exit`, or imports
a door. Where a flow spans two areas, the higher area passes the step in.

### 2.3 Core abstractions

New are `RecordSchema(kind, version, rules)`, `Layers` (the library, store and project folders, built once from
`store.home()` and the project path), `BuildService` (one `BuildStage` per stage, emitter in process) and
`BoardRecords` and `PartRecords` (one record kind read across the `Layers`). Only `records` reads `SPARK_HOME`. The
deploy classes keep their names.

### 2.4 Operation and envelope

An Operation's `name` is the word the envelope prints as `op`, such as `look`. Names are unique across spark. An
`Argument` holds a flag and its argparse keywords (`nargs`, `metavar`, `type`, `dest`, `default`). `data` lists the
keys of the envelope's `data`.

An area's `operations.py` holds its `OPERATIONS` tuple. A door imports it and calls `run_door`, so `parts.py`'s 30
Operations fit a 40-line door. With several Operations, each selector is its own flag in a required group of mutually
exclusive flags, as `parts.py` does today. Its 11 shared `OPTIONS` rows go in as `options=`.

`effects` come from `reads`, `writes`, `network`, `board`, `erases`. `codes` list every code the Operation may emit.
For `check_all`, `codes` is the union of each `Check`'s own `codes`. `run` returns an `outcomes.answer`, and
`status_of` decides the outcome, printed as `status`. The envelope keeps v1's keys and adds:

- a `code` on each problem and unchecked item. Code and Claude branch on it, never on the sentence. Starter codes:
  `tool_missing`, `no_project`, `no_requirements`, `no_board`, `no_port`, `port_busy`, `image_stale`, `sim_failed`, `crash`.
- `outcomes.step` for each `fix` and `next` entry (`op`, `argv`, `why`, `effects`, `needs_yes`, `needs_person`).
  `needs_yes` is consent. `needs_person` is a hand on the bench, such as plugging the USB cable.
- `diagnostics`: lines for a person, which `run_door` writes to stderr.

### 2.5 Extension seams

A seam is a swap point. Each is a registry (a dict from a name to a class) or a record, so its caller never changes.

| To add | You write |
|---|---|
| a board | a JSON record in `boards/`, for an ESP32 that Wokwi and MicroPython run |
| an MCU platform | one `FirmwarePlatform` subclass with its factories, a pin map writer and an image maker, its Adapters, one line in `PLATFORMS`. The key enters with the second platform as requirements' `firmware` field, default `micropython`, since the project picks the language. |
| no MCU | deferred (D16). Today a requirements file with no board answers `no_board`. |
| several MCUs | a second project folder (D12) |
| a tool | a row in `data/tools.json` and one Adapter, found by role through `records/tools` |
| a tool's MCP version | a `kind: mcp` row for the same role and one Adapter, picked by the person's setting |
| a check | one `Check` subclass with its `codes`, one line in `CHECKS` |
| a simulator | one subclass (an Adapter) of the `SimulationEngine` Strategy, with `prepare(design)` and `run(scenario)`, one line in `ENGINES`. Engine facts move under `simulation.<engine>` in records then. |
| a renderer | one Renderer, one line in its registry |

### 2.6 Running an Operation

```python
def run_operation(operation, values, **collaborators) -> answer
def run_door(prog, operations, argv=None, *, options=(), **collaborators) -> int
# look.py:  def main(argv=None, run=subprocess.run): return run_door("look.py", OPERATIONS, argv, run=run)
```

`run_operation` has no argparse and no stdout, so a later MCP door or page server calls it too.
`run_door` builds the parser (`prog`, `description`, `epilog`, `options`), turns a bad argument into an answer, calls
`run_operation`, prints, and returns `EXIT_FOR[status]`. Before it prints, it shows paths under the project as relative
and under the store as `$SPARK_HOME/...`, and masks the value of every `account_env` variable in `tools.json`. A
`crash` holds the class and a short message, and the traceback goes to stderr only with `--debug`.

Consent: `run_door` refuses an Operation with `erases` or `board` unless the door's process gave a `consent`
collaborator. A yes is never an Argument or a tool input. An MCP door gets only the terminal strategy, which fails closed.

Dry run: `--dry-run` makes `run_door` pass recording Fakes for `run` and the `FileWriter`, and the envelope lists
`data.would_write`. It lands with the first writing Operation.

A Service takes its collaborators in `__init__` with real defaults, as `DeployService` does.

```mermaid
classDiagram
  class Operation {
    <<Operation>>
    name
    arguments
    effects
    codes
    run(values, collaborators) answer
  }
  class Argument {
    <<Value>>
    flag
    keywords
  }
  class SparkError {
    <<Error>>
    outcome
    code
    fix
  }
  class FirmwarePlatform {
    <<Platform>>
    make_flasher()
    make_connection()
    pin_map_text(design)
    make_image(project)
  }
  class Flasher {
    <<Strategy>>
  }
  class EsptoolFlasher {
    <<Adapter>>
  }
  class SimulationEngine {
    <<Strategy>>
    prepare(design)
    run(scenario) RunRecord
  }
  class WokwiCliEngine {
    <<Adapter>>
  }
  class Check {
    <<Strategy>>
    codes
    answer(design) answer
  }
  class BuildService {
    <<Service>>
    run() BuildResult
  }
  class BuildStage {
    <<Strategy>>
  }
  class BoardRecords {
    <<Records>>
    load(board_id)
  }
  class Layers {
    <<Value>>
    library
    store
    project
  }
  Operation o-- Argument
  Operation ..> SparkError
  FirmwarePlatform ..> Flasher
  Flasher <|-- EsptoolFlasher
  SimulationEngine <|-- WokwiCliEngine
  BuildService o-- BuildStage
  BoardRecords --> Layers
```

```mermaid
sequenceDiagram
  actor P as Person or Claude
  participant D as scripts/look.py (door)
  participant H as run_door
  participant R as run_operation
  participant O as Operation look
  participant S as LookService
  participant A as EsptoolBoardReader (Adapter)
  P->>D: look.py --project p --json
  D->>H: run_door("look.py", OPERATIONS, argv, run=run)
  H->>H: parse, check consent
  H->>R: run_operation(look, values, run=run)
  R->>O: run(values, run=run)
  O->>S: look()
  S->>A: read(port)
  A-->>S: BoardReading, or ToolMissingError
  S-->>O: LookReport
  O-->>R: answer(problems with codes, next, diagnostics)
  R-->>H: answer
  H->>H: status_of, shorten paths, mask secrets, EXIT_FOR
  H-->>P: envelope on stdout, diagnostics on stderr, exit 0, 1 or 2
```

## 3. The code standard (reference)

"AST test" means `ArchitectureRules`, a test that reads the code's structure with Python's `ast`, parsing each file once.

| # | Rule | Check | Scope |
|---|---|---|---|
| S1 | A class docstring starts with its role word from developing.md's table. | AST test | `scripts/` |
| S2 | A Value is a frozen dataclass or a NamedTuple. | AST test | `spark/` |
| S3 | Only a module that holds an Adapter calls `subprocess`, `time.time`, `urllib` or `os.environ`. Only `records` reads `SPARK_HOME`. | AST test | `spark/` |
| S4 | Imports follow 2.2. No private name crosses a module. No cycles. | AST test | `spark/` |
| S5 | No `main`, `print` or `sys.exit` inside `spark/`. A door file is at most 40 lines. | AST test | `scripts/` |
| S6 | Function at most 60 lines, module at most 600. | AST test | `scripts/` |
| S7 | Every exception subclasses `SparkError`, directly or through its area's Error, and ends in `Error`. `except Exception` only in `run_door`. | AST test | `spark/` |
| S8 | No new `mock.patch` except `os.environ`. A file's count never rises. Every patch target resolves to the module that defines the name. | AST test | `tests/` |
| S9 | Code decides on a constant or a code, never on a sentence. | `test_no_magic_strings.py` | all |
| S10 | Every Operation a command page calls has `--json`, prints `outcomes.envelope`, and has an entry by `name` in `tests/test_json_contracts.py`. | contract test | doors |
| S11 | Public functions have type hints. | AST test | `spark/` |
| S12 | No class name has Validator, Verifier, Checker, Command, Library, Context or Manager as a whole CamelCase word. No function name has validator, verifier, checker or manager as a whole word. | AST test | all |
| S13 | A base class has two subclasses or a Fake in `tests/fakes.py`. | AST test | `spark/` |
| S14 | Each Strategy has a contract mixin of its name (`FlasherContract`) that its real classes and its Fake pass. | AST test | `tests/` |
| S15 | An Operation with `erases` names its gate. Only `bench/deploy` reaches the erase Adapter, through `require_open_gate`. | AST test, seam test | `spark/` |
| S16 | Only `records` writes files, through `store.write_file` or the `FileWriter` collaborator. | AST test | `spark/` |
| S17 | A record reader refuses a newer schema with `schema_too_new`. A bump ships one tested `migrate(record)`. Spark never rewrites a person's file unasked. | `RecordSchema` test | `records/` |
| S18 | No secret value or home path reaches stdout, stderr or a project file. | marker test | doors |

"All" means `scripts/` and `tests/`. The baseline holds one sorted key per line, such as
`"S6|scripts/parts.py|_op_list": 71`. A breach reads `S4 scripts/spark/design/x.py:12 imports spark.bench (2.2)`. It
prints at most 20, then a count. `--lower` rewrites the baseline and can only lower it.

## 4. Vocabulary (reference)

The role words are developing.md's table: Service, Strategy, Adapter, Value (a small fixed record of facts), Result,
Store, Decorator, Renderer, Platform, Fake, Error, plus Operation and Records. This table holds the other words.

| Term | One meaning |
|---|---|
| record | a JSON file of facts with an origin (part, board, chip) |
| library | the record folders shipped with spark (`parts/`, `boards/`). A Python file is a module. |
| part | a component or breakout record |
| board | the dev board record: chip, pins, power, physical |
| store | the person's local folder (`SPARK_HOME`), never the repo |
| drawer | what the person owns, kept in the store |
| project | the person's folder with requirements, firmware and simulation |
| design | the netlist and pin map derived from requirements |
| build | requirements to design, sheet, diagram and checks |
| check | one deterministic test of a design that returns an answer |
| outcome | ok, problems or could-not-run, printed as `status` |
| exit status | the number a script exits with, from `EXIT_FOR` |
| code | a constant that names one problem or unchecked item |
| envelope | the JSON form of an answer, the same for every `--json` |
| operation | one named job a door runs, printed as `op` |
| step | a suggested next call in an envelope (`outcomes.step`) |
| door | a script (later an MCP server) that parses, runs one operation and prints |
| area | one package folder of related code with its own operations |
| image | the flash image that passed the simulation |
| gate | a rule that opens or refuses an erase or a board write, with consent |
| registry | a dict from a name to a class, such as `PLATFORMS` |
| seam | a swap point a test or a setting can fill |
| baseline | the list of today's rule breaches, which may only shrink |
| golden | a saved correct output a test compares with |
| mutation row | a planted defect that the suite must catch |
| stdlib | Python's built-in modules, the only ones spark uses |

## 5. The plan (reference)

### 5.1 Order

Slice 1a can run before walk 1 (section 8). Until v0.13, the slices below land with the first story that needs them:
1b, 2 (`look`), `loop_status` as the second Operation, 3 (codes for `look`), then the `build` and `check_all` envelopes
with codes and `fix` steps, then a generated `docs/guide/operations.md`, then `idea`, `init` and `drawer`. In v0.13 the
areas move: bench, breadboard, firmware, checks, design with build, then records and parts. About 30 PRs.

### 5.2 The first slices

**Slice 1a: guards, measure and goldens (about 190 lines).** Switch the guard tests that list `scripts/*.py`
(`test_store`, `test_orphans`, `test_fab`, `test_self_confirmation`, `test_board_look`) and `measure.py` to `rglob`.
Move `measure.py` to `tools/` with the columns `baseline`, `mock.patch` and suite seconds. Record goldens of the demo
project's `--json` for `check_spine`, `check_all` and `deploy --dry-run`, one file per Operation and outcome in
`tests/golden/`. Only `tests/golden.py --accept <op>` updates one file, printing the diff. No code under `spark/`. Done when: no door output changes, the suite count does not drop, a
test plants a module one folder down and each guard sees it, and a changed golden fails.

**Slice 1b: the architecture test (about 330 lines plus the baseline).** `ArchitectureRules(root)` takes a folder.
Unittest cases build a temp tree and plant one breach per rule. `tests/mutations/p323-architecture.json` plants the
same in the checker. developing.md gains one test shape per role, what only the bench proves (flash, console, button,
USB prompt) and a five-line "add a flag" example. Done when: every
planted breach is caught with its rule, file, line and reason, and the generated baseline passes.

**Slice 2: the first Operation (about 500 lines).** First commit: move `outcomes.py` to `core/outcomes.py` (39
importers) with `mutate.py --retarget OLD NEW`, which rewrites `file` only and refuses when `find` is not unique. Then
add `SparkError`, `Operation`, `Argument`, `run_operation`, `run_door` with path shortening, secret masking and the
consent refusal, and `bench/operations.py`. Turn `look.py` into a door. Done when: its JSON matches the golden,
`test_look` passes unchanged, each case's exit equals `EXIT_FOR[status_of(...)]`, the secret marker test and an
erasing Operation with no gate both fail as planted, and `look.py` is at most 40 lines.

**Slice 3: codes for `look` (about 150 lines).** Add `code` at the 6 sites in `board_envelope`, the `next` steps and
the contract entry. Point `commands/deploy.md`'s look step at the codes. Done when: the contract test fails on a
removed key and on an unlisted code.

### 5.3 How a move runs

- A move PR moves the modules, updates every importer, retargets every patch and mutation row with `--retarget`, and
  keeps private names reachable where tests use them. No library shim. A door keeps its path.
- Guard regexes (`test_store:78`, `test_orphans:52,82`) learn the package form in the same PR.
- The bench move, for scale: 17 modules, 34 importers, 188 mutation rows. Contract mixins land with their area.
- Done when: no golden changes, the test count does not drop, and the PR prints "rows N, caught N".
- Per story, always: no new baseline entry, and at least one paid down in a file the story edits.
- The suite takes 110 s today. At 150 s the hook shards it.

### 5.4 Measuring progress

**Known breaches left: N.** `tools/measure.py` prints the detail, and each PR pastes the before and after:

```
SCORE classes 16% | fat CLIs 3 | thin CLIs 4 | private imports 3 | outcome literals 10 | roles stated 56/103
      | baseline N | mock.patch 336 | suite 110 s
```

A new column enters in the slice that first moves it. No column may get worse. "Areas moved, of 8" and the Miro table
start with v0.13.

## 6. Acceptance criteria

Each is checked by a test or by `measure.py`.

1. `ArchitectureRules` runs in the suite. Its baseline holds no entry outside S8, and S8's count only falls.
2. Every door in `scripts/` is at most 40 lines and calls `run_door` (fat CLIs 0).
3. Every Operation a page calls has `--json`, prints `outcomes.envelope` and has a contract entry.
4. Every problem has a listed `code`, and Operation names are unique.
5. Private imports 0, outcome literals 0, roles stated on every class.
6. Seam tests: a second board record, a fake `FirmwarePlatform`, a requirements file with no board never loads the
   active board, a new `Check`, a fake `SimulationEngine`, and a tool row switched to another Adapter by the setting.
   Each plugs in with no caller edit.
7. A crash gives `could-not-run`, code `crash`, exit 2, with no traceback on stdout.
8. Walk 1 passes at every merge, and no move PR changes a golden.
9. A dry run of every writing Operation leaves the project's file tree unchanged.

## 7. What we will not do

- No DI container, entry points, `pyproject`, `src/` layout, `wiring.py`, `adapters/` tree or library shims.
- No pydantic, click, ruff or mypy.
- No catalog, `Workspace`, `project` area, `EXPORTERS` registry or online store layer before a second user needs one.
- No base class for one implementation, no record classes, no `targets` list, state store or ledger.
- No MCP door before every door runs on `run_door`.
- No area move before v0.13 unless a story pulls it. No behaviour change inside a move.

The same PR as this design edits `developing.md:237` and `:278` (the Error suffix now spreads beyond the deploy area),
`:225` and `measure.py`'s module kind `library` (now `module`), `developing.md:301`, `journey.md:875`, and agents.md's
nine "exit code" lines (now "exit status") with the crash line in its exit table.

## 8. The one question for the PO

The question is the same as before. Slice 1a now also records today's outputs of the walk-1 scripts.

**Slice 1a before walk 1, or after it?** Example: you start the walk on the bench tomorrow.

- (a) Slice 1a lands first. It is one PR of about 190 lines in tests and the measure script, and no script output changes.
- (b) Walk 1 first, and slice 1a lands with the first story after it.

Trade-off: (a) costs one review slot now, and its goldens catch any change in what walk 1 runs. (b) keeps every slot
on walk 1. The council proposes (a).
