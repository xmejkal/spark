# The firmware codes, for AI agents

Each refusal of `run_scenario.py`, `flash_image.py` and `check_firmware.py` has a code
([P684](https://github.com/xmejkal/spark/issues/921)). The codes and one sentence each are in `scripts/spark/firmware/firmware_codes.py`.
Decide on a code, never on the English sentence.

Where a code shows today: `check_firmware.py --json` writes `code` on each item of `modules` that was not imported, and on each
item of `problems` and `unchecked` ([its JSON](json.md#check_firmwarepy)). `run_scenario.py --json` writes `code` on the item of `problems`
or `unchecked` of a run that failed or was refused ([its envelope](#run_scenariopys-envelope), P1078). `flash_image.py` takes no `--json`, so it prints
the sentence alone, with the same exit code as before. Its codes wait in the library for a `--json` or an Operation.

| script | codes |
| --- | --- |
| `run_scenario.py`, before the paid call | `no_sim_project`, `no_main_py`, `unknown_component_id`, `run_input_unusable`, `firmware_line_bad`, `tool_missing` (littlefs, the simulator or the MicroPython build; it ends with each place spark cannot read, P1071), `interpreter_unusable`, `files_not_written`, `no_token` |
| `run_scenario.py`, during the run | `simulator_cannot_start`, `simulator_hung` (wokwi-cli outlived its wall clock), `simulator_lost`, `board_silent`, `board_not_started` (all `unchecked`), and `never_ready`, `step_timeout`, `step_failed` (`problems`) |
| `flash_image.py` | `tool_missing`, `no_interpreter`, `files_not_folder`, `config_not_json`, `interpreter_unusable` (damaged, too large, or not the build for the board's chip), `files_not_written` |
| `check_firmware.py` | `import_failed`, `import_timeout`, `nothing_to_import`, `no_firmware_folder`, `own_test_failed` (a test failed or raised; its `subject` is its id), `own_tests_not_run` (no count in time, or no test ran: an empty `tests/` or every test skipped): all in `--json` |
| the image a deploy reads | `no_sim_toml`, `firmware_line_bad`, `no_image`, `log_unreadable`: a `DeployError`'s `reason` |

Before the paid call, `run_input_unusable` is a scenario or a firmware file that cannot be read, a `sim/wokwi.toml` with no
place to name the image, or an image whose place in `sim/` is no folder; `firmware_line_bad` is a firmware line that cannot be read, or one that names an image outside `sim/`,
the same code as the deploy's for the same line ([P689](https://github.com/xmejkal/spark/issues/930)). `files_not_written`, in
both scripts, is a file that littlefs did not take into the image's 2 MB file system (no space, or a name too long); its
sentence carries littlefs' own error. It was a traceback with exit 1.

`no_sim_toml`, `firmware_line_bad`, `no_image`, `log_unreadable` and `tool_missing` are also codes of the look and of
deploy ([their table](json.md#lookpy-and-deploypys-envelope)), with the same words.

## The own tests

`check_firmware.py` runs the project's `tests/` with `unittest` ([P1208](https://github.com/xmejkal/spark/issues/1757)). `data.tests` says
how it went, in one of three states:

- `recorded`: `passed` of `total` (the "35 of 35"), `failed` (the ids of the tests that failed, raised, or succeeded when they were
  expected to fail) and `skipped`. `passed` is `total` less the failed and the skipped, and a test is counted once: a test with three failing subtests is one failure, and one with three skipped subtests is one skipped test. Some passed and some skipped stays `ok`, with the skipped count.
  Each failed test is an item of `problems` with the code `own_test_failed`, its id as `subject`, and the last line of its traceback.
- `none-recorded`: there is no `tests/` folder. It has no number, `notes` says so, and it is no fault and no pass.
- `not-checked`: the tests did not finish in the time limit, gave no count, or ran no test (a `tests/` that holds none, or one whose every test was skipped: nothing passed and nothing failed, and a skipped is not a pass). It has no
  number, and `unchecked` holds an item with the code `own_tests_not_run`, so the status is `could-not-run`, never `ok`.

A failed own test blocks no deploy: `check_firmware.py` writes nothing, and a deploy reads the logs of `sim/runs/` only.
The tests' code runs on this machine, in the project folder.

## run_scenario.py's envelope

- The envelope (op `run-scenario`, [P1078](https://github.com/xmejkal/spark/issues/1582)). `data` holds `project`, `scenario`, `log` (the run's log in `sim/runs/`, or `null` when no run reached wokwi-cli) and `ran` (`false` for a refused run and for `--dry-run`). A run that failed is `problems`, one item with the scenario as `subject` and its code (`never_ready`, `step_failed`, `step_timeout`). A run the free checks refused is `could-not-run` with its code (`no_token`, `no_sim_project`, `tool_missing`, ...), and nothing was spent. A run that started and could not finish (`simulator_lost`, `simulator_hung`, `board_silent`) is `could-not-run` too, with `ran` true. Decide on the code (the tables above).
- Run `--dry-run --json` first: it needs no token, starts no run and writes nothing. An `ok` dry run's `next` is the paid run, op `run-scenario` with `needs_person` true, its argv holding the run's own `--micropython` and `--timeout-ms`. The paid run spends Wokwi CI minutes: ask the person first.
- A pass is `ok`. A pass whose scenario has no set-control or no expect-pin step, or whose steps were not counted, has its "passed, but ..." sentence as one item of `notes`: relay it whole ([never assume](never-assume.md)). A step or a diagram the run could not compare is an item of `assumptions`, `not checked: ...`, and the pass stays `ok`.
- After a paid run, `next` lists the steps `flow.py show` names now, and page.html is written again (P1035).
