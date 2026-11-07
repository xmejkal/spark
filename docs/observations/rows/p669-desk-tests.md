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
| 7 | `pdftotext -bbox` alone ties each P2 net label to the pin one row up, because the label sits above its wire | session | raised | the 600 dpi image of page 1 gave the right pins. A schematic text reader needs an image check |
| 8 | AR-9's `Claim` has no field for "this claim can move", but all four kinds need it for their outcome | session | raised | in the finding's hand-off for P665 #894 |
| 9 | `Claim` and `Conflict` clash with GLOSSARY.md:539-540 and :75,80 | session | raised | `PinClaim` and `PinConflict` proposed. The P665 plan council decides |
