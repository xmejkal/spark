# Risks and tests

## Risks
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | E ★C16: at least 3 paid runs in the walks, none after 2026-11-01, and friction explains it as well as low value. H the PO's words on P1190 want the step (A1) | Q9 to the PO, and a forward use log on the next walk | open |
| usability <!-- REQUIRED:risk-usability --> | E council/user.md USER-5: the page's "No simulation" line and the build's "Could not run" read as a failure. H A8 | a walk on the clock after item 3, with the PO's diary line | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | E ★C5, ★C15, council/tech-lead.md TL-4: the seam's selection sites are known. H A2, A4, A7 | the seam card's plan reads each site. Two free spikes (items 5 and 12) | open |
| viability <!-- REQUIRED:risk-viability --> | E ★C10: 50 simulated minutes per rolling 30 days on the free plan. A paid run is the PO's yes each time (D-a) | P413's count over one month (A6) | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E council/po-assistant.md PO-23, PO-24: a model the conversation wrote can pass firmware that fails on the real part | the result names "a model the conversation wrote" (A5) | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | n/a because the item changes how firmware is tested, not a circuit. No rung before the bench shows power (council/tech-lead.md PHYS) | — | n/a because no circuit changes |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | n/a because no motor or driver is in scope | — | n/a because no motor is in scope |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | n/a because no part's heat is in scope | — | n/a because no part's heat is in scope |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | n/a because a simulation has no noise or discharge | — | n/a because no simulator models it |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | E ★C8: a slider sets an ideal value. A real sensor drifts. The result must not claim the real value | the result line names "the real value was not shown" | open |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | E council/tech-lead.md PHYS: no rung before the bench shows a brown-out | the result's limits name it | open |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | E ★C21: Wokwi does not wake the C6 from a GPIO. The clock deep-sleeps (council/po-assistant.md PO-19) | the limits name it, and the bench tests it | open |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E ★C11: a stand-in board tests the chip's GPIO numbers. GPIO14 is missing on the C6 stand-in (P999) | P999's check that names a pin the stand-in lacks | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | E ★C20, research-wokwi.md §6: community chips carry mixed licences, and wokwi-boards reports none | item 12's licence rule | open |

## Assumptions
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | The free checks, once on the page, get run before the first deploy and catch a fault that otherwise costs a bench round | value | H the architect. E against the wider belief: ★C16 | high D17 | Q9, and a forward use log on the next walk | use: the free checks run before the first deploy of the next walk. Yield: over 3 walks, at least 1 fault with a firmware fix found before the first deploy. Proposed 2026-11-26 by the delegated council (the replay test is dropped, council/refuter.md part 3) | no run before the deploy, or no fault in 3 walks while the bench finds one of a kind the checks claim: only the honest words ship | open |
| A2 | A logic-level run of the person's own `main.py` on the stand-in works with no edit to firmware/ | feasibility | E ★C19: no irq, fixed bus values. H the tech lead (L) | low D17 | item 14's spike on the clock | the loop runs 10 simulated seconds with no edit, proposed 2026-11-26 | it needs an edit per firmware | open |
| A3 | A stand-in board by chip (Wokwi's ESP32-C6 DevKitC-1) covers the clock's GPIO and serial | feasibility | E ★C11, P999 #1455. E against it: the clock uses GPIO14, which the stand-in lacks (★C25) | low D17 | P999's build | the clock builds with a stand-in and names GPIO14, proposed 2026-11-26 | the stand-in lacks a pin the clock uses | open |
| A4 | One record field carries the controls for every strategy | feasibility | H council/tech-lead.md TL-9, the architect's decision 8 | low D17 | item 10's plan | one reader serves the chip's JSON and a built-in part, proposed 2026-11-26 | two sources of one control | open |
| A5 | A result that says "a model the conversation wrote" keeps the person's trust after a false pass | ethics | H the PO assistant's pre-mortem 3 | low D17 | an account question after the first such pass | the PO says he still trusts a pass that names the model, proposed 2026-11-26 | the person stops trusting "passed" | open |
| A6 | The free Wokwi plan's 50 minutes per 30 days is enough for the PO's projects with the free checks first | viability | E ★C10, ★C16 | low D17 | P413's count over one month | under 50 simulated minutes in 30 days, proposed 2026-11-26 | the minutes run out in a month | open |
| A7 | A community chip loads in wokwi-cli by reference with no file copied | feasibility | E ★C20 for Wokwi's own board. Not tried in wokwi-cli | low D17 | item 12's free spike | one free run with a referenced chip, proposed 2026-11-26 | it needs the source copied | open |
| A8 | "Skipped, with the reason" in grey reads as no failure to the person | usability | E council/user.md USER-5 against today's words | high D17 | the PO's diary line on the clock after item 3 | no diary line calls the grey state a failure, proposed 2026-11-26 | he reads grey as broken | open |
| A9 | The seam with one Adapter is worth one card before a second simulator exists | viability | E the P1089 council chose the same for the engine (council-answers.md:19). D-g | low D17 | none, a judgement | the PO or the council says yes to the seam card, proposed 2026-11-26 | the PO says wait for a second strategy | open |
| A10 | A free local emulator (esp-emulator or esp32sim) boots spark's own MicroPython C6 image unedited, and a host can drive it | feasibility | H the store's preanalysis/2026-11-26-own-simulator.md. Neither page shows a MicroPython C6 image that boots | high D17 | item 19's steps 1 and 2, free | the image spark built for a C6 walk project prints `ready` within 120 s of wall clock, and one press sent by the host changes a pin the host reads back, proposed 2026-11-26 | a miss: ways 1 and 2 leave the epic's first slice, and A2 goes high | open |
| A11 | A person marks some versions important, and a paid run follows | value | E against it: ★C16 (a floor). H D13 | low D17 | a use log over the next 3 walks, one offer at each deploy | at least 1 version marked and followed by a paid run, and at least 1 left unmarked, proposed 2026-11-26. A deploy with the PO away gives no information | no mark: item 16 ships `ask`, `never` and the threshold, and the mark waits | open |
| A12 | Spark can count the simulated minutes a run used | feasibility | E against it: a run log names the cap, not the time used (the walk project p581-sound-joystick's `sim/runs/the-button-changes-the-effect.log`, line 1) | low D17 | read wokwi-cli's output and docs (P413's first step), free | one source names the simulated time of one run, proposed 2026-11-26 | a miss: the count is an upper bound, said as "at most" | open |

## Collection plan
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Why were the three built simulations never run? <!-- REQUIRED:collection --> | Q2, A1 | the PO | Q9, relayed by spark-main | at his next message |
| Do the free checks, offered before the first deploy, run and find a fault? | A1 | the session on the next walk | a use log, no paid run | the next walk after items 2 and 3 |
| Do `wokwi-cli lint` and `chip compile` run with no token? | the free checks' scope | a free spike (item 5) | run with the token unset | beside items 2 and 3 |
| Does a community chip load by reference in wokwi-cli? | Q7, A7 | a free spike (item 12) | one run on the free plan, after the PO's yes for its minutes | slice 3 |
| How many minutes does a month of the PO's use spend? | A6 | P413 #539 | the count per run | after P413 |

## Results
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
n/a — no battery, motor, radio or regulator. This item changes how firmware is tested before the bench, and no circuit.
<!-- EXTEND:risks-sections -->
