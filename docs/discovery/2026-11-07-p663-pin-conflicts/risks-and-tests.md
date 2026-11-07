# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | E ★C17: one walk blocked, the gadget runs from hand-typed pins. H A3, A9: a second consumer and K6's demand | Q16 to the PO: which walk comes next | open |
| usability <!-- REQUIRED:risk-usability --> | D1, n = 1 (A4). H A8: Claude as data (★C2 says no today) | one question run on P581 with Claude relaying, answered in one turn, no re-ask on the second build | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | H A2 (one shape), A1 (★C5: the pins are `verified: false`), A5 (★C14, ★C16) | A2 on paper (R0, under an hour). A1 by eye against the kept V1.3 schematic | open |
| viability <!-- REQUIRED:risk-viability --> | H A6 (a new stop against "must not get worse"), A7 (★C9: no date for wave 6) | run the stop on walk3, walk4, reaction-game and the examples. Q2 to the PO | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E ★C11, ★C12: every observed kind is bookkeeping or wrong data, not damage. H: two drivers on one net (PH-11) is the damage case and no record holds a reset-time level | n/a because no observed kind damages hardware. A reset-level fact per part pin is a later record need (PH-16) | n/a because the model changes pin bookkeeping, not currents |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | — | n/a | n/a because the card changes pin assignment, not the supply |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | H ★C12: GPIO21 sources about 2.8 to 3.4 mA calculated against IOH 40 mA datasheet-typ (PH-4) | none needed. If the LED forward voltage matters, a meter in series with the module's LEDA (R6) | n/a because 7 to 9 percent of IOH |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | — | n/a | n/a because no dissipation changes |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | — | n/a | n/a because no fast edge or touched part changes |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | — | n/a | n/a because no sensor is read |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | — | n/a | n/a because no rail peak changes |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | — | n/a | n/a because no wake pin is in the kinds seen |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E ★C4, ★C7: `pins.py` says TFT_DC 11 while the cable holds 3, and GPIO21's second job is unnamed. H ★C11: GPIO3 is "Ignored" on a default chip, GPIO0 is the strap that bites | R0: the eight GDI pins against the kept V1.3 schematic (A1). R6: `espefuse.py summary` read-only over USB for the JTAG eFuse (Q12) | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | E ★C5: the GDI table is read off a schematic image, `verified: false`, and the wiki disagrees on FCS/BUSY labels. H PH-14: V1.1 and V1.2 boards differ on I2C pull-ups and the button | R0: cite the V1.3 schematic page with its sha256 (P460's open job). Read the board's revision into the connector fact | open |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | The FireBeetle's GDI pins as the part record gives them (BL 21, SCLK 17, MOSI 15, MISO 16, DC 3, RES 38, CS 18, SDCS 9) are right | feasibility | H ★C5: read off an image, `verified: false`. The games run with 18, 9, 3, 38, 21 on hardware (★C17) | — (decider) | R0: compare to the kept V1.3 schematic page 1 (sha256 4062428a…) by eye, and to the games' `gdi.py` | all 8 match both, set 2026-11-07 | any mismatch: the first slice waits for P460's citation | open |
| A2 | One shape (a resource with an owner and a claimant) covers K1, K2, K3 and K5, not only K1 | feasibility | H ★C1, ★C7: four mechanisms today, no shared code (AR-3) | — (decider) | R0: write the four seen kinds as rows against one record shape and count the rules left over | at most one per-kind rule left over for 4 of 4 kinds, set 2026-11-07 | more than one: the kinds are separate fixes under one name, not a model | open |
| A3 | A second consumer exists soon (the camera connector, a second board, P332's onboard parts) | value | H: P332 #426 and K4 exist. No walk planned for either | — (decider) | Q16 to the PO | at least one named with a walk card or a date, set 2026-11-07 | none named: build the GDI fix, not the model | open |
| A4 | The person wants to be asked "cable or wires?" and answers in one turn | usability | D1 (the PO chose B, 2026-11-07), n = 1 | — (decider) | on P581, one question run with Claude relaying | answered in one turn, no re-ask on the second build, set 2026-11-07 | a re-ask or a stall: the default places without asking (option A) | open |
| A5 | An answer lives in one place and survives a rebuild and `--keep` | feasibility | H ★C14 (the file keeps unknown keys), ★C16 (kept files drift) | — (decider) | change the answer, rebuild with `--keep`, read `pins.py`, the sheet and the kept `board.tsx` | all three agree with the new answer after one rebuild, set 2026-11-07 | one disagrees: P660 #886 goes first | open |
| A6 | A new stop for a left conflict breaks no project that builds today | viability | H: the brief's "must not get worse". No run | — (decider) | run the stop on walk3, walk4, reaction-game and the shipped examples | 0 new stops on projects with no real conflict, and every new stop names two claims and a pin, set 2026-11-07 | one false stop: the stop becomes a note first | open |
| A7 | The model can wait for wave 6 without the P581 walk being lost | viability | D2 (the PO). ★C9: no date in the plan | — (decider) | Q2 to the PO: "soon" in weeks, or a yes to a bridge | a date, a number of weeks, or a yes, set 2026-11-07 | no date and no bridge: the walk stays paused | open |
| A8 | Claude can act on a conflict as data (kind, claims, pin, choices) without reading the script | usability | E ★C2: not today. H the AI-UX lens | — (decider) | read what `assign_pins.py --json` prints on the P581 conflict after the first slice | kind, both claims, pin and choices present as keys, no parse of English, set 2026-11-07 | a sentence to parse: the interface repeats logic | open |
| A9 | Existing wiring (K6) can wait until a walk fires it | value | H: the PO said later (#892). P581 row 11 and P364 #466 describe it as the next journey | — (decider) | Q16: does the next walk start from a wired project? | the next walk is not #466, set 2026-11-07 | the next walk is #466: K6 moves into the first epic | open |
| A10 | K2 on the PO's board is bookkeeping: the JTAG eFuse is at its default | feasibility | H ★C11, the datasheet's table, not his chip | — (decider) | R6: `espefuse.py summary` over USB, read-only (Q12) | `EFUSE_STRAP_JTAG_SEL` = 0, set 2026-11-07 | burned: DC on GPIO3 needs the strap's level named in the sheet | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Are the eight GDI pins right (A1)? <!-- REQUIRED:collection --> | the first slice's data | the session, from the store | R0: the kept V1.3 schematic page 1 by eye, plus `gdi.py` | before the first story starts |
| Does one shape cover four kinds (A2)? | whether this is a model or four fixes | the session, with the Architecture lens's AR-9 | R0: a one-page table, no code | before the plan |
| What does D2 mean, and what is "soon" (A7)? | Q2 | the PO | AskUserQuestion, one question | next session |
| Is the JTAG eFuse at its default (A10)? | the strap's wording | the PO's bench, with his yes | `espefuse.py summary`, read-only | at his next bench time |
| Does a new stop break a project that builds today (A6)? | the walking skeleton | the session | run the stop on walk3, walk4, reaction-game, examples | with the first PR |
| Which walk comes next (A3, A9)? | Q16, the model's second consumer | the PO | one question | next session |
| What does the shelf copy of the DFR0664 record say, against the fixture? | ★C5's caveat | the session | `diff` the two files | before the first story |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a — no battery, motor, radio or regulator changes with this card. One pin figure, kept for the record: GPIO21 sources about 2.8 to 3.4 mA (calculated by the Physics lens from R15 2K, R3 1K and Vbe 0.7 V assumed) against IOH 40 mA (datasheet-typ, ESP32-S3 datasheet v2.2 Table 5-4 p.65). The rung that settles the LED branch is R5, a meter in series. Not needed for a decision.
<!-- EXTEND:risks-sections -->
