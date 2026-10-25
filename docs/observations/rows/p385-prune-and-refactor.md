# P385: the pruning list, a draft PRUNED.md and the refactor plan v2, findings rows

Findings from the plan councils and the agents of spike P385 #494 (2026-10-25, Prague). The plan is approved, and each
step adds its rows here.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan for the spike has no gap | plan council round 1, Sonnet | acted | 15 gaps: wrong walk records, open cards P397 and P399 missing, eight comment bullets with no plan line, three names for the card, columns that differ from `inventory.py`, a council of no allowed size, a circular check. All 15 fixed in the plan before approval |
| 2 | Round 1's fixes leave no new gap | plan council round 2, Sonnet | acted | 8 gaps: a substring walk match, walk columns that prove nothing, `factcheck.py` reads no tables, a comment map to a plan not yet written, six more unmapped bullets, mechanical work given to Fable, an unchecked council size, names without a role. All 8 fixed in the plan before approval |
| 3 | `Inventory` counts "named by" with whole names | measurer | raised | it counts a substring, so a page that names `emit_board.py` also names `board.py`. Five modules differ from a whole-name count: `tools/board.py` 10 against 2, `design.py` 4 against 2, `cost.py` 4 against 3, `flash_image.py` 6 against 5, `live.py` 6 against 5. The fact table uses `Inventory`'s count, as the plan says. A candidate for the prune of `tools/` |
| 4 | `Inventory` reads every page that names a script | measurer | raised | it reads no `AGENTS.md` and no docs outside `docs/guide/`. `tools/journey.py` shows as reached by nothing, but `AGENTS.md` names it and tests run it. The verdict for it must not rest on that column |
| 5 | `Inventory` sees every module | measurer | raised | it skips subfolders, so `scripts/stand_in/machine.py` is not in its list. A test loads it by path, and `pyproject.toml` lists it. The fact table has a row for it from `git ls-files` |
| 6 | Every library has a test | measurer | raised | `scripts/zone_time.py` has `run by tests` 0, while two modules import it |
| 7 | The PCB and fab checks hold about 2,700 lines off the breadboard journey (card body, 2026-10-21) | measurer | raised | `copper.py` and `fab.py` look PCB-only, but `emit_board.py` (the build) imports them, and `emit_footprint.py`, `tabbed_page.py` and `netlist.py` are on the build path. Only `check_bom`, `check_footprints` and `check_physics` (1,417 lines) are off it. The verdicts use 1,417 |
| 8 | `run by tests` counts only real use | measurer | raised | it also counts a test file that names a script in a docstring, so it is an upper bound. The pruning list says so |
| 9 | The tracked lines of `tools/circuit-to-wokwi` are 24,159 | measurer | acted | true when counted as `wc -l` counts. `tests/.mapping-under-test.json` is tracked, has no final newline, and a test writes it. The bundle `dist/converter.mjs` holds 21,897 of the 24,159 lines |
| 10 | The two `validate` functions are short | measurer | raised | `parts.validate` is one 230-line function, and `boards.validate` is 172 lines. Input for the core contract lesson |
| 11 | The walk columns show what a walk used | measurer | acted | 44 of 76 rows are named in neither walk record, and the walk 2 diary names scripts by bare name. The plan already says that a walk column vetoes no verdict |
| 12 | The jobs of `parts.py` are measured | measurer | raised | the job groups are the measurer's reading of names and a few bodies. Fable checks them in step 3 |
