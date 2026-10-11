# P158 part 1 — the completeness critic, on `proposal.md`

Written 2026-10-10 by the completeness critic, against spark 0.8.1 (main `a8aa34d`, E `git log -1` →
`a8aa34d 2026-10-09 17:13:40 +0200 Merge pull request #122`). The question asked of me: what is missing. Read whole:
`catalogue.md` (K1–K74), `proposal.md` (1,527 lines, 24,844 words by `wc -w`), the "Missed root causes" of all six
`diagnosis/*.verify.md`, the "missing" items and the questions for the decider of all eight lenses, and
`council/refuter-round-1.md` — so that what the refuter already found missing is pointed at, not re-found. Code opened at
every line cited below. Tags: **E** a pointer (file:line in spark at `a8aa34d` unless another repository is named; a
command and its output; a card), **H** a claim with its source, **D** a decision (who, when), **—** unknown. Nothing here
decides anything for the PO.

**How I ran things.** No spark command was run, so no scratch store was made. The PO's real store was only listed
(`ls`, `realpath`; nothing opened for writing). One read-only count over `~/.claude/projects/*/*.jsonl` (counts of three
byte sequences, no content printed). One slip, said here: I wrote a copy of the proposal's §1 to `<scratch>` (the
session's scratch root, not `<scratch>/p158/completeness-critic`) for a grep, and deleted it in the next command. No `gh`
call. Nothing else written but this file.

## Gaps

Each: **what is missing** · evidence · **where it should land**. Ordered by what it changes: first what would make a
change do harm or leave the reader unable to act, then catalogue halves, root causes, lens items, questions and
modalities. Items the refuter's round 1 already raised are listed once, in G28, by its number.

### What would make a ranked change do harm, or leave a fix half done

**G1 · CH-3 turns K64's unranked half into a silent hang.** K64 says "the lock is held across `--fetch`'s downloads and
the `built` line, silently"; §7 maps K64 to Q12 only (`proposal.md:1474`), and Q12 is about splitting `parts.py`. E:
`--fetch` declares `("network", "writes")` (`scripts/parts.py:1482`); `main` holds `store.locked()` around the whole
operation when `writes` is declared (`:2198-2201`); the lock is `fcntl.flock(held, fcntl.LOCK_EX)` with no timeout and no
message (`scripts/store.py:194`). Today two agents with two `TMPDIR`s lock two files (K5), so a slow download blocks
nobody else. CH-3 makes the lock one file beside the data, so after CH-3 one agent's stalled `--fetch` makes every other
writer of the store wait, printing nothing — in what CH-3 itself calls "this project's normal working mode"
(`proposal.md:331-332`). No change, test or "what breaks" line names it. **Land:** CH-3 — download outside the lock and
take it only to write; a writer that waits says so (who holds it, since when) and gives up as could-not-run after a stated
time; test: two processes, one holding the lock, the second exits 2 naming the holder.

**G2 · Retired sentences have more homes than the removal lists name, one of them a script.**
- CH-39 removes "after a build, run `init` again with `--force`" from `init.md:36-42`, `README.md:155` and
  `journey.md:717-722` (`proposal.md:1040`). E `grep -rn "init.*again\|--force"`: it also stands at `README.md:74`
  ("`check_all.py`, after `/spark:init` again"), `docs/guide/agents.md:144`, `docs/guide/commands.md:30`, `:49-53`,
  `commands/init.md:47`, `:60` — and **`scripts/init_project.py:485` prints it** ("no built design found, so the rails are
  empty — build, then re-run with --force"), recorded at `journey.md:579`. After CH-39 as written the script still tells
  the person to do what the pages stopped saying.
- CH-37 removes "builds with it" at `parts.py:1631` only (`proposal.md:995-996`). E: `scripts/parts.py:2088` prints "onto
  the shelf, so every project builds with it" for a shelved record that may owe `pin_order_proof` or `simulation`; the
  same words stand at `commands/idea.md:141` and in the recorded outputs `journey.md:468`, `:497`.
- `GLOSSARY.md:233-247` ("Owed, and broken") is a sixth prose restatement of the owed-facts table — DOCUMENTATION-12
  counts five, CH-37 rewrites five — and it names `pin_order_proof` as owed, which Q3 may change.
- The mechanism nobody ranked: a sentence retired in one commit has no check that keeps it out. EF-MISSING-8 and
  FE-MISSING-8 (port the bin's `tools/check-current-docs.py` as a retired-phrase gate) appear 0 times in the proposal
  (my grep); CH-41's closed-card check is another thing.
**Land:** CH-39's and CH-37's removal lists (with `init_project.py:485` and `parts.py:2088`); a retired-phrase function in
CH-41, seeded with the sentences CH-30, CH-34, CH-37, CH-39, CH-50 and CH-55 retire, reading the scripts' printed
strings as well as the pages.

**G3 · README's "What works today" says Build **works**, against two of the proposal's own findings.** E
`README.md:73`: "**works**: a requirements file to a board that builds". CH-23's title: "The library S3 cannot build a
design that spends MOSI or MISO" (`proposal.md:700`); K22: a board file that passes every check merges pads. No change
touches the row; DOC-M-D6 ("a **works** row links a section that holds a recorded block") and the documentation lens's
question on DoD 8 appear 0 times in the proposal. **Land:** a line in CH-23 (the row says "partly" until CH-23 lands) and
DOC-M-D6 inside CH-41 or CH-43, with its DoD 8 question in §5.

**G4 · The PO's "copy … the boards for sure" has no change.** The Block A table answers boards' copy ("a hand `cp`, no
provenance") with CH-26 (`proposal.md:647`). CH-26 writes `based_on` "on every copy into a project (catalog → project
writes none today, `parts.py:1303`)" — parts only. E: `promote` resolves through `record_home`, which walks part records
(`scripts/parts.py:1293-1296`; CH-21's own root cause cites `:966-969`); `grep -n based_on scripts/boards.py` → nothing.
The store lens's B3 ("one copy verb for both kinds") lost its board half. **Land:** CH-26 or CH-27 — a board copy into a
project, and from a project to the store, with `based_on`; or a §4 line saying boards are copied by hand until P178.

**G5 · The module half of "the closest board, or one made for it" is a page only.** For modules, CH-30 documents the three
existing stances (`proposal.md:853-858`); nobody — no lens, no diagnosis — proposed a lookup from a record's `function` to
the closest Wokwi built-in part, or a custom-chip skeleton generated from a record's pins. Neither is in §4 either, so the
PO cannot tell "not wanted" from "not thought of". **Land:** one §4 row or one P178-concept line under Block B.

### Catalogue rows, or halves of rows, that no change fixes

**G6 · K56's four other halves (C-32).** CH-16 fixes the `fix` printed only when there are no lines. Untouched: a
no-line refusal names no subject; notes repeat for untouched picks; a `skip` drawer entry reads "to get — known, not
owned"; an id with capitals is refused without saying ids are lower-case. E `grep` of the proposal for
`lower-case|capitals|no subject|skip` entry → 0. **Land:** CH-16, as four named tests.

**G7 · K46's two halves.** "No page says which nulls a person can answer and which need a meter" reaches only CH-28, a
P178 concept ("the fill list K46 asks for"); "a battery node's one number that matters (sleep current) is never asked"
reaches nothing: E `grep -n sleep scripts/init_project.py` → nothing. **Land:** CH-39 (init's questions), as one field
for a battery-powered design, marked needs-measurement.

**G8 · K33's synonym case and K36's ranking case.** `footswitch` finds nothing while `--match` offers `tactile-button`
(K33); a record-less L298N outranks the L9110S that has a record (K36). CH-18 tokenises, CH-53 ranks by words hit; neither
reaches a word the store does not hold, and neither ranks a candidate with a record above one without. **Land:** CH-53's
rank key (words hit, then has a record), and synonyms as record aliases in the data pass (Q6) — or §4 says they stay.

**G9 · K63's goal half** ("`/spark:init` re-asks the goal S already heard"): CH-20 takes the `--step` half, CH-39 the I²C
half, nothing the goal. **Land:** CH-39.

**G10 · K15's kept-name half** (names Windows or exFAT refuse) — CH-57 takes the modes, `fcntl` and the size cap, not
the names; and no question asks which platforms spark serves (G21). **Land:** CH-57, after G21.

**G11 · K11's crash case.** A history whose last line was cut by a crash mid-append stops `--pick`, `--step` and `--tally`
("line N is not a history event — fix it by hand", `scripts/store.py:294`); CH-5 makes the sentence quote 40
characters, and the person still edits the file by hand. The appender already guards the gluing case
(`_last_line_is_open`, `store.py:299-305`); the reader offers nothing for the one shape a crash leaves. Low. **Land:**
CH-5 — a dry-run repair for an unterminated last line, or one sentence saying why not.

**G12 · K42, K43, K44 are "not ranked" with no question.** §7 parks them on #99, #5, #93 (`proposal.md:1471-1473`);
nothing asks the PO whether they are outside part 1. K44 (choose among equivalent owned modules) is "search" in his own
2026-10-10 emphasis. **Land:** §5, and a "what this list does not fix" line in §1.

### Missed root causes nobody picked up

**G13 · NM-M4, FB-M4, DR-M5** — dropped (refuter round 1, Missing 4–6). Not repeated.

**G14 · A sentence has no single home, so a fix lands in some of its copies** — the root cause under G2, named by no
diagnosis: the owed-facts table in six prose places plus two printed strings; "re-run init with `--force`" in nine page
places plus one printed string. DOC-M-D5 ("lists in prose equal lists in code") covers tuples (`VERBS`, `PIN_ROLES`,
`PRIVATE`), not sentences. **Land:** §2.1 as a ninth shape, or inside R5 — "a sentence the system says lives in one
place: the code prints it, the pages point at it" — with G2's check.

### Lens "missing" changes not in the proposal

Each checked by `grep -c` of its id or its words in `proposal.md` (2026-10-10).
- **EF-MISSING-2 · the no-code git sync experiment on a copy of the store** (two clones, a pick in each, `merge=union` on
  `history.jsonl`, merge, write down what the output said): 0. It is the cheapest evidence for CH-29 and Q28 before any
  design. **Land:** a card before P178's council, or under CH-29's "depends on".
- **FE-MISSING-7 · the sync-case sentence** (what the store tolerates in a synced folder, and that two machines writing
  at once are not protected — `flock` serialises one machine, refuter round 1 on §2.3): 0. **Land:** CH-9's docs line or
  CH-42.
- **FE-MISSING-10 and RISKS-19 · nothing ties a fix to its K id** (`mutate.py --near <file>`; a column K id → card → test
  → commit): 0 and 0. Every pointer in the catalogue and the proposal is a line number at `a8aa34d`, and PR #125 already
  moves some (refuter round 1). **Land:** §3's preamble, as how the list is tracked.
- **DOC-M-D6** (G3) and **DOC-M-D7** (a sentence that documents a fault names its card; the card's close deletes it): 0.
  **Land:** CH-41.
- **UH-M-h · `parts.py --store`** (#101's own suggestion: "which store am I in, and is it the one with my parts?" before
  anything is written): 0. CH-1 names the store on answers; no command asks it. **Land:** CH-1 or CH-11.
- **UH-M-i · `check_spine` prints a temp work folder that is deleted a second later**: 0. **Land:** tier 5.
- **DOCUMENTATION-18 · `commands/idea.md:11` sends every `/spark:idea` run to "docs/2026-10-04-store-design.md §8 S and
  M"**: 0. **Land:** CH-42.
- **RISKS pre-mortem 6 · the sibling projects' command lines as spark tests.** The guard exists for `boards.py`:
  `TheCommandLineTheSmartBinDependsOnTest` (`tests/test_boards.py:314`, P41) pins the bin's eight invocations, and
  `test_validate_and_validate_for_fab_both_answer` (`:378`) validates every available board, the library XIAO included
  — the test CH-36 would turn red. The proposal cites neither; its "bin" lines are reasoned, and two are wrong (refuter
  round 1: CH-31, CH-36). Whether the bin's other spark calls — `check_bom.py` (bin `Makefile:186`, `:212`),
  `check_vendor_pins.py --offline` and live (`:220`, `:223`), `check_physics.py --rules` (`:228`) — are pinned by a test
  is — (not traced); CH-4 and CH-44 change what two of them print. **Land:** every block's "bin" line names the test that
  proves it, or says it is reasoned.

### Questions for the PO nobody asked, or a lens asked and §5 dropped

- **Q-a · What is "better", and how will this list show it?** #17's three words — more parts known, proven by use, fewer
  requests measured (D the PO, 2026-10-04, per RISKS-3) — appear 0 times in the proposal ("proven by use" 0, "fewer
  requests" 0); RISKS-3 is uncited (refuter round 1). Decides the epic's done line. **Land:** §5.
- **Q-b · What lands first, and how do 61 changes become cards?** (RISKS-18; refuter round 1, "Capacity"). **Land:** §5.
- **Q-c · PR #125 or CH-4's cache design?** Refuter round 1 found #125 (Missing 1); §5 should ask it. **Land:** §5.
- **Q-d (G21) · Which platforms does spark serve — macOS only, Linux, Windows?** Decides K15's name half, CH-10's
  case-insensitive test, CH-57's no-`fcntl` line. H: the PO's direction that spark goes public for hobbyists
  (2026-10-03, his memory notes). **Land:** §5.
- **Q-e · May an agent working on project B release project A's hold?** The AI-agent lens asked it
  (`user-ai-agent.md` §4); §5 has no permission question before CH-25 builds `--release`. **Land:** §5, beside Q1.
- **Q-f · D8's order.** FEASIBILITY's question 10 asked whether the PO accepts his "first fix" landing after the schema,
  the stand-in check and the cache move; §6 split 8 says "the PO may move it" and §5 does not ask. **Land:** §5.
- **Q-g · Are the sibling projects' `make check`s a contract every spark merge keeps green, or may a change break one
  with a note?** The proposal assumes green in every "bin" line without asking. **Land:** §5.
- **Q-h · Port the bin's `fake_machine.py`, `lib/checks` and `check-current-docs.py` into spark?** (existing-first's
  question 5). **Land:** §5, with G2 and CH-49.
- **Q-i · The hold verbs' names** — InvenTree's (allocate, release) or spark's (hold, release, forget) — existing-first's
  question 8; the person reads them in every refusal. **Land:** §5, with Q1.
- **Q-j · DoD 8** — must a **works** row link a recorded block? (documentation's question 4; G3). **Land:** §5.
- **Q-k · K42/K43/K44 in or out of part 1** (G12). **Land:** §5.
- **Q-l · Who scores the stranger run?** Q26 schedules it; the user-human lens also asked who scores it. **Land:** Q26.

### Modalities not run — and what this report settled

- **Areas nobody examined, so "no row" is not "no fault".** 0 mentions in the proposal each (my grep): the review and
  fabrication path (`skills/spark-review`, `agents/design-reviewer.md`, `scripts/check_bom.py`, `check_footprints.py`,
  `fab.py`, `copper.py`), `skills/spark-reverse-engineer`, `commands/identify.md`, `agents/part-finder.md`, `chips/`,
  `DECISIONS.md`, and `data/importers/dfrobot.js` — the importer D8's "automatically from the DFRobot orders" starts
  from, which returns only `{sku, name, count}` by design (`dfrobot.js:5-6`). The catalogue's sources were P100's walks,
  which never reached these. **Land:** a "not examined" line in §1, and P158 part 2 or a later council.
- **The bin's `make check` was run by nobody against any change** (the risks lens could not: it writes in the bin). A
  scratch copy of the bin with `SPARK=` at a scratch spark worktree would settle every "bin" line; spark's P41 test
  settles the `boards.py` half today. **Land:** each change's Done line.
- **EF-MISSING-2's git experiment: not run.** One of its "—" is settled by a code read here: **no history reader I traced
  depends on line order**, so a union merge's random order (STORE-17) changes none of their answers. E:
  `cost.windows` orders steps by `_start_of` time (`scripts/cost.py:200-212`); `store.recorded` compares event keys
  (`scripts/store.py:308-311`); `_op_tally` uses membership and `any` (`scripts/parts.py:2141-2149`); `events()`'s
  callers are `parts.py:1999`, `:2137` and `store.py:319` (`grep -n "events()" scripts/*.py`). Whether `--step`'s listing
  reads order: — (not traced). **Land:** §2.3's sentence the refuter asked to qualify.
- **A full mutation sweep: not run by anyone**; CH-2's "hours of machine time" is unmeasured (refuter round 1). **Land:**
  CH-2's proof.
- **A person typing: 0 of 74 rows.** Q26. Not repeated.
- **K62 is not only reasoned.** E my count, 2026-10-10, over 398 transcript files under `~/.claude/projects`: 8 hold a raw
  U+2028, 4 a raw U+2029, 1 a raw U+0085; 25 lines hold one, and `str.splitlines()` (`scripts/cost.py:110`) would cut each.
  Whether any sits inside a tallied project's step window: —. **Land:** catalogue K62's "observed by"; CH-58's proof can
  use a real line.
- **CH-13's chip ids, settled.** E esp-idf `components/bootloader_support/include/esp_app_format.h` (master, through the
  Espressif documentation search, 2026-10-10): `ESP_CHIP_ID_ESP32S3 = 0x0009`, `ESP_CHIP_ID_ESP32C6 = 0x000D` (13),
  `ESP_IMAGE_HEADER_MAGIC 0xE9`, `SPDX-License-Identifier: Apache-2.0`. The 13 is no longer H, and the source is
  Apache-2.0 rather than esptool's GPLv2+ code — which answers existing-first's licence question for a copied table.
  **Land:** CH-13 cites this header.
- **CH-12's grammar, settled for the version it was seen on.** E the bin's `node_modules`: `tscircuit` 0.0.2621 declares
  `@tscircuit/core ^0.0.1958`; the hoisted core is 0.0.1958; a second core, 0.0.1911, under
  `@tscircuit/runframe/node_modules` carries the same rule (`dist/index.js:11608`
  `if (/^\d+$/.test(hint)) return Number(hint);`). Whichever the build loads, the rule CH-12 quotes is there. Closes
  refuter round 1's CH-12 numbers point. **Land:** CH-12's citation.
- **Is the real store in a synced folder? No.** E `realpath ~/.local/share/spark` → itself (no link), mode `drwx------`;
  two folder-sync clients' folders exist under `~/Library/CloudStorage`. So CH-9's conflict copy has no instance today
  (SL verify C7 counted 0 non-plain stems); its rank rests on P178's direction. Answers FEASIBILITY §3's "—". **Land:**
  CH-9's "why this rank".
- **CH-33's "whether `wokwi-cli` loads a local board": still —.** One web search (below) returned only the web editor's
  "Load custom board file…"; `which wokwi-cli` → not found on this Mac, so its source was not read. **Land:** Q10 stays
  open; reading the CLI's source would settle it.

### Claims stated past their source

- CH-9: "Dropbox's, Syncthing's and iCloud's conflict names all fail `PLAIN`" (`proposal.md:439-440`), untagged; its
  source tags the Dropbox and iCloud names H (`existing-first.md:258-259`). **Land:** tag it H.
- §4: "a moved folder — a hobbyist's commonest folder change" (`proposal.md:1380`): no source, no tag. **Land:** H with
  a source, or drop the clause.
- Refuter round 1's Numbers section stands; not repeated.

### Already raised by the refuter's round 1 — kept here for completeness

**G28.** Missing 1 (PR #125), 2 (`sim_project.py:162` writes chips into the plugin; K13's chip half), 3 (`tools.py:445`
writes the store outside the door; `tools.py:47-48` reads the home at import), 7 (K21's "one `--step` outside Claude Code
spoils the tally"), 8 (K65's typed `origin`, decided 2026-10-06, unranked), 9 (SL verify C3 (c), `.lock` inside a
repository), 10 (RISKS-1, -3, -18, -19, STORE-17, USER-AI-AGENT-13, FEASIBILITY-11, -19 uncited), 11 (existing-first not
used). Where they land is in that file.

## Unexplained for a reader

The question: does the proposal explain, for a reader who knows nothing, **where** each mistake happens and **why**, in
words a hobbyist understands? For the "prints" lines, mostly yes — each is a sentence naming the file and the reason
(E e.g. CH-12's, `proposal.md:485-486`). For today's faults, mostly no:

1. **There is no map from the person's journey to the faults.** The list is ordered by tier and §1 by kind of fault
   (design, implementation, documentation, data). A hobbyist's "where" is a step: I say what I want → spark lists what I
   own → I pick → it writes the parts file → it builds → it simulates → I put it on the board. No table says, per step,
   what the person sees, what actually happened, why, and which change fixes it. **Land:** a §0 of one table, about
   fifteen rows, hobbyist words, ids in the last column only.

2. **The "why" of a change is often an id.** By my parse of each block's `root cause` field (2026-10-10), 22 of the 61
   blocks give it as ids and at most three words; CH-28 and CH-29 have no root-cause field. Ten cited root causes are
   stated in words nowhere in the proposal — RC-BR-5, -6, -7, -9, RC-NM-4, -5, RC-DR-2, -3, -4, -6 (each appears only in
   its block and in §7's index; `grep -n` per id) — and for six blocks one of them is the only cause given: CH-19, CH-24,
   CH-36, CH-43, CH-47, CH-61. CH-24 is the PO's own first fix (D8); its why is `RC-BR-6` and nothing else
   (`proposal.md:725`). **Land:** each block opens its root cause with one "because …" sentence, the id after it.

3. **"The picture in one page" is not one page.** E lines 43–126: 1,277 words, 108 id tokens, 59 code spans (my count) —
   one id for every twelve words. **Land:** §1 rewritten as the §0 table plus five sentences; the ids move to §7.

4. **The words are not defined, and spark's glossary is not used.** `envelope` (25 uses, first at `proposal.md:66`),
   `island` (5), `door` (16), `tombstone` (6), `could-not-run` (20) — the three outcomes are never spelled out; §2.4 says
   only "Three outcomes stay, defined once (`outcomes.py:19-43`)" (`:217`). spark already has `GLOSSARY.md` (416 lines,
   each word with "the failure that produced the word"), with entries for the three outcomes, the chain, mutation,
   anchor, caught/escaped/refused, record, catalog, shelf, `verified`, stand-in, owed and broken, the store, the drawer,
   pick and reserve, history, tally (`grep -n "^### " GLOSSARY.md`). The proposal links it 0 times; `envelope`, `island`,
   `door` and `tombstone` have no entry; and no change adds an entry for the words it introduces (`store`, `kind`, `next`,
   `based_on`, release and forget, `wokwi_pin_names`, `wokwi_stand_in`, `--board-skeleton`, "refused" for a mutant that
   does not compile — the word already means "the anchor did not match", `GLOSSARY.md:108-114`). `GLOSSARY.md` is also
   outside the docs gate (`tools/check_docs.py:30-33`), and CH-41 does not add it. **Land:** a reading note at the top
   pointing at `GLOSSARY.md` anchors; "its `GLOSSARY.md` entry" in the Done line of every change that adds a word.

5. **The mechanism is given in code, not in a concept.** CH-1's why is "the truthiness fall-through at `store.py:48`".
   The same three, in the words the proposal could use:
   - CH-1: *spark finds your parts list through a setting called `SPARK_HOME`. If the setting is empty, it quietly uses
     your real list; if it names a folder that is not there, it quietly starts a new, empty one — and either way the
     answer looks exactly like a correct one.*
   - CH-12: *a board file that labels a pad with a bare number such as `17` makes the circuit tool read it as "pin 17",
     so two different pads become one connection; every check reads that merged circuit, so every check passes.*
   - CH-25: *a part one project reserved stays reserved: no command gives it back, and the drawer listing does not show
     who holds it.*
   **Land:** the "because …" sentence of item 2, in this register.

6. **"Automatically" in D8 is not said plainly.** CH-24 fills pins from the vendor's header and chip facts from a table;
   the outline, the header rows and the power pads stay "OWED … measure them on the kept dimension drawing"
   (`proposal.md:738-742`). Nowhere does the proposal tell the PO in one sentence that the measuring stays his, or how a
   drawer entry's SKU — the only identity the import carries (`dfrobot.js:5-6`) — finds the board's documents.
   **Land:** CH-24's "why this rank" or proof.

7. **References to other documents' sections are not glossed.** `§5.8` (6 uses, first at `proposal.md:830`), `§6.4`,
   `§8 G`, `W1`, `D8`, `★C1`–`★C9` carry no half-sentence of what they say. **Land:** a half-sentence at first use.

## Searches

- Espressif documentation search, 2026-10-10: "ESP image header chip id field esp_chip_id_t ESP_CHIP_ID_ESP32C6 value" →
  [esp_app_format.h](https://github.com/espressif/esp-idf/blob/master/components/bootloader_support/include/esp_app_format.h)
  and the [App Image Format API reference](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/api-reference/system/app_image_format.html).
  Used (CH-13).
- Web search, 2026-10-10: "wokwi-cli custom board board.json local diagram" →
  [wokwi/wokwi-boards](https://github.com/wokwi/wokwi-boards),
  [ESP-IDF's Wokwi page](https://docs.espressif.com/projects/esp-idf/en/latest/third-party-tools/wokwi.html),
  [espboards.dev](https://www.espboards.dev/blog/use-wokwi-in-vscode-esp32). Did not settle CH-33.
- Local, read-only: spark at `a8aa34d` (`scripts/`, `tools/check_docs.py`, `tests/test_boards.py`, `GLOSSARY.md`,
  `README.md`, `docs/guide/`, `commands/`, `data/importers/dfrobot.js`); the bin's `Makefile` and `node_modules` package
  files; `~/.local/share/spark` listed only; `~/.claude/projects/*/*.jsonl` counted only.
