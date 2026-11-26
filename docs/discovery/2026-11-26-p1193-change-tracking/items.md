# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

From the architect's synthesis, part 7 (council/synthesis.md). Existing cards widen first. Four new cards follow,
each only where no card covers the work. A new card's P-number is the next free one when spark-main files it (the
highest on 2026-11-26, read between 09:31 and 09:34 CET, was P1193). Filing, comments and every board move are spark-main's, after the
PO's yes to this list.

## P1152 #1688 (widened) — the project timeline keeps only what D8 named, and has no named point, no outside change and no compare → the epic gains slices 1 to 6 of the story map, the area-declared kept records, and a Service over the one lower Strategy
- type: epic <!-- REQUIRED:item-type -->
- needed by: "we actually want to have that with all main steps that can be reverted" and "be able to see if things changed from the outside or be able to go back, make tags or like snapshots" (the PO, 2026-11-26, #1738) <!-- REQUIRED:needed-by -->
- value proven by: outcomes (1) to (3) of brief.md's Frame, each in a scratch project, quoted in its PR <!-- REQUIRED:value-proven-by -->
- depends on: P1155 for slices 2 to 6, and P1165 #1702 with P1166 #1703 before slice 3 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): epic <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1193 #1738 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Project history (as today) <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1151 #1687 (widened) — the git Adapter is built inside two callers and no configuration chooses it → init's Operation takes the builder, `GitRunner` is split from `ProjectCommit`, and the tools list gains the two roles with a `none` member
- type: story <!-- REQUIRED:item-type -->
- needed by: "again our strategies should be configurable, like this one, and we want the system to be consistent, not to repeat ourselves and reuse the selected strategy" (the PO, 2026-11-26, #1738) <!-- REQUIRED:needed-by -->
- value proven by: P1148 A7's lines in the PR: a Fake and git run with no change to the area, and with `project-timeline: none` a receive test of the shared role still runs (the PO-6 coupling test) <!-- REQUIRED:value-proven-by -->
- depends on: P1150 (done) and N1 (the words) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P793 #1105 (as today) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): as today <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1155 #1691 (widened) — nobody has seen spark's commits, or a return across the person's own commits and a squash merge → the A1 walk plus the widened A2 spike on temporary clones of three of the PO's repositories
- type: spike <!-- REQUIRED:item-type -->
- needed by: P1148 D13 (the PO, 2026-11-25), and P9 of this discovery for the A2 pass line <!-- REQUIRED:needed-by -->
- value proven by: the spike's lines against the pass lines in risks-and-tests.md (A1 and A2), with the count of returns that P1160 Q4 would refuse <!-- REQUIRED:value-proven-by -->
- depends on: P1152's first slice for A1. Nothing for the A2 part, which can run first <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1152 #1688 (as today) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): as today <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1153 #1689 (widened) — the plain words cover only a kept step → they also cover a named point, an outside change and "spark cannot tell"
- type: story <!-- REQUIRED:item-type -->
- needed by: P1148 D11 (the PO, 2026-11-25: plain words) <!-- REQUIRED:needed-by -->
- value proven by: a grep finds no git word in an area's line, and the golden files show the new lines <!-- REQUIRED:value-proven-by -->
- depends on: slice 2 of P1152 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1152 #1688 (as today) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): as today <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P1163 #1699 (a comment, no change of scope) — spark has no one concept of what a change makes out of date → a layout edit on the page is a kept step through the same Service, and its effects are D-q2's `changed` list, with no second seam
- type: epic <!-- REQUIRED:item-type -->
- needed by: "its kinda connected to making changes in general and what changes influence in later steps" (the PO, 2026-11-25, #1699) <!-- REQUIRED:needed-by -->
- value proven by: the comment on #1699 that links this brief <!-- REQUIRED:value-proven-by -->
- depends on: slices 2 and 5 of P1152 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): epic <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): as today <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): as today (parked, after v0.10) <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## #123 (widened) — the shared store waits on a trigger that D2 replaced → its body records D2, D3 and D4 and takes N3 as its child
- type: epic <!-- REQUIRED:item-type -->
- needed by: "definitely pushing and pulling things to some central repo" (the PO, 2026-11-26, #1738), D2 <!-- REQUIRED:needed-by -->
- value proven by: #123's body names D2 to D4 and N3 <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): epic <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store (as today) <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P342 #437 (widened) — RecordAdder's "publish" step has no target, and a record has no origin → publish calls the shared Service's share, and RecordAdder writes the `origin` block and the closed `made_by` set
- type: story <!-- REQUIRED:item-type -->
- needed by: "probably there should be some common ancestor or functionality for adding any part" (the PO, 2026-10-19, #437) and D4 <!-- REQUIRED:needed-by -->
- value proven by: a record that RecordAdder writes carries `origin` and a `made_by` from the closed set, read by slice 8's dry run <!-- REQUIRED:value-proven-by -->
- depends on: slice 8 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): as today <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): as today <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P390 #505 (re-read first) — its body says `layers()` adds the shelf for parts only, which is out of date (store.py:129, P989) → re-read the card. What can remain: the copy onto the shelf at `--requirements` and the label in `--match`. A board then becomes a shared kind with no new seam
- type: story <!-- REQUIRED:item-type -->
- needed by: "at least locally for all projects first" (the PO, 2026-10-22, #505) <!-- REQUIRED:needed-by -->
- value proven by: the card's body matches the code after the re-read <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): #123 (as today) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): as today <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## N1 — the planned names make `ProjectTimeline` the Strategy, and a named point, a share and a receive have no words → words.md rows for the Service, the lower Strategy, `kept_step.name`, "share", "get shared" and the new effect word
- type: chore <!-- REQUIRED:item-type -->
- needed by: "we want the system to be consistent, not to repeat ourselves" (the PO, 2026-11-26, #1738), and "Every plan checks its names: one word for one thing" (the PO's rules) <!-- REQUIRED:needed-by -->
- value proven by: the new rows in docs/guide/words.md, and a grep that finds no second meaning of each word in scripts/spark <!-- REQUIRED:value-proven-by -->
- depends on: C1, C4, C5 and C6 (the council's answers) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): chore <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1152 #1688 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Project history <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## N2 — a file that changed outside spark reads as current, or as fine when it has no stamp → the build phase reads `written_sha256`, and a record with no stamp says "spark cannot tell", with no git
- type: story <!-- REQUIRED:item-type -->
- needed by: "be able to see if things changed from the outside" (the PO, 2026-11-26, #1738) <!-- REQUIRED:needed-by -->
- value proven by: `flow.py show` on a scratch copy of a project with no needs basis prints the "cannot tell" line, and after a hand edit of board.tsx the build phase says so <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1152 #1688 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Project history <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## N3 — the store has no shared side → the shared records Service on the same seam: a receive as a read-only layer first, then the filter and the share (story map slices 7 to 10)
- type: epic <!-- REQUIRED:item-type -->
- needed by: "definitely pushing and pulling things to some central repo, like the parts maybe and probably more things, the learned facts about parts, svg pictures" (the PO, 2026-11-26, #1738), D2 to D4 <!-- REQUIRED:needed-by -->
- value proven by: outcome (4) of brief.md's Frame, then the public repository's first commit, which the PO reads before and after <!-- REQUIRED:value-proven-by -->
- depends on: slice 0's seam (P1151 with P1152's first slice), the PO's answers P4 and P5, and the settings of brief.md's "Settings this epic names", which move into P1194 #1740 when it exists <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): epic <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): #123 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## N4 — nobody has counted what a share of today's 28 records would carry → a read-only dry run with a draft allow-list, which counts each string with the PO's name, a folder of his or a project name
- type: spike <!-- REQUIRED:item-type -->
- needed by: D3 and D4 (the PO, 2026-11-26), and P1 <!-- REQUIRED:needed-by -->
- value proven by: the count per field and per record, with 0 strings of the three kinds in what would go <!-- REQUIRED:value-proven-by -->
- depends on: D7 (the PO's answer to P1: none of these texts by default) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): N3 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## N5 — `GitRunner` starts git with its own process, so the core's effects gate never sees a keep, a send or a receive → before the first send slice, `GitRunner` moves onto `outside.run`, and `ProgramRunner` gains the group stop that `ProjectCommit._stop` has
- type: story <!-- REQUIRED:item-type -->
- needed by: "the architecture needs to be well made so that we can change these srtrategies and tools and its reusable, dry" (the PO, 2026-11-26, #1738), and the council's C17 (D6): later, with a card filed <!-- REQUIRED:needed-by -->
- value proven by: a test that pins every Operation that keeps or sends declares its effects, and a hook that ignores SIGTERM is still stopped through `outside.run` <!-- REQUIRED:value-proven-by -->
- depends on: slice 0 (P1151 with P1152's first slice). It comes before slice 9 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1152 #1688 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Project history <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## N6 — another maker cannot offer a record to the public repository → "send for review" by a fork and a PR, with a waiting state ("sent, waits for review")
- type: story <!-- REQUIRED:item-type -->
- needed by: D12 (the PO, 2026-11-26: "Fork with PR is a later card"), and #123's "people could use spark and share whatever good modules and parts and boards" (the PO, 2026-10-09) <!-- REQUIRED:needed-by -->
- value proven by: a second scratch account's record reaches the scratch central repository as a PR, and the person's list says it waits for review <!-- REQUIRED:value-proven-by -->
- depends on: slice 9 (the owner's share) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): N3 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- Filing N1 to N6, and the comments and body changes on #1688, #1687, #1691, #1689, #1699, #123, #437, #505 · pending, needs the PO's yes to this list, then spark-main files <!-- REQUIRED:board-actions -->
