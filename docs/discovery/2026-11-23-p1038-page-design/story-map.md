# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
Come back → See where it stands → See what to do next → Act (pick, wire, build, deploy) → See it change → Show it <!-- REQUIRED:backbone -->

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | See where it stands | in the core, under P793: the deploy reader reads the project's logs and shows the witness's facts, with no tick on "ready unknown" (D7, D10) | Job 1 | E ★C10, A3 met for one board | `flow.py show --project .` in p934-display2 shows the last deploy's time, image and verdict |
| 1 | See where it stands, Act | the page's first slice: one NOW, several picks at once and the picks per need, developer lines folded, the brief's goal and must lines, a dated stamp over every file the page reads (a list separate from the click fingerprint), the build it draws from (Q13), and the how-to's "read page.html whole" defect fixed (D11, D5, D12) | Job 1, Job 2 | E P1011 #1470, C11 · H A5 | the PO reads the page of p934-display2 and names the next step; a walk picks four needs in one round trip |
| 1 | Act | no offer that changes the pins of a wired board without saying so | Job 2 | E C14 · H the pin move, not run | the page of p934-display2 shows no Build or Pick without its warning |
| 2 | See where it stands | the graphic style: tokens planned once, system fonts, D7 kept (D6) | Job 3 | E C15 · H A6 | the PO's verdict on a screenshot, n = 1 |
| 2 | See it change | the page is written again when a fact changes, by the trigger Q12 sets | Job 4 | E C11 · H A9 | at the walk's end page.html and `flow.py show --json` name the same stand |
| later | See it change | a live page as a consumer of the core's events: designed now, built later (D5) | Job 4 | E C17 · H A8 | a deploy in the chat changes an open page |
| later | Show it | a share for a viewer, on P834 (D9) | Job 3 | H the CV memory | — |

The Artifact how-to is no slice: it is a doc in the design, and each slice's PR keeps it current (D12). The order
follows D11: slice 0 runs in the core in parallel with, or before, slice 1.

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed, not applied. scrum/STORY_MAP.md has no row for the project page, and the page is not one journey step: it
shows every step. Two changes are proposed for that file. In the gap cell of step 10 (Breadboard), add "the project
page cannot see a deploy: the deploy reader is fixed at not started (P1038, ★C10)". Under the journey table, add one
line: "The project page (flow.py page, /spark:page) shows each step's state; its design is P1038 #1521." Neither change
moves a step's status, so the README journey table and tools/journey.py do not change.
<!-- EXTEND:map -->
