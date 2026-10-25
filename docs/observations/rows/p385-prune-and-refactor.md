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
| 13 | `tools/factcheck.py` exiting 0 proves the cites are true (the plan's verification) | drift reader | acted | it does not: it finds only a missing file or a line past the end. Every page gave `0 broken reference(s)`, while a compare of each cited line's text at the page's base commit against today found 43 of 143 stale in `refactor-plan.md` and 37 of 77 in P391's `design.md`. Step 4 compares line text, not only factcheck |
| 14 | Plan v1's pages agree with the code and each other | drift reader | raised | 40 untrue or not-yet-built claims in `drift.md` section 1. Some cites were wrong when written (`bench.md`, `glossary.md`). `core.md` lists `--describe` and `--debug`, which S5 excludes. `sourcing.md` cites S15, which the plan no longer has. The title says sixteen slices and lists 14 |
| 15 | S1 was built as planned | drift reader | raised | the harness is `tests/golden_bench.py`, the accept switch is `SPARK_ACCEPT`, there is no fixture folder, and 11 goldens exist against "at least 12". Deploy has no golden for a closed gate, a ready-seen run or a bad flag. Plan v2 describes S1 as built |
| 16 | P391's record names agree with plan v1 | drift reader | raised | P391's `RecordKind`, `RecordFinder` and `records.py` clash with v1's `Records`, `RecordFolders`, `RecordSchema` and the area `records`. Plan v2 item 3 names one set |
| 17 | `Brief` is a free name | drift reader | raised | `parts._brief` exists and does another job. Plan v2 item 3 |
| 18 | The only lazy edge is `parts -> boards` (comment 7) | drift reader | raised | `boards` and `parts` import each other lazily, a cycle. Plan v2 item 5 |
| 19 | Every comment bullet maps to a plan item | drift reader | raised | 4 of 42 map to none: "each card marks the code it touches" (goes to item 8), "Fable for design and final check" (a process rule the plan already follows: closed), "after walk 2's cards are built" (goes to item 10), `NO_PART_IN_DIAGRAM` (comment 8 drops it: closed) |
| 20 | The footprint stop is worded in three places (comment 9) | drift reader | raised | P411 #537 counts four spellings. Plan v2 item 5 takes P411's count |
| 21 | Item 7 names every deploy class change | drift reader | raised | it leaves out the removal of `DeployEntry` (comment 5) and does not name `DeployedStore` or `OutsideWorld`. Plan v2 item 7 |
| 22 | Each leaf has an import test | drift reader | raised | only `screen_text` has one. `zone_time` and `provenance` have none. Plan v2 item 5 |
| 23 | `Brief` belongs in the setup area (comment 4) | Fable, plan v2 | raised | plan v2 puts it in `records`, because `sourcing` would import upward from setup. The council checks |
| 24 | Stage 2 edits each file once | Fable, plan v2 | raised | stage 2 edits flat scripts (`board_facts`, `screen_text`) that stages 5 and 6 move again: a double touch |
| 25 | `text_guards` is a text-only leaf | Fable, plan v2 | raised | it takes `drawer`'s field caps (`LABEL_MAX`, `TEXT_MAX`, `TAGS_MAX`), which are record limits |
| 26 | Every helper name follows the verb rule | Fable, plan v2 | raised | `printable` and `one_line` bend it. Left to P382 #489 |
| 27 | The power renames can land now | Fable, plan v2 | raised | `POWER_FACT_FUNCTIONS` and its siblings rename before P405 #529 gives its finding. It can be premature |
| 28 | `RecordKind` follows P391's design | Fable, plan v2 | raised | it takes `version` and `required`, which P391's design lacks. Its author checks |
| 29 | The area pages' links still work | Fable, plan v2 | raised | nine area pages link `#into-<area>`, which v2 removed. Step 4 fixes them. `check_docs` does not gate discovery pages |
| 30 | `outcomes` is the home of `RECORDED`, `NONE_RECORDED` and `NOT_CHECKED` (slice OC4) | Fable, plan v2 | raised | it can be the wrong home. The council checks |
| 31 | S2's goldens are easy | Fable, plan v2 | raised | the closed-gate and ready-seen goldens need the fake esptool to reach an erase. V1 called it the hardest fixture |
| 32 | `Operation.schema()` types each result | Fable, plan v2 | raised | the shape of each Operation's data is untyped today, so the result schema is loose |
| 33 | One trace callable after each call serves Langfuse | Fable, plan v2 | raised | it gives no spans, and Langfuse can need a start and an end |
| 34 | `tools/match_eval.py` is reached by nothing | Fable, plan v2 | raised | it has a test, and `matching.py`'s docstring names it. The prune verdict rests on `Inventory`'s pages only (row 4) |
| 35 | Each verdict is one PR | Fable, plan v2 | raised | the PCB checks' move is two steps: the marker now, the module later |
| 36 | `tests/.mapping-under-test.json` belongs in git | Fable, plan v2 | raised | a test writes it, and it is tracked (row 9). Reported, not acted |
| 37 | Plan v2's numbers are measured | Fable, plan v2 | raised | some (`check_spine.run` 204 lines, and others) come from `drift.md`, not a new count. Step 4 re-measures |
| 38 | `--fact-set` maps to `_set_in_home` | Fable, plan v2 | raised | read from names, not from the body. Step 4 reads it |
| 39 | Plan v2 gives an order for the verdict groups | lessons writer, Opus | raised | it does not. Lesson 1 takes the order that proposed card 2 and the pruning list imply, so the plan must state the pick |
| 40 | The learning spike can run after stage 3 (proposed card 1) | lessons writer, Opus | raised | a contradiction: it runs "the build Operation", and the build becomes an Operation only in stage 6. After stage 3 only `look` is on the core |
| 41 | Plan v2 says what each test lane runs | lessons writer, Opus | raised | it gives only the 90 s check at stage 5, and not what the fast and slow lanes run |
| 42 | Every Claude Code form in lesson 5 has a tracked file | lessons writer, Opus | raised | the session-start hook is not in the repo, and the plugin ships no `hooks/` folder |
| 43 | Plan v2 counts the `mock.patch` lines | lessons writer, Opus | raised | `tests/test_deploy_gate.py` has 14, and 49 test files hold 361. The plan gives neither number |
| 44 | Plan v2 says how the five role tables bear on decision 1 | lessons writer, Opus | raised | section 6 names them as lesson 3's input and gives no link to decision 1. The lesson links them through "a reader finds the role in one row" |
| 45 | Plan v2's cites and counts are true | cite checker, Sonnet | acted | about 35 fixes: 15 in "Changes for the area pages", about 14 in the body, 6 in the verdicts. Re-measured: S4 36 import lines in 32 files, S11 16 modules and 35 files, P391 stale cites 50 of 95, `check_spine.run` 23 return sites, `emit_board.py` 1,176 lines. `_set_in_home` writes both `--fact-set` and `--function-set` and replaces keys whole, so P374 needs a merge into `facts` (row 38) |
| 46 | The area pages link to anchors that exist | cite checker, Sonnet | acted | every `#into-<area>` link now points at `#appendix-what-moves-where-by-name`. 73 links, 20 into `refactor-plan.md`, 0 bad. Two older home paths in P323's council pages were removed |
| 47 | Level 4 of plan v2 draws today's call order | cite checker, Sonnet | raised | the diagram has the Operation call the gate, and today `DeployService.deploy` does. A note was added, and the design is the council's to judge |
| 48 | Stage 2 leaves no module importing one above it | cite checker, Sonnet | raised | `matching` and `assign_pins` keep other `parts` imports until stage 6. The council judges whether stage 2's goal stands |
| 49 | Every module that serves only a pruned one has a verdict | cite checker, Sonnet | raised | `tests/matching/` (27 files) serves only `match_eval`, and no verdict names it |
| 50 | `drift.md`'s counts are current | cite checker, Sonnet | closed | it says 37 of 77 and 34 files, as measured in step 2. Row 45 holds the new counts, and `drift.md` stays as its run gave it (rule 3.2) |
| 51 | The patch counts on the area pages are current | cite checker, Sonnet | raised | `build.md` "6 and 7 patches" and `records.md` "about 39 patches" were not re-measured. A count gives 37 now |
