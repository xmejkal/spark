# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
See who uses the board → Take it → Use it → Give it back → The PO's bench first <!-- REQUIRED:backbone -->

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 (a folder name) | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | See | one command lists each board on USB with the projects that keep it, its last deploy and its grants, and opens no port | J1 | E ★C12 (some serials give cannot tell), council/tech-lead.md DIR-4 | the command's output with one board on USB |
| 1 | See | a tool that registered reports its deploy, so the view has a line for the game box | J1 | H D4, C4 | the view names pixel-games after a `box.py` deploy |
| 2 | Take, Give back | a record of the holder: the project, the board and the end time, with a take and a release | J2 | H ★C13 (one ended grant in one store) | the view shows the holder and the end time |
| 3 | Use | spark's board tools read the record and say whose board it is | J2 | H | a run in a second project prints the line |
| 4 | Give back | the record names what was on the board before the take | J3 | H C10 | the release prints what the holder owes |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
No row of `scrum/STORY_MAP.md` changes yet. The PO ordered the filing of slices 0 and 1 (D11). When they are filed, their cards join the line "Team tools" of that file.
<!-- EXTEND:map -->
