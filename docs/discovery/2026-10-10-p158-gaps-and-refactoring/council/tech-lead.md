# Tech lead — P158 part 1 council (architecture and technical direction)

Written 2026-10-10 against spark 0.8.1 (main `a8aa34d`, `git log -1`), from `../catalogue.md`, the six diagnoses and
their adversarial checks in `../diagnosis/`, and the primary artefacts they cite, re-read at the cited lines; the
direction cards #94 (P158), #89 (P154), #17 (P94), #123 (P178), #70 (P136), #101 (P164), #114 (P174), #96 (P160),
#93 (P157), #99 (P162), #5 (P76) (`gh issue view`, read-only); `docs/2026-10-04-store-design.md` and
`docs/2026-09-30-refactoring-architecture.md`; the P100 folder's `brief.md`, `items.md`, `council/tech-lead.md` and
the head of `council/refuter.md`. **I ran no spark command**: no store was copied, nothing was run against any store;
my own evidence is `grep`, `wc`, `sed` and `git log` over the tree, and `gh` reads. Where a claim rests on a run it is
a diagnosis's or a verifier's run, named as such. Tags: **E** a pointer, or a command and its output; **H** a claim
with its source; **D** a decision (who, when); **—** unknown. Line numbers are spark's at `a8aa34d`.

The PO's criteria (D PO 2026-10-10, verbatim): *"we want the system to be well designed so its well testable and
understandable where a mistake is happening and why"*. My questions: does each change fit P158's words ("changeable,
extendable and testable"; strategies and adapters; functionality-based replacement — no MCU, one, more than one),
P154 (engines switchable through settings), P94 (the store design) and P178 (one shared store online, a local store,
synced project records); what to remove or merge; where the architecture rather than a line is responsible; the
smallest structural set that makes a mistake land in one named place with one named reason; the module boundaries
and the test seams.

## 1. Findings

### Where the architecture is responsible

- **TECH-LEAD-1 · "Could not read" has seven readers, five exception classes and three ways of saying it.** · E ·
  `grep 'json.loads(.*read_text(' scripts/*.py` → 37 sites in 16 scripts (parts.py 11, check_all 3, check_spine 3,
  init_project 3, …; my run, 2026-10-10). The readers that wrap one: `boards._read_json` → `BoardError`
  (boards.py:170-176); `tools._read` → `ToolProblem` (tools.py:62-71); `store.projects`, `drawer.entries`,
  `needs.read` → `StoreProblem` (store.py:233-244, drawer.py:88-101, needs.py:40-63); `design.read` → `DesignError`
  (design.py:93-128); `parts._parse` → `None` (parts.py:1270-1274); `init_project.has_answers` → `True` on
  `OSError, ValueError` (init_project.py:236-245: "whatever is in it, it is not ours to replace"). No `read_json`
  exists in `scripts/` but `boards._read_json` and `parts._read_json_input` (grep). The 2026-09-30 architecture
  note's target item 3 — `outcomes.read_json(path, what)` "retiring the exit-1-for-an-unreadable-file class at eight
  sites" (`docs/2026-09-30-refactoring-architecture.md`, "The target") — did not land; its postscripts record P42,
  P35 and P29 and not it. The class is K11: a `UnicodeDecodeError` traceback, exit 1 (the store verify's RC-5 run).
  · supports only: that the diagnosability fault is one shape repeated, not thirteen bugs, and that the fix's shape
  is one reader and one exception the mains map to could-not-run. It does not say which sentence each reader prints.

- **TECH-LEAD-2 · The exit code is decided in one place and re-labelled in six.** · E · `outcomes.py:19` defines the
  three codes; `:9-13` blesses a local alias for the middle one as "ran, and the answer is no". The aliases:
  assign_pins.py:46 `EXIT_IMPOSSIBLE`, boards.py:116 `EXIT_INVALID`, check_vendor_pins.py:35 `EXIT_MISMATCH`,
  init_project.py:43 `EXIT_NOTHING_TO_DO`, parts.py:223 `EXIT_INVALID`, tools/mutate.py:56 `EXIT_ESCAPED` (grep).
  Two carry a meaning the table has not: `boards.main` returns `EXIT_INVALID` (1) for every `BoardError`, "no board
  selection" included (boards.py:537-539; K52; the chain verify's MC-8), and `init_project.main` returns
  `EXIT_NOTHING_TO_DO` (1) for "nothing to do — everything already exists" (its last branch) — a second `/spark:init`
  exits as "problems". `check_vendor_pins` prints a fourth status word, `mismatch`, which `tests/test_json_contracts.py:133-139`
  pins as such. · supports only: the alias is where "an exit code means two things" enters; a `main` that computes
  its own code bypasses `status_of`. Whether "nothing to do" is `ok` is the PO's (Q4).

- **TECH-LEAD-3 · Six seams where a sentence is the contract between two modules.** · E · (a) severity by channel:
  `check_spine.py:374-375` turns any stderr line of the generator subprocess into a PROBLEMS stage; the subprocess is
  at `:358-361`, while `emit_board` is imported as a module at `:62` and called in-process at `:431-432`; (b)
  `CONVERTER_HAS_NO_PART = "no Wokwi part is mapped"`, a substring (`:216-221`); the converter has no structured output
  (the firmware verify's M8, `cli.ts:47-52` read there); (c) the `note:` prefix on the five generator notes
  (emit_board.py:1129-1145) and `LIBRARY_NOTE` (design.py:157), which chain C2 would make a second contract; (d) the
  stop sentence spelled twice (parts.py:1920 `STOPS_AT_FOOTPRINT`; needs.py:511-512 — the board verify's M5); (e)
  owed versus broken decided by `_about`, a regex over problem sentences (parts.py:113-117; the chain verify's MC-3:
  `--audit` says "owes pin_order_proof" of a record `parts.load` refuses at the parts stage); (f) a pad's identity as
  hint-string equality across two writers that never consult the alias table (board RC-1, RC-2). · supports only:
  these are the places where a change of wording silently changes behaviour; (a), (b) and (e) have a structural fix
  (a return value, a `--json`, a table keyed by fact), (c) and (d) a shared constant, (f) one writer reading the table.

- **TECH-LEAD-4 · The one home is read on every call in `store`, and the plugin folder is spelled seven times.** · E ·
  `store.home()` reads the environment per call (store.py:46-52); `tools.PERSONAL = store.place("tools")` and
  `DOWNLOADS` are module constants read at import ("Read once, when the process starts", tools.py:44-47); the plugin
  folder: boards.py:38 (`LIBRARY`), :153 (`PLUGIN_ROOT`), check_vendor_pins.py:99 (`PLUGIN_ROOT`, written into by a
  live run — K14), fab.py:27, parts.py:45 (`LIBRARY`), store.py:33 (`PLUGIN`), tools.py:43 (`PLUGIN`) (grep);
  `sys.path.insert(0, SCRIPTS)` in 9 scripts (grep). The suite guard sets `SPARK_HOME` at `store` import
  (store.py:40-43), before `tools` imports, so the import-time read has no observed fault. · supports only: "implicit
  paths" is a pattern of two disciplines for one fact, with K14 its one observed fault; one `plugin_root()` beside
  `home()` and the rule "no module reads a home at import" are small and testable (import every module under one
  `SPARK_HOME`, change it, ask each path function again).

- **TECH-LEAD-5 · `parts.py` is the record contract, the document store, the shelf and the CLI in one module, and
  the store-side modules import it back.** · E · 2,214 lines (wc), 115 `def` (grep): the contract :72-794
  (`function_of` … `validate`), the shelf and the digest :895-965, the documents :985-1283, the matcher's first copy
  :1326-1352, `OPERATIONS` :1472-1529, 28 `_op_*` :1571-2159, `main` :2188 with `globals()["_op_" + …]` at :2201.
  `drawer.py:16-18` and `needs.py:15-21` import `parts` at the top (for `_problem`, `_parse`, `owes`,
  `broken_problems`, `VERBS`, `shelve`, `LIBRARY`); `parts.py` imports `drawer` 8 times, `needs` 6, `boards` 3,
  `cost` 2, `tools`, `emit_footprint`, `compare_design` once each inside functions (grep: 22 function-local sibling
  imports in parts.py, 3 in boards.py — `emit_footprint`, `parts`, `parts`; check_all's 12 are by design, its A7
  comment). `needs.py` imports the generators `emit_board` and `emit_footprint` (:18-19) and holds a copy of
  `component_name` (:430-432; K60). · supports only: a traceback out of `--pick` crosses parts → needs → drawer →
  parts → boards → emit_footprint, the opposite of "understandable where a mistake is happening"; the boundary that
  is missing is contract / documents / CLI (§2). It does not say the split is cheap: 266 mutation rows in 48 tables
  anchor into `scripts/parts.py` (grep over `tests/mutations/*.json`; 1,268 rows in all), and `tools/check_commit.py:143-147`
  refuses a push whose anchors no longer match — the net and the cost in one number.

- **TECH-LEAD-6 · Boards and parts are two record kinds with one walk and two of everything else.** · E · both
  resolve through `store.records` (boards.py:216-218; parts.py:252-262); `store.layers` adds the shelf and the catalog
  only when `kind == "parts"` (store.py:77-80); two loaders (`boards.load` → `BoardError`, boards.py:250-257;
  `parts.load` → `PartError`, :264-271), two contracts, the "stops" rule read from the part side (`parts.STOPS_AT_FOOTPRINT`;
  `needs.stops_at_footprint` importing `emit_footprint`, needs.py:149-152), `drawer.linkable` re-walking every listed
  project's `parts/` and `boards/` (drawer.py:111-117). The 2026-09-30 note counted "57 duplicated lines" in the two
  resolutions and declined the merge for blast radius ("Do not refactor"). · supports only: a board is a part-like
  record on a second code path; P158 part 2 meets this seam first (TECH-LEAD-7), which is the reason to weigh the merge
  again — not the line count.

### Direction fit

- **TECH-LEAD-7 · "One board" is a fact of the code at nine named places, and the board contract is ESP-shaped.** ·
  E · `needs._board_problems` ("it is one", :498-518); `needs.requirements` (`board=board_picks[0]`, :617);
  `design.load` (`wanted.get("board")`, :342); `check_spine.run` (:334); `boards.active_id` (one id; its docstring: two
  boards "means two projects", :183-211); `init_project` writing `boards/active.json` (:473-474); `emit_board` naming
  the module `Mcu` (7 occurrences; boards.py 2, netlist.py 1, the converter's `lib/mapping.ts` 2 — grep);
  `KIND_FUNCTION["board"]` (parts.py:69); one `SPARK_BOARD_JSON` for the converter (check_spine.py, the simulation
  stage). The contract: `REQUIRED_KEYS` = `chip, wokwi_part_type, pins, wake_capable_gpio, adc_gpio, physical`
  (boards.py:62-63); `PIN_ROLES` `console_uart, strapping, adc2_unusable_with_wifi, not_wake_capable` (:95-107);
  `capability_of`'s PWM default, "a statement about the chips this tool targets" (assign_pins.py:118-131);
  `micropython_port` and `deep_sleep` in the records. · supports only: part 2's "no MCU / an Arduino / two MCUs" is not
  a strategy a setting swaps today — it is a change at every one of these places plus a contract that stops being
  ESP-specific; so part 1 must not add a tenth place (chain C6's recommended variant would: a second file stating one
  board). Part 2's shape, said once here and not designed: a host is a record that plays the `compute` role, zero or
  more per design, named per instance like any other part.

- **TECH-LEAD-8 · P154's switch exists for external tools and is half an adapter.** · E · `data/tools.json`: `roles`
  (11: pdf-text, simulator, board-engine, diagram-converter, js-runtime, littlefs, firmware-image, parts-search,
  chip-docs, bench, ts-runtime), `contracts` (6), 13 tool entries (read 2026-10-10); `tools.find(role)` checks `meets`
  (tools.py:239-262); §6.3's reserved `strategies` key and its registry exist in no file (`grep -rn strategies scripts
  data tests` → nothing). The board-engine's *how* lives in `check_spine.run`: `[toolchain, "build", "board.tsx"]`,
  `workdir/dist/board/circuit.json`, `tsci_version`, `toolchain_can_build` (check_spine.py:399-417; `design.CIRCUIT_PATHS`,
  design.py:53); the simulator's in the converter call there; the firmware-image contract is chip-blind
  (`"micropython-esp32-bin"`; the firmware verify's M4). · supports only: pointing `roles.board-engine` at another
  engine through settings cannot work without code; P154's "some adapter or plugin" is an adapter module per engine
  behind the role (how to call it, where its output lands, how its version is read), not another settings key. The
  seven §6.2 seams are functions today, none behind a registry (store.py, drawer.py, needs.py, cost.py read).

- **TECH-LEAD-9 · What P178 needs from part 1 is identity, one door and a digest something reads — and no new
  name- or path-keyed structure.** · E · `store.layers()` is a literal row list with no "shared" row and no writable
  column (store.py:71-81; §6.1 asks for the column, design.md:273-275; the store verify's RC-4 (2)); `inside_git`
  refuses only PRIVATE places (store.py:94-96, :209-214), so a shared clone may carry catalog- and shelf-like records
  and never the drawer, history or projects (§5.8) — consistent; records are keyed by file stem (= id), projects by
  folder name (store.py:247-269; K4), holds by project name inside the drawer (needs.py:328-331); `based_on.digest`
  is written (parts.py:932-941) and read by name by nothing (the store verify's grep, RC-4 (1), M3); the `built`
  digest likewise (only `--tally` reads `built`, by event and project name). · supports only: the ordering — C5's
  project id, C8/C3's one reader and one door, and a reader of digests come before any sync design; and a hold is
  per-machine state that a shared store must not carry (M2's (i) derives it, (ii) keeps it private).

- **TECH-LEAD-10 · P136's "extendable checks" and P154's engines share one seam, and `check_all` already has its
  shape; the chain does not.** · E · `check_all.CHECKS` is a list of `Check` objects with `needs` and a `call`
  (check_all.py:59-98, :281-292); `CONVENTIONS` names the inputs (:301-305); a check whose input is missing is
  `skipped`, never passed (:85-88). `check_spine.run` is one function of about 190 lines (:330-520) with the engine
  calls inline. · supports only: a new check (KiCad DRC, ngspice) is a `Check` with a `needs` and a tool role — that
  extension point exists; a new engine inside the chain has none (M-F).

### Spec against code, and the tests

- **TECH-LEAD-11 · Four things the designs specified that the code never got.** · E · §6.1's writable column on the
  layer table (above); §6.3's `strategies` registry (above); the 2026-09-30 note's `read_json` (TECH-LEAD-1); §6.4.1's
  "one envelope from every `--json` run": `outcomes.envelope` is printed by `parts.py` alone (parts.py:2171-2185);
  `check_all` prints `{tool, status, resolved, results}` (its `main`), `check_spine` `{check, status, stages[, unserved]}`
  (`report`, :668-679 per the chain diagnosis), `emit_footprint` `{check, status, message}`
  (tests/test_json_contracts.py:142-146), `check_vendor_pins` a bare list (:133-139), `assign_pins` no `status`
  (:101-104); `--json` is offered by 9 scripts and not by `boards.py`, `tools.py`, `emit_board.py`,
  `init_project.py`, `flash_image.py`, `cost.py` (grep `"--json"`). · supports only: K55 and K57 are instances of one
  unbuilt rule; for an AI agent "where and why" has one shape in one script. It does not say the other shapes are
  wrong for a person at the terminal.

- **TECH-LEAD-12 · The suite is strong at the symbol level and has no outcome invariant across scripts.** · E ·
  1,712 `def test_` (grep; the store diagnosis's suite run: 1,699 ran, OK), 132 `.main([` entries in tests (grep, a
  proxy), 18,488 test lines against 11,487 script lines (wc); `tests/test_json_contracts.py` characterises the five
  shapes rather than one (:13-15); `tests/test_boards.py:316-372` holds the bin's Makefile contract (the 2026-09-30
  note's P41 landed). No test feeds every `main` a non-UTF-8 file, a list where an object belongs and a missing path
  and asserts exit 2 with one sentence and no traceback — the class K11, K28 and K52 live in. The anchors (1,268 rows)
  run at every push (`tools/check_commit.py:143-147`). · supports only: the missing seam is one suite-level test over
  outcomes, not more per-case tests; a `parts.py` split has a net (a moved `find` is refused) whose cost is the 266
  rows that must move with it.

- **TECH-LEAD-13 · The store's writers are one door, opt-in.** · E · the door: `write_json`, `write_file`,
  `copy_folder`, `append_event`, `keep` (store.py:138-230, :314-327, :382-405). Beside it: `check_vendor_pins`'
  `cache.write_text` into the plugin (:137-138); `promote`'s `shutil` (parts.py:1285-1296); the `datasheet-reader`
  agent with `Write, Edit` (agents/datasheet-reader.md:5, read 2026-10-10); `_write_record` choosing the door by
  `path.parent == store.place(name)` (parts.py:1846-1851, per the store verify's M4). · supports only: store C3's lock
  check inside the door cannot see a writer that never enters it; the guard is grep-shaped — no script writes under
  `store.home()` except through the five — and belongs beside `tests/test_orphans.py`.

### On the relayed question — formats, sync libraries, an editor

- **TECH-LEAD-14 · No library supplies the four invariants the store faults need; git is the transport the design
  already names; a schema is a format the existing tables can emit.** · H (sources: the store diagnosis §3's four
  options and its estimate "20–60 lines each in `store.py`"; the store verify's note on SQLite and synced folders,
  unfetched; design.md §3 "later a shared clone (P84)"; `--describe` generated from `OPERATIONS`, parts.py:2159-2168,
  as the precedent) · supports only: (a) identity by id, one lock beside the data, a unit of work and one reader are
  `store.py` changes, not dependencies; (b) for P178 the shared layer is a git clone of records — git is already
  required (`gh` in check_vendor_pins; the README's install) and names conflicts — and what it needs from part 1 is
  ids and digests; (c) for P160's editor, a JSON Schema generated from `OPERATIONS`, `PIN_ROLES`, the board C3's
  `PHYSICAL_KEYS`, `drawer.FIELDS`/`CHECKS` and `needs.CHECKS`, never hand-kept, with spark's own validators staying
  the enforcer and their sentences the message, gives any editor validation without a runtime dependency; (d) SQLite
  fits the small tables (projects, holds, history) and a synced folder worst, so not the drawer; (e) a lock-file
  library changes nothing — the fault is the lock's place. No search was run for this.

## 2. The proposed changes, judged

Direction in one paragraph. P158 part 1's words — changeable, extendable, testable — are served by the changes that
give a class of mistake one home (S1–S7 below) and strained by any that add a second statement of one thing (chain
C6's recommended variant, chain C1a's second seeder, needs C2's pair rule). P154 is served by nothing in part 1 and
blocked by nothing; its seam is M-F. P94's own unbuilt lines (§6.1's writable column, §6.3's registry, §6.4.1's one
envelope) are three of the missing changes. P178 is served by store C5's id, C7, C8/M-C, C3 and M-J, and strained by
store C12 making the catalog private and by any design that lets a hold travel.

Verdicts: **keep** · **change** (how) · **drop** (why) · **PO** (a decision before a verdict). Titles shortened; ids
are the diagnoses'. "The verify" is the area's adversarial check.

### store-levels-and-holds (C1–C13)

- C1 a missing `SPARK_HOME` refused; every answer names its store — **keep**; add M1 (set but empty); order the check
  with the git refusal (the verify's (b)); the `store` field belongs in the one envelope (M-B) so every script carries
  it, not `parts.py` alone. P164's precondition.
- C2 the real store written only on purpose — **PO**: the temp-root rule covers the incident's named shape and not a
  copy under the home folder (the verify); the flag (`SPARK_STORE=real` / `--store`) covers both at one line in the
  PO's shell. C1's field makes either visible.
- C3 one lock beside the data; a writer with no lock refuses — **keep**; M, not S (33 direct writes in the suite, the
  verify's (a)); `locked()` needs the home to exist, so after C1; add TECH-LEAD-13's grep test or the check sees two of
  three doors.
- C4 an operation's writes land all or none — **change** to the verify's variant: keep the ordered sequence, record
  what landed and say it on a stop, move `add_project` after `drawer.apply`, compute `shelvable` before `apply`;
  **drop** the staged rename-set (it rewrites the append-only history and is not one unit across file systems).
- C5 a project is its folder; an id travels with it — **keep the id** (the handle P178's sync needs, TECH-LEAD-9);
  the "never reuse a name" half only with the id (a moved project otherwise loses its holds, the verify's (b));
  `samefile` with the string fallback first.
- C6 holds listed and released — **PO first (M2)**: (i) derive holds on read from the listed projects' `needs.json`
  — no `used_in`, no `--release`, no state to drift; or (ii) keep `used_in`, add the operations, `--audit` compares.
  (i) fits the criteria and P178 (a shared store carries no holds); (ii) fits "the bin keeps this one" without touching
  the bin. The `--drawer` key column and K56 (print the `fix`) with either.
- C7 reads refuse what writes refuse; NFC — **keep**; no occurrence in the store today (the verify's (4)); cheap.
- C8 one reader; no store problem is a traceback — **keep and widen** (M-C): one `read_json(path, what)` for the 37
  sites and one exception the mains map; catch `UnicodeDecodeError` and the new class by name, never every
  `ValueError` (the verify's (a)); include `store.py:145`'s write-side read.
- C9 `--fetch` names what it could not keep — **keep**.
- C10 one layer, one count — **keep**.
- C11 a record has one home — **change**, split: (a) `promote` project→library: **drop the branch** (the library
  changes by pull request; `parts.py:1865` says so already); (b) `--requirements` shelving the project's own records:
  **PO**, after a rule for "proven" — the `built` reader (M-J) is the natural one (the verify's (b): four placeholder
  records would reach every project's `--list`); (c) the vendor-header cache into the store, through the store's door:
  **keep** (= board C7); (d) `datasheet-reader` loses `Write, Edit`: **keep** once `--fact-set` covers every field it
  writes (—); (e) the six literal store paths out: **keep**, with #23's grep as a docs test.
- C12 spec and code agree on privacy — **change** per the verify: `sources` into `PRIVATE` (§5.8's promise);
  `catalog`/`downloads` are the PO's and bear on P178 (a 0700 catalog cuts against a shared layer); the no-`fcntl` line
  and the fetch cap: keep.
- C13 the `built` digest covers the chain facts — **change**: build the reader (M-J) or drop the digests; keep the
  `note_built` sentence half.

### board-records (C1–C12)

- C1 a bare-number label refused — **keep** + M6 (the `pins` key side) + both tscircuit regexes.
- C2 `pad_aliases` reaches the footprint — **keep**; the validator rule as written refuses the S3 (`A4` is a key —
  the verify): the rule is "both keys map to one GPIO"; do the verify's M1 first — `check_spine` prints tscircuit's
  own `source_trace_not_connected_error` before the island (a reorder at :419-441): the "why" already exists there.
- C3 the `physical` schema written where enforced; unread keys refused; removals — **keep**; correct the Known list
  (M3: `thickness_mm`, `header.pad_mm`); the removals first; emitting mounting holes changes every generated footprint
  — **PO**.
- C4 `emit_footprint --json` on every path — **keep**, the could-not-run variant (removes a path); its shape joins M-B.
- C5 the drill sentence — **keep**.
- C6 one comment-key rule — **keep**; the fault that matters is the `//jtag` refusal's words.
- C7 the vendor cache in the store — **keep**; through `store`'s door (TECH-LEAD-13), the fallback order said.
- C8 a board record from a drawer entry — **keep** as D8's item (D PO 2026-10-09), L; the per-chip table is a third
  statement of chip facts — a test against both shipped boards or it drifts; the pick no longer writing `reused` is a
  by-design change — **PO**. Direction: P178's "find → create" and P162's board half; it must not add a one-board place
  (TECH-LEAD-7).
- C9 every stop from one rule; `--for-fab` requires geometry — **keep**; both spellings (M5); the XIAO is SMD —
  `footprint_source` (a converted vendor footprint) rather than header rows (the verify).
- C10 a board's `function` validated and carried — **keep**; the SKU fact in the record, the owned piece's in the
  drawer (the verify's M4); a malformed list refused instead of dropped.
- C11 `pins` against the stand-in — **keep**, merged with firmware C1 into one change (M7's silkscreen boards; a
  registry copy under `data/` with its version).
- C12 remove `footprint_module` — **keep** (a removal), with C9; count the fixtures and pages (the verify).

### chain-and-checks (C1–C9)

- C1a the chain re-seeds `rules.json` after `--keep` / C1b the derived half leaves the file — **change**: seed at
  `parts.py --requirements` (MC-6: a writer that already holds the picks and the records; no check becomes a writer);
  C1b is the direction and carries MC-1 (an empty derived list versus `compare_design`'s could-not-run) — **PO**;
  order C3 before any seed, for irrigation.
- C2 a declared signal reported, not refused; a stray stderr line is could-not-run — **change** to M-A: emit
  in-process and return typed notes (TECH-LEAD-3 (a)); keep the four circuit-gap notes as PROBLEMS because they are
  gaps (the verify); the `note:` prefix never becomes a contract.
- C3 a record says an input holds its own level — **change**: the key says *why floating is harmless* (a load, a
  module-side pull, gated by another pin) or a module-side pull is a fact the seed reads (MC-5: the amplifier's `SD`,
  the I²S lines); per-entry notes survive `merged` (MC-2).
- C4 one table for owed facts — **keep**, after MC-3 (`pin_order_proof`: owed, or a contract failure) — **PO**;
  `_about` and `LAYOUT_FACTS` go; the test per fact is the one that would have caught the diagnosis's own wrong row.
- C5 one reader, one namer — **keep**; fold `_name_after`.
- C6 the board changes in one place — **change**: take the alternative (`active_id` falls back to the requirements
  file's `board`; one statement fewer) — the recommended variant cements a single-board file that part 2 lifts
  (TECH-LEAD-7); the bin keeps `active.json` (no requirements file); `boards/README.md:21`'s "THE one place" gains its
  qualifier.
- C7 five small fixes — **keep**; K52 as could-not-run (MC-8); K63 the refuse variant.
- C8 `--keep` builds the kept `board.tsx` — **keep** (D PO 2026-10-05, #44); build in place (MC-4); irrigation
  records no `built` until regenerated — say it on the card.
- C9 the unserved note in every outcome — **keep**.

### needs-matching-vocabulary (C1–C9)

- C1 one matcher, hits not AND, the missed words said — **keep**; tokens, not substrings (M5); it changes documented
  behaviour — the two journey recordings, `tests/test_parts.py:791-797` and five pages (the verify) go on the card.
- C2 the pick says what the match knew; `--needs` shows the pick; a mark/pick pair rule — **keep the note** (with the
  verb, M1) and the listing; **drop the pair rule** (it refuses M-before-C and plant-alarm's file today); a `fit` value
  is a **PO** decision (M4).
- C3 drop a need, clear a pick — **keep**; `_reserve` extracted once (two copies → one); the history keeps old ids —
  say so; a tombstone that stays in the file travels through sync better than a vanished object (the verify; P178).
- C4 say how many entries no need can reach — **keep** + M8 (the question after an import, on drawer.md).
- C5 the skeleton carries every chain fact; research ends with `--audit` — **keep**; the alarm is `--audit`, not
  `--validate` (M3).
- C6 the cut lists its words and ids — **keep**; cap the ids per word.
- C7 a count on a need — **PO**; M7 first (one need per instance already yields `Valve1…Valve4`).
- C8 refuse a differently named requirements file — **keep**; irrigation's rename is its owner's (M6); say what "both
  exist" does.
- C9 the store's words shown — **keep** + M2's "one word more" case.

### firmware-and-bench (C1–C6)

- C1 stand-in pins as a board fact read first — **change** to the verify's M1: the emitter picks a name the part knows
  (the oracle is in hand at `mapping.ts:96`); the override gets a documented name (`wokwi_pin_names`, `null` kept) and
  a validator for keys and values; a "spend last" role only for a GPIO with no name at all (neither library board has
  one — the verify's (1)); amend, do not delete, the true sentences (M9); the converter's `--json` (M8) is the
  mechanism behind its (d), not a later chore.
- C2 `flash_image` refuses another chip's interpreter — **keep** in the verify's form: the 16-byte read where the
  board and the image meet (`check_spine`'s simulation stage), `--chip` optional; the 13 = C6 row from a newer esptool
  (M5).
- C3 the step from the image to the board — **PO** (a script or a page; P79's shape); a minimum esptool version; the
  write offset and the 4 MB-into-16 MB question are bench facts (—).
- C4 a sixth check, the firmware against the pin map — **change**: it re-adds a check the PO cut (D PO 2026-09-29,
  `066c4af` — the verify's M2) and must say why the convention now holds (`pins.py` since P36); it is use-against-map,
  not the literal triangle (M3); "has" = `pins` ∪ `pin_roles[*].gpio`; K53 (mutate.py's import-break over-count) first;
  M7 — the record's deep-sleep facts into `pins.py`'s header — is the S first consumer. Inside the 2026-10-01 boundary.
- C5 a scenario measured against the pin map — **keep**, as a note.
- C6 the documents follow the code — **change**: amend the true sentences; a retired-phrase check is the bin's, not
  spark's — a new S check if the PO wants one.

### docs-and-recorded-outputs (Changes 1–7)

- 1 the gate counts outputs behind the version — **keep as a report line**, never a failing check (a patch that
  changes no output would stale 44 blocks at once — the verify).
- 2 the README block ends where a shell can finish it; the gate runs it — **keep**; the file in the project; a
  recorded output and the tally's refusal shown beside it (M8).
- 3 one recorder at each release — **change**: promote or delete the gitignored recorder first (M1), classify the 42
  blocks into re-recordable and recorded-only (M2, M3), run `--check` from `check_commit.py` on a version change (M4:
  there is no release gate); cog's markers in pages agents read raw are a cost to measure.
- 4 the own-board route recorded; three facts written where the steps are — **keep** minus the half already on the
  page; `--fetch <board>` → could-not-run through the argument path.
- 5 the gate reads the agent pages — **keep** + M7 (name a page by its path) + leave `test_orphans`' sibling
  Makefiles out.
- 6 density and long lines — **PO**; the README's long lines are table rows (the verify); one card with Change 2.
- 7 one sentence on what spark has built — **keep**, per-store wording.

### Missing — changes nobody proposed, each structural

- **M-A · Emit in-process; notes are a return value.** `check_spine` calls `emit_board.render(design) -> (text,
  notes)` (the module is imported at :62 already); each note is `{kind, subject, sentence}`; the stage decides severity
  by `kind`. Removes the stderr channel (TECH-LEAD-3 (a)), the `note:` contract chain C2 would add, and the
  "emit_board.py crashed" path (an exception is could-not-run at `main` already). Closes the STATUS_LED
  exit-1-for-life with chain C2's content rule. M. Test: the fixture with `signals`; a fake generator that raises.
- **M-B · One envelope from every script, with the store named.** `outcomes.envelope` printed by every `--json`
  (`check` → `tool`; `check_vendor_pins`' list → one envelope, `mismatch` → `problems`; `assign_pins` gains `status`);
  `--json` on `boards.py`, `tools.py`, `emit_board.py`, `init_project.py`; the `store` field (store C1) in it.
  `tests/test_json_contracts.py` collapses to one shape. The §6.4.1 remainder (P43). M–L. Direction: "designed for
  agents first" (§6.4); P160's editor reads one shape.
- **M-C · One reader.** `outcomes.read_json(path, what) -> dict` raising `Unreadable(path, why)`; every `main` maps
  it to could-not-run; the seven readers call it; 37 sites (TECH-LEAD-1). S–M; the fix of K11's class and the
  2026-09-30 note's item 3.
- **M-D · Exit codes from the table only.** Delete the aliases that carry a new meaning (`boards` no-selection →
  could-not-run; `check_vendor_pins` mismatch → problems; `init_project` nothing-to-do → the PO's word); keep the
  aliases that mean "ran, found something" or delete them all; one grep test on `EXIT_PROBLEMS as`. S.
- **M-E · `parts.py` by seam.** `records.py` (the contract :72-794, digest and shelf :895-965, `skeleton`,
  `signals_for`, `unverified`), `documents.py` (:985-1283: keep, kept, read, fetch), `parts.py` the CLI
  (`OPERATIONS`, `_op_*`, `_say`, `main`); `drawer` and `needs` import `records` — the cycle goes, and every
  function-local sibling import in `parts.py` becomes a top-level import of the CLI. Cost: 266 anchor rows move in the
  same commit (TECH-LEAD-5); the net exists (`check_commit.py:143`). W16: moves, never copies. **PO**: the 2026-09-30
  note said no; its premise has changed (TECH-LEAD-5, -12).
- **M-F · The engine adapter (P154).** `engines/tscircuit.py` with `build(workdir) -> circuit_path`, `version()`,
  `can_build()`; `check_spine.run` calls the engine the role names; later the same for the simulator. M. Not part 1's;
  the direction that makes the role switch a switch.
- **M-G · Boards and parts on one loader.** `records.load(kind, id, project)` over `read_json` with a per-kind
  `validate`; `BoardError` and `PartError` become one `RecordProblem`; `layers()` gains its writable column and takes
  `kind` from a table, not an `if`. The seam part 2 meets first (TECH-LEAD-6, -7). **PO**; after M-C.
- **M-H · The outcome invariant.** One test: for every script with a `main`, three malformed inputs (a non-UTF-8
  file, a list where an object belongs, a missing path) → exit 2, one sentence on stderr naming the path, no
  traceback. Catches K11's, K28's and K52's class for every future script. S.
- **M-J · A reader of digests** (the store verify's M3). `--audit` and `--tally` compare a `built` or `based_on`
  digest with today's and say "re-prove" or "behind". The condition for store C11 (b) and C13.

### The smallest set of structural changes

Seven, each making one class of mistake land in one named place with one named reason; the diagnoses' other changes
are then fixes inside a shape, not new shapes.

| # | change | the one place | the one reason it prints | closes | proof |
| --- | --- | --- | --- | --- | --- |
| S1 | M-C one reader | `outcomes.read_json` | `<path> is not UTF-8 at byte N` / `is not JSON: …` / `holds a list` | K11, K16, K61's read half, K28's class | M-H green on every script |
| S2 | store C3 + the door test | `store.locked()` beside the data; the five doors | `called with no lock held` / `writes under the store outside its door` | K5, K6, K7, K14 | the K5 two-`TMPDIR` test; a mutation row per writing operation |
| S3 | store C5's id + C7 | `.spark/project.json`'s `id`; `PLAIN` on read | `carries the id of listed project X` / `not a plain key (a conflict copy?)` | K4, K9, K10, half of K3 | the three K4 runs answer with one sentence each |
| S4 | M-A + the converter's `--json` | `emit_board.render`'s notes; the converter's envelope | severity from `kind`, never from a channel or a substring | the STATUS_LED note (★C4), K32's classification, K20's reading | irrigation's chain exits 0 over its one declared signal |
| S5 | chain C4 + MC-3 | `records.CHAIN_FACTS` as a table | `owes X — the <stage> stops` | K47, K48; P125/P165's data | the per-fact `check_spine.run` test |
| S6 | M-B + store C1 | `outcomes.envelope` with `store` | one shape, the store named, three statuses | K1's visibility, K55, K57, K28 | `test_json_contracts` holds one shape |
| S7 | M-D | `outcomes.EXIT_FOR` alone | no alias means more than "ran, found something" | K52, the `init`-twice case, `mismatch` | a grep test on `EXIT_PROBLEMS as` |

Order: S1, S7 and S2 first (S each; S2 wants store C1 so `locked()` has a home); S6 next, which carries C1's field
everywhere; S5 after the PO's MC-3 answer; S3 with M2's; S4 last of the seven (M; it touches the chain's main loop).
M-E and M-G are the shape the fixes take if the PO trades the 266 anchors for a readable traceback; no K-row needs
them.

### Module boundaries and test seams

Proposed layers — a module imports only from a lower one; a function-local sibling import is a finding:

0. `outcomes` (statuses, the envelope, `read_json`, `Unreadable`), `fab`, `netlist`, `copper`.
1. `store` (the home, the places, the layer table with its writable column, the five doors, the lock, the history,
   `keep` and `fetch`).
2. `records` (the contract per kind — parts and boards — the owes/broken table, `function`, digests, shelving),
   `documents`.
3. `boards` (selection and `--resolve`, until M-G folds it), `design` (load and names — `component_name` moves here,
   chain C5), `assign_pins`.
4. `emit_board` (returns text and notes), `emit_footprint`.
5. `drawer`, `needs`, `cost` (the store-side strategies; `needs` keeps the one matcher).
6. the commands: `parts` (the CLI), `check_spine`, `check_all`, `init_project`, `tools`, the checks, `flash_image`.

Today's crossings, by my read: `parts` (layer 2 by content) importing `drawer`, `needs`, `cost`, `tools` (5–6) inside
functions — M-E ends it; `boards` (3) importing `emit_footprint` (4) for `footprint_stop` — the stop rule belongs with
the board contract (2), and `emit_footprint` imports it; `needs` (5) holding a copy of `component_name` (4) — chain C5.
`check_all`'s function-local imports are by design (its A7 comment) and stay.

Test seams, each one test that holds for every future module: (1) M-H, the outcome invariant; (2)
`test_json_contracts` on one envelope; (3) the store-door grep (no write under `store.home()` outside the five); (4) an
import-direction test over the layer list, in `test_orphans.py`'s style; (5) a home test (import every module under one
`SPARK_HOME`, change it, ask every path function again); (6) the anchors at push, which exist. The 2026-09-30 note's
rule stands: no new internal unit tests for a move; the CLI boundary is what a move cannot disturb.

### The ten that matter most

1. **Store C1 + M1** — one mechanism line; after it every agent's run names the store it answered from, the
   precondition for believing any other report (K1; the P100 facilitator's contradicted ★C1 was this). S.
2. **Store C3 + the door test** — the silent-corruption class (K5, K6, K7); structural: a writer refuses without the
   lock, and a grep names a writer outside the door. M.
3. **M-C (store C8 widened)** — one reader, no traceback, the right exit code at 37 sites; the cheapest diagnosability
   win for a person and an agent alike (K11, K16; the 2026-09-30 note's unbuilt item). S–M.
4. **Chain C4 + MC-3** — the owed-facts table every mouth reads; without it `--need`, `--audit`, `--requirements` and
   the chain contradict one another about one record (K47, K48); P125 and P165 rest on it. M, after the PO's answer.
5. **Board C1 (+M6) and C2 (+M1's reorder)** — the one silent circuit-class fault (K22) and the one that stops the
   library S3 the day a design spends its SPI pins (K23; the firmware diagnosis's 22-button run); the reorder prints
   the cause tscircuit already wrote. S–M.
6. **Chain C5** — three removals and one move; K59, K60, K61; a day.
7. **Needs C1 (+M5) + C9** — one matcher for one question; K33, K38; a documented behaviour changes, so the recordings
   and tests are on the card. S–M.
8. **Store C6 after M2** — K3, the blocker every second project on the one FireBeetle meets; the decision (derive or
   keep) first. M.
9. **M-A (chain C2 reshaped)** — severity from content; the exit-1-for-life on a declared signal; one channel fewer. M.
10. **Board C8** — K29, D8's first fix (D PO 2026-10-09); L; after 5 and with P162's board half; it must add no
    one-board place.

Decided already, so not ranked: chain C8 (D PO 2026-10-05, #44). The shape rather than a fix, so the PO's trade:
M-B, M-E, M-G. Outside part 1 by direction: M-F (P154); firmware C3 and C4 (P79; the 2026-09-29 cut).

## 3. What I could not check, and why

- I ran no spark command and copied no store, so every runtime claim is a diagnosis's or verifier's run, re-read at
  the lines it cites; where a cited line number differed from the file I read, the file won.
- The suite was not run (it writes bytecode under `~/Development/spark`); 1,712 is a grep of `def test_`, the store
  diagnosis's run says 1,699 ran — the difference (parametrised or skipped tests) is —.
- "132 `.main([`" is a proxy for tests entering a `main`; the 2026-09-30 note's "79% reach into a module by symbol"
  was not re-measured.
- M-E's cost is 266 anchor rows (grep), not an hour count; that `tools/mutate.py --anchors` refuses a moved `find` at
  push I read at `check_commit.py:143-147` and did not run.
- M-G's size: the 2026-09-30 note's "57 duplicated lines" is its measurement, not re-made.
- Whether `tools.PERSONAL`'s import-time read ever bites: no observed fault; reasoned only.
- P178 has no design on disk (#123 is the only statement); P154's and P136's discoveries have not run; my direction
  judgments rest on the cards' words.
- The six literal store paths in `agents/` and `commands/` are the store verify's grep, not mine;
  `agents/datasheet-reader.md:5` I read.
- Whether `--fact-set` can set every field the `datasheet-reader` writes (store C11 (d)): —.
- The firmware area's hardware facts (chip ids, the write offset, a µA meter) are the diagnoses' H and the bench's.

## 4. Questions for the decider

1. **M2 — a hold: derived on read (no `used_in`, no release operation) or a stored decision with
   `--release`/`--forget-project` and an audit line?** · decides store C6's shape, half of K3, and whether a shared
   store (P178) can ever know what is held anywhere.
2. **MC-3 — `pin_order_proof` absent: a fact a record owes (buildable, warned, marked — your words on #102) or a
   contract failure (as `parts.load` refuses today)?** · decides chain C4's table, `--requirements`' refusals, and
   which of the 17 catalog records the chain accepts.
3. **The `parts.py` split (M-E) and the boards/parts merge (M-G): is a readable traceback worth moving 266 mutation
   anchors and reopening the 2026-09-30 "do not refactor" verdict?** · decides whether the fixes land inside today's
   shape or a new one; no K-row needs the split.
4. **Exit codes (M-D): what does `/spark:init` run twice mean — `ok` (nothing to do is not a problem) or `problems`,
   as today?** · decides one alias; the other two (`boards` no-selection, `mismatch`) have one answer under
   `outcomes.py`'s own words.
5. **Chain C6: keep `boards/active.json` in step from `--requirements` (two statements synchronised) or let the
   requirements file be the board when it exists (one statement; the bin keeps its file)?** · decides whether part 1
   adds a one-board place that part 2 must remove.
6. **The real store's guard (store C2): the temp-root rule, the explicit flag, or both?** · decides P164's shape and
   what an agent's unscoped command does.
7. **Mounting holes emitted (board C3), and `sources`/`catalog`/`downloads` made private (store C12)?** · the first
   changes every generated footprint; the second cuts against a shared catalog (P178).

## 5. Searches

none — every claim rests on files in the repositories, `gh issue view` (read-only) and the discovery folders named in
the header. The library options in TECH-LEAD-14 are tagged H with their sources and were not searched.
