# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

## A dry change in the middle on scratch copies of two walk projects, with the hand actions counted
- type: spike <!-- REQUIRED:item-type -->
- needed by: "what happens when we ... go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, 'Well, let's add another joystick.' What would happen, actually" (the PO, 2026-11-17, #1234's comment) <!-- REQUIRED:needed-by -->
- value proven by: a finding with its count: each hand action of the change, assigned to a command fix or to a rule that spans phases, against Q1's pass line (A11) <!-- REQUIRED:value-proven-by -->
- depends on: Q1 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P867 #1234's parent, P820 #1173 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider: "v0.11 Change it and put it on again" widened, or "Views and editors" (Q12) <!-- REQUIRED:spark-process:slice -->

## The build replaces a board.tsx that spark wrote and nobody edited
- type: story
- needed by: "what happens when we ... go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, 'Well, let's add another joystick.' What would happen, actually" (the PO, 2026-11-17, #1234's comment)
- value proven by: after a changed design, the build writes the new board.tsx with no "traces differ" and no deletion by hand, and it still names a board.tsx that a person edited (walk 3, row 13)
- depends on: — ; a candidate for P869 #1236's triage, which may already hold the row
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P867 #1234's parent, P820 #1173
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider: "v0.11 Change it and put it on again" widened, or "Views and editors" (Q12)

## `--requirements` names each entry that an earlier pick explained and no pick explains now, and removes it on the person's yes
- type: story
- needed by: "what happens when we ... go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, 'Well, let's add another joystick.' What would happen, actually" (the PO, 2026-11-17, #1234's comment)
- value proven by: after a dropped need, requirements.json no longer lists the dropped part, with no edit by hand; an entry a person wrote stays (#1234's comment: "A person removes them by hand")
- depends on: Q2; a candidate for P869 #1236's triage
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P867 #1234's parent, P820 #1173
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider: "v0.11 Change it and put it on again" widened, or "Views and editors" (Q12)

## `flow.py show` marks everything made from a changed thing as out of date, with its cause
- type: story
- needed by: "what happens when we ... go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, 'Well, let's add another joystick.' What would happen, actually" (the PO, 2026-11-17, #1234's comment)
- value proven by: on a scratch copy of a walk project with a real change (a need added after the build), every phase made from the changed thing reads out of date with its true cause, in the lines and in the JSON; not on the sound demo's folder, whose requirements were written by hand (★C30, a hand-written file)
- depends on: Q5; the spike
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P867 #1234's parent, P820 #1173
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider: "v0.11 Change it and put it on again" widened, or "Views and editors" (Q12)

## A skipped stage or an unjudged phase never shows a tick in `flow.py show`
- type: story
- needed by: "A `could-not-run` or a `skipped` is not a pass" (the PO's rules; AGENTS.md)
- value proven by: the button-and-LED walk folder's build line shows no tick for its skipped stages
- depends on: —
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P867 #1234's parent, P820 #1173
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider: "v0.11 Change it and put it on again" widened, or "Views and editors" (Q12)

## The parts that stay keep their pins when a part is added, and a moved pin is named
- type: story
- needed by: "what happens when we ... go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, 'Well, let's add another joystick.' What would happen, actually" (the PO, 2026-11-17, #1234's comment)
- value proven by: with an added I2C part on a copy of the sound demo (6 of 15 kept signals move today, ★C4 (simulated; one board model)), the answer names every moved pin, and the signals on no bus keep their pins
- depends on: Q3; P868 #1235 (a pin on a bus line)
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P867 #1234's parent, P820 #1173
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider: "v0.11 Change it and put it on again" widened, or "Views and editors" (Q12)

## The firmware's pin names are compared with the pin map
- type: story
- needed by: "what happens when we ... go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, 'Well, let's add another joystick.' What would happen, actually" (the PO, 2026-11-17, #1234's comment)
- value proven by: a main.py that names a pin the pin map lacks reads as a problem in `flow.py show`
- depends on: Q5
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P867 #1234's parent, P820 #1173
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider: "v0.11 Change it and put it on again" widened, or "Views and editors" (Q12)

## After a change, the sheet gives the order of power, flash and wire
- type: story
- needed by: "what happens when we ... go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, 'Well, let's add another joystick.' What would happen, actually" (the PO, 2026-11-17, #1234's comment)
- value proven by: the sheet of a changed design opens with the order line of Q11
- depends on: Q11
- status: proposed
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P867 #1234's parent, P820 #1173
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider: "v0.11 Change it and put it on again" widened, or "Views and editors" (Q12)

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- file the eight items above · pending, needs the PO's yes to this list (a D that names items.md) <!-- REQUIRED:board-actions -->
- Later, one line each, not items yet (plans shrink with distance): the bench witnesses in the flow; a refused build keeps the last good outputs; the facts to test as a phase; one value for an offer and a `next` step.
