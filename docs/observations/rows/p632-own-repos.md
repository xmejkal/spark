# P632 the engine and the driver fork in their own repositories: rows

What the plan rounds, the review, the refuter and the mutation runs found. Card: [P632 #846](https://github.com/xmejkal/spark/issues/846).
PRs: https://github.com/xmejkal/s3lcd/pull/1, https://github.com/xmejkal/pixel-engine/pull/1, https://github.com/xmejkal/pixel-games/pull/35. Rows PR: https://github.com/xmejkal/spark/pull/849.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The engine reads two driver headers (`s3lcd.h` in `binding.c`, `blend565.h` in `fx_fire.c`), so the engine cannot leave alone. The PO picked two repositories: games → engine → driver | the plan, the code | acted | `xmejkal/pixel-engine` with `driver/`, `xmejkal/s3lcd`, both private |
| 2 | Plan round 1 (Fable refuter), MUST: three staying tests set `S3LCD_SRC` themselves | the plan, round 1 | acted | they import it from `clang_lib`, so the path lives once |
| 3 | Plan round 1, MUST: equal section sizes prove nothing, and `ESP_ERROR_CHECK` in `s3lcd.c` stores `__FILE__`, so the image size changes | the plan, round 1 | acted | `objdump -d` of the 19 objects is the proof: the same, all 19. The image grew by 32 bytes |
| 4 | Plan round 2, three SHOULD: the objdump listing names its object path on line 2, `test_fire.py` set its path after its import, and `games/lcd.py:15` and `README.md:42` still named `s3lcd/src` | the plan, round 2 | acted | the first two lines dropped, the import order fixed, both paths in the sweep |
| 5 | Only `test_balls_core.py` imports the engine alone. The other C tests import game modules (`motion.py`, `lcd.py`, `gfx.py`), so they stay in pixel-games | the plan | closed | P633 #847 decides where the Python twins and these tests live — P776: done by #847 (closed), P633 #847 (closed) |
| 6 | The first mutation run: 8 planted, 3 caught. A whole-suite run hides a wrong `sys.path` line, because the first file to set a path serves the rest. No test read the cmake and `build.sh` paths | the mutation run, round 1 | acted | `test_games_layout.py` and the engine's `test_layout.py`. The run after the fixes: 9 of 9 and 3 of 3 caught (pixel-games #35's body) |
| 7 | After the re-pin, the engine's `test_layout.py` shadowed the games' own, because `engine/tests` is on the games' path. A test run chained through `tail` hid the failure, and the commit went through | the suite after the re-pin | acted | renamed `test_games_layout.py`, a test refuses a shared module name. Logged in `~/.local/share/spark/learned-rules.md`: the rule against a chain through `tail` exists and was not followed |
| 8 | The Sonnet reviewer: stale paths in C comments (`binding.c`, `fx_fire.c`, `fx_fire.h`, `world.h`, `blend565.h`) and the walkthrough's line numbers without an engine commit | the PR review | acted | comments only, the walkthrough names pixel-engine `97f2d64` |
| 9 | The reviewer: the `build.sh` guard fails unclearly in a tarball without `.git` | the PR review | rejected | a GitHub tarball has no submodules, so a clearer message changes nothing |
| 10 | The Fable refuter reproduced every claim: history blob by blob, 137 + 22 tests, 19 of 19 objects, the fps, a fresh clone. One SHOULD: the driver re-pin step was missing from the PR body | the PR refuter | acted | pixel-engine re-pinned to s3lcd's merged main `68a86b2` before its merge (pixel-engine #1), merges with merge commits |
| 11 | A PR number in a moved commit message (for example `#18`) now links to the wrong repository | the history | acted | both READMEs say that such a number is a pixel-games PR |
| 12 | Same pixels, same fps: three rendered scenes are the same bytes, flappy 28 fps (run109 → run114), the rain 24 to 25 fps (run112a → run114) | bench.md P632 | closed | the bench table |
| 13 | Each new repository had no `.gitignore`, so a test run left `__pycache__` in the submodule | the work | acted | `.gitignore` in pixel-engine |
| 14 | The P628 Miro frame and the read-back of the deep-dive frames wait for Miro's daily limit (100 calls on the free plan) | Miro | closed | owed under P627 #840 on 2026-11-06 — P776: tracked by #840 (open), P627 #840 (open), P628 #841 (open) |
