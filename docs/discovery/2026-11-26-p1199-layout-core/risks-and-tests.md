# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | E ★C10, ★C11, ★C12: no move was seen in 23 project folders, the bench board has no edit path, and nobody is blocked (A1, A8) | the account question Q1, then the 14-day use log | open |
| usability <!-- REQUIRED:risk-usability --> | H council/user.md US-5, US-8, council/tech-lead.md TL-15: Claude needs hole names and a reason before the write. A rebuild can move parts that no edit holds (A5, A6) | one walk on a scratch project with `edit-layout --dry-run`, and Q5 | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | E ★C5, ★C6, ★C7, council/synthesis.md part 2 (two scratch checks): whole holes keep the goldens in a partial run. No whole-hole planner and no pad-lattice router exist (A2, A3, A4, A9) | the skeleton's PR runs the 9 goldens. Spike B for the perfboard router. Spike C for the FIT0193 | open |
| viability <!-- REQUIRED:risk-viability --> | E #1688 in Idea, P1193's A2 spike not run (A7). The edits survive a rebuild without P1152, but have no way back until it lands | P1155's result | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E drawing_match.py checks jumpers only. A perfboard's routes are joins that the check must read (★C4, A10) | a planted short in a perfboard fixture | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | n/a because the layout changes where parts sit, not what they draw | — | n/a |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | E ★C16 (council/tech-lead.md EP-1, EP-2): 30 mA to about 1.5 A in spark's records. Each join loses under 7 mV over 50 mm (calculated on handbook constants, H) | R1 once a net's current is derived from its largest consumer. A source for wire ampacity before any net above 2 A | open |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | E EP-2: 9.2 mW in a 50 mm bare wire at 1.5 A (calculated) | When a net above 1.5 A appears, R1 with the same formula | open, low |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | n/a because the layout core adds no fast switching and no touched surface. A long wire beside a motor is a later perfboard check | — | n/a |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | n/a because the layout changes no sensor's reading | — | n/a |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | n/a because the layout does not change the rails' peaks | — | n/a |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | n/a because the layout does not change any pin | — | n/a |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | D-d: the perfboard keeps the pins the firmware was tested on (#311 note 1). E kept_moves.py:13-17: a kept jumper never changes what is connected | the same-pins check over the joins (A10) | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | E ★C14, ★C15: the FIT0193 record has no pitch or hole counts. The button and the resistor have no lead pattern. The JST PH has a 2.0 mm pitch | R0: the seller's page or the button's datasheet. Spike C, calipers | open |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | The PO or Claude will place a part or a wire by hand, or want a goal, often enough to pay for the refactor of code that 181 tests pin | value | E against it: ★C10, ★C11 | — (decider) | Q1, then a 14-day use log: one line in the store's bench file each time he or Claude wants a part or a wire elsewhere on a drawn breadboard | proposed: at least 3 wishes across at least 2 projects in 14 days, to be dated by the PO before any result | fewer than that: the skeleton waits until the perfboard card is pulled | open |
| A2 | A planner on whole holes keeps every golden byte | feasibility | E council/synthesis.md part 2 (rank ties: 9 of 9), ★C6 (TL-1). No end-to-end run | — (decider) | the skeleton's PR runs tests.test_golden_breadboard | proposed: 9 of 9 the same | any golden changes and the diff is not read and accepted | open |
| A3 | One A* pass on the pad lattice with an insulated-jumper fallback joins every net of button-light and one motor circuit, with few jumpers | feasibility | H TL-7. E ★C7 timed a stand-in rule set | — (decider) | spike B | proposed: every net joined or named, the jumper count written down, set before the run | a net neither joined nor named | open |
| A4 | The FIT0193 is a 2.54 mm board of single pads, about 39 or 40 by 29 or 30 holes | feasibility | E ★C15: the record holds none of it | — (decider) | spike C: calipers, or the seller's page | — | another pitch, or strips | open |
| A5 | Claude finds `edit-layout`, uses hole names and reads the refusal before it writes | usability | H TL-15, US-5 | — (decider) | one walk on a scratch project | proposed: one dry run, one write, 0 edits of breadboard.json by hand | Claude edits breadboard.json by hand | open |
| A6 | A person who has wired the board accepts that a rebuild can move parts that no edit holds | usability | E against it: today every earlier part stays (kept_moves.py:175-184). H US-8 | — (decider) | Q5 | — | he wants every part to stay | open |
| A7 | P1152's kept step and take-back land, so an edit has a way back | viability | E #1688 in Idea. P1193's A2 spike has not run | — (decider) | P1155's result | — | the timeline does not land | open |
| A8 | The greedy `spread` plan is easier to solder than `smallest` | value | H US-6 | — (decider) | show the PO both plans of one circuit | — | he picks smallest | open |
| A9 | Every part has a footprint on the pitch, or is refused with a useful code | feasibility | E ★C14 | — (decider) | read the button's datasheet. Decide the resistor's span | — | a part that can neither be placed nor refused clearly | open |
| A10 | A join plan never joins two nets, and each join carries its net's current | ethics | E drawing_match.py for jumpers. EP-2 calculated on H constants | — (decider) | a planted short in a perfboard fixture, and a source for ampacity before any net above 2 A | proposed: the planted short is named, every time | a short is not named | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| When did the PO last want a part or a wire elsewhere on a drawn breadboard? <!-- REQUIRED:collection --> | D-q8, A1 | the PO | Q1, through spark-main | in the first question round |
| How often does he or Claude want a move? | A1 | the PO, with Claude | the 14-day log in the store's bench file | after Q7 sets the pass line |
| What are the FIT0193's pitch, pad and hole counts? | D-q7, A4 | the PO with calipers, or the seller's page | spike C | when the perfboard card is pulled (Q8) |
| Does a pad-lattice router join every net? | D-q3, A3 | a builder | spike B | after the MVP |
| Does a whole-hole planner keep the goldens end to end? | D-q1, A2 | a builder | the skeleton's PR | after the MVP |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a: the layout core adds no battery, motor, radio or regulator. The one number it adds is the loss in a join, under 7 mV and 9.2 mW over 50 mm at 1.5 A (calculated, council/tech-lead.md EP-2, settled by electronics-firmware:R1).
<!-- EXTEND:risks-sections -->
