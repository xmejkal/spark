# P694 breadboard move (W6-B3): rows

The claims of the W6-B3 plan, `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md` (section
"W6-B3, the breadboard move" and its "P694 claims check"), checked against main dac6d4d2 before any code, then the
refuter's check of that block, then the build. Card: [P694 #936](https://github.com/xmejkal/spark/issues/936).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `breadboard.py` is 600 lines, `breadboard_steps.py` 211 | plan | closed | 528 and 321 after P692. The ten files hold 2,393 lines. After the move the CLI is 83 lines and `sheet.py` 454 |
| 2 | 166 rows in the moved files | plan | closed | 175 in 14 tables. `--anchors` refused 13 of them on main (sheet 5, kept_moves 8) |
| 3 | 4 rows find text in the `main` that stays | plan | acted | 5: p191 15, p273 16, p279 8, p686 6, p692 6. `--retarget` the ten files, then a script gave the 5 back to `scripts/breadboard.py`. The CLI imports `CHANGE_LIST`, `REFUSALS`, `SHEET` and `write` by name, so `main` stayed byte-equal |
| 4 | 5 rows name an old module in their text | plan | acted | 4: p273 15, p287 30 (`kept_moves.`), p273 24 (`sheet.`, in `check_spine.py`), p412 25 (`drawing.`, in `part_shape.py`). `tabbed_page` and `breadboard_codes` kept their names |
| 5 | the move is only `git mv` and the import lines | claims check | acted | two names hid the new modules: the function `breadboard.drawing` (it hid the module `drawing` in `sheet.py`) and `check_spine.keep_breadboard`'s local `sheet` (an `UnboundLocalError`). Renamed to `drawing_text` and `sheet_path` in their own commit first. No row anchors on either |
| 6 | 17 baseline keys, R6 9 | plan | acted | 16 name a moved file. 15 follow it at equal values (`measure.py --rules --accept-new`): C1 2, R2 1, R3 2, R6 8, T1 2. `R1:scripts/breadboard.py:main` stays at 26. No new R1 key (`write` is 40) and no X2 key |
| 7 | each R6 docstring gets a role word and its key goes | plan | rejected | the coordinator: only path renames at equal values, so the move edits no docstring for a rule. The 8 R6 keys follow their file |
| 8 | 10 `MAY_READ` keys, 8 renamed | plan | acted | 12 keys. 9 renamed (`drawing`, `kept_moves` 2, `wiring_steps` 3, `sheet` 3). `breadboard_codes.CODES` and the two `part_pictures` stay |
| 9 | 53 import lines, 10 test files | plan | closed | 56 lines (14 among the ten, 6 in `scripts/`, 36 in 14 test files, 4 lazy and still lazy) and 10 reads through a module. 15 test files changed |
| 10 | the patch sites | claims check | acted | 12 `patch.object` sites. The 4 on `_plan_layout` name `sheet`, where it is looked up. 5 patch objects, 3 globals (`tabbed_page.subprocess` 2, `os.replace`). No test patches a name the CLI imports |
| 11 | `commands/build.md` and `recorded-run.md` change | plan | rejected | they name the CLI, which stays. Changed: `agents/scripts.md`, `patterns-and-names.md`, `data/wokwi-geometry.json`, the CLI's help, `areas/breadboard.md` |
| 12 | `__init__.py` holds `OPERATIONS` (the area page) | area page | rejected | it holds the index docstring alone and imports nothing, as the firmware area's. The page says the Operation card brings `OPERATIONS` |
| 13 | the closing check is `ls` | plan | acted | `ls` exits 2 when two of its files are gone. `TheBreadboardAreaTest` checks the ten modules, the CLI's top-level names (`main` only), an `__init__` with no import and each module alone in a child Python. A `drawing.py` copied back to `scripts/` and a planted `verdict()` in the CLI each failed it |
| 14 | `tools/map.py:32`-`:33` register two tables under `breadboard` | refuter | acted | they read `spark.breadboard.sheet`. `map.py --write` added the area to `docs/guide/map.md` |
| 15 | comments name the old homes (`spark/core/outcomes.py:45`, `onboard_parts.py:42`, `:130`) | refuter | acted | they name `kept_moves`, `bench_changes` and `sheet.BOARD_COMPONENT`. The moved docstrings that named `breadboard.`'s attributes or "`breadboard.py` calls it" name `sheet` |
| 16 | the import graph has no cycle | claims check | verified | each of the ten imports alone. `part_shape` (design) imports `drawing`, and `drawing_catalog` imports `part_shape`: a two-way area edge with no module cycle, for the design wave |
| 17 | `--anchors` refuses only what main refused | build | verified | 114 refused, the same names as main dac6d4d2. 13 on the moved files, and the `check_spine.py` rows the refuter saw were refused on main too |
| 18 | `test_breadboard_changes.py:20` imports with `as changes` | build | verified | kept: it was aliased before the move, so `MAY_READ` skips its reads as before. No new alias |
| 19 | `drawing_catalog` kept `sys.path.insert` | plan | acted | it went with its `sys` and `Path` imports. The CLI keeps its own, which `test_scripts_isolated` needs |
| 20 | the split keeps each file's mode | build | acted | `git mv` gave `sheet.py` the CLI's executable bit, and the rewritten `breadboard.py` lost it. `test_routes` caught it in the whole suite (`build.md` runs the CLI by path). The CLI is 755 again and `sheet.py` 644 |
| 21 | the whole suite is green | build | verified | 4,341 tests, `OK (skipped=1)`, exit 0, after row 20, and 4,344 after the rebase onto 924e48a4. A first run piped through `tail` printed exit 0 for a failed suite: read the exit code of `unittest`, never of the pipe |
| 22 | review: the import lines are not grouped and sorted as the firmware area's | review | acted | `drawing.py`, `check_spine.py` (with `tabbed_page`) and `test_breadboard_svg.py` import `from spark.breadboard import a, b` in one sorted line |
| 23 | review: `sheet.py:412` still aligns to the old `breadboard_drawing.NotWritten(` | review | acted | re-indented to `drawing.NotWritten(` |
| 24 | review: the upward edge from design to breadboard is not on the area pages | review | acted | `areas/design.md` and `areas/breadboard.md` say it: `part_shape` imports `drawing` (`NotDrawn`, five codes, `WOKWI_GEOMETRY_FILE`) and `drawing_catalog` imports `part_shape`. [P698 #943](https://github.com/xmejkal/spark/issues/943) plans its removal |
| 25 | review: docstrings say what was moved, or say the CLI writes the sheet | review | acted | `sheet.py` drops "Moved from", `breadboard_codes` names `sheet.write`, `__init__.py` fits 120 characters |
| 26 | review: names that sit close (`drawer` and `drawing`, `bench_changes`, `kept_moves` and `KeepMoves*`, `sheet.sheet`) | review | closed | noted for the names table, not acted: the page gave the module names — P776: stale note: Names noted, not acted. |
| 27 | review: two test locals named `sheet` (`test_breadboard_match.py:140`, `test_check_spine.py:466`) | review | verified | harmless: neither function reads the module `sheet`. Noted, not acted |
| 28 | review: `check_spine.py`'s `except` tuple names `sheet.NotBuilt` beside design's errors, not `sheet.REFUSALS` | review | closed | for the design wave, [P698 #943](https://github.com/xmejkal/spark/issues/943). It also catches `ValueError`, which P691 holds — P776: done by #943 (closed), P691 #933 (closed), P698 #943 (closed) |
