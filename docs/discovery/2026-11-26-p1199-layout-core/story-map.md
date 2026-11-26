# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
Plan the layout → Read it → Change it (the person or Claude) → Rebuild and keep the change → Take it back → Put it on a perfboard → Edit it on the page <!-- REQUIRED:backbone -->

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
All slices come after the MVP (council/synthesis.md S1, D-a, D-i), and the order is the PO's (Q2). Before the MVP
only the evidence runs: Q1 and the 14-day log.

| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | Change it, Rebuild and keep | the layout area born from `drawing.py`'s split, one predicate, a part edit as a fact in `.spark/layout-edits.json`, `show-layout` and `edit-layout` on the breadboard (N2) | J3, J4, J7 | H council/synthesis.md part 2, E ★C11, ★C19 | `edit-layout --dry-run` names a refusal before a write. The edit stays after a rebuild on the FireBeetle full board. 9 of 9 goldens the same |
| 1 | Change it | join edits, the Wokwi importer, `plan-layout` | J3, J4 | H synthesis part 2 | an edited breadboard.json from wokwi.com comes in as edits, and the next build keeps them |
| 2 | Take it back | the edits record as one kept-step row of the project timeline, and a take-back with its preview | J5 | H synthesis part 2, D P1193 D6 | an edit and its take-back on a scratch project, with the clash named before the yes (council/user.md US-8) |
| 3 | Put it on a perfboard | the perfboard surface from the drawer record, the pad-lattice join router with three join kinds, the same-pins check over joins (#311, N3, N4) | J2, J8 | E #311, H TL-7 | a button-light perfboard plan that the check accepts (#311's Done when) |
| 4 | Plan the layout | the goal member: `smallest` and `spread`, chosen by `layout-placement`, reported in holes across and down | J1 | H TL-8, synthesis S2, S3 | one circuit planned with each goal, two different cut sizes in holes, the same bytes on a second run |
| 5 | Edit it on the page | one thin page component for both surfaces: it draws `show-layout` and sends a drop to `edit-layout` (P1163, P1162) | J6 | E P294 finding, H synthesis D-q5 | a drag on the page and Claude's words make the same edit record |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed, not applied, for scrum/STORY_MAP.md's journey table (`| # | step | spark today | gap |`):

- Row 10, Breadboard, its gap cell gains: "a person or Claude cannot place a part or a wire through an Operation, and a full-board project has no edit path at all (P1199 #1747)".
- A new row after 10, until the PO orders the perfboard: `| 10b | Perfboard, optional, after the editor | none (P275 #311) | the perfboard as one more surface of the layout core, its joins and the boards in your drawer (P1199 #1747) |`.
<!-- EXTEND:map -->
