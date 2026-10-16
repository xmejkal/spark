# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
Build → See it on my board → Edit the layout → Wire or solder it → Fix a part in the catalogue → Save and share <!-- REQUIRED:backbone -->

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | See it on my board | S0: the base in mm (surface, holes, join groups, placements, connections, layout), breadboard first; `breadboard.json` stays byte-equal | J1, J7 | H council/tech-lead.md TL-1, TL-2, TL-35 | the existing tests pass and the Wokwi file's sha256 is unchanged |
| 0 | See it on my board | S1: P268's SVG on the base, with spark's own pictures, shown inside `breadboard.md` | J1, J5 | D-a, H TL-35 | `breadboard.svg` for button-light, seen in VS Code and on GitHub |
| 0 | See it on my board | S2: one circuit source, and a check that a layout's joined holes equal the circuit's points | J7 | E TL-7 | a fixture with a wrong jumper fails the check |
| 1 | See it on my board | S3: the layout file and a read-only TS viewer, one bundled file, as a local page and an Artifact, with schematic and PCB tabs from tscircuit's circuit-to-svg | J1, J7 | E TL-10, TL-19, TL-20 | the same file opens in both hosts |
| 1 | Edit the layout | S4: drag a part or a jumper on the breadboard, check in the page, save, and the next build keeps the edit | J3, J6 | H TL-18, TL-26, ★C5 | edit, rebuild, the edit survives, a breaking edit is reported |
| 2 | Wire or solder it | S5: stripboard: the surface, cuts and links, a planner | J2 | D-b, H TL-35 | a button-light stripboard layout that passes S2's check |
| 2 | Wire or solder it | S6: plain perfboard: grid routes, back wires and bridges | J2 | D-b, H TL-35 | the same, on perfboard |
| 3 | Fix a part in the catalogue | S7: the catalogue editor: pins in mm, joined pins, polarity, picture, with pictures from the web kept in the store | J4, J5 | E council/data.md DATA-1 to DATA-24 | a module edited and drawn in two views |
| 3 | Save and share | S8: sharing a layout or a record, decided with P178 | J6 | E #123 | — |
| later | all | Electron, only if the local page falls short | J3 | H TL-35 | — |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed, not applied, for `scrum/STORY_MAP.md` line 45 ("v0.13 and later"): its "breadboard to perfboard to PCB" becomes "views and editors for every stage (P269 #304): the base, the SVG, a viewer, an editor, stripboard and perfboard, the catalogue editor". The S5 and S6 stories sit on the board's existing Slice "7 Perfboard to PCB".
<!-- EXTEND:map -->
