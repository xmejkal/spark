# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>. -->

The architect's list (council/architect.md §11), in slice order. Nothing is filed. spark-main files on the PO's yes.
Cards left alone: P999 #1455 (do it beside slice 0), P1000 #1456 (waits on the bench read of the e-paper controller), P1078 #1582 (a prerequisite of item 6), P413 #539 (feeds item 9).

## 1. A board that no simulator covers ends the simulation stage `skipped` with a reason, and the build record's top status follows
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: the clock's `.spark/build.json` after a rebuild says `skipped` with the reason, and `scripts/spark/flow/guide.py`'s special case for `board_not_in_wokwi` is gone <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: absorbs the clock half of P995 #1452 (the spike's answer stands, the card closes as answered)

## 2. `check-firmware`: the import check and the project's own tests in one free Operation, with no `sim/` needed, and one kept record stamped with the firmware's sha256
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: `check-firmware --json` on the clock gives the import count and "35 of 35" for its tests <!-- REQUIRED:value-proven-by -->
- depends on: the P1078 #1582 pattern for the envelope <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: absorbs P410 #536's "quick free check"

## 3. The page: the Simulation step's coverage line and the free checks' state
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: the clock's page names what can run and the free checks' result, in grey where nothing more runs <!-- REQUIRED:value-proven-by -->
- depends on: items 1 and 2 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): the page epic, linked to P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 4. The list "what this simulation cannot show" prints only after a run
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a deploy with no run prints one line, "no simulation tested this image", and no list <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 5. Spike: do `wokwi-cli lint` and `chip compile` run with no token and no minutes?
- type: spike <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a finding with the commands run and their output, token unset <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: absorbs Q1 of P492 #671, and leaves its Q3

## 6. The `Simulator` seam with no behaviour change: the base, `WokwiSimulator`, the Fake, the table from contract to Adapter, at every selection site of council/architect.md §3
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: the goldens hold, and one table names the Adapter <!-- REQUIRED:value-proven-by -->
- depends on: P1078 #1582 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 7. The run record names its simulator and its grade
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a log header names the simulator, its version and the grade <!-- REQUIRED:value-proven-by -->
- depends on: item 6 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: is P308 #374, absorbed

## 8. The `simulator` role, on or off, as the one setting, said by the commands
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a project with the role off runs the free checks and says that no paid run happens <!-- REQUIRED:value-proven-by -->
- depends on: item 6 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: replaces P410 #536

## 9. The cost and the time cap before the yes for a paid run
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: the question before a run names the minutes this month by spark on this machine and the free plan's 50 <!-- REQUIRED:value-proven-by -->
- depends on: item 6, P413 #539 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: P413 #539 stays and feeds it

## 10. `SimulationControls`, and the scenario shown as sentences with the values and ranges it sets
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: the VL6180X project's scenario reads "Set the distance to 80 mm" with the range 0 to 255 <!-- REQUIRED:value-proven-by -->
- depends on: item 6 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 11. The result on the page, the caveat in the verdict's line
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: walk2's run reads "passed, but it tested only the start" <!-- REQUIRED:value-proven-by -->
- depends on: item 7 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 12. Spike: a community chip named by reference in wokwi-cli, and its licence rule
- type: spike <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: one free run with a chip named by `github:` reference, its licence read, and the rule written <!-- REQUIRED:value-proven-by -->
- depends on: the PO's yes for the run's minutes <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: replaces P409 #535. P344 #439 is its worked example

## 13. Spike: a live value in Wokwi's editor for a spark project
- type: spike <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a finding: how a spark project opens in Wokwi's editor with its controls, or why it cannot <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 14. Spike, free: the clock's `main.py` loop on the stand-in with a virtual clock, with no device model
- type: spike <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: a finding: whether the loop runs 10 simulated seconds with no edit to firmware/ <!-- REQUIRED:value-proven-by -->
- depends on: A1's test result, and the PO's reading of the non-goals (Q3) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1190 #1735 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## 15. Gate A's evidence row: "Tested before the board", with the highest tier reached
- type: story <!-- REQUIRED:item-type -->
- needed by: "we need to analyze and design how it should actually work, what  steps it takes, cause I knw there are some free steps we can do, but then the payd part" (the PO, 2026-11-26, P1190 #1735) <!-- REQUIRED:needed-by -->
- value proven by: the "On the board" card shows the row and never locks on it <!-- REQUIRED:value-proven-by -->
- depends on: item 7, and the PO's answer to Q5 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P79 #16 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey, as P1190 <!-- REQUIRED:spark-process:slice -->
- the tied card: —

## Board actions
- file items 1 to 15 · pending, the PO's yes to this list · through spark-main <!-- REQUIRED:board-actions -->
- close P995 #1452 as answered, P409 #535 and P410 #536 as replaced, P308 #374 as absorbed · pending, the PO's yes · through spark-main
