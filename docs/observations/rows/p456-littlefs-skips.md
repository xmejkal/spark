# P456: the tests that need littlefs skip with the reason in eight more test files

Findings of P456 (#621), 2026-10-31, Prague, built on main b9156270 (includes P451, P454, P455). Counts taken on this head, `-B`, own TMPDIR.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Plan: 304 failing lines, 300 failing entries, on main 00a410b6 | plan | verified, re-measured | on b9156270: 11 files, `/usr/bin/python3` 3.9: Ran 603, failures=171, errors=135; 296 FAIL/ERROR lines, 300 failing methods (header lines), plus the `setUpClass` of `BenchGoldenTest` and the `TheBenchCodesTableTest` table test |
| 2 | Harness: pyenv 3.10 with `sys.modules["littlefs"] = None` fails the same names as 3.9 | plan step 1 | verified | `PYTHONPATH=<scratch>/block python3`: the same 296 FAIL/ERROR lines and the same ok lines, `diff` empty; nothing fails for another reason |
| 3 | 19 whole classes (18 plus `BenchGoldenTest`), 44 classes with a failure | plan | verified | 19 classes get `@needs_littlefs` on the class, the other 25 on each failing method |
| 4 | `test_journey_basic` is missing from the card | plan | acted | 2 methods of `TheBasicJourneyTest` decorated |
| 5 | `TheBenchCodesTableTest.test_every_reason_raised_is_in_the_table` heals when test_board_look skips | plan | verified, no change | not decorated; on 3.9 it passes (`result.wasSuccessful()` counts a skipped inner test as a pass) but covers 19 of 23 codes there; the hook's 3.10 runs all |
| 6 | After on 3.9: OK, `skipped=320` | this PR | verified | 300 decorated methods plus the 20 tests of `BenchGoldenTest`; the skipped names equal the 300 failing names (`diff` empty) apart from the 20 golden tests |
| 7 | 3.10 with littlefs: main and branch equal | this PR | verified | both Ran 623, OK, no skips; the ok names equal (`diff` empty); "littlefs package is not installed" appears 0 times |
| 8 | Step 4: fake-finder tests might run on 3.9 with a stand-in image | plan | rejected | `ToolMissingEvidenceTest` with `write_bytes(b"x")` passed on 3.10 and failed on 3.9: the littlefs check runs before the interpreter lookup. `test_a_missing_interpreter_is_could_not_run...` (flash_image), `test_a_missing_tool_could_not_run...` (run_scenario) and `test_a_missing_image_tool_with_no_simulation...` (deploy_json) fail on 3.9 undecorated for the same reason. Kept decorated; the undecorated fake-finder tests that already pass (e.g. board_look `test_a_missing_image_tool_is_tool_missing...`) keep running |
| 9 | Later (proposed): an injected image checker would let the port, chip, flash and tool-missing tests run on 3.9 | P452 row 5 | raised (LATER) | also unblocks step 4 above |
| 10 | Later (proposed): a CI job on Python 3.9 | plan | raised (LATER) | catches a test that needs littlefs and is not marked |
| 11 | Mutation table | plan | closed | tests only, no script logic changes |
