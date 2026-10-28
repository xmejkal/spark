# Glossary: one word for one thing

> Each word below has one meaning in the code, the docs and the output. A name marked "proposed" does not exist in the
> code yet. The role words (Service, Strategy, Adapter, Value and the rest) are in the table in
> [developing.md](../../../guide/developing.md), and this page adds the other words.

Back to [the architecture](README.md).

## 1. The words

| Word | One meaning |
|---|---|
| CLI | A script in `scripts/` with a `main()`. It parses arguments, runs one Operation and prints. Replaces "door". |
| subcommand | One job of a CLI, such as `show` in `parts.py show`. A CLI is one topic, a noun, and has one subcommand per job. The subcommand is the verb alone (P381). |
| frontend | What a person or Claude talks to: the CLI as text, the CLI with `--json` (Claude's commands, skills and agents), later an MCP server. |
| Operation | One job, one class with one public method `run()`, named verb + object, such as `ShowPart`. Its module, class and op name use the same words: the module `show_part`, the class `ShowPart`, the op `"show-part"`, and its subcommand is the verb, `parts.py show` (P381). Its name is printed as `op`. An op in a golden or a command page today keeps its spelling, so `LookAtBoard` prints `look` (plan decision 5). Proposed class. |
| helper | A class that does one thing for an Operation, with several methods about it. An `-er` noun or a plain noun, such as `BoardReader` or `PortFinder`. A Service, a Store or an Adapter is a helper with its role word (P381). |
| area | One package folder under `scripts/spark/`, such as `bench`. Proposed. |
| module | One Python file. Never "library module". |
| core | The area that holds the contract every other area uses. Proposed. |
| status | One of `ok`, `problems`, `could-not-run`. A check or a build stage also has `skipped`. Replaces "outcome". |
| exit code | The number the process exits with: 0, 1 or 2, from `EXIT_FOR` (`outcomes.py:31`). Always two words. |
| code | A constant in snake_case that names one problem or unchecked item, such as `no_port`. Never an exit code. |
| Finding | One item in `problems`, `unchecked` or `unmeasured`: severity, subject, code, sentence, fix. Proposed class. |
| severity | Which list a Finding goes in: `problem`, `unchecked` or `unmeasured` (`outcomes.py:49`). |
| OperationResult | What an Operation returns: data, findings, next steps and lines. Proposed class. |
| envelope | The JSON form of an OperationResult, version 1 (`outcomes.py:68`). It only gains keys. |
| NextStep | One action that comes next, JSON `next`. Proposed class over `outcomes.step` (`outcomes.py:84`). |
| fix | The text that says what to do about a Finding. A string, as today (`board_envelope.look_envelope`). |
| sentence | The text a person reads in a Finding. |
| why | The text a person reads in a NextStep. |
| lines | Text for a person. stdout without `--json`, stderr with it. Replaces the proposed `diagnostics`. |
| effect | What an Operation does outside: `reads`, `writes`, `runs` (a tool), `network`, `board`, `deletes`. `runs` is proposed. The code and the goldens say `deletes`. |
| OutsideWorld | The Value that holds the callables for every effect: run, write, fetch, clock, consent, and the `environ` variables the Operation reads. Proposed. |
| probe | A read-only look at a board or a port: `ConsoleProbe`, `ReadyProbe`, `DoctorProbe`. It changes nothing on the board. A class that changes the port, such as today's `ConsoleProbe.cure`, is no probe: the names pass (P382) splits it. |
| backend | A swappable outside thing: a tool, the firmware platform, the store or the simulator. |
| Backends | The Value that holds every backend choice of one run, built once. Proposed. |
| registry | A dict in capitals from a name to a class, beside its base class, such as `MATCHERS` (`matching.py:222`). |
| record | A JSON file of facts with an origin: a part, a board or a chip. Never a log. |
| fact | One field of a record. |
| reading | What a board said on USB (`BoardReading`). Not a fact until a record holds it. |
| library | The record folders spark ships: `parts/`, `boards/`, `chips/`. |
| store | The person's folder, `SPARK_HOME`, never the repository. |
| project | The gadget's folder, with `requirements.json`. |
| RecordFolders | The Value of the three places a record lives: library, store, project. Proposed. Replaces `Layers`. |
| RecordKind | The Strategy of what differs per record kind: its `version`, `required` keys and `validate` rules. Proposed. Replaces `RecordSchema`. |
| RecordFinder | Reads one record kind across the three folders, the nearest wins. Proposed. Replaces `Records`. |
| Record | The Value of one loaded record, with its kind and place. Proposed (P391). |
| Brief | The Value of the project's brief in `.spark/project.json`: `prefer`, `sellers`. Proposed, in records. |
| DeployRecordStore | The Store that reads and records what spark knows of the last deploy to a board (`scripts/deploy_record_store.py`, P431). Moves to records. |
| leaf | A module that imports nothing of spark. Three today: `zone_time`, `text_guards` and `provenance`. |
| text guard | A function where text leaves spark: `printable` to the screen, `clean` to the store, `one_line` to a generated file. All three live in `text_guards` (OC8). |
| kanban | The team's GitHub Projects board. Its tool is `tools/kanban.py` after the rename, today `tools/board.py`. |
| trace | The one callable that `run_operation` gives an Operation's name, values, result and seconds after each run. Proposed. |
| design | The netlist and pin map derived from the requirements. |
| build | The chain from requirements to design, breadboard sheet, Wokwi diagram and checks. |
| stage | One link of the build chain, JSON `stages`. The refactor plan's units are waves. |
| wave | One of the six units of the refactor plan, a set of slices. Version 1 and the cards before 2026-10-26 say "stage" for it. P391's design keeps its own word, stage. |
| step | An action that comes next (NextStep). A wiring line is a WiringStep. A journey has "journey steps". |
| platform | The firmware's language family, such as MicroPython (`FirmwarePlatform`). |
| board | The dev board, as a record or on USB. The circuit file is a "circuit". |
| port | The board's serial device, `--port`. The "port" of ports and adapters is a seam. |
| seam | A Strategy base or a Value that a backend fills, so the core sees no tool: `FirmwarePlatform`, `OutsideWorld`. The papers say port. |
| image | The flash image a passed simulation tested. |
| check | One `Check` subclass that grades a design, run by `check_all`. |
| tool | An outside program, one row in `data/tools.json`. In the envelope, `tool` names the CLI that printed it. |
| gate | The rule that opens or refuses an erase or a board write, with consent. |
| consent | The person's yes, asked by a `ConsentStrategy`, or given by a stored grant. In a graph, `DeferringConsentStrategy` (proposed) never asks: its `require_ready` raises with the next step, and the Operation returns a `needs_yes` step with the command for the person's own terminal. Never a CLI flag: a Strategy in `OutsideWorld`, or the token. |
| rule | One line of the code standard, checked by `ArchitectureRules`. Proposed. |
| baseline | The list of today's rule breaches. It only shrinks. |
| golden | A file with the expected `--json` and exit code of one Operation on one fixture project. Proposed. |
| Fake | A stand-in for a real part in tests, in `tests/fakes.py`. `Fake`, then the whole name: `FakeOutsideWorld`, `FakeFirmwarePlatform`. |
| Wokwi definition | The kept JSON file of one Wokwi part type, a board included, a `documents` entry of its record (`wokwi-board`). Never "part", which is a part record (P396). |
| limit | One thing that no simulation can show of the project, as a component and a sentence: a line of `sim/WHAT-THIS-CANNOT-SHOW.md`, of the log's limits section and of `data.limits` of the look (P37, P396, P345). |
| caveat | One thing that this passed run did not test, as a sentence: a scenario with no `set-control` step, or a log that cannot be counted. A list of them is `data.caveats` (P345). |

## 2. Clashes and how they are settled

| Word | Meanings found today | Settled |
|---|---|---|
| door / CLI / interface | design.md's "door", AGENTS.md:27's "interfaces" | CLI. The function that runs a CLI is `run_cli`, proposed. |
| outcome / status | design.md 2.4 "outcome, printed as status". The code has `status_of`, `STATUS_FOR`. | status, four words. The module `outcomes.py` keeps its name. |
| code | problem code, exit code (`board_envelope.py`), Python for a board (`BoardCodeError`, `board_connection.py:41`) | code is a problem code. New code says `exit_code` and `source`. |
| verdict | exit code (`check_spine.py`), status (`check_all.py`), a look's stop or warning | private functions become `exit_code_of`, `overall_status`. JSON keys stay. |
| person text | `sentence`, `why`, `reason` (`check_all.py`), `message` (`emit_footprint._report`), `detail` (`check_spine.py`) | new JSON uses only `sentence` and `why`. |
| finding / problem / failure | `Finding` twice (`check_footprints.py:54`, `check_physics.py:93`), `Failure` (`compare_design.py:44`), `parts._problem` | one `Finding` in core. The three classes fold into it at the checks move. |
| answer | `outcomes.answer` (`outcomes.py:49`), `parts.Answer` | `OperationResult`. "answer" is not a class name. |
| check | `Check` (`check_all.py:63`), `BoardCheckStrategy` (`board_doctor.py`), `ReadyCheck` (`ready_check.py:43`) | `DoctorProbe`, `ReadyProbe`, both proposed, in the bench move. "Step" keeps one meaning, and both look without changing. |
| stage | build stages, deploy's `STAGE_*` (`board_envelope.py`) | build only. `DeployPhase` in code, proposed. JSON `stage` stays. |
| step | next action, wiring `Step` (`breadboard_steps.py:34`) | `NextStep`, `WiringStep` (proposed, breadboard move). |
| record | fact file, `WiringRecord` (`breadboard_changes.py:103`) | `WiringLog` (proposed). A simulation log is a `RunLog` (proposed). |
| facts | record fields, `FactsFile` that holds a reading (`board_facts.py`) | `ReadingFile` (proposed, bench move, S11). |
| clock | `SystemClock` (monotonic, sleep), `board_grant.read_local_time` (the wall time), `FakeClock`, `FakeLocalClock` | `SystemClock` is the one clock with `now`, `monotonic`, `sleep`. One `FakeClock` (S7a). |
| Operation | a class with `run()` (this page, the standard), a Value holding a function (`core.md`, v1) | a class with `run()`, one module each, `OPERATIONS` in the area's `__init__.py`. |
| board | dev board, `Board` circuit class (`check_physics.py:114`) | `CircuitBoard` (proposed, checks move). Script names stay. |
| Layers | design.md 2.3's folder Value, and architecture layers | `RecordFolders`. |
| catalog | `parts.py --catalog`, a central Operation list | "operation registry" for the list. The flag stays. |
| parts | the record folder, `parts.py`, the area | the area is `sourcing`. The folder and the CLI keep `parts`. |
| needs | a goal's needs (`needs.py`), a check's inputs (`check_all.py:63`) | `Check.inputs` (proposed, checks move). |
| describe / render | person text in `render` (`check_all.py:434`) and `describe` (`board_doctor.py`) | `render` returns person text. `describe` is only the machine description. |
| fact value | `emit_board.fact_value` (deleted in P431), `boards.is_fact_value`, `boards.fact_value_problems` | `provenance.read_value`, `boards.is_pin_map_constant`, `boards.board_fact_problems`. Settled in [section 3 of the plan](refactor-plan.md#3-names-the-clashes-and-their-role-names). |
| power | a part's `power` list, a board's `power` block, `power_pads`, the verb `power` | `supply_pins` and `power_facts` in code. The record keys stay. Settled in [section 3 of the plan](refactor-plan.md#3-names-the-clashes-and-their-role-names). |
| board (Kanban) | `scripts/boards.py` reads dev board records, `tools/board.py` reads the team's GitHub board | `tools/kanban.py`. Settled in [section 3 of the plan](refactor-plan.md#3-names-the-clashes-and-their-role-names). |
| brief | `parts._brief` (a part's three-key summary), the project's brief | `_part_summary` and `Brief`. Settled in [section 3 of the plan](refactor-plan.md#3-names-the-clashes-and-their-role-names). |
| not checked | `LastDeploy.state` with `why`, `ScenarioSteps.unread`, `None` from a reader | one shape, `state` and `why`, with the three words and `NOT_CHECKED_MESSAGE` in `outcomes.py` (OC4, done in P428). Settled in [section 3 of the plan](refactor-plan.md#3-names-the-clashes-and-their-role-names). |

## 3. Public names that stay, each with one meaning

A public name is one a person or Claude types or reads. Renaming one costs every page, skill and habit that uses it,
so each stays and the glossary fixes its meaning.

| Name | Its one meaning |
|---|---|
| `--json` | print one envelope on stdout, nothing else |
| `--project` | the project folder, default "here" |
| `--port` | the board's serial device |
| `--keep` | two meanings today: `parts.py --keep FILE` and `check_spine.py --keep DIR`. A card asks the PO to rename one. |
| `--circuit`, `--code`, `--dry-run` | as each CLI's help says. Unchanged. |
| `status`, `op`, `tool`, `data`, `problems`, `unchecked`, `next`, `truncated`, `notes`, `assumptions` | the envelope's keys (`outcomes.py:68`) |
| `needs_yes` | the step needs the person's consent |
| `needs_person` | the step needs a hand on the bench, such as plugging USB. Proposed key. |
| `stage`, `stages`, `verdict` | the JSON keys keep their spelling. Code names follow section 2. |
| `micropython_port` | the MicroPython build a board record names. A fact the platform reads. |
| `platform` | the requirements key that picks the firmware platform, default `micropython`. Proposed key: `deploy.main` builds `FirmwarePlatform.micropython` today. |
| every script name | `emit_board.py`, `check_spine.py`, `look.py` and the rest keep their names. |
