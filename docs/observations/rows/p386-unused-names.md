# P386 R2: unused names rows

Gaps and findings from R2 of P386 (#495), the unused names and three small rules (2026-10-22, Prague). One agent
(Opus 5.5) did the work on top of R1.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan says 47 F401 findings and 20 E401 findings after them | plan | verified | F401 was 47 and E401 was 24 before F401 and 23 after. Ruff fixed all 23 |
| 2 | Re-exports are only needed in the scripts that `tests/test_outcomes.py` lists in `SCRIPTS` | plan | rejected | `tests/test_check_commit.py:143,201,208,215` read `check_commit.EXIT_OK` and `EXIT_PROBLEMS`, and `check_commit` is not in `SCRIPTS`. Four tests failed after the F401 fix, so `tools/check_commit.py` got the same re-exports |
| 3 | `from outcomes import EXIT_OK as EXIT_OK` keeps F401 quiet for every name | plan | rejected | Ruff honours only the same-name form. The aliases `EXIT_PROBLEMS as EXIT_MISMATCH` (`scripts/check_vendor_pins.py:44`) and `as EXIT_INVALID` (`scripts/parts.py:219`) still fire, so those two lines carry `noqa: F401` |
| 4 | `tests/test_assign_pins.py` holds an E741 at line 580 | plan | rejected | The place is line 589. The other four lines (491, 522, 537, 549) and the `tools/snapshot.py` and `tests/test_snapshot.py` lines held |
| 5 | The `boards.definition_path(project)` call in `scripts/check_all.py` stays, and only `active =` goes | plan | verified | Line 406. Its exception writes the "not resolved" note. `tests.test_check_all` passes |
| 6 | The unit suite is the oracle | plan | verified | 2924 tests, OK, 2 skipped, before and after each step. Ruff prints no finding |
| 7 | `ignore` ends with only E702 | plan | verified | `pyproject.toml` holds E702 with the comment "ruff format, after the walk" |
| 8 | Dead code: `scripts/check_all.py` imports `EXIT_OK`, `EXIT_PROBLEMS` and `EXIT_COULD_NOT_RUN` and uses none of them | prune sweep | raised | `/usr/bin/grep -n EXIT_ scripts/check_all.py` finds only line 58. Only `tests/test_check_all.py` and `tests/test_outcomes.py` read them. The decision on `EXIT_*` in scripts waits for the refactor after the walk |
| 9 | Dead code: `EXIT_MISMATCH` in `scripts/check_vendor_pins.py` and `EXIT_INVALID` in `scripts/parts.py` are bound and never read inside their module | prune sweep | raised | `/usr/bin/grep -rn "EXIT_MISMATCH" scripts tools` finds only line 44. `EXIT_INVALID` has only line 219 in `parts.py`, and `boards.py` has its own. Only the `SCRIPTS` contract reads them |
| 10 | Repeat: `scripts/boards.py:119` and `scripts/parts.py:219` import the same `EXIT_PROBLEMS as EXIT_INVALID` alias | prune sweep | raised | Two names for one code in two scripts. One decision, with the `EXIT_*` question above |
| 11 | Dead code: `import boards` in `scripts/emit_board.py:40` was unused and is gone | prune sweep | acted | Ruff removed it. The suite passes, so no code needed its side effect |
| 12 | Repeat: `tests/test_parts.py` imported `tempfile` and `unittest.mock` inside 17 test methods and never used them | prune sweep | acted | Ruff removed them in the F401 commit |
