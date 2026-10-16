# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. Step 8, sharing, is the store epic P178 (#123), D6: no new item. The Fusion export is step 9 (D9). -->

## Step 1: a small common base for every stage, breadboard only
- type: story <!-- REQUIRED:item-type -->
- needed by: "please also create some common base" (the PO, 2026-10-16); D7 <!-- REQUIRED:needed-by -->
- value proven by: the suite passes and the XIAO fixture's `breadboard.json` keeps its sha256 (cf3f8e53…, from `hashlib.sha256(breadboard.drawing(tests/data/breadboard/button-light-xiao/requirements.json))`, run 2026-10-16) <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: filed D8, #306 P270 <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P269 (#304) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one <!-- REQUIRED:spark-process:slice -->

## Step 2 = P268 (#302): the picture of the breadboard in breadboard.md
- type: story
- needed by: "start with a smsall version of svg and our custom modules/parts/boards pictures" (the PO, 2026-10-16); D4
- value proven by: `breadboard.svg` for button-light in VS Code and on GitHub, and he says the picture helped him wire (A3)
- depends on: step 1
- status: filed D8, #302 P268, filed before
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one

## Step 3: a page on the Mac with the breadboard, schematic and PCB tabs
- type: story
- needed by: "we can start by a webpage" (the PO, 2026-10-16); D5
- value proven by: the page opens the layout of button-light, with all three tabs, and one circuit source checks the layout
- depends on: step 2
- status: filed D8, #307 P271
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one

## Step 4: the same page as an Artifact
- type: story
- needed by: "reusable for the artifact" (the PO, 2026-10-16); D5
- value proven by: the same bundled file opens as an Artifact
- depends on: step 3
- status: filed D8, #308 P272
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one

## Step 5: edit the layout, and the next build keeps the moves
- type: story
- needed by: "a really nice editor"; "it should stay where we move it" (the PO, 2026-10-16); D11: it stays after a rebuild
- value proven by: edit, rebuild, the move survives or is named
- depends on: step 3
- status: filed D8, #309 P273
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one

## Step 6a: stripboard: cuts, links and a planner
- type: story
- needed by: "Plain perfboard, Stripboard, Both" (the PO, 2026-10-16); D3: later
- value proven by: a button-light stripboard layout that the circuit check accepts
- depends on: step 3
- status: filed D8, #310 P274
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): 7 Perfboard to PCB

## Step 6b: plain perfboard: grid routes, back wires and bridges
- type: story
- needed by: "how making routes works there" (the PO, 2026-10-16); D3
- value proven by: a button-light perfboard layout that the circuit check accepts
- depends on: step 6a
- status: filed D8, #311 P275
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): 7 Perfboard to PCB

## Step 7: the catalogue editor, with pictures from the web kept in the store
- type: story
- needed by: "the catalogue editing app for the parts and modules and boards and batteries"; "import images from web"; "to be able to add and edit where on the picture which holes and connectors etc are" (the PO, 2026-10-16)
- value proven by: a module edited and drawn in two views, its picture credited, with its holes, pins and connectors marked on its picture or photo (D10)
- depends on: step 3
- status: filed D8, #312 P276
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store

## Step 9: export for Fusion 360, a 3D model with the PCB and the parts
- type: story
- needed by: "export should be possible, ultimately whatever is needed for fusion , if possoble to have it 3d made there, including pcb and parts" (the PO, 2026-10-16); D9
- value proven by: button-light's board and parts open in Fusion 360 as a 3D model
- depends on: step 7
- status: filed D8, #313 P277
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): 9 An enclosure

## The XIAO board record gets its header facts
- type: chore
- needed by: found on the way (C12)
- value proven by: the XIAO record validates with rows, pitch and first pad, cited
- depends on: —
- status: filed D8, #314 P278
- label (the repository's type label): chore
- parent (the epic, as a sub-issue): P269 (#304)
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey

## Board actions
- filed the items above, each a sub-issue of #304 in Idea · D8, done 2026-10-16. Steps 1, 3, 4 and 5 wait for the new Slice option "Views and editors" (D13), which the PO adds by hand <!-- REQUIRED:board-actions -->
