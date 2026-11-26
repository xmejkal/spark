# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H, no test yet (A1, A2); E ★C3 shows repeats for n = 1 | the prototype walk of A1; the count of A2 rerun at the decision | open |
| usability <!-- REQUIRED:risk-usability --> | H (A3, A8); E ★C7 five names for one layer | the same walk: he says what each word means | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | H (A4, A5) on E ★C1 ★C11 | a test in the plan that adds a fourth layer with no caller change | open |
| viability <!-- REQUIRED:risk-viability --> | E ★C2 nobody blocked; H A7 the order with P1193 | Q11 to the PO | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E ★C5 ★C13: a project can redirect a role; a grant is a standing yes | A6's refusal test; Q10 | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | n/a because this item holds no hardware | — | n/a |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | n/a because this item holds no hardware | — | n/a |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | n/a because this item holds no hardware | — | n/a |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | n/a because this item holds no hardware | — | n/a |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | n/a because this item holds no hardware | — | n/a |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | n/a because this item holds no hardware | — | n/a |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | n/a because this item holds no hardware | — | n/a |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E physics-1 to 4: grants, the direct-flashing switch, P410's check and the image build fields decide what reaches a board | keep grants and the switch out of the seam; P410's setting never stands in for the typed yes (Q10) | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | n/a because this item holds no hardware | — | n/a |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | A person looks on a page for why spark did something and whose word a value is, rather than asking Claude | value | H PO-17 | — (decider) | a prototype walk of the Settings artboard, 3 tasks | 3 of 3 found without help, set 2026-11-26 | 1 or fewer found: the page waits, and show-settings in the chat comes first | open |
| A2 | A personal default saves repeated choices | value | E ★C3 (3 of 24 briefs) | — (decider) | rerun the count at the decision | 3 or more projects repeat a personal choice, set 2026-11-26 | fewer than 3: the person's layer waits | open |
| A3 | The words "spark's default", "yours", "this project" and "your account" are understood without "global" | usability | H USER-10, ★C7 | — (decider) | in the walk, he says what each word means | 4 of 4 right, set 2026-11-26 | a word misread: rename before the plan | open |
| A4 | A new small class beside the tools list, one Storage per layer, holds every candidate setting with no change to the tools list's callers | feasibility | H TL-3, TL-6 | — (decider) | the plan's spike reads storage.py's fit | 0 callers of tool_finder change in slice 0, set 2026-11-26 | a caller must change: Q6 again | open |
| A5 | An account layer can be added later as one list item, with no caller change | feasibility | H TL-21 | — (decider) | a test in slice 0 adds a fake fourth layer | the test passes with 0 caller edits, set 2026-11-26 | callers name a layer: the seam's shape changes | open |
| A6 | Allowed layers per setting stop a cloned project from widening sharing or spending | ethics | E ★C5 ★C12 | — (decider) | a scratch project sets a share setting | refused, with a sentence naming the file, set 2026-11-26 | accepted: the trust rule is wrong | open |
| A7 | The seam is worth building after the MVP and before P1193's roles land in the tools list | viability | H TL-18, E ★C2 | — (decider) | Q11 to the PO | he chooses (a) or (b) of Q11, set 2026-11-26 | P1151 goes first: the two roles move twice | open |
| A8 | Asking once at the first need, with "use spark's default" kept, does not nag | usability | H USER-14, ★C6 | — (decider) | the walk of the author question | he answers once and is not asked again in 3 runs, set 2026-11-26 | asked again: the ask is wrong | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Does the page earn its place (A1, A3)? <!-- REQUIRED:collection --> | Q1, Q8 | the PO | a prototype walk of the Settings artboard, 3 tasks | at his next design sitting |
| Does a choice repeat across projects (A2)? | Q7 | the facilitator | rerun the count of ★C3 | at the decision |
| Has he used a second computer (Q12)? | Q9 | the PO | one account question | with Q1 |
| Where did he look for why spark did something (Q13)? | Q8 | the PO | one account question | with Q1 |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a — no battery, motor, radio or regulator
<!-- EXTEND:risks-sections -->
