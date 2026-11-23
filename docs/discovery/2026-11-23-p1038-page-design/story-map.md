# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** the epic's map by D26 (delegated, the PO's to change); the delta to scrum/STORY_MAP.md below stays proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
Come back → See where it stands → See what to do next → Act (pick, wire, build, deploy) → See it change → Show it <!-- REQUIRED:backbone -->

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | See where it stands | P1043 #1533, in the core under P793: the deploy reader reads the project's logs, shows the witness's facts with no tick on "ready unknown", and a run with no read-back shows what its log knows (D7, D10) | Job 1 | E ★C10, A3 met for one board | `flow.py show --project .` in p934-display2 shows the last deploy's time, image and verdict, and the read-back case |
| 0 walking skeleton | See it change | P1035 #1518, core piece 3: a core hook writes page.html again on disk after each run that writes to a project (D16), with no GitHub call (D23); it covers the copy on disk only, the published copy waits for Claude's republish, and #1518's text must name D16 | Job 4 | E C11 · H A9 | after a deploy run, page.html on disk and `flow.py show --json` name the same stand |
| 1 | See where it stands, Act | P1038's first page slice, split into stories (1a structure and words, 1b the brief lines with D15's field, 1c the stamp and the named build, 1d several picks at once, decided with P829 #1187 because it is click-path work): one NOW, several picks at once and the picks per need, developer lines folded, the brief's goal, must and decided lines (D15), a dated stamp over every file the page reads, the build it draws from with a mismatch shown (D17, P1045 #1535), partial results worded plainly (QA5), and the how-to's "read page.html whole" step fixed (D11, D12) | Job 1, Job 2 | E P1011 #1470, C11 · H A5 | the PO reads the page of p934-display2 and names the next step; a walk picks four needs in one round trip |
| 1 | See what to do next | two stories: core code reads the project's open GitHub issues into a dated file when /spark:page republishes, then a reader shows them beside the phases, marked as the project's, titles and labels only, none ranked (D19, D23) | Job 1 | E QA2 · H A2's grouping (T-9) | the page of p934-display2 lists its open issues with the read time; with no file it says "issues not read"; a deploy run makes no GitHub call |
| 1 | Act | P1044 #1534: no offer that changes the pins of a wired board without saying so | Job 2 | E C14 · H the pin move, not run | the page of p934-display2 shows no Build or Pick without its warning |
| 2 | See where it stands | the graphic style: tokens planned once, system fonts, D7 kept (D6) | Job 1, Job 3 | E C15 · H A6 | the PO's verdict on a screenshot, n = 1 |
| later | See it change | a live page as a consumer of the core's events: designed now, built later (D5) | Job 4 | E C17 · H A8 | a deploy in the chat changes an open page |
| later | Show it | a share for a viewer, on P834 (D9, D20) | Job 3 | E QA4 (no detail) | — |

The Artifact how-to is no slice: it is a doc in the design, and each slice's PR keeps it current (D12). Slice 0 runs in
the core in parallel with slice 1 (D7). After slice 1, one walk runs A1's and A9's tests, a fresh session follows the
how-to in it, and the PO decides again before slice 2 (D25). Each fact on the page is also in `flow.py show --json` (D22).

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed, not applied. scrum/STORY_MAP.md has no row for the project page, and the page is not one journey step: it
shows every step. Two changes are proposed for that file. In the gap cell of step 10 (Breadboard), add "the project
page cannot see a deploy: the deploy reader is fixed at not started (P1038, ★C10)". Under the journey table, add one
line: "The project page (flow.py page, /spark:page) shows each step's state; its design is P1038 #1521." Neither change
moves a step's status, so the README journey table and tools/journey.py do not change.
<!-- EXTEND:map -->
