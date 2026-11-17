# P867: the fifth refuter pass, on D19 to D22, the Hand-off and commit 9cafca31, 2026-11-17

Read-only. 23 claims checked, 13 hold. It could not check the PO's exact answers behind D19 to D22, which a second
session recorded.

1. REFUTED, D21 and the Hand-off's Order line. P869 #1236 could not take items.md as worded: its inputs were the
   three rows files, it held 0 comments, and no board action told it. Fix: a comment on #1236 that names items.md and
   the Q16 row.
2. WEAKER THAN WRITTEN, "eight command fixes". items.md holds 1 spike and 8 stories. Four of the eight are fixes to a
   command, four are new behaviour, and the order line waits on Q11. Fix: "eight items".
3. GAP, nothing owns the outcome. D21 files no card, so the table and the page, and D10's plan before a change, are
   only "later" lines, and P829's wait (D11) has no end. Facts for a testable card: `PHASES` in
   scripts/spark/flow/flow_codes.py:9 lists the nine phases. docs/guide/agents/flow.md is a page of them. A Done-when
   that can fail is a test that the page's table equals `PHASES`, as tests/test_journey.py does for the picture.
   Gaps: where the table lives, the bench step's place (D9), and that D6 and D10 are not built.
4. WEAKER THAN WRITTEN, the Hand-off's Proof line. It drops the Frame's firmware pin check and "recorded / none
   recorded", it tests `flow.py show` and not the table and page, and it promises a next step while `next` is `[]`.
   The Hand-off does not say that the Frame's outcome was narrowed (D17, D15).
5. WEAKER THAN WRITTEN, "Still open" and "Decision needed: none now". They leave out D6's undecided reversal of
   P280's rule, D9's open order and states, Q5's line-or-graph reading, and A3 and A7.
6. WEAKER THAN WRITTEN, the Hand-off's Rules. They drop D7's "until P868 #1235".
7. STALE: items.md's nine slice lines still end with "(Q12)". story-map.md:8 fixes the bench test's place.
   risks-and-tests.md:9 brings back ★C16's rejected wording, :10 names the sound demo, :11 and :12 say "paper spike"
   and "slice 0", :49 says "after Q1 sets its pass line". verification.md lists only the second pass.
8. HOLDS: the checker ("Output check: pass"), the jobs (D19), D20, the Ready-for line and "11 H, 4 high".

## Searches

- none

Commands and reads, in order: `git show 9cafca31` of the folder, `gh issue view 1236 -R xmejkal/spark`, a read of
scripts/spark/flow/flow_codes.py:9 and docs/guide/agents/flow.md, and `discovery.py check` on the folder.
