# Store and simulation scenarios — P158 part 1, council lens

Written 2026-10-10 by the store-and-simulation-scenarios lens, against spark 0.8.1 (main `a8aa34d`, `git log -1` →
`a8aa34d 2026-10-09 Merge pull request #122 from xmejkal/release-0.8.1`). The PO's emphasis of 2026-10-10, verbatim:
*"Mostlu e need to be able to have the basic globsal vs local store, to be able to create search for and update and copy
or share the store things, the boards for sure, maybe we should also add how exactly to replace a board or a module in the
simulation, so wokwi uses the closest board or maybe we can create one"* and *"maybe some new file formats or synch
libraries or techinques could be used from an existing library that does somwthing that would make the whole store synch
and global and loval and project store sync and rules and editor?"* Read as four readings: (1) a shared online store vs
the local store; (2) create, search, update, copy and share records — boards first; (3) how a board or a module is
replaced in the simulation; (4) what existing format, sync library or technique could carry it.

**How this was made.** Read: the catalogue, the six diagnoses and their verifications, the seven other council reports,
the store design and discovery, the 2026-09-30 architecture, the cards #17, #22, #23, #96, #99, #101, #114, #118, #119,
#123 (`gh issue view`, read-only), and spark's `scripts/store.py`, `parts.py`, `boards.py`, `sim_project.py`, the
converter's `lib/board.ts`, `lib/mapping.ts`, `cli.ts`, both board files, `boards/README.md`, `docs/guide/how-it-works.md`,
`commands/build.md`. Runs: on a copy of the PO's store (`cp -R` to `<scratch>/store`, 2026-10-10 17:2x) with `SPARK_HOME`,
`HOME` and `TMPDIR` as three separate words on every command; `env | grep SPARK_HOME` under the prefix printed the scratch
path once, first. Scratch projects `projX` (a skeleton) and `projY` (a copied board file) live under `<scratch>`. The real
store was neither run against nor written; nothing was written under spark but this file. Tags: **E** a pointer, a
command and its output, a card, a URL with its date; **H** a claim with its source; **D** a decision (who, when); **—**
unknown. Agreement with another lens is cited, not restated.

A note on method, E: the lens folder held an earlier, unfinished run of this lens (13:15–13:20, its own store copy with
two scratch projects listed, no report). My `cp -R` into the existing `store/` nested the fresh copy one level down, so I
started over in a fresh folder; the fresh copy's `projects.json` lists the five real projects and none of the earlier
run's, so that run's writes stayed in its scratch. Nothing of it is used here.

## 1. Findings

Each: id · claim · tag · pointer · supports only.

### What exists today, and where it stalls

- **STORE-1 · Boards have no store at all: a board record lives in one project's `boards/` or in the plugin's `boards/`,
  and nowhere a second project can find it.** `store.layers()` adds the shelf only for kind `parts` and the catalog only
  for `parts` with drafts; boards are read from `[project, library]`. A board file in `projY/boards/` was listed from
  `projY` (`* myboard-s3 (project)`) and not from `projX`, whose `--list` showed the two library boards only. · E ·
  `scripts/store.py:71-81` (`:78` `if kind == "parts"`, `:80` the same); `scripts/boards.py:38` (`LIBRARY`), `:212-214`
  (`store.records("boards", LIBRARY, project, …)`); the two `boards.py --list` runs. · supports only: for boards, "local
  store" does not exist — "global" is the plugin (written by the maintainer) and "local" is one project; for parts it
  exists as the shelf and the catalog.

- **STORE-2 · The one create verb accepts a board and writes the wrong thing, silently.** `parts.py --skeleton
  firebeetle2-esp32c6 --kind board --vendor dfrobot --project projX` → `wrote …/projX/parts/firebeetle2-esp32c6.json — every
  null is a fact to record`, exit 0: a part-shaped record (`body_mm`, `pin_order`, `needs`, `footprint`) in `parts/`, which
  `boards.py` never reads (`--list` unchanged after it). `parts.py --validate` then asks for `body_mm` and `pin_order`;
  `--audit` lists it as a part that `owes: footprint, pin_order, pin_order_proof, body_mm, simulation`; `--promote
  firebeetle2-esp32c6 --project . --dry-run` → `would promote to ~/Development/spark/parts/firebeetle2-esp32c6.json`. No
  output says that a board is a `boards/<id>.json` with another contract. · E · the four runs; `scripts/parts.py:1480`
  (the row: "write a record to fill in, to the project's parts/"), `:1540` (`--kind`: "motor-driver, sensor, regulator,
  …" — no word on boards). · supports only: a fix-now refusal; not in the catalogue (K29 is "no route", K37 "the skeleton
  omits chain facts"; neither is "the skeleton takes a board and makes a part").

- **STORE-3 · Search, show, update, copy and share are parts-only, and their refusals send the reader to a search that
  cannot find boards.** `--need esp32` → `nothing in the library matches 'esp32'. Research it: /spark:research "esp32"`,
  exit 0, with two ESP32 board files shipped; `--show firebeetle2-esp32s3` → `no part called 'firebeetle2-esp32s3'` and an
  `available:` list of 13 parts, exit 1; `--fact-set myboard-s3 … --project .` and `--function-set myboard-s3 …` → `no part
  record called 'myboard-s3' — \`parts.py --need\` finds what exists`, exit 1; `--promote myboard-s3` → `no record called
  'myboard-s3' to promote`, exit 1. `--describe --json` lists 28 operations; none takes a board. · E · the runs;
  `scripts/parts.py:1332-1351` (`need` walks `available(project)`, parts), `:966-969` (`record_home` reads only
  `"parts"`), `:1285-1306` (`promote`). · supports only: the agent's contract (§6.4) has no board half, and its one fix
  sentence is circular for a board. `/spark:research` has no board flow either (K29, K42).

- **STORE-4 · `boards.py` answers in no envelope.** Its options are `--path --id --list --paths --validate --get --resolve
  --for-fab --project`; `--list --json` → `boards.py: error: unrecognized arguments: --json`, exit 2; there is no
  `--describe`. · E · `boards.py --help` and the run. · supports only: an agent reading board facts parses text; K57 names
  `tools.py` and not this one.

- **STORE-5 · A folder holding a board file but no `boards/active.json` is "no project", and `--validate` then answers about
  the plugin.** From `projY` with `boards/myboard-s3.json` and no selection: `--list` omitted the person's file;
  `--validate` → `boards.py: no board selection at ~/Development/spark/boards/active.json`, exit 1. The docstring says "the
  nearest directory up the tree holding `boards/` or `.spark/`"; the code requires `boards/active.json` or `.spark/`. · E
  · `scripts/boards.py:135-147`; the runs. · supports only: K52's message, met from a person's folder, naming a file the
  person does not own; the step "copy the closest definition" (how-it-works.md:160) leads straight into it unless
  `active.json` is written first.

- **STORE-6 · A copy into a project carries no provenance, so "project store sync" has nothing to compare.** `--promote
  dfr0819-ds3231sn-rtc --project .` (catalog → project) → `promoted to …/projX/parts/dfr0819-ds3231sn-rtc.json`, and `grep -c
  based_on` on the copy → 0; the copy is `shutil.copy2`. A shelf copy does carry `based_on {project, digest}`. A board copied
  by hand (the documented route) carries nothing. · E · `scripts/parts.py:1303`; `:932-941`; the run. · supports only:
  K13's drift has no anchor on the copies a person makes; the digest-reader the existing-first lens names (MISSING-6) can
  only read the shelf's.

- **STORE-7 · The shared layer is specified, decided in outline, and unbuilt — and nothing in the code holds its place.**
  The read order ends `→ shared` and "later a **shared** clone (P84)"; the plan item is "a public repo of records that pass
  the contract, cloned read-only onto the search path at a pinned commit; `--contribute` and a reviewer's CI"; decided: the
  database/NoSQL/Markdown half dropped, no shared document files ever, the shared database starts "when the first person
  outside the project researches a part". `store.layers()` has no `shared` row and no "writable" column (which §6.1 asked
  for), there is no contribute verb, and no natural key that would see a local and a shared copy as one. · E/D ·
  `docs/2026-10-04-store-design.md:47`, `:223-224`, `:273-275`; `docs/2026-10-04-store-discovery.md:135-138`, `:209-210`,
  `:215-216`, `:222-227` (D the PO, 2026-10-04); `scripts/store.py:71-81`; #123 (P178: "maybe a git repo??", the PO,
  2026-10-09). · supports only: reading (1) needs no new concept, only the row, the verb and the key; the PO's 2026-10-09
  wording widens "parts" to "modules and parts and boards".

- **STORE-8 · "Global, local and project" are three relations with three privacy rules, and one sync mechanism for all
  three would break one of them.** (i) shared ↔ local: records only — never the drawer, the drawer imports, the history,
  the projects list, document bytes or photos (§5.8; "No shared document files, ever"); (ii) the person's own store across
  their own machines: everything, private, and 30 MB of its 33 MB is kept documents (`du -sh` on the copy:
  `sources/` 30M, the store 33M; FEASIBILITY-5 has the same); (iii) local ↔ project: a copy pinned to its source by a
  digest (STORE-6). A pull-request review fits (i) and is absurd between two of one person's laptops; a folder sync fits
  (ii) and would publish (i)'s private half if pointed at the shared repository. · H (mine) on E pointers ·
  `docs/2026-10-04-store-design.md:262-267`; `docs/2026-10-04-store-discovery.md:138`; the `du` run. · supports only:
  the survey below answers per relation, not with one tool.

- **STORE-9 · Nothing compares the simulator's stand-in with the board's own chip.** A copy of the S3 file with `"chip":
  "esp32c6"` and `wokwi_part_type` still `board-esp32-s3-devkitc-1` → `boards.py --validate` → `active myboard-s3
  (project): ok`, exit 0; `--get wokwi_part_type` → `board-esp32-s3-devkitc-1`, `--get chip` → `esp32c6`. The converter's
  board type carries `chip` and no code reads it; the registry spark bundles has no chip field (entry keys: `type, pins,
  documented, isBoard, category`). The documented own-board route's step 1 — "Copy the closest definition … take the pin
  map from the vendor's own `pins_arduino.h`" — keeps the old board's stand-in and says nothing about it. · E · the run;
  `tools/circuit-to-wokwi/lib/board.ts:27-36`; `scripts/boards.py:62` (`wokwi_part_type` required, its value unchecked
  beyond the power pads, `:307-313`); the registry read under `tools/circuit-to-wokwi/node_modules/@wokwi/diagram-lint/dist/registry/parts.json`;
  `docs/guide/how-it-works.md:160-171`. · supports only: a silent wrong-silicon simulation is one copy away on the
  documented route; not in the catalogue (K32 is the missing-pin half, met only because the pin was missing).

- **STORE-10 · "The closest Wokwi board" can be a lookup, not a guess.** wokwi-boards' own `board.json` names each board's
  microcontroller: `esp32-devkit-v1` → `"mcu": "esp32"`, `esp32-s3-devkitc-1` → `"esp32-s3"`, `esp32-c6-devkitc-1` →
  `"esp32-c6"`, `xiao-esp32-c6` → `"esp32-c6"`. None of its 55 board folders is a DFRobot board. For the PO's four ESP boards
  with no board file, by the chip their drawer labels name: DFR1075 (FireBeetle 2 ESP32-C6, ×2) and DFR1117 (Beetle ESP32
  C6, ×3) → `board-esp32-c6-devkitc-1`; DFR0994 (Romeo ESP32-S3, ×1) → `board-esp32-s3-devkitc-1`; DFR0575 (Beetle ESP32,
  ×2) → `board-esp32-devkit-c-v4` or `-devkit-v1`. · E (the `mcu` fields, the folder list: `gh api
  repos/wokwi/wokwi-boards/contents/…`, read-only, 2026-10-10; the drawer entries and counts: `parts.py --drawer --json`
  paged over 110 entries on the copy) · H (the chip of DFR0575 from its label alone, "Beetle ESP32 Microcontroller") ·
  supports only: board C8's per-chip table can carry the stand-in, and STORE-9's check can name the right candidates;
  copying the `mcu` facts is a table of facts, not a copy of wokwi-boards' files (STORE-11's licence note).

- **STORE-11 · A Wokwi custom board is spark's board record in another shape — and the chain cannot run one today.** A
  wokwi-boards board is `board.json` + `board.svg`; `board.json` holds `name`, `mcu`, `fqbn`, `width`/`height` in mm, and
  `pins` as `{label: {x, y (mm), target: "GPIO39" | "GND" | "power(3.3)"}}`. spark's record has `pins` (label → GPIO),
  `power_pads` (pad → rail), `physical.width_mm`/`height_mm`/`header` (from which `emit_footprint` already places every pad),
  `chip` and `vendor.arduino_variant` (the FQBN's last word). But a custom board is loaded locally only in the wokwi.com
  editor ("press F1 and choose 'Load custom board file…'"); Wokwi's VS Code/CLI project-config page documents `[[chip]]`
  (`name`, `binary`) and no board key; and the wokwi-boards repository declares no licence (no `LICENSE` at its root;
  the API's `license` is null). · E · `gh api repos/wokwi/wokwi-boards/contents/boards/esp32-devkit-v1/board.json`
  (2026-10-10); https://github.com/wokwi/wokwi-boards (README, fetched 2026-10-10);
  https://docs.wokwi.com/vscode/project-config (built 2026-10-09, fetched 2026-10-10); `gh api repos/wokwi/wokwi-boards`
  → `license: null`, root `.github .gitignore .vscode README.md boards tools`. — whether `wokwi-cli` loads a local board
  at all (neither page says; not tried: `wokwi-cli` is not installed here, E `command -v`). · supports only: "create a
  Wokwi board" is a generator spark could own (a composition of facts it holds) whose output today serves the web editor
  and an upstream pull request — not `check_spine`'s simulation stage; a copy of wokwi-boards' own SVGs or JSON into
  spark is a licence question with no stated answer.

- **STORE-12 · Replacing a module in the simulation is built, enforced and documented once; replacing a board is none of
  the three.** A part's `simulation` is one of: a built-in Wokwi part standing in, with a `stand_in` sentence the contract
  requires; a custom chip kept beside the record (`<chip>.chip.json`, `<chip>.chip.c`, compiled by `wokwi-cli chip
  compile`) with a `note`; or `skip` with a reason — and `limits_of` writes every such sentence into
  `WHAT-THIS-CANNOT-SHOW.md` beside the diagram. The board has `wokwi_is_stand_in`, which no code reads, no required
  sentence, and `limits_of` walks `design.parts` only, so the board's own stand-in never reaches that file. The research
  route never says how to write a part's stance: `grep -n simulation commands/research.md agents/parts-researcher.md` →
  nothing. · E · `scripts/parts.py:496`, `:502-504`; `scripts/sim_project.py:62-71`, `:75-104` (`:90`), `:133-160`,
  `:167-178`; `commands/build.md:174-177`; `tools/circuit-to-wokwi/lib/board.ts:35`; the grep (2026-10-10). · supports
  only: the board half of reading (3) can copy the part half's rule; the module half needs one paragraph where research
  is described (K37 is the skeleton's half).

- **STORE-13 · A custom chip is code, so sharing one is a licence decision nobody has made — and a chip cannot stand in
  for a board.** spark's shipped chips say `"author": "smartbin"` and carry no licence line (`grep -rn -i
  "license\|licence\|SPDX" parts/*/chip/` → nothing); Wokwi's chip template is MIT (`gh api repos/wokwi/inverter-chip` →
  MIT), `wokwi-cli` MIT; the 2026-10-04 discovery left "whether [shared records] may carry code (a Wokwi chip)" open. The
  chips API offers GPIO, analog, timers, UART, I2C, SPI and a framebuffer — peripherals; the page says nothing of a chip
  being a microcontroller. · E (the grep, the licences, the page https://docs.wokwi.com/chips-api/getting-started, built
  2026-10-09, fetched 2026-10-10; `docs/2026-10-04-store-discovery.md:240`) · H (a chip cannot run firmware: the API has no
  CPU or flash; the page is silent) · supports only: a module may be replaced by a chip; a board may be replaced only by a
  Wokwi board of the same silicon (STORE-10) or a custom board (STORE-11); a shared store that carries chips needs a
  licence per chip.

### Reading (4) — what exists that could carry sync, rules and editing

- **STORE-14 · Plain JSON files in a git repository is the best fit for the shared store, and writing no sync code is
  right; the facts below close the alternatives the other lenses left at H.** I agree with EXISTING-FIRST-25/-26/-27,
  TECH-LEAD-14, RISKS-17 and FEASIBILITY-5/-6 and do not restate them. Added, E: `cr-sqlite` is a loadable SQLite extension,
  and neither the PO's Python (pyenv 3.10.0) nor `/usr/bin/python3` can load one (`sqlite3.Connection` has no
  `enable_load_extension`); ElectricSQL now describes itself as "The agent platform built on sync" and syncs from
  Postgres (H for Postgres, memory; E for the description); CouchDB is a server and PouchDB a JavaScript library; Dolt
  replaces files with SQL tables (contra D 2026-10-04 "no database"); git-annex, DVC and git-lfs move large files — the
  document bytes D 2026-10-04 says are never shared; Automerge (`pip install automerge`, Rust core, MIT) and pycrdt (MIT)
  merge concurrent edits of one document, a problem a one-writer store with pull-request review does not have. · E (`gh
  api repos/<each>` 2026-10-10: licence, last push; the `sqlite3` probe; `command -v` for each tool) · supports only: the
  shared store = a git repository of records (parts, boards, and chips if the licence question is answered); spark adds
  a read-only layer row, a contribute verb and a natural key — no dependency.

- **STORE-15 · "Project store sync" is a lockfile technique, and spark has half of it.** `based_on {project, digest}` on a
  shelf copy is a lock entry: which source, at which content. Written on every copy into a project too (STORE-6) and read
  by `--audit` (MISSING-6), it gives "this copy is behind its source" and a `--refresh` after a dry run that shows the
  difference — the pattern of npm's and Cargo's lockfiles and of a git submodule pinned at a commit. · H (those tools'
  designs, memory) on E (`scripts/parts.py:932-941`; STORE-6's run) · supports only: no library; one field written in one
  more place and one reader.

- **STORE-16 · Syncthing names its conflict copies so that store C7's plain-key check catches them by itself.** The
  pattern is `<filename>.sync-conflict-<date>-<time>-<modifiedBy>.<ext>`, and the losing file is the older one; a drawer
  file `dfrobot-sen0193.sync-conflict-…-<DEVICE>.json` has a stem with dots and capitals, which `PLAIN`
  (`[a-z0-9][a-z0-9-]*`) refuses. · E · https://docs.syncthing.net/users/syncing.html (written for v2.1.0, fetched
  2026-10-10); `scripts/store.py:99`. · supports only: for relation (ii) of STORE-8, spark needs no Syncthing support —
  store C7 (name the file) and C3 (the lock beside the data) are the whole of it; this turns EXISTING-FIRST-30's H to E
  for one client.

- **STORE-17 · git's union merge is safe for `history.jsonl` only if no reader depends on line order, and that is not yet
  shown.** The driver "take[s] lines from both versions … This tends to leave the added lines in the resulting file in
  random order". `step` events carry a `start`; `reused`, `passed_over` and `built` carry no time; duplicates are harmless
  (`recorded()`). · E · https://git-scm.com/docs/gitattributes (2.56.0, fetched 2026-10-10); `scripts/store.py:273-274`,
  `:308-311`; the copy's `history.jsonl` lines. · — whether `--tally` or the step window reads line order (not traced) ·
  supports only: MISSING-2's experiment (existing-first) must include a `--tally` before and after the merge; relevant
  only if relation (ii) is done with git.

- **STORE-18 · KiCad library content inside a shared spark store would set that store's licence.** KiCad's libraries are
  CC-BY-SA 4.0; the exception for designs does not cover redistributing library elements "as a collection", which then
  follows CC-BY-SA with attribution. A shared board record that carries a converted vendor or KiCad footprint (the route
  EXISTING-FIRST-16 and board C9 propose for the XIAO) brings that licence with it. · E · https://www.kicad.org/libraries/license/
  (fetched 2026-10-10, undated) · H · Seeed's OPL library CC BY-SA 4.0 (the bin's CLAUDE.md; not re-read) · supports
  only: the open choice "CC0 or CC-BY" (`docs/2026-10-04-store-discovery.md:240`) has a third case: records point at
  footprints, never carry them, or the shared store is CC-BY-SA for those files.

### Reading (4) — the survey

What each candidate does for *this* job — the store's sync between the shared, the local and a project's records, its
rules, and an editor — judged by the PO's rule (D the PO, 2026-10-06: only free things; one best tool per job; a local CLI
first; users install nothing heavy). Licences and last pushes from `gh api repos/<owner>/<repo>` (read-only,
2026-10-10) unless marked; "here" from `command -v` on the PO's Mac.

| candidate | does for this job | does not | licence | a user installs | free | agent drives it from a CLI | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| plain JSON records in a git repository | the shared store (clone = local copy of the shared layer, pinned commit = a version; pull request = contribution and review; CI = the contract) | merge two edits of one record by itself; privacy — it must never hold the private half | git GPL-2.0 (H) | nothing: git 2.49.0 here, already required | yes | yes (`git`, `gh`) | **adopt for relation (i)** — write nothing new |
| a private git remote for the person's own store | relation (ii), history and named conflicts per file | needs `inside_git` scoped to a project's tree (MISSING-3); documents are 30 MB of binaries | as git | nothing | yes (a private repo) | yes | **the person's choice**, not spark's default |
| git `merge=union` on `history.jsonl` | merges two appends without a conflict | keeps line order (STORE-17) | — | nothing | yes | yes | **only with MISSING-2's test** |
| Syncthing | relation (ii) peer to peer; conflict copies named (STORE-16) | review, history, a shared store | MPL-2.0 | a daemon (not here) | yes | yes (`syncthing cli`, H) | **spark survives it (C7, C3); does not ship it** |
| rclone (`bisync`) | relation (ii) to cloud storage | review, history; bisync conflicts are its own rules (H) | MIT | a Go binary (not here) | yes | yes | **same as Syncthing** |
| git-annex · DVC · git-lfs | large files under version control | anything D allows: document bytes are never shared (discovery:138, :215) | git-annex GPL/AGPL (H) · DVC Apache-2.0 · git-lfs NOASSERTION | each a new tool (none here) | yes | yes | **no** — they solve the forbidden half |
| Dolt | versioned SQL tables with branch, diff, merge | `cat`/`grep` of a record; the D "no database" | Apache-2.0 | a Go binary (not here) | yes | yes | **no** |
| SQLite (stdlib 3.43.2) | transactions, a lock beside the file | a synced folder (FEASIBILITY-6); human-readable files | public domain (H) | nothing | yes | yes | **not the source of truth**; a rebuildable index later, if the catalog outgrows a glob (18 records today) |
| cr-sqlite | CRDT merges inside SQLite | load in the PO's Python (STORE-14, E) | MIT | a native extension and a Python built to load it | yes | partly | **no** |
| ElectricSQL · Litestream · LiteFS | Postgres-to-client sync · SQLite replication to object storage · a FUSE cluster | a local, serverless, one-person store | Apache-2.0 (all three) | a server or cloud bucket | partly | yes | **no** |
| CouchDB / PouchDB | master–master replication with revision trees | a CLI without a server; files a person opens | Apache-2.0 | an Erlang server / a JS runtime | yes | via HTTP | **no** |
| Automerge (automerge-py) · Yjs / pycrdt | conflict-free merge of concurrent edits | review of what enters a shared store; `grep` on a binary change log | MIT · Yjs NOASSERTION by GitHub (MIT, H) · pycrdt MIT | `pip install automerge` (Rust wheels) | yes | yes (Python) | **no** — a single-writer store with PR review has no concurrent edits to merge |
| JSON Schema + VS Code (`$schema`, `json.schemas`) | rules as data; validation, completion and hover in the editor the PO uses; one statement for Python and TypeScript | enforce chain rules spark computes (pin roles, the stand-in check) | jsonschema MIT (4.2.1 installed here, not a spark dependency) | nothing for the editor; `jsonschema` only if spark validates with it | yes | yes | **adopt, generated from spark's tables** (EXISTING-FIRST-23/MISSING-1, TECH-LEAD-14) — for boards it also documents every `wokwi_*` key |
| Datasette (+ sqlite-utils, datasette-write) | a browsable table of records, from JSON via `sqlite-utils insert` | editing the source files (datasette-write edits SQLite, has no licence: `license` none, 12 stars) | Apache-2.0 · Apache-2.0 · none | `pip install` and a server process | yes | yes | **no**; P86's generated read-only page (discovery §4) is smaller |
| a KiCad library editor / KiCad's tables and PCM | the global-plus-project table design and a static checksummed index (EXISTING-FIRST-27) | anything on the user's path (D the PO, 2026-10-06, P136) | GPL-3.0+ (H); libraries CC-BY-SA 4.0 (STORE-18) | KiCad | yes | `kicad-cli` (not here) | **copy the design, not the tool** |
| wokwi-boards (`board.json` + `board.svg`) | the format a custom Wokwi board takes; `mcu` per board (STORE-10) | run locally in `wokwi-cli` (—, STORE-11) | none declared | nothing (a format) | yes | yes (`gh api`) | **read its `mcu` facts; generate, never copy, a board** |
| Wokwi custom chips (`chip.json` + C → WASM) | replace a module in the simulation; already spark's mechanism | replace a microcontroller (STORE-13) | template MIT; spark's chips none stated | `wokwi-cli` for `chip compile` (not here) | compile free; scenario runs spend CI minutes (`commands/build.md:209-210`) | yes | **keep; give each shared chip a licence** |
| `@wokwi/diagram-lint` registry | every built-in part's pin names, offline | chips or `mcu` | MIT file / ISC `package.json` (EXISTING-FIRST-21) | already in the converter | yes | yes | **copy under `data/` with its version** (MISSING-7) |
| Arduino `boards.txt` | SKU → variant → FQBN for a board skeleton (board C8) | geometry, power | LGPL-2.1 (H) | nothing (`gh api`) | yes | yes | **keep as C8 has it** |
| LCSC/JLCPCB (`jlcpcb:C…` footprints, spark's JLCPCB MCP) · EasyEDA via `easyeda2kicad.py` | a part's footprint and 3D model by LCSC number | a module's or a board's chain facts | JLCPCB data terms — · easyeda2kicad AGPL-3.0 | the MCP (spark's plugin) · `pip` | yes | yes | **a research source; never the store's format** |
| Octopart/Nexar exports | prices and stock | anything free (H: keyed API) | commercial (H) | an account | no | — | **no** (the rule's "only free") |
| DFRobot wiki and product pages | a board's documents: the dimension drawing, schematics (board C8 step 4) | a machine API (H) | — | nothing | yes | via the person's browser (§6.6) | **records point; documents kept privately** |
| InvenTree | allocate/release names for holds (EXISTING-FIRST-28) | a local CLI | MIT | a Django server | yes | via REST | **benchmark only** |

**Recommendation, in the PO's rule's terms.** One tool per relation, all of it already on his machine, nothing written
that a library would do better: **git** carries the shared store (relation i) — free, local CLI, required already, and an
agent drives it with `git` and `gh`; **spark's own `based_on` digest** carries the project relation (iii) — no library
exists for "this record copy is behind its source in this tool's contract", and spark has half of it; **nothing from
spark** carries the person's own machines (ii) — he may use a private git remote or a folder sync, and spark's job is to
survive both (store C3, C7; STORE-16, STORE-17). **JSON Schema, generated from spark's tables**, is the rules-and-editor
format: VS Code reads it with nothing installed. No new file format: the records stay JSON, one file per record.
Writing nothing new for sync is the best fit, said plainly.

## 2. The three scenarios walked today

Run on the store copy as both readers would: a person reading `docs/guide/how-it-works.md` and `boards/README.md`, and an
agent starting from `parts.py --describe --json` (28 operations, E) and `boards.py --help`.

### A · "What is global, what is local?" (reading 1)

| place | holds today (E: counts on the copy and in spark) | written by | read by |
| --- | --- | --- | --- |
| spark's library, the plugin | 8 part records (`ls parts/*.json`), 2 board files (`ls boards/*.json`), 2 chips | the maintainer, by pull request; and `--promote` from any project (K12) | every project |
| the person's store, `~/.local/share/spark` | catalog 18, shelf 5 (parts only), drawer 110 entries, sources 85 kept documents, history 8 lines, projects 5 | parts.py operations | every project, for **parts**; nothing for boards (STORE-1) |
| a project | its `parts/`, its `boards/`, `.spark/needs.json`, `requirements.json` | the person, `--skeleton`, `--promote`, `--requirements` | that project |
| a shared store | nothing | — | — |

Stall: "global" exists only as the plugin, which a person cannot write to without a pull request, and which `--promote`
writes to anyway (K12); "local" exists for parts and not for boards (STORE-1); "shared" is a row in a design (STORE-7).

### B · "I have a board in my drawer with no record" — create, search, update, copy, share

The board: DFRobot DFR1075, FireBeetle 2 ESP32-C6, ×2 (E: `dfrobot-dfr1075 | FireBeetle 2 ESP32 C6 IoT Development Board
… | 2 | None` — no `is`).

| step | the person, from the documents | the agent, from `--describe` | what happened (E, the copy) | stall |
| --- | --- | --- | --- | --- |
| 0 · see it | `parts.py --drawer` | `--drawer --json`, paged 20 at a time | listed by label and count; no key in the plain listing, `is` null | K3 (no key in the plain listing) |
| 1 · search whether one exists | idea.md sends a board with no file to how-it-works "Your own dev board" (`commands/idea.md:140`) | `--need firebeetle c6`, `--need dfr1075`, `--need esp32` | all three: `nothing in the library matches …`, exit 0 — although two ESP32 board files ship; `boards.py --list` shows only the library's two | STORE-3 (new); K33 (word matching) |
| 2 · search whether someone shared one | — | — | no shared layer; no command | STORE-7 |
| 3 · create | step 1 of five: "Copy the closest definition … take the pin map from the vendor's own `pins_arduino.h`" (how-it-works.md:160-163) | `--skeleton <id> --kind board --project .` (the only create row) | the person: a hand copy whose stand-in is the old board's (STORE-9); the agent: a part-shaped record in `parts/`, exit 0 (STORE-2) | K29, K24/K25/K26 (no schema), STORE-2, STORE-9 (new) |
| 4 · check it | `boards.py --validate --project .` | the same, or `parts.py --validate` | without `boards/active.json`: `no board selection at ~/Development/spark/boards/active.json`, exit 1; with it: `ok`, also for a C6 chip on an S3 stand-in | STORE-5, K52, STORE-9 |
| 5 · update it | edit the JSON by hand; the validator's refusals are the only schema | `--fact-set`, `--function-set` | `no part record called 'myboard-s3' — parts.py --need finds what exists`, exit 1 | STORE-3; K24, K31 (no documented `function` on boards) |
| 6 · copy it into my project | `cp` from spark's `boards/`; then `boards/active.json` | `--promote <board> --project .` | `no record called 'myboard-s3' to promote`, exit 1; a hand copy carries no `based_on` | STORE-3, STORE-6, K13 |
| 7 · use it in a second project | name it in `requirements.json` | `--pick <p> board=<id>` | the copy is invisible from any other project (STORE-1); the library S3 is held by the bin (K3) | STORE-1, K3 |
| 8 · share it back | — | `--promote` (parts only, and to the plugin) | no store place for boards, no shared layer, no contribute verb | STORE-1, STORE-7, K12 |

The same walk for a **module or part** goes further: create (`--skeleton`), search (`--need`, `--match`), update
(`--fact-set`, `--function-set`) and copy (`--promote` catalog → project) all run; it stalls at the project's own record
reaching the shelf (K12: `--promote` writes the plugin; `--requirements` shelves only what came from the catalog or
another project), at drift (STORE-6, K13), at research records that arrive owing facts (K37), and at sharing (STORE-7).

### C · "My board is not in Wokwi" — the closest board, or one made for it; and a module Wokwi lacks

| step | today | what happened or what the source says | stall |
| --- | --- | --- | --- |
| 1 · is there a Wokwi part for it? | the record's `//wokwi_part_type` prose; nothing searches | none of wokwi-boards' 55 folders is a DFRobot board (E, STORE-10) | — (a fact, recorded on the S3 only) |
| 2 · choose the closest | a hand-typed `wokwi_part_type` | nothing checks its silicon against `chip` (STORE-9); the `mcu` that would decide it is in wokwi-boards, not in the registry spark bundles | STORE-9 (new) |
| 3 · map the pins | `wokwi_pin_naming`, and the per-pad table misnamed `wokwi_power_pins` (renames and `null` work, E in the firmware verify) | undocumented, validated for power pads only; a GPIO the stand-in lacks stops the last stage with `"14" is not a pin of …` | K32; EXISTING-FIRST-1 |
| 4 · say what the stand-in loses | `wokwi_is_stand_in: true` | read by no code; `WHAT-THIS-CANNOT-SHOW.md` lists parts only (`sim_project.py:90`) | STORE-12 (new) |
| 5 · or make a Wokwi board | nothing in spark | the format maps from the record (STORE-11); a local board runs in the web editor; in `wokwi-cli` — | STORE-11 |
| M · a module Wokwi lacks | `simulation`: a stand-in with a required `stand_in` sentence, a custom chip beside the record, or `skip` (`commands/build.md:174-177`) | works and is enforced; research never asks for it (grep 0); a shared chip has no licence | K37, STORE-12, STORE-13 |

## 3. The smallest change sets

Sizes: S under an hour, M a day, L more (H, mine). Every failure message names where and why, for a person and for an
agent reading the same line.

### Store basics — global vs local, with create, search, update, copy, share; boards first

Prerequisites already proposed elsewhere, not repeated: store C1 with its M1 (refuse a missing or empty `SPARK_HOME`,
name the store in every answer), C3 (one lock beside the data), C7 (reads refuse what writes refuse), C8 (one reader);
board C3/MISSING-1 (the board schema written once); MISSING-6 (one reader of digests).

| # | change | kind | size | test | failure message |
| --- | --- | --- | --- | --- | --- |
| B0 | `--skeleton --kind board` is refused: a board is a `boards/<id>.json` under another contract | bug | S | `test_parts.py::test_a_skeleton_of_kind_board_is_refused_naming_the_board_route` (asserts no file under `parts/`, exit 1); one mutation row | `firebeetle2-esp32c6: a board is not a part record — it is boards/firebeetle2-esp32c6.json, under the board contract (boards/README.md); copy the closest board with --promote <board> --project . and set its chip, pins and stand-in` |
| B1 | `--need` and `--show` see boards: `need()` also walks `boards.records(project)`, matching id, name, chip and SKU; `--show <board>` prints the board with its layer; the circular fix sentence becomes true | bug | S | `test_parts.py::test_need_esp32_lists_both_library_boards`; `test_show_names_a_board_and_its_layer` | for a real gap: `nothing matches 'esp32 c5' in parts or boards (project, store, library, catalog) — research it …` |
| B2 | boards get a place in the person's store — `PLACES["boards"]`, read order project → store → library — so a board written once is found from every project | story (decision B-Q1) | S–M | `test_boards.py::test_a_board_in_the_store_is_listed_from_a_fresh_project`; `…_the_project_s_copy_wins` | `--list` names each board's layer: `myboard-c6 (store)`; a clash names both files |
| B3 | one copy verb for both kinds, both directions, never into the plugin: library or store → project, and project → store, each writing `based_on {layer, id, digest}`; `--audit` reads it (MISSING-6) | story | M | `test_parts.py::test_a_copy_into_a_project_records_where_it_came_from`; `test_audit_names_a_copy_behind_its_source` (change the source after copying) | `projX's copy of myboard-c6 is behind the store's (pins differ) — --promote myboard-c6 --project projX --refresh --dry-run shows the change` |
| B4 | update a board through the same door as a part: `--fact-set`/`--function-set` accept a board id, check the result with `boards.validate`, write in its own home, never the library — or, smaller, document "edit the file; `boards.py --validate` is the check" (with B5's envelope) | story (or docs) | M (or S) | `test_parts.py::test_fact_set_on_a_board_is_checked_by_the_board_contract` | the board validator's own sentences, prefixed with the file |
| B5 | `boards.py` answers in the one envelope (`--json`), or its read operations become rows of `parts.py`'s `OPERATIONS` so `--describe` lists them | chore | M | `tests/test_json_contracts.py` gains `boards.py --list --json` and `--validate --json` | the envelope's `problems`, each naming the board file and key |
| B6 | the shared layer (P84 as decided): a read-only `shared` row after the catalog for parts and boards, pointing at a git clone at a pinned commit; `--contribute <id> --into <clone> --dry-run` writes the filtered record (the shelf's filter) and prints the `git`/`gh` commands for the person's yes; a natural key (vendor, SKU) so a local and a shared copy are seen as one | story | L | a fixture clone in the suite: a contributed record validates in the clone; `--need` labels it `[shared @<commit>]`; a local edit shows `diverged` | `myboard-c6 (shared @1a2b3c4) and your store's myboard-c6 differ — yours wins here; --contribute offers yours` |

### Simulation replacement — documented, and checked where it can be

| # | change | kind | size | test | failure message |
| --- | --- | --- | --- | --- | --- |
| S1 | one section, "When Wokwi has no part for it", in `boards/README.md` and `commands/build.md`: a board → the closest Wokwi board with the same `mcu` (the table of S2), `wokwi_part_type`, `wokwi_pin_naming`, the per-pad name table with `null` for "not on the stand-in", and what the stand-in costs; a module → a stand-in with `stand_in`, a custom chip (files, `wokwi-cli chip compile`, `note`), or `skip`; and how-it-works' step 1 gains "a copied file keeps the old board's stand-in — set it for your chip" | docs | S | `tests/test_docs.py`: the section names every `wokwi_*` key the board contract reads and the three part stances | — (a page) |
| S2 | `--validate` refuses a stand-in of other silicon, and names the candidates: a table `data/wokwi-boards.json` `{type: mcu}` taken from wokwi-boards' `board.json` `mcu` fields at a cited commit (facts, not their files), checked against `chip` | bug | S | `test_boards.py::test_a_stand_in_of_another_chip_is_refused` (the `projY` file of STORE-9 as the fixture); `test_the_shipped_boards_stand_in_on_their_own_silicon` | `wokwi_part_type board-esp32-s3-devkitc-1 is an esp32-s3; this board's chip is esp32c6 — Wokwi boards with that chip: board-esp32-c6-devkitc-1, board-xiao-esp32-c6` |
| S3 | the per-pad names: board C11 in the firmware verify's form (the emitter picks a label the stand-in knows; the override documented, renamed or aliased, `null` allowed, validated against the registry copy of MISSING-7) | bug | S–M | as board C11 and firmware C1 say | as they say |
| S4 | a board's stand-in says what it costs, and the simulation says it: `wokwi_is_stand_in` becomes a sentence (`wokwi_stand_in`) the contract requires when the type is not the board's own — the rule `parts.py:502-504` already applies to parts — and `limits_of` reads `design.board` as well as the parts | bug | S | `test_sim_project.py::test_the_board_s_stand_in_reaches_what_this_cannot_show`; `test_boards.py::test_a_stand_in_board_must_say_what_it_loses` | `WHAT-THIS-CANNOT-SHOW.md`: `- **mcu** — the generic ESP32-S3 devkit stands in: same silicon; the silkscreen labels are lost, TX/RX are named TX/RX there` |
| S5 | a generator `boards.py --wokwi-board <id> --out <dir>` writing `board.json` + a plain `board.svg` from the record (pins with targets, mm positions from `emit_footprint`'s pad placement, width and height) — for the web editor and an upstream pull request to wokwi-boards | story (decision S-Q1) | M | `test_boards.py::test_a_wokwi_board_from_the_s3_record_names_every_label_with_its_gpio` | `could not place pads for <id>: physical.header owes …` — the footprint's own refusal |

## 4. Fix now vs P178's concept

**Fix now** — bugs and documentation that decide nothing P178 must decide: B0, B1, S1, S2, S4, and S3 as the board and
firmware lenses already propose; with them the prerequisites store C1(+M1), C3, C7, C8. STORE-5's docstring and message
(name the person's folder, not the plugin's `active.json`) is one line beside K52. One sentence in `commands/research.md`
and `agents/parts-researcher.md` on the `simulation` stance (STORE-12) belongs with needs C5 (the skeleton's chain facts).

**P178's first slice** — small, and each needs one decision first: B2 (where boards live in the store), B3 (copies pinned
or followed — B-Q3), B4 (a door or a documented hand edit), B5 (where the board operations live).

**P178's concept** — B6 (the shared layer, its natural key, origin and review badges, CI), the licence of shared records
and chips (STORE-13, STORE-18), relation (ii) of STORE-8 (whether spark says anything about a person's own machines
beyond surviving them), holds derived or stored (the store verify's M2 — a shared store must not carry them), the project
id (store C5), the editor (JSON Schema generated from spark's tables; P160's "levels"), and S5 (a generated Wokwi board,
after S-Q1).

## 5. What I could not check, and why

- Whether `wokwi-cli` or Wokwi for VS Code can load a board defined locally: neither the project-config page nor the
  wokwi-boards README says, and `wokwi-cli` is not installed here (E `command -v`); a run would also spend CI minutes.
- Whether a custom chip can act as a microcontroller: the chips-API page is silent; STORE-13's "it cannot" is H.
- The licence of wokwi-boards' files: none declared (E); whether Wokwi states one elsewhere is —.
- The chip on DFR0575 (Beetle ESP32): from its drawer label only (H); the other three from labels that name the chip.
- Whether any reader of `history.jsonl` depends on line order (STORE-17): not traced through `--tally`.
- `wokwi-custom-chips`, a GitHub owner that appeared in a search result: `gh api users/wokwi-custom-chips` → 404; whether a
  community chip registry exists is —.
- Licences marked H in the survey (git, git-annex, SQLite, KiCad the application, Arduino core data, Yjs's file) were not
  read at source; JLCPCB's data terms were not read (—).
- No board record was written through a whole chain run: B and C stop where the table says; I did not run
  `check_spine` or the converter (the board and firmware lenses did, and I cite them).
- Sizes in §3 are estimates; test names are proposals in the suite's style, not written.

## 6. Questions for the decider

| question | what it decides |
| --- | --- |
| B-Q1 · Do boards get a place in your store (read project → store → library), like parts have the shelf? | B2, and whether a board made in one project is found from the next |
| B-Q2 · One table of operations for parts and boards (boards as rows of `parts.py`), or `boards.py` with its own envelope? | B4, B5, and whether `--describe` is the one contract an agent reads |
| B-Q3 · A record copied into a project: pinned to its source by a digest and refreshed on request after a dry run (a lockfile), or always read through from the store? | B3 and #17's "projects update their data" (K13) |
| B-Q4 · The shared store: one public git repository of records — parts, boards, and chips? — cloned read-only at a pinned commit, contributed by pull request, as decided on 2026-10-04 for parts? | B6, and P178's first value line |
| B-Q5 · The shared records' licence: CC0, CC-BY, or CC-BY-SA where a record carries a KiCad-derived footprint — or records only point at footprints? And may a shared record carry a chip (code), under which licence? | STORE-13, STORE-18 |
| B-Q6 · Your own machines (relation ii): does spark stay out (you choose a private git remote or a folder sync, and spark survives both), or does spark support one of them? | whether `inside_git` is re-scoped (MISSING-3) now or later |
| S-Q1 · For a board Wokwi lacks: the closest Wokwi board with the same chip and a per-pad name table (works in the chain today), and a generated custom board only for the web editor and an upstream pull request — or wait until Wokwi documents local boards in its CLI? | S5, and whether "create one" is in P178 or later |

## 7. Searches

Ten allowed; eight used (two web searches, six page fetches), each with the decision it served. `gh api` reads, read-only, are
listed after.

| # | query or URL, verbatim | decision served | used |
| --- | --- | --- | --- |
| 1 | search: `Wokwi custom board definition board.json board.svg wokwi.toml local custom board VS Code` | whether spark can create a Wokwi board for a board Wokwi lacks | found the repository and the chips pages → 2, 3 |
| 2 | fetch https://github.com/wokwi/wokwi-boards (2026-10-10) | how a custom board is made and loaded; its licence | used — STORE-11 (web-editor loading); licence not on the page |
| 3 | fetch https://docs.wokwi.com/vscode/project-config (built 2026-10-09) | whether the chain's `wokwi-cli`/VS Code run can take a local board | used — STORE-11 (`[[chip]]` only) |
| 4 | search: `wokwi-cli OR "Wokwi for VS Code" custom board "board.json" local not in wokwi-boards` | the same, from another side | nothing decisive — left as — |
| 5 | fetch https://docs.wokwi.com/chips-api/getting-started (built 2026-10-09) | what a chip can replace; its licence | used — STORE-13 |
| 6 | fetch https://git-scm.com/docs/gitattributes (2.56.0) | whether `merge=union` keeps `history.jsonl` whole under a git sync | used — STORE-17 |
| 7 | fetch https://www.kicad.org/libraries/license/ | whether KiCad-derived footprints may sit in a shared spark store, and under what licence | used — STORE-18 |
| 8 | fetch https://docs.syncthing.net/users/syncing.html (v2.1.0) | whether store C7's plain-key check catches a folder-sync client's conflict copy | used — STORE-16 |

`gh api`, read-only, 2026-10-10: `repos/wokwi/wokwi-boards` (licence null; root listing), `…/contents/boards` (55
folders), `…/contents/boards/{esp32-devkit-v1,esp32-s3-devkitc-1,esp32-c6-devkitc-1,xiao-esp32-c6}/board.json` (the `mcu`
fields and the format); `repos/wokwi/{inverter-chip,wokwi-cli,wokwi-features,wokwi-elements}` (licences);
`users/wokwi-custom-chips` (404); `repos/<owner>/<repo>` for automerge/automerge, automerge/automerge-py, yjs/yjs,
y-crdt/pycrdt, vlcn-io/cr-sqlite, electric-sql/electric, dolthub/dolt, iterative/dvc, syncthing/syncthing, rclone/rclone,
simonw/datasette, simonw/sqlite-utils, simonw/datasette-write, apache/couchdb, pouchdb/pouchdb, uPesy/easyeda2kicad.py,
python-jsonschema/jsonschema, sqlite/sqlite, superfly/litefs, benbjohnson/litestream, git-lfs/git-lfs (licence, last push,
description); `repos/automerge/automerge-py/contents/README.md`. Local, no network: `command -v` for git, git-annex, dvc,
dolt, syncthing, rclone, datasette, sqlite-utils, sqlite3, couchdb, check-jsonschema, node, bun, wokwi-cli, kicad-cli;
the `sqlite3` extension probe; the registry under the converter's `node_modules`.
