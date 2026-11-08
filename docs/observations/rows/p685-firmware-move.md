# P685 firmware move (W6-F3): rows

The claims of the W6-F3 plan, `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md` (section
"W6-F3, the firmware move" and its "P685 claims check"), checked against main 46bca725 before any code, then the
refuter's check of that block. Card: [P685 #922](https://github.com/xmejkal/spark/issues/922).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the split table: `PASSED`, `PASSED_WITH_CAVEAT`, `ONE_RUN_MESSAGE`, `NO_MAIN` and `run_record` go to `scenario_run.py` | plan | acted | `ScenarioSteps.passed_sentence` reads them and `from_log`, `run_record`, `file_hashes` share `_header`: a cycle. They went to `scenario_steps.py` |
| 2 | `scenario_steps.py` imports nothing of firmware | plan | acted | `from_log` read `sim_project.WHY_LOG_UNREADABLE`. The sentence moved to `scenario_steps.py`, which imports only `spark.core` |
| 3 | `project_image` reaches only `ScenarioSteps` (the class diagram) | plan | acted | it read `run_scenario.DEFAULT_IMAGE`. `DEFAULT_IMAGE` moved to `sim_project`, and `UNNAMED_FIRMWARE` is built from it (refuter) |
| 4 | the bench readers include `ready_check` | plan | rejected | no such module. The readers are `board_connection`, `board_console`, `download_mode`, `ready_probe` and `image_evidence` |
| 5 | the CLI passes its own `Path(__file__)` to the build command | plan | acted | `build_command` is called by `project_image` and `image_evidence`. `image_builder.FLASH_IMAGE_SCRIPT` names the CLI with `parents[2]`, as `deploy_image.py:40` does. `test_flash_image`, `test_project_image` and `test_image_evidence` assert the CLI path |
| 6 | `import_child.main` becomes `import_one` | plan | acted | `import_one` is `import_probe`'s. It became `import_named` |
| 7 | the three `sys.path.insert` lines go | plan | rejected | `test_scripts_isolated` runs each CLI with `-I`, so the CLIs keep theirs. The moved libraries have none. The one `EXEMPT` entry went |
| 8 | the `__file__` paths that break are the ones listed | plan | acted | also `pyproject.toml:15`, `test_journey_basic.py:55`, `import_firmware.py:13` (help), `measure.py:8`, `mutate.py:48,128`, `test_check_commit.py:98` |
| 9 | the five test files import from `spark.firmware` | plan | acted | 15 files import a firmware module. Seven `mock.patch.object` sites follow their name (refuter: `STARTUP_ALLOWANCE_S` to `scenario_run`) |
| 10 | 1,656 lines, 47 or 52 import lines, 228 rows, 15 baseline keys | plan | closed | 2,087 lines in the files, 59 import lines, 267 rows, 11 baseline keys |
| 11 | `--retarget` moves the rows, the split ones by hand | plan | acted | `--retarget` for the 7 whole files (100 rows), a scratch script by where each `find` lives for the CLIs. 7 rows changed text (refuter). `--anchors` refuses the same 118 rows as main |
| 12 | the eight T1 keys move | plan | acted | 7 moved. `T1:scripts/flash_image.py:file-write` is `main`'s and stays with the two R1 `main` keys. The R6 key went (`Service:`) |
| 13 | `firmware_codes` joins `measure.LEAVES`, `board_codes` keeps aliases until W6-F3 | plan | closed | P684 did U1 with equal literals. Five codes are shared and stay. `board_codes.py:15` and `test_json_contracts.py:255` now say why |
| 14 | 14 agent-facing pages | plan | closed | 4 guide pages named a moved path, plus `how-it-works.md`'s link. `patterns-and-names.md` names the third area |
| 15 | the second module is `run_log.py` (claims check) | refuter | rejected | `run_log` already means the file in `sim/runs/`, and `areas/firmware.md` plans `RunLog` in `scenario_run.py`. It stays `scenario_steps.py` |
| 16 | `p97-council.json` "re-check 1" is refused on `sim_project.py` | build | closed | stale on main before this PR, not this card's. It stays as it is, retargeted |
| 17 | the goldens call the CLIs by path, so they stay valid | plan | closed | `golden_firmware.py:117`. They pass after each commit |
| 18 | `scenario_steps.py` defines `NO_MAIN` twice | review | acted | the copy after `run_record` is gone |
| 19 | comments name the old modules (`image_evidence.py:120`, `:407`, `scenario_run.py:122`, `test_mutate.py:523`) | review | acted | they name `import_probe`, `image_builder` and the new stand-in folder |
| 20 | `areas/firmware.md` points at `run_scenario`, `import_firmware.py:58`, `flash_image.py:33` and `:89` | review | acted | it names `scenario_steps`, `import_probe.import_one`, `image_builder.filesystem` and `image_builder.board_build` |
| 21 | the `firmware_codes` docstring says "until W6-F3" | review | acted | it says what is true now, as `board_codes.py:15` does |
| 22 | `how-it-works.md:157` names `sim_project.py` without its folder | review | acted | `spark/firmware/sim_project.py` |
| 23 | the closing check passes with a firmware library in `scripts/` under a new name | review | acted | `TheFirmwareAreaTest` also pins each CLI's own functions. A planted `verdict` in `run_scenario.py` failed it |
| 24 | `test_self_confirmation.py:7` names `flash_image.FILESYSTEM_OFFSET` | review | acted | `image_builder.FILESYSTEM_OFFSET` |
| 25 | the split's import lines and triple blank lines | review | acted | grouped in `scenario_run.py` and `project_image.py`. `--anchors` refuses the same 118 rows as main |
| 26 | `import_probe.import_one` and `import_child.import_named` are two names for one job | review | rejected | they are the parent and the child: one starts a process, the other imports in it. Both names stay |
| 27 | `scenario_steps` is too narrow a name for what it holds | review | rejected | row 15 decided it |
| 28 | the bench imports `sim_project` and `image_builder` too, not only `scenario_steps` | review | verified | those edges are older than the move, and the arrow from the bench to firmware is allowed |
| 29 | `check_commit.py:94` now drops a `stand_in` folder at any depth | review | verified | intended, as `measure.py` and `test_orphans` do |
| 30 | `run_scenario.main` builds the image twice | review | raised | older than the move. Filed as [P696 #939](https://github.com/xmejkal/spark/issues/939) |
| 31 | `sim_project` reaches `board_codes` through `parts` and `missing_facts` | review | raised | a design-area edge, noted for that wave |
