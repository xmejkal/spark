# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

## P<next free number> — nothing shows which project uses a connected board → one command lists each board on USB with the projects that keep it, its last deploy and its grants, and opens no port
<!-- P917 is the highest number on 2026-11-18. Read the highest number again just before filing. -->
- type: story <!-- REQUIRED:item-type -->
- needed by: "Well, at least to see how it's in the projects." (the PO, 2026-11-18, comment 1 on #1298) <!-- REQUIRED:needed-by -->
- value proven by: the command's output with one board on USB, and a test that proves that it opens no port <!-- REQUIRED:value-proven-by -->
- depends on: — (the PO chose it as the first slice, D8) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P365 #467, the parent of P917 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): team tools, the slice of P917 <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P<next free number> — a tool that is not spark's leaves no trace in the store → a tool tells the store about itself once, and then reports its deploys to a board
- type: story <!-- REQUIRED:item-type -->
- needed by: "mostly just spark, but tools that register can access and use it and share too" (the PO, 2026-11-18, D4 and D7 in brief.md) <!-- REQUIRED:needed-by -->
- value proven by: after a registered tool reports a deploy, the view names that tool's project for the board <!-- REQUIRED:value-proven-by -->
- depends on: the view's item above, and the PO's answer to Q4 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P365 #467, the parent of P917 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): team tools, the slice of P917 <!-- REQUIRED:spark-process:slice -->

## In pixel-games: `box.py` registers with the store and reports each deploy
- type: story <!-- REQUIRED:item-type -->
- needed by: "It tells the store about itself" (the PO, 2026-11-18, D7 in brief.md, with `box.py` as the example) <!-- REQUIRED:needed-by -->
- value proven by: after `box.py deploy`, spark's view names pixel-games for the game box <!-- REQUIRED:value-proven-by -->
- depends on: the item above, and A6's test (the pixel-games session's yes with the command) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): — (the pixel-games repository's labels are not read yet) <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — (its epic in pixel-games is the PO's choice) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): pixel-games <!-- REQUIRED:spark-process:slice -->

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- file the three items above · pending, it needs the PO's yes to this list <!-- REQUIRED:board-actions -->
