# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

## The deploy reader reads the project's board logs (P793 piece 6)
- type: story <!-- REQUIRED:item-type -->
- needed by: "get back to where the page is and try to show this project on the page ... so we can make it work" (the PO, 2026-11-23, brief.md Frame); the core gap is named in P793 #1105's comment of 2026-11-23 <!-- REQUIRED:needed-by -->
- value proven by: `flow.py show --project .` in p934-display2 shows the last deploy's time, image and ready verdict with no tick on "ready unknown" (D10); its NOW sentences carry the PO's review (#1105 piece 6, size M) <!-- REQUIRED:value-proven-by -->
- depends on: D10 (the deploy states); A3 is met for one board <!-- REQUIRED:depends-on -->
- status: filed D18 as P1043 #1533 (spark-main, 2026-11-23, Idea, slice v0.10 The basic journey) <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P793 #1105 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): v0.10 The basic journey (as filed) <!-- REQUIRED:spark-process:slice -->

## The page offers Build and Pick on a wired board, and a rebuild can move its pins
- type: bug
- needed by: the user lens, USER-3 (council/user.md), from the P1010 commit; not seen by the PO, and the diary says "the page offers no build now" (diary.md:203), so a look at the rendered page comes first (R-6)
- value proven by: the page of p934-display2 shows no Build or Pick that moves a pin without saying so
- depends on: —
- status: filed D18 as P1044 #1534 (spark-main, 2026-11-23, Idea, slice v0.10 The basic journey)
- label (the repository's type label): bug
- parent (the epic, as a sub-issue): P1038 #1521
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider

## The page's step numbers disagree with its picture, and its stamp has no date and names no build
- type: bug
- needed by: the user lens, USER-4 and USER-7 (council/user.md); the PO: "not very readable or intuitive" (P1011 #1470); the cause is an old build drawn by new code (R-7)
- value proven by: on a page written again after P1009, step N of the list is pill N of the picture, and the stamp shows a date
- depends on: —
- status: filed D18 as P1045 #1535 (spark-main, 2026-11-23, Idea, slice v0.10 The basic journey)
- label (the repository's type label): bug
- parent (the epic, as a sub-issue): P1038 #1521
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider

## The README's Bench row looks stale after the P934 walk
- type: chore
- needed by: the PO assistant lens, PO-29 (council/po-assistant.md)
- value proven by: the Bench row of "What works today" matches the walk's deploys, or says why not
- depends on: —
- status: filed D18 as P1046 #1536 (spark-main, 2026-11-23, Idea, slice v0.10 The basic journey)
- label (the repository's type label): chore
- parent (the epic, as a sub-issue): P1038 #1521 (as filed)
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- file the four items above · taken, D18: spark-main filed P1043 #1533, P1044 #1534, P1045 #1535, P1046 #1536, each in Idea <!-- REQUIRED:board-actions -->
