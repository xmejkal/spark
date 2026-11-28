# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item. -->

The proposals below are cards for spark-main to file after the PO's yes. P275 #311 stays the build card of the perfboard. Each card is a sub-issue of its epic. None is in Ready.

## The same-pins check reads each join as a set of holes (ConnectedGroups)
- type: refactor story. The goldens stay byte for byte, but the check's public codes `not-joined`, `joined-to-other` and `joined-to-unused` change for agents (docs/guide/agents/scripts.md:219-220) <!-- REQUIRED:item-type -->
- needed by: "we don't want to have multiple places in the codebase implementing almost the same, remember this" (the PO, 2026-11-28) <!-- REQUIRED:needed-by -->
- value proven by: 9 of 9 golden breadboards stay byte for byte (at most 5 of them draw a placement or a route). One test catches a bare wire over another net's pad. A grep finds one union-find in scripts/spark <!-- REQUIRED:value-proven-by -->
- depends on: Q2 (the order against P1199 D3), and a perfboard join to test against, so it lands with the walking skeleton unless Q2 says otherwise <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): refactor <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1199 #1747 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## One GridSearch and the router's weights as one named Value (TrackWeights)
- type: refactor story, byte-neutral
- needed by: "lets just leave the penalties for turning and crossing and such configurable or at least as constants in the code, so that we can later play around with it" (the PO, 2026-11-28, #1937)
- value proven by: 9 of 9 goldens, tests/test_wire_routing.py with `cut_short` equal, a test that pins each default, and `TRIES` derived from the Value's own numbers
- depends on: P1350 #1937 merged, and Q2 (the order against P1199 D3)
- status: proposed
- label (the repository's type label): refactor
- parent (the epic, as a sub-issue): P1199 #1747
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## Split drawing.py: the Wokwi renderer and round_px to their own module
- type: chore, byte-neutral
- needed by: "feel free to refactor anytime you think something could be dried out" (the PO, 2026-11-28)
- value proven by: drawing.py at about 542 lines (lines 543 to 599 out), 9 of 9 goldens, no private `_round_px` import left (a grep)
- depends on: Q2 (the order against P1199 D3)
- status: proposed
- label (the repository's type label): refactor
- parent (the epic, as a sub-issue): P1199 #1747
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## A drawer perfboard gets its holes and pitch, with each fact's origin
- type: story
- needed by: "the person's perfboard sizes come from the drawer, cut smaller, never bigger" (the PO, 2026-11-26, #311 note 2)
- value proven by: the FIT0193's entry holds holes across, holes down and pitch, each `assumed` or `measured`. One Operation with a dry run writes them, and the CLI's `--json` names it
- depends on: P1238 #1791 for the measured values (the Operation can write assumed values first)
- status: proposed
- label (the repository's type label): feature
- parent (the epic, as a sub-issue): P275 #311
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## The perfboard plan in text and JSON on the CLI (the walking skeleton)
- type: story
- needed by: "the perfboard step, it should actually maybe not be so much different from the breadboard" (the PO, 2026-11-28)
- value proven by: one CLI run on button-light, or the gadget Q6 names, writes each part's holes, each join with its kind and every hole, and the cut, and the same-pins check passes. Its `--json` has `board`, `parts`, `joins`, `weights` and `pins_kept`
- depends on: the two refactor stories above, spike P1239 #1792, the drawer story, Q3 and Q6
- status: proposed
- label (the repository's type label): feature
- parent (the epic, as a sub-issue): P275 #311
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## After a drag that changes the wiring, one sentence for Claude with Copy (the drag's first slice)
- type: story
- needed by: "and for now it can for example based on it generate a prompt, or something, when the wiring changes, to copy and say to claude" (the PO, 2026-11-28, #1699)
- value proven by: one Operation takes a dragged layout and names the wiring change in one sentence, on button-light's breadboard. The CLI with `--json`, spark's commands and skills, and the page's Copy all reach it
- depends on: the design's drag model (P1352's design), the layout JSON of the walking skeleton
- status: proposed
- label (the repository's type label): feature
- parent (the epic, as a sub-issue): P1163 #1699
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## Board actions
- file the six items above as cards, each with "Needed by" and its slice · pending. It needs a D that names items.md. Then spark-main files them <!-- REQUIRED:board-actions -->
