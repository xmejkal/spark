# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
Idea (pick a part, name its connector) → Research (the connector's pins as a record fact) → Build: assign (the cable default placed and said in one line, a conflict named or stopped) → Build: sheet and pin map (the cable step, the shared pin named) → Deploy (nothing new: the pin map is already true). The steps where a conflict shows today are in the journeys of [jobs-and-journeys.md](jobs-and-journeys.md): walk 4 steps 4, 5 and 8, walk P581 steps 3 to 6 and 9. <!-- REQUIRED:backbone -->

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | Build: assign | the assigner stops on a left conflict of kinds K1, K2 and K5. K3 (the backlight and the onboard LED on GPIO21) is named on the run as a note, never a stop, because the LED is soldered and no answer exists (PH-5, PH-15). Slice 0 takes the note reading, a note by D6. One sentence names both claims and the pin. `--json` prints a JSON answer with a `code` for the kind. This is option C of D1 as the net, with no question (D4) | J3, J5 | E ★C1, ★C2, ★C4, ★C7 | `assign_pins.py --json` on a fixture per kind: exit 1 and a JSON object with `code`, both claims and the pin, and a K3 fixture that exits 0 with the note. The P581 file stops on GPIO18, GPIO9 and GPIO38 instead of exit 0 |
| 0 walking skeleton | Research | the board record holds the GDI connector's pins (P460 #628's shape) and the screen's record says it plugs into GDI | J1 | E ★C5, ★C6 · caveat: the pins are `verified: false`, and no code reads them for placement | `boards.validate` passes the record. A reader lists the connector's eight GPIOs |
| 1 cable default | Build: assign | a part that fits a board's connector goes on the cable by default (P665, D4). The connector's pins are placed first. The strap on GPIO3 is accepted and named (P527 #726). One line says so: "screen on the GDI cable (8 pins fixed); say 'wires' to change". A "wires" line on the part in `requirements.json` places the screen like any part. No question is asked | J1, J2, J5 | D4 · H ★C8, ★C14 | the P581 file: a run with no line places DC on GPIO3, names the strap and prints the one line. A run with "wires" places the screen like any part. Neither run asks. The second build prints the same |
| 1 cable default | Build: sheet and pin map | the sheet says "plug the ribbon cable" for a part on a connector. `pins.py` carries the cable's pins. The second job of GPIO21 is named beside `ONBOARD_LED` | J1, J2 | H (ux UX-18: no cable step in `breadboard.py` today, only the record's prose line) | `breadboard.md` of the P581 project holds the cable line and no wire for DC, CS, RST, SD_CS or BL |
| 1 cable default | Build | a changed pin map after the "wires" line stops a kept `board.tsx` that no longer matches (P660 #886) | J3 | E ★C16 | a rebuild after the line changes names the difference |
| 2 the other kinds | Build: assign | K4 (two connectors) and K7 (a pin spent) as notes, by part not by connector, once a second connector is recorded | J3 | H (physics PH-6, PH-7, journey Q-D5) | a fixture with the camera connector: no stop for the DFR0664, a note for a part on IO7 |
| 2 the other kinds | Idea | when the board has a connector and the part names it, `/spark:idea` shows the default line at pick time | J1 | H (journey JO-12, JO-13) | the idea page prints the one line before `requirements.json` is written |
| 3 existing wiring | Idea and Build | K6: spark asks "what is wired?" once and keeps those pins (option D of #892), after a walk fires it | J4 | H (risks A9, RI-28) | a wired project's next build moves no pin that a wire already uses |

Slice 0 and slice 1 together are P665, the bridge of D6: D4's default with C as the net. Slice 0 alone is the net. The bridge lands on today's `assign_pins.py` (D6), and wave 6's design move carries it into the core.

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed rows for `scrum/STORY_MAP.md`, in its own shapes. Not applied.

The journey table, rows to change:

| # | step | spark today | gap |
| --- | --- | --- | --- |
| 3 | Choose parts | (as today) | a part that plugs into a connector the board fixes (GDI) is picked with no word for the connector (walk 4 G23, P663) |
| 4 | Assign pins | `assign_pins.py`, `--emit-pins` | a connector's fixed pin, an onboard part's pin and a strap are four mechanisms and no model (P663 #892). The refusal is one sentence, exit 1, not JSON. The spine says exit 2 for the same refusal |
| 10 | **Breadboard** | (as today) | the sheet has no "plug the ribbon cable" step, only the record's prose line. When the person named the pin, `pins.py` does not name a shared onboard job (P663, P332 #426) |

The slices table, a row to add under v0.10 (or a new Slice the decider names):

| # | slice | for | done when | items |
| --- | --- | --- | --- | --- |
| **v0.10 (proposed)** | **Pin conflicts**: one model in the core, shown and asked in every interface | maker | the P581 project builds with no two claims on one pin. Each conflict is named or stopped once, and the override survives a rebuild. Proved by `check_spine.py requirements.json --keep .` on P581 and a fixture per kind | P663 #892 (epic, proposed), P460 #628, P527 #726, P660 #886, and the stories in [items.md](items.md) |
<!-- EXTEND:map -->
