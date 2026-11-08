# P702 design values move (W6-D3a): rows

The claims of the W6-D3a plan are in `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md`
(sections "The four moves, W6-D3a, W6-D3b, W6-D3c and W6-U3" and "W6-D3a, the design values", and the "P702 claims
check"). They were checked against main 2d131ffd before any code, then the build. Card:
[P702 #949](https://github.com/xmejkal/spark/issues/949).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the six files hold 1,500 lines | plan | closed | 1,541 after P700: `design.py` 477, `assign_pins.py` 589. After the move the CLI `assign_pins.py` is 89 lines, `pin_assigner.py` 512 and `loader.py` 473 |
| 2 | 121 rows in the moved files | plan | closed | 127 in 33 tables. `--anchors` refused 5 of them on main (`fab.py`, P434), still refused |
| 3 | rows of a `main` that stays go back to the CLI | plan | acted | 3 rows (`p699-design-net` 12, `sprint-4-p20` 1, `sprint-8-p36` 7). `--retarget` the five moved files, then a script gave the 3 back to `scripts/assign_pins.py`. The CLI imports by name what `main` reads (`assign`, `Impossible`, `pin_module`, `pulled_up`, `render`) |
| 4 | the move is only `git mv` and the import lines | claims check | acted | no importer binds `loader` or `pin_assigner`, so no rename commit. But `design` is also a local `Design` value (`design.board`, `design.signals`), so the module's reads were renamed by scope with `symtable`, never by text. A class field `design: object` (`emit_board.BoardInputs`) was caught in the diff and kept |
| 5 | rows that name an old module in their text | build | acted | 18 rows of 14 tables read `loader.`, `pin_assigner.` or `from spark.design import loader` where the importer does. 3 of them (`p97-requirements-fix` 17 to 19) only in `replace`: `--anchors` passed them, but the mutant would raise `NameError`, a catch for the wrong reason (P695 row 20) |
| 6 | `sprint-3-p13` 2 loads a second copy of `design.py` by path | build | acted | its `replace` loads `Path(__file__).resolve().parents[1] / "design" / "loader.py"` as `loader` |
| 7 | 11 baseline keys | plan | acted | 10 (`R6:Impossible` went in P700). 6 follow their file at equal values (`measure.py --rules --accept-new`): `C1:Impossible`, `R1:assign` 116, `R2` `onboard_lines`, `rails_requested`, `Netlist.__init__`. `R6:Netlist` goes: its docstring starts with `Value`. `R1:main` 62, `R2:main`, `C3:EXIT_IMPOSSIBLE` and `T1:file-write` stay with the CLI. No key rose, and no new key |
| 8 | 15 `MAY_READ` keys take the new name | plan | closed | the six hold 11 keys. 6 renamed (`pin_assigner` 5, `loader.CIRCUIT_PATHS`). The `copper` 3 and `fab` 2 keep their stem. No `as` import is new; `design as design_library` went |
| 9 | 52 import lines | plan | closed | 56: 3 among the six, 29 in `scripts/` (2 lazy, still lazy), 24 in 16 test files (4 lazy). The 2 lazy `import assign_pins` that run `main` keep the CLI |
| 10 | the patch sites follow the module that looks the name up | claims check | verified | 2 sites patch an attribute of the module object (`test_check_all.py:951`, `test_check_spine.py:2224`), so they name `loader`. A planted early binding (`EARLY_PARTS_OF = loader.parts_of` at `check.py`'s top) failed `test_the_placeholder_list_uses_the_design_module_everyone_else_imports` |
| 11 | `__file__` and `SCRIPTS` lines | plan | acted | `fab.py:30` takes `parents[3]`. The `SCRIPTS` and `sys.path.insert` lines of `design.py` and `assign_pins.py` went from the libraries, with each `noqa: E402`, `import sys`, `argparse`, `json` and the `outcomes` import only `main` read. The CLI keeps its one path line |
| 12 | the closing check | plan | acted | `TheDesignAreaTest`: the six modules, `assign_pins.py` alone of the six in `scripts/` and it defines `main` only, an `__init__` with no import, each module imports alone. A `netlist.py` copied back to `scripts/` and a planted `verdict()` in the CLI each failed it |
| 13 | the split keeps each file's mode | build | verified | the CLI is 755, the seven files of `spark/design/` 644 |
| 14 | `--anchors` refuses only what main refused | build | verified | 114 refused, the same names as main 2d131ffd, none new |
| 15 | 9 agent pages name a moved path | plan | closed | 3 do: `how-it-works.md` (the libraries), `patterns-and-names.md` (fab's path; the sixth area package added), `developing.md` (`loader.one_board_message`). The rest name the CLI, which stays. `areas/design.md` says the five moved and `__init__` imports nothing. `map.py --write` added the area |
| 16 | two comments name `netlist.py` | build | rejected | `drawing.py:74` and `wiring_steps.py:228` name the file, which keeps its name. A longer path would break the 120-character line |
| 17 | the story's tests are green | build | verified | 34 test modules (the moved modules', their importers', the goldens, architecture, self-confirmation, map, docs, lint, rows): `Ran 1952 tests`, `OK`, exit 0. No full suite and no mutation run (the PO, 2026-11-08) |
| 18 | review: the `Netlist` docstring now starts with `Value:`, a text change in a move PR | review | acted | a deliberate prune: the role word removed the `R6:Netlist` key (row 7), as P694 and P695 did for their R6 keys. No row anchors on the line |
| 19 | review: 12 comments and docstrings name the old module as `design.X` | review | acted | they name `loader.X` (`boards.py`, `check_all.py`, `emit_board.py` 3, `needs.py`, `parts.py`, `check.py` 2, `test_check_all.py`, `test_emit_board.py` 2). `test_design.py:357` keeps `design.signals`, the `Design` value's field |
| 20 | review: `pin_assigner.py`'s docstring shows the CLI's usage lines | review | acted | the usage lives in the CLI's docstring, and the library's first line names the CLI. `map.py --write` followed |
| 21 | review: `areas/design.md` names `assign_pins.Impossible`, `.pin_module`, `.ROLE_PENALTY` and `design.Design` | review | acted | they name `pin_assigner` and `loader` |
| 22 | the review's fixes keep the anchors | review fixes | verified | `--anchors` refuses 114, the same names as before the fixes and as main 2d131ffd |
