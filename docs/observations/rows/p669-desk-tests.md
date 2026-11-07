# P669 the two desk tests: rows

What the plan check, the review and the session found while the spike ran. Card:
[P669 #897](https://github.com/xmejkal/spark/issues/897). Finding: `docs/observations/2026-11-07-p669-spike/finding.md`.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Comparing the record with `gdi.py` compares the record with a copy of itself, because `gdi.py:4-6` says its pins come from the record | refuter, plan check | acted | the schematic was read first, and the A1 table has a column for each value's origin |
| 2 | "plus record facts" let A2 pass by construction, since any per-kind logic can be renamed a fact | refuter, plan check | acted | a three-part test for a rule left over, fixed in the plan before the table |
| 3 | K2's case is a connector pin on a strap, not `NAMED_STRAP_REFUSAL`, and its outcome has three values | refuter, plan check | acted | the K2 row counts D7's case too, and the outcome column has stop, warn with the flag, and note |
| 4 | Q21's second half (does A1 settle Q7?) and who changes `verified: false` had no step | refuter, plan check | acted | a per-pin answer in the finding. No record changes in this PR |
| 5 | "kind" meant three things, and the plan's field names differed from the AR-9 diagram | refuter, plan check | acted | the finding uses the diagram's names, and "kind" is the K code |
| 6 | The fix to row 12 of the P663 rows file is outside this card | refuter, plan check | acted | left for the next rows PR |
| 7 | Pairing the hidden marker words of `pdftotext -bbox` by distance ties most P2 net labels to the pin one row up | session | raised | corrected by row 10. The visible words pair right, and the 600 dpi image confirms them |
| 8 | AR-9's `Claim` has no field for "this claim can move", but all four kinds need it for their outcome | session | raised | in the finding's hand-off for P665 #894 |
| 9 | `Claim` and `Conflict` clash with GLOSSARY.md:539-540 and :75,80 | session | raised | `PinClaim` and `PinConflict` proposed. The P665 plan council decides |
| 10 | The `-bbox` side finding's example was wrong: the visible label and pin number share a y, and only the hidden marker words are one row off | refuter, PR | acted | row 7's claim and the finding say to pair the visible words |
| 11 | The cited lines in `lcd.py` and `app.py` hold at firebeetle-games d05ad58, not 707e35a, and `app.py:130` passes MISO to `machine.SPI` | refuter, PR | acted | the finding cites d05ad58. MISO is still not exercised, since no code reads the bus |
| 12 | Six copies of `gdi.py` exist, not five (`firebeetle-games/backup/files/gdi.py`) | refuter, PR | acted | the finding says six, all sha1 c5d0281c |
| 13 | K2 got a note, but brief.md:76 and Q5 (a) say K2 stops. Under a stop A2 flips unless one attribute covers both strap cases | refuter, PR | acted | the verdict names the condition and the later decisions (D6, P665 #894, P527 #726) |
| 14 | The outcome from `movable` assumes Q10 answers no to a severity per kind | refuter, PR | acted | the second condition of the A2 verdict |
| 15 | The hand-off said nothing stops P665 after P664, but its "Depends on" also lists P527 #726, Q4, Q9, Q10 and Q20 | refuter, PR | acted | the hand-off lists them |
| 16 | brief.md:76 ("K1, K2 and K5 stop") disagrees with P665 #894 and P527 #726 (a connector's pin on a strap is named, not stopped) | refuter, PR | raised | for the P665 plan council, with Q10 |
