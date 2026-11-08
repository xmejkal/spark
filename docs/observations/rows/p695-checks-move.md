# P695 checks move (W6-C3): rows

The claims of the W6-C3 plan are in `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md`
(section "W6-C3, the checks move" and its "P695 claims check"). They were checked against main 087ae1a4 before any
code, then the build. Card: [P695 #937](https://github.com/xmejkal/spark/issues/937).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the seven files hold 2,585 lines | plan | closed | 2,708 after P693. After the move the CLIs are 40 to 73 lines, and `physics_check.py` is 609 |
| 2 | 118 rows in the moved files | plan | closed | 132 in 27 tables. `--anchors` refused 1 of them on main (`sprint-8-p52` 21) |
| 3 | 14 rows find text in a `main` that stays | plan | acted | 15: `p693-check-codes` 11 joins. `--retarget` the seven files, then a script gave the 15 back to the six CLIs. Each CLI imports the names its `main` reads by name, so the six `main`s stayed byte-equal |
| 4 | 4 rows name an old module in their text | plan | acted | 5: `p693-check-codes` 3, `sprint-2` 8, `sprint-3-p13` 1, `sprint-8-p52` 21 (refused on main, still refused) and `sprint-3-p13` 3. The two `sprint-3-p13` rows load the second copy from the file beside them, as `SCRIPTS` went |
| 5 | the move is only `git mv` and the import lines | claims check | acted | 16 test locals named `check` read `check_all.` in the same function, so `check.CHECKS` raises `UnboundLocalError`. Renamed to `each` (a loop) and `chosen` (a `next(…)`), and the static method `check` to `demo_check`, in their own commit first. No row anchors on them |
| 6 | 27 baseline keys, R2 1 | plan | acted | 26 name a moved file (no R2 key). 19 follow it (`measure.py --rules --accept-new`): C1 1, R1 4, R6 12, T1 2, 18 at equal values. `R1 physics_check.py:<module>` falls from 659 to 609. The 6 `main` R1 keys and C3 `EXIT_MISMATCH` stay with the CLIs. `R1 check_spine.py:<module>` took its value on main, 1046 (1048 since P694) |
| 7 | 6 `MAY_READ` keys | plan | acted | 7. 6 renamed (`physics_check` 3, `check` 2, `build_check` 1). `check_codes.CODES` stays |
| 8 | 25 import lines outside the six | plan | closed | 26 (`parts.py:493` lazy, 25 in 11 test files, 7 lazy and still lazy) and 14 among the seven. No `as` import is new |
| 9 | the patch sites | claims check | acted | the two tests that replace `run` and call `main` patch the CLI, where `main` looks it up. `_patched_run` takes the module. A patch of `build_check.run` before `check_footprints.main` failed the test (the early-binding plant). The 8 `check_vendor_pins` sites and `test_check_all.py:950` name the library |
| 10 | the wiring test, two source paths and one exemption follow | claims check | acted | `test_check_all.py` finds the checks in `scripts/spark/checks/` less `check` and `check_codes`. `test_check_footprints.py`, `test_check_physics.py` read the moved source, and `test_board_look.py` exempts `physics_check.py` |
| 11 | each CLI keeps its docstring | build | acted | no CLI passes `__doc__` to argparse. The library keeps the long docstring (why the check exists), and the CLI gets its first line, its usage and where the check lives |
| 12 | a library keeps the CLI's `noqa: E402` and imports | build | acted | the path lines went, and with them each `noqa: E402`, `import sys` and every import only `main` read. Each library's imports sit in one block. `vendor_pins_check` imports no outcome at all |
| 13 | the closing check | plan | acted | `TheChecksAreaTest`: the seven modules, the six CLIs and `check_spine.py` in `scripts/`, each CLI defines `main` only, an `__init__` with no import, each module imports alone. A `rules_check.py` copied back to `scripts/` and a planted `verdict()` in `check_bom.py` each failed it |
| 14 | the split keeps each file's mode | build | acted | the CLIs are 755 and the seven libraries 644 |
| 15 | `--anchors` refuses only what main refused | build | verified | 114 refused, the same names as main 087ae1a4, none new |
| 16 | agent pages name a check path | plan | closed | they name the CLIs, which stay. Changed: `patterns-and-names.md` (the fifth area package), `areas/checks.md` (today's lines, `__init__` imports nothing). `tools/map.py --write` added the area to `docs/guide/map.md` |
| 17 | the whole suite is green | build | verified | 4,361 tests, `OK (skipped=1)`, exit 0 at a1173ad3 |
| 18 | review: physics_check names `check_footprints` where the library is meant, with a note inside the import block | review | acted | it names `build_check` at the three places, and the `package_of` note sits after the imports on one line, so the module stays at 609 |
| 19 | review: check.py's Audit A7 note described the removed `sys.path` line | review | acted | it still says something true about the lazy imports, so it sits above the first check that imports lazily. The lazy `import design` in `placeholder_components_in` stays: a row anchors on it |
| 20 | `sprint-3-p13` 2 loads `design` by `SCRIPTS`, which went | review fixes | acted | missed by the build: the mutant raised `NameError`, a catch for the wrong reason. Its `replace` loads `Path(__file__).resolve().parents[2] / "design.py"`. A `--copy` run of rows 1 and 2 on `check.py`: 2 planted, 2 caught |
| 21 | review: `check_bom.py`'s import line is 138 characters | review | acted | wrapped. No row finds it |
| 22 | `parts.py:493` imports the pull-up band from `spark.checks.rules_check` | review | raised | an upward edge from records and sourcing to checks (U1), old and lazy, now visible. The records move takes the band down into design or records |
| 23 | names sit close: `check.py` is the commonest local name; `build_check`, footprints and `Buildability`; `order_check`, `check_bom` and `TheOrder`; `rules_check`, `compare_design` and `RulesVsNetlist` | review | raised | for the names table, from the area page. The page gave the module names |
| 24 | `PROBLEM` and `PACKAGE_POWER_W` are written in both `build_check.py` and `physics_check.py` | review | raised | a prune after the move |
| 25 | the CLIs still hold some logic in `main` | review | raised | byte-equal by design. For the checks Operation card |
| 26 | `sprint-8-p52` 21 was refused on main | refuter | raised | dead before this card, [P682 #918](https://github.com/xmejkal/spark/issues/918). Still refused, with the new module name |
| 27 | `R1 check_spine.py:<module>` 1048 to 1046 | refuter | verified | stale since P694, correct now |
| 28 | `check_bom.py --circuit nope.json` and `check_vendor_pins.py nope.json` crash on both trees | refuter | raised | older than the move, [P688 #926](https://github.com/xmejkal/spark/issues/926) |
| 29 | `agents/design-reviewer.md:55` names a check path | refuter | verified | it names a CLI, still true |
