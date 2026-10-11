# P158 part 1 — the proposal: what goes wrong where and why, the refactoring, and the change list in priority order

Written 2026-10-10 by the synthesiser, third version. The first version (1,527 lines) went through the refuter's round 1
(`council/refuter-round-1.md`) and the completeness critic (`council/completeness-critic.md`); the second version folded
both and went through the refuter's round 2 (`council/refuter-round-2.md`); every round-2 verdict is folded here. The two
sections at the end, *Changes since round 1* and *Changes since round 2*, list each change one line at a time, and
*Status*, last, counts them. Against spark 0.8.1 at main `4a18333` (E `gh api repos/xmejkal/spark/commits/main` →
`4a18333 2026-10-10T17:32:07Z Merge pull request #125 from xmejkal/p179-vendor-cache`, my run, 2026-10-10). This is a
proposal; nothing is filed and nothing is decided here.

The PO's words it answers, 2026-10-10, verbatim: *"come up with an explanation as to what exactly is going wrong where
and why and how to refactor it well and add or remove parts to simplify it and really making it work and fix the gaps
based on the user and ai experience and suggest a list of changes into the system? That we could then later turn into an
epic of stories and chores and prioritize etc?"* · *"Lets really order it by priority, so we're fixing what matters."* ·
*"lets make sure its really good, with a few adversarial rounds, really well thought through. We also want the system to
be well designed so its well testable and understandable where a mistake is happening and why"* · *"Mostlu e need to be
able to have the basic globsal vs local store, to be able to create search for and update and copy or share the store
things, the boards for sure, maybe we should also add how exactly to replace a board or a module in the simulation, so
wokwi uses the closest board  or maybe we can create one"* · *"maybe some new file formats or synch libraries or
techinques could be used from an existing library that does somwthing that would make the whole store synch and global
and loval and project store sync and rules and editor?"*

**What this rests on.** Read whole: `catalogue.md` (K1–K74); the six diagnoses and their six verifications in
`diagnosis/`; the eight council lenses, the refuter's two rounds and the completeness critic in `council/`. The second
version's reads at `a8aa34d` are kept where the code did not change: `git diff --stat a8aa34d 4a18333` touches nine
files — `docs/guide/agents.md`, `docs/guide/how-it-works.md`, two files under `docs/observations/`,
`scripts/check_vendor_pins.py`, two mutation tables and two test files (E my run) — so every other line cited at
`a8aa34d` is the same line at `4a18333`. In the changed files, lines moved: `agents.md` by +5 after its line 126,
`how-it-works.md` by +1 after line 57 and +2 after line 175, `tests/test_json_contracts.py` by +22 after line 141 (E the
diff's hunk headers); every pointer into them below is at `4a18333`. Re-read by me at `4a18333` (E, 2026-10-10):
`scripts/store.py:40-52` (`home()`, with its `XDG_DATA_HOME` branch), `:94-96` (`PRIVATE`), `:180-218` (`locked()`,
`_target`, `_make_ready`); `scripts/tools.py:43-80`, `:525-535`, `:580-592`; `scripts/init_project.py:38-46`,
`:405-420`, `:480-505`; `scripts/outcomes.py:1-25`; `scripts/boards.py:38`, `:153`, `:488-545`;
`scripts/check_spine.py:428-442`; `scripts/cost.py:100-112`, `:243-247`, `:270-278`; `scripts/parts.py:895-916`,
`:936-942`, `:2150-2156`, `:2192-2212`; `scripts/needs.py:30-36`, `:50-72`, `:122`; `scripts/drawer.py:54`;
`scripts/design.py:92-101`; `tools/mutate.py:57-61`, `:196-204`, `:222-228`; `scripts/check_vendor_pins.py:27-31`,
`:108-171`, `:230`, `:272-275`; `boards/firebeetle2-esp32s3.json:5`, `:105`, `:115`; `boards/xiao-esp32-c6.json:5`,
`:9`; `docs/guide/agents.md:83-88`, `:129-133`, `:149`, `:253`, `:300`, `:322`, `:418`, `:461`;
`docs/guide/how-it-works.md:157`, `:161`, `:177`; `tests/test_json_contracts.py:164`; `scrum/README.md:7`;
`docs/observations/INDEX.md:270-297` and `docs/observations/2026-10-10-p179-council.md`;
`scrum/PRODUCT_BACKLOG.md:1076-1083`; `docs/2026-10-04-store-discovery.md:120-125`. My counts: `tests/mutations/*.json`
→ 116 files, 1,281 rows (1,241 on `.py`, 24 `.md`, 13 `.json`, 2 `.ts`, 1 `.js`); module-level definitions of the plugin
folder → `boards.py:38`, `:153`, `parts.py:45`, `store.py:33`, `tools.py:43` (and `check_vendor_pins.py:108` reusing
`boards`'); `except store.StoreProblem` in a script → `parts.py:2208` (its `main`), `init_project.py:418` (around
`add_project` only), `check_spine.py:628` (around the history line only). Read-only `gh`, 2026-10-10: `pr view 125`,
`issue view 124`, `126`, `127`, `128`, `issue list --state all --limit 12`, `pr list --state all --limit 6`, `project
item-list 1` and `2`. The bin, read only: `boards/active.json`. The PO's real store: its top folder listed (`ls -la`),
nothing opened, no spark command run, no copy made this round — every store figure below is the second version's or the
round-2 refuter's read of their own copies (E theirs, 2026-10-10). Nothing was written anywhere but this file and my
scratch folder.

**Three facts that changed after the lenses wrote.** (1) The stray `dfrobot_firebeetle2_esp32c6.pins_arduino.h` that the
catalogue and five lenses cite as untracked in spark's `.spark/cache/` was moved on 2026-10-10 by P179's own work into
round 0's scratch project's `.spark/cache/`, sha256 unchanged (E #124 comment 2026-10-10T15:20:33Z). (2) **PR #125 is
merged.** The PO merged it at 2026-10-10T17:32:08Z (D; E `gh pr view 125` → `MERGED`, merged by `xmejkal`); #124 closed
at 17:32:09Z, and its comment at 17:36:24Z reads "Done — reproduced on main after the merge of #125 (4a18333),
2026-10-10" (E, quoted by round 2). Its rule, in the docstring it added: *"A live run writes the header it fetched into
`.spark/cache/` of the project that owns the board file, and its line names the file. For a board spark ships, that
project is spark itself, so a live run refreshes the shipped header. `--offline` reads the project's copy first, then
spark's, and says whose answered. A board file in no project is refused live, never written beside."* (E
`check_vendor_pins.py:27-31`). The second version still called #125 open and ranked its merge (CH-62); round 2 refuted
that, so CH-62 leaves the list, Q32 is answered, and CH-24's and CH-47's dependency on it is met. (3) **#125's own
council left rows for P158** (E `docs/observations/INDEX.md:281-297`, N12–N28, status "raised"), which the second
version cited nowhere (round 2, Missing 1): N13 (an agent reads the header in two shapes and no field says whose copy
answered — "raised for the one envelope (P43's shape, P158's plan)"), N14 and N28 (one owner for "where is spark" and
"which project owns this path", and writes that refuse spark's folder unless asked — "an input to P158's design"), N24
(any `.spark/` further up owns a board file), N25 (an unmarked folder inside spark's tree sends a new board's header
into spark's cache), N26 (a symlinked board file or `boards/` folder writes into spark's tracked cache), N27 (with two
spark copies, spark's own cache is called "the project's"), and N12 (the bin's tracked headers are read by nothing —
"the bin's to decide"). They land in CH-4, CH-73, §2.3 and §4. Three cards made at 17:37–17:42Z the same day touch pages
ranked changes edit: P180 (#126, in Review, PR #129: three documentation experts on every council), P181 (#127, in
Review: P179's documentation — `how-it-works.md`, `agents.md`, `--help`; its F4: *"agents.md's JSON row says every entry
has `source`; a could-not-run entry has only `board`, `status` and `reason`"*) and P182 (#128, in Idea: README's first
screen). Each block that edits the same page says so.

**How to read.** Tags: **E** a pointer (file:line in spark at `4a18333` unless another repository is named; a command
and what it printed; a card), **H** a claim with its source, **D** a decision (who, when), **—** unknown. Ids: **K** the
catalogue's rows; **RC-SL/BR/CC/NM/FB/DR-n** the diagnoses' root causes (store-levels-and-holds, board-records,
chain-and-checks, needs-matching-vocabulary, firmware-and-bench, docs-and-recorded-outputs); **SL-/BR-/CC-/NM-/FB-Cn,
DR-n** their proposed changes; **SL-M, BR-M, CC-MC, NM-M, FB-M, DR-M** the verifiers' missed causes; lens findings by
their own ids (STORE-, TECH-LEAD-, USER-AI-AGENT-, USER-HUMAN-, RISKS-, FEASIBILITY-, EXISTING-FIRST-, DOCUMENTATION-n);
lens "missing" items prefixed by lens (TL-M-A, UAA-M-A, UH-M-a, EF-MISSING-n, FE-MISSING-n, DOC-M-Dn); the store lens's
changes B0–B6 and S1–S5; **R1-…** a line of the refuter's round 1, **R2-…** of its round 2; **G1–G28** the completeness
critic's gaps; **N12–N28** the rows #125's council raised (`docs/observations/INDEX.md`). Sizes — S under an hour, M a
day, L more — are the lenses' estimates (H). Where a verifier or a refuter round refuted or narrowed a statement, only
the corrected version is used; §7 lists every correction taken.

**Words.** spark's own `GLOSSARY.md` defines most words used here, each with the failure that produced it: the three
outcomes `ok` (it looked and found nothing), `problems` (it looked and found something, exit 1) and `could-not-run` (it
could not look, exit 2 — the founding rule **W1**, *"A check that could not look must never read as a check that
passed"*, `scrum/WORKING_AGREEMENTS.md:15`); the chain; mutation, anchor, caught / escaped / refused; record, catalog,
shelf, `verified`, stand-in, owed and broken; the store, the drawer, pick and reserve, history, tally. Words this
proposal uses that the glossary does not hold: **envelope** — the one JSON answer every `--json` script prints
(`status`, `data`, `problems`, `unchecked`; `outcomes.envelope`); **island** — a component the build left joined to none
of the nets around it (`check_spine.py:433-437`); **door** — the store's own write functions in `store.py`
(`write_json`, `write_file`, `copy_folder`, `append_event`, `keep`), which make folders private and refuse private data
inside a git work tree; **hold** — a drawer entry's `used_in`: how many pieces each project has reserved; **tombstone**
— a removed entry kept in the file as `{"id": …, "drop": true}` so a sync carries the removal; **hard / soft
prerequisite** — a change that cannot be built before another lands / one that can, and prints one sentence less until
it does; **silent** — defined in §3. References to other documents: **§5.8** is the store design's privacy section (the
drawer, the history, the projects list and document bytes never leave the person's machine;
`docs/2026-10-04-store-design.md:262`); **§6.4** its "designed for agents first" section (the three outcomes and the
self-description an agent reads; `:312`); **§8 G** its "research only the gap" step (`:477`); **D8** the PO's decision
of 2026-10-09 that the first fix is a board record made automatically from his DFRobot orders (P100 `brief.md:83`);
**★C1–★C12** the P100 brief's claims about what works today; **G0.1–G0.10** round 0's gaps (P100
`council/round-0-runner.md`); **P<n>** a backlog item, **#n** a GitHub issue or pull request.

## 1. The picture in one page

### What a person meets, step by step

The faults by the step of the journey where a person or an agent meets them. Plain words first; the ids are in the last
column only, and §3 holds each fix.

| step | what you see | what actually happened, and why | fixed by |
| --- | --- | --- | --- |
| 0 · which store am I in? | answers about your parts, exit 0 | spark finds your parts through a setting, `SPARK_HOME`. Set but empty, it quietly reads another store — the one `XDG_DATA_HOME` points at if that is set, else your real one; naming a folder that is not there, it quietly starts a new, empty one; no answer says which store answered | K1, K2 · CH-1, CH-11 |
| 1 · say what you want | a need you typed wrong stays | a need cannot be removed or renamed; the page says "fix it by hand" in a file the tool otherwise owns | K35 · CH-50 |
| 2 · see what you own | your drawer, by label and count | the listing never says which project reserved what, and 91 of your 110 entries say nothing of what they do, so no need can find them | K3, K36 · CH-72, CH-25, CH-19 |
| 3 · search the library | "nothing matches — research it" | the search wants every word inside the id, name, kind or alias, so one word too many (or quotes) misses a part you own; it never looks at boards at all | K33, STORE-3 · CH-18, CH-21 |
| 4 · match needs to what you own | WiFi on your ESP32 "is a gap"; the right sensor behind "… 3 more" | a board record cannot say what it does; the list cuts at eight and the cut cannot be opened | K31, K41 · CH-54, CH-51 |
| 5 · pick | the pick is taken | a part that does not do the need is taken in silence; a board another project reserved cannot be freed by any command; a board with no board file is reserved, then refused two steps later | K34, K3, K29 · CH-17, CH-25, CH-24 |
| 6 · make a record for a board you own | a file is written, exit 0 | the only "create" verb writes a part file for a board; the hand route had ten gaps in round 0; a pad labelled with a bare number such as `17` makes the circuit tool read it as "pin 17", so two pads become one connection and every check passes | STORE-2, K29, K22 · CH-14, CH-24, CH-12, CH-22 |
| 7 · write the parts file | "wrote requirements.json" | a second file is written beside the project's own one under another name; a file holding a list is replaced by an empty object without a word | K40, K61 · CH-7, CH-6 |
| 8 · build | "the chain runs end to end", or a stop naming an unrelated terminal | with your own `board.tsx` kept, the build judges the regenerated board, not yours; a pad the S3 prints as `MI` cannot be found as `MISO`; when the build also left a part joined to nothing, the stop names only that part, and otherwise it prints the error's type, never its message | K20, K23 · CH-35, CH-23 |
| 9 · check | `[FAIL]`, or "could not look", or `ok` for a board with no outline | the rules file is a snapshot taken whenever `init` ran; a fab check passes a board whose footprint has no geometry | K45, K46, K30 · CH-39, CH-36 |
| 10 · simulate | a pass, or a stop at the last stage | a stand-in of another chip passes every check; a pin the stand-in names differently stops the last stage; what the stand-in costs is never said; a scenario "pass" asserts 1 of 12 pins | STORE-9, K32, STORE-12, K67 · CH-13, CH-31, CH-32, CH-49 |
| 11 · put firmware on the board | the documents end at `pins.py` | no page or tool reaches the board, and the image may be built for another chip | K66 · CH-34, CH-13 |
| 12 · reuse in a second project | nothing | a copied record falls behind its source with no sign; `--promote` puts a project's record into spark's own folder, which an update replaces; a board file in an unmarked folder inside spark, or a symlinked one, still sends a live check's header into spark's tracked cache; boards have no place in your store | K13, K12, N25, N26, STORE-1 · CH-26, CH-63, CH-4, CH-27 |
| 13 · share | — | there is no shared store | STORE-7 · CH-29 (P178) |
| 14 · read the documents | recorded outputs from spark 0.6 and 0.7; a README block that ends in exit 2 | the outputs are pasted by hand and nobody re-pasted them; the gate does not read the pages agents follow | K68, K69, K74 · CH-40, CH-43, CH-41 |
| 15 · an agent reads the JSON | `ok` | the JSON drops the notes, CONFLICT lines and kept files the text prints; one exit code means two things in `boards.py`; the vendor-pin check says whose copy answered in two shapes, by a word, never by a folder | K55, K56, N13, N24, N27 · CH-16, CH-21, CH-73 |

**In five sentences.** The store names things by how they are spelled — a folder name, a file name, a setting's text —
so a typo, a copy or a sync client's duplicate becomes a different thing with no sign (RC-SL-1, RC-SL-2; K1, K4, K9).
Facts and sentences are stated in several places and each copy drifts on its own: the owed facts in six prose places,
the board contract in its refusals, the re-run-init sentence in nine pages and one printed line, a chip's name in two
spellings (RC-CC-4, RC-BR-3, G14; R2-Missing 4). A severity is decided by a channel or a substring instead of by what
was found — any stderr line "breaks the chain", a converter error is recognised by its wording (RC-CC-2, TECH-LEAD-3).
An answer rarely says where it looked or what it skipped, so "nothing matches" and "not owned" read the same over an
empty store, a missed word and a part you own (UAA-M-C, K33, K36). And the person's data and spark's own files are
written by several writers that bypass the one door and the one lock, and whether a write may land in spark's own folder
is decided by where a file sits, not by what it is (RC-SL-3, RC-SL-4, R1-Missing 2–3, N14, N25, N26).

**Who saw these.** Every catalogue row was seen by an AI agent (44) or reasoned from code (28); 2 by the PO with an
agent; 0 by a person typing alone (E `catalogue.md:157`). Every "a person would…" below is therefore H (RISKS-4).

### Design faults — the mechanism does what it was built to do, and that is the fault

- **The store's identities are spellings.** A project is its folder name and resolved path string, a drawer key is any
  file stem on read, a label is a raw string: a copied project reserves the same stock again, a vanished folder's name
  passes to a newcomer with its holds, a sync client's conflict copy counts as owned stock (`owned 16`, the drawer holds
  8) (RC-SL-1 as corrected; K4, K9, K10; E the store diagnosis's runs `store-k4`, `store-k9`).
- **The store's home is a spelling with no existence check, and no `ok` answer names the store it read.** A `SPARK_HOME`
  that names a folder that does not exist silently becomes a new, empty store, and every owned part then reads "known,
  not owned", exit 0, word for word like a correct answer (K1); one that is set but empty silently reads — and writes —
  the fallback: `XDG_DATA_HOME/spark` when that is set, else the default, real store, and an agent that meant a scratch
  store cannot tell either from its output (K2) (RC-SL-2, SL-M1; E `store.py:48-52`: `if os.environ.get("SPARK_HOME"):`
  … `if os.environ.get("XDG_DATA_HOME"):` … `return Path.home() / ".local" / "share" / "spark"`; R2, §1 row). Unset is
  the designed default and reads the right store (R1, §1 row 2).
- **The write lock follows the process, not the data.** Its file is in `tempfile.gettempdir()`, every agent brief sets
  `TMPDIR`, two processes on one store both write; it is applied from outside by `OPERATIONS`, `init` bypasses it, it is
  held across `--fetch`'s downloads with no timeout and no message, and it is taken for a dry run too, which writes
  nothing (RC-SL-3; K5, K6, K7, K64's lock half; E `store.py:186-187`, `:194`; `parts.py:1482`, `:2198-2200`; G1; R2,
  CH-3 row).
- **A hold has no operation and two meanings.** `used_in` is written as a pick's side effect, derived for the picking
  project and stored for every other; nothing releases it and the plain listing never shows it (RC-SL-6, SL-M2; K3; E
  `needs.py:326-331`).
- **A project's proven record has a documented home, and it is the wrong one for everyone but the maintainer.**
  `--promote` from a project writes the plugin's own library; the rule is written down three times (`agents.md:131`
  "copies a project's record into the plugin's own library: never run it unasked"; `--describe`, `parts.py:1490`;
  `parts.py:1296`), and the write is announced. What is silent is the later loss: an update replaces the folder (RC-SL-4
  as corrected by R1, §1 row 6; K12). The layer table's "writable" column the store design asked for was never built
  (FEASIBILITY-14, `store.py:71-81`). **And whether a write may land in spark's own folder is decided by where a board
  file sits.** #125 lets a live vendor-pin check refresh the header of a board spark ships, and finds the board's owning
  project by walking up from the board file's resolved path (`check_vendor_pins.py:126`, `boards.project_root`); so a
  new board in a folder inside spark's tree with no marker of its own, or a symlinked board file or `boards/` folder,
  resolves to spark, and its header is written into spark's tracked cache (N25, N26, raised by #125's own refuter; E
  `INDEX.md:294-295`). The line names the file it wrote; the later loss at an update, or the dirtied tracked header, is
  silent, as with K12.
- **Boards are a second record kind with none of the first kind's verbs.** No store place, no search, no create, no
  update, no copy, no envelope; the one create verb takes `--kind board` and writes a part (STORE-1…STORE-5;
  TECH-LEAD-6).
- **A pad has three names, and the two writers that join them never read the alias table** (RC-BR-1; K23); tscircuit
  reads an all-digit hint as a pin number, which no spark rule looks at (RC-BR-2 as narrowed: a merged netlist, no
  copper short observed; K22; E the rule in `@tscircuit/core` 0.0.1958, `index.js:11653`, and in the second core
  0.0.1911 under `@tscircuit/runframe`, `dist/index.js:11608` — the bin's `tscircuit` 0.0.2621 declares `@tscircuit/core
  ^0.0.1958`; the critic's settled CH-12 point).
- **A chip has two spellings and nothing maps them.** spark writes `esp32s3` and `esp32c6`
  (`boards/firebeetle2-esp32s3.json:5`, `boards/xiao-esp32-c6.json:5`); wokwi-boards writes its `mcu` as `esp32-s3`,
  `esp32-c6`, and its folders drop the `board-` prefix of a Wokwi part type (STORE-10, E). Three changes need the map —
  the stand-in check, the board skeleton's chip table, the generated Wokwi board — and none owns it (R2, Missing 4;
  CH-13 does now).
- **The simulator's names for a board's pins are consulted only at the last stage** (RC-FB-1 as corrected: for both
  library boards 0 GPIOs are absent on the stand-in; two S3 labels and nine XIAO labels have no pin of that *name*; K32).
- **The chain's verdicts take severity from a channel and judge a file the person does not keep.** Any stderr line of the
  generator is "the chain is broken" (RC-CC-2); `--keep` protects `board.tsx` and builds the regeneration (RC-CC-3; K20);
  the rules file holds the person's answers beside a snapshot of derived facts taken once (RC-CC-1; K46); "owes" is one
  flat list whose consequences live in five places (RC-CC-4 as corrected; K47, K48); the board is stated in two files
  (RC-CC-6; K49); the floating-input rule has one word for an input (RC-CC-8 as corrected; K45).
- **Matching has two matchers and the pick consults neither, and the marks cannot record a loose fit.** `--need` is an
  AND of substrings over four fields and never reads the drawer or `function`; `--match` reads both behind a verb gate;
  `--pick` resolves an id and checks nothing; the four marks say whether a part is available, never whether it does the
  need's words (NM-M4, `needs.py:23`); the needs file has no tombstone, and its reader refuses any field or pick shape
  it does not know (`needs.py:34`, `:53-54`, `:68-70`), so recording more than an id is a schema change; the cut at
  eight is unreachable (RC-NM-1, -2, -3, -6, -7; K33, K34, K35, K41, K39; R2, CH-17 row).
- **The firmware is outside every check — since the PO cut the check on 2026-09-29** (RC-FB-3 as corrected; D `066c4af`
  "no AI bloat, nothing kept that nothing uses"); the record's deep-sleep facts have no consumer (RC-FB-4); the image
  builder takes no board, and the tools list's `firmware-image` role takes no chip, so the chip is never compared
  (RC-FB-2 as corrected; FB-M4; FEASIBILITY-15).
- **A sentence has no single home, so a fix lands in some of its copies** (G14, named by no diagnosis): the owed facts
  are restated in six prose places and two printed strings (DOCUMENTATION-12 counts five; `GLOSSARY.md:233-245` is the
  sixth; `parts.py:1631`, `:2088`); "after a build, run init again with `--force`" stands in nine page places —
  `README.md:74`, `:155`; `agents.md:149`; `commands.md:30`, `:49-53`; `commands/init.md:36-42`, `:47`, `:60`;
  `journey.md:717-722` (G2, G14) — and is printed by `init_project.py:485`, recorded at `journey.md:579`.
- **The docs gate proves that a recorded output carries a provenance note, never that it is current, and nothing
  re-records** (RC-DR-1; K68); its version test keys on "v0.8.1 anywhere in README" (DR-M5, `tools/check_docs.py:173`);
  its scope is three places (RC-DR-5; K74).

### Implementation faults — the design says one thing, the code another

- **Readers are not symmetrical with writers.** 37 raw `json.loads(…read_text…)` sites in 16 scripts (TECH-LEAD-1; R1
  recounted 37 and 16); a non-UTF-8 record is a traceback, exit 1 — the code for "problems" (RC-SL-5; K11); `design.read`
  decodes with the locale, not UTF-8 (`design.py:99`; R2, CH-6 row); a `.part` reads as kept (K16); a URL that did not
  answer is dropped with status `ok` (K17). The one reader was a named target on 2026-09-30 and never built
  (EXISTING-FIRST-9; `docs/2026-09-30-refactoring-architecture.md:73-74`).
- **Three writers go around the door.** `tools.py --on/--off/--pin/--use/--new` write the store's `tools.json` with a
  plain `write_text`, outside the door and the lock (E `tools.py:445`); `tools.py` reads the home at import
  (`PERSONAL = store.place("tools")`, `:47-48`), and four scripts import it at module level (E `check_spine.py:68`,
  `flash_image.py:26`, `init_project.py:40`, `sim_project.py:18`); `sim_project.py:162` copies a compiled chip beside a
  library record inside the plugin, where the binaries are tracked (`parts/l9110s-module/chip/l9110s.chip.wasm`)
  (R1-Missing 2, 3; R2 holds).
- **The requirements writer has its own loader and a third copy of the naming rule** (RC-CC-5; K59, K60, K61) and knows
  one file name (RC-NM-8 as corrected: one documented name, one older project with another; K40).
- **Five contract checks test the wrong property** (RC-CC-7; K50, K51, K52, K54, K63); `emit_footprint --json` prints TSX
  (RC-BR-4; K28); and when the build left a component joined to nothing, `check_spine` returns on that island and never
  reports the build errors it has already read (`check_spine.py:433-437`); when there is no island, it reports their
  types only, never the message that names the cause (`:438-441`) (BR-M1 as corrected by R1 and R2, §1 rows).
- **Each output channel drops what the other carries.** The plain text prints a `fix` only when an answer has no lines
  (E `parts.py:2182-2184`); the envelope drops the pick's notes, `--show`'s CONFLICT lines and `--keep`'s kept files;
  `next` is filled by nothing (USER-AI-AGENT-1, -2, -3, -6; K55, K56); and the vendor-pin check says whose copy answered
  as a name inside `source` offline and as a `wrote` path live, and calls a cache "the project's" or "spark's" by
  comparing one folder (`check_vendor_pins.py:149-151`), so a stray `.spark/` up the tree and a second spark copy are
  both "the project's" (N13, N24, N27).
- **One exit code means two things in one script.** `boards.py` maps every `BoardError`, "no selection" included, to 1
  (`boards.py:537-539`). `init`'s "nothing to do" → 1 is not a second case: `NOTHING_TO_DO` is one of the aliases
  `outcomes.py:9-11` names as "fine as a local name for 'ran, and the answer is no'", so it is the written design, which
  the PO may change (Q25) (R2, §1 row). `check_vendor_pins` adds a fourth *status word*, `mismatch`, to its JSON
  (`check_vendor_pins.py:230`) while its exit code is the shared 1 (TECH-LEAD-2; R1, §1 row 16).
- **The acceptance bar over-counts.** `tools/mutate.py` scores a mutant that no longer imports as caught (K53; E
  `tools/mutate.py:88`).
- **The cost line's last window never closes**, so the number grows on each read, and one `--step` outside Claude Code
  spoils a project's tally for good (E `docs/observations/INDEX.md:210`, E16b, "verified", "not yet a named item";
  R1-Missing 7). The transcript reader cuts a line at U+2028 (`cost.py:110`); the halves are counted as unreadable and
  the count is printed (`cost.py:274-275`, `parts.py:2154`), so that undercount is signed, though the line never says why
  (R2; the catalogue's K62 grade "with no sign" is wrong).

### Documentation faults

19 of the 74 rows are documentation faults alone, 12 are documentation and code together (DOCUMENTATION-1). The ones
that matter: no page holds the board file's schema though one page says another does (K24, K25, K26; DOCUMENTATION-9);
"a stand-in costs only the silkscreen labels" (K32 — true of GPIOs, false of two names, FB-M9); three pages, two orders
for `init`, and a sentence that blames the person (DOCUMENTATION-10); six literal store paths in the pages agents follow
(K58; DOCUMENTATION-11); the owed facts restated six times and wrong at one row (DOCUMENTATION-12, G2); `--describe`
wrong in three places (K57); README's one typed block ends in a predicted exit 2 (K69); README's "What works today" says
Build **works** (`README.md:73`) while a design spending MOSI or MISO on the library S3 cannot build (K23) and a numeric
label passes every check (K22) (G3); no page says what a store mistake looks like — the half of the journey where every
P100 walk stalled (DOCUMENTATION-8); a page cites a closed card as the plan for an open gap (DOCUMENTATION-6);
`commands/idea.md:11` sends every `/spark:idea` run to "docs/2026-10-04-store-design.md §8 S and M" (DOCUMENTATION-18);
no page says how to replace a board or a module in the simulation (STORE-12); `GLOSSARY.md` (416 lines) is outside the
docs gate (`tools/check_docs.py:32`); `agents.md:85-86` tells an agent to "use a scratch `SPARK_HOME`" and not to make
its folder, which CH-1's refusal would then stop (R2, CH-1 row). Two open cards already hold part of this: P181 (#127)
for `how-it-works.md` agreeing with itself and `agents.md`'s JSON row, P182 (#128) for README's first screen.

### Data faults

91 of 110 drawer entries say nothing of what they do, so no need reaches them (K36; E the needs diagnosis's count, its
verifier's re-count, round 2's re-count on its copy); every researched record arrives owing `pin_order_proof` and
`simulation` (K37); the XIAO lacks header geometry and `power.io_volts` (K30), and has no `wokwi_is_stand_in` key at all
(R2, CH-32 row); no board record states `function` (K31); five keys of the S3 file are read by nothing (BR-M3); the S3
record's own stand-in note omits that GPIO43/44 are `TX`/`RX` there (FB-M9); irrigation's `irrigation.requirements.json`
and rc-car's two files carry another name than the writer reads (NM-M6, RISKS-20); irrigation's `rules.json` says its
four hand-typed entries were "seeded" (CC-MC-2). In the PO's store the S3 and the LiPo are held by the bin by hand: the
bin has no `needs.json` and no history line names it (E the second version's read: five listed projects, only
plant-alarm's `.spark/` holds a `needs.json`; `history.jsonl` 8 lines, all plant-alarm; six entries carry `used_in` — R1
re-read the six and the 8 lines on its own copy). The store's top folder holds a file no place names:
`b12-kept-from-the-bin.jsonl`, 6,575 bytes, mode `0644`, dated 2026-10-04 (E my `ls -la`; R2-Missing 7) — B12's URL
proofs for the documents moved out of the bin, written by hand (E `scrum/PRODUCT_BACKLOG.md:1081`,
`docs/2026-10-04-store-discovery.md:123`); `PLACES` does not name it (`store.py:61-63`) and no script writes it, so
`--audit` and any sync see it as nothing. Not a fault, for CH-9: on the second version's copy no two of the 103 drawer
entries that carry a `part_number` share it with the same `from`, and 0 of the 12 entries with an `is` link share one (E
`python3 -I` over `<scratch>/p158/synth-2/store`, 2026-10-10; round 2 re-read both on its own copy).

### Things that work as designed but mislead — and whether the design should change

| what | by design because | change the design? |
| --- | --- | --- |
| a green build exits 0 with "— but not every need is on the board" (★C7) | `check_spine.py:536`; D the PO 2026-10-08 (#94) | no; the note prints in every outcome, as the JSON already does (CC-C9, folded into CH-38) |
| irrigation's chain exits 1 for life on its one declared signal (STATUS_LED) | `how-it-works.md:37` | **yes** — severity by content (CH-38) |
| `--tally` exits 2 outside a Claude Code session | could-not-run, never 0 (`cost.py:47`) | no for the exit; README's typed block stops ending in it (CH-43); the window and the spoil are faults (CH-64) |
| `--tally` says "N lines of the transcripts could not be read and are left out of the count" | counted and said, never dropped (`cost.py:105-106`, `:274-275`) | no; the reader stops making those lines, and the line says why a line is unreadable (CH-58, tier 4) |
| `check_all` after `init` exits 2 "could not look" | nulls are the output (`init_project.py:16-21`) | no for the word; **yes** for the sequence, and an empty rule list needs a decision (CH-39, Q4) |
| a board pick with no board file is reserved, recorded, then refused at `--requirements` | warned at the pick by design (P100 refuter) | the PO's — CH-24's pick half (Q11) |
| an unknown id is `problems`, exit 1 | §6.4.1, D the PO 2026-10-04 | the PO's (Q14); a `kind` word removes the ambiguity either way (CH-46) |
| a gap is `ok` | §6.4.1 | no; the answer must say where it looked (CH-1, CH-18, CH-19) |
| `[other words]` is honest | the agent judges fit (§5.6) | no; it needs a legend where it prints (CH-52) and a record of the fit (CH-17) |
| `? V33: draws 355 mA of 1.50 A` | the module's radio peak, verified (`boards/firebeetle2-esp32s3.json:393-399`) | no; the line carries the source of every figure (CH-44) |
| the S3 and LiPo are held by the bin | D the PO ×3 (RISKS-9) | the PO's (Q5); CH-72 shows the hold, CH-25 changes only the cost of releasing |
| a local exit-code alias (`EXIT_MISMATCH`, `EXIT_INVALID`, `EXIT_NOTHING_TO_DO`, …) | `outcomes.py:9-13`, which names `NOTHING_TO_DO` among them | no; only `boards.py`'s "no selection" adds a meaning (CH-21); whether `init` run twice should be `ok` is the PO's (Q25) |
| a dry run of a writing operation takes the store's lock | `parts.py:2198-2200` takes it for every operation that declares `writes` | **yes**, once the lock sits in the store: a dry run writes nothing and takes no lock (CH-3) |

### What this list does not fix, and what nobody examined

**Not fixed here, on purpose:** K42 (research only the gap, §8 G; #99 P162), K43 (the ways in beyond goal-first; #5 P76),
K44 (choosing among equivalent owned modules; #93 P157), K49's one-MCU limit (P158 part 2), K64's split of `parts.py`
(Q12), and N12 — the bin's own tracked `.spark/cache/*.h`, which nothing reads and its refresh target rewrites (#125's
council: "the bin's to decide"). Q40 asks whether K42–K44 belong in part 1. **Not examined by any diagnosis or lens**, so
"no row" is not "no fault" (the critic's list, E its grep of the first version: 0 mentions each): the review and
fabrication path (`skills/spark-review`, `agents/design-reviewer.md`, `scripts/check_bom.py`, `check_footprints.py`,
`fab.py`, `copper.py`), `skills/spark-reverse-engineer`, `commands/identify.md`, `agents/part-finder.md`, `chips/`,
`DECISIONS.md`, and `data/importers/dfrobot.js` — the importer D8's "automatically from the DFRobot orders" starts from,
which returns only `{sku, name, count}` per product by design (E `dfrobot.js:5-6`). They belong to P158 part 2 or a later
council. Also not run by anyone: the bin's `make check` against any change (it writes inside the bin), a full mutation
sweep, a person typing (Q26), and a test-suite run with CH-1's refusal in `home()` (how many tests need a `mkdir`: —).

## 2. The refactoring direction

The criterion (D the PO, 2026-10-10): a mistake lands in one named place with one named reason, for a person and for an
agent reading the same output. Read that way, the 74 rows are not 74 bugs but a few shapes repeated: a fact or a sentence
stated in several places, a reader or writer that bypasses the one door, a severity decided by a channel or a substring,
and an answer that does not say where it looked (TECH-LEAD-1…-3; FEASIBILITY §2.3's nine clusters). The smallest
structural set that removes those shapes is eight changes; every other change in §3 is a fix inside a shape, not a new
shape.

### 2.1 Eight shapes, each with one place and one reason

| # | the one place | what it replaces | the one reason it prints | argued by | ranked as |
| --- | --- | --- | --- | --- | --- |
| R1 | `store.home()` refuses, on every call — read, dry run or write — a `SPARK_HOME` that is set but empty or names no folder (checking `inside_git` first, so the git sentence stands), and names the folder it would otherwise use (`XDG_DATA_HOME/spark` or the default); `tools`' call-time `personal()` and `downloads()` re-raise that refusal as a `ToolProblem` naming `SPARK_HOME`, so every existing `except ToolProblem` says it instead of a traceback; every answer carries `store`; no module reads a home at import | the truthiness fall-through at `store.py:48`; `tools.PERSONAL`/`DOWNLOADS` computed at import (`tools.py:47-48`) | `SPARK_HOME names <path>, which is not a folder …` / `in store <path>` | SL-C1 + SL-M1; TECH-LEAD S6, `tech-lead.md:64-65`; UAA-M-C; UH-M-b; R1 (CH-1 row); R2 (R1 and CH-1 rows: the traceback through `tools`, the `XDG_DATA_HOME` fallback) | CH-1 |
| R2 | the person's data is written only through the store's door, under one lock beside the data (`<home>/.lock`), or into the person's project; spark's own folder (one `plugin_root()`) is written only through one helper, and only when the operation names the file as spark's own artefact — the header of a board whose resolved file is one of spark's own `boards/*.json` (#125's rule, with "shipped" read from the file, not from where it sits), or a library chip's compiled binary; anything else is refused at run time, naming the path and the operation | the temp-folder lock; `init`'s unlocked write; `tools.py:445`'s plain write; `--promote`'s copy into the plugin library (`parts.py:1296`); five module-level spellings of the plugin folder; the second version's test-time write map, which saw only what the suite wrote and allowed the very path N25 and N26 reach (R2) | `called with no lock held` / `refused: <path> is inside spark's own folder, and <operation> names it as no artefact of spark's — a person's data goes into the store or the project` | SL-C3; SL-M4; TECH-LEAD-4, -13, S2; FE-MISSING-4; FEASIBILITY cluster C; R1 (R2 row); R2 (R2 row, CH-4 Mechanism); N14, N28 (#125's council: "writes that refuse spark's folder unless asked") | CH-3, CH-4 |
| R3 | one reader, `outcomes.read_json(path, what)`, raising one exception every `main` maps to could-not-run, reading UTF-8 | 37 raw reads in 16 scripts, seven readers with five exception classes, `_parse`'s silent `None`, the requirements writer's own loader, `design.read`'s locale decoding | `<path> is not UTF-8 at byte N` / `is not JSON: …` / `holds a list; … is an object` | SL-C8; CC-C5; TECH-LEAD-1, S1; EXISTING-FIRST-9 (the 2026-09-30 target 3); FEASIBILITY cluster A; R2 (CH-6 row) | CH-5, CH-6 |
| R4 | identity by the thing: a project id in a file of its own that every operation listing a project writes (never `.spark/project.json`, which is the person's brief, `init_project.py:24`); plain keys enforced on read; two drawer entries with one vendor part number named; labels in one Unicode form; one `based_on` shape on every copy, its digest over the whole record less `SHELF_DROPS`, and a reader that compares a copy with its source field by field and says which side moved | identity by spelling (folder name, file stem, raw label); digests written and read by nothing; two `based_on` shapes; a copy digest over six build facts, which cannot see a stand-in change or tell a moved source from an edited copy (R2) | `carries the id of listed project X` / `not a plain key (a conflict copy?)` / `two entries, one part number` / `differs from its source in <fields> — the source changed since the copy` | SL-C5, SL-C7, SL-M3; TECH-LEAD-9, S3; FEASIBILITY cluster D; STORE-15; R1 (R4 row, CH-26, CH-29); R2 (CH-26 row) | CH-9, CH-10, CH-26, CH-63, CH-29 |
| R5 | one table of facts per record kind — the owed-facts table (fact → stage → consequence), `PHYSICAL_KEYS`, `PIN_ROLES`, and one chip-name table (spark's `esp32s3` ↔ Wokwi's `mcu` `esp32-s3` ↔ the part type `board-esp32-s3-devkitc-1`) — that the docs, the skeleton, `BUILD_FACTS`, the stand-in check and a schema read; and **one home per sentence**: the code prints it, the pages point at it, and a retired sentence is kept out by a check that reads pages and printed strings | `CHAIN_FACTS` as a flat list with five readers deciding its consequence; `_about`'s regex over problem sentences; a board contract "enforced rather than documented"; a sentence restated in nine places; two chip spellings compared by nobody | `owes X — the <stage> stops` / `physical.<key> is read by no script` / `<type> is not in data/wokwi-boards.json — could not look` / `<page>:<line> says a retired sentence: "…"` | CC-C4 + CC-MC-3; BR-C3; TECH-LEAD S5; FEASIBILITY clusters B, E; DOC-M-D5; G14; EF-MISSING-8, FE-MISSING-8; R2 (Missing 4, CH-13 row) | CH-13, CH-22, CH-37, CH-41, CH-28 |
| R6 | one answer shape: `outcomes.envelope` from every `--json` script, carrying `store`, a closed `kind` per item, a filled `next`; an `Answer` holds each class of line in its own field (`lines`, `notes`, `conflicts`, `kept`), and both printers render every field, so a line cannot reach the text without reaching the envelope; a source is named by its folder | five JSON shapes (TECH-LEAD-11); the text withholding `fix`; notes appended to `lines` only, so the envelope drops them; the vendor-pin check's two shapes for "whose copy" | — (it carries every other reason) | TL-M-B; UAA-M-A, -M-B, -M-D; UH-M-a; R1 (CH-16 row); R2 (CH-16 Mechanism: one field per class of line); N13 | CH-16, CH-21, CH-46, CH-73 |
| R7 | severity from content: the generator's notes are a value with a kind, the converter answers in JSON | `check_spine.py:374-375` (any stderr line is "the chain is broken"); `CONVERTER_HAS_NO_PART`, a pinned substring | `<signal> of yours assigned and left for you to wire` / `the stand-in <part> has no pin for GPIO<n> …` | CC-C2; TL-M-A; FB-M8; TECH-LEAD-3 | CH-38, CH-31, CH-46 |
| R8 | exit codes from `outcomes.EXIT_FOR`; a local alias of the middle code stays — the written design, which names `NOTHING_TO_DO` among the aliases (`outcomes.py:9-13`); the one mapping that adds a meaning — `boards.py`'s "no selection" → 1 — goes, pinned by a test; a JSON `status` is one of the three words | `boards.py:537-539`; `check_vendor_pins`' `mismatch` in its JSON status (`:230`) | three statuses, one meaning each | TL-M-D; CC-MC-8; R1 (R8 row, CH-45); R2 (§1 row on `init`) | CH-21, CH-45 |

### 2.2 What is removed or merged

Removed (each is ranked in §3): `promote`'s project → plugin-library branch and `LIBRARY` as its write target for a
project record (`parts.py:1296`; CH-4) · the plugin write `check_vendor_pins` made when the board's project held no copy
— **done by #125**, merged 2026-10-10 (D) · the lock file in the temp folder (`store.py:187`; CH-3) and the lock a dry
run takes (`parts.py:2198-2200`; CH-3) · the home read at import in `tools.py:47-48` (CH-1) · four of the five
module-level definitions of the plugin folder, in favour of one `plugin_root()` (CH-4) · `needs._called` and
`needs._name_after`, folded into one `component_name` in `design.py`; the silent replacement of a non-object
requirements file (`needs.py:612`) (CH-6) · every store-file reader's own `json.loads` and `_parse`'s quiet `None`
outside link-by-number (CH-5) · `_about`, `needs.LAYOUT_FACTS`, the comment "no build can place it" (`parts.py:97`) and
every copy of "builds with it" (`parts.py:1631`, `:2088`, `commands/idea.md:141`, `journey.md:468`, `:497`) (CH-37) ·
the stderr → PROBLEMS rule and the `note:` prefix as a contract (CH-38) · the second spelling of the stop sentence
(`needs.py:511-512` against `parts.py:1920`; CH-66) · `footprint_module` and the four keys of the S3 file no script
reads, unless given a reader (CH-22) · the hand-written-file procedure for freeing a hold (`needs.py:250-257`,
`idea.md:96-98`; CH-25) · "fixed by hand in `needs.json`" (`idea.md:25-26`; CH-50) · "after a build, run `init` again
with `--force`" in its nine page places and in `init_project.py:485`'s printed line (CH-39) · the README block's
`--tally` line (CH-43) · `build.md:80-90`'s second pasted copy of a chain run (CH-41) · the six literal store paths in
agent and command pages (CH-48) · the one exit-code mapping that adds a meaning (CH-21) · `agents.md:297-333`'s
exception list, row by row as CH-46 lands · `boards/README.md`'s bin-specific steps (#61) and, once CH-24 lands, the
five-step hand route for a board · the temp work folder's line in `check_spine` (CH-71) · `str.splitlines()` in the
transcript reader, for the history reader's byte split (CH-58).

**Kept, against the first version** (R1): `wokwi_is_stand_in` — it is the one fact that says whether a stand-in is in
use, so CH-32 gives it a reader instead of removing it; the key name `wokwi_power_pins` — the bin's own converter copy
reads it (`~/Development/smartbin-local/tools/circuit-to-wokwi/lib/mapping.ts:108`), so CH-31 documents it instead of
renaming it. **Kept, against the second version** (R2): `init`'s `EXIT_NOTHING_TO_DO` alias, which `outcomes.py:9-11`
names (the PO may change what `init` run twice answers, Q25); `BUILD_FACTS` as it is — it vouches for a build, which a
stand-in does not change, and CH-26's copy digest is another digest; the commit gate's archived-tree run (P172) as it
is, with no write map added to it (R2: the run-time helper of R2 replaces the map).

Added, and nothing else: a project id; one reader and one exception; a `store` field, a `kind` word and a filled `next`;
one field per class of line in an `Answer`; one `based_on` shape on every copy, parts and boards, its digest over the
whole record, and one reader of digests; a copy verb for boards; one `plugin_root()` and one write helper for spark's
own folder; a generated copy of the Wokwi part registry, tested equal to the converter's, and one chip-name table of
each Wokwi board's `mcu` and spark's spelling of it under `data/`, each with its version and source; a `held by` column
in the drawer listing; the hold operations (if holds stay stored, Q1); a recorded `fit` on each need, with the needs
file's schema 2; a promoted recorder; a closed-card and a retired-sentence check in the docs gate; one key naming the
folder whose header answered in the vendor-pin check; contract tests for the bin's other spark calls.

### 2.3 The store's levels, holds and paths as one explicit thing

- **One layer table, with the column the design asked for.** `store.layers()` today is a literal list of `(layer, path)`
  with `if kind == "parts"` branches (E `store.py:71-81`); the store design asked for each row to say "whether it is
  writable" (`docs/2026-10-04-store-design.md:274-275`). The table becomes the one statement of the levels: per row the
  kinds it holds (parts, boards), its place, who may write it (spark's maintainer by pull request, the person through
  `parts.py`, nobody), whether it is private, and the read order. "Where a record goes when it has proven itself" is then
  read from the table, not chosen per writer (FEASIBILITY-14; FE-MISSING-2; STORE-1). Boards gain a row in the person's
  store (CH-27, a decision: Q8); a read-only `shared` row comes with P178 (CH-29).
- **Two kinds of write, one rule each, enforced where the bytes go.** The person's data — drawer, shelf, catalog,
  history, projects list, kept documents, a project's own records — goes through the door into the store, or into the
  project, and never into the plugin, because an update replaces the plugin folder and the person is told nothing (K12).
  A regenerable artefact of spark's own — the vendor header of a board spark ships, the compiled binary of a library
  chip — may be refreshed in the plugin, because losing it costs a refetch or a recompile and nothing of the person's:
  this is #125's rule, read here as the general one. What changes (R2, Mechanism; #125's council, N14 and N28): "a board
  spark ships" is decided from the board file itself — its resolved path is one of the plugin's own `boards/*.json` —
  and not from the folder it sits in, and the decision is made by one helper every writer into the plugin calls
  (`promote`'s `copy2`, `check_vendor_pins`' `write_text`, `sim_project`'s `copy2`), with the door's own `_make_ready`
  refusing a store target under `plugin_root()` (a `SPARK_HOME` set inside spark's tree). An unmarked folder inside
  spark's tree (N25) and a symlinked board file (N26) are then refused at the write, with a sentence, instead of being
  caught — or not — by a test. Chip identity and name clashes stay P149's and P150's (#83, #84; K13).
- **Paths.** One `home()` and one `plugin_root()` — the plugin folder is defined at module level five times today (E
  `boards.py:38`, `:153`, `parts.py:45`, `store.py:33`, `tools.py:43`; TECH-LEAD-4 counts seven spellings) — and one
  `boards.project_root` for "which project owns this path", which #125 already made the owner for the vendor header
  (N3); every answer that used it names the folder it found (N24, N27; CH-73). The second version folded this into a
  rule "since no K row needs it"; #125's council has since raised it for P158 by name (N14, N28), so CH-4 carries
  `plugin_root()`. No module reads a home at import — `tools.py:47-48` does today, and once `home()` can refuse (CH-1)
  that read would raise at the import of four scripts, before any `main` can turn it into a sentence; at call time it
  would still pass through every `except ToolProblem` as a traceback unless `tools` re-raises it as one (R2, R1 row) —
  so CH-1 does both. A test imports every module under one `SPARK_HOME`, changes it, and asks every path function again.
- **Holds.** A stored decision, released by an operation and audited against each listed project's picks (my lean in §6,
  split 1, because two of five listed projects hold or would hold parts with no `needs.json`); shown in the plain listing
  whichever way Q1 goes (CH-72); a hold is per-machine state that a shared store never carries (TECH-LEAD-9). The release
  can reuse the path a pick already runs: a pick re-derives the picking project's holds and releases any that no pick
  explains (`needs.py:326-331`, said as "released … — no pick of this project explains it", `parts.py:2013-2015`;
  R1-Missing 11; R2 holds).
- **Three relations, three mechanisms** (STORE-8). Shared ↔ local carries records only, through git (D the PO
  2026-10-04: "a public repo of records … cloned read-only … at a pinned commit",
  `docs/2026-10-04-store-discovery.md:209-211`). The person's own machines are the person's choice — a private git
  remote or a folder sync — and spark's job is to survive a folder sync: conflict copies refused by name on read (CH-9;
  Syncthing's naming fails `PLAIN`, E STORE-16; Dropbox's and iCloud's, H `existing-first.md:258-259`). Two limits, said
  plainly (R1, §2.3 row): `flock` serialises the processes of **one** machine, so two machines writing one synced store
  at once are kept apart by nothing but the conflict-copy refusal; and a private git remote holding the drawer, shelf,
  projects list or history is refused today (`store.py:211-214`; FEASIBILITY-19), so it needs Q28 (b) and `inside_git`
  scoped to a project's work tree (EF-MISSING-3). Local ↔ project is a copy pinned to its source by a digest, a lockfile
  `--audit` reads (STORE-15; CH-26, CH-63). The real store is not in a synced folder today (E the critic: `realpath
  ~/.local/share/spark` → itself, mode `drwx------`). What a sync would carry needs a list too: a file at the store's
  root that no place names (`b12-kept-from-the-bin.jsonl`, §1) is invisible to `--audit` and to any rule written per
  place (Q45).
- **The PO's format and sync question, answered once.** No new file format: one JSON file per record (137 files, 319,145
  bytes on the copy — E FEASIBILITY-5, `feasibility.md:59`) and an append-only JSONL. Git's union merge "tends to leave
  the added lines in the resulting file in random order" (STORE-17, gitattributes 2.56.0); no history reader traced
  depends on line order — `cost.windows` orders steps by their start time (`cost.py:200-212`), `store.recorded` compares
  event keys (`store.py:308-311`), `_op_tally` uses membership (`parts.py:2141-2149`) — and whether `--step`'s listing
  reads order is — (the critic's code read). So `history.jsonl` is safe under a union merge as far as traced, and
  CH-70's experiment settles the rest. No sync library: SQLite's own page warns of network file systems and of
  background copies taken mid-transaction (RISKS-17, FEASIBILITY-6, fetched 2026-10-10); CRDT libraries (pycrdt,
  Automerge) merge live concurrent edits, which a one-writer store with pull-request review does not have, and bring
  compiled dependencies (FEASIBILITY-9, STORE-14); Dolt, CouchDB/PouchDB, ElectricSQL, git-annex/DVC/git-lfs each solve
  another problem or the forbidden half (STORE-14's survey table). Git carries the shared layer and is already required.
  For "rules and editor": a JSON Schema per record kind, generated from spark's own tables and mapped in VS Code, gives
  validation, completion and hover with nothing installed (FEASIBILITY-8, EXISTING-FIRST-23) — spark's validators stay
  the enforcer and their sentences the message (CH-28). What any transport needs first is R4 plus a tombstone
  (FEASIBILITY §2.2): without them every transport corrupts quietly.

### 2.4 Exit codes and outputs a person and an agent read the same way

Three outcomes stay, defined once (`outcomes.py:19`; W1). On top: exit codes from the table, local aliases kept, the one
mapping that adds a meaning changed and pinned by a test (R8, in CH-21; `--get no_such_field` stays exit 1, which the
bin's contract test pins, `tests/test_boards.py:366-369`); one envelope from every `--json` script with `store`, `kind`
and `next` (R6); an `Answer` that holds notes, CONFLICT lines and kept files in fields of their own, which both printers
render, so nothing the text says can be missing from the envelope by construction — one test per field instead of one
per omission (R2, CH-16 Mechanism); every `fix` and `next` printed in text (UAA-M-B, UH-M-a); every search says where it
looked and how much it could not look at (UAA-M-C; CH-18, CH-19, CH-21); every figure a check prints names its record
key and the source or the "unverified" of each figure (UH-M-c; CH-44); a source of a fact named by its folder, never by
"the project's" alone (CH-73); one outcome-invariant test — every `main`, fed a non-UTF-8 file, a list where an object
belongs and a missing path, exits 2 with one sentence naming the path and no traceback (TL-M-H; in CH-5) — whose first
case, every `main` under an empty or missing `SPARK_HOME`, lands with CH-1 (R2).

### 2.5 Module boundaries and test seams

The layers the tech lead proposes, a module importing only from a lower one: 0 `outcomes`, `fab`, `netlist`, `copper` ·
1 `store` · 2 the record contract per kind with the owed-facts table and the digests, and the documents · 3 board
selection, `design` (which takes `component_name`), `assign_pins` · 4 `emit_board` (returning text and notes),
`emit_footprint` · 5 `drawer`, `needs`, `cost` · 6 the commands. Today's crossings: `parts.py` (layer 2 by content)
imports `drawer`, `needs`, `cost` and `tools` inside functions (22 function-local sibling imports, R1 recounted 22);
`boards` imports `emit_footprint` for the stop rule; `needs` holds a copy of `component_name` (TECH-LEAD-5); and CH-18
as the second version wrote it would have added one more — `parts.py` importing the private `needs._words` — so its word
splitter moves to layer 1 (R2, CH-18 row). The move of `parts.py` into contract / documents / CLI is **not** proposed
now: 266 mutation anchors sit in `parts.py` and 196 in `needs.py` (FEASIBILITY-2; R1 recounted 462), the 2026-09-30 note
said "do not refactor" for that reason (EXISTING-FIRST-12), and no K row needs it (TECH-LEAD §2) — Q12 asks the PO.

The test seams, each one test that holds for every future module: (1) the outcome invariant; (2) one envelope shape in
`tests/test_json_contracts.py`, and one test per `Answer` field that text and envelope both render it; (3) **the write
guard, at run time**: one helper refuses a write inside `plugin_root()` unless the operation names the file as spark's
own artefact, and its tests are the cases #125's refuter named — an unmarked folder inside spark's tree (N25), a
symlinked board file (N26) — plus a promote from a project, a chip compile and a shipped header's refresh (R2: the
second version's map over the commit gate's archived tree saw only what the suite wrote, and its allow-list admitted the
shipped-header path N25 and N26 reach); (4) an import-direction test over the layer list; (5) the home test (§2.3); (6)
lists in prose equal lists in code (DOC-M-D5); (7) the mutation anchors at every push, plus a dated full sweep per epic
once `mutate.py` stops counting a non-importing mutant as caught (CH-2); (8) **the sibling projects' command lines as
spark tests** — `TheCommandLineTheSmartBinDependsOnTest` (`tests/test_boards.py:312`, P41) already pins the bin's
`boards.py` calls; CH-68 adds its `check_vendor_pins`, `check_physics` and `check_bom` calls (RISKS pre-mortem 6). P41's
`test_validate_and_validate_for_fab_both_answer` accepts exit 0 or 1 (`tests/test_boards.py:378-382`), so it cannot see
the bin's Gerber recipe go red; CH-36's scope test is that recipe's only guard (R2).

### 2.6 Recorded documents that a check can hold

The rule every page rests on is "a pasted output is real" (`docs/2026-10-05-readme-design.md:80-82`), and its only
mechanism is a hand paste that did not happen at three releases (DOCUMENTATION-2). The shape: promote the recorder that
exists untracked under `.superpowers/` (DR-M1, DOCUMENTATION-3) instead of writing a third; bind each recorded block to
its command and its store state explicitly (8 or 10 of 42 blocks sit under no command — two counts: DR verify M2 counted
8, `.verify.md:194`, DOCUMENTATION-17 counted 10; the difference is —); two classes of block, re-recordable and
recorded-only (the 2026-10-05 blocks ran on the real store, DOCUMENTATION-15; DR-M3; `developing.md:120-153` reads live
boards); `--check` in `tools/check_commit.py` on a commit that changes `.claude-plugin/plugin.json`'s version, because
no release gate exists (DR-M4, FEASIBILITY-16); the version count as a report line, never a failure (DR-1 as judged by
all lenses); the gate reads the pages agents follow and `GLOSSARY.md`, names a page by its path (DR-M7), keys an output
on its note, names a cited card that is closed, keeps retired sentences out, and keys its version check on the version
line, not on "v0.8.1 anywhere in README" (CH-40, CH-41; DR-M5). One rule in `developing.md`: a sentence that documents a
fault names its card, and the card's close deletes the sentence (DOC-M-D7). And one rule for every card of the epic, the
PO's of 2026-10-10 (D, quoted on #126 and #128): before every pull request the documentation experts check that the
pages the change touches are up to date, understandable, readable and — for README — tempting first, with examples, then
details, with the specifics on linked pages; P180 (#126, PR #129) writes it into `scrum/README.md` (R2-Missing 3).

## 3. The prioritised change list

**The priority rule, stated once and then applied.**

- **Tier 1 — faults that harm or mislead silently.** *Silent*, defined so it can be checked: the answer's status or exit
  says success (`ok`, exit 0, "wrote", "caught") while what it reports is false, or leaves out a fact it read or holds
  about the very thing it reports, and nothing in that answer says so — a merged netlist every check passes, an empty
  store read as "not owned", a cache written into the plugin, "1 owned" for a board another project holds. A traceback,
  a refusal, a non-zero exit or a line naming the problem is a **sign**, and a signed fault is tier 2 or lower (R1, "The
  order"). The clause "leaves out a fact it read" replaces the second version's "incomplete", whose boundary depended on
  which omissions one counted (R2, "The order" 2); Q43 lets the PO narrow it to false results only.
- **Tier 2 — what blocks the documented journey for a person or an agent**, opening, as the brief asks, with the PO's
  emphasis of 2026-10-10: block A, the basic store — global vs local; create, search, update, copy and share; boards
  first — and block B, replacing a board or a module in the simulation, each change marked **fix now** or **P178
  concept**. A change of those blocks that fails silently is ranked in tier 1 and named in the block's table.
- **Tier 3** — wrong or unverifiable verdicts, numbers and documents. **Tier 4** — friction. **Tier 5** — polish.

**Inside a tier, in this order, every key stated** (R1 and R2 each found the order resting on a rule it did not state;
the keys below decide every pair, and each block's "why this rank" names the key that placed it):

- (a) **the brief's rule:** the change that unblocks the most others first — counted as the **hard** prerequisite edges
  into changes **of this epic**: a soft edge blocks nothing (the dependent ships and prints one sentence less), and a
  P178 concept goes to #123's discovery, not to this epic, so edges into concepts are listed on the block but not
  counted (R2, "The order" row on the counts). (a2) Between equal counts, the soft in-epic edges break the tie;
- (b) **the brief's rule:** a removal before an addition — a change whose kind is `remove`, or whose fix is to delete,
  merge or stop something, before one that adds;
- (c) **mine, stated so it can be struck (Q42):** the harm if it lands late, in three classes and no order inside a class
  — (1) a circuit, a simulation or the person's data wrong; (2) an answer or a verdict wrong; (3) a count, a number or a
  document wrong (R2: the second version ordered simulation, circuit, layout and data inside class 1 by a rule it did not
  state);
- (d) **mine, stated (Q42):** who has met it — a harm a card or a round records (#101's twelve projects, round 0's stray
  header, PO-6's paid run, K47's PO), before an agent's run (the catalogue's "an AI agent at the keyboard"), before a
  code read only (its "nobody — reasoned only");
- (e) **the PO's own words** where they name an order — D8, 2026-10-09: *"we want to start by the boards"*; 2026-10-10:
  *"the boards for sure"*;
- (f) **mine, stated (Q42):** reach on the PO's machine today — a fault that needs a condition his setup lacks (a synced
  folder, a second machine, no `fcntl`) after one that does not;
- (g) the catalogue's order of the change's first K id, so that no pair is left to judgement.

**After the keys, one constraint** (R2, "The order" 1): a change never ranks above its own hard prerequisite. Where the
keys would put it there, the prerequisite moves up to sit right before it when the dependent is the PO's named first fix
(key (e): CH-23 moves up to sit before CH-24, D8's board skeleton), and otherwise the dependent moves down to sit right
after its last hard prerequisite (CH-28, a P178 concept, sits after CH-37). A soft prerequisite may rank lower; the
block then says what it prints until that change lands. §7 lists every edge, and a parser over it finds no hard edge
pointing up.

Enabling work is not a key: a change is not pulled up because others prove themselves with it (R1: the first version
promoted CH-2 for that reason and not CH-40; R2: the second version's CH-1 still said it — the clause is gone). A
decision or a data pass is not a change to the system and has no rank; it is named in each change it gates, and *How the
list becomes cards* at the end of this section says when each is asked.

**How a block reads.** rank · id · title (the fault, then the fix) · kind, size, card (an existing card the epic reuses,
or none), **fix now** / **P178 concept** where it applies · fixes · root cause (a "because …" sentence in plain words,
then the ids) · removes / adds · test (named, runnable in the suite's style; proposed, not written) · prints (the
failure sentence: where and why) · depends on (hard unless marked soft) · unblocks (hard in-epic edges counted; soft and
P178 edges listed after) · the bin, irrigation, plant-alarm (what breaks and how it is handled, with the test that shows
it or the word "reasoned") · proof the PO can read · why this rank (the key that placed it).

**Done, for every change**, beside its own test: a word the change adds to an output gets its `GLOSSARY.md` entry (the
critic, item 4); its card carries its K ids, its test names and its commit, so a fixed row can still be told from an
open one after the line numbers cited here go stale (RISKS-19; #125 already moved lines the second version cited — R2);
"the bin stays green" is claimed only with the test that shows it, or marked "reasoned" (RISKS pre-mortem 6); and before
its pull request the documentation experts check every page it touches against the PO's brief of 2026-10-10 (§2.6;
R2-Missing 3).

**Before rank 1 — decisions and data, no code.** Nine of the PO's questions (§5) gate ranks below: holds stored or
derived (Q1, before CH-25 and CH-29), the real-store guard (Q2, CH-11), `pin_order_proof` owed or broken (Q3, CH-37), an
empty rule list (Q4, CH-39), the S3 for P100's rounds (Q5), the drawer's data pass (Q6, CH-19), irrigation's file name
(Q7, CH-7), the pick's fit as a need field (Q41, CH-17), and the stand-in flag for a person's own board file (Q44,
CH-32). Q32 — merge
#125 — is answered: merged (D). The risks lens ranks the data pass and these decisions above all code (RISKS rank 1;
RISKS-2: one `--drawer-set` of `function` on four ESP SKUs took `--match` for a board from 2 candidates to 6 on a copy,
no code changed); Q5 alone decides whether the PO's round A is blocked by a finding or by his choice (RISKS-9).

### Tier 1 — faults that harm or mislead silently

Order: by the keys above. The **unblocks** counts — hard edges into changes of the epic — top to bottom: 5, 4, 3, then
four with 2, three with 1, fifteen with 0 (R2: the second version's "7, 5, 5, 4, 4, 3 …" counted soft edges and edges
into P178 concepts as unblocking). By §3's definition of silent, two changes left this tier — CH-57 to tier 3, CH-58 to
tier 4 — and one joined it, CH-72, the half of CH-25 that needs no decision (R2).

#### 1 · CH-16 · The JSON drops what the text says, and the text drops the fix the JSON carries — each class of line a field of the answer that both printers render, and every fix and next printed

- **kind** story · **size** S–M · **card** #58 (P124)
- **fixes** K55, K56 (all five halves, with G6); USER-AI-AGENT-1, -2, -6, -8; USER-HUMAN-3, -7 · **root cause** because
  the text and the JSON are printed from one answer by two printers that each leave something out: the text prints a
  `fix` only when there are no lines (`parts.py:2182-2184`), and the pick's notes, `--show`'s CONFLICT lines
  (`:1459-1461`), `--unverified`'s open facts and `check_spine --keep`'s kept files (`check_spine.py:682-684`) never
  reach the envelope (USER-AI-AGENT-1…-3)
- **removes / adds** `Answer` gains one field per class of line — `notes` (the pick's and `--requirements`' notes),
  `conflicts` (`--show`'s CONFLICT lines) — and `--unverified`'s open facts go into `unchecked`, which exists;
  `check_spine`'s answer gains `kept: [{file, left_alone|wrote}]`; both printers render every field, so a note can no
  longer be appended to `lines` alone and reach the text without the envelope (R2, Mechanism: the second version tested
  nine omissions one by one, and a tenth appended to `lines` tomorrow would be dropped again with no test to see it). In
  text, every problem's `fix` and every `next` under the answer's lines (UH-M-a). And K56's four other halves (G6): a
  refusal with no lines names its subject; a note is said once, not for every untouched pick; a `skip` drawer entry
  reads as skipped, not "to get — known, not owned"; an id with capitals is refused saying ids are lower-case. The
  vendor-pin check's two shapes for whose copy answered are CH-73's (N13).
- **test** one per field, not one per omission (R2):
  `test_parts.py::test_each_answer_field_reaches_both_the_text_and_the_envelope` (a subTest each for `notes`,
  `conflicts`, `unchecked`); `test_check_spine.py::test_kept_reaches_both_the_text_and_the_envelope`;
  `test_parts.py::test_a_refusal_with_lines_prints_its_fix_in_text`; and K56's halves:
  `::test_a_no_line_refusal_names_its_subject`; `::test_a_note_is_said_once_for_untouched_picks`;
  `::test_a_skip_entry_reads_as_skipped`; `::test_an_id_with_capitals_is_refused_saying_ids_are_lower_case`.
- **prints** the held-board refusal in text gains its line: `refused, so nothing was written: firebeetle2-esp32s3 — 1
  owned, held by smartbin-local — 1 picked here — free it: …` (the command once CH-25 lands); `--pick --json` carries
  `notes: ["dfrobot-dfr1075: a board needs a board file — …"]`.
- **depends on** — · **unblocks** 5: CH-17, CH-25, CH-35, CH-46, CH-48
- **bin · irrigation · plant-alarm** none runs these in its build — reasoned.
- **proof** USER-AI-AGENT's J10 envelope contains "board file"; USER-HUMAN's run 5 prints the fix in text.
- **why this rank** tier 1: for an agent acting on the JSON, as `agents.md` tells it to, an `ok` envelope without the
  CONFLICT line is a wrong answer with no sign; key (a): it unblocks five changes of the epic outright, more than any
  other change in the list.

#### 2 · CH-13 · Wrong silicon passes silently: a stand-in of another chip validates, and an interpreter built for another chip is packed — refuse both where the facts already meet, through one chip-name table

- **kind** bug · **size** S + S · **card** none · **fix now** (block B; the store lens's S2)
- **fixes** STORE-9; K66's silent half · **root cause** because nothing compares the Wokwi board a record names with the
  chip the record says it is, and the image builder never reads the image's own header, so a copied board file keeps the
  old board's stand-in and a MicroPython build for another chip is packed without a word (`boards.py:62`, `:307-313`;
  `flash_image.py:61-69`; RC-FB-2 as corrected — the bin's script never read a header either). The image half guards the
  symptom; the mechanism, a tools-list role that takes no chip (FB-M4, FEASIBILITY-15), is §4's "not now".
- **removes / adds** `data/wokwi-boards.json`, one row per Wokwi board type — its wokwi-boards folder (the type without
  `board-`), its `mcu` as wokwi-boards spells it (`esp32-s3`) and spark's spelling of the same chip (`esp32s3`) — copied
  from wokwi-boards' `board.json` files at a cited commit (STORE-10; the repository declares no licence, so facts with a
  citation, never its files — STORE-11). It is the one chip-name table, read by this check, by CH-24's per-chip table
  and by CH-33 (R2, Missing 4: compared directly, `esp32s3` and `esp32-s3` differ, and both shipped boards would be
  refused). `--validate` refuses a stand-in whose chip, read through the table, differs from the record's `chip`, and
  names the same-chip candidates; a stand-in type the table lacks is could-not-run naming the table, never `ok`; a
  16-byte read of an ESP image header — magic `0xE9`, chip id at byte offset 12 — in `check_spine`'s simulation stage,
  where the resolved board and `--firmware` already meet, with an optional `--chip` on `flash_image.py` for the
  standalone case (FB verify C2: a `--project` default cannot resolve irrigation's board). The chip ids are cited from
  ESP-IDF's `components/bootloader_support/include/esp_app_format.h` — `ESP_CHIP_ID_ESP32S3 = 0x0009`,
  `ESP_CHIP_ID_ESP32C6 = 0x000D`, `ESP_IMAGE_HEADER_MAGIC 0xE9`, Apache-2.0 (E the critic, Espressif documentation
  search, 2026-10-10), which turns the C6's id from H to E and answers existing-first's licence question for a copied
  table.
- **test** `test_boards.py::test_a_stand_in_of_another_chip_is_refused` (STORE-9's file as the fixture);
  `test_boards.py::test_the_shipped_boards_stand_in_on_their_own_silicon`;
  `::test_a_stand_in_the_chip_table_lacks_is_could_not_run_naming_the_table`;
  `::test_the_chip_table_spells_each_chip_both_ways_once`;
  `test_flash_image.py::test_an_interpreter_for_another_chip_is_refused_before_any_byte_is_written`.
- **prints** `wokwi_part_type board-esp32-s3-devkitc-1 is an esp32s3 (wokwi-boards' mcu: esp32-s3); this board's chip is
  esp32c6 — Wokwi boards with that chip: board-esp32-c6-devkitc-1, board-xiao-esp32-c6` · `<type> is not in
  data/wokwi-boards.json, so its chip cannot be compared — could not look; add its row (type, mcu, chip) from
  wokwi-boards at a cited commit` · `<file> is a MicroPython build for chip id 13 (esp32c6) but firebeetle2-esp32s3 is
  an esp32s3 (chip id 9) — refused, nothing written`.
- **depends on** — · **unblocks** 4: CH-24, CH-30, CH-31, CH-34; soft CH-32; P178: CH-33 reads its table
- **bin** its own `build-flash-image.py` is untouched; its `make check` validates both library boards (`boards-valid`,
  `Makefile:230-233`), each on its own silicon through the table — shown by
  `test_the_shipped_boards_stand_in_on_their_own_silicon`, the test that would also catch a direct compare of the two
  spellings turning the bin's `boards-valid` and irrigation's chain red (R2); **irrigation** its
  `sim/micropython-esp32s3.bin` reads chip id 9 (FB verify, E) — passes; **plant-alarm** has no firmware.
- **proof** STORE-9's run (`chip: esp32c6` on the S3 stand-in → `ok`, exit 0) exits 1 with the sentence; the FB
  diagnosis's chip-13 run exits 2.
- **why this rank** tier 1: wrong silicon validates with `ok` and packs with exit 0; key (a): it unblocks four changes
  of the epic, second only to CH-16; and it is the list's first board change (key (e)).

#### 3 · CH-18 · `--need` answers "nothing matches — research it" for parts the person owns, and its answer depends on how the words were quoted — split the query into words, keep each word a substring test, name the word that missed and what was not searched

- **kind** bug · **size** S · **card** #10 (P39), its first step · **fix now** (block A: search)
- **fixes** K33 (step 1); USER-AI-AGENT-7; USER-HUMAN-5, -20; I1, open since 2026-09-29 (irrigation `DIARY.md:26-31`) ·
  **root cause** because the search takes the words as typed, wants every one of them inside the id, name, kind or alias,
  and on a miss says only "nothing matches", never which word missed or where it did not look (RC-NM-1; NM-M5;
  `parts.py:1329`)
- **removes / adds** the query is split by one `words()` moved down to layer 1 (beside `store.PLAIN`) and imported by
  both `needs` and `parts` — not `needs._words` (`needs.py:122-123`) imported into `parts.py`, a private name of a
  layer-5 module reached from layer 2, which §2.5's import-direction seam would flag (R2, CH-18 row) — so `"soil
  sensor"` and `soil sensor` are one search; each word stays a substring test under the AND, so prefix finds keep
  working (R1: the first version's "tokens, not substrings, against the haystack" would lose `vl6180` →
  `vl6180x-breakout` and `l9110` → `l9110s-module`, with the suite still green); on a miss, which word missed, the
  counts searched, and that the drawer and the function words are not searched here. Ranking by words hit is CH-53.
- **test** `test_parts.py::test_need_quoted_or_not_is_one_search`; `::test_need_12_v_inlet_names_the_words_that_missed`;
  `::test_need_keeps_prefix_finds` (`vl6180`, `l9110`); `tests/test_parts.py:790-798` stays green.
- **prints** `nothing matches all of: 12, v, inlet — "inlet" alone matches 4 (jst-ph-2-power-inlet, …); searched id,
  name, kind and aliases of 31 records (library 8, shelf 5, catalog 18); the drawer's 110 entries and function words are
  not searched here — parts.py --match <project> searches them`.
- **depends on** soft CH-1 (until it lands, the miss line names the layers it searched, not the store's path) ·
  **unblocks** 3: CH-42, CH-52, CH-53; soft CH-21
- **bin** none; **irrigation** its DIARY records I1 as history; **plant-alarm** none. Reasoned.
- **proof** on a copy of his store `--need "soil sensor"` and `--need soil sensor` give one answer; `--need 12 V inlet`
  names the missing words; `--need vl6180` still finds the breakout.
- **why this rank** tier 1: "nothing matches, research it" over a part he owns is a wrong answer with no sign, and the
  agent's most frequent recorded wrong turn (I1, USER-1, USER-9, the P162 council); key (a): it unblocks three.

#### 4 · CH-26 · A copy into a project carries no provenance, and the digests spark already writes are read by nothing — one `based_on` shape on every copy, and `--audit` says which copy or proof is behind

- **kind** story · **size** M · **card** #82 (P148) · **fix now** (provenance and its reader); `--refresh` is **P178**
  (Q9)
- **fixes** K13 (its record half); K19 as corrected (a proof written and never read); STORE-6, STORE-15; SL-M3;
  EXISTING-FIRST-4 · **root cause** because a copy into a project is a plain file copy that remembers nothing of where it
  came from, and the one copy that does remember — a shelf copy's `based_on {project, digest}` — is compared by nothing,
  so a copy falls behind its source and no command can see it (RC-SL-4, its digest half; SL-M3: `grep
  '\["digest"\]\|\.get("digest")' scripts/*.py` → nothing)
- **removes / adds** one `based_on` shape on every copy — `{from: <layer>, project: <name or null>, id, digest}`, every
  key always present, so no reader branches (R1) — whose `digest` is taken over the whole record less `SHELF_DROPS`, not
  over `BUILD_FACTS`: the six build facts leave out `simulation` and `body_mm`, so the shelf's digest today cannot see a
  stand-in change — half of K13's own example — nor say which fact changed (R2, CH-26 row; `parts.py:899-915`, `:940`);
  written on catalog → project (`parts.py:1303` writes none today) and by CH-4 and CH-63. `--audit` compares each copy
  with its source **field by field**, prints `differs: <fields>`, and says which side moved: "the source changed since
  the copy" when the copy still matches its own `based_on` digest, "edited here since the copy" when it does not, both
  when both. A shelf copy in the old `{project, digest}` shape is read as an alias, compared field by field, says it
  cannot tell which side moved, and is rewritten on its next write; a copy with no `based_on` at all — every copy made
  before this change but the shelf's — is compared with the record of the same id in the layers above it, field by
  field, and says it records no source. `--audit` also compares each `built` line's digests with today's records — a
  lockfile, read-only. `BUILD_FACTS` stays as it is: it vouches for a build, which a stand-in does not change, so §4's
  condition "before something reads a digest" is now met and its answer is still no (R2). `note_built` returns a
  sentence and `check_spine.py:625-629` prints it.
- **test** `test_parts.py::test_every_copy_writes_the_one_based_on_shape`;
  `::test_audit_names_the_fields_a_copy_differs_in_and_which_side_moved` (its fixture changes the source's `simulation`
  stand-in — R2: a fixture changing a `BUILD_FACTS` field would pass even with the old digest);
  `::test_a_copy_edited_here_reads_as_edited_not_behind`;
  `::test_a_shelf_copy_in_the_old_shape_is_read_compared_and_rewritten`;
  `::test_audit_says_a_built_line_is_stale_after_its_pin_order_changed` (`pin_order` is in `BUILD_FACTS`,
  `parts.py:903`, R1); `test_check_spine.py::test_a_build_of_an_unlisted_project_says_it_was_not_recorded`.
- **prints** `rc-car's copy of tactile-button differs from spark's library in host_parts, simulation — it records no
  source, so which side moved cannot be told; compare, then --fact-set or delete the copy` · for a copy with `based_on`:
  `… differs from the shelf's in pin_order — the shelf changed since the copy` · `built on <date> with another pin_order
  for sen0193 — rebuild to re-prove` · `the build was not recorded in your history: <project> is not on your projects
  list — /spark:init or parts.py --step puts it there`.
- **depends on** soft CH-5 (until it lands, a copy it cannot read is named by the reader it reaches today) ·
  **unblocks** 2: CH-35, CH-63; soft CH-4; P178: CH-29, `--refresh`
- **bin** none; **irrigation** its four shelf copies match today (SL diagnosis: `True` ×4); **rc-car** its
  `tactile-button` copy named with the fields it differs in (K13) — a read; **plant-alarm** none. Reasoned.
- **proof** `--audit` on a copy of his store names rc-car's copy and the fields it differs in, says it records no
  source, and names nothing else.
- **why this rank** tier 1: drift has no sign (K13) and K19's proof misleads silently; key (a): it unblocks two, and
  (a2) its soft edge (CH-4) puts it first of the four that unblock two.

#### 5 · CH-17 · A pick that does not do the need — another verb, other words, no record — is taken with the same silence, and the needs file cannot say so — the pick records its fit and says it

- **kind** story · **size** M (R2: a schema change, not S–M) · **card** none · **decision** Q41 (a `fit` field on the
  need, or a mark value)
- **fixes** K34; NM-M1; NM-M4; USER-HUMAN-4 · **root cause** because the pick resolves an id and never asks the matcher
  whether the part does the need, and the needs file has no word for "fits loosely" — its four marks say whether a part
  is available, not whether it does the need's words — so a wrong intent is written as if it were right and nothing
  downstream can tell (RC-NM-2; NM-M4: `MARKS = ("have", "have-unknown", "know", "gap")`, `needs.py:23`). And the needs
  file's reader refuses a pick that holds more than an id, and a need that holds a field it does not know
  (`needs.py:34`, `:68-70`), so recording anything more is a change to the file's schema (R2, CH-17 row). The first
  version printed a note at pick time and recorded nothing; R1 called that a symptom fix.
- **removes / adds** one `candidates()` call per picked need (`plan_pick` makes none, `needs.py:267-335`); a `fit`
  recorded in `needs.json` as a field of the need, keyed by the picked id — `"fit": {"l9110s-module": "other-verb"}`,
  each value one of `does` (the verb and the words), `other-words`, `other-verb`, `no-record` (reserved, not placed) —
  never inside the pick, whose one-key shape six sites assume (`needs.py:34`, `:225`, `:236`, `:283`, `:297`;
  `parts.py:2011`); `fit` joins `CHECKS` with its own sentence; a file that holds a `fit` is written as schema 2 and the
  reader reads 1 and 2, so an older spark meets a newer file with the sentence it already has — `is schema 2 — this
  spark reads schema 1` (`needs.py:55-56`) — instead of calling `fit` an unknown field (R2-Missing 5: the version rule);
  printed at the pick, shown by `--needs` (`parts.py:1940-1946`), carried by `--requirements` as a note and read by the
  build's unserved note; a pick written before this change reads as `fit: not recorded`, never a refusal; `idea.md`'s M
  step gains the rule for an all-`[other words]` list. NM-C2's mark/pick pair rule is not added (§4). The pick's time is
  measured (it parses every record per need, FEASIBILITY §2.5).
- **test** `test_needs.py::test_a_pick_of_another_verb_is_recorded_and_said`;
  `::test_a_pick_of_a_candidate_with_other_words_is_recorded_and_said`;
  `::test_a_pick_with_no_record_says_reserved_not_placed`; `::test_requirements_and_the_build_read_the_fit`;
  `::test_a_pick_from_before_the_fit_reads_as_not_recorded`; `::test_a_needs_file_holding_a_fit_is_read`;
  `::test_a_schema_1_file_is_still_read`; `::test_a_schema_2_file_meets_a_schema_1_reader_with_its_sentence` (the old
  reader's sentence, pinned).
- **prints** `temp: l9110s-module does drive, not sense — recorded as other-verb; say why to the person, or pick another`
  · `temp: sen0193-soil-moisture does soil-moisture, not temperature — recorded as other-words`.
- **depends on** CH-16; Q41 · **unblocks** 2: CH-42, CH-50
- **bin, irrigation** have no `needs.json`; **plant-alarm** its picks read as `fit: not recorded`; its next pick
  rewrites its `needs.json` as schema 2, which a spark older than this change refuses with the schema sentence — said on
  the card and in the release note (R2: every `--match` there reads that file). Reasoned.
- **proof** the NM verifier's run `--pick <node> temp=l9110s-module` prints the note, and the next day `--needs` and
  `--requirements` show `other-verb`.
- **why this rank** tier 1: a wrong intent is written with exit 0 and "1 reused"; key (a): it unblocks two; key (c) puts
  the person's record of intent (class 1) before CH-21's and CH-19's wrong answers (class 2).

#### 6 · CH-21 · Boards cannot be searched, shown or checked like records, `boards.py` answers in no envelope, and its exit 1 also means "no selection" — `--need` and `--show` see boards, `boards.py` speaks the envelope, `--validate` runs with no selection, and a missing selection is could-not-run

- **kind** bug · **size** S–M · **card** none (the envelope theme is #23 P92's) · **fix now** (block A: search; B1, B5's
  smaller form; STORE-5)
- **fixes** STORE-3, STORE-4, STORE-5; K52; CC-MC-8; TECH-LEAD-2's `boards.py` half (carried from CH-45, R2) · **root
  cause** because the search and the show walk part records only (`parts.py:1332-1351`, `:966-969`), `boards.py` has no
  `--json`, and `--validate` asks for a selection inside its per-board loop (`boards.py:476`), so a board answers
  "nothing matches" or "no board selection" though its file is right there
- **removes / adds** `--need` also walks `boards.records(project)`, matching id, name, chip and SKU; `--show <board>`
  prints the board and its layer; `boards.py --list --json` and `--validate --json` answer in `outcomes.envelope`;
  `--validate` computes the selection once, as `--list` already does (`:526-529`), and runs with none; a missing
  selection where one is needed is could-not-run, exit 2, while every other `BoardError` keeps exit 1 — `--get
  no_such_field` must stay exit 1, which the bin's contract test pins (`tests/test_boards.py:366-369`) — the one
  exit-code mapping that adds a meaning (R8), carried here from CH-45 because this change edits the same lines first
  (R2, CH-21 row); its sentence says how to select, never `--id`, which prints the active id and selects nothing
  (`boards.py:495`; R2, CH-45 row); the docstring and the message name the person's folder, not the plugin's
  `active.json` (STORE-5). Moving the board operations into `parts.py`'s `OPERATIONS` is Q8.
- **test** `test_parts.py::test_need_esp32_lists_both_library_boards`; `::test_show_names_a_board_and_its_layer`;
  `tests/test_json_contracts.py` gains `boards.py --list --json` and `--validate --json`;
  `test_boards.py::test_validate_runs_with_no_board_selection`; `::test_no_board_selection_is_could_not_run`;
  `::test_get_no_such_field_stays_exit_1` (the existing pin, named).
- **prints** for a real miss: `nothing matches 'esp32 c5' in parts or boards (project, store, library, catalog) —
  research it: /spark:research "esp32 c5"` · `boards.py: no board selection at <project>/boards/active.json — could not
  look; select one: write boards/active.json as {"schema": 1, "board": "<id>"} (boards.py --list names the ids)` — exit
  2.
- **depends on** soft CH-18 (the words split one way), CH-5 (a board file it cannot read is named by today's reader
  until then) · **unblocks** 2: CH-24, CH-63; P178: CH-27
- **bin** its Makefile's text calls of `boards.py` print as today — shown by `TheCommandLineTheSmartBinDependsOnTest`
  (`tests/test_boards.py:312`, P41); its `--get` call keeps exit 1 (`tests/test_boards.py:366-369`), and it holds
  `boards/active.json` (E its file), so no call of it meets the new exit 2; **irrigation, plant-alarm** none.
- **proof** STORE-3's `--need esp32` lists the two shipped boards; STORE-5's `--validate` from a folder with a board file
  and no `active.json` validates that file.
- **why this rank** tier 1: the same failure shape as CH-18 — "nothing matches, research it" with two ESP32 board files
  shipped (R1: one shape, one tier); key (a): it unblocks two; key (c) puts it after CH-17 (an answer, not the person's
  record), and key (e) before CH-19 — a board.

#### 7 · CH-19 · 91 of 110 drawer entries can be reached by no need, and no answer says so — count them where they are skipped, ask after an import, and run the data pass with the PO

- **kind** story · **size** S, plus the PO's time · **card** related: #93 (P157), #99 (P162) · **decision** Q6
- **fixes** K36; USER-HUMAN-6; RISKS-2; NM-M8 · **root cause** because a drawer entry becomes a candidate only when it
  links a record or states what it does, an import gives it neither, and `--match` skips the rest without counting them
  (RC-NM-4)
- **removes / adds** `--match` gains a line with the count of silent entries and up to three labels nearest the need's
  words; `drawer_silent` in `--audit`; a `function` column in `--drawer`; a step in `commands/drawer.md` after an import
  where the agent proposes `function` from each label and the person says yes (the import's payload stays `{sku, name,
  count}`, D the PO 2026-10-04; `dfrobot.js:5-6`). Then the data pass, as a card with the PO. Synonyms the store does not
  hold (`footswitch` for a tactile button, K33) are given as record aliases in that pass (G8).
- **test** `test_parts.py::test_match_counts_the_entries_no_need_can_reach`; `::test_audit_lists_silent_drawer_entries`;
  `test_drawer.py::test_the_drawer_listing_shows_a_missing_function`.
- **prints** `91 of 110 drawer entries say nothing of what they do, so no need reaches them — /spark:drawer sets
  function; nearest by label for "obstacle ahead": DFRobot SEN0311 …, …` (with the store CH-1 names; until it lands,
  without the store's path).
- **depends on** soft CH-1; Q6 for the data pass · **unblocks** 2: CH-51, CH-53
- **bin · irrigation · plant-alarm** none. Reasoned.
- **proof** RISKS-2's measure: `--match` for `board — compute / microcontroller` lists 2 candidates and says why; after
  the pass, 6.
- **why this rank** tier 1: the owned-first promise fails with no sign for 91 of his 110 entries; key (a): it unblocks
  two; behind CH-21 by key (e) alone.

#### 8 · CH-1 · A `SPARK_HOME` that is set but empty silently reads another store, one naming no folder silently becomes a new empty store, and no answer says which store answered — refuse both in `home()`, carry the refusal through every script as could-not-run, and name the store in every answer

- **kind** bug · **size** S–M (R1: not "two lines and one field" — a refusal, an envelope field, a line on every write,
  a line on `--match`/`--pick`, a read-only `--store`, the import fix, test rewrites — and, R2, the store's refusal
  carried through `tools`) · **card** none of its own; the precondition of #101 (P164)
- **fixes** K1; K2 (its "no sign in the output" half); SL-M1; USER-AI-AGENT-4; USER-HUMAN-2; UH-M-h; R2-Missing 6 ·
  **root cause** because spark finds the store through one setting and treats its text as the answer: if the setting is
  empty it quietly falls back to another store (the one `XDG_DATA_HOME` names when that is set, else the real one), if
  it names a folder that is not there it quietly makes a new one on the first write — and an `ok` answer never says
  which store it read (RC-SL-2; `store.py:48-52`)
- **removes / adds** removes the truthiness fall-through at `store.py:48`. Adds, in `home()` itself, a refusal of a
  `SPARK_HOME` that is set but empty or names no folder — on every call, so a read, a `--match` and every `--dry-run`
  are refused too, not only a write (R1, CH-1 row) — checking `inside_git` first, which walks a path that need not exist
  (`store.py:130`), so a refusal inside a repository keeps naming the repository (the two git tests,
  `tests/test_drawer.py:214-221`, `tests/test_store.py:159-166`); the default home (unset) is still made on first write;
  `tools.PERSONAL` and `DOWNLOADS` become functions read at call time, because `tools.py:47-48` reads the home at import
  and four scripts import it at module level — and those two functions catch the store's refusal and raise it as a
  `ToolProblem` naming `SPARK_HOME`, one `try` in one place, because a call-time read alone only moves the traceback:
  `StoreProblem` (`store.py:119`) is not a `ToolProblem` (`tools.py:59`), so it would pass through
  `init_project.py:411-413` and `tools.py`'s own `except ToolProblem` (`:532` reads `PERSONAL` outside that `try`) and
  end in a traceback, exit 1 (R2, R1 and CH-1 rows; R2-Missing 6); for `flash_image.py`, `sim_project.py` and
  `check_spine.py` R2 did not trace the path, so the per-script test below decides it; the refusal names the folder
  `home()` would otherwise use — `XDG_DATA_HOME/spark` when that is set, else `~/.local/share/spark` (R2);
  `agents.md:85-86` ("use a scratch `SPARK_HOME`") gains "and make its folder first", since a scratch home that does not
  exist is now refused (R2); a `store` field in `outcomes.envelope`; an `in store <path>` line on every write; `your
  drawer is empty (store <path>)` on `--match`/`--pick` over an empty drawer (UH-M-b); `parts.py --store`, one read-only
  line — `store <path> — drawer 110 entries, shelf 5, catalog 18, projects 5` — #101's own suggestion (UH-M-h).
- **test** `test_store.py::test_a_spark_home_that_is_empty_or_names_no_folder_is_refused_on_read_and_write`;
  `test_store.py::test_a_missing_spark_home_inside_a_repository_names_the_repository`;
  `test_tools.py::test_changing_spark_home_after_import_moves_the_tools_list`;
  `test_parts.py::test_every_envelope_names_the_store`; `test_parts.py::test_store_says_which_store_and_what_it_holds`
  (its counts from a fixture store, never the PO's — R2);
  `test_store.py::test_the_refusal_names_the_folder_home_would_otherwise_use` (with and without `XDG_DATA_HOME`);
  `test_tools.py::test_a_refused_store_is_a_tool_problem_naming_spark_home`;
  `tests/test_outcome_invariant.py::test_every_main_under_an_empty_or_missing_spark_home_exits_2_with_the_sentence_and_no_traceback`
  (R2: the second version's tests ran no `main`, so none could see the traceback). Tests that point `SPARK_HOME` at a
  folder they expect the first write to make each gain a `mkdir` (how many: —).
- **prints** `parts.py: SPARK_HOME names <path>, which is not a folder — mkdir it for a new store, or unset it to use
  <the fallback: $XDG_DATA_HOME/spark, or ~/.local/share/spark>` · `SPARK_HOME is set but empty — a failed expansion?
  name a scratch store, or unset it to use <the fallback>` · through `tools`: `init_project.py: SPARK_HOME names <path>,
  which is not a folder — …` — could-not-run, exit 2, in every script.
- **depends on** — (it carries the store's refusal to every `main` itself, rather than waiting for CH-5's reader — R2) ·
  **unblocks** 1: CH-42; soft CH-3, CH-4, CH-11, CH-18, CH-19, CH-25
- **bin · irrigation · plant-alarm** none sets `SPARK_HOME` (E R2: `grep -rIl SPARK_HOME` in all three, excluding
  `node_modules`, `.git`, `dist` → nothing); for kind `boards`, `store.layers` adds no store row (`store.py:78`), and
  `boards.validate`'s calls into `parts` read no home (R2, its trace) — nothing breaks, E.
- **proof** the P100 refuter's reproduction — the pick with `SPARK_HOME` at a missing folder, as a dry run, which
  answered `firebeetle2-esp32s3: to get — known, not owned` and `would write to your history: 1 reused`, exit 0 (P100
  `council/refuter.md:54-55`) — answers could-not-run, exit 2, with the sentence; `parts.py --store` names his store and
  its counts (on his copy, 2026-10-10: `drawer 110 entries, shelf 5, catalog 18, projects 5`, E R2).
- **why this rank** tier 1: a wrong or empty store answers exactly like the right one, and the harm is recorded (#101's
  twelve projects; P100's refuter's dry run); key (a): it unblocks one change outright (CH-42), and (a2) its six soft
  edges — the most of any change — put it first of the three that unblock one. Counted with soft edges equal to hard
  ones it would be first of all (§6, split 23; Q42). The second version's "every later proof could otherwise run on the
  wrong store" was the enabling argument, which is not a key (R2).

#### 9 · CH-6 · The requirements writer replaces a list without a word, writes back two entries that are one name, and keeps a third copy of the naming rule — it reads through `design.read` and names with one function

- **kind** bug (three removals, one move) · **size** S · **card** #118 (P175), #119 (P176)
- **fixes** K59, K60, K61 · **root cause** because the writer has its own loader, which turns a file it does not expect
  into an empty object, and its own copy of the naming rule, which is not the one the build checks (RC-CC-5)
- **removes / adds** removes `needs._called` (`needs.py:430-432`), the silent replacement at `needs.py:612`, and
  `_name_after` (`:425-427`, folded); moves `component_name` into `design.py` (`emit_board.component_name` aliases it,
  its 12 call sites unchanged); `needs.requirements` reads through `design.read` when the file exists, and starts from
  `{}` when it does not — the first `--requirements` has no file, and `design.read` refuses a missing one
  (`design.py:96-97`; R2, CH-6 row); `design.read` reads UTF-8 instead of the locale's encoding (`design.py:99`),
  because the suite runs a C locale with coercion off (`tests/test_drawer.py:652`), where a non-ASCII requirements file
  would read as "is not JSON" (R2); `parts.main` catches `design.DesignError` as a problem naming the file — without
  that mapping the list file would end in a traceback, exit 1, the K11 class this change exists to remove (R1, CH-6
  row).
- **test** `test_needs.py::test_a_requirements_file_that_is_a_list_is_refused_and_left_alone`;
  `::test_two_hand_written_entries_that_are_one_name_are_refused_naming_both`;
  `::test_the_first_requirements_with_no_file_still_writes_one`;
  `test_design.py::test_an_unnamed_entry_s_default_name_is_one_name_with_a_named_one`;
  `::test_a_requirements_file_is_read_as_utf8_in_a_c_locale`;
  `test_parts.py::test_a_design_error_is_a_problem_naming_the_file_never_a_traceback`.
- **prints** `requirements.json holds a list; a requirements file is an object with parts` · `parts[0] is called OpenLid
  and parts[1] Openlid — the build refuses two components of one name …` — exit 1, nothing written.
- **depends on** — (it maps `DesignError` itself rather than waiting for CH-5) · **unblocks** 1: CH-39
- **bin · irrigation · plant-alarm** nothing breaks (CC verify C5) — reasoned.
- **proof** the chain diagnosis's three reproductions (`proj-k61`, `proj-k59`, the default-name file) flip.
- **why this rank** tier 1: a person's file is overwritten and the output says what was written, not what was lost; key
  (a): it unblocks one; key (b): three removals, so it leads CH-14.

#### 10 · CH-14 · `--skeleton --kind board` writes a part-shaped record into `parts/`, exit 0 — refuse it, naming the board route

- **kind** bug · **size** S · **card** none · **fix now** (block A: create; B0)
- **fixes** STORE-2 · **root cause** because the one create verb takes any `--kind` and always writes a part, and nothing
  in its row or its help says a board is another kind of file (`parts.py:1480`, `:1540`)
- **removes / adds** a refusal of `--kind board`; one mutation row.
- **test** `test_parts.py::test_a_skeleton_of_kind_board_is_refused_naming_the_board_route` (no file under `parts/`, exit
  1).
- **prints** `firebeetle2-esp32c6: a board is not a part record — it is boards/firebeetle2-esp32c6.json, under the board
  contract (boards/README.md); start it as boards/README.md and how-it-works.md's "Your own dev board" say: copy the
  closest board file, then set its chip and its stand-in (CH-13 checks them)` — until CH-24's command exists, whose name
  then replaces that clause (R2, CH-14 row: at this rank neither CH-24 nor CH-63 exists, so the second version's
  sentence named a verb nobody could run).
- **depends on** — · **unblocks** 1: CH-24
- **bin · irrigation · plant-alarm** none.
- **proof** STORE-2's run exits 1 with the sentence instead of `wrote …/parts/firebeetle2-esp32c6.json`, exit 0.
- **why this rank** tier 1: the only create verb an agent finds in `--describe` writes a record no board reader sees,
  exit 0, and `--promote` then offers to put it in the plugin; key (a): it unblocks one, after CH-6 by key (b).

#### 11 · CH-12 · A board file whose pad labels are bare numbers merges pads in the netlist every check reads, and every check passes — refuse a label or key tscircuit reads as a pin number

- **kind** bug · **size** S · **card** none (G0.3)
- **fixes** K22 · **root cause** because the circuit tool reads a pad hint made only of digits as "pin number N", and
  spark's board check never looks at the pad labels it collects, so a label such as `17` joins two pads into one
  connection that every later check takes as the truth (RC-BR-2 as narrowed: no copper short observed in tsci 0.0.2621; a
  netlist in which the 3V3 pad answers to `17`, a phantom port, and a converter refusal two stages later — BR verify
  RC-2, E)
- **removes / adds** in `boards.validate`, where labels are already collected (`boards.py:344-349`): a label, or a
  `pins`/`power_pads` key (BR-M6), matching tscircuit's own grammar (`/^\d+$/`, `/^pin(\d+)$/i`) is refused. The grammar
  is cited from both cores the bin can load — `@tscircuit/core` 0.0.1958, `index.js:11651-11654`, and 0.0.1911 under
  `@tscircuit/runframe`, `dist/index.js:11608` — and `tscircuit` 0.0.2621, the version K22 was seen on, declares
  `@tscircuit/core ^0.0.1958` (E the critic, the bin's `node_modules`; this settles R1's version point). One sentence in
  the board schema (CH-22).
- **test** `test_boards.py::test_a_bare_number_pad_label_or_key_is_refused` (a digits fixture under `tests/data/`);
  `::test_the_shipped_boards_carry_no_numeric_label`;
  `test_emit_footprint.py::test_a_footprint_never_doubles_a_pin_number`.
- **prints** `physical.header_order.row_18[13] is "17": a bare number, which tscircuit reads as pin position 17 — the pad
  at position 17 is "3V3", and the two would become one port. Print the silkscreen word (SCK, IO17), never the GPIO
  number.`
- **depends on** — · **unblocks** 0; soft CH-24 (its owed `header_order` is filled by hand from the drawing — the very
  step at which round 0 typed bare numbers)
- **bin** `make check` validates the library S3, which has no numeric label (BR verify) — shown by
  `test_the_shipped_boards_carry_no_numeric_label`; **irrigation, plant-alarm** unchanged.
- **proof** `boards.py --validate` on the digits fixture exits 1 with the sentence; on the S3 and the XIAO, exits 0.
- **why this rank** tier 1: the PO's own example of a silent fault, "a short that passes the checks"; it unblocks none
  outright, and (a2) its one soft edge puts it first of the fifteen that unblock none.

#### 12 · CH-4 · `--promote` puts a project's record into spark's own folder, which the next update replaces, and a live check still writes a header into spark's tracked cache from an unmarked folder or through a symlink — `--promote` from a project goes to the shelf, and every write into spark's folder passes one run-time guard

- **kind** bug + remove · **size** M · **card** #22 (P91) for promote-to-shelf; #84 (P150) for its promoted-records
  half; N14, N25, N26, N28 (#125's council) · **fix now** (block A: global vs local)
- **fixes** K12 (its silent-loss half); SL-M4; R1-Missing 2 (the writers around the door); N14, N25, N26, N28;
  TECH-LEAD-4 (the plugin folder spelled five times) · **root cause** because the rule for where a proven project record
  goes is written down as "the plugin's own library" (`agents.md:131`; `--describe`, `parts.py:1490`; `parts.py:1296`) —
  the maintainer's place, which an update replaces for everyone else — so the write is announced and the later loss is
  silent (RC-SL-4 as corrected by R1); and because #125's rule lets a live check write into spark's cache whenever the
  board file resolves to a folder spark owns — judged by where the file sits, not by whether it is one of spark's boards
  — so an unmarked folder inside spark's tree, or a symlinked board file, reaches spark's tracked cache (N25, N26)
- **removes / adds** removes `LIBRARY` as `promote`'s target for a project record (`parts.py:1296`; `:1865` already says
  the library changes by pull request); `--promote` from a project → the shelf, writing CH-26's one `based_on` shape
  (the function exists, `parts.py:932-941`); `agents.md:131` and `--describe` say "onto your shelf". Adds one
  `plugin_root()` in `store` (layer 1), which `boards.py:38`, `:153`, `parts.py:45` and `tools.py:43` import instead of
  spelling the folder again, and one write helper, `store.write_own(path, artefact)`, through which the three writers
  into the plugin go — `promote`'s `copy2`, `check_vendor_pins`' header write, `sim_project.py:162`'s chip copy —
  refusing any target under `plugin_root()` unless `artefact` names it: the header of a board whose **resolved** file is
  one of the plugin's own `boards/*.json`, or the compiled binary of a library chip; and `_make_ready` refuses a store
  target under `plugin_root()` (a `SPARK_HOME` set inside spark's tree). That is #125's council's own proposal — "one
  owner for 'where is spark' … and writes that refuse spark's folder unless asked" (N14, N28) — and it replaces the
  second version's test-time map over the commit gate's archived tree, which saw only what the suite wrote and allowed
  the shipped-header path N25 and N26 reach (R2, R2 row and Mechanism). Chip identity stays P149's and P150's (#83,
  #84). Shelving a project's own records at `--requirements` (SL-C11 (b)) is not part of this (§4).
- **test** `test_parts.py::test_promote_from_a_project_goes_onto_the_shelf_with_based_on`;
  `test_store.py::test_a_write_into_the_plugin_is_refused_unless_it_names_spark_s_own_artefact`;
  `::test_a_spark_home_inside_the_plugin_is_refused`;
  `test_check_vendor_pins.py::test_a_new_board_in_an_unmarked_folder_inside_spark_is_refused_live` (N25);
  `::test_a_symlinked_board_file_does_not_write_spark_s_cache` (N26);
  `::test_a_shipped_board_s_header_is_still_refreshed` (#125's rule);
  `test_sim_project.py::test_a_library_chip_compile_goes_through_the_helper`;
  `test_paths.py::test_the_plugin_folder_is_defined_once`.
- **prints** `promoted to your shelf: sen0308-soil-moisture (based on irrigation) — every project finds it` · `refused:
  <spark>/.spark/cache/dfrobot_firebeetle2_esp32c6.pins_arduino.h is inside spark's own folder, and the board file
  <path> is not one of spark's boards (it resolves to <real path>) — run the live check from the board's own project, or
  --offline` (could-not-run, exit 2).
- **depends on** soft CH-1, CH-26 · **unblocks** 0
- **bin** calls no `parts.py`; its `make refresh-vendor-pins` (`Makefile:223`) refreshes spark's shipped headers for
  library board files, which the guard admits by name — shown by `test_a_shipped_board_s_header_is_still_refreshed`, the
  bin's own run reasoned; **irrigation, plant-alarm** promote nothing and refresh no header today — reasoned.
- **proof** a promote dry run from a project names the shelf; a live check of a board file in a scratch folder under
  spark's tree is refused with the sentence, and `git status --short` in spark prints nothing afterwards.
- **why this rank** tier 1: the loss at the next update is silent, and so is a rewritten tracked header; it unblocks
  none, and key (b) puts this removal first of the changes that unblock none, after CH-12's soft edge.

#### 13 · CH-11 · Nothing keeps an agent's unscoped command off the PO's real store — the guard he chooses, and a refusal that names the rule and the store

- **kind** story · **size** S–M · **card** #101 (P164) · **decision** Q2
- **fixes** K2 (its incident half); RISKS-14; USER-AI-AGENT-13 · **root cause** because the only guard is prose in the
  agent guide, and two agents on record did not hold it — one ran with three assignments as one string and read an empty
  store as "not owned", another's `export` did not survive to its next tool call and twelve scratch projects landed in
  his `projects.json` (USER-AI-AGENT-13; #101; RC-SL-2)
- **removes / adds** one of, or both: (a) a write to the default home is refused when the project or the current folder
  is under the system temp root (`tempfile.gettempdir()`, `/tmp` and its macOS alias) — it covers the recorded incident,
  whose twelve projects sat in an agent's scratch folder under that root (RISKS-14, E), and not a scratch copy under
  `~/Development`; (b) `SPARK_STORE=real` set once in the PO's shell, every other write to the default home refused — it
  covers both cases.
- **test** `test_store.py::test_a_write_from_a_temp_folder_never_reaches_the_default_home` (`HOME` at a scratch folder);
  for (b) `::test_the_default_home_is_written_only_with_the_flag`.
- **prints** `this command would write your store at <path>; say so with SPARK_STORE=real, or point SPARK_HOME at a
  scratch store — nothing written` (could-not-run).
- **depends on** soft CH-1; Q2 · **unblocks** 0
- **bin · irrigation · plant-alarm** their builds write no store; under (b) the PO sets one variable once. Reasoned.
- **proof** #101's own line: an agent's write in a fresh shell with no `SPARK_HOME` answers could-not-run naming the
  rule; the PO's commands write as before.
- **why this rank** tier 1: the harm has happened once, with no sign; it unblocks none, and key (d) — a recorded harm
  (#101) — puts it first of class 1's additions, above CH-3, whose harm is reasoned only: R1's and R2's swap, applied,
  since the second version kept CH-3 above by edges to CH-8 and CH-25 that gave no reason (§6, split 18). It enters
  Ready the day Q2 is answered.

#### 14 · CH-49 · A scenario's pass says nothing of what it covered — the coverage of the pin map as a note, before a Wokwi minute is spent

- **kind** story · **size** S · **card** related #7 (P59), #8 (P74)
- **fixes** K67 in part; RC-FB-3's scenario half · **root cause** because a scenario passes on whatever it asserts, and
  nothing compares what it asserts with the pins the design uses, so "the scenario passed" reads as "the firmware is
  right" (RC-FB-3 as corrected)
- **removes / adds** a scenario's coverage of the pin map, printed as a note by the simulation stage; an `expect-pin`
  must name a pin the stand-in knows. The firmware facts in `pins.py` and the held check are CH-67.
- **test** `test_sim_project.py::test_a_scenario_s_coverage_of_the_pin_map_is_said`;
  `::test_an_expect_pin_the_stand_in_lacks_is_refused`.
- **prints** `wet-and-dry.scenario.yaml asserts 1 of 12 pin-map constants (VALVE1_VALVE_CTRL on GPIO38); never asserted:
  VALVE2_VALVE_CTRL, VALVE3_VALVE_CTRL, VALVE4_VALVE_CTRL, STATUS_LED, …; a pass proves those pins nothing`.
- **depends on** — · **unblocks** 0
- **irrigation** its scenario prints `1 of 12` as a note, no stage flips; **bin** its own checks; **plant-alarm** no
  firmware. Reasoned.
- **proof** irrigation's scenario prints the line before a Wokwi minute is spent.
- **why this rank** tier 1: a pass over 1 of 12 pins is `ok` over a result that leaves out what the chain holds (R1
  moved it up from tier 3); it unblocks none; class 1 (a simulation's verdict), and key (d) puts it with CH-11 among the
  recorded harms — it was met on a paid run (PO-6) — after CH-11 by key (g).

#### 15 · CH-36 · `--validate --for-fab` answers ok for a board whose footprint has no geometry — the board being fabricated must carry its geometry

- **kind** bug · **size** S · **card** #55 (P121), its proof · **fix now**
- **fixes** K30's fab half; BR-M5's fab half · **root cause** because the fab check asks only that two footprint names
  are present (`REQUIRED_FOR_FAB = ("footprint_module", "footprint_export")`, `boards.py:67`), not that the footprint
  can be drawn (RC-BR-7)
- **removes / adds** `--for-fab` requires the footprint's geometry (`physical.header` and its rows, width, height), not
  two names; it judges the selected board — the one a fab package is made of — and, with no selection, every board,
  saying which; `footprint_module` leaves this rule here and the files in CH-22. The XIAO's stop label and data are
  CH-66.
- **test** `test_boards.py::test_a_board_with_no_header_geometry_fails_for_fab` (#55's own proof);
  `::test_for_fab_judges_the_selected_board_and_says_so`; `test_validate_and_validate_for_fab_both_answer`
  (`tests/test_boards.py:378-382`, which accepts 0 or 1) stays green.
- **prints** `xiao-esp32-c6: not ready to fabricate — physical.header is absent, so the footprint cannot place its pads
  (boards/README.md, the board file key by key)`.
- **depends on** — · **unblocks** 0
- **bin** its Gerber recipe runs `boards.py --validate --for-fab` (`Makefile:182`) with the S3 selected, which has
  geometry — green **because** the fab requirement applies to the selected board: applied to every available board, as
  `--validate` walks them (`boards.py:467`), the recipe would exit 1 on the library XIAO until it has geometry (R1,
  CH-36 row); `test_for_fab_judges_the_selected_board_and_says_so` shows the scope, the bin's own run is reasoned — and
  P41's `test_validate_and_validate_for_fab_both_answer` accepts exit 0 or 1 (`tests/test_boards.py:378-382`), so this
  scope test is the only guard of the bin's Gerber recipe (R2); **plant-alarm** its XIAO fails `--for-fab`, honestly;
  **irrigation** none.
- **proof** `boards.py --validate --for-fab` in a scratch project selecting the XIAO exits 1 with the sentence; with the
  S3, exits 0.
- **why this rank** tier 1: `ok` over a board that cannot be drawn (R1 moved it up from tier 2); it unblocks none; class
  1 (a circuit for fabrication), and key (d) puts it after the recorded harms — an agent met it (K30).

#### 16 · CH-10 · The same folder under another spelling is a second project — compare folders, not strings

- **kind** bug · **size** S · **card** none (C-8 on #94)
- **fixes** K4 (its spelling half) · **root cause** because a project is recognised by its resolved path as text, and on
  a file system that ignores case two spellings of one folder are two texts (RC-SL-1, its implementation half:
  `store.py:255-256` promises "however its path is spelled"; SL verify RC-1 (1))
- **removes / adds** `project_name` compares with `os.path.samefile` for an existing folder, with the string comparison
  first when the listed folder is gone (SL verify C5 (a)). Name reuse for a vanished folder stays as it is — it is how a
  moved project keeps its holds (SL verify C5 (b)); the copy and vanished-folder cases wait for the project id (CH-29).
- **test** `test_store.py::test_a_folder_under_another_spelling_is_the_same_project` (skipped, and said, on a
  case-sensitive file system); `::test_a_listed_folder_that_is_gone_does_not_raise`.
- **prints** `<path>/proj-e is the listed project 'Proj-E' spelled differently — listed once`.
- **depends on** — · **unblocks** 0; P178: CH-29
- **bin · irrigation · plant-alarm** all five listed folders exist (RISKS-20) — unchanged, reasoned.
- **proof** the store diagnosis's `Proj-E` / `proj-e` run lists one project.
- **why this rank** tier 1: a second listing reserves stock again with no sign; it unblocks none in the epic — its only
  dependent, CH-29, is a P178 concept (R2); class 1, a code read (K4's spelling half, by the catalogue), present on his
  Mac, whose file system the store diagnosis's `Proj-E` / `proj-e` run showed to ignore case; first of the code reads by
  key (g).

#### 17 · CH-3 · The store's write lock follows `TMPDIR`, `/spark:init` and `tools.py` write outside it, and it is held across downloads with no word — one lock beside the data, held by every writer, never across the network, and a wait that says who holds it

- **kind** bug · **size** M · **card** #114 (P174)
- **fixes** K5, K6, K7; K64's lock half (G1); C-9, C-11, C-38 · **root cause** because the lock's file is named in the
  temporary folder, which every agent sets for itself, so two agents lock two different files and both write; and
  because the lock is applied from outside by a table of operations, a writer that is not in the table (`init`,
  `tools.py`) never takes it (RC-SL-3; `store.py:187`; `init_project.py:417`; `tools.py:445`)
- **removes / adds** removes the lock file in `tempfile.gettempdir()`, and the lock a dry run takes: a dry run writes
  nothing, and with the lock in the store every unscoped dry run of a writing operation — an agent's against the PO's
  real store included — would otherwise make the default home and a file inside it (`parts.py:2198-2200` takes the lock
  for every operation that declares `writes`, `--dry-run` included; R2, CH-3 row). Adds `<home>/.lock`, made with the
  home on the first write and never by a read or a dry run; `with store.locked()` around `init_project.py:417` and
  around `tools.py`'s write of the store's `tools.json`, which goes through the door (R1-Missing 3); `--fetch` downloads
  outside the lock and takes it only to write (G1: after this change one agent's stalled download would otherwise make
  every other writer of the store wait in silence); a writer that waits says so after 2 s — who holds the lock (process,
  operation, since when, written into the lock file) — and gives up as could-not-run after a stated time (60 s, H — a
  proposal); one mutation row per writing operation (12, `("writes",)` → `()`); then, once the suite's 42 direct store
  writes are wrapped in a fixture that holds the lock (FEASIBILITY-4's pattern, `grep -c -E
  'store\.(write_json|write_file|copy_folder|append_event|add_project)\('` → `tests/test_store.py` 41,
  `tests/test_drawer.py` 1), a refusal inside the door when no lock is held. A home inside a git work tree (allowed
  today for a store holding only `catalog/` and `sources/`) would show `.lock` there as an untracked file (SL verify C3
  (c)); the line names it, and Q28 decides whether such a home stays allowed.
- **test** `test_store.py::test_two_processes_with_two_tmpdirs_cannot_hold_one_store_at_once`;
  `::test_a_write_outside_the_lock_is_refused`; `::test_a_writer_waiting_on_the_lock_names_the_holder_and_gives_up`;
  `test_parts.py::test_fetch_downloads_outside_the_lock`;
  `test_tools.py::test_tools_on_writes_through_the_door_under_the_lock`;
  `test_init_project.py::test_init_registers_under_the_lock`;
  `test_parts.py::test_a_dry_run_leaves_the_home_s_listing_unchanged` (R2); the 12-row table at every push.
- **prints** `store.write_json("drawer", …) was called with no lock held — the operation's row in OPERATIONS must say
  writes` (could-not-run) · `waiting for the store's lock: held by parts.py --pick (pid 4711) since 14:02:11` · `gave up
  after 60 s: the store's lock is still held by parts.py --pick (pid 4711) — nothing written`.
- **depends on** soft CH-1 · **unblocks** 0 (the second version's edges to CH-8 and CH-25 gave no reason: today's lock
  already serialises a release or a half-write for one `TMPDIR` as it does a pick, `parts.py:2198-2200` — R2; both edges
  are gone)
- **bin · irrigation · plant-alarm** their builds run no writing operation — unchanged, reasoned.
- **proof** the store diagnosis's K5 run comes out serialised; its K7 run lists 24 of 24 registrations (today 18).
- **why this rank** tier 1: a part reserved twice or a registration lost, with no output; it unblocks none; class 1, a
  code read (K5–K7, "nobody — reasoned only"), so after CH-11's recorded harm (R1's and R2's swap, §6 split 18), and
  after CH-10 by key (g).

#### 18 · CH-15 · `--fetch` drops a URL that did not answer and says ok, and an interrupted keep is listed as kept — name each, answer problems, skip the leftover

- **kind** bug · **size** S · **card** #21 (P90), its "says nothing when a fetch fails" half
- **fixes** K17, K16 · **root cause** because the download helper turns a failure into "nothing" and its caller skips a
  nothing without a word (`parts.py:1277-1282`), and the listing of kept documents takes every file in the folder,
  including the `.part` a killed download leaves (`parts.py:1205-1208`) (RC-SL-5)
- **removes / adds** removes that `None`; `fetch_documents` returns each failure with its reason; status `problems`,
  exit 1; the record is written only when a document was kept; `find_kept` skips a `.part` and names it;
  `commands/research.md:44-53` and `agents/parts-researcher.md:52-55` say what exit 1 means here.
- **test** `test_parts.py::test_a_url_that_does_not_answer_is_named_and_the_fetch_is_problems`;
  `::test_an_interrupted_keep_is_named_never_listed_as_kept`.
- **prints** `not kept: https://… — does not answer (Connection refused) — the record still cites it; --sources lists
  every URL's answer` · `leftover-datasheet.pdf.part: an interrupted keep, not a kept document — delete it`.
- **depends on** soft CH-5 · **unblocks** 0
- **bin · irrigation · plant-alarm** none. Reasoned.
- **proof** the store diagnosis's K17 `--fetch --json` answers `"status":"problems"` with the URL in `problems`.
- **why this rank** tier 1: "kept, checked" is the document store's whole promise, and today a record cites a document
  the store never kept, under `ok`; it unblocks none; class 1, a code read (K16, K17), after CH-3 by key (g).

#### 19 · CH-20 · A dimension of −3 × 0 mm "owes nothing", and `--step` lists a folder that does not exist — refuse both

- **kind** bug · **size** S · **card** none (C-33, C-34)
- **fixes** K54, K63 (its `--step` half) · **root cause** because the record check asks only that a dimension is a
  number, not that it is a size, and `--step` lists a project without looking for its folder (RC-CC-7)
- **removes / adds** `body_mm` width and height are finite numbers above 0, a present non-number named as one
  (`parts.py:101-104`, `:658-660`; `--fact-set` inherits it); `--step` refuses a folder that does not exist (CC verify
  C7); `commands/idea.md:13-15` puts `--step S` after `--needs-set`, which makes the folder.
- **test** `test_parts.py::test_a_dimension_that_is_not_above_zero_is_refused_by_name`;
  `::test_a_step_on_a_folder_that_does_not_exist_is_refused_and_lists_nothing`.
- **prints** `body_mm.width is -3; a dimension is above 0 mm` · `body_mm.width is 'wide', not a number` · `no folder at
  <path>; run --needs-set first, which makes it — nothing listed`.
- **depends on** — · **unblocks** 0
- **bin · irrigation · plant-alarm** none. Reasoned.
- **proof** the chain diagnosis's two reproductions flip.
- **why this rank** tier 1: a part laid out at 0 × 0 mm under "owes nothing", and a listed phantom folder; it unblocks
  none; class 1 — the second version's "layout class, behind CH-36 by key (d)" used an order inside class 1 that no key
  stated (R2) — a code read (K54, K63), last of class 1's faults present on his machine by key (g).

#### 20 · CH-9 · A sync client's conflict copy is counted as owned stock, so is a hand copy, and one label in two Unicode forms is two entries — reads refuse what writes refuse, and two entries with one part number are named

- **kind** bug · **size** S · **card** none (C-12, C-13 on #94)
- **fixes** K9 (the doubling, both halves), K10; STORE-16; EXISTING-FIRST-30 · **root cause** because the drawer reads
  every `*.json` in its folder as an entry whatever its file name, so a duplicate under any name doubles what is owned;
  and a label is stored as typed, so two spellings of one letter are two keys (RC-SL-1)
- **removes / adds** `PLAIN.fullmatch(stem)` on read in `drawer.entries()` and `store.records()`, naming the file (the
  conflict-copy half); two entries carrying one `part_number` from one `from` are named, both files, and the read stops —
  the hand-`cp` half, which a plain name such as `dfrobot-sen0193-copy.json` passes (R1); entries that share a linked
  record but not a part number stay legitimate (two shops' buttons); NFC labels in `drawer.clean()`; `slug()` through
  NFKD with combining marks dropped; a label with no ASCII letter keyed `entry-<8 hex of its sha256>` instead of by
  insertion order; `tests/test_drawer.py:242` rewritten to the hash key.
- **test** `test_drawer.py::test_a_conflict_copy_in_the_drawer_is_named_not_counted`;
  `::test_two_entries_with_one_part_number_are_named`; `::test_two_spellings_of_one_label_are_one_entry`.
- **prints** `<store>/drawer/dfrobot-sen0193 (conflicted copy).json is not a drawer entry: its name is not a plain key (a
  sync client's conflict copy?) — compare it with dfrobot-sen0193.json and delete one; the drawer is read whole or not at
  all` (could-not-run) · `dfrobot-sen0193.json and dfrobot-sen0193-copy.json both carry part number SEN0193 from dfrobot
  — one is a copy: delete it, or merge the counts into one`.
- **depends on** soft CH-5 · **unblocks** 0; P178: CH-29
- **bin · irrigation · plant-alarm** 0 non-plain stems in every layer and project today and 0 hand entries whose key
  would change (SL verify C7, E); 0 groups of entries sharing a part number on my copy of his store (E §1, data faults)
  — nothing changes. K10's "the PO's labels are Czech" is refuted (0 such labels, SL verify RC-1 (4)); the change is
  ranked by its mechanism, not that clause.
- **proof** K9's `--match` reads `owned 8 … free 7` (today `owned 16 … free 14`).
- **why this rank** tier 1: doubled stock with no sign; it unblocks none in the epic — its only dependent is CH-29, a
  P178 concept (R2); class 1, a code read (K9, K10), and key (f) puts it last of class 1: its reach today is nil, since
  his store sits in no synced folder (E the critic) and 0 entries share a part number on his copy (E §1).

#### 21 · CH-54 · What a dev board gives for free has no record, so WiFi on an ESP32 reads as "a gap" — `function` on board records, validated and sourced

- **kind** story · **size** M · **card** none · **decision** Q24 (a need the board serves: picked, or marked served)
- **fixes** K31; USER-4, USER-6; FEAS-4/5; BR-M4 · **root cause** because a board record has no field that says what the
  board does while the matcher reads that field for every candidate, so the board is never a candidate for WiFi (RC-BR-8
  as corrected: the drawer entry has a documented `function` slot; the board record has none, and a malformed one is
  accepted by `--validate` and dropped by `--match`)
- **removes / adds** `boards.validate` calls `parts.function_problems(board)`; the S3 record states `communicate / wifi
  bluetooth` (the WROOM-1 datasheet it cites), `power / lipo-charging` (the schematic it cites), `connect / usb-device`
  (a source to add); the XIAO no USB device (FEAS-5); the schema page says which fact goes where — the SKU's in the
  record, this piece's in the drawer.
- **test** `test_needs.py::test_a_need_the_board_serves_lists_the_board`;
  `test_boards.py::test_a_malformed_function_on_a_board_is_refused`.
- **prints** `function is [{"does": one of sense, input, …, "what": words}]` (parts' sentence, now on boards).
- **depends on** soft CH-22 (until it lands, a board's `function` is checked by the parts' sentence and the board page
  does not list it yet); Q24 · **unblocks** 0
- **bin** the library S3 changes in the same commit as the rule (RISKS-12) — its `make check` validates it; reasoned;
  **others** none run `--match`.
- **proof** USER-4's walk: `report / communicate / wifi` lists the S3 instead of "nothing in the store does this".
- **why this rank** tier 1: "a gap" over a board that has WiFi is CH-18's shape — a wrong answer with no sign (R1 moved
  it up from tier 4); it unblocks none; class 2, met by an agent (USER-4, K31), and key (e) — a board record — puts it
  before CH-72.

#### 22 · CH-72 · `--drawer` says "1 owned" for a board another project holds, and nothing in the listing says who holds it — a `held by` column in the listing and in its JSON

- **kind** bug · **size** S · **card** none (C-31 on #94, its listing half) · **fix now** (block A: use in a second
  project)
- **fixes** K3's listing half; USER-HUMAN-3's first half; R2 ("The order" 2) · **root cause** because the drawer listing
  reads every entry whole and then shows its label, count, link and unsure or skip mark only: the reservation it has
  just read is dropped from the text and from the JSON alike (`drawer.py:276-284` builds each shown entry without
  `used_in`; `parts.py:1772-1775` prints it), so the person sees "1 owned" for the FireBeetle S3 and learns that the bin
  holds it only at the pick, two steps later (RC-SL-6, its listing half; SL-M2)
- **removes / adds** adds the drawer key and a `held by <project> (<n>)` column to `--drawer`, and `held` to each entry
  of `--drawer --json`; an entry no project holds prints nothing new. It is the half of the second version's CH-25 that
  needs no decision: the listing reads one value per entry whether Q1 keeps holds stored or derives them. The release
  operations stay CH-25's.
- **test** `test_drawer.py::test_the_listing_shows_the_key_and_who_holds_it`; `tests/test_json_contracts.py` pins `held`
  in `--drawer --json`.
- **prints** `FireBeetle 2 ESP32-S3 (N16R8) …   1  —  held by smartbin-local (1)` (key `dfrobot-dfr0975`).
- **depends on** — · **unblocks** 0
- **bin · irrigation · plant-alarm** the bin's two holds and plant-alarm's four now show in the listing; nothing they
  run reads `--drawer`. Reasoned.
- **proof** `--drawer` on a copy of his store prints `held by smartbin-local` beside the S3 and the LiPo, and `held by
  plant-alarm` beside its four.
- **why this rank** tier 1, by §3's sharpened definition of silent — the listing leaves out a fact it read about the
  very entry it reports (R2, "The order" 2, which offered to narrow the definition or to lift this column; both are
  done); it unblocks none; class 2, met by an agent (USER-3's walk, K3), after CH-54 by key (e). It is one of the three
  walls of the PO's round A (RISKS-1) and S.

#### 23 · CH-55 · A re-picked board moves `requirements.json` and leaves `boards/active.json` on the old one — the selection follows, and says so

- **kind** bug · **size** S · **card** none (C-40 on #94)
- **fixes** K49's `active.json` half · **root cause** because the board is stated in two files and `--requirements` moves
  only one of them (RC-CC-6)
- **removes / adds** `_op_requirements` writes `active.json` when the board it writes differs, and prints the move;
  `boards/README.md:21` ("THE one place it is chosen") gains its qualifier. The alternative — the requirements file is
  the selection and `active.json` goes for such projects — is the smaller system with part 2 (§6, split 3).
- **test** `test_needs.py::test_a_re_picked_board_moves_active_json_with_it_and_says_so`.
- **prints** `boards/active.json: firebeetle2-esp32s3 → xiao-esp32-c6`.
- **depends on** soft CH-7 (until irrigation's file is renamed, the move is said for the file the writer reads) ·
  **unblocks** 0
- **bin** keeps its `active.json` (no requirements file) — safe, reasoned; **others** none.
- **proof** `boards.py --id` agrees with `requirements.json` after a re-pick.
- **why this rank** tier 1: the old selection stays with nothing said (R1 moved it up from tier 4); it unblocks none;
  class 2, a code read (K49) — no check reads the selection (CC-MC-7) — so last of class 2.

#### 24 · CH-64 · The cost line's last window never closes, so the number grows on each read, and one step outside Claude Code spoils a project's tally for good — close the window, and count around a step that cannot be counted

- **kind** bug · **size** M · **card** none (E16b, "not yet a named item")
- **fixes** K21's other half (R1-Missing 7) · **root cause** because the tally counts from a project's first marked step
  up to *now*, so reading it adds the reading to it, and one step marked with no session makes every later count refuse
  (E `docs/observations/INDEX.md:210`, E16b, "verified": two `--tally` reads with nothing marked between counted `1
  request` then `2 requests`; after a step with no session the tally said `a step of spoilt was marked in no Claude Code
  session, so its cost cannot be counted`, exit 2)
- **removes / adds** a project's last window ends at its last marked step (or at a closing mark — the T step `893e48a`
  names as a later card), never at the moment of reading; a step marked outside a session is named and its own window
  left out, while the steps after it are counted.
- **test** `test_cost.py::test_two_reads_with_nothing_marked_between_count_the_same`;
  `::test_a_step_outside_a_session_is_named_and_later_steps_still_count`.
- **prints** `tally: 3 steps counted; the step of spoilt was marked in no Claude Code session — its own cost is not
  counted`.
- **depends on** — · **unblocks** 0
- **bin · irrigation · plant-alarm** none. Reasoned.
- **proof** E16b's reproduction: two reads, one number; the spoiled step named once.
- **why this rank** tier 1: a cost that grows each time it is read is a wrong number with no sign; it unblocks none;
  class 3, reproduced by an agent (E16b, "verified"), so ahead of CH-2.

#### 25 · CH-2 · `mutate.py` scores a mutant that no longer imports as caught, and no full sweep is dated since 2026-09-29 — a mutant that does not compile, import or parse is refused; then sweep before and after the epic

- **kind** chore · **size** S, plus machine time (at most ≈12.3 h: 1,281 rows at `4a18333` (E my count) × the suite's
  34.6 s, the store diagnosis's `Ran 1699 tests in 34.627s` on an earlier day — an upper bound, because
  `tools/mutate.py:201-202` runs a mutant's near tests first and stops at the first failure, so only an escape runs the
  whole suite (R2); the suite then held 1,699 tests, #125's branch 1,713, #124 comment 2026-10-10T16:16:34Z) · **card**
  none (K53 noted on #94, 2026-10-08; under #103 P166)
- **fixes** K53; RISKS-5, RISKS-6; FEASIBILITY-20; EF-MISSING-4; FE-MISSING-10 · **root cause** because the tool judges a
  mutation by the suite's verdict alone, so a mutant that breaks the import makes the suite fail and is scored as if a
  test had noticed the changed behaviour (`tools/mutate.py:88` `return result.returncode == 0 and "\nOK" in verdict`)
- **removes / adds** before the suite, in a subprocess, the mutated `.py` file is compiled **and imported** — a compile
  alone misses a removed import or a renamed constant, which compile and then fail at import (R1); a mutated `.json`
  file is parsed; such a mutant is `refused` — the word the glossary already gives a row that tests nothing ("fix the
  table; nothing ran", `GLOSSARY.md:108-114`), whose entry gains this second reason (the critic: a new word would
  collide); a `.md`, `.ts` or `.js` row (40 of the 1,281 rows at `4a18333` mutate a non-`.py` file: 24 `.md`, 13
  `.json`, 2 `.ts`, 1 `.js` — E my count) says no load check applies to it; `tools/mutate.py --rows-in <file>` lists the
  rows anchored in a file (not `--near`: "near" already names P98's near tests and prints as `caught near`,
  `tools/mutate.py:59-60`, `:226` — R2), so a card can say how many it re-anchored (FE-MISSING-10); a dated full sweep
  (`tools/mutate.py tests/mutations/*.json`, its time printed) before the first store or `parts.py` commit of the epic
  and after the last (RISKS-5: the last dated sweep, 2026-09-29, ran 16 tables and 74 mutations; 116 tables and 1,281
  mutations at `4a18333` — E my count; 115 and 1,268 at `a8aa34d`, FEASIBILITY-1, R1).
- **test** `tests/test_mutate.py::test_a_mutant_that_does_not_import_is_refused_not_caught`;
  `::test_a_json_mutant_that_does_not_parse_is_refused`; `::test_a_markdown_row_says_no_load_check_applies`;
  `::test_rows_in_lists_the_rows_anchored_in_a_file`.
- **prints** `refused: <table> row <n> — the mutated scripts/parts.py does not import (NameError: …, line L); a row must
  change behaviour, not break the import — fix the table`.
- **depends on** — · **unblocks** 0 (CH-67's held check needs it, and that check exists only if Q22 is "yes" — R2)
- **bin · irrigation · plant-alarm** none.
- **proof** the sweep's summary line, with its date, count and wall time, pasted on the card.
- **why this rank** tier 1: "caught" over a mutant that tested nothing is a success over a false result, in the tool
  every later proof leans on — but enabling work is not a key (R1); it unblocks none; class 3, a code read (K53; two
  rows ever, RISKS-6), so last of tier 1.

### Tier 2 — what blocks the documented journey, the PO's emphasis first

#### Block A — the basic store: global vs local; create, search, update, copy and share — boards first

Where each of the PO's words stands today, walked by the store lens on a copy of his store (STORE-1…STORE-18, its
scenario B, E), and which rank answers it. Six of the answers are ranked in tier 1 because they fail silently (CH-4,
CH-14, CH-18, CH-21, CH-26, CH-72); one, the header cache, was merged on 2026-10-10 (#125). CH-23 sits in this block
because it is the last hard prerequisite of CH-24, the PO's first fix (§3's constraint); CH-28 is answered here and
ranked after CH-37, the table it reads (the same constraint). The P178 concept ranks of this block enter Design, not
Build, when their turn comes; inside the block, a fix-now change goes before a concept of equal count, because a concept
enters Design, not Build.

| the PO's word | boards | modules and parts | answered by (rank · fix now / P178) |
| --- | --- | --- | --- |
| global vs local | "global" is the plugin (written by the maintainer) and "local" is one project; the person's store has no place for boards (STORE-1) | the shelf and the catalog exist; `--promote` writes the plugin (K12) | CH-4 (12, fix now); #125 (merged 2026-10-10); CH-27 (31, P178 first slice); CH-29 (33, P178 concept) |
| create | `--skeleton --kind board` writes a part; no board flow anywhere (STORE-2, K29) | `--skeleton` exists and omits three chain facts (K37) | CH-14 (10), CH-23 (27), CH-24 (28) — fix now; CH-37 (48) |
| search | `--need esp32` finds nothing with two ESP32 boards shipped (STORE-3) | `--need` is an AND of substrings that never reads the drawer (K33) | CH-18 (3), CH-21 (6) — fix now; CH-53 (65) |
| update | the validator's refusals are the only schema; `--fact-set` refuses a board (STORE-3, K24) | `--fact-set` / `--function-set` exist | CH-22 (26, fix now: edit and validate, written down); a board door for `--fact-set` is P178's (Q8) |
| copy | a hand `cp`, no provenance (STORE-6) | `--promote` catalog → project writes no `based_on` (STORE-6) | CH-26 (4, fix now); CH-63 (30: library → project fix now, project → store P178 first slice); `--refresh` is P178's (Q9) |
| use in a second project | the one S3 is held by the bin (K3), and the listing does not say so | the same for every held part | CH-72 (22, fix now); CH-25 (29, fix now after Q1); Q5 for P100's round A |
| share | no shared layer, no contribute verb, no key (STORE-7) | the same | CH-70 (32, P178 prerequisite); CH-29 (33, P178 concept) |
| format, sync library, technique | — | — | §2.3: no new format, no sync library; git for the shared layer, `based_on` for project copies, survive a folder sync for the person's machines; CH-70's experiment before P178's council |
| rules and editor | two hand-written schemas that disagree (EXISTING-FIRST-24) | none | CH-22 (26, fix now); CH-28 (49, P178 / P160 concept, after CH-37) |

#### 26 · CH-22 · The board file's contract is documented only by its refusals, and five keys are carried and read by nothing — write the schema where it is enforced, refuse an unread key, remove what nothing reads

- **kind** chore + remove · **size** M · **card** #61 (P127) · **fix now** (block A: update)
- **fixes** K24, K25, K26, K27's mounting-holes half (as a decision); BR-M3; BR-C6; BR-C12; the update verb for boards
  (B4's smaller form) · **root cause** because the board contract lives in the code that refuses a wrong file and in no
  page — the page said to "have the schema" holds only the name rule (`how-it-works.md:146`) — so a person learns it one
  refusal at a time, and keys nobody reads are carried as if they mattered (RC-BR-3; DOCUMENTATION-9)
- **removes / adds** removes `footprint_module` (both board files, `board.ts:48`, four test fixtures, `agents.md:461`,
  `boards/README.md:71`; BR verify C12 — CH-36 has already taken it out of the fab rule) and the four keys of the S3
  file no script reads (`flush_edge`, `corner_radius_mm`, `thickness_mm`, `header.pad_mm`) unless one is given a reader
  — in the same commit as the rule; the bin-specific steps of `boards/README.md` (#61). Adds `PHYSICAL_KEYS` with the
  "carried and ignored" refusal `PIN_ROLES` already has; one comment-key rule for every walker (the `//jtag` refusal
  stops calling a comment a role); a "the board file, key by key" section checked by `test_docs.py` against
  `PHYSICAL_KEYS`, `PIN_ROLES` and the pad forms (one GPIO on two pads = two `pins` keys; an NC pad = a label with no
  key); `pad_aliases` and every `wokwi_*` key documented — `wokwi_power_pins` as the per-pad name table it already is
  (CH-31); the bare-number rule (CH-12); one sentence: updating a board is an edit of its file, and `boards.py
  --validate` is the check. P181 (#127, in Review) edits `how-it-works.md` and `agents.md` now; this change's page edits
  land after it. Mounting holes: emitted or removed (Q16).
- **test** `test_boards.py::test_every_key_the_shipped_boards_carry_is_read_or_refused`;
  `::test_a_comment_key_is_skipped_wherever_keys_are_walked`;
  `test_docs.py::test_the_board_schema_page_names_every_physical_key_and_role`.
- **prints** `physical.flush_edge is read by no script, so it would be carried and ignored. Known: footprint_export,
  header, header_order, height_mm, mounting_holes, pad_aliases, width_mm, wokwi_size_px` (the Known list corrected by
  BR-M3).
- **depends on** — · **unblocks** 3: CH-24, CH-31, CH-66; soft CH-54; P178: CH-28, CH-33
- **bin** green only if the library file's removals land in the same commit as the rule (RISKS-12: its `make check`
  validates the library S3) — shown by `test_every_key_the_shipped_boards_carry_is_read_or_refused` and P41's
  `TheCommandLineTheSmartBinDependsOnTest`; its committed `.spark/board.json` goes stale until `make` re-resolves (BR
  verify) — no break; its converter copy types `footprint_module` as required
  (`tools/circuit-to-wokwi/lib/board.ts:40`), a type with no runtime read (R1) — said on the card; **irrigation**
  unchanged unless holes are emitted (Q16); **plant-alarm** none.
- **proof** a second agent writes a C6 record from `boards/README.md` alone without meeting G0.2, G0.5 or G0.10 (round
  0's own proof line); `grep -rn footprint_module scripts boards` prints nothing.
- **why this rank** tier 2, block A first: create (CH-24), the simulation keys (CH-31), the XIAO's stops (CH-66) and the
  editor (CH-28) all read the contract; key (a): it unblocks three changes of the epic, the most in tier 2, and it
  removes keys first. Round 2's strongest case would put it third of all, above every tier-1 change but two (§6, split
  24; Q35).

#### 27 · CH-23 · The library S3 cannot build a design that spends MOSI or MISO, and the chain's stop names a terminal two hops from tscircuit's own sentence — report the build's error messages whether or not there is an island, and carry every alias onto the footprint

- **kind** bug · **size** S–M · **card** none · **fix now**
- **fixes** K23; BR-M1; USER-HUMAN-13; G3 · **root cause** because the footprint writes each pad's printed label only,
  so a pin the board file calls `MISO` has no pad answering to it (RC-BR-1); and when the build also left a part joined
  to nothing, the chain returns on that island and never reports the build errors it has already read, while with no
  island it reports their types only, so the sentence that names the cause never reaches the person
  (`check_spine.py:419`, `:433-441`; BR-M1 as corrected by R1 and R2)
- **removes / adds** in `check_spine`, the build's error **messages** — not only `element["type"]` — printed in every
  case — before the island when there is one, alone when there is none (R1: a reorder alone would print `1 error(s):
  <type>`; R2: with an island today they never print at all); the footprint writes every `pins` key aliased to a pad as
  a second hint, the printed label first (`portHints={["MI","MISO"]}`); the alias rule becomes "a target that is also a
  `pins` key maps to the same GPIO" (BR-C2's rule as written would refuse the S3's own `SS → A4` — BR verify); the S3
  record's `//pad_aliases` comment, which states this exact fault (`firebeetle2-esp32s3.json:97`), is rewritten;
  README's "What works today" Build row (`README.md:73`, "**works**") names this limit until the change lands (G3) —
  with P182 (#128), which rewrites README's first screen, or before it.
- **test** `test_emit_footprint.py::test_an_aliased_pin_is_a_second_hint_on_its_pad`;
  `test_check_spine.py::test_a_build_error_s_message_is_printed_before_an_island`;
  `::test_a_build_error_s_message_is_printed_with_no_island` (asserts the text `Could not find port for selector ".Mcu >
  .MISO"`, a fixture circuit); the 21-LED requirements file builds with 0 `source_trace_not_connected_error` (with the
  toolchain tests).
- **prints** `[!!  ] build  Could not find port for selector ".Mcu > .MISO" — the footprint has no pad answering to MISO
  (pads: MI, MO, …)`, before `Led08SeriesA.pin1 (a terminal connected to nothing)`.
- **depends on** — · **unblocks** 1: CH-24
- **bin** its footprint comes from its own script — untouched; **irrigation** its committed `FireBeetle2Esp32S3.tsx`
  drifts from the regenerated one by one hint, no net changes (BR verify) — said on the card; **plant-alarm** none.
  Reasoned.
- **proof** the 21-LED S3 design two lenses reproduced reaches `[ok] build`; round 0's `IO<n>` record builds past
  `.Mcu > .D3`.
- **why this rank** tier 2: the stop is a sign, but it names the wrong cause and the board cannot be built; key (a): it
  unblocks one — CH-24, the PO's named first fix — so §3's constraint moves it up from the rest of tier 2 to sit right
  before it (R2, "The order" 1 and 3: at rank 43 it held CH-24's Build behind fourteen other changes).

#### 28 · CH-24 · A board the person owns with no board file is reserved, recorded, then refused, and the only route is a five-step page round 0 ran with ten gaps — a board record from a drawer entry

- **kind** story · **size** L · **card** #99 (P162), its board half; D8 · **fix now** (decided) · **decisions** Q11, Q35
- **fixes** K29, K72, K73; G0.1, G0.9; USER-HUMAN-12; STORE scenario B step 3 · **root cause** because no operation makes
  a board file: the pick accepts a board with none and warns, the requirements step refuses it, and the person is sent to
  write JSON by hand against a contract no page holds (RC-BR-6)
- **removes / adds** adds `--board-skeleton <drawer entry> --project <p>` (one operation and one allowed-tools pattern,
  FEASIBILITY-13; whether it is a `parts.py` row or a `boards.py` verb is Q8) writing `boards/<id>.json` in the project:
  the Arduino variant from the core's `boards.txt` (3 of the PO's 4 unfiled SKUs are named there — E the board
  diagnosis's read-only fetch; the Beetle ESP32 DFR0575 is —); `pins` through `check_vendor_pins.parse_pins` on that
  header, so the record is born agreeing with its own check; chip facts and the same-chip Wokwi board from a per-chip
  table citing `soc_caps.h` per row, tested against both shipped boards (BR verify), with the Wokwi board read from
  CH-13's chip-name table (one table, R2); the board's documents kept through `--keep` with their sha256; `function`
  from the label, marked unverified (CH-54's field); geometry, `power_pads` and `power.*` written as owed fields, each
  naming the kept document to read it from. A board pick with no file prints this command; whether it still records
  `reused` is Q11. The five-step hand route in `how-it-works.md` goes once the command exists. **What "automatically"
  means here, said plainly** (the critic, item 6): the command fills the pin map and the chip facts; the outline, the
  header rows and the power pads stay the PO's to measure on the kept dimension drawing, because no document gives them
  as data; and the import knows each board only as `{sku, name, count}` (`dfrobot.js:5-6`), so finding a SKU's documents
  is a lookup on the vendor's product page, done by the agent with the person — its exact form is —.
- **test** `test_parts.py::test_a_board_skeleton_from_a_drawer_entry_names_its_variant_and_fills_pins_from_the_header`
  (the fetch patched with the C6 header); `::test_the_chip_table_agrees_with_both_shipped_boards`;
  `::test_a_pick_of_a_board_with_no_file_names_the_command`.
- **prints** `wrote boards/firebeetle2-esp32c6.json: pins from espressif/arduino-esp32
  variants/dfrobot_firebeetle2_esp32c6/pins_arduino.h (20); chip facts from spark's esp32c6 table; stand-in
  board-esp32-c6-devkitc-1 (same chip); OWED before it can build: physical.header, physical.header_order,
  physical.width_mm, physical.height_mm (measure them on the kept dimension drawing <sha256…>), power_pads (from the kept
  schematic)`.
- **depends on** CH-13, CH-14, CH-21, CH-22, CH-23; soft CH-12; CH-31 only for its simulation stage, not its build; #125
  — merged 2026-10-10, met · **unblocks** 1: CH-47; P178: CH-27
- **bin · irrigation** none; **plant-alarm** its board is the XIAO (CH-66). Reasoned.
- **proof** `--board-skeleton dfrobot-dfr1075` on a copy of his store, the owed fields filled, then `check_spine` on the
  board and one LED reaches `[ok] build` — round 0's pass line, from a command.
- **why this rank** tier 2: four of his six ESP SKUs (DFR0575 ×2, DFR0994 ×1, DFR1075 ×2, DFR1117 ×3 — the import's
  counts) cannot be built with today, and with K3 and K36 it is one of the three walls of the PO's own round A
  (RISKS-1); key (a): it unblocks one, and its last hard prerequisite, CH-23, sits right above it. It is L, so its
  Design starts in the first slice (*How the list becomes cards*) and its Build after ranks 26–27 — not, as the second
  version's Q35 said, after rank 43 (R2).

#### 29 · CH-25 · A hold has no operation, and freeing one means writing a JSON file by hand — release it with a command

- **kind** story · **size** M · **card** none (C-31 on #94) · **fix now, after Q1** · **decisions** Q1, Q34 (may project
  B release A's hold), Q38 (the verbs' names)
- **fixes** K3 (its release half; the listing half is CH-72); USER-HUMAN-3 (its second half); STORE scenario B step 7 ·
  **root cause** because a reservation is written only as a side effect of a pick, nothing but another pick of the same
  project changes it, and the plain drawer listing prints neither the key nor the reservation, so the person is told
  "held by smartbin-local" and given no way out but a hand-written file (RC-SL-6; SL-M2)
- **removes / adds** under "stored" (my lean, §6 split 1; the `held by` column is CH-72's, tier 1): `--release <project>
  [entry …]` and `--forget-project <project>`, each with a dry run, built on the path a pick already runs — re-derive
  the project's holds from its picks and release what no pick explains (`needs.py:326-331`; said as "released … — no
  pick of this project explains it", `parts.py:2013-2015`; R1-Missing 11) — so for a project with a `needs.json` a
  release is that path, and for one without (the bin) it is a hold set to the given count; history lines stay (they are
  events); `--audit` names a hold whose project folder is gone and a hold no listed project's picks explain;
  `_how_to_free` (`needs.py:250-257`) names the operation instead of a JSON template with a literal `…`; the command
  reaches the text through CH-16. Under "derived" (Q1's other answer) `used_in` goes and these operations have no target
  — and the bin and irrigation, which have no `needs.json`, hold nothing until they state their picks in one.
- **test** `test_needs.py::test_a_release_lets_another_project_pick_the_board`;
  `test_parts.py::test_audit_names_a_hold_whose_folder_is_gone`;
  `test_needs.py::test_a_release_and_a_pick_share_one_path`.
- **prints** `firebeetle2-esp32s3 — 1 owned, held by smartbin-local (dfrobot-dfr0975) — 1 picked here · release it:
  parts.py --release smartbin-local dfrobot-dfr0975 --dry-run, then without`.
- **depends on** CH-16; soft CH-1; Q1 (the second version's edge to CH-3 gave no reason, R2) · **unblocks** 1: CH-42;
  P178: CH-29
- **bin** its two hand-given holds stay until he releases them; **plant-alarm** its four stay; **irrigation** holds none.
  Reasoned.
- **proof** USER-3's walk (P100 `council/user.md:11`) ends in one command the refusal names, not a grep of the store.
- **why this rank** tier 2: every second project on his one FireBeetle meets it (★C1), and it is the second wall of
  round A (RISKS-1); key (a): it unblocks one, and key (e) puts it after the two board changes; it waits on Q1. Whether
  the S3 is released for P100's rounds is Q5 — this changes only the cost (RISKS-9).

#### 30 · CH-63 · Boards are copied by hand, with no provenance — one copy verb for a board, writing the same `based_on`

- **kind** story · **size** S–M · **card** none (the store lens's B3, its board half) · **fix now** (library or store →
  project); **P178 first slice** (project → store, after CH-27)
- **fixes** STORE-6's board half; G4 (the PO's "copy … the boards for sure" had no change) · **root cause** because the
  documented way to start or reuse a board is a hand `cp` of its file, which remembers nothing of its source, and the
  only copy verb, `--promote`, resolves part records only (`parts.py:1293-1296`; `grep -n based_on scripts/boards.py` →
  nothing, the critic)
- **removes / adds** a copy verb for a board (where it lives is Q8): library or store → the project's `boards/<id>.json`,
  writing CH-26's `based_on`; it never overwrites a differing project file, naming both; it selects nothing silently and
  says how to select; project → store once CH-27 gives boards a store place. `--audit` reads its `based_on` through
  CH-26. `how-it-works.md`'s "copy the closest definition" names the verb.
- **test** `test_boards.py::test_a_board_copied_into_a_project_records_where_it_came_from`;
  `::test_a_copy_never_overwrites_a_differing_board_file`.
- **prints** `copied firebeetle2-esp32s3 (library) to boards/firebeetle2-esp32s3.json, based on digest 1a2b… — select it
  in boards/active.json or requirements.json's board` · `boards/firebeetle2-esp32s3.json is here and differs from the
  library's — nothing copied; compare them, or copy under another id`.
- **depends on** CH-21, CH-26; P178: CH-27, for its project → store half only, which is P178's own — the fix-now half
  needs neither · **unblocks** 0
- **bin** keeps its own board files; **irrigation, plant-alarm** none. Reasoned.
- **proof** a copied board in a scratch project carries `based_on`, and `--audit` names it behind after the library file
  changes.
- **why this rank** tier 2, block A: the PO's "copy … the boards"; it unblocks none, and as the block's last fix-now
  change it goes before the block's concepts.

#### 31 · CH-27 · Boards have no place in the person's store — a store place for boards, and a layer table that says where every record may be written

- **kind** story · **size** S–M · **card** none · **P178 first slice** · **decision** Q8
- **fixes** STORE-1; FEASIBILITY-14; FE-MISSING-2 · **root cause** because the layer list adds the shelf and the catalog
  for parts only (`store.py:77-80`) and the "writable" column the store design asked for was never built
  (`docs/2026-10-04-store-design.md:274-275`), so a board made in one project is found from no other
- **removes / adds** `PLACES["boards"]`; read order project → store → library for boards; `layers()` rows carry kinds,
  writable-by and private; copy and promote read "where it goes" from the table.
- **test** `test_boards.py::test_a_board_in_the_store_is_listed_from_a_fresh_project`; `::test_the_project_s_copy_wins`;
  `test_store.py::test_every_writer_writes_only_a_layer_the_table_marks_writable`.
- **prints** `--list` names each board's layer — `firebeetle2-esp32c6 (store)`; a clash names both files.
- **depends on** CH-21, CH-24; Q8 · **unblocks** 0 in the epic; P178: CH-29, CH-63's project → store half
- **bin** reads the library S3 through its Makefile — unchanged, shown by P41's test; **others** none.
- **proof** a board written in one scratch project is listed from another.
- **why this rank** tier 2, block A: "local" exists for parts and not for boards; a P178 concept (first slice), so after
  the block's fix-now changes, and before CH-70 by key (d): a lens met it (STORE-1).

#### 32 · CH-70 · Nobody has run the store through a sync — the no-code experiment on copies, before P178's council

- **kind** chore (an experiment; no code) · **size** S (one hour, H — EXISTING-FIRST's estimate) · **card** none (P84's
  experiment, never run) · **P178 concept** (its prerequisite)
- **fixes** EF-MISSING-2; STORE-17's —; FE-MISSING-7's evidence · **root cause** because every statement about a synced
  store is reasoned — what two writers on two machines do to `history.jsonl`, the drawer and the projects list has never
  been observed (EXISTING-FIRST-25; STORE-17)
- **removes / adds** in `<scratch>`: two copies of one store copy; a pick in each through spark (the three-assignment
  prefix); then each copy's files committed to its own branch of a scratch git repository (so no store is ever inside a
  git work tree while spark writes it — `_make_ready` refuses that, `store.py:212-214`, and EF-MISSING-3's re-scoping is
  not needed for the experiment), `merge=union` on `history.jsonl`, merge; the merged files copied out to a third store
  and read with `--audit`, `--tally` and `--step`'s listing. Written down: what conflicted, what each output said,
  whether `--step`'s listing reads line order (the one reader not traced, §2.3), and what happened to the file at the
  store's root that no place names (`b12-kept-from-the-bin.jsonl`, §1).
- **test** none (an observation); its record is the test.
- **prints** —.
- **depends on** — · **unblocks** 0 in the epic; P178: CH-29
- **bin · irrigation · plant-alarm** none — copies only.
- **proof** a page in P178's discovery folder with the commands and their outputs.
- **why this rank** tier 2, block A: the cheapest evidence for the PO's sync question and for Q28 before any design; a
  concept's prerequisite that no one has run, so after CH-27 by key (d).

#### 33 · CH-29 · There is no shared store: no layer, no contribute verb, no key that sees a local and a shared copy as one — the shared layer as a git repository of records

- **kind** story · **size** L · **card** #123 (P178) · **P178 concept** · **decisions** Q1, Q17, Q28
- **fixes** STORE-7, STORE-8, STORE-13, STORE-18; K4's copy and vanished-folder halves (through the project id); the PO's
  "global" and "share" · **root cause** because the shared layer was decided in outline on 2026-10-04 and nothing in the
  code holds its place — no layer row, no contribute verb, no key that recognises one record in two places (STORE-7)
- **removes / adds** as decided in outline (D, `docs/2026-10-04-store-discovery.md:209-211`) and to be designed by P178's
  council: a read-only `shared` row after the catalog for parts and boards, a git clone at a pinned commit; `--contribute
  <id> --into <clone> --dry-run` writing the filtered record (never the drawer, history, projects list or document bytes,
  §5.8) and printing the `git`/`gh` commands for the person's yes; a natural key (vendor, SKU); the project id in a file
  of its own, written by every operation that lists a project, listed as `{name: {folder, id}}` — not in
  `.spark/project.json`, which is the person's brief and is written only by `init` (`init_project.py:24`, `:403`), so a
  project listed by a pick alone, like plant-alarm, would have no place for it (R1, CH-29 row); a copy is then refused as
  a second project and a vanished folder's name is never reused; holds never travel; a licence per shared record and chip
  (Q17).
- **test** a fixture clone in the suite: a contributed record validates in the clone; `--need` labels it `[shared
  @<commit>]`; a local edit shows as diverged;
  `test_store.py::test_a_copied_project_folder_is_refused_as_a_second_project`.
- **prints** `myboard-c6 (shared @1a2b3c4) and your store's myboard-c6 differ — yours wins here; --contribute offers
  yours` · `<path> carries the id of the listed project irrigation — a copy? give it its own id with …`.
- **depends on** CH-9, CH-10, CH-25, CH-26, CH-27, CH-70; Q1, Q17 · **unblocks** 0
- **bin · irrigation · plant-alarm** each gains an id file the first time a writing operation lists it — a new file in
  each project, said on the card; nothing else until they contribute. Reasoned.
- **proof** a second machine's clone finds a board contributed from the first.
- **why this rank** tier 2, block A: the PO's next version (#123, 2026-10-09); by §3's constraint it sits after its last
  hard prerequisite (CH-70), and its design is P178's council, not a fix.

#### Block B — replacing a board or a module in the simulation: the closest Wokwi board, or one made for it

How it is done, once the block lands (one section of `boards/README.md`, CH-30):

| you are replacing | Wokwi has it | Wokwi has one of the same chip | Wokwi has nothing that fits |
| --- | --- | --- | --- |
| **a board** (the microcontroller) | `wokwi_part_type` is its own part, `wokwi_is_stand_in: false` | the same-chip Wokwi board from CH-13's chip-name table — "the closest" is a lookup by chip, not a guess (none of wokwi-boards' 55 boards is a DFRobot board; each names its chip, STORE-10, spelled `esp32-s3` where spark writes `esp32s3`); `wokwi_is_stand_in: true` and a sentence of what it loses (CH-32); the per-pad name table for a pin the stand-in names differently or lacks (CH-31) | a generated custom Wokwi board — for the web editor and an upstream pull request only, while the chain's CLI cannot load one (CH-33, P178 concept, Q10); a chip cannot stand in for a microcontroller (H, STORE-13) |
| **a module** (a part) | `simulation` names the built-in part | a built-in part standing in, with the `stand_in` sentence the contract already requires (`parts.py:502-504`) | a custom chip kept beside the record (`<chip>.chip.json`, `<chip>.chip.c`, `wokwi-cli chip compile`, a `note`), or `skip` with a reason; a lookup by function, or a chip skeleton from the record's pins, is CH-69 (P178 concept) |

Today a module's replacement is built, enforced and documented once (`commands/build.md:174-177`), and a board's is none
of the three (STORE-12). CH-13 — a stand-in of another chip refused, naming the same-chip candidates through one
chip-name table — is ranked in tier 1 (rank 2) because it fails silently.

#### 34 · CH-31 · A GPIO the stand-in names differently stops the chain at its last stage, and the table that maps it is undocumented and unchecked — the converter picks a name the stand-in knows, and the table is documented and checked per GPIO

- **kind** bug · **size** M · **card** none · **fix now**
- **fixes** K32; FB-M1, FB-M7; BR-M7; EXISTING-FIRST-1; FEASIBILITY-10 · **root cause** because the simulator's names
  for a board's pins are first looked at by the converter, after the assigner has already spent the pin and the build
  has passed, and the one field that can rename or drop a pin is called `wokwi_power_pins`, documented nowhere and
  checked for power pads only (RC-FB-1 as corrected; RC-BR-9)
- **removes / adds** no `not_on_simulator` role for the library boards (its reason would be false: 0 of the S3's 24 and
  0 of the XIAO's 11 GPIOs are absent on their stand-ins — FB verify (1); §4). For a GPIO with several labels the
  converter picks one the stand-in knows (`mapping.ts:96`; the registry is already in hand, `geometry.ts:58`).
  `wokwi_power_pins` — which already carries renames and `null` (FB verify RC-1 (2), E) — keeps its name, because the
  bin's converter copy reads that key (`~/Development/smartbin-local/tools/circuit-to-wokwi/lib/mapping.ts:108`) and a
  rename would empty the bin's table (R1); it is documented as the per-pad name table (CH-22) and its TypeScript type
  admits `null`. `--validate` checks **per GPIO** that some label of each GPIO, mapped as `mapping.ts:96,108` maps it,
  is a pin of the stand-in — not every `pins` key, which would refuse the XIAO's nine silkscreen labels that the bin's
  `make check` validates (R1); the registry it checks against is a generated copy under `data/wokwi-parts.json` with its
  version and licence notice (`@wokwi/diagram-lint` 0.1.1: MIT `LICENSE`, ISC `package.json` — EXISTING-FIRST-21), with
  a suite test that it equals the converter's bundled registry, so it cannot drift (§6, split 6 resolves the copy
  against R1's "read the converter's own"); the S3 file gains `"TX": "TX", "RX": "RX"`; a spend-last role only for a
  GPIO with no name on the stand-in at all (a person's board on a generic devkit, round 0's case); the converter's
  `"<n>" is not a pin of <type>` for the `mcu` becomes could-not-run naming the stand-in and the remedy (one pinned
  string until CH-46's converter JSON retires it). The bundle is rebuilt (`bundle.sh`; the sha pin at
  `tests/test_check_spine.py:850`) — the change's real cost (FB verify).
- **test** a converter test that a design on `TX` and a design on the XIAO's `SDA` each emit a pin the part knows;
  `test_boards.py::test_a_gpio_the_stand_in_names_differently_is_mapped_or_named`;
  `test_boards.py::test_the_xiao_s_silkscreen_labels_pass_per_gpio`;
  `test_check_spine.py::test_a_missing_stand_in_pin_is_could_not_run_naming_the_stand_in`;
  `tests/test_wokwi_parts.py::test_the_registry_copy_equals_the_converter_s` (with the toolchain tests).
- **prints** at `--validate`: `pins.D3 is GPIO14, which board-esp32-c6-devkitc-1 has no pin for — add "D3": null to
  wokwi_power_pins (the simulation leaves it unwired), or move the signal` · at the last stage: `[????] simulation the
  stand-in board-esp32-s3-devkitc-1 has no pin for GPIO43 (pad TX): the design built; move <signal> off TX to simulate
  it, or prove it on the bench`.
- **depends on** CH-13, CH-22 · **unblocks** 1: CH-46; P178: CH-33
- **bin** its converter copy merges the table last too, and the key keeps its name — green, reasoned; the library S3
  gains its two entries in the same commit as the rule (RISKS-12); its `make check` validates the library XIAO, which
  passes per GPIO — shown by `test_the_xiao_s_silkscreen_labels_pass_per_gpio`; **irrigation** uses no `TX`/`RX`;
  **plant-alarm** once the XIAO builds, `SDA`, `SCL`, `A0`–`A2` map to `D` names instead of failing (FB verify).
- **proof** the FB diagnosis's one-button design on `TX` converts (6 connections, FB verify, E); round 0's record stops
  at `--validate` naming GPIO14, before any build.
- **why this rank** tier 2, block B first: K32 stopped round 0 at the last stage on a fact no document carried, and the
  field that fixes it exists; key (a): it unblocks one.

#### 35 · CH-30 · How to replace a board or a module in the simulation is written nowhere, and two sentences say a stand-in costs only labels — one section that says it, amended sentences

- **kind** chore (docs) · **size** S · **card** none · **fix now** (S1)
- **fixes** K32's documentation half; STORE-12; FB-M9; DOCUMENTATION-13; BR-M2 (the amended sentences) · **root cause**
  because no page describes the three stances a part can take or any stance for a board, and `boards/README.md:96-97`
  and the S3 record's `//wokwi_part_type` (`:104`) claim more than the mechanism keeps
- **removes / adds** one section, "When Wokwi has no part for it", in `boards/README.md` with a pointer from
  `commands/build.md` — the table above, in full: for a board, the same-chip Wokwi board (CH-13's table),
  `wokwi_part_type`, `wokwi_pin_naming`, `wokwi_is_stand_in` and its sentence (CH-32), the per-pad name table with `null`
  for "not on the stand-in" (CH-31), and what the stand-in costs; for a module, a built-in part standing in with its
  `stand_in` sentence, a custom chip kept beside the record (`<chip>.chip.json`, `<chip>.chip.c`, `wokwi-cli chip
  compile`, a `note`), or `skip` with a reason; a chip cannot stand in for a microcontroller (H, STORE-13).
  `how-it-works.md`'s step 1 gains "a copied file keeps the old board's stand-in — set it for your chip";
  `commands/research.md` and `agents/parts-researcher.md` ask for a part's simulation stance (today `grep simulation`
  there → nothing, STORE-12). The two sentences are amended — true of GPIOs (24 of 24 on the devkit), false of two names
  (`TX`, `RX`) — not deleted.
- **test** `test_docs.py::test_the_simulation_section_names_every_wokwi_key_and_the_three_part_stances`.
- **prints** — (a page).
- **depends on** CH-13 · **unblocks** 0; P178: CH-69
- **bin · irrigation · plant-alarm** none.
- **proof** one section answers "how do I replace a board or a module in the simulation"; the amended sentence names
  `TX`/`RX`.
- **why this rank** tier 2, block B: the cheapest answer to the PO's third reading; it unblocks none in the epic; it
  ties with CH-32 on every key to (d), and key (e) — the PO's own words, "add how exactly to replace a board or a module
  in the simulation" — puts the page first.

#### 36 · CH-32 · A board's own stand-in never reaches `WHAT-THIS-CANNOT-SHOW.md`, and its flag is read by nothing — the flag is read, and a stand-in board must say what it loses, as a part must

- **kind** bug · **size** S · **card** #69 (P135) · **fix now** (S4) · **decision** Q44
- **fixes** STORE-12; #69's second bullet · **root cause** because `wokwi_is_stand_in` is written in the board files and
  read by no code (`lib/board.ts:35` types it only), and the page of a simulation's limits walks the parts only
  (`sim_project.py:90`), so the board's stand-in never says what it costs
- **removes / adds** keeps `wokwi_is_stand_in` — it is the one fact that says a stand-in is in use, and the bin's
  `CLAUDE.md:108` names it (R1: the first version removed it, leaving its own rule nothing to decide from); makes it
  required (true or false) and read — and the library XIAO, which has no such key today (its `wokwi_part_type` is its
  own Wokwi part, `boards/xiao-esp32-c6.json:9`), gains `false` in the same commit, so the bin's `boards-valid`
  (`Makefile:230-233`), which validates the library XIAO, stays green (R2, CH-32 row); a person's own board file without
  the flag is refused with the sentence, and the release note says so (Q44 offers "absent reads as false" instead); when
  true, a `wokwi_stand_in` sentence is required, as `parts.py:502-504` requires one of a part; CH-13's table
  cross-checks it (a type whose chip differs is refused there); `limits_of` reads the board too.
- **test** `test_sim_project.py::test_the_board_s_stand_in_reaches_what_this_cannot_show`;
  `test_boards.py::test_a_stand_in_board_must_say_what_it_loses`; `::test_the_shipped_boards_carry_the_stand_in_flag`;
  `::test_a_board_file_without_the_flag_is_refused_naming_it`.
- **prints** in `WHAT-THIS-CANNOT-SHOW.md`: `- **mcu** — the generic ESP32-S3 devkit stands in: same silicon; the
  silkscreen labels are lost, and GPIO43/44 are named TX/RX there` · for a board without it: `wokwi_is_stand_in is true
  for firebeetle2-esp32s3, so wokwi_stand_in must say what board-esp32-s3-devkitc-1 loses, as a part's stand_in does` ·
  `xiao-esp32-c6: wokwi_is_stand_in is missing — say true (a Wokwi board of the same chip stands in) or false (the Wokwi
  part is this board)`.
- **depends on** soft CH-13 (until it lands, the sentence is required but not cross-checked); Q44 · **unblocks** 0
- **bin** its simulation is its own; the library S3 gains the sentence and the library XIAO gains `false`, both in the
  rule's commit — shown by `test_the_shipped_boards_carry_the_stand_in_flag`; its `CLAUDE.md:108` stays true; its own
  `boards/` holds only `active.json` (E my `ls`). Reasoned.
- **proof** the documented example's simulation lists the board's stand-in (#69's own proof line).
- **why this rank** tier 2, block B: replacing a board must say its cost exactly as replacing a module already does; it
  unblocks none, after CH-30 by key (e).

#### 37 · CH-33 · spark cannot make a Wokwi board for a board Wokwi lacks — generate `board.json` and `board.svg` from the record, for the web editor and upstream

- **kind** story · **size** M · **card** none · **P178 concept** · **decision** Q10
- **fixes** STORE-11; the PO's "or maybe we can create one" · **root cause** because a custom Wokwi board is
  `board.json` (`name`, `mcu`, `fqbn`, size in mm, `pins {label: {x, y, target}}`) plus `board.svg`, every fact of which
  spark's record holds, yet nothing composes them; and the result loads only in the wokwi.com editor — the CLI's project
  config documents `[[chip]]` and no board key, and whether `wokwi-cli` loads a local board is still — (STORE-11; the
  critic's one search did not settle it, and `wokwi-cli` is not installed on this Mac)
- **removes / adds** `boards.py --wokwi-board <id> --out <dir>` writing both files from the record (pad positions from
  `emit_footprint`'s placement; its `mcu` from CH-13's chip-name table, never spark's spelling) — generated, never
  copied (wokwi-boards declares no licence, STORE-11).
- **test** `test_boards.py::test_a_wokwi_board_from_the_s3_record_names_every_label_with_its_gpio`.
- **prints** `could not place pads for <id>: physical.header owes …` (the footprint's own refusal).
- **depends on** CH-22, CH-31; Q10 · **unblocks** 0
- **bin · irrigation · plant-alarm** none.
- **proof** the generated FireBeetle S3 board loads in wokwi.com's editor ("Load custom board file…") with its silkscreen
  labels.
- **why this rank** tier 2, block B: "create one" serves the web editor and an upstream pull request only, while the
  same-chip route (CH-13, CH-31) works in the chain now; a P178 concept, placed after its last hard prerequisite
  (CH-31); reading `wokwi-cli`'s source would settle whether it can do more.

#### 38 · CH-69 · A module Wokwi lacks has no help to find its closest part — a lookup from a record's function to a built-in part, or a chip skeleton from its pins

- **kind** story · **size** — · **card** none · **P178 concept** — proposed here; no lens or diagnosis weighed it (G5)
- **fixes** the module half of the PO's "closest … or create one" (G5) · **root cause** because the three stances for a
  module exist (CH-30) but choosing among them is the researcher's judgement with nothing to start from, so the PO cannot
  tell whether a helper was not wanted or not thought of (G5)
- **removes / adds** two candidates for P178's council, neither built here: (a) a lookup from a record's `function.what`
  to the registry's built-in parts — the registry spark bundles carries a `category` per part (STORE-9: entry keys `type,
  pins, documented, isBoard, category`), so the lookup is plausible (H); (b) a custom-chip skeleton (`chip.json` with the
  record's `pin_order` as its pins, an empty `chip.c`) written beside the record for the researcher to fill.
- **test** —, until designed.
- **prints** for (a): `sen0193-soil-moisture: no Wokwi part named; built-in parts of category "sensors" with an analog
  output: wokwi-potentiometer, …` (H, a shape).
- **depends on** CH-30 · **unblocks** 0
- **bin · irrigation · plant-alarm** none.
- **proof** —, until designed.
- **why this rank** tier 2, block B, last: an idea with no lens behind it, written down so the PO can keep or drop it.

#### The rest of tier 2

#### 39 · CH-7 · `--requirements` writes a second requirements file beside the project's own — rename the one project's file, and refuse when another name sits there

- **kind** bug (+ data) · **size** S · **card** none · **decision** Q7
- **fixes** K40; NM-M6; RISKS-20 · **root cause** because the writer knows one file name and never looks beside it, while
  the chain accepts any name (RC-NM-8 as corrected: one documented name; the writer never looks)
- **removes / adds** data first: `git mv irrigation.requirements.json requirements.json` in irrigation — its owner's
  change (Q7); rc-car holds `car.requirements.json` and `remote.requirements.json`, two boards — its owner's decision
  (RISKS-16 and NM-M6 make it data first, R1). Code: before the write, list `*requirements*.json`; refuse when one
  exists under another name, and when `requirements.json` and another both exist and differ, naming each.
- **test** `test_needs.py::test_a_requirements_file_under_another_name_refuses_the_write_and_names_it`;
  `::test_two_requirements_files_that_differ_are_both_named`; `::test_the_same_name_merges_as_before`.
- **prints** `irrigation.requirements.json is here and is not the file --requirements reads and writes
  (requirements.json): rename it (git mv), then run again — nothing written`.
- **depends on** Q7 · **unblocks** 1: CH-39; soft CH-55
- **irrigation** refused until renamed (intended); its `firmware/pins.py:1` names `irrigation.requirements.json` in a
  generated header, so the rename regenerates it (R1); **rc-car** refused until its owner decides; **bin, plant-alarm**
  unchanged. Reasoned.
- **proof** the tech lead's FEAS-8 (1) run stops at the sentence instead of writing a 6-part file beside the 12-part one.
- **why this rank** tier 2: the answer prints the path it wrote, which is a sign (R1 moved it down from tier 1); a
  second source of truth that the chain accepts blocks the next steps (CH-39 seeds from this file); key (a): it unblocks
  one, first of the rest of tier 2.

#### 40 · CH-5 · A file spark cannot read ends in a traceback and exit 1 ("problems"), and a history line cut by a crash stops three commands — one reader, one exception, could-not-run naming the path

- **kind** bug · **size** S for the function, M for the sweep · **card** #65 (P131) for the checks' half; none for the
  store's (C-22 on #94)
- **fixes** K11; the class of K28 and K52 by test; TECH-LEAD-1; EXISTING-FIRST-9; G11 · **root cause** because every
  script reads JSON its own way — 37 raw `json.loads(…read_text…)` sites in 16 scripts — and most catch the JSON error
  but not a bad byte, so one foreign-encoded file ends in a traceback whose exit code says "the answer is no" instead of
  "could not look" (RC-SL-5; `parts.py:2202`)
- **removes / adds** adds `outcomes.read_json(path, what)` (opens with `utf-8-sig`, raises `Unreadable(path, why)`),
  mapped to could-not-run by every `main`; the store-file readers (13, H — the store diagnosis's grep,
  `store-levels-and-holds.md:452`, which its verifier did not recount) and `store.py:145` (the write side's read) first,
  the other raw sites second; `main` catches `UnicodeDecodeError` and `Unreadable` by name, never every `ValueError` (SL
  verify C8 (a)); the history reader names the first 40 characters of a bad line, and the appender, finding an
  unterminated last line that does not parse, cuts it before appending and says so — the one shape a crash mid-append
  leaves, which the gluing guard `_last_line_is_open` (`store.py:299-305`) does not repair (G11). Removes each reader's
  own sentence and `_parse`'s quiet `None` outside link-by-number. Adds the outcome-invariant test (TL-M-H), whose first
  case — every `main` under an empty or missing `SPARK_HOME` — CH-1 brings with it (R2); the store's own refusal is
  mapped by CH-1, and this change does the rest. The drawer, projects and history readers already turn a bad file into a
  sentence (`drawer.py:95-96`, `store.py:240`, `:291`; R1).
- **test** `test_parts.py::test_a_non_utf8_record_is_could_not_run_naming_the_file_never_a_traceback` (`--show`,
  `--validate`, `--need`, `--audit`, `--requirements`); `tests/test_outcome_invariant.py` over every `main`;
  `test_store.py::test_a_history_line_cut_by_a_crash_is_cut_and_said_at_the_next_append`.
- **prints** `parts.py: <path> is not UTF-8 at byte 67 (0xE9) — re-save it as UTF-8` (exit 2) · `history.jsonl: the last
  line, '{"event": "reused", "proj…', was cut by an interrupted write — removed before appending`.
- **depends on** — · **unblocks** 0; soft CH-9, CH-15, CH-21, CH-26, CH-37
- **bin · irrigation · plant-alarm** no output changes for a readable file — reasoned.
- **proof** the store diagnosis's K11c commands — six commands, four different answers, a traceback exit 1 today — answer
  exit 2 with one sentence.
- **why this rank** tier 2: a traceback is a sign, so it is not tier 1 (R1); it blocks every command once one byte is
  wrong; it unblocks none outright, and (a2) its five soft edges lead the rest of tier 2's zeros. Four tier-1 changes
  (CH-9, CH-15, CH-21, CH-26) lean on it softly and print today's reader's sentence until it lands (R2).

#### 41 · CH-66 · The XIAO is labelled "stops at the footprint stage" while its schematic stops first, and the stop is spelled in two places — every stop from one rule, one sentence each, and the XIAO's data

- **kind** bug (+ data) · **size** M · **card** #55 (P121) · **fix now** (its data waits on Q21)
- **fixes** K30's label half; BR-M5's spelling half · **root cause** because "stops at" is computed from one gap — the
  missing header geometry — and spelled twice (`needs.py:511-512` against `parts.py:1920`), while the XIAO also owes the
  `power.io_volts` a part's resistor is sized from (RC-BR-7)
- **removes / adds** `boards.footprint_stop` becomes `chain_stops(board)` returning every stop, one sentence each — the
  second spelling at `needs.py:511-512` goes; the XIAO's data: `power.io_volts` 3.3 V cited from the ESP32-C6 datasheet,
  and its footprint as a `footprint_source` converted from Seeed's KiCad footprint with `tsci convert`, not through-hole
  rows drawn for a castellated module (BR verify; Q21; Seeed's library is CC-BY-SA 4.0, H — STORE-18).
- **test** `test_boards.py::test_a_board_that_owes_io_volts_says_it_stops_at_the_schematic`;
  `::test_every_stop_sentence_comes_from_one_function`.
- **prints** `xiao-esp32-c6 (library) stops at: the footprint stage (no header geometry in its board file); the
  schematic, for a part that sizes a resistor from power.io_volts (not stated)`.
- **depends on** CH-22; Q21 · **unblocks** 0
- **plant-alarm** two stops printed instead of one, then none after the data; **bin** its `make check` validates the
  library XIAO — the data change lands with the rule in one commit (RISKS-12), shown by P41's test; **irrigation** none.
- **proof** `boards.py --list` prints both stops for the XIAO; after the data, none.
- **why this rank** tier 2: "two library boards" is one, and the label about the second is wrong for the part most
  likely picked with it; it unblocks none, and key (b) puts this removal of a second spelling first of the remaining
  zeros.

#### 42 · CH-8 · A write that stops halfway answers with a Python list, and a pick lists the project before the drawer is written — keep the ordered writes, and say what landed

- **kind** bug · **size** S · **card** none (C-10 on #94)
- **fixes** K8; K9 (its half-write) · **root cause** because an operation's writes are separate file writes with no
  record of which landed, so a stop reports an internal list instead of what is now on disk (RC-SL-3, its third fact)
- **removes / adds** keeps the ordered, idempotent writes (the staged all-or-none of SL-C4 is not taken, §4); records
  each step as it lands and says them on a stop; `add_project` after `drawer.apply` in `_op_pick`; `shelvable` computed
  before `drawer.apply` in `_drawer_answer` (SL verify C4).
- **test** `test_drawer.py::test_a_drawer_set_that_stops_says_what_was_written`;
  `test_needs.py::test_a_pick_that_cannot_write_the_drawer_lists_no_project`.
- **prints** `written before the stop: drawer/k8-widget-one.json, shelf/led-test-k8.json — the rest was not; the same
  command, retried, finishes it` (could-not-run, exit 2).
- **depends on** — (the second version's edge to CH-3 gave no reason, R2) · **unblocks** 0
- **bin · irrigation · plant-alarm** none. Reasoned.
- **proof** the store diagnosis's K8 run prints the sentence instead of a list repr; its K9 pick leaves `projects.json`
  unchanged.
- **why this rank** tier 2: a stop answers could-not-run, exit 2, which is a sign (R1 moved it down from tier 1); it
  unblocks none; class 1 (the person's files half-written), met by an agent (K8, the P97 council), before CH-35 by key
  (g).

#### 43 · CH-35 · `--keep` protects `board.tsx` and builds the regeneration, so the verdict, `check_all` and the history describe a board the person does not have — build the kept file, in place, and say how it differs

- **kind** story · **size** M · **card** #44 (P110); D the PO 2026-10-05: build the kept file · **fix now** (decided)
- **fixes** K20; CC-MC-4; FE-MISSING-9; USER-AI-AGENT-6; USER-HUMAN-10 · **root cause** because `--keep` keeps the
  person's file and then builds the freshly generated one beside it, so every verdict after that line is about another
  board (RC-CC-3)
- **removes / adds** with a `board.tsx` in `--keep DIR`, the chain still emits (for the diff) and builds the kept file
  in place — the project folder, where a hand-written file's local imports resolve (the bin's imports four siblings,
  CC-MC-4) — the stage line names the line count it differs by, and a kept generated footprint that differs too; no
  `built` event when it differs, said; `kept` in the JSON (CH-16). Flips `tests/test_check_spine.py:316-331`;
  `build.md:72-74`, `journey.md:706-709` and `agents.md:418-429` change together.
- **test** `test_check_spine.py::test_a_kept_board_tsx_is_what_dist_holds_and_the_stage_says_how_it_differs`;
  `::test_a_kept_board_that_differs_records_no_built_event_and_says_so`.
- **prints** `[ok  ] schematic  board.tsx kept: differs from what requirements.json generates in 13 line(s);
  FireBeetle2Esp32S3.tsx in 1 — delete them to regenerate` · `the build was not recorded in your history: board.tsx is
  not what the requirements generate`.
- **depends on** CH-16, CH-26 · **unblocks** 0
- **bin** unreachable (no requirements file); **irrigation** `dist/` becomes its own board's build and records no `built`
  until regenerated (13 lines differ) — to be said to the PO; **plant-alarm** none. Reasoned.
- **proof** on a copy of irrigation, `dist/board/circuit.json` holds no `BtnModePullupA` and the stage says 13 lines
  differ.
- **why this rank** tier 2: decided on 2026-10-05 and open since; the sign today is two stderr lines after the verdict,
  so it is not silent; it unblocks none; class 1 (the verdict is about another board), met by an agent (K20).

#### 44 · CH-34 · The documented journey ends at `pins.py`: nothing says how firmware reaches a board — the two tools in the tools list and the two commands on the page

- **kind** chore (docs) · **size** S · **card** #16 (P79), its smallest piece · **fix now** · **decision** Q13
- **fixes** K66 (★C6, USER-7, A5, PO-11); USER-HUMAN-1; FB-M5; EF-MISSING-5 · **root cause** because no tools-list role
  puts bytes on a board, and the pages stop at the simulator's image (RC-FB-2; `grep -rli "esptool\|mpremote" README.md
  docs/guide commands skills` → 0 files, FB verify)
- **removes / adds** removes "Not yet. No command does this yet" (`journey.md:913`); `esptool` (role `flasher`, with a
  minimum version — the PO's 3.3 has no final ESP32-C6 target, FB-M5; the exact minimum is H) and `mpremote` (role
  `device-files`) in `data/tools.json`, so `/spark:setup` says what the bench needs; the Bench section of `journey.md`
  and README's row carry the two commands composed from the record's `chip` and `micropython_port`, with the bin's
  `deploy.sh` as the worked example, marked as the bin's and unrun on hardware; `how-it-works.md`'s tools table ("The
  tools spark calls", `:206`) gains both. A script that composes them with the person's yes is P79's shape (Q13).
- **test** `test_tools.py::test_flasher_and_device_files_are_roles_with_a_minimum_version`; the docs gate's name and flag
  checks cover the page.
- **prints** `[????] flasher  esptool is not installed — install: python3 -m pip install --user "esptool>=4"`.
- **depends on** CH-13 · **unblocks** 0
- **bin** keeps its `deploy.sh`; **irrigation, plant-alarm** none.
- **proof** the two commands run once on the owned FireBeetle with the PO's yes, and the board's first serial line
  recorded beside them (needs Q5).
- **why this rank** tier 2: every P100 round's pass line is "firmware that runs", and the documents end one step before
  it; the page is S, the bench is the PO's; it unblocks none; class 3 (a page), so last of the tier.

### Tier 3 — wrong or unverifiable verdicts, numbers and documents

Order by the keys: two changes unblock one (CH-45, then CH-41 by key (c)); then the zeros — CH-68 first by its two soft
edges, the removals (verdicts before documents, key (c)), CH-28 where §3's constraint places it, then the additions.
CH-57 came down from tier 1, and CH-73 is new (R2).

#### 45 · CH-45 · One script's JSON adds a fourth status word, and `init` run twice answers `problems` — three status words only, and `init`'s answer as the PO decides

- **kind** chore · **size** S · **card** none (P43 #11 closed) · **decision** Q25
- **fixes** TECH-LEAD-2 (its `check_vendor_pins` and `init` halves; the `boards.py` half is CH-21's, R2); CC-MC-8; K52's
  exit kind · **root cause** because `check_vendor_pins` writes `mismatch` into its JSON status
  (`check_vendor_pins.py:230`) where every other script writes one of three words; and because `init`'s "nothing to do"
  uses the `NOTHING_TO_DO` alias that `outcomes.py:9-11` names as the written design — a choice, not a fault, which the
  PO may change (R2, §1 row)
- **removes / adds** `check_vendor_pins`' JSON status `mismatch` → `problems`, the per-board word kept as detail on the
  entry (re-pin `tests/test_json_contracts.py`, which #125 edited); `init`'s "nothing to do" → the PO's word (Q25), and
  nothing if he keeps it; the `boards.py` mapping and its two tests went to CH-21 (R2, CH-21 row). The first version's
  grep test on `EXIT_PROBLEMS as` stays dropped (R1).
- **test** `test_json_contracts.py::test_every_json_status_is_one_of_the_three_words`;
  `test_init_project.py::test_nothing_to_do_answers_as_decided`.
- **prints** `check_vendor_pins.py --json`: the disagreeing board's entry reads `"status": "problems"`, the word
  `mismatch` kept in the entry's own detail; the exit stays 1. (The second version's sentence here sent the reader to
  `--id`, an option that selects nothing — R2; the selection sentence is CH-21's now.)
- **depends on** soft CH-68 (until it lands, the bin's `vendor-pins-agree` line is reasoned); Q25 · **unblocks** 1:
  CH-46
- **bin** `make check` reads `check_vendor_pins`' exit — a mismatch stays exit 1 — green; the bin's Makefile does not
  read the word `mismatch` (E `grep -n mismatch Makefile` there → nothing, the second version's run); **irrigation,
  plant-alarm** none.
- **proof** `check_vendor_pins.py --offline --json` on a board that disagrees prints `problems` and exits 1; `init` run
  twice answers as Q25 decides.
- **why this rank** tier 3: an agent branches on the status word (`agents.md:8`); key (a): it unblocks one; class 2, so
  before CH-41 (class 3) by key (c).

#### 46 · CH-41 · The docs gate does not read the pages agents follow or the glossary, names a page by its file name, keys an output on a fence tag, cannot see a closed card, and lets a retired sentence back in — widen it and make it name where

- **kind** chore · **size** S–M · **card** none (C-36 on #94) · **decision** Q39 (DoD 8)
- **fixes** K74's scope half; DOCUMENTATION-4, -5, -6, -16; DOC-M-D1, -M-D2, -M-D5, -M-D6, -M-D7; DR-M5; EF-MISSING-8;
  FE-MISSING-8; G2, G3 · **root cause** because the gate reads three places and checks names, not currency or retired
  words, so a sentence fixed in one commit returns in the next and a wrong flag on a command page reaches an agent first
  (RC-DR-5; G14)
- **removes / adds** removes `build.md:80-90`'s second pasted copy of a chain run (a link instead). Adds
  `commands/*.md`, `skills/*/SKILL.md`, `agents/*.md` (7 + 3 + 4 = 14 pages, R1's `ls`) and `GLOSSARY.md` to `doc_files`
  (how many problems the 14 pages raise today: — , not run); a page named by its path; an output keyed on its note, and
  stage lines with no note flagged in any fence; a closed card named by a page reported (P43 #11 at `agents.md:253`,
  `:300` at `4a18333`); a **retired-sentence check** — the bin's `tools/check-current-docs.py` shape (EF-MISSING-8,
  FE-MISSING-8) — reading the pages and the scripts' printed strings, seeded with the sentences CH-30, CH-34, CH-37,
  CH-39, CH-50 and CH-55 retire; the version check keyed on README's version line, not on "v0.8.1 anywhere in README"
  (DR-M5, `check_docs.py:173`); one list shared with `tests/test_orphans.py::routes()` minus its sibling-project
  Makefiles; lists in prose equal to lists in code (`VERBS`, `PIN_ROLES`, `PRIVATE`); a rule in `developing.md` that a
  sentence documenting a fault names its card and the card's close deletes the sentence (DOC-M-D7); and, if Q39 says so,
  a **works** row in README's "What works today" links a section holding a recorded block (DOC-M-D6).
- **test** `test_docs.py::test_the_pages_agents_follow_and_the_glossary_are_read`; `::test_a_page_is_named_by_its_path`;
  `::test_a_closed_card_named_by_a_page_is_reported` (on a recorded listing);
  `::test_a_retired_sentence_is_named_where_it_returns` (a page and a printed string);
  `::test_the_version_check_reads_the_version_line`; a mutation row "an agent page is not read".
- **prints** `docs/guide/agents.md: names P43 (#11), closed 2026-10-06 — say what replaced it, or drop the link` ·
  `scripts/init_project.py:485 prints a retired sentence: "build, then re-run with --force" (retired by CH-39)`.
- **depends on** — · **unblocks** 1: CH-43
- **bin · irrigation · plant-alarm** none.
- **proof** `python3 tools/check_docs.py` → `docs: 22 file(s), …` (README, AGENTS, 5 guides, 14 agent pages, the
  glossary — my `ls`, 2026-10-10) and the P43 line.
- **why this rank** tier 3: the first page an agent in Claude Code reads is a command page, outside the gate, and every
  sentence fix in this list can come back without it; key (a): it unblocks one; class 3, after CH-45 by key (c). With
  the PO's documentation brief of 2026-10-10 (§2.6), Q31 lets him pull it forward.

#### 47 · CH-68 · Whether a spark change breaks the bin is checked for one of the four spark tools it calls — the bin's `check_vendor_pins`, `check_physics` and `check_bom` calls pinned as spark tests, as P41 pins `boards.py`

- **kind** chore · **size** S–M · **card** none (the 2026-09-30 document's "`boards.py`'s command line is a cross-repo
  contract with zero tests", which P41 answered for `boards.py` only) · **decision** Q36
- **fixes** RISKS pre-mortem 6; FEASIBILITY-11; the critic's "the bin lines are reasoned" · **root cause** because the
  bin calls four spark scripts from its Makefile (`Makefile:182`, `:186`, `:212`, `:220`, `:223`, `:228`, `:232`;
  FEASIBILITY-11) and only the `boards.py` calls are a spark test (`tests/test_boards.py:312`, P41), so a change to
  another script's output or exit can break the bin while spark's suite is green — two "bin" lines of the first version
  were wrong for exactly this reason (R1: CH-31, CH-36)
- **removes / adds** `TheSmartBinsOtherCallsTest` beside P41's, one case per call, each naming the Makefile line it
  pins: `check_vendor_pins.py <the library board files> --offline` (exit and line shape, as merged with #125),
  `check_physics.py <circuit> --rules <rules>` on a fixture, `check_bom.py` on a fixture. irrigation's and plant-alarm's
  calls likewise, if they make any (FEASIBILITY-11 lists the bin's; whether irrigation's own scripts call spark beyond
  `check_spine` is —).
- **test** the class itself; a mutation row that changes `check_physics`' line shape is caught.
- **prints** `the smart bin's Makefile:228 runs check_physics.py … --rules .spark/rules.json and reads its exit: this
  change made it 2 where it was 0 — the bin's make check would go red`.
- **depends on** — · **unblocks** 0; soft CH-44, CH-45
- **bin** protected by it; **irrigation, plant-alarm** none.
- **proof** the class is green on main and red on a branch that changes `check_physics`' exit for a passing board.
- **why this rank** tier 3: whether a spark change breaks the bin is unverifiable today except for `boards.py`; it
  unblocks none outright, and (a2) its two soft edges put it first of the tier's zeros.

#### 48 · CH-37 · One record gets three verdicts from one module — "builds with it", "owes", "does not meet the part contract" — one owed-facts table, read by every mouth, and every copy of the sentence removed

- **kind** story · **size** M · **card** #59 (P125), #102 (P165), #20 (P89) · **decision** Q3
- **fixes** K47, K48, K37; CC-MC-3; NM-M3; DOCUMENTATION-12; USER-HUMAN-11; G2's "builds with it" half · **root cause**
  because what a missing fact does to the chain is decided in five places and stated in none, so the search promises a
  build that the requirements step then refuses (RC-CC-4 as corrected: a pin order without its proof stops the parts
  stage, exit 2 — CC verify's `proj-proof` run, E; RC-NM-5: research writes records that owe what the chain reads)
- **removes / adds** removes `_about`'s regex (`parts.py:113-117`), `needs.LAYOUT_FACTS`, the comment "no build can
  place it" (`parts.py:97`), and every copy of "builds with it": `parts.py:1631`, `parts.py:2088` ("onto the shelf, so
  every project builds with it", printed for a shelved record that may owe `pin_order_proof` or `simulation`),
  `commands/idea.md:141`, and the recorded outputs `journey.md:468`, `:497` (G2; the first version removed `:1631`
  only). Adds `CHAIN_FACTS` as a table fact → (stage, consequence): footprint and pin_order — the schematic stops;
  body_mm — a placeholder, said in the file; simulation — that stage does not run; pin_order_proof — the parts stage
  stops (as the loader enforces today) or owed and marked (Q3). `owes` in the envelope as `{fact, stage, consequence}`;
  `--requirements` refuses exactly the facts that stop; `--need`, `--match`, `--audit` and `--describe` print the same;
  the research skeleton is derived from the table plus `function` (NM-C5), and `commands/research.md` ends with `--audit
  --project .`, because `--validate` is silent on a null `simulation` or `function` by design (NM-M3); the six prose
  restatements — DOCUMENTATION-12's five and `GLOSSARY.md:233-245` (G2) — become one recorded output and pointers.
- **test** `test_check_spine.py::test_what_each_owed_fact_does_to_the_chain_is_what_the_table_says` (a record without
  each fact through `check_spine.run`); `test_needs.py::test_requirements_refuses_exactly_the_facts_the_build_stops_on`;
  `test_parts.py::test_the_skeleton_holds_every_chain_fact_and_function`; the retired sentence in CH-41's gate.
- **prints** `ds3231-rtc owes simulation — the board builds; the simulation stage will not run until it is filled` ·
  `owes pin_order_proof — the parts stage stops: the loader refuses a pin order without its proof`.
- **depends on** Q3; soft CH-5 · **unblocks** 0; P178: CH-28
- **irrigation** its records carry `pin_order_proof` (P81) — unchanged; **bin, plant-alarm** none; the recorded
  `--need`/`--match`/`--audit` blocks change (CH-40). Reasoned.
- **proof** `--need rtc` on a copy of his store lists the four DFRobot RTCs with what each owes and what that stops,
  instead of "builds with it".
- **why this rank** tier 3: the person reads the promise first and the refusal second; it unblocks none in the epic; key
  (b): five removals; class 2, met by the PO himself (K47, "both") — first of the removals.

#### 49 · CH-28 · Rules and an editor for every record: a JSON Schema per kind, generated from spark's own tables

- **kind** story · **size** M–L · **card** #96 (P160), its first increment · **P178 / P160 concept** (its first instance
  is fix now, inside CH-22) · **decision** Q15
- **fixes** the PO's "rules and editor" (2026-10-10); the editor half of K24; the fill list K46 asks for; FEASIBILITY-8;
  EXISTING-FIRST-23, -24; TECH-LEAD-14 (c); FE-MISSING-1; EF-MISSING-1 · **root cause** because each record kind's rules
  live only in its validator's code, so an editor can say nothing while a person types, and the two hand-written board
  schemas that exist disagree (EXISTING-FIRST-24)
- **removes / adds** a JSON Schema per record kind (board, part, drawer entry, needs, requirements, rules, tools),
  generated from `PHYSICAL_KEYS`, `PIN_ROLES`, `drawer.FIELDS`/`CHECKS`, `needs.CHECKS`, the owed-facts table and, once
  CH-65 lands, the typed `origin` — never kept by hand; a `json.schemas` mapping for VS Code; the converter's TypeScript
  board type generated from the same file (H, `json-schema-to-typescript`, not checked); a conformance test. spark's
  validators stay the enforcer and their sentences the message. Run-time use of `jsonschema` is Q15 (not in the standard
  library — FEASIBILITY-7).
- **test** `tests/test_schemas.py::test_the_schemas_are_generated_from_the_tables_and_agree_with_the_validators` (every
  shipped record and every shape-refusing fixture gets the same verdict from both).
- **prints** in the editor: `physical/header/drill_mm -> -3 is less than or equal to the minimum of 0`
  (EXISTING-FIRST-23's probe, E).
- **depends on** CH-22, CH-37; soft CH-65 (until it lands, the schemas carry `verified` as it is) · **unblocks** 0
- **bin** has a `.vscode/`; a mapping is the PO's choice; nothing breaks. Reasoned.
- **proof** a board file opened in VS Code completes its keys and shows each key's sentence on hover.
- **why this rank** a block A concept placed by §3's constraint, not by its tier: it reads the tables CH-22 and CH-37
  make, so it sits right after CH-37, its last hard prerequisite (R2, "The order" 1: the second version ranked it 34,
  above CH-37 at 49); its Design can start in #123's discovery whenever the PO says.

#### 50 · CH-38 · Irrigation's chain says "the chain is broken" for life over the one signal its author declared, and any stray stderr line would say the same — severity from content, not from a channel

- **kind** story · **size** S–M · **card** none
- **fixes** the STATUS_LED by-design note (★C4's surviving half); CC-C9's asymmetry; TECH-LEAD-3 (a) · **root cause**
  because the chain treats any line the generator writes to stderr as a broken chain, so a note about a signal the person
  declared on purpose has the weight of a failure (RC-CC-2; `check_spine.py:374-375`)
- **removes / adds** removes the stderr → PROBLEMS rule and the `placed − claimed` note as a problem; the generator's
  notes become values with a kind, returned in-process (TL-M-A; `check_spine` imports `emit_board` already) — or, as the
  S step, a `NOTE_PREFIX` constant both files import (CC verify); a declared signal is reported on the schematic line;
  the four circuit-gap notes stay problems because they are gaps (`--requirements` pre-warns three of four, CC verify);
  any other stderr line is could-not-run; the unserved note prints in every outcome, as the JSON already does (CC-C9).
  `how-it-works.md:37` and `build.md:41-43` change.
- **test**
  `test_check_spine.py::test_a_signal_the_file_declares_is_said_on_the_schematic_line_and_does_not_break_the_chain`;
  `::test_a_stderr_line_that_is_no_note_is_could_not_run`; the test at `:1085-1098` extended.
- **prints** `[ok  ] schematic  46 trace(s) written; 1 signal of yours assigned and left for you to wire: STATUS_LED`.
- **depends on** — · **unblocks** 0
- **irrigation** `check_spine` exits 0 for the first time; a board with a dangling assigned pin then records `built` —
  said on the card; **bin, plant-alarm** none. Reasoned.
- **proof** `check_spine.py irrigation.requirements.json` on a copy exits 0 with `[ok] build`.
- **why this rank** tier 3: a verdict wrong by agreement stops being read (irrigation `DIARY.md:134-135`: "as build.md
  says it will be"); it unblocks none; key (b): a removal; class 2, recorded in irrigation's own diary, after CH-37 by
  key (g) (no K id).

#### 51 · CH-39 · The rules file is a snapshot taken whenever `init` ran, the pages and one printed line give two orders and blame the person, and the floating-input rule cannot be told what the record already says — seed the derived half where the picks are, and give the rule its words

- **kind** story · **size** M · **card** #79 (P145), #45 (P111), #48 (P114) · **decision** Q4
- **fixes** K45, K46 (with G7), K63's I²C and goal halves (G9); CC-MC-1, -2, -5, -6; DOCUMENTATION-10; USER-HUMAN-8, -15
  · **root cause** because the rules file holds the person's answers beside derived facts copied once, whenever `init`
  happened to run, so the order of two commands decides what `check_all` sees; and the rule has one word for an input,
  so a record that says why its input cannot float has nowhere to say it (RC-CC-1; RC-CC-8 as corrected: irrigation's
  four entries were typed by its author on 2026-09-29, a day before seeding existed — CC verify, `c6c583e`)
- **removes / adds** removes "after a build, run `init` again with `--force`" wherever it stands — `README.md:74`,
  `:155`; `journey.md:579`, `:717-722`; `commands.md:30`, `:49-53`; `commands/init.md:36-42`, `:47`, `:60`;
  `agents.md:149` (E my grep and the critic's, G2) — and the line `init_project.py:485` prints ("build, then re-run with
  --force", recorded at `journey.md:579`), which would otherwise go on telling the person what the pages stopped saying;
  and the sentence that blames the person (`compare_design.py:254-259`, `check_physics.py:471-478`). Adds: the derived
  half — rail names, declared inputs, host-pulled bus lines — seeded by `parts.py --requirements`, which already holds
  the picks and the records (CC-MC-6), never by a check; a need key saying why a floating input is harmless here — a
  current load, a module-side pull, gated by another pin — with `verified` and `source`, read by the seed and the rule
  (CC-C3 widened by CC-MC-5); `//` notes that state the rule, never the origin, and a per-entry note for a pin left out
  (CC-MC-2); the bus fields asked only when a bus exists; for a battery-powered design, one field — the sleep current —
  marked needs-measurement (G7, K46: "a battery node's one number that matters … is never asked"); `init` reads the goal
  from the project's needs when they hold one, instead of asking again (G9); Q4 decided (zero derived rules after the
  records were read: `ok` with `checked: 0` and the reason, or could-not-run as today). Until the code lands, the pages
  say one order — a day's documentation fix.
- **test** `test_needs.py::test_requirements_seeds_the_derived_rules_and_keeps_every_answer`;
  `test_init_project.py::test_an_input_whose_record_says_why_floating_is_harmless_is_not_seeded_and_the_note_says_which`;
  `::test_init_does_not_ask_a_goal_the_needs_hold`;
  `::test_a_battery_design_is_asked_its_sleep_current_as_needs_measurement`;
  `test_compare_design.py::test_an_empty_rule_list_after_the_records_were_read_answers_as_decided`.
- **prints** `rules.json: seeded 2 input(s), 2 bus line(s), 3 rail(s) from the picks — every answer kept` ·
  `Valve1.SIGNAL left out of must_not_float: its record says it holds its own level (a current load: the opto's LED
  behind a resistor — open is off)`.
- **depends on** CH-6, CH-7; Q4 · **unblocks** 0
- **bin** its hand-written rules are untouched (no requirements file); **irrigation** one record key, and its four
  entries deleted by its owner (they are his); **plant-alarm** its first seed would list the amplifier's four inputs and
  fail them unless spark's DFR0954 record gains the key first (CC-MC-5, #79) — said before, not found after. Reasoned.
- **proof** on a copy of irrigation `check_all` shows no `[FAIL]` and `init --force` does not bring the entries back; the
  K46 sequence reads `rules-vs-netlist [ok]` with no `--force` typed.
- **why this rank** tier 3: two documented orders give two `check_all` answers, and a FAIL stands that the record's own
  words refute; it unblocks none; key (b): ten copies of a sentence removed; class 2, met by an agent (K45).

#### 52 · CH-46 · An agent tells a design fault from a tool's limit by matching strings — a closed `kind` word on every stage and item, a filled `next`, and the converter's own JSON

- **kind** story · **size** M · **card** none (P43 #11 closed; its shapes parked under #52 P118) · **decision** Q14
- **fixes** USER-AI-AGENT-3, -5, -9; UAA-M-A, -M-D, -M-E; FB-M8; TECH-LEAD-3 (b), -11 · **root cause** because the kind
  of a failure — the design, an input, a tool, a simulator's limit, a crash, the store — is carried only in prose and
  substrings (`CONVERTER_HAS_NO_PART`, `check_spine.py:216`; the `Traceback` prefix `agents.md:322` teaches), so an
  agent's branching is string matching
- **removes / adds** removes the substring classifiers and, row by row, `agents.md:297-333`'s exception list. Adds a
  closed `kind` (design, input, tool, limit, crash, store) on `check_spine`'s stages, `check_all`'s results and
  `parts.py`'s problems and unchecked; `--json` on the converter, `tools.py --status`, `init_project.py` and
  `emit_board.py`; `next` filled by every refusal that knows its command, or removed from the envelope (Q14); one
  envelope shape in `tests/test_json_contracts.py`.
- **test** `test_json_contracts.py::test_every_emitted_item_has_a_kind_from_the_set`;
  `::test_a_refusal_with_a_fix_has_a_next_the_parser_accepts`.
- **prints** `[????] simulation (limit) the stand-in has no pin for GPIO43 …` — one word to branch on.
- **depends on** CH-16, CH-31, CH-45 · **unblocks** 0
- **bin** its Makefile reads text, not spark's JSON shapes — reasoned (CH-68 pins the calls).
- **proof** `agents.md`'s exception list shrinks to rows whose cards are open.
- **why this rank** tier 3: the shape behind several tier-1 fixes, but nothing silent waits on it; it unblocks none; key
  (b): it removes the substring classifiers; class 2, met in the agent lens's runs (no K id), after CH-39 by key (g).

#### 53 · CH-48 · `--describe`, the contract agents read first, is wrong in three places, `tools.py` answers no JSON, and six agent pages spell the store's path — test the contract, add the JSON, point at one sentence

- **kind** chore · **size** S–M · **card** #23 (P92)
- **fixes** K57; K58's documentation half; DOCUMENTATION-11, -19 · **root cause** because `--describe` is tested for its
  arguments, not for what each operation returns (DOCUMENTATION-19), and the pages name the store by its default path
- **removes / adds** removes the six literal `~/.local/share/spark` paths in `agents/` and `commands/` (one pointer to
  "your store" instead; R1 recounted six); `agents/datasheet-reader.md` loses `Write, Edit` once `--fact-set` is shown
  to set every field it fills (— today, SL verify C11 (f)). Adds a test of `--describe`'s effects against each
  operation's answer; `tools.py --status --json`; #23's grep as a docs test. #125 edited `agents.md`, and P181 (#127, in
  Review) edits it again — its F4 corrects the JSON row this change's describe test leans on — so this change follows
  it.
- **test** `test_parts.py::test_describe_declares_what_each_operation_returns`;
  `test_docs.py::test_no_agent_or_command_page_spells_the_store_path`.
- **prints** `agents/parts-researcher.md:53 spells the store's path — point at docs/guide/how-it-works.md#your-store`.
- **depends on** CH-16 · **unblocks** 0
- **bin** its CLAUDE.md names `parts.py --kept` — unchanged, reasoned.
- **proof** `grep '\.local/share' agents commands` prints nothing — #23's own proof.
- **why this rank** tier 3: the store cannot move (P178) while six agent sentences spell its path; it unblocks none; key
  (b): a removal; class 2 (the contract an agent reads first), a code read (K57).

#### 54 · CH-43 · README's one typed block ends in an exit 2 it predicts and is outside the gate — end it where a shell finishes, run it, and show its output

- **kind** chore (docs) · **size** S · **card** none · **decision** Q19
- **fixes** K69; DOCUMENTATION-14; DR-M6, DR-M8; USER-HUMAN-16 · **root cause** because README's block leaves out the
  steps the idea page requires and ends at the tally, which only Claude Code can finish, and the gate never runs it
  (RC-DR-2)
- **removes / adds** removes the `--tally` line and the sentence explaining its exit 2; the block writes its needs file
  in the project, keeps `--needs-set`, `--match`, `--pick`, `--requirements`, is marked `<!-- runs: exit 0 -->`, carries
  a recorded output with its note, and the tally's honest refusal is shown as a second, recorded block;
  `failed_examples` prints the last lines of a failing block (today discarded, `check_docs.py:160`) and isolates `HOME`,
  `TMPDIR` and `PATH` as well as `SPARK_HOME` before more blocks are marked `runs:` (DR-M6). P182 (#128) rewrites
  README's first screen; this block goes in with it or after it, never against it.
- **test** the gate itself (`TheDocsTest`); the existing mutation "a failing example passes".
- **prints** `README.md: the example 'python3 … --pick …' exits 1, not 0: refused, so nothing was written: …`.
- **depends on** CH-41 · **unblocks** 0
- **bin · irrigation · plant-alarm** none reads README's block (DR verify).
- **proof** a reader typing the block gets exit 0 at every line.
- **why this rank** tier 3: the one block a stranger types ends in a predicted failure; it unblocks none; key (b): a
  removal; class 3, met by an agent (K69, USER-14).

#### 55 · CH-47 · The own-board route is documented as unrun and lacks two facts the scripts hold — record it on 0.8.1, and make two refusals name the field

- **kind** bug (docs) · **size** M · **card** none
- **fixes** K70's runnable part, K72, K73; DR-4 as narrowed (the field's name is already on the page,
  `how-it-works.md:173`) · **root cause** because the own-board pages are the smart bin's workflow and say "not run",
  and two refusals do not name the field a person must fix (RC-DR-3, RC-DR-4 as corrected)
- **removes / adds** "this was not run for these docs" (`how-it-works.md:156-157` at `4a18333`; P181 (#127) adds the
  own-board step's example line and says to commit the kept header, its F3, so this block records what F3 leaves) leaves
  with recorded blocks beside it: the `--validate` refusal of an unedited copy (`runs: exit 1`, offline), then ok;
  `check_vendor_pins` recorded only (network, `gh`); how to list the variant folders; `--keep`/`--kept` for a board's
  documents; the 404 sentence names `vendor.arduino_variant` and the listing; `--fetch <board>` refused truthfully, exit
  2; after CH-24 the route is that command.
- **test** two `runs:` blocks; `test_check_vendor_pins.py::test_a_404_names_the_variant_field_and_the_listing`;
  `test_parts.py::test_fetch_of_a_board_id_says_it_is_a_board`.
- **prints** `vendor.arduino_variant names no folder under variants/ of espressif/arduino-esp32 — list them: gh api
  repos/espressif/arduino-esp32/contents/variants --jq '.[].name' | grep -i <vendor>` · `firebeetle2-esp32s3 is a board;
  --fetch takes a part — keep a board's document with --keep <file> --url <url>`.
- **depends on** CH-24 (#125: merged, met) · **unblocks** 0
- **bin** its variant is valid — unchanged, reasoned.
- **proof** a second person makes a validated board file from the page alone without meeting G0.1 or G0.9.
- **why this rank** tier 3: after CH-24 it is that command's page; it unblocks none; key (b): a removal; class 3, met by
  round 0 (K70), after CH-43 by key (g).

#### 56 · CH-57 · The code's private places are fewer than the spec's, so kept documents may sit inside a git work tree; a system with no file locking says nothing; a download has no size cap; and a file at the store's root no place names — make spec and code agree, and say the rest

- **kind** chore · **size** S · **card** none · **decision** Q29 (the catalog's and downloads' modes), Q33 (platforms),
  Q45 (the root file)
- **fixes** K15 · **root cause** because the code's list of private places (`store.py:96`, five places) is shorter than
  the spec's "all private" (`docs/2026-10-04-store-design.md:120`), and the no-lock branch was written as a comment, not
  as a line the person sees (`store.py:28-30`) (RC-SL-7); and so `sources`, outside `PRIVATE`, is not refused inside a
  git work tree by `_make_ready` (`store.py:211-214`), and a store whose home sits in a repository keeps vendor
  documents where one `git add .` publishes them (R2, CH-57 row)
- **removes / adds** `sources` into `PRIVATE` (§5.8 promises twice that document bytes are never published; SL verify —
  not the spec shrink SL-C12 leaned to, §4); the place chmod'ed, not `home()`; `catalog` and `downloads` are Q29 against
  P178's shared direction; one stderr line where `fcntl` is absent — README names macOS and Linux and has no lines for
  Windows (E `README.md:85-91`), so after Q33 that line may become a refusal; `FETCH_MAX_BYTES`, named and said in its
  refusal; the kept-name half — names Windows or exFAT refuse (G10) — waits on Q33; `--audit` names a file at the
  store's root that no place names — today `b12-kept-from-the-bin.jsonl`, 6,575 bytes, `0644`, B12's URL proofs written
  by hand (`scrum/PRODUCT_BACKLOG.md:1081`) — and Q45 asks where it belongs.
- **test** `test_store.py::test_the_private_places_are_the_ones_the_spec_names`;
  `::test_a_download_past_the_cap_is_refused`; `::test_no_file_locking_is_said`;
  `::test_a_kept_document_inside_a_git_work_tree_is_refused`;
  `test_parts.py::test_audit_names_a_file_at_the_store_root_no_place_names`.
- **prints** `<url> is 61 MB and spark keeps at most <cap> — download it yourself and --keep it` · `this system has no
  file locking (fcntl): two writers at once could lose a write — run one spark command at a time`.
- **depends on** Q29, Q33, Q45 (each for its half) · **unblocks** 0
- **bin · irrigation · plant-alarm** none; the PO's store is on one Mac, its home already 0700. Reasoned.
- **proof** `ls -ld` of a fresh store matches the spec's sentence.
- **why this rank** tier 3, not tier 1 where the second version had it: no answer reports anything false, a file's mode
  is never reported, and his home is `0700`, so no other user reaches its `0755` folders (R2, CH-57 row) — spec against
  code; it unblocks none; class 1 (kept documents can be published), but an addition, so after the tier's removals by
  key (b).

#### 57 · CH-65 · `verified: true` means four things — the maker's words, measured, computed, proven by use — and `--show` calls facts verified that cite no kept document — the typed `origin` the PO decided on 2026-10-06

- **kind** story · **size** M–L · **card** #85 (P151) · **decided** (D the PO, 2026-10-06, #17 comment T11:14, decision
  2); its form is P151's
- **fixes** K65 (R1-Missing 8) · **root cause** because one flag and a prose source carry four kinds of evidence, so a
  reader cannot tell a datasheet figure from a bench measurement, and `--show` prints "verified" for a fact whose
  document was never kept (K65; `parts.py:1354-1375`: the skeleton has `verified` and `source`, no `origin`)
- **removes / adds** `origin` per fact — `maker` (a document's words), `measured`, `computed`, `proven-by-use` — with its
  source; `verified` read as an alias for one release, then removed; `--show` says "verified" only for a fact whose
  document is kept; the schemas (CH-28) carry it.
- **test** `test_parts.py::test_every_fact_has_one_origin_word`;
  `::test_show_calls_verified_only_a_fact_whose_document_is_kept`;
  `::test_a_record_with_only_verified_reads_as_its_alias`.
- **prints** `vl6180x-breakout.pin_order: origin maker (datasheet p.4, not kept) — keep it with --keep <file> --url <url>
  to make it checkable`.
- **depends on** — · **unblocks** 0; soft CH-28
- **irrigation** its seven records read through the alias until migrated; **bin, plant-alarm** none. Reasoned.
- **proof** `--show` on the S3 prints the 355 mA figure with `origin maker (WROOM-1 datasheet v1.1, Table 11)` and says
  whether that document is kept.
- **why this rank** tier 3: an unverifiable fact the PO decided to fix four days before this list and nothing built
  (K65); it unblocks none in the epic; class 2, met by an agent's read (K65), first of the class's additions by key (g).

#### 58 · CH-67 · The board's firmware facts reach no one, and a typo in them is an absence — the facts into `pins.py`, a shape check; the firmware check waits on the PO's own cut

- **kind** story · **size** S + S (the check, L, held) · **card** #7 (P59), #8 (P74), #64 (P130) · **decision** Q22
- **fixes** K67 in part; RC-FB-4; FB-M2, -M3, -M6, -M7 · **root cause** because the board record's deep-sleep facts have
  no consumer, so nothing validates them and nothing hands them to the firmware that needs them (RC-FB-4); the check of
  firmware against the pin map was cut by the PO on 2026-09-29 (RC-FB-3 as corrected; `066c4af`)
- **removes / adds** the record's deep-sleep facts (the wake API, one level for all pins, the C6's missing
  `wake_on_ext0`, `simulated_by_wokwi`) written into `pins.py`'s header by `assign_pins --emit-pins` — facts, never
  behaviour, inside the 2026-10-01 boundary (FB-M7); a shape check for the `deep_sleep` block, so a typo and an absence
  differ (FB-M6). Held for Q22: the use-against-map check (FB-C4), which re-adds the check the PO cut; its case is that
  projects now carry `firmware/pins.py` (P36); it is a coverage observation, not the bin's literal triangle (FB-M3);
  "has" = `pins` ∪ `pin_roles[*].gpio`; CH-2 first.
- **test** `test_assign_pins.py::test_pins_py_carries_the_board_s_deep_sleep_facts`;
  `test_boards.py::test_a_misspelt_deep_sleep_key_is_named`.
- **prints** `deep_sleep.single_pin_apii is not a deep-sleep fact any reader knows — did you mean single_pin_api?`.
- **depends on** CH-2 (for the held check); Q22 · **unblocks** 0
- **irrigation** its `pins.py` gains a header block on the next `--emit-pins`; **bin** its own checks; **plant-alarm** no
  firmware. Reasoned.
- **proof** irrigation's regenerated `pins.py` carries the wake facts; a misspelt key is named.
- **why this rank** tier 3: facts nothing reads, made checkable; it unblocks none; class 2, met by the 2026-10-01
  council (K67), after CH-65 by key (g); the check itself is the PO's call.

#### 59 · CH-44 · A figure on a check's line drops the source the record holds — every printed figure names its key and its source, or "unverified" with its who and why

- **kind** story · **size** S · **card** none (related #42 P108)
- **fixes** USER-HUMAN-9; UH-M-c · **root cause** because `check_physics` prints the who and why of each **unverified**
  figure (`check_physics.py:305-306`) and drops the source of each **verified** one (`:309-310`), so the 355 mA on
  README's line cannot be traced from the line (R1 corrected the first version's "drops them")
- **removes / adds** beside every figure a check prints, its record key and its source — and, once CH-65 lands, its
  `origin` word.
- **test** `test_check_physics.py::test_every_printed_figure_names_its_key_and_its_source`.
- **prints** `? V33: draws 355 mA (Mcu module_peak_a, WROOM-1 datasheet v1.1, Table 11) of 1.50 A (regulator_3v3_a,
  unverified: the dev board's rating, not found in a kept document)`.
- **depends on** soft CH-68 (until it lands, the bin's `check_physics` line is reasoned) · **unblocks** 0
- **bin** `check_physics` runs in its `make check` (`Makefile:228`): its lines gain words, its exit is unchanged — shown
  by CH-68's test once it lands.
- **proof** README's 355 mA line is traceable from the line alone.
- **why this rank** tier 3: the PO's own "a wrong number" turned around — right today, unreadable as right; it unblocks
  none; class 2, met in the user lens's run, and with no K id after CH-65 and CH-67 by key (g).

#### 60 · CH-73 · The vendor-pin check says whose copy answered in two shapes and by a word, so a stray `.spark/` up the tree and a second copy of spark both read as "the project's" — one key that names the folder, live and offline

- **kind** bug · **size** S · **card** none (N13, N24, N27, raised by #125's council) · **fix now**
- **fixes** N13, N24, N27; R2-Missing 1 · **root cause** because the answer names its source in two shapes — a file's
  name inside `source` when offline, a `wrote` path when live — and decides "the project's" or "spark's" by comparing
  one folder with spark's own cache (`check_vendor_pins.py:149-151`), while a project is whatever folder up the tree
  holds `boards/active.json` or `.spark/` (`boards.py:135-147`); so a stray `boards/.spark/` and a second copy of spark
  are both "the project's", and an agent reads two shapes for one fact (E `docs/observations/INDEX.md:282`, `:293`,
  `:296`)
- **removes / adds** one key on every entry, live and offline: `header: {folder, file}`, the folder being the path the
  project walk chose, and the word `spark` only when that folder is the running plugin's `plugin_root()` (CH-4); the
  text line names the folder. `source` keeps its words for one release, then goes; `agents.md:253`'s row says so, after
  P181 (#127) has corrected that row for could-not-run entries (its F4). Which folder should own a board file at all
  (N24's stray `boards/.spark/`) is left to `boards.project_root` as #125 made it: this change makes the choice visible,
  not different.
- **test** `test_check_vendor_pins.py::test_every_entry_names_the_folder_whose_header_answered` (live and offline);
  `::test_a_stray_spark_folder_up_the_tree_is_named` (N24); `::test_a_second_spark_copy_is_not_called_spark` (N27);
  `tests/test_json_contracts.py` pins `header`.
- **prints** `firebeetle2-esp32s3: offline, header from ~/Development/spark/.spark/cache/ (a project folder — not the
  running plugin)`.
- **depends on** — · **unblocks** 0
- **bin** `vendor-pins-agree` (`Makefile:220`) reads the exit only — unchanged, reasoned (CH-68 pins it); **irrigation,
  plant-alarm** do not call it (FEASIBILITY-11).
- **proof** an offline check from the bin names spark's cache folder, and one from a scratch folder holding a stray
  `boards/.spark/` names that folder.
- **why this rank** tier 3: a source named by a word that can be false is an unverifiable answer, and rare on his
  machine; it unblocks none; class 2, raised from a code read by #125's refuter, so last of the class's additions.

#### 61 · CH-40 · Recorded outputs are re-recorded by a hand paste that did not happen at three releases — promote the recorder that exists, bind and classify every block, and check it when the version changes

- **kind** story · **size** S + M + M · **card** related: #13 (P77), #28 (P102d) · **decision** Q18
- **fixes** K68; DOCUMENTATION-2, -3, -15, -17; DR-M1…DR-M4; RISKS pre-mortem cause 8 · **root cause** because the gate
  proves that an output carries a provenance note, never that the note is current, and nothing re-records (RC-DR-1)
- **removes / adds** removes the hand paste and `journey.md:195`'s "recording script" sentence once the script is
  tracked. Adds: the recorder under `.superpowers/` (102 + 176 + 22 lines, gitignored, path-bound to a gone worktree; R1
  re-listed them) promoted or deleted before a third is written (Q18: promote, cog, or mdsh); each block bound to its
  command and its store state (8 or 10 of 42 sit under no command — DR verify M2 counted 8, DOCUMENTATION-17 counted 10;
  the difference is —); two classes, re-recordable and recorded-only; `--check` in `tools/check_commit.py` on a commit
  that changes `plugin.json`'s version (no release gate exists, DR-M4); the count of outputs behind the version as a
  report line, never a failure (a patch that changes no output would raise 44 false alarms, DR verify); DoD 10 gains "a
  release re-records and `--check` passes".
- **test** `tests/test_record_docs.py::test_redaction_of_paths_session_ids_and_the_tsci_line`;
  `test_check_commit.py::test_a_version_change_runs_the_recorder_check`;
  `test_docs.py::test_an_output_recorded_on_an_older_version_is_counted_not_failed`.
- **prints** `journey.md: the output at line 81 (re-recordable) was recorded on spark 0.7.0; the plugin is 0.8.1`
  (report); at a version change, the block's diff and `re-record it, or mark it recorded-only`.
- **depends on** Q18 · **unblocks** 0
- **bin · irrigation · plant-alarm** none reads the guides (DR verify).
- **proof** after the next version bump, every re-recordable block's note names the shipped version.
- **why this rank** tier 3: "a pasted output is real" is the rule every page rests on; FEASIBILITY-12 and the
  documentation lens would pull it forward as enabling work, which is not a key (R1) — Q31 lets the PO pull it; it
  unblocks none; class 3, met by an agent (K68).

#### 62 · CH-42 · A stranger's first pages say where the checks' mistakes show and nothing of the store's — one section, written for the outputs tier 1 leaves, and the sync case said

- **kind** chore (docs) · **size** S · **card** none
- **fixes** DOCUMENTATION-8, -18; DOC-M-D3; FE-MISSING-7 · **root cause** because the pages tell the reader what to do,
  not how a wrong turn looks, and for the store half the refusals are the ones K56 withholds
- **removes / adds** `agents.md`'s "What never to assume" and the command pages gain, in their symptom → cause → what to
  do shape: the store each answer names (CH-1), a held part in the listing (CH-72) and its release command (CH-25), the
  words `--need` missed and what it did not search (CH-18), a pick's recorded fit (CH-17), the drawer's silent count
  (CH-19); `how-it-works.md` gains one paragraph on a synced store — what spark tolerates (a folder sync's conflict
  copies, named and refused, CH-9) and what it does not (two machines writing at one moment: the lock serialises one
  machine only, §2.3) (FE-MISSING-7); `commands/idea.md:11`'s pointer to "docs/2026-10-04-store-design.md §8 S and M"
  becomes the page's own words (DOCUMENTATION-18). Where it touches README, it goes with P182 (#128). The PO may instead
  take DOC-M-D3's original as a one-day stopgap before tier 1 — sentences describing today's silences, each naming its
  card and retired by CH-41's checks.
- **test** the gate's name checks over the new section; CH-41's retired-sentence check over the stopgap.
- **prints** — · **depends on** CH-1, CH-17, CH-18, CH-25 · **unblocks** 0
- **bin · irrigation · plant-alarm** none.
- **proof** a reader of `agents.md` alone can tell "nothing owned" from "the wrong store".
- **why this rank** tier 3: every recorded stall was in the store half and no page says what one looks like; an addition
  that waits on four changes; class 3, a lens's read, so last of the tier.

### Tier 4 — friction

All six unblock none; the removals first (CH-50, CH-56, CH-53, CH-58), then the additions. CH-58 came down from tier 1
(R2).

#### 63 · CH-50 · A need cannot be dropped or renamed and a pick cannot be cleared; the page says "fix it by hand" — drop and clear through the same set-only door

- **kind** story · **size** M · **card** none · **decision** Q20 (a tombstone that stays in the file, or removal)
- **fixes** K35; the way out of K34 · **root cause** because the needs file took the drawer's set-only rule without the
  drawer's tombstone, so nothing a command writes can say "gone" (RC-NM-3; `docs/2026-10-04-store-design.md:328`)
- **removes / adds** removes "there is no removing or renaming a need yet, so a wrong one is fixed by hand"
  (`commands/idea.md:25-26`, R1's pointer) and the two-space refusal of an empty pick (`needs.py:287`); adds `{"id":
  "temp", "drop": true}` to `--needs-set` and `--pick <project> temp=` (empty) as a clearing, both releasing holds
  through one extracted `_reserve` (two copies become one); a rename said as a drop plus an add, and that history lines
  keep the old need id (NM verify).
- **test** `test_needs.py::test_a_dropped_need_releases_its_holds_and_is_said`;
  `::test_an_empty_pick_clears_and_releases`; `::test_a_drop_is_set_only_a_retry_changes_nothing`.
- **prints** `dropped temp — released dfrobot-sen0193: 1 of 1` · `temp: no pick — released …`.
- **depends on** CH-17; Q20 · **unblocks** 0
- **plant-alarm** its file reads as today; **bin, irrigation** have no `needs.json`. Reasoned.
- **proof** the K35 sequence on a copy ends with the need gone and `used_in` restored, by commands alone.
- **why this rank** tier 4: the only edit path is a hand edit of a file the tool validates on read — friction, not harm;
  key (b): a removal; class 1 (the person's record stays wrong until edited), met by USER-10 (K35).

#### 64 · CH-56 · `emit_footprint --json` prints TSX, and a generated footprint says "NOT the ? mm on the vendor drawing" — JSON or could-not-run, and a sentence for a missing drill

- **kind** bug · **size** S · **card** none
- **fixes** K28, K27 · **root cause** because `main` writes the module to stdout and returns before the function that
  alone knows `--json`, and the header template fills a missing drill with `?` (RC-BR-4; `emit_footprint.py:162-163`,
  `:229-230`)
- **removes / adds** removes the early `return` at `emit_footprint.py:230` for `--json` (`--json` without `--out` is
  could-not-run) and the `"?"` default; the header says the drawing states no drill and the hole is sized from the pin.
- **test** a second case at `tests/test_json_contracts.py:164` (at `4a18333`; BR-M9);
  `test_emit_footprint.py::test_a_board_with_no_vendor_drill_says_so`.
- **prints** `emit_footprint.py: --json needs --out: the module goes to a file, the report to stdout`.
- **depends on** — · **unblocks** 0
- **bin** does not call `emit_footprint`; `check_spine` calls it with `-o` — unchanged, reasoned.
- **proof** the command round 0 typed prints JSON or the refusal.
- **why this rank** tier 4: an agent asking for the envelope gets code, exit 0 — but the code is the sign; small and
  loud; key (b): a removal; class 2, met by round 0 (K28), and key (e) — a board's footprint — puts it before CH-53.

#### 65 · CH-53 · `--need` is an AND over four fields while `--match` reads functions and the drawer — one word test for both, ranked by words hit, then by having a record

- **kind** story · **size** M · **card** #10 (P39), its second step
- **fixes** K33 (step 2), K36's ranking case (G8) · **root cause** because two matchers answer one question with two
  rules and two vocabularies, and neither ranks a candidate with a record above one without, so a record-less L298N
  outranks the L9110S that has one (RC-NM-1; K36)
- **removes / adds** removes `parts._matches` as a separate rule; adds one `words_hit` over id, name, kind, aliases,
  every `function.what` and live drawer entries, used by `--need` and `needs._what_matches`; `--need` ranked by words
  hit, then by having a record (G8), a drawer entry marked `(drawer, no record)`. A documented behaviour changes:
  `parts.py:1334`'s docstring, `tests/test_parts.py:791-797` (`["motor", "driver"]` becomes "ranked first with 2 of 2"),
  the recorded blocks at `journey.md:524` and `:533` (CH-40), and what "a match is the answer" means
  (`commands/research.md:24`). Synonyms the store lacks (`footswitch`) are aliases from the data pass (CH-19, Q6), not a
  matcher rule.
- **test** `test_parts.py::test_need_reads_a_function_word_the_name_does_not_say`;
  `::test_need_offers_a_drawer_entry_with_the_word_and_names_it_record_less`;
  `::test_a_candidate_with_a_record_ranks_above_one_without_at_equal_hits`.
- **prints** each line `matched: inlet · missed: 12, v`.
- **depends on** CH-18, CH-19 · **unblocks** 0
- **bin** none; **irrigation**'s DIARY phrases answer differently (history, not re-run). Reasoned.
- **proof** `--need temperature` finds a catalog record whose function says temperature and whose name does not; the
  L9110S ranks above the L298N for "motor driver".
- **why this rank** tier 4: step 1 (CH-18) removes the silent misdirection; this changes a documented ranking and waits
  behind it; key (b): a removal; class 2, met by an agent (K33).

#### 66 · CH-58 · The transcript reader cuts a line at a Unicode line separator, so the tally counts lines as unreadable and never says why — split bytes on newline, as the history reader already does, and say why a line is unreadable

- **kind** bug · **size** S · **card** none (C-15)
- **fixes** K62; FE-MISSING-5 · **root cause** because `str.splitlines()` also splits on U+2028, U+2029 and U+0085,
  which a transcript line may hold, so one line becomes two unreadable halves (`cost.py:110`) — counted and said
  (`cost.py:274-275`, `parts.py:2154`), which is a sign, but one that names no cause (R2)
- **removes / adds** one `lines_of(bytes)` used by `cost.py` and `store.events` (`store.py:284-286`); the
  unreadable-lines sentence names the first such line's file and why it failed — not JSON, or no time.
- **test** `test_cost.py::test_a_line_separator_inside_a_transcript_line_does_not_cut_it` (a real line can be the
  fixture, the critic).
- **prints** `2 lines of the transcripts could not be read and are left out of the count: <file>:<line> is not JSON (cut
  mid-write?)`.
- **depends on** — · **unblocks** 0
- **bin · irrigation · plant-alarm** none.
- **proof** a transcript with U+2028 inside a line counts its requests. Not only reasoned: over 398 transcript files
  under `~/.claude/projects`, 8 hold a raw U+2028, 4 a U+2029 and 1 a U+0085, 25 lines in all (E the critic's count,
  2026-10-10); whether any sits inside a tallied window is —.
- **why this rank** tier 4, not tier 1: `--tally` prints the count of unreadable lines (`cost.py:274-275`), a sign by
  §3's own definition, so the catalogue's K62 grade "with no sign" is wrong (R2); key (b): two splitters merged into
  one; class 3, a code read, last of the tier's removals.

#### 67 · CH-52 · The store's own words are shown nowhere before a need is written, and `[other words]` has no legend where it prints — show them, and say what each mark means

- **kind** story · **size** S · **card** related: #10 (P39)
- **fixes** K38; NM-M2; USER-HUMAN-4's legend · **root cause** because `does` is closed and `what` is open by decision,
  and the store's 19 distinct (does, what) pairs — 14 written, 5 through `KIND_FUNCTION`, NM verify, R1 — are listed by
  no operation, so a person learns them from refusals (RC-NM-9)
- **removes / adds** under a need with no word match, the verb's words in the store and the "one word more" case; one
  legend line under every `--match` answer that carries a mark; `idea.md`'s S step says to write `what` in the store's
  words where one fits; a sentence that code never reads `condition`.
- **test** `test_needs.py::test_a_need_with_no_word_match_is_shown_the_verb_s_words`;
  `test_parts.py::test_a_match_answer_with_marks_carries_the_legend`.
- **prints** `the store's words for sense: distance, soil-moisture — your need says "distance sensor"; the store's word
  is "distance" — one word more` · `[other words] = the same verb, not your words — your call; (drawer) = owned, no
  record — reserved, not placed`.
- **depends on** CH-18 · **unblocks** 0
- **bin · irrigation · plant-alarm** none.
- **proof** the `mp3-player` / `audio-player` pair on a copy shows both words under `sound`.
- **why this rank** tier 4: the person learns the vocabulary from refusals today; cheap; an addition; class 2, met by an
  agent (K38), before CH-51 by key (g).

#### 68 · CH-51 · The candidate list cuts at eight and the cut is unreachable — list the cut by its words and ids

- **kind** story · **size** S–M · **card** related: #5 (P76, the "obstacle ahead" example)
- **fixes** K41 · **root cause** because the list ranks by place, cuts at eight before paging, and says only how many it
  cut (RC-NM-6; `parts.py:1955-1956`)
- **removes / adds** replaces `… N more, none with the need's words` with the cut grouped by `what`, ids under each,
  capped with `+n` per word (NM verify: ids per word grow once the 91 entries carry functions); `more` in the JSON as
  word → ids (no reader of the old integer, NM verify).
- **test** `test_needs.py::test_the_cut_candidates_are_listed_by_their_words_and_reachable_in_json`; the cap test at
  `tests/test_needs.py:327` stays.
- **prints** `… 3 more under other words — distance: vl6180x-breakout (library), sen0311 (drawer); soil-moisture:
  sen0193-soil-moisture (shelf)`.
- **depends on** CH-19 · **unblocks** 0
- **bin · irrigation · plant-alarm** none.
- **proof** the #5 example on a copy shows the rangefinders under `distance` on the first page.
- **why this rank** tier 4: the right answer is one page away, and "… 3 more" is the sign; the 4 KB budget holds; an
  addition, class 2, met by an agent (K41).

### Tier 5 — polish

#### 69 · CH-71 · `check_spine` prints the path of a work folder that is deleted a second later — say `<temp>`, or nothing

- **kind** bug · **size** S · **card** none · **fixes** UH-M-i · **root cause** because the footprint step's own report
  line, written into a temporary build folder, is printed as it is (`wrote
  <scratch>/tmp/spark-spine-…/FireBeetle2Esp32S3.tsx (32 pads, 1.00 mm holes)` before `wrote FireBeetle2Esp32S3.tsx`) ·
  **removes / adds** removes the work folder's path from the line · **test**
  `test_check_spine.py::test_no_line_names_the_work_folder` · **prints** `wrote FireBeetle2Esp32S3.tsx (32 pads, 1.00 mm
  holes)` · **depends on** — · **unblocks** 0 · **projects** none · **proof** the journey's recorded run no longer needs
  its `<temp>` redaction there · **why this rank** polish; the journey already redacts it; key (b): a removal, and class
  2 (a path that is gone), so first of the tier.

#### 70 · CH-59 · `--catalog` says 18 records and `--audit` 17 owed of the same layer — one walk, and the shadowed id named

- **kind** chore · **size** S · **card** none · **fixes** K18 · **root cause** because `--catalog` globs the folder
  itself while `--audit` walks the layers, where the shelf shadows one catalog record (RC-SL-5; `parts.py:879`) ·
  **removes / adds** removes `catalog_records`' own glob; `--catalog` lists through the one walk and names what the
  shelf shadows · **test** `test_parts.py::test_catalog_and_audit_agree_on_the_catalog_s_count` · **prints** `18 files,
  1 shadowed by the shelf (sen0193-soil-moisture)` · **depends on** — · **unblocks** 0 · **projects** none · **proof**
  both commands print one count · **why this rank** two true counts that look like one wrong one; key (b): a removal;
  class 3.

#### 71 · CH-60 · A hyphenated chip name is refused, a stray `>` survives a URL, and a record's sentence can forge Markdown — three small contract fixes

- **kind** bug · **size** S · **card** #19 (P87) for the Markdown half · **fixes** K50, K51 · **root cause** because the
  name rule accepts letters, digits and `_` only (`parts.py:185`, `:517`), the URL cleaner stops one character early,
  and a record's sentence is written into a Markdown file as typed (`sim_project.py:108-115`) (RC-CC-7) · **removes /
  adds** a chip-name rule of letters, digits, `_` and `-` (whether Wokwi accepts a hyphen is H); the `>` after a removed
  URL goes with it; a record's sentence normalised to one line where it is read · **test**
  `test_parts.py::test_a_hyphenated_chip_name_is_a_name`;
  `test_needs.py::test_a_stray_bracket_after_a_url_leaves_with_it`;
  `test_sim_project.py::test_a_line_break_in_a_record_s_sentence_cannot_forge_a_heading` · **prints** the existing
  sentences · **depends on** — · **unblocks** 0 · **projects** none · **proof** the chain diagnosis's reproductions flip
  · **why this rank** each says what happened and loses nothing; three fixes, class 2.

#### 72 · CH-61 · No page says what spark has built so far — one sentence, per store

- **kind** chore (docs) · **size** S · **card** none · **fixes** K71; DR-7 · **root cause** because the "menu" is a
  planning artefact in the backlog, not a statement in the persona's documents (RC-DR-6) · **removes / adds** one
  sentence in README's "What it shows on the example": two gadgets built from the library as documented, and `parts.py
  --list` / `boards.py --list` print the rest — 8 library records, more in a person's store (13 on the PO's copy, DR
  verify) · **test** the gate's name checks · **prints** — · **depends on** — · **unblocks** 0 · **projects** none ·
  **proof** USER-13's question answered from README alone · **why this rank** a sentence — with P182 (#128), which
  rewrites README's first screen; the real menu is a function of the library; class 3.

### How the list becomes cards, and what lands first

The list has 72 changes: the second version's 71, less CH-62 (#125, merged), plus CH-72 (split from CH-25) and CH-73
(#125's council rows N13, N24, N27). The scrum limits are 2 per working stage, Ready 5 and at most 4 cards in flight
across both boards (E `scrum/README.md:7`). Read on 2026-10-10 (E `gh project item-list 2` and `1`): four cards are in
flight — P100 and P158 in Discovery, P180 and P181 in Review — the bin's board holds 3 in Ready and none in a working
stage, and spark's board holds none in Ready. So the second version's first slice of four working-stage cards did not
fit (R2, refuted): once P158, P180 and P181 are done and P100 stays, three working-stage cards fit; four only if P100
waits. Whether Ready 5 counts the two boards together is — (`scrum/README.md:7` does not say). How many cards close in a
week is — (18 in Done on the spark board on 2026-10-10, the 18th being P179, E; their dates —, RISKS-18).

**Cards.** One epic, P158 part 1's fixes, with stories by area, each a coherent pull request (the PO's rule: a new pull
request for every bigger feature). Existing cards are reused where named; the P178 concepts go to #123's discovery, not
to this epic; the two open documentation cards, P181 (#127) and P182 (#128), go first where a change edits their pages.

| story | changes, in rank order | existing cards it reuses |
| --- | --- | --- |
| the store says which store, and keeps the person's data | CH-1, CH-4, CH-11, CH-10, CH-3, CH-15, CH-9, CH-5, CH-8, CH-57 | #101, #114, #22, #84, #21, #65 |
| boards as records: checked, found, made, copied | CH-13, CH-21, CH-14, CH-12, CH-36, CH-54, CH-22, CH-23, CH-24, CH-63, CH-66, CH-73 | #55, #61, #99 |
| simulation stand-ins said and checked, and the step to the bench | CH-49, CH-31, CH-30, CH-32, CH-34 | #69, #7, #8, #16 |
| matching that says what it missed | CH-18, CH-17, CH-19, CH-72, CH-25, CH-50, CH-53, CH-52, CH-51 | #10, #93, #99 |
| answers an agent can act on | CH-16, CH-45, CH-46, CH-48, CH-56, CH-71, CH-59, CH-60 | #58, #23 |
| the chain judges the person's board | CH-6, CH-20, CH-55, CH-7, CH-35, CH-37, CH-38, CH-39, CH-67, CH-44 | #118, #119, #44, #59, #102, #20, #79, #45, #48, #7, #8, #64 |
| documents that stay true | CH-41, CH-43, CH-47, CH-65, CH-40, CH-42, CH-61 | #13, #28, #85; after #127 and with #128 |
| trust in the proofs | CH-26, CH-64, CH-2, CH-68, CH-58 | #82 |
| P178 concepts (#123's discovery) | CH-27, CH-70, CH-29, CH-33, CH-69, CH-28; CH-26's `--refresh`; CH-63's project → store half | #123, #96 |

**The first slice**, by rank, inside the limits as read:

- **The PO's answers, no stage limit, in week one:** Q5 (which board round A uses — the one decision that unblocks his
  round A with no code, RISKS-9), Q1 (holds), Q2 (the guard), Q6 (the data pass, with RISKS-2's before-and-after
  `--match`), Q7 (irrigation's rename, by its owner), Q35 (D8's order), Q42 and Q43 (the ordering keys and the definition
  of silent), Q44 (the stand-in flag). Q32 is answered: #125 is merged.
- **Working stages — three, once P158, P180 and P181 are done:** Build: CH-16 and CH-13 (ranks 1 and 2); Design: CH-24
  (L — the PO's first fix and the first L story on the list; its Build waits for ranks 26–27). If P100 waits, the fourth
  slot takes rank 3, CH-18, when a Build card moves to Review.
- **Ready (5):** CH-18, CH-26, CH-17, CH-21, CH-19 (ranks 3–7). CH-1 is next, at rank 8.

What the PO gets first: the agent's JSON carries what the text says; wrong silicon is refused through one chip-name
table; owned parts and shipped boards are found by search; a copy says which fields it differs in and which side moved;
and, from his answers, round A either unblocked or knowingly left waiting. The order puts the store's own guard, CH-1,
at rank 8, behind seven changes that unblock more of the epic; round 2's strongest case puts it first, and Q42 (b) or
Q35 (b) is where he says so. The ranks after the slice are taken in order as stages free up; an L story enters Design
when it is next among L stories, not when its rank reaches Build.

## 4. What not to do

| do not | why | source |
| --- | --- | --- |
| adopt SQLite, a CRDT library (pycrdt, Automerge, Yjs), Dolt, CouchDB/PouchDB, ElectricSQL/Litestream/LiteFS, git-annex/DVC/git-lfs, or a folder-sync daemon as the store's mechanism | SQLite's own page warns of network file systems and of background copies taken mid-transaction — the shape of a synced folder; a CRDT merges live concurrent edits, which a one-writer store with pull-request review does not have, and brings compiled dependencies; the others solve another problem or the half §5.8 forbids (document bytes are never shared); none is "free, few, local CLI first" | RISKS-17; FEASIBILITY-6, -9; STORE-14 (its survey table); EXISTING-FIRST-26; D the PO 2026-10-04 ("no database"), 2026-10-06 (free, few, local) |
| move the vendor-header cache into the store (the first version's CH-4), or reopen #125's design | #125 was merged by the PO on 2026-10-10 (D); it keeps the header with the project that owns the board, and the bin's `make refresh-vendor-pins` refreshes spark's shipped header; what #125's council left for P158 — N13, N14, N24–N28 — is taken by CH-4 and CH-73, not by moving the cache | R1, CH-4 row and Missing 1; R2, Preamble (2); #124 comments 2026-10-10T16:16:34Z and 17:36:24Z |
| prove "nothing writes the plugin" with a grep | a grep sees `write_text`, not where it writes: 25 direct writes outside `store.py`, most into projects, make it either red on legitimate writes or an allow-list that proves nothing; a run-time guard at the write sees where bytes land (§2.5, seam 3) | R1, Mechanism (CH-4 / R2); R2, CH-4 Mechanism |
| add a write map to the commit gate's archived-tree run (the second version's seam 3) | it sees only what the suite writes, never a person's run, and its allow-list admits the shipped-header path that N25 and N26 reach; one run-time helper refuses the write where it happens and names the path (CH-4) | R2, R2 row and Mechanism; N14, N28 |
| remove `wokwi_is_stand_in` | it is the only fact that says whether a stand-in is in use, so a rule requiring a stand-in sentence has nothing else to decide from; the bin's `CLAUDE.md:108` names it | R1, CH-32 row |
| rename `wokwi_power_pins` now | the bin's own converter copy reads that key (`mapping.ts:108` there); renaming it in the library S3 empties the bin's per-pad table (`3V3 → 3V3.1`, `GND1 → GND.1`) unless both change together; the key is documented under its name instead | R1, CH-31 row |
| check every `pins` key against the stand-in's registry | it would refuse the XIAO's nine silkscreen labels, which the bin's `make check` validates; check per GPIO — some label of each GPIO is a pin of the stand-in | R1, CH-31 row; FB verify |
| match `--need` on whole tokens | `vl6180` would stop finding `vl6180x-breakout` and `l9110` `l9110s-module`, with the suite still green; split the query into words, keep each word a substring test | R1, CH-18 row; NM-M5 |
| switch `--need` to OR over substrings | the one-letter word in "12 V inlet" would match nearly every record; words first (CH-18), ranking later (CH-53) | NM-M5 |
| put the project id in `.spark/project.json` | it is the person's brief, written by `init` only and rewritten only if it has no answers (`init_project.py:24`, `:403`); a project listed by a pick alone (plant-alarm) has none | R1, R4 and CH-29 rows |
| build a chip-keyed tools role (FB-M4's mechanism) inside this epic | one interpreter ships (the S3's); CH-13's 16-byte read turns the silent wrong-chip case into a refusal naming the chip; a chip-parameterised `roles` is a shape change (M) with one consumer; it becomes a change when a second chip's interpreter ships | FB-M4; FEASIBILITY-15; R1, CH-13 row (the guard "still earns its place") |
| give a non-importing mutant a new outcome word | `refused` already means "the row tests nothing; fix the table" (`GLOSSARY.md:108-114`); widen its entry instead of adding a word | the critic, item 4 |
| test "every text line is reachable from the envelope" | text lines are prose; without a stated mapping the test passes vacuously; test each omission by name | R1, CH-16 row |
| pull a change up the list because other changes prove themselves with it | it was applied to CH-2 and not to CH-40, and the second version still said it of CH-1; enabling work is not one of the stated keys | R1, "The order"; R2, the enabling row |
| count soft edges, or edges into P178 concepts, as unblocking | a soft edge blocks nothing and a concept is not built in this epic; counted, they ranked CH-1 first for an edge count of 7 that was 1 hard and 6 soft | R2, the unblocks row |
| stage every write of an operation as all-or-none (SL-C4 as written) | it rewrites the append-only history on every pick and is not one unit across file systems; the answer's honesty is the need, and CH-8 gives it in twenty lines | SL verify C4; FEASIBILITY §2.4 |
| shrink the store design's "all private" to the code's five places (SL-C12's lean) | §5.8 promises twice that document bytes are never published, and a kept document is marked `private_only` | SL verify RC-7, C12 |
| widen `BUILD_FACTS` (SL-C13's digest half) | it vouches for a build, which a stand-in or an outline does not change; CH-26 now reads digests, so the second version's condition is met and the answer is still no — a copy is compared through its own digest over the whole record | SL verify M3, C13; R2, CH-26 row |
| shelve every project record at `--requirements` (SL-C11 (b)) before "proven" has a meaning | four of irrigation's seven records are placeholders and would reach every project's list | SL verify C11 (b); Q27 |
| reuse no listed project name until the id exists (SL-C5's second half alone) | a moved folder would lose its holds and be listed as `proj-2` | SL verify C5 (b) |
| refuse a need's mark that disagrees with its pick (NM-C2's pair rule) | it refuses `idea.md`'s documented M-before-C order and plant-alarm's real `needs.json` on every read; CH-17 records the fit instead | NM verify C2, E; NM-M4 |
| add a `count` to a need before the one sentence | one need per instance already yields `Valve1…Valve4`, reserves four and writes four events | NM-M7; Q23 |
| give the library boards a `not_on_simulator` role (FB-C1 (c)) | 0 of their GPIOs are absent on their stand-ins; the role would spend the XIAO's only ADC pins last with a false reason | FB verify RC-1 (1); RISKS-13 |
| delete the two stand-in sentences (`boards/README.md:96-97`, the S3 note) | they are true of GPIOs and false of two names: amend them | FB-M9; DOCUMENTATION-13 |
| read the Wokwi registry from `node_modules` in a Python validator | couples a validator to an installed node package; a generated copy under `data/`, tested equal to the converter's, is the testable form (§6, split 6) | BR verify C11; EF-MISSING-7 |
| copy wokwi-boards' `board.json`/`board.svg` files into spark | the repository declares no licence; copy the chip facts with a citation, generate any board | STORE-11, STORE-10 |
| fill the XIAO's `physical.header` with through-hole rows | the XIAO is a castellated module; the honest route is a converted vendor footprint (`footprint_source`) | BR verify C9; Q21 |
| make the chain re-seed `rules.json` after a kept build (CC-C1a) | a check would write another check's input, and the file would have two authors; seed at `--requirements` | CC verify MC-6, C1 |
| fail the docs gate on a recorded output's version (DR-1 as a failing check) | a patch release that changes no output raises 44 false alarms; a version is provenance, a diff is currency | DR verify Change 1 |
| count long lines in the docs gate (DR-6's measure) | README's long lines are 8 table rows of 10, which Markdown cannot wrap; a rule that fails, or nothing | DR verify Change 6 |
| name a "release gate" in prose before one exists | it is exactly how `journey.md:195`'s "recording script" went stale; the check runs in `check_commit.py` or it is a sentence | DR-M4 |
| port the bin's literal-triangle firmware check into spark | with `import pins` there are no GPIO literals to compare; the check that fits is use-against-map, and it waits on the PO's cut | FB-M3; Q22 |
| split `parts.py` (TL-M-E) or merge the board and part loaders (TL-M-G) inside this epic | no K row needs either; 266 + 196 mutation anchors sit in `parts.py` and `needs.py`; the 2026-09-30 note said "do not refactor" there — the PO's trade (Q12), after CH-2's sweep if at all | TECH-LEAD-5, §2; FEASIBILITY-2; EXISTING-FIRST-12; RISKS-7 |
| build the engine adapter (TL-M-F) in this epic | it is P154's direction; part 1 neither serves nor blocks it | TECH-LEAD-8, §2 |
| change ★C7's exit code or the tally's exit 2 | both are by design and decided; CH-38, CH-43 and CH-64 change what is printed around them | D the PO 2026-10-08 (#94); `cost.py:47` |
| let a hold travel to a shared store | it is per-machine state; the shared layer carries records only | TECH-LEAD-9; §5.8 |
| rank by a severity clause the data refutes | K10's "Czech labels" (0 in the drawer), K22's "copper short" (none observed), K45's "derived entries" (typed by hand), K62's "with no sign" (the count is printed) | RISKS-16; SL verify RC-1 (4), SL-M5; BR verify RC-2; CC verify RC-8; R2, CH-58 row |
| compare spark's `chip` with wokwi-boards' `mcu` directly | `esp32s3` and `esp32-s3` differ, so both shipped boards would be refused and the bin's `boards-valid` and irrigation's chain turn red; one chip-name table maps the spellings (CH-13) | R2, CH-13 row |
| record a pick's fit inside the pick | the reader refuses a pick with two keys (`needs.py:34`) and six sites assume one; the fit is a field of the need, with schema 2 (CH-17) | R2, CH-17 row |
| take the store's lock for a dry run once the lock lives in the store | a dry run writes nothing, and every unscoped dry run — an agent's against the real store included — would make the default home and its `.lock` | R2, CH-3 row |
| require `wokwi_is_stand_in` without giving the library XIAO `false` in the same commit | the bin's `boards-valid` validates the library XIAO, which has no such key | R2, CH-32 row |
| send a person or an agent to `boards.py --id` to select a board | `--id` prints the active id and selects nothing; the sentence says to write `boards/active.json` (CH-21) | R2, CH-45 row |
| call `tools/mutate.py`'s new listing `--near` | "near" already names P98's near tests and prints as `caught near` | R2, CH-2 row |
| treat `init`'s "nothing to do" → 1 as a fault | `outcomes.py:9-11` names `NOTHING_TO_DO` among the sanctioned aliases; whether `init` run twice should answer `ok` is the PO's (Q25) | R2, §1 row |
| change the bin's own tracked `.spark/cache/*.h` from spark | nothing reads them, and #125's council left them "the bin's to decide" | N12, `docs/observations/INDEX.md:281` |
| take round 2's strongest top five as the order without the PO | it sets the brief's tier rule aside for D8; that trade is his (Q35) | R2, The order 4 |

## 5. Open questions for the PO

| # | question | what it decides | the options |
| --- | --- | --- | --- |
| Q1 | A hold: stored and released by an operation, or derived on read from each listed project's `needs.json`? | CH-25's shape; CH-29; whether a shared store can ever know what is held | (a) stored: `used_in` stays, `--release`/`--forget-project`, `--audit` names disagreements; (b) derived: `used_in` goes, nothing to release — and the bin and irrigation, which have no `needs.json`, hold nothing until they get one (§1); (c) derived where a `needs.json` exists, stored by hand elsewhere |
| Q2 | The real store's guard: a rule on the project's folder, a flag in your shell, or both? | CH-11 | (a) refuse writes from a project under the temp root — covers the incident on record only; (b) `SPARK_STORE=real` once in your shell — covers a scratch copy under `~/Development` too; (c) both |
| Q3 | A `pin_order` without its proof: a fact a record owes (buildable, warned, marked — your #102 words) or a contract failure (as the loader refuses today)? | CH-37's table; `--requirements`' refusals; what `--audit` calls 17 catalog records | (a) owed and marked; (b) a contract failure, and `--audit` says "broken" |
| Q4 | An empty derived rule list after the records were read: `rules-vs-netlist` answers `ok` with `checked: 0` and the reason, or stays could-not-run? | CH-39; whether the first sensor-only board is exit 2 for ever (RISKS-11) | (a) `ok, checked: 0` with the reason; (b) could-not-run, as W1's letter reads; (c) a `checked` statement in the rules file |
| Q5 | For P100's rounds: release the S3 and LiPo from the bin, use a second board once it has a record (CH-24), or a scratch copy of the store? | whether round A waits on a finding or on your choice (RISKS-9); with Q6, the only things that unblock round A without code | (a) release; (b) a second board after CH-24; (c) a scratch store, said in every report |
| Q6 | The drawer's data pass — `function` on the 91 silent entries (and aliases such as `footswitch`), proposed by the agent from each label, written after your yes — as a card with you, before the code? | CH-19's measure; round A's matching (RISKS-2) | (a) before the code; (b) after CH-19's count lands; (c) only the six ESP SKUs and the owned sensors first |
| Q7 | Irrigation's `irrigation.requirements.json` → `requirements.json`, and rc-car's two files? | CH-7, CH-39's order | (a) rename irrigation's; (b) rc-car: one file per board in two projects, or a convention for two boards |
| Q8 | Boards in your store (read project → store → library), and the board operations as rows of `parts.py` or `boards.py` with its own envelope? (B-Q1, B-Q2) | CH-27, CH-21's second half, CH-24's and CH-63's home, CH-22's update door | (a) a store place, rows in `parts.py`; (b) a store place, `boards.py` keeps its own verbs in the envelope; (c) no store place yet |
| Q9 | A record copied into a project: pinned to its source by a digest and refreshed on request after a dry run, or read through from the store? (B-Q3) | CH-26's `--refresh`; #17's "projects update their data" | (a) pinned, a lockfile; (b) read-through, no project copy |
| Q10 | A board Wokwi lacks: the same-chip Wokwi board with a per-pad name table (works in the chain now) only, or also a generated custom board for the web editor and upstream? (S-Q1) | CH-33 | (a) same-chip only; (b) also generate; (c) wait until Wokwi's CLI documents local boards — or read `wokwi-cli`'s source to know (the critic) |
| Q11 | A board pick with no board file: reserve and record `reused` as today, warn and not record, or refuse? | CH-24's pick half; the by-design note in §1 | (a) as today plus the command; (b) reserve, no `reused`; (c) refuse until the record exists |
| Q12 | Split `parts.py` (contract / documents / CLI) and merge the board and part loaders — worth 462 moved anchors and reopening the 2026-09-30 verdict? | the shape the fixes land in | (a) no; (b) after this epic, with a dated sweep before and after; (c) now |
| Q13 | The step to a board: a page with two commands, or a script that composes them and refuses a wrong chip? | CH-34's size; P79's shape | (a) the page (CH-34); (b) a script under P79 |
| Q14 | An unknown id: `problems`, exit 1 (decided 2026-10-04), or could-not-run? And `next`: fill it or remove it? | CH-46; the agent guide's exception list | (a) keep, with a `kind` word; (b) could-not-run; `next` filled or removed |
| Q15 | JSON Schemas: shipped for editors and checked in the suite only, a `jsonschema` run-time dependency, or a small validator of spark's own? | CH-28 | (a) editors and suite only; (b) a dependency; (c) own subset validator |
| Q16 | Mounting holes: emitted by the footprint, or removed from the record? | CH-22 | (a) emit (every regenerated footprint changes; four drills under the drill check); (b) remove |
| Q17 | Shared records' licence: CC0, CC-BY, or CC-BY-SA where a KiCad-derived footprint is carried — and may a shared record carry a chip (code)? | CH-29 | (a) CC0; (b) CC-BY; (c) records point at footprints, never carry them; chips with a licence each |
| Q18 | The recorder: promote the untracked one, cog, or mdsh? | CH-40 | (a) promote (no dependency); (b) cog (three comment lines per block in pages agents read raw); (c) mdsh (every block rewritten) |
| Q19 | Is a person typing spark's scripts without Claude Code a persona spark serves? And README's "Two roads to a board" (231 lines against ~120): a run block or a pointer? | CH-43, CH-42, CH-16's text half, CH-52 | (a) served: text gets fix, next, legend, a start line; (b) not served: README stops promising it |
| Q20 | A dropped need: a tombstone that stays in the file, or removed? | CH-50 | (a) tombstone (travels through sync better); (b) removal |
| Q21 | The XIAO's footprint: a converted vendor footprint, or header rows? | CH-66's data; whether plant-alarm ever builds | (a) `footprint_source` from Seeed's KiCad footprint (CC-BY-SA, H); (b) leave the XIAO stopping |
| Q22 | Re-add a firmware check you cut on 2026-09-29, now as use-against-map over `pins.py`? | CH-67's held half | (a) yes, after CH-2; (b) no — the `pins.py` header, the shape check and CH-49's coverage note only |
| Q23 | Four valves: one need per instance (works today) or a `count` on a need? | CH-50's neighbour; `idea.md:37` | (a) one sentence in `idea.md`; (b) a schema change |
| Q24 | A need the board itself serves (WiFi, the LiPo socket): picked, or marked served by the board pick? | CH-54; the build's unserved note | (a) picked, reserving nothing; (b) marked served |
| Q25 | `/spark:init` run twice: `ok`, or `problems` as today — through the `NOTHING_TO_DO` alias that `outcomes.py:9-11` sanctions? | CH-45's `init` half | (a) `ok`; (b) `problems`, by the written design |
| Q26 | One stranger run (slice 5: README only, own machine and board, a diary nobody helps with) scheduled as a card before this list is called done — and who scores it? | whether "better" can be claimed for the primary persona (RISKS-4); the user-human lens asked who scores it | (a) yes, with a date and a named scorer; (b) later |
| Q27 | What makes a project's own record "proven" enough for the shelf — a `built` line, a `ran` line, your yes? | SL-C11 (b), held in §4 | (a) a `built` line CH-26 reads; (b) your yes per record |
| Q28 | Your own machines: spark stays out (you pick a private remote or a folder sync, spark survives the sync), or spark supports one? (B-Q6) | CH-9, CH-3 and CH-42's sentence suffice for (a); (b) re-scopes `inside_git` (EF-MISSING-3) and decides a home inside a repository (CH-3's `.lock`) | (a) stay out; (b) support a private git remote |
| Q29 | The catalog's and downloads' modes: private (0700, as §5.1 says) or readable (as a shared layer wants)? | CH-57 | (a) private; (b) readable |
| Q30 | What is "better", and how will this list show it? Your #17 measure (2026-10-04): more parts known, proven by use, fewer requests measured — two of the three stay unmeasured after every change here (RISKS-3) | the epic's done line | (a) a card whose proof is one of the three observed (a `built` digest compared — CH-26; a tally in a terminal — CH-64; `--match` offering a part that was silent — CH-19); (b) the epic is done when its cards are |
| Q31 | What lands first, and do the 72 changes become one epic with area stories? And does Ready 5 count both boards together? | the cut line (§3, end); whether the PO pulls an enabling change forward (CH-40, CH-41, CH-2) | (a) the first slice as proposed — three working-stage cards; (b) another cut; (c) one card per change |
| Q32 | PR #125 — **answered**: merged by the PO on 2026-10-10T17:32Z (D) | CH-62 (done); CH-24's and CH-47's dependency (met) | — |
| Q33 | Which systems does spark serve — README names macOS and Linux (Linux unrun) and has no lines for Windows (`README.md:85-91`); your direction is a public, hobbyist plugin (2026-10-03, your notes)? | CH-57's no-locking line (a line or a refusal), its kept-name half (G10), CH-10's case test | (a) macOS and Linux, said; (b) Windows too |
| Q34 | May an agent working on project B release project A's hold? One person, one Mac today; a shared store later | CH-25's permission rule, before the operation exists (USER-AI-AGENT §4) | (a) yes, with the dry run and the sentence naming A; (b) only with A named on the command line; (c) only from A's folder |
| Q35 | D8's order: by the brief's tier rule the board skeleton (CH-24) ranks 28, its Design in the first slice and its Build after the board contract and the alias fix (CH-22, CH-23, ranks 26–27) — or round 2's strongest top five, which sets the tier rule aside for D8: CH-1 with the store's refusal mapped, CH-13, CH-22, CH-16, then CH-14 + CH-21 + CH-23 as one pull request? | where your first fix sits (§6, splits 17 and 24) | (a) the tier rule as applied; (b) round 2's top five; (c) the tier rule, with CH-22 and CH-23 pulled into Design beside CH-24 |
| Q36 | Are the sibling projects' `make check`s a contract every spark merge keeps green, or may a change break one with a note? | CH-68; every "bin" line | (a) a contract, tested (CH-68); (b) a note on the card |
| Q37 | Port the bin's `fake_machine.py`, its `lib/checks` and `check-current-docs.py` into spark as the generic versions, the bin then using spark's? | CH-41's retired-sentence check (its shape), CH-67's held check | (a) port the docs check now, the firmware ones with Q22; (b) port none; spark writes its own |
| Q38 | The hold verbs' names: spark's (hold, release, forget) or InvenTree's (allocate, release)? | the words in CH-25 and in every refusal the person reads | (a) spark's; (b) InvenTree's |
| Q39 | DoD 8: must a **works** row of README's "What works today" link a section holding a recorded block? | CH-41's DOC-M-D6 half; README's Build row (G3) | (a) yes, checked by the gate; (b) no, the council reads it |
| Q40 | K42 (research only the gap), K43 (the other ways in) and K44 (choosing among equivalent owned modules — "search" in your 2026-10-10 words): in part 1 or not? | whether three journey blocks get changes here or stay on #99, #5, #93 | (a) out of part 1; (b) K44 in, with CH-53; (c) all in |
| Q41 | A pick's fit: a `fit` field on the need, keyed by the picked id, with the needs file's schema 2 — or a new value of the need's mark? | CH-17 (NM-M4), and what an older spark says to a newer `needs.json` | (a) a field, schema 2 (my lean: a recorded fact; the mark stays "is it available"; an older spark refuses with its schema sentence); (b) a mark value — five marks, schema 1 kept, but an older spark refuses the new value as a bad mark |
| Q42 | The ordering keys: (a) counts hard edges into this epic's changes, soft ones breaking ties — or soft and hard alike? And (c) harm, (d) who met it, (f) reach — mine — keep, strike, or reorder? | the order inside each tier of §3; whether CH-1 or CH-16 is first; whether I1 (CH-18) outranks the agent's JSON (CH-16) | (a) keep as stated; (b) count soft edges equal to hard (CH-1 first, CH-16 second); (c) strike (c), (d) and (f), order by (a), (b), (e), (g); (d) put (c) first |
| Q43 | "Silent" includes an answer that leaves out a fact it read about the very thing it reports — or only an answer whose report is false? | which of CH-72, CH-19, CH-49 and CH-16's text half stay in tier 1 | (a) as stated: they stay; (b) false results only: they move to tier 2 |
| Q44 | `wokwi_is_stand_in`: required — the library XIAO gaining `false`, a person's own board file without it refused with a sentence and a release note — or absent read as false? | CH-32 | (a) required; (b) absent is false, said on the schema page |
| Q45 | `b12-kept-from-the-bin.jsonl`, B12's URL proofs at your store's root, named by no place: keep it there and let `--audit` name it, fold its proofs into the kept documents' records, or delete it now that every document is kept? | CH-57's root-file half; what a sync of the store would carry (CH-70) | (a) keep, named by `--audit`; (b) fold into the records; (c) delete |

## 6. Where the lenses split, and how the proposal resolves each

| # | the split | who stood where | resolution here, and why |
| --- | --- | --- | --- |
| 1 | Holds: derived on read, or stored and released | TECH-LEAD (§2 C6, Q1): derive fits the criteria and P178; RISKS-10 and the SL verifier: testability favours derive, "the bin keeps this one" favours stored; the user lenses: either, with the command printed | **Left to the PO (Q1), with a lean to stored for now (CH-25).** Two of five listed projects (the bin, irrigation) have no `needs.json`; the bin's two holds were set by hand (no history line names it). Derived holds would free the S3 the PO decided three times to keep with the bin (RISKS-9) unless the bin first states its picks. The release reuses the path a pick already runs (`needs.py:326-331`), so stored holds add one verb, not a second mechanism. The `held by` column is shown either way (CH-72, tier 1). |
| 2 | What comes first overall | store C1: TECH-LEAD, USER-AI-AGENT, EXISTING-FIRST; the data pass and decisions: RISKS; "one door": FEASIBILITY; the flash step: USER-HUMAN; the recorder: DOCUMENTATION | **The stated keys decide.** With hard edges counted, CH-16 comes out first (it unblocks five); CH-1 is eighth, first of the changes that unblock one, by its six soft edges (split 23). The data pass and the decisions have no rank and go to the PO in week one (§3, the first slice). The flash step blocks the journey but is signed (tier 2, CH-34); the recorder is the documents' mechanism (tier 3, CH-40; enabling work is not a key, Q31 lets the PO pull it). |
| 3 | `boards/active.json`: kept in step from `--requirements`, or replaced by the requirements file's `board` | TECH-LEAD: the alternative (one statement fewer); USER-AI-AGENT, USER-HUMAN, RISKS, FEASIBILITY, EXISTING-FIRST, DOCUMENTATION: the recommended variant now | **Kept in step now (CH-55, tier 1 — silent, R1).** No check reads the selection (CC-MC-7), the bin's Makefile reads `active.json`, and part 2 replaces "the board" as one field anyway — the alternative is the smaller system then, not now. |
| 4 | `--need`: one matcher ranked by hits now, or two sentences first | USER-HUMAN: the sentences alone leave the quoting trap; USER-AI-AGENT, RISKS, FEASIBILITY, the NM verifier: sentences first, ranking later; R1: tokens must stay substrings | **Both, in two steps (CH-18, then CH-53).** Step 1 splits the query with one `words()` moved to layer 1 (R2) under the AND — quoting stops mattering, USER-HUMAN's objection — keeps each word a substring test (R1), and says the missed word and what was not searched; the ranking, which rewrites a documented behaviour and two recordings, is step 2. |
| 5 | A declared signal: a shared `NOTE_PREFIX` constant, or the generator's notes as a returned value | the CC verifier, USER-AI-AGENT, RISKS, FEASIBILITY: the constant; TECH-LEAD (M-A): notes in-process, the stderr channel removed | **The return value is the shape, the constant the S step (CH-38).** The PO's criterion — one place, one reason — favours removing the channel; size decides at Build. |
| 6 | The stand-in's pins: a Python validator with a registry copy, or the converter's own registry | BR verify C11 and EF-MISSING-7: a copy under `data/`, never `node_modules` from Python; FEASIBILITY-10: one card; R1 (existing-first): the converter already holds the registry (`geometry.ts:58-59`, `PinOracle`), so a copy is a second, versioned source | **A generated copy, tested equal to the converter's (CH-31).** The validator stays pure Python and testable without Node (testability); the equality test makes the copy unable to drift from the one source (R5's rule: derived copies are checked, never hand-kept); the check is per GPIO so the XIAO passes (R1). |
| 7 | Where the image's chip is checked | the FB diagnosis: a `--project` default on `flash_image.py`; the FB verifier, USER-AI-AGENT, RISKS, FEASIBILITY: `check_spine`'s simulation stage plus an optional `--chip` | **The stage (CH-13)**: irrigation has no `.spark/board.json`, so a `--project` default cannot resolve its board. |
| 8 | Where the board skeleton (D8, "the first fix") ranks | USER-HUMAN 7, RISKS 5, TECH-LEAD 10, FEASIBILITY after the schema, the stand-in check and the cache move; R1: in the top ten (RISKS-1) | **Rank 28 by the keys, its Design in the first slice and its Build after ranks 26–27** (§3) — see splits 17 and 24; Q35 asks the PO. |
| 9 | The flash step: the top of the list, or P79's later work | USER-HUMAN rank 1; TECH-LEAD: outside part 1 by direction (P79); RISKS 10; EXISTING-FIRST 9 | **The page in tier 2 (CH-34), the script under P79 (Q13).** It blocks the journey and costs S as a page; a script is P79's shape and the PO's. |
| 10 | Firmware against the pin map: a sixth check now, or held | USER-HUMAN, USER-AI-AGENT: keep as use-against-map; FEASIBILITY, TECH-LEAD: hold for three decisions | **Held (Q22); its S consumers ship** — the coverage note in tier 1 (CH-49, silent), the `pins.py` facts in tier 3 (CH-67). The PO cut the check on 2026-09-29. |
| 11 | Which mutation work comes first | RISKS rank 3 (a dated sweep); FEASIBILITY, EXISTING-FIRST: K53 before any mutation-row proof; R1: CH-2 rides with the first change that proves itself by a row | **Rank 25 (CH-2)**, last of tier 1: "caught" over a mutant that tested nothing is itself silent, but it is a count, met by a code read only, and nothing in the epic needs it unless Q22 says yes (R1, R2). |
| 12 | JSON Schema: now, or P160's first increment | EXISTING-FIRST (MISSING-1, now); FEASIBILITY (P160's first increment); TECH-LEAD (generated, never hand-kept); DOCUMENTATION (generated or checked) | **Its first instance now inside CH-22 (`PHYSICAL_KEYS` and a checked page); the schema set as a P178/P160 concept (CH-28), generated, with Q15 for run-time use.** |
| 13 | The envelope and `kind`: one structural change or several fixes | TECH-LEAD (M-B), USER-AI-AGENT (M-A, M-B): structural; the diagnoses: per-case fixes | **The shape is R6 (§2.1)**; the part that fails silently — the JSON dropping what the text says — is tier 1 (CH-16), tested by name; the `kind` word is tier 3 (CH-46). |
| 14 | SL-C11, "a record has one home" | every lens: keep the direction, split it | **Split**: promote-to-shelf in CH-4; the header in #125 (merged 2026-10-10); the digest reader in CH-26; the datasheet-reader's tools in CH-48 once `--fact-set` is shown to cover them; shelving a project's own records held for Q27 (§4). |
| 15 | The docs gate's version check: failing, or a report line | the DR diagnosis: failing after the recorder; every lens and the DR verifier: report line | **Report line (CH-40)**; the recorder's diff is what fails, on a version change; the check reads the version line (DR-M5, CH-41). |
| 16 | The "not run" admissions: one dated table (DOC-M-D4), or retire them by recorded runs | DOCUMENTATION: a table and a test; the DR verifier: a run for these docs retires a sentence | **Not ranked on its own**: CH-47 retires the one admission a script can run; the rest are structural (a conversation, an agent, a paid run, the install) and stay honest prose. The table is offered with Q19. |
| 17 | The top of the list: the stated rule (silent first, then what unblocks most) against who is blocked today | R1's "strongest case": CH-1; #125 and CH-12; CH-14 + CH-21; CH-24; CH-25 — because the only person blocked is the PO, at round A, by K3 + K29 + K36 together (RISKS-1), and his own words are "start by the boards" (D8); the brief's rule: silent faults first | **The rule orders the ranks; RISKS-1 is answered in the first slice.** Under the rule, CH-1, CH-14 and CH-21 are in tier 1 anyway (ranks 8, 10, 6), and #125 is merged; CH-24 and CH-25 block the journey but are signed, so tier 2 (ranks 28, 29). A rank orders Build; Design and the PO's decisions are other stages, so CH-24's Design, Q5 (round A's board) and Q6 (the data pass) all start in week one (§3). If the PO prefers R1's top five, or R2's (split 24), Q35 and Q42 are where he says so. |
| 18 | CH-3 (the lock) or CH-11 (the guard) first | R1: swap them — K2's harm has happened (#101), K5 has never been met; USER-AI-AGENT-13 | **Applied, after round 2.** The second version refused it by key (a), through edges from CH-8 and CH-25 to CH-3 that gave no reason (R2); without them CH-3 unblocks none, and key (d) puts CH-11's recorded harm first (CH-11 rank 13, CH-3 rank 17). CH-11 still waits on Q2; it enters Ready the day Q2 is answered. |
| 19 | CH-2 (mutation bar) or CH-12 (bare-number labels) first | the first version: CH-2 at 2, as enabling; R1: swap them — CH-12 is the deterministic circuit fault, CH-2's over-count is "—" in size (two rows ever) | **Applied:** enabling work is no longer a key. Counted as round 2 asks, neither unblocks a change outright — CH-12's edge to CH-24's hand-filled fields is soft, CH-2's to the held firmware check exists only if Q22 says yes — so CH-12 leads tier 1's zeros by its soft edge (a2) and CH-2, a count met by a code read, closes the tier: CH-12 at 11, CH-2 at 25. |
| 20 | K14's header: PR #125's owning-project cache, or the store | the first version (CH-4): the store's `cache/vendor-headers/`; #124's council and R1: the owning project, which is spark for a shipped board | **Resolved: #125, merged by the PO on 2026-10-10 (D).** The general rule it implies — a regenerable artefact of spark's own may be refreshed in the plugin by the operation that names it, a person's data never — is read into R2, which #125's own council's N14 and N28 turn into one run-time helper (CH-4). |
| 21 | Is a printed path a sign? (CH-7) Is "a gap" silent? (CH-54) | the first version: CH-7 tier 1, CH-54 tier 4; R1: CH-7 prints the path it wrote, CH-54 is CH-18's shape | **Both applied, by the one definition of silent in §3**: an answer that says success while what it reports is false — or, since round 2, leaves out a fact it read about what it reports — with nothing saying so. CH-7's line names the file it wrote — a sign — so tier 2; "a gap" over a board that has WiFi says nothing is wrong — tier 1. |
| 22 | Two drawer entries for one thing: a plain-key check is enough, or name duplicates too | the first version: the plain key alone; R1: a hand `cp` under a plain name passes it | **Both (CH-9):** the plain key catches a sync client's copy; two entries with one vendor part number are named for the hand copy. Entries that share a linked record but not a part number stay legitimate (two shops' buttons). On his copy, 0 entries share a part number today (E §1). |
| 23 | Counting "unblocks" (key (a)) | the first two versions: hard and soft edges alike, P178 concepts included; R2: state both choices, or count hard in-epic edges only | **Hard edges into changes of the epic; soft ones break ties.** A soft edge blocks nothing by its own definition, and a concept is not built in this epic. It moves CH-1 from 1 to 8 and CH-16 to 1. Q42 (b) restores the other count. |
| 24 | D8's "boards first" against the brief's tier rule | R2: a prerequisite of the PO's named first fix waits behind 27 tier-1 changes, eleven of which unblock nothing; its strongest top five: CH-1 with the refusal mapped, CH-13, CH-22, CH-16, then CH-14 + CH-21 + CH-23 | **The tier rule stays** — the brief sets it, and D8 orders only inside a tier (key (e)); §3's constraint pulls CH-23 up beside CH-22, so CH-24's Build waits for ranks 26–27, not 43. Round 2's top five is Q35 (b). |
| 25 | The guard on writes into spark's folder: a test-time map over the commit gate's archived tree, or a run-time helper | R1 and existing-first: P172's gate as the run-time form of a grep; R2 and #125's council (N14, N28): a test-time symptom guard, blind to N25 and N26 — refuse the write where it happens | **The run-time helper (CH-4).** It refuses a person's run, not only a test's, and names the path and the operation; the map is not added (§4). |
| 26 | "Incomplete" in the definition of silent | R2: narrow it to "omits what the answer claims to cover", or lift CH-25's `held by` column into tier 1 | **Both, as one rule:** an answer that leaves out a fact it read about the thing it reports is silent; the column is that case, and its own change (CH-72, tier 1). Q43 lets the PO keep only false results. |
| 27 | CH-57's and CH-58's tier | R1: up into tier 1, silent by the rule; R2: CH-58 is signed (the count is printed), CH-57 reports nothing false | **R2's reading: tier 3 and tier 4**, because §3's definition is about what the answer says; the catalogue's K62 grade is corrected. |
| 28 | A board file with no stand-in flag | R1: keep the flag and read it; R2: requiring it refuses the library XIAO, which the bin validates | **Required, the XIAO gaining `false` in the same commit, a person's own file refused with a sentence and a release note** (CH-32) — a missing fact is named, not guessed. Q44 offers "absent is false". |
| 29 | The store's refusal in scripts that catch only `ToolProblem` | R2: map `StoreProblem` in every `main`, or re-raise it in `tools` as a `ToolProblem` (its "simpler") | **Re-raise in `tools` (CH-1)** — one `try` in one place — with a test over every `main`, because R2 traced two scripts and left three at —. |
| 30 | `init`'s "nothing to do" → 1 | the first two versions: a mapping that adds a meaning; R2: `outcomes.py:9-11` names `NOTHING_TO_DO` as a sanctioned alias | **The written design**, out of §1's faults and R8's list; whether it should change is Q25. |
| 31 | Where CH-9 and CH-10 sit in tier 1 | R2: both below CH-11, CH-15 and CH-4 — their only dependent is a P178 concept, CH-9's reach is nil, and both are code reads | **CH-9: applied** (rank 20, after CH-15 by key (f), reach). **CH-10: in part** — below CH-11 and CH-4, above CH-15 (16 and 18): R2's reasons hold for CH-15 as well (no dependent in the epic, a code read), and CH-10's fault can happen on his Mac today, so key (g) decides. |

## 7. Evidence index

**Facts of my own, this round (E, 2026-10-10, read-only, spark at `4a18333`).** `gh api
repos/xmejkal/spark/commits/main` → `4a18333 2026-10-10T17:32:07Z`; `gh pr view 125` → `MERGED`, `mergedAt
2026-10-10T17:32:08Z`, merged by `xmejkal`; `gh issue view 124` → `CLOSED 2026-10-10T17:32:09Z`; `gh issue view 126`,
`127`, `128` (titles, states, bodies: P180 OPEN in Review, P181 OPEN in Review, P182 OPEN in Idea); `gh issue list
--state all --limit 12`; `gh pr list --state all --limit 6` (PR #129 OPEN); `gh project item-list 2` → Discovery 2
(P100, P158), Review 2 (P180, P181), Done 18, Idea 83, Ready 0; `gh project item-list 1` → Ready 3, Done 1, Idea 19.
`git diff --stat a8aa34d 4a18333` → 9 files, 493 insertions, 32 deletions, and its hunk headers for the line shifts.
Read at the lines listed in the preamble. My greps: the plugin folder defined at module level → `boards.py:38`, `:153`,
`parts.py:45`, `store.py:33`, `tools.py:43`; `except store.StoreProblem` → `parts.py:2208`, `init_project.py:418`,
`check_spine.py:628`; `re-run with --force` in `init_project.py` → `:279` (a comment), `:485` (the print);
`kept-from-the-bin` → `scrum/PRODUCT_BACKLOG.md:1081`, `docs/2026-10-04-store-discovery.md:123`, `:246` and one
discovery page, no script. My count over `tests/mutations/*.json` → 116 files, 1,281 rows (1,241 `.py`, 24 `.md`, 13
`.json`, 2 `.ts`, 1 `.js`). My parser over both refuters' *Verdicts* tables → round 1, 92 rows; round 2, 45 rows
(Status). `ls -la ~/.local/share/spark` → `b12-kept-from-the-bin.jsonl` 6,575 bytes `-rw-r--r--` 2026-10-04, the home
`drwx------`, `catalog`, `downloads`, `sources` `drwxr-xr-x`. The bin, read only: `boards/` holds only `active.json`,
whose `board` is `firebeetle2-esp32s3`. A parser over §7's dependency list and the ranks → no hard edge points up; the
soft edges that point down are listed under the dependency list.

**Facts of my own, second version (E, 2026-10-10, read-only, spark at `a8aa34d`).** `gh api
repos/xmejkal/spark/commits/main` → `a8aa34d`; `gh pr view 125` → OPEN, created 2026-10-10T16:16:29Z, `mergedAt null`,
nine files (`docs/guide/agents.md`, `docs/guide/how-it-works.md`, `docs/observations/2026-10-10-p179-council.md`,
`docs/observations/INDEX.md`, `scripts/check_vendor_pins.py`, `tests/mutations/p179-vendor-cache.json`,
`tests/mutations/sprint-5-p10.json`, `tests/test_check_vendor_pins.py`, `tests/test_json_contracts.py`); `gh issue view
124` → OPEN (both superseded: merged and closed, above); `git diff main...p179-vendor-cache --stat` → 9 files, 493
insertions, 32 deletions; its `check_vendor_pins.py` docstring "WHERE IT KEEPS THE HEADER". Read at the lines:
`store.py:28-41`, `:46-52`, `:129-135`, `:186-194`, `:209-218`; `tools.py:45-49`, `:440-446`; `sim_project.py:155-164`;
`parts.py:1481-1483`, `:1630-1632`, `:2011-2016`, `:2086-2090`, `:2196-2210`; `check_spine.py:415-445`;
`boards.py:533-540`; `init_project.py:483-487`, `:497-501`; `needs.py:320-334`; `outcomes.py:1-20`;
`tests/test_boards.py:312-318`, `:364-382`; `tools/check_commit.py:108-139`; `data/importers/dfrobot.js:1-10`;
`docs/guide/agents.md:124-128`; `README.md:72-74`, `:85-91`; `GLOSSARY.md:108-121`, `:233-245`, its headings (416
lines); `scrum/WORKING_AGREEMENTS.md:15`; `docs/2026-10-04-store-design.md`'s headings (§5.8 at :262, §6.4 at :312, §8
at :399, G at :477); `docs/observations/INDEX.md:210` (E16b); `council/feasibility.md:57-60`. My greps: module-level
`import tools` → `check_spine.py:68`, `flash_image.py:26`, `init_project.py:40`, `sim_project.py:18` (and
`parts.py:1109`, function-local); "re-run init with `--force`" → `README.md:74`, `:155`, `journey.md:579`, `:717`,
`commands.md:30`, `:49`, `commands/init.md:36`, `init_project.py:279`, `:485`; "builds with it" → `parts.py:1631`,
`:2088`, `commands/idea.md:141`, `journey.md:468`, `:497`. `ls` → 5 guides, 14 agent pages (`commands/*.md`,
`skills/*/SKILL.md`, `agents/*.md`), `AGENTS.md`, `README.md`, `GLOSSARY.md`. The bin, read only: `Makefile:180-183`,
`:218-233`; `tools/circuit-to-wokwi/lib/mapping.ts:106-109`; `grep -n mismatch Makefile` → nothing. The store: `cp -R`
to `<scratch>/p158/synth-2/store`, read with `python3 -I`: 110 drawer entries; keys `schema` 110, `label` 110, `count`
110, `part_number` 103, `from` 101, `bought` 99, `unsure` 100, `function` 12, `is` 12, `used_in` 6, `skip` 1; 0 groups
sharing `(from, part_number)`; 0 shared `is` links; 0 repeated labels. `stat` of the real store's `drawer/` and
`history.jsonl` → 2026-10-08 12:33.

**K rows → changes.** K1 CH-1 · K2 CH-1, CH-11 · K3 CH-72 (the listing), CH-25 (the release), Q5 · K4 CH-10, CH-29 ·
K5–K7 CH-3 · K8 CH-8 · K9 CH-9, CH-8 · K10 CH-9 · K11 CH-5 · K12 CH-4 (shelving half held, Q27) · K13 CH-26, CH-63
(chips: P149/P150, named in CH-4) · K14 #125 (merged; CH-62 done) · K15 CH-57 (tier 3) · K16 CH-15 · K17 CH-15 · K18
CH-59 · K19 CH-26 · K20 CH-35 · K21 by design for its exit 2; its README half CH-43; its window and spoil CH-64; its
undercount CH-58 (tier 4) · K22 CH-12 · K23 CH-23 · K24–K26 CH-22 · K27 CH-22, CH-56 · K28 CH-56 · K29 CH-24 · K30 CH-36
(fab), CH-66 (label, data) · K31 CH-54 · K32 CH-30, CH-31 · K33 CH-18, CH-53 (synonyms: CH-19's pass) · K34 CH-17 · K35
CH-50 · K36 CH-19 (ranking: CH-53) · K37 CH-37 · K38 CH-52 · K39 Q23 · K40 CH-7 · K41 CH-51 · K42 not ranked (Q40; #99)
· K43 not ranked (Q40; #5) · K44 not ranked (Q40; #93) · K45 CH-39 · K46 CH-39 (sleep current, G7) · K47, K48 CH-37 ·
K49 CH-55 (the one-MCU half: P158 part 2) · K50, K51 CH-60 · K52 CH-21, CH-45 · K53 CH-2 · K54 CH-20 · K55 CH-16 · K56
CH-16 (all halves) · K57 CH-48 · K58 CH-48 · K59–K61 CH-6 · K62 CH-58 (tier 4; its "no sign" grade corrected, R2) · K63
CH-20 (`--step`), CH-39 (I²C, goal) · K64 CH-3 (the lock across downloads), Q12 (the split) · K65 CH-65 · K66 CH-13,
CH-34 · K67 CH-49, CH-67 · K68 CH-40 · K69 CH-43 · K70 CH-47 · K71 CH-61 · K72, K73 CH-24, CH-47 · K74 CH-41.

**Root causes → changes.** RC-SL-1 CH-9, CH-10 · RC-SL-2 CH-1, CH-11 · RC-SL-3 CH-3, CH-8 · RC-SL-4 CH-4, CH-26, CH-27 ·
RC-SL-5 CH-5, CH-15, CH-59 · RC-SL-6 CH-72, CH-25 · RC-SL-7 CH-57 · RC-BR-1 CH-23 · RC-BR-2 CH-12 · RC-BR-3 CH-22 ·
RC-BR-4 CH-56 · RC-BR-5 #125 (merged) · RC-BR-6 CH-24 · RC-BR-7 CH-36, CH-66 · RC-BR-8 CH-54 · RC-BR-9 CH-31 · RC-CC-1
CH-39 · RC-CC-2 CH-38 · RC-CC-3 CH-35 · RC-CC-4 CH-37 · RC-CC-5 CH-6 · RC-CC-6 CH-55 · RC-CC-7 CH-20, CH-21, CH-60 ·
RC-CC-8 CH-39 · RC-CC-9 kept by design (its asymmetry in CH-38) · RC-NM-1 CH-18, CH-53 · RC-NM-2 CH-17 · RC-NM-3 CH-50 ·
RC-NM-4 CH-19 · RC-NM-5 CH-37 · RC-NM-6 CH-51 · RC-NM-7 Q23 · RC-NM-8 CH-7 · RC-NM-9 CH-52 · RC-FB-1 CH-31 · RC-FB-2
CH-13, CH-34 · RC-FB-3 CH-49, CH-67 · RC-FB-4 CH-67 · RC-DR-1 CH-40 · RC-DR-2 CH-43 · RC-DR-3, RC-DR-4 CH-47 · RC-DR-5
CH-41 · RC-DR-6 CH-61. Missed causes: NM-M4 CH-17 · FB-M4 §4 (with CH-13's guard) · DR-M5 CH-41 · G14 (a sentence with
no single home) R5, CH-37, CH-39, CH-41 · BR-M2 CH-30 · BR-M8 CH-12 · BR-M9 CH-56 · DR-M3 §2.6 · DR-M7 CH-41 (§2.6) ·
SL-M5 §4's severity row (R2-Missing 8: each covered in substance before, now by id).

**#125's council rows → where they land** (`docs/observations/INDEX.md:281-297`). N12 §4 (the bin's to decide) · N13
CH-73, R6 · N14 CH-4, §2.3 · N24 CH-73 · N25 CH-4 · N26 CH-4 · N27 CH-73 · N28 CH-4, §2.3. N1–N11 and N15–N23 were acted
on inside #125.

**The dependency list the unblocks counts are read from** (hard unless marked soft; an edge into a P178 concept is
listed, not counted). CH-3 ← soft CH-1 · CH-4 ← soft CH-1, CH-26 · CH-9 ← soft CH-5 · CH-11 ← soft CH-1; Q2 · CH-15 ←
soft CH-5 · CH-17 ← CH-16; Q41 · CH-18 ← soft CH-1 · CH-19 ← soft CH-1; Q6 · CH-21 ← soft CH-18, CH-5 · CH-24 ← CH-13,
CH-14, CH-21, CH-22, CH-23; soft CH-12 · CH-25 ← CH-16; soft CH-1; Q1 · CH-26 ← soft CH-5 · CH-27 ← CH-21, CH-24; Q8 ·
CH-28 ← CH-22, CH-37; soft CH-65 · CH-29 ← CH-9, CH-10, CH-25, CH-26, CH-27, CH-70; Q1, Q17 · CH-30 ← CH-13 · CH-31 ←
CH-13, CH-22 · CH-32 ← soft CH-13; Q44 · CH-33 ← CH-22, CH-31; Q10 · CH-34 ← CH-13 · CH-35 ← CH-16, CH-26 · CH-37 ← soft
CH-5; Q3 · CH-39 ← CH-6, CH-7; Q4 · CH-42 ← CH-1, CH-17, CH-18, CH-25 · CH-43 ← CH-41 · CH-44 ← soft CH-68 · CH-45 ←
soft CH-68; Q25 · CH-46 ← CH-16, CH-31, CH-45 · CH-47 ← CH-24 · CH-48 ← CH-16 · CH-50 ← CH-17; Q20 · CH-51 ← CH-19 ·
CH-52 ← CH-18 · CH-53 ← CH-18, CH-19 · CH-54 ← soft CH-22; Q24 · CH-55 ← soft CH-7 · CH-57 ← Q29, Q33, Q45 · CH-63 ←
CH-21, CH-26; P178: CH-27 for its project → store half, which is P178's own · CH-66 ← CH-22; Q21 · CH-67 ← Q22, and, if
Q22 says yes, its held check ← CH-2 (not counted until then) · CH-69 ← CH-30. All others depend on no change. **Gone
since the second version:** CH-8 ← CH-3 and CH-25 ← CH-3 (neither block gave a reason; today's lock already serialises
both for one `TMPDIR` — R2); CH-24 ← CH-62 and CH-47 ← CH-62 (met: #125 merged). **P178 concepts** (edges into them
listed on each block, not counted): CH-27, CH-28, CH-29, CH-33, CH-69, CH-70. **Soft edges that point down** — the
dependent ranks above its soft prerequisite and prints one sentence less until it lands, as its block says: CH-18 (3)
and CH-19 (7) ← CH-1 (8); CH-26 (4), CH-21 (6), CH-15 (18) and CH-9 (20) ← CH-5 (40); CH-54 (21) ← CH-22 (26); CH-55
(23) ← CH-7 (39); CH-45 (45) ← CH-68 (47); CH-28 (49) ← CH-65 (57). **Hard edges that point down:** none (my parser over
this list and the ranks, 2026-10-10).

**Round 1's lines this proposal folds in** (`council/refuter-round-1.md`; each also in *Changes since round 1*).
Preamble rows 1–2; §1 rows on `SPARK_HOME`, promote, the island, exit codes, and §2.3's two rows; R1, R2, R4, R8; every
partly or refuted change row (CH-1, -2, -4, -6, -7, -9, -18, -23, -26, -29, -31, -32, -36, -44, -45) and the notes on
CH-3, -5, -8, -12, -13, -16, -17, -21, -24, -40, -41, -47, -48, -50; "The order" (re-tiering, unstated keys, the four
swaps, capacity); "Mechanism or symptom" (CH-1, -2, the door test, -6, -9, -13, -16, -17, -18, -23, -26, -31, -32, -36,
-45, the bin's `board.ts:40`); "Missing" 1–11; "Numbers" (42 with its pattern, 13 marked H, 8 or 10, the machine time,
"0 problems", "two lines", the grep on `mismatch`, the core version, 319,145 bytes).

**Round 2's lines this proposal folds in** (`council/refuter-round-2.md`; each also in *Changes since round 2*). Every
row of its *Verdicts*: the preamble (1) and (2); §1's rows on `SPARK_HOME`, promote, the island, exit codes, the door,
the data; §2's R1, R2 and §2.3 rows; the order's rows on silent, CH-58, CH-57, the keys, enabling work, the unblocks
counts, CH-3 ↔ CH-11, the first slice, the "because" sentences, Q35; the change rows CH-1, -2, -3, -4, -6, -13, -14,
-16, -17, -18, -19, -21, -22, -23, -24, -26, -32, -45, -62, the CH-9/-10/-12 row, the CH-49 group and the CH-5 group.
"The order" 1–4 and its strongest top five (Q35 (b), §6 split 24). "Mechanism or symptom" on CH-1, -2, -3, -4/R2, -6,
-13, -16, -17, -18, -26, -32, -36, -45, -58 and the three projects. "Missing" 1–8. "Numbers" (12.2 h as an upper bound,
1,281 rows, 1,713 tests, the unblocks composition, 18 in Done, four cards in flight, the store counts from a fixture).

**The completeness critic's gaps this proposal folds in** (`council/completeness-critic.md`). G1 (CH-3), G2 (CH-37,
CH-39, CH-41), G3 (CH-23, CH-41, Q39), G4 (CH-63), G5 (CH-69), G6 (CH-16), G7 (CH-39), G8 (CH-19, CH-53), G9 (CH-39),
G10 (CH-57, Q33), G11 (CH-5), G12 (§1, Q40), G14 (§1, R5); EF-MISSING-2 (CH-70), FE-MISSING-7 (CH-42), FE-MISSING-10 and
RISKS-19 (CH-2, §3's Done), DOC-M-D6 and -D7 (CH-41, Q39), UH-M-h (CH-1), UH-M-i (CH-71), DOCUMENTATION-18 (CH-42),
RISKS pre-mortem 6 (CH-68, §2.5 seam 8); Q-a…Q-l (Q30–Q40, Q26); the "not examined" areas (§1); the settled facts — no
traced history reader depends on line order (§2.3), the chip ids (CH-13), both tscircuit cores (CH-12), the real store
is in no synced folder (§2.3, CH-9), K62 observed in transcripts (CH-58), CH-33's question still open; the untagged
claims (CH-9's conflict names, §4's "commonest folder change"); "Unexplained for a reader" items 1–7 (§1's journey table
and five sentences, the "because …" sentences, the Words paragraph, CH-24's "automatically", the glossed references).

**Corrections from the diagnoses' verifiers** (the refuted versions are used nowhere above).
- *Store* (`diagnosis/store-levels-and-holds.verify.md`): RC-1's kind is design for the copy and the vanished folder and
  implementation for the spelling; the history is also keyed by name; irrigation holds 7 records, not 9; K10's "Czech
  labels" — 0 in the drawer (110 entries, 99 imports). RC-2: no *ok* answer names the store, broken files do; M1, an
  empty `SPARK_HOME` is the default home. RC-3: the lock place also differs per macOS user. RC-4: the digest is read by
  name by nothing; the design's writable column was never built. RC-5: K19 is not a reader fault but M3 (a proof never
  read); K16 only for a killed process; `store.py:145` reads too. RC-6: the `--json` refusal names the key; the plain
  text drops it (K56). RC-7: §5.8 promises document bytes private twice. M2 (holds two things at once), M4 (the door is
  opt-in); C3 (c) (a `.lock` inside a repository); C4 → the S form; C5's never-reuse half breaks a move; C11 (b) shelves
  placeholders; C13 has no reader.
- *Boards* (`board-records.verify.md`): RC-2 — no copper short; a phantom port; RC-3 — five unread keys; RC-4 — the
  contract test runs `-o` only; RC-7 — the guide already names the geometry half; RC-8 — the drawer's `function` slot
  (M4); RC-9 — the 21-LED design reaches `TX`; M1 (errors printed after the island — and, R1, by type only), M5 (two
  spellings), M6 (keys too), M7 (the XIAO's silkscreen names); C2's alias rule refuses the S3's own file; C9's XIAO is
  SMD.
- *Chain* (`chain-and-checks.verify.md`): RC-2 — three of the four notes are pre-warned; RC-4 — a pin order without
  proof stops the parts stage; RC-6 — `boards/README.md:21` contradicts `idea.md:132-133`; RC-8 — irrigation's entries
  were typed by hand on 2026-09-29; MC-1 to MC-8.
- *Needs* (`needs-matching-vocabulary.verify.md`): RC-1 — the kind reaches the matcher through `KIND_FUNCTION`; the AND
  is documented; RC-2 — another verb passes too (M1); RC-4 — the test pins the record gate, not the entry gate; RC-5 —
  seven connectors and three flow meters; `--validate` is silent on a null `simulation` or `function` (M3); RC-8 — one
  documented name, the writer of 2026-10-07; M2 (the subset rule), M4 (no mark for a loose fit — now CH-17's mechanism),
  M5 (substrings), M6 (rename first), M7 (one need per instance), M8 (the import's question has no step); C2's pair rule
  breaks plant-alarm. USER-AI-AGENT-7: the diagnosis's "`--need soil sensor` → nothing" was the quoted form.
- *Firmware* (`firmware-and-bench.verify.md`): RC-1 — 0 GPIOs absent; the override exists; the superset sentence is true
  of GPIOs; the bundle is the cost; RC-2 — the bin's script never read the header, and a per-project tools override
  exists (M4, the chip-blind role — §4); RC-3 — the check was cut by the PO (M2), literal comparison is vacuous with
  `import pins` (M3), and the README names the gap; M5 (esptool 3.3 cannot flash a C6), M6 (`deep_sleep` has no schema),
  M7 (the `pins.py` header), M8 (the converter's missing JSON), M9 (amend, not delete).
- *Docs* (`docs-and-recorded-outputs.verify.md`): RC-1 — the version test is "v0.8.1 anywhere in README" (M5, now in
  CH-41); RC-3 — retiring is an edit after a recorded run, and K70's "stale" misreads the convention; RC-4 — the field's
  name is already on the page; M1 (the recorder exists, untracked), M2 (8 unpaired blocks; DOCUMENTATION-17 counts 10),
  M3 (blocks not functions of the plugin and the store), M4 (no release gate), M6 (the gate isolates `SPARK_HOME` only),
  M7 (pages named by file name), M8 (README shows no output); Change 6's counts are bytes, not characters.

**Lens findings this proposal rests on.** STORE-1…STORE-18 and B0–B6, S1–S5, B-Q1…B-Q6, S-Q1
(`council/store-scenarios.md`); TECH-LEAD-1…-14, S1–S7, M-A…M-J (`council/tech-lead.md`); USER-AI-AGENT-1…-14,
UAA-M-A…M-F, and its §4 question on releasing another project's hold (`council/user-ai-agent.md`); USER-HUMAN-1…-20,
UH-M-a…M-i (`council/user-human.md`); RISKS-1…-20 and its pre-mortem (`council/risks.md`) — RISKS-1, -3, -18, -19
uncited in the first version, now in §3, §5 (Q30, Q31) and §6 (split 17); FEASIBILITY-1…-22, its clusters A–I, its
question 10, FE-MISSING-1…-10 (`council/feasibility.md`) — FEASIBILITY-11 and -19 now cited (CH-68, §2.3);
EXISTING-FIRST-1…-31, EF-MISSING-1…-8 and its questions 5 and 8 (`council/existing-first.md`); DOCUMENTATION-1…-20,
DOC-M-D1…M-D7 and its question 4 (`council/documentation.md`).

**Searches.** None by me, in either round. The lenses' searches and fetches are listed in their own reports (SQLite's
corruption page, VS Code's JSON page, wokwi-boards, Wokwi's project-config and chips pages, gitattributes, KiCad's
library licence, Syncthing's conflict naming, cog, mdsh, the CRDT search, InvenTree, KiCad's tables); the critic's
Espressif documentation search (`esp_app_format.h`) and its one web search on `wokwi-cli` boards are cited above as
theirs.

## Changes since round 1

One line each: what changed, and why (R1 = `council/refuter-round-1.md`; G = `council/completeness-critic.md`). Kept as written for the second version; ranks and lines here are the second version's, and *Changes since round 2* says where round 2 changed them.

**Facts and the picture (preamble, §1)**
- The stray header was moved by P179's own work, sha256 unchanged — replaces "who removed it: —" (R1, preamble row 1).
- #124's fix is PR #125, open and ready to merge; it is now rank 7 (CH-62), and the first version's store cache for headers is withdrawn to §4 (R1, preamble row 2, Missing 1).
- "An unset, empty or missing `SPARK_HOME`" → "empty reads the real store, missing becomes a new one"; unset is the designed default (R1, §1 row).
- The promote rule is documented in three places and wrong for all but the maintainer; what is silent is the later loss (R1, §1 row).
- `check_spine` reports the build errors it has already read only after the island, and then by type only (R1, §1 row).
- "An exit code means two things in three scripts" → two mappings in two scripts; local aliases are the written design; `mismatch` is a JSON status word (R1, §1 row).
- Added: a journey table in plain words, five summary sentences, a Words paragraph pointing at `GLOSSARY.md`, and glosses for §5.8, §6.4, §8 G, W1, D8, ★C, G0 (G, "Unexplained" 1, 3, 4, 7).
- Added: the three writers around the door — `tools.py:445`, `tools.py:47-48` (read at import by four scripts, my grep), `sim_project.py:162` (R1-Missing 2, 3).
- Added: "a sentence has no single home" as a design fault, with its nine page lines and one printed line (G14, G2).
- Added: NM-M4, FB-M4 and DR-M5 named as causes (R1-Missing 4–6); the tally's window and spoil (R1-Missing 7); README's Build "works" row and the glossary outside the gate (G3, G "Unexplained" 4).
- Added: what this list does not fix (K42–K44, Q40) and the areas no one examined, including the DFRobot importer (G12, G modalities).
- Added: 0 drawer entries share a part number on the PO's copy, read for CH-9 (my read, `python3 -I` on a scratch copy).

**The refactoring direction (§2)**
- R1 (the shape): the refusal sits in `home()` on every call, reads and dry runs included, after `inside_git`; no module reads a home at import (R1, CH-1 row; my grep of module-level `import tools`).
- R2: two kinds of write — the person's data never in the plugin, spark's regenerable artefacts refreshed there only by the operation that names them (#125's rule generalised); a run-time write map replaces the grep test (R1, R2 row, Mechanism).
- R4: the project id in a file of its own, not the brief; duplicates by part number; one `based_on` shape (R1, R4, CH-26, CH-29 rows).
- R5: one home per sentence, kept by a retired-sentence check (G14; EF-MISSING-8; FE-MISSING-8).
- R6: omissions tested by name, not by a vacuous property (R1, CH-16 row).
- R8: local aliases kept; the two mappings change, each pinned by a test (R1, R8 and CH-45 rows).
- §2.2: `wokwi_is_stand_in` and the key name `wokwi_power_pins` are now kept, with the reasons (R1, CH-31 and CH-32 rows).
- §2.3: `flock` serialises one machine; a private git remote is refused today; the union-merge condition and the critic's code read that no traced reader depends on line order; 319,145 bytes, not "312 KB" (R1, §2.3 rows and Numbers; STORE-17; G modalities).
- §2.3: holds released through the path a pick already runs (R1-Missing 11).
- §2.5: seam 3 is the run-time map over the commit gate's archived tree; seam 8, the sibling projects' command lines, is added (R1, Mechanism; RISKS pre-mortem 6).
- §2.6: "8 or 10 of 42"; DOC-M-D7's rule; the version check on the version line (R1, Numbers; DR-M5).

**The rule and the order (§3)**
- "Silent" is defined once, so a traceback or a printed path is a sign (R1, "The order").
- All ordering keys are stated — the brief's (a) and (b), the PO's own words (e), and my (c) and (d), which Q42 lets him strike; enabling work is not a key (R1, "The order").
- Each block carries an **unblocks** line, and §7 lists the dependencies the counts are read from, so the order can be checked.
- Down from tier 1 to tier 2: CH-5, CH-7, CH-8 — each prints a sign (R1).
- Up into tier 1: CH-26, CH-36's fab half, CH-49's coverage note, CH-54, CH-55, CH-57, CH-58 — each silent by the rule's own test (R1).
- CH-18 and CH-21 now share tier 1, and CH-54 with them — one failure shape, one tier (R1).
- CH-2 moves from rank 2 to rank 16; CH-12 stays at 12 and is now above it — the swap R1 asked for, by key (c) (R1; §6 split 19).
- CH-3 stays above CH-11 by key (a); the swap is refused with its reason, and CH-11 enters when Q2 is answered (R1; §6 split 18).
- R1's "strongest case" top five is answered by the first slice — CH-24's Design, Q5 and Q6 in week one — and by Q35 (R1; RISKS-1; §6 split 17).
- Added: how the list becomes cards, the first slice inside the stage limits, and what the PO gets first (R1, Capacity; RISKS-18; G Q-b).
- Added: the Done rule — a glossary entry for each new word, K id → card → test → commit on every card, and "the bin stays green" only with a test or "reasoned" (G "Unexplained" 4; RISKS-19; RISKS pre-mortem 6).
- Every root cause now opens with a "because …" sentence in plain words, ids after (G "Unexplained" 2, 5).

**The changes (§3)**
- CH-1: refusal in `home()` on every call; "unset" out of the title; size S–M; the proof's dry run now answers exit 2; `tools.py`'s import read moved to call time; `parts.py --store` (R1; UH-M-h; my grep).
- CH-2: compile **and** import in a subprocess; JSON mutants parsed; non-`.py` rows said; `refused` widened, not a new word; machine time computed (≈12.2 h, H); `--near` (R1; G; FE-MISSING-10).
- CH-3: downloads outside the lock; a waiting writer names the holder and gives up; `tools.py`'s write under the lock; SL verify C3 (c); "42" with its pattern named (G1; R1-Missing 3, 9; R1 Numbers).
- CH-4: the cache half removed to CH-62; root cause corrected; the run-time write map; compiled chips named as an artefact (R1).
- CH-5: tier 2; "13" marked H; a crash-cut history line cut and said (R1; G11).
- CH-6: maps `DesignError` itself, so it no longer waits for CH-5 (R1, CH-6 row).
- CH-7: tier 2; data first (R1, CH-7 row).
- CH-9: two entries with one part number named (the hand-copy half); conflict-name claims tagged; rank reasoned by reach (R1, CH-9 row; G, claims past their source).
- CH-12: both tscircuit cores cited, the version point settled (G modalities).
- CH-13: chip ids from `esp_app_format.h` (Apache-2.0); the image half called a symptom guard, its mechanism in §4 (G; R1, CH-13 row).
- CH-15: K16 joins it (R1's re-tier of CH-5).
- CH-16: each omission tested by name; K56's four other halves added (R1; G6).
- CH-17: the pick records its `fit` (NM-M4's mechanism), Q41 added (R1, CH-17; R1-Missing 4).
- CH-18: each word stays a substring test; a prefix test added (R1, CH-18 row).
- CH-19: synonyms as aliases in the data pass (G8).
- CH-22: the bin's `board.ts:40` type noted (R1, Mechanism).
- CH-23: error messages, not types; the test asserts the selector text; README's Build row (R1; G3).
- CH-24: depends on #125; "automatically" said plainly; Design in the first slice (R1; G "Unexplained" 6; RISKS-1).
- CH-25: built on the pick's own release path; Q34 and Q38 (R1-Missing 11; G Q-e, Q-i).
- CH-26: one `based_on` shape with every key present (R1, CH-26 row).
- CH-29: the project id in its own file; depends on CH-70 (R1, CH-29 row; EF-MISSING-2).
- CH-31: the key keeps its name; the check is per GPIO; the registry copy is generated and tested equal to the converter's (R1, CH-31 row and Missing 11).
- CH-32: the flag is kept and read; a stand-in board must say what it loses (R1, CH-32 row).
- CH-36: split — the fab half, scoped to the selected board so the bin's Gerber recipe stays green, in tier 1; the XIAO's label and data become CH-66 (R1, CH-36 row).
- CH-37: every copy of "builds with it" removed, and the glossary's restatement counted (G2).
- CH-39: the nine page lines and `init_project.py:485`'s printed line removed; the sleep current asked; the goal not asked twice (G2, G7, G9).
- CH-40: "8 or 10 of 42" (R1, Numbers).
- CH-41: "0 problems" → —; the glossary in the gate; the retired-sentence check; DOC-M-D6/D7; DR-M5 (R1; G2, G3; R1-Missing 6).
- CH-42: the sync-case paragraph; `idea.md:11`'s design-doc pointer (FE-MISSING-7; DOCUMENTATION-18).
- CH-44: "drops the source of each verified figure", not "drops them" (R1, CH-44 row).
- CH-45: two mappings and their tests; the grep test dropped; `--get` stays exit 1; the bin's `mismatch` grep run (R1, CH-45 row and Numbers).
- CH-47, CH-48: depend on or are edited by PR #125, said (R1).
- CH-49: split — the coverage note in tier 1; the `pins.py` facts become CH-67 (R1, "The order").
- CH-50: the pointer is `idea.md:25-26` (R1).
- CH-53: ranks by words hit, then by having a record (G8).
- New: CH-62 (merge #125), CH-63 (a board copy verb, G4), CH-64 (the tally's window, R1-Missing 7), CH-65 (the typed `origin`, R1-Missing 8), CH-66 and CH-67 (the two split halves), CH-68 (the bin's other calls as tests, RISKS pre-mortem 6), CH-69 (a module's closest part, a P178 concept, G5), CH-70 (the no-code sync experiment, EF-MISSING-2), CH-71 (the deleted temp folder's path, UH-M-i).
- Refused as changes, with the reason in §4: FB-M4's chip-keyed role now; a rename of `wokwi_power_pins`; removing the stand-in flag; a grep door test; whole-token matching; the id in the brief; a new mutant word; a vacuous property test; enabling work as a key.
- Not added as a separate change: TECH-LEAD-4's seven spellings of the plugin folder — folded into §2.3's paths rule, since no K row needs it.

**Questions, splits, what not to do (§4, §5, §6)**
- §4: eleven rows added (above), and the unsourced "a hobbyist's commonest folder change" clause dropped (G, claims past their source).
- §5: Q30–Q42 added — "better" by #17's words, the cut line, #125, platforms, releasing another project's hold, D8's order, the siblings' contract, porting the bin's checks, the hold verbs, DoD 8, K42–K44, the pick's fit, the ordering keys; Q26 asks who scores the stranger run; Q10 notes reading `wokwi-cli`'s source (G Q-a…Q-l; R1; mine for Q41, Q42).
- §6: splits 17–22 added — the top of the list, CH-3/CH-11, CH-2/CH-12, #125 or the store, what counts as a sign, duplicates beyond the plain key; split 6 now resolves the registry copy against R1's "use the converter's own".
- §7: the dependency list, my own facts, and an index of every round-1 line and critic gap taken.

## Changes since round 2

One line each: what changed, and why (R2 = `council/refuter-round-2.md`; its section and row, or "Missing n"). The section
above, *Changes since round 1*, is kept as it was written; where round 2 changed one of its lines, the line here says so.

**Facts and the picture (preamble, §1)**
- #125 is merged (the PO, 2026-10-10T17:32:08Z, D) and #124 closed: CH-62 leaves the list, Q32 is answered, CH-24's and CH-47's dependency on it is met, §2.2's row reads "done by #125", and every pointer into the nine files #125 changed is re-pointed at `4a18333` — `agents.md:126` → `:131`, `:144` → `:149`, `:248`/`:295` → `:253`/`:300`, `:292-328` → `:297-333`, `:317` → `:322`, `:413-424` → `:418-429`, `:456` → `:461`; `how-it-works.md:145` → `:146`, `:155-156` → `:156-157`, `:172` → `:173`; `tests/test_json_contracts.py:142` → `:164`; the gone `check_vendor_pins.py:111-112`/`:137-138` dropped (R2, Preamble (2); the round-1 lines "#124's fix is PR #125, open" and "CH-62 rank 7" are superseded).
- An empty `SPARK_HOME` reads `XDG_DATA_HOME/spark` when that is set, else the real store; §1, the journey table and CH-1's printed fix say so (R2, §1 and CH-1 rows).
- `check_spine`: with an island the build's errors never print; without one, their types only — replaces round 1's "only after the island" (R2, §1 row; CH-23).
- `init`'s "nothing to do" → 1 is the written design (`outcomes.py:9-11` names `NOTHING_TO_DO`): out of §1's faults and R8's list; one exit-code mapping adds a meaning, `boards.py`'s (R2, §1 row; supersedes round 1's "two mappings in two scripts").
- Added: #125's council rows N12–N28, quoted where they land (R2-Missing 1); P180 (#126), P181 (#127) and P182 (#128) where they touch ranked changes' pages (R2-Missing 2).
- Added as design faults: whether a write may land in spark's folder is decided by where a board file sits (N25, N26); a chip has two spellings and nothing maps them (R2-Missing 4); the needs file's reader refuses a field or pick shape it does not know (R2, CH-17 row).
- Added as data: `b12-kept-from-the-bin.jsonl` at the store's root, named by no place, and what it is — B12's URL proofs, written by hand (R2-Missing 7; my read of `scrum/PRODUCT_BACKLOG.md:1081`); the XIAO has no `wokwi_is_stand_in` key (R2, CH-32 row).
- Added: the lock a dry run takes (R2, CH-3 row); the tally's unreadable count is a sign, so K62's "no sign" grade is wrong (R2, CH-58 row); `design.read` decodes with the locale (R2, CH-6 row); `agents.md:85-86` and CH-1's refusal (R2, CH-1 row).
- "What this list does not fix" gains N12 and a suite run with CH-1's refusal (R2, Numbers).

**The refactoring direction (§2)**
- R1: `tools` re-raises the store's refusal as a `ToolProblem`, so no script ends in a traceback; the refusal names the fallback folder (R2, R1 row, CH-1 Mechanism).
- R2: one run-time write helper and one `plugin_root()` replace the second version's test-time map, which could not see N25 or N26 (R2, R2 row and CH-4 Mechanism; N14, N28).
- R3: `design.read`'s locale decoding is among what it replaces (R2, CH-6 row).
- R4: the copy digest is taken over the whole record less `SHELF_DROPS`; `--audit` compares field by field and says which side moved (R2, CH-26 row).
- R5: one chip-name table joins the tables (R2-Missing 4).
- R6: one `Answer` field per class of line, rendered by both printers (R2, CH-16 Mechanism); a source named by its folder (N13; CH-73).
- R8: one mapping adds a meaning, carried by CH-21; `init`'s alias is kept (R2, §1 and CH-21 rows).
- §2.2: removed — a dry run's lock, four of five plugin-folder definitions, `str.splitlines()` in the transcript reader; kept against the second version — `init`'s alias, `BUILD_FACTS`, the commit gate without a map; added — the write helper, the chip table, the `held by` column, schema 2 of `needs.json`, the folder key (R2).
- §2.3: the two-kinds-of-write rule enforced at run time; `plugin_root()` carried by CH-4 now that #125's council asked for it (TECH-LEAD-4 is no longer only folded); the root file (R2; N14, N28).
- §2.4: the outcome invariant's first case lands with CH-1 (R2, CH-1 Mechanism).
- §2.5: seam 2 tests per field; seam 3 is the run-time guard; CH-18's splitter at layer 1; P41's 0-or-1 test cannot guard the bin's Gerber recipe (R2, CH-16, CH-4, CH-18, CH-36 rows).
- §2.6: the PO's documentation brief of 2026-10-10 as a rule for every card (R2-Missing 3).

**The rule and the order (§3)**
- "Silent": the second version's "incomplete" becomes "leaves out a fact it read or holds about the very thing it reports", and Q43 asks the PO (R2, The order 2).
- Key (a) counts hard edges into changes of the epic only; soft edges break ties as (a2); edges into P178 concepts are listed, not counted (R2, the unblocks row). The result: CH-16 first (5), CH-1 eighth.
- Key (c): three classes, no order inside a class — the second version's simulation > circuit > layout > data is gone (R2, the keys row).
- Keys (f) reach today and (g) catalogue order added, so no pair is left to judgement (R2, The order 3: CH-9 and CH-10 below CH-11, CH-15 and CH-4).
- The constraint: no change above its hard prerequisite — CH-23 moves up to sit before CH-24 (key (e)), CH-28 down after CH-37; soft edges pointing down are listed in §7 (R2, The order 1).
- Enabling work: CH-1's "every later proof" clause removed (R2, the enabling row).
- Each block's "why this rank" names the key that placed it (R2: the keys must decide every pair).
- The Done rule gains the documentation experts' check (R2-Missing 3).
- Before rank 1: Q32 answered; Q41 and Q44 added.
- The first slice: three working-stage cards once P158, P180 and P181 are done, read from both boards — not four (R2, refuted).
- Tier moves: CH-58 → tier 4, CH-57 → tier 3 (R2, The order 2); CH-62 off the list; CH-72 into tier 1; CH-73 into tier 3.
- Swaps: CH-11 above CH-3 (the edges that kept CH-3 above gave no reason) and above CH-36 and CH-20 (key (d)); CH-9 below CH-11, CH-15 and CH-4 (key (f): its reach today is nil); CH-23 up beside CH-22 (the constraint); CH-5's mapping of the store's refusal moved into CH-1 — all applied (R2, The order 3). Applied in part: CH-10 sits below CH-11 and CH-4 but above CH-15, because the reasons R2 gives for moving it (no dependent in the epic, a code read only) hold for CH-15 too, so key (g) decides.
- Round 2's strongest top five is Q35 (b) and §6 split 24, not applied — the brief's tier rule stands (R2, The order 4).

**The changes (§3)**
- CH-1: the store's refusal re-raised in `tools`; a test over every `main`; the fallback named; `agents.md:85-86`; its counts from a fixture; no enabling clause; rank 8 (R2, CH-1 row, Mechanism, Missing 6).
- CH-2: "at most ≈12.3 h" over 1,281 rows; `--rows-in`, not `--near`; its one dependent conditional on Q22; rank 25 (R2, CH-2 row, Numbers).
- CH-3: a dry run takes no lock, with a test; its edges to CH-8 and CH-25 dropped; rank 17, below CH-11 (R2, CH-3 row, The order 3).
- CH-4: a run-time write helper and one `plugin_root()`; N25's and N26's cases as tests; the test-time map withdrawn; size M (R2, R2 row, CH-4 Mechanism; N14, N25, N26, N28).
- CH-5: the store's own refusal is CH-1's; four tier-1 changes lean on it softly, said (R2, The order 1).
- CH-6: a missing file stays `{}`; `design.read` reads UTF-8 (R2, CH-6 row).
- CH-8: its edge to CH-3 dropped (R2, the CH-3 row).
- CH-13: one chip-name table with both spellings and the folder; a type it lacks is could-not-run; its printed line in one spelling (R2, CH-13 row, Missing 4).
- CH-14: prints today's route until CH-24 lands (R2, CH-14 row).
- CH-16: one `Answer` field per class of line, rendered by both printers; tests per field, not per omission; rank 1 (R2, CH-16 Mechanism).
- CH-17: the fit is a field of the need, with schema 2 and a version rule; size M; tests for old and new files and the old reader's sentence; plant-alarm said (R2, CH-17 row, Mechanism, Missing 5).
- CH-18: its word splitter at layer 1 (R2, CH-18 row).
- CH-21: carries CH-45's `boards.py` mapping and both its tests; its selection sentence names `boards/active.json`, never `--id` (R2, CH-21 and CH-45 rows).
- CH-22: pointers at `4a18333`; P181 goes first (R2, Preamble (2), Missing 2).
- CH-23: error messages printed with or without an island; moved up to rank 27 by the constraint; P182 for README's row (R2, §1 row, The order 1 and 3).
- CH-24: #125 met; Build after ranks 26–27; reads CH-13's table (R2, CH-24 row, Q35 row).
- CH-25: the `held by` column split out as CH-72; its edge to CH-3 dropped (R2, The order 2 and 3).
- CH-26: a digest over the whole record less `SHELF_DROPS`; field-by-field compare naming the side that moved; a fixture that changes `simulation` (R2, CH-26 row, Mechanism).
- CH-28: placed after CH-37, its last hard prerequisite (R2, The order 1).
- CH-32: the XIAO gains `false`; a person's file without the flag refused with a sentence; Q44 (R2, CH-32 row, Mechanism).
- CH-35, CH-39, CH-41, CH-46, CH-47, CH-56: line pointers at `4a18333` (R2, Preamble (2)).
- CH-36: P41's test accepts 0 or 1, so the scope test is the bin recipe's only guard (R2, CH-36 row).
- CH-42, CH-43, CH-61: go with P182 (R2-Missing 2).
- CH-45: its `boards.py` half moved to CH-21; its printed `--id` gone; its `init` half is Q25's (R2, CH-45 row, §1 row).
- CH-47, CH-48: after P181; #125 met (R2-Missing 2).
- CH-57: tier 3; its root cause is `sources` outside `PRIVATE` inside a git work tree; the root file and Q45 (R2, CH-57 row, Missing 7).
- CH-58: tier 4; prints why a line is unreadable (R2, CH-58 row).
- CH-62: off the list — merged (R2, Preamble (2), CH-62 row).
- New: CH-72, the drawer's `held by` column, tier 1 (R2, The order 2); CH-73, whose copy answered named by its folder, tier 3 (R2-Missing 1; N13, N24, N27).
- The verifiers' missed causes BR-M2, BR-M8, BR-M9, DR-M3, DR-M7, SL-M5 are now cited by id where they land (R2-Missing 8).

**Questions, splits, what not to do (§4, §5, §6, §7)**
- §4: rows changed — #125's cache, `BUILD_FACTS`, enabling work; rows added — the commit-gate map, a direct chip compare, a fit inside the pick, a dry run's lock, the flag without the XIAO's `false`, `--id` as a selector, `--near`, soft edges as unblocking, `init`'s alias as a fault, N12 (R2).
- §5: Q25, Q31, Q32 (answered), Q35, Q41, Q42 changed; Q43 (silent), Q44 (the stand-in flag), Q45 (the root file) added (R2).
- §6: splits 1, 2, 8, 11, 17–20 updated; splits 23–30 added (R2).
- §7: facts at `4a18333`; #125's council rows mapped; the dependency list rewritten and checked by a parser; round 2's lines indexed (R2).

**Numbers**
- 1,281 mutation rows in 116 tables at `4a18333` (was 1,268 in 115 at `a8aa34d`); 18 cards in Done on the spark board (was 17); four cards in flight; the machine time an upper bound (R2, Numbers; my count).

## Status

**72 changes**: 25 in tier 1, 19 in tier 2 (block A 8, block B 5, the rest 6), 18 in tier 3, 6 in tier 4, 4 in tier 5;
six of them are P178 concepts or their prerequisite, ranked but meant for #123's discovery (CH-27, CH-70, CH-29, CH-33,
CH-69, CH-28). **Refuter verdicts**, read from each round's *Verdicts* tables by a parser over the second column (my
run, 2026-10-10): **round 1** — 92 rows: 65 holds, 25 partly, 1 refuted (the preamble's "#124 … CH-4 reuses it"), 1
partly with its cache half refuted (CH-4); **round 2** — 45 rows: 17 holds (14 plain, one "as a definition", one "with
two findings", one "root cause"), 23 partly, 4 refuted (#125 still open; CH-58's tier; the first slice inside the
limits; CH-62), 1 not re-opened (CH-29, CH-63, CH-65, CH-67, CH-69, CH-70, CH-71). The completeness critic gave gaps
(G1–G28), not verdicts. **Still disputed**, each left to the PO: the count behind key (a) — hard edges only, as here, or
soft ones too, which puts CH-1 first (§6 split 23, Q42); D8's boards-first order against the brief's tier rule — round
2's top five (split 24, Q35); whether an answer that leaves out a fact it read is silent (split 26, Q43); holds stored
or derived (split 1, Q1); from round 2, whether I1 outweighs the agent's JSON (CH-18 ↔ CH-16; Q42); and CH-10's place
against CH-15, which key (g) decides (split 31). **Not yet read by any refuter:** CH-72, CH-73, every fold of this
round, and the seven changes round 2 did not re-open; and the bin's `make check` has still been run against no change.
