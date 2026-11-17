# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
Say the goal → Agree the needs → Pick the parts (with where to get them, what to replace) → Test the facts on the bench → Build the board files (schematic, pins, sheet; the PCB later) → Wire the breadboard → Write the firmware → Simulate → Put it on the board → Change it and go round again <!-- REQUIRED:backbone -->

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | Change it | a change in the middle needs no file deleted or edited by hand: the build replaces its own unedited board.tsx, and the requirements drop what no pick explains, on a yes | J2 | E ★C29 (counted by the refuter) | a need added and one dropped on a scratch copy of a walk project, with no hand action between the commands |
| 0 | Change it | `flow.py show` marks everything made from a changed thing as out of date, with its true cause | J1, J2 | E ★C1 (one project) | the same scratch copy: every phase made from the changed thing reads out of date with its cause, in the lines and in the JSON |
| 0 | Change it | a skipped stage or an unjudged phase never shows a tick | J1, J6 | E ★C10 (a board-only project) | the button-and-LED walk folder's build line shows no tick for skipped stages |
| 1 a change that is safe at the bench | Build the board files | the parts that stay keep their pins when a part is added, and a pin that had to move is named as moved | J2 | E ★C4 (simulated; one board model) | an I2C part added on a copy of the sound demo: every moved pin is named, and the signals on no bus keep their pins (the bus lines wait for P868 #1235) |
| 1 | Write the firmware | the firmware's pin names are compared with the pin map | J2 | H ★C5 (not run) | a main.py that names a dropped pin reads as a problem in `flow.py show` |
| 1 | Wire the breadboard | after a change, the sheet gives the order of power, flash and wire | J2 | H ★C6 (not measured) | the sheet of a changed design opens with the order line the PO confirmed (Q11) |
| 2 the bench as witnesses | Put it on the board | the flow shows what spark last recorded of the wiring and of the deploy, never as a pass | J1, J2 | E ★C9 (never what is on the bench) | the deploy phase reads "recorded: this project's image of <time>" or "none recorded" |
| 2 | Change it | a refused build keeps the last good outputs | J3 | E ★C7 (by design) | after a refused build the earlier pins.py and sheet are still there, marked out of date |
| 3 the PO's phases | Pick the parts, Test the facts | the facts to test are a phase before the wiring; the shops and the part to replace are views of the parts | J4 | H ★C12 (counted by the lens) | the page's rail shows the phase, and `parts.py --unverified`'s lines are on it |
| later | every activity | one value for an offer and a `next` step, from which a framework's graph can be made | J6 | H ★C13 (a contract) | one sentence: a generated graph walks a basic project |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed in words, not applied, and not yet in the file's table shape: scrum/STORY_MAP.md defines the slice "v0.11 Change it and put it on again" as a firmware edit with one receipt line (council/existing.md:34, EX-20, read by the lens). The rows of slices 0 to 2 above would widen that slice to a change of the design, or would sit in a new slice. Which of the two is Q12, so the rows in the file's own shape wait for that answer.
<!-- EXTEND:map -->
