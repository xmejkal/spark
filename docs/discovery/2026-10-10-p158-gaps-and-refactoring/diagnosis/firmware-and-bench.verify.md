# P158 part 1 — verification of the firmware-and-bench diagnosis

Written 2026-10-10 by the area's refuter, against spark 0.8.1 (main `a8aa34d`, E: `git rev-parse --short HEAD`), over
`firmware-and-bench.md` and the catalogue rows it answers (K32, K66, K67). I did not write the diagnosis; I tried to
refute it. Tags as in the diagnosis: **E** a pointer (file:line in `~/Development/spark` unless another repository is
named; a command and what it printed), **H** a claim with its source only, **D** a decision (who, when), **—** unknown.

Every spark command and every converter run below went against a copy of the PO's store at `<scratch>/store` with
`SPARK_HOME`, `HOME` and `TMPDIR` set on the command, verified once (E: `env | grep` printed the three pointing into
`<scratch>`); `~/.local/share/spark` was never run against or written. The converter runs reuse the diagnostician's kept
circuits (`<scratch>`'s `chain/keep1` — one button, its trace moved to `TX` — and `k32/circuit.json`, irrigation's
build) with the plugin's bundled `dist/converter.mjs` under node; the only files written are under my own scratch folder.
Two things were read that the diagnosis could not: the Wokwi part registry, asked directly through the converter's
`node_modules` (`@wokwi/diagram-lint` 0.1.1, E), and esptool's chip-id table, from the esptool 3.3 installed under the
PO's pyenv (E: `python3 -m pip show esptool` → `Version: 3.3`).

The PO's criteria for every change (D: PO, 2026-10-10): *"well designed so its well testable and understandable where
a mistake is happening and why"* — testability, diagnosability, simplicity (remove before add).

## Verdicts

### RC-firmware-and-bench-1 — partly

**Lines read (verbatim).**
- `scripts/assign_pins.py:148` `for label, gpio in sorted(board["pins"].items(), key=lambda pin: (pin[1], pin[0])):`;
  `:150-151` `if any(role in UNAVAILABLE_ROLES for role in roles): continue`; `:61` `UNAVAILABLE_ROLES = ("strapping",)`.
  As cited: the candidates come from the record alone.
- `scripts/boards.py:62-63` `REQUIRED_KEYS = ("schema", "id", "name", "chip", "wokwi_part_type", "pins",
  "wake_capable_gpio", "adc_gpio", "physical")`; `:307-313` the `wokwi_power_pins` loop over `power_pads` only, under the
  comment `:306` *"Nothing compared the two lists; a person running the chain on one project was the check"*. As cited.
- `tools/circuit-to-wokwi/lib/geometry.ts:52` *"137 of them, offline"*; `:103-106` `isValidPin(wokwiType, pin) { if
  (!this.knowsPart(wokwiType)) return true; return this.pinsOf(wokwiType).includes(pin); }`. As cited.
- `lib/emitters/wokwi.ts:174-181` the `isValidPin` check and `` `"${pin}" is not a pin of ${mapping.wokwiType}. Valid pins: ` ``.
  As cited.
- `lib/mapping.ts:96` `byName[name] = WOKWI_NAMES_PINS_BY_GPIO ? String(gpio) : name;` — as cited. **`:109`** `return {
  ...byName, ...(board.wokwi_power_pins ?? {}) };` and **`:273-276`** `export function wokwiPinName(mapping, designPin) {
  if (mapping.pins && designPin in mapping.pins) return mapping.pins[designPin] ?? null; return designPin; }` with
  `:116` `pins: WOKWI_PINS,` on the `BOARD` mapping — three lines the diagnosis did not weigh (below).
- `scripts/check_spine.py:216` `CONVERTER_HAS_NO_PART = "no Wokwi part is mapped"`; `:482-489` the one-string
  classification; `:507-514` *"no test on this machine reaches run's simulation stage"*. As cited.
- `boards/README.md:96-97` *"a same-silicon devkit stands in and `wokwi_is_stand_in` says so — the diagram addresses pins by
  GPIO number, so a stand-in costs only the silkscreen labels in the picture."*; `boards/firebeetle2-esp32s3.json:104`
  *"it exposes GPIO 0-21 and 35-48 - a superset of every pin this board brings out"*; `:115` `"wokwi_is_stand_in": true,`.
  As cited. `wokwi_is_stand_in` outside `node_modules`: `lib/board.ts:35` (the type), `boards/README.md:96`, the record
  `:115` — no script or emitter (E: `grep -rn` over `scripts tools/circuit-to-wokwi/lib boards docs/guide commands
  skills README.md`, 2026-10-10). Holds.
- `commands/build.md:100-105` *"Three outcomes, never two … `!!` is a defect in the design, named."*;
  `tests/test_check_spine.py:721-733` the B11 test pair. As cited.
- The registry, asked myself (E: `<scratch>/registry/standin-pins.mjs`, node, 2026-10-10): `board-esp32-s3-devkitc-1`
  **44** pins, among them `"TX"` and `"RX"` and no `"43"`/`"44"`; `board-esp32-c6-devkitc-1` **32** pins — `0`–`13`,
  `15`, `18`–`23`, no `14`, `16`, `17`; `board-xiao-esp32-c6` **15** pins — `D0`–`D10`, `$gpio15`, `3V3`, `5V`, `GND`.
  The diagnosis's three counts hold.
- The assigner spends the S3's `TX`/`RX` (E, re-run: `assign_pins.py many.json --board firebeetle2-esp32s3` → `22
  signal(s) placed`, `SIG20 TX GPIO43 … taken only because nothing free was left [console_uart, not_wake_capable]`,
  `SIG21 RX GPIO44 …`); the XIAO's I2C lands on the `SDA`/`SCL` labels (E, re-run: `SDA SDA GPIO22 on the board's own I2C
  pin — dedicated hardware, not a choice [i2c]`). Both hold.

**What holds.** The assigner knows nothing of the stand-in; `--validate` compares power pads only; the one flag that
says "stand-in" is read by no code; `check_spine` classifies a converter failure by one substring; the documents claim
a cost ("labels only") the mechanism does not guarantee; round 0's stop (K32) was a pin the generic C6 devkit truly has
not (`14`, E: the registry; `council/round-0-runner.md:5`, `:24-25`).

**What is weaker or wrong, and the sentences to change.**

1. *"`firebeetle2-esp32s3` on the S3 devkit — 2 of 25 header pins absent on the stand-in"* and *"`xiao-esp32-c6` on its
   own Wokwi part — 9 of 20 absent"*. **Zero GPIOs of either library board are absent on its stand-in.** The FireBeetle
   S3 brings out 24 distinct GPIOs under 25 labels (E: the record's `pins`, counted); the devkit has all 24 — 22 by
   number and GPIO43/44 as the pads `TX`/`RX`. The XIAO brings out 11 distinct GPIOs under 20 labels; Wokwi's XIAO has all
   11 as `D0`–`D10` (`D3`=21, `D4`=22, `D5`=23, `D6`=16, `D7`=17, `D8`=19, `D9`=20, `D10`=18 in the record). What is
   absent is a **name**: the converter derives the Wokwi name by one board-wide rule (`wokwi_pin_naming`,
   `mapping.ts:96`) and the design writes its trace to the label the assigner chose (`SDA`, not `D4`). These two cases are
   simulable the moment the emitter picks a name the part knows; they are not stand-in limits. Only a user's own board on
   a generic devkit — round 0's — has pins the part lacks. Change the two sentences to: *"2 of 25 labels (and 0 of 24
   GPIOs) have no pin of that name on the stand-in"*, *"9 of 20 labels (0 of 11 GPIOs)"*, and say which case is which.
2. *"The record has no field that could carry the fact — the `null` convention exists for parts (`mapping.ts:53-59`),
   not for the board"*. **Refuted by experiment.** `wokwi_power_pins` is spread last into the board's Wokwi pin table
   (`mapping.ts:109`), the table is the `BOARD` mapping's `pins` (`:116`), and `wokwiPinName` honours a rename and a
   `null` for the board exactly as for a part (`:273-276`). E (2026-10-10, bundled converter under node, the three
   variables set, output under `<scratch>/exp/`):
   - the `TX` design against the unmodified S3 record → `"43" is not a pin of board-esp32-s3-devkitc-1`, no diagram (the
     diagnosis's run, reproduced);
   - the same design against the record plus `"wokwi_power_pins": {…, "TX": "TX"}` → `wrote out-tx-override.json`,
     **6** connections, two of them at `mcu:TX` — **the S3's "absent pin" case is simulable today with one data line**;
   - irrigation's `circuit.json` against the record plus `"D3": null` → `wrote out-d3-null.json`, **33** connections
     against **34** in the diagnostician's `out-s3.json`, and no `mcu:38` endpoint — the board can already say "the
     stand-in has no such pin";
   - the same with `"D3": "99"` → `"99" is not a pin of board-esp32-s3-devkitc-1` — the override is read for a GPIO pad;
   - `boards.validate(...)` on all three modified records → `ok` (E: called from `scripts/`, 2026-10-10).
   So the sentence should read: *"The record has a field that already carries the fact — `wokwi_power_pins`, merged
   last into the board's Wokwi pin table and honoured for a rename and a `null` — but it is named for power pads, its
   TypeScript type (`Record<string, string>`, `lib/board.ts:39`) excludes `null`, no page documents it (E: `grep -rn
   wokwi_power_pins boards/README.md docs/guide commands README.md` → nothing), and `--validate` checks neither its keys
   nor its values."* The mechanism is not a missing field; it is a misnamed, undocumented, unvalidated one, plus the
   absence of anything that derives its content from the registry the converter bundles.
3. *"The documents then say the opposite of the mechanism"* and C1's **removes** of the S3 note's *"a superset of every
   pin this board brings out"*. The note is **true of GPIOs** (24 of 24 on the devkit); what it omits is that two of them
   are named `TX`/`RX` there. Amend it; do not delete a true sentence. `boards/README.md:97`'s "labels only" is true for
   the library S3 once the two names are right and false for a generic devkit standing in for a user's board — say both.

**Also found on C1(a)'s cost.** The bundle refuses even `--help` without a board: E `node dist/converter.mjs --help` →
`Error: SPARK_BOARD_JSON is not set …` (board.ts reads the file at import, `lib/board.ts:77-88`). A `--part-pins`
query needs that read made lazy or a board handed to it, and the bundle rebuilt (`tools/circuit-to-wokwi/bundle.sh`,
bun) with `tests/test_check_spine.py:850` pinning the sources' sha256. "~15 lines in `cli.ts`" is not the size.

### RC-firmware-and-bench-2 — partly

**Lines read (verbatim).**
- `scripts/flash_image.py:72-76` `def interpreter_path(given): """The MicroPython build: the one given, else the tools
  list's download (P82)."""` … `return Path(tools.find("firmware-image").command[0])`; `:80-85` the four arguments
  `--micropython`, `--files`, `--config`, `-o/--output`; `:16-17` *"made general here for backlog P31: any project, any
  file tree, the board's chip named on the command line by the image"*; `:62-63` `if len(interpreter) >
  FILESYSTEM_OFFSET: raise ValueError(…)` — the only check on the interpreter; `:14` *"the simulated board boots to a bare
  REPL with no main.py, which is the symptom"*. As cited; the wrong-chip pack follows from `:62-63` (nothing reads the
  header) and I did not re-run `<scratch>/chipid`.
- `data/tools.json` → `roles`: 11 (`pdf-text`, `simulator`, `board-engine`, `diagram-converter`, `js-runtime`,
  `littlefs`, `firmware-image`, `parts-search`, `chip-docs`, `bench`, `ts-runtime`), `firmware-image → micropython-esp32s3`,
  `bench → sigrok`; the entry's `"for": "the interpreter the flash image starts with, for an ESP32-S3"`,
  `"meets": ["micropython-esp32-bin"]`; `contracts.firmware-image → "micropython-esp32-bin"` (E: read with python,
  2026-10-10). As cited.
- `docs/guide/journey.md:913` *"**Not yet.** No command does this yet."*; `:605` `[????] firmware-image … is not installed`;
  `README.md:77` the Bench row `**not yet**`; `commands/build.md:186-188`; `docs/2026-10-01-firmware-skill.md:135-136`
  *"(`esptool`, `mpremote` appear nowhere). That is P56's increment III"*; `docs/2026-10-01-firmware-and-tests.md:141`
  *"**III — the bench. Mostly documents.**"*. As cited. `grep -rli "esptool\|mpremote" README.md docs/guide commands
  skills` → nothing (E, 2026-10-10).
- `~/Development/smartbin-local/tools/build-flash-image.py:40-45` *"Named after the chip, not hard-coded: the Makefile
  guards this target on a file called micropython-<chip>.bin, and a constant here that named a different chip made the
  guard pass and the script then fail looking for the previous board's build. Which is exactly what happened when the
  board changed from an ESP32-C6 to an S3."* and `MICROPYTHON_IMAGE = SIM / ("micropython-%s.bin" % RESOLVED_BOARD["chip"])`.
  As cited. `~/Development/smartbin-local/firmware/micropython/deploy.sh:15-28` `mpremote rm -r :smartbin` … `mpremote
  soft-reset`; its `:2` *"Deploy the firmware to a XIAO ESP32-C6 running MicroPython."* As cited (and P58's note holds).
- The real S3 build's header: `xxd -l 16 ~/Development/irrigation/sim/micropython-esp32s3.bin` → `e903 022f ac88 3c40
  ee00 0000 0900 0000` — magic `0xe9`, byte 12 = `0x09` (E). esptool 3.3's source, installed: `class ESP32S3ROM … IMAGE_CHIP_ID
  = 9` (E: `site-packages/esptool.py:1974-1977`) — **9 = ESP32-S3 is now E, not H**. 13 = ESP32-C6 stays **H**: this
  esptool has only `ESP32C6BETAROM` with `IMAGE_CHIP_ID = 7` (`:2447-2449`) and no final C6 class.

**What holds.** The title and the mechanism: the image builder resolves a store-wide role, takes no board, and nothing
downstream of the image exists in spark; the step is said absent in prose and nowhere else.

**What is weaker, and the sentences to change.**

1. *"**kind** … implementation (the dropped chip check)"* and *"it generalised the bin's script by removing the board
   from its inputs"*. The bin's script never checked the chip either: `grep -n "chip_id\|0xe9\|magic\|header"
   tools/build-flash-image.py` → nothing (E). Its guard is a **filename** derived from the resolved board
   (`micropython-<chip>.bin`, `:44`; the Makefile's `MICROPYTHON_BIN := $(SIM)/micropython-$(BOARD_CHIP).bin`,
   `~/Development/smartbin-local/Makefile:78`). spark dropped the board-derived name; C2's header read is new to both
   scripts. Write *"the dropped board-derived file name; neither script reads the image header"*.
2. The diagnosis omits the design's own route for another chip: tools.json's `//` — *"A person's ~/.local/share/spark/
   tools.json and a project's .spark/tools.json override any field of any entry; the project wins"* — and `tools.find`
   merges them (`scripts/tools.py:240` `lists = merged(project, personal)`); `/spark:setup` has `--new` for *"the person's
   own entry"* (`commands/setup.md:70`). A C6 project can point `roles.firmware-image` at its own download today. The
   mechanism to name is that **the role→tool table has no parameter and the contract `micropython-esp32-bin` is
   chip-blind**, so nothing derives that override from the board's `chip`/`micropython_port` or checks it against them.
   The RC's conclusion stands; its "why" should carry this.

### RC-firmware-and-bench-3 — partly

**Lines read (verbatim).**
- `scripts/check_all.py:281-292` `CHECKS = [VendorTruth("vendor-truth", …), Buildability(…), TheOrder(…), Physics(…),
  RulesVsNetlist(…)]` — five; `:301-305` `CONVENTIONS = {"circuit": …, "rules": …, "package": …}`; `:299-300` *"it never
  passed `--design` or `--firmware` at all — so the flagship check was permanently unasked and the review still called
  itself complete."* As cited.
- `scripts/assign_pins.py:392-411` `def pin_module(board, assignments, source):` … `lines.append("%s = %d  # %s" % …)`;
  nothing in `scripts/` parses one back (E: the grep for `import machine|fake_machine|FakePin` over `scripts tools skills
  commands` → nothing, 2026-10-10). As cited.
- `docs/2026-10-01-firmware-and-tests.md:24-26`, `:59` (the T0 row), `:122-126` (increment I). As cited.
- `~/Development/irrigation/sim/scenarios/wet-and-dry.scenario.yaml:19-22` and `:29-32` — two `expect-pin` steps,
  `part-id: mcu`, `pin: 38`; `sim/runs/2026-09-29-wet-and-dry.log` ends `[wet and dry] Scenario completed successfully`.
  As cited.
- `~/Development/irrigation/firmware/main.py:76` `for index, adc in enumerate(probes[:len(valves)]):`; `:19` `BUTTON_PIN =
  pins.BTNMODE_BUTTON` — the only occurrence of `BUTTON_PIN` in the file (E: grep); `:99` `main()`. As cited.
- `~/Development/smartbin-local/tools/circuit-to-wokwi/check-consistency.ts:7-13` and `lib/checks/firmware-pins.ts:9-14`
  *"Three independent statements have to agree … None is derived from another, which is what gives the check teeth."*;
  `wc -l lib/checks/*.ts` → 93 + 121 + 124 + 100 = **438** (E). As cited.
- The prototype: `<scratch>`'s `k67/t0_check.py` is 44 lines by `wc -l` (the diagnosis says 45 — immaterial) and
  `k67/t0-output.txt` carries the four lines quoted. Holds.

**What holds.** Today no check reads firmware, `check_all`'s conventions name none, nothing in the plugin executes
MicroPython on a Mac, and irrigation's scenario asserts one GPIO of twelve.

**What is weaker or missing, and the sentences to change.**

1. *"The firmware is outside every check"* is true **since 2026-09-29, by the PO's decision, not by an oversight of
   design.** `scripts/check_firmware.py` (222 lines) was added on 2026-09-24 (`efcc4cc`, *"Firmware against board,
   matched on what is physically true"*), listed in `check_all` as `Firmware("firmware-vs-board", ["firmware",
   "board_file"], "every pin the firmware drives is one this board can do it with")` with the convention `"firmware":
   ["firmware/*/config.py", "firmware/config.py", "config.py"]` (E: `git show 066c4af^:scripts/check_all.py`, lines
   295-296 and 313 of that version), and cut on 2026-09-29 in `066c4af` — *"Petr's call, 2026-09-29: no AI bloat, nothing
   kept that nothing uses … check_firmware.py: run by neither project; the bin has its own in make check"* (D, E: `git
   log -1 066c4af`). The comment at `check_all.py:297-300` is that check's fossil. The RC's "kind: design" should read
   "design, after a deliberate cut (D: PO, 2026-09-29)", and C4 must answer the cut's reason — why it will be used this
   time. The answer exists: a project now has `firmware/pins.py` because P36's `--emit-pins` (journey.md:867) landed
   after the cut, and the old convention matched a `config.py` irrigation never had.
2. §2's last bullet — *"C4 generalises that shape; it does not re-derive one statement from another and call it a
   check"* — misstates what C4 can do. The cut check compared `PIN_* = n` literals by regex (`PIN_CONSTANT =
   re.compile(r"^(PIN_[A-Z0-9_]+)\s*=\s*(\d+)…")`, E: the file at `efcc4cc`); the bin's `firmware-pins.ts` compares
   `config.py`'s literals; increment I at `firmware-and-tests.md:122-126` says *"compares every GPIO literal in the
   project's firmware against the pin map"*. **For a firmware that does `import pins` there are no literals**: the P36
   design removed the independent statement those three compare, so that shape is vacuous on every spark-generated
   project. What the prototype measures is the firmware's *use* of the map — a coverage observation, input-dependent, and
   the diagnosis's three findings say so honestly. Change the bullet to say C4 is a different kind of check (use against
   map), not the triangle.
3. *"**how a person or an AI agent would have known** · Nothing in spark's output."* Narrower: nothing in a *run's*
   output. `README.md:76`'s Firmware row says *"Not built yet: checking the firmware on a Mac against it (P59, P74)"*
   and `docs/guide/journey.md:887-888` says the same (E). The gap is named where a person reads before running.

### RC-firmware-and-bench-4 — holds

**Lines read (verbatim).**
- `boards/firebeetle2-esp32s3.json:281-285` `"deep_sleep": { "wake_api": "esp32.wake_on_ext1", "single_pin_api":
  "esp32.wake_on_ext0", "single_polarity_for_all_pins": true, "simulated_by_wokwi": false,`; `:7` `"micropython_port":
  "ESP32_GENERIC_S3"`; `:403` `deep_sleep_ua` → `"value": null, "verified": false, "source": "DFRobot publish no quiescent
  or deep-sleep figure for either SKU. …"`. As cited.
- `boards/xiao-esp32-c6.json:109` *"esp32.wake_on_ext0 does not exist on the C6 and Pin.irq(wake=DEEPSLEEP) silently does
  nothing; wake_on_ext1 and wake_on_gpio both exist. Verified on MicroPython v1.29."*; `:111-114` `"wake_api":
  "esp32.wake_on_ext1"`, `"single_polarity_for_all_pins": true`, `"simulated_by_wokwi": false`. As cited.
- Readers: `grep -n "deep_sleep\|micropython_port" scripts/*.py` → one line, `scripts/parts.py:1046` — `"deep_sleep_current":
  ["deep-sleep", "deep sleep"]`, a datasheet-search keyword for a *part* fact, not a reader of the board key (E). The
  diagnosis's "none" is right in substance; say *"no reader; the one hit is a datasheet keyword"*. `wake_capable_gpio` and
  `adc_gpio`: consumed for a decision by `assign_pins.py:129,131` only — as cited — but also read for shape by
  `boards.py:329-335` (`for key in ("wake_capable_gpio", "adc_gpio"): … "must be a list of GPIO numbers"`) and required
  at `:63`; the word "only" should be "only for a decision".
- `scripts/boards.py:91-94` *"Nothing noticed, because a role nobody consumes looks exactly like a role that is fine."*;
  `docs/2026-10-01-firmware-skill.md:103-107` *"The facts are already in the records, and nothing reads them … Only the
  first two are consumed (`assign_pins.py:129,131`). A 30-line `esp32` fake seeded from them … refused ext1 on the S3's
  GPIO47 and raised on `wake_on_ext0` for the C6"*; `:25-34` the table — wrong without notes 4 + 3 + 2 + 1 + 0 + 0 + 0 + 0
  = **10** of 4 + 4 + 4 + 4 + 4 + 4 + 4 + 2 = **30** runs (E, summed from the table). As cited.
- `tools/circuit-to-wokwi/lib/board.ts:63-67` declares `deep_sleep?: { wake_api; single_polarity_for_all_pins;
  simulated_by_wokwi }`; `grep -rn "simulated_by_wokwi\|deep_sleep" lib/ *.ts` → those two lines only (E). As cited.
- No page points at the block: `grep -rn "deep_sleep\|wake_on_ext\|single_polarity" commands skills docs/guide README.md`
  → `docs/guide/agents.md:461` alone, naming `deep_sleep_ua` for P126 (E). Holds.

**Verdict.** Holds. The two precision notes above do not change the mechanism: the facts a firmware harness would
enforce are recorded, validated for nothing beyond JSON, surfaced by no page or generated file, and consumed by no code.

## Missed root causes

Each is a rival explanation or a mechanism under a finding the diagnosis attributes elsewhere.

- **M1 · One naming rule per board, and the exception is a misnamed field.** For both library boards the "stand-in
  lacks the pin" cases are name mismatches (RC-1, point 1); the converter has the oracle in hand when it names the pin
  (`PinOracle`, `geometry.ts:58`) and the record lists the labels sharing a GPIO (`SDA`/`D4`, `TX`/43), so the emitter
  could pick a name the part knows at `mapping.ts:96` with no record change and no new CLI. The per-pad exception that
  exists today, `wokwi_power_pins`, carries renames and `null` and is validated and documented nowhere (E: RC-1,
  point 2). Rival to C1(a)–(c): the data and the code for the two latent cases are already in the converter; what is
  missing is the choice of label, a documented name for the override, and a validator for its keys and values.
- **M2 · The firmware check was cut, not never built** (RC-3, point 1; D: PO, 2026-09-29, `066c4af`). A proposal that
  re-adds one has to say why it will be used: the convention. The cut one looked for `config.py`; a spark project has
  `firmware/pins.py` since P36. The diagnosis's C4 conventions (`firmware/pins.py`, `firmware/main.py`) are that answer
  and should be stated as such.
- **M3 · Importing the pin map removed the independent statement the literal-comparison checks compared** (RC-3,
  point 2). The bin's `firmware-pins.ts`, the cut `check_firmware.py` and increment I all compare GPIO literals; with
  `import pins` there are none. So "generalise the bin's check" cannot be the plan; the plan is a use-against-map check,
  which proves less and must say so.
- **M4 · The tools list's role→tool mapping has no parameter.** `tools.find("firmware-image")` cannot take a chip, the
  contract `micropython-esp32-bin` is chip-blind, and the route for another chip is a per-project override nothing
  derives from or checks against the board record (RC-2, point 2). C2 guards the symptom at the image; the mechanism is
  that a board-dependent job is modelled as a store-wide one.
- **M5 · The flasher the PO's machine has predates the C6.** esptool 3.3 (E: `pip show`) has `ESP32C6BETAROM`
  (`IMAGE_CHIP_ID = 7`) and no final ESP32-C6 class; it cannot flash the XIAO, and the `13 = ESP32-C6` row of C2's
  table cannot be read from it (stays H). C3's `flasher` entry needs a minimum version, and the implementation must
  read the table from a newer esptool's `targets/`. `mpremote 1.29.0` is installed (E: `mpremote version`).
- **M6 · The `deep_sleep` block has no schema.** No reader means no validator: a typo in `single_pin_api` or a
  `simulated_by_wokwi` spelled wrong passes `--validate`, and the S3 has `single_pin_api` while the XIAO legitimately
  has not, so absence and typo look alike — the `PIN_ROLES` lesson at `boards.py:87-94`, repeated for the firmware
  facts. Any consumer (C4) must first be able to trust the shape.
- **M7 · The consumer the 2026-10-01 decision chose is the conversation, and nothing puts the facts in front of it.**
  The boundary (`firmware-and-tests.md:86-100`) makes records *"prose for the author"*; `pin_module` already writes the
  record's role notes into `pins.py` per pin (`assign_pins.py:407-410`) and writes nothing of `deep_sleep`. A header
  derived from the record (the wake API, "one level for all pins", the C6's missing `wake_on_ext0`, `simulated_by_wokwi`)
  is a few lines inside the boundary and gives RC-4's facts a consumer before any fake `esp32` exists — the "with
  notes" column of the skill document's table is exactly this delivery. Rival to C4 as the first consumer.
- **M8 · The classifier's mechanism is substring matching over free text**, and C1(d) adds a second pinned string. The
  converter has no structured output (E: its flags, `cli.ts:47-52`); every converter sentence that is a limit rather
  than a design fault will need its own pin until it has one. The diagnosis defers `--json` to "a later chore"; it is the
  mechanism.
- **M9 · The S3 note and the README sentence are true in part**, and C1/C6 "remove" them. The devkit is a superset of the
  FireBeetle's GPIOs (24 of 24, E: the registry against the record); the README's "labels only" holds for the library S3
  once two names are right and fails for a generic devkit standing in for a user's board. The fix is an amendment that
  states the exception and the two cases, not a deletion.

## The changes, judged

Against the PO's three criteria, plus mechanism-or-symptom, whether the named test catches the regression, whether the
message names where and why, whether a removal would do, and what it costs the current users.

**C1 — stand-in pins as a board fact read first.**
- *Mechanism or symptom:* (a)+(b) build a second channel to the oracle and print a note; (d) pins a second string.
  (c) defines the role by the diagnosis's own count, which is **by label**, and would mark 9 of the XIAO's 20 labels —
  among them `A0`–`A2`, its only ADC pins, and `SDA`/`SCL` — as "not on the simulator" though every one of those GPIOs
  simulates under a `D` name (E: RC-1, point 1). On the S3 it would spend `TX`/`RX` last with a reason that is false
  once the two names are mapped (E: the `TX` design simulated with one data line). For the two library boards the role
  would never be right; for a user's generic devkit (round 0) it would be. Symptom for the library, mechanism for the
  user's board — and it needs the emitter fixed first or the design still fails at the converter.
- *Simpler:* fix the name choice in `mapping.ts` with the oracle already there (M1); give the override a documented
  name (rename `wokwi_power_pins` or add `wokwi_pin_names`, keep the `null` meaning) and validate its keys against the
  record's labels and its values against the registry when the converter is present; for a GPIO with no name on the
  part, the converter's own sentence gains the remedy (*"the stand-in <part> has no pin for GPIO<n> (pad <label>); move
  <signal> or prove it on the bench"*). Only then is a "spend last" role worth its cost, and only for GPIOs with no
  known label at all.
- *Testable:* the `tests/test_boards.py` fake-converter test would test a note; a converter-side test (its own suite,
  run by `tests/test_converter.py`) that a design on `TX` and a design on the XIAO's `SDA` both emit a known pin is the
  test that catches the regression that matters.
- *Diagnosable:* the three sentences proposed are good in shape; the `assign_pins` one would be false for the library
  boards as (c) is specified.
- *Cost not in the diagnosis:* the bundle must change (board.ts's import-time read; `bundle.sh`; the sha pin at
  `tests/test_check_spine.py:850`), and `boards.py --validate` would start depending on node and the bundle for a note.

**C2 — `flash_image.py` refuses an interpreter built for another chip.**
- *Mechanism or symptom:* a guard at the symptom (M4 is the mechanism); a good guard — the fact is in 16 bytes.
- *Testable:* yes; the two fixtures exist; the table's literal for 9 is now E (esptool 3.3's source), 13 must be read
  from a newer esptool (M5) and cited.
- *Diagnosable:* the sentence names the file, both chips and the remedy. Good.
- *What breaks:* `--project DIR` "default: up from `--files`" resolves a board how? irrigation has **no**
  `.spark/board.json` (E: `ls ~/Development/irrigation/.spark/` → `project.json`, `rules.json`); the chain resolves its
  board from the requirements file's `board` key (`check_spine.py:334` `boards.load(project, requirements.get("board"))`)
  into `sim/board.json`. A project with no resolvable board must get *"could not check the chip"* and still write, or
  the documented line `flash_image.py --files firmware -o sim/flash-with-firmware.bin` (`commands/build.md:181`) stops
  working from a folder that has only `firmware/`.
- *Simpler:* the 16-byte read as a function in `flash_image.py`, called from `check_spine`'s simulation stage, where the
  resolved board and `--firmware IMAGE` already meet (`check_spine.py:473`, `:582-583`) — no new argument, one more
  sentence on a stage that already has three outcomes. `flash_image.py` keeps `--micropython` as the person's statement
  (the P31 decision) and gains an optional `--chip` for the standalone case.

**C3 — the step from the image to the board.**
- *Mechanism:* the step is absent; this adds it as two tools and a composed command. Within the 2026-10-01 boundary.
- *Testable/diagnosable:* the fake-tools test and the sentences are the right shape.
- *Not in the diagnosis:* the `flasher` entry needs a minimum version (M5: esptool 3.3 cannot flash a C6); the write
  offset and the 4 MB-into-16 MB question are flagged by the diagnosis and are bench facts (—).
- *What breaks:* nothing for current users; the bin keeps `deploy.sh`. The PO's choice between the script and the
  page stands as the diagnosis leaves it.

**C4 — a sixth check: the firmware against the pin map it imports.**
- *Mechanism:* for K67, yes — and it must name the cut (M2) and what kind of check it is (M3).
- *Would the test catch the regression:* the fixture → `VALVE4_VALVE_CTRL`, `BTNMODE_BUTTON` — yes. The mutation
  proof leans on `tools/mutate.py`, which scores a mutation "caught" when the mutated file no longer imports (K53):
  that over-count has to be fixed first or the table lies in C4's favour.
- *Does the message name where and why:* *"set to 0 at boot and never driven in 3 loops with soil at 2.9 V (dry) — a
  loop over fewer outputs than the design has?"* names where; the why is a guess marked as one. Honest.
- *What breaks:* (i) *"refuses `Pin(n)` for a GPIO the board has not"* seeded from `pins` refuses the XIAO's user LED:
  GPIO15 is in `pin_roles.onboard_led` and `strapping` and **not** in `pins` (E: the record; the Wokwi part exposes it
  as `$gpio15`). A plant-alarm firmware that blinks it would be refused for a pin the board has. "Has" must be `pins` ∪
  `pin_roles[*].gpio`, or the record needs an on-board list. (ii) irrigation's `check_all` gains a failing check beside
  K45's; the recorded outputs (README's "five in the journey's run", journey.md) change (K68's territory). (iii) The
  bin's firmware is at `firmware/micropython/main.py` and imports `config.py`, not `pins.py` → *not asked for*; fine, but
  say it. (iv) Running `main()` at import under a fake needs `sys.modules["time"]` replaced and an exception out of
  `sleep_ms` (the prototype's method); an `asyncio` firmware (the bin's shape) needs another cut-off. (v) The 4,000-line
  ceiling (`firmware-and-tests.md:135-139`) is the PO's, as the diagnosis says.
- *Simpler first step:* M7 — the record's deep-sleep facts into `pins.py`'s header — gives RC-4 a consumer for a few
  lines and no fake; C4 then builds on a shape the author has already read.

**C5 — a scenario measured against the pin map.**
- *Mechanism:* a count — the right thing for "passed over it". The bin's `scenario-pins.ts` (E: its header, 124 lines)
  is the precedent and says why the bin needed it (a board change left every `expect-pin` addressing `xiao`).
- *What breaks:* irrigation's scenario → `1 of 12`; as a **note**, nothing; as a problem, irrigation's simulation stage
  flips. Keep it a note, as proposed.
- Add: an `expect-pin` must also name a pin the *stand-in* knows (`38`, not `TX`) — the same registry answers it.

**C6 — the documents follow the code.**
- *Removes a true sentence:* the S3 note's superset claim is true of GPIOs (M9); amend it with the `TX`/`RX` exception
  and the two cases. The README sentence likewise.
- *Testable as written — no:* *"the retired sentence joins whatever list of retired phrases that check keeps"* —
  `tools/check_docs.py` keeps no such list; its checks are missing command/script names, flags, links and anchors,
  output notes, and runnable examples (E: the file's head and `tests/test_docs.py`'s twelve test names). The retired-phrase
  check is the **bin's** `tools/check-current-docs.py` (the bin's CLAUDE.md). In spark it would be a new check, size S,
  and should be proposed as one.

## What breaks for current users

- **The bin** (`~/Development/smartbin-local`): has its own `boards/`, `.spark/board.json`, `build-flash-image.py` and
  `deploy.sh`, and firmware under `firmware/micropython/` on `config.py`. C1–C3 change nothing it runs; C4's conventions
  do not find its firmware (*not asked for*); C5 does not reach its `sim/` through spark. A record change to the library
  S3 (C1/C6) reaches the bin only when it copies the record. The bin's `check-consistency.ts` already does C4's and C5's
  jobs for itself — with literals, which it has (`config.py`).
- **irrigation** (`~/Development/irrigation`): on the library S3 with twelve signals; the assigner never reaches `TX`/`RX`,
  so C1(c) moves no pin. C2's `--project` default must cope with no `.spark/board.json` (above). C4 turns its `check_all`
  from one FAIL (K45) into two, which is the intended finding and a change to the recorded outputs; C5 prints `1 of 12`.
  Its `sim/micropython-esp32s3.bin` is the real S3 build (chip id 9, E), so C2 passes it.
- **plant-alarm** (`~/Development/plant-alarm`): XIAO + `sen0193-soil-moisture` + `max98357a-dfr0954` (E: its
  `requirements.json`), no firmware, no `sim/`. Today it stops at the footprint (P121). Once it builds, C1(c) as specified
  would label `A0`–`A2` (its only ADC pins, where the soil probe must land) and `SDA`/`SCL` "not on the simulator" with a
  false reason; C4's fake would refuse GPIO15, the user LED, if "has" is read from `pins` alone.

## Searches

None on the web, and no Espressif-docs query. Read locally: the repositories named above; the Wokwi part registry
through the converter's `node_modules` (`@wokwi/diagram-lint` 0.1.1, offline); esptool 3.3's source under the PO's pyenv;
the diagnostician's kept scratch artefacts (`chain/keep1`, `k32`, `k67`, `chipid`, `assign`), re-run where a claim rested
on them; `git log`/`git show` on `efcc4cc` and `066c4af` (read-only). No `gh` call was made.
