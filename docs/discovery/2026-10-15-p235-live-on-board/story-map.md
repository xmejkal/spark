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
| 0 walking skeleton <!-- REQUIRED:slices --> | Make the board enterable | the board-only bench project reads its console without waiting and answers a typed line, so Ctrl-C gets through, as the rule in docs/guide/agents.md:577-578 already says. blink-c6 already does both (blink.py:77-81), so this row is done if Q13 picks blink-c6 | job 1, job 4 | E ★C2 | the project passes in Wokwi and prints `ready` on the XIAO C6 (P246 #260) |
| 0 walking skeleton | Open a live session | the bench rung: 10 `exec "print(1)"` on the running firmware at least one minute after a passed deploy and 10 after re-plugs, each answer kept. It also settles what a reset does to a pin and whether `resume` keeps a value (P222 narrowed) | job 1, job 4 | H ★C3, ★C4 | a bench log in docs/observations/ with each count |
| 0 walking skeleton | Try a line | one gated call runs a short snippet with `BoardConnection.run_code` and says reached, not reached or unknown in mpremote's own words. It keeps the board's answer in a log beside sim/runs/board/ | job 1, job 4 | E ★C1, H ★C5 | the log of one try on the XIAO C6, and fake-run tests |
| 0 walking skeleton | End the session | the try ends with the reset the PO picks (Q5) and says what stayed changed on the board | job 1, job 4 | H ★C4, ★C7 | the end line in the same log |
| 1 | See what it says | a bounded read of the console for N seconds. It says that opening the port can restart the board, and it reports download mode with the existing DownloadModeProbe | job 2 | E ★C6, ★C12 | a kept read of a boot on the XIAO C6, with the ROM line |
| 2 | Run a file | run one local file from memory (`mpremote run`). It says that the file is not on the board afterwards | job 1 | E ★C8 | one file run on the XIAO C6, and the board's files still match the last passed run |
| 3 | Read a pin | the board record gains the USB and flash pin roles. A read names the pin by name and number and refuses the denied pins (Q8) | job 3 | E ★C7 | a refused read of GPIO12, and a read of the BOOT button on the bare board |
| 4 | Open a live session | the agent opens a session under a stored grant that a person gave in a terminal, shaped with P242 (#249) | job 4 | H ★C5 | a session that Claude opens without a new yes, inside the grant's limits |
| later | Reach it without a cable | WebREPL and OTA, in their own discovery | job 1, job 2 | E ★C9 | — (D31) |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed, not applied. In scrum/STORY_MAP.md, under "The slices, in order", one new row replaces P235's mention in the
row "v0.13 and later". The board's Slice for it needs the PO's word (no Slice option fits today).

| # | slice | for | done when | items |
| --- | --- | --- | --- | --- |
| **Live 0** | **Live on the board, the walking skeleton**: the board's Slice to be named by the PO | hobbyist | on the bare XIAO C6, one gated call runs a line on the running board, says reached or not in mpremote's words, ends with the chosen reset, and keeps a log (the P235 map, `docs/discovery/2026-10-15-p235-live-on-board/story-map.md`) | P246 (#260), P222 (#204, narrowed), new stories from items.md |

The journey table in the same file gains nothing: live work comes after step 10 (Breadboard) and is not a new step.

Not mapped yet: #224 says P218's journeys J4 (debug on the board live) and J6 (try things live) and its deploy map's slices 4 and 6 belong here. Their move, and the update of scrum/STORY_MAP.md and the Miro board, wait on Q25.
<!-- EXTEND:map -->
