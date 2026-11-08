# The firmware codes, for AI agents

Each refusal of `run_scenario.py`, `flash_image.py` and `import_firmware.py` has a code
([P684](https://github.com/xmejkal/spark/issues/921)). The codes and one sentence each are in `scripts/firmware_codes.py`.
Decide on a code, never on the English sentence.

Where a code shows today: `import_firmware.py --json` writes `code` on each item of `modules` that was not imported
([its JSON](json.md#import_firmwarepy)). `run_scenario.py` and `flash_image.py` take no `--json`, so they print the
sentence alone, with the same exit code as before. Their codes wait in the library for a `--json` or an Operation.

| script | codes |
| --- | --- |
| `run_scenario.py`, before the paid call | `no_sim_project`, `no_main_py`, `run_input_unusable` (the scenario, littlefs, the firmware line, the files or the MicroPython build cannot be used), `firmware_line_bad` (an image outside `sim/`), `tool_missing`, `no_token` |
| `run_scenario.py`, during the run | `simulator_cannot_start`, `simulator_hung` (wokwi-cli outlived its wall clock), `simulator_lost`, `board_silent`, `board_not_started`, `never_ready`, `step_timeout`, `simulator_failed` |
| `flash_image.py` | `tool_missing`, `no_interpreter`, `files_not_folder`, `config_not_json`, `interpreter_unusable` (damaged, too large, or not the build for the board's chip) |
| `import_firmware.py` | `import_failed`, `import_timeout` (in `--json`), `nothing_to_import`, `no_firmware_folder` (in the library only) |
| the image a deploy reads | `no_sim_toml`, `firmware_line_bad`, `no_image`, `log_unreadable`: a `DeployError`'s `reason` |

`no_sim_toml`, `firmware_line_bad`, `no_image`, `log_unreadable` and `tool_missing` are also codes of the look and of
deploy ([their table](json.md#lookpy-and-deploypys-envelope)), with the same words.
