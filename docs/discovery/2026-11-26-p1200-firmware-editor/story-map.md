# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied. D2 to D5 trimmed it <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
See the firmware → See what the board runs → Change a value → Make the image → Deploy → Read the board back <!-- REQUIRED:backbone -->

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | See the firmware | the page's fold shows main.py and pins.py as masked, read-only text, after P1004 (items.md, item 1, D8) | J1 | H A1 | `show-firmware --json` and the fold on a scratch project |
| 0 | See what the board runs | the deploy phase's line, as today | J3 | E council/synthesis.md, n6 | the page of a project with a board log |
| 0 | Change a value | one "Ask Claude" sentence with Copy (item 5) | J2 | D3 | the sentence pasted into the chat changes the value |
| 0 | Make the image | Claude runs `flash_image.py` in the chat, as today | J2 | E commands/deploy.md:118-124 | the new image's sha256 in the look |
| 0 | Deploy | the look, the line to type with Copy, his typed yes, as today | J4 | E commands/deploy.md:2 | the board log |
| 0 | Read the board back | the deploy's verify stage, as today | J3 | E scripts/spark/bench/deploy_stages.py:28 | "ready seen" on the page |
| 1 | See what the board runs | each file "matches", "differs" or "not read" (item 4) | J3 | H A3 | the page after a deploy that ended "ready unknown" |
| 2 (dropped by D3) | Change a value | `save-firmware` from the CLI, with the guard and a kept step (item 17) | J2, J5 | H A2 | a refused save after Claude changed the file |
| 3 (dropped by D3) | Change a value | the edit on the page, carried as a payload | J2, J5 | H A2 | the same refusal, from the page |
| 4 (dropped by D4) | Deploy | a second host, chosen by the spike (item 6) | J4 | H A7 | the spike's finding |
| 5 (dropped by D4) | Deploy | the page starts a deploy inside a standing grant (D-q3 b) | J4 | H | the board log names the grant as the yes |

Slice 0 adds one new story and one offer row. Every other step of the backbone already runs on the one host that exists. D5 keeps the show slice of slice 0 (P1242 #1799), built after the MVP walk and after P1004 (D8). The rest of slice 0 runs today. Slice 1's read-back is a comment on P1217 #1766 (D4). Slices 2 to 5 are dropped.

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
proposed, not applied: one row in scrum/STORY_MAP.md under the page's activity, "the page shows the firmware as read-only text after P1004 (P1242 #1799)". D3 to D5 dropped the other slices
<!-- EXTEND:map -->
