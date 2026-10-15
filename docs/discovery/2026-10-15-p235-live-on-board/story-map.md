# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
Make the board enterable → Open a live session → Try a line → See what it says → Run a file → Read a pin → End the session → Keep what was learned → Reach it without a cable <!-- REQUIRED:backbone -->

The backbone follows Jobs 1 to 4 in jobs-and-journeys.md. "Open a live session" is the gate of D29 and D43. "Reach it without a cable" is WebREPL and OTA, kept for their own discovery (D31).

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | Open a live session | P252, the bench: what a reset does to pins, whether `resume` keeps a value, what "ends with a reset" means (D10) | job 1, job 4 | H ★C4, ★C7 | a bench log in docs/observations/ |
| 0 walking skeleton | Make the board enterable | P251, the cure: a silent console after power-on gets a USB-side reset and one retry, said and logged (D6, AT187) | job 1, job 4 | E docs/observations/2026-10-15-p235-reach-test.md | 10 replugs, 10 of 10 reached (A11) |
| 0 walking skeleton | Open a live session | P253, the grant: one yes in the PO's terminal for a board and a time limit, one look at the grant (D12, D13) | job 4 | E ★C5 | a grant found inside its limit and refused after it |
| 0 walking skeleton | Try a line | P254, the C6 record's USB and flash pins, and a try that names one is refused (D14) | job 1, job 3 | E ★C7 | a refused try that names GPIO12, with its source |
| 0 walking skeleton | Make the board enterable | P246, a new board-only project that reads its console and shows what a try changed (D16) | job 1, job 4 | E ★C2 | it passes in Wokwi and prints `ready` on the bare XIAO C6 |
| 0 walking skeleton | Try a line, End the session | P247, `spark live --code ... --json` inside a grant: reached, not reached or unknown, the reset from P252, `LiveTryResult` as JSON (D9, D11, D15) | job 1, job 4 | E ★C1 | a log of one try by Claude on the XIAO C6, and fake-run tests |
| 0 walking skeleton | Keep what was learned | P256, the upstream report (D6, D8), and P255, a Decorator row in developing.md (D8) | — | E AT187 | the issue's URL, and the merged docs PR |
| 1 | See what it says | P248, a bounded console read that says opening the port can restart the board | job 2 | E ★C6, ★C12 | a kept read of a boot on the XIAO C6, with the ROM line |
| 2 | Run a file | P249, run one local file from memory | job 1 | E ★C8 | one file run, and the board's files still match the last passed run |
| 3 | Read a pin | P250, read a pin by name, P254's pins refused | job 3 | E ★C7 | a read of the BOOT button on the bare board |
| 4 | Open a live session | P242 (#249) reuses P253's grant as its standing yes | job 4 | D D12 | P242's own proof |
| later | Reach it without a cable | WebREPL and OTA, in their own discovery | job 1, job 2 | E ★C9 | — (D31) |
## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed, not applied (D17 applies it at the close, after the PO confirms). In scrum/STORY_MAP.md, under "The
slices, in order", one new row comes before "v0.13 and later", and that row drops "live on the board (P235 #224, ...)".
The board's Slice option needs the PO's word (no option fits today).

| # | slice | for | done when | items |
| --- | --- | --- | --- | --- |
| **Live 0** | **Live on the board, the walking skeleton**: Claude runs a line of code on the PO's running board | hobbyist | on the bare XIAO C6 with P246's project, the PO types one grant in his terminal, and Claude's `spark live --code ... --json` reaches the board, cures a silent console after a power-on, refuses the USB and flash pins, ends with the chosen reset, and keeps a log (`docs/discovery/2026-10-15-p235-live-on-board/story-map.md`) | P252, P251, P253, P254, P246 (#260), P247, P256, P255 |

The journey table in the same file gains nothing: live work comes after step 10 (Breadboard) and is not a new step.

The journeys J4 and J6 already point at P235 in scrum/STORY_MAP.md (lines 67-68): "J4, debug on the board live:
later, the epic P235 (#224)" and "J6, try things live over USB or Wi-Fi: later, the epic P235 (#224)". Proposed:
"later" becomes "Live 0 (J6 over USB), Live 3 (J4)", and J6's Wi-Fi part stays later (D31).

P218's deploy map (docs/discovery/2026-10-13-p218-deploy-and-board/story-map.md) has two rows that move here (D17):
slice 4 "Try things live" (live reads and tries over USB, P222 #204) becomes this map's slice 0, and slice 6 "Reach it
without a cable" (OTA and a Wi-Fi REPL) becomes this map's "later" row. Slice 4's other row, "Change it and put it on
again" (update files without a full flash, D20), stays with P218. A closed discovery's folder is history, so the
proposal is one line under each moved row there: "moved to P235, docs/discovery/2026-10-15-p235-live-on-board".
<!-- EXTEND:map -->
