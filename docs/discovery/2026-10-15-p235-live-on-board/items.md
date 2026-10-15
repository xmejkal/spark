# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

Every item is a proposal. Nothing is filed. A new item takes the next free number, read again at filing; the numbers
below follow P246, the highest filed on 2026-10-15. Slice 0's items are in build order. No Slice option of the board
fits P235 today, so each asks the PO for a new one (story-map.md, delta). P222 (#204) stays as it is: it keeps its wide
question (belay, the MCP plugin, D30) for later, and gets a comment that P252 took its bench questions (D10).

## 1. P252 (new) — bench: what a reset does to pins, whether values survive, what "ends with a reset" means
- type: story (a bench session; its answer is a bench log, D10) <!-- REQUIRED:item-type -->
- needed by: "First story of slice 0" (the PO, 2026-10-15, D10), from "so that might really allow us to do some cool stuff reagrding updates, debugging, connection with agents" (the PO, 2026-10-13, #204) <!-- REQUIRED:needed-by -->
- value proven by: a bench log in docs/observations/ on the bare XIAO C6: the on-board LED pin after a soft reset and after a hard reset (A5), `resume` with a value set before it (A10), whether the port stays after each reset, and the proposed meaning of `reset_at_end` for Q5 and Q9, which the PO then picks <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P235 (#224) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0), first <!-- REQUIRED:spark-process:slice -->

## 2. P251 (new) — spark cures a board whose USB output died at power-on
- type: story
- needed by: "Both" (the PO, 2026-10-15, D6): spark detects the silence, does the USB-side reset, says so, and retries once
- value proven by: on the XIAO C6, 10 replugs, then a spark reach call after each: 10 of 10 reached, and each cured silence named in the output and the log (A11). Baseline: docs/observations/2026-10-15-p235-reach-test.md, 1 to 6 silent of 10. Built as `RetryingBoardConsole` around a platform-neutral `BoardConsole` (D7), with a fake that goes silent on cue
- depends on: —
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 3. P253 (new) — the live grant: one yes in the PO's terminal for a board and a time limit
- type: story
- needed by: "One grant, P242 reuses it" (the PO, 2026-10-15, D12) and "Once, at the grant" (D13)
- value proven by: the PO types `spark live --grant --minutes 30` in his terminal, one look runs, he types yes, and the store keeps a grant for that board and token. A later call inside the time limit finds it, and one after it is refused. Fake-run tests cover expired, other board and no grant. P242 (#249) later reuses the same record class. The command's name is a sketch: spark's commands are scripts today, and the design names it
- depends on: —
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 4. P254 (new) — the C6 record's USB and flash pins, and a try that names one is refused
- type: story
- needed by: "Record them, refuse them" (the PO, 2026-10-15, D14)
- value proven by: boards/xiao-esp32-c6.json gains GPIO12 and GPIO13 (USB) and GPIO24 to GPIO30 (flash), each with its role and Espressif source (URL, version, page). A try whose code names one of them is refused with the pin, its role and its source. The refusal reads the code's text, so the output says that a pin number built at run time is not caught
- depends on: —
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 5. P246 (#260) — a new board-only project for live tries
- type: story, on the existing card
- needed by: "then we'll make another testing project without anything" (the PO, 2026-10-15, #260) and "A new P246 project" (D16); and the PO, 2026-10-15 (D18): "lets make the functionality itself cool, do some cool stuff with what we have so the diodes and maybe a button if it's accessible, lets play with various animations eand effects". Proposed scope: effects on the one on-board LED (for example breathe by PWM, heartbeat, candle flicker, strobe, morse of a typed word), a typed line picks the effect and its speed, and the BOOT button cycles effects once the record cites its pin (AT158; it is a strapping pin, so a press at reset enters download mode)
- value proven by: a new project with nothing but the XIAO C6: it passes in Wokwi, prints `ready` on the bare board, reads its console without waiting (docs/guide/agents.md:577-578), and shows what a live try changed, for example the on-board LED
- depends on: —
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224), as today
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 6. P247 (new) — the live try: `spark live --code ... --json` runs a line on the running board
- type: story
- needed by: "just running code live on the device when connected" (the PO, 2026-10-13, #224), "Reach and read" (D9) and "Set it now" (D15)
- value proven by: on the XIAO C6 with P246's project, inside a grant, Claude's call runs `print(1)`, says reached, not reached or unknown (D11 names both causes when it cannot get in), ends with the reset from P252, and returns `LiveTryResult` as JSON. Fake-run tests cover each answer
- depends on: P246, P251, P252, P253, P254
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 7. P256 (new) — the upstream report to MicroPython
- type: chore (an outside report, its text in upstream-report.md)
- needed by: "Both" (the PO, 2026-10-15, D6), OK on the text given with "ok, lets go" (D8), posted after the plan
- value proven by: the issue's URL on MicroPython's tracker, linked from AT187
- depends on: the plan done (D8)
- status: proposed
- label (the repository's type label): chore
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 8. P255 (new) — a Decorator row in the naming table
- type: chore
- needed by: "remember to name the classes and objects well so they're understandable" (the PO, 2026-10-15) and his OK (D8)
- value proven by: docs/guide/developing.md's table "Patterns and names in spark's core" has a Decorator row with `RetryingBoardConsole` as its example, in a docs-only PR
- depends on: the plan done (D8)
- status: proposed
- label (the repository's type label): chore
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## Later — P248 (new), a bounded console read
- type: story
- needed by: "Seral monitor, things like that" (the PO, 2026-10-13, #224)
- value proven by: a read of N seconds on the XIAO C6 keeps a boot with its ROM line, says that opening the port can restart the board, and names download mode with DownloadModeProbe
- depends on: Q10, A6
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 1)

## Later — P249 (new), run one file from memory
- type: story
- needed by: "just running code live on the device when connected" (the PO, 2026-10-13, #224)
- value proven by: one local file runs on the XIAO C6 from memory, the command says the file is not on the board afterwards, and the board's files still match the last passed run
- depends on: P247
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 2)

## Later — P250 (new), read a pin by name
- type: story
- needed by: "and debugging maybe?" (the PO, 2026-10-13, #224)
- value proven by: a read of the BOOT button on the bare board changes when the PO presses it, and a read of a pin from P254's list is refused
- depends on: Q11, P247, P254
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 3)

## P242 (#249) — a comment: it reuses the live grant
- type: story, a comment on the existing card
- needed by: "connection with agents" (the PO, 2026-10-13, #204) and "One grant, P242 reuses it" (D12)
- value proven by: P242's standing yes uses P253's grant record class, and the record says whose yes it was
- depends on: P253
- status: proposed
- label (the repository's type label): story (the card's own label stays)
- parent (the epic, as a sub-issue): P218 (#200), as today
- slice (one Slice option of the board, or "ask the decider for a new one"): the card's own Slice

## Board actions
- pending, each needs the PO's yes to this list: file P247, P251 to P256 as sub-issues of #224; refine #260 (P246) with D16; comment on #204 (P252 took its bench questions, D10), #235 (round 3 of the spike, AT187, D5) and #249 (P242 reuses P253's grant, D12); a new Slice option "Live 0" and later ones; move P218's J4 and J6 and its deploy map's slices 4 and 6 under P235 in scrum/STORY_MAP.md and on Miro (D17) <!-- REQUIRED:board-actions -->
