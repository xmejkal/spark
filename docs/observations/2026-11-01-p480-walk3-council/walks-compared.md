# Walks 1 to 3 compared

> Seven causes come back in two or more walks. Two of them come back in all three: the board's own parts (LED, button) and the unsaid
> effects of a command. Plan.md fixes the board's own parts and the pages first. It leaves out four cards that walks raised twice or more.
> Walk 3 is the first walk that reaches a lit LED through spark's own deploy, so the chain works and the gaps now sit in what it says.

Sources: the seven rows files, plan.md, and `gh issue view` (read only, 2026-11-01). "W1 5" means walk 1's P326 row 5.
Walk 1 is p326 and p330 (T-Display). The photo walk is p366. Rehearsal is `2026-10-31-walk3-rehearsal.md` (R). Walk 2 is p400 (G rows).

## 1. Gaps that repeat

| # | gap | rows by walk | card each time | card now |
|---|---|---|---|---|
| A | The board's own LED and button are not parts | W1 2, 3, 10, 19 (P330 30); W2 G7, G23; R 1, 3; W3 G13, G20, G28, G29 | P332 (#426), P355 (#453), P389 (#504), P396, P397, P467 (#635), P447 (#599), N2, N3 | P332, P467, P447 open. P355, P389, P396, P397 closed. N2, N3 not filed |
| B | The simulation cannot press or see them, and "passed" says too little | W1 6; W2 G23; R 3; W3 G24, G28, G31, G32 | P396, P397, P345 (#440), N4, C1 | P396, P397, P345 closed. N4, C1 not filed |
| C | A serial-monitor warning that the run disproves | W1 6; W2 G18; R 4; W3 G26, 41 | P213 note, then none ("cause stays open"), P468 (#636), P468 rewritten | P468 open, the rewrite is not filed |
| D | "not asked for" on skipped checks | W2 G1, G22; W3 G6 | P118 (#52) both times | open, never done in three walks |
| E | A command writes the store and says nothing | W2 G2, G4, G5, G25; W3 G5, G8, G17, G25, G27 | P137 (#71), P118, N2 of P400 (P402 #519), N6, N7 | P137 open. P402 closed. N6, N7 not filed |
| F | The look restarts the board, or needs two button presses | W1 P330 26; R 10, 28; W3 G19, G34 | P469 (#637), P462 (#630), P472 (#643) | P469 open. P462, P472 closed |
| G | The look's status and `next` mislead | W1 P330 17, 22; W2 G27; W3 G3, G18, G36 | none for W1, P401 (#518) for erase only, N8 | N8 not filed. P401 closed |
| H | Which unit or board is on USB | W1 P330 21, 31; W2 G10; R 9; W3 G1, G7, G15 | P333 (#427), P403 (#520), P466 (#634), N9 | P466 open. P333, P403 closed. N9 later |
| I | `--match` and `--offer` show old or noisy output | W2 G8, G9; W3 G11, G12 | P314 (#388), P390 (#505), P406 (#531) | all three open |
| J | The example firmware lacks console lines that read without waiting | W2 G24; W3 G30 | P77 (#13), then N6 | P77 open. N6 not filed |
| K | The firmware build or image for the chip is wrong or unknown | W1 11, 17; W2 G16; R 16, 17, 18 | P335 (#429), P349 (#445) | P335 closed. P349 open, three walks |
| L | A board's Wokwi definition is not kept | W2 row 66; R 3; W3 G13, G29 | P391 stage 4, P447, N2 | P447 open. N2 not filed |

Never filed or only a row: the unlist command (W3 G10, plan drops it), the doubled `does` words (G12), the hand-edit rule (G33, now N1).

## 2. The kinds that come back, and the root cause

1. **Effects nobody says (E, G, J).** The root is in the process: a command's effects are written by hand into a page, and the page drifts.
   The code holds a list of effects (`parts.py:1599`) but `--help`, the pages and the verdicts do not read it. So every walk finds one more.
2. **A board's own parts (A, B, L).** The root is in the code: a part is a record with a Wokwi type, and a board's LED or button is a
   `pin_roles` row with no part. `board_alone` (`check_spine.py:583-586`) draws the devkit alone. Each card fixed one reader and not the seam.
3. **Words that mislead (C, D, G).** The root is that a message is a literal string at the place that finds the fact, and nobody tests it against a
   second case. "not asked for" has two causes (`check_spine.py:547`). The serial warning reads no board fact.
4. **The simulation's honesty (B).** The root is a verdict built from a flag ("passed") where the log has step counts. Each walk adds one limit
   line (P396, P345, N4). The cause is that the verdict is not built from what was tested.
5. **The board as a moving target (F, H, K).** The root is that a board's USB and download behaviour sits in tool fields, not in the board
   record, so each unit and each build is a surprise. P472 and P349 hold the facts, and the look does not read them yet.
6. **Cards that wait (D, I, J, K).** The root is the process: P118, P314, P390, P406, P77, P349 are small, open for 3 walks, and not in anyone's rank.

## 3. What improved

- Walk 1 copied firmware with `mpremote` outside spark (W1 7, 8). Walk 3 deployed through spark and the LED lit (plan.md, intro).
- Erase without naming what it replaces (W2 G29) did not come back. P401 closed. Held board "free 0" (G10) did not come back. P403 closed.
- The brief's goal never reached idea (W2 G6). Walk 3 has no such row. P402 closed.
- One CP2104 board as two ports (W1 P330 21) did not come back. P333 closed.
- The rehearsal's failed flash (R 29, 37) has its fixes merged: P461, P462, P463, P464 all closed.
- Walk 2 had a paid run with "passed" and no must line named (G23). Walk 3 has a free run, and the gap shrank to one bare verdict line (row 52).
- The rows are better checked: P400 had 95 rows with 9 "raised" claims unchecked. Walk 3's 54 rows are all checked, with 8 refuted (rows 39-46).
- Not improved: D, I, J, C, K. Each is a small open card.

## 4. Does plan.md's order fix the repeating causes first?

Partly. It starts with N4 and N6 (kinds 1 and 4), then N2, N1, N3 (kind 2). That fits. It misses four cards that came back:

| change | reason |
|---|---|
| Add P118 (#52) at rank 2, beside N6 | XS words. It is the one gap in walks 2 and 3 with the same row, and no rank holds it. |
| Move P468 (#636) above N1, to rank 3 | It is in four walks (C). It is XS and N3 does not need it. N1 keeps its rank for the lost-edit bug. |
| Move P469 (#637) above N5, to rank 7 | Three walks (F), and every walk pays two presses. N5 is a mistake that N6 already lowers. |
| Put P467 (#635) next to N3, after it | Cause A also shows in `--match` order. N3 alone leaves the old ranking. |
| Add P314 (#388) and P390 (#505) as one XS pair after N8 | Walk 2 G8 and walk 3 G11 are the same row. It is a record that lives in one project. |
| Move N7 (effects) above N8 | Cause 1 is the widest in the table. N8 is one step of the same family (status words). |
| Keep P349 (#445) out of the rank, but give it a PO question | Three walks name it. A card that is "refinement" for that long needs a yes or a close. |
| Keep P476 (#652) last | Plan.md is right: W4-2 keeps deploy's lines byte-equal. |

Not checked: the diaries (only rows used), the code at `53c1cbb8`, and whether P118 and P406 have a body that already blocks a rank.
