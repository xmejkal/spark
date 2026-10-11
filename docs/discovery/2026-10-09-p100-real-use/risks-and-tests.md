# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | P100 tells us nothing: it measures the agent, a scratch store or a broken baseline, not the product (po-assistant pre-mortem) | ★C4, ★C8, ★C9 | write the pass lines and the board decision before round A; score diaries by user step and outcome (DIR-3) | open |
| usability <!-- REQUIRED:risk-usability --> | a hobbyist stalls where the agent did: the board held (★C1), the vocabulary (C10), no path to a running board (★C6) | user USER-3/7/9 | the rounds' diaries, each stall a numbered gap | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | no round can pick a board: both library boards held; the XIAO does not build; his other boards have no record | ★C1, ★C2 | Q3 — release the S3, a scratch store, or research a board | open — Q3 |
| viability <!-- REQUIRED:risk-viability --> | the rounds write into his real store (reservations, catalog, history) and leave it in a state P178 inherits | FEAS-10, PO-9 | Q3 (b) or a decision on what a round may write; the guard P164 is a P178 sub-issue | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | none beyond personal use; a LiPo on round B's node (see power) | — | — | n/a |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | the node's life rests on an assumed 100 mA × 5 s burst and an unpublished board draw; the PSRAM's deep-sleep draw is a bench question | C11 (calculated; the burst H) | measure the board's sleep and burst current with his meter (does he own a µA-capable one? tech-lead Q6) | open |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | no motor in either candidate (the irrigation valves are MOSFET-driven solenoids — round C adds no motor) | tech-lead FEAS-4/5 | — | n/a |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | no high-current part in A or B; irrigation's buck is the existing design's | — | — | n/a for A/B; C unchanged |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | a footswitch cable on the MIDI controller is an ESD path; unexamined | — | the bench: does it reset when kicked? | open if MIDI is chosen |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | SCD41 needs its ASC/forced recalibration; the soil probe's reading is relative (the irrigation diary) | H (vendor docs not re-read here) | read the vendor page when the sensor is chosen | open if the node is chosen |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | the node's WiFi burst on a LiPo through the board's regulator; the datasheet's peak is not the board's | C11, PHYS-2 | measure the burst at the battery with a scope or a meter's min/max | open |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | the S3 wakes from GPIO (the bin's firmware proves the API on paper only — nothing has run on hardware); Wokwi does not wake the C6 (B27 for the S3); for D8's C6: `Pin.irq(wake=DEEPSLEEP)` silently no-ops and `esp32.wake_on_ext0` does not exist — `esp32.wake_on_ext1` is the route (bin CLAUDE.md, Power); round 0 recorded wake_capable_gpio 0–7 and deep_sleep_ua 36 (the wiki's) | bin CLAUDE.md; B16, B27; council/round-0-runner.md | a wake-reason line printed on the real board (the bin's own B16, shared) | open |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | starting the S3's USB device stack disables its serial console; re-flash in download mode; the S3's two power designs differ in I2C pull-ups (B21) | PHYS-5, PHYS-7 (Espressif docs read 2026-10-09) | note it in the MIDI round's plan; identify his board's revision (B21) | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | the library's eight records serve neither candidate; owned sensors have no record; the DFRobot pages for SCD41/VEML7700 modules are the research source | ★C3 | round B researches them; cost counted | open |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | P100 can measure the product rather than the agent, with n = 1 | value | ★C8, ★C9: every run so far was an agent or the PO | — (decider) | pass lines and the board decision written before round A; diaries scored by someone who did not write them | each round's diary opens with its predictions, dated — set 2026-10-09 | the scorer finds the diary records fixes, not stalls | open |
| A2 | a round can pick a board at all | feasibility | ★C1, ★C2: both library boards held; the XIAO does not build | — (decider) | Q3 | one documented act releases or chooses a board — set 2026-10-09 | no documented act exists → a gap filed, the round runs in scratch | open — Q3 |
| A3 | the library serves one small owned-parts project fully (round A) | feasibility | ★C3: only the plant alarm's shape | — (decider) | `--match` on round A's needs: every need gets an exact candidate | zero "[other words]" picks — set 2026-10-09 | a gap on an owned-parts round | open |
| A4 | research of an owned sensor (SCD41 / VEML7700) yields a record the chain can build with (round B) | feasibility | README "Research: partly — done by agents, not run here"; the catalog's 18 records' state unknown (DIR-2) | — (decider) | run `/spark:research` on one owned sensor; `--validate`; build | a cited record with no owed fact the build reads — set 2026-10-09 | the record lands owed and the build refuses it | open |
| A5 | "firmware that runs" has a path the person can follow | usability | ★C6: no document says how code gets onto the board | — (decider) | write the flashing step into the round's plan from the vendor's page, then see if a round reaches it | a wake-reason line (node) or a MIDI note on the Mac (controller) seen — set 2026-10-09 | not reached → P79's bench step is the blocker, filed | open |
| A6 | irrigation's `check_all` FAIL (★C4) is B13's rule too wide for LED-load inputs, not the project's data | feasibility | refuter ★C4: the STATUS_LED exit 1 is documented since 2026-09-29 (no change at all — ruled in); the FAIL follows 4daa58f meeting four `must_not_float` entries the DFR0457 record calls a current load | — (decider) | read the four rules entries against the DFR0457 record and B13's rule; record both causes in round C's diary | both causes named in the diary before round C — set 2026-10-09 | the project's own rules entries are wrong → round C starts by fixing data, a different test | open — narrowed |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| his yes to the changed frame (three rounds, round 0 on the C6)? <!-- REQUIRED:collection --> | everything after | the PO | AskUserQuestion, one question | next |
| Q1 — importance of A1–A6 and the pass lines | the riskiest test | the PO | AskUserQuestion | after the frame |
| the domains for A and B; round C's feature | rounds A–C | the PO | AskUserQuestion | after Q1 |
| who scores the predictions (not their author) | every diary's scoring, round 0's included | the PO | AskUserQuestion | before round A |
| does the C6 wake from GPIO under MicroPython (`wake_on_ext1`), and what does the board draw in deep sleep? | round A's pass line; C11 does not transfer | a bench measurement (B16's protocol, shared) | the board on a meter — not run | round A |
| are the four `must_not_float` entries on irrigation's valve inputs the project's error or B13's width? | A6, Q6 | the rules file against the DFR0457 record | a read, then one `check_all` | round C's first step |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
- D8's board (the C6, round 0's record): deep sleep 36 µA board-level (stated, the DFRobot wiki; the chip alone 7 µA datasheet-typ, C6 DS Table 5-11) · radio peak 354 mA (datasheet-max, DS Table 5-7 p66) · charge 0.5 A (stated, wiki; 0.54 A calculated from R9) · regulator_3v3_a not read · settled by: a bench measurement of the board asleep and at a WiFi burst (electronics-firmware:R1, not run) — the first rung before any battery-life number for round A
- The S3 numbers in C11 (8 µA, 59/227 days) do not apply to the C6 and, for the PO's N16R8, not to the S3 either (the datasheet's note above Table 12); no number for that board until measured
- No motor, no mains; the LiPo (1000 mAh, stated) is held by the bin — round A's battery is open
<!-- EXTEND:risks-sections -->
