# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. -->

## Spike: does a hand edit survive the next build?
- type: spike <!-- REQUIRED:item-type -->
- needed by: "think of saving and loading" (the PO, 2026-10-16) <!-- REQUIRED:needed-by -->
- value proven by: the spike's three cases in risks-and-tests.md Results (A1) <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P269 (#304) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 1b From a vague idea <!-- REQUIRED:spark-process:slice -->

## S0: one base for every stage, in mm, breadboard first
- type: story
- needed by: "please also create some common base" (the PO, 2026-10-16)
- value proven by: the suite passes and `breadboard.json` keeps its sha256 for button-light
- depends on: the spike
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one

## S1 = P268 (#302): the SVG in the sheet with spark's own pictures
- type: story
- needed by: "start with a smsall version of svg and our custom modules/parts/boards pictures" (the PO, 2026-10-16)
- value proven by: `breadboard.svg` for button-light, seen in VS Code and on GitHub
- depends on: S0
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one

## S2: one circuit source and a check that a layout matches it
- type: story
- needed by: "a good thought through way of displaying the schema in different stages" (the PO, 2026-10-16)
- value proven by: a fixture with a wrong jumper fails the check
- depends on: S0
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one

## S3: a read-only viewer as a local page and an Artifact, with schematic and PCB tabs
- type: story
- needed by: "we can start by a webpage ... reusable for the artifact" (the PO, 2026-10-16)
- value proven by: the same layout file opens in both hosts
- depends on: S1, S2
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one

## S4: edit the breadboard layout, and the next build keeps the edit
- type: story
- needed by: "a really nice editor" (the PO, 2026-10-16)
- value proven by: edit, rebuild, the edit survives, a breaking edit is reported
- depends on: S3, the spike
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one

## S5: stripboard: cuts, links and a planner
- type: story
- needed by: "Plain perfboard, Stripboard, Both" (the PO, 2026-10-16)
- value proven by: a button-light stripboard layout that passes S2's check
- depends on: S2
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): 7 Perfboard to PCB

## S6: plain perfboard: grid routes, back wires and bridges
- type: story
- needed by: "how making routes works there" (the PO, 2026-10-16)
- value proven by: a button-light perfboard layout that passes S2's check
- depends on: S5
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): 7 Perfboard to PCB

## S7: the catalogue editor, with pictures from the web kept in the store
- type: story
- needed by: "the catalogue editing app for the parts and modules and boards and batteries"; "import images from web" (the PO, 2026-10-16)
- value proven by: a module edited and drawn in two views, its picture credited
- depends on: S3, Q8
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store

## The XIAO board record gets its header facts
- type: chore
- needed by: found on the way (C12); P267's drawing needs the board's pins in mm
- value proven by: the XIAO record validates with rows, pitch and first pad, cited
- depends on: —
- status: proposed
- label (the repository's type label): chore
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey

## Board actions
- file the items above, each a sub-issue of #304 · pending, needs the PO's yes to this list <!-- REQUIRED:board-actions -->
