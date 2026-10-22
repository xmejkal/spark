# P386 R0 yardstick: findings rows

Rows from the plan checks of P386 (#495), set R0. An implementer (Sonnet 5.5) checked each plan claim in the code on
2026-10-22. Later sets of the card add their rows to this file.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The `P172:` note on a `# noqa` line is a broken directive for Ruff, in 68 files plus `tests/test_suite_temp.py` | plan step 1 | verified | 69 files, 69 lines, changed to `(P172)`. Ruff then prints no "Invalid `# noqa` directive" warning. Planted on `scripts/outcomes.py`, the warning appeared and `tests/test_lint.py` failed |
| 2 | The one E402 is `tests/test_converter.py:38`, a second `import sys` | plan step 2 | verified | The second `import sys` is gone, `sys` is imported at the top already. `ROOT` and the path line moved up. `ruff check` passes |
| 3 | Ruff in the main checkout would scan `.claude/worktrees`, which `.gitignore` does not list | pyproject.toml | acted | `.claude` is added to `extend-exclude`, which the plan did not list. A worktree run did not show the problem, because it has no nested worktrees |
| 4 | The starting numbers in the plan are right: C901 24, PLR0913 29, B904 23, B023 7, UP031 1,570, E501 1,861, F401 47, E401 21, E702 40, E741 11, E731 3, F841 2 | plan step 5 | verified | One run of `ruff check --statistics --exit-zero --output-format json` with `select = E,F,B,UP,SIM,C90,PLR` and no `ignore`. Total 3,753 findings. Every number equals the plan's. Also 352 `mock.patch` lines (279 `.object`), 98 files with `sys.path` before `tests/test_lint.py`, 434 `noqa` before it |
| 5 | `tests/test_parts.py:940` holds `catalog, store =` | plan R2 step 3 | rejected | Line 940 does not. Ruff F841 names `tests/test_parts.py:946`. Lines 923 and 971 hold the same text and use `store`. R2 must edit line 946 only |
| 6 | `factcheck.py` reports one broken reference on the plan | plan step 7 | verified | `README.md:97` is ambiguous, because six files share the name. The plan means the root README. Not a wrong claim. The names `diff_line`, `stale_doc_paths` and `text_line` are proposed, so they are expected |
| 7 | The plan names `tests/test_converter.py:38` for the E402 fix, and `tests/test_assign_pins.py:491` for an E741 | factcheck | raised | Line numbers shift after R0 edits, so R2 must take the finding lines from Ruff at that time, not from the plan |
| 8 | The step 4 test skips cleanly without Ruff and fails on a planted F821 | plan step 4 | verified | `PATH=/usr/bin:/bin` run: OK (skipped=1). Planted `print(undefined_name_for_mutation)`: FAILED with Ruff's F821 line |
