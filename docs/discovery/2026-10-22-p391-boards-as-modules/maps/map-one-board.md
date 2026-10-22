# Map 3: where one board is assumed (Sonnet mapper, 2026-10-22; grep hits, not all files read in full)

Data shape: requirements["board"] bare string id; boards/active.json {"schema":1,"board":id}; .spark/board.json resolved copy. boards.py:208-213 raises "A project is built around ONE board ... Two boards means two projects".
| assumption | file:line | lift |
| board is a string, one id, ONE-board error | boards.py:183-213 active_id | data shape |
| .spark/board.json + active.json one resolved board; SPARK_BOARD_JSON env one file | boards.py:42,50,321-359; check_spine.py:503-515 | data shape + loop |
| boards.load(project, board_id=None) falls back to active | boards.py:253, 510 get | small |
| ButtonPlaces.of_project reads requirements["board"] | boards.py:297 | data shape |
| design.load / parts_of call boards.load(root, wanted.get("board")); Design has one .board, read ~20 places | design.py:268,377 | deep |
| assign_pins.assign(board, signals), pin_module: one board, one pin namespace, one pins.py | assign_pins.py:152-243,392-405,461-519 | deep: signals need an owner board |
| emit_board one Mcu (placements["Mcu"]), one footprint_export, mcu_power_nets, ".Mcu" trace strings | emit_board.py:374,498,591,630,809,867-898,1065 | deep rewrite, hardest |
| emit_footprint one --board | emit_footprint.py:151-217 | loop |
| check_spine one "board" stage; sim diagram one part id "mcu" from wokwi_part_type | check_spine.py:83,363-418,548-555 | loop / deep for Wokwi |
| breadboard THE_BOARD key, one catalog entry, built.board | breadboard.py:274,306,315,363-384,467-492; breadboard_steps.py:18-21,147; breadboard_changes.py:82 | deep |
| sim_project/run_scenario design.board | sim_project.py:49 | loop |
| check_all matched[0].board | check_all.py:218,254-256 | small |
| firmware_platform board_of(project)=requirements["board"], record_of, micropython() | firmware_platform.py:22-40 | small-medium |
| flash_image .get("board") for micropython_port | flash_image.py:79-90 | small |
| deploy one FirmwarePlatform.micropython(project), one record["chip"], one port, one image | deploy.py:43,191; deploy_service.py:88,179 | medium |
| look / board_look.record_of reads requirements["board"] | board_look.py:277-285 | medium |
| store boards/<MAC>.json per physical board, facts "board": type; built event single board key | board_facts.py:23-72; store.py:275-276 | fits many; event needs a list |
| init_project writes active.json from one --board | init_project.py:483-491,500 | data shape |
| needs PICKS board capped at 1; _board_problems "pick one board"; content["board"] one id, board_was | needs.py:27,314,340,544,618-659 | medium |
| parts _op_requirements prints/writes content["board"], one footprint_stop | parts.py:2243-2251 | small-medium |
| KIND_FUNCTION["board"]=("compute","microcontroller"); boards/ separate type, boards.validate | parts.py:70,141,158-167 | context |
| drawer {"part"|"board": id} two kinds | drawer.py:86,133-136 | none |
A part record cannot carry an MCU today: no mcu key, no microcontroller kind; simulation.wokwi.chip (parts.py:565-585) is a custom Wokwi chip. Board-only fields: physical, chip, pins, wokwi_part_type, micropython_port.
Hardest: emit_board (single Mcu), Design.board, assign_pins (one namespace). Easiest: loops in check_spine, emit_footprint, flash_image, look/deploy ports. Cheapest first step: requirements["board"] read through one accessor; today ~9 separate .get("board") sites (board_look, boards, firmware_platform, flash_image, design x2, check_spine, needs, parts).
