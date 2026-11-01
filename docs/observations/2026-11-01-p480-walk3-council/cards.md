# P480 cards: ready to file after the PO's OK

> Ten new cards and one spike (section 1), ten edits to open cards (section 2), one question on G27 (section 3).
> Nothing here is filed. Each new card is a sub-issue of P100 (#6), except C1, which goes under P365 (#467).
> The order and the reasons are in `plan.md`. The PO's words are verbatim from P480 (#658).

## The PO's decisions, 2026-11-01

The PO said "ok, let's do it" to the whole list. The cards are filed: N1 is P482 (#661), N2 is P483 (#662), N3 is P484 (#663), N4 is P485 (#664), N5 is P486 (#665), N6 is P487 (#666), N7 is P488 (#667), N8 is P489 (#668), N10 is P490 (#669), N11 is P491 (#670), C1 is P492 (#671). N9 went into P466 (#634). The ten edits to open cards and the comment on P332 (#426) are made.

Ready, in the PO's order: P485 (#664), P487 (#666), P483 (#662), P468 (#636), P482 (#661). P469 (#637), P473 (#647) and P476 (#652) wait at the top of Idea, because Ready holds five. G27: option A, so `built` stays as AT151 decided until P491 (#670) draws the sheet. P481 (#660) is planned together with P488 (#667).

## 1. New cards

### N1: P? — every `/spark:build` overwrites the person's `sim/diagram.json` → the converter merges into the kept diagram

Label: bug. Slice: v0.10 The basic journey. Size S.

**Needed by.** The PO, 2026-11-01 08:17: "cause actually that should also be possible that one changes the chema
manually or edits the code manually etc." N3 sends board-only builds through the same path. Repro in `plan.md`: a moved
part and a `handAdded` part are both gone after the second build, and the two builds are byte-equal.

**The change.** The build copies the project's `sim/diagram.json` into its temp `sim/` before the converter runs
(`check_spine.py:705`), so `merge.ts` finds the old diagram (`cli.ts:85`). The verdict says how many parts and wires the
merge kept. The PR corrects `tools/circuit-to-wokwi/ARCHITECTURE.md:89-91`.

**Done when.** A test builds twice, with a moved part and a `handAdded` part between the builds, and both stay. A first
build with no old diagram is unchanged.

**Value proven by.** The next walk edits the diagram by hand, builds again, and keeps the edit.

### N2: P? — the FireBeetle's record names no Wokwi definition, so no limit says which GPIOs a scenario reaches → the record cites the S3 devkit's `board.json`, and the store keeps it

Label: task. Slice: v0.10 The basic journey. Size XS.

**Needed by.** The PO, 07:41: "at least some basic simulations and schams should work like now with this simple case
that however shows a lot of what to do with an unknown board or part for the schema r the simulation." Closes G13, G29.

**The change.** One `documents` entry in `boards/firebeetle2-esp32s3.json`, as the XIAO record has: the URL of
`esp32-s3-devkitc-1/board.json` in `github.com/wokwi/wokwi-boards`, its sha256 and the date. The store keeps the file
under `sources/`. Spark commits no Wokwi file. The PR cites the `wokwi_is_stand_in` note on P409 (#535).

**Done when.** `parts.py --match` no longer says "names no Wokwi definition" for the FireBeetle, and the P396 check lists
GPIO 21 and 47 as reachable. A test pins both.

**Value proven by.** P468 and N3 read the kept definition with no new fetch.

### N3: P? — a board-only diagram holds the board alone → the board's own LED and button are parts with `onboard`, wired by the converter

Label: story. Slice: v0.10 The basic journey. Size M, two PRs. After N1 and N2.

**Needed by.** The PO, 08:05: "it must be just like a parameter of any part or module or anthing that it is already on
swome thing, some board or mdule, it can lik to it or just say on me kindof ... really do show up in the schema as parts,
they just know they are on the board". And 07:41: "let's reenable simulation". Closes G26, G28, and G20 in part.

**The change.** PR 1: `OnboardPartReader`, beside `onboard_entries` in `scripts/boards.py`, turns each `pin_roles` row that
names a pin into a part with `onboard` set to the board's id. Its name for a person comes from the role's label, not the
id. It reads and writes nothing. PR 2: `design.parts_of` appends those parts, the converter wires them, and
`board_alone`'s hand-written diagram goes (`check_spine.py:571-590`). The P396 GPIO check stays. `refactor-plan.md:354`
gains the reader's row (target `records/board_records.py`).

**Done when.** Walk 3's requirements build a diagram with an LED on GPIO21 and a button on GPIO47, wired to the board,
and a test reads both. The FireBeetle's limits still name what the stand-in lacks. No paid Wokwi run.

**Value proven by.** A free scenario on walk 3's project presses the button and reads the LED.

### N4: P? — a passed run that tested no must line says only "passed" → the verdict says "passed: the firmware starts, no must line tested"

Label: story. Slice: v0.10 The basic journey. Size XS.

**Needed by.** The PO, 07:41: "so that we at least know what's actually working and what not". G32.

**The change.** `run_scenario.py` builds the verdict line from the step counts the log already holds (log line 3,
"step counts: expect-pin 0, set-control 0, wait-serial 2"). The JSON gets the same words.

**Done when.** A test with zero `expect-pin` and zero `set-control` steps gets the new line in the text and the JSON. A run
with an `expect-pin` step keeps "passed".

**Value proven by.** Claude reports walk 3's run as "the firmware starts", not as a test of the must lines.

### N5: P? — `parts.py <op> walk3` made `walk3/walk3` → one finder takes a listed name or an existing folder, says which, and makes nothing else

Label: bug. Slice: v0.10 The basic journey. Size S.

**Needed by.** The PO, 07:19: "yeah the cleanup should  done nd also noted and debugged how it happened". G9, G17.

**The change.** `ProjectFinder` wraps `store.find_listed_name` (`store.py:266`). It takes a listed name first, then an
existing folder, and says which it took. It never makes a folder. The card changes §8 S rule 5 ("the project's folder
made when it is new", `needs.py:114`), and the PR says so in the rule's text.

**Done when.** `--step walk3 S` from inside `walk3` uses the listed project and says so. A name nobody listed gives
`could-not-run` and makes no folder. Tests pin both.

**Value proven by.** No walk makes a nested project folder again.

### N6: P? — six pages told Claude wrong or nothing → each page says what its command writes and does

Label: chore. Slice: v0.10 The basic journey. Size XS.

**Needed by.** The PO, 07:59: "good point to note down and analyze and fix later."

**The change.** `commands/init.md` names the store's `projects.json` (G5). `commands/idea.md` says that `--step` writes
the history and shows its dry run first (G8, G17), and that the other-choice note comes only with a pin limit
(`needs.py:377`, G14). `commands/build.md:147` and the tally hint `parts.py:2282` say a board-only build writes no
`built` (G27). `commands/deploy.md` says what to do when the host refuses the run (G35). The firmware step shows the lines
that read the console without waiting (G30).

**Done when.** Each sentence is in its page, and the hint test pins the tally line.

**Value proven by.** The next walk's Claude reads these pages and says nothing wrong about the store.

### N7: P? — no `--help` names the store place a command writes → each write in `effects` names its `place` and `path`, and the build has a dry run

Label: story. Slice: v0.10 The basic journey. Size M. After N6.

**Needed by.** The PO, 07:59: "good point to note down and analyze and fix later." G25.

**The change.** `effects` stays the one name (`parts.py:1599`, `board_envelope.py:59,98`, `NextStep` in
`spark/core/result.py:18`). Each write adds `place`, a key of `store.PLACES` (`store.py:85`) or `project`, and `path`.
`--describe --json` and `--help` read the same declaration. `check_spine.py` gets `--dry-run`. N6's effect sentences then
point to the declaration.

**Done when.** A test fails for an operation that writes the store and declares no `place`. `--help` of `parts.py` and
`check_spine.py` names each place. `docs/guide/agents.md` says how a caller reads it.

**Value proven by.** An agent asks `--describe --json` before a write, and its answer matches what the run writes.

### N8: P? — the look says "could-not-run" for "read, no token yet" and for "not read", with an empty `next` → a `board_read` field, a `NO_REQUIREMENTS` code and a full `next`

Label: story. Slice: v0.10 The basic journey. Size S. After P469 (#637).

**Needed by.** The person in walk 3, 07:02 (diary): "Yes, use the look to find out what board we have and what its state
is." Stalls S1, S4, S6. G3, G18, G19, G36.

**The change.** A missing `requirements.json` gets `NO_REQUIREMENTS`. A file with no `board` key keeps `NO_BOARD_NAMED`
(`board_look.py:470-474`). `board_read` is true when the board answered chip, flash and MAC, and it names which of
P469's looks read it. `next` drops `--port` when one board is on USB (`board_envelope.py:38`), and after the bootloader
buttons it carries "press RESET once" (`board_doctor.py:46-47`).

**Done when.** Tests pin each: a look with no `requirements.json`, a look that read every field, one board with no
`--port`, and the RESET line.

**Value proven by.** The next walk's first look gives a next step that the person runs as printed.

### N10: P? — spark has no place for a must line seen working on the bench → `seen_on_bench`, written only on the person's typed yes

Label: story. Slice: parked after v0.10. After W4-2.

**Needed by.** The PO, 07:41: "so that we at least know what's actually working and what not". G37.

**The change.** Deploy's gate asks the person, after "ready seen", which must lines they saw work. Their typed yes writes
`seen_on_bench` beside `unnamed_must` in the board's store record. Claude never writes it.

**Done when.** The next look shows each must line seen on the bench, and a test shows that no path without the typed
yes writes it.

**Value proven by.** A walk's diary names a must line as tested on the bench from spark's own output.

### N11: P? — a board's own parts reach the diagram only → the breadboard sheet, the schematic and the page show them, and the `board_only` fork goes

Label: story. Slice: parked after v0.10. After N3 and P446 (#597, part shapes).

**Needed by.** The PO, 07:27: "it might be better to show the schema and the breadboard and all even though its just
onboard". G20.

**The change.** The sheet, the schematic and the page read the parts N3 adds. The fork at `check_spine.py:386-389` goes.

**Done when.** Walk 3's build writes a breadboard sheet and a schematic that show the LED and the button on the board.

**Value proven by.** A board-only walk gets the same outputs as a walk with one added part.

### C1: P? — Spike: spark uses few of Wokwi's free tools and has no own emulator → a finding on the best use of Wokwi and what an own emulator on free software costs and proves

Label: spike. Slice: parked after v0.10. Sub-issue of P365 (#467).

**Needed by.** The PO, 07:41: "let's just made this best usage and substitutions of wokwi tools card to spike it and
explore hw to best wokwi and what it would actually mean to make our own emulator based on some freely usable software
... I'd like to get into that after the MVP".

**The change.** A finding with sources answers three questions. 1: which free Wokwi tools spark uses, and which it can use
more (`wokwi-cli lint`, `chip compile`, `--vcd-file`, wokwi-mcp). 2: what an own emulator costs and proves, from
`docs/discovery/2026-10-18-p295-own-simulator/finding.md` (G23). 3: how each model is checked against the real part.
A board or module that Wokwi lacks is P409 (#535), and this spike links it. G21, G24, G31, I2 wait for this finding.

**Done when.** The finding answers the three questions with sources, and the PO picks the next step.

**Value proven by.** The PO's pick becomes a card in a later version.

## 2. Edits to existing cards

| card | section | exact new text |
|---|---|---|
| P468 #636 | title | "P468: the 'no serial monitor' warning fires for boards that print over USB → it reads the Wokwi definition's `serialInterface`" |
| P468 #636 | body, replace the body above "Needed by" | "Walk 3's diagram had no connections, and its run matched `ready` (log line 40). Walk 2 heard the XIAO with no wires too (P400 row 18). The warning at `check_spine.py:605-607` tests `serial_wired(diagram)`, not a board fact. The kept XIAO definition sets `serialInterface: USB_SERIAL_JTAG`, and Wokwi's ESP32 guide says to remove `$serialMonitor` wires then (docs.wokwi.com/guides/esp32, read 2026-11-01). Outcome: the warning reads `serialInterface` from the kept definition, after N2 keeps the S3 devkit's. If that definition does not set it, walk 3's run is the evidence, and the PR says so. Done when: walk 3's build prints no serial warning, and a board on a UART console with no wires keeps it." |
| P469 #637 | body, add before "Needed by" | "The P472 finding (#643, PR #645): there are two looks. mpremote on the running MicroPython does not restart the board. esptool `flash-id` restarts it. The look uses mpremote first, and esptool only when mpremote cannot reach the board. Download mode with no hands is `machine.bootloader()` through mpremote, then esptool `--before no-reset`. Walk 3 needed the buttons twice (G34). Done when also: the look says which look read the board. N8 follows this card." |
| P466 #634 | body, add before "Needed by" | "Slice 1 also takes walk 3's G15: the doctor prints the USB serial `34851842e4100000`, which holds the MAC (`board_doctor.py:103`). Slice 2 (walk 3's G1, G4, G7, ex-N9): the look reads a board before init and names its chip, MAC and store record. Done when also: an empty folder's look names the chip, the MAC and the store record." |
| P406 #531 | Done when, add | "The offer does not print the same `does` words twice (walk 3 G12: 'compute microcontroller' twice)." |
| P118 #52 | Value proven by, add | "The 'not asked for' line names its cause when nothing is built yet (`check_all.py:466`, walk 2 G1, walk 3 G6)." |
| P399 #515 | The change, add after PR 1 | "After N3, a board-alone diagram holds the board's own LED and button. The id check then knows their ids, and a test presses one and reads the other." |
| P476 #652 | body, add before "Needed by" | "Waits for W4-2 (deploy on the core). The why goes on the event that W4-2 reports (decision on #94, P478 #656), so deploy's lines change once." |
| P473 #647 | Done when, add | "The store rides `NextStep` (`spark/core/result.py:18`), so W4-2 builds deploy's `next` on it." |
| P409 #535 | body, add | "Walk 3's spike C1 (P?) links here for a board or module that Wokwi lacks. N2 and N3 answer it for the FireBeetle's LED and button." |

No open card closes. P332 (#426) keeps the assigner side: one comment, "N3 draws the board's own parts. This card keeps
the pins they hold out of the assigner."

## 3. The question for the PO on G27

Walk 3's board-only build passed every stage it ran. It skipped the breadboard sheet and the schematic, so by your
decision AT151 it wrote no `built` line, and the tally shows walk3 as not built.

After N3, the same build draws the LED and the button in the diagram, but N11 (the sheet) comes later. Which do you want?

- **A.** `built` stays as today: written only when no stage is skipped. Walk 3 gets it after N11.
- **B.** A board-only build writes `built` when every stage it ran passed, and the line names the skipped stages.
