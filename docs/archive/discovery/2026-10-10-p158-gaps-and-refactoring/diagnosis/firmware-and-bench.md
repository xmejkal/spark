# P158 part 1 — diagnosis: firmware-and-bench

Written 2026-10-10 by the area's diagnostician, against spark 0.8.1 (main `a8aa34d`), for the catalogue rows K32, K66
and K67 (`../catalogue.md`). Every claim is tagged: **E** a pointer (file:line in `~/Development/spark` unless another
repository is named; a command and what it printed), **H** a claim with its source only, **D** a decision (who, when),
**—** unknown. Every run below went against a copy of the PO's store at `<scratch>/store` with `SPARK_HOME`, `HOME` and
`TMPDIR` set on the command, verified once with `env` (E: the three variables printed, pointing into `<scratch>`); the real
store `~/.local/share/spark` was never run against or written. The chain was run in `<scratch>/chain/`, a copy of
`~/Development/irrigation` without its `sim/`, `dist/` and `.git`, with `node_modules` linked, so its `tsci` could build.
The scope is the computed task's: from a built board to running firmware — `pins.py`, `flash_image.py`, the step from the
image to a board (★C6), the bench "not yet" (P79), the firmware direction of 2026-10-01, the C6's MicroPython wake limits
and the unmeasured deep-sleep numbers (C11). The PO's criteria for every change: *"well designed so its well testable and
understandable where a mistake is happening and why"* (D: PO, 2026-10-10) — testability, diagnosability, simplicity.

The one user line the harness relayed for this run asks whether *"some new file formats or synch libraries or
techniques could be used from an existing library"* for the store. This area has one concrete instance of that, and it
is in RC-1 and C1: the facts round 0 could not find are already carried by a library the plugin bundles.

## 1. Root causes

### RC-firmware-and-bench-1 · The simulator's pin vocabulary is consulted at the last stage by the converter, while the pin is spent at the first stage by the assigner, and the two never meet in a record or a check

**where** · `scripts/assign_pins.py:143-157` (`candidates` is built from `board["pins"]` alone; the only disqualifying
role is `UNAVAILABLE_ROLES = ("strapping",)`, `:61`) · `scripts/boards.py:305-311` (`validate` compares `power_pads`
against `wokwi_power_pins` and nothing else against the simulator; its own comment: *"Nothing compared the two lists; a
person running the chain on one project was the check"*) · `tools/circuit-to-wokwi/lib/geometry.ts:58-106` (the
`PinOracle`: the registry bundled in `@wokwi/diagram-lint`, *"137 parts, offline"*, `isValidPin` at `:103-106`) ·
`lib/emitters/wokwi.ts:169-181` (the check and the sentence `"<pin>" is not a pin of <type>. Valid pins: …`) ·
`lib/mapping.ts:92-109` (the board's pin names are derived from `board.pins` as `String(gpio)` when `wokwi_pin_naming` is
`gpio`, so there is no place to say a board pin is absent, while a PART mapping can say so with `null`, `:53-59`) ·
`scripts/check_spine.py:216-221` and `:482-489` (a converter failure is `PROBLEMS` — *"no diagram was produced"* — unless
its text contains the one string `no Wokwi part is mapped`) · `boards/README.md:95-97` (*"a stand-in costs only the
silkscreen labels in the picture"*) · `boards/firebeetle2-esp32s3.json`, key `//wokwi_part_type` (*"it exposes GPIO 0-21
and 35-48 - a superset of every pin this board brings out"*) and `wokwi_is_stand_in` at `:115`.

**why** · A board record names the Wokwi part that stands in for it (`wokwi_part_type` is a required key,
`boards.py:62-63`), but which pins that part has is known only to the converter's registry, read at the simulation stage
after the board has built. The assigner spends GPIOs by capability and role cost from the record alone, so it spends a
GPIO the stand-in lacks with the same confidence as any other, and `boards.py --validate` says `ok` because nothing in
the contract mentions the stand-in's pins (E: `boards.py --validate --project <scratch>/validate` → `active
firebeetle2-esp32s3 (library): ok`, `xiao-esp32-c6 (library): ok`, exit 0). The record has no field that could carry
the fact — the `null` convention exists for parts (`mapping.ts:53-59`), not for the board — and the one flag that says
"this is a stand-in", `wokwi_is_stand_in`, is read by no code: `grep -rn wokwi_is_stand_in` over the repository without
`node_modules` finds the TypeScript type (`lib/board.ts:35`), the S3 record (`:115`) and prose; no script or emitter (E,
2026-10-10). The documents then say the opposite of the mechanism. Round 0 met this on a C6 record (K32); it is latent
on both library boards:

- E · the registry, asked offline through the converter's own `node_modules` (`<scratch>/registry/standin-pins.mjs`,
  2026-10-10): `board-esp32-s3-devkitc-1` has 44 pins (0–21, 35–42, 45–48 as numbers; `TX`, `RX`, `RST`, `3V3.1`,
  `3V3.2`, `5V`, `GND.1`–`GND.4`); `board-esp32-c6-devkitc-1` 32 pins (0–13, 15, 18–23, `TX`, `RX`, `NC0`, `NC1`, …);
  `board-xiao-esp32-c6` 15 pins (`D0`–`D10`, `$gpio15`, `3V3`, `5V`, `GND`).
- E · against the library records: `firebeetle2-esp32s3` on the S3 devkit — **2 of 25** header pins absent on the
  stand-in, `TX=GPIO43`, `RX=GPIO44` (the devkit names those pads `TX` and `RX`, the converter emits `"43"` and `"44"`);
  `xiao-esp32-c6` on its own Wokwi part — **9 of 20** absent, `SDA`, `SCL`, `SS`, `MOSI`, `MISO`, `SCK`, `A0`, `A1`,
  `A2` (the Wokwi part knows only `D0`–`D10`, the record keys the same GPIOs twice and the assigner chooses the vendor
  label: `assign_pins.py xiao-i2c.json` → `SDA SDA GPIO22`, `SCL SCL GPIO23`, E); the S3 record moved onto the C6 devkit
  — **7 of 25** absent, among them `D3=GPIO38` and `D10=GPIO14` — GPIO14 being the pin that stopped round 0, which the C6 FireBeetle brings out as D3.
- E · the assigner does spend the S3's two absent pads: 22 plain signals → `SIG20 TX GPIO43 … taken only because
  nothing free was left [console_uart, not_wake_capable]`, `SIG21 RX GPIO44 …` (`assign_pins.py many.json`, exit 0).
- E · a design wired to the S3's `TX` pad builds and cannot be simulated: one button, its trace hand-moved from `.Mcu >
  .D3` to `.Mcu > .TX` in the kept `board.tsx`, `npx --no tsci build board.tsx` → 6 `pcb_trace`, 0 errors; the converter
  on that `circuit.json` with the current S3 record → `1 problem(s) converting the board: - "43" is not a pin of
  board-esp32-s3-devkitc-1. Valid pins: … (component mcu, pin TX, net connectivity_net4)`, exit 1, no diagram
  (`<scratch>/chain/run-tx.txt`).
- E · round 0's shape reproduced offline: irrigation's built `circuit.json` converted against the current S3 record →
  `wrote out-s3.json`, exit 0; the same record with `wokwi_part_type` set to `board-esp32-c6-devkitc-1` → `3 problem(s)`
  (`"38"`, `"14"`, `"3V3.1"` are not pins of the C6 devkit), exit 1, no diagram (`<scratch>/k32/run-c6.txt`).
- E · the XIAO case cannot be reached through the chain today: `check_spine.py xiao-tof.json` stops at
  `[????] footprint no footprint could be generated for xiao-esp32-c6 … physical.header (no header geometry at all)`,
  exit 2 (`<scratch>/chain/run-xiao.txt`; P121). The 9-of-20 figure stands on the registry and `mapping.ts:96` alone.

**kind** · design.

**explains** · K32 (and the latent S3/XIAO cases above, which no row carries).

**how a person or an AI agent would have known** · Only at the end, from the converter's `Valid pins:` list — which is
the list round 0 used to fix the power-pin names (`council/round-0-runner.md:24-25`). Before that point every output says
the opposite: `--validate` prints `ok`, `boards/README.md:97` says the stand-in costs only labels, the S3 record's note
says the devkit is a superset. At the end the stage says `[!!] simulation no diagram was produced`, which the three-outcome
vocabulary defines as *"a defect in the design, named"* (`commands/build.md:100-105`) — the design was fine. The
sentence names a pin number and a part, not the cause (the board has the GPIO, the stand-in has no pad for it) and not
the remedy (which signal to move). The classification rests on one string (`check_spine.py:216`), the same shape audit
B11 fixed for the "no Wokwi part" case (`tests/test_check_spine.py:721-733`); the converter has no structured output to
read instead (its flags: `--check --chips --circuit --help --mapping --out`, E). And the stage is untested by its own
admission: *"no test on this machine reaches run's simulation stage"* (`check_spine.py:511-514`).

### RC-firmware-and-bench-2 · The flash image is built for the simulator, the chain's idea of "firmware" ends at that image, and the board's chip never reaches the image builder

**where** · `scripts/flash_image.py:72-76` (`interpreter_path`: the given file, else `tools.find("firmware-image")` — a
role resolved per store, not per board) · `:79-86` (the arguments: `--micropython`, `--files`, `--config`, `-o`; no board,
no project; E `--help`) · `:16-17` (*"made general here for backlog P31: any project, any file tree, the board's chip
named on the command line by the image"*) · `data/tools.json` → `roles` (11 roles: `pdf-text`, `simulator`,
`board-engine`, `diagram-converter`, `js-runtime`, `littlefs`, `firmware-image`, `parts-search`, `chip-docs`, `bench`,
`ts-runtime`; `bench` is the sigrok MCP, `firmware-image` is one download, `micropython-esp32s3`, E) ·
`docs/guide/journey.md:911-914` (*"Not yet. No command does this yet"*), `commands/build.md:186-188`, `README.md:77` ·
`docs/archive/2026-10-01-firmware-skill.md:135-136` (*"nothing in spark or the bin says how to put MicroPython on a board
(`esptool`, `mpremote` appear nowhere). That is P56's increment III"*) · `docs/archive/2026-10-01-firmware-and-tests.md:141-144`
(increment III: *"the bench. Mostly documents"*).

**why** · `flash_image.py` was lifted from the bin's `tools/build-flash-image.py` for the headless simulator, where the
image is the only way files reach the board (`flash_image.py:9-14`), and it generalised the bin's script by removing the
board from its inputs. The bin's version names the interpreter after the resolved board's chip —
`MICROPYTHON_IMAGE = SIM / ("micropython-%s.bin" % RESOLVED_BOARD["chip"])` — with a comment recording why: *"a constant
here that named a different chip made the guard pass and the script then fail looking for the previous board's build.
Which is exactly what happened when the board changed from an ESP32-C6 to an S3"* (`~/Development/smartbin-local/tools/
build-flash-image.py:40-45`, E). spark's version takes the interpreter from a store-wide role and asks no board, so the
tools list's S3 build goes into every project's image unless the person remembers `--micropython`, and an interpreter for
the wrong chip is packed without a word: E · `flash_image.py --micropython <a file whose image header says chip id 13>
--files … -o out.bin` for a project whose board is the S3 → `wrote … 4096 KB`, exit 0 (`<scratch>/chipid/`). The fact that
would refuse it is in the file's first 16 bytes: an ESP image header carries the chip id at offset 12, and the real
`ESP32_GENERIC_S3` build the PO's store holds reads `magic=0xe9 chip_id=9` there (E: `~/Development/irrigation/sim/
micropython-esp32s3.bin`, read 2026-10-10; that 9 means ESP32-S3 and 13 means ESP32-C6 is H — esptool's image-header
table, from memory, to be read from esptool's source when implemented). Downstream of the image there is nothing: no
role in the tools list puts bytes on a board, no script composes `esptool`/`mpremote` from the facts the record already
holds (`chip`, `micropython_port`), and no page says the step exists — E: `grep -rli "esptool\|mpremote" README.md
docs/guide commands skills` → **0** files (2026-10-10; the same grep the user lens ran 2026-10-09, `council/user.md:15`).
The bin has the step, hand-written: `deploy.sh` (`mpremote rm/mkdir/cp … :` then `mpremote soft-reset`,
`~/Development/smartbin-local/firmware/micropython/deploy.sh:15-28`, E) — for a board already running MicroPython, which
the bin's README then names a XIAO's pins for (P58, #5). It was named as the missing increment on 2026-10-01 and is filed
nowhere but as the P79 breadboard epic (#16, body: *"Today spark's only output is a PCB … nothing tells a person which wire
goes from which module pin to which GPIO"*) and as the proposed story in `../2026-10-09-p100-real-use/items.md:57-66`.

**kind** · design (the step is absent) and implementation (the dropped chip check).

**explains** · K66 (★C6, USER-7, A5, PO-11).

**how a person or an AI agent would have known** · The step's absence is said in prose — README's table, the Bench
section — and nowhere else; the recorded setup picture shows `[????] firmware-image … is not installed` and nothing
about a flasher (`docs/guide/journey.md:605`). The wrong-chip image says nothing anywhere: it fails inside a paid Wokwi
run or on the bench as a board that prints nothing, and the only symptom the script names is the littlefs one
(`flash_image.py:14`: *"the simulated board boots to a bare REPL with no main.py"*), which is a different fault.

### RC-firmware-and-bench-3 · The firmware is outside every check: the pin map is exported and never compared back, no check reads firmware, the only executor of firmware is the metered simulator, and a scenario's assertions are not measured against the pin map either

**where** · `scripts/check_all.py:281-292` (five checks: `vendor-truth`, `buildability`, `the-order`, `physics`,
`rules-vs-netlist`) and `:295-305` (`CONVENTIONS` has `circuit`, `rules`, `package` — no firmware; the comment at
`:297-300` records a `--firmware` argument that *"never passed … so the flagship check was permanently unasked"*) ·
`scripts/assign_pins.py:392-411` (`pin_module` writes `pins.py`; nothing in `scripts/` imports or parses one back) ·
`docs/archive/2026-10-01-firmware-and-tests.md:24-26` (*"`grep -rl "import machine|fake_machine|FakePin"` over `scripts/ tools/
skills/ commands/` returns nothing"*), `:59` (tier T0: *"firmware GPIO ↔ board file ↔ netlist; declared-but-undriven
pins … spark can generate — it owns both sides"*), `:122-126` (increment I) · `~/Development/irrigation/sim/scenarios/
wet-and-dry.scenario.yaml:19-22, 29-32` (two `expect-pin` steps, both `pin: 38`) and `sim/runs/2026-09-29-wet-and-dry.log`
(*"Scenario completed successfully"*) · the bin's `tools/circuit-to-wokwi/check-consistency.ts:1-13` and
`lib/checks/firmware-pins.ts:1-16` (*"Three independent statements have to agree … None is derived from another, which
is what gives the check teeth"*; `lib/checks/` is 438 lines by `wc -l`, E).

**why** · spark owns both sides of the T0 contract — it writes `pins.py` from the same assignment it traces onto the
board — and compares neither side with the firmware. `check_all` discovers its inputs by convention and the conventions
name no firmware, so a project's `firmware/` is invisible to the one command that judges a project. Nothing in the plugin
can execute a line of MicroPython on a Mac, so the only thing that ever runs a generated project's firmware is Wokwi, and
a Wokwi scenario proves exactly what it asserts: irrigation's asserts one GPIO of the twelve in its pin map, twice, and
passed (E, the files above). The two defects that scenario passed over are visible in a second with a recording fake
`machine` of 45 lines and no simulator (E, `<scratch>/k67/t0_check.py`, 2026-10-10, soil driven to a dry reading so a
valve has reason to open):

```
main.py ran at import; 3 loop(s) of its while True under the fake machine
  VALVE4_VALVE_CTRL      GPIO13  constructed, never driven or read again: constructed OUT; init value=0
  BTNMODE_BUTTON         GPIO18  NEVER TOUCHED: pins.py assigns it; the firmware constructs no Pin or ADC on it
  STATUS_LED             GPIO15  constructed, never driven or read again: constructed OUT; init value=1
3 of 12 pin-map constants have no firmware behind them
```

(`VALVE1`–`3` were driven to 1; the LED's single write at boot is legitimate — a check must say which class a line is in,
see C4.) The first two are P59's findings (#7 body: `GPIO13 (Valve4) is set to 0 at boot and never driven again`;
`BUTTON_PIN = 18` is never read) — `main.py:76` loops `probes[:len(valves)]`, three probes over four valves, and
`main.py:19` assigns `BUTTON_PIN` and never uses it (E). The precondition P59 names is also E: `import main` with a fake
`machine` and a `time` whose `sleep_ms` sleeps runs `main()` at import (`main.py:99`) and never returns — `timeout 5`
→ exit 124. So the paid tier ran and the free tier does not exist, which is the whole of K67.

**kind** · design.

**explains** · K67 (PO-6, PO-14, P59 #7, P74 #8; P130 #64 is the scenario half).

**how a person or an AI agent would have known** · Nothing in spark's output. The scenario log ends in *"completed
successfully"* and says nothing of what fraction of the design it exercised; `check_spine`'s simulation stage writes
`WHAT-THIS-CANNOT-SHOW.md`, which is about the stand-ins (`scripts/sim_project.py:107-123`), not about coverage; `check_all`
does not know the firmware is there. P59's defects were found by a lens writing the check by hand on 2026-10-01
(`docs/archive/2026-10-01-firmware-and-tests.md:36-41`).

### RC-firmware-and-bench-4 · The board facts a firmware harness would enforce are recorded and consumed by nothing

**where** · `boards/firebeetle2-esp32s3.json` → `deep_sleep` (`wake_api`, `single_pin_api`,
`single_polarity_for_all_pins`, `simulated_by_wokwi`), `micropython_port`, `power.deep_sleep_ua` (`value: null,
verified: false` — honest; E), `wokwi_is_stand_in` · `boards/xiao-esp32-c6.json` → `deep_sleep` (`wake_api`
`esp32.wake_on_ext1`, `simulated_by_wokwi false`, and in `//deep_sleep`: *"esp32.wake_on_ext0 does not exist on the C6
and Pin.irq(wake=DEEPSLEEP) silently does nothing"*) · readers: `grep -n "deep_sleep\|micropython_port" scripts/*.py`
→ none; `wake_capable_gpio` and `adc_gpio` are read by `assign_pins.py:129-131` only (E, 2026-10-10) ·
`scripts/boards.py:87-94` (the PIN_ROLES comment: *"a role nobody consumes looks exactly like a role that is fine"*) ·
`docs/archive/2026-10-01-firmware-skill.md:103-107` (*"The facts are already in the records, and nothing reads them … A 30-line
`esp32` fake seeded from them, written in scratch, refused ext1 on the S3's GPIO47 and raised on `wake_on_ext0` for the
C6"*) · the converter's type declares `deep_sleep.simulated_by_wokwi` (`lib/board.ts:63-67`) and uses it nowhere (E,
grep of `lib/`).

**why** · The C6's MicroPython wake limits and the S3's single-polarity ext1 are exactly the facts a firmware author gets
wrong and a bench then pays for (`firmware-skill.md:25-34`: 10 of 30 runs wrong without notes), and they sit in the records
as `//` prose beside booleans no code reads. The deep-sleep draw (C11) is the same: `deep_sleep_ua` is `null` in the S3
record with the right reason — DFRobot publish none, the datasheet's footnote sits on light-sleep, the PO's N16R8 is not the
measured variant (`../2026-10-09-p100-real-use/brief.md:56`) — and nothing asks for it, so it stays a bench item nobody
is pointed at (B15/B16 in the bin; the tech lead's Q6, whether the PO owns a meter that reads µA, —). The harness that
would consume them is P56's increment II, not built; its budget argument is at `firmware-and-tests.md:135-139`.

**kind** · design.

**explains** · K67 (its "nothing checks the firmware" half is the missing consumer); the scope's C6 wake limits and C11.

**how a person or an AI agent would have known** · By reading the record's `//` notes before writing firmware. No
output points at them; a firmware arming `esp32.wake_on_ext0` on the C6 fails only on hardware.

### Found on the way, outside this area (reproduced, for the board-records diagnostician)

E · The library S3 record cannot be built once a design spends `MOSI` or `MISO`: 22 buttons on the S3 →
`[!!] build 2 error(s): source_trace_not_connected_error`; the two errors in `dist/board/circuit.json`: `Could not find
port for selector ".Mcu > .MOSI". Component ".Mcu > " found, but does not have pin "MOSI". It has no ports` and the same
for `MISO` (`<scratch>/chain/keep22/`, 2026-10-10). The footprint's pads are hinted `MI`/`MO` from `header_order`
(`boards/firebeetle2-esp32s3.json` → `physical.header_order.row_18`), the trace is written to the record's key — K23's
mechanism, on the library's own board, not only on round 0's.

## 2. What the design gets right and must be kept

- **Three outcomes, never two**, with the exit code saying which (`scripts/outcomes.py:19-28`; `commands/build.md:100-105`).
  Every change below adds a sentence to one of the three; none adds a fourth.
- **The converter checks pin names offline before writing anything**, against a registry it bundles (`lib/geometry.ts:
  48-57`), and takes its board from `SPARK_BOARD_JSON` with deliberately no default (`lib/board.ts:77-88`). RC-1's fix is
  to ask that oracle earlier, not to build another. This is also the one answer this area has to the relayed user line:
  the stand-in's pins are an existing library's data (`@wokwi/diagram-lint` 0.1.1, with `REMOTE_BOARDS_URL =
  https://wokwi.github.io/wokwi-boards/boards.json` for a refresh, E: the package in the converter's `node_modules`), not
  facts to record by hand in a board file.
- **A part mapping can say "the stand-in has no such pin"** with `null`, as a recorded decision (`lib/mapping.ts:53-59`).
  C1 gives the board the same sentence, derived rather than typed.
- **The record rule for stand-ins**: a built-in part standing in must say what differs (`scripts/parts.py:502-504`),
  and the simulation stage prints and files it (`WHAT-THIS-CANNOT-SHOW.md`, `scripts/sim_project.py:75-123`). "A pass here
  is not a bench" is already said; C5 adds how much of the design the pass covered.
- **`wokwi_power_pins` is checked at validate time** against the pads a board can wire (`scripts/boards.py:305-311`) —
  the right shape, applied to power pads only. C1 extends it to GPIO pads instead of inventing a second mechanism.
- **`pins.py` is plain integers**, one per signal, each with its pad, the reason it was chosen and the record's note on
  the pin; a name Python cannot spell is refused (`scripts/assign_pins.py:392-411`). Plain integers import under CPython
  and MicroPython alike (P60), which is what makes C4 possible without a simulator.
- **Roles are a cost with a printed reason** — *"taken only because nothing free was left"* (`assign_pins.py` output,
  E). C1 is one more role with one more reason in the same sentence shape.
- **The flash image's constants are pinned against MicroPython's own source as literals in the test**, never read back
  from the module (`tests/test_flash_image.py:18-27`) — the P54 lesson; C2 adds the chip id the same way.
- **The tools list is data** — roles, contracts, checked downloads with a sha256 (`data/tools.json`;
  `micropython-esp32s3`). C3's two tools are two entries, not code paths.
- **The boundary of 2026-10-01**: spark emits what is derived from records it holds and nothing that encodes behaviour
  (`docs/archive/2026-10-01-firmware-and-tests.md:86-100`). Every change here stays inside it: a composed command, a comparison,
  a count.
- **`simulation_detail` was split out of `run` so it could be tested at all** (`check_spine.py:507-514`). The pattern,
  not the exception: C1(d) tests the classifier the same way.
- **The bin's `check-consistency.ts` compares three independent statements against the board design, not against each
  other** (`~/Development/smartbin-local/tools/circuit-to-wokwi/lib/checks/firmware-pins.ts:1-16`). C4 generalises that
  shape; it does not re-derive one statement from another and call it a check.

## 3. Changes

### C1 · The stand-in's pins are a board fact the chain reads first, not a sentence the converter prints last
- **kind** bug · **size** M
- **fixes** K32; the latent S3 (`TX`/`RX`) and XIAO (`SDA`/`SCL`, …) cases above.
- **removes** `boards/README.md:95-97`'s sentence that a stand-in *"costs only the silkscreen labels"*; the S3 record's
  `//wokwi_part_type` claim of *"a superset of every pin this board brings out"*; and `wokwi_is_stand_in` as a flag no
  code reads — either (b) below words its note with it, or it goes.
- **adds** (a) the bundled converter answers `--part-pins <wokwiType>` with the registry's pin list as JSON (the
  `PinOracle` already exists; ~15 lines in `cli.ts`); (b) `boards.py --validate` asks it through
  `tools.find("diagram-converter")` and prints, per board, the header pins the stand-in has no pad for, as a note, not
  a refusal — a simulator's limit is not a board fault — and when node or the converter is absent prints
  `could not check the stand-in's pins: <the tools list's sentence>` rather than nothing; (c) `assign_pins` reads the
  same list (through the resolved board or a `--stand-in-pins` input written by (b) into `.spark/board.json`, the
  resolved file every consumer already reads) and gives those GPIOs a role `not_on_simulator` with a cost like
  `console_uart`'s, so they are spent last, each with the reason; (d) `check_spine` classifies the converter's
  `"<n>" is not a pin of <type>` for component `mcu` as `COULD_NOT_RUN` naming the stand-in and the remedy, pinned on the
  converter's own sentence the way `CONVERTER_HAS_NO_PART` is (`check_spine.py:216`) until the converter has a
  structured `--json` (a later chore).
- **testable** `tests/test_boards.py`: a definition whose stand-in list (a fake converter on PATH, the `fake_compiler`
  pattern of `tests/test_sim_project.py:40-44`) lacks one of its GPIOs → the note names `label=GPIO<n>` and the stand-in;
  a definition whose stand-in has every pin → no note; no converter → the could-not-check sentence.
  `tests/test_assign_pins.py`: with one plain signal and two free pins of which one is `not_on_simulator`, the simulated
  pin is taken; with every simulated pin spent, the other is taken with the reason. `tests/test_check_spine.py`: the
  text above → `COULD_NOT_RUN`; the sentence for another component → still `PROBLEMS`.
- **diagnosable** `boards.py --validate`: `firebeetle2-esp32s3 (library): ok — the Wokwi stand-in board-esp32-s3-devkitc-1
  has no pad for TX=GPIO43, RX=GPIO44 (it names those pads TX, RX); a design on them builds but cannot be simulated —
  assign_pins spends them last`. `assign_pins`: `BTN21_BUTTON TX GPIO43 … the simulator's stand-in has no pin for GPIO43:
  a design on it builds but cannot be simulated — taken only because nothing free was left [console_uart,
  not_on_simulator]`. `check_spine`: `[????] simulation the stand-in board-esp32-s3-devkitc-1 has no pin for GPIO43 (pad
  TX): the design built; move BTNTX_BUTTON off TX to simulate it, or prove it on the bench`.
- **proof the PO can read** the three commands above on the library S3 print those three sentences; the one-button
  design moved to `TX` (`<scratch>/chain/keep1`) ends `[????]` instead of `[!!]`; round 0's C6 record stops at the pin
  map with `D3=GPIO14` named as not on the stand-in, before any build.

### C2 · `flash_image.py` refuses an interpreter built for another chip
- **kind** bug · **size** S
- **fixes** the silent half of K66's path (RC-2's implementation part).
- **removes** nothing.
- **adds** a `--project DIR` argument (default: up from `--files`, as the chain resolves a project) that resolves the
  board and reads its `chip`; a 3-line read of the image header (magic `0xE9` at offset 0, chip id at offset 12) and a
  chip-id table read from esptool's source at implementation and cited in the module (today H: 9 = ESP32-S3,
  13 = ESP32-C6); a refusal before any byte is written.
- **testable** `tests/test_flash_image.py`: an interpreter whose header says 13 for an `esp32s3` board → `EXIT_COULD_NOT_RUN`
  and the sentence; 9 → the image is written (the two fake files of `<scratch>/chipid/` are the fixtures); the table's
  literals come from esptool's source, never from the module (the P54 rule the file already follows).
- **diagnosable** `flash_image.py: <file> is a MicroPython build for chip id 13 (esp32c6) but firebeetle2-esp32s3 is an
  esp32s3 (chip id 9) — refused, nothing written. The tools list's firmware-image is the S3 build; for a C6 pass
  --micropython <its .bin from micropython.org/download/ESP32_GENERIC_C6>`.
- **proof** the command that exited 0 in RC-2 exits 2 with that sentence; the real S3 build still packs.

### C3 · The step from the image to the board: two tools and the commands spark composes from facts it already holds
- **kind** story · **size** M (the script and its tests; the page is part of it)
- **fixes** K66 (★C6, USER-7, A5; PO-11's "one shared piece of work").
- **removes** the Bench section's *"Not yet. No command does this yet"* (`docs/guide/journey.md:913`) and the README
  row's `—` (`README.md:77`).
- **adds** two entries in `data/tools.json` — `esptool` (role `flasher`) and `mpremote` (role `device-files`), both
  `kind: pip`, with their install lines — and one script, `flash.py`, that composes from facts spark holds: the board's
  `chip` and `micropython_port` (the record), the interpreter (the tools list, checked by C2), the project's `firmware/`
  (the same tree `flash_image.py` packs); prints the two commands it would run (`esptool … write_flash` of the
  interpreter, then `mpremote cp` of the files and a reset) and runs them only after the person's yes, the way
  `tools.py --install` does; reports a board not found, a tool not installed, and a chip mismatch as could-not-run. Writes
  no behaviour: the firmware is still the conversation's (D: PO, 2026-10-01, `firmware-and-tests.md:17-18`). The journey's
  Bench section shows the command, its printed plan, and what the board prints first.
- **testable** fake `esptool` and `mpremote` on PATH recording their argv (the `fake_compiler` pattern): the test asserts
  the argv carries the board's chip and the interpreter's path; a missing tool → the tools sentence and exit 2; a chip
  mismatch → C2's sentence, no command run; the dry run runs nothing.
- **diagnosable** `[????] flasher esptool is not installed — install: python3 -m pip install --user esptool`;
  `flash.py: no board answered on a USB port — plug it in, or name it with --port`; `flash.py: the image is for esp32c6,
  firebeetle2-esp32s3 is an esp32s3 — refused, nothing written`; on success, the last line is the board's own first
  serial line, quoted.
- **proof** on the owned FireBeetle (D: the only board, `memory/smartbin-parts-owned.md`): `flash.py --project .` prints
  its plan, the PO says yes, the board prints its first line, pasted on the card. Two facts this cannot settle from a desk
  and must be read or measured at implementation: the write offset per chip (H: `0x0` for the S3 and C6, from
  micropython.org's per-board pages, not read today) and whether the 4 MB image `flash_image.py` builds can be written
  whole to the PO's 16 MB N16R8 or whether files must go by `mpremote` (—; see §4).
- **alternative, cheaper** a page with the two commands and no script (size S). It cannot check the chip, cannot say
  could-not-run, and leaves the port and the first line to the person. The PO chooses; P79's breadboard shape (#16) is his
  to set, and this is the smallest piece under it, proposed, not decided.

### C4 · A sixth check: the firmware against the pin map it imports
- **kind** story · **size** M (the fake `machine` seeded from the board record is the bulk; P56 increment II's budget
  question at `firmware-and-tests.md:135-139` is the PO's)
- **fixes** K67 (P59 #7, P74 #8), and gives RC-4's facts their first consumer.
- **removes** nothing in spark (later, the bin's private `firmware-pins.ts` can retire in favour of the plugin's — the
  bin's business).
- **adds** `check_all` entry `firmware-vs-pin-map` with conventions `firmware/pins.py` and `firmware/main.py`; a recording
  fake `machine` seeded from the resolved board that refuses `Pin(n)` for a GPIO the board has not, `ADC` outside
  `adc_gpio`, a wake source outside `wake_capable_gpio`, `esp32.wake_on_ext0` where `deep_sleep.single_pin_api` is absent
  (the C6); an import of the firmware under a loop cap (a fake `time.sleep_ms` that ends the loop after N) and a wall
  clock; three findings reported separately, each saying what it can conclude: *runs at import* (P59: `main()` at module
  scope), *never touched* (a constant no `Pin`/`ADC`/bus ever took — robust), *not shown driven or read by this run*
  (input-dependent, said so, with the inputs used). A project with no `firmware/` → `not asked for`, as `the-order` is.
- **testable** a fixture with the irrigation stub's shape (12 constants; a loop over 3 of 4 outputs; an unread input) →
  exit 1 naming `VALVE4_VALVE_CTRL` and `BTNMODE_BUTTON`; the same with the loop over all four → the first finding gone;
  `tools/mutate.py` pointed at the fixture (the P56 doc's own suggestion, `:109-112`): every constant's use mutated
  → the check names it or the mutation table says which escaped.
- **diagnosable** `[firmware-vs-pin-map] BTNMODE_BUTTON = GPIO18 (pad D6): in pins.py and never constructed as a Pin —
  the requirements ask for BtnMode's button and the firmware never reads it`; `VALVE4_VALVE_CTRL = GPIO13 (pad D11): set to
  0 at boot and never driven in 3 loops with soil at 2.9 V (dry) — a loop over fewer outputs than the design has?`;
  `main.py runs at import (main() at module scope, line 99) — nothing can test it; put it under if __name__ ==
  "__main__"`; `Pin(99): firebeetle2-esp32s3 has no GPIO99 (its header: GPIO0-21, 38, 43, 44, 47)`.
- **proof** the 45-line prototype's output in RC-3 (`<scratch>/k67/t0-output.txt`), free and without a simulator, beside
  the paid scenario that passed over the same file.

### C5 · A scenario is measured against the pin map before it spends a minute
- **kind** story · **size** S
- **fixes** K67's "passed over it" half; gives P130 (#64) a yardstick.
- **removes** nothing.
- **adds** a comparison, in C4's check or `sim_project`: every `expect-pin` in `sim/scenarios/*.yaml` names a GPIO that is
  in `pins.py`, and the report counts the pin-map outputs no scenario asserts; with `deep_sleep.simulated_by_wokwi`
  false, a scenario that waits for a GPIO wake is named as one that cannot pass here (the bin's `sim/README.md:159-163`
  experiment, recorded in the record). The bin's `lib/checks/scenario-pins.ts` (124 lines) is the precedent.
- **testable** a scenario asserting GPIO 38 against a pins.py of 12 → `1 of 12`; a scenario asserting a GPIO not in
  pins.py → named with the constants that are.
- **diagnosable** `wet-and-dry.scenario.yaml asserts 1 of 12 pin-map constants (VALVE1_VALVE_CTRL on GPIO38); never
  asserted: VALVE2_VALVE_CTRL, VALVE3_VALVE_CTRL, VALVE4_VALVE_CTRL, STATUS_LED, …; a pass proves those pins nothing`.
- **proof** irrigation's scenario → that line, before any minute is spent.

### C6 · The documents follow the code
- **kind** chore · **size** S
- **fixes** the documentation half of K32 and K66.
- **removes/adds** `boards/README.md:93-97` says what a stand-in costs (its missing pads, named by `--validate`); the S3
  record's `//wokwi_part_type` note names `TX`/`RX`; `docs/guide/journey.md` Bench and `README.md:77` point at C3 (until
  it lands, at the two commands with the bin's `deploy.sh` as the worked example, marked as the bin's and as unrun on
  hardware); `docs/guide/how-it-works.md:216-229`'s tools table gains `flasher` and `device-files`.
- **testable** `tools/check_docs.py` / `tests/test_docs.py` already check recorded outputs; the retired sentence joins
  whatever list of retired phrases that check keeps, so it cannot return.
- **diagnosable** the docs check names the file and line that still carries the retired sentence.
- **proof** `grep -n "costs only the silkscreen" boards/README.md` → nothing; the Bench section shows a run.

## 4. What I could not check, and why

- **No Wokwi run** — each spends CI minutes and D4 says ask first (`../2026-10-09-p100-real-use/brief.md`); every
  simulation claim above is the converter's offline verdict (the diagram written or not), not a scenario's.
- **The XIAO's `SDA`/`SCL` stand-in case through the chain** — the chain stops at the footprint for the library XIAO
  (`[????] footprint … physical.header`, exit 2, P121). The 9-of-20 figure rests on the registry listing and
  `mapping.ts:96`; the chain's verdict for it is reasoned, not seen.
- **Nothing touched hardware** — the board in the drawer is held by the bin (★C1) and this task forbids the real
  store; whether the FireBeetle accepts the 4 MB image whole (littlefs block count against a 16 MB flash) and the write
  offset per chip are bench and page facts, —. The chip-id meanings 9 and 13 are H (esptool's table, from memory).
- **The deep-sleep draw (C11)** — a bench measurement (B15/B16); whether a µA-capable meter exists is — (tech lead Q6).
- **The cost of generalising the bin's checks** — measured only as `wc -l` (438 lines in `lib/checks/`, 120 in
  `check-consistency.ts`); the plugin's 4,000-line ceiling argument (`firmware-and-tests.md:135-139`) is for the PO.
- **The classifier's other misreads** — I tested one converter sentence; whether other converter failures are also
  design-fault-shaped limits (B11's family) was not surveyed.
- **spark's own tests in this area pass as they are**: `python3 -m unittest tests.test_flash_image tests.test_sim_project
  tests.test_converter` → `Ran 43 tests … OK` (E, 2026-10-10, against the store copy). None of them reaches the faults
  above, which is the testability finding, not a contradiction.

## 5. Searches

none — no web search and no Espressif-docs query was made. Everything read was a file in the repositories named above,
the converter's `node_modules`, or a GitHub issue read with `gh issue view` (read-only): spark #16, #7, #8, #64, #94,
#6, #123; the bin's #8, #2, #5, #10, #21. `REMOTE_BOARDS_URL` was read from the package, not fetched.
