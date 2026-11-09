# P709 area names: rows

The classes take the area pages' names, and every exception name ends in Error (rule C1). Renames only: behaviour,
printed text, exit codes and JSON keys stay. Card: [P709 #956](https://github.com/xmejkal/spark/issues/956).

The reference counts are `grep -w` hits on b13c1b77: scripts (files/hits), tests, mutation tables.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `NotDrawn` becomes `NotDrawnError` | brief, areas/breadboard.md:6 | acted | defined `breadboard/drawing.py:70`; 6/36, tests 24, 1 table; C1 and R6 keys; no golden holds it; done in f23de7ee |
| 2 | `NotBuilt` becomes `NotBuiltError` | brief, areas/breadboard.md:6 | acted | `breadboard/sheet.py:59`; 2/15, tests 8, 1 table; a C1 key; done in f23de7ee |
| 3 | `CouldNotKeep` becomes `CouldNotKeepError` | brief, areas/checks.md:6 | acted | `checks/vendor_pins_check.py:172`; 1/6, tests 0, 2 tables; C1 and R6 keys; done in f23de7ee |
| 4 | `BadArgument` becomes `BadArgumentError` | brief | acted | `core/outcomes.py:132`; 3/7, tests 1, 1 table; C1 and R6 keys. The code `bad_argument` and `render_bad_argument` stay; done in f23de7ee |
| 5 | `RefusedInput` becomes `RefusedInputError` | brief | acted | `design/board_emitter.py:1065`; 4/8, tests 5, 2 tables; a C1 key. `REFUSED_INPUT_MESSAGE` stays; done in f23de7ee |
| 6 | `Impossible` becomes `ImpossibleError` | brief, areas/design.md:6 | acted | `design/pin_assigner.py:115`; 5/23, tests 29, 6 tables; a C1 key. `tests/golden_design.py:127` names it in a comment, no golden file does; done in f23de7ee |
| 7 | `StoreProblem` becomes `StoreError`, not `StoreProblemError` | decision | acted | `records/store.py:155`; 17/48, tests 42, 11 tables. "Problem" and "Error" say the same role twice; the store is the subject, as in `DeployError`; done in f23de7ee |
| 8 | `ToolProblem` becomes `ToolError`, not the page's `ToolMissingError` | decision, areas/records.md:6 | acted | `records/tool_finder.py:52`; 24/84, tests 81, 12 tables. It is raised for a broken tools file, a failed install and a contract not met too (`records_codes`), so "missing" would lie; done in f23de7ee |
| 9 | `UnknownMatcher` becomes `UnknownMatcherError` | brief, areas/sourcing.md:7 | acted | `sourcing/matching.py:34`; 3/6, tests 1, 0 tables; C1 and R6 keys; `tools/match_eval.py:104` names it in a comment; done in f23de7ee |
| 10 | `NoTranscript` becomes `NoTranscriptError` | brief, areas/sourcing.md:7 | acted | `sourcing/run_cost.py:48`; 3/12, tests 2, 1 table; C1 and R6 keys; done in f23de7ee |
| 11 | a renamed exception's class name is printed only on a crash path | check | verified | `check_spine.py:181`, `check.py:90`, `cli.py:77`, `deploy_image.py:287` and `build_service.py:43` print `type(x).__name__`; no golden under `tests/golden*` holds any old name |
| 12 | `Step` becomes `WiringStep`, typename too | brief, areas/breadboard.md:6 | acted | `breadboard/wiring_steps.py:39`, a namedtuple; 1/9, tests 0, tables 0. Its repr is printed nowhere; done in 6bc2c348 |
| 13 | `WiringRecord` becomes `WiringLog` | brief, areas/breadboard.md:6 | acted | `breadboard/bench_changes.py:103`; 3/8 (with `outcomes.py:45`), tests 15, tables 0. `FILE_NAME` stays `wiring-record.json`; done in 6bc2c348 |
| 14 | the five check classes take the page's names | brief, areas/checks.md:6, :32-36 | acted | `checks/check.py:116-259`: `RulesVsNetlist` to `RulesCheck`, `Physics` to `PhysicsCheck`, `Buildability` to `BuildCheck`, `VendorTruth` to `VendorPinsCheck`, `TheOrder` to `OrderCheck`; R6 keys move. The check names (`vendor-truth` and the rest) are printed and stay; done in 691be01a |
| 15 | `is_fact_value` becomes `is_pin_map_constant` | refactor-plan.md:217 | acted | `records/board_records.py:586`; 2/5, tests 1, 1 table (`p353-onboard-roles.json`); done in 89e94eaa |
| 16 | `fact_value_problems` becomes `board_fact_problems` | refactor-plan.md:217 | acted | `records/board_records.py:593`; 1/3, tests 0, tables 0; done in 89e94eaa |
| 17 | `_brief` becomes `_part_summary` | refactor-plan.md:222 | acted | `sourcing/part_handlers.py:111`; 2/4 (`goal_handlers.py` imports it), tests 0, tables 0; done in 89e94eaa |
| 18 | the power renames | refactor-plan.md:218 | closed | they wait for #529 (P405), as the card says |
| 19 | not a rename: `PinAssigner` needs Extract Class | areas/design.md:75 | raised | no class exists; it would hold `pin_assigner.assign` and its helpers `candidates`, `capability_of`, `roles_of`, `_cost`, `_why_not` |
| 20 | not a rename: `PinMap` needs Extract Class | areas/design.md:79 | raised | `assign` returns plain assignments and leftovers; a Value would hold them with `render` and `pin_module` |
| 21 | not a rename: `BoardEmitter` needs Extract Class | areas/design.md:86 | raised | `board_emitter.py` holds about fifty functions (`place`, `header_lines`, `signal_lines` and the rest); `BoardInputs` is another thing |
| 22 | not a rename: `NeedsService` needs Extract Class | areas/design.md:90 | raised | `needs.py` holds `match`, `offer`, `plan_pick` and `plan_set` as functions |
| 23 | not a rename: `BuildInputs` needs Extract Class | areas/build.md:57 | raised | `build_service.run` takes its inputs as arguments (`requirements`, `workdir`, `toolchain`, `project`, `firmware`) |
| 24 | not a rename: `ProjectSetupService` needs Extract Class | areas/build.md:31 | raised | `project_setup.py` holds `rules_for`, `write`, `merged`, `design_in` and the rest as functions |
| 25 | not a rename: `TscircuitEngine` needs Extract Class | areas/build.md:41 | raised | `board_engine.py`'s `find_toolchain`, `toolchain_can_build`, `tsci_version` and `modules_for` |
| 26 | not a rename: `DiagramConverter` needs Extract Class | areas/build.md:42 | raised | `board_engine.py`'s `find_converter`, `converter_command`, `converter_stage_problem` and `convert` |
| 27 | the docstring at `part_handlers.py:4` says `vendor_order` and `sellers` wait for `Brief`'s card | brief | acted | `part_handlers.py:37-44` already read `Brief.from_project(project)`, so the card is done in substance; done in the docstrings commit; row 28 needed no change |
| 28 | a docstring says a class renamed here "comes with its card" | brief | verified | none does: the five such docstrings name `ToolFinder`, `BuildService`, `RunCostService`, `DatasheetService` and the Operations, which are not renames |
| 29 | renaming a class moves its R6 key, so the baseline takes the new key at the equal value | check | acted | `--accept-new`, a rename: ten R6 keys moved (five exceptions, five checks), ten C1 keys went, no value rose |
| 30 | 114 mutation rows are refused by `--anchors` | check | raised | the same 114 rows are refused on b13c1b77 (`git archive` copy, the lists diff empty), so none comes from P709; a later sweep re-anchors them |
| 31 | the records page names `ToolMissingError` and `ToolFinder` for `tool_finder` | areas/records.md:6 | raised | `ToolError` is the class today (row 8); `ToolFinder` needs Extract Class over `tool_finder.find` and its helpers |
| 32 | `patterns-and-names.md` said only the deploy area uses the Error suffix | check | acted | the role table and the names list now say every exception ends in Error, held by rule C1 |
