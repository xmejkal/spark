# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H ★C10: the PO is not blocked. His want is D (#224). Whether he uses a spark command instead of `mpremote` is untested (A2, A8) | the account questions Q14 and Q20, then a use log of slice 0 at the bench | open |
| usability <!-- REQUIRED:risk-usability --> | E ★C6, ★C13: opening the port and the look can restart the board or leave it in download mode | the reach rung (A1) and 20 port opens with the ROM line kept (A6) | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | E ★C2, ★C3, ★C4, ★C5: reach is not reliable, each try restarts the interpreter, and the gate is written for an erase | the reach rung on P246's project (A1, A10), then the gate change at design | open |
| viability <!-- REQUIRED:risk-viability --> | E ★C14: nothing to install, mpremote is MIT, personal use | none needed | n/a because the slices use free tools already on the Mac and spark is MIT |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E ★C7: free `exec` can drive the USB pins and drop the port, or the flash pins. H PHY-2: two shorted outputs give about 97 mA, calculated | Q8 (a deny list), and the bench rung for A5 on the on-board LED | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | E the bench boards run on USB power, no battery (frame) | none needed | n/a because no battery and no sleep in the USB slices |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | H PHY-8: a driver input left high keeps a motor on while no code runs. No motor on the bench | read again when a project with a motor (the RC cars) uses a live session | n/a because the bench has no motor |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | — no load on the bare board | none needed | n/a because the bare board drives only its LED |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | H the facilitator's reading: the port drops in the logs follow resets (★C6), and no log shows an EMC symptom | none needed | n/a because no motor or radio runs in the USB slices |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | — no sensor on the bench | none needed | n/a because no sensor is read in slice 0 |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | — the Seeed regulator rating and the USB current limit were not read (tech-lead.md, could not check) | read the XIAO C6 schematic when a breadboard load joins a live session | n/a because the bare board draws no load |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | — live sessions keep the board awake | none needed | n/a because no sleep mode is in scope |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E ★C7: the record lacks USB, JTAG and flash roles, and pins.py holds no direction (P218 ★C16) | Q8, then a refused read of GPIO12 in slice 3 | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | E ESP-IDF GPIO page and the C6 datasheet, read 2026-10-15. H the MicroPython reset page (search summary only) and the Seeed schematic (not read) | open the MicroPython reset page and the Seeed schematic at design | open |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | mpremote reaches a running C6 outside a deploy reliably enough that a live try works the first time | feasibility | E ★C3, ★C2 (the post-flash causes are known and acted on) | — (decider) | the reach rung: `exec "print(1)"` 10 times on the running firmware at least one minute after a passed deploy, and 10 after re-plugs, on P246's project | the PO sets it at Q1. Proposed: 19 of 20 answers, the facilitator's opinion, set 2026-10-15 | below the pass line: fix reach (P238 #235) before any live command | open |
| A2 | the PO uses a spark live command instead of typing `mpremote` himself | value | H POA-28 | — (decider) | Q14, then a use log of slice 0 over his next 5 bench sessions | proposed by the facilitator: he uses it in 3 of his next 5 bench sessions (a session is one day at the bench with the board plugged in), set 2026-10-15 | he types `mpremote` himself in most sessions | open |
| A3 | a restart per try is acceptable to the PO | usability | H ★C4 | — (decider) | Q9 and Q15 | — (a decision, not a count), set 2026-10-15 | he needs state kept between tries | open |
| A4 | the firmware the conversation writes can always read its console without harm to its timing | feasibility | E ★C2 (two firmwares). The rule already stands in agents.md:577-578, so this is a check on new firmware | — (decider) | P246's project and button-light pass the reach rung | proposed: both reach in the rung, set 2026-10-15 | a firmware that cannot read its console | open |
| A5 | a soft reset leaves a driven pin as it was | feasibility | H ★C7 (PHY-4) | — (decider) | on the bare board: `Pin(15, Pin.OUT).value(1)` through exec, soft reset, look at the LED | — (an observation: lit or not), set 2026-10-15 | the pin is released: a soft reset is enough to end a try | open |
| A6 | opening the port restarts the C6 often enough to matter for a monitor | usability | E ★C6 (the logs disagree) | — (decider) | 20 opens with pyserial, DTR and RTS logged, the ROM line `rst:` kept | proposed by the facilitator: a restart in 2 or more of 20 bare opens (DTR and RTS off, the firmware running, no esptool run before) means the monitor must say it, set 2026-10-15 | 0 of 20: the monitor can promise no restart | open |
| A7 | a grant kept in the store for a live session is safe enough | ethics | H ★C5 | — (decider) | Q6, then a design review | — (a decision), set 2026-10-15 | the PO wants a yes per try | open |
| A8 | live tries by the agent add trust beyond the simulation | value | H #204 ("connection with agents") | — (decider) | Q20 after slice 0 | — (an account), set 2026-10-15 | he does not read the agent's tries | open |
| A9 | the PO wants pin reads before he has wires | value | E ★C11 | — (decider) | Q22 | — (an account), set 2026-10-15 | he wants them only with wires: slice 3 waits | open |
| A10 | `mpremote resume` keeps values between two calls | feasibility | H ★C4 (TL-2) | — (decider) | on the bare board: `exec "x=5"`, then `resume exec "print(x)"` | — (an observation: 5 or an error), set 2026-10-15 | it does not: tries cannot build on each other | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Q14 to Q24, the account questions <!-- REQUIRED:collection --> | Q2, Q6, Q9, Q10 | the PO | AskUserQuestion, one at a time, past tense | this discovery, after Q1 |
| A1, A5, A6, A10, the reach rung | Q2, Q3, Q5, Q9 | the PO's hands (presses, re-plugs) and Claude's runs | one bench session on P246's board-only project (P222 narrowed) | after Q3, once P246's project exists |
| Q2 to Q13, the decisions | the first slice and its design | the PO | AskUserQuestion | this discovery, after Q1 |
| the MicroPython reset page and the Seeed XIAO C6 schematic | Q5, Q8 | Claude | open both at their sources | at design |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a: no battery, motor or regulator is in the USB slices, and the bare board runs on USB power. The one number here is
the harm of a wrong pin: two shorted outputs give about 97 mA, and an LED with no resistor about 79 mA (calculated from
datasheet-typ points IOH 40 mA at 2.64 V and IOL 28 mA at 0.495 V, a linear model that overstates the current,
https://documentation.espressif.com/esp32-c6_datasheet_en.html page 65, read 2026-10-15, PHY-2). The rung that would
settle it: a meter in series with a 330 ohm resistor on the pin (measured). It cannot show lifetime damage.
<!-- EXTEND:risks-sections -->
