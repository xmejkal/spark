# P369: every entry script runs under python3 -I

Findings of P369 (#471), 2026-10-31, Prague, built on main b9156270 (includes P451). Python 3.10 pyenv, `-I -B`, own TMPDIR.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `parts.py --list` under `-I` stops with `No module named 'outcomes'` | card #471 | verified, the name is `'spark'` now | parts.py:220 `from spark.core.outcomes import ...`; outcomes moved to `scripts/spark/core/` |
| 2 | Any action crashes | card #471 | verified | `--help` and `--list` give the same traceback, exit 1 |
| 3 | Other scripts that import `outcomes` crash the same way | card #471 | verified, wider | of 24 entry scripts, 14 crashed (boards, check_bom, check_footprints, check_vendor_pins, compare_design, cost, deploy, flash_image, grant, live, look, parts, reach, run_scenario); 10 passed. Same list on b9156270 as on 00a410b6 |
| 4 | Fix: one line in the 14 | plan | acted | `sys.path.insert(0, str(Path(__file__).resolve().parent))` before the first sibling import; look.py also gets `from pathlib import Path` (15 code lines) |
| 5 | A launcher script or an installed package | plan | rejected | it changes every command line in `commands/*.md` and makes the user install something |
| 6 | import_child.py | plan | acted | exempt in the test: its first argument is a module (P443), run with `-I` on purpose |
| 7 | R1 on boards.py (969) and parts.py (2375), both over 600 | plan | acted | the path line replaces the blank line before the first sibling import; line counts unchanged, `measure.py --rules` exit 0 |
| 8 | Plan missed two fixtures | build | acted | `test_look` pins the set of look.py imports (now holds `pathlib`); `test_suite_temp` needs every test module to import `suite_temp` first |
| 9 | A check for libraries that run `__main__` code | plan | raised (LATER) | the 41 libraries have no guard; nothing checks that they stay so |
| 10 | Two spellings of the idiom (`SCRIPTS = ...; sys.path.insert(0, str(SCRIPTS))` and the one-liner) | plan | raised (LATER) | unify in one spelling |
