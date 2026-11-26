# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

From council/synthesis.md part 6. Comments on open cards come first, and a new card only where no card owns the job
(council/po-assistant.md PA-6). N1 to N4 were working names. This session read the next free P-number just before it
filed each one, on spark-main's word (D10). Items 4, 5, 7 and 9 waited on Q4, and item 10 on Q5. D4 and D5 answered both, each with option (a). The question numbers are the brief's. Before the MVP nothing here is code.

## 1. A comment on P1199 #1747: the first evidence is Q1's answer and the 14-day log
- type: comment on an open card (no change of scope) <!-- REQUIRED:item-type -->
- needed by: "being also able for humans to edit the connections and move the parts around ?" (the PO, 2026-11-26, #1747) <!-- REQUIRED:needed-by -->
- value proven by: the log's lines in the store's bench file, read against A1's pass line <!-- REQUIRED:value-proven-by -->
- depends on: D9 set the pass line (at least 3 log lines in 14 days, set 2026-11-26) <!-- REQUIRED:depends-on -->
- status: filed D10: comment https://github.com/xmejkal/spark/issues/1747#issuecomment-7193783520 (with item 8) <!-- REQUIRED:item-status -->
- label (the repository's type label): — (a comment) <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## 2. A comment on P269 #304: its common base is P1199's layout core, and P269 keeps the views
- type: comment on an open card
- needed by: "please also create some common base" (the PO, 2026-10-16, #304)
- value proven by: #304's body points to P1199 for the base, and no second base is planned
- depends on: —
- status: filed D10: comment https://github.com/xmejkal/spark/issues/304#issuecomment-7193784095
- label (the repository's type label): — (a comment)
- parent (the epic, as a sub-issue): —
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## 3. A comment on P1194 #1740: the setting rows this epic names
- type: comment on an open card
- needed by: "for now just remember it for all configurable streategies and things like this" (the PO, 2026-11-26, #1740)
- value proven by: the ten rows of brief.md "Settings this epic names" on #1740
- depends on: —
- status: filed D10: comment https://github.com/xmejkal/spark/issues/1740#issuecomment-7193784619
- label (the repository's type label): — (a comment)
- parent (the epic, as a sub-issue): —
- slice (one Slice option of the board, or "ask the decider for a new one"): 10 The store

## 4. A comment on P1152 #1688 (D4): the layout's kept row is the edits record, at slice 2
- type: comment on an open card
- needed by: "This time its regarding the  breadboard layoutand wiring, the PCB, the perfobard ayout etc" (the PO, 2026-11-26, #1738)
- value proven by: #1688's slice 2 lists the layout row, and slice 5 keeps board.tsx alone
- depends on: D4 (answered, option a)
- status: filed D10: comment https://github.com/xmejkal/spark/issues/1688#issuecomment-7193785194
- label (the repository's type label): — (a comment)
- parent (the epic, as a sub-issue): —
- slice (one Slice option of the board, or "ask the decider for a new one"): Project timeline

## 5. A comment on P1202 #1751 (D4): the build records a digest of breadboard.json to notice a hand edit
- type: comment on an open card
- needed by: "be able to see if things changed from the outside" (the PO, 2026-11-26, #1738)
- value proven by: #1751 names breadboard.json's digest and the offer to import a hand edit, with no kept-step row for the file
- depends on: D4 (answered, option a)
- status: filed D10: comment https://github.com/xmejkal/spark/issues/1751#issuecomment-7193785962
- label (the repository's type label): — (a comment)
- parent (the epic, as a sub-issue): —
- slice (one Slice option of the board, or "ask the decider for a new one"): Project timeline

## 6. N1: the words for layout, layout edit, join and footprint, and the three op names (after the MVP)
- type: chore
- needed by: "the architecture needs to be well made so that we can change these srtrategies and tools and its reusable, dry, etc etc" (the PO, 2026-11-26, his standing line for every brief, in the store's spark-main handover note)
- value proven by: docs/guide/words.md holds the four rows and says which "layout" is which (BreadboardLayout against PillLayout)
- depends on: —
- status: filed D10: P1236 #1789, a sub-issue of #1747, Idea, Views and editors
- label (the repository's type label): chore
- parent (the epic, as a sub-issue): P1199 #1747
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## 7. N2: the walking skeleton of the layout core on the breadboard (after the MVP)
- type: story
- needed by: "Can we refactor out some protocole or omdule or class or whatever to reuse for these common problems?" (the PO, 2026-11-26, #1747)
- value proven by: `layout.py edit --part ... --hole ... --dry-run` names a refusal before any write, a part edit stays after a rebuild on the FireBeetle full board, and tests.test_golden_breadboard keeps 8 of 9, with the rebuild golden's diff read and accepted (D13). The edit's key reuses bench_changes' step key
- depends on: N1, D3 (after the MVP), D4, D6, and #94's breadboard PR (council/tech-lead.md cost table)
- status: filed D10: P1237 #1790, a sub-issue of #1747, Idea, Views and editors
- label (the repository's type label): story
- parent (the epic, as a sub-issue): P1199 #1747
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## 8. Lines in P1199 #1747 for the slices after the skeleton
- type: comment on an open card (lines, not cards, until each is next)
- needed by: "options to go for the smallest size or to take up the whole perfobard and use the space" (the PO, 2026-11-26, #1747)
- value proven by: #1747 lists join edits with the Wokwi importer, `plan-layout`, then the goal member with `layout-placement`
- depends on: N2
- status: filed D10: in the comment of item 1 on #1747
- label (the repository's type label): — (a comment)
- parent (the epic, as a sub-issue): —
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## 9. A comment on P293 #352: Claude's "put it there" is `edit-layout`, and a pin change is a design change
- type: comment on an open card
- needed by: "I would like to just kind of tell Claude, and he would do it for me on the board" (the PO, 2026-10-18, #352)
- value proven by: #352 names `edit-layout` for the place and the design area for "Connect it to pin number 20"
- depends on: D4
- status: filed D10: comment https://github.com/xmejkal/spark/issues/352#issuecomment-7193786547
- label (the repository's type label): — (a comment)
- parent (the epic, as a sub-issue): —
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## 10. A comment on P1163 #1699 (D5): the page's move is one request to `edit-layout`
- type: comment on an open card
- needed by: "I'd also lke to be able to change the position of elements and wiring etc on the breadboard (later also on perfboard)" (the PO, 2026-11-25, #1699)
- value proven by: #1699 names `edit-layout` as the page's one call, with its findings and P1202's `changed` list as the effects, and run-request carrying a drag's values for an allow-listed Operation (D5, a change P1082 #1587 owns)
- depends on: D5
- status: filed D10: comment https://github.com/xmejkal/spark/issues/1699#issuecomment-7193786997
- label (the repository's type label): — (a comment)
- parent (the epic, as a sub-issue): —
- slice (one Slice option of the board, or "ask the decider for a new one"): parked, after v0.10

## 11. A comment on P1162 #1698: the drag on the breadboard and the perfboard is P1163's
- type: comment on an open card
- needed by: "adding drag&drop to the pages" (the PO, 2026-11-25, #1698)
- value proven by: #1698 points the layout's drag to P1163 and keeps the other pages, with P294's drag layer named
- depends on: —
- status: filed D10: comment https://github.com/xmejkal/spark/issues/1698#issuecomment-7193787519
- label (the repository's type label): — (a comment)
- parent (the epic, as a sub-issue): —
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## 12. A comment on P275 #311: the perfboard is one more surface kind of the core
- type: comment on an open card
- needed by: "they can be made smaller but not bigger" (the PO, 2026-11-26, #311)
- value proven by: #311 names the join router, the three join kinds, the grid facts in the drawer record, the same-pins check over joins, the cut size in holes, and spikes B and C first
- depends on: —
- status: filed D10: comment https://github.com/xmejkal/spark/issues/311#issuecomment-7193788091
- label (the repository's type label): — (a comment)
- parent (the epic, as a sub-issue): —
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## 13. N3: a spike, the FIT0193's grid facts (under #311)
- type: spike
- needed by: "we probably want to be able to set what sizes of perfboards the user has available" (the PO, 2026-11-26, #311)
- value proven by: the drawer record holds pitch, pad kind, holes across and holes down, each with its origin
- depends on: D8 (he measures it with calipers when the perfboard card is pulled)
- status: filed D10: P1238 #1791, a sub-issue of #311, Idea, Views and editors
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P275 #311
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## 14. N4: a spike, a pad-lattice router with an insulated-jumper fallback (under #311)
- type: spike
- needed by: "using good algorithm to offer the best options of routing" (the PO, 2026-11-26, #1747)
- value proven by: on button-light and one motor circuit, with the roomy goal by default (D7), every net joined or named, the jumper count and the seconds written down, against a pass line set before the run. perfwire's solver and stripboard-py's router spec read first (D-q6)
- depends on: N3
- status: filed D10: P1239 #1792, a sub-issue of #311, Idea, Views and editors
- label (the repository's type label): spike
- parent (the epic, as a sub-issue): P275 #311
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- Filing items 1 to 14 · taken 2026-11-26 by this session on spark-main's word, D10. Four cards and nine comments (items 1 and 8 share one) <!-- REQUIRED:board-actions -->
