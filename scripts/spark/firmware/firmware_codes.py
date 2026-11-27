"""
The reasons a firmware step stops, each a code with one sentence (P684, W6-F2): run_scenario.py, flash_image.py,
check_firmware.py and the image a deploy reads (project_image.py).

A leaf: it imports nothing of spark but `spark.core.codes`. Each refusal names its code, so an agent decides on the code and never on the English
sentence (no magic strings, P260). A refusal that raises gives its exception a `code`; one that returns a sentence returns
a Refusal (`spark.core.result`). `check_firmware.py --json` writes the code of each problem and unchecked item, with its fix (P1208). The six codes it answers with
are Codes (P853, P935), each holding its meaning and its fix, a str that equals its word, so a reader of the word is unchanged.
`run_scenario.py --json` writes the code of its refusal or its failure too (P1078). flash_image.py prints the sentence alone,
and its codes wait in the library for the Operation that comes later.

Five codes are also board_codes' (NO_SIM_TOML, FIRMWARE_LINE_BAD, NO_IMAGE, LOG_UNREADABLE, TOOL_MISSING), as equal
literals in two leaves: project_image raises the first four from here, and the bench raises TOOL_MISSING itself (P685). The codes every Operation can write are the core's.
"""

from spark.core.codes import Code

# --- MVP ---
#: The image a deploy reads, and the firmware line a run reads (equal to board_codes').
NO_SIM_TOML, FIRMWARE_LINE_BAD, NO_IMAGE = "no_sim_toml", "firmware_line_bad", "no_image"
LOG_UNREADABLE, TOOL_MISSING = "log_unreadable", "tool_missing"
#: run-scenario (run_scenario.py): what stops a run before the paid call.
NO_SIM_PROJECT, NO_MAIN_PY, RUN_INPUT_UNUSABLE, NO_TOKEN = "no_sim_project", "no_main_py", "run_input_unusable", "no_token"
UNKNOWN_COMPONENT_ID = "unknown_component_id"
#: run-scenario (run_scenario.py): wokwi-cli and the board, during the run.
SIMULATOR_CANNOT_START, SIMULATOR_HUNG, SIMULATOR_LOST = "simulator_cannot_start", "simulator_hung", "simulator_lost"
BOARD_SILENT, BOARD_NOT_STARTED, NEVER_READY = "board_silent", "board_not_started", "never_ready"
STEP_TIMEOUT, STEP_FAILED = "step_timeout", "step_failed"
#: flash_image.py.
NO_INTERPRETER, INTERPRETER_UNUSABLE = "no_interpreter", "interpreter_unusable"
FILES_NOT_FOLDER, CONFIG_NOT_JSON, FILES_NOT_WRITTEN = "files_not_folder", "config_not_json", "files_not_written"
#: check_firmware.py, the import check (each a Code with its fix, P1208).
NO_FIRMWARE_FOLDER = Code("no_firmware_folder", "the project has no firmware/ folder to import",
                          "write the firmware in a firmware/ folder of the project, or name the project with --project")
NOTHING_TO_IMPORT = Code("nothing_to_import", "firmware/ holds nothing to import but the boot files and the pin map",
                         "move the code out of main.py into a module that main.py calls")
IMPORT_FAILED = Code("import_failed", "a firmware module raised when it was imported",
                     "fix the error on the module's last line, then run check_firmware.py again")
IMPORT_TIMEOUT = Code("import_timeout", "a firmware module did not finish its import within the timeout",
                      "move what loops or waits at module level into a function that main.py calls")
#: check_firmware.py: the project's own tests (P1208).
OWN_TEST_FAILED = Code("own_test_failed", "a test in the project's tests/ failed or raised",
                       "fix the test, or the code it tests, then run check_firmware.py again")
OWN_TESTS_NOT_RUN = Code("own_tests_not_run", "the project's tests did not finish within the timeout, gave no count, or ran no test (an empty tests/, or every test skipped)",
                         "run `python3 -m unittest discover -s tests` in the project to see why, then run check_firmware.py again")

#: Each code and the one sentence that says what it means.
CODES = {
    NO_SIM_TOML: "the project has no sim/wokwi.toml",
    FIRMWARE_LINE_BAD: "the firmware line of sim/wokwi.toml cannot be read, or names an image outside sim/",
    NO_IMAGE: "the image that sim/wokwi.toml names is not there yet",
    LOG_UNREADABLE: "a run log in sim/runs/ cannot be read",
    TOOL_MISSING: "a tool the step needs is missing or cannot be used",
    NO_SIM_PROJECT: "sim/ holds no diagram.json or no wokwi.toml, so there is nothing to simulate",
    NO_MAIN_PY: "firmware/ has no main.py, so the board would boot to a bare prompt and never print ready",
    RUN_INPUT_UNUSABLE: "the scenario or the firmware's files cannot be read, sim/wokwi.toml names no image and a run cannot "
                        "name one there, or the image's place is no folder",
    NO_TOKEN: "the simulator's account token is not set, and a run spends Wokwi CI minutes",
    UNKNOWN_COMPONENT_ID: "a step of the scenario names a component id that sim/diagram.json does not hold",
    SIMULATOR_CANNOT_START: "wokwi-cli could not be started",
    SIMULATOR_HUNG: "wokwi-cli did not finish within the simulated time and the startup allowance, so it was stopped",
    SIMULATOR_LOST: "wokwi-cli lost its connection to the simulator",
    BOARD_SILENT: "the board printed nothing before the timeout: its TX and RX may not reach the serial monitor",
    BOARD_NOT_STARTED: "wokwi-cli stopped before the board printed anything",
    NEVER_READY: "the firmware never printed ready, so no step was tested",
    STEP_TIMEOUT: "a step waited for something that never came before the timeout",
    STEP_FAILED: "a step of the scenario failed",
    NO_INTERPRETER: "the MicroPython build file is not there",
    INTERPRETER_UNUSABLE: "the MicroPython build is damaged, too large, or not the build for the board's chip",
    FILES_NOT_FOLDER: "--files names no folder",
    CONFIG_NOT_JSON: "--config is not JSON",
    FILES_NOT_WRITTEN: "the files were not written into the image's 2 MB file system: littlefs names the error (no space, a "
                       "name too long)",
    NO_FIRMWARE_FOLDER: NO_FIRMWARE_FOLDER.meaning,
    NOTHING_TO_IMPORT: NOTHING_TO_IMPORT.meaning,
    IMPORT_FAILED: IMPORT_FAILED.meaning,
    IMPORT_TIMEOUT: IMPORT_TIMEOUT.meaning,
    OWN_TEST_FAILED: OWN_TEST_FAILED.meaning,
    OWN_TESTS_NOT_RUN: OWN_TESTS_NOT_RUN.meaning,
}

# --- end MVP ---
