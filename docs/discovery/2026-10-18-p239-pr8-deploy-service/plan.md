# P239 PR 8: DeployService

> TL;DR: the flow in `deploy.py`'s `main` (plan, look, gate, flash, facts, ready, recovery, log, record) moves into
> `scripts/deploy_service.py` as `DeployService`, which has no `print` and no `sys.exit`. A new `FirmwarePlatform`
> (`scripts/firmware_platform.py`) holds the parts that depend on MicroPython. `main` parses, prints and maps the exit
> code. Every printed line, exit code and store record stays the same.

Summary: after this PR a second caller (`--json` in P213, `/spark:deploy`, an MCP tool) can run a deploy without a
terminal and print its own way. `FirmwarePlatform` is the one place where an Arduino or PlatformIO build would plug in
later; it earns its place now because the brief asked for it as one constructor argument and it costs one small class.
Card [#238](https://github.com/xmejkal/spark/issues/238), brief item 4 of [P218's finish](../2026-10-17-p218-finish/brief.md).

## Council

Round 1 (tech lead, Sonnet; refuter, Opus; 2026-10-18). The refuter reproduced point 1. Changes:

- Exception scope stays as on main: a fault after the flash is a traceback today (`find_passed_log`, `tools.find`).
  `deploy()` ends when the flash ends; main calls `verify()` outside its `try`. One `try` covers `look`,
  `choose_consent` and `deploy`, same handlers, same order. Brief change: `verify`, not `deploy`, returns the result.
- `run = run or subprocess.run` stays in main; the console probe is built inside `verify`, only when ready is unknown.
- `FirmwarePlatform` calls `tools.find` through the module (tests patch it). `look()` uses `board_look.looker`.
- Tests that patch or call moved names are re-pointed (listed under Tests). Mutation tables with 49 entries on
  deploy.py are re-anchored.
- Declined, decided by the tech lead and refuter for the PO (delegated): no split of the PR, no committed golden harness.

Round 2 (tech lead and PO assistant, Sonnet). Changes:

- No cache of `tools.find`: each `make_*` calls it as main did, so the number of calls is unchanged. `deploy()` returns
  the `DeployPlan` it ran, and `verify` takes it, so the connection uses the plan's command as before.
- Factory methods are verbs: `make_flasher`, `make_shell_command`, `make_connection`, `make_ready_check`,
  `make_console_probe`. The result field is `log_path` (the class `BoardLog` is a Value). `verify` takes `who`, a
  sentence, not the whole consent. The callback is `show_line`, not `say`.
- The dry-run builds its mpremote line with `platform.make_connection(...)`, so main names no MicroPython class.
- `plan()` order stays: `make_flasher` (chip, then tool), then `make_shell_command`, so errors keep their precedence.
- Layers: this summary added; "Waits on you" added; words glossed. The store record is written before main prints the
  board log line; only an error other than OSError or StoreProblem shows the difference, and it is named in the PR.
- Observation rows start at AT450; P287's PR takes AT420 onward, so they do not clash.

Review (reviewer Sonnet, refuter Opus; after the build). Changes to the design above:

- The chip is read before the tool is looked for (`_esptool_flasher`), as the old `plan` did.
- The store record leaves `verify`: `DeployService.record(result, consent)` writes it, main calls it after printing the
  board log line and reads `consent.who` inside the same `try`, so the order of lines and the "not written" case match
  main. `verify(report, planned, show_line)` no longer takes `who`; `DeployResult` carries `facts` and has no store fields.
  This replaces the round 2 note on the record's order.

## What moves

| Now in `deploy.py` | Becomes |
|---|---|
| `plan()`, `newer_files`, `DeployPlan`, `OLDER_RUNS_WAY_OUT` | `DeployService.plan(port)`, same plan and notes |
| the look call in `main` | `DeployService.look(port)`, returns the `LookReport` (what the look found) |
| gate, token re-check, `require_ready`, flash loop | `DeployService.deploy(report, token, consent, show_line)` |
| `put_facts`, `read_board`, recovery block, `write_board_log`, `BoardLog`, `record_deploy` | `DeployService.verify(report, who, plan, show_line)` |
| `board_of`, `chip_of`, `tools.find`, `EsptoolFlasher(...)`, `BoardConnection(...)`, `ReadyCheck(...)`, `ConsoleProbe` | `FirmwarePlatform`, built by `FirmwarePlatform.micropython(project)` |

Stays in `deploy.py`: arguments, `EPILOG`, `WATCH`, `rerun_line`, `grant_hint`, `choose_consent` (they read `args` and
print), the dry-run and the exit-code map. `--help`, exit codes, lines and the store record do not change.

## Output without print

`show_line` takes one line (main passes `print(line, flush=True)`). The service calls it for lines that appear while a
step runs: `yes: ...`, `running: ...` before each command, the R-press request. The rest is returned in `DeployResult`.
A refusal is an exception main prints to stderr: `LookStop`, `DeployError`, `tools.ToolProblem` (exit 2),
`GateClosedError` (its own code). A failed flash raises `DeployError` with the sentence main printed before.
The brief names `deploy(token, consent, on_press_reset)`; the report is an argument because the yes is chosen after the
look; one `show_line` replaces `on_press_reset` because the order of lines is the contract.

## Classes

```
FirmwarePlatform  (plain noun; not a Value, its parts act)       scripts/firmware_platform.py
  micropython(project)  classmethod                              Arduino later is another builder
  make_flasher() -> Flasher            chip_of(project) + tools.find("flasher") -> EsptoolFlasher
  make_shell_command() -> argv         tools.find("board-shell") -> tools.command_for
  make_connection(command, port, run) -> BoardConnection         (command: the plan's shell command)
  make_ready_check(connection) -> ReadyCheck
  make_console_probe(port, run) -> probe or None
  board_of(), chip_of()                requirements.json's board and its chip, moved unchanged

DeployService  (Service)                                         scripts/deploy_service.py
  __init__(project, platform, ignore_older_runs=False, run=subprocess.run, clock=None, probe=None)
  plan(port=None) -> DeployPlan        image checks, then the tools; DeployError / ToolProblem
  look(port=None) -> LookReport
  deploy(report, token, consent, show_line) -> DeployPlan         gate, plan again, token, flash; returns the plan it ran
  verify(report, who, plan, show_line) -> DeployResult            facts, ready, recovery, board log, store record
DeployResult (Result)  facts_line, ready, log_path, store_record, store_problem, repl_command
```

```
main            service                  platform / board
 |-plan(port)->|-image checks---------->| make_flasher, make_shell_command
 |  (--dry-run: main prints, returns 0)
 |-look(port)->|-looker.run------------>| board
 | print lines; choose consent (grant or terminal)
 |-deploy(report, token, consent, show_line)->|-gate, show_line("yes:"), plan again, token, require_ready
 |             |-run(command) x2, show_line("running:") before each
 |<-DeployPlan (a flash error is a DeployError; main's one try ends here)
 |-verify(report, who, plan, show_line)->|-facts, ready, probe, show_line(R press), log, record
 |<-DeployResult; main prints facts line, verdict, log, record; exit 0, 1 or 2
```

## Names, checked against developing.md's table

- `DeployService` ends in `Service`; `DeployResult` ends in `Result`. Both are already in the table.
- `FirmwarePlatform` is a plain noun; its docstring says what varies. A row "Platform" is added to the table.
- Functions start with a verb (`plan`, `look`, `deploy`, `verify`, `make_*`). One word for one thing: "report" is a
  `LookReport`, "result" a `*Result`, "plan" a `DeployPlan`, "log" a `BoardLog` and `log_path` its file.

## Tests, first

1. Golden capture (scratch): every `deploy.main` call across `test_deploy`, `test_deploy_gate` and `test_journey_basic`
   (argv, exit code, stdout, stderr; temp paths and times replaced), plus `--help` and a dry run. Taken before, compared
   after; the PR body holds the result, and the reviewer re-runs the script.
2. `tests/test_deploy_service.py`, with Fakes (stand-ins from `tests/fakes.py`): lines in a `show_line` list, the failed
   flash, a fault after the flash stays a traceback; an ast test (reads the code's syntax tree) that the two new
   modules hold no `print` call and no `sys.exit` and that `firmware_platform` imports no `deploy_service`.
3. Re-pointed: `deploy.plan` becomes `DeployService.plan` (test_deploy_gate:226, test_deploy:187,193),
   `deploy.file_hashes` becomes `deploy_service.file_hashes` (:435), `deploy.BoardLog`, `DeployPlan`, `DeployError`.

## Docs and bookkeeping

developing.md (the paragraph on what each PR gave, "Until PR 8 merges", the Platform row), agents.md near line 424 only
if it names moved helpers. README and `tools/journey.py`: no change, an internal refactor. Mutation table
`tests/mutations/p239-pr8.json` (a mutation table is a list of planted defects the suite must catch); tables anchored on moved
lines are re-anchored (their `find` text is the exact line the plant edits). Observation rows from AT450.

## Not done, and what waits on you

The one recovery path (`RetryingBoardConnection`) stays a new card; `--json` is step 5. The real flash cannot run
here. **Waits on you:** the bench check of one real flash (P213b's walk or [P290](https://github.com/xmejkal/spark/issues/290)'s)
and the PR's review and merge.
