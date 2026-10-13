# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | E ★C21: J1 is the one job with a blocked person, the PO (n = 1). D6 asks for a seamless known board. Other makers are H | the PO's walk to a lit LED (P100) through slice 0. Then a use log of slice 1 for a week (n = 1) | open |
| usability <!-- REQUIRED:risk-usability --> | H A6, A8: a look that leaves the board in download mode, and a yes that an agent passes by habit (POJ-28 item 2) | the PO runs slice 0 at the bench and answers the account questions (Q23) | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | E ★C3, ★C5, ★C7 read from sources. H A1 to A5, A10, A11: nothing ran on a board | P228's read-only bench, then P215's one flash, each about an hour (electronics-firmware:R5) | open |
| viability <!-- REQUIRED:risk-viability --> | E ★C20: each image change needs a metered Wokwi run. E PO-3: esptool is GPL-2.0-or-later, called as a separate process. Slices 0 to 2 need no new tool (★C14) | a desk read (electronics-firmware:R0) of the metered cost per change, and Q4's answer on the update gate | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E ★C1, ★C2: an erase of any board esptool reaches, behind a prose gate. H A7, A8. A backup can hold Wi-Fi credentials (TLJ-14). OTA reaches a board over the network (TLJ-25) | fake-run tests of the core gate (electronics-firmware:R2), then the PO's answers to Q2 and Q3 | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | E PHYS-8: the VCC pad gives 3.6 to 4.5 V on USB by #73's reading, not 5 V. It matters to what a live try drives, not to a flash | the meter reading #73 names, under P139 | n/a because no deploy decision rests on a power figure |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | none: no motor in the deploy journeys | — | n/a because deploy drives no motor. A live write to a wired pin sits in the contract row |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | — | — | n/a because a deploy dissipates nothing beyond the board's own use |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | E TLJ-5, `boards/firebeetle2-esp32s3.json` `pin_roles.console_uart`: GPIO43 and 44 twitch at every reset, and every look resets the chip (★C8) | a bench symptom test: does a look or a flash twitch a load on GPIO43 or 44? | open |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | H USERJ-22: a live ADC read is a fact about one moment | — | n/a because no reading decides a deploy |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | H TLJ-16: the firmware drives its outputs at once after the first boot, with the loads attached | the first boot at the bench with only the LED on its resistor (electronics-firmware:R5) | open |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | H TLJ-1, TL-12: a board in deep sleep drops its native USB, so a look or a session reads nothing (state D) | a desk read of the vendor's USB guide (electronics-firmware:R0). When a project sleeps, a bench step | open |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E ★C16, ★C17: strap, console and USB pins are named, a signal's direction is not exported, and the revision changes the I2C bus | a desk check of the pin list against `pin_roles` (R0), and an I2C scan with nothing wired beside the revision read by eye (R5) | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | E: the documents disagree in four places. The BOOT and RESET press order (PHYS-2). The S3 builds (★C6). The flash mode: DIO in the kept header, QIO in the build file (TLJ-15). The VCC pad (PHYS-8). An S3 errata blocks USB-OTG download on chips dated before 2219 (PHYS-2) | a desk read (R0), and a look at the part in hand: the chip's date code and the revision | open |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
Every test below is read-only or a single flash through the gate. None needs a Wokwi minute. The bench rows are
electronics-firmware:R5 on the PO's board, P228's read-only bench (#215) or P215's flash half (#196).

| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | a command can see `ready` after a flash on the S3's native USB | feasibility | H ★C7, PHYS-1 | — unrated (Q1) | P215 bench: `mpremote connect <port> repl --capture`, press RESET, then Ctrl-D | `ready` is in the capture after the soft reset, and the hard-reset case is logged as seen or not seen, set 2026-10-13, proposed | `ready` is not seen after a soft reset: the skeleton's proof line needs another read | open |
| A2 | the 4 MiB image boots on the 16 MB N16R8 and mounts a filesystem that holds `main.py` | feasibility | H: ★C5 is refuted, the partition outgrows the image's filesystem on 16 MiB | — unrated (Q1) | P215 bench: `mpremote fs ls` and `os.statvfs('/')` after the flash | `main.py` is listed and the block count is written down, set 2026-10-13, revised the same day before any result after ★C5 was refuted, proposed | a bare REPL with no `main.py`: the image layout changes before any other slice | open |
| A3 | the Standard MicroPython build is right for the N16R8 for a button-and-LED project | feasibility | H ★C6 | — unrated (Q1) | P215 bench: `gc.mem_free()`, `esp32.idf_heap_info`, and the esptool features line | the Standard build prints `ready`, and the heap figure is logged as measured, set 2026-10-13, proposed | no boot or no `ready`: the matching-base slice moves into slice 0 | open |
| A4 | the pinned esptool refuses another chip with a read and writes nothing | feasibility | E ★C19: shown only with a fake run | — unrated (Q1) | P228 bench: `esptool --chip esp32c6 flash-id` against the S3 | a non-zero exit with a message that names the chip, set 2026-10-13, proposed | it connects or reads: the core compares the chip itself before any write | open |
| A5 | esptool 5.5.0 prints the chip, the flash size and the MAC of the N16R8 in a form the core can parse | feasibility | E ★C3 from master source, H for 5.5.0 | — unrated (Q1) | P228 bench: `flash-id`, `chip-id`, `read-mac`, `get-security-info`, outputs kept as fixtures | each of chip, flash size and MAC is in the output, and the PSRAM line is logged as present or absent, set 2026-10-13, proposed | a field is missing: the probe reads it through MicroPython or reports it as unknown | open |
| A6 | a read-only look leaves the board running, with no button press | usability | H ★C8, USERJ-5 | — unrated (Q1) | P228 bench: run `flash-id` while the board runs its firmware, then watch it | the board runs again with no button press, set 2026-10-13, proposed | it waits in download mode: every look ends with the RESET sentence | open |
| A7 | the facts the core can read, with the person's word for the rest, catch the wrong-board cases that harm a breadboard project: another chip, another SKU, another board swapped in | value | H ★C3, ★C4, ★C25, POJ-26 | — unrated (Q1) | P228 bench, read-only: compare the outputs with the real record, and with a scratch copy changed to the N4. If a second board is at the desk, swap it in | the real record reads same for chip and flash. The N4 copy reads "flash differs". A swapped board reads another MAC. Revision and wiring read unknown. Set 2026-10-13, proposed | a wrong board reads same on every field: the gate needs the person's confirmation on every first write | open |
| A8 | a yes bound in the core to port, MAC and image stops an agent from erasing without the person | ethics | H ★C10, TLJ-16 last row | — unrated (Q1) | fake-run tests of the core (electronics-firmware:R2), with no yes and with a yes for another MAC | both runs refuse and erase nothing, set 2026-10-13, proposed | either run erases: the yes must come from the person's own terminal (Q3 option a) | open |
| A9 | the silent checks of a known board catch a swapped board and a board changed by another tool | ethics | H POJ-34, TLJ-29 | — unrated (Q1) | bench, after slice 0: flash the board by hand with another tool, then run the known-board deploy | the deploy stops and names the field before any write, set 2026-10-13, proposed | it writes: the known board also needs the board's files or a marker read (Q5) | open |
| A10 | the USB serial number is the MAC while MicroPython runs, so the port list tells two boards apart with no contact | feasibility | E ★C9 for the ROM, H for MicroPython | — unrated (Q1) | P215 bench, after the flash: `mpremote devs` beside `esptool read-mac` | the serial in `mpremote devs` equals the MAC, set 2026-10-13, proposed | they differ: two boards are told apart only by an esptool read, which resets them | open |
| A11 | the PO reads the revision from the board in under a minute, by eye | usability | E ★C17 | — unrated (Q1) | P228 bench: the chip between BOOT and USB-C, or the back silkscreen | V1.1 or V1.2 is logged within 1 minute, by the PO's own clock, set 2026-10-13, proposed | it cannot be read: the electrical inference of PHYS-7 is tried, and the revision stays unknown | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| How important is each assumption, and what pass line holds? <!-- REQUIRED:collection --> | Q1 | the PO | asked in this session, one question at a time | next |
| What do esptool 5.5.0, `mpremote devs` and the PO's eyes show on the N16R8 (A4, A5, A6, A7, A11)? | Q7, Q10, Q19, slice 0 | the PO, at P228's read-only bench | the commands in A4 to A7 and A11, outputs kept as fixtures | the P228 session |
| Does `ready` show, does the filesystem mount, and does the Standard build serve (A1, A2, A3, A10)? | Q11, Q16, slice 0 | the PO, at P215's flash half | one flash through the gate | after P228 and P219's first story |
| Does the core gate refuse with no yes and with a yes for another MAC (A8)? | Q3 | Claude, with fake-run tests | tests in the repository | with P219's first story |
| Which IDF version builds MicroPython v1.29.0 (★C5 caveat)? | A2 | Claude, a desk read of MicroPython's v1.29.0 build files | one fetch, inside a search budget the PO sets | before the P215 session |
| What is the sha256 of the SPIRAM_OCT file? | Q11 | the PO, on a yes to the download | a download into the store | when Q11 says fetch |
| Which friction moments did the PO meet before (the account questions)? | Q23 | the PO | past-tense questions from `council/user.md` and `council/user-journeys.md` | as the PO chooses |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a for energy, peaks and heat: no deploy decision rests on them. The board runs from USB on the bench.

The deploy's time budget instead, from TLJ-2 and TLJ-32:

- the write of the 4 MiB image: upper bound 91 s (calculated: 4 MiB × 10 bit / 460,800 baud, no compression, inputs
  stated). Native USB does not use the baud rate (H). Measured value — until the bench (electronics-firmware:R5).
- a 16 MiB backup with `read-flash`: upper bound 364 s (calculated, the same inputs). Measured value —.
- each read (`mpremote devs`, `mpremote exec`, an esptool connect): — until the bench measures it.
<!-- EXTEND:risks-sections -->
