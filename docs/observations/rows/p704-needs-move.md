# P704 needs move (W6-D3c): rows

The claims of the W6-D3c plan are in `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md`
(sections "The four moves, W6-D3a, W6-D3b, W6-D3c and W6-U3" and "W6-D3c, the needs", and the "P704 claims check").
They were checked against main 508798dc before any code, then the build. Card:
[P704 #951](https://github.com/xmejkal/spark/issues/951).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the extractions `plan_pick` (57) and `requirements` (55) go after the `git mv` | plan | acted | before it, each its own commit (the brief, P703 row 3): P700's `_picks_given` and `_passed_over` (`plan_pick` 31 lines), with `p97-cost`'s layer row, and `_part_picks` and `_held_file` (`requirements` 34). No function of the module is over 40 lines |
| 2 | the extractions are paid by prunes in `needs.py` (P700) | plan | acted | no prune in the module paid them: its docstrings and comments are wrapped at 120, and no statement joins within 120 (checked by script). The module went 831 to 860. `kept_reason` and its URL and price patterns (31 lines) moved to `spark/core/text_guards.py` beside `clean`, as P403 moved the label guards: 829. Its 19 rows followed by a scratch script, and `test_needs` reads `text_guards.kept_reason` |
| 3 | the `R1:<module>` key moves at its value, which does not rise | plan | acted | for the PO's eye: `R1:scripts/needs.py:<module>` 831 became `R1:scripts/spark/design/needs.py:<module>` 829 (`measure.py --rules --accept-new`). `R3:candidates` 6 follows at 6. No other key changed, and no new key |
| 4 | 221 rows | plan | verified | 221 in 22 tables: 19 to `text_guards.py` (row 2), 202 by `--retarget`. 7 rows of 5 tables name `needs.` in `parts.py`'s text: the bound name stays `needs`, so they stay |
| 5 | `--anchors` refuses only what main refused | build | verified | 114 refused, the same names as main 508798dc, none new, after the guard move and after the `git mv` |
| 6 | 11 import lines, `parts.py`'s 7 lazy | plan | verified | each reads `from spark.design import needs`, the 7 in `parts.py` still inside their functions. No `as` import |
| 7 | name clashes with `needs` | claims check | verified | every importer binds the same name as before (`symtable`). The one local `needs` in `test_needs.py` reads no module attribute. No rename |
| 8 | patch sites follow the module that looks the name up | claims check | verified | none names `needs`. `test_needs` patches `parts.LIBRARY`, which `needs._how_to_fill` reads at call time: a planted early binding (`EARLY_LIBRARY = parts.LIBRARY` in `needs.py`) failed `test_what_a_pick_owes_is_filled_where_its_record_lives` and `test_a_library_pick_that_owes_only_its_outline_says_it_is_filled_in_spark_s_repository` |
| 9 | `MAY_READ` | plan | verified | no key names `needs` or `kept_reason` |
| 10 | the closing checks | plan | acted | `TheDesignAreaTest` holds ten modules with `needs`, and no design library module is left in `scripts/` |
| 11 | 2 agent-facing pages | plan | acted | `how-it-works.md:153` names `spark/design/needs.py`. `developing.md:238` names the file `needs.py`, still right. `areas/design.md`, `areas/core.md` and `areas/sourcing.md` (it said `needs.py` imports `design`, now `loader`) follow. `map.py --write` |
| 12 | the map of the guard move's commit | build | closed | `map.py --write` ran in the move's commit, so `text_guards`' docstring row is one commit late. The branch's head is green — P776: stale note: One commit late map row. |
