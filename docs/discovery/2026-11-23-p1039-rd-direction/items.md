# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->
The least that answers the epic: three spikes at most, and none is filed under Q4's option (a). More issues are filed than closed (174 against 95 in the 7 days to 2026-11-23, E ★C24, a ratio that measures the filing rule too), so each block says which existing card it touches, and none closes a card. The riskiest test is the PO's own answers and needs no card. Four directions get no new card, in the architect's opinion. The factory's later stages stay on P79 #16 and P203 #163, and the line's end is in the brief's Found on the way. The interface split stays on P793 #1105, P417 #545 and P1038 #1521. The knowledge guard stays on P200 #153 and waits on A6. A local AI gets one line in scrum/VISION.md's "later" row and no card until Q11 names a machine. The seams S1 to S7 are a comment on #1105, not cards. Each number is read at filing.

## P? — The first step in a harness that is already installed: `flow.py show --json` on a fixture, with no install
- type: spike <!-- REQUIRED:item-type -->
- needed by: "How can we make our system more general, not only for Claude but just generally runnable?" (the PO, 2026-11-23, #1522, the comment posted at 15:30 CET) <!-- REQUIRED:needed-by -->
- value proven by: the harness's own answer: the op and the next step it names from spark's JSON, with no source file read (A2, step 0) <!-- REQUIRED:value-proven-by -->
- depends on: the PO's yes, because it costs model use on his own account in that harness. No install and no build <!-- REQUIRED:depends-on -->
- status: not filed, D10 (no trial now) <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1039 #1522 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): team tools <!-- REQUIRED:spark-process:slice -->
- existing cards: none closed. If the PO orders it inside this discovery, it runs under #1522 and needs no card. Its result goes onto P217 #199 as a comment
<!-- EXTEND:item-fields -->

## P? — One fixed task, five reruns, graded by spark's own facts: do the reruns agree?
- type: spike
- needed by: "How do we evaluate what models we use for what?" (the PO, 2026-11-23, #1522, the comment posted at 15:30 CET)
- value proven by: five results of one task (a requirements file to `/spark:build` exit 0), each with its outcome and its tokens, against A4's pass line, and the row of the model table that the PO named (A5)
- depends on: Q10's answer (the row and the result that changes it, the ceiling, whether a report leaves the computer), with the cost named first. It runs outside the hook
- status: not filed, D15 (no eval now)
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P1039 #1522
- slice (one Slice option of the board, or "ask the decider for a new one"): team tools
- existing cards: none closed. It takes up retro R11's entry 58 ("two model tests offered, not run") and gives P711 #960 its grader. P289 #345, P317 #401 and P943 #1346 stay as they are

## P? — Each Claude-only construct per command as one table, then the job of /spark:build in one other harness
- type: spike
- needed by: "How can we make our system more general, not only for Claude but just generally runnable?" (the PO, 2026-11-23, #1522, the comment posted at 15:30 CET)
- value proven by: the table (one row per construct per command), then one run that exits 0 with no source file read and no construct that the table missed (A2's pass line)
- depends on: the first spike's result, A1 holding for this direction (Q7), the seams S1 and S2, and the PO's yes to the model use, with the cost named first. An install only if he picks a harness that is not on his computer
- status: not filed, D10 and D21
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P1039 #1522
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one. None of the board's 21 options names work past the MVP, and "parked, after v0.10" is the nearest
- existing cards: none closed. P217 #199 keeps the PO's words of 2026-10-13 and gets a comment that links this spike. P227 #213 stays as the later slice

## P? — The clock or the bin off the breadboard: what spark gives today for a permanent build, on a perfboard or a PCB, and where it stops
- type: spike
- needed by: "A permanent build" and "including the perfboard optional step, not just pcb" (the PO, 2026-11-23, D11, Q14b)
- value proven by: one of his two gadgets taken from its breadboard design through spark's steps toward a perfboard layout (optional) and a PCB, with each step's result, the step where spark stops, and what the person must do by hand from there
- depends on: D21. No paid run and no order. Ordering a PCB is a cost, and it waits on his yes with the cost named
- status: proposed, filing allowed by D21
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P1039 #1522
- slice (one Slice option of the board, or "ask the decider for a new one"): spark-main picks it. The nearest cards are P79 #16 (the PCB only after a working breadboard), P275 #311 (plain perfboard) and P203 #163 (the design in a CAD program)
- existing cards: none closed. Its result goes onto P79 #16 and P275 #311 as a comment

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- none taken. This session moves no card (D0), and spark-main moves cards <!-- REQUIRED:board-actions -->
- comment on P793 #1105 with the seams S1 to S7 as acceptance lines · taken by spark-main on 2026-11-23 after D5, with lines on P1043 #1533, P937 #1333 and P417 #545 and none on P1035 (in Build). The core-gaps finding was still not read by this discovery
- file the permanent-build spike as a sub-issue of #1522 · pending, spark-main files it on D21. The three other spikes are not filed (D10, D15)
- comment on P217 #199 with the first spike's result · pending, on that result
- one line per direction in scrum/VISION.md's "later" row, with the story map's delta, in one PR · pending, on the PO's answer to Q4
- P1039 #1522 stays in Discovery, waiting on the PO for Q1 and the queue · pending, spark-main sets "Waiting on" and "Waiting since"
- withdrawn after the refuter: the comments on P1005 #1464 and P1004 #1463. #1463 already names the flag, and #1464 is about the tool failing, not about a missing tool
