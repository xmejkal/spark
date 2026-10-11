# Diagnosis — board records and footprints (P158 part 1, area `board-records`)

Written 2026-10-10 by the area's diagnostician, against spark 0.8.1 (main `a8aa34d`). Findings diagnosed: K22–K31 from
`../catalogue.md`, plus K14 (the vendor-header cache) and K32 (the stand-in's pins), whose code is in this area although the
catalogue files them elsewhere. Every claim is tagged: E a pointer or a run and what it printed, H a claim with its source,
D a decision (who, when), — unknown.

**How the runs were made.** The PO's store was copied once (`cp -R ~/.local/share/spark <scratch>/store`, 2026-10-10) and
every spark command ran with `SPARK_HOME=<scratch>/store HOME=<scratch>/home TMPDIR=<scratch>/tmp` as three words
(`env | grep SPARK_HOME` under that prefix printed the scratch path). The builds used `tsci 0.0.2621` from the bin's
`node_modules/.bin` through `PATH`, read-only, with the working directory under `<scratch>`; the converter ran under
`node v22.23.2` from spark's `tools/circuit-to-wokwi/dist/converter.mjs`. Nothing was written under `~/Development/spark`
outside this folder, nor under the real store, nor under the bin, irrigation or plant-alarm. Line numbers are spark's at
`a8aa34d` unless another file is named; tscircuit's are `@tscircuit/core` 0.0.1958's `dist/index.js` as installed in the
bin (the regexes quoted; the behaviour was observed with tsci 0.0.2621).

**The PO's criteria (2026-10-10, verbatim):** *"we want the system to be well designed so its well testable and
understandable where a mistake is happening and why"*. Each root cause below ends with the diagnosability test — what
output, if any, pointed at it — and each change says how it becomes testable and what its failure prints.

## 1. Root causes

### RC-board-records-1 · One pad, three names, joined by string equality — and the alias table reaches readers, not writers

- **where:** `scripts/emit_footprint.py:174-179` (the footprint's `portHints` is the `header_order` label alone);
  `scripts/emit_board.py:790` (a signal trace is `.Mcu > .<entry["pin"]>`, the `pins` key) and `:832-838`, `:868`
  (a power trace is `.Mcu > .<power_pads key>`); `scripts/assign_pins.py:407` (`pad_aliases` read — for the comment in
  `pins.py` only); `scripts/boards.py:349-362` (`--validate` reads it: a `pins` key must sit on a pad *or be aliased to
  one*); `tools/circuit-to-wokwi/lib/board.ts:94-115` and `lib/mapping.ts:93-108` (the converter reads it, both ways).
  `grep -n pad_aliases scripts/emit_footprint.py scripts/emit_board.py` → nothing (E, 2026-10-10).
- **why:** A header pad has (a) the vendor's name — the `pins` key, `MISO`, which `check_vendor_pins.py:77-83` needs to
  match `pins_arduino.h`; (b) the silkscreen label — the `header_order` entry, `MI`, which the footprint prints as the
  pad's hint; (c) tscircuit's own pin number, by the pad's position in the footprint (`pin11`). tscircuit joins a trace to
  a pad by (a) == (b) or by (c). spark writes the footprint in (b) and the traces in (a), and `pad_aliases` — the one
  statement that a ≠ b — is consulted by the validator, the firmware comment and the simulator, and by **neither of the two
  files tscircuit joins**. Wherever a ≠ b, the trace reaches nothing. On the shipped S3 that is `MISO`, `MOSI` and `SS`
  (`boards/firebeetle2-esp32s3.json:98-102`); the `spi` role makes those pins "taken last", which is why no design has
  landed there yet. Round 0's `IO<n>` file with `D3 → IO14` failed the same way (`council/round-0-runner.md:23`).
- **reproduced (E):** a requirements file of 21 `led-red-5mm` on `firebeetle2-esp32s3`:
  `emit_board.py … --assume-missing-sizes` exits 0 and writes `<trace from=".Mcu > .MOSI" …>` (line 161 of the output),
  `.Mcu > .MISO` (162), `.Mcu > .A4` (174); the generated footprint carries `portHints={["MI"]}`, `["MO"]`, `["A4"]` and
  0 occurrences of `MISO`, `MOSI` or `"SS"` (`/usr/bin/grep -c`). `tsci build` of that footprint with one trace to
  `.Mcu > .MISO` and one to `.Mcu > .MI`: `source_trace_not_connected_error: Could not find port for selector
  ".Mcu > .MISO". Component ".Mcu > " found, but does not have pin "MISO"`, while `.Mcu > .MI` resolved to `pin11`.
  `check_spine.py` on the 21-LED file: `[ok] schematic 67 trace(s) written · [ok] footprint · [!!] build Led07SeriesA.pin1
  (a terminal connected to nothing); Led08SeriesA.pin1 (a terminal connected to nothing) … the chain is broken` — Led07
  and Led08 are the two on MOSI and MISO. This is the same message shape as round 0's "unrelated open terminal"
  (`runner.md:22`): it was this fault, two hops from its cause.
- **kind:** design.
- **explains:** K23. The bin's CLAUDE.md calls `pad_aliases` "the bridge" — true for the converter and the firmware
  comment, false for the board the person orders.
- **diagnosability:** tscircuit names the symptom and the selector at the build stage; the chain names the LED's resistor
  terminal, not the MCU pad; spark names nothing before the build — the S3's own file passes `--validate`, and round 0's
  aliased file passed because the rule at `boards.py:351-356` asks only that the aliased pad exists. An agent reading
  `does not have pin "MISO"` has to already know that `pad_aliases` is not applied to footprints; the only place that
  knowledge lives is a grep with no hit.

### RC-board-records-2 · `header_order` labels are free text, and tscircuit reads an all-digit hint as a pin number

- **where:** `scripts/boards.py:343-350` (labels collected into a set; nothing is checked about them), `:418-425` (the
  name rule, applied to `pins` and `power_pads` keys only); `scripts/parts.py:185` (`SELECTOR_SAFE = "^[A-Za-z0-9_]+$"` —
  a string of digits passes); `scripts/emit_footprint.py:175-179` (labels written as hints, escaped, under the comment "a
  label no pin names is held to no name rule" — deliberate, for `D-` and `D+`). tscircuit: `getPinNumberFromPortHints`
  (`index.js:11651-11657`, `/^\d+$/` → `Number(hint)`), `getPinNumberFromHints` (`:9622-9627`, `/^(pin)?\d+$/`),
  `getPinNumberFromLabels` (`:12483-12487`), `Port.getNameAndAliases` (`:4343-4351`: a port with a pin number also answers
  to `pin<N>` and `<N>`).
- **why:** every plated hole in a `<footprint>` gets a pin number by position (1..32), and any hint that is all digits
  claims a pin number of its own. A pad printed `17` at position 13 therefore claims pin 17 — the number the pad at
  position 17 already has — and tscircuit keeps both as one pin number with two ports, `pin17` and `pin17_internal_1`, each
  answering to `pin17` and `17`. Nothing in spark models (c); the name rule that would have refused the label does not
  look at `header_order`.
- **reproduced (E), on an S3 copy whose GPIO pads carry their GPIO numbers as labels (round 0's first C6 file had this
  shape, `runner.md:19`, `:22`):** `boards.py --validate --for-fab --project <scratch>/proj-digits` →
  `active digits-s3 (project): ok`, exit 0. `emit_footprint.py --board digits-s3` → `wrote … (32 pads, 1.00 mm holes)`, exit
  0. `tsci build` (two resistors, four traces) → `Build exiting with code 0`, 0 errors, 4 `pcb_trace`s; **38 `source_port`s
  for 32 plated holes**: five pin numbers exist twice — `pin14_internal_1 hints=['pin14_internal_1','pin14','GND1','14']`,
  `pin15_internal_1 […,'pin15','15','GND2']`, `pin16_internal_1 […,'16','GND3']`, `pin17_internal_1
  […,'pin17','17','3V3']`, `pin18_internal_1 […,'18','RST']`. The pad printed `14` (D10, GPIO14) now answers to `GND1`;
  the 3V3 pad answers to `17` (SCK's GPIO). spark's own netlist, which takes every hint as a name
  (`scripts/netlist.py:92-109`: "A pad has one identity and several spellings"), then reports `Mcu.17 sits on nets
  [the 3V3 net, its own net]` and `Mcu.14 sits on [GND1's net]`, `Mcu.15 sits on [GND2's net]` — to every check that
  reads the netlist (`compare_design`'s `must_not_float`, the supply walk, a firmware-pins rule), GPIO17 is on 3V3 and
  GPIO14 and GPIO15 are grounded. The converter then refuses every board pin (`"pin17" is not a pin of
  board-esp32-s3-devkitc-1 …`, 9 problems, no diagram) because `pinNameOf` (`lib/netlist.ts:66-70`) drops digit hints
  and falls back to the port's generated name.
- **what this build did NOT show:** a short in copper. Each of the four traces reached its own hole (`.Mcu > .17` →
  `pin17`, the hole printed 17; `.Mcu > .3V3` → `pin17_internal_1`, the 3V3 hole); the holes keep 32 distinct
  `pcb_port_id`s. The catalogue's "joins 3V3 to the pad printed RX" and the runner's "the build joined 3V3 to …"
  (`runner.md:6`, `:22`) rest on the same hint reading as mine (`pin17_internal_1 (hints pin17, 17, 3V3)`), not on a
  copper trace. Whether another selector path or another tscircuit version resolves the doubled pin number to the wrong
  hole is — . What stands is narrower and still silent: a netlist every check reads in which the pads are merged, a
  schematic whose 3V3 port is also labelled 17, and a simulation that cannot be made.
- **kind:** implementation (the rule's scope) on the design seam of RC-1.
- **explains:** K22.
- **diagnosability:** none. `--validate` ok, `--for-fab` ok, footprint ok, build exit 0 with 0 errors. The first message is
  the converter's, two stages later, and it names a generated port name, not the label.

### RC-board-records-3 · The `physical` schema is defined by its readers and documented by its refusals

- **where:** `scripts/boards.py:61-63` (`REQUIRED_KEYS` names `physical` with no shape), `:19-24` ("The contract is
  enforced rather than documented"), `:363-369` (the `pin_roles` loop: the refusal is the only list of roles, and a
  `//`-prefixed key is not skipped — unlike `header_order` at `:347` and `emit_footprint.py:128`);
  `scripts/emit_footprint.py:83-98` (`_missing`: the nine fields the footprint needs — the nearest thing to a schema, in
  code), `:162-163` (`physical["header"].get("drill_mm", "?")`); `tools/circuit-to-wokwi/lib/board.ts:27-68` (a second,
  partial schema, in TypeScript); `boards/README.md:55-58` (the only schema prose: the name rule) and `:1-4` (the steps
  are the bin's — #61); `docs/guide/how-it-works.md:150` ("`boards/README.md` has the schema").
- **why:** the readers disagree about what `physical` is, and three keys the shipped S3 file carries have no reader at all:
  `grep -rln` over `scripts/*.py`, the converter's `lib/` and `cli.ts` (2026-10-10) → `flush_edge` none, `corner_radius_mm`
  none, `mounting_holes` none, `footprint_module` read by `boards.py` (REQUIRED_FOR_FAB, a name check) and `board.ts` (an
  interface field) only — nothing consumes its value; `drill_mm` read by `boards.py` (a number, if present) and
  `emit_footprint.py` (the comment, `?` when absent — E: `nodrill-s3` renders `The holes are 1.00 mm, NOT the ? mm on the
  vendor drawing.`). PIN_ROLES is closed for a good reason (`:87-94`: a role nobody reads looks like a role that is fine),
  but the same hazard — "carried and ignored" — is unguarded for `physical` keys. Repeated and NC pads have a working form
  that no page states: two `pins` keys on one GPIO are legal (`boards.py:319-325`, `test_boards.py:235`); a label with no
  `pins` entry is legal (`D-`, `D+`, `RST` are such on the S3); a label on two holes stays two ports (E: a footprint with
  `SDA` and `GND` on two holes each builds with 0 errors — `pin1 ['pin1','SDA','1']`, `pin3 ['pin3','SDA','3']`).
- **reproduced (E):** `pin_roles.jtag` → `pin_roles.jtag is not a role any script reads, so it would be carried and
  ignored. Known: adc2_unusable_with_wifi, console_uart, i2c, …`; `//jtag` inside `pin_roles` → the same sentence plus
  `pin_roles.//jtag needs both a 'gpio' list and a 'note'` (round 0's `runner.md:19`).
- **kind:** documentation, with a design half (unread keys).
- **explains:** K24, K25, K26, K27 (the `?` and the unemitted mounting holes).
- **diagnosability:** the refusals are good sentences, one at a time; an agent writing a record learns the schema by being
  refused (`runner.md:11`, `:18-19`) and learns nothing about the keys that are accepted and never read.

### RC-board-records-4 · `emit_footprint.main` returns before `_report` on the stdout path

- **where:** `scripts/emit_footprint.py:225-230` (`if args.out: … return _report(…)`; else `sys.stdout.write(text);
  return EXIT_OK`), `:233-239` (`_report` is the only function that reads `args.json`).
- **reproduced (E):** `emit_footprint.py --board firebeetle2-esp32s3 --json` → the TSX module on stdout, nothing on
  stderr, exit 0; with `-o` → `{"check": "emit-footprint", "status": "ok", "message": "wrote … (32 pads, 1.00 mm holes)"}`.
- **kind:** implementation. **explains:** K28.
- **diagnosability:** the output is code where JSON was asked, exit 0 — an agent parsing it gets a decode error naming
  character 0, as mine did.

### RC-board-records-5 · The vendor-header cache has a home in the plugin and none in the store

- **where:** `scripts/check_vendor_pins.py:98-99` (`PLUGIN_ROOT`), `:102-112` (`cached_header`: beside the board's
  project when a file is already there, else the plugin's `.spark/cache`), `:132-138` (the live branch writes to that
  path); `import store` does not occur in the file (E, grep). `git ls-files .spark/cache` → the S3's and the XIAO's
  headers are **tracked**; the C6's from round 0 is untracked (`git status --short`, 2026-10-10).
- **why:** the cache predates the store: "the plugin's own cache: the boards it ships come with their vendor headers
  fetched" (`:98`) is right for shipped boards and makes a project's board write into the plugin. E (no network, no
  write): `cached_header(<scratch>/proj-k14/boards/firebeetle2-esp32s3.json, "dfrobot_firebeetle2_esp32c6")` →
  `~/Development/spark/.spark/cache/dfrobot_firebeetle2_esp32c6.pins_arduino.h`. `SPARK_HOME` is never consulted.
- **kind:** design. **explains:** K14 (catalogued under store-levels-and-holds; the code is this area's).
- **diagnosability:** nothing is printed about where the header was written; `git status` in the plugin is the only sign.

### RC-board-records-6 · A board the person owns with no board file is accepted, reserved and recorded by the pick, refused by the requirements, and no operation makes the file

- **where:** `scripts/needs.py:260-264` (`_unfiled_boards`), `:320-321` (a *note*, not a problem, so the pick writes),
  `:498-520` (`_board_problems`: the refusal, pointing at `docs/guide/how-it-works.md`, "Your own dev board");
  `scripts/parts.py:1988-2010` (`_op_pick` writes when `problems` is empty), `:1472-1535` (OPERATIONS: no board-record
  operation); `commands/research.md` is parts-only (#99: "it has no flow for a BOARD").
- **reproduced (E):** `--needs-set` one need `board / compute / microcontroller`; `--pick <proj> board=dfrobot-dfr1075` →
  exit 0: `set dfrobot-dfr1075: used_in null → {"proj-k29": 1}` · `dfrobot-dfr1075: a board needs a board file — a record
  in boards/ — before spark can build with it` · `listed proj-k29 on your projects` · `wrote to your history: 1 reused`.
  `--requirements <proj>` → exit 1: `refused, so nothing was written: dfrobot-dfr1075 — picked as the board, but a board
  needs a board file … and it has none; spark has one that builds for firebeetle2-esp32s3; xiao-esp32-c6 stops at the
  footprint stage (P121) …`. The hold and the `reused` event stay after the refusal.
- **what the drawer knows about such a board (E, the scratch copy):** `drawer/dfrobot-dfr1075.json` carries `label`
  ("FireBeetle 2 ESP32 C6 IoT Development Board (Supports Wi-Fi 6, Bluetooth 5, Solar-Powered)"), `count 2`,
  `part_number {maker: dfrobot, number: DFR1075}`, `from`, `bought` — no `is`, no `function`. The S3's entry got
  `is: {board: firebeetle2-esp32s3}` because the board file lists the SKU (`drawer.py:125-131`).
- **kind:** design (a missing operation). **explains:** K29; the data F0/D8 starts from.
- **diagnosability:** the pick's note names the fix as "a record in boards/"; the refusal names a five-step page. Neither
  names a command, because there is none; the person or agent is sent to write JSON against a schema RC-3 says is
  documented nowhere.

### RC-board-records-7 · The XIAO's record lacks what the chain reads, and "stops at" is computed from one gap

- **where:** `boards/xiao-esp32-c6.json:18-27` (`physical`: no `header`, no `header_order`; `:123` says so), no `power`
  key at all (`grep -n io_volts boards/*.json` → the S3's line 413 only); `scripts/boards.py:232-246` (`footprint_stop` =
  `footprint_gaps` only), `:391-399` (`--for-fab` requires two *names*, `footprint_module` and `footprint_export`, not
  geometry — E: the XIAO is `ok` under `--validate --for-fab`); `scripts/check_spine.py:333-385` (stage order: board →
  parts → schematic → footprint → build); `scripts/emit_board.py:651-664` (`series_ohms` raises "the board states no
  power.io_volts"), `:1117-1120` (caught → could-not-run).
- **reproduced (E):** `check_spine.py` on `{board: xiao-esp32-c6, parts: [led-red-5mm]}` → `[ok] board Seeed XIAO
  ESP32-C6 … · [????] schematic cannot emit a board: led-red-5mm asks for 5 mA through a series resistor, but the board
  states no power.io_volts — nothing to compute it from · the chain was NOT exercised`. `boards.py --list` says
  `xiao-esp32-c6 (library) stops at the footprint stage (P121)`; `emit_footprint.py --board xiao-esp32-c6 --json` →
  `could-not-run … physical.header (no header geometry at all)`.
- **kind:** data (the record) and implementation (one gap computed, two exist; `--for-fab` checks names, not geometry).
- **explains:** K30. P121 (#55)'s proof line "`boards.py --validate --for-fab` fails a board with no header geometry" is
  not met today.
- **diagnosability:** the schematic refusal is a good sentence; the label the person read before building said a later
  stage. Two statements about the same board disagree because they come from two rules.

### RC-board-records-8 · A board's `function` is read by the matcher and carried by no board file

- **where:** `scripts/parts.py:65-69` (`KIND_FUNCTION["board"] = ("compute", "microcontroller")`), `:72-78`
  (`function_of(record, board=True)` prefers the record's own `function` when well-formed and **silently ignores** a
  malformed one — `and not function_problems(record)`), `scripts/needs.py:177` (candidates: a board's functions by the
  need's verb); `boards.py` `validate` never mentions `function` (not required, not forbidden, not shape-checked); neither
  shipped board file carries it (`grep -n '"function"' boards/*.json` → nothing).
- **reproduced (E):** as shipped, needs `board / compute / microcontroller` and `report / communicate / wifi` →
  `report — communicate / wifi · nothing in the store does this — a gap`. With a project copy of the S3 carrying
  `"function": [{"does":"compute","what":"microcontroller"}, {"does":"communicate","what":"wifi bluetooth"},
  {"does":"power","what":"lipo charger battery"}, {"does":"connect","what":"usb-c usb-device"}]`: `boards.py --validate`
  → ok, and `--match` → `report — communicate / wifi · owned 1 firebeetle2-esp32s3 (project) wifi bluetooth free 0`.
  The slot exists; the data and the sentence saying it may be filled do not.
- **kind:** data and documentation.
- **explains:** K31 (the WiFi half, the LiPo-socket half, the USB half — all the same slot; the facts themselves still
  need their sources: WiFi/BLE from the module datasheet, the charger from the schematic the record already cites, USB
  device from Espressif's S3 documentation — and the C6's USB cannot be a device, `council/tech-lead.md` FEAS-5/PHYS-4).
- **diagnosability:** "a gap" is the matcher's honest reading of a record that says nothing; nothing tells the record's
  author that it could say more, and a malformed `function` on a board would be dropped with no word.

### RC-board-records-9 · The stand-in's pin list is checked for power pads only, though it ships with the converter

- **where:** `scripts/boards.py:302-313` (`power_pads` keys must appear in `wokwi_power_pins`; `pins` values are never
  compared with anything); `tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/registry/parts.json` (a list of
  137 parts, each `{type, pins, …}`; embedded in `dist/converter.mjs` — `grep -c board-esp32-c6-devkitc-1` → 1);
  `lib/geometry.ts:58-105` (`PinOracle.pinsOf`); `lib/mapping.ts:82-108` (a GPIO becomes `String(gpio)`; `wokwi_power_pins`
  is merged **last**, so an entry there overrides a GPIO's number).
- **facts (E, read from the registry 2026-10-10):** `board-esp32-s3-devkitc-1` lists 44 pin names, among them `RX` and `TX`
  and not `43`, `44` — so the shipped S3's `TX` (43) and `RX` (44) would fail at simulation exactly as round 0's GPIO14 did,
  with `"43" is not a pin of board-esp32-s3-devkitc-1`; `board-esp32-c6-devkitc-1` lists 32 names, none of `14`, `16`,
  `17` — the FireBeetle 2 C6's `D3`, `TX`, `RX` (`runner.md:12`). The data to say so at `--validate` time is on disk.
- **kind:** design (a check that exists for one key and not its sibling).
- **explains:** K32 (catalogued under firmware-and-bench; the record side is here), and a latent S3 case nobody has hit
  because `console_uart` pins are taken last.
- **diagnosability:** the converter's message is exact and arrives at the last stage, naming a number and the valid list;
  nothing earlier says that a pin of this board has no name on its stand-in, nor how to give it one — although
  `wokwi_power_pins` already can (`mapping.ts:108`), undocumented for that use.

## 2. What the design gets right and must be kept

- **Every problem at once, each naming the key, the rule and the consequence** — `boards.py:281-287`; e.g. `:353-356`
  ("A footprint built from this would have no pad for it, and every trace to it would silently reach nothing"). The
  refusals round 0 met were the only good documentation it had (`runner.md:19`).
- **Facts, never decisions**, enforced at any depth — `FORBIDDEN_KEYS` `boards.py:69-85`, `:376-388`;
  `tests/test_boards.py:239`. The reason a board file stays swappable.
- **A closed `PIN_ROLES` with its reason** (`boards.py:87-107`) and the test that every role the assigner prices is one a
  board may carry (`tests/test_boards.py:286-294`). Keep the closure; fix the documentation (C6).
- **One rule by which a board "stops"**, said by three places — `emit_footprint.footprint_gaps` (`:101-109`),
  `boards.footprint_stop` (`:232-246`), `needs.stops_at_footprint` (`:149-152`); "said, never refused" (F12, C-7:
  `init_project.py:476-477`, `needs.py:322-324`). C9 extends the rule; it does not add a second.
- **Refuse to guess geometry; size the hole from the pin, never from the vendor's drill** — `emit_footprint.py:15-33`,
  `:62-80` (derived from `data/fabrication.json` through `fab`), with an independent witness (`tests/test_emit_footprint.py`
  `REFERENCE`, `:110-147`) and a refusal test for every underivable field (`:168-206`).
- **Labels escaped, never trusted** — `emit_footprint.py:175-179` (`json.dumps`), the crafted-label tests
  (`tests/test_boards.py:175-211`). C1 narrows what a label may be; it must keep this.
- **`power_pads` with a direction, and the conditional VCC** — the record's own account at
  `boards/firebeetle2-esp32s3.json:116-143`; `emit_board.py:825-838`, `:849-878` (said, not skipped).
- **The `wokwi_power_pins` check** (`boards.py:302-313`) — the exact shape C11 copies for `pins`.
- **One resolved file for Python and TypeScript, no fallback path** — `boards.py:45-51`, `:260-278`; `board.ts:16-25`
  ("a converter that guesses the board silently converts one design against another's pin map").
- **The project's own file wins over the library** — `boards.py:34-37`, `store.records`.
- **The one check that looks outside, failing closed** — `check_vendor_pins.py:13-25`, `:117-130`; its parser
  (`parse_pins`, `:68-69`) is reusable for C8.
- **`BOARD_FACTS` digested into the `built` line** (`parts.py:906-915`): `pins`, `power_pads`, `physical`.
- **Documents by checksum, cited per fact** — `boards/firebeetle2-esp32s3.json:316-355`; `parts.document_problems` at
  `boards.py:440`; `hardware_revisions` (`:295-315`) as the model for "one SKU, two boards".
- **`tests/test_boards.py`, `test_emit_footprint.py`, `test_check_vendor_pins.py`: 76 tests, all passing** (`python3 -m
  unittest` on the three files under the scratch prefix, 2026-10-10: `Ran 76 tests … OK`). Every change below adds to
  them; none replaces them.

## 3. Changes

### C1 · A `header_order` label tscircuit would read as a pin number is refused
- **kind:** bug · **size:** S · **fixes:** K22
- **removes / adds:** adds one rule to `boards.validate` where labels are already collected (`:343-350`): a label matching
  tscircuit's own grammar `^(pin)?\d+$` (case-insensitive) is refused; a label that is also a `pins` or `power_pads` key is
  held to `SELECTOR_SAFE` (today only the key side is). Nothing removed. Written in `boards/README.md`'s schema (C3) in one
  sentence: *a pad label is what is printed; it may not be a bare number, because the footprint tool reads a number as a
  pin position.*
- **testable:** `test_boards.py::test_a_bare_number_pad_label_is_refused` (the digits file from `<scratch>` as a fixture
  under `tests/data/`, every GPIO pad a number → refused, naming each); `test_the_shipped_boards_carry_no_numeric_label`;
  `test_emit_footprint.py::test_a_footprint_never_doubles_a_pin_number` (every hint in the rendered module fails the
  regex). The 76 existing tests must still pass.
- **diagnosable:** `physical.header_order.row_18[13] is "17": a bare number, which tscircuit reads as pin position 17 —
  the pad at position 17 is "3V3", and the two would become one port. Print the silkscreen word (SCK, IO17), never the
  GPIO number.`
- **proof:** `boards.py --validate` on round 0's digit-label file (kept as the fixture) exits 1 with that sentence; on
  the S3 and the XIAO exits 0; the digits footprint can no longer be generated.

### C2 · `pad_aliases` reaches the footprint, so a trace by either name finds the pad
- **kind:** bug · **size:** S–M · **fixes:** K23
- **removes / adds:** `emit_footprint.render` writes `portHints={["MI", "MISO"]}` — the printed label first (the
  converter's `pinNameOf` and spark's `printed_name` take the first non-numeric hint), then every `pins` key aliased to it.
  `boards.validate` gains the inverse of its existing rule: an alias target must be a label that is **not itself a `pins`
  key** (so `SS → A4` stays legal and `A4` keeps one identity). Nothing removed. The alternative — rename the S3's `MISO`
  key to `MI` and drop the table — breaks `check_vendor_pins` (`:77-83`: the vendor defines no `MI`), so the alias stays
  and the footprint learns it; one writer changes, both names resolve.
- **testable:** `test_emit_footprint.py::test_an_aliased_pin_is_a_second_hint_on_its_pad` (the S3: the `MI` hole's hints
  are `["MI", "MISO"]`); `test_check_spine.py` (or `test_emit_board.py`): the 21-LED requirements file from `<scratch>`
  builds with 0 `source_trace_not_connected_error` — a regression test for the whole seam, since the assigner reaching the
  SPI pins is what exposes it.
- **diagnosable:** when a trace still cannot resolve, `check_spine`'s build stage adds the cause beside the symptom:
  `Led08SeriesA.pin1 (a terminal connected to nothing) — its trace is from ".Mcu > .MISO", and the footprint has no pad
  answering to MISO (pads: MI, MO, …); physical.pad_aliases maps MISO to MI` — read from `board.tsx`'s own `<trace>` lines
  and the footprint's hints, both files the chain already holds.
- **proof:** round 0's `IO<n>` file with `D3 → IO14` builds past `.Mcu > .D3`; the 21-LED S3 design reaches `[ok] build`.

### C3 · The `physical` schema is written where it is enforced, and a key nobody reads is refused
- **kind:** chore (docs) + bug · **size:** M · **fixes:** K24, K26, K27 (the mounting-holes half), half of K25
- **removes / adds:** adds a `## The board file, key by key` section to `boards/README.md` generated or checked from the
  code: every key under `physical` with *who reads it* (`emit_footprint`, `emit_board`, the converter, `check_footprints`),
  *for which stage* (firmware / footprint / fab / simulation), its unit, and whether `null` is allowed; the `//` comment
  convention; the three pad forms (one GPIO on two pads = two `pins` keys, one rail on two pads = two `power_pads` keys, an
  NC pad = a label with no key); the `header_order` row keys (`row_<pins>`, any name, in `header.pins` order). Adds a
  `PHYSICAL_KEYS` set to `boards.py` and the same "carried and ignored" refusal `PIN_ROLES` has (`:363-367`). **Removes**
  `flush_edge` and `corner_radius_mm` from the S3 file (no reader; `flush_edge` is implied by `emit_footprint.pads`'s one
  alignment, `:113-117`) — or gives them a reader, the PO's call; `mounting_holes` is either emitted by `render` as four
  `<hole>` elements (the fab needs them; `emit_board`'s header says "Not decided here, and it must be: mounting holes") or
  removed. Replaces `boards/README.md:35-73`'s bin-specific steps with spark's five from `how-it-works.md` (#61).
- **testable:** `test_boards.py::test_every_key_the_shipped_boards_carry_is_read_or_refused` (walk both files; every
  `physical` key is in `PHYSICAL_KEYS`, and every member of `PHYSICAL_KEYS` is read by a named script — a grep in the test,
  as `test_every_role_the_assigner_prices…` does for roles); `tests/test_docs.py` gains a check that `boards/README.md`
  names every key in `PHYSICAL_KEYS` and every name in `PIN_ROLES`.
- **diagnosable:** `physical.flush_edge is read by no script, so it would be carried and ignored. Known:
  footprint_export, header, header_order, height_mm, mounting_holes, pad_aliases, thickness_mm, width_mm, wokwi_size_px`
  — the same sentence shape the roles already print.
- **proof:** a second agent writes a C6 record from `boards/README.md` alone and meets none of G0.2, G0.5, G0.10
  (items.md's own proof line for the ten gaps); `git grep -c '"?"'` in a generated footprint is 0.

### C4 · `emit_footprint.py --json` prints JSON on every path
- **kind:** bug · **size:** S · **fixes:** K28
- **removes / adds:** `main` routes the stdout case through `_report` too: `{"check": "emit-footprint", "status": "ok",
  "message": "32 pads, 1.00 mm holes", "module": "<the TSX>"}`; or, simpler and the recommended one, `--json` with no
  `--out` is a could-not-run (`--json needs --out: the module goes to a file, the report to stdout`). Removes the early
  `return EXIT_OK` at `:230`.
- **testable:** `test_emit_footprint.py::test_json_without_out_is_json` — `main(["--board","firebeetle2-esp32s3","--json"])`
  prints one line `json.loads` accepts with `check == "emit-footprint"`; `tests/test_json_contracts.py` already pins the
  other scripts' shapes and gains this one.
- **diagnosable:** the JSON line itself, or `could-not-run: --json needs --out …`.
- **proof:** the command round 0 typed (`runner.md:20`) prints JSON.

### C5 · The footprint's header says what the drawing states, and nothing else
- **kind:** bug · **size:** S · **fixes:** K27
- **removes / adds:** `render` prints `NOT the 0.9 mm on the vendor drawing` only when `drill_mm` is a number and `the
  vendor drawing states no drill; the hole is sized from the pin` otherwise; the `"?"` default at `:163` goes. Pairs with
  C3's mounting-holes decision.
- **testable:** `test_emit_footprint.py::test_a_board_with_no_vendor_drill_says_so` (no `?` in the output; the sentence
  present).
- **diagnosable:** the generated file's second line, as today — with a sentence instead of a `?`.
- **proof:** round 0's C6 footprint header reads as a sentence.

### C6 · One comment-key rule for every walker, and the roles listed where a person reads
- **kind:** bug (+ docs) · **size:** S · **fixes:** K25
- **removes / adds:** one helper `is_comment(key)` (`key.startswith("//")`) used by every loop that walks a board object's
  keys — `pins`, `power_pads`, `pin_roles`, `header_order`, `wokwi_power_pins` — replacing the two inline checks
  (`boards.py:347`, `emit_footprint.py:128`); `PIN_ROLES` and their one-line meanings printed into `boards/README.md` by
  C3's generator (the dict already carries the sentences, `:95-107`).
- **testable:** `test_boards.py::test_a_comment_key_is_skipped_wherever_keys_are_walked` (a `//note` under each of the
  five objects: no problem about it); the docs test from C3 covers the role list.
- **diagnosable:** unchanged refusal for a real unknown role; no refusal for a comment.
- **proof:** round 0's `//jtag` note stays where it was written.

### C7 · The vendor-header cache lives in the store, and the check says where it wrote
- **kind:** bug · **size:** S · **fixes:** K14 (G0.7)
- **removes / adds:** `cached_header` asks `store.home()` for `cache/vendor-headers/<variant>.pins_arduino.h` and falls
  back, read-only, to the plugin's tracked copies for shipped boards; the live branch writes to the store path and prints
  `cached at <path>` in its line; `.spark/cache/` stays for the two tracked shipped headers, or moves to `data/` (the PO's
  call — they are test fixtures today, `tests/test_check_vendor_pins.py:163-170`). Removes the plugin-path write.
- **testable:** `test_check_vendor_pins.py::test_a_live_fetch_is_cached_under_spark_home_not_the_plugin` (`fetch_variant_header`
  patched; `SPARK_HOME` set to a temp dir; the plugin folder unchanged — `git status` clean is the proof the PO reads);
  the existing P10 test (`:123-133`, a project copy of a shipped board is checked against the plugin's cache) must still
  pass.
- **diagnosable:** `firebeetle2-esp32c6 ok (20 pins against espressif/arduino-esp32 …; cached at ~/.local/share/spark/cache/vendor-headers/dfrobot_firebeetle2_esp32c6.pins_arduino.h)`.
- **proof:** after a live check on a project board, `git status --short` in the plugin prints nothing (items.md's own
  proof line).

### C8 · A board record from a drawer entry: the skeleton spark can fill, the fields it must ask for
- **kind:** story · **size:** L · **fixes:** K29 (F0/D8, #99's board half, #123's "first fix")
- **removes / adds:** adds one operation — `parts.py --board-skeleton <drawer entry> --project <p>` (or a board flow in
  `/spark:research`) — that writes `boards/<id>.json` from what is mechanical today and leaves the rest as **owed fields
  that `--validate --for-fab` names** (C9), each with the source to read:
  1. **the Arduino variant** — from the drawer label against `espressif/arduino-esp32` `boards.txt` (E, fetched read-only
     2026-10-10, 3,162,786 bytes: `dfrobot_firebeetle2_esp32c6.name=DFRobot FireBeetle 2 ESP32-C6`,
     `dfrobot_beetle_esp32c6.name=DFRobot Beetle ESP32-C6`, `dfrobot_romeo_esp32s3.name=DFRobot Romeo ESP32-S3` — three of
     the PO's four unfiled boards; the Beetle ESP32 (DFR0575) has no `DFRobot`-named row, —); this closes G0.1/K72 too;
  2. **`pins`** — `check_vendor_pins.parse_pins` on that header (exists, `:68-69`), so the record is born agreeing with the
     check that would verify it;
  3. **`chip`, `wake_capable_gpio`, `adc_gpio`, `wokwi_part_type`, `micropython_port`** — from a per-chip table spark
     ships (`esp32s3`, `esp32c6`, `esp32c3`…: `SOC_RTCIO_PIN_COUNT`, the ADC1 range, the devkit stand-in, the generic
     MicroPython port — the facts round 0 read from `soc_caps.h`, `runner.md:16`), each row citing its `soc_caps.h`;
  4. **`documents`** — the DFRobot wiki page for the SKU (the S3 file's `sources.vendor` URL shape; round 0 found
     `SKU_DFR1075`'s page), the dimension drawing and the schematics zip kept in the store with their sha256 (P62b, G0.9);
  5. **`physical.header`, `header_order`, `width_mm`, `height_mm`, `first_pad_from_edge_mm`** — **not** mechanical: round 0
     parsed a vector PDF ad hoc in 14 minutes (`diary-round-0-board.md`); the skeleton writes these as owed, naming the
     kept drawing, and an agent or the person measures; the same for `power_pads`, `hardware_revisions`, `power.*`;
  6. **`function`** (C10) — from the label's own words (the DFR1075 label says Wi-Fi 6 and Bluetooth 5), marked unverified.
  Also changes the pick: a board pick with no file prints the skeleton command instead of a page name, and either does not
  record `reused` or records it as `reused (board file owed)` — today it reserves and records a board it cannot build
  (RC-6's run). Removes the five-step hand route from `how-it-works.md` once the command exists.
- **testable:** `test_parts.py::test_a_board_skeleton_from_a_drawer_entry_names_its_variant_and_fills_pins_from_the_header`
  (the fetch patched with the C6 header the plugin already caches; the written file passes `--validate`, fails
  `--validate --for-fab` naming exactly the owed geometry fields); `test_a_pick_of_a_board_with_no_file_names_the_command`.
- **diagnosable:** `wrote boards/firebeetle2-esp32c6.json: pins from espressif/arduino-esp32 variants/dfrobot_firebeetle2_esp32c6/pins_arduino.h
  (20); chip facts from spark's esp32c6 table; OWED before it can build: physical.header, physical.header_order,
  physical.width_mm, physical.height_mm (measure them on the kept dimension drawing <sha256…>), power_pads (from the kept
  schematic)` — every owed field with the document to read it from.
- **proof:** `--board-skeleton dfrobot-dfr1075` on the PO's store (with his yes to the fetches), then the owed fields
  filled, then `check_spine` on the board + one LED reaches `[ok] build` — round 0's pass line, from a command.

### C9 · A board says every stage it stops at, from one rule; `--for-fab` requires geometry
- **kind:** bug · **size:** M · **fixes:** K30 (P121 #55's proof line)
- **removes / adds:** `boards.footprint_stop` becomes `chain_stops(board) -> [str]` and returns every named stop:
  `footprint_gaps` (as today) and `power.io_volts not stated — a part that sizes a series resistor from it stops at the
  schematic`; `--list`, `--match`, `--audit`, `--pick`, `init --board` print them all (they already print one);
  `--validate --for-fab` adds `footprint_gaps` to its two names. Removes nothing. The XIAO's data: `physical.header`,
  `header_order` and `io_volts` filled with sources — the geometry from Seeed's KiCad footprint through `tsci convert`
  (the route the bin's CLAUDE.md records for this very board: Seeed's OPL library, CC BY-SA 4.0; H until re-run) or from
  Seeed's dimension drawing; `io_volts` 3.3 V cited from the ESP32-C6 datasheet (round 0 read Table 5-2/5-4 of v1.5,
  `runner.md:56`).
- **testable:** `test_boards.py::test_a_board_with_no_header_geometry_fails_for_fab` (the XIAO today — P121's own proof);
  `test_a_board_that_owes_io_volts_says_it_stops_at_the_schematic`; `test_check_spine.py`: the documented example builds
  on each library board once the data lands (P121's "A test builds the documented example on each library board").
- **diagnosable:** `xiao-esp32-c6 (library) stops at: the footprint stage (no header geometry in its board file); the
  schematic, for a part that sizes a resistor from power.io_volts (not stated)` — before anything is picked.
- **proof:** `boards.py --list` on a fresh checkout prints one line per stop for the XIAO; after the data, none.

### C10 · A board's `function` is a documented, validated key — and both shipped boards carry one with sources
- **kind:** story · **size:** M · **fixes:** K31 (USER-4, USER-6, FEAS-4/5)
- **removes / adds:** `boards.validate` calls `parts.function_problems(board)` (the shape rule parts already have), so a
  malformed list is refused instead of dropped (`parts.py:74`); `boards/README.md` (C3) says a board may state what it
  gives for free, in the 13 verbs; the S3 file gets `communicate / wifi bluetooth` (the WROOM-1 datasheet it already
  cites), `power / lipo-charging` (`charge_current_a` already cites the schematic), `connect / usb-device` (the S3's
  USB-OTG — a source to add, Espressif's S3 datasheet); the XIAO gets `communicate / wifi bluetooth zigbee` and **no**
  USB-device (the C6 cannot, PHYS-4). `--match`'s "a gap" then reads `owned 1 firebeetle2-esp32s3 … wifi bluetooth` (E:
  that is what it printed with the key present); the build's verdict stops calling `report` unserved for the same reason.
  Open for the PO: whether a need the board itself serves should be *picked* (it reserves nothing) or marked served by
  the board pick — `_unserved` (`needs.py:522-540`) decides today by picks.
- **testable:** `test_needs.py::test_a_need_the_board_serves_lists_the_board` (the S3 for `communicate / wifi`);
  `test_boards.py::test_a_malformed_function_on_a_board_is_refused`; `test_every_shipped_board_states_a_function_with_a_source`.
- **diagnosable:** `function is [{"does": one of sense, input, …, "what": words}]` — parts' sentence, now on boards; and
  `--match` printing the board where it printed "a gap".
- **proof:** USER-4's walk: `report / communicate / wifi` no longer says "nothing in the store does this".

### C11 · `pins` are checked against the stand-in's pin list; a GPIO the stand-in names differently is mapped in the file
- **kind:** bug · **size:** S · **fixes:** K32 (the record side; the S3's latent TX/RX)
- **removes / adds:** `boards.validate` reads the registry the converter ships (`@wokwi/diagram-lint`'s `parts.json`, or a
  copy under `data/wokwi-parts.json` with its version) and, for a board with `wokwi_pin_naming: gpio`, refuses a `pins`
  GPIO whose number is not a pin of `wokwi_part_type` **unless** `wokwi_power_pins` (renamed `wokwi_pin_names` in a later
  schema version, or kept) maps that pad to the name the stand-in uses — the override `mapping.ts:108` already applies.
  The S3 file gains `"TX": "TX", "RX": "RX"`. For a pin the stand-in truly lacks (the C6 devkit's GPIO14), the record says
  `not_simulated: [14]` and the validator accepts it as a stated limit; whether the assigner should then avoid that pin
  when a simulation is wanted is a design question for the firmware-and-bench area (K32's home), not decided here.
- **testable:** `test_boards.py::test_a_gpio_the_stand_in_has_no_pin_for_is_reported` (the S3 as shipped today → 43 and
  44 named; with the two entries → clean); `test_the_shipped_boards_simulate_every_pin_or_say_which_cannot`.
- **diagnosable:** `pins.TX is GPIO43, which board-esp32-s3-devkitc-1 has no pin called "43" for; it calls that pin TX —
  add "TX": "TX" to wokwi_power_pins, or list 43 under not_simulated` — at `--validate`, not at the last stage.
- **proof:** round 0's chain would have stopped at `--validate` with `pins.D3 is GPIO14, which board-esp32-c6-devkitc-1
  has no pin for — list 14 under not_simulated`, instead of at the simulation with `"14" is not a pin`.

### C12 · Remove `footprint_module`
- **kind:** remove · **size:** S · **fixes:** part of K24 and K30's "names a file nobody has"
- **removes / adds:** the key's only readers are the name check in `REQUIRED_FOR_FAB` (`boards.py:67`, `:395-399`) and
  the converter's interface field (`board.ts:48`); no script consumes its value, and the XIAO's `"XIAO-ESP32-C6-SMD"` names
  a footprint spark does not have (#55). With C9 making `--for-fab` ask for geometry, the name check guards nothing.
  Remove it from `REQUIRED_FOR_FAB`, both board files, `board.ts`, and the README; `footprint_export` stays (read by
  `emit_board.py:572`, `:611`, `check_spine.py:378`).
- **testable:** `test_boards.py::test_fab_readiness_is_separate_from_being_valid` updated to geometry; the schema test of
  C3 fails if the key reappears.
- **diagnosable:** with C3, a file still carrying it gets `physical.footprint_module is read by no script …`.
- **proof:** `grep -rn footprint_module scripts tools/circuit-to-wokwi/lib boards` → nothing.

### On the PO's question (2026-10-10): existing formats and libraries instead of a schema of our own
- The grammar that caused K22 is tscircuit's, and C1 adopts it verbatim (`^(pin)?\d+$`) rather than inventing a second.
- The XIAO's missing geometry has an existing source and an existing converter: a KiCad footprint through `tsci convert`
  (the bin's CLAUDE.md: "how the XIAO came in"; Seeed's OPL library, CC BY-SA 4.0 — H until re-run). A generated
  footprint from `physical.header` and a converted vendor footprint are two routes to the same module; the record could
  name either (`footprint_source: {kicad_mod: <kept document>}` or `physical.header`), and `footprint_gaps` would accept
  either. Not proposed as a change until the PO says whether a converted footprint counts as "verified".
- The stand-in's pins are in a library spark already ships (`@wokwi/diagram-lint`'s registry, 137 parts) — C11 reads it.
- The SKU → variant bridge is `boards.txt` in the Arduino core (fetched once, §5) — C8 reads it; PlatformIO's
  `boards/*.json` and MicroPython's `board.json` are H alternatives, not checked.
- A schema language (JSON Schema) for the board file would make C3's "key by key" machine-checked and give the converter
  its TypeScript types from one source; it is the PO's call whether a schema file is simpler than `PHYSICAL_KEYS` plus a
  test. Nothing here needs a sync library; the board record is one file per board and the store's existing layers.

## 4. What I could not check, and why

- **Round 0's actual C6 files** (`c6-digit-labels.json`, `c6-io-labels.json`, the final record): they lived in the
  runner's scratch folder, not in the repository; I reproduced the mechanisms on copies of the S3 file. The chain on the
  final C6 record was not re-run.
- **A short in copper from digit labels:** not observed — in tsci 0.0.2621 both `.Mcu > .17` and `.Mcu > .3V3` reached
  their own holes. The catalogue's and the runner's "joined" wording is a reading of port hints, as mine is; whether a
  different selector path or tscircuit version resolves the doubled pin to the wrong hole is —.
- **The live `check_vendor_pins.py` write:** not re-run — it writes into the plugin folder, which I may not write; the
  path was shown by calling `cached_header()` with no network.
- **The Wokwi simulation stage** (`wokwi-cli`, a token, paid minutes): not run; the converter alone was run on the digit
  build, and the registry was read from disk.
- **`tsci convert` of Seeed's XIAO footprint:** not re-run; the claim is the bin's CLAUDE.md's, and the footprint file
  left that repository (B12).
- **F0's geometry step in general:** round 0 parsed one DFRobot dimension drawing; whether every DFRobot drawing is a
  vector PDF with the outline as a scale reference is —. The variant for the Beetle ESP32 (DFR0575) is — (no
  `DFRobot`-named row in `boards.txt`).
- **Exit codes of the two `check_spine` runs:** not captured (a pipe swallowed them); the stage markers `[????]` and
  `[!!]` are quoted instead.
- **The P178 context** (#17's typed `origin`, the shared store): read for what a board record must be; nothing here
  decides where a board record lives — that is the store-levels area's and the PO's.

## 5. Searches

- **Fetch (read-only, `gh api`), 2026-10-10:** `repos/espressif/arduino-esp32/contents/boards.txt` (`.size` 3,162,786
  bytes), grepped for `^[a-z0-9_]*\.name=.*DFRobot` and `build.variant=dfrobot` → 11 DFRobot variants, among them
  `dfrobot_firebeetle2_esp32c6`, `dfrobot_beetle_esp32c6`, `dfrobot_romeo_esp32s3`, `dfrobot_firebeetle2_esp32s3`.
  Decision served: whether C8's variant step can be mechanical from the drawer label. **Used** (C8, RC-6).
- No web search; the Espressif documentation MCP was not queried. The tscircuit grammar, the Wokwi registry and the
  arduino header parser were read from files on this machine.
