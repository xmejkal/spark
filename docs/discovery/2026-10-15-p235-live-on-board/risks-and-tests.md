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
| A1 <!-- REQUIRED:assumptions --> | mpremote reaches a running C6 outside a deploy reliably enough that a live try works the first time | feasibility | E docs/observations/2026-10-15-p235-reach-test.md: 10 of 10 after a reset, 7 of 10 after a replug | high D4 | the reach rung: `exec "print(1)"` 10 times on the running firmware after `mpremote reset`, and 10 after replugs, on button-light (P246's project did not exist yet) | 19 of 20 answers, set 2026-10-15 before the run (D4, the facilitator's line, the PO chose to test it) | below the pass line: fix reach before any live command | retired 2026-10-15: missed, 17 of 20 (Results). The cause is AT187, the cure is P251 (D6), and A11 carries what is left |
| A2 | the PO uses a spark live command instead of typing `mpremote` himself | value | H POA-28 | — (decider) | Q14, then a use log of slice 0 over his next 5 bench sessions | proposed by the facilitator: he uses it in 3 of his next 5 bench sessions (a session is one day at the bench with the board plugged in), set 2026-10-15 | he types `mpremote` himself in most sessions | open |
| A3 | a restart per try is acceptable to the PO | usability | H ★C4 | — (decider) | Q9 and Q15 | — (a decision, not a count), set 2026-10-15 | he needs state kept between tries | open |
| A4 | the firmware the conversation writes can always read its console without harm to its timing | feasibility | E ★C2 (two firmwares). The rule already stands in agents.md:577-578, so this is a check on new firmware | — (decider) | P246's project and button-light pass the reach rung | proposed: both reach in the rung, set 2026-10-15 | a firmware that cannot read its console | open |
| A5 | a soft reset leaves a driven pin as it was | feasibility | H ★C7 (PHY-4) | — (decider) | on the bare board: `Pin(15, Pin.OUT).value(1)` through exec, soft reset, look at the LED | — (an observation: lit or not), set 2026-10-15 | the pin is released: a soft reset is enough to end a try | open |
| A6 | opening the port restarts the C6 often enough to matter for a monitor | usability | E ★C6 (the logs disagree) | — (decider) | 20 opens with pyserial, DTR and RTS logged, the ROM line `rst:` kept | proposed by the facilitator: a restart in 2 or more of 20 bare opens (DTR and RTS off, the firmware running, no esptool run before) means the monitor must say it, set 2026-10-15 | 0 of 20: the monitor can promise no restart | open |
| A7 | a grant kept in the store for a live session is safe enough | ethics | H ★C5 | — (decider) | Q6, then a design review | — (a decision), set 2026-10-15 | the PO wants a yes per try | open |
| A8 | live tries by the agent add trust beyond the simulation | value | H #204 ("connection with agents") | — (decider) | Q20 after slice 0 | — (an account), set 2026-10-15 | he does not read the agent's tries | open |
| A9 | the PO wants pin reads before he has wires | value | E ★C11 | — (decider) | Q22 | — (an account), set 2026-10-15 | he wants them only with wires: slice 3 waits | open |
| A10 | `mpremote resume` keeps values between two calls | feasibility | H ★C4 (TL-2) | — (decider) | on the bare board: `exec "x=5"`, then `resume exec "print(x)"` | — (an observation: 5 or an error), set 2026-10-15 | it does not: tries cannot build on each other | open |
| A11 | a USB-side chip reset (a port open with DTR and RTS off) and one retry reach the XIAO C6 on this Mac when its console went silent after a power-on | feasibility | E reach-test.md, the cause hunt: 1 clear cure (08:48, silence shown by the LED blink) and 1 likely cure (08:25, silence not shown before the reset), AT187. Rival: both cures came after mpremote opened the port with DTR and RTS True, so the cure can need that line change first, and a cold port may not reset. Rival: any fresh boot reaches 4 to 9 times in 10, so 1 cure in 1 fits a plain reboot | — (decider; D20 accepts it as remaining risk) | P251's proof: replugs on the XIAO C6, a diagnostic listen and a spark reach call after each, until at least 3 silent boots occurred, with the cure tried also from a cold port | D22, the PO: each of the 3 or more silent boots cured and reached, every other replug reached, each cure named in the output and the log, set 2026-10-15. Expected replugs (negative binomial mean 3/p): about 9 at the pooled probe rate 7 of 20, about 30 at 1 in 10; 14 and 52 for a 90 % chance | a silent board the cure does not reach: P251 needs another cure, or the silence goes upstream only | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Q14 to Q24, the account questions <!-- REQUIRED:collection --> | A2 (value) for slice 0 rests on Q14 and Q20; the others on later slices | the PO | AskUserQuestion, one at a time, past tense | Q14 and Q20 at the close (A2 and the value risk rest on them); the rest only if a later slice rests on one |
| A1, the reach rung | Q2 | the PO's hands (replugs) and Claude's runs | done 2026-10-15 on button-light, docs/observations/2026-10-15-p235-reach-test.md | done |
| A5, A10, Q5, Q9: what a reset does to pins, whether values survive, what "ends with a reset" means | slice 0's design | the PO's hands and Claude's runs | D10's first story, a short bench session on the bare board | the first story of slice 0 |
| A11, the cure | P251's done line | the PO's replugs and spark's reach call | P251's proof, 10 replugs | when P251 is built |
| A6, the restart on a bare open | slice 1 (the monitor) | the PO's hands and Claude's runs | 20 bare opens | before slice 1 |
| Q2 to Q13, Q25, the decisions | the first slice and its design | the PO | AskUserQuestion | done 2026-10-15: D9 to D17 |
| the MicroPython reset page and the Seeed XIAO C6 schematic | Q5, Q8 | Claude | open both at their sources | at design |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |
| 2026-10-15 | docs/observations/2026-10-15-p235-reach-test.md | A1: 10 of 10 after `mpremote reset` with the firmware running; 7 of 10 after a replug, each miss `could not enter raw repl`; after miss 1 only, a port open restarted the board and the next try passed; misses 5 and 7 not diagnosed | missed: 17 of 20 against 19 of 20 (D4) | the reach after a power-on is fixed first; slice 0 starts with that cause; A1 retired, A11 carries what is left |
| 2026-10-15 | docs/observations/2026-10-15-p235-reach-test.md, the cause hunt (D5) | probe silences: round A 1 of 10, round B 6 of 10 (each silent boot then touched by esptool, `Invalid head of packet (0x08)`, not download mode), round C stopped at its first silence (replug 4); on that boot the LED blinked as the sent code asked (the PO's eyes), a soft reset did not cure it, a port open with DTR and RTS off did (08:48) | no pass line set for the hunt | AT187; D6 picks the cure (P251) and an upstream report; A11 opened. 1 of 10 against 6 of 10: two-sided Fisher exact p = 0.057, so one rate near 0.35 with chance fits |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a: no battery, motor or regulator is in the USB slices, and the bare board runs on USB power. The one number here is
the harm of a wrong pin: two shorted outputs give about 97 mA, and an LED with no resistor about 79 mA (calculated from
datasheet-typ points IOH 40 mA at 2.64 V and IOL 28 mA at 0.495 V, a linear model that overstates the current,
https://documentation.espressif.com/esp32-c6_datasheet_en.html page 65, read 2026-10-15, PHY-2). The rung that would
settle it: a meter in series with a 330 ohm resistor on the pin (measured). It cannot show lifetime damage.
<!-- EXTEND:risks-sections -->
