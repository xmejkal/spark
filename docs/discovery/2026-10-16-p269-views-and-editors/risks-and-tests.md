# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H ★C6, A3, A4 | Q10's account questions, then S1 shown to the PO | open |
| usability <!-- REQUIRED:risk-usability --> | H council/user.md, A3, A6 | S1 and S3 in front of the PO, one net highlighted in two views | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | H ★C1 ★C5, A1, A2, A5, A7, A9 | the A1 spike, then S0 with `breadboard.json` byte-equal | open |
| viability <!-- REQUIRED:risk-viability --> | H ★C7 C8, A8, A10, A11 | read the upstream licence files; one Artifact publish of S3 | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E ★C7 | keep share-alike and vendor pictures only in the person's store, with credit | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | n/a because this item draws and edits a circuit; it changes no power design | — | n/a |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | E C10: sources disagree on a strip's current, and records hold 5 current fields | a current field on records with a motor or a load, before any strip check | open |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | E C10 | as above: no heat check on a perfboard until the currents are recorded | open |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | n/a because the views draw what the build already chose | — | n/a |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | n/a because no sensor reading changes | — | n/a |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | n/a because no supply changes | — | n/a |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | n/a because no firmware changes | — | n/a |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E ★C4: two ways to find the circuit's points could draw a wire the firmware does not expect | S2: one circuit source and a check | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | E ★C2 C9: no pin positions in mm, and two sizes for the XIAO | Q-D1 and Q-D10 in council/data.md | open |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | A person's edit to a layout survives the next build, or is reported by name | feasibility | H ★C5 | — (decider) | the spike in brief.md | 3 of 3 cases survive or are reported, set 2026-10-16 | an edit lost silently in any case | open |
| A2 | One model of holes, join groups, placements and connections fits breadboard, stripboard, perfboard and PCB | feasibility | H ★C1 | — (decider) | S0, and a stripboard surface sketched on paper against it | breadboard.json byte-equal and a strip cut expressed without a new class, set 2026-10-16 | a stage that needs its own model | open |
| A3 | A picture in the sheet helps the PO wire more than the numbered steps alone | value | H council/user.md USER-25 | — (decider) | S1 shown to the PO, and Q10's Q-b | he says he wired from the picture, set 2026-10-16 | he keeps to the steps | open |
| A4 | The PO will solder a perfboard or stripboard from spark's layout | value | H ★C6 | — (decider) | Q10's Q-d and Q-e | he names a board in his drawer and a project for it, set 2026-10-16 | no perfboard project in sight | open |
| A5 | Pin positions in mm can be filled for the parts he owns from the KiCad footprints and datasheets | feasibility | H ★C2 | — (decider) | fill one module and the XIAO by hand | both in under an hour each, set 2026-10-16 | a part with no source for its pins | open |
| A6 | tscircuit's circuit-to-svg is good enough for the schematic and PCB tabs | usability | H ★C3 | — (decider) | render button-light's schematic and PCB once | readable to the PO, set 2026-10-16 | he finds it unreadable | open |
| A7 | One bundled TS file runs as a local page and as an Artifact | feasibility | H C8 | — (decider) | publish a one-file viewer as an Artifact | it opens and reads a layout, set 2026-10-16 | the Artifact refuses it | open |
| A8 | Pictures from the web can be kept in the person's store with their credit, legally, for personal use | viability | H ★C7 | — (decider) | read the upstream licence files of Fritzing, wokwi-boards and one vendor | each allows a personal copy with credit, set 2026-10-16 | a source forbids it | open |
| A9 | A grid planner routes button-light on plain perfboard well enough to edit | feasibility | H TL-35 | — (decider) | a Lee-routing spike on the button-light netlist | all points routed with no crossing on one side, set 2026-10-16 | it needs a person for a basic circuit | open |
| A10 | Each slice fits a few days of work and keeps the build green | viability | H TL-35 | — (decider) | S0's size after it merges | under 400 lines of code changed, set 2026-10-16 | S0 grows past that | open |
| A11 | Sharing can wait for the store epic P178 | viability | H council/data.md | — (decider) | Q8 and Q9 | the PO agrees, set 2026-10-16 | he wants sharing in the first slices | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| How important is each assumption? <!-- REQUIRED:collection --> | Q1 | the PO | AskUserQuestion | now |
| His own use: Q-a to Q-j | Q10, A3, A4 | the PO | AskUserQuestion, a few at a time | after Q1 |
| Do edits survive a rebuild? | A1 | the lead | the spike | after the PO's yes to it |
| Upstream licences | A8 | the lead | read the licence files | before S1 |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a because this item draws and edits; it adds no battery, motor, radio or regulator. A stripboard current check waits for current fields on records (C10).
<!-- EXTEND:risks-sections -->
