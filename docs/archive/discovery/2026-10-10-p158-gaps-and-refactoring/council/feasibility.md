# Feasibility — P158 part 1 (what each change takes and touches, which are one, which conflict)

Written 2026-10-10 by the Feasibility lens, against spark 0.8.1 (main `a8aa34d`, `git log -1`), reading `../catalogue.md`
(K1–K74), the six diagnoses and their verifications in `../diagnosis/`, the primary artefacts they cite (`scripts/*.py`,
`boards/*.json`, `commands/*.md`, `docs/guide/*.md`, `tests/`, `tools/`, `data/tools.json`), the store design and discovery
(`docs/2026-10-04-store-design.md`, `docs/archive/2026-10-04-store-discovery.md`, `docs/archive/2026-09-30-refactoring-architecture.md`), the
P100 folder (`../../2026-10-09-p100-real-use/brief.md`, `items.md`, `council/tech-lead.md`) and the cards #17, #22, #23, #44,
#58, #59, #70, #89, #93, #94, #96, #99, #101, #102, #114, #118, #119, #123, #5, #16 (`gh issue view`, read-only). Runs: the
test suite and the mutation anchors on an rsync copy of the repository without `.git` (`<scratch>/mut/spark`), with a copy of
the PO's store (`cp -R` to `<scratch>/store`) and `SPARK_HOME`, `HOME`, `TMPDIR` as three separate words (`env | grep
SPARK_HOME` under the prefix printed the scratch path once, first); the real store was never run against and nothing was
written under it; nothing was written under `~/Development/spark` but this file. Tags: **E** a pointer or a run and its
output; **H** a claim with its source; **D** a decision (who, when); — unknown. Every size below is an estimate (H, mine)
and says what it rests on; S is under an hour of code and test, M a day, L more. The PO's criteria (D PO 2026-10-10) are
applied to every change: testability, diagnosability (where and why, to a person and to an agent), simplicity (remove before
add). The harness relayed one user line for this run — the PO's question of 2026-10-10 about *"new file formats or synch
libraries or techinques … from an existing library … the whole store synch and global and loval and project store sync and
rules and editor"* — answered in §2.2.

My questions: what each proposed change takes and touches (files, tests, docs, the repositories that use spark), which a read
or a spike settles, which are one change in disguise, which conflict, and an honest estimate for each.

## 1. Findings

Each: FEASIBILITY-n · claim · tag · pointer · supports only (what the evidence carries, no more).

- **FEASIBILITY-1 · The suite is 1,699 tests in 33 s and every mutation anchor holds.** E `python3 -B -m unittest discover -s
  tests` on `<scratch>/mut/spark` with the scratch store → `Ran 1699 tests in 32.956s` / `OK (skipped=3)`; wall 33.56 s
  (`/usr/bin/time -p`); `tools/mutate.py --anchors tests/mutations/*.json --root .` → `1268 mutation(s) in 115 table(s): every
  anchor present, once`; `cat tests/test_*.py | grep -c 'def test_'` → 1,712 definitions in 36 files. Supports only: a change's
  test cost is minutes of run time, and the acceptance bar (every table's `find` string present once) is intact on `a8aa34d`.
- **FEASIBILITY-2 · The hidden cost of any move in `parts.py` or `needs.py` is the mutation tables, not the code.** E my
  count over `tests/mutations/*.json`: 1,268 rows, of which `scripts/parts.py` 266, `scripts/needs.py` 196, `scripts/store.py`
  72, `scripts/check_spine.py` 48, `scripts/drawer.py` 40, `scripts/init_project.py` 25, `scripts/design.py` 23,
  `scripts/boards.py` 21, `scripts/emit_footprint.py` 3, `scripts/check_vendor_pins.py` 2; `wc -l scripts/parts.py` → 2,214.
  E `tools/check_commit.py:142-147` runs `--anchors` at every push and `:177` fails the push on a refused anchor. E
  `docs/archive/2026-09-30-refactoring-architecture.md:114-116` said the same at "72 of the 132 mutation anchors". Supports only:
  K64's structural refactor (C-41, "split `parts.py`") is a table-re-anchoring project — about 460 rows (36 % of 1,268) sit
  in the two files — while the per-fault changes below each touch a region and a handful of rows.
- **FEASIBILITY-3 · "One reader for a JSON file" was a named target on 2026-09-30 and was not built; the fault class recurred
  in two diagnoses.** E `docs/archive/2026-09-30-refactoring-architecture.md:73-74` (target item 3: `outcomes.read_json(path, what)`
  "retiring the exit-1-for-an-unreadable-file class at eight sites"), `:57` ("8 raw against 3 guarded"); today
  `grep -c 'json.loads(' scripts/*.py` → 41 lines in 18 files (`parts.py` 11), and at least nine reader functions each do
  their own open-and-check: `store.projects` (`store.py:239`), `drawer.entries` (`drawer.py:92`), `needs.read`
  (`needs.py:47`), `needs.requirements` (`needs.py:513`), `design.read` (`design.py:98-99`), `boards._read_json`,
  `parts._parse` (`parts.py:1272`), `parts.load` (`parts.py:266`), `check_vendor_pins.check_board` (`:116`). K11, K16 (store)
  and K59, K60, K61 (chain) are this class. Supports only: SL-C8 and CC-C5 are one change with a dated specification; the
  comparable P42 landed at −8 code lines against −45 estimated (E `docs/2026-09-30-…:149-150`), so the gain is one place to
  guard, not lines.
- **FEASIBILITY-4 · The lock is pinned by 8 tests for 12 writing operations, and the suite writes the store directly 42
  times.** E `python3 -c` over `parts.OPERATIONS` → 12 rows carry `writes` (`skeleton, fetch, keep, promote, drawer-set,
  drawer-import, function-set, fact-set, needs-set, pick, requirements, step`); `grep -c 'locked('` → `tests/test_store.py`
  7, `tests/test_needs.py` 1, `tests/test_parts.py` 0, `tests/test_drawer.py` 0; `grep -c -E
  'store\.(write_json|write_file|copy_folder|append_event|add_project)\('` → `tests/test_store.py` 41, `tests/test_drawer.py` 1.
  Supports only: SL-C3's "a writer that holds no lock refuses" meets those 42 calls, so its size is M (a fixture that wraps
  them) — a suite-only exemption would be a second guard of the K2 kind (the verifier's (a)).
- **FEASIBILITY-5 · The record layers are small enough for any text sync; the documents are 91 % of the store and are
  private by design.** E `du -sh` on the copy: 33 MB total, `sources/` 30 MB (85 files), `downloads/` 1.7 MB, `drawer/` 440 KB
  (110 files), `shelf/` 204 KB, `catalog/` 188 KB; `find … -name '*.json' | wc -l` → 137 files, `wc -c` → 319,145 bytes;
  `history.jsonl` 8 lines; `projects.json` 5 projects. E `docs/2026-10-04-store-design.md:264-265` (§5.8: document bytes never
  published). Supports only: a shared layer of records is a 312 KB text problem; nothing about documents may be synced.
- **FEASIBILITY-6 · SQLite's own corruption page warns of network-filesystem locking and of background copies taken
  mid-transaction, and says nothing of cloud-sync folders by name.** E fetch of sqlite.org/howtocorrupt.html, 2026-10-10:
  §2.1 "some filesystems contain bugs in their locking logic … This is especially true of network filesystems and NFS in
  particular … database corruption might result"; §1.2 "Systems that run automatic backups in the background might try to make
  a backup copy of an SQLite database file while it is in the middle of a transaction. The backup copy then might contain some
  old and some new content, and thus be corrupt." Supports only: a store that may live in a synced folder (a sync client is a
  background copier — H, my inference) should not keep its tables in one SQLite file; on one disk SQLite would work, at the
  price of `cat`, `diff` and `grep` (the drawer is 110 files a person opens today).
- **FEASIBILITY-7 · The PO's Python has `sqlite3` in the standard library and `jsonschema` installed; a hobbyist's has only
  the first.** E `python3 --version` → 3.10.0; `import sqlite3` → 3.43.2; `import jsonschema` → 4.2.1, requires `attrs`,
  `pyrsistent` (`importlib.metadata.requires`). H (my knowledge): current `jsonschema` releases depend on `referencing` and a
  compiled `rpds-py`. Supports only: a schema file costs nothing to ship and read; enforcing it at run time is a dependency
  decision against "users install nothing heavy" (D PO 2026-10-06, memory).
- **FEASIBILITY-8 · An editor for every JSON record exists for the price of a schema file and one settings line.** E fetch of
  code.visualstudio.com/docs/languages/json, 2026-10-10: `json.schemas` with `fileMatch` and `url`; "To map a schema that is
  located in the workspace, use a relative path"; "structural and value verification based on an associated JSON schema",
  "suggestions as you type with IntelliSense", "information about properties on hover"; `$schema` in the file is
  VS Code-specific. Supports only: the "editor" half of the PO's question for a person; it gives an agent nothing that
  `parts.py --describe --json` and the envelope do not already give.
- **FEASIBILITY-9 · A CRDT library exists for Python as compiled bindings and solves a problem no store scenario names.** E
  web search 2026-10-10: `pycrdt` (bindings for Yrs, the Rust Yjs; Text, Array, Map types; manylinux wheels on pypi.org); no
  Python `automerge` in the results (—). E `drawer.py:6-7` (every write sets, "gone is count 0"), `store.py:272-274`, `:308-327`
  (history lines idempotent by `EVENT_KEYS`). Supports only: the store's writes already merge the way a CRDT would (last
  writer per field, union of events) once identity and tombstones exist; a CRDT library would add a compiled dependency for
  live concurrent editing of one document, which #123's find/create/share/reuse acts do not ask for.
- **FEASIBILITY-10 · Two diagnoses propose the same stand-in-pins check in two shapes, and the data route already works.** E
  `../diagnosis/board-records.md` C11 (a registry copy under `data/`, a validate rule) and
  `../diagnosis/firmware-and-bench.md` C1 (a converter `--part-pins` CLI, a `not_on_simulator` role, a classifier string); E
  `../diagnosis/firmware-and-bench.verify.md` RC-1 (2): the `TX` design converted with `"TX": "TX"` in `wokwi_power_pins` → 6
  connections; `"D3": null` → 33 connections; `node dist/converter.mjs --help` → `SPARK_BOARD_JSON is not set`. Supports
  only: one card, data and validator first (BR-C11's testable form), the bundle untouched until a structured `--json` is
  wanted; FB-C1(c)'s role would be false for both library boards (the verifier's point 1).
- **FEASIBILITY-11 · Four listed projects depend on spark's command lines, in different places.** E the bin's `Makefile:49-53,
  96, 182, 186, 212, 220, 223, 228, 232` run `boards.py` (`--path`, `--id`, `--paths`, `--get`, `--resolve`, `--validate
  --for-fab`, `--validate`), `check_vendor_pins.py` (`--offline` and live), `check_bom.py`, `check_physics.py --rules
  .spark/rules.json`; the bin keeps `boards/active.json`, a committed `.spark/board.json`, a hand-written `.spark/rules.json`,
  no requirements file (`ls`). E irrigation: `irrigation.requirements.json`, a committed generated `FireBeetle2Esp32S3.tsx` and
  `board.tsx`, `parts/` with 7 records and 2 chip folders, `.spark/rules.json`, no `needs.json`. E plant-alarm:
  `requirements.json` (XIAO), `.spark/needs.json` with four needs, `battery` marked `have` with no pick. E rc-car:
  `car.requirements.json` and `remote.requirements.json` (two boards), `parts/` 3 records. E `projects.json` on the copy lists
  irrigation, smartbin-local, rc-car, spark-quickstart, plant-alarm. Supports only: which changes need a same-commit edit of a
  library file (BR-C1, C3, C9, C11, C12 reach the bin's `make check` through the library S3 file), that NM-C8's glob meets a
  two-board project, and that CC-C1's seed meets plant-alarm's amplifier inputs (its verifier's MC-5).
- **FEASIBILITY-12 · Most of the 56 changes alter a printed sentence, and every printed sentence in the guides is a
  hand-pasted block the gate cannot see drift in.** E `tools/check_docs.py:142-145` (`undated_outputs` checks the note's
  presence only), `:165-166` (`failed_examples` compares an exit code, never the text); 42 ```` ```text ```` blocks and 44
  version markers, 0 of them 0.8.x (E the catalogue's grep, re-measured in `../diagnosis/docs-and-recorded-outputs.verify.md`
  RC-1); a recorder and a comparer exist under `.superpowers/` (gitignored, `.gitignore:8`), path-bound to a worktree that is
  gone (E the docs verifier's M1 — I did not open those files). Supports only: the recorder (DR-3) is a cost multiplier for
  every diagnosability change, so its place in the order is early; and until it exists each card's Done line re-records by
  hand.
- **FEASIBILITY-13 · A new operation costs one allowed-tools pattern per command and one routes test, every time.** E
  `commands/idea.md:3` pre-approves 11 `parts.py` patterns, one operation each; `tests/test_routes.py:358`
  `test_each_parts_py_pattern_names_one_operation_that_stays_on_the_machine`, `:351` `test_no_command_or_skill_pre_approves_a_
  network_operation`. Supports only: SL-C6 (`--release`, `--forget-project`), NM-C3 (`drop`, an empty pick), BR-C8
  (`--board-skeleton`) and FB-C3 (`flash.py`) each carry this fixed small cost; it is not where their size is.
- **FEASIBILITY-14 · The home SL-C11 needs was specified on 2026-10-04 and not built.** E `docs/2026-10-04-store-design.md:274-275`
  (§6.1: "the table of layers nearest-first (each row naming its record-store implementation and whether it is writable)");
  `scripts/store.py:71-81` (`layers()` returns `(layer, path)` and nothing else). Supports only: "where a record goes when
  it has proven itself" belongs in the layer table (a `writable` column, ~10 lines H), before any shelving rule.
- **FEASIBILITY-15 · The tools list is data with chip-blind roles.** E `data/tools.json`: entries are `{for, kind:
  download|path, file|exe, url, sha256, meets, install}`; `roles` is a flat `role → tool` map (11 roles); `contracts` maps
  `firmware-image → micropython-esp32-bin`. Supports only: FB-C3's two tools are two entries (S); the FB verifier's M4 (a
  chip-parameterised role) is a shape change to `roles` (M), not a data edit.
- **FEASIBILITY-16 · There is no release gate for a recorder's `--check` to live in.** E `tools/pre-push` → `check_commit.py`;
  `check_commit.py:135-147` runs the suite and the anchors, `:174-177` `check_backlog`; nothing reads
  `.claude-plugin/plugin.json`'s version; `scrum/README.md` DoD 10 is prose. Supports only: DR-3's check runs in
  `check_commit.py` on a commit that changes the version (S to add), or it stays a sentence.
- **FEASIBILITY-17 · The chain is cheap to prove by running; the simulation stage is not.** E `../diagnosis/chain-and-checks.md`
  §4 (the reference design 6.6 s, irrigation 9.6 s wall) and `../diagnosis/docs-and-recorded-outputs.md` RC-2 (6 s), their
  runs; `scripts/check_spine.py:507-514` ("no test on this machine reaches run's simulation stage"); every Wokwi run spends
  paid minutes (D PO 2026-10-09, #80 Q4 per the P100 brief D4). Supports only: every chain-side change can carry an end-to-end
  proof in its test; nothing on the simulation stage can, which bounds FB-C1(d) and FB-C5 to unit tests of the sentence.
- **FEASIBILITY-18 · The needs file's missing removal is an acknowledged gap, and the sync-friendly form is a tombstone.** E
  `commands/idea.md:24-25` ("there is no removing or renaming a need yet, so a wrong one is fixed by hand"); `drawer.py:7`
  (the drawer's tombstone is count 0); `store.py:272-274` (history events keyed, never deleted). Supports only: NM-C3's shape
  (`dropped: true` in the file, or removal) is a decision that bears on P178, not only on K35.
- **FEASIBILITY-19 · `inside_git` makes the shared and the private layers necessarily separate folders.** E `store.py:94-96`
  (`PRIVATE`), `:209-214` (`_make_ready` refuses a private target inside a git work tree). Supports only: a shared layer as a
  git clone can hold catalog-like records and never the drawer, history or projects list — which is what §5.8 wants anyway;
  the "git as the store's own history" option in `../diagnosis/store-levels-and-holds.md` §3 would need that rule rewritten,
  the split needs nothing rewritten.
- **FEASIBILITY-20 · Nobody owns K53, and two proposed proofs lean on it.** E `tools/mutate.py:190-209` (`_run` scores a
  mutation caught when the suite is not green, with no import or compile check of the mutated file); #94 comment
  2026-10-08T23:41 ("counts a mutation as caught when the mutated file no longer imports"); FB-C4's mutation proof and SL-C3's
  12 rows both read `mutate.py`'s verdict. Supports only: a ~10-line fix (compile the mutated file; a `SyntaxError` is
  REFUSED, not CAUGHT) is a prerequisite for trusting any new table's "every row caught" line.
- **FEASIBILITY-21 · The derived half of `rules.json` needs no build, so the seed can live in a writer that exists.** E
  `../diagnosis/chain-and-checks.verify.md` MC-6 (`design.rails_requested`, `emit_board.power_connections`,
  `rails_without_a_source`, `declared_inputs`, `i2c_lines` — all from the requirements and the records; `needs._power_gaps`
  already computes the rails for `--requirements`); E `scripts/needs.py:442-472` (`_power_gaps`) and `init_project.py:81-131`
  read by me. Supports only: CC-C1 in MC-6's form (seed at `parts.py --requirements`) is M and makes no check a writer; a
  `needs → init_project` import adds no cycle I could find (`init_project` imports `design`, `emit_board`, `boards`, `store`,
  `tools`; `needs` imports `design`, `emit_board` — H, read, not run).
- **FEASIBILITY-22 · The docs gate's scope widening is free today and its cost is subprocesses.** E `tools/check_docs.py:30-33`
  (7 files), `:74-81` (`_help` runs each named script's `--help`, cached per script and verb); `ls commands skills agents` → 7
  + 3 + 4 = 14 pages; the docs verifier's run of the five per-page functions over the 14 pages → 0 problems and 5.5 s for the
  gate (E its RC-1, RC-5). Supports only: DR-5 is S and silent; the one defect to fix with it is the page named by `path.name`
  (its M7).

## 2. The proposed changes, judged from the feasibility lens

### 2.1 The ten that matter most — my order, and the reason for each rank

The order rests on four things: silent harm to the PO's own data first; mechanisms many rows share, because one change
closes several and shrinks what later changes touch; the PO's decided items placed where their foundations are done; and the
recorder early, because every sentence change below re-records guide blocks by hand until it exists (FEASIBILITY-12).

1. **One door into the store** — SL-C1 with the store verifier's M1 (an empty `SPARK_HOME` is set, not unset), SL-C3 (the
   lock beside the data; a writer with no lock refuses; `init` under the lock), BR-C7 = SL-C11(c) (the vendor-header cache
   under the store, through the same door), SL-C4 in its S form (the pick's four writes in an order that lists no project
   before the drawer is written, and a stop that says what landed). Closes K1, K2's visibility, K5, K6, K7, K8/K9's half-write
   answer, K14 — six "harms silently" rows against the real store. Touches `store.py` (72 anchors) in ~50 lines, `init_project.py:417`,
   `check_vendor_pins.py:102-138`, `parts.py:2002-2008`; tests: 4 new, 42 direct writes wrapped (FEASIBILITY-4), 12 mutation
   rows. M. SL-C2 (P164's mechanism) is a D layered on this door, not part of it.
2. **One reader** — SL-C8 (`store.read_json`: `utf-8-sig`, a named sentence, never a traceback; include `store.py:145`) and
   CC-C5 (`needs.requirements` reads through `design.read`; `component_name` moves to `design.py`; `needs._called` and
   `_name_after` go). Closes K11, K16, K59, K60, K61. Touches ≥ 13 read sites and 12 `component_name` call sites; W16 says the
   copies go in the same commit. S for the function, M for the sweep. Its specification is dated 2026-09-30 (FEASIBILITY-3).
3. **The batch of exact bugs with deterministic tests** — BR-C1 (+ the key side), BR-C4 (the could-not-run variant), BR-C5,
   BR-C6, SL-C7, SL-C9, SL-C10, CC-C2, CC-C7 (five), CC-C9, FB-C5, DR-7. Fourteen S items; each closes a row with one named
   sentence and one test, needs no decision, and together they are about two days. CC-C2 alone makes irrigation's chain exit
   0 for the first time (E `../diagnosis/chain-and-checks.md` C2's proof line).
4. **The silent short on the library board** — BR-C2 (the footprint carries both hints; the validator rule corrected to
   "same GPIO" — as written it refuses the S3's own `SS → A4`) with the chain verifier's MC-1 (`check_spine` prints tscircuit's
   own `source_trace_not_connected_error` beside the island). Reproduced on the library S3 with 21 LEDs by two lenses (E both
   board files). S–M; two tests, one needing the toolchain. Irrigation's committed footprint then drifts from the regenerated
   one with nothing saying so — which is rank 10's CC-C8 territory, so say it on the card.
5. **Identity and holds, in the shape sync needs** — SL-C5 (the spelling half now; "never reuse a name" only with the project
   id), SL-C6 after the M2 decision (holds derived on read, or stored with `--release`/`--forget-project`), NM-C3 (drop a need,
   clear a pick — the tombstone form is the PO's call). Closes K3, K4, K35; K3 is the row every second project of the PO's
   meets. These four invariants — identity by id, a tombstone, a conflict copy named (SL-C7, in rank 3), a digest compared
   (SL-M3) — are what any sync of P178's three levels needs before a tool is chosen (§2.2). M + M, two decisions first.
6. **The owed-facts table** — CC-C4 with the chain verifier's MC-3 decision (a `pin_order` without proof: owed, or a contract
   failure as `parts.load` enforces today), `BUILD_FACTS` and the research skeleton derived from the same table (SL-C13's
   true half, NM-C5), `_about`'s regex removed. One table, four mouths (`--need`, `--audit`, `--match`, `--requirements`);
   closes K19's width, K37, K47, K48 and gives P125/P165 their data. M; one decision first.
7. **The recorder and the gate** — DR-3 as the docs verifier reshaped it (promote the recorder that exists, bind each block to
   its command and store, classify the 42 blocks, hook `--check` into `check_commit.py` on a version change), DR-1 as a report
   line, DR-5 with the page named by its path. Closes K68, K74's scope half; lowers the docs cost of every card above and below.
   S + M + S; the cog variant only after a ten-line trial of its markers in a page an agent reads raw.
8. **Matching** — NM-C1 in two steps (the two sentences first; tokens and hits-ranked second, since it rewrites a documented
   behaviour, `tests/test_parts.py:791-797` and two recorded blocks), NM-C9, NM-C4 with the `drawer.md` step that gives the
   count a path to zero, NM-C6. Closes K33, K36, K38, K41 and the "[other words]" half of K34; the 91-entry data pass is the
   PO's time, not code. S + S + S + S–M.
9. **The rules cluster** — CC-C1 in MC-6's form (the derived half seeded by `parts.py --requirements`, the "after a build, run
   `init --force`" prose removed from three pages), CC-C3 widened to "why floating is harmless here" (the DFR0954's `SD` in
   spark's own library is the second case), MC-1 decided (zero derived rules: `ok` with `checked: 0` and the reason, or
   could-not-run). Closes K45, K46, K63's I²C half. M; ordered CC-C3 before CC-C1 for irrigation, and K40's rename before
   either (NM-C8's M6). Plant-alarm gains a red it does not have today (its amplifier's four inputs) — a true finding, said in
   advance.
10. **The decided items, in their foundations' order** — CC-C8 (P110, D PO 2026-10-05: build the kept `board.tsx`, in place,
    no `built` when it differs), then BR-C8's mechanical half (D8, the PO's "first fix": the Arduino variant from `boards.txt`,
    `pins` from the vendor header through `parse_pins`, a per-chip table; geometry owed) after BR-C3 (the schema) and BR-C11
    merged with FB-C1 (the stand-in's pins), then FB-C3 (the step from the image to the board — the journey's end, the PO's
    choice of a script or a page), then SL-C11's shelving once a `built` line has a reader. M, L, M, M. FB-C4, NM-C7, DR-6's
    density rule and the cog markers wait for their decisions (§4).

What this order leaves for part 2 or a later card, on purpose: K42, K43, K44 (features: G, the ways in, equivalents), K49's
other half (no MCU, two MCUs), K64's structural split (FEASIBILITY-2), K65's typed `origin` (the schema's business, §2.2),
K21 (by design), K62 (a one-function fix nobody proposed — §2.6).

### 2.2 The PO's question of 2026-10-10 — formats, sync libraries, techniques, rules, an editor

The question, relayed verbatim: *"maybe some new file formats or synch libraries or techinques could be used from an existing
library that does somwthing that would make the whole store synch and global and loval and project store sync and rules and
editor?"* Judged for feasibility against spark as it is (E store.py whole, the layer table, the drawer's and the history's write
rules) and the three lookups in §5.

**File formats — keep the files, add the schema.** One JSON file per record (137 files, 312 KB — FEASIBILITY-5) and one JSON
Lines file for events are already the formats text sync and git handle best: one entity per file, diffable, mergeable per
file. What is missing is not a format but a *statement* of each format: `boards.py:19` says "the contract is enforced rather
than documented", and five diagnoses found keys that are carried and read by nothing (BR-C3: `flush_edge`, `corner_radius_mm`,
`thickness_mm`, `header.pad_mm`, `mounting_holes`; FB-RC-4: `deep_sleep`, `wokwi_is_stand_in`; SL-M3: the `built` digest;
BR-C12: `footprint_module`). A **JSON Schema per kind** — part, board, drawer entry, needs, requirements, rules — is the
existing format for that statement, and it is three things at once: the key-by-key documentation BR-C3 asks for, a shape
validator, and an editor (FEASIBILITY-8: VS Code validates, completes and explains on hover from a schema mapped by a
relative path). The converter's TypeScript types could be generated from the same files (H, json-schema-to-typescript; not
checked). Cost: six schemas, M–L (H: 50–150 lines each, read off the Python checks that exist — `drawer.CHECKS`,
`needs.CHECKS`, `boards.REQUIRED_KEYS`/`PIN_ROLES`/`FORBIDDEN_KEYS`, `parts.REQUIRED_KEYS`/`CHAIN_FACTS`), plus a conformance
test that every shipped record and every fixture the Python refuses for a shape reason gets the same answer from the schema
(S), or the two drift into two statements (W16). What a schema cannot say stays in Python: `id` equals the file name, an
alias target is a pad, two `pins` keys on one GPIO, owed (absent) against broken (wrong), the git-tree refusal. Run-time
enforcement is a decision (FEASIBILITY-7): `jsonschema` is not in the standard library, so either the schema is checked in the
suite and shipped for editors while the hand checks stay the run-time contract, or spark carries a dependency, or a ~100-line
validator for the subset it uses (`type`, `required`, `enum`, `pattern`, `additionalProperties`, `minimum`) is written — the
third is the "no bloat" form and the PO's call. Settled by a spike: write the drawer-entry schema (13 fields, `drawer.py:24`,
`:71-73`) and run `jsonschema` over the copy's 110 entries — an hour.

**Sync libraries — none; the store's writes already merge, once four invariants exist.** The libraries that exist for this
(FEASIBILITY-9: `pycrdt`, compiled Yrs bindings) solve live concurrent editing of one document; #123's acts are find, create,
share, reuse by one person per store and a reviewed shared layer, and `pycrdt` would add a compiled wheel against "users
install nothing heavy" (D PO 2026-10-06). The store's own rules are already merge-friendly: a drawer write sets fields and never
deletes (last writer per field), the history is append-only and idempotent by key (a union merge), a document is addressed by
its checksum. What any sync — git, a synced folder, a future service — needs and the store lacks is exactly the store cluster
of this council: **identity by thing** (SL-C5's project id; #17's recommendation of 2026-10-06 that records and chips be named
by a checksum of their content, D PO decision 1 of that day), **a tombstone** (NM-C3; the drawer's is count 0), **a conflict
copy named** (SL-C7: the `(conflicted copy)` stem a sync client leaves), and **a digest compared on read** (SL-M3 for `built`,
K13/P148 for a project's copy of a library record). So the sync question and rank 5 are one change in disguise: do those four,
and the choice of transport is open and cheap; skip them, and every transport corrupts quietly.

**Techniques — git for the shared layer, a folder for the private one, SQLite for nothing yet.** The shared layer is a text
problem (312 KB today), review is a pull request, and git is a tool spark already requires (`gh` for `check_vendor_pins.py`,
the GitHub install); P84 was decided in that shape on 2026-10-04 — "a public repo of records that pass the contract, cloned
read-only onto the search path at a pinned commit" (E `docs/archive/2026-10-04-store-discovery.md:209-211`, §6 decision 4) — and KiCad's
libraries are the precedent the P94 read named (E #17 comment 2026-10-06T11:12). It fits the code as it is: `layers()` gains
one read-only row (`shared`, ~10 lines H), a sync step is a clone or pull at a pin (S–M), a `--contribute` export that strips
what §5.8 forbids is M. It fits the privacy rule without rewriting it: `inside_git` refuses private places inside a work tree
(FEASIBILITY-19), so the drawer, history and projects list cannot live in the shared clone — the split the design wants. The
private store stays a folder; if the person's own client syncs it (Dropbox, iCloud), SL-C7 names the conflict copies and SL-C3's
lock beside the data serialises one machine — two machines writing one synced store at the same moment is the one case nothing
covers (—; a sentence in how-it-works, not code). SQLite (`sqlite3` is in the standard library) would give transactions and
`UNIQUE` to the three small tables (projects, holds, history) at the price of `cat`/`diff`/`grep` and of being one binary blob
to any sync client — and its own page warns of exactly the background copier a synced folder is (FEASIBILITY-6). Not a
candidate until a scenario needs a transaction the S form of SL-C4 cannot give. Content addressing exists (`sources/<sha256>/`)
and `based_on.digest` is half of it for records; the missing piece is a reader, not a library.

**Rules.** `rules.json` holds two kinds of content in one file (CC-RC-1): the person's answers and a snapshot of derived facts.
The technique is to derive at the point that holds the data (MC-6: `--requirements`, or the check itself — CC-C1b) and keep
only answers in the file; the rules schema then documents the fill list K46 asks for (which nulls a person can answer, which
need a meter), and MC-2's per-entry provenance stops the file from misstating its own origin. An editor for the rules is the
same schema in VS Code; nothing else is needed.

**Editor (P160, #96).** Three editors exist or are one file away: for a person, VS Code with the schemas (FEASIBILITY-8); for an
agent, `parts.py --describe --json` and the envelope, which exist (`parts.py:1472-1537`, `outcomes.py:65-74`); for both, later, a
generated read-only page from the `--json` outputs (the 2026-10-04 discovery's recommendation, E `store-discovery.md:160-162`).
Proposal: P160's first increment is the schema set, not an application — it costs no dependency, serves both users, and is
the documentation BR-C3 owes anyway.

### 2.3 One change in disguise — the clusters (the same root cause, one card each)

- **A · one reader**: SL-C8, CC-C5, K11, K16, K59, K60, K61, and DR-4's `--fetch`-of-a-board refusal path (the argument-refusal
  route). FEASIBILITY-3.
- **B · keys nobody reads — one statement per kind**: BR-C3, BR-C6, BR-C10's shape half, BR-C12, FB-M6 (`deep_sleep` has no
  schema), NM-C5's "skeleton holds every chain fact" test, K54 (a dimension above 0), K57 (`--describe` under-declares), K65
  (`origin`). The schema set of §2.2; BR-C3's `PHYSICAL_KEYS` test ("every key a shipped record carries is read by a named
  script, or refused") generalises to every kind.
- **C · one door into the store**: SL-C1 (+M1), SL-C2, SL-C3, SL-C4 (S form), SL-M4, BR-C7 = SL-C11(c), K58's `Write`/`Edit`
  agent, P150's compiled chips. Rank 1 plus the grep-shaped test the store verifier's M4 names ("no script writes under
  `store.home()` except through `store.write_* / copy_folder / append_event / keep`").
- **D · identity for sync**: SL-C5, SL-C6 with M2, SL-C7, NM-C3, SL-M3, K13/P148. Rank 5; the §2.2 invariants.
- **E · one table of owed facts**: CC-C4, MC-3, SL-C13's `BUILD_FACTS`, NM-C5's skeleton, K48, P125 #59, P165 #102. Rank 6.
- **F · the stand-in's pins**: BR-C11 and FB-C1 (FEASIBILITY-10), FB-C5's "a scenario names a pin the stand-in knows", FB-C6's
  amendments, K32.
- **G · the rules file**: CC-C1a/b, MC-1, MC-2, MC-6, CC-C3 with MC-5, K45, K46, K63's I²C half. Rank 9.
- **H · a kept file drifts from a generated one**: CC-C8 with MC-4 (the kept `board.tsx`, in place), the kept footprint file
  (`keep_into` leaves every `*.tsx`, `check_spine.py:652-657`), K13 (a project's copy of a library record), SL-C11(d) (the shelf
  copy's digest), P148's drift report. One mechanism: a digest compared and said at `--keep`, `--audit` and `--requirements`.
- **I · the recorded page**: DR-1, DR-3, DR-5, DR-4's recorded blocks, FB-C6's retired-sentence check (the bin's
  `tools/check-current-docs.py` is the precedent, E the bin's CLAUDE.md; spark has none — E `tools/check_docs.py` read whole),
  K68, K70, K74.

### 2.4 Conflicts — where two proposals cannot both land as written

- SL-C4 (all-or-none through `.part` staging) against the store's own load-bearing wall "the history as an append-only line
  per event" (`../diagnosis/store-levels-and-holds.md` §2) and against a `needs.json` on another file system: the S form (the
  verifier's) resolves it; the L form does not.
- SL-C5's "never reuse a listed name" against an ordinary `mv` of a project (holds stranded until `--forget-project`): safe
  only with the project id — order the id first or drop that half.
- SL-C6 (`--release`) against SL-M2's option (i) (holds derived on read: nothing to release): a decision before the card.
- SL-C12 as leaned ("shrink the spec") against §5.8's promise made twice (`design.md:264-265`; `boards/firebeetle2-esp32s3.json:325`
  `private_only`): add `sources` to `PRIVATE`; a 0700 `catalog` against P178's shared direction (D).
- SL-C11(b) (shelve every project record on `--requirements`) against "proven": four of irrigation's seven records are
  placeholders (E the store verifier's run, 7/7 `shelvable`); needs SL-M3's reader (a `built` line vouches) first.
- SL-C13's digest widening against SL-M3 (no reader compares a digest): a wider number nobody reads changes no answer.
- BR-C2's validator rule as written ("an alias target is not itself a `pins` key") against the S3's own file (`A4` is a `pins`
  key, `firebeetle2-esp32s3.json:162`): the "same GPIO" rule instead.
- BR-C3's removals from the library S3 file and BR-C11's two entries against the bin's `make check` (FEASIBILITY-11): same
  commit, or the bin goes red; the bin's committed `.spark/board.json` goes stale until re-resolved.
- BR-C9's "fill the XIAO's `physical.header`" against the module's SMD package (`emit_footprint.pads` draws two flush rows of
  plated holes, `:113-118`): the `footprint_source` route is the honest one (D).
- FB-C1(c)'s `not_on_simulator` role against the facts: for both library boards every GPIO simulates under another name (E
  the FB verifier); the role would be true only for a user's generic devkit.
- FB-C4 against the PO's cut of `check_firmware.py` (D PO 2026-09-29, `066c4af`: "nothing kept that nothing uses"), against
  the 4,000-line argument ("one number mean two things", `docs/archive/2026-10-01-firmware-and-tests.md:135-139`) and against K53 (its
  mutation proof reads a scorer that over-counts): three things to settle before a line is written.
- NM-C2's mark/pick pair rule against `idea.md`'s M-before-C order and plant-alarm's file (`battery`: `have`, no pick — E):
  drop the rule.
- NM-C7 (a `count` on a need) against §5.3's two readings and against the verifier's M7 (one need per instance already yields
  `Valve1…Valve4`): a decision; the sentence in `idea.md` first.
- NM-C8's glob against rc-car (`car.requirements.json`, `remote.requirements.json`, no `requirements.json` — FEASIBILITY-11):
  the refusal must handle several files and say so, or rc-car's `--requirements` is refused with a sentence about one.
- CC-C1a (a check writes `rules.json`) against "a check is not a writer" and against CC-C3's order for irrigation (the four
  valve entries return on the first `--keep` unless the record says `holds_level` first): MC-6's form, CC-C3 before.
- CC-C1 (any form) against plant-alarm: the first seed lists the DFR0954's `BCLK`, `LRC`, `DIN`, `SD` and B13 fails all four
  (the chain verifier's MC-5) — a new red, to be said before, not found after.
- CC-C6's recommended variant (synchronise `active.json`) against its alternative (remove the file for projects with a
  requirements file) and against `boards/README.md:21` ("THE one place it is chosen") and the bin's Makefile (reads
  `active.json`): the recommended variant now, the alternative with part 2.
- CC-C8's sketch (copy the kept file into the work folder) against a hand-written `board.tsx`'s local imports (the bin's
  imports four siblings — the chain verifier's MC-4): build in place.
- DR-1 as a failing check against patch releases that change no output (0.8.1 changed two files, two lines — E `git show
  --stat 1fc0909` per the docs verifier): 44 false alarms; a report line.
- DR-3's cog markers (3 lines × 42 blocks in pages agents read raw) against the agent guide being one of those pages: a trial
  first; the existing recorder promoted either way.
- DR-6 and DR-2 both rewrite `README.md:111-158`: one card.

### 2.5 Every proposed change — keep · change · drop, what it touches, my size

Columns: **touches** names files, tests (new / rewritten), docs and the repositories reached; **size** is mine (H) with what it
rests on; **settle by** says whether a read, a spike or a decision (D) closes the open point; **kin** names the cluster (§2.3)
or the twin, **×** a conflict (§2.4).

#### Store levels and holds (`../diagnosis/store-levels-and-holds.md` C1–C13)

| change | verdict | touches | size — rests on | settle by | kin · × |
| --- | --- | --- | --- | --- | --- |
| C1 a missing `SPARK_HOME` refused; every answer names its store | keep; **change**: refuse set-but-empty too (M1); put the check where a write happens or word it to carry both sentences, since two tests expect the git refusal for a store inside a repository (`tests/test_drawer.py:214-221`, `tests/test_store.py:159-166`) | `store.home`/`_make_ready` (~8 lines), `outcomes.envelope` (+1 field), `parts._say`/`_write_lines` (+1 line); tests 3 new, 2 rewritten; `docs/guide/agents.md` envelope fields; repos: none (the bin's `make` sets no `SPARK_HOME`) | S — `store.py:46-52` read; the verifier's (a)–(c) | read (done) | C · × the git refusal's tests |
| C2 the real store written only on purpose (P164) | keep as the PO's D; **change**: the card says "closes the temp-root case; the copy-under-home case needs the flag" | `store._make_ready`, `append_event` (~10 lines); 1 test with `HOME` at a scratch folder; every agent page carries `SPARK_HOME` inline (#101's last line); repos: none | S–M — #101 body; `store.py:209-218` | D (which mechanism) | C |
| C3 one lock beside the data; a writer with no lock refuses | keep; **change**: wrap the suite's 42 direct writes in a fixture that holds `locked()` — not a suite flag (a second K2-class guard); `locked()` must `mkdir` the home or follow C1 | `store.locked`/`write_json`/`copy_folder`/`append_event` (~15 lines), `init_project.py:417` (1 line); tests 2 new + the wrap; 12 mutation rows (one per writing operation); repos: none | M — FEASIBILITY-4; the verifier's (a)–(d) | spike: add the check, run the suite (33 s) | C · × order with C1 |
| C4 an operation's writes land all or none | **drop as written** (L; breaks the append-only wall; a cross-file-system rename is not one unit); **change** to the S form: ordered writes, each recorded, a stop says what landed; `add_project` after `drawer.apply`; `shelvable` before `apply` | `parts._op_pick:2002-2008`, `drawer.apply:267-273`, `parts._drawer_answer:1751-1759` (~25 lines); tests 2 (K8, K9 fixtures) | S — those lines read; the verifier's alternative | read (done) | C · × the history wall |
| C5 a project is its folder; a vanished name is not reused | keep the spelling half (`samefile`, with the string fallback when the *listed* side is gone); the "never reuse" half **only with the id** (a `mv` strands its holds otherwise); the id in `.spark/project.json` and `projects.json` as `{name: {folder, id}}` | `store.project_name`/`add_project` (~10 lines), `init_project.PROJECT_TEMPLATE` (+id), every reader of `projects()`; tests 3 (one skipped on a case-sensitive file system, said) | S + M — `store.py:247-269`; the verifier's (a)–(c) | read; the id is a D (a P178 handle) | D · × moved projects |
| C6 holds listed and released | keep after M2's D; **change**: the command goes into the problem's `sentence` or K56 is fixed with it (the plain refusal prints no `fix`, `parts.py:2182`); a key and a `held by` column in `--drawer` | `drawer.listing`, `parts._op_drawer`, `OPERATIONS` +2 rows, `needs._how_to_free:250-257`, `parts.audit`; `commands/idea.md:3` +2 patterns, `:96-98` prose; tests 3 + routes (FEASIBILITY-13) | M — `OPERATIONS` read; the verifier's (a)–(c) | D (M2: derive on read, or stored) | D · × M2 (i) |
| C7 reads refuse what writes refuse; labels in one form | keep; nothing breaks today (0 non-plain stems in every layer and project — the verifier's E) | `drawer.entries:87-92`, `store.records:84-91` (+2 lines each), `drawer.clean`, `store.slug` (NFC/NFKD); tests 2 + `test_drawer.py:242` rewritten; 1 mutation row | S — those lines read | read (done) | D (a conflict copy named is a sync invariant) |
| C8 one reader; no store problem is a traceback | keep; **change**: catch `UnicodeDecodeError` and the new `StoreProblem` by name, not every `ValueError` (a traceback is *where* for an agent); include `store.py:145`; **fold with CC-C5** into one `read_json` used by every reader in FEASIBILITY-3 | ≥ 13 read sites (`parts.py` 8, `drawer.py` 1, `store.py` 1, `needs.py` 2, `check_vendor_pins.py` 1) + `design.read` + `boards._read_json`; `parts.main:2202`; tests 3; anchors near those lines (parts.py carries 266) | S the function, M the sweep — my grep (41 sites) and the arch doc's item 3 | read (done) | A |
| C9 `--fetch` names every URL it could not keep | keep | `parts._download:1277-1282`, `fetch_documents:1259-1265`, `_op_fetch` (~10 lines); 1 test; `commands/research.md:44`, `agents/parts-researcher.md:52` say what exit 1 means | S | read (done) | — |
| C10 one layer, one count | keep | `parts.catalog_records:879` → the one walk, or `audit` (~5 lines); 1 test | S | read (done) | — |
| C11 a record has one home that is the store | keep the direction; **split**: (a) `promote` from a project → the shelf with `based_on`, the `LIBRARY` target deleted (`parts.py:1296`, `:1865` already says the library changes by PR) S; (b) `--requirements` shelves the project's own **only when a `built` line vouches** — after SL-M3's reader (four of irrigation's seven are placeholders) M; (c) = BR-C7 S; (d) `--audit` compares `based_on.digest` and a project copy against the library (P148) M; (e) `datasheet-reader` loses `Write`/`Edit` only once `--fact-set` can set `documents.*.title`/`version`, `verified`, `source` (—); six literal paths → one sentence S | `parts.promote`/`shelve`/`audit`, `needs.py:604`, `check_vendor_pins.cached_header`, `agents/datasheet-reader.md:5`, `agents/parts-researcher.md:53,58`, `commands/setup.md:11,51`, `commands/drawer.md:10`, `commands/research.md:105`; tests ≥ 5 + `test_docs` gains #23's grep; repos: irrigation is the one whose records would be shelved | L as one card; S+M+S+M+S split — the verifier's `shelvable` run (E), FEASIBILITY-14 | (e) by a read of `--fact-set`'s fields; (b) by SL-M3 | C, H · × placeholders on the shelf |
| C12 spec and code agree on privacy; the no-`fcntl` case said; a fetch cap | **change**: add `sources` to `PRIVATE` (§5.8 twice), chmod the place not `home()`; `catalog`/`downloads` a D; the stderr line; `FETCH_MAX_BYTES` from the largest kept document (— not measured) | `store.PRIVATE:96`, `_make_ready:217`, `locked`, `fetch:345-361` (~10 lines); tests 2; `design.md` §5.1 one sentence | S | D (catalog 0700 vs P178) | × P178's shared layer |
| C13 the `built` line vouches for what the chain reads | **drop the digest half** until a reader exists (SL-M3: nothing compares a digest — `grep '\["digest"\]'` → nothing, the verifier's E); keep `note_built`'s sentence and `check_spine.py:625-629` printing it | `parts.note_built:923-925`, `check_spine.py:625-629`; 1 test; `BUILD_FACTS` derived from CC-C4's table | S | read (done) | E, SL-M3 |

#### Board records (`../diagnosis/board-records.md` C1–C12)

| change | verdict | touches | size — rests on | settle by | kin · × |
| --- | --- | --- | --- | --- | --- |
| C1 a bare-number pad label is refused | keep; **change**: the `pins` key side too (M6), both of tscircuit's regexes | `boards.validate:343-350` (~8 lines); tests 3, a fixture under `tests/data/`; `boards/README.md` one sentence; repos: the bin's `make check` validates the library S3 (no numeric label) — green | S — the verifier's probe (E) | read (done) | — |
| C2 `pad_aliases` reaches the footprint | keep the hint half (one line); **change** the validator rule to "an alias target that is also a key maps to the same GPIO"; do MC-1 (print tscircuit's own error) before any reconstructed sentence | `emit_footprint.render:178` (+ aliases), `boards.validate` (~5 lines), `check_spine.py:430-441` (reorder ~6); tests 2 (+1 toolchain); repos: irrigation's committed footprint drifts (said, cluster H) | S–M — the verifier's three-hole probe (E) | read (done) | H, CC-MC-1 · × the rule as written |
| C3 the `physical` schema written where it is enforced; an unread key refused | keep as the schema set's first instance (§2.2); **change**: five unread keys, not three (`thickness_mm`, `header.pad_mm`); mounting holes a D (emitting them changes every regenerated footprint and adds four drills to `check_footprints`); the library file's removals land with the bin in mind | `boards.py` (`PHYSICAL_KEYS` + loop ~15), `boards/README.md` (+ P127's rewrite), `boards/firebeetle2-esp32s3.json`; tests 2 + a docs test; repos: bin (`make check`), irrigation (footprint regen if holes), bin's `.spark/board.json` stale | M — the verifier's grep (five keys) | D (holes); read for the rest | B · × bin same-commit |
| C4 `emit_footprint.py --json` prints JSON on every path | keep the could-not-run variant (removes a path) | `emit_footprint.main:229-231` (3 lines); `tests/test_json_contracts.py:142` second case | S | read (done) | B (K55/K57) |
| C5 the header says what the drawing states | keep | `render:162-163` (2 lines); 1 test | S | read (done) | — |
| C6 one comment-key rule | keep as consistency; the `//jtag` refusal text is the real fault | `boards.py:347`, `:363`, `emit_footprint.py:128` (one helper); 1 test | S | read (done) | B |
| C7 the vendor-header cache lives in the store | keep; **change**: name the writer (through the store's door; a cache is not private, so no git refusal) and the fallback order for the bin's `--offline` (library copies read-only) | `check_vendor_pins.cached_header:102-112`, `:137-138` (~8 lines, `import store`); 1 test (P10's stays); repos: bin `Makefile:220,223` — green with the fallback | S — the file read whole | read (done) | C (= SL-C11 c) |
| C8 a board record from a drawer entry | keep as the decided item (D8); **order after** C3, C9, C11+FB-C1, C7; **split**: the mechanical half (variant from `boards.txt`, `pins` by `parse_pins`, a per-chip table with a test that it agrees with both shipped boards) M; the pick-side change (no `reused` for an unfiled board) a D; geometry owed and named | `OPERATIONS` +1 row, a new module (~150 lines H), `data/<chips>.json` (new), `check_vendor_pins.fetch_variant_header` reused, `commands/research.md` board flow, `how-it-works.md` five steps retired; `allowed-tools` + routes; tests 2 + the chip-table test | L — the diagnosis's `boards.txt` fetch (E: 3 of 4 unfiled boards named) | spike: `parse_pins` over the cached C6 header against round 0's record (minutes) | B, F, C7 · × the by-design pick |
| C9 every stop from one rule; `--for-fab` requires geometry | keep; **change** both spellings (M5: `parts.py:1920`, `needs.py:511-512`); the XIAO's data is a D (`footprint_source`, not through-hole rows) | `boards.footprint_stop` → `chain_stops`, `parts.STOPS_AT_FOOTPRINT`, `needs._board_problems`, `init_project.py:476`, the `--list`/`--match`/`--audit` printers; tests 2; repos: bin (`--for-fab` on the S3, green), plant-alarm (two stops printed) | M | D (XIAO route) | × SMD module |
| C10 `function` on boards, validated | keep; **change**: the drawer slot exists and is read (M4) — decide "SKU fact → the record, this piece → the entry"; whether a need the board serves is *picked* is a D | `boards.validate` (+1 call), both board files (+`function` with sources), `boards/README.md`; tests 3; repos: none run `--match` | M — the sources are the work | D | B, NM-C4 |
| C11 `pins` checked against the stand-in | keep, **merged with FB-C1**: a registry copy under `data/` with its version; the rule "every `pins` key, mapped as `mapping.ts:96,108` maps it, is a pin of `wokwi_part_type`" (covers M7); the S3 file gains `"TX": "TX", "RX": "RX"` | `boards.validate` (~15 lines), `data/wokwi-parts.json` (new, from `@wokwi/diagram-lint` 0.1.1), the S3 file; tests 2; repos: bin's converter copy merges `wokwi_power_pins` last (green), bin `--validate` needs the two entries in the same commit | S–M — FEASIBILITY-10 | the FB verifier's runs (E) | F · × FB-C1(c) |
| C12 remove `footprint_module` | keep (a removal) with C9 | `REQUIRED_FOR_FAB`, 2 board files, `lib/board.ts:48`, `tests/test_boards.py:54,184,215,250`, `docs/guide/agents.md:456`, `boards/README.md:71` | S | read (done) | B |

#### Needs, matching and the vocabulary (`../diagnosis/needs-matching-vocabulary.md` C1–C9)

| change | verdict | touches | size — rests on | settle by | kin · × |
| --- | --- | --- | --- | --- | --- |
| C1 one matcher: `--need` reads `function.what` and the drawer, says which words missed | keep in **two steps**: (i) keep the AND, add "which word missed" and "the drawer and `function` are not searched" (S); (ii) tokens not substrings (M5 — the one-letter word `v` would flood), hits-ranked, one `words_hit` for both matchers (M): it rewrites a documented behaviour (`parts.py:1334`, `tests/test_parts.py:791-797`, `journey.md:524,533`, five pages that send agents to `--need`) | `parts._matches:1326-1329`, `need`, `catalog_matches`, `needs._what_matches:127-131`; tests 3 + 1 rewritten; 2 recorded blocks re-recorded | S then M — the verifier's alternative | read (done) | NM-C9, NM-M2 · × documented AND |
| C2 the pick says what the match knew; `--needs` shows the pick | keep the note (with the verb — M1: a motor driver picked for `sense` passes silently today) and the `--needs` line; **drop the pair rule** (it refuses `idea.md`'s M-before-C and plant-alarm's file); a `fit` mark is a D (M4) | `needs.plan_pick` (+ one `candidates()` call per picked need — it parses every record per need, `needs.py:151-184`; measure the pick's time), `parts._op_needs:1940-1946`; tests 3; `commands/idea.md` M step | S–M | read; D (a fit mark) | × the pair rule |
| C3 a need can be dropped, a pick cleared | keep; **change**: the tombstone form (`dropped: true`) is the sync-friendly one — a D; the history keeps the old need id (say so); a mistyped empty id told from a clearing; extract `_reserve` (a refactor: two copies to one) | `needs.plan_set:75-103`, `plan_pick:212-292` (+~40 lines), `CHECKS`; `commands/idea.md:24-25`; tests 4 inside the set-only discipline (`tests/test_needs.py:53-201`) | M — those lines read; FEASIBILITY-18 | D (tombstone or removal) | D |
| C4 every answer over the drawer says how many entries it could not look at | keep; **add** the `commands/drawer.md` step (M8) or the count has no path to zero; the 91-entry pass is the PO's time | `parts._op_match`/`_op_audit`/`_op_drawer` (+~15 lines), `drawer.listing` (+`function`); `commands/drawer.md` +1 paragraph; tests 3 | S code | read (done) | BR-C10, P157 |
| C5 the skeleton carries every chain fact; research ends with `--audit` | keep; **change** the diagnosability line (M3: `--validate` is silent on a null `simulation` and `function` — `parts.py:82`, `:483-485`); derive the skeleton's keys from the owed-facts table (cluster E) | `parts.skeleton:1354-1378` (+3 keys), a set-inclusion test, `commands/research.md` §4, `skills/spark-design/references/part-data.md`, `agents/parts-researcher.md` | S | read (done) | E |
| C6 the cut lists its words and ids | keep; **change**: cap ids per word with "+n" (ids per word are unbounded once the 91 carry functions) | `parts.py:1955-1969` (~15 lines); tests 1 (+ the existing cap test) | S–M | read (done) | NM-C9 · × the 4 KB budget |
| C7 a need says how many the design uses | **hold** for the D; M7 first (one need per instance already yields `Valve1…Valve4`, `needs.py:484`) — one sentence in `idea.md` | if made: `needs.CHECKS`/`plan_pick:297`/`_merge_parts`, `tests/test_needs.py:141-146` flips, `idea.md:37`, §5.3 | M | D | × §5.3's two readings |
| C8 `--requirements` refuses a differently named file | keep after M6 (`git mv` in irrigation — the project owner's change; DIARY/PLAN name the old file); **change**: the glob meets rc-car's two files — handle "several" and "both exist and differ" | `needs.requirements:511-519` (+~8 lines); tests 2; repos: irrigation (rename), rc-car (refused until a decision) | S — FEASIBILITY-11 | read (done) | CC-C6/K49 · × rc-car |
| C9 the store's words shown where a need is written | keep; **add** M2's "one word more" case | `parts._op_match` (+~6 lines), `commands/idea.md` S step (+2 sentences); 1 test | S | read (done) | NM-C1 |

#### Chain and checks (`../diagnosis/chain-and-checks.md` C1–C9)

| change | verdict | touches | size — rests on | settle by | kin · × |
| --- | --- | --- | --- | --- | --- |
| C1 the derived half of `rules.json` re-seeded | **change** to MC-6: seed at `parts.py --requirements` (already a writer, holds picks and records); remove "after a build, run `init --force`" from `commands/init.md:36-42`, `README.md:155`, `docs/guide/journey.md:717-722`; C1b (derive at check time) as the direction, carrying MC-1's D; MC-2's per-entry provenance | `needs.requirements` (+ `init_project.rules_for`/`merged` call), `init_project.merged:296-302`, `compare_design.py:254-259`, `check_physics.py:471-478` (sentences); tests 2; repos: irrigation (its four entries re-seed unless CC-C3 first; `needs.requirements` reads only `requirements.json` while `design_in` globs — K40 first), plant-alarm (a new red: MC-5), bin (hand list, unaffected in MC-6's form) | M (MC-6) / L (C1b) — FEASIBILITY-21 | D (MC-1); a one-minute read of the import graph | G · × CC-C3's order, K40, MC-5 |
| C2 a declared signal is reported, not refused; a non-note stderr line is could-not-run | keep; **change**: a shared `NOTE_PREFIX` constant `check_spine` imports (a tested contract), "left for you to wire"; say that `built` is then recorded for a board with a dangling pin | `emit_board.py:1125-1130`, `check_spine.py:374-375` (+~8 lines), `docs/guide/how-it-works.md:37`, `commands/build.md:41-43`; tests 2 (`tests/test_routes.py:151` stays); repos: irrigation exits 0 for the first time | S–M | read (done) | — |
| C3 a record says an input defines its own level | **change**: widen to "why floating is harmless here" (a load, a module-side pull, gated by another pin) or a module-side pull the seed reads — MC-5: spark's own `parts/max98357a-dfr0954.json` (`SD`) is the second case and plant-alarm wires it; a fact with `verified`/`source`; a per-entry note (MC-2) | `parts.validate` (a need key), `init_project.declared_inputs:81-101`, `compare_design.py:209-211`, spark's amplifier record, irrigation's DFR0457 record (the owner's edit); tests 3 | M | read (done) | G · × order before C1 |
| C4 one table says what each owed fact does to the chain | keep; **change**: MC-3's D first; the `pin_order_proof` row is `("parts", stops — the loader refuses)` (E the verifier's run); `_about`'s regex goes; `BUILD_FACTS` and the skeleton read the same table | `parts.CHAIN_FACTS:98` → a table, `owes`/`_about`/`broken_problems:101-131`, `needs.LAYOUT_FACTS:327`/`:505`, `parts.py:1631`, `:1518`, the `--audit`/`--match` printers; tests 2 (+ the per-fact `check_spine.run` test); recorded `--match`/`--audit`/`--need` blocks | M | D (MC-3) | E · × `test_needs` policy pins |
| C5 one reader, one namer | keep; **fold** `_name_after` (M7 of that verifier: same transform, nothing pins agreement); = SL-C8's twin | `design.py` (+`component_name` ~15 lines), `emit_board.component_name` → alias, `needs.py:430-432` deleted, `:511-519` → `design.read`; tests 3 | S | read (done) | A |
| C6 the board changes in one place | keep the recommended variant now (`_op_requirements` writes `active.json`, +~6 lines, 1 test); the alternative with part 2; `boards/README.md:21` gains a qualifier either way | `parts._op_requirements:2070-2109`, `boards/README.md:21`; repos: bin reads `active.json` — safe under both | S | read (done) | K49 · × part 2 |
| C7 five small contract fixes | keep all five; K52 also could-not-run (MC-8), K63 the *refuse* variant with `idea.md:13-15` reordered, K50's hyphen stays H | `boards.py:476`, `parts.py:101-104`, `:658-660`, `:1903`, `:2112-2126`, `:517`, `needs.py:360-362`, `sim_project.py:92-97`; tests 5 | S each (one card) | read (done) | B (K54) |
| C8 `--keep` builds the kept `board.tsx` | keep (D PO 2026-10-05, #44); **change**: build in place (MC-4: a hand-written file's imports are not in the work folder), the work folder for the diff only; no `built` when it differs, said; flip `tests/test_check_spine.py:316-331` | `check_spine.run`/`keep_into`/`main` (~40 lines), `commands/build.md:72-74`; tests 2 flipped + 2 new; repos: irrigation's `dist/` becomes its board's build and records no `built` until regenerated (13 lines differ) | M | read (done) | H · × MC-4 |
| C9 ★C7's note on its own line in every outcome | keep | `check_spine.render:554` (1 line); the test at `:1085-1098` extended | S | read (done) | — |

#### Firmware and bench (`../diagnosis/firmware-and-bench.md` C1–C6)

| change | verdict | touches | size — rests on | settle by | kin · × |
| --- | --- | --- | --- | --- | --- |
| C1 the stand-in's pins as a board fact read first | **change**, merged with BR-C11: data first — document and rename the override (`wokwi_power_pins` carries renames and `null` today, undocumented, typed without `null`), validate its keys and values; the converter picks a label the part knows for a GPIO with several labels (M1, `mapping.ts:96`); **drop** (c)'s role for library boards (false reason); keep (d) as one pinned string until the converter has `--json` (M8) | `boards.validate`, the S3 file, `boards/README.md:95-97` and the S3 note amended (M9), `mapping.ts` + `bundle.sh` + the sha pin at `tests/test_check_spine.py:850` (the bundle is the cost), `check_spine.py:216` (+1 string); tests 2 + a converter test | M — FEASIBILITY-10 | the verifier's runs (E) | F · × (c) |
| C2 `flash_image.py` refuses an interpreter for another chip | keep the 16-byte read; **change**: in `check_spine`'s simulation stage where the board and `--firmware` meet (`:473`, `:582-583`), `--chip` optional for the standalone case; the literal 9 is E, 13 must be read from esptool ≥ 4's `targets/` (the PO's 3.3 has no final C6 class) | `flash_image.py` (+~15 lines), `check_spine.py`; tests 2 (fixtures exist in `<scratch>`) | S | a read of a newer esptool's source (not made) | FB-M4 · × a `--project` default from a folder with only `firmware/` |
| C3 the step from the image to the board | keep as the PO's choice (a script M, a page S); **add**: `flasher` needs a minimum esptool version (M5), the write offset per chip and the 4 MB image on a 16 MB N16R8 are bench facts (—) | `data/tools.json` (+2 entries), `flash.py` (new, ~120 lines H), `docs/guide/journey.md` Bench, `README.md:77`, `how-it-works.md` tools table; tests with fake `esptool`/`mpremote` on PATH | M — FEASIBILITY-15 | D (script or page); the bench | — |
| C4 a sixth check: the firmware against the pin map | **hold** for three decisions: the cut (`066c4af`, D PO 2026-09-29), the 4,000-line "one number two things", K53 first (FEASIBILITY-20); if made: conventions `firmware/pins.py`+`main.py`, "has" = `pins` ∪ `pin_roles[*].gpio` (the XIAO's GPIO15), FB-M7's header into `pins.py` first (S) | `check_all` (+1 check), a new module (~250 lines H), tests + a mutation table; repos: irrigation gains a second FAIL (recorded outputs change), the bin "not asked for" (`config.py`) | L | D ×3 | × the cut, K53 |
| C5 a scenario measured against the pin map | keep as a note; **add**: an `expect-pin` must name a pin the stand-in knows | `sim_project` (+~20 lines); tests 2 | S | read (done) | F |
| C6 the documents follow the code | **change**: amend, do not delete true sentences (M9: the superset claim is true of GPIOs); the retired-sentence check does not exist in spark (`check_docs.py` read whole) — propose it as a new S check (§2.6) | `boards/README.md:93-97`, the S3 note, `journey.md` Bench, `README.md:77`, `how-it-works.md:216-229` | S | read (done) | I |

#### Docs and recorded outputs (`../diagnosis/docs-and-recorded-outputs.md` Changes 1–7)

| change | verdict | touches | size — rests on | settle by | kin · × |
| --- | --- | --- | --- | --- | --- |
| 1 the gate counts outputs behind the shipped version | keep as a **report line**, never failing (44 false alarms per patch release; `developing.md:103` is a dated record by its own words) | `check_docs.py` (+1 function ~10 lines), 1 test, 1 row in `tests/mutations/p104-docs.json` | S | read (done) | I |
| 2 the README block ends where a shell can finish it; the gate runs it | keep; the needs file inside the project (the P172 leak count); a recorded ```` ```text ```` output and the tally's refusal shown beside the sentence (M8) | `README.md:117-132`, `check_docs.py:157`; the gate gains four subprocesses (~1–2 s on a 5.5 s gate — H from the verifier's timing) | S | read (done) | I · × DR-6 (one card) |
| 3 one recorder at each release; drift fails a check | **change**: promote the recorder and comparer that exist (M1) with a per-block binding; classify the 42 blocks (M2: 8 with no `sh` block above; M3: live-board and `gh`-state blocks are recorded-only); hook `--check` into `check_commit.py` on a version change (M4, FEASIBILITY-16); cog only after a ten-line trial of its markers in a raw page | `tools/record_docs.py` (promoted), `check_commit.py` (+ a version branch ~10 lines), the 42 notes gain a class; tests: redaction unit test, a `--check` test | L → S + M + M split | a read of `.superpowers/…/record-journey.sh` (176 lines — not opened by me); the cog trial | I · × cog markers |
| 4 the own-board route recorded; three facts written where the steps are | keep minus the half already on the page (`how-it-works.md:172` names `vendor.arduino_variant`); `--fetch <board>` refused through the argument-refusal path, exit 2; `runs:` blocks offline only (the live vendor check writes the plugin's cache — BR-C7 first) | `how-it-works.md` "Your own dev board" (or `boards/README.md` after P127), `check_vendor_pins.py:61-63` (the 404 sentence), `parts.py:1670-1680`; tests 2 + 2 `runs:` blocks | M | read (done) | BR-C3, BR-C7 |
| 5 the gate reads the pages agents follow | keep; **add** M7 (`path.relative_to(root)` — three `SKILL.md`s and two `README.md`s would be one name); do not share `routes()`'s sibling Makefiles | `check_docs.py:30-33`, `:187`; `tests/test_orphans.py:27-36` shares a list minus the Makefiles; `developing.md:157`, `readme-design.md:92`; tests 1 + 1 mutation row | S — FEASIBILITY-22 | read (done) | I |
| 6 density and long lines | **drop** the long-line count (README's are table rows); the 231 → ~120 cut is a D and overlaps Change 2 — one card | `README.md:111-158`; a measure in `check_docs.py` only if the PO makes "about 120" a rule | S / M | D | × DR-2 |
| 7 one sentence on what spark has built | keep; **add** the per-store fact (the library holds 8; `--list` adds the person's store: 13 on the copy) | `README.md` one sentence | S | read (done) | — |

### 2.6 Missing — changes nobody proposed, from this lens

- **MISSING-1 · The schema set** (§2.2): six schema files, a conformance test against the Python checks, the VS Code mapping,
  and the "every key a shipped record carries is read by a named script or refused" test for every kind — the one mechanism
  under cluster B. M–L; the run-time enforcement is the D in §4.
- **MISSING-2 · A `writable` column in the layer table** (FEASIBILITY-14): ~10 lines in `store.layers`, the specified home
  for "where a record goes"; SL-C11(a) and (b) read it instead of each writer choosing.
- **MISSING-3 · K53's fix** (FEASIBILITY-20): `tools/mutate.py` compiles the mutated file and scores a `SyntaxError` as
  REFUSED, not CAUGHT (~10 lines, 1 test); before any new mutation table is trusted.
- **MISSING-4 · A grep-shaped test that no script writes under the plugin folder or outside `store.home()` except through
  the store's door** (the store verifier's M4): covers K14, `promote`'s `shutil` (`parts.py:1292`), compiled chips (P150) in
  one test; S.
- **MISSING-5 · K62 as one function**: `cost.py:110` splits a transcript on `str.splitlines()` while `store.events` already
  splits bytes on `\n` for the same reason (`store.py:284-286`): one `lines_of(bytes)` used by both; S, 1 test, 1 row.
- **MISSING-6 · K55 and K57 together**: one test that runs every `OPERATIONS` row against its declared `data` keys and asserts
  the envelope's `problems` carry what the text prints (CONFLICT lines, open facts); `tools.py --json` (#23). S–M; it is the
  contract the agent reads (§6.4.3) and the editor would read (P160).
- **MISSING-7 · The sync-case sentence**: `docs/guide/how-it-works.md` says in one paragraph what the store tolerates (a synced
  folder: conflict copies named by SL-C7) and what it does not (two machines writing at one moment) — S, prose, after rank 1.
- **MISSING-8 · A retired-sentence check in spark** (FB-C6's test as written does not exist): the bin's
  `tools/check-current-docs.py` shape, over the guides and the agent pages; S.
- **MISSING-9 · The kept footprint's drift** (cluster H): `keep_into` leaves every `*.tsx`; irrigation's committed
  `FireBeetle2Esp32S3.tsx` already differs from the generator's (BR-C2 changes it again). CC-C8's stage line names the board
  file only; one more line names the footprint. S, inside CC-C8.
- **MISSING-10 · An anchor-exposure line per change**: `tools/mutate.py --near <file>` listing the rows anchored in a file, so a
  card's Done line can say how many it re-anchored (FEASIBILITY-2 makes this the hidden cost of every move). S; a tool for the
  maintainer, not the product.

## 3. What I could not check, and why

- No proposed change was run as a spike. Every size is an estimate resting on the lines read, the diagnoses' and verifiers'
  runs (cited where used) and the counts in §1; the one spike that would recalibrate most (SL-C3's writer check against the
  42 direct writes) is a 33 s suite run away and was not made, by the rule that this lens changes nothing.
- The real store was not run against; every count of the store is the copy's as of the `cp -R` on 2026-10-10.
- The bin's `make check` against a changed library file was not run: `boards.py --resolve` writes the bin's `.spark/board.json`,
  which the rules forbid; FEASIBILITY-11 is read from the Makefile and the folder listings.
- The `.superpowers/` recorder scripts were not opened (the docs verifier's M1 is cited as its E); whether they promote in an
  hour or a day is —.
- `jsonschema`'s current dependency set (`referencing`, `rpds-py`) is H from my knowledge; the installed 4.2.1's is E. Whether a
  hobbyist's Python carries any version is —.
- esptool's `IMAGE_CHIP_ID` for the final ESP32-C6 (13 in the FB diagnosis) stays H; the installed 3.3 has only a beta class (E
  the FB verifier); a newer esptool's `targets/` was not read.
- cog's comment-marker behaviour and how a raw page reads with 126 marker lines: not tried.
- Whether the PO's store is in a synced folder today (Dropbox, iCloud): — (not asked; it decides how much §2.2's tolerance
  sentence matters now).
- The import graph for MC-6 (`needs` calling `init_project.rules_for`): read, not run; a cycle would show on the first import.
- The chain's build time is the other lenses' measurement (6–10 s); my runs built nothing.
- Whether `candidates()` per picked need (NM-C2) slows a pick noticeably on 110 entries: not measured.
- rc-car and spark-quickstart were read from folder listings only; which spark commands they run is —.

## 4. Questions for the decider

Each: question · what it decides.

1. Holds — derived from every listed project's `needs.json` on read, or stored in `used_in` with `--release` and
   `--forget-project` (the store verifier's M2)? · decides SL-C5's second half, SL-C6's existence, and whether K3's way out is a
   command or nothing.
2. The real store's guard — the temp-root rule alone, or `SPARK_STORE=real` set once in your shell? · decides SL-C2's card
   and one line in your shell forever.
3. A `pin_order` without its proof — an owed fact (buildable, warned, marked — your #102 words) or a contract failure (as
   `parts.load` refuses today)? · decides CC-C4's table, `--requirements`' refusal list and what `--audit` calls the 17 catalog
   records.
4. The schema set — checked in the suite and shipped for editors only (no dependency), a `jsonschema` dependency, or a small
   validator of our own? · decides MISSING-1's shape, how BR-C3's documentation is written, and P160's first increment.
5. The sync direction — the shared layer as a git repository of records cloned at a pin, the private store a plain folder,
   no database and no CRDT library (my proposal in §2.2)? · decides whether SQLite and `pycrdt` leave the table and whether
   rank 5's four invariants are built in the shape sync needs (the project id, a tombstone that stays in the file).
6. A quantity on a need — `count`, or one need per instance (already yields `Valve1…Valve4`)? · decides NM-C7 and one
   sentence in `idea.md`.
7. The XIAO — header geometry drawn as plated holes, or a `footprint_source` pointing at Seeed's converted footprint? ·
   decides BR-C9's data half and whether plant-alarm's board can ever build.
8. The board selection — `--requirements` writes `active.json` now (two statements kept in step), or `active.json` goes for
   projects with a requirements file (part 2)? · decides CC-C6 and the qualifier in `boards/README.md:21` and the bin's
   CLAUDE.md.
9. The flash step — a script (`flash.py`, composed from the record and the tools list) or a page with the two commands? ·
   decides FB-C3's size and whether P100's rounds can end in firmware that runs before P79 is designed.
10. Your "first fix" (D8, the board record from the DFRobot orders) — accept that its mechanical half lands after the schema,
    the stand-in check and the cache move (rank 10's order), with geometry owed and named? · decides the order of the board
    cluster against your words.
11. The recorder — promote the one on disk, or cog? And does `check_commit.py` gain a version-change branch? · decides DR-3's
    mechanism and whether DoD 10 stays prose.
12. Zero derived rules — `rules-vs-netlist` answers `ok` with `checked: 0` and why, or stays could-not-run for ever on a
    sensor-only board (MC-1)? · decides K46's steady state and CC-C1b's shape.
13. The catalog's modes — private (0700, as §5.1 says) or readable (as a shared layer wants)? · decides SL-C12's tuple.
14. A MicroPython fake inside spark's 4,000-line idea, or a separate package? · decides whether FB-C4 is spark's at all.

## 5. Searches

Three lookups, each named by the decision it served.

- Fetch, read-only: `https://www.sqlite.org/howtocorrupt.html` (2026-10-10) · decision: whether SQLite is a candidate backing
  for a store that may live in a synced folder (P178) · **used** — FEASIBILITY-6 (§2.1 network-filesystem locking; §1.2
  background copies mid-transaction; nothing about cloud-sync folders by name).
- Web search, verbatim: `Python CRDT library JSON documents sync pycrdt automerge-py install wheel` (2026-10-10) · decision:
  what "sync libraries" exist for Python JSON documents and what they weigh · **used** — FEASIBILITY-9 (`pycrdt`: Yrs
  bindings, Text/Array/Map, manylinux wheels on pypi.org; no Python automerge in the results).
- Fetch, read-only: `https://code.visualstudio.com/docs/languages/json` (2026-10-10) · decision: whether an editor for the
  records comes free with a schema file (the PO's "editor") · **used** — FEASIBILITY-8 (`json.schemas` with `fileMatch` and a
  relative path; validation, completion and hover from the schema).

No Espressif-docs query, no other web lookup. The `jsonschema` dependency facts are from the installed package's metadata
(E) and my knowledge (H); the git-as-transport precedent is #17's comment of 2026-10-06 (E), not a search.
