# P867: the closing refuter pass (refuter 4), 2026-11-17

Scope: `git diff 87efb601..9aa68162` of docs/discovery/2026-11-17-p867-journey-redefined/ (D5 to D18). Read-only.
It did not review commit 997a00a6 (D19 to D21). Result: 16 claims checked, 8 hold.

1. STALE, brief.md:12. "Decision needed" still names Q2, Q3, Q4 and Q6 to Q16, which are all answered except Q11.
   The checker does not catch this. Fix: name Q11, then the PO's yes to items.md and to D14 to D18.
2. STALE, lines in other files that the answers changed and nobody updated:
   - items.md:11, 31, 41, 61, 71 and 91 still depend on Q1 to Q5. Every "slice" line (15, 25, ...) still asks about
     Q12, which D15 answered.
   - story-map.md:30 still waits on Q12. story-map.md:8 and :24 put the bench test "before the wiring", but D9 says
     its place is not decided.
   - jobs-and-journeys.md:41, 43 to 45, 49, 61 and 63 still point to answered questions.
   - risks-and-tests.md:52 says it is "still to read" whether `vendor` is a maker. D12 says it was read. :53 says
     "in the queue", but D13 answered it. A2 to A12 say "Q1 sets it", but D18 sets no pass line.
3. GAP: no item and no row in the story map carries D6 (one previous version), D10 (a plan before a change), D12
   (the small view) or the table and page from D5 and D17. Fix: one item for the table and the page, and "later"
   lines at items.md:100 for D6, D10 and D12.
4. WEAKER THAN WRITTEN, brief.md:112. Q5 is marked "answered D5 (the line ... no graph)". The option the PO chose
   says only "a table of phases and a page of documentation, with no slice of its own". Nothing in it chooses a line
   or rules out a graph. Fix: "partly D5. line against graph is the reading of this session".
5. WEAKER THAN WRITTEN, brief.md:140. In D10 the option the PO picked read "what goes out of date, which wires you
   move at the bench, what is lost". D10 replaced "what is lost" with "what is kept as the previous version". Fix:
   use his option's words.
6. REFUTED in part, brief.md:59 and risks-and-tests.md:41. The grep count gives 10 dfrobot, 1 seeed and 4 other
   makers (15), and 18 files hold the key. The gap of 3 is `"vendor": null`. Those 3 are the Hadex and LaskaKit
   records. Their `sku` is the shop's code (D228A, LA217012, LA131042), so for them the view's "product code" is a
   shop's code, not the maker's. No record has a top-level url: the "12 hold a url" are URLs inside their sources
   and documents. ★C12's caveat says nobody read whether `vendor` is a maker, but D12 did. A10 says "counted by the
   lens", but this session counted. Fix: name the 3 null values and the shop codes, correct the two attributions.
7. HOLDS, but D6 is incomplete (code read, not run). kept_files.py:301-307 and :322-326 do delete the earlier
   files. One case does the opposite: when the sheet stage itself refuses (:194-199), built-from.json is rewritten
   first and the old breadboard.md is left in place, listed as "not written". D6 never says that P280's rule (a
   refused build removes earlier outputs, verification.md:39) must be reversed. Fix: one sentence in D6.
8. REFUTED, D18 against brief.md:11. "Stands on" counts A3 as rated high, but D18 (:148) gives A3 no rating.
   risks-and-tests.md:34 says "high. answered D7". The PO's own wish (n = 1) does not answer "a person wants", which
   is the risk A12 rates high. Fix: keep A3 and A7 open, cite D7 and D10 as his n = 1 evidence, rate them in D18.

Holds: D16 (AGENTS.md:29-30 and the firmware decision's lines 88-97 forbid exporting behaviour into a gadget. spark's
own answers already carry a `next` list, outcomes.py:103). D14: the PO wrote "yes, go on fully automatically" at 12:25:55 Prague. It was a reply to a message that listed
Q11 to Q16 and the ratings. Each delegated answer is marked as the
session's own). The option texts behind D6, D7, D9, D11 and D12 match what the rows say.

## Searches

- none

Commands and reads, in order: `git diff 87efb601..9aa68162` of the folder. A search for the `vendor` values in the store's catalog with a count of the record files (15 values, 18 files, 3 with `null`). Read and not run: scripts/spark/build/kept_files.py:194-199, :301-307 and :322-326, AGENTS.md:29-30, docs/archive/2026-10-01-firmware-and-tests.md:88-97, scripts/spark/outcomes.py:103. `discovery.py check` on the folder: "Output check: pass" at 9aa68162.
