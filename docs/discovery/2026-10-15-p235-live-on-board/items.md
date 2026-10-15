# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

Filed on 2026-10-15 by D21, each with its issue number below. A new item takes the next free number, read again at filing; the numbers
below follow P246, the highest filed on 2026-10-15. Slice 0's items are in build order. No Slice option of the board
fits P235 today, so each asks the PO for a new one (story-map.md, delta). P222 (#204) stays as it is: it keeps its wide
question (belay, the MCP plugin, D30) for later, and gets a comment that P252 took its bench questions (D10).

## 1. P252 (new) — bench spike: what a reset does to pins, whether values survive, what "ends with a reset" can mean
- type: spike (research, so a spike by the PO's standing rule; D10 called it a story, and its answer is a finding with a bench log) <!-- REQUIRED:item-type -->
- needed by: "First story of slice 0" (the PO, 2026-10-15, D10), from "so that might really allow us to do some cool stuff reagrding updates, debugging, connection with agents" (the PO, 2026-10-13, #204) <!-- REQUIRED:needed-by -->
- value proven by: a bench log in docs/observations/ on the bare XIAO C6: the on-board LED pin after a soft reset and after a hard reset (A5), `resume` with a value set before it (A10), the proposed meaning of `reset_at_end` for Q5 and Q9, which the PO then picks <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: filed D21 #263 <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P235 (#224) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0), first <!-- REQUIRED:spark-process:slice -->

## 2. P251 (new) — spark cures a board whose USB output died at power-on
- type: story
- needed by: "Both" (the PO, 2026-10-15, D6): spark detects the silence, does the USB-side reset, says so, and retries once
- value proven by (proposed by the facilitator, pending the PO): on the XIAO C6, replugs with a diagnostic listen and a spark reach call after each, until at least 3 silent boots occurred: each silent boot cured and reached, every other replug reached, and each cure named in the output and the log (A11). It cannot pass with zero cures. At the probe rounds' pooled rate, 7 silent of 20, that takes about 9 replugs, 14 for a 90 % chance; at 1 in 10, about 30, and 52 for 90 %. The cure is also tried from a cold port, because both shown cures came after mpremote had opened the port with DTR and RTS True (rival: the cure needs that line change first). Baseline counts per round: docs/observations/2026-10-15-p235-reach-test.md. Platform-neutral per D7, with a fake that goes silent on cue; the class names are the design's
- depends on: —
- status: filed D21 #264
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 3. P253 (new) — the live grant: one yes in the PO's terminal for a board and a time limit
- type: story
- needed by: "One grant, P242 reuses it" (the PO, 2026-10-15, D12) and "Once, at the grant" (D13)
- value proven by: the PO types a grant command (sketch: `spark live --grant --minutes 30`; D12 says only "a time limit", and 30 has no D) in his terminal, one look runs, he types yes, and the store keeps a grant for that board and token. A later call inside the time limit finds it, and one after it is refused. Fake-run tests cover expired, other board and no grant. P242 (#249) later reuses the same record class. The command's name is a sketch: spark's commands are scripts today, and the design names it
- depends on: —
- status: filed D21 #265
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 4. P254 (new) — the C6 record's USB and flash pins, and a try that names one is refused
- type: story
- needed by: "Record them, refuse them" (the PO, 2026-10-15, D14)
- value proven by: boards/xiao-esp32-c6.json gains GPIO12 and GPIO13 (USB) and GPIO24 to GPIO30 (flash), each with its role and Espressif source (URL, version, page). A try whose code names one of them is refused with the pin, its role and its source. Open for design (H, the facilitator, not part of D14): the refusal reads the code's text, so a pin number built at run time passes
- depends on: —
- status: filed D21 #266
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 5. P246 (#260) — a new board-only project for live tries
- type: story, on the existing card
- needed by: "then we'll make another testing project without anything" (the PO, 2026-10-15, #260) and "A new P246 project" (D16); and the PO, 2026-10-15 (D18): "lets make the functionality itself cool, do some cool stuff with what we have so the diodes and maybe a button if it's accessible, lets play with various animations eand effects". Proposed scope: effects on the one on-board LED (for example breathe by PWM, heartbeat, candle flicker, strobe, morse of a typed word), a typed line picks the effect and its speed, and the BOOT button cycles effects once the record cites its pin (AT158; it is a strapping pin, so a press at reset enters download mode)
- value proven by (proposed by the facilitator; D16 says only "a new board-only project"): a new project with nothing but the XIAO C6: it passes in Wokwi, prints `ready` on the bare board, reads its console without waiting (docs/guide/agents.md:577-578), and shows what a live try changed, for example the on-board LED
- depends on: —
- status: filed earlier as #260; refined by a comment, D21
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224), as today
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 6. P247 (new) — the live try: one gated call runs a line on the running board (sketch name `spark live --code ... --json`)
- type: story
- needed by: "just running code live on the device when connected" (the PO, 2026-10-13, #224), "Reach and read" (D9) and "Set it now" (D15)
- value proven by: on the XIAO C6 with P246's project, inside a grant, Claude's call runs `print(1)`, says reached or not (D9; a third verdict "unknown" is a sketch), names both causes when it cannot get in (D11), ends with the reset P252 informs and the PO picks, and answers in `--json` (D15; `LiveTryResult` is a sketch name). Fake-run tests cover each answer
- depends on: P246, P251, P252, P253, P254
- status: filed D21 #267
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 7. P256 (new) — the upstream report to MicroPython
- type: chore (an outside report, its text in upstream-report.md)
- needed by: "Both" (the PO, 2026-10-15, D6), OK on an earlier text given with "ok, lets go" (D8, 09:07); the text changed after it, so it needs his re-read; posted after the plan
- value proven by: the issue's URL on MicroPython's tracker, linked from AT187
- depends on: the plan done (D8)
- status: filed D21 #268
- label (the repository's type label): chore
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## 8. P255 (new) — Decorator and Fake rows in the naming table
- type: chore
- needed by: "remember to name the classes and objects well so they're understandable, well readable, ReachCure sounds  vague, what is it? state?command?data?" (the PO, 2026-10-15, this session, on the sketch name ReachCure) and his OK to the Decorator row (D8); a Fake row has no D yet, so it is proposed
- value proven by: docs/guide/developing.md's table "Patterns and names in spark's core" has a Decorator row and a Fake row, and settles the roles shape-for-design.md marks as open (a wrapper of the store's files, a value with a why_ function), in a docs-only PR
- depends on: the plan done (D8)
- status: filed D21 #269
- label (the repository's type label): chore
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 0)

## Later — P248 (new), a bounded console read
- type: story
- needed by: "Seral monitor, things like that" (the PO, 2026-10-13, #224)
- value proven by: a read of N seconds on the XIAO C6 keeps a boot with its ROM line, says that opening the port can restart the board, and names download mode with DownloadModeProbe
- depends on: Q10, A6
- status: filed D21 #270
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 1)

## Later — P249 (new), run one file from memory
- type: story
- needed by: "just running code live on the device when connected" (the PO, 2026-10-13, #224)
- value proven by: one local file runs on the XIAO C6 from memory, the command says the file is not on the board afterwards, and the board's files still match the last passed run
- depends on: P247
- status: filed D21 #271
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 2)

## Later — P250 (new), read a pin by name
- type: story
- needed by: "and debugging maybe?" (the PO, 2026-10-13, #224)
- value proven by: a read of the BOOT button on the bare board changes when the PO presses it, and a read of a pin from P254's list is refused
- depends on: Q11, P247, P254
- status: filed D21 #272
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P235 (#224)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one (Live 3)

## P242 (#249) — a comment: it reuses the live grant
- type: story, a comment on the existing card
- needed by: "connection with agents" (the PO, 2026-10-13, #204) and "One grant, P242 reuses it" (D12)
- value proven by: P242's standing yes uses P253's grant record class, and the record says whose yes it was
- depends on: P253
- status: comment posted on #249, D21
- label (the repository's type label): story (the card's own label stays)
- parent (the epic, as a sub-issue): P218 (#200), as today
- slice (one Slice option of the board, or "ask the decider for a new one"): the card's own Slice

## Board actions
- filed P252 #263, P251 #264, P253 #265, P254 #266, P247 #267, P256 #268, P255 #269, P248 #270, P249 #271, P250 #272 as sub-issues of #224, Status Idea · taken, D21
- comments on #260, #204, #249, #235 · taken, D21
- the Slice option "Live 0" · pending: the PO adds it by hand (D21), because an API edit rewrites the field's option list
- the map moves in scrum/STORY_MAP.md and P218's story map · taken in this PR, D17, D23 <!-- REQUIRED:board-actions -->
