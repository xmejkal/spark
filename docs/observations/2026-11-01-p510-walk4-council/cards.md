# P510 cards: filing text for the PO's OK

> Fourteen new cards (section 1, N5 and N6 each split in two), edits to eleven open cards and one comment on the walks
> epic (section 2). Nothing is filed yet. Each new card is a sub-issue of P100 (#6), slice v0.10 The basic journey. The
> order and the reasons are in `plan.md` (final, with its second round). The PO's words are verbatim from walk 4's diary
> and the rows file's "Ideas and asks". A gap code G1 to G46 is walk 4's. Walk 3's council also had N codes, so until a
> card has its P number, a row writes "walk 4 N3 (drop a need)".

## 1. New cards

### N1: the board emitter traces the pin name, not the pad → one `BoardPads` reader, and the verdict names the trace

Label: bug. Slice: v0.10 The basic journey. Size S.

### Needed by

The person, walk 4 step 19: `we definitelly should fix this`. Every SPI or I2C part on the FireBeetle 2 and the XIAO C6
(G29, G30, refuter R1 and R2). The XIAO breaks since P278 (`2b868965`, 2026-10-18).

**The change.** `emit_board.signal_lines` writes `.Mcu > .MOSI`, while the footprint pad is `MO` (`emit_board.py:812-813`,
and `signal_lines(part_list, assignments)` at `:1048` gets no board). A `BoardPads` Value in `scripts/boards.py` reads
`physical.pad_aliases` once and answers `pad_of(label)`. The emitter, `assign_pins.py:418` and `breadboard.py:150,315` call
it. The TypeScript converter's copies (`tools/circuit-to-wokwi/lib/board.ts:102,112`, `lib/mapping.ts:94`) stay out of
scope. The build verdict carries the first two selector messages of `circuit.json` (`check_spine.py:496`).

**Done when.** Three builds end with 0 errors: `dfr0664-tft-2in` on the FireBeetle 2, `dfr0664-tft-2in` on the XIAO C6,
and `vl6180x-breakout` on the XIAO C6. A test for each shipped board checks that the pad of every pin label is in its
footprint. A test finds no Python file outside `scripts/boards.py` that reads the key `pad_aliases`: `BoardPads` and the
record validator (`boards.py:694`) both live there. A broken trace prints its selector in the text and in `--json`.

### N2: `requirements.json` cannot pin a part's signal → a requirements signal with the part's signal name sets its pin

Label: story. Slice: v0.10 The basic journey. Size S. After N1.

### Needed by

The person, walk 4 step 9: `Iwant to test adding a GDI display and displaying something, to test the whole module adding
scenario`. Spark's pin map disagreed with the GDI cable on 5 of 8 signals (G27). The first slice of C2 (refuter R11).

**The change.** Today `signals: [{"name": "TFT_BL", "pin": "D13"}]` beside `dfr0664-tft-2in` is refused: "both TFT_BL"
(`design.py:376-382`, where the signals are derived). A requirements signal whose name is a part's signal and that
gives a `pin` sets that signal's pin, and adds no second signal. The refusal is P163's guard against one signal placed
twice (`tests/mutations/p163-case-names.json`), so it stays for an entry with no `pin`. The assigner already honours a
named label (`assign_pins.py:228-247`).

**Done when.** Walk 4's requirements with the 8 GDI pins as signals build with the cable's labels, and `pins.py` names
them. A test pins one part signal and shows the refusal for a pin name the board lacks. P163's tests in
`tests/test_design.py` pass unchanged. `docs/guide/agents.md` and the build page say how to write it.

### N3: spark cannot drop a need from a project → `parts.py --needs-drop` with a dry run drops it and frees its hold

Label: story. Slice: v0.10 The basic journey. Size S.

### Needed by

Walk 4 step 18: `--pick . light=` is refused, and no flag removes a need (G26). The journey "swap a part" has no step.

**The change.** A `DropNeed` Operation behind `parts.py --needs-drop PROJECT NEED`, beside `--needs-set`. It removes the
need and its pick from the project's needs file. The holds come from the picks on each plan (`needs.py:430-453`), so the
next plan frees the hold. The dry run prints what changes and writes nothing. Its `effects` names the file in
today's form. P488 (#667) later moves every write, `DropNeed` too, to `place` and `path`, so no second field comes.
Words: a need is dropped, a hold is freed.

**Done when.** A test drops `light` from a project with a held part: the dry run changes no byte, the run leaves no pick,
and `--drawer` shows the piece free. The import test then names firmware that still imports a gone signal name.

### N4: a refused pick hides the third fix and the drawer key → the refusal puts every fix in `next`

Label: story. Slice: v0.10 The basic journey. Size XS. After N3 and P473 (#647).

### Needed by

Walk 4 steps 2 and 3: an ended project's hold blocked the pick (G3), the refusal named two fixes (G6), and `--drawer`
printed no entry key for `--drawer-set` (G7). UX finding 10.

**The change.** A refused pick names the holding project and three fixes in order: drop the holding need (N3's
command), pick another part, or, only if the person owns another piece, the `--drawer-set` line with the entry key.
`--json` carries them in the envelope's `next` as `NextStep`s (`spark/core/result.py:18`), with no new key. The item's
`fix` stays a sentence (`json.md:234`). The count is a fact about the person's drawer, so its step has `needs_yes: true`:
Claude asks and never runs it on its own (`commands/drawer.md:39-40`). `--drawer` prints each entry's key.

**Done when.** A test refuses a held pick and reads the three steps in the text and in `next`, the drawer step with
`needs_yes: true`. `--drawer --json` has `key` for each entry. `json.md:256`, which says that no operation fills `next`,
is corrected.

### N5a: the idea page reads a brief that does not exist yet → step S runs `/spark:init` first

Label: story. Slice: v0.10 The basic journey. Size XS. A page only.

### Needed by

Walk 4 steps 1 and 5: the idea page reads the brief that `/spark:init` writes only at step L (G1, `commands/idea.md:25`),
and Claude wrote the goal by hand (G9, UX 15).

**The change.** `commands/idea.md` runs `/spark:init` before step S, or step S stops with "run /spark:init first".

**Done when.** A new project's brief holds the goal after step S, in a walk-through of the page with a scratch store.

### N5b: the build ends with no next step → its verdict names the firmware step in `next`

Label: story. Slice: v0.10 The basic journey. Size XS. After N1 (the same verdict, `check_spine.py:496`) and P473 (#647).

### Needed by

Walk 4 step 7: a new person did not know that firmware comes next (G11, stall S3).

**The change.** `check_spine --json` gains one key, `next`, with one `NextStep` (`spark/core/result.py:18`): `look.py`,
whose `why` says "first write `firmware/main.py` from `pins.py`". The text prints the same line. The conversation
writes the firmware, so spark names the step only.

**Done when.** A test reads the step in the text and in `--json`. `json.md:140` lists `next` among `check_spine.py`'s keys.

### N6a: Claude offers the deploy grant only when asked → the deploy page offers it once, at the first stop for a yes

Label: story. Slice: v0.10 The basic journey. Size XS. A page only.

### Needed by

The person, walk 4 step 54 (I3): `change the system so that there's also an option to do all yourself without me having
to switch to the other terminal and paste things`. Walk 4 had ten typed yeses (UX 2), and deploy printed the grant
line once, at step 17.

**The change.** The grant line and its step exist: deploy prints it where a grant can cover the deploy (`deploy.py:134-148`),
and its envelope puts a `grant` step in `next` with `needs_yes` (`board_envelope.py:95-98`). Today
`commands/deploy.md:53-57` offers it only "if the person wants". The page now offers it once per session, at the first
stop for a typed yes, with today's words about what it covers. An image that no simulation tested gets no grant line
(`commands/deploy.md:83`), so the offer helps those deploys only after decision 1.

**Done when.** `commands/deploy.md` says when to offer the grant and what it covers, and a reviewer reads it against
`board_grant.py:85` (the question) and `:107` (no `--no-simulation`).

### N6b: the deploy grant names no project and no count → it names both, and `--check --scope deploy` reads it

Label: story. Slice: v0.10 The basic journey. Size S. After W4-3 (grant on the core, `wave4-plan.md`), W4-2 (deploy
on the core), and the PO's decisions 1 and 3 in `plan.md`.

### Needed by

The person, walk 4 step 54 (I3): `change the system so that there's also an option to do all yourself without me having
to switch to the other terminal and paste things ? ... I wantto be able to keep this half manual way, but the fully
automatic would be great`. Walk 4 had ten typed yeses (UX 2).

**The change.** The deploy grant exists since P242 (`board_grant.py:14-15,85,172`), and its `Grant` holds no project
and no count. The grant names the project folder and a deploy count beside its minutes, and the question shows both.
`grant.py --check --scope deploy --json` gives the scope, the project and the minutes left (today `--check` reads a
live grant only, `grant.py:90`). Each covered deploy prints "used the deploy grant of <who>, 4 of 10 deploys, 38
minutes left". The `grant` step in `next` stays the one place for the command, with no new key. The half-manual way
stays. A board whose USB serial is not its MAC gets no grant, and the words say so (refuter R8).

**Done when.** A fake clock ends a grant by time and by count. A deploy of a second project is refused by the grant.
The answers to decisions 1 and 3 are built or named as not built.

### N7: deploy ends at a late port and keeps no later line → it waits for the port and reports later console lines

Label: story. Slice: v0.10 The basic journey. Size S. After W4-2 (deploy on the core, `wave4-plan.md`), which
carries E2 (`event-seam-plan.md:226`). Today deploy passes a `show_line` lambda (`deploy.py:248,270`) and has no `outside`.

### Needed by

Walk 4 step 43: `ready unknown` 3 times, because the port came back late (G40, UX 13). Step 31: no later console line is
kept (G35). The 2 s of silence does not tell a running firmware from a dead board, in walks 3 and 4 (G16).

**The change.** Deploy waits for the port to come back, up to a time it names, before it says `ready unknown`. Then it
says "the port came back after N seconds. The board is ready." `ready unknown` stays only when the wait ran out. A
watch step sends later console lines as `Event` lines through `outside.report` (E1, reached by deploy in E2), and the
board log keeps them. It adds no log path of its own (architecture A11).

**Done when.** A fake port that returns after 3 s gives `ready` with no retry by Claude. A fake console line after the
short read reaches the board log. The deploy goldens of P508 change only in the lines this card names.

### N8: the chain's stages say different things about what a run tests → one sentence, and the pick names a skip

Label: story. Slice: v0.10 The basic journey. Size S.

### Needed by

Walk 4 step 6: `--match` and `--pick` said that no scenario can press the button, and the build wired a stand-in that a
scenario pressed (G10). The pick said nothing of the display's `simulation` skip (G28). With `--no-simulation` the look
listed no limits (G33). Claude merged three messages by hand (UX 12).

**The change.** One reader gives the sentence "a scenario can reach this pin" or "cannot", from the board record and the
part's `simulation` field (today in `needs.py:202-208`). It is not P399's `ScenarioSteps`, which reads the ids that a
scenario file names (#515, PR 1). `--match`, `--pick`, the build and the look print it. The look with `--no-simulation` lists
the limits and the unnamed must lines.

**Done when.** A test reads one sentence in the four outputs for walk 4's button and display. The `--no-simulation` look
lists the display's must line.

### N9: the file system is a fixed 2 MB at 0x200000 → the layout comes from the image's own table

Label: story. Slice: v0.10 The basic journey. Size S. After P511 (#706) returns the self-built image's table.

### Needed by

Walk 4 step 57: `flash_image.py` refused the s3lcd image's own 14 MB `vfs` (G42), so spark cannot carry a native driver
build (I2).

**The change.** `FLASH_SIZE` is 4 MB and the file system sits at `FILESYSTEM_OFFSET` 0x200000 (`flash_image.py:37-38,82`).
`:121-126` refuses any other `vfs` or `ffat`. A `FlashLayout` Value reads the image's own table: it keeps the table's
`vfs` entry, else today's 2 MB at 0x200000, and the flash size is the end of the table's last entry, at least 4 MB.
No board reading enters: the build's simulation stage makes the tested image with no board on USB. The look already
refuses an image larger than the measured flash (`board_look.py:280`), and the record's `flash_mb: [16, 4]` stays a
check there.

**Done when.** A fixture table with its own `vfs` passes, and today's tables give byte-equal images. A table that ends
at 16 MB gives a 16 MB image, and a fake 4 MB look refuses it with today's words.

### N10: spark does not say which MicroPython runs on the board → the image, the look and the facts file name the build

Label: story. Slice: v0.10 The basic journey. Size S. After P511 (#706) and W4-2, which moves what deploy writes.

### Needed by

Walk 4 steps 40, 42 and 62: `flash_image.py --micropython` took an outside interpreter silently (G38,
`flash_image.py:255-256`), the look did not say which build the image holds (G39), and an image written outside spark
left no trace (G46).

**The change.** `--micropython` with a path outside the project's tools list says so and names `tools.py --new`. The
facts file gains `interpreter {build, sha256}` (`board_facts.py:23-27`), and so does the board's last deploy. The look
names the build. A sha256 that differs from the last deploy says "this image was not written by spark".

**Done when.** A test flashes with a path outside the tools list and reads the sentence. A fake look reads the build
name, and a fake changed sha256 gives the warning.

### N11: the stand-ins sit in two folders and know no C module → one documented folder, and a project adds its own

Label: chore. Slice: v0.10 The basic journey. Size XS. Ride-along: it enters Ready only with a card that touches
`import_firmware.py`.

### Needed by

Walk 4 steps 8, 20 and 57: the editor flags MicroPython's names (G14), `framebuf` sits apart from `machine` in
`scripts/stand_in/fallback/` (G32), and `import s3lcd` had to sit inside a function (G43).

**The change.** `framebuf` moves beside `machine` in `scripts/stand_in/`. The import child also puts a project's own
`stand_in/` folder on `sys.path` (`import_firmware.py:52,61`), so a project stands in for a C module itself. Spark ships
no stand-in for a third-party driver. `docs/guide/agents.md` lists the folder and says how an editor reads it.

**Done when.** A test imports firmware that imports a module from the project's `stand_in/` at the top level.

### N12: the BOOT button has no name in `pins.py` → the record names it with its download-mode caveat

Label: task. Slice: v0.10 The basic journey. Size XS. Ride-along: it enters Ready only with a card that touches a
board record.

### Needed by

Walk 4 step 23: GPIO0 is known only in a strapping note, so `pins.py` has no name for the second button (G34).

**The change.** The FireBeetle 2 record's `onboard_button` gains `labels` for the user button (GPIO47) and BOOT (GPIO0),
with a source and the caveat "held at reset, it enters download mode". Its `gpio` stays `[47]`, so the pick and the
scenario never offer BOOT as the button to press. `assign_pins.onboard_lines` (`:452-456`) writes only `<NAME>_<LABEL>`
when labels exist, and `ONBOARD_BUTTON_ON` stays (`:460-464`). No board record uses `labels` today. No code change.

**Done when.** `pins.py` names `ONBOARD_BUTTON_USER` and `ONBOARD_BUTTON_BOOT` with the caveat, and `ONBOARD_BUTTON_ON`.
The plain name `ONBOARD_BUTTON` stops existing, so old firmware stops importing it, and the PR text says it. A pick that
puts a part on D9 (also GPIO0) names the shared GPIO.

## 2. Edits to open cards

Each edit is a new section "### From walk 4 (P510, #705, 2026-11-01)" at the end of the body.

- **P460 (#628), the GDI spike.** Delete the line "Order: after the FireBeetle walk". Add: "Walk 4 plugged the DFR0664
  display into GDI by hand. Its pin tables are in `walk4-diary.md`, read off an image, so they stay `verified: false`
  until this finding cites the schematics. GDI BL and the onboard LED share GPIO21, and GDI shares IO1, IO2 and IO7 with
  the camera (G22). Every GDI GPIO is already a header label (refuter R10), so the assigner does not change. The finding
  tests the class diagram in `docs/observations/2026-11-01-p510-walk4-council/plan.md`: `Connector`, `ConnectorPin`,
  `ConnectorPlug`, a part's `plugs_into`. Words: this body's "plug" for the board's socket becomes "connector", and its
  "plug type" becomes the connector's `kind`. The build card is filed after this finding. It also reads a need's
  condition `plugs into` (G19) and leaves `ONBOARD_LED` out of `pins.py` while a connector claims GPIO21 (G31). G20, G23, G24."
- **P466 (#634), the MAC names its unit.** Add: "Walk 4's G4: the refusal did not say which of the 2 owned boards is on
  USB, because a hold counts pieces (`drawer.py:327`). Done when also: a hold names its board by MAC."
- **P469 (#637), the look without a restart.** Add two slices. Slice 1, the held plan: the look reads through mpremote.
  Slice 2, after W4-2 (deploy on the core, `wave4-plan.md`), with one Done-when line: "Deploy enters download mode by
  `machine.bootloader()` through mpremote, then esptool `--before no-reset`, on an S3 that runs MicroPython, with no key
  press, on the bench. The C6 keeps the button words." Add: "The plan drops 'hard-reset pinned' for the look. After a
  write the flasher keeps `--after watchdog-reset` (`flasher.py:51`), because hard-reset leaves a BOOT-entered S3 in
  download mode (`flasher.py:45-50`). Walk 4's G15, G36 and G41: 11 presses in one walk. The PO's answer to decision 2
  of P510's plan gates both slices and sets which yes covers the call."
- **P490 (#669), seen on the bench.** Add: "Seen again in walk 4 (G18), so two walks. Walk 4's G17 also lands here: a must
  line that no scenario can test is marked `bench only` in the needs, and the look lists it until the person's typed yes
  records it."
- **P409 (#535), the Wokwi spike.** Add: "Walk 4's G25: Wokwi has no part for the DFR0664's ST7789 at 240x320, so the
  display was tested only on the board. Wokwi's `st7789` part is a question for this finding."
- **P336 (#430), driver records.** Add: "Walk 4 ran this card's ladder on the bench: framebuf and SPI in Python reached 1
  to 13 frames per second, and the s3lcd C driver ran smoothly (P509 #704). The last rung needs a pinned third-party
  build. P511 (#706) returns its facts: the build entry (source URL, license, sha256), whether its USB console stays
  alive (G45), and its USB serial (G44). A fixed serial means a grant cannot name the board (P510 row 53). The flash
  layout is walk 4 N9 (P510), the interpreter name walk 4 N10."
- **P349 (#445), the most specific build.** Add: "Walk 4's G37: the N16R8's 8 MB of PSRAM stays off, because the record
  names one `micropython_port` for both SKUs (`boards/firebeetle2-esp32s3.json:7,9`). The most specific build for the
  N16R8 is `ESP32_GENERIC_S3-SPIRAM_OCT`. Done when also: the look's measured flash or PSRAM picks the SKU's build, or
  the person is asked which SKU it is."
- **P399 (#515), the scenario dry run.** Add: "Walk 4's G12 asks for exactly PR 2's `--dry-run`."
- **P118 (#52), the `!` lines.** Add, if the PO says yes to decision 4: "Walk 4's G8 is the third walk. This card's first
  PR is the 'not asked for' line alone (`check_all.py:466`), size XS. The rest stays."
- **P488 (#667), each write names its place.** Add: "Walk 4's G2: the `--needs-set` dry run names its fields but not the
  file it writes or whether it lists the project. The test covers `--needs-set`."
- **P390 (#505), the board shelf.** Add, if the PO says yes to decision 4: "Walk 4's G5, the third walk: `--match` lists
  `xiao-esp32-c6-fresh (button-light)` with no word. Done when also: a record that one project holds is labeled with
  that project in `--match`."
- **P492 (#671), the Wokwi spike.** Add: "Walk 4's G13 is the third walk with no press and read on the Mac. The PO, decision
  4 of P510: after the MVP, as this card says."
- **Comment on P365 (#467), the walks epic.** "Walk 4's I1, the person: `there should be test options or presets or
  something` and `to be able to test from clean or weith already having it etc`. A walk's setup step names its start:
  a clean store, or one free board. Walk setup, not a product card."

Status moves, for the PO's order: P506 (#700) and P503 (#692) back to Idea. P473 (#647) leaves Ready until rank 7.
