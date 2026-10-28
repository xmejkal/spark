# P385 #494: what plan v1 says that the code no longer holds

Base commit d064a65 (2026-10-25). Plan v1 is `docs/discovery/2026-10-19-p323-target-architecture/architecture/`, cited at
`17708e6`. This page has three sections. Section 1 lists the claims that are untrue or not built yet. Section 2 counts the cites
that moved. Section 3 maps each bullet of the nine comments on #494 to an item of the approved plan. The
"today" column is one of: moved, renamed, gone, not built yet, true. Put "true" only where a note is needed.

How it was checked. `tools/factcheck.py` was run on every page. Each run ended with `0 broken reference(s)`, because the
tool only sees a missing file or a line past the end. It cannot see a cite that points at the wrong line. So each cite
was also compared by the text of its line at the base commit of its page (`17708e6` for plan v1, `c4df11b` for P391,
`e569acd` for P322). Names were checked with `ast` over all tracked `.py` files.

## 1. Names and claims that are no longer true

### Stage 1 and decision 3

| page | claim | today | evidence |
|---|---|---|---|
| refactor-plan.md (summary box, stage table, heading "Stage 1: the bench net, before walk 2") | Stage 1 is two PRs before walk 2 on 2026-10-27 | gone | Walk 2 ran by 2026-10-23 (`docs/observations/2026-10-23-p400-walk2-council/`). S1 merged as P380 #487, PR #492. S2 is not built. |
| refactor-plan.md (decision 3, stage table "Waits on decision 3") | Open: (a) both slices merge by 2026-10-23, or (b) after walk 2 | gone | #413, the PO, 2026-10-21: S1 before walk 2, S2 and every later stage after it, one PR at a time. The reason: do not break the system before MVP. Decisions 1, 2 and 4 stay open. |
| refactor-plan.md (after the stage diagram) | "Stage 1 goes first, because walk 2 runs on the bench" | gone | Walk 2 ran. Stage 2 waits on decisions 1 and 2. |
| README.md ("Your call" 3, summary box) | Walk 2 is due 2026-10-27. The bench goes first for walk 2 | gone | Same as above. |
| notes.md (conflicts table) | "0a only if it merges by 2026-10-23" | gone | Decision 3 is answered. |
| areas/bench.md (line 4) | The bench area moves first, because walk 2 runs on it | gone | Decision 4 (when area moves start) is still open. |
| refactor-plan.md S1 "Files" | Test helper `tests/golden.py` with `--accept OP` | renamed | `tests/golden_bench.py`. The switch is the variable `SPARK_ACCEPT=<op>`. |
| refactor-plan.md S1 "Files" | Fixture `tests/data/projects/bench-c6/`, a C6 board | gone | `golden_bench.py` builds the project at test time. `BOARD_ID` is `firebeetle2-esp32s3`. |
| refactor-plan.md S1 "Goal" | "`tests/golden/` does not exist" | gone | It holds 13 files (11 json, 2 txt). |
| refactor-plan.md Stage 1 "Done when" | `ls tests/golden/*.json` counts at least 12. `grep -L '"code"'` prints nothing | gone | 11 json files. No golden has a `code` key, so the grep lists them, because S2 is not built. |
| refactor-plan.md S1 "Goldens" | Look bad flag, look ok with `--no-simulation`, deploy gate closed, deploy ready seen, deploy bad flag | not built yet | `CASES` in `golden_bench.py` has 13 Cases. Deploy has only dry run (json, txt) and `could-not-run-no-terminal`. Look with `--no-simulation` is `could-not-run`. |
| refactor-plan.md S2 | `board_codes.py`, a `code` at six item sites, `fix_step`, `needs_person`, top-level `backends`, a `bad_argument` parser | not built yet | `git grep` finds none of these in `scripts/`. |
| refactor-plan.md S3 to S13, core.md, all proposed names | `scripts/spark/`, `test_architecture.py`, `architecture_baseline.json`, `tools/measure.py`, `--retarget`, `tools/map.py`, `docs/guide/map.md`, `slow_test_*`, `OutsideWorld`, `Backends`, `Operation`, `OperationResult` | partly built | `tests/test_architecture.py`, `tests/architecture_baseline.json`, `tools/measure.py` and `mutate.py --retarget` exist since P440 (2026-10-28). The rest of the names does not exist yet. |

### Names the comments mention

| page | claim | today | evidence |
|---|---|---|---|
| bench.md, plan "Into bench", S11 | `LookStopError` | not built yet | Today `LookStop` (`board_look.py`, class at :53). The rename is a planned S11 step. |
| firmware.md, plan "Into firmware" | `RunLog` and `status_of_run` | not built yet | `run_scenario.run_record` builds a dict. `verdict` stays. |
| firmware.md | "`ScenarioSteps` (in `run_scenario`)" | true, target home not built | `run_scenario.ScenarioSteps` exists (:100). The components table gives it no module. Comment 4 wants a small module beside `RunLog`. |
| none (comment 4) | `Brief` in the setup area | not built yet | Two readers remain in `parts.py`: `vendor_order` and `sellers`. A `parts._brief` exists with another meaning (a one-line summary of a part). |
| none (comments 4, 5) | `DeployEntry` | not built yet, out of the plan | `LastDeploy` (`board_facts.py`) is the Value. `record_deploy` still writes a dict. |
| none (comments 4, 5) | `DeployedStore` | not built yet | Named in P391 `design.md` only. |
| none (comment 4) | `ONBOARD_NAMES`, `ONBOARD_VERBS` | gone | `boards.ONBOARD_ROLES`, a tuple of `OnboardRole` (constant, scenario_verb, does, what, not_in_diagram). |
| none (comment 7) | `sim_project.NO_PART_IN_DIAGRAM` | gone | Field `OnboardRole.not_in_diagram`. Comment 8 drops the bullet. |
| bench.md, glossary.md | module `ready_probe`, `ReadyProbe`, `make_ready_probe` | not built yet | Today `ready_check.py`, `ReadyCheck`, `FirmwarePlatform.make_ready_check`. |
| plan "Into records" | `boards.py` holds `load`, `ButtonPlaces`, `BoardError`, `validate`, `REQUIRED_KEYS`, `footprint_stop` | true, but grown | 843 lines now. Adds `OnboardRole`, `ONBOARD_ROLES`, `POWER_FUNCTIONS`, `SimulatedPart`, `read_simulated_part`, `WOKWI_DEFINITION` and the readers. MVP spans :330-465 and :489-566. |
| all area pages | (no mention) | true, unnamed | New and on no page: `LastDeploy`, `zone_time`, `screen_text`, `provenance`, `onboard_limits`, `write_limits`, `ImageEvidence.caveats`, `emit_footprint.why_no_footprint`, `check_spine.NO_FOOTPRINT_HINT`. |

### Counts and sizes

| page | claim | today | evidence |
|---|---|---|---|
| refactor-plan.md (title) | "five stages, sixteen slices" | gone | 14 are listed: S1 to S13, with S7a and S7b. |
| refactor-plan.md | 2,817 tests. 1,999 mutation rows | moved | 3,171 test cases load (`unittest` discover, `countTestCases`). 2,010 mutation rows. The 217 bench rows still hold. |
| refactor-plan.md S11, appendix | 31 files import a bench module. 16 modules hold 2,164 lines | moved | 34 files with the same grep on 15 modules. 2,266 lines. |
| refactor-plan.md, areas | `check_spine.run` is 192 lines at :347-538. `parts.validate` is 240 lines | moved | `check_spine.run` is 204 lines at :353-556. `parts.validate` is 230 lines at :631. |
| refactor-plan.md, areas | Sizes: `emit_board.py` 1172, `emit_footprint.py` 243, `sim_project.py` 201, `image_evidence.py` 176, `drawer.py` 421, `needs.py` 655 | moved | 1176, 251, 256, 199, 427, 669. |
| core.md | `COMMON_ARGUMENTS` holds `--describe` and `--debug`, and a crash traceback shows only with `--debug` | gone (page conflict) | Plan S5 says "No `--debug` flag". "What we will not do" says no `--describe` and no `--debug`. |
| sourcing.md | "The goldens of S15 run every `parts.py` Operation" | gone | The plan has no S15. Stage 5 holds the goldens of each area. |
| glossary.md | `STAGE_*` at `board_envelope.py:23` | moved | :26. |

### P391 `design.md`

| page | claim | today | evidence |
|---|---|---|---|
| design.md stage 1 | Boards go onto the shelf (P390) | not built yet | P390 #505 is open. `tests/test_store.py` still pins `store.layers("boards")` to project and library. |
| design.md section 3 | `RecordKind`, `PartRecordKind`, `BoardRecordKind`, `Record`, `RecordFinder`, `ShelveRecord`, `scripts/records.py`, `boards.chosen` | not built yet | None exists. P391 `Record*` names clash with plan v1's `Records`, `RecordFolders`, `RecordSchema` and area `records`. |
| design.md stage 4 and question 5 | P389's onboard parts "enter the board contract here". "Stage 4 waits for P389" | gone | P389 merged (#528, #530). `ONBOARD_ROLES`, `POWER_FUNCTIONS` and `SimulatedPart` are in `boards.py`. |
| design.md stage 4 | Wokwi definition as a `documents` source under its sha256 (comment 4) | not built yet | The text is not in the file. |
| design.md section 5 | `boards.validate` is `boards.py:340-503`, 160 lines | moved | `validate` is at :569 and 172 lines. |
| design.md section 4 | Wokwi part `mcu` at `check_spine.py:555` | moved | :572. Comment 4 said :560 on 10-24, and P407 moved it again. |

### P322 `facts.md` (a dated measurement, so only reported)

| page | claim | today | evidence |
|---|---|---|---|
| facts.md | Score: classes 16%, roles 56/103. 59 modules, 14,313 code lines, 103 classes, 647 functions | moved | `measure.py` today: classes 17%, roles 63/110. 63 modules, 15,014 lines, 110 classes, 668 functions. Fat 3, thin 4, private imports 3 and literals 10 are unchanged. |
| facts.md | `deploy.main` is 28 lines. `check_spine.run` 192. `parts.validate` 240. `boards.validate` 161. `emit_board.main` 115 | moved | 33, 204, 230, 172, 117. 35 library modules are now 39. |

## 2. Moved cites

Factcheck says `0 broken reference(s)` on every page. "Stale" is a cite whose line text no longer sits at the cited
line. "Distinct cites" counts each `file:line` once.

| page | distinct cites | stale | five worst (cite, now) |
|---|---|---|---|
| refactor-plan.md | 143 | 43 | `boards.py:595` (:832), `boards.py:340` (:569), `tests/test_needs.py:1416` (:1575), `run_scenario.py:252` (:353), `run_scenario.py:124` (:219) |
| P391 design.md | 77 | 37 | `boards.py:340` (:569), `boards.py:502` (:739), `tests/test_needs.py:1406` (:1528), `assign_pins.py:461` (:484), `check_spine.py:555` (:572) |
| areas/build.md | 14 | 10 | `tests/test_needs.py:1416` (:1575), `check_spine.py:767` (:788), `:635` (:656), `:509` (:527), `:432` (:450) |
| areas/design.md | 8 | 5 | `boards.py:236` (:247), `emit_footprint.py:208` (:219), `assign_pins.py:392` (:396), `assign_pins.py:113` (:117), `check_all.py:406` (text gone) |
| areas/firmware.md | 10 | 4 | `run_scenario.py:124` (:219), `run_scenario.py:171` (:266), `sim_project.py:157` (:212), `run_scenario.py:212` (several matches) |
| P322 facts.md | 15 | 7 | `boards.py:340` (:569), `deploy.py:126` (:141), `parts.py:621` (:631), `check_spine.py:347` (:353), `deploy_service.py:69` (:57) |
| glossary.md | 25 | 4 | `parts.py:230` (:240), `parts.py:238` (:248), `emit_footprint.py:236` (:244), `board_facts.py:35` (:39) |
| areas/core.md | 6 | 3 | `run_scenario.py:249` (:350), `assign_pins.py:113` (:117), `parts.py:1672` (:1674) |
| areas/records.md | 12 | 3 | `boards.py:553` (:790), `run_scenario.py:249` (:350), `boards.py:592` (two matches) |
| areas/sourcing.md | 6 | 2 | `parts.py:130` (:136), `parts.py:1581` (:1583) |
| notes.md | 7 | 2 | `run_scenario.py:249` (:350), `parts.py:230` (:240) |
| areas/bench.md | 25 | 1 | `board_look.py:296` (:308) |
| README.md, areas/breadboard.md, areas/checks.md | 3, 11, 5 | 0 | none |

Some cites were wrong when written. Factcheck cannot see them. A check of the name next to the cite at `17708e6` found:

- `bench.md` `board_console.py:80` (`SystemClock` is :83) and `:86` (`ConsoleProbe` is :89).
- `bench.md` `board_doctor.py:160` and `:162` (the two lookups are :162 and :164).
- `glossary.md` `board_doctor.py:74` (`BoardCheckStrategy` is :76) and `:188` (`describe` is :190).

The plan itself cites :162, :164 and :76, so the pages disagree with each other.

## 3. The comments, mapped

Comments 10 and 11 carry no plan change and are left out. Items are those of the approved plan, "What plan v2 adds to v1".
Items 9 and 10 have no comment behind them. Item 9 comes from the card body and item 10 from #413.

| comment (date) | bullet (first words) | plan item | note |
|---|---|---|---|
| 1 (10-22) | the pruning list names each module's MVP part and later part | 8 | Also the MVP span columns of `pruning-list.md` (outputs table). |
| 1 (10-22) | the plan marks them with `# --- MVP ---` and `# --- Later, not MVP ---` | 8 | |
| 1 (10-22) | each card also marks the code it touches | none | Asks for a habit per card (the per-card sweep). It is already in the rules file. |
| 2 (10-22) | each Operation exports its arguments and result as JSON Schema | 4 | The comment calls it "item 3 of this card". The numbers differ from the plan's. |
| 2 (10-22) | no Operation asks or prints, consent is an argument or a grant | 4 | |
| 2 (10-22) | the runner's one hook is where a tracer plugs in | 4 | |
| 2 (10-22) | a Retriever port over parts and datasheets | 4 | |
| 2 (10-22) | LangGraph, LangChain, Langfuse only in an optional adapter | 4 | |
| 2 (10-22) | after walk 2, one learning spike (build as a LangGraph node and MCP tool) | 4 | Item 4 makes it a proposed card. |
| 2 (10-22) | Models: design and final check on the best model | none | Asks for a process. Plan steps 3 and 6 carry it, no item does. |
| 3 (10-23) | when: after walk 2's cards are built | none | Asks for timing. P397, P399, P345 PR 2 and P374 are still open. The PO pulled P385 on 10-25 (comment 10). |
| 3 (10-23) | up to date: plans checked against the code that landed | 11, 12 | Item 11 is the cites. Item 12 covers P391 and P322. This page is the name check. |
| 3 (10-23) | the bar: reuse, defined interfaces, solid OO, clear names, no slop | 1 | |
| 3 (10-23) | levels: 2 to 4, the same rules on each, top-down and bottom-up | 2 | |
| 3 (10-23) | proposed Done-when: the levels, one diagram per level, a home per new class | 2, 7 | Item 2 draws the four levels on one worked area. |
| 4 (10-24) | new code the plans do not name (`SimulatedPart`, `read_simulated_part`, `WOKWI_DEFINITION`, `onboard_limits`, `ImageEvidence.caveats`) | 7 | `ONBOARD_NAMES` in this bullet is gone (section 1). |
| 4 (10-24) | `ScenarioSteps` gets its own small module beside `RunLog` | 7 | |
| 4 (10-24) | name the edge: `image_evidence` imports from `run_scenario` | 5 | The import exists (`image_evidence.py`, top level). |
| 4 (10-24) | names under another name: `LookStopError`, `RunLog`, `status_of_run`, `DeployEntry`, `DeployedStore`, `Brief`, `OutsideWorld` | 7 | Item 7 names only `LookStop`, `RunLog`, `ScenarioSteps`, `Brief`. |
| 4 (10-24) | one onboard role table in `boards.py` so displays and chargers extend it | 7 | Item 6 holds the five role tables. |
| 4 (10-24) | P391 `design.md`: stage 4 names the Wokwi definition, stale cites | 12 | |
| 5 (10-24) | `DeployEntry` is not needed, `LastDeploy` is the Value | 7 | Item 7 does not say the name comes out. |
| 5 (10-24) | `zone_time` is a leaf, no module imports upward | 5 | |
| 5 (10-24) | `read_last_deploy` on the store side, `LastDeploy.line()` on the look side | 6 | Both sit in `board_facts.py` today. |
| 5 (10-24) | one "not checked" template, `LastDeploy` | 6 | Users: `LastDeploy`, the `SimulatedPart` reader (P397), `ScenarioSteps`. |
| 5 (10-24) | one home for the two cleaners | 3 | Revised by comments 6 and 7 (the home grows to three guards). |
| 6 (10-25) | one print edge for all scripts, the body of `parts._say` | 6 | |
| 6 (10-25) | two cleaners, one home `screen_text.py`, so `matching` drops `drawer` | 3 | Revised by comment 7. `matching.py` still imports `drawer`. |
| 6 (10-25) | leaves `zone_time` and `screen_text`, one test over every leaf | 5 | One leaf test exists, for `screen_text` only. |
| 6 (10-25) | one fact, two readers: the asking project's name | 6 | Two names and each call site. |
| 6 (10-25) | `drawer.holders_of` is the one stock reader | 6 | |
| 7 (10-25) | `ONBOARD_NAMES` and `ONBOARD_VERBS` gone, the readers of `ONBOARD_ROLES` | 7 | Target: beside `SimulatedPart`. |
| 7 (10-25) | `provenance.py` is a third leaf | 5 | It imports no module. |
| 7 (10-25) | three text guards, a home name for all three outlets | 3, 5 | `assign_pins` reaches `parts.one_line`. |
| 7 (10-25) | `NO_PART_IN_DIAGRAM` is a second table | none | Dropped by comment 8. |
| 7 (10-25) | `parts` imports `boards` in four functions, say if it stays lazy | 5 | Both ways are lazy and `boards` imports `parts` back (two sites). |
| 8 (10-25) | drop the `NO_PART_IN_DIAGRAM` bullet, the board-record area list, the two MVP spans | 7, 8 | Also the pruning list ("first split candidate"). |
| 8 (10-25) | name clash: "fact value" (three), "power" (four), one reader for a board's fact | 3, 6 | |
| 8 (10-25) | two fact rules, two homes: `provenance.fact_problems` and `is_fact_value` | 6 | |
| 8 (10-25) | one role spelled in five tables, waits for P405 | 6, 9 | P405 #529 is open. |
| 9 (10-25) | new names `why_no_footprint`, `NO_FOOTPRINT_HINT`, `REFUSED_INPUT_MESSAGE` | 7 | Footprint area. |
| 9 (10-25) | the order of refusals is written twice, one function | 6 | |
| 9 (10-25) | the footprint stop is worded in three places | 5 | P411 #537 says four spellings. Item 5 says three. |
| 9 (10-25) | the spine calls the rendering code, not `emit_footprint.main` | 6 | |

Bullets in the table: 42. Mapped to no item: 4 (comment 1 third bullet, comment 2 models, comment 3 when, comment 7 `NO_PART_IN_DIAGRAM`).
