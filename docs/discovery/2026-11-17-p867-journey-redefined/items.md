# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

## A paper spike: one "made from" table over the three P711 walk folders
- type: spike <!-- REQUIRED:item-type -->
- needed by: "what happens when we ... go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, 'Well, let's add another joystick.' What would happen, actually" (the PO, 2026-11-17, #1234's comment) <!-- REQUIRED:needed-by -->
- value proven by: a finding with its table: how many of the 7 things of #1234's comment the table names from files and records alone, against Q1's pass line <!-- REQUIRED:value-proven-by -->
- depends on: Q1 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P867 #1234's parent, P820 #1173 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider: "v0.11 Change it and put it on again" widened, or "Views and editors" (Q12) <!-- REQUIRED:spark-process:slice -->

## `flow.py show` marks everything made from a changed thing as out of date, with its cause
- type: story
- needed by: "what happens when we ... go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, 'Well, let's add another joystick.' What would happen, actually" (the PO, 2026-11-17, #1234's comment)
- value proven by: on the sound demo's walk folder as it stands, the build and the breadboard read out of date with the cause, in the lines and in the JSON
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
- value proven by: a second joystick on a copy of the sound demo moves no kept signal, or the answer names each one that moved
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
- file the six items above · pending, needs the PO's yes to this list (a D that names items.md) <!-- REQUIRED:board-actions -->
- Later, one line each, not items yet (plans shrink with distance): the bench witnesses in the flow; a refused build keeps the last good outputs; the facts to test as a phase; one value for an offer and a `next` step.
