# P683 firmware golden net (W6-F1): rows

What the build of W6-F1 found against its plan, `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md`
(section "W6-F1, the golden net"), and the choices it made. Card: [P683 #920](https://github.com/xmejkal/spark/issues/920).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the guard: a fake token in every child, `"also": []`, the shim refuses any other token, a test asserts the shim is found | plan | acted | `ShimGuardTest`, written and committed before any golden. `FirmwareGoldenTest.setUpClass` also refuses to run a Case unless `tools.find("simulator")` is the shim |
| 2 | `tools.find` takes an absolute `exe` (risk 4) | plan | closed | `shutil.which` takes a path: `test_the_simulator_found_is_the_shim` passes, so the shim stays off `PATH` |
| 3 | `"also": []` leaves the shim or nothing | plan | acted | `tools.locate` also falls back to the `fetch` file in the store's downloads. The child's store is its own and empty, so it was harmless, but the entry sets `"fetch": null` too |
| 4 | the guard bites | build | acted | the token row tried by hand: with a pretend token in the parent, the shim refused and 3 tests failed; with none, 2 failed and 1 erred. The real token was never set in any run (`env -u WOKWI_CLI_TOKEN`) |
| 5 | the goldens sit beside the bench's (`tests/golden/`) | build | rejected | `test_golden_bench`'s `test_every_golden_has_its_case` and `test_no_golden_holds_a_path_of_this_machine` read the whole folder, and that file is #915's. The goldens are in `tests/golden-firmware/` |
| 6 | `SPARK_ACCEPT=run-scenario` writes the goldens, reusing the bench's check | plan | acted | `golden_bench.op_of` splits at the first dash (`run`), and `golden_bench.py` is not edited. `golden_firmware` has its own `op_of` (the script's name with dashes) and `check_golden` |
| 7 | the Case is `golden_bench.Case` without the two canned board files | plan | rejected | it is `golden script argv exit_code plant env`. `plant` writes into the project (None removes a file), `env` adds the fake tool's output per Case. One golden holds stdout, then stderr after `--- stderr ---`, then the run's log: `run_scenario.py` prints a pass on stdout and the rest on stderr, so no `stderr_golden` |
| 8 | the scrub needs a sha256 pattern for the run log | plan | rejected | `replacements_of` replaces the image's sha256 exactly (`sim/*.bin`), and the `file sha256` line is of the fixed `main.py`. `CLOCK` matches the log's date (`TZ=UTC`). No new pattern; its mutation row became "the stderr dropped" and "the golden project's own log kept" |
| 9 | the mutation row "a Case's exit code ignored" | plan | rejected | with the check removed every Case still ends with its code, so the row survives. The row plants a wrong expected code instead, which the check catches |
| 10 | the bench's project serves the firmware Cases as is | build | acted | `build_project` leaves its passed run's `sim/runs/s.log`, which showed in the flash and import goldens. `run_script` removes the project's logs first, so a golden shows only a log its run wrote. Each Case runs in its own copy of the project |
| 11 | `import-firmware-problems.json`: a module whose import raises | plan | acted | a missing module (`import missing_driver`), not a name a stand-in lacks: the stand-in's words name its own path, which W6-F3 moves |
| 12 | none of the three CLIs runs through `run_cli` | plan | closed | no `run_cli` in the three scripts. `<project-dir>/sim` is a scrubbed path in the no-sim golden |
| 13 | four places run the fake tool directly | plan | closed | `test_run_scenario.py:30`, `test_deploy.py:36`, `test_journey_basic.py:51`, `golden_bench.py:35` and `:154`. `fake_wokwi_cli.py` is unchanged |
| 14 | size est. 120 test lines and 8 goldens | plan | raised | 240 lines (141 helper, 99 tests, the guard among them) and 8 goldens |
| 15 | `developing.md` names the firmware goldens | build | acted | at its budget of 379 lines: two paragraphs reflowed, and "the two grant runs add about 10 s" dropped to make room |
