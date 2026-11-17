# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H: nobody is blocked (★C16 (rework, not a stop)); the need is the PO's wish and three walks' rows (n = 1) | Q2 to Q8 with the PO; the walks run again on the first slice | open |
| usability <!-- REQUIRED:risk-usability --> | E ★C10 (a tick for skipped stages), ★C1 (one project); E two sentences read wrong in walk 3 (rows 5, 6) and one in walk 2 (row 6) | the PO reads slice 0's output on the sound demo before more is built | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | H A1: one rule over recorded inputs for every phase; E ★C3 (four mechanisms today) | the paper spike of the brief's Riskiest section | open |
| viability <!-- REQUIRED:risk-viability --> | H A6: more phases must not slow a basic project (AGENTS.md's one bar); E ★C16 (rework, not a stop) | the button-and-LED walk again after slice 0, by the clock | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E ★C6 (not measured): a 3.3 V output on a new part's signal pin when a person wires before flashing; E walk rows on a look that restarts another project's board (P865 #1231) | Q11's order line; a meter check named on the sheet | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | E C28: the 3V3 budget of the sound project has unknown values before any change (council/physics.md:17); found on the way | R1 once the values are measured (R6) | n/a because this item defines spark's journey and ships no hardware; the gap is a found-on-the-way row |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | — | — | n/a because no motor is in the item or in the walk projects |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | — | — | n/a because this item defines spark's journey and ships no hardware |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | — | — | n/a because this item defines spark's journey and ships no hardware |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | E C22: the joystick's top range clips at 2900 mV, datasheet-typ as the lens read it | R0: re-read the datasheet page; R6 on the stick | open, found on the way |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | — | — | n/a because this item defines spark's journey and ships no hardware |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | — | — | n/a because this item defines spark's journey and ships no hardware |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E ★C4: 2 of 15 kept signals move, simulated, one project; E ★C6 (not measured); E C25: a switch lands on the board's own button | R0 and R1: the assigner run on more designs; R6 for what the old image does on the new wiring | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | E C23, C24: a record names another chip; the display's DC pin differs between the cable and the pin map | R0: a review of the two records | open, found on the way |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | One rule over recorded inputs gives the state of every phase that matters, also of the firmware and of the bench | feasibility | H council/architecture.md:138 (AR-13); E ★C3 (read by the lens) | — (decider) | the paper spike on the three P711 walk folders | at least 5 of the 7 things of #1234's comment named from files and records alone, proposed 2026-11-17 | fewer than 5: the graph does not carry the journey, and the line or the table is the shape | open |
| A2 | The PO's phase order is what a person needs | value | D-h: his guess, asked as a question; n = 1, and he is the decider | — (decider) | Q6 and Q9; then a walk on the result | not set yet, noted 2026-11-17; Q1 sets it | he reads the proposed table and reorders it | open |
| A3 | A person wants the pins of the parts that stay kept, also at the cost of a worse placement | value | H council/feasibility.md:81 (Q-F2); E ★C4 (simulated; one project) | — (decider) | Q3 | not set yet, noted 2026-11-17; Q1 sets it | "fresh each time": slice 1's first row falls away | open |
| A4 | The bench can be shown as witnesses without being read as the bench's real state | usability | E p711-walk4-button-led/rows.md row 6: "last deploy here" was read as the box's state | — (decider) | the PO reads slice 2's sentences on his game box's project | not set yet, noted 2026-11-17; Q1 sets it | he reads "recorded" as "is" | open |
| A5 | One definition serves the CLI, the agents, the page and a later framework | feasibility | H; no framework exists (council/user.md:85, US-52 as the lens names it); E ★C13 (a contract) | — (decider) | none cheap before a framework is chosen (P417) | not set yet, noted 2026-11-17; Q1 sets it | a framework needs a stored state | open |
| A6 | More phases and more "out of date" marks do not slow a basic project | viability | H AGENTS.md's one bar; E ★C16 (rework, not a stop) | — (decider) | the button-and-LED walk again, by the clock | not set yet, noted 2026-11-17; Q1 sets it | the basic walk takes longer than before | open |
| A7 | A person wants a plan before a change is applied | usability | H council/ux.md:66 (UX-24, Terraform's plan) | — (decider) | Q7 | not set yet, noted 2026-11-17; Q1 sets it | "change first" | open |
| A8 | P827 and P828 survive the redefinition when the rail renders the phases it is given | feasibility | H ★C15 (the lens's reading) | — (decider) | a read of P827's plan against the phase table before it is built | not set yet, noted 2026-11-17; Q1 sets it | the plan hard-codes nine panels | open |
| A9 | A person follows an order line at the bench | ethics | H ★C6 (not measured); council/physics.md:25 (PH-12) | — (decider) | Q11; then the next walk's rows | not set yet, noted 2026-11-17; Q1 sets it | the walk shows the line skipped | open |
| A10 | The shops have data to show | feasibility | E ★C12: 1 of the 8 library parts has a vendor and a product code, counted by the lens | — (decider) | a count over the store's catalog records | not set yet, noted 2026-11-17; Q1 sets it | most records name a shop | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Does one "made from" table explain the seven things the walks saw? <!-- REQUIRED:collection --> | Q5, A1 | the facilitator, from the three walk folders | the paper spike | after Q1 sets its pass line |
| Do kept pins move on other designs and boards? | Q3, A3 | the facilitator | the assigner on scratch copies of the other walk projects | with the spike |
| What damage does the wire-before-flash state do? | Q11, A9 | nobody from files; the vendor's absolute maximum ratings, or a bench measurement | R0: the datasheet's ratings page | when Q11 is asked |
| How many store catalog records name a shop? | Q9, A10 | the facilitator | one count over the store's records | before Q9 |
| Which page did the PO praise? | Q10 | the PO | Q10 | in the queue |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a for the item itself: it defines a journey and adds no battery, motor, radio or regulator. One number from the walk projects bears on it: the sound project's 3V3 budget is incomplete (C28: the amplifier names no current fact and the display's peak is null; a null is an unknown), and the physics lens's hand sum of about 0.6 A against a 1.5 A regulator figure is calculated from unverified values (council/physics.md:17). The rung that settles it is electronics-firmware:R6, a bench measurement.
<!-- EXTEND:risks-sections -->
