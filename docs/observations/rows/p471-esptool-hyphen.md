# P471: spark calls esptool's hyphen commands, with a floor of esptool 5.0

Findings of P471 (#642), 2026-10-31 and 2026-11-01, Prague, built on main da8b6950. Rows 1-9 are the plan council (two rounds), rows 10-14 the build, rows 15-25 the review (Sonnet reviewer and Opus refuter) and its fix round, rows 26-31 the fix-commit refuter (Opus) and the mutation run.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | esptool 4.12.0 knows only `flash_id`, and 5.0.0 is the first with `flash-id`, `erase-flash` and `write-flash` | plan, refuter round 1 | verified | 4.12.0 `esptool/__init__.py:542` argparse, no aliases. 5.0.0 `:624`, `:832`, `:910`. PyPI sdist sha256 values in `scripts/flasher.py` and the PR |
| 2 | The old names are mapped in `cli_util.py:33` | plan | rejected | `:33` maps reset modes. The command names are mapped in `get_command`, `cli_util.py:251-263` |
| 3 | The floor must read the installed version on its own: `installed_versions` returns `{}` with no pin | council round 1 | verified, acted | `tools._installed_release`, used by `installed_versions` and the floor |
| 4 | An `entry_problem` rule refuses `--pin` below the floor | council round 1 | rejected, then acted another way | round 2: `--pin` writes through `choose` and never calls `entry_problem`. The refuter later showed the loop (row 17), fixed in the `--pin` branch |
| 5 | A compare built on `_release` | council round 1 | rejected | round 2: `_release("5.0")` is `"5"` and `"dev0"` has no digits. `versions.release_tuple` reads leading digits |
| 6 | Entry fields are documented in agents.md and how-it-works.md | plan | rejected | refuter round 1: only `commands/setup.md:71` lists them |
| 7 | `tools/journey.py` needs the FireBeetle note | plan | rejected | its Bench text stays true. Only `README.md:91` was stale. The journey picture's date moved with the README, so `docs/guide/journey.svg` was regenerated (row 12) |
| 8 | A `READ` constant beside `ERASE, WRITE` | plan | rejected | council round 1: the string changes at `board_look.py:195`, no new name |
| 9 | The README Bench note is not in P471's Done-when | council round 2 | rejected | it is a stale claim P461's PR left. The prune rule fixes it in the PR that touches the step |
| 10 | `tools.py` passes its length baseline with the floor inside | plan | rejected | `tests/test_architecture` allows 677 lines, the change made 709. The compare moved to `scripts/versions.py`, `tools.py` is 670 and its baseline went down to 670 |
| 11 | A new test class for the floor | plan | rejected | the mock-patch baseline forbids 3 more `mock.patch` calls. The tests sit in `APythonToolIsComparedWithItsPinTest` |
| 12 | The journey picture stays | plan | rejected | its date follows the README. `docs/guide/journey.svg` regenerated, date only |
| 13 | `_python_versions` removed, so 4 rows of `tests/mutations/p214.json` lose their anchor | builder | acted | re-anchored, each `find` once |
| 14 | 8 rows of `tests/mutations/p239-pr7.json` match nothing | builder | raised (LATER) | refuter: `--anchors` refuses the same 8 on origin/main, so this PR did not cause them. Not all are BOOT_HINT rows ("the plan flashes for another chip" is one) |
| 15 | Every interface stops with "too old ... Install:" for esptool 4.12.0, no "hold BOOT", no erase retry | refuter | verified | look (text, `--json`), deploy (`--dry-run`, `--token`, stage `plan`), grant (no grant written), `tools.py --status`. Board_doctor is never reached |
| 16 | `to_install` leaves a too-old esptool out, so /spark:setup never offers the upgrade | refuter | verified, acted | fix round |
| 17 | `--pin esptool=4.12.0` exits 0, and the refusal then offers to install 4.12.0 | refuter | verified, acted | fix round: `--pin` refuses a version below `oldest_version` |
| 18 | The versions docstring says a pin counts a pre-release as its release | review | verified, acted | false for `release`. The docstring names only the floor compare |
| 19 | `versions.key` is a vague name | review | acted | renamed `release_tuple` |
| 20 | No direct test of the compare. The `break` and the trailing-zero lines have no row | review | acted | a table test of `release_tuple` and `is_older`, and two rows |
| 21 | A floor test asserts only that `find` raises | review | acted | it asserts the sentence |
| 22 | agents.md puts the too-old refusal at the deploy's stage `look` | refuter | acted | the refusal comes at stage `plan` |
| 23 | The bench goldens read the real installed esptool, so a machine with esptool 4.x fails them with "too old" | review | raised (LATER) | the goldens assume the pinned tools. /spark:setup installs 5.5.0 |
| 24 | The fake esptool ignores its arguments, so the goldens do not prove the hyphen | review | closed | the unit tests in `test_board_look.py` and `test_deploy.py` hold the argv |
| 25 | `tools.py` stays under its baseline with the fix round inside | builder | rejected, acted | `installed_release` and `too_old` moved to `scripts/versions.py`, which now reads the module metadata (its docstring says so). The `--pin` logic left `main` for `tools.pin()`. The p214 rows were re-anchored, two of them to `versions.py` |
| 26 | `--pin esptool.version=4.12.0` and `--pin esptool=v4.12.0` get past the floor, and setup then offers the old version | fix-commit refuter | verified, acted | `pin()` sets the field first and refuses a `version` below `oldest_version` or with no digits. One test covers the three forms |
| 27 | `tools.py` still imports `importlib.metadata` after the read moved to `versions.py` | fix-commit refuter | acted | the import goes, and the test patches `tools.versions.importlib.metadata` |
| 28 | The agents.md row says a deploy refuses mpremote at stage `look` | fix-commit refuter | verified, acted | `DeployService.plan()` finds esptool and mpremote (`deploy_service.py:84-85`), so the row says stage `plan`. The old words were on main before this PR |
| 29 | The PR body names `key`, leaves out the `to_install` and `--pin` refusals, and draws board_doctor as reached | fix-commit refuter | acted | the PR body is rewritten |
| 30 | Mutation run on a285c8a5: 31 planted, 30 caught, 9 refused | mutation-tester | acted | 2,530 s. The escape: no version with letters and a later dotted part, so `if digits != part: break` was unseen. `("5.0rc1.2", (5,))` joins the table. The 9 refusals: the 8 older rows of row 14 and this PR's floor row, re-anchored on `here = versions.too_old(entry)` |
| 31 | The board memory and the first rows heading named times and a date one hour late | lead | acted | corrected. The lead's clock guesses were wrong, and `date` is the source |
