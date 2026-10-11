# Verification — board records and footprints (P158 part 1, area `board-records`)

Written 2026-10-10 by the area's refuter against `~/Development/spark` at `a8aa34d` (spark 0.8.1, `.claude-plugin/plugin.json`),
the commit the diagnosis names. Every root cause was opened at its cited lines and the lines are quoted below; where a run
decided the verdict it was re-run here, never taken from the diagnosis. Tags: E a pointer or a run and what it printed, H a
claim with its source, D a decision (who, when), — unknown.

**How the runs were made.** The PO's store was copied once (`cp -R ~/.local/share/spark <scratch>/store`) and every spark
command ran with `SPARK_HOME=<scratch>/store HOME=<scratch>/home TMPDIR=<scratch>/tmp` as three words; `env | grep
SPARK_HOME` under that prefix printed `<scratch>/store`. Builds used `tsci 0.0.2621` with `@tscircuit/core 0.0.1958` from the
bin's `node_modules/.bin`, read-only, with the working directory under `<scratch>`. Nothing was written under
`~/Development/spark` outside this folder, nor under the real store, the bin, irrigation or plant-alarm. Line numbers are
spark's at `a8aa34d`; tscircuit's are core 0.0.1958's `dist/index.js`.

## Verdicts

### RC-board-records-1 — holds

Lines read (E):
- `scripts/emit_footprint.py:178-179`: `'      <platedhole portHints={[%s]} pcbX="%gmm" pcbY="%gmm" '` /
  `'outerDiameter="%gmm" holeDiameter="%gmm" shape="circle" />' % (json.dumps(label), x, y, pad, hole))` — one hint per
  hole, the `header_order` label.
- `scripts/emit_board.py:790-791`: `lines.append('    <trace from=".Mcu > .%s" to=".%s > .%s" />  {/* %s */}'` /
  `% (entry["pin"], target[0], target[1], …` — the selector is the `pins` key.
- `scripts/emit_board.py:879`: `lines.append(power_trace("Mcu", pad, net, rules, unjustified=unjustified))`, and `:159`:
  `return '    <trace from=".%s > .%s" to="net.%s"%s />%s' % (` — the power selector is the `power_pads` key. (The
  diagnosis cites `:868`; that line is the `NAMES NO RAIL` comment. The trace is at `:879` through `power_trace`. A
  pointer, not a finding.)
- `scripts/boards.py:352`: `if name not in pads and aliases.get(name) not in pads:` — the validator accepts an aliased key.
- `scripts/assign_pins.py:407`: `pad = ((board.get("physical") or {}).get("pad_aliases") or {}).get(entry["pin"], entry["pin"])`
  — for the comment in `pins.py` only.
- `scripts/check_vendor_pins.py:78-79`: `theirs = vendor_pins.get(label)` / `if theirs is None:` — a `pins` key the vendor's
  header does not define is a mismatch, so renaming `MISO` to `MI` breaks the check, as C2's alternative paragraph says.
- `grep -rn pad_aliases scripts tools/circuit-to-wokwi/lib` (2026-10-10): `boards.py:350,354,360`, `assign_pins.py:407`,
  `mapping.ts:94`, `board.ts:61,102,112` — nothing in `emit_footprint.py` or `emit_board.py`.

Re-run (E, 2026-10-10): 21 `led-red-5mm` on `firebeetle2-esp32s3`, `emit_board.py … --assume-missing-sizes` → exit 0, stderr
empty, `.Mcu > .MOSI` at output line 161, `.Mcu > .MISO` at 162, `.Mcu > .A4` at 174 — the diagnosis's line numbers exactly;
`emit_footprint.py … -o` → `portHints={["MI"]}` (line 22), `["MO"]` (23), `["A4"]` (38), 0 occurrences of `MISO`, `MOSI`
or `"SS"` (`/usr/bin/grep -c`). A three-hole probe footprint built with tsci: a hole hinted `["MI"]` and a trace to
`.Mcu > .MISO` → `source_trace_not_connected_error: Could not find port for selector ".Mcu > .MISO". Component ".Mcu > "
found, but does not have pin "MISO"`; a hole hinted `["MO", "MOSI"]` and a trace to `.Mcu > .MOSI` → resolved, one
`pcb_trace` leaving that hole. So the join is by hint equality and a second hint is enough — C2's mechanism, shown.
`check_spine.py` on the 21-LED file (`--keep`): `[!!  ] build  Led07SeriesA.pin1 (a terminal connected to nothing);
Led08SeriesA.pin1 (a terminal connected to nothing). A board builds, routes and reports no error with a component joined to
nothing …`, `the chain is broken`, exit 1 — the diagnosis's message, verbatim.

Two things the diagnosis does not say, both E:
- The record itself states the fault: `boards/firebeetle2-esp32s3.json:97` `"//pad_aliases": "… A footprint generated from
  the silkscreen gives a pad called MI while the design writes a trace to MISO, and they do not connect — silently, because
  nothing downstream knows the two words mean one pad."` The record's author knew; the footprint writer was never taught.
  "Design" is the right kind: the table was designed as the bridge, and one of the two writers never consulted it.
- A data route exists and round 0 took it (`council/round-0-runner.md:24`): pads labelled with the vendor's names, `SS→A4
  the only alias`, `[ok] build 5 trace(s)`. It works by giving the footprint the vendor's word instead of the silkscreen's,
  which is what `pad_aliases` exists to avoid. The diagnosis weighs renaming the key; it should also name relabelling the
  pad, since that is the workaround a person meets first. C2 loses neither word.

### RC-board-records-2 — holds, as the diagnosis itself narrowed it

Lines read (E):
- `scripts/boards.py:344-349`: `if order:` / `pads = set()` / `for key, labels in order.items():` /
  `if key.startswith("//"):` / `continue` / `pads |= set(labels)` — labels are collected; nothing is checked about them.
- `scripts/boards.py:418-419`: `for label in pins if isinstance(pins, dict) else {}:` /
  `if not re.fullmatch(parts.SELECTOR_SAFE, label):` — the name rule walks `pins` keys (and `power_pads` keys at `:422-423`),
  never labels.
- `scripts/parts.py:185`: `SELECTOR_SAFE = "^[A-Za-z0-9_]+$"` — a string of digits passes.
- `@tscircuit/core 0.0.1958 dist/index.js:11651-11653`: `var getPinNumberFromPortHints = (portHints) => {` /
  `for (const hint of portHints ?? []) {` / `if (/^\d+$/.test(hint)) return Number(hint);` and `:11654`
  `const pinNameMatch = /^pin(\d+)$/i.exec(hint);`; `:9621` `if (!/^(pin)?\d+$/.test(normalizedHint)) continue;` (the
  function `getPinNumberFromHints` is at `:9618-9625`, not `:9622-9627` as cited); `:12484` `const pinNumber =
  labels.find((p) => /^(pin)?\d+$/.test(p));`; `:4348` `...typeof props.pinNumber === "number" ? [`pin${props.pinNumber}`,
  props.pinNumber.toString()] : [],` (in `getNameAndAliases`, `:4342-4352`).
- `tools/circuit-to-wokwi/lib/netlist.ts:68`: `const named = hints.filter((hint) => !/^(pin)?\d+$/.test(hint));`.
- `scripts/emit_footprint.py:175`: `# P87's attribute half: a label no pin names is held to no name rule (the FireBeetle's D-
  and D+ are none), so it` — the deliberate part, which C1 leaves standing.

Re-run (E, 2026-10-10): a four-hole probe footprint with hints `A`, `3`, `X`, `B` in that order and traces to `.Mcu > .3` and
`.Mcu > .X`; `tsci build` → `Build exiting with code 0`, 0 error elements, **5 `source_port`s for 4 plated holes**:
`source_port_2 pin3 pin_number=3 hints ['pin3','3']` at the hole x=2.54 mm (position 2, printed `3`); `source_port_3
pin3_internal_1 pin_number=None hints ['pin3_internal_1','pin3','3','X']` at x=5.08 mm (position 3, printed `X`);
`source_port_4 pin2 pin_number=2 hints ['pin2','2']` with **no `pcb_port`** — a phantom. Both traces reached their own holes
(`pcb_trace` ends at (2.54, 0) and (5.08, 0)). So the pad printed `X` also answers to `3` and `pin3`; the selector
`.Mcu > .3` matches two ports and tscircuit took the first; a selector `.Mcu > .pin2` would land on copper that does not
exist. No copper short — which is what the diagnosis's "what this build did NOT show" says, and the catalogue's K22 wording
("joins 3V3 to the pad printed RX") is a reading of hints, as the diagnosis says. spark's emitter never writes `pin<N>`
selectors for the Mcu, so the phantom is not a spark exposure today; it is one for a hand-edited `board.tsx`.

### RC-board-records-3 — partly

Lines read (E):
- `scripts/boards.py:19`: `The contract is enforced rather than documented. A board definition that a person merely` — a
  stated design decision, which the diagnosis quotes.
- `scripts/boards.py:62-63`: `REQUIRED_KEYS = ("schema", "id", "name", "chip", "wokwi_part_type",` /
  `"pins", "wake_capable_gpio", "adc_gpio", "physical")` — `physical` required, no shape.
- `scripts/boards.py:363-367`: `for role_name, role in (board.get("pin_roles") or {}).items():` /
  `if role_name not in PIN_ROLES:` / `problems.append(` / `f"pin_roles.{role_name} is not a role any script reads, so it
  would be carried "` / `f"and ignored. Known: {', '.join(sorted(PIN_ROLES))}")` — no `//` skip, unlike `:347` and
  `emit_footprint.py:128` (`row_keys = [key for key in order if not key.startswith("//")]`).
- `scripts/emit_footprint.py:162-163`: `"// The holes are %.2f mm, NOT the %s mm on the vendor drawing. That figure is
  their"` / `% (hole, physical["header"].get("drill_mm", "?")),`.
- `boards/README.md:55-58`: the `id`, `pins`/`power_pads` names and `drill_mm` rule — the only prose about keys; `:3-4` the
  note that the steps are the bin's.
- `docs/guide/how-it-works.md:145` (not `:150` as cited): `… boards/README.md … has the schema, and the rule that a board
  definition carries facts, never decisions` — a claim the README does not meet.
- `scripts/boards.py:319-325` (two `pins` keys on one GPIO legal) and `tests/test_boards.py:235-237`
  (`test_two_labels_on_one_gpio_are_allowed`) — as cited.

Where it is narrower than the code: the diagnosis counts "three keys the shipped S3 file carries [that] have no reader at
all: `flush_edge`, `corner_radius_mm`, `mounting_holes`". My grep over `scripts/*.py`, `tools/*.py`,
`tools/circuit-to-wokwi/lib` and `cli.ts` (2026-10-10) finds no reader of two more: `physical.thickness_mm`
(`firebeetle2-esp32s3.json:27`, `1.6`; `emit_board.py:116` takes the board's thickness from
`fab.process("board_thickness_mm")`, the new board's, not the module's) and `physical.header.pad_mm` (`:39`, `1.5`; the
generator computes its own pad at `emit_footprint.py:69-80`). So five keys are carried and unread, and `drill_mm` is read
for one comment. **Sentence to change:** "three keys the shipped S3 file carries have no reader at all" → five, naming
`thickness_mm` and `header.pad_mm`; and C3's example refusal lists `thickness_mm` among the *Known* keys, which contradicts
C3's own test ("every member of `PHYSICAL_KEYS` is read by a named script") — drop it from the list or give it a reader.

The design half holds against the rival "it is deliberate": `boards.py:19` makes the refusals the documentation on
purpose, and `PIN_ROLES` refuses an unread role for the reason at `:89-94`; nothing equivalent guards `physical`, so an
accepted-and-unread key is the one case the deliberate design does not cover.

### RC-board-records-4 — holds

Lines read (E): `scripts/emit_footprint.py:225-230`: `if args.out:` / `Path(args.out).write_text(text)` /
`return _report(args, EXIT_OK, "wrote %s (%d pads, %.2f mm holes)"` / `% (args.out, len(pads(board)),
hole_diameter_mm(rules)))` / `sys.stdout.write(text)` / `return EXIT_OK`; `:235` `if args.json:` — inside `_report`, the only
reader of `args.json`.

Re-run (E): `emit_footprint.py --board firebeetle2-esp32s3 --json` → exit 0, stderr empty, 51 lines on stdout beginning
`// Generated by spark's emit_footprint.py from boards/firebeetle2-esp32s3.json — do not hand-edit.`; `json.loads` of it
→ `Expecting value: line 1 column 1 (char 0)`. With `-o fp.tsx --json` → `{"check": "emit-footprint", "status": "ok",
"message": "wrote fp.tsx (32 pads, 1.00 mm holes)"}`. Added E: `tests/test_json_contracts.py:142-146` characterises
`emit_footprint` with `-o` only, so the suite pins the path that works and never ran the one that does not.

### RC-board-records-5 — holds

Lines read (E): `scripts/check_vendor_pins.py:98-99`: `#: The plugin's own cache: the boards it ships come with their vendor
headers fetched.` / `PLUGIN_ROOT = Path(__file__).resolve().parent.parent`; `:111-112`: `own = path.parent.parent /
CACHE_DIR / name` / `return own if own.is_file() else PLUGIN_ROOT / CACHE_DIR / name`; `:137-138`:
`cache.parent.mkdir(parents=True, exist_ok=True)` / `cache.write_text(header)`. The whole file was read: no `import store`,
no `SPARK_HOME`, and the result's `source` (`:139`) names the repo, not the path written.

Re-run (E): `cached_header(<scratch>/proj-k14/boards/firebeetle2-esp32s3.json, "dfrobot_firebeetle2_esp32c6")` with no
network → `~/Development/spark/.spark/cache/dfrobot_firebeetle2_esp32c6.pins_arduino.h`. `git ls-files .spark/cache` →
`XIAO_ESP32C6.pins_arduino.h`, `dfrobot_firebeetle2_esp32s3.pins_arduino.h` (tracked); `git status --short` → `??
.spark/cache/dfrobot_firebeetle2_esp32c6.pins_arduino.h` — round 0's write is still in the plugin folder on 2026-10-10.
The tracked two are read by `tests/test_check_vendor_pins.py:160-172` (`TheRealBoardsAgreeWithTheirVendors`) and
`:123-133` (the P10 test), as the diagnosis says. "The cache predates the store" is H (the diagnosis's); the code's
docstring at `:104-108` explains the READ fallback (P10, intake R12) and says nothing about writing — consistent with the
write being a side effect of reusing the read path.

### RC-board-records-6 — holds

Lines read (E): `scripts/needs.py:320-321`: `notes += ["%s: a board needs a board file — a record in boards/ — before spark
can build with it" % key` / `for key in _unfiled_boards(after, known, entries)]` — a note; `:513-516`: `return
[parts._problem(key, "picked as the board, but a board needs a board file — a record in boards/ — before spark can "` /
`"build with it, and it has none; %s" % said,` / `'%swrite a board file for %s first (docs/guide/how-it-works.md, "Your own
dev board")'`; `scripts/parts.py:2002-2008`: `if not problems and not args.dry_run:` / `store.add_project(target)` /
`drawer.apply(changes)` / `for event in events:` / `store.append_event(event)` / … / `needs.write(target, after)`.
`OPERATIONS` (`parts.py:1472-1529`) has `skeleton` for a part ("write a record to fill in, to the project's parts/") and no
board operation; `commands/research.md` names "board" only as the PCB (grep, 2026-10-10).

Re-run on the store copy (E): `--pick <proj> board=dfrobot-dfr1075` → `set dfrobot-dfr1075: used_in null → {"proj-k29":
1}` · `dfrobot-dfr1075: a board needs a board file — a record in boards/ — before spark can build with it` · `listed
proj-k29 on your projects` · `wrote to your history: 1 reused`; `--requirements <proj>` → `refused, so nothing was written:
dfrobot-dfr1075 — picked as the board, but a board needs a board file … spark has one that builds for
firebeetle2-esp32s3; xiao-esp32-c6 stops at the footprint stage (P121) …`; afterwards the copy's
`drawer/dfrobot-dfr1075.json` holds `used_in {'proj-k29': 1}`, the last history line is
`{"event":"reused","project":"proj-k29","need":"board","entry":"dfrobot-dfr1075"}`, and `projects.json` names the project.
The entry's fields are as the diagnosis lists: `label`, `count 2`, `part_number`, `from`, `bought`, `unsure`; no `is`, no
`function`.

Rival weighed: this is not a fault nobody saw. #99 (P162, read 2026-10-10) says "it has no flow for a BOARD", and the
catalogue files "warned at the pick, refused at `--requirements`" under *by design, disputed*. The diagnosis's kind, "a
missing operation", is the same statement; what it adds is the exact state the refusal leaves behind (hold, event,
listing). C8's pick-side change (not writing `reused`) alters that by-design behaviour — the PO's call, not a bug fix.

### RC-board-records-7 — holds

Lines read (E): `boards/xiao-esp32-c6.json:18-27` — `physical` holds `footprint_module`, `footprint_export`, `width_mm`,
`height_mm`, `wokwi_size_px` and nothing else; no `power` key anywhere in the file (`grep -n io_volts boards/*.json` →
`firebeetle2-esp32s3.json:413` only); `:123` `… this file has no header_order yet for a pad_aliases entry to point at.`
`scripts/boards.py:246`: `return parts.STOPS_AT_FOOTPRINT if isinstance(board, dict) and
emit_footprint.footprint_gaps(board) else ""`; `:395-399`: `for key in REQUIRED_FOR_FAB:` / `if not physical.get(key):` /
`problems.append(` / `f"physical.{key} is not set: no verified footprint for this board, "` — two names (`REQUIRED_FOR_FAB
= ("footprint_module", "footprint_export")`, `:67`). `scripts/emit_board.py:659-664`: `supply, forward = fact_value(board
or {}, "power", "io_volts"), …` / `raise ValueError("%s asks for %g mA through a series resistor, but %s — nothing to
compute it from"` / … `else "the board states no power.io_volts"))`; `:1117-1121` catches it as `cannot emit a board: %s`,
`EXIT_COULD_NOT_RUN`. `scripts/check_spine.py:333-385`: board, parts, schematic, footprint, build — in that order.

Re-run (E): in a scratch project whose `active.json` names the XIAO, `boards.py --validate --for-fab --project …` →
`active  xiao-esp32-c6 (library): ok`, exit 0; `--list` → `* xiao-esp32-c6 (library) stops at the footprint stage (P121) —
no header geometry in its board file`; `check_spine.py requirements.json`, run from inside the project (the script has no
`--project` flag: `error: unrecognized arguments: --project …`), on `{"board": "xiao-esp32-c6", "parts":
["led-red-5mm"]}` → `[ok  ] board  Seeed XIAO ESP32-C6` · `[????] schematic  cannot emit a board: led-red-5mm asks for 5 mA
through a series resistor, but the board states no power.io_volts — nothing to compute it from` · `the chain was NOT
exercised — this is not a pass`, exit 2. #55's "Value proven by" (read 2026-10-10): "`boards.py --validate --for-fab` fails
a board with no header geometry" — not met today.

Rival weighed: the guide already says so — `docs/guide/how-it-works.md:175-178`: "No contract check catches missing header
geometry: `boards.py --validate --for-fab` answers ok on the XIAO, which has none (P121) …". The diagnosis should cite it:
the geometry half is documented and carded (#55 open); the `io_volts` half is the part no page states, and the part that
makes the `--list` label wrong for the one part most likely picked.

### RC-board-records-8 — partly

Lines read (E): `scripts/parts.py:65-69` `KIND_FUNCTION = {… "board": ("compute", "microcontroller")}`; `:74-75`: `if
record.get("function") and not function_problems(record):` / `return record["function"]` — a malformed `function` falls
through to the kind with no word; `scripts/needs.py:177`: `functions = parts.function_of(record, board=kind == "board") +
[f for e in holding for f in e.get("function") or []]`; `boards.validate` (`:281-441`, read whole) never names `function`;
`grep -n '"function"' boards/*.json` → nothing.

Re-run on the store copy (E): needs `board / compute / microcontroller` and `report / communicate / wifi`; `--match` as
shipped → `report — communicate / wifi` · `nothing in the store does this — a gap`. A project copy of the S3 carrying
`"function": [{"does":"compute","what":"microcontroller"},{"does":"communicate","what":"wifi bluetooth"}]` → `--validate`
ok, `--match` → `owned 1    firebeetle2-esp32s3 (project)                  wifi bluetooth  free 0`. The same copy with
`"function": "not a list"` → `--validate` `ok`, `--match` → `a gap` again and no word about the dropped key — the silent
drop, shown.

Where it is wider than the code: the diagnosis says "The slot exists; the data and the sentence saying it may be filled do
not." The drawer has both already. `scripts/drawer.py:24` `FIELDS = ("label", "count", "part_number", "revision", "is",
"function", …)`, `:71-73` checks it (`'a function is [{"does": one of %s, "what": words}]'`), `commands/drawer.md:28`
documents it, and `needs.py:177` adds a holding entry's functions to the board's. Run (E): `--drawer-set` on the copy's
`dfrobot-dfr0975` with `function: [{"does":"communicate","what":"wifi bluetooth"}]` (dry run printed `would set …`, the
real run `set dfrobot-dfr0975: function null → …`), then `--match` on a project with no board copy → `report —
communicate / wifi` · `owned 1    firebeetle2-esp32s3 (library)                  wifi bluetooth  free 0`. **Sentence to
change:** "nothing tells the record's author that it could say more" → "the board *record* has no documented `function`;
the *drawer entry* has one, documented, and the matcher reads it — a statement about the piece a person owns, where a fact
about every board of that SKU belongs." C10's case then rests on where the fact belongs (the record, with a source), not
on the slot not existing; the diagnosability finding — a malformed `function` on a board is accepted by `--validate` and
dropped by `--match` without a word — stands as shown.

### RC-board-records-9 — holds

Lines read (E): `scripts/boards.py:307-310`: `wokwi_pins = board.get("wokwi_power_pins")` / `if isinstance(wokwi_pins,
dict) and board.get("wokwi_part_type"):` / `for pad in sorted(board.get("power_pads") or {}):` / `if pad not in
wokwi_pins:` — `pins` values are compared with nothing; `tools/circuit-to-wokwi/lib/mapping.ts:96` `byName[name] =
WOKWI_NAMES_PINS_BY_GPIO ? String(gpio) : name;` and `:108` `return { ...byName, ...(board.wokwi_power_pins ?? {}) };` —
merged last, so an entry there overrides a GPIO's number. `lib/geometry.ts:93-101` `pinsOf` reads the bundled registry.

Registry read myself (E, `tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/registry/parts.json`, package
version 0.1.1, a list of 137 parts): `board-esp32-s3-devkitc-1` has 44 pins — `0`–`21`, `35`–`42`, `45`–`48`, `5V`, `RX`,
`TX`, `RST`, `3V3.1`, `3V3.2`, `GND.1`–`GND.4` — and no `43`, `44`; `board-esp32-c6-devkitc-1` has 32, none of `14`, `16`,
`17`. `dist/converter.mjs` names `board-esp32-c6-devkitc-1` once (`grep -c`). Stronger E than the diagnosis gives for the
"latent" S3 case: the 21-LED design placed an LED on `.Mcu > .TX` (GPIO43; `console_uart` costs 40 in
`assign_pins.py:73`, a penalty, not a refusal), so a design that reaches it exists today and would stop at the simulation
with `"43" is not a pin of board-esp32-s3-devkitc-1`, hidden only because that design breaks earlier (RC-1).

Two things the diagnosis does not say: (a) the record's own `//wokwi_part_type` (`firebeetle2-esp32s3.json:104`) states the
stand-in "exposes GPIO 0-21 and 35-48 - a superset of every pin this board brings out - and it names its pins by raw GPIO
number" — by name it does not: 43 and 44 are `TX` and `RX`; the record is wrong exactly where C11 would check; (b)
`boards/README.md:97` "a stand-in costs only the silkscreen labels in the picture" — the same claim in prose (K32 cites
it).

## Missed root causes

- **M1 (E) — The chain's build stage prints the island and drops tscircuit's own error, which names the cause.**
  `scripts/check_spine.py:430-437` returns on `islands_in(...)` before `:438-441` looks at `errors`. On the 21-LED run the
  kept `dist/board/circuit.json` holds two elements `source_trace_not_connected_error: Could not find port for selector
  ".Mcu > .MOSI". Component ".Mcu > " found, but does not have pin "MOSI"` (and the same for `MISO`), and the build line
  reads `… A board builds, routes and reports no error with a component joined to nothing` — "reports no error" while the
  circuit file reports two. This is the mechanism behind RC-1's "two hops from its cause" and round 0's "unrelated open
  terminal" (`runner.md:22`); it is a check-ordering fault in `check_spine`, not a footprint fault. Against the criteria:
  a failure that names where and why already exists in the data; printing it (both findings, or the errors first) is a
  reorder, where C2's "diagnosable" clause proposes parsing `board.tsx` and the footprint to rebuild the same sentence —
  an add where a reorder would do. Shared with the chain-and-checks area.
- **M2 (E) — Statements inside the record and the README that are false.** `firebeetle2-esp32s3.json:104` (the stand-in
  "names its pins by raw GPIO number"; `TX`/`RX` are named) and `boards/README.md:97` ("costs only the silkscreen labels").
  Data and docs, under RC-9; C11 checks the pins and leaves both sentences.
- **M3 (E) — Two more carried-and-unread keys**: `physical.thickness_mm` and `physical.header.pad_mm` (grep as under
  RC-3). RC-3's count and C3's *Known* list both miss them.
- **M4 (E) — The drawer entry's `function` is an existing, documented route for "what the board gives for free"**
  (`drawer.py:24,71-73`, `commands/drawer.md:28`, `needs.py:177`; the run under RC-8). RC-8/C10 should say both slots exist
  and decide which one a board's WiFi belongs in: a fact about the SKU → the record; a fact about this piece → the drawer.
- **M5 (E) — The stop sentence has two spellings**: `parts.py:1920` `STOPS_AT_FOOTPRINT = "stops at the footprint stage
  (P121) — no header geometry in its board file"` and `needs.py:511-512` `"; %s stop%s at the footprint stage (P121) — no
  header geometry in %s board file"` (`_board_problems`). The diagnosis's "one rule by which a board stops, said by three
  places" is true of the rule (`footprint_gaps`) and not of the sentence. C9 must change both, or they disagree the day a
  board has two stops (W16).
- **M6 (E, code read) — The digit grammar applies to `pins` keys too; C1 covers labels only.** `SELECTOR_SAFE`
  (`parts.py:185`) accepts `"17"`; a key `"17"` aliased to a non-numeric pad (`pad_aliases: {"17": "D3"}`) passes
  `boards.py:352` and is written as `.Mcu > .17`, which tscircuit reads as pin position 17 (`index.js:11653`). One more
  line in C1's rule covers the key side.
- **M7 (E) — The stand-in check C11 scopes to `wokwi_pin_naming: gpio` misses the silkscreen case.** The registry's
  `board-xiao-esp32-c6` has 15 pins: `5V`, `D0`–`D10`, `3V3`, `GND`, `$gpio15`. The XIAO's `pins` keys `SDA`, `SCL`, `SS`,
  `MOSI`, `MISO`, `SCK`, `A0`–`A2` (`xiao-esp32-c6.json:41-49`) are not among them, and `mapping.ts:96` maps a silkscreen
  board's key to itself, so a trace to `.Mcu > .SDA` would stop with `"SDA" is not a pin of board-xiao-esp32-c6`. Also the
  XIAO's `wokwi_power_pins` keys `V33`, `GND`, `V5` (`:12-16`) name pads that no `header_order` and no `power_pads` hold;
  the check at `boards.py:309` iterates `power_pads`, which the XIAO lacks, so nothing is compared. Hidden today only
  because the XIAO stops before the simulation (RC-7).
- **M8 (E) — The phantom port.** In the digit probe the displaced pin number left `pin2` with no `pcb_port` (RC-2's run).
  Not reachable from spark's emitter; reachable from a hand-written trace. Belongs in RC-2's statement of effects.
- **M9 (E) — `tests/test_json_contracts.py:142-146` pins `emit_footprint` with `-o` only** — the characterisation that let
  RC-4 live; C4's test is that test's second case, not a new file.

## The changes, judged

Criteria (the PO, 2026-10-10): testability · diagnosability (a failure names where and why, to a person and to an agent
reading the output) · simplicity (remove before add). For each: mechanism or symptom; would the named test catch the
regression; does the message name where and why; would a removal do; what it touches for the bin, irrigation,
plant-alarm (their files read 2026-10-10, see the next section).

- **C1 (refuse a bare-number label)** — mechanism (tscircuit's grammar against an unchecked label). The test catches a
  regression: `validate()` on a digit-label fixture is deterministic and needs no toolchain. The message names row, index,
  the number and the colliding pad. No removal would do (there is no rule to remove). Add M6's key side, and match both of
  tscircuit's regexes (`/^\d+$/` and `/^pin(\d+)$/i`, `index.js:11653-11654`). Users: neither shipped board has a numeric
  label (S3 `:60-95` read; the XIAO has no `header_order`) — green.
- **C2 (`pad_aliases` reaches the footprint)** — mechanism, shown by the alias probe. The S3 regression test (`MI` hole
  hints `["MI", "MISO"]`) catches a regression without a toolchain; the 21-LED end-to-end needs tsci and belongs with the
  tests that already need one. **The validator rule as written is self-contradictory**: "an alias target must be a label
  that is not itself a `pins` key (so `SS → A4` stays legal …)" — `A4` *is* a `pins` key (`firebeetle2-esp32s3.json:162`,
  `"A4": 10`), so that rule would refuse the S3's own file. The rule that fits the fact: when the target is also a key,
  both keys must map to the same GPIO (`SS` and `A4` are both 10). Diagnosability: the proposed reading of `board.tsx` and
  the footprint is an add; M1's reorder prints tscircuit's own sentence (`Could not find port for selector ".Mcu >
  .MISO"`) for free — do that first, then judge whether the reconstructed hint is still needed. Users: the hints of every
  regenerated S3 footprint change. irrigation commits a spark-generated `FireBeetle2Esp32S3.tsx` (its first line is the
  generator's header; one `["MI"]` hint) and a `board.tsx` whose Mcu traces are `3V3, A0, A1, A2, A5, D3, D6, D10, D11,
  D12, GND1, GND2, GND3, SCL, SDA, VCC` — no aliased pad, so no functional change, and the committed footprint drifts
  from the generated one with nothing saying so (K20's shape). The bin's `FireBeetle2Esp32S3.tsx` is made by its own
  `tools/generate-firebeetle-footprint.py`, not by spark — untouched; its converter copy merges aliases the same way
  (`tools/circuit-to-wokwi/lib/mapping.ts:94-108` in the bin) — untouched.
- **C3 (the schema written where it is enforced; unread keys refused)** — mechanism for K24/K26 and for K27's holes. The
  test as described (walk both files; every `physical` key in `PHYSICAL_KEYS`; every member read by a named script, by
  grep) catches drift both ways — once the *Known* list is corrected (M3: drop `thickness_mm` or read it; add
  `header.pad_mm` to the removals). The message mirrors `PIN_ROLES`'s and names where and why. Remove before add:
  deleting `flush_edge`, `corner_radius_mm`, `thickness_mm`, `header.pad_mm` from the S3 file *is* the removal; emitting
  mounting holes is an add that changes every generated footprint (irrigation's committed one drifts again) and puts four
  more drills under `check_footprints.check_through_hole_drills` (`:165`) — whether 2.0 mm holes pass its floor is — (not
  run). Users: the bin has **no board file of its own** (`ls boards/` → `active.json` only) and its `Makefile:49-53, 96,
  182, 232` run spark's `boards.py --path/--id/--paths/--get`, `--resolve`, `--validate --for-fab` and `--validate` against
  the *library* S3 file, so a new refusal lands on the bin's `make check` the moment it merges unless the library file is
  cleaned in the same change; the bin's committed `.spark/board.json` (resolved 2026-10-04, carrying the five keys) is
  re-resolved by `make` on the bench machine and read by CI for `id`, `chip`, `micropython_port` only (`Makefile:55-60`)
  — no break there. The bin's `tools/generate-board-spec.py` reads `pins`, `pin_roles`, `name`, `id`, `chip`,
  `wake_capable_gpio`, `adc_gpio` — none of `physical`.
- **C4 (`--json` on every path)** — mechanism; the "could-not-run without `--out`" variant removes a path and is the
  simpler one. Test: the no-`-o` case added to `test_json_contracts.py:142` (M9). Users: `check_spine.py:379-381` calls
  `emit_footprint.main` with `-o` — unaffected; the bin's Makefile does not call `emit_footprint` (grep → nothing).
- **C5 (the drill sentence)** — the symptom, correctly small; its test is exact. Fine.
- **C6 (one comment-key rule)** — the kind is consistency, not bug: the shipped file's convention is a comment *beside* a
  keyed table (`"//pins"`, `"//pad_aliases"`, `"//power_pads"` at the parent) and *inside* only a dict read by field name
  (`header`, a `power_pads` entry). The real friction is the refusal text for `//jtag` ("not a role any script reads"),
  which is wrong for a comment. A helper is fine and adds a small hazard — a `//`-prefixed `pins` key disappears silently
  — acceptable because `//` is explicit. The test as described catches it.
- **C7 (the cache lives in the store)** — mechanism; the test (patched fetch, `SPARK_HOME` at a temp dir, plugin folder
  unchanged) catches the regression; the `cached at <path>` line names where. Say whether the write goes through
  `store`'s writer (0600/0700, and the git-tree refusal at `store.py:212-214`) or `Path.write_text` — the diagnosis does
  not. Users: the bin's `Makefile:220` runs `check_vendor_pins.py $(BOARD_FILES) --offline` and `:223` the live check, on
  the library's S3 file — the read-only fallback to the plugin's tracked copy keeps `--offline` green; after a live run the
  written copy lives in the store, which the bin's `--offline` must then find (the fallback order decides; say it).
- **C8 (a board skeleton from a drawer entry)** — the design of a decided item (#99's board half; D8, the PO 2026-10-09),
  not the fix of a fault nobody saw; size L. Mechanism for K29. Testable as described (patched fetch). Diagnosable (owed
  fields with the document to read them from) — yes. Two cautions: the per-chip table is a third statement of chip facts
  beside `soc_caps.h` and the board file — without a test that it agrees with both shipped boards it drifts; and the
  pick-side change (not writing `reused`) alters a by-design behaviour the catalogue lists as disputed — the PO decides.
  The `boards.txt` variant step is H until re-run (the diagnosis fetched it once; 3 of the PO's 4 unfiled boards named).
- **C9 (every stop from one rule; `--for-fab` requires geometry)** — mechanism for K30. Change both spellings (M5), or the
  test "a board that owes io_volts says it stops at the schematic" passes while `_board_problems` still says footprint.
  Users: the bin's `make` runs `--validate --for-fab` on the library — the S3 has geometry, green; plant-alarm (board
  `xiao-esp32-c6`, parts `sen0193-soil-moisture`, `max98357a-dfr0954`; its `board.tsx` imports a `XiaoRealFootprint`
  nobody has) would see two stops printed at `--match`/`--pick`. **The XIAO data step is not only data:** `emit_footprint.pads`
  draws two flush rows of plated holes (`:113-118`), and the XIAO is a castellated/SMD module (`footprint_module:
  "XIAO-ESP32-C6-SMD"`), so filling `physical.header` makes a through-hole footprint for an SMD part. The diagnosis's
  "On the PO's question" bullet on `footprint_source` is the honest route and should be the proposal, not a footnote.
- **C10 (`function` on boards, validated)** — mechanism for K31's record half; `function_problems` on boards is one call;
  the test catches the silent drop (shown under RC-8). Add M4: the drawer slot exists, so the change reads "the board
  record carries the sourced fact, the drawer the owned piece's", and `needs.py:177` already sums both. Users: none of the
  three runs `--match` in its checks.
- **C11 (`pins` against the stand-in)** — mechanism for K32's record side on gpio-named boards; M7 for silkscreen-named
  ones. The rule that covers both in one sentence: every `pins` key, mapped the way `mapping.ts:96,108` maps it, is a pin
  of `wokwi_part_type`. Reading the registry from `tools/circuit-to-wokwi/node_modules` couples a Python validator to an
  installed node package; a copy under `data/` with its version (the diagnosis's second option) is the testable form.
  Users: the S3 file gains `"TX": "TX", "RX": "RX"`; the bin's converter copy merges `wokwi_power_pins` last too — green.
- **C12 (remove `footprint_module`)** — a removal, the criteria's preferred direction; nothing reads the value (grep under
  RC-3). Touch points the diagnosis under-counts: `tests/test_boards.py:54, 184, 215, 250` (four fixtures),
  `docs/guide/agents.md:456` ("`physical.footprint_module` and `footprint_export`"), `boards/README.md:71`, `board.ts:48`
  in spark and `tools/circuit-to-wokwi/lib/board.ts:40` in the bin's converter copy (an interface field; absent at runtime
  it is `undefined` — no break). Only together with C9, as the diagnosis says.

## What breaks for current users

Read 2026-10-10: the bin's `Makefile`, `boards/`, `.spark/board.json`, `tools/generate-board-spec.py`,
`tools/circuit-to-wokwi/lib/*.ts`; irrigation's `boards/active.json`, `board.tsx`, `FireBeetle2Esp32S3.tsx`; plant-alarm's
`requirements.json`, `board.tsx`.

- **smartbin-local** — no board file of its own; `boards/active.json` names the library S3. `Makefile:49-53, 96, 182, 220,
  223, 232` run spark's `boards.py` (`--path`, `--id`, `--paths`, `--get`, `--resolve`, `--validate --for-fab`,
  `--validate`) and `check_vendor_pins.py` (`--offline` and live) against the library file. So C1, C3, C9, C11 and C12
  reach the bin's `make check` through the library S3 file on the day they merge: green if the library file changes in
  the same commit (C3's removals, C11's two entries), red otherwise. C2 and C3's mounting holes do not touch the bin's own
  footprint (generated by the bin's `tools/generate-firebeetle-footprint.py`). The committed `.spark/board.json`
  (2026-10-04) goes stale until `make` re-resolves it; CI reads `id`, `chip`, `micropython_port` from it only.
  `generate-board-spec.py` reads no `physical` key. C7 moves the live cache; the bin's `--offline` run must still find a
  header (the fallback order).
- **irrigation** — library S3 via `active.json`; commits `FireBeetle2Esp32S3.tsx` (spark-generated) and `board.tsx` (no
  aliased pad used). C2 and C3's holes change the regenerated footprint → the committed copy drifts with no message
  (K20/K13's shape); no functional change to its nets. C11: no `TX`/`RX` used.
- **plant-alarm** — XIAO; `board.tsx` already imports the missing `XiaoRealFootprint`; C9 prints two stops instead of one;
  if the XIAO ever gets geometry (and M7's pin names), its chain reaches the build for the first time, where new stops may
  appear — not a break, a first run.

## Searches

- `gh issue view 55`, `99`, `61` (read-only, 2026-10-10): #55's "Value proven by" line, #99's "it has no flow for a
  BOARD", #61's statement that boards/README.md's steps are the bin's. Used under RC-6, RC-7 and RC-3.
- No web search; the Espressif documentation MCP was not queried. tscircuit's grammar (`@tscircuit/core 0.0.1958`), the
  Wokwi registry (`@wokwi/diagram-lint 0.1.1`) and every spark line were read from files on this machine; `tsci 0.0.2621`
  built the two probes and the 21-LED chain under `<scratch>`.
