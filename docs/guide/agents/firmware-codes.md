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
| `check_firmware.py`, the pin names | `pin_map_name_missing`, `pin_map_not_read` ([the pin map](#the-pin-map)): in `--json` |
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

A failed own test blocks no deploy: `check_firmware.py` keeps its answer in `.spark/check-firmware.json`, which no gate reads ([P1209](https://github.com/xmejkal/spark/issues/1758)), and a deploy reads the logs of `sim/runs/` only.
The tests' code runs on this machine, in the project folder.

## The pin map

`check_firmware.py` compares the pin names that the firmware uses with the names that `firmware/pins.py` holds ([P882](https://github.com/xmejkal/spark/issues/1250)). It reads the files with `ast` and runs nothing, so `pins.py` is read as text too. It reads every `.py` under `firmware/` except `pins.py`, `firmware/lib/` (the drivers' folder) and the secrets files.

A **use** is one pin name at one file and line: `pins.X` after `import pins` or `import pins as p`, and each name of `from pins import X [as Y]`, at the import's line. `data.pin_map.used` counts uses, not names. `missing` holds the uses whose name the map lacks, each `{name, file, line}`, and each is a `pin_map_name_missing` problem with the subject `<file>:<line>`. With no `firmware/pins.py` while a file uses `pins`, it is one problem with the subject `firmware/pins.py` and the fix "build the board with --keep, which writes firmware/pins.py"; `missing` still lists each use, and `data.pin_map.has_map` is `false`. `not_compared` holds the **places** the check cannot compare, each `{file, line, form}`, and each is also an item of `assumptions`:

| form in a firmware file | what the check does |
| --- | --- |
| `import pins`, `import pins as p` | each `pins.X` or `p.X` read is a use. `pins.__name__` and any `__x__` are no pin name |
| `from pins import X`, `from pins import X as Y` | `X` is a use at the import's line, whatever the file does with the name later |
| `from pins import *` | a place: it takes every name, so the names the file uses are not compared |
| the module used as a value: `p = pins`, `f(pins)`, `getattr(pins, "X")`, `pins.X = 1`, `del pins.X` | a place: the names it reaches are not compared |
| the module name bound another way in the file (a parameter, a def, an assignment) | a place at the import's line: its pin names are not compared |
| `import pins.x`, `from .pins import X`, `__import__("pins")`, `importlib`, `exec` | not read at all (no use, no place) |

A file that does not parse, a pin map that does not parse, or a map that takes names it does not show (`from x import *`, a `__getattr__`), is `could-not-run` with `pin_map_not_read`, and the sentence names the file and the line. No name was compared then, so the run is never `ok`. A place is never a pass either: the result line counts it (`not compared in 2 places, first firmware/main.py:1`), and the status stays as the other checks left it.

The record keeps the map's names (`data.pin_map.names`). When `firmware/pins.py` gains or loses a name after the record, `flow.py show` marks the firmware `stale` and names the free checks as the next step ([P1270](https://github.com/xmejkal/spark/issues/1829)). A pin that moved keeps its name, so it does not.

What the check does not read: a name built at run time, a dynamic import, a driver in `firmware/lib/`, and the places above. A name that `pins.py` binds with `:=` or through `globals()` is not seen as bound, so a use of it is reported missing. A read in `try: ... except AttributeError` still counts as a use, but a name that the same file asks about with `hasattr(pins, "X")` or `getattr(pins, "X", default)` is a place in that file, not a missing use. It compares names only. It never sees whether the pin is wired, right or used right. `flow.py show` reads the check record only while it is current: after `firmware/` changes, the firmware phase has no status again until `check_firmware.py` runs again, unless the older record kept other `pin_map.names` than `pins.py` binds now (`stale`, above). A current record that names a missing pin name makes the firmware phase `problems`, with the pin line first.

## run_scenario.py's envelope

- The envelope (op `run-scenario`, [P1078](https://github.com/xmejkal/spark/issues/1582)). `data` holds `project`, `scenario`, `log` (the run's log in `sim/runs/`, or `null` when no run reached wokwi-cli) and `ran` (`false` for a refused run and for `--dry-run`). A run that failed is `problems`, one item with the scenario as `subject` and its code (`never_ready`, `step_failed`, `step_timeout`). A run the free checks refused is `could-not-run` with its code (`no_token`, `no_sim_project`, `tool_missing`, ...), and nothing was spent. A run that started and could not finish (`simulator_lost`, `simulator_hung`, `board_silent`) is `could-not-run` too, with `ran` true. Decide on the code (the tables above).
- Run `--dry-run --json` first: it needs no token, starts no run and writes nothing. An `ok` dry run's `next` is the paid run, op `run-scenario` with `needs_person` true, its argv holding the run's own `--micropython` and `--timeout-ms`. The paid run spends Wokwi CI minutes: ask the person first.
- A pass is `ok`. A pass whose scenario has no set-control or no expect-pin step, or whose steps were not counted, has its "passed, but ..." sentence as one item of `notes`: relay it whole ([never assume](never-assume.md)). A step or a diagram the run could not compare is an item of `assumptions`, `not checked: ...`, and the pass stays `ok`.
- After a paid run, `next` lists the steps `flow.py show` names now, and page.html is written again (P1035).
