# Risks and tests

## Risks
<!-- One row per type. evidence now: tag and ids (★C<n>, A<n>). status: open, retired or n/a because …. -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H no soldering date and no evidence of a soldered perfboard (★C4, A1). The step scores zero on the MVP bar (★C3) | Q6, one question: which gadget and which board first | open |
| usability <!-- REQUIRED:risk-usability --> | H the mirror and the turn of the board (★C8, A3), a bare wire named by its two ends only (★C7) | Q9, an account, then a dry rehearsal on an offcut with no solder (A3) | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | E first fit refuses parts on single pads, measured (★C10). Two crashes with no row letters (★C11). H one search with a jumper edge (A5) | the seam moves with the 9 goldens (A4, A6), then spike P1239 (A5) | open |
| viability <!-- REQUIRED:risk-viability --> | E the MVP cards first (★C3). H the lane cost, sessions not checked (PA-3). H if P1237 and P1350 change the code, the paper is redone (PA-9) | Q2 on the order. Keep the design short and decision-shaped | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | H a solder blob between two pads of different points shorts 3V3 to GND (UL-8) | the beep list with 3V3 against GND first, before USB (story map slice 1) | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | E at 1.5 A, 50 mm of 24 AWG drops 6.2 mV, a one-pitch bridge 0.32 mV (P1199 EP-2, calculated). No record holds a cell | n/a now: no battery record. A cell holder brings its own rules | n/a because no record holds a cell |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | E the L9110S at 0.8 A a channel (stated), under the guide's 20 AWG line for amps (TL2-18). No 30 AWG wire-wrap over 0.5 A (TL2-6) | a rule in the join weights: a net's current from its largest consumer picks the wire | open |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | H soldering a dev board straight in puts heat next to the module (TL2-20) | female headers by default (Q4) | open |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | E Espressif: the antenna past the base board's edge (TL2-8). E no board record names its antenna end (★C17) | if the placer needs it, one record fact: the antenna end, with its origin | open |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | none: the layout changes no sensor | — | n/a because the perfboard moves no sensor's reading |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | E the drops above are under 10 mV at 1.5 A (P1199 EP-2) | none needed at today's records | n/a because the drops are under 10 mV |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | none: the layout changes no pin or mode | — | n/a because the pins stay the tested ones |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E D-b: a fresh plan keeps the tested pins. H the plan's `pins_kept` against pins.py (UL-5, UL-10) | the same-pins check over the joins as sets of holes (★C15) and `pins_kept`, which is true only if equal | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | E the drawer holds no pin header and no female socket (UL-7). E the FIT0193 has no hole facts (★C5) | P1238, the PO's calipers. The parts table lists "to get" | open |

## Assumptions
<!-- About ten at most. importance: "— (decider)" until rated. pass line: written, with its date, before any result. -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | He solders a perfboard within a few months of this design (PA-9), before the code it describes moves | value | H PA-4, PA-9 (★C4) | — (decider) | Q6, one question | proposed: he names one gadget and one board he plans to solder, set 2026-11-28 | "none planned yet": keep the design to the shared parts and the walking skeleton | open |
| A2 | A plan in text and JSON on the CLI (slice 0) is a result he calls done | value | H PA-6 | — (decider) | Q3, one question | proposed: he picks the text plan as the first done, set 2026-11-28 | he needs the drawing or the page first: slice 0 grows | open |
| A3 | A person who follows the step sheet puts each joint in the right hole after turning the board | usability | H UL-4 (geometry) | — (decider) | Q9 (an account), then a dry rehearsal on an offcut with no solder | proposed: 0 joints in a wrong hole, of every joint the button-light plan names, set 2026-11-28 | one joint in a wrong row: the sheet says how to turn, or the view mirrors the other axis | open |
| A4 | One `GridSearch` lifted from `TrackRouting` keeps 9 of 9 golden breadboards byte for byte (at most 5 of them draw a route) and `cut_short` equal | feasibility | E ★C13, ★C14 (code read). H the heap's tie order | — (decider) | the move itself after P1350, the hook's story run | proposed: 9 of 9 goldens equal and tests/test_wire_routing.py passes, set 2026-11-28 | one golden moves: the search keeps its own copy until the order is understood | open |
| A5 | One A* over a two-face pad lattice, with the insulated jumper as one more edge, routes button-light and the e-paper clock within the budget | feasibility | H TL2-16, TL2-17 | — (decider) | spike P1239 | proposed: both route, each search under 60000 states (`BUDGET`, wire_routing.py:207), set 2026-11-28 | one does not route: a second join router, or a person's jumper | open |
| A6 | First fit's loop serves the perfboard once the free-hole rule (P412) and the tall-module row are breadboard rules | feasibility | E ★C10 (measured with the rule off) | — (decider) | the seam move, the hook's goldens | proposed: 9 of 9 goldens equal and the resistor and the XIAO placed on a single-pad surface, set 2026-11-28 | a golden moves: the rules stay in the loop behind a flag | open |
| A7 | The FIT0193 has a 2.54 mm pitch and single pads, not strips | feasibility | H the seller's label only (★C5) | — (decider) | P1238, the PO's calipers | proposed: pitch 2.54 ± 0.05 mm and each pad its own island, set 2026-11-28 | strips: the surface's groups are rows, close to the breadboard's | open |
| A8 | Claude changes a perfboard plan right from the layout JSON alone, with no picture | usability | H UL-5 | — (decider) | a paper trial: the proposed JSON of button-light and 3 named requests (another board, the smallest goal, a part moved) to a fresh Claude Sonnet | proposed: 3 of 3 requests name the right Operation and arguments, set 2026-11-28 | a wrong one: the JSON or the Operation's help changes | open |
| A9 | After a drag, one sentence for Claude with Copy is enough, and he does not need the drag to apply by itself | usability | E D2 ("for now it can for example ... generate a prompt") | — (decider) | a use log on the first walk after the slice lands (n = 1) | proposed: he finishes one drag through Claude without asking for a direct apply, set 2026-11-28 | he asks for a direct apply: the drag calls `edit-layout --apply` | open |
| A10 | The byte-neutral moves inside the breadboard area cost no MVP card a slot | viability | H MF1, PA-2 | — (decider) | Q2, his word on the order | proposed: no MVP card waits on a refactor slot in the week after his answer to Q2, set 2026-11-28 | an MVP card waits: the moves go after the MVP walk | open |
| A11 | Planning on a perfboard inside `build-board --keep` keeps the build's time | feasibility | H the refuter: first fit scans every hole for each candidate (drawing.py:206-207, :313-325), one refusal took 4.21 s (★C10) | — (decider) | time the walking skeleton on button-light and on the clock, three runs each | proposed: the build of the xiao golden takes at most 10 % longer, set 2026-11-28 | it takes longer: the perfboard plan runs as its own Operation, outside the build | open |

## Collection plan
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Which gadget and board does he solder first? <!-- REQUIRED:collection --> | D-q5, D-q4, D-q6 (A1) | the PO | Q6 in the question dialog | this session |
| What is the first done result? | D-q1 (A2) | the PO | Q3 | this session |
| How is the dev board held? | D-q4 | the PO, or the council by his delegation | Q4 | this session |
| How does he turn a board, and did he solder one? | D-q1, the sheet's mirror (A3) | the PO, an account | Q9 | this session, if the team needs it |
| The FIT0193's pitch, pads and mounting holes | D-q5 (A7) | the PO with calipers | P1238 #1791 | when the perfboard card is pulled (D-f, D8) |
| Does one search with a jumper edge route both gadgets? | D-q3 (A5) | a builder in spike P1239 | a spike with the numbers | after P1350 merges |
| Perfboard Designer's licence and router | D-q3, what the spike reuses | the spike | read its repository | at P1239's start, on Q8's yes |

## Results
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
n/a for energy: no battery, no new regulator and no radio change. The perfboard moves no part's power. Peaks per join, from P1199 EP-1 and EP-2 (calculated from records, rung R2): the largest consumer is the FireBeetle's 3V3 regulator at 1.5 A (stated, marked unverified). At that current, 50 mm of 24 AWG drops 6.2 mV and a one-pitch bridge 0.32 mV. The L9110S at 0.8 A a channel (stated) stays under the guide's 20 AWG line. No dissipation per part changes. A bench reading with the meter on a soldered board (a later rung) can settle the drops.
