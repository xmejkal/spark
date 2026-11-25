# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
Open a session → Start the project → Decide the records → Keep each decision → Take a step back <!-- REQUIRED:backbone -->

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | Start the project | init writes the ignore list first, with or without a repository | job 1 | D D6, E brief ★C15 | a scratch init: `git check-ignore` names the rules link, the flash image and `sim/runs/` |
| 0 walking skeleton | Start the project | init is a core Operation that calls the exchangeable strategy. The git strategy makes the folder in the projects home and the repository with a first commit, and a human strategy leaves the folder to the person | job 1, job 4 | D D5, D6, D10, E brief ★C13 | `--json` of one start in a scratch home: the folder, the repository and one commit |
| 0 walking skeleton | Start the project | a setting in the person's store turns the repository off once, and the strategy then keeps nothing and says so | job 1 | D D6 | a scratch init with the setting off: no `.git`, and one plain line |
| 0 walking skeleton | Keep each decision | the brief write is kept through the strategy, with a plain line and the id in the JSON | job 2 | D D5, D11, E brief ★C21 | the A1 test (P1155), run once the rows above exist in scratch code, against its pass line (D13): 3 of 3 kept lines |
| 0 walking skeleton | Open a session | the team's process moves to `scrum/`, the PO's lines to a file of his in `scrum/`, and the store's `rules.md` links to it | job 3 | D D3, D4, E brief ★C5 | 29 of 29 links resolve, and the linked file names no card, lane, hook or PR |
| 1 | Keep each decision | after the A1 test's result: the needs, the picks, the requirements and the board are kept, one step per decision | job 2 | D D8 | a replay of one fixture walk: one step per decision, a clean tree (A6) |
| 1 | Take a step back | a read-only Operation lists the kept steps | job 2 | D D9 | its `--json` on the scratch walk |
| 1 | Take a step back | a take-back Operation: the person's yes through the core, then the strategy takes the step back, and a pick's take-back also restores its hold in the store | job 2, job 4 | D D7, D8, D9 | the A2 spike's pass line, once the PO sets it |
| 2 | every activity | a second strategy (by hand, or a Fake) behind the same seam | job 4 | D D5 | a Fake strategy in the tests, with no change to the areas (A7) |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed for `scrum/STORY_MAP.md`, "The journey, and what spark offers at each step", not applied:

| # | step | spark today | gap |
| --- | --- | --- | --- |
| 1 | Install, start a project | README; `/spark:init` (`init_project.py`) | add: no step makes the folder or its repository, no ignore list. This discovery's slice 0 (init calls the strategy, the git strategy makes the folder and the repository, the ignore list) |
| 3 | Choose parts | `/spark:idea` (M, C, L) | add: a decided record is not kept as a step, and the only way back is the brief's commit. This discovery's slice 1 |
