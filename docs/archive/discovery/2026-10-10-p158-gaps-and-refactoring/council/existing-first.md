# Existing-first — P158 part 1: what already does this, in spark, in the PO's own tools, and outside

Written 2026-10-10 by the existing-first lens, against spark 0.8.1 (main `a8aa34d`, `git log -1`). The question this lens
was given: what already does what the six diagnoses propose — in spark itself, in the person's own tools (the bin's
`make check`, its board validators, its tests), and outside (KiCad, tscircuit, Wokwi, esptool and mpremote, MicroPython's
tooling, vendor libraries, other part stores) — what each does and does not do, under what licence, and which proposed
changes duplicate something that exists. The PO's own words for this run, verbatim as relayed: *"maybe some new file
formats or synch libraries or techinques could be used from an existing library that does somwthing that would make the
whole store synch and global and loval and project store sync and rules and editor?"*

**The short answer, each line argued below.** (1) *Sync, global/local/project:* the tool is git, which spark already
requires, over the file shape the store already has (one JSON file per record, an append-only JSONL, documents under their
sha256); the design to copy is KiCad's library tables plus its Plugin and Content Manager's static checksummed index; one
spark rule (`inside_git`) stands in the way; SQLite and CRDT libraries point the other way. (2) *Rules and editor:* a JSON
Schema per file spark writes, named by `$schema`, gives VS Code validation, completion and hover documentation with no
editor built, and the same file can replace the two hand-written schemas (Python and TypeScript) of the board record;
Python's `jsonschema` is already installed on the PO's machine but is not a spark dependency — a decision. (3) *No new
file format is needed;* what is missing is identity (a project id), a reader for digests spark already writes, and a lock
beside the data.

**How this was made.** Reads only: the catalogue, the six diagnoses and their verifications, the P100 folder's reports, the
21 store cards (`gh issue view`, read-only), spark's primary artefacts (`scripts/*.py`, `data/tools.json`, `boards/`,
`docs/`, `tools/`, `tests/`), the bin's `Makefile`, `tools/` and firmware harness, and the licence and version of every
outside tool present on this machine. A copy of the PO's store was made at `<scratch>/store` (33 MB by `du -sh`; 110
drawer entries, 18 catalog records by `ls | wc -l`) with the three-word prefix verified once (`env | grep SPARK_HOME`
printed the scratch path); **no spark command was run** — this lens needed tool inventories, not store runs, and every
run cited below is a diagnostician's or refuter's, re-read not re-run. The real store, the bin, irrigation and plant-alarm
were read, never written; nothing was written under spark but this file. Tags: **E** a pointer, a command and its output,
a card number; **H** a claim with its source; **D** a decision (who, when); **—** unknown. Every number carries its
provenance.

## 1. Findings

Each: id · claim · tag · pointer · supports only.

### A. Already in spark, covering a finding wholly or in part

- **EXISTING-FIRST-1** · spark already has a per-pad Wokwi name override that can also say "the stand-in has no such pin":
  `wokwi_power_pins` is merged last into the board's Wokwi pin table and `wokwiPinName` honours a rename and a `null` for
  the board exactly as for a part. · E · `tools/circuit-to-wokwi/lib/mapping.ts:96`, `:109`, `:273-276`;
  `firmware-and-bench.verify.md` RC-1 point 2 (runs of 2026-10-10: the one-button design on `TX` simulated once the S3
  record carried `"TX": "TX"`; irrigation converted with `"D3": null` → 33 connections and no `mcu:38`);
  `scripts/boards.py:307-313` checks only `power_pads` keys against it; no page names the field (the verify's grep). ·
  supports only: the data route exists, misnamed, undocumented and unvalidated — so board-records C11 and firmware C1 reduce
  to naming, documenting, validating and deriving an existing field, not to a new mechanism.
- **EXISTING-FIRST-2** · The drawer entry already carries a documented `function` field that the matcher reads, so "what the
  board gives for free" (K31) has a slot today. · E · `scripts/drawer.py:24`, `:71-73`; `commands/drawer.md:28`;
  `scripts/needs.py:177`; `board-records.verify.md` RC-8 run (a `--drawer-set` on `dfrobot-dfr0975` with
  `communicate / wifi bluetooth` made `--match` list the board for `report`). · supports only: a slot exists; which slot a
  SKU-wide fact belongs in (the record, with a source) is board C10's decision, not a missing field.
- **EXISTING-FIRST-3** · The tools list already lets a person or a project point `roles.firmware-image` at another
  MicroPython build, so a C6 project can name its own interpreter today; what does not exist is a chip on the role or its
  contract. · E · `data/tools.json:2` ("A person's … and a project's `.spark/tools.json` override any field of any entry;
  the project wins"), `:16-23` (the contract `micropython-esp32-bin` names no chip); `scripts/tools.py:75-94` (`merged`),
  `:449-456` (`use`); the store copy holds no personal `tools.json` (E, `ls`). · supports only: firmware C2 guards a symptom
  at the image; the mechanism is a store-wide role for a board-dependent job (the firmware verify's M4).
- **EXISTING-FIRST-4** · Two drift detectors already exist as data with no reader: `based_on.digest` on every shelf copy and
  the `built` line's digests per board and part; nothing reads a digest by name. · E · `scripts/parts.py:932-941`,
  `:901-929` (the diagnoses' pointers); `store-levels-and-holds.verify.md` RC-4 (1) and M3 (`grep -n
  '\["digest"\]\|\.get("digest")' scripts/*.py` → no match; `--tally` tests only event and project, `parts.py:2148`). ·
  supports only: store C13 widens a proof nobody reads; the missing piece is one reader (an `--audit` line), after which
  K13's drift and K19's width both become visible.
- **EXISTING-FIRST-5** · `--audit` already prints the two sentences research would need — `owes: pin_order_proof,
  simulation` and `says nothing of what it does — set it once with --function-set` — while `--validate` is silent on owed
  facts by design. · E · `scripts/parts.py:1929-1931` (the needs diagnosis's pointer and run: `catalog 0 current, 17 owe
  facts`); `needs-matching-vocabulary.verify.md` M3 (`broken_problems` drops every problem about an owed key; commit
  `b9fcf8a`, 2026-10-04). · supports only: needs C5's research.md line is routing to an existing answer, not a new check;
  its proof must name `--audit`, not `--validate`.
- **EXISTING-FIRST-6** · The docs gate's mechanisms exist, and so does a recorder — on disk, gitignored: the gate's
  `OUTPUT_NOTE`, its executed `runs:` blocks and a README-only version check; the recorder `record.sh` (102 lines),
  `journey/record-journey.sh` (176) and `journey/blocks.py` (22) with their recorded outputs under `rec-out/`,
  `readme-out/` and `journey/out/`. · E · `tools/check_docs.py:20`, `:148-167`, `:170-173`;
  `.superpowers/discovery-inputs/2026-10-08/council-p97/fix-docs-recorded/` (`ls`, `wc -l`, 2026-10-10; the folder is
  ignored per `docs-and-recorded-outputs.verify.md` M1, `.gitignore:8`). `cog` is not installed (E: `which cog`, `pip show
  cogapp` → nothing). · supports only: docs Change 3 starts from "promote or delete what is there"; cog is an existing tool
  for the same job with a cost the docs verify sized (3 marker lines × 42 blocks in pages agents read raw).
- **EXISTING-FIRST-7** · Mutation testing is the acceptance bar and exists at scale — `tools/mutate.py` and 115 tables under
  `tests/mutations/`, run as anchors at every push — and K53 (a mutation scored "caught" when the mutated file no longer
  imports) is a defect in that bar. · E · `ls tests/mutations | wc -l` → 115 (2026-10-10); `tools/check_commit.py:143`;
  `catalogue.md` K53 (the grep for an import check → nothing); #94 comment 2026-10-08T23:41. · supports only: every change
  whose proof is "a mutation row" (store C3's twelve rows, firmware C4's firmware table) over-counts in its own favour until
  K53 is fixed — K53 first.
- **EXISTING-FIRST-8** · The board skeleton (board C8) is mostly a composition of readers spark already has, plus one vendor
  file: `check_vendor_pins.parse_pins`, the two tracked vendor headers, and the Arduino core's `boards.txt` as the SKU →
  variant bridge. · E · `scripts/check_vendor_pins.py:67-68`; `git ls-files .spark/cache` → the S3's and the XIAO's
  headers (the verifies); the board diagnostician's read-only `gh api` fetch of `boards.txt` (3,162,786 bytes; 11 DFRobot
  variants; 3 of the PO's 4 unfiled boards named — DFR1075, DFR1117, DFR0994; the Beetle ESP32 DFR0575 not found). · H ·
  PlatformIO's `boards/*.json` (`build.variant`) and MicroPython's `ports/esp32/boards/*/board.json` as alternative
  bridges — memory of both repositories' layouts, not read today. · supports only: steps 1–4 of C8 reuse existing parsers;
  step 5 (header geometry) stays hand work — round 0 parsed a vector PDF ad hoc in 14 minutes (`diary-round-0-board.md`).
- **EXISTING-FIRST-9** · The "one reader" was specified ten days ago and never built: the 2026-09-30 architecture's target 3,
  `outcomes.read_json(path, what)` "retiring the exit-1-for-an-unreadable-file class at eight sites", has no
  implementation; today there are ten reader functions with their own sentences and 37 raw `json.loads(… read_text/
  read_bytes …)` sites across 16 scripts. · E · `docs/archive/2026-09-30-refactoring-architecture.md:73-74`; `grep read_json
  scripts/outcomes.py` → nothing and `git log --all -S "read_json" -- scripts/outcomes.py` → nothing (2026-10-10); the
  readers `boards._read_json`, `tools._read`, `store.projects`, `drawer.entries`, `needs.read`, `design.read`,
  `parts._parse`, `parts._read_json_input`, `parts.read`, `cost._read`; raw sites by file: `parts.py` 11, `check_all.py`
  3, `check_spine.py` 3, `init_project.py` 3, the rest 1–2 each (my grep, 2026-10-10). · supports only: store C8 is the
  re-found target 3, wider than the diagnosis's thirteen store-file sites; the exit-1-for-could-not-read class the
  architecture named is still open.
- **EXISTING-FIRST-10** · One reader already globs `*requirements.json` while the writer knows one name: `init_project.
  design_in` reads irrigation's `irrigation.requirements.json`; `needs.REQUIREMENTS` is `"requirements.json"`. · E ·
  `chain-and-checks.verify.md` RC-1 (the glob at `init_project.py:68`); `scripts/needs.py:381`. · supports only: needs C8
  can reuse one existing rule (the glob, or one name) rather than add a third; the irrigation rename (its verify's M6) is
  the data fix that needs no code.
- **EXISTING-FIRST-11** · 28 of the catalogue's 74 rows already carry a fix and a size on the board: the P97 council's
  checklist C-8…C-41 on #94 — e.g. C-9 (the lock on the store folder's inode) is store C3, C-8 (`samefile`) is store C5,
  C-12 (plain-key stems) is store C7, C-10 (two-phase apply) is store C4, C-22 (one `read_json`) is store C8, C-30 (the
  skeleton's keys) is needs C5, C-36 (widen `doc_files`) is docs Change 5, C-40 (`active.json`) is chain C6. · E ·
  `catalogue.md:158`; #94 comment 2026-10-08T12:52. · supports only: for these rows the design exists; the council's work
  is the order and three decisions (holds derived or stored — store verify M2; an empty rule list — chain verify MC-1;
  `pin_order_proof` owed or broken — chain verify MC-3), not new design.
- **EXISTING-FIRST-12** · The 2026-09-30 architecture ruled out exactly the refactoring K64 asks for: "Do not refactor
  `parts.py`, `emit_board.py`, `assign_pins.py` — 72 of the 132 mutation anchors", and named "a `checks/` package" as a
  warning sign; `parts.py` has since grown from part of 1,273 lines (the three files together, 09-30) to 2,214 on its own.
  · E · `docs/archive/2026-09-30-refactoring-architecture.md:110-122`, `:129-131`; `wc -l scripts/parts.py` → 2214 (the
  catalogue's, 2026-10-10). · supports only: the two documents conflict and the PO decides; the stopping rule the earlier
  one gave ("stop when one command's behaviour has one home") is a usable test for C-41's steps.
- **EXISTING-FIRST-13** · spark already keeps one validated file for every consumer, `.spark/board.json`, which the bin's
  Make, firmware generator and TypeScript read. · E · `scripts/boards.py:45-51`, `:260-278`; the bin's `Makefile` (the
  `RESOLVED_BOARD` block) and `tools/build-flash-image.py:38`. · supports only: a new derived fact — the stand-in's missing
  pins (firmware C1(c)) — belongs in that file, not in a second resolved file.

### B. Already in the person's own tools (the bin, `~/Development/smartbin-local`)

- **EXISTING-FIRST-14** · The bin's `make check` already runs, project-privately, the four firmware checks the firmware
  diagnosis proposes: `pins-agree` (`tools/circuit-to-wokwi/check-consistency.ts`, 120 lines, over `lib/checks/
  firmware-pins.ts` 121, `scenario-pins.ts` 124, `bringup-pins.ts` 93, `wake-polarity.ts` 100 — 558 lines by `wc -l`,
  2026-10-10), `firmware-compiles` (`mpy-cross` over every module), `firmware-simulates` (`micropython
  sim/run_on_micropython.py`, 208 lines, over `tests/fake_machine.py`, 371 lines, "14 checks" per its CLAUDE.md) and
  `simulation-matches` (`bun test` plus `cli.ts --check`). · E · the bin's `Makefile` (those targets); the files' line
  counts. Two caveats, E: the bin compares `config.py` GPIO literals, which a spark project that imports `pins.py` has none
  of (`firmware-and-bench.verify.md` M3); the fake is permissive — `Pin(99)` succeeds (`docs/archive/2026-10-01-firmware-skill.md`,
  "Found on the way"). · supports only: firmware C4, C5 and C6 are ports and generalisations of checks that exist, with a
  shape change (use-against-map, not a triangle of literals) the verify named.
- **EXISTING-FIRST-15** · The retired-phrase documentation gate firmware C6 wants exists in the bin and not in spark: the bin's
  `tools/check-current-docs.py` (146 lines) has a `RETIRED` dict, an `ON_PURPOSE` list of exact quotes with reasons that
  fails when a quoted passage disappears, and a `NEGATED` rule; spark's `tools/check_docs.py` checks names, flags, output
  notes, runnable blocks, links, personal paths and the README version — no retired phrases. · E · both files read
  2026-10-10. · supports only: a port of one small file; the verify's "whatever list of retired phrases that check keeps"
  names a list spark does not have.
- **EXISTING-FIRST-16** · A second route to a footprint already exists as tooling: the bin generates the S3's footprint as a
  KiCad `.kicad_mod` from drawing numbers typed in by hand (`tools/generate-firebeetle-footprint.py`, 177 lines; its
  docstring records the 25.40 mm vs 22.86 mm row-spacing trap) and converts it with `tsci convert`; spark's own skill
  reference documents the same route for the XIAO from Seeed's OPL library. · E · the bin's script and its docstring;
  `skills/spark-design/references/tscircuit-recipes.md:36-41`. · H · Seeed's OPL library is CC BY-SA 4.0 (the bin's
  CLAUDE.md; the licence file not read today). · supports only: board C9's `footprint_source` (a converted vendor
  footprint beside a generated one) reuses existing tools; `emit_footprint.footprint_gaps` would have to accept either.
- **EXISTING-FIRST-17** · The chip guard firmware C2 wants exists in the bin as a file name, not a header read, and the
  "image to board" step exists as the bin's `deploy.sh` over `mpremote`. · E · the bin's `tools/build-flash-image.py:38-46`
  (`MICROPYTHON_IMAGE = SIM / ("micropython-%s.bin" % RESOLVED_BOARD["chip"])`, with the comment recording the C6 → S3
  incident); `firmware/micropython/deploy.sh:15-28` (the diagnosis's pointer; `mpremote rm/mkdir/cp … soft-reset`); neither
  script reads the image header (`firmware-and-bench.verify.md` RC-2 (1)). · supports only: C3 has a worked example in
  the PO's own repository; C2's header read is new to both.

### C. Outside — what exists, what it does and does not do, and its licence

- **EXISTING-FIRST-18** · `esptool` 3.3 (GPLv2+) is installed and already reads the chip id C2 wants: `esptool image_info
  <file>` exists, and its per-chip table has the S3 at 9 and the C6 only as a beta class at 7. · E · `pip show esptool`
  (Version 3.3, License GPLv2+); `python3 -m esptool image_info --help` (2026-10-10); `IMAGE_CHIP_ID` lines in the
  installed `esptool.py` (the verify names `ESP32S3ROM = 9` at `:1974-1977`, `ESP32C6BETAROM = 7` at `:2447-2449`). · H ·
  the final ESP32-C6 id (13) is in esptool 4.x's `targets/esp32c6.py` — memory, not read. · supports only: C2 can shell out
  to `esptool image_info` or copy its table with a citation; either way a minimum esptool version belongs in
  `data/tools.json`, because 3.3 cannot flash a C6 (the verify's M5).
- **EXISTING-FIRST-19** · `mpremote` 1.29.0 (MIT) is installed and already does the files half of firmware C3: `devs`, the
  connect shortcuts, `fs cp`, `run`, `mip install`, `soft-reset`, `bootloader`, `sha256sum`. · E · `pip show mpremote`;
  `mpremote --help` (2026-10-10). · supports only: the tool and its commands exist; spark's part is the plan, the yes and
  the three-outcome envelope.
- **EXISTING-FIRST-20** · MicroPython's unix port (`micropython` v1.29.0, Homebrew) and `mpy-cross` (v1.29.0) are installed,
  and the unix port's `machine` has no `Pin`, `ADC` or `I2C`. · E · `which micropython`; `micropython -c "import sys;
  print(sys.version)"`; `mpy-cross --version`; `micropython -c "import machine; print(dir(machine))"` → `PinBase, Signal,
  idle, mem8, mem16, mem32, soft_reset, time_pulse_us` (2026-10-10). · supports only: the real-runtime tier is free and
  local (the bin's `firmware-simulates` proves it), and a fake `machine` is unavoidable for it — the bin's exists; spark's
  P56 document sized a seeded, refusing one at about 250–280 code lines (H, its estimate).
- **EXISTING-FIRST-21** · `@wokwi/diagram-lint` 0.1.1 ships the 137-part registry the converter already reads, including the
  three stand-ins; its `LICENSE` file is MIT (Uri Shaked, 2023) while its `package.json` says ISC; `REMOTE_BOARDS_URL`
  points at `wokwi/wokwi-boards` for a refresh. · E · `tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/{LICENSE,
  package.json,README.md,dist/index.js:5}` (2026-10-10); the registry counts from the firmware diagnostician's offline
  read (S3 devkit 44 pins, C6 devkit 32, XIAO C6 15); `lib/geometry.ts:58-106` (`PinOracle`). · supports only: a validate-
  time check of the stand-in's pins reads a file spark already ships; copying `parts.json` under `data/` with its version
  is permitted under either licence, each requiring the notice; the discrepancy between the two licence statements should
  be noted in the copy. The `wokwi-boards` repository's own licence: — (not read).
- **EXISTING-FIRST-22** · tscircuit already names the cause spark drops, and its grammar is the one board C1 adopts: the kept
  `circuit.json` holds `source_trace_not_connected_error: Could not find port for selector ".Mcu > .MISO"` while the chain
  prints "reports no error"; the pin-hint grammar is `/^\d+$/` and `/^pin(\d+)$/i`. Licences on this machine: `tscircuit`
  0.0.2621 MIT (`package.json`); `@tscircuit/core` 0.0.1958 and `@tscircuit/cli` 0.1.2124 MIT by their `LICENSE` files
  (their `package.json` has no `license` field); `@tscircuit/footprinter` 0.0.426 and `circuit-json` 0.0.489 ISC. · E ·
  `board-records.verify.md` M1 (`scripts/check_spine.py:430-441`); `@tscircuit/core` `dist/index.js:11651-11654` (the
  verify's read); the bin's `node_modules/*/package.json` and `LICENSE` files (2026-10-10). · supports only: printing
  tscircuit's sentence is a reorder of existing output; no parser to write; every tscircuit piece spark uses is MIT or ISC.
- **EXISTING-FIRST-23** · The "editor" half of the PO's question has an existing answer: a JSON Schema per file, associated
  by `$schema` in the file or by `json.schemas`/`fileMatch` in VS Code's settings, gives validation, completion and hover
  descriptions in the editor; a validator names where and why by path. `jsonschema` 4.2.1 (MIT) is already installed in
  the PO's Python, and spark does not depend on it (`store.py` imports only the standard library). The PO edits in VS Code.
  · E · VS Code documentation ("Editing JSON with Visual Studio Code", search 2026-10-10: association by `$schema` or
  `json.schemas` with `fileMatch`; "value sets, default values, and descriptions that enable completion and hover") —
  `$schema` is a VS Code convention, not the JSON Schema specification; `pip show jsonschema` (4.2.1, MIT); my probe
  `Draft7Validator(...).iter_errors({"physical": {"header": {"drill_mm": -3}}})` printed `physical/header/drill_mm -> -3
  is less than or equal to the minimum of 0`; `scripts/store.py:10-11`; the bin's `.vscode/settings.json` (E, exists);
  memory ("Agents visible in VS Code"). · supports only: a schema file serves the board record (K24, K25, K26), the rules
  file (K46: which nulls a person can answer), the needs file (K35) and the drawer entry without building an editor;
  whether spark takes a Python dependency, or generates the schema from `PHYSICAL_KEYS`/`CHECKS` for editors only, is a
  decision (question 1).
- **EXISTING-FIRST-24** · Two hand-written schemas of the board record exist today and disagree: Python's (`REQUIRED_KEYS`,
  `emit_footprint._missing`, the validator's inline rules) and TypeScript's (`lib/board.ts:27-68`); five keys the S3 file
  carries are read by nothing. · E · `board-records.md` RC-3; `board-records.verify.md` M3 (`flush_edge`,
  `corner_radius_mm`, `mounting_holes`, `thickness_mm`, `header.pad_mm`). · H · `json-schema-to-typescript` generates the
  TS types from one schema (npm; memory). · supports only: one schema file consumed by both removes a copy; board C3's
  `PHYSICAL_KEYS` plus a test is the smaller step that leaves two schemas.
- **EXISTING-FIRST-25** · Git is already a hard dependency of spark's chain and gate, and it carries the primitives P178 asks
  for: a remote (the shared store), clone and pull (the local store), per-file conflicts named by path (where a sync client
  leaves a silent conflict copy — K9), `git status`/`git diff` as the drift report K13 lacks, and content-addressed
  objects (what `sources/<sha256>/` already imitates). For the append-only `history.jsonl`, git's `merge=union` attribute
  merges two appends without a conflict, and `recorded()` makes a duplicated line harmless. The one spark rule in the way
  is the refusal of a private place inside *any* work tree, written so a project's `git add .` never publishes the drawer.
  · E · `scripts/check_vendor_pins.py:55-64` (`gh`); `tools/check_commit.py:33-38` (`git archive`); `scripts/store.py:
  129-135` (`inside_git`), `:209-218` (`_make_ready`), `:308-311` (`recorded`), `:382-405` (`keep`); spark has no
  `.gitattributes` today (E, `cat` → none). · H · `merge=union` (git-attributes documentation; not run here). · D · the
  shared layer is a reviewed public repository of records, started when the first outsider researches a part — the PO,
  2026-10-04 (`docs/archive/2026-10-04-store-discovery.md` §6 (4)); privacy §5.8 says what never leaves the machine. · supports
  only: the sync half of the PO's question has an existing, already-required tool, and the store's file shape fits it;
  what a shared remote may hold is a privacy decision already half taken.
- **EXISTING-FIRST-26** · SQLite is in Python's standard library and would give store C4's all-or-nothing and C3's lock
  beside the data for the small tables — but it points away from the PO's direction: a synced or network file system is
  where SQLite's own guidance warns of corruption, a sync client treats one database file as one conflict, and the store's
  current shape — one JSON per entry, an append-only JSONL, documents under their checksum — is the shape git and folder
  sync merge best. CRDT libraries (Automerge, Yjs) would merge JSON automatically but bring a JavaScript or Rust runtime
  and a binary change log that takes the drawer out of `cat` and `grep` reach. · E · `python3 -c "import sqlite3"` →
  library 3.43.2 (2026-10-10). · H · sqlite.org, "How To Corrupt An SQLite Database File" (not fetched); Automerge and
  Yjs are MIT (memory). · D · "No pluggable backends now — no database, NoSQL or Markdown store" — all five lenses and
  the PO, 2026-10-04 (store-discovery §4, §6 (4)). · supports only: the diagnosis's SQLite option and the PO's "synch"
  wish pull in opposite directions; the decision of 2026-10-04 already chose files in git.
- **EXISTING-FIRST-27** · KiCad's library-table model is an existing design for "global and project", and its Plugin and
  Content Manager is an existing design for "a shared online store": a global `sym-lib-table`/`fp-lib-table` in the user's
  configuration folder and a project-specific table in the project folder, both consulted; a PCM repository is static JSON
  over HTTPS — `repository.json` → `packages.json` (sha256-checked) → package zips (sha256-checked), no server. spark's
  `layers()` and its resolved `.spark/board.json` already follow the table model, the #17 read of 2026-10-06 recommended
  "Projects follow KiCad … named by a checksum of their content", and spark already has the checked fetch and keep and
  checksummed downloads a PCM-shaped index needs. · E · search 2026-10-10 (two sources on the PCM's JSON-and-sha256 chain
  and on the two tables); `scripts/store.py:71-81`, `:345-361`, `:382-405`; `scripts/tools.py:421-434`
  (`settle_download`); #17 comment 2026-10-06T11:12. · H · "the project's entry wins on a nickname" — KiCad manual, memory;
  the search did not confirm it. · D · the user does not need KiCad; it is off the default path (the PO, 2026-10-06, P136
  D10, #70 comment 2026-10-06T19:03). · supports only: P178's shared index needs no new concept — a static checksummed
  index in a git repository is implementable with spark's existing fetch and keep; KiCad's PCM *application* (GPL-3.0, H)
  is not reusable and the PO has kept KiCad off the user's path.
- **EXISTING-FIRST-28** · InvenTree (MIT; a Django server with a REST API and a Python client; hierarchical parts and stock
  locations, multi-level BOMs, build orders) is a ready-made inventory of the drawer's kind, and it has the operation K3
  lacks — stock allocated to a build and released — but it is a server with a database, has no record contract, no chain
  facts and no per-fact provenance, and its install cuts against "free, few, local". · E · search 2026-10-10
  (github.com/inventree/InvenTree). · D · "only free things; one best tool per job, a local CLI first" — the PO,
  2026-10-06 (memory; P154 #89). · supports only: a benchmark for the drawer's operations and their names (allocate,
  release), not a replacement.
- **EXISTING-FIRST-29** · `filelock` 3.6.0 (Unlicense) is installed and would change nothing for K5: the fault is the lock's
  place, and any file lock needs a path (`home()/.lock` is one line); its one gain — no `fcntl` on Windows — is a platform
  spark does not support. · E · `pip show filelock`; `README.md:91` ("`data/tools.json` has no lines for Windows"). ·
  supports only: the store diagnosis's "a lock-file library changes nothing" holds.
- **EXISTING-FIRST-30** · Sync clients' conflict copies are never plain keys, so one existing rule catches every client
  without naming any: `PLAIN` allows only `[a-z0-9][a-z0-9-]*`; Dropbox's "(conflicted copy)", Syncthing's
  ".sync-conflict-…" and iCloud's " 2" carry spaces, dots, parentheses or capitals. · E · `scripts/store.py:99`. · H ·
  the three clients' naming (their documentation; memory). · supports only: store C7's one check on `entries()` is the
  whole fix for K9; no per-client code.
- **EXISTING-FIRST-31** · cog (MIT) exists for the re-recording job docs Change 3 names, with `--check` and `--diff`, and is
  not installed here; executable-documentation tools are many, and spark's own `runs:` blocks are already one. · H · the
  docs diagnosis's read of cog.readthedocs.io (2026-10-10). · E · `which cog`, `pip show cogapp` → not installed. ·
  supports only: an existing tool exists; whether 126 marker lines in agent-read pages are acceptable is the PO's.

### D. What each outside tool does and does not do, with its licence (as found on this machine, 2026-10-10)

| tool | here | licence (how read) | does, for a finding | does not |
| --- | --- | --- | --- | --- |
| git 2.49.0 | yes | GPL-2.0 (H, memory) | remote, clone, named conflicts, `merge=union`, content-addressed objects, `status` as drift (K9, K13, P178) | nothing about the record contract; `inside_git` must be re-scoped |
| tscircuit 0.0.2621 · core 0.0.1958 · cli 0.1.2124 | bin's `node_modules` | MIT (package.json; LICENSE files) | build, DRC elements in `circuit.json`, the selector error, pin-hint grammar, `tsci convert`, `jlcpcb:C…` footprints | reading `pad_aliases` (spark's seam) |
| @tscircuit/footprinter 0.0.426 · circuit-json 0.0.489 | bin's `node_modules` | ISC (package.json) | footprinter strings; the netlist format every check reads | — |
| @wokwi/diagram-lint 0.1.1 | spark's converter | MIT (LICENSE) / ISC (package.json) | the 137-part registry with every stand-in's pin names; `invalid-pin` lint | the wake-from-GPIO limit; nothing about a board file |
| wokwi-cli | not installed | — (not read) | compiles chips locally; runs scenarios (paid minutes) | wake an ESP32 from a GPIO (recorded on the C6; B27 for the S3) |
| esptool 3.3 | yes (pyenv) | GPLv2+ (`pip show`) | `image_info` reads the chip id; `write_flash` | the final C6 target (needs ≥ 4.x, H) |
| mpremote 1.29.0 | yes | MIT (`pip show`) | `devs`, `cp`, `run`, `mip`, `soft-reset`, `bootloader` | flashing the interpreter (esptool's) |
| micropython 1.29.0 (unix) · mpy-cross | yes (brew, pyenv) | MIT (H) | real-runtime tier; compile check | a `machine` with `Pin`/`ADC`/`I2C` (E: `dir(machine)`) |
| jsonschema 4.2.1 | yes (pyenv) | MIT (`pip show`) | path-and-message validation; the file VS Code also reads | a spark dependency today |
| VS Code | yes (the bin's `.vscode/`) | proprietary (MIT source, H) | `$schema`/`json.schemas` validation, completion, hover (E, docs) | a store editor |
| sqlite3 (stdlib) 3.43.2 | yes | public domain (H) | transactions, a lock beside the file | a synced or shared file (its own guidance, H) |
| filelock 3.6.0 | yes | Unlicense (`pip show`) | a lock on a path | the lock's *place*, which is the fault |
| cog | no | MIT (H) | in-place regeneration, `--check`, `--diff` | the pairing of 8 of 42 blocks with no `sh` block (docs verify M2) |
| KiCad / kicad-cli | not installed | GPL-3.0+; libraries CC-BY-SA 4.0 with exception (H) | ERC/DRC as an optional gate (`skills/spark-review/SKILL.md:77`); the library-table and PCM designs; `.kicad_mod` footprints | nothing on the user's path (D the PO, P136 D10) |
| InvenTree | no | MIT (search) | stock, locations, BOMs, allocate/release | a record contract, provenance, a local CLI |
| Arduino `boards.txt` · PlatformIO `boards/*.json` · MicroPython `board.json` | fetched read-only once (boards.txt) | LGPL-2.1 core data (H) · Apache-2.0 (H) · MIT (H) | the SKU → variant → port bridge for a board skeleton | header geometry; power facts |
| Dolt · Syncthing · rclone | not installed | Apache-2.0 · MPL-2.0 · MIT (all H) | versioned SQL; folder sync; one-way sync | each a new tool against "few, local" |

## 2. The proposed changes, judged from this lens

For each change in the six diagnoses, by its title: **keep** (an existing mechanism is used, or none is needed), **change**
(how, naming the existing thing), **drop** (why), and what is **missing**. Verdicts rest on the findings above and the
verifications' corrections; sizes are the diagnoses' (H).

### store-levels-and-holds (C1–C13)

- C1 *A `SPARK_HOME` that names nothing is refused, and every answer names its store* — **keep**, with the verify's M1
  (set-but-empty) and its ordering against the git refusal; the one envelope exists (`outcomes.envelope`, `:65-74`) and
  gains one key; nothing outside is needed.
- C2 *The real store is written only on purpose (P164)* — **keep as a decision for the PO**: the flag form closes the
  copy-under-home case, the temp-root form does not (the verify); the existing precedent is the suite guard at import
  (`store.py:40-43`).
- C3 *One lock, beside the data, held by every writer* — **keep**; already carded as C-9 and C-11 on #94 (EXISTING-FIRST-11);
  `filelock` changes nothing (EXISTING-FIRST-29); the verify's cost (33 direct test writes) stands.
- C4 *An operation's writes land all or none* — **change**: take the verify's simpler form (record what landed; move
  `add_project` after `drawer.apply`; check `shelvable` first) and keep the append-only history as it is; SQLite's
  transactions would give the full form for the tables and point the wrong way (EXISTING-FIRST-26).
- C5 *A project is its folder, not its spelling* — **keep** the `samefile` half (carded C-8); the "never reuse a name" half
  only with the project id, which a git-synced store needs anyway (EXISTING-FIRST-25).
- C6 *Holds are seen in the listing and released by an operation* — **keep after the M2 decision** (derive on read, or a
  stored decision with `--release`/`--forget-project`); InvenTree's allocate/release is the benchmark for the names
  (EXISTING-FIRST-28); K56's `fix` must reach the plain text with it, or the person still sees no command.
- C7 *Reads refuse what writes refuse; labels in one form* — **keep**; `PLAIN.fullmatch(stem)` already covers every sync
  client (EXISTING-FIRST-30); the NFC/NFKD half touches 0 entries today (the verify's count) — rank it by mechanism.
- C8 *One reader for a store file, and no store problem is ever a traceback* — **keep**; it is the 2026-09-30 target 3,
  never built (EXISTING-FIRST-9); widen to the 37 raw sites in a second step; catch `UnicodeDecodeError` and `StoreProblem`
  by name, not every `ValueError` (the verify).
- C9 *`--fetch` names every URL it could not keep* — **keep**; carded C-21 (P90 #21).
- C10 *One layer, one count* — **keep**.
- C11 *A record has one home that is the store* — **change**: split it; the digest reader (EXISTING-FIRST-4) and the cache
  under the store (board C7) first; "shelve every project record" waits for the definition of proven (the `built` line —
  the verify: four placeholder records would land on the shelf); the agents' loss of `Write` waits for a check that
  `--fact-set` covers every field they fill.
- C12 *The spec and the code say the same about privacy* — **keep the verify's version** (sources private; the home's 0700 is
  the wall); the catalog's mode becomes a design question once a store is shared (EXISTING-FIRST-25, -27).
- C13 *The `built` line vouches for what the chain reads* — **drop the digest half** until a reader exists
  (EXISTING-FIRST-4); keep the sentence half (`note_built` says why it did not record).
- *An existing mechanism instead of hand-rolled files?* (the diagnosis's own paragraph) — git and content-addressed files
  fit the PO's direction (EXISTING-FIRST-25, -27); SQLite does not (EXISTING-FIRST-26); a lock library changes nothing
  (EXISTING-FIRST-29). The four invariants the diagnosis names (identity by thing, one lock beside the data, a unit of work,
  one reader) are right and are what git needs underneath it.

### board-records (C1–C12)

- C1 *A `header_order` label tscircuit would read as a pin number is refused* — **keep**; tscircuit's own grammar
  (EXISTING-FIRST-22); add the verify's M6 (the key side).
- C2 *`pad_aliases` reaches the footprint* — **keep**, with the verify's correction of the alias rule (both keys map to one
  GPIO) and **after** its M1: print tscircuit's own `Could not find port for selector` sentence, a reorder in
  `check_spine`, before rebuilding it from `board.tsx`.
- C3 *The `physical` schema is written where it is enforced; a key nobody reads is refused* — **change**: the existing form
  that also serves the editor and the TypeScript converter is one JSON Schema file (EXISTING-FIRST-23, -24); `PHYSICAL_KEYS`
  plus a test is the smaller step; either way remove the five unread keys from the S3 file (the verify's M3) and decide
  mounting holes as a decision, not a side effect.
- C4 *`emit_footprint.py --json` prints JSON on every path* — **keep**, the could-not-run variant; the test belongs in the
  existing `tests/test_json_contracts.py` (the verify's M9).
- C5 *The footprint's header says what the drawing states* — **keep**.
- C6 *One comment-key rule for every walker* — **keep**.
- C7 *The vendor-header cache lives in the store* — **keep**; use `store.place`/`write_file` (they exist) and state the
  read-only fallback order the bin's `--offline` depends on (the verify).
- C8 *A board record from a drawer entry* — **keep** as the PO's decided first fix (D8, 2026-10-09); it is composition
  (EXISTING-FIRST-8); the per-chip table is a third statement of chip facts — cite `soc_caps.h` per row and test it against
  both shipped boards; PlatformIO's and MicroPython's board files are H alternatives to `boards.txt`.
- C9 *A board says every stop it stops at; `--for-fab` requires geometry* — **keep**, both sentence spellings (the
  verify's M5); the XIAO's geometry comes from `tsci convert` of Seeed's footprint (EXISTING-FIRST-16) — make
  `footprint_source` the proposal, not the footnote.
- C10 *A board's `function` is a documented, validated key* — **keep with the verify's M4**: the drawer slot exists
  (EXISTING-FIRST-2); the record carries the sourced SKU fact, the entry the owned piece's.
- C11 *`pins` are checked against the stand-in's pin list* — **change**: it is the documentation, validation and derivation
  of the existing `wokwi_power_pins` override (EXISTING-FIRST-1); read the registry from a copy under `data/` with its
  version and licence notice (EXISTING-FIRST-21); the rule that covers both naming schemes: every `pins` key, mapped as
  `mapping.ts:96,108` maps it, is a pin of the stand-in (the verify's M7).
- C12 *Remove `footprint_module`* — **keep** (a removal), together with C9.
- *On the PO's question* (the diagnosis's paragraph) — agree on every point; the one option it leaves as "the PO's call",
  a schema language, this lens moves to a proposal (EXISTING-FIRST-23).

### needs-matching-vocabulary (C1–C9)

- C1 *One matcher: `--need` reads `function.what` and the drawer, matches by words hit* — **change**: tokens, not
  substrings (`needs._words` exists; the verify's M5); the simpler step first — keep the AND and say which words missed and
  that the drawer and `function` were not searched — then rank by hits; the recorded runs and five agent pages change
  with it (the verify).
- C2 *The pick says what the match knew; the needs listing shows the pick* — **keep** the note (with the verb, M1) and the
  listing; **drop** the mark/pick pair rule (it refuses plant-alarm's file and idea.md's M-before-C — the verify).
- C3 *A need can be dropped, and a pick cleared* — **keep**; the shared `_reserve` is a removal of a copy; a tombstone
  travels better under sync than a vanished object (the verify) — consistent with EXISTING-FIRST-25.
- C4 *Every answer that runs over the drawer says how many entries it could not look at* — **keep**, with the drawer.md
  step the verify's M8 names; the data pass is the PO's (P157 #93).
- C5 *The research skeleton carries every fact the chain reads; research ends with `--audit`* — **keep**; `--audit` already
  says it (EXISTING-FIRST-5); correct the proof line to `--audit`.
- C6 *The cut lists its words and ids* — **keep**; cap the ids per word (the verify).
- C7 *A need says how many the design uses* — **a decision first**; the verify's M7 shows the model already expresses a
  quantity as needs (`valve-1 … valve-4` → `Valve1 … Valve4`); one idea.md sentence before any schema change.
- C8 *`--requirements` refuses when a differently named requirements file sits in the project* — **keep after the
  irrigation rename** (the verify's M6, one `git mv`); reuse `design_in`'s existing glob or decide one name
  (EXISTING-FIRST-10).
- C9 *The store's words are shown where a need is written and matched* — **keep**; add the verify's M2 case ("one word
  more").

### chain-and-checks (C1–C9)

- C1 *The chain re-seeds the derived half of `rules.json`* — **change** to the verify's MC-6: seed at `parts.py
  --requirements`, already a writer with the records in hand (`needs._power_gaps` computes the rails today); no check
  writes another check's input; MC-1 (an empty rule list is could-not-run forever) is a decision C1b must carry.
- C2 *A signal the file declares is reported, not refused* — **keep**; a shared `NOTE_PREFIX` constant between
  `emit_board` and `check_spine` (the verify) instead of a string-prefix contract.
- C3 *A record can say that an input defines its own level* — **change**: name the key by why floating is harmless (a
  current load, a module-side pull, a gated data input — the verify's MC-5 shows spark's own amplifier record), with
  `verified`/`source` as `body_mm` has.
- C4 *One table says what each owed fact does to the chain* — **keep after MC-3's decision** (`pin_order_proof` owed or
  broken); the table replaces `_about`'s regex — a removal.
- C5 *The requirements writer reads the file through `design.read` and names instances with the one function* — **keep**;
  three removals; fold `_name_after` (the verify).
- C6 *The board changes in one place* — **keep** the write-`active.json` variant now; `boards/README.md:21` ("THE one place
  it is chosen") and the bin's CLAUDE.md say the same sentence and need the qualifier.
- C7 *Five small contract fixes* — **keep**; K52 also exits the wrong kind of wrong (MC-8); K63 the refuse variant.
- C8 *`--keep` builds the kept `board.tsx`* — **keep** (D the PO 2026-10-05, #44) **but build in place**: the documented
  remedy `npx --no tsci build board.tsx` (`commands/build.md:74`) already resolves a hand file's local imports (MC-4);
  no `built` event when the file differs.
- C9 *★C7 — keep; one wording option* — **keep**.

### firmware-and-bench (C1–C6)

- C1 *The stand-in's pins are a board fact the chain reads first* — **change** to the verify's M1: the converter has the
  oracle in hand when it names a pin — fix the name choice in `mapping.ts`; document and validate the existing override
  (EXISTING-FIRST-1); a "spend last" role only for a GPIO with no name on the stand-in at all; the classifier's second
  pinned string (C1(d)) is the symptom of a converter with no structured output — `--json` on the converter is the
  mechanism (the verify's M8); the bundle rebuild and the sha pin are the unsized cost.
- C2 *`flash_image.py` refuses an interpreter built for another chip* — **change**: shell out to `esptool image_info`, or
  copy its table with a citation (EXISTING-FIRST-18); call it from `check_spine`'s simulation stage, where the resolved
  board and the image already meet (the verify); pin a minimum esptool version in `data/tools.json`.
- C3 *The step from the image to the board* — **keep**; both tools are installed (EXISTING-FIRST-18, -19), the bin's
  `deploy.sh` is the worked example (EXISTING-FIRST-17); the page variant first, the script when the PO wants the chip check
  and the could-not-run; the C6 needs a newer esptool than the PO's machine has.
- C4 *A sixth check: the firmware against the pin map it imports* — **change**: say what it is — a use-against-map check,
  not the bin's triangle of literals (the verify's M3) — and why it will be used where the 2026-09-29 cut was not (the
  `pins.py` convention, M2); fix K53 first (EXISTING-FIRST-7); "has" = `pins ∪ pin_roles[*].gpio` (the XIAO's user LED);
  the cheapest first consumer of the deep-sleep facts is the `pins.py` header (the verify's M7), no fake needed.
- C5 *A scenario is measured against the pin map* — **keep** as a note; the bin's `scenario-pins.ts` is the precedent
  (EXISTING-FIRST-14); an `expect-pin` must also name a pin the stand-in knows.
- C6 *The documents follow the code* — **change**: amend the two true-in-part sentences instead of deleting them (the
  verify's M9); the retired-phrase gate is a port of the bin's `check-current-docs.py` (EXISTING-FIRST-15), proposed as a
  small change of its own.

### docs-and-recorded-outputs (Changes 1–7)

- Change 1 *The gate counts every recorded output behind the shipped version* — **change**: a report line, never a failure
  (a version is provenance, a diff is currency — the verify); or let the recorder's `--check` print the count.
- Change 2 *The README's typed block ends where a shell can finish it* — **keep**; keep the file inside the project; give
  the block a recorded output (the verify's M8).
- Change 3 *Recorded outputs are re-recorded by one tool at each release* — **change**: promote or delete the recorder on
  disk first (EXISTING-FIRST-6); classify the 42 blocks (re-recordable or recorded-only — the verify's M2, M3); hook `--check`
  into `check_commit.py` on a version change, because no release gate exists (M4); cog is the existing tool if its
  markers are acceptable (EXISTING-FIRST-31).
- Change 4 *The own-board route is recorded on 0.8.1* — **keep**; cut the half already on the page (the verify);
  `--fetch` on a board id takes the truthful refusal through the argument path.
- Change 5 *The gate reads the pages agents follow* — **keep**; name pages by path (M7); share `routes()` minus the sibling
  Makefiles.
- Change 6 *Density and long lines: one measured rule, or none* — **change**: a rule that fails, or nothing; README's long
  lines are table rows (the verify's count).
- Change 7 *One sentence says what spark has built* — **keep**, with the per-store count.

### Missing — changes nobody proposed, from this lens

- **MISSING-1 · A schema per file spark writes, and `$schema` in the file.** JSON Schema for the board record, the rules
  file, the needs file, the part record, the drawer entry and the tools file; each `description` is the documentation
  board C3 wants, written once; VS Code validates, completes and shows it on hover; `jsonschema` (installed, MIT) or a
  generator from `PHYSICAL_KEYS`/`CHECKS` validates in Python; the TypeScript converter's `board.ts` types derive from the
  same file. Serves K24, K25, K26, K35, K46 and the PO's "rules and editor". Testable: the shipped files validate; a
  key not in the schema is refused with a path. Diagnosable: `physical/header/drill_mm -> -3 is less than or equal to the
  minimum of 0` — where and why, to a person in the editor and to an agent on stderr. The cost is a dependency or a
  generator (question 1). (EXISTING-FIRST-23, -24)
- **MISSING-2 · A no-code sync experiment with git on a copy of the store**, the store-discovery skeptic's P84 experiment
  never run: `git init` in a copy, two clones, a pick in each, a `merge=union` attribute on `history.jsonl`, then merge;
  write down what conflicts and what the output said. One hour; it tells P178's council what a synced store really does
  before any design. Needs `inside_git` scoped to a project's work tree, which is MISSING-3. (EXISTING-FIRST-25)
- **MISSING-3 · Scope `inside_git` to a project's work tree.** The rule at `store.py:129-135`/`:209-218` refuses a private
  place inside *any* repository; the reason it exists (a project's `git add .`) holds only for a project's tree. One
  function, the existing tests at `tests/test_store.py:147-213` to flip on purpose. A prerequisite for a store that is a
  repository. (EXISTING-FIRST-25)
- **MISSING-4 · Fix K53 before any change's proof is "a mutation row".** `tools/mutate.py` scores an import failure as a
  catch; store C3's twelve rows and firmware C4's table would be over-counted. Small, and it protects the acceptance bar
  every other change leans on. (EXISTING-FIRST-7)
- **MISSING-5 · `esptool` and `mpremote` as `data/tools.json` entries now, with a minimum esptool version**, before any
  `flash.py`: `/spark:setup` then says what is missing for the bench, and C3's page can name them. (EXISTING-FIRST-18, -19)
- **MISSING-6 · One reader for the digests spark already writes** — an `--audit` line comparing each shelf copy's
  `based_on.digest` and each `built` line's digests with today's records — before any widening of the digest (store C13)
  or any "proven by use" rule (store C11). (EXISTING-FIRST-4)
- **MISSING-7 · A copy of the Wokwi registry under `data/wokwi-parts.json` with its version and licence notice**, the one
  data file board C11 and firmware C1 both need, so a Python validator never imports from `node_modules`.
  (EXISTING-FIRST-21)
- **MISSING-8 · Port the bin's retired-phrase gate to spark** as `check_docs.py`'s next function, with spark's own retired
  sentences ("costs only the silkscreen labels", "THE one place it is chosen" once chain C6 lands, "Not yet. No command
  does this yet" once firmware C3 lands). (EXISTING-FIRST-15)

### The ten that matter most, in this lens's order

1. **store C1 (+ M1)** — refuse a missing or empty `SPARK_HOME`; name the store in every answer. The cheapest closure of a
   silent harm (K1, K2's blindness): two lines and one envelope key, the envelope exists, nothing outside is needed.
2. **board C2 after the verify's M1** — print tscircuit's own `Could not find port` sentence (a reorder), then teach the
   footprint the alias. The library's own S3 cannot build a design that reaches MOSI or MISO today (E: the 21-LED run), and
   the first half is existing output.
3. **board C1 (+ M6)** — refuse bare-number labels and keys by tscircuit's grammar. A silent pad merge on the route the PO
   made the first fix (D8); S; the grammar exists.
4. **store C3 (+ C-11)** — the lock beside the data, every writer checks. Carded already (#114); the only guard against a
   part reserved twice; mechanism, not symptom.
5. **store C8 (= the 2026-09-30 target 3)** — one reader, no traceback, the right exit code. Planned and never built; 37
   raw sites; closes K11, K16 and the exit-1-for-could-not-read class.
6. **needs C5 (+ verify M3)** — the skeleton carries every chain fact; research ends with `--audit`. Every researched
   record arrives owing today; the sentences exist; the set test catches the next drift.
7. **board C7** — the vendor-header cache under the store through `store.place`. The one-home rule broken by a tool that
   says nothing; S; the store API exists.
8. **chain C5** — one reader (`design.read`), one `component_name`. Three removals close three cards (#118, #119, K61)
   with no new rule.
9. **firmware C3, the page and the tools entries first (MISSING-5)** — the step from the image to the board. The biggest
   journey blocker (★C6, K66); both tools are installed; the bin's `deploy.sh` is the worked example.
10. **store C6 after M2's decision (+ K56)** — holds listed and released. It blocks every second project on the one
    FireBeetle; the decision (derive on read, or stored with `--release`) must come first, and the plain refusal must
    carry the command.

Behind these, in this order: MISSING-4 (K53) before any mutation-row proof; MISSING-1 (the schema) as the first design
step of P178's editor; docs Change 5 (+ M7), a pure guard; firmware C1 reduced to the name choice in `mapping.ts`;
needs C1 in its simpler form.

## 3. What this lens could not check, and why

- **No spark command was run** — only the store copy and the prefix check. Every run cited is a diagnostician's or
  refuter's of 2026-10-10, re-read against the files, not re-run; where a number is theirs it is marked as such.
- **Licences read at source** are only those present on this machine: tscircuit's packages, `@wokwi/diagram-lint`,
  esptool, mpremote, jsonschema, filelock (E). KiCad's and its libraries', Seeed's OPL, SQLite's, git's, cog's, PlatformIO's,
  MicroPython's, Dolt's, Syncthing's, Automerge's and Yjs's are H from memory; the `wokwi-boards` repository's is — .
  None of this is legal advice; the one posture question (calling a GPL tool as a subprocess from MIT code) is question 4.
- **git's `merge=union` on `history.jsonl`** was not run (MISSING-2 is the test). **VS Code's hover on nested
  `description` fields** was not tried on spark's files; the documentation says it.
- **esptool's final ESP32-C6 chip id (13)** is from memory; the installed 3.3 has only the beta class (E).
- **KiCad's "project table wins"** came back unconfirmed by the search and stays H; the PCM chain is E.
- **InvenTree's allocation model** is known from the search summary only.
- **PlatformIO's and MicroPython's board files** as variant bridges: H; not fetched (one `boards.txt` fetch was the board
  diagnostician's, and this lens kept to its three searches).
- **Round 0's C6 files** are not in the repository; nothing here re-runs them.
- **The bin's `make check` targets** were read from its `Makefile`, not run.
- **Line numbers** were re-read in `store.py`, `boards.py`, `outcomes.py`, `drawer.py`, `tools.py`, `check_docs.py`,
  `check_vendor_pins.py:40-140`, `parts.py`'s constants, skeleton, `OPERATIONS` and `main`; other pointers are the
  diagnoses' and verifications', cited as theirs.

## 4. Questions for the decider

| question | what it decides |
| --- | --- |
| Is a Python dependency (`jsonschema`, MIT, already on your machine) acceptable for spark's schemas, or must the schema be generated from Python and shipped for editors only? | MISSING-1's shape; whether board C3 is `PHYSICAL_KEYS` plus a test or one schema file for Python, TypeScript and the editor |
| May the store be a git repository — the shared store a remote, the local store a clone — so that `inside_git` is scoped to a project's work tree? | the sync direction (EXISTING-FIRST-25); whether SQLite and CRDT libraries are off the table (EXISTING-FIRST-26); MISSING-2 and MISSING-3 |
| For the shared store's index: a KiCad-PCM-shaped static index (JSON plus sha256) served from a git repository, or git alone (clone the whole repository)? | P178's find-and-download shape; whether `tools.settle_download` and `store.keep` are reused as they are |
| May spark name `esptool` (GPLv2+) in `data/tools.json` and shell out to it, with a minimum version, or must it copy the chip-id table with a citation? | firmware C2 and C3's form, and the licence posture (not legal advice) |
| Should the bin's `fake_machine.py`, its four `lib/checks` and `check-current-docs.py` be ported into spark as the generic versions — the bin then using spark's — or stay the bin's? | firmware C4, C5 and C6 and MISSING-8; the P56 document's ceiling argument for a MicroPython test library inside the plugin |
| Holds: derived from the listed projects' `needs.json` on read (no `used_in`, no `--release`), or a stored decision with `--release` and `--forget-project`? | store C5 and C6, and what a synced store must merge |
| Are 126 marker lines in pages agents read raw acceptable (cog), or is the recorder on disk promoted instead? | docs Change 3 |
| Do the drawer's operations take InvenTree's words (allocate, release) or spark's (hold, release, forget)? | the names in store C6 — small, but the agent pages carry them |

## 5. Searches

| query, verbatim | decision served | used |
| --- | --- | --- |
| InvenTree open source inventory management license MIT Python API client parts stock BOM | whether a ready-made parts inventory under a free licence exists as an alternative to building the drawer's missing operations (K3) | used — EXISTING-FIRST-28 |
| VS Code JSON schema validation "$schema" property "json.schemas" setting fileMatch completion hover descriptions | whether the "editor" half of the PO's question has an existing answer without building an editor | used — EXISTING-FIRST-23, MISSING-1 |
| KiCad global and project specific library tables fp-lib-table sym-lib-table project wins; Plugin and Content Manager repository.json packages sha256 | whether an existing design for global/project layering and for a shared online index exists to copy (P178) | used — EXISTING-FIRST-27; the "project wins" half unconfirmed, H |

Local reads, no network: `pip show` for esptool, mpremote, jsonschema, filelock, cogapp, pydantic; `mpremote --help`;
`python3 -m esptool image_info --help`; `micropython -c "import machine; print(dir(machine))"`; the `package.json` and
`LICENSE` files under the bin's and the converter's `node_modules`; `gh issue view` of the 21 cards (read-only); the
bin's `Makefile`, `tools/` and firmware harness; the gitignored recorder folder. No Espressif-docs query.
