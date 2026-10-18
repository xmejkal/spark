# P239 PR 8: DeployService

> TL;DR: the flow in `deploy.py`'s `main` (plan, look, gate, flash, facts, ready, recovery, log, record) moves into
> `scripts/deploy_service.py` as `DeployService`, which has no `print` and no `sys.exit`. A new `FirmwarePlatform`
> (`scripts/firmware_platform.py`) holds the parts that depend on MicroPython: flasher, connection, ready check, console
> probe. `main` parses, prints and maps the exit code. Every printed line, exit code and store record stays the same.
> Card [#238](https://github.com/xmejkal/spark/issues/238), brief item 4 of [P218's finish](../2026-10-17-p218-finish/brief.md).

## Council

(Filled in after each round.)

## What moves

| Now in `deploy.py` | Becomes |
|---|---|
| `plan()`, `newer_files`, `DeployPlan`, `OLDER_RUNS_WAY_OUT` | `DeployService.plan(port)`, same plan value, same notes |
| the look call in `main` | `DeployService.look(port)` returns the `LookReport` |
| gate, token re-check, `require_ready`, flash loop | `DeployService.deploy(report, token, consent, say)` |
| `put_facts`, `read_board`, the recovery block, `write_board_log`, `BoardLog`, `record_deploy` | `DeployService.verify(report, consent, say)` (private steps) |
| `board_of`, `chip_of`, `tools.find`, `EsptoolFlasher(...)`, `BoardConnection(...)`, `ReadyCheck(...)`, `ConsoleProbe.for_tool` | `FirmwarePlatform` methods, built by `FirmwarePlatform.micropython(project)` |

Stays in `deploy.py`: arguments, `EPILOG`, `WATCH`, `rerun_line`, `grant_hint`, `choose_consent` (they read `args` and
print), the dry-run, and the exit-code map. `--help`, exit codes, lines and the store record do not change.

## How output works without print

`DeployService` gets `say`, a function that takes one line (main passes `print(line, flush=True)`). It calls it for the
lines that must appear while a step still runs: `yes: ...`, `running: ...` before each command, and the R-press request.
Everything else is returned: `DeployResult` holds what main prints after the flash. A refusal is an exception that main
prints to stderr: `LookStop`, `DeployError`, `tools.ToolProblem` (exit 2) and `GateClosedError` (its own code). A flash
that fails raises `DeployError` with the sentence main printed before, `BOOT_HINT` tail included.

The brief names `deploy(token, consent, on_press_reset)`. Two changes: the `report` is an argument, because the person's
yes is chosen after the look and from its verdict; and one `say` replaces `on_press_reset`, because `yes:` and `running:`
need the same hook and the order of lines is the contract.

## Classes

```
FirmwarePlatform  (plain noun; not a Value, its parts act)       scripts/firmware_platform.py
  micropython(project)  classmethod                              MicroPython today; Arduino later is another builder
  flasher() -> Flasher               chip_of(project) + tools.find("flasher") -> EsptoolFlasher
  shell_command() -> argv            tools.find("board-shell") -> tools.command_for
  connection(command, port, run) -> BoardConnection
  ready_check(connection) -> ReadyCheck
  console_probe(port, run) -> probe or None
  board_of(), chip_of()              requirements.json's board, its chip (moved unchanged)

DeployService  (Service)                                         scripts/deploy_service.py
  __init__(project, platform, ignore_older_runs=False, run=subprocess.run, clock=None, probe=None)
  plan(port=None) -> DeployPlan      image checks, then the tools; raises DeployError / ToolProblem
  look(port=None) -> LookReport      board_look.looker(project, run).run(...)
  deploy(report, token, consent, say) -> DeployResult             gate, plan again, token, flash, then verify
  verify(report, consent, say) -> DeployResult                    facts, ready, recovery, board log, store record
DeployResult  (Result, namedtuple)   facts_line, ready, board_log, store_record, store_problem, repl_command
DeployPlan, BoardLog                 move with the service, unchanged
```

```
main            service            platform / look / gate / board
 |-parse------>|
 |-plan(port)->|-image checks------>| flasher(), shell_command()
 |<-DeployPlan-|  (--dry-run: main prints and returns 0)
 |-look(port)->|-looker.run-------->| board
 |<-LookReport-|
 | print lines; choose consent (grant or terminal)
 |-deploy(report, token, consent, say)->|-require_open_gate, say("yes:")
 |             |-plan(report.port), token check, require_ready
 |             |-run(command) x2, say("running:") before each
 |             |-verify: facts, ready, probe, say(R press), log, record
 |<-DeployResult  (or DeployError / GateClosedError)
 | print facts line, verdict, board log, store record; exit 0, 1 or 2
```

## Names, checked against developing.md's table

- `DeployService` ends in `Service`; `DeployResult` ends in `Result` (the table already lists both).
- `FirmwarePlatform` is a plain noun and its docstring says what varies (the brief dropped "Value").
- Methods start with a verb or answer as a noun of what they hand over: `plan`, `look`, `deploy`, `verify`; on the
  platform `flasher()`, `connection()` build and return one thing, like `tools.find`. The Strategy table row allows a
  plain noun for `Flasher`; the factory methods are named for what they return.
- `say` is a callback that takes a line. `store_problem` is a sentence; a field `store_record` is a path or None.
- One word for one thing: "report" is the `LookReport`, "result" is a `*Result`, "plan" is the `DeployPlan`.

## Tests, first

1. A golden capture (scratch, not committed) of every `deploy.main` call across `test_deploy`, `test_deploy_gate` and
   `test_journey_basic`: argv, exit code, stdout, stderr with temp paths and times replaced, plus `--help` and the
   dry-run. Taken before, compared byte for byte after.
2. `tests/test_deploy_service.py`: the service with fakes (no print: a `say` list holds the lines; `DeployError` for a
   failed flash); an ast test that `deploy_service.py` and `firmware_platform.py` hold no `print` call and no
   `sys.exit`; `FirmwarePlatform.micropython` returns EsptoolFlasher, BoardConnection, ReadyCheck.
3. `test_deploy.py` and `test_deploy_gate.py` keep their asserts; only their imports of moved names change.

## Docs and bookkeeping

developing.md (the paragraph on what each PR gave, and "Until PR 8 merges"), agents.md (the module list near line 424
if it names deploy's helpers; no JSON or exit code moves), `docs/guide` command pages unchanged. README and
`tools/journey.py`: no change, an internal refactor. Mutation table `tests/mutations/p239-pr8.json`; tables anchored on
moved lines are re-anchored. Observation rows from AT450 (P287's PR takes AT420 onward).

## Not done

The real flash: it waits for the PO's bench (P213b's walk or P290's). The one recovery path (the brief's decision:
move, do not merge `RetryingBoardConnection`) stays a new card. `--json` is step 5.
