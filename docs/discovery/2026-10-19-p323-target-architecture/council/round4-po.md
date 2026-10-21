# Round 4: the PO's voice

> **TL;DR.** The shape is right, but the paper is too big to read and puts readability nowhere first. Cut it to
> about 150 lines with readability as goal one, fix the stale walk 1 question, and run the refactor as slices that
> each follow a walk 2 need.

## Findings

1. **Readability is his first word, and the design does not rank it.** His ask lists readability "most of all".
   The design leads with packages, Operations and an AST test. The rules that serve reading (S1 role word, S5 thin
   door, S6 size, S12 names) are mixed with 14 others. Fix: name five goals in his order (readable, testable,
   exchangeable, reusable, consistent) and put each rule under the goal it serves.
2. **No answer to "how does a reader find the code".** A person or Claude opening `scripts/spark/bench/` needs one
   place that says what the area does and which Operations it holds. Fix: each area's `operations.py` starts with a
   short docstring that is that index, and `look` after slice 2 is the worked example every later move copies.
3. **Too big to decide on.** 463 lines, 13 papers (about 1300 lines) and 116 rows. Three history tables come before
   the TL;DR, so he reads the past before the proposal. His rule wants a short Council section at the top, not three
   tables. Fix: five lines of council at the top, everything else in the rows file.
4. **Section 8 is stale.** Walk 1 is done (PRs #447 and #449). The live date is walk 2 by 2026-10-27 (P378 #484,
   P305 #371). The TL;DR still says "before walk 1". Fix: ask the question against walk 2.
5. **The product bar is missing.** Nothing says how this moves a basic project closer to a breadboard with working
   firmware. The link exists: codes and `next` steps for `look`, `deploy` and `check_all` are what Claude reads on
   the bench. Fix: one sentence in the TL;DR, and order the per-story slices by what walk 2 finds.
6. **Slice 2 is not one step.** About 500 lines: a 39-importer move, five new classes, path shortening, secret
   masking and the consent refusal. Fix: 2a moves `outcomes` only (mechanical). 2b adds `Operation`, `run_door` and
   the `look` door. 2c adds masking and consent with the first Operation that needs them (`deploy`).
7. **18 rules at once is a wall.** Fix: slice 1b turns on the rules that have no breach today as hard rules, and the
   rest enter the baseline. The final design shows the 18 as a reference table, not in the body.
8. **Names to check against developing.md's table.** `Layers` does not say its role (it is the record folders). Try
   `RecordFolders`. "door" is coined, though section 4 defines it. Keep it only if he reads it at a glance.
9. **Speculation is mostly gone, keep it gone.** `FirmwarePlatform` stays: it is his 10-15 word (board code behind
   a platform-neutral interface). `SimulationEngine` stays a Strategy only with a Fake, as S13 says. Dry run stays
   deferred. Good.

## The final design he reads (about 150 lines)

1. TL;DR in a quote block, then three sentences, then "Your call" with the open questions.
2. Council: five lines, which rounds ran and what they changed most.
3. One picture: doors, areas, core. One sequence for `look`.
4. Five goals in his order, each with its two to four rules and how a test enforces them.
5. How a reader finds code: the area index and the worked example.
6. Slices: one table row each, with "adds one thing", its size and "Done when".
7. What we will not do. Then a reference appendix: the full rule table, vocabulary, seams.

## Decisions for the PO, in this order

1. **Readability first.** Is the order readable, testable, exchangeable, reusable, consistent right?
2. **The shape.** Yes or no to scripts as thin doors over one package, one Operation per job, one rules test.
3. **Slice 1a before walk 2 or after it.** (a) 1a lands this week, about 220 lines, no output changes, and its
   goldens catch a change in what walk 2 runs. (b) Walk 2 first. Walk 2 is due 2026-10-27, so I lean to (b) unless
   1a merges by 2026-10-23.
4. **When the area moves start.** Until v0.13 only per-story pay-down (D13). He confirms or names a date.

Not his: the 60, 600 and 40 line limits, the codes, the S-rules. The council decides those.

## Rows

- Readability not ranked first; group rules under five goals in his order, readable first.
- No reader index per area; `operations.py` docstring as the area index, `look` as the worked example.
- Design too long to decide on; cut to about 150 lines with the shape above, history to the rows file.
- Section 8 and TL;DR say walk 1, which is done; re-ask against walk 2 (2026-10-27).
- Product bar not stated; say codes and `next` steps help the bench, order slices by walk 2's findings.
- Slice 2 holds several things; split into 2a (move outcomes), 2b (Operation and look door), 2c (masking, consent).
- 18 rules shown at once; hard rules where breaches are 0, the rest in the baseline, full table in an appendix.
- `Layers` does not say its role; rename to `RecordFolders`, and check "door" with the PO.
- PO decisions unordered; ask the four above in order, one at a time.
