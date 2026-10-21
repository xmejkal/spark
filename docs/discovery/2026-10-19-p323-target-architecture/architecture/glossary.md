# Glossary: one word for one thing

> Each word below has one meaning in the code, the docs and the output. A name marked "proposed" does not exist in the
> code yet. The role words (Service, Strategy, Adapter, Value and the rest) are in the table in
> [developing.md](../../../guide/developing.md), and this page adds the other words.

Back to [the architecture](README.md).

## 1. The words

| Word | One meaning |
|---|---|
| CLI | A script in `scripts/` with a `main()`. It parses arguments, runs one Operation and prints. Replaces "door". |
| subcommand | One job of a CLI, such as `identify` in `board.py identify`. A CLI is one topic, a noun, and has one subcommand per job (P381). |
| frontend | What a person or Claude talks to: the CLI as text, the CLI with `--json` (Claude's commands, skills and agents), later an MCP server. |
| Operation | One job, one class with one public method `run()`, named verb + object, such as `IdentifyBoard`. Its module, class, op name and subcommand use the same words: the module `identify_board`, `IdentifyBoard`, `"identify-board"`, `board.py identify` (P381). Its name is printed as `op`. Proposed class. |
| helper | A class that does one thing for an Operation, with several methods about it. An `-er` noun or a plain noun, such as `ChipReader` or `GrantStore` (P381). |
| area | One package folder under `scripts/spark/`, such as `bench`. Proposed. |
| module | One Python file. Never "library module". |
| core | The area that holds the contract every other area uses. Proposed. |
| status | One of `ok`, `problems`, `could-not-run`. A check or a build stage also has `skipped`. Replaces "outcome". |
| exit code | The number the process exits with: 0, 1 or 2, from `EXIT_FOR` (`outcomes.py:31`). Always two words. |
| code | A constant in snake_case that names one problem or unchecked item, such as `no_port`. Never an exit code. |
| Finding | One item in `problems`, `unchecked` or `unmeasured`: severity, subject, code, sentence, fix, fix_step. Proposed class. |
| severity | Which list a Finding goes in: `problem`, `unchecked` or `unmeasured` (`outcomes.py:49`). |
| OperationResult | What an Operation returns: data, findings, next steps and lines. Proposed class. |
| envelope | The JSON form of an OperationResult, version 1 (`outcomes.py:68`). It only gains keys. |
| NextStep | One action that comes next, JSON `next`. Proposed class over `outcomes.step` (`outcomes.py:84`). |
| fix | The text that says what to do about a Finding. A string, as today (`board_envelope.py:58`). |
| fix_step | The same advice as a NextStep, or null. A new key beside `fix`, so the envelope only gains keys. Proposed. |
| sentence | The text a person reads in a Finding. |
| why | The text a person reads in a NextStep. |
| lines | Text for a person. stdout without `--json`, stderr with it. Replaces the proposed `diagnostics`. |
| effect | What an Operation does outside: `reads`, `writes`, `runs` (a tool), `network`, `board`, `erases`. `runs` is proposed. |
| OutsideWorld | The Value that holds the callables for every effect: run, write, fetch, clock, consent, and the `environ` variables the Operation reads. Proposed. |
| probe | A read-only look at a board or a port: `ConsoleProbe`, `ReadyProbe`, `DoctorProbe`. It changes nothing on the board. | A class that changes the port, such as today's `ConsoleProbe.cure`, is no probe: the names pass (P382) splits it.
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
| design | The netlist and pin map derived from the requirements. |
| build | The chain from requirements to design, breadboard sheet, Wokwi diagram and checks. |
| stage | One link of the build chain, JSON `stages`. |
| step | An action that comes next (NextStep). A wiring line is a WiringStep. A journey has "journey steps". |
| platform | The firmware's language family, such as MicroPython (`FirmwarePlatform`). |
| board | The dev board, as a record or on USB. The circuit file is a "circuit". |
| port | The board's serial device, `--port`. |
| image | The flash image a passed simulation tested. |
| check | One `Check` subclass that grades a design, run by `check_all`. |
| tool | An outside program, one row in `data/tools.json`. In the envelope, `tool` names the CLI that printed it. |
| gate | The rule that opens or refuses an erase or a board write, with consent. |
| consent | The person's yes, asked by a `ConsentStrategy`. Never an argument. |
| rule | One line of the code standard, checked by `ArchitectureRules`. Proposed. |
| baseline | The list of today's rule breaches. It only shrinks. |
| golden | A file with the expected `--json` and exit code of one Operation on one fixture project. Proposed. |
| Fake | A stand-in for a real part in tests, in `tests/fakes.py`. `Fake`, then the whole name: `FakeOutsideWorld`, `FakeFirmwarePlatform`. |

## 2. Clashes and how they are settled

| Word | Meanings found today | Settled |
|---|---|---|
| door / CLI / interface | design.md's "door", AGENTS.md:27's "interfaces" | CLI. The helper is `run_cli`, proposed. |
| outcome / status | design.md 2.4 "outcome, printed as status". The code has `status_of`, `STATUS_FOR`. | status, four words. The module `outcomes.py` keeps its name. |
| code | problem code, exit code (`board_envelope.py`), Python for a board (`BoardCodeError`, `board_connection.py:41`) | code is a problem code. New code says `exit_code` and `source`. |
| verdict | exit code (`check_spine.py`), status (`check_all.py`), a look's stop or warning | private functions become `exit_code_of`, `overall_status`. JSON keys stay. |
| person text | `sentence`, `why`, `reason` (`check_all.py`), `message` (`emit_footprint.py:236`), `detail` (`check_spine.py`) | new JSON uses only `sentence` and `why`. |
| finding / problem / failure | `Finding` twice (`check_footprints.py:54`, `check_physics.py:93`), `Failure` (`compare_design.py:44`), `parts._problem` (`parts.py:238`) | one `Finding` in core. The three classes fold into it at the checks move. |
| answer | `outcomes.answer` (`outcomes.py:49`), `parts.Answer` (`parts.py:230`) | `OperationResult`. "answer" is not a class name. |
| check | `Check` (`check_all.py:63`), `BoardCheckStrategy` (`board_doctor.py:74`), `ReadyCheck` (`ready_check.py:43`) | `DoctorProbe`, `ReadyProbe`, both proposed, in the bench move. "Step" keeps one meaning, and both look without changing. |
| stage | build stages, deploy's `STAGE_*` (`board_envelope.py:23`) | build only. `DeployPhase` in code, proposed. JSON `stage` stays. |
| step | next action, wiring `Step` (`breadboard_steps.py:34`) | `NextStep`, `WiringStep` (proposed, breadboard move). |
| record | fact file, `WiringRecord` (`breadboard_changes.py:103`) | `WiringLog` (proposed). A simulation log is a `RunLog` (proposed). |
| facts | record fields, `FactsFile` that holds a reading (`board_facts.py:35`) | `ReadingFile` (proposed, bench move). |
| board | dev board, `Board` circuit class (`check_physics.py:114`) | `CircuitBoard` (proposed, checks move). Script names stay. |
| Layers | design.md 2.3's folder Value, and architecture layers | `RecordFolders`. |
| catalog | `parts.py --catalog`, a central Operation list | "operation registry" for the list. The flag stays. |
| parts | the record folder, `parts.py`, the area | the area is `sourcing`. The folder and the CLI keep `parts`. |
| needs | a goal's needs (`needs.py`), a check's inputs (`check_all.py:63`) | `Check.inputs` (proposed, checks move). |
| describe / render | person text in `render` (`check_all.py:434`) and `describe` (`board_doctor.py:188`) | `render` returns person text. `describe` is only the machine description. |

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
| `platform` | the requirements key that picks the firmware platform, default `micropython`. Proposed key: `deploy.py:171` hard-codes MicroPython today. |
| every script name | `emit_board.py`, `check_spine.py`, `look.py` and the rest keep their names. |
