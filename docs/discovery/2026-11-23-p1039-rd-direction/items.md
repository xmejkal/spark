# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->
The least that answers the epic: three spikes at most, and none is filed under Q4's option (a). The backlog grew by 173 filed against 93 closed in the 7 days to 2026-11-23 (E ★C24), so each block says which existing card it absorbs. Four directions get no new card, in the architect's opinion. The factory's later stages stay on P79 #16 and P203 #163, and the line's end is in the brief's Found on the way. The interface split stays on P793 #1105, P417 #545 and P1038 #1521. The knowledge guard stays on P200 #153 and waits on A6. A local AI gets one line in scrum/VISION.md's "later" row and no card until Q11 names a machine. The seams S1 to S7 are a comment on #1105, not cards. Each number is read at filing.

## P? — Which direction does a project reach for: the PO's account and the 72 walk rows sorted by cause
- type: spike <!-- REQUIRED:item-type -->
- needed by: "lets create another kinda bigger R&D epic and think about whats next, how to make it a software factory, what other harnesses or frameworks we can support, how we should evaluate and improve the system" (the PO, 2026-11-23, #1522 body) <!-- REQUIRED:needed-by -->
- value proven by: a Results row in risks-and-tests.md: the dated occasions that the PO names, and the count of walk rows per cause, against A1's pass line <!-- REQUIRED:value-proven-by -->
- depends on: Q1 (the pass line) and the PO's choice of the test. No build <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1039 #1522 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): team tools <!-- REQUIRED:spark-process:slice -->
- absorbs or closes: nothing. If the PO chooses the test inside this discovery, it runs under #1522 and needs no card. Its table of rows gives P711 #960 and P200 #153 their first evidence
<!-- EXTEND:item-fields -->

## P? — One fixed task, three reruns, graded by spark's own facts: do the reruns agree?
- type: spike
- needed by: "How do we evaluate what models we use for what?" (the PO, 2026-11-23, about 15:5x CET, #1522)
- value proven by: three results of one task (a requirements file to `/spark:build` exit 0), each with its outcome and its tokens, against A4's pass line, and the row of the model table that the PO named (A5)
- depends on: Q10's answer (the row and the result that changes it, the ceiling, whether a report leaves the Mac), with the cost named first. It runs outside the hook
- status: proposed
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P1039 #1522
- slice (one Slice option of the board, or "ask the decider for a new one"): team tools
- absorbs or closes: the two model tests of retro R11's entry 58 ("two model tests offered, not run"). It gives P711 #960 its grader. P289 #345, P317 #401 and P943 #1346 stay as they are

## P? — Each Claude-only construct per command as one table, then the job of /spark:build in one other harness
- type: spike
- needed by: "How can we make our system more general, not only for Claude but just generally runnable?" (the PO, 2026-11-23, about 15:5x CET, #1522)
- value proven by: the table (one row per construct per command), then one run that exits 0 with no source file read and no construct that the table missed (A2's pass line)
- depends on: A1 holding for this direction (Q7), the seams S1 and S2, and the PO's yes to an install and a model, with the cost named first
- status: proposed
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P1039 #1522
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider for a new one. None of the board's 21 options names work past the MVP, and "parked, after v0.10" is the nearest
- absorbs or closes: P217 #199, whose words of 2026-10-13 become this spike's frame, so the proposal is to close #199 into it. P227 #213 stays as the later slice

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- none taken. This session moves no card (D0), and spark-main moves cards <!-- REQUIRED:board-actions -->
- comment on P793 #1105 with the seams S1 to S7 as acceptance lines · pending, on the PO's answer to Q5
- file the spikes above as sub-issues of #1522 · pending, on a D that names items.md, and only under Q4's option (b)
- close P217 #199 into the third spike · pending, on the same D
- comment on P1005 #1464 (`live.py` exists) and on P1004 #1463 (`flash_image.py --config` exists) · pending, from the brief's Found on the way
- one line per direction in scrum/VISION.md's "later" row, with the story map's delta, in one PR · pending, on the PO's answer to Q4
- P1039 #1522 stays in Discovery, waiting on the PO for Q1 and the queue · pending, spark-main sets "Waiting on" and "Waiting since"
