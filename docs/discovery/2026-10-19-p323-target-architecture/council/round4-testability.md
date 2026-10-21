# Round 4: testable, exchangeable, reusable

Lens: test architect (ports and adapters, strategies, fakes over mocks). Model: Opus. Read-only on the code, 2026-10-21.

> **TL;DR.** Spark needs eight seams, not more. Today the platform seam leaks: 8 tool lookups bypass `FirmwarePlatform`, so an Arduino swap would edit 5 callers. Put every backend choice in one `Backends` value that `records` builds once, let each area's registry turn a name into a strategy, and keep frontends (CLI, Claude, MCP) as doors that only parse and print. Only 466 of 2,817 tests (17%) test from the outside, so before any move a golden net over every door must exist, with fake tools as processes.

## The seams

A seam is an outside thing behind a protocol. "Chosen by" is who builds the real one. "Configured in" is the one place a person changes it.

| Seam | Protocol | Real adapter | Fake | Chosen by | Configured in |
|---|---|---|---|---|---|
| Command runner | `run(argv, **kw) -> CompletedProcess` | `subprocess.run` | a recording `run` with canned output; `--dry-run`'s recorder | the door's default | none |
| Tool finder | `ToolFinder.find(role) -> Tool` | `tools.find` over three layers | `FakeToolFinder({role: argv})` | `Backends` | `data/tools.json` < `$SPARK_HOME/tools.json` < `<project>/.spark/tools.json`, project wins (`tools.py:79-85`) |
| Firmware platform | `make_flasher`, `make_connection`, `make_port_finder`, `make_board_reader`, `make_console_probe`, `pin_map_text`, `make_image` | `MicroPythonPlatform` (esptool, mpremote) | `FakePlatform` assembled from `FakeBoardConnection`, `FakeConsoleProbe` | `PLATFORMS[backends.platform]` in `bench/operations.py` | requirements.json `platform`, default `micropython` |
| Simulation engine | `prepare(design)`, `run(scenario) -> RunRecord` | `WokwiCliEngine` | `tests/fake_wokwi_cli.py`, a fake process (kept) | `ENGINES[tool name]` in `firmware/operations.py` | the `simulator` role in the tools layers (`data/tools.json:5`) |
| Store | `Layers(library, store, project)` | `Layers.from_environ()` | `Layers(tmp)` | `Backends` | `SPARK_HOME` < `XDG_DATA_HOME` < `~/.local/share/spark` (`store.py:47-52`) |
| Network | `fetch(url) -> bytes` | `store.fetch`, the only `urlopen` (`store.py:357`) | a dict from URL to bytes | `Backends` | none |
| Clock | `now() -> aware datetime`, `sleep(s)`, `monotonic()` | `time`, `datetime` | one `FakeClock` with all three | the door's default | the machine's zone |
| Consent | `ConsentStrategy.ask`, `require_ready` | `TerminalConsentStrategy`, `StandingConsentStrategy` | `FakeConsent` | the frontend (door) | a grant in the store |

The serial port is not a seam of its own. The console script runs pyserial through `run` (`board_console.py:51`, `:89`), and `FakeConsoleProbe` covers it. The file writer of S16 stays a collaborator of `run_door` for dry run, not a ninth seam.

## Findings

**F1. The platform seam leaks.** `FirmwarePlatform` (`firmware_platform.py:41`) makes the flasher and connection, but 8 lookups of `board-shell` or `flasher` sit outside it: `live.py:84`, `reach.py:79`, `grant.py:88,95`, `board_look.py:296-297`, `board_doctor.py:160,162`. `EsptoolReader` is built directly at `grant.py:95` and `board_look.py:297`. So "one subclass, one line in `PLATFORMS`" (design 2.5) is false today. Fix: the platform also makes the port finder and the board reader. Only the platform calls the tool finder for a board tool. The seam test: a `FakePlatform` drives `look`, `grant`, `live`, `reach` and `deploy` with no caller edit.

**F2. The tool finder is the most patched thing in the suite.** `mock.patch.object(tools, "find")` appears 37 times and `tools.shutil.which` 29 times, 66 of the 336 patch lines. `tools.find` is a module function that 11 scripts call (24 sites). Fix: `ToolFinder` is a collaborator in `records/tools`, with `FakeToolFinder` in `tests/fakes.py`. S8's count then falls by about 66 as areas move. This also makes a tool swap a config change: the finder reads the layers, the caller only names a role.

**F3. Backends are chosen in four places.** Tools in three JSON layers, the board in requirements.json or `boards/active.json`, the platform hard-coded at `deploy.py:171`, the store from the environment. Fix: one frozen `Backends` value (role: Value) that `records` builds once per run: `Backends.for_project(project, environ)` holds `layers`, `tools` (a `ToolFinder`), `platform` (a name) and `fetch`. It holds choices, not built services, so it is not a container (D3). Each area's `operations.py` turns a name into a strategy with its own registry. A test builds `Backends` from a temp folder and fakes. This answers the PO's "backend can be configured well": one reader, one Value, one registry per kind.

**F4. A tool's MCP version is a frontend swap, not a core adapter.** `tools.locate` returns None for `kind: mcp` (`tools.py:162-163`): Claude Code runs the server, and spark never calls it. Four rows are MCP (`jlcpcb`, `espressif-docs`, `wokwi-mcp`, `sigrok`). Fix: when a person picks the MCP row for a role, the agent calls the MCP tool and passes its result to the Operation as an input file. The core takes the same input either way. Cut the "one Adapter per MCP row" in design 2.5 until spark has an MCP client. Test: the Operation's golden is equal for both sources of the same input.

**F5. A frontend swap must touch no core code. Prove it with one parity test.** The doors are the CLI (`run_door`), Claude (command pages call the CLI with `--json`), and later MCP (`run_operation`). Consent is the one collaborator the frontend picks. Fix: for each golden, `main(argv + ["--json"])` prints exactly `envelope(run_operation(...))` with the same fakes. Any logic in a door then breaks parity. Today it would: `deploy.py:165-178` prints and decides exit codes inside `_deploy`.

**F6. Code duplicated across doors.** `PortFinder(tools.find("board-shell"), run)` is built in 4 places (F1). `GrantService` in `grant.py:90,99`, `live.py:89`, `deploy.py:192`. "Print to stderr and return 2" occurs 36 times in 17 files. `--json` and `--project` are declared in 14 files each. Fix: `run_door` owns the error path, shared `OPTIONS` own the flags, and `bench/operations.py` builds `GrantService` and the platform once. Reusable as is: `DeployService`, `ConsentStrategy`, `outcomes`, `ScenarioRun`.

**F7. Fakes are scattered and two clocks differ.** 5 Fakes live outside `tests/fakes.py`: `test_board_doctor.py:28,38`, `test_board_live.py:27,140`, `test_sim_project.py:170`, against `developing.md:285`. `FakeClock` (`fakes.py:59`) and `FakeLocalClock` (`fakes.py:88`) have two shapes, and `DeployService.sleep` is a class attribute a test replaces (`deploy_service.py:75`). Fix: move the four that stand in for a swappable part to `fakes.py`, merge the clocks into one `FakeClock`, and pass `sleep` in `__init__`. No `Clock` class (round 3 holds).

**F8. Seven scripts run outside programs with no `run` to inject.** `check_spine.py:162,170,391,432,509`, `sim_project.py:157`, `run_scenario.py:171`, `import_firmware.py:58`, `parts.py:1180`, `tabbed_page.py:48`, `check_vendor_pins.py:67`. Tests patch them instead (`check_spine.run` 6, `find_toolchain` 7). Fix: each Adapter takes `run`, as `board_look.py:70` does. S3 already confines the call, so this lands with each area's move.

**F9. A production module branches on the test runner.** `store.py:40` swaps `SPARK_HOME` when `unittest` is imported. It is a good net, but a test cannot choose its store without `os.environ`. Fix: tests pass `Layers`. Keep the net until no test needs it.

## Decoupling: what each area may know

An area knows other areas only by their interfaces: a Strategy base, a Value or a Service's public methods. It never knows a concrete Adapter. Only the area's `operations.py` names one, through its registry and `Backends` (F3). So `operations.py` is the one place that wires a backend, and a frontend calls only `OPERATIONS`.

| Area | May depend on (interfaces) | Its seams, as parameters | Run alone in a test with |
|---|---|---|---|
| records | core | run, fetch, Layers | `Layers(tmp)`, a fetch dict |
| parts | records' `PartRecords`, `Layers` | fetch | `Layers(tmp)` over `tests/data/` records |
| design | parts, records' `BoardRecords` | none | records from `tests/data/` |
| firmware | design's `Design` Value | `SimulationEngine`, run | `fake_wokwi_cli.py`, a recording run |
| breadboard | design's `Design` | Renderer (`DRAWING_RENDERERS`), part pictures | `FakePartPictures`, `FakeTscircuitExport` |
| checks | design's `Design` | `Check` | a `Design` Value |
| bench | firmware's `FirmwarePlatform` base, records | platform, consent, clock, run | `FakePlatform`, `FakeConsent`, `FakeClock` |
| build | breadboard, firmware, checks (their Services) | `BuildStage` | a fake stage per area below |

A new implementation is one subclass in the area that owns the base, one registry line beside the base, and one config value (`platform`, a tools row, `simulator` role). No caller changes, because callers receive the strategy as a parameter. Its test inherits the base's contract mixin (S14).

**F11. One rule a test can enforce.** Add to `ArchitectureRules`: *S19. Outside `<area>/operations.py`, no module imports a class that holds an Adapter (S3), nor another area's module other than its package interface (`spark.<area>`, the names in its `__init__`).* An area's `__init__` exports its bases, Values and Services only. Today the rule would flag `grant.py:95` and `board_look.py:297`, which build `EsptoolReader` themselves (F1). With S19, a test of one area imports that area and `tests/fakes.py`, and nothing else from spark.

## Do today's tests test from the outside?

Measured with an `ast` scan of every `test*` method in `tests/test_*.py`, with its `setUp` and its file's helpers (static, so a helper in another test file is missed):

| How the test reaches spark | Tests | Share | Through an area move |
|---|---|---|---|
| Outside: only a door's `main(argv)` or a spawned script | 466 | 17% | unchanged: the door keeps its path and `main` |
| A public function inside a door module (`parts`, `emit_board`, `check_spine`) | 921 | 33% | edited: the function moves into its area, so the import changes (D14, no shim) |
| A public name of a library module | 528 | 19% | edited: the module moves, so the import changes, the body stays |
| Inside: a private name or a `mock.patch` of a spark module | 470 | 17% | breaks or must be retargeted |
| No spark module named (tests of `tools/`, helpers from other files) | 432 | 15% | mostly unchanged |

Most outside tests sit in `test_needs` (197), `test_drawer` (77), `test_cost` (52) and `test_parts` (47). The inside tests that a move breaks sit in the bench and records areas: `test_deploy_gate` 76, `test_tools` 65, `test_board_grant` 64, `test_board_look` 38, `test_check_spine` 32, `test_deploy` 21, `test_look` 15, `test_live` 13. They patch `tools.find`, `check_spine.run` and private helpers that the move renames. So the bench move, the first in v0.13, edits the most tests, and those are the tests with the least outside cover. `test_json_contracts.py` checks envelope keys in 15 tests, not values. `tests/golden/` does not exist yet.

**F10. The net must exist before the first move, and slice 1a covers 3 of 24 doors.** Slice 1a records goldens for `check_spine`, `check_all` and `deploy --dry-run`. A green run then proves nothing for `look`, `grant`, `live`, `reach`, `parts` (30 Operations), `drawer`, `init_project`, `run_scenario`, `flash_image`, `import_firmware`, `assign_pins`, `emit_board` or `breadboard`. Fix, the net per door before its area moves:

- A golden per door, per Operation and per outcome (ok, problems, could-not-run) on fixture projects under `tests/data/`: the `--json` envelope and the exit code. stderr is not golden, because its text may improve.
- The door is reached only through `main(argv)` or as a process, never a private name. So the golden test never changes in a move.
- Fake tools are processes, as `tests/fake_wokwi_cli.py` already is. Add `fake_esptool.py` and `fake_mpremote.py`, chosen through the fixture's `.spark/tools.json` (`also` paths, `tools.py:179-182`) or a fake bin folder first on `PATH`. No patch, so the net survives F2's `ToolFinder` change too.
- One golden of the text output per door that a person reads (`look`, `deploy --dry-run`, `check_all`), since a person reads that and not the JSON.
- Order: the bench doors first, because the bench move breaks the most inside tests. Slice 1a keeps its three. Each later area gets its goldens in the PR before its move, never in the move itself.
- Done when: every door that a command page calls has a golden, and a planted change in one envelope value fails exactly one golden.

## The test pyramid

Measured today on this Mac (Python 3.10): 2,817 tests in 122.2 s. Three spots cost 44 s: `test_mutate` 27.3 s (43 tests, each runs a unittest process), `test_docs` 9.5 s in one test, and `test_needs.py:1416` 7.5 s because it runs a real `tsci build` inside a unit module.

| Level | What | Count | Budget | In the hook |
|---|---|---|---|---|
| Unit | Value, Service with Fakes, Strategy contract mixins | about 2,600 | 50 s, no process, at most 50 ms each | yes |
| Operation | golden per Operation and outcome, through `run_operation`, plus parity (F5) | about 150 | 10 s | yes |
| Door | one smoke test per door that spawns the script | 24 | 10 s | yes |
| Real tool | tsci, node, bun, a real wokwi-cli with a token | about 10 | 30 s | slow lane, skipped without the tool |
| Spark's own tools | `test_mutate`, `check_commit` | about 60 | 30 s | slow lane |
| Bench | a real board | 0 in the suite | walk checklist | never |

Slow tests stay off the hook's wall time, not out of the gate. Files named `slow_test_*.py` hold the last two lanes. The default `test*.py` pattern skips them. `check_commit.measure` (`tools/check_commit.py:135`) runs both patterns in two processes at once, so the push waits about as long as the fast lane. A person runs the fast lane alone in the dev loop. `measure.py` gains "suite s" and "slowest test s". A test over 2 s in the fast lane fails the hook unless it is in the baseline, which may only shrink.

## Rows

1. Platform seam leaks through 8 tool lookups (F1): add `make_port_finder` and `make_board_reader` to `FirmwarePlatform`, and a `FakePlatform` seam test over five doors.
2. `tools.find` is patched 66 times (F2): add a `ToolFinder` collaborator and `FakeToolFinder`, landing with slice 2.
3. Backends chosen in four places (F3): add a `Backends` Value built once by `records`; registries per area.
4. MCP tool versions have no core adapter (F4): drop "one Adapter per MCP row" from 2.5; an MCP result enters as an input.
5. No proof that a door holds no logic (F5): add a parity test per golden, `main --json` equals `envelope(run_operation)`.
6. Door code duplicated (F6): `run_door` owns the error path; shared `OPTIONS`; `bench/operations.py` builds `GrantService` once.
7. Fakes outside `fakes.py` and two clocks (F7): move four Fakes, merge the clocks, pass `sleep` in `__init__`.
8. Seven scripts call `subprocess` with no `run` (F8): inject `run` into each Adapter at its area's move.
9. `store.py:40` branches on unittest (F9): tests pass `Layers`; keep the net until unused.
10. Suite 122 s with 44 s in three spots (pyramid): a `slow_test_*` lane run in parallel by the hook, a 2 s per-test ratchet, two measure columns.
11. Only 17% of tests test from the outside, and slice 1a covers 3 of 24 doors (F10): a golden per door and outcome, with fake tool processes, before each area moves, the bench doors first.
12. Areas can reach concrete Adapters and each other's internals (F11): add S19, adapters only in `operations.py`, cross-area imports only through the package interface.
13. Cut seams that serve nothing yet: no serial-port seam, no MCP client, no `Clock` class, no Renderer registry beyond `DRAWING_RENDERERS`.
