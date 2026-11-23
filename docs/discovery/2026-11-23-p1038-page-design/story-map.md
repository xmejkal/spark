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
| 0 walking skeleton <!-- REQUIRED:slices --> | See where it stands | the page's NOW and stand come from the project's deploy logs, and the page's stamp has a date and covers every file it reads | Job 1 | E ★C10, C11 · H that the logs give the stand without the board's MAC (A3) | `flow.py show --project .` in p934-display2 names a stand past the deploy; the stamp's date is the newest of the files read |
| 1 | See what to do next | the page shows the goal, the must lines and the last deploy (image, time, verdict), and says what spark does not check | Job 1 | E ★C13, USER-2, USER-9 | the PO reads the page of p934-display2 and names the next step without asking Claude (A1) |
| 1 | Act | no offer that changes the pins of a wired board without saying so | Job 2 | E C14 · H the pin move (not run) | the page of p934-display2 shows no Build or Pick without its warning |
| 2 | Act | the picks grouped per need, several picks at once, developer lines folded away (P1011) | Job 2 | E P1011 #1470 | a walk picks four needs in one round trip |
| 2 | See where it stands | the graphic style: tokens planned once, system fonts, D7 kept | Job 3 | E C15 · H the PO's eye (A6) | the PO's verdict on a screenshot, n = 1 |
| 3 | See it change | an open page shows the new state after Claude's step without a reload | Job 4 | E C17 · H that db fits the state (A8) | a deploy in the chat changes the open page within a minute |
| 3 | Show it | the how-to for building such an Artifact, for Claude and for a person | Job 4 | E C18 | a fresh session follows the how-to and republishes without a read error |
| later | Show it | a share for a viewer without the drawer facts | Job 3 | H the CV memory | — |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed, not applied. scrum/STORY_MAP.md has no row for the project page, and the page is not one journey step: it
shows every step. Two changes are proposed for that file. In the gap cell of step 10 (Breadboard), add "the project
page cannot see a deploy: the deploy reader is fixed at not started (P1038, ★C10)". Under the journey table, add one
line: "The project page (flow.py page, /spark:page) shows each step's state; its design is P1038 #1521." Neither change
moves a step's status, so the README journey table and tools/journey.py do not change.
<!-- EXTEND:map -->
