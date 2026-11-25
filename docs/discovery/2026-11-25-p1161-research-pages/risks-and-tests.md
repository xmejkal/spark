# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H no evidence that he starts a job from the page more readily than in the chat (A1). Nobody is blocked today (★C15, n = 1) | the next walk's diary, one row per moment (A1) | open |
| usability <!-- REQUIRED:risk-usability --> | E a wait of 3 to 6 minutes per research (USER-15). H the copy, paste and refresh loop (A2) | the same walk: count his steps and note each complaint | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | E the write Operations exist (★C3). H a sentence filled from ids is enough for Claude (A3). E nothing marks a build stale after an edit (★C4, A4) | paste each new sentence into a fresh session 3 times, and unit tests for the stamp | open |
| viability <!-- REQUIRED:risk-viability --> | E no research run is measured in this store (★C9). H the token cost is one he accepts (A6) | `run_cost.py` on the slice 0 walk, with a ceiling he names first | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E an edit can set `verified: true` with any words and pass a check falsely (★C5, A8). E the drawer rule keeps drawer text out of a search (A9) | read every `fact-set` of the walk, and a test on the sentence templates | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | n/a because the epic changes records and pages, no device | — | n/a |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | n/a because the epic changes records and pages, no device | — | n/a |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | n/a because the epic changes records and pages, no device | — | n/a |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | n/a because the epic changes records and pages, no device | — | n/a |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | n/a because the epic changes records and pages, no device | — | n/a |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | n/a because the epic changes records and pages, no device | — | n/a |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | n/a because the epic changes records and pages, no device | — | n/a |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E a wrong pin order reaches the board and the sheet unguarded: the build reads `pin_order` whatever its proof says (council/tech-lead.md PHYS-1). E a board's on-board facts become pin-map constants the firmware imports (PHYS-6) | slice 1 keeps an edit `verified: false` unless a bench result names who, when and how, and the build goes out of date after it (★C4) | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | E a wrong `forward_voltage_v` gives a wrong series resistor (PHYS-4), and a rail current set verified turns needs-measurement into a pass (★C5). E no check reads a supply range or a logic threshold (PHYS-5) | the same guard as the contract row | open |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | He starts a research or an edit from the page's sentence more readily than by typing his own words | value | H none for it: every edit and research in the walks ran in the chat (★C15, n = 1) | — (decider) | the next walk's diary: one row at each moment he wants research or an edit, with what he did | proposed: he copies the page's sentence at 3 or more of the first 5 such moments (set by the decider before the walk), set 2026-11-25 | he types his own words at 3 or more of 5: the page's worth is in what it shows, and the offers stay small | open |
| A2 | Copy, paste, wait 3 to 6 minutes, `/spark:page`, reload is a loop he accepts | usability | E waits of about 3 min, 6 min 18 s and 6 min 20 s, one run each (USER-15) | — (decider) | the same walk: count his steps, note each complaint | proposed: no row where he asks why he must do a step, set 2026-11-25 | 2 or more such rows: a direct channel (Q2 B) moves up | open |
| A3 | A sentence filled only from ids and names in spark's records is enough for Claude to start the right job | feasibility | E three fixed sentences work today (scripts/spark/flow/flow_codes.py:152-154) | — (decider) | paste each new sentence into a fresh session in a scratch project, 3 times each | proposed: 3 of 3 start the right command and ask before any network use, set 2026-11-25 | 2 of 3 or fewer: the sentence names the command too | open |
| A4 | Stamping the records a build read gives no false "out of date" | feasibility | H not tested; the shelf copy is rewritten on a refresh (scripts/spark/sourcing/record_home.py:179-189) | — (decider) | unit tests, then one walk's builds | proposed: 0 false marks across the walk, set 2026-11-25 | any false mark: the stamp reads the record's facts, not its bytes | open |
| A5 | Job a is mostly "what I saw or measured", not a web search | value | E and H 0 of 9 facts of one part need a new web search, by the user lens's reading (★C16, n = 1 part) | — (decider) | sort the 107 unverified facts of the 10 shelf records (PO-8) by who can settle each | proposed: 60 % or more are not for the web, set 2026-11-25 | under 60 %: "check it online" leads the card | open |
| A6 | A research started from the page costs tokens he accepts | viability | E no research run measured in this store; older runs about 0.17 M to about 5.0 M tokens, n = 1 or not stated, 2026-10-03 (★C9) | — (decider) | `run_cost.py` on the slice 0 walk | proposed: the PO names a ceiling before the run, and the run stays under it, set 2026-11-25 | over the ceiling: the sentence names the smaller agent, or research stays rare | open |
| A7 | Two module candidates can be shown before any datasheet is read | feasibility | E only for commodity parts, and that path never ran in a walk (★C11) | — (decider) | the spike of slice 3 | proposed: 2 candidates with maker, part number, fits and lacks, for 2 of 3 real needs, set 2026-11-25 | fewer: find by criteria stays a chat request with no page moment | open |
| A8 | No path of this epic lets an unproven fact become `verified: true` | ethics | E the guard holds only as far as the writer is honest (★C5) | — (decider) | read every `fact-set` of the walk | proposed: every `verified: true` has a source that names who, when and how, set 2026-11-25 | any one without: spark forms the source sentence (Q6 B) before more edits | open |
| A9 | No drawer text beyond a chosen part's name, and no photo, leaves the machine through this epic | ethics | E the rule exists (commands/drawer.md:93-94) | — (decider) | a test on the sentence templates | proposed: the test passes, and Q4's small question is answered, set 2026-11-25 | a fail: the template is fixed before it ships | open |
| A10 | The hobbyist the vision names has these four jobs too | value | H none: nobody beyond the PO was reached | — (decider) | none available now | not set, 2026-11-25: no test is available | — | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Does he start a job from the page's sentence (A1)? <!-- REQUIRED:collection --> | the first slice's worth, and whether a direct channel moves up | the PO, at the next walk | a diary row at each moment, with the time from `date` | the next walk after slice 0's sentences exist, or before any build with the canvas's sentences |
| What does a module research cost in tokens (A6)? | the cost line's words (Q11) | spark-main, from the slice 0 walk | `run_cost.py` on that run's transcript | the slice 0 walk |
| Who can settle each unverified fact on the shelf (A5)? | which control leads job a (Q6) | a lens agent, no network | sort the 107 unverified facts of the 10 shelf records by their notes | before slice 1's plan |
| What does a find by criteria return for a module (A7)? | whether slice 3 is built | a spike session, its token cost named first | one real need run two ways | after slice 0 |
| Can a Claude Artifact page take a photo upload, and where does it keep it? | the photo screen (Q2) | spark-main or a design session | `describe_capabilities` of the Artifact server | before any design of slice 2's screen |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a because the epic changes records and pages, with no battery, motor, radio or regulator. The physical side is in the contract and supply rows above.
<!-- EXTEND:risks-sections -->
