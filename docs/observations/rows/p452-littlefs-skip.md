# P452: the look tests that need littlefs skip with the reason

Findings of P452 (#607), 2026-10-30, Prague, built on main 5a40f2d7 (includes #614). Counts taken on this head, `-B`, own TMPDIR.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Card: 11 failures and 7 errors on a Python without littlefs | card #607 | verified, stale | `/usr/bin/python3 -B -m unittest tests.test_look` (3.9.6): Ran 51, FAILED failures=14, errors=11 (25). Python 3.10 pyenv: Ran 51, OK |
| 2 | Plan: 25 failing names, 24 to skip plus the tool_missing test | plan | verified | all 25 fail from the missing import (7 `ModuleNotFoundError` in `build_from_firmware`, 18 from `image_evidence._why_image_differs`); none is about anything else |
| 3 | After: 3.9 Ran 51, OK (skipped=24); 3.10 Ran 51, OK, no skips | this PR | verified | the skipped names (`-v`) equal the 24 failing names minus `test_no_simulation_with_a_finder_that_lacks_littlefs_gives_no_token_and_the_install_line`: `diff` empty |
| 4 | The tool_missing test runs on both Pythons | plan step 3 | acted | `self.image.write_bytes(b"x")` replaces `build_from_firmware()`; passes on 3.9 and 3.10 |
| 5 | 18 of the 24 test port, chip and flash logic and need littlefs only through the image check | plan | proposed (LATER) | an injected image checker would let them run on 3.9 |
| 6 | The same import breaks 8 more test files on 3.9 | plan | proposed | card P456: the other 8 test files skip with the reason on a Python without littlefs; reuses `needs_littlefs` |
