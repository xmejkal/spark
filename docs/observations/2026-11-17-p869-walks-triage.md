# P869: the triage of P711's three walks and P867's items

> 32 walk rows, one more row (D14), 3 page notes that are in no rows file, 8 proposed items and 10 "Later" lines
> are triaged here. 16 rows join open cards, 5 become new cards, 2 are dropped and 9 stay rows. There are 11 cards
> to file. Six cards stand before the new walks. Two of them are recommended for the top of Ready, above P827 and P828.

The card is P869 ([#1236](https://github.com/xmejkal/spark/issues/1236)), under the walks epic P365 (#467). P480 (#658,
`2026-11-01-p480-walk3-council/`) and P510 (#705, `2026-11-01-p510-walk4-council/`) did the same for earlier walks.
This file is the triage on Fable 5.2, 2026-11-17 (Europe/Prague), revised after one lens and two rounds of the refuter. Each of
their rulings was checked in the code first. Where a ruling and the code differ, the code stands, and section 7
says so. The section "Filed" below says what was filed and posted from it on 2026-11-17.

## Filed

The PO said yes to the cards on 2026-11-17 ("after a thorough analysis, we should create the cards, refine it, so its
well testable, exchangable, reusable"), and the session filed them in his auto mode after the last refuter round.
Each card is in Idea, under its epic, with its slice. Sections 4 and 5 keep the ids N1 to N11.

| id | card | result |
| --- | --- | --- |
| N1 | P874 ([#1242](https://github.com/xmejkal/spark/issues/1242)) | the build replaces its own board.tsx, keeps one previous version, and still leaves a person's edits alone |
| N2a | P875 ([#1243](https://github.com/xmejkal/spark/issues/1243)) | the sheet keeps the list of changes since the last sheet spark wrote for another design |
| N3 | P876 ([#1244](https://github.com/xmejkal/spark/issues/1244)) | one read of the console that leaves the firmware running, after a bench row names the cause |
| N4 | P877 ([#1245](https://github.com/xmejkal/spark/issues/1245)) | it names each such entry and removes it on the person's yes |
| N5 | P878 ([#1246](https://github.com/xmejkal/spark/issues/1246)) | a tick only for a judged pass, and the reason that is true |
| N6 | P879 ([#1247](https://github.com/xmejkal/spark/issues/1247)) | a finding: can a trace between two pins carry the signal's name? |
| N7 | P880 ([#1248](https://github.com/xmejkal/spark/issues/1248)) | every phase made from a changed thing reads out of date, with its cause |
| N8a | P881 ([#1249](https://github.com/xmejkal/spark/issues/1249)) | a signal on no bus keeps its pin, and every moved pin is named |
| N9 | P882 ([#1250](https://github.com/xmejkal/spark/issues/1250)) | a name the pin map lacks reads as a problem in the firmware phase |
| N10 | P883 ([#1251](https://github.com/xmejkal/spark/issues/1251)) | spark prints a plan (what goes out of date, which wires move, what is lost) and changes nothing until the yes |
| N11 | P884 ([#1252](https://github.com/xmejkal/spark/issues/1252)) | buy lines from what the records hold: the maker, the product code, and whether the drawer has it |

The lines of section 5 are comments on #1231, #1230, #1235, #270, #1241, #1168, #539, #1010, #434, #1005 and #716.

Ready is unchanged. The order of section 6 is a recommendation, and the place of each card in Ready is the PO's to
order. No card was moved into or out of Ready.

## 1. What was read, and how

- The rows: `spark-walks/p711-identify-amp/rows.md` (9 rows counted), `spark-walks/p711-walk4-button-led/rows.md`
  (7 rows counted) and `spark-walks/p711-sound-demo/rows.md` (16 rows counted), 32 in all. Also the 9 notes of
  `spark-walks/p711-sound-demo/page-notes.md` and walk 3's `diary.md`.
- `docs/discovery/2026-11-17-p867-journey-redefined/items.md` (8 items without the spike, and two "Later" bullets
  with 4 and 6 lines) and `brief.md` (D5 to D14, D21).
- The open cards #1228, #1229, #1230, #1231, #1235, #1238, #1241, and six `gh issue list --search` runs.
- The code at `364bb059`. Each claim below names its `file:line`. A claim with no line says "not checked".
- `flow.py show` ran on scratch copies of two walk folders, with `SPARK_HOME` on a scratch copy of the store. No
  board was touched, no simulation ran, and no build ran.

The bar is `scrum/VISION.md` and AGENTS.md: does the card move a basic project closer to a breadboard with working
firmware? Codes in this file: A is walk 1 (the amplifier's picture), B is walk 2 (the button and the LED), C is
walk 3 (the sound demo), I is an item of `items.md`, L is a "Later" line, N is a card of this triage. The N codes
keep their first numbers, so the council's reports still match: N2 is N2a, and N8 is N8a.

| input | JOINED | NEW | DROPPED | STAYS A ROW |
| --- | --- | --- | --- | --- |
| the 32 walk rows | 16 | 5 | 2 | 9 |
| the D14 row | 0 | 1 | 0 | 0 |
| the 3 page notes in no rows file | 0 | 0 | 0 | 3 |
| the 8 items | 0 | 7 | 0 | 1 |
| the 10 "Later" lines | 3 | 3 | 0 | 4 |

So 12 lines of the walks stay a row: 9 rows and 3 page notes.

## 2. The rows

### Walk 1, the DFR0954 amplifier (9 rows)

| row | what | outcome | where, and the line to add |
| --- | --- | --- | --- |
| A1 | `/spark:research` ends at reuse and looks for no picture | JOINED | P735 (#1010, a full record of each DFRobot part) and P340 (#434, research keeps datasheets and pictures). Add to each: "walk 1 of P711, row 1: with the goal of a breadboard picture, research ended at reuse and looked for no picture". |
| A2 | `parts.py --show` prints no `body_mm` | JOINED | P862 (#1228). Checked: `scripts/spark/sourcing/show_part.py` holds no `body_mm`. No line. |
| A3 | the record keeps no product picture | JOINED | P735 (#1010) and P340 (#434), with A1. |
| A4 | `drive / audio amplifier` offers no amplifier | JOINED | P863 (#1229). No line. |
| A5 | every walk board is held by older projects | STAYS A ROW | With C1. No start list of a walk exists. Walk 3's diary says the holds were freed by hand with `/spark:drawer`. The row also names plant-alarm, which is no walk, so a start step for walks frees only a part of it. Q7 proposes that step. |
| A6 | does the DFR0954 carry its own speaker socket? | JOINED | P864 (#1230). The answer (the kept drawing, page 1) is that card's evidence. |
| A7 | no breadboard picture for a module with a full record | JOINED | P734 (#1005, each module drawn). No line. |
| A8 | the sheet asks for a supply on the amplifier's outputs | DROPPED | Fixed by P860 (#1226, closed, PR #1232). Not run again here. |
| A9 | the speaker terminal is a separate part "to get" | JOINED | P864 (#1230), with A6. |

### Walk 2, the button and the LED (7 rows)

| row | what | outcome | where, and the line to add |
| --- | --- | --- | --- |
| B1 | the pick names the joystick as the other choice for a button | STAYS A ROW | `needs.py:296-310` names the first owned, free part with a Wokwi model whose words match. It is a ranking wish. No walk stopped on it. |
| B2 | the tally says "its cost was not counted" | STAYS A ROW | With C3. `run_cost.py:263-265` prints it when no count reached the line. Why three answers came in one session is not checked. The tally does not move a project to a breadboard. |
| B3 | the look reads a board of another project and restarts it | JOINED | P865 (#1231). Section 5 gives its Done-when lines. |
| B4 | spark cannot say how many free Wokwi minutes are left | JOINED | P413 (#539, a count of the Wokwi minutes). Add: "`run_scenario.py` shows the month's total before it asks for a run (walk 2 of P711, row 4)". The card's own caveat stands: spark does not know Wokwi's balance, so the line names no plan figure. |
| B5 | reads in a row flip between failing and passing | JOINED | P865 (#1231). Every read restarts the board (`board_look.py:54`, `:201`). Section 5 has its line. |
| B6 | "spark's last deploy here: walk4" reads as the box's state | JOINED | P865 (#1231). Add: "the last-deploy line (`board_look.py:392`) says it is spark's own record and that a flash outside spark is not seen (P867's D8: a witness has a source and a time)". |
| B7 | no way to watch the firmware's lines while it runs | NEW | N3, with the D14 row. |

### Walk 3, the sound demo on the game box (16 rows)

| row | what | outcome | where, and the line to add |
| --- | --- | --- | --- |
| C1 | two walks cannot both hold one walk board | STAYS A ROW | With A5. |
| C2 | the record names no speaker socket, and the build stops | JOINED | P864 (#1230). Section 5. |
| C3 | the tally gave three different answers | STAYS A ROW | With B2. |
| C4 | a supply on SPK_P and SPK_N again | DROPPED | Fixed by P860 (#1226, closed). |
| C5 | a button's ground goes to "the row of Max98357aDfr0954 GND" | STAYS A ROW | The wiring is right: the ends of a point meet in the row of one end (`wiring_steps.py:52`). It is a wording choice. Look again when P828 (#1186) puts the steps on the page. |
| C6 | "Disconnect the SPEAKER_N supply." for a wire nobody wired | NEW | N2a for the list. What was wired is a witness: one line to add to P873 (#1241), section 5. |
| C7 | the page shows only three tabs | JOINED | P827 (#1185), P828 (#1186) and P873 (#1241). No line. |
| C8 | the schematic names nets `Mcu_pin4` and `Mcu_pin20` | NEW | N6, a spike first. |
| C9 | "a log from an older spark names no image" | NEW | N5. |
| C10 | the commands start with `${CLAUDE_PLUGIN_ROOT}` | STAYS A ROW | Written on purpose (`flow_codes.py:47-49`). A person reaches the commands through Claude or the page (P827). Q5. |
| C11 | "Tell Claude your goal in the chat" though the brief holds the goal | STAYS A ROW | P820's plan holds "a stored goal" after its MVP. Seen again in this triage's run. |
| C12 | a pin on an I2S bus line is refused | JOINED | P868 (#1235). Section 5. It happens only when spark describes wiring that exists, here the game box. |
| C13 | "traces differ" for a board.tsx that spark wrote | NEW | N1, with item I1. |
| C14 | BOOT and RESET twice: once for the look, once for the deploy | JOINED | P865 (#1231). Section 5. |
| C15 | the deploy line of another walk came from the terminal's history | STAYS A ROW | The line was the person's own history. Whether the deploy's question names the project folder is not checked. |
| C16 | the project lists a joystick, and the gadget held an encoder | JOINED | P873 (#1241). Add: "P867's D8 names this case: a gadget rewired outside spark reads `none recorded`, never the project's parts (walk 3 of P711, row 16)". Walk 3 stopped here (diary, 08:06). The coordinator relays the PO's word that the joystick is connected since 2026-11-17. That word is in no file read here. No card of its own is needed: the box now matches its project, and the general case is the witness line on P873. |

### The D14 row

A read that leaves the firmware running goes before the new walks (brief.md D14). NEW, N3, with B7. P248 (#270) is
a timed read at boot and names download mode. It is not a watch of firmware that keeps running, so it gets one
pointer to N3.

### The page notes (9 notes)

Six notes are also rows: 1 (A7, C7), 2 (C8), 5 (C11), 6 (C9), 7 (C10) and 9 (C7). Notes 3, 4 and 8 are in no rows
file, and they stay rows. Notes 3 and 4 (a label over a pin label, traces past the outline): nobody looked at them
in a browser. Note 8: `flow.py show` lists pick offers when every need is picked (`phase_readers.py:153-154`,
`show_flow.py:39-40`). The offers are true, and an agent uses them to pick again.

## 3. The items and the "Later" lines

| code | item | outcome | where |
| --- | --- | --- | --- |
| I1 | the build replaces a board.tsx that spark wrote | NEW | N1 |
| I2 | `--requirements` removes an entry that no pick explains | NEW | N4 |
| I3 | out of date, with its cause | NEW | N7 |
| I4 | a skipped stage or an unjudged phase shows no tick | NEW | N5 |
| I5 | kept pins, and every moved pin named | NEW | N8a. Its bus-line half is lines to add to P868 (#1235), section 5. |
| I6 | the firmware's pin names against the pin map | NEW | N9 |
| I7 | the order of power, flash and wire after a change | STAYS A ROW | It waits for Q11 of P867's brief, a bench row of the next walk. A card now would guess the order. |
| I8 | a second build erases the list of bench changes | NEW | N2a. Its witness half is a line to add to P873 (#1241). |
| L1 | the bench witnesses in the flow | STAYS A ROW | Later. The line on P873 in section 5 names its first case. |
| L2 | a refused build keeps the last good outputs | STAYS A ROW | It reverses P280 (`kept_files.py:169-179`, `:301-307`, `:322-327`). P816 (#1168) pulls the other way. Q9. |
| L3 | the facts to test as a phase | STAYS A ROW | It is P867's D9 bench step, an open note of P873 (#1241). |
| L4 | one value for an offer and a `next` step | STAYS A ROW | Later. No row of the walks needs it. |
| L5 | the table of phases and the page | JOINED | P873 (#1241), filed. |
| L6 | one kept previous version (P867's D6) | NEW | Inside N1, for board.tsx only. N4 uses the same store for requirements.json. |
| L7 | the bench test as a step (P867's D9) | JOINED | P873 (#1241), its open note. |
| L8 | a plan and a yes before a change (P867's D10) | NEW | N10 |
| L9 | the small "where to get it" view (P867's D12) | NEW | N11 |
| L10 | module images drawn after the real module (P867's D13) | JOINED | P734 (#1005). Add the PO's words: "How nice the module images were, noty just some basic shapes but really drawn by a photo or web serach, so it looks really nice." No vendor file enters the repository. |

How each decision of P867's brief is met: D5 by N1, N2a and N4. D6 by N7 (the cause) and half by N1: the sheet,
`pins.py` and `dist/` are still removed under P280's rule (Q9). D7 by N8a and the lines on P868. D8 by the line
on P873, and N3 notes it. D9 by P873. D10 by N10, and by the yes in N4. D11 in section 6. D12 by N11. D13 by P734.
P829 (#1187) has a "D10" of its own, from P820's plan. In this file "P867's D10" is the plan before a change.

## 4. The cards to file

Each card is a sub-issue of its parent, in Idea. The filer reads the highest P-number first (P873 on 2026-11-17).
Each names the piece of the core it adds or touches (AGENTS.md: one core, many interfaces), so the CLI, the agents
and the page call one piece. Each names the decision that its plan must take.

| code | type | parent | slice | size |
| --- | --- | --- | --- | --- |
| N1 board.tsx replaced | story | P365 #467 | v0.10 The basic journey | S |
| N2a the list of bench changes stays | story | P365 #467 | v0.10 The basic journey | S |
| N3 a console read that leaves the firmware running | story | P365 #467 | v0.10 The basic journey | S |
| N4 the requirements' entries | story | P365 #467 | v0.10 The basic journey | S |
| N5 the true marks | bug | P820 #1173 | Views and editors | S |
| N6 the schematic's net names | spike | P820 #1173 | Views and editors | XS |
| N7 out of date with its cause | story | P820 #1173 | Views and editors | M |
| N8a kept pins, moved pins named | story | P820 #1173 | Views and editors | M |
| N9 the firmware's pin names | story | P820 #1173 | Views and editors | S |
| N10 a plan before a change | story, not refined | P820 #1173 | Views and editors | not sized |
| N11 the buy lines | story | P820 #1173 | Views and editors | S |

### N1: the build leaves alone a board.tsx that spark itself wrote, so a changed design needs a deletion by hand → the build replaces its own board.tsx, keeps one previous version, and still leaves a person's edits alone

### Needed by

The PO, 2026-11-17, #1234's comment. An excerpt: the dots mark words left out, and the rest is exact.

```text
what happens when we ... go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, 'Well, let's add another joystick.' What would happen, actually
```

Walk 3 of P711, row 13. P867's D5 (the command fixes first) and D6 (nothing deleted, one previous version).

### What is true today

- `kept_into` leaves every existing `.tsx` alone and says "delete it to have it regenerated"
  (`scripts/spark/build/kept_files.py:99-101`). It does not know who wrote the file.
- The build record `.spark/build.json` holds the requirements' sha256 and no sha256 of board.tsx
  (`kept_files.py:367-369`, `scripts/spark/build/build_record.py`).
- The "left alone" tests of board.tsx are in `tests/test_check_spine.py` (`:358`, and near `:810`).

### Done when

- A test beside the "left alone" tests: a second build over a board.tsx whose bytes equal the ones the first build
  wrote gives a kept entry `did: "replaced"`, and no `traces differ` entry.
- The same test: the replaced file exists once as the previous version, and a third build keeps only the newest
  previous one.
- A board.tsx with one byte changed by a person still gives `left alone` and, when its traces differ, `traces differ`.
- A project built before this card (no sha256 in the record) gives `left alone`, as today.
- `/spark:build`'s page and `build_board.py --help` say the three cases.

### Notes

- Type: story, size S. Parent: P365 #467. Slice: v0.10 The basic journey. Stands before a walk that changes a design.
- The core: the sha256 of each file spark wrote, in `BuildRecordStore`. The previous copy is written by a Store
  (`PreviousVersionStore`) or by a step of `BuildRecordStore`. `kept_into` gets it as a parameter.
- The plan decides where the previous copy lives. A `*.tsx` copy inside the project may be read by tscircuit.
- It covers board.tsx only. P867's D6 stays half done for the sheet, `pins.py` and `dist/` (Q9).

### N2a: a second build erases the list of bench changes → the sheet keeps the list of changes since the last sheet spark wrote for another design

### Needed by

The PO's words as in N1. Item 8 of `items.md`, and P867's D5 (the erased change list is a command fix that goes
first). No walk row shows the erasure: the discovery's dry change found it.

### What is true today

- `sheet.write` reads `wiring-record.json` (`scripts/spark/breadboard/sheet.py:421`), compares, and writes the new
  record over it (`:438`). A second build of one design then says "Nothing to change on the bench." (`:397`).
- `tests/test_breadboard_record.py:64` pins that sentence for a second build of the same design. The other tests of
  the list are in `tests/test_breadboard_changes.py`.
- `WiringLog` is documented as a Value and has `write()` (`scripts/spark/breadboard/bench_changes.py:103-157`).

### Done when

- If Q10 is answered as recommended: a test in `tests/test_breadboard_record.py`. A design is changed and built
  twice. The second sheet still shows the list of the first rebuild, with the time of the sheet it counts from.
- A test: a build of a third design lists the changes from the second design's sheet only.
- The section's words say "since the sheet spark wrote on <time>". They never say what is on the bench.
- The expectation at `tests/test_breadboard_record.py:64` changes only with the PO's answer to Q10.

### Notes

- Type: story, size S. Parent: P365 #467. Slice: v0.10 The basic journey. Stands before a walk that changes a design.
- The core: `WiringLog` keeps the record of the last sheet of another design. Its `write()` moves to a Store if
  the plan touches it.
- The plan decides when the list is cleared (Q10).
- Not in this card: a baseline that a witness moves. Spark has no witness of the wiring today (section 5, P873).

### N3: after a deploy, reading the console stops the firmware or needs keys → one read of the console that leaves the firmware running, after a bench row names the cause

### Needed by

The PO stopped walk 3 on 2026-11-17:

```text
No, actually, let's start over with a new walk when  we fix the gaps and bugs from these runs
```

Walk 2 of P711, row 7: a walk that checks a must line on the bench needs a read that leaves the firmware running.
D14 of P867's brief (the facilitator's answer on the PO's delegation, confirmed in D20): that read goes before the
new walks, after a bench row says which cause stops `main.py`.

### What is true today

- The deploy's last line tells the person to open mpremote's console and press Ctrl-C, then Ctrl-D
  (`scripts/spark/bench/deploy_image.py:47-48`). Ctrl-D restarts `main.py`.
- `scripts/spark/bench/board_console.py:5-7` says that the port's open itself restarted a XIAO C6. So the cause is
  not known, and the first bench row decides it.
- `ConsoleProbe.console()` reads with DTR and RTS off and takes no seconds today (`board_console.py:97`, `READ_S`
  at `:20`). `FakeConsoleProbe.console()` (`tests/fakes.py:169`) has the same form.
- `live.py` stops the firmware and resets the board (its `--help`).

### Done when

- First, a bench row by the PO: on one board with a firmware that prints a line each second, which step stops the
  lines (the open, Ctrl-C, or Ctrl-D). The row is in the PR's rows file.
- A test with `FakeConsoleProbe`: the read takes N seconds, prints each line, and sends nothing to the board.
  `ConsoleProbe.console()` and the fake get the same seconds parameter.
- A test: a busy port gives could-not-run from the probe's `KIND_BUSY`.
- `--json` carries the lines, the port and the start time with its zone.
- The deploy's last line names this read first.
- A second bench row: the PO presses the button, and the firmware's line appears while the firmware goes on.

### Notes

- Type: story, size S. Parent: P365 #467. Slice: v0.10 The basic journey. It needs the PO's bench twice.
- The core: a `WatchConsole` Operation on `ConsoleProbe`. `main()` only parses and prints.
- Related: P248 #270 (a timed read at boot on the XIAO C6, and naming download mode), P520 #716 (later console
  lines after a deploy) and P870 #1237 (a spike on streaming).
- What the read saw is a witness (P867's D8) only if spark writes it down. That is not in this card.

### N4: `--requirements` keeps an entry that an earlier pick wrote and no pick explains now → it names each such entry and removes it on the person's yes

### Needed by

The PO's words as in N1. Item 2 of `items.md`. P867's D5, D6 and D10.

### What is true today

- `_merge_parts` keeps what no pick explains, "added by hand, or left by a pick since changed", and says it
  (`scripts/spark/design/need_requirements.py:129-161`). It cannot tell the two apart. Its tests are in
  `tests/test_needs.py`.
- `--needs-drop` only notes that requirements.json still lists the part (`scripts/spark/idea/drop_need.py:71`,
  `need_requirements.py:21-39`). A person removes it by hand.
- The loader reads `part` and `name` of a `parts` entry and refuses no other key
  (`scripts/spark/design/loader.py:215-232`).

### Done when

- A test in `tests/test_needs.py`: a need is dropped, then `--requirements --dry-run` names the entry as written
  for a pick that is gone, with a code, and changes no byte.
- With the yes, the entry is gone, an entry that a person wrote stays, and the file before is kept as the one
  previous version.
- An entry in a file written before this card reads as the person's, and stays.
- `flow.py show` reads the requirements as up to date after it. The `--help` and the idea page say it.

### Notes

- Type: story, size S. Parent: P365 #467. Slice: v0.10 The basic journey. Stands before a walk that drops a part.
- The core: `need_requirements.requirements` gets the origin of each entry. The removal is one Operation with a
  dry run, as `DropNeed` is. It uses N1's store for the previous version.
- The plan decides where the origin lives: a key in the entry (the loader allows it today) or a record beside the file.
- The yes is a new effect that the Operation asks for. No removal has one today.

### N5: `flow.py show` ticks a build whose stages were skipped and phases that nobody judged, and blames "an older spark" where no simulation log exists → a tick only for a judged pass, and the reason that is true

### Needed by

The PO's rule, in AGENTS.md and his rules file: "A `could-not-run` or a `skipped` is not a pass". Item 4 of
`items.md`, and walk 3 of P711, row 9.

### What is true today

- `BuildReader` gives the mark of the record's status (`scripts/spark/flow/phase_readers.py:205`). Seen on a
  scratch copy of walk 2's folder: `✓ build: the last build, …: ok, parts: skipped, schematic: skipped, footprint:
  skipped, build: skipped`.
- `BreadboardReader` ticks because the sheet exists and is not stale (`phase_readers.py:215-220`).
  `RequirementsReader` ticks a file with no needs beside it, with "nothing to compare" (`:170`).
- `why_untested` says "a log from an older spark names no image" whenever no run names the image
  (`scripts/spark/firmware/project_image.py:90-93`). It reads `*.log` in `sim/runs/` itself (`:72`). Walk 2's folder
  holds one board log in `sim/runs/board/`, and walk 3's `sim/runs/board/` is empty. Neither holds a simulation log.
- No golden of `flow.py show` exists. Its tests are in `tests/test_flow.py`.

### Done when

- A test in `tests/test_flow.py`: a build record with a skipped stage gives a mark that is not `✓`, in the lines and
  in `--json`.
- A test: a sheet that exists gives the breadboard phase a mark that is not `✓`, and a requirements file with
  nothing to compare gives the same. The words say that nobody judged it.
- A test: a project with no `*.log` in `sim/runs/` gets a reason with no word of an older spark. A project whose
  logs name no image keeps today's sentence.
- `docs/guide/agents/flow.md` names the mark.

### Notes

- Type: bug, size S. Parent: P820 #1173. Slice: Views and editors. It goes before P827 (#1185), whose page shows
  the same marks.
- The core: `BuildReader`, `BreadboardReader`, `RequirementsReader` and `ProjectImage.why_untested`. No new class.
- The plan decides which mark an unjudged phase gets, among the marks at `phase_readers.py:30-31`.

### N6: the schematic names a signal's net `Mcu_pin4` → a finding: can a trace between two pins carry the signal's name?

### Needed by

The PO, 2026-11-17, at the bench, on walk 3's page:

```text
Please also take notes on the page ad what is already abailable and what not and lets find gaps and bugs.
```

Walk 3 of P711, row 8, and page note 2.

### What is true today

- A signal's trace is written pin to pin, and the signal's name is only in a comment
  (`scripts/spark/design/board_sections.py:266`, and walk 3's board.tsx, lines 41 to 55). tscircuit then names the net
  itself. Walk 3's `dist/board/circuit.json` holds `Mcu_pin` names.
- `_TRACE` reads a trace as `from="…" to="…"` only (`scripts/spark/build/kept_files.py:48-49`).

### Done when

A finding with its sources: whether tscircuit accepts a named net between two pins, in which form, and what
`_TRACE` and the netlist check then read. A story follows only on a yes.

### Notes

- Type: spike, size XS. Parent: P820 #1173. Slice: Views and editors. Before P828 (#1186) shows the schematic.

### N7: after a change, the build and the sheet still read `✓` → every phase made from a changed thing reads out of date, with its cause

### Needed by

The PO's words as in N1. P867's D6: "everything made from it reads out of date with its cause and nothing is
deleted". Item 3 of `items.md`.

### What is true today

- Each reader looks one step back. The build is out of date only when the requirements file's sha256 changed
  (`scripts/spark/flow/phase_readers.py:179-185`).
- `ShowFlow` calls each reader alone (`scripts/spark/flow/show_flow.py:63`). A `Phase` is `phase status mark by says
  offers` (`phase_readers.py:39`).
- Seen on a scratch copy of walk 3's folder: `↻ requirements: out of date`, then `✓ build … ok` and
  `✓ breadboard: breadboard.md`.

### Done when

- A test in `tests/test_flow.py`, on a fixture project (not walk 3's folder, whose requirements were written by
  hand): a need is added after the build. `flow.py show --json` gives requirements, build and breadboard as out of
  date, each with a `cause`.
- `cause` is a code from `flow_codes.py` with the phase it names, never English text. The lines render it.
- A phase before the change keeps its mark. No file is deleted.
- `docs/guide/agents/flow.md` and `json.md` name the `cause` key.

### Notes

- Type: story, size M. Parent: P820 #1173. Slice: Views and editors. After N4 and N5.
- The core: the `PhaseReader` interface changes, so that a reader gets the phases before it, and the `Phase` tuple
  gets `cause`. The page (P827) and an agent read the same key.

### N8a: adding a part moves the pins of parts that stay, and nothing says so → a signal on no bus keeps its pin, and every moved pin is named

### Needed by

The PO's words as in N1. P867's D7: spark always names every pin that moves, and a signal on no bus keeps its pin.

### What is true today

- The council reproduced it on the sound demo: a second joystick named JoyTwo moves 2 of 15 signals
  (AUDIO_SHUTDOWN from 6 to 8, JOY_SW from 7 to 47). An added button moves 0 of 15, so it cannot be the fixture. Not run again here.
- The assigner already honours a pin asked by name (`placed_by_name`, `scripts/spark/design/pin_assigner.py:240-260`).
- Nothing reads an earlier `pins.py` back. Only its header is known (`pin_assigner.py:511`, `kept_files.py:318`).

### Done when

- A new fixture of the sound demo: the suite has none today (`tests/data/breadboard/` holds only `amplifier` of
  that design). A test on it with JoyTwo added: AUDIO_SHUTDOWN and JOY_SW have their pins of before.
- A test: when a pin must move, the answer lists `signal, from, to, why` for each one, in the lines and in
  `--json`. The count equals the pins that differ between the two `pins.py` files.
- A test: a first build, with no earlier pin map, places as today.

### Notes

- Type: story, size M. Parent: P820 #1173. Slice: Views and editors. After P868 (#1235).
- The core: a reader of the earlier pin map (new), a `KeptPins` Value that goes into the `placed_by_name` branch,
  and a `MovedPin` Value that N10 reuses.
- The plan's decision is the PO's (Q8): what happens when a kept pin no longer fits a new signal's needs.
- Beside it: P663 (#892, one conflict model) and P665 (#894, the bridge on today's assigner).

### N9: nothing compares the pin names in main.py with the pin map → a name the pin map lacks reads as a problem in the firmware phase

### Needed by

The PO's words as in N1. Item 6 of `items.md`.

### What is true today

- `import_firmware.py` imports every firmware file except `main.py` and `boot.py` (`scripts/import_firmware.py:10-11`).
  Its tests cover `import pins` and `from pins import …` in the other files (`tests/test_import_firmware.py:529`, `:536`).
- `FirmwareReader` gives no status, "because spark cannot judge the firmware"
  (`scripts/spark/flow/phase_readers.py:223-233`).

### Done when

- A test in `tests/test_import_firmware.py` or a file of its own: a `main.py` that names `pins.JOY_SW` with no such
  name in `firmware/pins.py` gives the name and the line. A `main.py` whose names all exist gives nothing.
- A test in `tests/test_flow.py`: the firmware phase reads `problems` for the first case, and no status for the second.
- The check runs nothing of `main.py` and judges no behaviour (AGENTS.md: facts, never behaviour).
- `--json` carries the names. The flow page says what the check cannot see.

### Notes

- Type: story, size S. Parent: P820 #1173. Slice: Views and editors.
- The core: a `CheckPinNames` Operation in `scripts/spark/firmware/`, called by `FirmwareReader`. It is not a
  `Check` of the checks runner.
- The plan decides how the names are read: by `ast`, and which forms count (`import pins as p`, `from pins import X`).

### N10: a change in the middle is applied at once → spark prints a plan (what goes out of date, which wires move, what is lost) and changes nothing until the yes

### Needed by

The PO's words as in N1. P867's D10 ("Plan first", 2026-11-17). P829 (#1187, a click that sends an offer) waits
for this design (P867's D11).

### What is true today

- No command prints such a plan. Two of its lists have a source to come: N7 (out of date) and N8a (the moved
  pins). The wires come from the sheet's change list (N2a).
- "What is lost" has no source. N1 and N4 say what they replace. What a refused build removes is P280's rule, and
  the card that settles Q9 must give that list.

### Done when

One sentence, because it is far: a dry run of one change on a fixture prints the lists from N7, N2a and N8a and
what is lost, changes no byte, and the same run with the yes applies it. Refine when those are Done.

### Notes

- Type: story, not refined. Parent: P820 #1173. Slice: Views and editors. After N2a, N7, N8a and Q9's answer.
- The core: a `PlanChange` Operation that composes the results. It adds no logic of its own.

### N11: where to get a part is on no view → buy lines from what the records hold: the maker, the product code, and whether the drawer has it

### Needed by

The PO, 2026-11-17, at the bench (page-notes.md):

```text
the goal, the needs, the parts and modules and boards and the schema and where to get parts from and where else they are available, which ones to validate, which oneds to replace
```

P867's D12: a small view now, from the records only, with no price, no stock and no other shop.

### What is true today

- The maker is `vendor` and the code is `sku`. In the repository's `parts/`, 2 of 8 records hold `vendor` and 1 of 8
  holds `sku` (a text search). The council counted the PO's store: 18 of 18 hold the keys, 3 with `vendor` null,
  which are shop records whose `sku` is the shop's code. The store was not counted again here.
- No record has a link of its own. The URLs in `sources` and `documents[].url` are datasheets, so the link reads
  `null` today.
- `scripts/spark/sourcing/drawer.py:183-229` already reads `sku` and `vendor`.

### Done when

- A test: for a project with one owned pick and one pick to get, the Operation gives one row per pick with
  `maker`, `code`, `link` and `in_drawer`. A value the record lacks is `null`. A datasheet URL is never the link.
- `parts.py` prints the rows, and `--json` carries them. No request leaves the machine.
- The page (after P827) shows the same rows from the same Operation.

### Notes

- Type: story, size S. Parent: P820 #1173. Slice: Views and editors. P820's own D10 (shops after the MVP) stays.
- The core: a `ListBuyLines` Operation, in the family of `ListParts`, `ListDrawer` and `ShowPart`. It reuses the
  reader in `drawer.py`.
- Beside it: P309 (#375, buy lines name no shop) and P209 (#178, one way to a store record). The shop search stays out.

## 5. The lines to add to open cards

### Proposed by P869's triage, for the PO's refinement

P865, P864 and P868 each say "To refine with the PO". The lines below are proposals for that refinement. They are
not Done-when lines yet.

**P865 (#1231), the look reads any board.** Rows B3, B5, B6, C14. True today: with one board on USB,
`LookService.run` takes it and reads at once (`scripts/spark/bench/board_look.py:456-460`). `mpremote devs` lists a
USB serial without opening the port (`board_look.py:106`, `:154-163`). The store keys a deploy by the board's MAC
(`scripts/spark/records/deploy_record_store.py:73`). Whether the USB serial equals the MAC on the ESP32-S3 is not
checked. If it does not, the check needs a read. Proposed:

- A test with a fake finder and a fake reader: the store names another project for the board that is listed. The
  look stops with exit 2, names the port, says that a read restarts the board, and `read` is never called.
  `--port` goes on.
- A test: a board the store names for this project is read with no question.
- A test for B5, with a fake port that comes back late: the next read waits for the port or names the restart as
  the cause. It never ends on "No serial data received" alone.
- A test for C14: the look and the deploy that follows make one read between them, or the look says how many
  restarts come.
- The last-deploy line of B6, as in section 2.
- The core: a `BoardIdentity` Strategy that is swapped into `LookService`, and shared by `LookService`,
  `DeployService` and `ReachBoard`.

**P864 (#1230), the amplifier's own speaker socket.** Rows A6, A9, C2. It is not XS: it needs a record key, a
change where the gap is found (`power_rails`, called at `scripts/spark/design/need_requirements.py:230`), and a
change of the board emitter, which stops on a net with one member. Proposed:

- The record says that SPK_P and SPK_N end in the module's own 2-pin socket, with the drawing as the source (page
  1, its sha256) and `verified: false`. P735 (#1010) is in Design: use its key for a connector if it has one.
- A fixture of the board, the DFR0954 and a speaker with no record: `parts.py --requirements` prints no "nothing
  listed receives it" line (`write_requirements.py:26`), and `/spark:build` exits 0 with no `speaker-terminal`.
- The sheet tells the person to plug the speaker into the module's socket, and never to put a supply there.

**P868 (#1235), a pin on a bus line.** Row C12, and the bus-line half of item I5. True today: the loader refuses it
for every bus (`scripts/spark/design/loader.py:381-384`). The reason given there is a second part on the same bus.
Proposed:

- A test with the game box's pins (BCLK D12, LRC D11, DIN D10): the build runs, and `pins.py` names the three with
  the reason "asked for by name".
- A test: a pin that the board cannot route the bus to is refused, and the refusal names the pin and the bus.
- A test: two parts on one bus with pins that split the bus are still refused, with both named.
- From P867's D7: when an added part would move a line of a bus, the build stops with a question (exit 2,
  `needs_reply`) that names each line. The council's case: an added I2C part moves 6 of 15 signals on the sound
  demo, three of them I2S lines. P663 (#892) holds the conflict model for that question.
- The core: the refusal moves from the loader to the assigner's bus placement, which knows what the board routes.

### Other lines

**P248 (#270), a bounded console read.** One pointer: "N3 is the read of a firmware that keeps running. This card
stays the timed read at boot and the naming of download mode. Both use `ConsoleProbe`."

**P873 (#1241), the table and the page.** Add: the C16 line of section 2. Add also: "the witness of the wiring
has no source today. A deploy record holds the project, the time and the verdict of one board's MAC, and nothing
of the sheet. Walk 3 deployed to a box wired for another project. Whether wiring comes before flashing is Q11 of
P867's brief. The bench step (D9) is where a witness of the wiring is written (D8)."

**P816 (#1168), an unfinished build leaves the earlier dist/.** Its Done-when allows two ways: removed and said,
or "kept and named as an earlier build's". Add: "P867's D6 (nothing is deleted) picks the second way".

**P413 (#539), P735 (#1010), P340 (#434), P734 (#1005), P520 (#716):** the lines in sections 2 and 3. For P520:
"its watch step calls N3's `WatchConsole`".

P871 (#1238, the board doctor, a spike) stays where it is. It concerns only a walk on the game box.

## 6. The order

**(a) What stands before the new walks.** Six cards, by the walk each one stops:

| card | which walk it stops | what it stands on |
| --- | --- | --- |
| P865 (#1231) the look names the board | every walk with a board: bench safety | a walk row: walk 2, row 3 |
| P864 (#1230) the speaker socket | the sound walk, on any board | a walk row: walk 3, row 2. A workaround exists: a separate speaker terminal. |
| N1 board.tsx replaced | a walk that changes its design | rework on the PO's D5. Walk 3, row 13 shows it. |
| N2a the list of bench changes | a walk that changes its design | rework on the PO's D5. No walk row shows it. |
| N4 the requirements' entries | a walk that drops a part | rework on the PO's D5. No walk row shows it. |
| N3 the console read | a walk that checks a must line on the bench | D14, and walk 2, row 7 |

Only P865 stopped a walk with no way around. The other five stand on the PO's words "when we fix the gaps and
bugs from these runs" and on D5 and D14.

P868 (#1235, a pin on a bus line) stops no basic walk. It stops only a walk that describes wiring that exists,
which is the sound walk on the game box. It follows the six, and N8a follows it.

Ready holds 4 cards of spark's lane. The recommended top of Ready:

| place | card | why here |
| --- | --- | --- |
| 1 | P865 (#1231) | Bench safety. Every walk with a board starts with the look, and it restarted another session's board. |
| 2 | N1 | The first of D5's command fixes, small, and it needs no bench. |
| 3 | P827 (#1185) | The PO's D11 of P867. N5 (the true marks) goes just before it. |
| 4 | P828 (#1186) | The PO's D11 of P867. N6 (the spike) goes before it. |

Next, each entering on top when a place frees: N3 (after its first bench row), N2a, N4, P864, then P868.
N7 to N11 follow P828. P862 (#1228) and P863 (#1229) stop no walk and stay in Idea.

**(b) Ready today** holds P711 (#960), P827 (#1185), P828 (#1186) and P829 (#1187). Both moves below are the
PO's to order (brief.md D11: "P829's place in Ready is his to order"). They are recommendations, in Q1.

- P829 (#1187) out, to Idea, with "Waiting on: N10".
- P711 (#960, the walks) out, to Idea, with "Waiting on" the six cards of (a). It cannot be pulled before them.

**(c) Questions that only the PO can answer.** Work goes on with the recommended answer, except where a move is his.

- Q1. Ready: do P711 and P829 leave Ready, and do P827 and P828 keep places 3 and 4 under two blockers?
  Recommended: yes to both. Nothing is moved before his word.
- Q2. May the 11 cards be filed as written, and the open cards get the lines of section 5? Recommended: yes.
- Q3. The slices. Recommended: "v0.10 The basic journey" for the fixes to a command (N1, N2a, N4), and "Views and
  editors", where P867 and P873 sit, for the flow's new behaviour (N5 to N11). No slice is widened (brief.md D15).
- Q4. Is a deploy by spark a witness that the sheet before it was wired? Recommended: no. The deploy record says
  nothing of the sheet, and walk 3 deployed to a box wired for another project. The witness goes to P873.
- Q5. Row C10: do the flow's commands keep `${CLAUDE_PLUGIN_ROOT}`? Recommended: yes for now.
- Q6. N3 needs his bench twice, about ten minutes each: the row that names the cause, then the watch itself.
  Recommended: both at the start of the first new walk's session.
- Q7. A start step for every walk, which does not exist today: free the earlier walks' holds with `/spark:drawer`
  and say which. Recommended: yes, as a line on P365 (#467). It does not free a hold of a project that is no walk.
- Q8. N8a: a kept pin no longer fits a new signal's needs. Recommended: move the fewest pins and name each (D7).
- Q9. P280's rule removes the sheet, `pins.py` and `dist/` of an earlier build, and P867's D6 says nothing is
  deleted. Recommended: D6 stands. P816 (#1168) takes its "kept and named" way, and P280's rule is decided with L2
  when P873 is refined. Until then N1 covers board.tsx only.
- Q10. N2a: when is the list of bench changes cleared? Recommended: the sheet keeps the last list with the time
  of the sheet it counts from, until a build of another design replaces it. A second build of one design then no
  longer says "Nothing to change on the bench.", so the test at `tests/test_breadboard_record.py:64` changes with
  this answer and not before.

## 7. Not checked, and where the code stands against a report

- No bench claim: which step stops `main.py`, the restarts per read, download mode after a look, and whether the
  USB serial is the MAC.
- The council's counts were not run again: 2 of 15 and 6 of 15 moved signals, and 18 of 18 store records.
- The bodies of P663 (#892), P665 (#894), P309 (#375), P209 (#178), P340 (#434),
  P734 (#1005), P735 (#1010), P827, P828 and P829. Their titles and states were read. Of P413 (#539) only the
  caveat lines were read.
- Whether the deploy's question names the project folder (C15), and why the tally gave three answers (B2, C3).
- Page notes 3 and 4 in a browser. The PO's word on the joystick (C16) is relayed, and in no file read here.
- Against the reports: `sheet.py:418` is the line that names the record's path, and the comment is `:419`. In
  `parts/`, `sku` is in 1 of 8 records and `vendor` in 2 of 8, not both in 2. The `placed_by_name` code is at
  `pin_assigner.py:240-260` inside the range the report gave. `deploy_record_store.py` is in
  `scripts/spark/records/`. The breadboard reader's tick is at `phase_readers.py:215-220`.
