# The pruning list: facts for card P385

The measured facts about every tracked file under `scripts/` and `tools/`. Card
[#494](https://github.com/xmejkal/spark/issues/494), base commit `d064a65`. This file holds facts only. The
verdicts come later, from Fable 5.1, and a number here vetoes no verdict.

Rerun it from the repository root. The output must be the same, byte for byte:

    python3 docs/discovery/2026-10-25-p385-prune-and-refactor/pruning_facts.py --walk <the walk 2 diary>

A later walk adds one column in one step: `--walk <record>`, where the record is a file or a folder. The column is
named after the record. A record outside the repository prints only its file name and its sha256, never its folder.
The walk 2 diary lives outside the repository. Its sha256 is in the table's footer.

How to read the columns:

- `lines`: newlines in the tracked file, as `wc -l` counts them.
- `imported by`: how many `scripts/` and `tools/` modules import it, at the top or inside a function, then their names.
  `tools/inventory.py` finds them.
- `named by`: how many of the 40 pages that `tools/inventory.py` reads contain the file name. Inventory matches the
  text as a substring.
- `run by tests`: how many `tests/*.py` files import it or contain its file name. A name inside a docstring counts.
- `named in <record>`: whole-name mentions in the walk record. `board.py` does not match `emit_board.py`.
  A mention inside a folder path counts only for the module's own folder.

## The verdicts

Fable 5.1 wrote these on 2026-10-25 from the facts below and the code at `d064a65`. A verdict is one of four words.
"keep" means the module stays, whole or split later by its area's move. "split" means the refactor cuts it into modules
of one job each, named in plan v2. "move behind a module" means the code leaves the MVP path and stays reachable through
one plug-in point, and the tag `pre-refactor-2026-10-25` keeps it. "prune" means the code goes, and the tag keeps it. A
walk column alone decides nothing: `design.py` is named in neither walk record, and eight build modules import it.

Counts over the 76 rows: keep 68, split 4, move behind a module 3, prune 1.

### The groups

(a) Reached by nothing. `tools/journey.py`: keep. `AGENTS.md` names it and `tests/test_journey.py` runs it, so the
inventory's column is the gap (row 4), not the module. `tools/match_eval.py`: prune. No page names it, nothing imports
it, and two docstrings and the P211 papers only mention it. Its test `tests/test_match_eval.py` goes with it. The tag
keeps both. When a second matcher is tuned, they return. `scripts/stand_in/machine.py`: keep. `import_firmware.py`
runs a firmware on the Mac with it, and walk 1 named `import_firmware.py` four times.

(b) Flags no page names. The table measures modules, not flags, so the 19 flags get their verdict in the prune PR by one
rule. A flag that a test or a script passes gets its line on the script's page. A flag that nothing passes goes, and
`PRUNED.md` lists it. The five flags of `tools/match_eval.py` go with the module.

(c) The PCB and fab checks off the breadboard journey. `check_bom.py`, `check_footprints.py` and `check_physics.py`
(1,417 lines, tests 1,488): move behind a module. The plug-in point exists: `check_all.CHECKS`, a list of `Check`
subclasses (`TheOrder`, `Buildability`, `Physics`). The first step is the marker `# --- Later, not MVP: the PCB order,
P136 ---` over the three rows and the three modules. The second step, a card, moves the three subclasses into one module
that `CHECKS` reads. `copper.py`, `fab.py`, `netlist.py`, `tabbed_page.py` and `emit_footprint.py` stay with the build
(row 7: the build imports each).

(d) `scripts/parts.py`. The measurer's 15 job groups hold, with five corrections after a read of the bodies. `one_line`
and `COMMENT_UNSAFE`, with `SELECTOR_SAFE`, `FOOTPRINT_NAME`, `ENDS_THE_COMMENT` and `NOT_A_PLAIN_ID`, guard a word for a
generated file: their own job, and the leaf's in plan v2's OC8. `audit` walks every record of a project: its own job, the
`audit` Operation that moves to design. `without_location`, `keep_in_store` and `keep_local` keep a photo or a datasheet
in the store without its GPS data: one job, "keep a document", not shelving. `vendor_order` and `sellers` read the
project's brief: one job, the `Brief` Value. `describe` and `_row` describe the CLI for Claude (`--describe`): a
command-line job. That makes 18 jobs. The verdict is split, in the sourcing move of plan v2's stage 6. The record
contract goes to `RecordKind`, documents to `sourcing/datasheets.py` and shelving to `ShelveRecord`. The brief goes
to `records/brief.py`, the text guard to `text_guards.py`, the needs commands to design's Operations and the parser
to `run_cli`. `parts.py` stays the CLI.

(e) `tools/circuit-to-wokwi`: keep. The build runs `cli.ts` through the bundle `dist/converter.mjs` (21,898 of 24,159
lines), so a user installs no bun: free, few and local. The bundle is spark's own build product, not a vendor file, and
`bundle.sh` with `tests/test_check_spine.py` pins it to its sources' sha256. The lock file stays, because the bundle is
rebuilt from it. One finding for the prune PR: `tests/.mapping-under-test.json` is tracked and a test writes it (row 9).

(f) `scripts/boards.py`, the first split candidate: 843 lines, 60 names, 25 importers, `validate` alone 172 lines. The
cut follows the roles. `load`, `records`, `active_id`, `resolve`, `ButtonPlaces`, the onboard role table with its
readers, `SimulatedPart` and `read_simulated_part` go to `records/board_records.py`. The rules `role_entry_problems`,
`power_problems` and `fact_value_problems` become named rules of `RecordKind.validate`. `footprint_stop` goes to design.
`boards.py` keeps `main`, `get` and `_validate_all` as the CLI. Next in line: `emit_board.py` (1,176 lines),
`check_spine.py` (1,004) and `parts.py` (2,414), which is largest and goes last because its split is the sourcing move.

### The table

"all" means every top-level name of the module. "none" means no name.

| module | verdict | MVP span | later span | reason |
| --- | --- | --- | --- | --- |
| scripts/ai_files.py | keep | all | none | `init_project` imports it, `/spark:init` writes the AI files |
| scripts/assign_pins.py | keep | all | none | the build: `check_spine`, `emit_board`, `breadboard` import it |
| scripts/board_connection.py | keep | all | none | 7 bench modules import it |
| scripts/board_console.py | keep | all | none | 6 bench modules import it |
| scripts/board_doctor.py | keep | all | none | 7 importers. the look, deploy, live and reach run it on a failed read |
| scripts/board_envelope.py | keep | all | none | the `--json` of look and deploy |
| scripts/board_facts.py | keep | all | none | OC5 splits it into `DeployedStore` (records) and the look's line (bench) |
| scripts/board_grant.py | keep | all | none | the grant gates live and deploy, 6 importers |
| scripts/board_live.py | keep | all | none | `live.py`'s flow |
| scripts/board_look.py | keep | all | none | 8 importers, the look |
| scripts/board_reach.py | keep | all | none | `reach.py`, the PO's bench tool |
| scripts/boards.py | split | `load`, `records`, `active_id`, `resolve`, `ButtonPlaces`, `OnboardRole` to `read_simulated_part`, `is_gpio` to `power_problems`, `validate`, `get`, `main` | `REQUIRED_FOR_FAB` and the `for_fab` branch of `validate` (kept: the PCB checks read the fab keys) | group (f) |
| scripts/breadboard.py | keep | all | none | the sheet, which `check_spine --keep` writes |
| scripts/breadboard_changes.py | keep | all | none | `breadboard` imports it on every rebuild |
| scripts/breadboard_drawing.py | keep | all | none | 4 importers, the drawn breadboard |
| scripts/breadboard_keep.py | keep | all | none | the person's moves across a rebuild, a Strategy already |
| scripts/breadboard_match.py | keep | all | none | the drawing check, `breadboard` imports it |
| scripts/breadboard_steps.py | keep | all | none | 3 importers |
| scripts/check_all.py | keep | `Check`, `CHECKS`, `CheckedFolder`, `render`, `RulesVsNetlist`, `VendorTruth`, `main` | `TheOrder`, `Buildability`, `Physics` (kept: group (c)) | 11 pages name it, AGENTS.md's "checks the board" |
| scripts/check_bom.py | move behind a module | none | all (kept: the order check of a fab package, P136) | only `check_all` imports it, and no fab package exists |
| scripts/check_footprints.py | move behind a module | none | all (kept: "will this board be buildable", a PCB question) | `check_all` and `check_physics` import it, not the build |
| scripts/check_physics.py | move behind a module | none | all (kept: the PCB physics, P136) | only `check_all` imports it |
| scripts/check_spine.py | split | `run`, `main`, `board_alone`, `find_toolchain`, `toolchain_can_build`, `converter_command`, `simulation_detail`, `Stage` | none | 1,004 lines, `run` is 204. the build move splits it into `BuildService` and stages |
| scripts/check_vendor_pins.py | keep | all | `fetch_variant_header` and its `gh` run (kept: the network path of `VendorTruth`) | `check_all` imports it, 5 pages name it |
| scripts/compare_design.py | keep | all | none | `check_all` and `parts` import it |
| scripts/copper.py | keep | all | none | `emit_board` sizes a trace with it (row 7) |
| scripts/cost.py | keep | all | none | `parts.py --tally` and `--step`, the idea step's cost line |
| scripts/deploy.py | keep | all | none | the deploy, walk 2 named it 16 times |
| scripts/deploy_gate.py | keep | all | none | the only way to the erase, 5 importers |
| scripts/deploy_service.py | keep | all | none | the deploy flow |
| scripts/design.py | keep | all | none | 8 build modules import it |
| scripts/download_mode.py | keep | all | none | 4 bench importers |
| scripts/drawer.py | keep | all | none | the drawer. `clean` leaves for `text_guards` (OC8) |
| scripts/emit_board.py | split | all | none | 1,176 lines, over R1's 600. the design move cuts `BoardEmitter` under 600 a module |
| scripts/emit_footprint.py | keep | all | none | the build's footprint stage, 5 importers |
| scripts/fab.py | keep | all | none | `emit_board` reads via and board numbers from it (row 7) |
| scripts/firmware_platform.py | keep | all | none | `deploy` builds the platform |
| scripts/flash_image.py | keep | all | none | the image, 6 pages, walk 1 named it |
| scripts/flasher.py | keep | all | none | esptool behind one seam |
| scripts/grant.py | keep | all | none | the grant CLI, 6 pages |
| scripts/image_evidence.py | keep | all | none | look and deploy ask it |
| scripts/import_firmware.py | keep | all | none | walk 1 named it 4 times |
| scripts/init_project.py | keep | all | none | `/spark:init`, 7 pages |
| scripts/live.py | keep | all | none | the live try CLI, 6 pages |
| scripts/look.py | keep | all | none | the look, walk 2 named it 12 times |
| scripts/matching.py | keep | all | none | the matcher registry of `--need` and `--match`. its `drawer` import leaves in OC8 |
| scripts/needs.py | keep | all | none | needs, match, pick and requirements. 669 lines pay down R1 in the design move |
| scripts/netlist.py | keep | all | none | `check_spine` builds the `Netlist` (row 7) |
| scripts/outcomes.py | keep | all | none | 32 importers, the first module of core (S4) |
| scripts/part_pictures.py | keep | all | none | the drawing's pictograms |
| scripts/parts.py | split | all | none | 2,414 lines, 18 jobs (group (d)). `parts.py` stays the CLI |
| scripts/project_image.py | keep | all | none | the image's run logs, for look and deploy |
| scripts/provenance.py | keep | all | none | a leaf, called by both `validate` functions |
| scripts/reach.py | keep | all | none | the PO's bench tool, walk 2 named it 9 times |
| scripts/ready_check.py | keep | all | none | after a flash, 4 importers |
| scripts/restricted_pins.py | keep | all | none | the pins a live try must not touch |
| scripts/run_scenario.py | keep | all | none | the simulation, walk 2 named it 40 times |
| scripts/screen_text.py | keep | all | none | a leaf, renamed `text_guards.py` in OC8 |
| scripts/sim_project.py | keep | all | none | the simulation project, walk 2 named it 7 times |
| scripts/stand_in/machine.py | keep | all | none | `import_firmware` runs a firmware on the Mac with it, `pyproject.toml` lists it |
| scripts/store.py | keep | all | none | 13 importers, the person's store |
| scripts/tabbed_page.py | keep | `TabbedHtmlPage`, `TscircuitExport` | the PCB tab's lines (kept: P271's page has three tabs) | `check_spine` writes `page.html` with it |
| scripts/tools.py | keep | all | none | 15 importers, `/spark:setup` |
| scripts/zone_time.py | keep | all | none | a leaf. its test comes in `tests/test_leaves.py` (row 6) |
| tools/board.py | keep | all | none | the session start and the day close. renamed `kanban.py` (plan v2, section 3) |
| tools/check_backlog.py | keep | all | none | the WIP limits, `check_commit` runs it |
| tools/check_commit.py | keep | all | none | the push hook's gate |
| tools/check_docs.py | keep | all | none | the docs name only what is there, the gate runs it |
| tools/circuit-to-wokwi | keep | `cli.ts`, `lib/`, `dist/` | none | group (e) |
| tools/factcheck.py | keep | all | none | each slice's PR runs it on the plan |
| tools/inventory.py | keep | all | none | `pruning_facts.py` imports `Inventory` |
| tools/journey.py | keep | all | none | group (a) |
| tools/match_eval.py | prune | none | none | group (a). the tag keeps it with `tests/test_match_eval.py` |
| tools/mutate.py | keep | all | none | the mutation run before each PR, 7 pages |
| tools/pre-push | keep | all | none | the gate |
| tools/snapshot.py | keep | all | none | developing.md "Recording what spark answers" |

## The fact table

<!-- facts:start -->
| module | lines | imported by | named by | run by tests | named in walk 1 | named in walk 2 | named in walk2-diary.md |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scripts/ai_files.py | 123 | 1: init_project.py | 0 | 1 | 0 | 1 | 0 |
| scripts/assign_pins.py | 559 | 3: breadboard.py, check_spine.py, emit_board.py | 8 | 8 | 4 | 6 | 0 |
| scripts/board_connection.py | 141 | 7: board_facts.py, board_live.py, board_reach.py, firmware_platform.py, live.py, reach.py, ready_check.py | 1 | 5 | 0 | 0 | 0 |
| scripts/board_console.py | 148 | 6: board_doctor.py, board_reach.py, deploy.py, firmware_platform.py, live.py, reach.py | 0 | 8 | 0 | 0 | 0 |
| scripts/board_doctor.py | 202 | 7: board_envelope.py, board_live.py, deploy.py, grant.py, live.py, look.py, reach.py | 1 | 3 | 0 | 0 | 0 |
| scripts/board_envelope.py | 140 | 2: deploy.py, look.py | 0 | 2 | 0 | 7 | 0 |
| scripts/board_facts.py | 150 | 2: board_look.py, deploy_service.py | 1 | 4 | 1 | 3 | 0 |
| scripts/board_grant.py | 254 | 6: board_live.py, deploy.py, deploy_service.py, grant.py, image_evidence.py, live.py | 1 | 4 | 0 | 0 | 0 |
| scripts/board_live.py | 101 | 1: live.py | 1 | 1 | 0 | 0 | 0 |
| scripts/board_look.py | 311 | 8: board_doctor.py, board_grant.py, deploy.py, deploy_service.py, grant.py, live.py, look.py, reach.py | 1 | 5 | 1 | 4 | 0 |
| scripts/board_reach.py | 65 | 2: board_live.py, reach.py | 0 | 1 | 0 | 4 | 0 |
| scripts/boards.py | 843 | 25: assign_pins.py, board_doctor.py, board_envelope.py, board_look.py, check_all.py, check_spine.py, check_vendor_pins.py, deploy.py, deploy_service.py, design.py, download_mode.py, drawer.py, emit_footprint.py, firmware_platform.py, flash_image.py, flasher.py, grant.py, init_project.py, live.py, look.py, needs.py, parts.py, reach.py, sim_project.py, tools.py | 11 | 15 | 3 | 2 | 1 |
| scripts/breadboard.py | 603 | 1: check_spine.py | 4 | 7 | 0 | 1 | 2 |
| scripts/breadboard_changes.py | 235 | 1: breadboard.py | 1 | 2 | 0 | 0 | 0 |
| scripts/breadboard_drawing.py | 477 | 4: breadboard.py, breadboard_keep.py, breadboard_match.py, check_spine.py | 0 | 4 | 0 | 0 | 0 |
| scripts/breadboard_keep.py | 338 | 1: breadboard.py | 1 | 2 | 0 | 0 | 0 |
| scripts/breadboard_match.py | 93 | 1: breadboard.py | 1 | 1 | 0 | 0 | 0 |
| scripts/breadboard_steps.py | 211 | 3: breadboard.py, breadboard_changes.py, breadboard_drawing.py | 0 | 5 | 0 | 0 | 0 |
| scripts/check_all.py | 559 | 0 | 11 | 7 | 3 | 1 | 4 |
| scripts/check_bom.py | 185 | 1: check_all.py | 4 | 1 | 0 | 0 | 0 |
| scripts/check_footprints.py | 570 | 2: check_all.py, check_physics.py | 4 | 5 | 0 | 0 | 0 |
| scripts/check_physics.py | 662 | 1: check_all.py | 4 | 7 | 0 | 0 | 0 |
| scripts/check_spine.py | 1004 | 0 | 13 | 13 | 2 | 27 | 1 |
| scripts/check_vendor_pins.py | 292 | 1: check_all.py | 5 | 4 | 0 | 0 | 0 |
| scripts/compare_design.py | 297 | 2: check_all.py, parts.py | 3 | 3 | 0 | 0 | 0 |
| scripts/copper.py | 122 | 2: check_physics.py, emit_board.py | 3 | 3 | 0 | 0 | 0 |
| scripts/cost.py | 302 | 1: parts.py | 4 | 1 | 0 | 0 | 0 |
| scripts/deploy.py | 259 | 0 | 9 | 12 | 8 | 16 | 8 |
| scripts/deploy_gate.py | 106 | 5: board_envelope.py, board_grant.py, deploy.py, deploy_service.py, grant.py | 1 | 3 | 1 | 4 | 0 |
| scripts/deploy_service.py | 185 | 1: deploy.py | 0 | 4 | 2 | 3 | 0 |
| scripts/design.py | 382 | 8: assign_pins.py, breadboard.py, check_all.py, check_spine.py, emit_board.py, emit_footprint.py, init_project.py, needs.py | 4 | 7 | 0 | 0 | 0 |
| scripts/download_mode.py | 39 | 4: board_console.py, board_doctor.py, deploy.py, deploy_service.py | 0 | 2 | 0 | 0 | 0 |
| scripts/drawer.py | 427 | 4: breadboard.py, matching.py, needs.py, parts.py | 2 | 1 | 0 | 3 | 1 |
| scripts/emit_board.py | 1176 | 7: breadboard.py, check_all.py, check_physics.py, check_spine.py, init_project.py, needs.py, sim_project.py | 8 | 5 | 0 | 1 | 0 |
| scripts/emit_footprint.py | 251 | 5: boards.py, check_spine.py, emit_board.py, needs.py, parts.py | 4 | 4 | 0 | 0 | 0 |
| scripts/fab.py | 57 | 5: check_footprints.py, check_physics.py, copper.py, emit_board.py, emit_footprint.py | 3 | 2 | 0 | 0 | 0 |
| scripts/firmware_platform.py | 84 | 1: deploy.py | 0 | 3 | 0 | 0 | 0 |
| scripts/flash_image.py | 158 | 2: image_evidence.py, run_scenario.py | 6 | 6 | 2 | 0 | 1 |
| scripts/flasher.py | 66 | 3: board_look.py, firmware_platform.py, grant.py | 0 | 3 | 2 | 0 | 0 |
| scripts/grant.py | 122 | 0 | 6 | 7 | 0 | 1 | 0 |
| scripts/image_evidence.py | 199 | 2: deploy.py, look.py | 0 | 7 | 0 | 4 | 0 |
| scripts/import_firmware.py | 110 | 0 | 3 | 4 | 4 | 1 | 1 |
| scripts/init_project.py | 522 | 1: check_spine.py | 7 | 5 | 2 | 3 | 3 |
| scripts/live.py | 104 | 0 | 6 | 3 | 0 | 0 | 0 |
| scripts/look.py | 80 | 0 | 9 | 8 | 6 | 12 | 2 |
| scripts/matching.py | 230 | 3: match_eval.py, needs.py, parts.py | 0 | 1 | 0 | 0 | 0 |
| scripts/needs.py | 669 | 2: check_spine.py, parts.py | 2 | 2 | 0 | 5 | 1 |
| scripts/netlist.py | 138 | 3: check_physics.py, check_spine.py, compare_design.py | 2 | 1 | 0 | 0 | 0 |
| scripts/outcomes.py | 106 | 32: assign_pins.py, board_envelope.py, board_grant.py, board_live.py, board_look.py, boards.py, breadboard.py, check_all.py, check_bom.py, check_commit.py, check_footprints.py, check_physics.py, check_spine.py, check_vendor_pins.py, compare_design.py, cost.py, deploy.py, deploy_gate.py, emit_board.py, emit_footprint.py, flash_image.py, grant.py, import_firmware.py, init_project.py, live.py, look.py, match_eval.py, mutate.py, parts.py, reach.py, run_scenario.py, tools.py | 4 | 9 | 0 | 5 | 0 |
| scripts/part_pictures.py | 55 | 1: breadboard_drawing.py | 0 | 2 | 0 | 0 | 0 |
| scripts/parts.py | 2414 | 11: assign_pins.py, boards.py, breadboard.py, check_spine.py, design.py, drawer.py, emit_board.py, emit_footprint.py, matching.py, needs.py, sim_project.py | 21 | 14 | 1 | 27 | 2 |
| scripts/project_image.py | 97 | 4: board_look.py, deploy.py, deploy_service.py, firmware_platform.py | 0 | 5 | 2 | 1 | 0 |
| scripts/provenance.py | 31 | 2: boards.py, parts.py | 0 | 1 | 0 | 0 | 0 |
| scripts/reach.py | 105 | 0 | 3 | 3 | 0 | 9 | 0 |
| scripts/ready_check.py | 75 | 4: board_envelope.py, deploy.py, deploy_service.py, firmware_platform.py | 1 | 2 | 0 | 0 | 0 |
| scripts/restricted_pins.py | 81 | 2: board_live.py, live.py | 1 | 1 | 0 | 0 | 0 |
| scripts/run_scenario.py | 366 | 6: board_connection.py, board_console.py, download_mode.py, image_evidence.py, project_image.py, ready_check.py | 9 | 5 | 0 | 40 | 4 |
| scripts/screen_text.py | 10 | 3: board_facts.py, needs.py, parts.py | 0 | 1 | 0 | 0 | 0 |
| scripts/sim_project.py | 256 | 3: check_spine.py, project_image.py, run_scenario.py | 1 | 5 | 0 | 7 | 0 |
| scripts/stand_in/machine.py | 91 | 0 | 0 | 1 | 1 | 0 | 0 |
| scripts/store.py | 407 | 13: ai_files.py, board_facts.py, board_grant.py, boards.py, breadboard.py, check_spine.py, deploy.py, drawer.py, grant.py, init_project.py, needs.py, parts.py, tools.py | 3 | 11 | 0 | 4 | 0 |
| scripts/tabbed_page.py | 143 | 1: check_spine.py | 0 | 3 | 0 | 0 | 0 |
| scripts/tools.py | 654 | 15: board_doctor.py, board_look.py, check_spine.py, deploy.py, firmware_platform.py, flash_image.py, flasher.py, grant.py, image_evidence.py, init_project.py, live.py, parts.py, reach.py, run_scenario.py, sim_project.py | 11 | 24 | 0 | 0 | 1 |
| scripts/zone_time.py | 16 | 2: board_facts.py, board_grant.py | 0 | 0 | 0 | 0 | 0 |
| tools/board.py | 378 | 0 | 10 | 2 | 0 | 0 | 0 |
| tools/check_backlog.py | 460 | 2: board.py, check_commit.py | 4 | 1 | 0 | 0 | 0 |
| tools/check_commit.py | 177 | 0 | 4 | 3 | 0 | 0 | 0 |
| tools/check_docs.py | 231 | 0 | 2 | 1 | 0 | 0 | 0 |
| tools/circuit-to-wokwi | 24159 (26 files) | 0 | 5 | 5 | 1 | 3 | 0 |
| tools/factcheck.py | 136 | 0 | 3 | 1 | 0 | 0 | 0 |
| tools/inventory.py | 124 | 0 | 1 | 1 | 0 | 0 | 0 |
| tools/journey.py | 164 | 0 | 0 | 2 | 0 | 0 | 0 |
| tools/match_eval.py | 115 | 0 | 0 | 1 | 0 | 0 | 0 |
| tools/mutate.py | 398 | 0 | 7 | 2 | 0 | 0 | 0 |
| tools/pre-push | 6 | 0 | 4 | 3 | 0 | 0 | 0 |
| tools/snapshot.py | 322 | 0 | 1 | 1 | 0 | 0 | 0 |

Walk records:
- walk 1: `docs/observations/2026-10-19-p326-walk1.md` and `docs/observations/2026-10-19-p351-walk1-council`
- walk 2: `docs/observations/2026-10-23-p400-walk2-council`
- walk2-diary.md: outside the repo, sha256 9ee2356cc5f6f7f89b6c869d7fb4e01bf48138fa1f2e6bbbd4663bb5558da486
<!-- facts:end -->

## Facts for the verdicts

Every number below came from the command named beside it, run at `d064a65`. Here `T` is the fact table above.

### (a) Modules reached by nothing

Command: `python3 tools/inventory.py` (73 scripts, 2 reached by nothing). Then the table, rows where `imported by` is 0
and `named by` is 0.

- Inventory says nothing reaches `tools/journey.py` (164 lines) and `tools/match_eval.py` (115 lines).
- The table adds `scripts/stand_in/machine.py` (91 lines). Inventory does not read subfolders. A test loads it by
  path and `pyproject.toml` lists `scripts/stand_in`.
- Both Inventory finds are read by tests (`run by tests` is 2 and 1). `AGENTS.md` names `tools/journey.py`, but
  Inventory does not read `AGENTS.md`. Command: `git grep -c "journey.py" -- AGENTS.md` printed 1.
- 21 rows have `named by` 0. 20 rows have `imported by` 0. The overlap is the three rows above.
- One module has `run by tests` 0: `scripts/zone_time.py` (16 lines). Two modules import it.
- 44 of 76 rows are named in neither walk 1 nor walk 2 (awk over `T`, columns 7 and 8). 43 are also not in the diary.

### (b) Flags no page names, per script

Command: `python3 tools/inventory.py`, the Commands table, last column. The summary line says 156 flags, 19 named on no page.

| script | flags no page names |
| --- | --- |
| `scripts/boards.py` | `--id` `--path` `--paths` |
| `scripts/check_all.py` | `--boards` |
| `scripts/check_vendor_pins.py` | `--repo` |
| `scripts/flash_image.py` | `--config` `--output` |
| `scripts/import_firmware.py` | `--timeout` |
| `scripts/parts.py` | `--from` `--signals` |
| `scripts/run_scenario.py` | `--timeout-ms` |
| `scripts/tools.py` | `--personal` |
| `tools/match_eval.py` | `--cases` `--drawer` `--json` `--match` `--matcher` |
| `tools/mutate.py` | `--root` `--tests` |

That is 10 scripts and 3+1+1+2+1+2+1+1+5+2 = 19 flags.

### (c) PCB and fabrication checks off the breadboard journey

"Off the journey" here means: not imported by `scripts/check_spine.py` (the build), which `/spark:build` runs. Evidence
is the `imported by` column of `T` and `/usr/bin/grep -n "import check_" scripts/check_all.py scripts/check_spine.py`.

| module | lines | imported by | evidence for the count |
| --- | --- | --- | --- |
| `scripts/check_bom.py` | 185 | `check_all.py` | The check named `TheOrder` in `check_all.py` (line 266). Reads a fab package. The README says it was "skipped, with no fab package yet". |
| `scripts/check_footprints.py` | 570 | `check_all.py`, `check_physics.py` | Docstring: "Will this board be buildable". Reads board-house limits through `fab.py`. Not imported by the build. |
| `scripts/check_physics.py` | 662 | `check_all.py` | Imports `copper.py` and `netlist.py`. The README says "physics could not look" in the journey's run. Not imported by the build. |

Total of these three: 1417 lines (`cat scripts/check_bom.py scripts/check_footprints.py scripts/check_physics.py | wc -l`).
Their tests: `tests/test_check_bom.py`, `test_check_footprints.py` and `test_check_physics.py` hold 1488 lines (`wc -l`).

Modules the PCB checks share with the build, so removing the checks does not free them:

| module | lines | imported by | why it stays with the build |
| --- | --- | --- | --- |
| `scripts/copper.py` | 122 | `check_physics.py`, `emit_board.py` | `emit_board.py` line 192 calls `copper.width_to_emit_mm` to size a trace. |
| `scripts/fab.py` | 57 | `check_footprints.py`, `check_physics.py`, `copper.py`, `emit_board.py`, `emit_footprint.py` | `emit_board.py` lines 120 to 122 read via and board numbers from it. |
| `scripts/emit_footprint.py` | 251 | `boards.py`, `check_spine.py`, `emit_board.py`, `needs.py`, `parts.py` | `check_spine.py` line 430 runs it. A board with no footprint stops the build (P407). |
| `scripts/tabbed_page.py` | 143 | `check_spine.py` | Draws the PCB tab of `page.html`. `named by` is 0. |
| `scripts/netlist.py` | 138 | `check_physics.py`, `check_spine.py`, `compare_design.py` | `check_spine.py` line 305 builds `netlist.Netlist`. |

The three checks plus `copper.py` and `fab.py` hold 1596 lines (`wc -l` of the five files). `data/fabrication.json`
adds 53 lines. Tests of copper and fab add 141 and 149 lines. The five test files together hold 1778 lines.

Not counted in, with the reason: `scripts/compare_design.py` compares a written rule with the built design, no
PCB step. `scripts/check_vendor_pins.py` compares a board record with the vendor's pin list.

### (d) `scripts/parts.py`: 2414 lines, 126 top-level functions and classes

Command: a short `ast` walk of `scripts/parts.py` (`end_lineno - lineno + 1`, decorators included). The functions and
classes hold 1827 lines. The top-level constants hold 146 lines.
The rest is imports, docstrings and blank lines. The groups are my reading of the names and a look at a few bodies.
Each entry is `name lines`.

- Know what a record is for, and say it is broken: 9 names, 92 lines. `function_of` 15, `function_problems` 8, `aliases` 4, `_absent` 4, `owes` 4, `_shape_problems` 6, `broken_problems` 3, `audit` 40, `one_line` 8
- Find and load a record, and the errors it raises: 9 names, 30 lines. `PartError` 2, `BadArgument` 2, `_problem` 2, `_cannot` 2, `_note` 4, `_with_project` 2, `available` 2, `definition_path` 6, `load` 8
- Check field types: 4 names, 35 lines. `ListOf` 5, `MapOf` 5, `_type_name` 2, `type_problems` 23
- Validate a record against the rules: 13 names, 443 lines. `bus_line_of` 10, `printed_names` 9, `has_placeholder_footprint` 3, `footprint_pad_count` 20, `chip_folder` 3, `pin_order_problems` 18, `document_problems` 18, `_citations` 10, `i2c_pullup_problems` 26, `host_part_problems` 32, `simulation_problems` 56, `control_problems` 8, `validate` 230
- Say what a part asks of the board: 3 names, 39 lines. `signals_for` 24, `open_questions_of` 12, `unverified` 3
- Search the store and the vendor catalog: 6 names, 62 lines. `vendor_order` 12, `_url_in_prose` 5, `catalog_records` 13, `_found` 6, `catalog_matches` 6, `need` 20
- Shelve a record in the store, and its history: 9 names, 76 lines. `digest` 7, `note_built` 12, `_shelf_copy` 10, `shelvable` 3, `shelve` 15, `record_home` 4, `any_record` 6, `keep_in_store` 13, `_shelved_from` 6
- Strip GPS data from a photo: 1 name, 36 lines. `without_location` 36
- Read, fetch and keep datasheets: 15 names, 227 lines. `scan_datasheet` 40, `datasheet_pages` 11, `read_datasheet` 24, `keep_local` 9, `records_with_documents` 9, `citing` 19, `find_kept` 32, `document_key` 7, `to_fetch` 4, `document_name` 3, `fetch_plan` 13, `fetch_documents` 23, `_parse` 5, `_download` 6, `promote` 22
- Prepare research: sellers, skeleton, sources, conflicts: 8 names, 120 lines. `sellers` 15, `skeleton` 22, `cited_urls` 12, `reachable` 7, `sources_resolve` 3, `pull_conflicts` 3, `conflicts_of` 44, `_holding_low` 14
- Command: read, validate and research a record: 20 names, 199 lines. `describe` 25, `_row` 2, `_brief` 2, `_read_json_input` 6, `_op_list` 8, `_op_show` 11, `_op_validate` 16, `_op_signals` 3, `_op_unverified` 11, `_op_need` 19, `_op_skeleton` 15, `_op_sources` 11, `_op_fetch` 11, `_op_keep` 10, `_op_read` 6, `_op_kept` 3, `_op_promote` 6, `_op_catalog` 9, `_op_audit` 15, `_op_describe` 10
- Command: write a record or a set-only change: 8 names, 118 lines. `_change_line` 14, `_write_lines` 10, `_record_path` 17, `_refresh_shelf_copy` 16, `_write_record` 6, `_set_in_home` 30, `_op_function_set` 8, `_op_fact_set` 17
- Command: the drawer: 4 names, 47 lines. `_drawer_answer` 19, `_op_drawer` 11, `_op_drawer_set` 6, `_op_drawer_import` 11
- Command: needs, match, pick and requirements: 11 names, 214 lines. `_op_needs` 7, `_op_match` 32, `_op_offer` 8, `_op_needs_set` 11, `_op_pick` 34, `_what_a_pick_wrote` 19, `_names_your_entries` 7, `_released` 8, `_op_requirements` 45, `_op_step` 15, `_op_tally` 28
- Command line: parser, text and main: 6 names, 89 lines. `_not_negative` 5, `_Parser` 5, `_parser` 9, `_text_of` 26, `_say` 21, `main` 23

Largest single entries: `validate` 230 lines, `OPERATIONS` (a constant table) 65, `simulation_problems` 56,
`_op_requirements` 45, `conflicts_of` 44. The five command groups hold 667 lines. The ten record groups hold 1160.

### (e) `tools/circuit-to-wokwi`: 24159 tracked lines in 26 files

Command: `git ls-files tools/circuit-to-wokwi | xargs cat | wc -l` printed 24159. Per file: `wc -l`.

| part | files | lines | what |
| --- | --- | --- | --- |
| bundle (`dist/`) | 2 | 21898 | `converter.mjs` 21897 lines (674138 bytes), `converter.sources.sha256` 1 line |
| lock file | 1 | 54 | `bun.lock` |
| sources | 10 | 1356 | `cli.ts` 156 and nine files under `lib/` (1200) |
| tests | 9 | 630 | seven `*.ts` files, `README.md` and `.mapping-under-test.json` (0 lines, 183 bytes, no final newline) |
| other | 4 | 221 | `ARCHITECTURE.md` 172, `bundle.sh` 14, `package.json` 22, `tsconfig.json` 13 |

21898 + 54 + 1356 + 630 + 221 = 24159. The bundle is 90.6 percent of the lines (`awk` over these numbers).
`bundle.sh` says that `tests/test_check_spine.py` fails while `dist/converter.sources.sha256` does not match the
sources. `scripts/check_spine.py` line 194 names `tools/circuit-to-wokwi/cli.ts` as the converter.
The table row says `named by` 5 and `run by tests` 5.

### (f) `scripts/boards.py`: 843 lines, 60 top-level names

Command: the same `ast` walk, with start and end line. 4 classes (77 lines), 28 functions (511 lines) and 28 constants
(70 lines). `validate` alone spans 172 lines.

`LIBRARY` 42-42, `PROJECT_BOARDS_DIR` 45-45, `SELECTION_NAME` 46-46, `DEFINITION_SUFFIX` 47-47, `RESOLVED_NAME` 54-54, `SPARK_DIR` 55-55, `NOT_A_BOARD` 58-58, `SUPPORTED_SCHEMA` 63-63, `REQUIRED_KEYS` 66-67, `REQUIRED_FOR_FAB` 71-71, `FORBIDDEN_KEYS` 80-89, `PIN_ROLES` 99-116, `CONSOLE_UART` 119-119, `ONBOARD_LED` 121-121, `ONBOARD_BUTTON` 122-122, `ONBOARD_DISPLAY` 123-123, `ONBOARD_BATTERY_SENSE` 124-124, `BoardError` 133-134, `walk_up` 137-146, `project_root` 149-162, `PLUGIN_ROOT` 168-168, `project_or_library` 171-182, `_read_json` 185-191, `selection_file` 194-195, `active_id` 198-224, `records` 227-229, `definition_path` 232-239, `available` 242-244, `footprint_stop` 247-261, `load` 264-272, `_words` 275-277, `ButtonPlaces` 280-324, `OnboardRole` 331-348, `ONBOARD_ROLES` 353-364, `POWER_FUNCTIONS` 368-372, `onboard_entries` 375-384, `pin_labels` 387-389, `names_pins` 392-397, `_power_functions` 400-406, `onboard_functions` 409-411, `WOKWI_DEFINITION` 415-415, `_COMMENT` 417-417, `_GPIO` 418-418, `SimulatedPart` 421-432, `read_simulated_part` 435-464, `resolve` 468-486, `LABEL` 493-493, `FACT_NAME` 494-494, `LEVEL_LABEL` 495-495, `LEVEL_FACT` 496-496, `is_gpio` 499-500, `is_fact_value` 503-507, `fact_value_problems` 510-516, `role_entry_problems` 519-555, `power_problems` 558-565, `validate` 569-740, `KEY_PATH_SEPARATOR` 744-744, `get` 747-760, `_validate_all` 763-784, `main` 787-839
