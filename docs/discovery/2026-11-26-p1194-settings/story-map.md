# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
Meet a choice → See whose word it is → Change it at a layer → Spark uses it and says so → (later) It follows you <!-- REQUIRED:backbone -->

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | See whose word it is | the seam class with three file layers and an empty account slot; show-settings lists the vendor order with its value, default and layer, in sentences and `--json` | J3, J5 | H A4, A5 | `show-settings --json` in a test project; a test adds a fake fourth layer |
| 1 | Spark uses it and says so | P410's check before the board as a setting, per project with a personal default; deploy's first line names the check and whose word it is | J2 | E #536 | the deploy's first line in a walk |
| 2 | Change it at a layer | set-setting with the layers each setting allows, and a refusal that names the file | J2, J3 | E ★C5 | the refusal test of A6 |
| 3 | Meet a choice | a setting with no value asks once, with "use spark's default" kept; first for P1193's author | J1, J5 | E ★C6 ★C11 | the walk of A8 |
| 4 | See whose word it is | the page: the settings list and each step's fold, changes as sentences to Claude | J3 | H A1 | the prototype walk of A1 on the built page |
| 5 | Meet a choice | the shops and the vendor order as personal defaults; the tools list shown read-only | J1 | E ★C3 | the count of A2 falls to 0 repeats |
| later | It follows you | the account layer with a GitHub sign-in (N1) | J4 | D6, D7 | — |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed for scrum/STORY_MAP.md, slice 10 The store, not applied: one row per slice 0 to 5 above, after the PO's yes to items.md and in the same change as the board's Slice field.
<!-- EXTEND:map -->
