# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
Know each part's body → See the board in 3D → Export it → Open it in a CAD tool → Make a case → Print and fit. J6 (switch a strategy with one setting) runs under every activity. <!-- REQUIRED:backbone -->

Before slice 0, with no product code: tests T1 and T2.

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton: a spark board in 3D, in Fusion <!-- REQUIRED:slices --> | Know each part's body | the z facts have one word each, one rule and one question, and the amplifier fixture's three records hold them with a source | J1, J7 | E ★C1 · H Q14 | the words.md rows, and `parts.py --validate` naming the records whose `facts.thickness_mm` holds an overall height |
| 0 | Know each part's body | each module and the Mcu get a box body from the record through the body-maker chain. A missing fact is named, never a 16 x 12 mm default | J1 | E ★C2 · E AR-18 | the build's finding for a record with no z fact |
| 0 | See the board in 3D | the same body shows in tscircuit's 3D tab and in the GLB, under its reference | J2 | E ★C21 | a screenshot of the tab on the amplifier fixture |
| 0 | Export it | `export-board` writes `board.step`, checks every body first and never reaches the network | J3 | E ★C3 ★C22 | the JSON answer, and the solid names in the file |
| 0 | Open it in a CAD tool | the PO opens `board.step` in Fusion and sees each part at its real size, by name | J3 | H ★C4 ★C10 | his screenshot of the browser tree |
| 0 | every activity | `body-makers`, `board-exporter` and `export-forms` each have a name, a default and a layer, and a Fake member runs in the tests | J6 | H | the plan's settings table and the tests |
| 1 a case for a board I own | Know each part's body | the FireBeetle's record holds its z range and each opening's z, measured by the PO | J1, J7 | E C26 ★C25 | the record's lines with their sources |
| 1 | Make a case | `show-board-mechanics` gives the outline, thickness, holes, bodies and openings as JSON, and a null is named and asked | J7 | E US-19 · H AR-12 | the JSON for his FireBeetle, and one cold Claude run (A9) |
| 1 | Make a case | `make-case` gives a base and a lid through `CaseMaker`, and the answer names each number and whose word it is | J4 | E ★C5 ★C19 | the answer's lines |
| 1 | Print and fit | the case file opens in his slicer, prints, and the board fits | J5 | H A2, A10 | a photo of the board in the case with a calliper reading |
| 1 | every activity | the Case step of the journey gets a phase reader, and README and `tools/journey.py` change in the same PR | J2 | E AR-23 | `tests/test_journey.py` |
| 2 a kept body file | Know each part's body | `parts.py --keep-body` keeps his own STEP in the store, and `StoredBodyMaker` shows it with its credit | J1 | E ★C7 | his DFRobot file on the board, and no body file in the project |
| 3 the 3D page | See the board in 3D | the bin project's viewer, ported, written again at each export | J2 | E ★C18 | `board-3d.html` opens offline |
| 4 Claude in a CAD tool | Open it in a CAD tool | the `cad-tool` role, a Fusion entry that is off, and one chat offer | J3, J4 | E ★C11 | one session where Claude opens the export in his Fusion |
| 5 a case for a spark board | Make a case | how a module sits on the carrier is a fact, each part's opening is placed, and a fit check reads the mechanics | J4, J7 | E PHY-2 · E ★C23 | a case that fits a real carrier board, once one exists |
| later | Know, See, Make | the perfboard's filler (after P1199 #1747 and P275 #311), a jig for P1198 #1746, a body with the photo on its top face, a KiCad writer (#1728) | J1, J2 | E C16 · H | one line each on #1745 |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
The map has no row for the board's Slice "9 An enclosure" (E scrum/STORY_MAP.md:32-46, and the board's Slice field read with `gh`). Rows in the map's own shapes:

Journey table, change row 7 and row 12:

| # | step | spark today | gap |
| --- | --- | --- | --- |
| 7 | See it | `tsci dev`, Wokwi for VS Code (P65, P67) | a module shows no body in 3D (P1185 #1729) |
| 12 | Case — a body per part, a 3D export, a CAD tool, a printed case | `tsci export -f step` and `-f glb` run by hand. No Operation | a body per part (P1185 #1729), `export-board` (P1183 #1727), the mechanics and the case (P1197 #1745) |

Slices table, add one row after "v0.13 and later":

| # | slice | for | done when | items |
| --- | --- | --- | --- | --- |
| **9** | **An enclosure** — the board's Slice "9 An enclosure", after the MVP | maker first, hobbyist H | proposed: for one real board, one Operation writes a STEP that opens in Fusion 360 with each part as a named body at its real size, and a case made from the records' facts prints and fits | P1197 #1745 (epic), P1198 #1746 (parked), the new cards of items.md. P1185 #1729 and P1183 #1727 stay in Slice 7 and are extended |

"Journeys, by release", change the J9 line: "J9, the PCB and a printed body from the same conversation: later (the north star, P203 #163). P1197's jobs J1 to J7 are in docs/discovery/2026-11-26-p1197-3d/jobs-and-journeys.md."

One word to settle: the map and the board say "Enclosure", and the code's step says "Case" (E `flow_codes.py:481`). The architect's opinion: "Case" in the map's row. The board's Slice name is the PO's.
<!-- EXTEND:map -->
