# P1208: check-firmware, the free checks in one Operation that needs no sim/: rows

Card: [P1208 #1757](https://github.com/xmejkal/spark/issues/1757). The card's done-when: "`check-firmware --json` on the clock
gives the import count and '35 of 35' for its tests". The PO approved the plan on 2026-11-26. This file holds the acted,
raised and rejected findings only: the plan council's rows C1 to C14 (C15 confirmed the plan and needs no row) and what the
build found. 2026-11-26.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the clock gives "35 of 35" | the card | acted | on a copy of `p934-display2`, `check_firmware.py --project <copy> --json` gave `imports {"imported": 6, "total": 6}` and `tests {"state": "recorded", "passed": 35, "total": 35, "failed": [], "skipped": 0}`, status ok, exit 0. The walk folder itself was never run |
| 2 | a failed own test blocks no deploy | D8 and the Q8 answer | acted | the Operation declares `reads` and `runs` and writes nothing, and the deploy reads the logs of `sim/runs/` only (`project_image.read_run_logs`). `test_it_declares_reads_and_runs_and_writes_nothing` |
| 3 | the record under `.spark/` has no reader yet | O2 of the plan | raised | P1209 [#1758](https://github.com/xmejkal/spark/issues/1758), which adds the page line and, with its reader, the record |
| 4 | the critical cap is 50 and full | council C1 | acted | no new row carries a `tier` key (`tests/mutations/p1208-check-firmware.json`) |
| 5 | `--timeout` needs a float kind that the core's schema refuses | council C2 | acted | no `--timeout`: the import timeout (`IMPORT_TIMEOUT_S`, 5 s) and the tests' (`OWN_TESTS_TIMEOUT_S`, 60 s) are constants, and `CheckFirmware(import_timeout_s=, tests_timeout_s=)` takes shorter ones for a test. The core is untouched. `test_import_firmware` gives its short timeout the same way |
| 6 | a module `check_firmware.py` beside the script breaks the basename rule | council C3 | acted | the module is `spark/firmware/firmware_check.py` |
| 7 | `TheChecksAreaTest` globs `scripts/check_*.py` and lists `check_firmware.py` as a checks CLI | the build, `tests/test_architecture.py:449` | raised | not in the plan, so the test is left red and unchanged. One line fixes it: leave `check_firmware.py` out of that glob, or list it as the firmware area's CLI. For the PO or spark-main to decide, and to file |
| 8 | a runner as a Service adds a T1 breach and writes the `-I -B` launch twice | council C4 | acted | the Adapter `IsolatedPython` (`isolated_python.py`) starts every child through the given `run`. The T1 baseline of `import_probe.py` (3) is gone, and the new modules add none |
| 9 | six rows anchor on `scripts/import_firmware.py` | council C5 | acted | `--anchors` refused 15 rows: six on the script, eight on `import_probe.py` and one of `p1077` (the catalogue's `bench` row). 14 moved, in four tables, each planted by hand and caught. One row retired: "P59: --json prints the text" (`p59-firmware-stand-in.json`), because `--json` is now the core's `view_for`, which the core's own tests and rows hold |
| 10 | the runner's method `run` clashes with the `run` callable | council C6 | acted | the keyword is `own_tests_reader` and the method `read(project, run)` |
| 11 | `tests/test_outcomes.py` `READERS` could list the runner | council C6 | rejected | its rows feed a reader one text, and a good, a malformed and a missing input each. The runner starts a child, so its three states are pinned in `tests/test_own_tests.py` instead |
| 12 | the settings section names no setting | council C7 | acted | each choice is a constant or a keyword in the firmware area, and none is a setting: the free checks always run |
| 13 | a package `tests/` fails relative and package imports in the child | council C8 | acted | the child puts the project first on `sys.path` and discovers a package from the project's folder. `test_tests_in_a_package_import_relative_and_from_the_firmware_folder` |
| 14 | a test that prints with no newline breaks the last JSON line | council C9 | acted | the child points `sys.stdout` at stderr while the tests run, then writes a newline and the line. Two tests and row 4 |
| 15 | `passed` can go below zero, an unexpected success counts as passed, an empty `tests/` is "0 of 0" ok | council C10 | acted | a failing test counts once, an unexpected success is a failure, a run of 0 tests is `not-checked`, and `passed` never goes below 0. One test each |
| 16 | the failure sentence cannot name the error's line | council C11 | acted | the child sends the last traceback line beside each id, and each Finding's sentence ends with it |
| 17 | `journey.svg` and `map.md` need their tools | council C12 | acted | `python3 tools/journey.py` and `python3 tools/map.py --write`; `scripts.md` says that the tests may write files in the project |
| 18 | the child prints `ran`, the Value says `total`; the Operation has no `summary` | council C13, C14 | acted | `total`, and a `summary` |
| 19 | the own tests get none of the import check's stand-ins | the build | raised | a project's test that imports `machine` fails as `own_test_failed` unless the test brings its own (the clock's do). `scripts.md` says so. Plan risk R3, unchecked on a project that does import it: for the PO's next walk |
| 20 | a `tests/` folder that holds no test is `could-not-run` (exit 2) | council C10, the build | raised | v2-10 says "not-checked with a note, never 0 of 0 ok"; the build made it a `could-not-run` finding (`own_tests_not_run`), so the exit is 2, not 0. The PO may prefer a note: one line in `firmware_check.own_test_findings` |
