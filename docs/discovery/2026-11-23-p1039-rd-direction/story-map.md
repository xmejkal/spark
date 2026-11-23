# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
The maker's line: Shape the idea → Pick the parts → Build and check → Wire the breadboard → Write and test the firmware → Deploy → Iterate → Order a PCB → Make an enclosure. Across every activity, the team's loop: Walk → Fix → Teach the agents → Measure. <!-- REQUIRED:backbone -->

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
This epic builds nothing, so slice 0 is the thinnest set of proofs that touches all five questions at no build cost. The later slices are an order to test, in the architect's opinion, not a plan. "Every activity" means the whole backbone. J7 is the job proposed in jobs-and-journeys.md.

| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | every activity | the PO reads one picture of the line, the architecture and the options, and answers the queue | J6 | D the PO, 2026-11-23, #1522 (the request) | a D row in the brief that confirms the understanding |
| 0 | every activity | the seams S1 to S7 stand as acceptance lines on the open pieces of P793 #1105 | J2, J5 | H ★C3, ★C7, ★C8, ★C9, ★C11 (each with its caveat) | the comment on #1105 |
| 0 | Measure | the riskiest test says which direction a project reaches for | J3 | H A1 | a Results row: the occasions the PO names, and the 72 walk rows sorted by cause |
| 1 the line has an end | Deploy | a recorded deploy reads as recorded in the flow, on the page and in `--json` | J1, J5 | E ★C19 (shows the product) | `flow.py show` on a deployed walk project |
| 1 | Iterate | after the first deploy the flow says where the gadget stands and what a change makes out of date | J7 (proposed) | E ★C20 (an account, n = 1) | a change on a scratch copy of a deployed project reads out of date with its cause |
| 2 an agent walks on spark's pages alone | Teach the agents | the entry page names the call that says where a project stands, and each untaught tool gets a line | J4 | E council/ux-and-ai-ux.md:24 (UX-2), ★C15 (accounts, n = 1) | the page and one grep |
| 2 | Walk | one walk runs only through spark's commands, skills and agents (P711 #960) | J3, J4 | E ★C15 (a weak sign) | the walk's rows, sorted by cause |
| 2 | Teach the agents | a new script or flag fails the hook until an agent page names it | J4 | E ★C13, ★C14 (a lower bound) | a red hook on a scratch branch with an untaught flag |
| 3 one measured row | Measure | one fixed task runs 3 times and spark's own facts grade it | J3 | H A4, ★C18 (inside Claude Code only) | the three results and their tokens |
| 3 | Measure | one row of the model table rests on a result | J3 | H A5, ★C17 | the row with its pointer |
| 4 a second binding | every activity | LookAtBoard runs as an MCP tool and as a LangGraph node with 0 lines changed in the core (P417 #545) | J2, J5 | H A9, ★C9 (not run in a second interface) | the spike's finding |
| 4 | every activity | the job of `/spark:build` runs in one other harness | J2 | H A2, ★C5 (read through a summariser) | exit 0 with no source file read |
| later | Order a PCB, Make an enclosure | the order and the enclosure enter as phases with their effect words (P79 #16, P203 #163) | J1 | H ★C22 (a reading of the code) | one sentence each |
| later | every activity | a local model reads an answer and names the next step | J2 | H A3, ★C27 (none ran spark's tasks) | 9 of 10 golden answers |
| later | every activity | one local server streams to a live page and to the HTTP MCP | J5 | H ★C8 | — |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed, not applied. Three changes to scrum/STORY_MAP.md, each waiting on a question of the brief.

1. The journey table gets one new row between step 10 and step 11 (waits on Q3):

| # | step | spark today | gap |
| --- | --- | --- | --- |
| 10a | **Iterate**: change the gadget after it runs (a new behaviour, a battery, a bench trial) | the flow's nine phases end at deploy, and the deploy phase reads "not started" after a deploy | a deploy that reads as recorded, and a change that marks what it makes out of date (P867's slices) |

2. The slices table keeps its rows. The row "v0.13 and later" gets one more sentence (waits on Q4, option a): "Past the MVP (P1039 #1522), one line each until a project reaches for it: the line's end and iteration, generally runnable (P217 #199, P227 #213), the agents' knowledge and its measure (P200 #153, P711 #960), a local AI (no card)." No new Slice option is proposed. If Q4's answer is (b), the spikes need a Slice, and the decider is asked for a new one.

3. "Journeys, by release" gets one line (waits on the proposed J7): "Proposed, new, from P1039: the gadget changes after its first deploy: after v0.11."

A matching line in scrum/VISION.md's "later" row is part of Q4's option (a). It is named here only because the map and the vision change in one PR. The journey rows 9 to 11 of the map read behind the product (H, the architect's reading, in the brief's Found on the way), and this delta does not touch them.
<!-- EXTEND:map -->
