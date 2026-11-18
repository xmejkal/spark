# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

## P919 #1301 — nothing shows which project uses a connected board → one command lists each board on USB with the projects that keep it, its last deploy and its grants, and opens no port
<!-- P918 (#1299) is the highest number on 2026-11-18. Read the highest number again just before filing. -->
- type: story <!-- REQUIRED:item-type -->
- needed by: "Well, at least to see how it's in the projects." (the PO, 2026-11-18, comment 1 on #1298) <!-- REQUIRED:needed-by -->
- value proven by: the command's output with one board on USB, and a test that proves that it opens no port <!-- REQUIRED:value-proven-by -->
- depends on: — (the PO chose it as the first slice, D8) <!-- REQUIRED:depends-on -->
- status: filed D11, https://github.com/xmejkal/spark/issues/1301 <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P365 #467, the parent of P917 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): team tools, the slice of P917 <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P920 #1302 — a tool that is not spark's leaves no trace in the store → a tool tells the store about itself once, and then reports its deploys to a board
- type: story <!-- REQUIRED:item-type -->
- needed by: "mostly just spark, but tools that register can access and use it and share too" (the PO, 2026-11-18, D4 and D7 in brief.md) <!-- REQUIRED:needed-by -->
- value proven by: after a registered tool reports a deploy, the view names that tool's project for the board <!-- REQUIRED:value-proven-by -->
- depends on: the view's item above (the project's name is decided, D9) <!-- REQUIRED:depends-on -->
- status: filed D11, https://github.com/xmejkal/spark/issues/1302 <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P365 #467, the parent of P917 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): team tools, the slice of P917 <!-- REQUIRED:spark-process:slice -->

## P921 #1303 — in pixel-games: `box.py` registers with the store and reports each deploy
- type: story <!-- REQUIRED:item-type -->
- needed by: "It tells the store about itself" (the PO, 2026-11-18, D7 in brief.md, with `box.py` as the example) <!-- REQUIRED:needed-by -->
- value proven by: after `box.py deploy`, spark's view names pixel-games for the game box. For that, `box.py` names the board of the deploy, and today it reports no port and no USB serial (C25) <!-- REQUIRED:value-proven-by -->
- depends on: the item above. A6's pass line needs this card, so this card does not wait for A6 <!-- REQUIRED:depends-on -->
- status: filed D11, https://github.com/xmejkal/spark/issues/1303 <!-- REQUIRED:item-status -->
- label (the repository's type label): story, on a spark card: the pixel-games repository holds no issues, and the sound lane's cards are spark issues <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P365 #467, as P917's own. The epic is the PO's choice, and he can move it <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): pixel-games <!-- REQUIRED:spark-process:slice -->

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- file the three items above · taken 2026-11-18, D11: P919 #1301, P920 #1302 and P921 #1303, each in Idea under P365 #467 <!-- REQUIRED:board-actions -->
