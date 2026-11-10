# Proposed items

The PO said yes to this list (D13). Each item is filed as a sub-issue of P735 #1010, with Slice "10 The store" (D16).

## The research pipeline: sources and strategies, designed with a council
- type: story, a design that starts in plan mode with a two-round council and an architecture lens <!-- REQUIRED:item-type -->
- needed by: "Let's really have it well designed so it becaomes a good base for all modules, parts and boards" (the PO, 2026-11-10) <!-- REQUIRED:needed-by -->
- value proven by: slice 0 of story-map.md, `parts.py --show sen0526-i2s-mic` with the picture, outline, holes and header row, made by the pipeline with no hand edit <!-- REQUIRED:value-proven-by -->
- depends on: the geometry count spike for the order of the strategies <!-- REQUIRED:depends-on -->
- status: filed D13, P737 #1013 <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P735 #1010 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store, D16 <!-- REQUIRED:spark-process:slice -->

## The fact need tree: which consumer needs which fact
- type: story
- needed by: "Maybe we should actually implement some kind of dependency tree for a few things in spark and one of them would be information, like what needs what specific info for what part or bus or somethhing" (the PO, 2026-11-10)
- value proven by: `data/fact-needs.json` holds the rows that have a reader today (council/fact-tree.md:238). `parts.py --unverified sen0526-i2s-mic` names the consumer of each open fact, and a test fails on a row whose consumer does not exist
- depends on: the architecture direction (Q6), and Q7 for its scope
- status: filed D13, P738 #1014
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P735 #1010
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store, D16

## Spike: how much geometry DFRobot publishes for the owned modules
- type: spike
- needed by: "full records of my DFRobot parts, or at least a subset" (the PO, 2026-11-10)
- value proven by: a table, one row per owned PCB module: dimension drawing, schematic, STEP, layout zip, each linked or not. Five drawings read for hole positions, against the pass line of A1
- depends on: Q1 (the pass line), Q3 (the scope)
- status: filed D13, P739 #1015
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P735 #1010
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store, D16

## `--skeleton` writes the forbidden `sourcing` block and hides a shelf record
- type: bug
- needed by: "we'll fix gaps and bugs afterwards" (the PO, 2026-11-10)
- value proven by: `parts.py --skeleton` writes no `sourcing` key, and on an id the shelf holds it names the shelf record and writes nothing (council/tech-lead.md TL-13, TL-14)
- depends on: none
- status: filed D13, P740 #1016
- label (the repository's type label): bug
- parent (the epic, as a sub-issue): P735 #1010
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store, D16

## `--fact-set` refuses `legs` and `host_requirements`
- type: bug
- needed by: "we'll fix gaps and bugs afterwards" (the PO, 2026-11-10)
- value proven by: `parts.py --fact-set <id> <file>` writes `legs` and adds a `host_requirements` line (TL-15)
- depends on: none
- status: filed D13, P741 #1017
- label (the repository's type label): bug
- parent (the epic, as a sub-issue): P735 #1010
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store, D16

## `--read` answers FOUND on the wrong row
- type: bug
- needed by: "we'll fix gaps and bugs afterwards" (the PO, 2026-11-10)
- value proven by: on the kept SEN0526 datasheet, `--want supply_voltage` answers the operation row (1.6 to 3.6 V), `--want snr` answers page 3, `--want input_high` finds VIH (TL-19)
- depends on: none
- status: filed D13, P742 #1018
- label (the repository's type label): bug
- parent (the epic, as a sub-issue): P735 #1010
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store, D16

## `--need` finds an owned part by what it does, and finds boards
- type: story, a P211 matcher default that changes only with the PO's yes (council/refuter.md:38)
- needed by: "full records of my DFRobot parts" (the PO, 2026-11-10), Job 1
- value proven by: `--need "load switch"` names DFR0457 and the drawer count, `--need ESP32-C6` names the XIAO ESP32-C6 board (TL-12)
- depends on: none
- status: filed D13, P743 #1019
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P735 #1010
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store, D16

## Board record tools: bare GPIO labels and the stand-in rule
- type: bug
- needed by: "we'll fix gaps and bugs afterwards" (the PO, 2026-11-10)
- value proven by: `check_vendor_pins.py` passes a board whose silkscreen prints GPIO numbers, and `boards.py --validate` refuses a stand-in with no Wokwi document (TL-17, TL-18)
- depends on: none
- status: filed D13, P744 #1020
- label (the repository's type label): bug
- parent (the epic, as a sub-issue): P735 #1010
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store, D16

## Wrong claims in kept records and docs
- type: chore
- needed by: "we'll fix gaps and bugs afterwards" (the PO, 2026-11-10)
- value proven by: the DFR0457 shelf record loses the wrong 12 V note (C11). Its irrigation wording (C15) goes too, because the irrigation project keeps its own copy in its parts/ folder, part-data.md:51 no longer says DFRobot ships no KiCad footprints (C14), `led-red-5mm` follows the researcher's rule for a pin order read off a drawing (C16)
- depends on: none
- status: filed D13, P745 #1021
- label (the repository's type label): chore
- parent (the epic, as a sub-issue): P735 #1010
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store, D16

## Board actions
- file the nine items above · taken 2026-11-10, D13 <!-- REQUIRED:board-actions -->
