# P869: the triage of P711's three walks and P867's items

> 32 walk rows, one more row (D14), 8 proposed items and 10 "Later" lines are triaged here. 16 rows join open cards,
> 5 become new cards, 2 are dropped and 9 stay rows. There are 11 new cards, written out ready to file. Seven cards
> block a new walk. Two of them go on top of Ready now, above P827 and P828.

The card is P869 ([#1236](https://github.com/xmejkal/spark/issues/1236)), under the walks epic P365 (#467). P480 (#658,
`2026-11-01-p480-walk3-council/`) and P510 (#705, `2026-11-01-p510-walk4-council/`) did the same for earlier walks.
This file is one author's triage, on Fable 5.2, on 2026-11-17 (Europe/Prague). No refuter read it yet. Nothing is
filed, moved or commented: section 4 is filing text for the PO's yes.

## 1. What was read, and how

- The rows: `spark-walks/p711-identify-amp/rows.md` (9 rows counted), `spark-walks/p711-walk4-button-led/rows.md`
  (7 rows counted) and `spark-walks/p711-sound-demo/rows.md` (16 rows counted), 32 in all. Also the 9 notes of
  `spark-walks/p711-sound-demo/page-notes.md`.
- `docs/discovery/2026-11-17-p867-journey-redefined/items.md` (8 items without the spike, and two "Later" bullets
  with 4 and 6 lines) and `brief.md` (D5 to D14, D21).
- The open cards #1228, #1229, #1230, #1231, #1235, #1238, #1241, and six `gh issue list --search` runs.
- The code at `364bb059`. Each claim below names its `file:line`. A claim with no line says "not checked".
- `flow.py show` ran on scratch copies of two walk folders, with `SPARK_HOME` on a scratch copy of the store. No
  board was touched, no simulation ran, and no build ran.

The bar is `scrum/VISION.md` and AGENTS.md: does the card move a basic project closer to a breadboard with working
firmware? Codes in this file: A is walk 1 (the amplifier's picture), B is walk 2 (the button and the LED), C is
walk 3 (the sound demo), I is an item of `items.md`, L is a "Later" line, N is a new card.

## 2. The rows

### Walk 1, the DFR0954 amplifier (9 rows)

| row | what | outcome | where, and the line to add |
| --- | --- | --- | --- |
| A1 | `/spark:research` ends at reuse and looks for no picture | JOINED | P734 (#1005, each module drawn). No line: its rows name it. |
| A2 | `parts.py --show` prints no `body_mm` | JOINED | P862 (#1228). Checked: `scripts/spark/sourcing/show_part.py` holds no `body_mm`. No line. |
| A3 | the record keeps no product picture | JOINED | P734 (#1005). Add D13's words (section 3, line L10). |
| A4 | `drive / audio amplifier` offers no amplifier | JOINED | P863 (#1229). No line. |
| A5 | every walk board is held by older walk projects | STAYS A ROW | With C1. A hold is freed by hand today, and only walks that share one board hit it. The walks' start list frees the earlier walk's holds. |
| A6 | does the DFR0954 carry its own speaker socket? | JOINED | P864 (#1230). The answer (the kept drawing, page 1) is that card's evidence. |
| A7 | no breadboard picture for a module with a full record | JOINED | P734 (#1005). No line. |
| A8 | the sheet asks for a supply on the amplifier's outputs | DROPPED | Fixed by P860 (#1226, closed, PR #1232). Not run again here. |
| A9 | the speaker terminal is a separate part "to get" | JOINED | P864 (#1230), with A6. |

### Walk 2, the button and the LED (7 rows)

| row | what | outcome | where, and the line to add |
| --- | --- | --- | --- |
| B1 | the pick names the joystick as the other choice for a button | STAYS A ROW | `needs.py:296-310` names the first owned, free part with a Wokwi model whose words match. It is a ranking wish. No walk stopped on it. |
| B2 | the tally says "its cost was not counted" | STAYS A ROW | With C3. `run_cost.py:263-265` prints it when no count reached the line. Why three answers came in one session is not checked. The tally does not move a project to a breadboard. |
| B3 | the look reads a board of another project and restarts it | JOINED | P865 (#1231). Section 5 gives its Done-when lines. |
| B4 | spark cannot say how many free Wokwi minutes are left | JOINED | P413 (#539, a count of the Wokwi minutes). Add: "the total is shown against the free plan's 50 minutes per 30 days, before a run (walk 2 of P711, row 4)". Its body was not read. |
| B5 | reads in a row flip between failing and passing | JOINED | P865 (#1231). Every read restarts the board (`board_look.py:54`, `:201`). |
| B6 | "spark's last deploy here: walk4" reads as the box's state | JOINED | P865 (#1231). Add: "the last-deploy line (`board_look.py:392`) says it is spark's own record and that a flash outside spark is not seen (D8: a witness has a source and a time)". |
| B7 | no way to watch the firmware's lines while it runs | NEW | N3, with the D14 row. |

### Walk 3, the sound demo on the game box (16 rows)

| row | what | outcome | where, and the line to add |
| --- | --- | --- | --- |
| C1 | two walks cannot both hold one walk board | STAYS A ROW | With A5. |
| C2 | the record names no speaker socket, and the build stops | JOINED | P864 (#1230), a blocker. Section 5. |
| C3 | the tally gave three different answers | STAYS A ROW | With B2. |
| C4 | a supply on SPK_P and SPK_N again | DROPPED | Fixed by P860 (#1226, closed). |
| C5 | a button's ground goes to "the row of Max98357aDfr0954 GND" | STAYS A ROW | The wiring is right: the ends of a point meet in the row of one end (`wiring_steps.py:52`). It is a wording choice. Look again when P828 (#1186) puts the steps on the page. |
| C6 | "Disconnect the SPEAKER_N supply." for a wire nobody wired | NEW | N2. The change list compares with the last build, not with what was wired. |
| C7 | the page shows only three tabs | JOINED | P827 (#1185), P828 (#1186) and P873 (#1241). No line. |
| C8 | the schematic names nets `Mcu_pin4` and `Mcu_pin20` | NEW | N6. |
| C9 | "a log from an older spark names no image" with no log at all | NEW | N5. |
| C10 | the commands start with `${CLAUDE_PLUGIN_ROOT}` | STAYS A ROW | Written on purpose (`flow_codes.py:47-49`). A person reaches the commands through Claude or the page (P827). It is a question for the PO (Q5). |
| C11 | "Tell Claude your goal in the chat" though the brief holds the goal | STAYS A ROW | P820's plan holds "a stored goal" after its MVP. Seen again in this triage's run. |
| C12 | a pin on an I2S bus line is refused | JOINED | P868 (#1235), a blocker. Section 5. |
| C13 | "traces differ" for a board.tsx that spark wrote | NEW | N1, with item I1. |
| C14 | BOOT and RESET twice: once for the look, once for the deploy | JOINED | P865 (#1231). Section 5. |
| C15 | the deploy line of another walk came from the terminal's history | STAYS A ROW | The line was the person's own history. Whether the deploy's question names the project folder is not checked. |
| C16 | the project lists a joystick, and the gadget holds an encoder | JOINED | P873 (#1241). Add: "the D8 row names this case: a gadget rewired outside spark reads `none recorded`, never the project's parts (walk 3 of P711, row 16)". |

### The D14 row

A read that leaves the firmware running goes before the new walks (brief.md D14). NEW, N3, with B7. The candidate
cause is real text: `scripts/spark/bench/deploy_image.py:47-48` tells the person to "press Ctrl-C, then Ctrl-D".
Whether Ctrl-C is what stops `main.py` needs a bench row. It is not checked here.

### The page notes (9 notes, each also a row above)

Notes 1 and 9 join P734, P828 and P827. Note 2 is N6. Note 6 is N5. Notes 5 and 7 are C11 and C10. Notes 3 and 4
(a label over a pin label, traces past the outline) stay rows: nobody looked at them in a browser. Note 8 stays a
row: `flow.py show` lists pick offers when every need is picked (`phase_readers.py:153`, `show_flow.py:39-40`).
The offers are true, and an agent uses them to pick again.

## 3. The items and the "Later" lines

| code | item | outcome | where |
| --- | --- | --- | --- |
| I1 | the build replaces a board.tsx that spark wrote | NEW | N1 |
| I2 | `--requirements` removes an entry that no pick explains | NEW | N4 |
| I3 | out of date, with its cause | NEW | N7 |
| I4 | a skipped stage shows no tick | NEW | N5 |
| I5 | kept pins, and every moved pin named | NEW | N8, after P868 (#1235) |
| I6 | the firmware's pin names against the pin map | NEW | N9 |
| I7 | the order of power, flash and wire after a change | STAYS A ROW | It waits for Q11, a bench row of the next walk. A card now would guess the order. |
| I8 | a second build erases the list of bench changes | NEW | N2 |
| L1 | the bench witnesses in the flow | STAYS A ROW | Later. N2 and N3 are its first two cases. |
| L2 | a refused build keeps the last good outputs | STAYS A ROW | It reverses P280 (`kept_files.py:301-307`, not read here). P873 (#1241) holds it as the PO's question. |
| L3 | the facts to test as a phase | STAYS A ROW | It is D9's bench step, an open note of P873 (#1241). |
| L4 | one value for an offer and a `next` step | STAYS A ROW | Later. No row of the walks needs it. |
| L5 | the table of phases and the page | JOINED | P873 (#1241), filed. |
| L6 | one kept previous version (D6) | NEW | Inside N1, as the `PreviousVersion` piece. N4 uses it again. |
| L7 | the bench test as a step (D9) | JOINED | P873 (#1241), its open note. |
| L8 | a plan and a yes before a change (D10) | NEW | N10 |
| L9 | the small "where to get it" view (D12) | NEW | N11 |
| L10 | module images drawn after the real module (D13) | JOINED | P734 (#1005). Add the PO's words: "How nice the module images were, noty just some basic shapes but really drawn by a photo or web serach, so it looks really nice." No vendor file enters the repository. P735 (#1010) is the records' side. |

How each PO decision is met: D5 by N1, N2 and N4. D6 by N7 (the cause) and N1 (one previous version). D7 by N8 and
P868. D8 by N2 and N3. D9 by P873. D10 by N10, and by the yes in N4. D11 in section 6. D12 by N11. D13 by P734.

## 4. The new cards, ready to file

Each card is a sub-issue of its parent, in Idea, with the slice named in its Notes. The filer reads the highest
P-number first (P873 on 2026-11-17). Each names the piece of the core it adds or touches (AGENTS.md: one core, many
interfaces), so the CLI, the agents and the page call one piece.

### N1: the build leaves alone a board.tsx that spark itself wrote, so a changed design needs a deletion by hand → the build replaces its own board.tsx, keeps one previous version, and still leaves a person's edits alone

### Needed by

The PO, 2026-11-17, #1234's comment:

```text
what happens when we ... go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, 'Well, let's add another joystick.' What would happen, actually
```

Walk 3 of P711, row 13. The PO's decisions D5 (the command fixes first) and D6 (nothing deleted, one previous version).

### What is true today

- `kept_into` leaves every existing `.tsx` alone and says "delete it to have it regenerated"
  (`scripts/spark/build/kept_files.py:99-101`). It does not know who wrote the file.
- The build record `.spark/build.json` holds the requirements' sha256 and no sha256 of board.tsx
  (`kept_files.py:367-369`).

### Done when

- `tests/test_kept_files.py` (or the module's test file): a second build over a board.tsx whose bytes equal the
  ones the first build wrote gives a kept entry `did: "replaced"`, and no `traces differ` entry.
- The same test: the replaced file exists once as the previous version, and a third build keeps only the newest
  previous one.
- A board.tsx with one byte changed by a person still gives `left alone` and, when its traces differ, `traces differ`.
- A project built before this card (no sha256 in the record) gives `left alone`, as today.
- `/spark:build`'s page and `build_board.py --help` say the three cases.

### Notes

- Type: story, size S. Parent: P365 #467. Slice: v0.10 The basic journey. Blocks a new walk.
- The core: a `PreviousVersion` Value (keeps one earlier copy of a file spark replaces) and the sha256 of each file
  spark wrote in `BuildRecordStore`. N4 uses `PreviousVersion` again. Where the copy lives is the plan's choice.

### N2: a second build erases the list of bench changes, and the list assumes the last sheet was wired → the list is made against the last sheet a witness says was wired, or says that none is recorded

### Needed by

The PO's words as in N1. His decision D8: the bench is state only through a witness that spark wrote, or "none
recorded". Walk 3 of P711, row 6, and item 8 of `items.md`.

### What is true today

- `sheet.write` compares the new steps with `wiring-record.json` and then writes the new record over it
  (`scripts/spark/breadboard/sheet.py:418`, `:438`). A second build of one design then says "Nothing to change on
  the bench." (`sheet.py:397`).
- Nothing records that a person wired a sheet. Walk 3 read "Disconnect the SPEAKER_N supply." for a wire that the
  old sheet asked for and nobody had put in.

### Done when

- A test in `tests/test_breadboard.py`: a design is changed and built twice. The second sheet still lists the
  changes of the first rebuild.
- A test: with no witness, the section says that spark has no record of what is wired, and gives the whole wiring.
  It never says "Nothing to change on the bench." for a change no witness covers.
- A test: after a witness for sheet X, a build lists the changes from X only.
- The breadboard page says what counts as a witness.

### Notes

- Type: story, size S to M. Parent: P365 #467. Slice: v0.10 The basic journey. Blocks a walk that changes a design.
- The core: `bench_changes.WiringLog` gets a baseline that only a witness moves. The first witness is a deploy
  that spark made after the sheet (the deploy record exists, `deploy_record_store`). The PO's own word "wired" is
  a later kind (D8). Open for the plan: whether a deploy is a fair witness of the wiring (Q4).

### N3: the deploy's own line stops the firmware, so nobody can watch a must line on the bench → one read of the console that leaves the firmware running

### Needed by

The PO stopped walk 3 on 2026-11-17:

```text
No, actually, let's start over with a new walk when  we fix the gaps and bugs from these runs
```

Walk 2 of P711, row 7. D14 of P867's brief (the facilitator's answer on the PO's delegation, confirmed in D20): a
read that leaves the firmware running goes before the new walks, after a bench row names the cause.

### What is true today

- The deploy's last line tells the person to open mpremote's console and "press Ctrl-C, then Ctrl-D"
  (`scripts/spark/bench/deploy_image.py:47-48`, said at `:169` and `:241`). That this is what stops `main.py` is
  a candidate. No bench row proves it.
- `ConsoleProbe` already opens the port with DTR and RTS off, so the open chooses no boot mode, and reads 2 s
  (`scripts/spark/bench/board_console.py:1-8`, `:20`). The deploy and the doctor use it. No command gives it to a person.
- `live.py` stops the firmware and resets the board (its `--help`).

### Done when

- First, a bench row by the PO: on one board with a firmware that prints a line each second, which step stops the
  lines (the open, Ctrl-C, or Ctrl-D). The row is in the PR's rows file.
- A test with a fake port: the watch reads N seconds, prints each line, writes nothing to the port and sends no
  reset. A busy port gives could-not-run with the code the probe has (`EXIT_PORT_BUSY`).
- `--json` carries the lines, the port, the start time with its zone and `"wrote_to_board": false`.
- The deploy's last line names the watch command first. The golden of the deploy's lines changes only there.
- A bench row: the PO presses the button, and the firmware's line appears while the firmware goes on.

### Notes

- Type: story, size S. Parent: P365 #467. Slice: v0.10 The basic journey. Blocks a new walk (D14).
- The core: a `WatchConsole` Operation on `ConsoleProbe`. `main()` only parses and prints. P870 (#1237, a spike on
  streaming) can reuse it. P520 (#716) asks for "later console lines" after a deploy: add to it "its watch step
  calls N3's Operation".
- What the watch saw is a witness (D8) only if spark writes it down. That is not in this card.

### N4: `--requirements` keeps an entry that an earlier pick wrote and no pick explains now → it names each such entry and removes it on the person's yes

### Needed by

The PO's words as in N1. Item 2 of `items.md`. D5, D6 and D10.

### What is true today

- `_merge_parts` keeps what no pick explains, "added by hand, or left by a pick since changed", and says it
  (`scripts/spark/design/need_requirements.py:129-161`). It cannot tell the two apart.
- `--needs-drop` only notes that requirements.json still lists the part (`scripts/spark/idea/drop_need.py:71`,
  `need_requirements.py:21-39`). A person removes it by hand.

### Done when

- A test in the requirements' test file: a need is dropped, then `--requirements --dry-run` names the entry as
  "written for a pick that is gone" and changes no byte.
- With the yes, the entry is gone, an entry that a person wrote stays, and the file before is kept as the one
  previous version.
- An entry in a file written before this card reads as the person's, and stays.
- `flow.py show` reads the requirements as up to date after it. The `--help` and the idea page say it.

### Notes

- Type: story, size S. Parent: P365 #467. Slice: v0.10 The basic journey. Blocks a walk that drops a part.
- The core: `need_requirements.requirements` gets the origin of each entry (which pick wrote it). The removal is
  one Operation with a dry run, as `DropNeed` is. It uses N1's `PreviousVersion`.

### N5: `flow.py show` ticks a build whose stages were all skipped, and blames "an older spark" where no log exists → a tick only for a judged pass, and the reason that is true

### Needed by

The PO's rule, AGENTS.md and his rules file: "A `could-not-run` or a `skipped` is not a pass". Item 4 of
`items.md`, and walk 3 of P711, row 9.

### What is true today

- `BuildReader` gives the mark of the record's status (`scripts/spark/flow/phase_readers.py:205`). Seen on a
  scratch copy of walk 2's folder: `✓ build: the last build, …: ok, parts: skipped, schematic: skipped, footprint:
  skipped, build: skipped`.
- `why_untested` says "a log from an older spark names no image" whenever no run names the image, also with no
  log at all (`scripts/spark/firmware/project_image.py:90-93`). Seen on both scratch copies.

### Done when

- A test in `tests/test_flow.py` (or the readers' test file): a build record with a skipped stage gives a mark that
  is not `✓`, in the lines and in `--json`.
- A test: a project with no file in `sim/runs/` gets a reason with no word of an older spark. A project whose logs
  name no image keeps today's sentence.
- The golden of `flow.py show` changes only in these two lines. `docs/guide/agents/flow.md` names the mark.

### Notes

- Type: bug, size XS. Parent: P820 #1173. Slice: Views and editors. It goes before P827 (#1185), whose page shows
  the same marks.
- The core: `BuildReader` and `ProjectImage.why_untested`. No new class. Which mark a skipped build gets
  (`◐` or `?`) is the plan's choice among the marks at `phase_readers.py:30-31`.

### N6: the schematic names a signal's net `Mcu_pin4` → the net carries the signal's name from the pin map

### Needed by

The PO, 2026-11-17, at the bench, on walk 3's page:

```text
Please also take notes on the page ad what is already abailable and what not and lets find gaps and bugs.
```

Walk 3 of P711, row 8, and page note 2.

### What is true today

- A signal's trace is written pin to pin, and the signal's name is only in a comment
  (`scripts/spark/design/board_sections.py:266`, and walk 3's board.tsx, lines 41 to 55). tscircuit then names the net
  itself. The scratch copy's `dist/board/circuit.json` holds `Mcu_pin` names.

### Done when

- A test of the board emitter: after a build of the button-and-LED fixture, no net name in `circuit.json` matches
  `Mcu_pin\d+`, and each signal of `pins.py` is the name of one net.
- The checks that read traces (`kept_files._compare_traces`, the netlist check) pass unchanged on the fixtures.
- A spike line first, in the PR: which trace form tscircuit accepts for a named net between two pins.

### Notes

- Type: story, size S. Parent: P820 #1173. Slice: Views and editors. Before P828 (#1186) shows the schematic.
- The core: `board_sections.signal_lines`. Not a blocker of a walk.

### N7: after a change, the build and the sheet still read `✓` → every phase made from a changed thing reads out of date, with its cause

### Needed by

The PO's words as in N1. His decision D6: "everything made from it reads out of date with its cause and nothing is
deleted". Item 3 of `items.md`.

### What is true today

- Each reader looks one step back. The build is out of date only when the requirements file's sha256 changed
  (`scripts/spark/flow/phase_readers.py:179-185`).
- Seen on a scratch copy of walk 3's folder: `↻ requirements: out of date`, then `✓ build … ok` and
  `✓ breadboard: breadboard.md`.

### Done when

- A test on a fixture project (not walk 3's folder, whose requirements were written by hand): a need is added
  after the build. `flow.py show --json` gives requirements, build and breadboard as out of date, each with a
  `cause` that names the changed thing.
- The lines show the cause after the phase. A phase before the change keeps its mark. No file is deleted.
- `docs/guide/agents/flow.md` and `json.md` name the `cause` key.

### Notes

- Type: story, size M. Parent: P820 #1173. Slice: see Q3. After N4 and N5.
- The core: a `StaleCause` Value that a `PhaseReader` hands to the phases after it. The page (P827) and an agent
  read the same key. P873 (#1241) writes the rule as "today" once this is Done.

### N8: adding a part moves the pins of the parts that stay, and nothing says so → a signal on no bus keeps its pin, and every moved pin is named

### Needed by

The PO's words as in N1. His decision D7: spark always names every pin that moves, a signal on no bus keeps its
pin, and a bus line is asked until P868 (#1235).

### What is true today

- The discovery measured it on a copy of the sound demo: 6 of 15 kept signals moved with one added I2C part
  (`items.md`, ★C4, simulated, one board model). Not run again in this triage, and the assigner was not read.

### Done when

- A test on a fixture: a part on no bus is added. Each earlier signal on no bus has its pin of before in `pins.py`.
- A test: when a pin must move, the build's answer lists `signal, from, to, why` for each one, in the lines and in
  `--json`, and the count equals the pins that differ between the two `pins.py` files.
- A bus line whose pin would move stops with a question (exit 2, `needs_reply`), until P868 is Done.

### Notes

- Type: story, size M. Parent: P820 #1173. Slice: see Q3. After P868 (#1235). Refine the first line of "What is true
  today" in the code before the plan.
- The core: the earlier pin map as an input of the assigner (a `KeptPins` Value), and one `MovedPin` result that
  N10's plan reuses.

### N9: nothing compares the pin names in main.py with the pin map → a name the pin map lacks reads as a problem in the firmware phase

### Needed by

The PO's words as in N1. Item 6 of `items.md`.

### What is true today

- `import_firmware.py` imports every firmware file except `main.py` and `boot.py` (`scripts/import_firmware.py:10-11`).
- `FirmwareReader` gives no status, "because spark cannot judge the firmware"
  (`scripts/spark/flow/phase_readers.py:223-233`).

### Done when

- A test: a `main.py` that names `pins.JOY_SW` with no such name in `firmware/pins.py` gives the firmware phase
  `problems`, with the name and the line. A `main.py` whose names all exist gives no status, as today.
- The check runs nothing of `main.py` and judges no behaviour (AGENTS.md: facts, never behaviour).
- `--json` carries the names. The flow page says what the check cannot see (a name built at run time).

### Notes

- Type: story, size S. Parent: P820 #1173. Slice: see Q3.
- The core: a `PinNamesCheck` Operation that reads two files. `FirmwareReader` and `import_firmware.py` call it.

### N10: a change in the middle is applied at once → spark prints a plan (what goes out of date, which wires move, what is lost) and changes nothing until the yes

### Needed by

The PO's words as in N1. His decision D10 ("Plan first", 2026-11-17). P829 (#1187, a click that sends an offer)
waits for this design (D11).

### What is true today

- No command prints such a plan. Its three parts have no source yet: N7 (out of date), N2 (the wires) and N8
  (the moved pins). P873 (#1241) notes that D10 has no card.

### Done when

One sentence, because it is far: a dry run of one change on a fixture prints the three lists from N7, N2 and N8,
changes no byte, and the same run with the yes applies it. Refine when those three are Done.

### Notes

- Type: story, not refined. Parent: P820 #1173. Slice: see Q3. After N2, N7 and N8.
- The core: a `PlanChange` Operation that composes the three results. It adds no logic of its own.

### N11: where to get a part is on no view → a small view of what the records hold: the maker, the product code, the link, and whether the drawer has it

### Needed by

The PO, 2026-11-17, at the bench (page-notes.md):

```text
the goal, the needs, the parts and modules and boards and the schema and where to get parts from and where else they are available, which ones to validate, which oneds to replace
```

His decision D12: a small view now, from the records only, with no price, no stock and no other shop.

### What is true today

- The page-notes table says "nowhere" for where to get a part. The brief counted `vendor` and `sku` in the store's
  catalog (D12). The record keys were not read in this triage.

### Done when

- A test: for a project with one owned pick and one pick to get, the Operation gives one row per pick with
  `maker`, `code`, `link` and `in_drawer`. A value the record lacks is `null`, never filled in.
- `parts.py` prints the rows, and `--json` carries them. No request leaves the machine.
- The page (after P827) shows the same rows from the same Operation.

### Notes

- Type: story, size S. Parent: P820 #1173. Slice: Views and editors. P820's D10 (shops after the MVP) stays.
- The core: a `WhereToGet` Operation over the picks and the records.

## 5. The open cards that block a walk: the lines to add

These three are in Idea with "To refine with the PO". The lines below make each one a check that can fail.

**P865 (#1231), the look reads any board.** Rows B3, B5, B6, C14. True today: with one board on USB,
`LookService.run` takes it and reads at once (`scripts/spark/bench/board_look.py:456-460`). `mpremote devs` already
lists the board's USB serial without opening the port (`board_look.py:106-107`, `:154-163`). Add to Done when:

- A test with a fake finder and a fake reader: the board's serial is not one that the store names for this
  project. The look stops with exit 2, names the port and the serial's last 4 characters, says that a read
  restarts the board, and the reader's `read` is never called. `--port` goes on.
- A test: a board the store names for this project is read with no question.
- A test: the look and the deploy that follows make one read between them, or the look says how many restarts come.
- The core: a `BoardIdentity` check before `EsptoolReader.read`. `look.py`, `deploy.py` and `reach.py` call it.

**P864 (#1230), the amplifier's own speaker socket.** Rows A6, A9, C2. True today: `parts/max98357a-dfr0954.json`
names no socket, and `--requirements` then says "nothing listed receives it"
(`scripts/spark/design/write_requirements.py:26`, from `need_requirements.py:203`). Add to Done when:

- The record says that SPK_P and SPK_N end in the module's own 2-pin socket, with the drawing as the source (page
  1, its sha256) and `verified: false`.
- A fixture of the board, the DFR0954 and a speaker with no record: `parts.py --requirements` prints no "nothing
  listed receives it" line, and `/spark:build` exits 0 with no `speaker-terminal` in the parts.
- The sheet tells the person to plug the speaker into the module's socket, and never to put a supply there.
- The core: one record fact that `_power_gaps` and the board emitter read. No logic per part (AGENTS.md: records
  grow by need). P735 (#1010, connectors in the DFRobot records) is in Design: use its key if it has one.

**P868 (#1235), a pin on a bus line.** Row C12. True today: the loader refuses it for every bus
(`scripts/spark/design/loader.py:381-384`). The reason given there is a second part on the same bus. Add to Done when:

- A test with the game box's pins (BCLK D12, LRC D11, DIN D10): the build runs, and `pins.py` names the three with
  the reason "asked for by name".
- A test: a pin that the board cannot route the bus to is refused, and the refusal names the pin and the bus.
- A test: two parts on one bus with pins that split the bus are still refused, with both named.
- The core: the refusal moves from the loader to the assigner's bus placement, which knows what the board routes.

P871 (#1238, the board doctor, a spike) does not block a walk on a walk board. It blocks only a walk on the game
box, which another session restores. It stays where it is.

## 6. The order

**(a) What blocks a new walk, in order.** Ready holds 4 cards of spark's lane.

| place | card | why here |
| --- | --- | --- |
| 1 | P865 (#1231) the look names the board | Bench safety. Every walk with a board starts with the look, and it restarted another session's board. |
| 2 | P864 (#1230) the speaker socket | Small, mostly a record. Without it the sound walk's build stops or asks for a part nobody needs. |
| next 1 | P868 (#1235) a pin on a bus line | The sound walk cannot describe the box. D7 and N8 wait for it. It is the largest of the seven. |
| next 2 | N1 board.tsx replaced | The first of D5's command fixes. Every changed design needs a deletion by hand today. |
| next 3 | N3 the watch | D14 puts it before the new walks. It needs the PO's bench row first, so it follows the cards that need no bench. |
| next 4 | N2 the list of bench changes | D5's third fix, and D8's first case. Only a walk that changes a design needs it. |
| next 5 | N4 the requirements' entries | D5's second fix. Only a walk that drops a part needs it. |

Places 3 and 4 of Ready stay P827 (#1185) and P828 (#1186), on the PO's D11 (Q1). Each "next" card enters on top
when a place frees. N5 (the true marks, XS) goes just before P827. N6 goes before P828. N7 to N11 follow P828.
P862 (#1228) and P863 (#1229) block no walk and stay in Idea.

**(b) What moves in Ready today.** Ready holds P711 (#960), P827 (#1185), P828 (#1186) and P829 (#1187).

- P829 (#1187) moves out, to Idea, with "Waiting on: N10" (D11: it waits).
- P711 (#960, the walks) moves out, to Idea, with "Waiting on: P865, P864, P868, N1, N3". It cannot be pulled
  before them, so it only holds a place. It comes back on top when they are Done.
- P827 and P828 move down to places 3 and 4.

**(c) Questions that only the PO can answer.** Work goes on with the recommended answer.

- Q1. Ready has 4 places, and 7 cards block a walk. Do P827 and P828 keep two places (D11), or do four blockers
  fill Ready? Recommended: they keep places 3 and 4, and a blocker enters on top each time a place frees.
- Q2. May the new cards be filed as written, and the three open cards get the lines of section 5? Recommended:
  yes. It is the same act as P510's filing.
- Q3. The slice of N7 to N10 (new behaviour after a change). D15 named none. Recommended: "v0.11 Change it and put
  it on again", which exists on the board with 4 cards. The fixes N1 to N4 are in "v0.10 The basic journey".
- Q4. Is a deploy by spark a fair witness that the sheet before it was wired (N2)? Recommended: yes, as the first
  witness, said with its source and time. His own word "wired" comes later (D8).
- Q5. Row C10: do the flow's commands keep `${CLAUDE_PLUGIN_ROOT}`? Recommended: yes for now. P827's page carries
  the commands, and a person asks Claude.
- Q6. N3 needs his bench twice, about ten minutes each: the row that names the cause, then the watch itself.
  Recommended: both at the start of the first new walk's session, before the walk.
- Q7. The walks' start list frees the earlier walk's holds (A5, C1), with no card. Recommended: yes.

## 7. Not checked

- No bench claim: which key stops `main.py`, the restarts per read, and download mode after a look.
- N8's count (6 of 15 signals move) and the assigner's code. N11's record keys. `kept_files.py:301-326` (P280).
- The bodies of P413 (#539), P734 (#1005), P735 (#1010), P827, P828 and P829. Their titles and stages were read.
- Whether the deploy's question names the project folder (C15), and why the tally gave three answers (B2, C3).
- Page notes 3 and 4 in a browser.
- The test file names in the Done-when lines are first guesses where they say "or the module's test file".
