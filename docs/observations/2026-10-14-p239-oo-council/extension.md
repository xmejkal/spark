# P239 council: testability and extension lens (deploy area)

Verdict: the leaf classes are good seams. The weak part is `deploy.main()`, 90 lines that parse, plan, look, gate, flash, connect, write facts, check, log, record and map exit codes. Every change below lands there.

## Five changes walked through

**(a) Reconnect after esptool's reset (P238).** Right place: `BoardConnection._mpremote`, one class, as its docstring promises. Two gaps: no injected sleep, so a retry test would really wait; and the port can renumber after the reset while `main()` holds only `report.port` (`PortFinder` is gone after the look). Touches: `BoardConnection` plus its constructor call in `main()`; `ReadyCheck`, `FactsFile` need no change. Missing seam: a `ReconnectStrategy` (given port, finder, sleep) passed into `BoardConnection`.

**(b) `--json` and an MCP tool (P213).** Needs a core that returns a result. Today `main()` prints as it goes, then returns an int, and verdict, log path, store record and notes exist only as printed strings. Touches: `main()` splits into `Deployer.run()` returning a `DeployResult`, and a printer. The `look.lines` pattern is the model: `Report` is already data. Missing seam: the result object.

**(c) Another shell or flasher.** Shell side: `BoardConnection` is mpremote-specific (hard-coded `exec`, `fs cp`, `fs cat`, "Traceback"), with no base class, so a second shell needs an interface extracted from it. `PortFinder` runs `mpremote devs` and has no base class. Flasher side: `BoardReader` is a proper strategy, but `flash_commands` is a function with esptool's ERASE, WRITE and `--chip` baked in, and `main()` runs the commands in a loop. Touches: `deploy.py`, `board_look.looker`, `board_connection`. Missing seams: a `Flasher` (`erase_and_write(image, port)`, `plan()`, `read(port)`, merging `EsptoolReader` into it) and a `BoardShell` interface (`connect(port)`, `list_ports()`).

**(d) Re-check a flashed board, no erase.** `ReadyCheck` and `FactsFile` already do exactly this. But the steps are welded into `main()` after the flash loop: expected hashes, connection, facts, check, log, record. A `recheck.py` would copy about 20 lines. Touches: `main()`. Missing seam: the post-flash stage as its own method (`Verifier.verify(project, port)`), with the flash step before it.

**(e) A second consent path.** `Consent` is the best seam in the area. `gate_open(report, token, consent, image)` takes any consent. Leaks: `record_deploy` hard-codes `"typed in a terminal by <user>"`, so a web yes would be recorded as a lie. `Closed(NO_TERMINAL)` is raised from inside `TerminalConsent`, and the exit code comes from `Closed`, so a pending web yes (answer arrives later) has no state. `rerun_line(args, port)` is built in `main()` from argparse args. Touches: `record_deploy` plus a `Consent.who` attribute, and `main()`'s construction.

## Tests today

- `GateCase.deploy` builds one fake `run` that sniffs argv (`"fs" in command`, `"devs"`, `"flash_id"`, `"exec"`) and answers all four tools. It patches the global `tools.find`. The fake knows mpremote's grammar, so a second shell means rewriting it.
- Three more fakes duplicate the idea: `Mpremote` (test_board_connection), `Unreachable` (test_ready_check), and `LookCase.look`'s own `run` (test_board_look). `test_look.py` and `ProjectCase.deploy` carry two more sniffing `run`s. `Connection` in test_ready_check lacks `read_file` and is not used by the facts tests.
- Time is not injectable: `datetime.now()` in `keep_board_log` and `board_facts.facts`. The store is not injectable: `record_deploy` calls module-level `store.locked/place/write_json`, and tests patch `store.write_json`.
- Reaching through imported names: `mock.patch.object(deploy, "passed_log")`, `board_look.boards.load`, `image_check.run_scenario.run_record`, `tools.find` (global), and `GateCase.copied` shared state. Tests parse `command[-3] == "cp"`, mpremote's argv layout.

## Shared fakes, one per seam

- `FakeBoardConnection(answers, copies, unreachable)`, in `tests/fakes.py`, implementing `run_code`, `copy_to_board`, `read_file`, `repl_command`. It replaces `Connection`, `fs`, `on_board`, `Unreachable` and most of `Mpremote`. Keep `Mpremote` for `BoardConnection`'s own tests only.
- `FakeFlasher(flash_id_text, fails)` records `erased/written` and answers `read`. It replaces the `"flash_id"` and `"erase_flash"` branches.
- `FakeConsent(answer)` is `Says`, moved, with a `who`.
- `FakeClock` (now, sleep) and a store root argument.

## Seams to add, smallest first

1. `Consent.who` (one line each) so `record_deploy` stops lying.
2. Move `Says` to a shared fakes module, and add `FakeBoardConnection`. No production change.
3. Inject `now` and the store into `keep_board_log`, `facts` and `record_deploy` (default arguments, same behaviour).
4. `DeployResult` plus `Deployer.run()` splitting `main()`: plan, look, gate, flash, verify. `main()` prints.
5. `Verifier` (post-flash stage) callable alone: (d).
6. `Flasher` strategy, and `ReconnectStrategy` inside `BoardConnection` with an injected sleep and a `PortFinder`: (a) and (c).
7. `BoardShell` interface extracted from `BoardConnection` and `PortFinder`: last, only when a second shell is real.
