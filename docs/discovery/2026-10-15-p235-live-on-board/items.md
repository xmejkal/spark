# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

Every item is a proposal. Nothing is filed. An item on an existing card goes into its body or a comment once the PO
says yes. A new item takes the next free number, P247 on 2026-10-15 (read from `gh issue list --state all`), read
again at filing. No Slice option of the board fits P235 today, so each item asks the PO for a new one (story-map.md,
delta). The order follows the proposed map and changes with Q2 and Q3.

## P246 (#260) — the board-only project reads its console and answers a typed line
- type: story, on the existing card <!-- REQUIRED:item-type -->
- needed by: "then we'll make another testing project without anything" (the PO, 2026-10-15, #260) <!-- REQUIRED:needed-by -->
- value proven by: the project passes in Wokwi, prints `ready` on the bare XIAO C6, and answers a typed line, as docs/guide/agents.md:577-578 already asks. If Q13 picks blink-c6, this card closes with blink-c6 as the bench <!-- REQUIRED:value-proven-by -->
- depends on: Q4, Q13 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P235 (#224), as today <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0) <!-- REQUIRED:spark-process:slice -->

## P222 (#204), narrowed — four bench questions on the bare board
- type: spike, on the existing card
- needed by: "so that might really allow us to do some cool stuff reagrding updates, debugging, connection with agents" (the PO, 2026-10-13, #204)
- value proven by: a finding in docs/observations/ with sources: the reach rung's count (A1), what a soft reset does to the LED pin (A5), whether `resume` keeps a value (A10), and 20 port opens with the ROM line (A6). belay and the MCP plugin (D30) move to a later spike if Q3 says so
- depends on: P246's project, Q1, Q3
- status: proposed
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P235 (#224), as today
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## P247 (new) — a live try: one gated call runs a line on the running board
- type: story
- needed by: "just running code live on the device when connected" (the PO, 2026-10-13, #224)
- value proven by: on the XIAO C6, one call through the gate runs a short snippet, says reached, not reached or unknown in mpremote's own words, ends with the reset Q5 picks, and keeps a log beside sim/runs/board/. Fake-run tests cover each answer
- depends on: P222 narrowed (A1), Q5, Q6, Q7, Q12
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## P248 (new) — a bounded console read
- type: story
- needed by: "Seral monitor, things like that" (the PO, 2026-10-13, #224)
- value proven by: a read of N seconds on the XIAO C6 keeps a boot with its ROM line, says that opening the port can restart the board, and names download mode with DownloadModeProbe
- depends on: Q10, A6
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 1)

## P249 (new) — run one file from memory
- type: story
- needed by: "just running code live on the device when connected" (the PO, 2026-10-13, #224)
- value proven by: one local file runs on the XIAO C6 with `mpremote run`, the command says the file is not on the board afterwards, and the board's files still match the last passed run
- depends on: P247
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 2)

## P250 (new) — read a pin by name, with the restricted pins refused
- type: story
- needed by: "and debugging maybe?" (the PO, 2026-10-13, #224)
- value proven by: the XIAO C6 record gains its USB and flash pin roles with their sources. A read of GPIO12 is refused, and a read of the BOOT button on the bare board changes when the PO presses it
- depends on: Q8, Q11, P247
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 3)

## P242 (#249) — a comment: the standing yes also covers a live session
- type: story, a comment on the existing card
- needed by: "connection with agents" (the PO, 2026-10-13, #204)
- value proven by: Claude opens a live session on the XIAO C6 without a new terminal yes, inside the grant's limits, and the record says whose yes it was
- depends on: Q6
- status: proposed
- label (the repository's type label): story (the card's own label stays)
- parent (the epic, as a sub-issue): P218 (#200), as today
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 4), or the card's own Slice

## P251 (new) — spark cures a board whose USB output died at power-on
- type: story
- needed by: "Both" (the PO, 2026-10-15, D6), after the cause hunt: spark detects the silence, does the USB-side reset, says so, and retries once
- value proven by: on the XIAO C6 with button-light, 10 replugs, then a spark reach call after each: 10 of 10 reached, and each cured silence is named in the call's output and log (docs/observations/2026-10-15-p235-reach-test.md is the baseline: 1 to 6 silent of 10)
- depends on: —
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): #224
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0), first in it

## Upstream report to MicroPython — the C6's USB output dies on some power-on boots
- type: chore (an outside report, its text in upstream-report.md)
- needed by: "Both" (the PO, 2026-10-15, D6): "we also report it upstream to MicroPython, with your OK on the text"
- value proven by: the issue's URL on MicroPython's tracker, after the PO's OK on the text
- depends on: the PO's OK on upstream-report.md (posting is outward, core rule 8)
- status: proposed
- label (the repository's type label): chore
- parent (the epic, as a sub-issue): #224
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## Board actions
- none taken. Filing, the comments on #204, #249 and #260, and a new Slice option wait on the PO's yes to this list <!-- REQUIRED:board-actions -->
