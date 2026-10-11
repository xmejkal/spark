# P158 part 1 — the risks-and-assumptions lens

Written 2026-10-10 against spark 0.8.1 (main `a8aa34d`, E `git log -1`), for the council the PO asked for the same day
(*"what exactly is going wrong where and why and how to refactor it well and add or remove parts to simplify it … suggest a
list of changes into the system"*, D the PO, 2026-10-10). The one user line the harness relayed asks whether *"some new
file formats or synch libraries or techinques could be used from an existing library"* for the store — answered at RISKS-17
and in §2 (store), as an option, not a decision.

**What I read**, whole: `../catalogue.md` (K1–K74), the six diagnoses and their six adversarial checks in `../diagnosis/`,
the P100 folder (`brief.md`, `items.md`, `risks-and-tests.md`, `verification.md`, `diary-round-0-board.md`,
`council/po-assistant.md`, `council/user.md`, `council/tech-lead.md`, `council/refuter.md`, `council/round-0-runner.md`),
`docs/2026-10-04-store-design.md`, `docs/2026-09-30-refactoring-architecture.md`, `scripts/store.py`, `scripts/boards.py`
(the resolver and `main`), `tools/mutate.py`, `tools/check_commit.py`, `scrum/README.md` (the limits, the DoD), the bin's
`Makefile` (its spark lines), irrigation's `DIARY.md`, `.spark/rules.json`, `board.tsx`, plant-alarm's `board.tsx`,
`.spark/needs.json`, `requirements.json`, the real store's `projects.json` (a read), and twenty-two store
cards — #94, #123, #101, #114, #44, #102, #59, #17, #99, #93, #96, #118, #119, #6, #16, #5, #89, #70, #19, #22, #23, #58 (`gh issue view`, read-only).
`../design/` is empty (E `ls`): nothing is decided yet.

**How I ran.** One copy of the PO's store (`cp -R` to `<scratch>/p158/risks/store`, 33 MB by `du -sh`), every spark
command prefixed `SPARK_HOME=… HOME=… TMPDIR=…` as three words (E `env | grep SPARK_HOME` under the prefix →
`<scratch>/store`), one scratch project `proj-data`. Seven commands, in the appendix; the fourth WROTE to the copy
(`--drawer-set`, four entries), so the copy is no longer the real store's image. The real store was never run against or
written. Nothing under `~/Development/spark` was written but this file. Tags: **E** a pointer or a run and its output;
**H** a claim with its source; **D** a decision (who, when); **—** unknown. Every number carries its provenance.

The PO's criteria, applied throughout (D the PO, 2026-10-10, verbatim): *"we want the system to be well designed so its
well testable and understandable where a mistake is happening and why"* — testability, diagnosability, simplicity.

## 1. Findings

| id | claim | tag | pointer | supports only |
| --- | --- | --- | --- | --- |
| RISKS-1 | Nobody outside the project is blocked, and no card is in Ready, Build or Review: the spark board holds Idea 82, Discovery 2 (P100 #6, P158 #94), Done 17, no other status; 81 issues are open. The one person blocked is the PO, at P100 round A (his declared next step, D3/#123 "First, test what works now"), by three findings TOGETHER: K3 (his only S3 and the LiPo held by the bin — a pick on the store as it is is refused, my run 7), K29 (his four other ESP SKUs have no board file — a pick is accepted with a note, `--requirements` refuses) and K36 (91 of 110 drawer entries unreachable by any need). Round 0 is done; rounds A/B/C have not started and his yes to the changed frame is unrecorded. | E | my `gh project item-list 2 --owner xmejkal` and `gh issue list`, 2026-10-10 (read-only); `brief.md:10`, `:19`, `:113`; my run 7 → `refused, so nothing was written: firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here` | who waits on what today; not the order of fixes |
| RISKS-2 | The wall that blocks round A's MATCHING is data, not code. On the copy, one `--drawer-set` giving `function: [{compute, microcontroller}]` to his four unfiled ESP SKUs (DFR1075, DFR1117, DFR0994, DFR0575) took `--match` for `board — compute / microcontroller` from 2 candidates (the two library boards, `free 0`) to 6 (`owned 2 dfrobot-dfr0575 (drawer) … free 2`, `owned 1 dfrobot-dfr0994 … free 1`, `owned 2 dfrobot-dfr1075 … free 2`, `owned 3 dfrobot-dfr1117 … free 3`, plus the two) with NO code changed. The pick of `dfrobot-dfr1075` then passes with `a board needs a board file — a record in boards/ — before spark can build with it` (K29). | E | my runs 2, 4, 5, 6 (appendix); the board-records refuter's run on `dfrobot-dfr0975` (`board-records.verify.md`, RC-8) agrees | that K36/K44's "blocks the journey" half is one data pass away for the board need; the NEXT wall (K29) is a missing operation (board C8), and the one after (K3) is the PO's own decision (RISKS-9) |
| RISKS-3 | After all 56 proposed changes ship, "better" by the PO's own measure is still unmeasured for two of its three words. #17 (D the PO, 2026-10-04): *more parts known, proven by use, fewer requests measured*. "Proven by use": the `built` digest is written and read by nothing (store verifier M3: `grep '\["digest"\]\|\.get("digest")' scripts/*.py` → nothing); no change adds a reader; nothing in any project has touched hardware (the bin's CLAUDE.md: "Nothing has touched hardware"); the only hardware-facing change is fw C3 (a flash step) and the PO may choose its page variant. "Fewer requests measured": `--tally` exits 2 outside a Claude Code session (K21) and no change makes the line reachable to a person typing. "More parts known": nmv C5 fixes the skeleton; the 91 silent entries are a data pass nobody has scheduled (nmv C4 counts them). | E for the pointers; H the conclusion (mine) | #17 body; `store-levels-and-holds.verify.md` M3; catalogue K21, K66; `firmware-and-bench.md` RC-2/C3; `needs-matching-vocabulary.md` C4 | that the list fixes what agents hit, not what the PO defined as the goal — the pre-mortem's first cause (§2) |
| RISKS-4 | Every one of the 74 rows was seen by an agent (44) or reasoned from code (28), 2 by the PO and an agent, 0 by a person typing alone. A proposal that fixes 56 things agents met and then measures them with agents cannot say whether a hobbyist is better off. R2.6 (a stranger's run) was merged into P100 and keeps no item of its own. | E | `catalogue.md:157` (the observer count); `brief.md` ★C9 and its caveat; `council/refuter.md` ★C9 | the measurement limit; a stranger run is the only test of the primary persona (slice 5) |
| RISKS-5 | The safety net the refactoring would lean on is, at every push, an anchor check: `check_commit.py` runs the suite and `mutate.py --anchors` (the `find` string occurs exactly once) — never a mutation. The full sweep is owed "when an epic is done" and the last DATED one I found is the sprint-4 close audit of 2026-09-29: 16 tables, 74 mutations, all caught. Today there are 115 tables and 1,268 mutations (my count, `json.load` over `tests/mutations/*.json`, 2026-10-10); `parts.py` is 2,214 lines (K64). Whether an undated sweep ran since is —. | E | `tools/check_commit.py:143` (`"--anchors"`); `tools/mutate.py` docstring at `anchors()` ("Anchors take a second to check; the suite takes minutes per table, so this is what runs at every commit and the full run is what runs per item and when an epic is done"); `scrum/README.md:244`; `docs/observations/INDEX.md:159` (C19); my count | that "a mutation row pins it" — said in at least ten of the 56 change blocks — is a claim about tables nobody has run whole in eleven days; not that mutations would escape |
| RISKS-6 | K53 makes RISKS-5 worse: `mutate.py` scores a mutation CAUGHT whenever the suite is not green — a mutated file that no longer imports counts as caught — so a sweep's "caught" number is an upper bound on tests that notice a behaviour change. The fw diagnosis's C4 proof leans on this tool; the fw refuter says fix K53 first. | E | `tools/mutate.py:88-89` (`return result.returncode == 0 and "\nOK" in verdict`), `:165-181`; catalogue K53; `firmware-and-bench.verify.md` "The changes, judged", C4 | the size of the over-count is —; the direction is certain |
| RISKS-7 | Twenty-three of the 56 changes touch `parts.py` or `needs.py` (store C1, C4, C6, C8, C9, C10, C11, C13; all nine nmv changes; chain C4, C5, C6, C7; board C8; docs Change 4 — my count of each block's named files), the two files the 2026-09-30 architecture council said NOT to refactor because they carried 72 of 132 anchors then and "a silent re-anchor failure there costs the mutation regime's whole value while the suite still reads green". The share today is — (not recounted). | E the doc and the blocks; H the count (mine) | `docs/2026-09-30-refactoring-architecture.md`, "Do not refactor"; the six diagnoses' §3 | that the refactoring runs where the regime is weakest; with RISKS-5, that a dated full sweep before the first commit and after the last is the cheapest insurance |
| RISKS-8 | About 23 of the 56 changes carry a decision the diagnoses or their refuters hand to the PO before the change is safe (M2 holds derived or stored; MC-1 the meaning of an empty rule list; MC-3 `pin_order_proof` owed or broken; the real-store guard's shape; the privacy tuple; "proven in one project" for shelving; a count on a need; whether a board-served need is picked; the XIAO's footprint route; chain C1a vs MC-6; cog vs own recorder; a failing or a reporting docs check; the flash script vs a page …). Built to one reading, three already break something: nmv C2's pair rule refuses plant-alarm's `needs.json` on every read (its `battery` is `mark: have` with no pick); store C5's "never reuse a listed name" strands a MOVED project's holds until the id lands; store C11 shelves irrigation's four placeholder-footprint records for every project. | E the three breaks (the refuters' runs, re-read); H the count (mine) | `needs-matching-vocabulary.verify.md` C2 and "What breaks"; `store-levels-and-holds.verify.md` C5, C11; plant-alarm `.spark/needs.json` (my read) | that decisions, not code, are the critical path for about a third of the list; §4 lists them |
| RISKS-9 | The S3's hold is a decision the PO has made three times, and the diagnoses treat it as a mechanism: §11 "the bin's S3 and LiPo, reserved twice" (D 2026-10-04); his 2026-10-07 answer kept the S3 with the bin (store design §8 L, amended 2026-10-08); D7 (2026-10-09) declined releasing it for the rounds. Store C6 (a `--release` operation) changes the COST of releasing from a hand-written file to one command; it does not change whether the refusal stands on his store. | D the PO ×3; E the pointers | `docs/2026-10-04-store-design.md:548`, `:499-501`; `brief.md:84` (D7); catalogue K3 | that round A on the S3 waits on him, not on K3; a C6 shipped before his decision closes K3 as filed and leaves the walk where it is |
| RISKS-10 | The holds model is undecided between two coherent designs (store verifier M2: derive every project's holds from the listed projects' `needs.json` on read and delete `used_in`; or keep `used_in` and add release + an audit of disagreements), and three changes (store C5's hold inheritance, C6 whole, the `--audit` hold lines) are specified for the stored design only; under "derive", `--release` has no target and a vanished folder holds nothing by itself. | E | `store-levels-and-holds.verify.md` M2; `store-levels-and-holds.md` C5, C6 | that C5/C6 wait on one decision; testability favours derive, the PO's wish to say "the bin keeps this one" without touching the bin's design favours stored (the verifier's reading, H) |
| RISKS-11 | W1 ("a check that could not look must never read as a check that passed") has two deliberate readings of an EMPTY rule list that contradict (chain verifier MC-1): init writes "empty means the records declare none", `compare_design` reads "comparing nothing is not agreement" and answers could-not-run. A design whose records declare no `direction: "in"` pin and whose I²C parts carry their own pull-ups is exit 2 on `rules-vs-netlist` for ever; chain C1a and C1b both leave it so. No current project meets it (irrigation has four entries; the bin's list is hand-written; plant-alarm has no rules file) — the first sensor-only board will. | E | `chain-and-checks.verify.md` MC-1 (`init_project.py:168-172` vs `compare_design.py:250-259`) | that the first "simple" project after these fixes meets a permanent exit 2 whatever C1 does; a decision (§4), not a fix |
| RISKS-12 | Every change to spark's LIBRARY board file reaches the bin's `make check` the day it merges. The bin has no board file of its own (`boards/` holds `active.json` only, E `ls`) and its Makefile resolves the library S3 file through spark: `boards.py --path/--id/--paths/--get` (lines 49-53), `--resolve` (96), `--validate --for-fab` (182), `check_vendor_pins.py $(BOARD_FILES) --offline` (220) and live (223), `check_physics.py … --rules .spark/rules.json` (228), `boards.py --validate` (232). Board C1, C3, C9, C11, C12 add validate rules; board C7 moves the live cache the `--offline` run then has to find; chain C1b must keep reading the bin's hand-written rules (`must_not_float` MotorDriver BIA/BIB, `i2c_buses` SDA/SCL, E my read). | E | the bin's `Makefile` (lines quoted); `board-records.verify.md` "What breaks" | green only if the library file changes in the SAME commit as the rule (C3's removals, C11's `TX`/`RX`); the bin's own footprint (`tools/generate-firebeetle-footprint.py`) and its hand rules are untouched |
| RISKS-13 | Three current projects break under specific changes AS WRITTEN; each has a named repair in its verify file. plant-alarm: nmv C2's pair rule (RISKS-8); any rules seed (chain C1a, C1b, `/spark:init`) lists its four amplifier inputs `BCLK/LRC/DIN/SD` — wired straight to MCU pins in its `board.tsx:34-37` — and B13 fails all four (MC-5); fw C1(c)'s `not_on_simulator` role would label its only ADC pins `A0`–`A2` falsely (0 of its 11 GPIOs are absent on Wokwi's XIAO; the labels differ); fw C4's fake refuses GPIO15, its LED, if "has" is read from `pins` alone. irrigation: nmv C8 refuses `--requirements` until the rename (intended; M6 first); store C11 shelves its seven records, four placeholders; chain C8 records no `built` while its `board.tsx` differs from the regeneration (13 diff lines); board C2/C3 change the regenerated footprint and its committed `FireBeetle2Esp32S3.tsx` (imported at `board.tsx:1`) drifts with no message — K20's shape one file over. The bin: RISKS-12. | E | the three verify files' "What breaks"; my reads of plant-alarm `board.tsx:28-40`, `.spark/needs.json`, irrigation `board.tsx:1`, the bin's `Makefile` | the changes as written; the repairs are in §2 |
| RISKS-14 | The real-store guard (store C2, P164 #101) as drafted — refuse a write when the project is under the temp root — would have caught the one recorded incident only because the draft names `/tmp` and its macOS alias explicitly: the twelve projects pointed at `scratchpad/refuter/proj7/...`, an agent's Claude scratchpad, which lives under the system's `/tmp` tree (`<scratch>`), not under `~`; Python's `tempfile.gettempdir()` on this Mac with `TMPDIR` unset is `/tmp` (`realpath` → `/private/tmp`), and with an agent's `TMPDIR` set it is that agent's folder, not the scratchpad root. A scratch COPY of a real project under `~/Development` (the P100 refuter's `irr`) passes any temp-root rule. | E | `.superpowers/discovery-inputs/2026-10-08/council-p97/ai-matching-refuter.md:12` ("all pointing at `scratchpad/refuter/proj7/...`"); my run `env -u TMPDIR python3 -c 'import tempfile,os; …'` → `/tmp`, `/private/tmp`; `store-levels-and-holds.verify.md` C2 | that the temp-root rule covers the incident on record and not the copy-under-home class; the flag (`SPARK_STORE=real`, #101's first option) is the only version that covers both — the PO's call, as #101 says |
| RISKS-15 | M1 — `SPARK_HOME=""` (set but empty, the exact shape of "an `export` that did not survive to a later tool call") falls through to the DEFAULT home with no sign, and store C1 as written ("set and `is_dir()` false") never sees it. Two lines. | E | `store-levels-and-holds.verify.md` M1 (its run: `SPARK_HOME="" HOME=<scratch>/home python3 -c 'import store; print(store.home())'` → `<scratch>/home/.local/share/spark`); `scripts/store.py:48` (`if os.environ.get("SPARK_HOME"):`) | that C1 without M1 leaves the recorded incident's mechanism open |
| RISKS-16 | Three catalogue rows rest on data the refuters found absent, the person's own, or one project's: K10's severity clause ("the PO's shop labels are Czech") — 0 Czech labels and 0 `entry-N` keys in the 110-entry drawer; K45's four `must_not_float` entries were typed by irrigation's author on 2026-09-29 (`c6c583e`), a day before seeding existed, and `merged` rewrites the `//` note that now claims derivation (MC-2); K40 is one project's file name, ended by one `git mv` (M6). And K22's "joins 3V3 to the pad printed RX" is a reading of port hints: in tsci 0.0.2621 each trace reached its own hole; what stands is a merged netlist every check reads and a converter refusal, not a copper short. Ranking by mechanism alone sends code where data, a rename or a decision would do, and ranks one row by a harm not observed. | E | `store-levels-and-holds.verify.md` RC-1 (4); `chain-and-checks.verify.md` RC-8, MC-2; `needs-matching-vocabulary.verify.md` M6; `board-records.md` RC-2 "what this build did NOT show" and `board-records.verify.md` RC-2 | that the council's rank must carry a "data or decision first" column per row; not that the mechanisms are wrong — each still exists |
| RISKS-17 | On the PO's sync question: SQLite's own page says locking "is especially true [unreliable] of network filesystems and NFS in particular" (§2.1) and that a background copy of the database "while it is in the middle of a transaction … might be corrupt" (§1.2); it says nothing about cloud-synced folders. Git as the store's transport needs `inside_git` (`store.py:129-135`) and the private-target refusal (`:211-214`) rewritten, as the store diagnosis says. The sync-friendly half spark already has is per-entry files plus digests (`sources/<sha256>/`, `based_on.digest`), which store C7 (conflict copies named) and the verifier's "content-addressed files with a manifest" extend. | E the page and the lines; H the fit (the store refuter's and mine) | sqlite.org/howtocorrupt.html (fetched 2026-10-10; page dated 2026-04-13), §2.1, §1.2; `scripts/store.py`; `store-levels-and-holds.md` §3 "An existing mechanism" | that a single database file is the wrong shape for a folder the PO may sync; nothing about which service or whether he will |
| RISKS-18 | Capacity: 56 changes against limits of 2 per working stage, Ready 5, at most 4 cards in flight across both boards; today 0 cards in Ready, Build or Review; 17 in Done on a board that started 2026-10-05 (how many of the 17 closed in those five days is —). At one card per change the list is weeks of Ready/Build churn; grouped by area, six L items (store C11, board C8, chain C1b, fw C3, fw C4, docs Change 3) are stories whose spec goes through Design (limit 2) first. | E the limits and the board; H the arithmetic's reading | `scrum/README.md:7`, `:48`, `:103-109`; my `gh project item-list` 2026-10-10 | that the order decides what lands this month; the ten in §2 are my proposal for it |
| RISKS-19 | The catalogue's own pointers go stale at the first merge: 74 rows and 56 blocks cite `a8aa34d` line numbers; nothing ties a fix to its K id. After ten merges nobody can tell a fixed row from an open one — the P100 PO assistant's pre-mortem cause 7, now for P158. | H | `catalogue.md` header; `council/po-assistant.md` pre-mortem 7 | a process risk; the remedy is a column (K id, test name, commit) on each card and in the catalogue, not code |
| RISKS-20 | All five listed project folders exist today (irrigation, smartbin-local, rc-car, spark-quickstart — git repositories; plant-alarm — not one), so store C5's "a vanished folder's name is not reused" strands nothing now; its regression case (a moved folder) is a future hobbyist's, and the id half of C5 is what makes it safe. rc-car is in `projects.json` and no diagnosis names it: K13 (its `tactile-button` copy behind spark's) and its `car.requirements.json` (K40's shape again) follow it into store C11's audit lines and nmv C8's refusal. | E | my read of `~/.local/share/spark/projects.json` and `os.path.isdir` per folder (a read); `ls ~/Development/rc-car`; catalogue K13 | that two of five listed projects (rc-car, irrigation) carry the K40 file-name shape; a third project the changes must be checked against |

## 2. The proposed changes, judged from this lens

For each change: **keep** · **change** (how) · **drop** (why) · what it depends on. Mechanism-or-symptom and the named tests
are the refuters' work; here each is read for the risk it carries and the assumption it rests on. "Missing" names a change
nobody proposed. The ordering of the ten follows.

### store-levels-and-holds (13)

- **C1 · a missing `SPARK_HOME` is refused; every answer names its store** — **keep**, and **change**: add M1 (RISKS-15); order
  the check with the git refusal (two existing tests point `SPARK_HOME` into a repository folder that does not exist yet and
  assert the privacy sentence — `store-levels-and-holds.verify.md` C1 (b)). The `"store"` envelope field is the cheapest
  guard against every later experiment being run on the wrong store (F5's class). Depends on: nothing.
- **C2 · the real store is written only on purpose** — **change**: present both mechanisms to the PO with RISKS-14: the
  temp-root rule covers the recorded incident only by naming `/private/tmp`; the flag covers the copy-under-home class too.
  Ship after C1 so the refusal names the store it protected. Depends on: D the PO (#101).
- **C3 · one lock beside the data; a writer with no lock refuses** — **keep** the lock move and `init_project`'s `locked()`
  (S, closes K5 and K7); **change**: the `_HELD` check inside `write_json`/`copy_folder`/`append_event` meets 33 direct calls in
  the suite (`tests/test_store.py` 32, `tests/test_drawer.py` 1 — E my grep agrees with the verifier) — each needs the
  wrapper, or a suite exemption, which is a second guard of K2's kind. The 12-row mutation table (one per writing
  operation) is the right pin for K6 and costs nothing; do it first, the writer check after the wrappers. C1 before C3
  (`home()/.lock` needs the home to exist). Depends on: C1.
- **C4 · writes land all or none** — **drop as written** (L): staging `history.jsonl` as `.part` + rename rewrites the whole
  history on every pick and removes the append-only wall the diagnosis itself lists to keep; `needs.json` lives in the
  project, possibly another file system. **Take** the verifier's S alternative: keep the sequence, record each step as it
  lands, say `written before the stop: … — the rest was not; the same command, retried, finishes it`; move `add_project`
  after `drawer.apply` so a pick that cannot write the drawer lists no project (K9); compute `shelvable` before `apply`.
- **C5 · a project is its folder** — **keep** the `samefile` half (with the fallback when the LISTED side is gone);
  **change**: the "never reuse a listed name" half only together with the id in `.spark/project.json` — alone it turns a
  moved project into `name-2` with no holds (RISKS-8). Depends on: the id (M), and M2 for what the id carries.
- **C6 · holds listed and released** — **change**: decide M2 first (RISKS-10); under "stored", add the key column to
  `--drawer` and the operations, and put the release command in the problem's SENTENCE, because `_say` drops `fix`
  whenever an answer has lines (K56) — else the person still sees only `held by smartbin-local`. In a shared store (P178) a
  release by another project's agent is a permission question; say so on the card. Depends on: D the PO (M2), RISKS-9.
- **C7 · reads refuse what writes refuse; labels in one form** — **keep** (S; 0 non-plain stems and 0 affected hand labels
  today, E the verifier). The sync-friendly half of RISKS-17.
- **C8 · one reader; no store problem is a traceback** — **keep**; **change**: catch `UnicodeDecodeError` and `StoreProblem`
  by name, not every `ValueError` — a traceback is "where" for the agent reading it (the PO's criterion); add `store.py:145`
  to the reader list (the write side has the same assumption).
- **C9 · `--fetch` names what it could not keep** — **keep**. The agent pages must say what exit 1 means there.
- **C10 · one layer, one count** — **keep**.
- **C11 · a record has one home that is the store** — **split**: promote-to-shelf with `based_on` (keep); delete the
  project→library branch of `promote` (a removal; the library changes by pull request, `parts.py:1865` says so already);
  the vendor-header cache under the store with the folder named (keep, and say which writer — the store's door or
  `write_text` — and the fallback order the bin's `--offline` depends on, RISKS-12); the six literal paths and the
  `datasheet-reader`'s `Write` (keep, after showing `--fact-set` can set every field the agent fills — —). **Defer**
  shelving the project's own records until "proven in one project" has a definition (it shelves four placeholder footprints
  for every project, RISKS-8/13); the `built` line read by M3's reader is the obvious one. Depends on: M3, the rename M6 for
  irrigation (its `--requirements` reads `requirements.json`, which it does not have).
- **C12 · spec and code agree on privacy** — **change**: not the spec shrink (it un-says §5.8, which lists document bytes
  twice); add `sources` to `PRIVATE`, say in §5.1 that the 0700 home is the wall; `catalog` and `downloads` are the PO's
  call against P178's shared-store direction. Keep the no-`fcntl` line and the fetch cap.
- **C13 · the `built` line vouches for what the chain reads** — **drop the digest half** until a reader exists (M3: nothing
  compares a digest; `--tally` tests event and project only) — a wider digest changes no answer and its test proves a write
  nobody reads (RISKS-14's class). **Keep** `note_built` returning a sentence and `check_spine` printing it.
- **Missing**: M1 (two lines, RISKS-15); M4 — one door: a grep-shaped test that no script writes under `home()` except
  through `store.write_* / copy_folder / append_event / keep` (twelve call sites, E the verifier), which is what C3's lock
  check cannot see; M2 as a decision card; a dated full mutation sweep (`tools/mutate.py tests/mutations/*.json`, its time
  printed) BEFORE the first store commit and after the last (RISKS-5).

### board-records (12)

- **C1 · a bare-number label is refused** — **keep**; **change**: cover `pins` keys too (M6: `SELECTOR_SAFE` accepts `"17"`)
  and both tscircuit regexes (`/^\d+$/`, `/^pin(\d+)$/i`). Deterministic, no toolchain, S — on the route the PO named first
  (D8). Say on the card that no copper short was observed (RISKS-16).
- **C2 · `pad_aliases` reaches the footprint** — **keep** the mechanism (shown by the alias probe); **change**: the validator
  rule as written refuses the S3's own file (`A4` IS a `pins` key) → "a target that is also a key must map to the same
  GPIO"; print tscircuit's own `Could not find port for selector` from `circuit.json` before building a reconstructed
  sentence (the board verifier's M1 — a reorder in `check_spine.py:430-441`, shared with the chain area); say in the
  output that irrigation's committed footprint now differs from the regenerated one (RISKS-13).
- **C3 · the `physical` schema written where it is enforced; unread keys refused** — **keep**; **change**: the Known list
  (M3: `thickness_mm` and `header.pad_mm` are unread too); the removals from the library S3 file land in the SAME commit as
  the rule or the bin's `make check` goes red (RISKS-12); mounting holes are a separate decision (an add that puts four
  drills under `check_footprints.check_through_hole_drills`, untested).
- **C4 · `--json` on every path** — **keep** the could-not-run variant (a removal). Its test is the second case of
  `tests/test_json_contracts.py:142`, not a new file.
- **C5 · the drill sentence** — **keep**.
- **C6 · one comment-key rule** — **keep**; the hazard (a `//`-prefixed `pins` key vanishes silently) is explicit enough.
- **C7 · the vendor-header cache lives in the store** — **keep**; **change**: name the writer and the fallback order
  (store first, then the plugin's two tracked headers, read-only); the bin's `Makefile:220` `--offline` run must still find
  a header after a live run (RISKS-12).
- **C8 · a board record from a drawer entry** — **keep** as the PO's own first fix (D8, 2026-10-09: *"create one
  automatically based on the DFRobot orders and researches all it needs"*), L → Design first; **change**: the per-chip
  table is a third statement of chip facts beside `soc_caps.h` and the board files — a test that it agrees with both
  shipped boards or it drifts; the pick-side change (no `reused` for a board with no file) alters a by-design behaviour
  → the PO; the `boards.txt` variant step is E once (3 of his 4 unfiled SKUs named; the Beetle ESP32 DFR0575 —). This is
  the change that unblocks round A's board after RISKS-2's data pass.
- **C9 · every stop from one rule; `--for-fab` requires geometry** — **keep**; **change**: both spellings of the stop
  sentence (M5: `parts.py:1920` and `needs.py:511-512`); the XIAO's geometry is NOT `physical.header` (that draws through-hole
  rows for a castellated SMD module) but a `footprint_source` naming a converted KiCad footprint — the diagnosis's own
  footnote should be the proposal.
- **C10 · `function` on boards, validated** — **keep**; **change**: say both slots exist (the drawer's `function` is
  documented and the matcher already sums it, M4) and which fact goes where: a fact about the SKU → the record with a
  source; a fact about this piece → the drawer. RISKS-2 is the drawer slot at work.
- **C11 · `pins` against the stand-in's registry** — **keep**; **change**: a copy of the registry under `data/` with its
  version, not a read of `node_modules`; the rule covers silkscreen-named boards too (M7: Wokwi's XIAO has `D0`–`D10`, the
  record's keys are `SDA`, `SCL`, …); the override that already works (`wokwi_power_pins`, merged last, honours `null`
  and a rename — E the fw refuter's run) gets a documented name and a validator before any new role (fw C1).
- **C12 · remove `footprint_module`** — **keep**, only with C9; the touch points are under-counted (four test fixtures,
  `docs/guide/agents.md:456`, `boards/README.md:71`, the bin's converter copy — no break).
- **Missing**: the board verifier's M1 (print the build's own errors before the island — a reorder); M2 (two false
  sentences — the S3 record's `//wokwi_part_type` and `boards/README.md:97` — amended, not deleted).

### needs-matching-vocabulary (9)

- **C1 · one matcher, hits not AND, says which words missed** — **change**: tokens, not substrings (M5: under an OR the
  one-letter word in "12 V inlet" hits every record holding a `v`); the simpler first step is the two sentences (which
  word missed; the drawer and `function` are not searched) with the AND kept — a tenth of the change and it removes K33's
  misdirection; the full change rewrites a documented behaviour (`parts.py:1334`'s docstring, `tests/test_parts.py:791-797`),
  two recorded blocks (`journey.md:524`, `:533` — K68's gate) and five pages that send agents to `--need`.
- **C2 · the pick says what the match knew; `--needs` shows the pick** — **keep** the note (with the "other VERB" case,
  M1: a motor driver picked for a temperature need passes today) and the listing line; **drop the pair rule** (RISKS-8,
  RISKS-13): it refuses the documented M-before-C order and the gap → research → pick path, and refuses plant-alarm's file
  on read. If the PO wants fit recorded, that is a new mark or a `fit` field — a decision (M4).
- **C3 · drop a need, clear a pick** — **keep**; **change**: say that the history's `reused` events keep the old need id
  (or the tally and the history disagree); distinguish a mistyped empty id from a clearing; a tombstone that stays in the
  file (`{"id","dropped": true}`) travels through sync and merge better than a vanished object — the PO's sync question
  again, not this task's decision.
- **C4 · say how many entries no need can reach** — **keep** (S; the right FIRST step, because the fix is data —
  RISKS-2); **change**: add the drawer.md step (M8: after an import, the agent proposes `function` from the label and the
  person says yes) or the count has no path to zero but improvisation.
- **C5 · the skeleton carries every chain fact; research ends with `--audit`** — **keep**; it is the one test in the six
  diagnoses that catches the NEXT drift; **change**: the diagnosability line — `--validate` is silent on a null
  `simulation` and `function` by design (M3), so `--audit` is the alarm, said so.
- **C6 · the cut lists its words and ids** — **keep**; cap the ids per word (the 91 entries, once they carry functions,
  can share one word).
- **C7 · a need says how many the design uses** — **defer**: a PO decision first (the diagnosis says so); M7 shows one
  need per instance already yields `Valve1…Valve4`, reserves four and writes four `reused` events — one sentence in
  `idea.md` before a schema change.
- **C8 · refuse when a differently named requirements file sits in the project** — **keep**; do M6 first (one `git mv` in
  irrigation; rc-car has the same shape, RISKS-20); extend to "both exist and differ".
- **C9 · the store's words shown where a need is written** — **keep**; add M2's "one word more" case (the commonest
  cause of `[other words]` on the copy).
- **Missing**: M4 (a mark or field for "fits loosely" — vocabulary before a check); M8 (the asked-once step after the
  import); the data pass itself as a card with the PO (his yes per entry — §6.4.5), measured by RISKS-2's command before
  and after.

### chain-and-checks (9)

- **C1 · the chain re-seeds the derived half of `rules.json`** — **change**: not C1a as written (a CHECK becomes a writer
  of another check's input; `rules.json` gets two authors; `--keep` on plant-alarm would create a rules file nobody asked
  for and B13 would fail four pins on the next `check_all` — RISKS-13); take MC-6 (seed at `parts.py --requirements`,
  already a writer with the picks and records in hand); C1b as the direction, with MC-1 (RISKS-11) decided first or it
  moves the fault from "stale" to "permanently unexercised". `needs.requirements` reads `requirements.json` while
  `init_project.design_in` globs `*requirements.json` — K40/M6 first or irrigation gets a second file.
- **C2 · a declared signal is reported, not refused; a stray stderr line is could-not-run** — **keep**; **change**: a
  shared `NOTE_PREFIX` the two files import (today all five notes start `note:`, so the split is a string contract between
  two files); keep the four circuit-gap notes as PROBLEMS because they are circuit gaps, not because `--requirements`
  pre-warned (it pre-warns three of four); say that a board with a dangling assigned pin then records `built`. Irrigation's
  `check_spine` exits 0 for the first time — a recorded expectation in its DIARY changes; fine.
- **C3 · a record says an input holds its own level** — **change**: name the key by what the check does with it (why
  floating is harmless: a current load, a module-side pull, a pin gated by another) — MC-5 shows two more cases in spark's
  own amplifier record (`SD` pulled up on the module; three I²S data inputs); order before any seed (irrigation's four
  entries come back otherwise); a per-entry note survives `--force`, a template note does not (MC-2).
- **C4 · one table for what each owed fact does to the chain** — **keep** the shape and its test (the one that would have
  caught the diagnosis's own wrong row); **change**: `pin_order_proof` → `("parts", "stops — the loader refuses the record")`
  (E the verifier's run); decide MC-3 first — today one record gets two verdicts from one module (`--audit` "owes",
  `--need` "builds with it", the chain `[????] parts … does not meet the part contract`); the `_about` regex
  (`parts.py:113-117`) goes with the table.
- **C5 · one reader, one namer** — **keep**; fold `needs._name_after` (the same transform on a need id, untested for
  agreement). Nothing breaks.
- **C6 · the board changes in one place** — **keep** the recommended variant now; note that `boards/README.md:21` and the
  bin's `CLAUDE.md` both say `active.json` is "THE one place" — the alternative (fall back to the requirements file) is the
  smaller system later and safe for the bin today (it keeps `active.json`).
- **C7 · five small contract fixes** — **keep**; K52 also stops exiting 1 ("problems") for a selection question (MC-8);
  K63 prefer the refuse variant and reorder `idea.md:13-15` (no half-state).
- **C8 · `--keep` builds the kept `board.tsx`** — **keep** (D the PO, 2026-10-05, #44); **change**: build IN PLACE (MC-4: a
  hand-edited `board.tsx` imports siblings the work folder lacks — the bin's imports four); say to the PO that irrigation
  records no `built` until its file is regenerated; `keep_into` leaves ANY `.tsx` alone, the generated footprint included,
  so the kept board imports a stale footprint after a board-definition change — same class, one file over.
- **C9 · the unserved note in every outcome** — **keep** (chore).
- **Missing**: MC-1 as a decision card (RISKS-11); MC-2 (a `//` note that states the rule, never the origin — small);
  MC-6 as the first step of C1.

### firmware-and-bench (6)

- **C1 · the stand-in's pins as a board fact the chain reads first** — **change**: the diagnosis's counts were refuted (0
  of the S3's 24 and 0 of the XIAO's 11 GPIOs are absent on their stand-ins; two S3 labels and nine XIAO labels have no pin
  of that NAME), so (c)'s `not_on_simulator` role would be false for both library boards and spend the XIAO's only ADC
  pins last (RISKS-13); (a)+(b) need the converter bundle rebuilt (its `board.ts` reads the board at import; `--help`
  fails without one — E the refuter) and make `boards.py --validate` depend on node for a note; (d) pins a second
  substring. **Take** M1 first: the emitter picks a name the part knows (`mapping.ts:96`, the oracle is in hand); give the
  existing override (`wokwi_power_pins`, which already honours `TX: "TX"` and `null` — E) a documented name and a
  validator (board C11); a spend-last role only for a GPIO with no name at all (a user's generic devkit — round 0's case).
  The classifier's mechanism is the converter's missing `--json` (M8), not one more pinned string.
- **C2 · `flash_image.py` refuses an interpreter built for another chip** — **keep** the 16-byte read (9 = ESP32-S3 is now
  E from esptool 3.3's source; 13 = ESP32-C6 stays H — that esptool has no final C6 class, M5); **change**: the
  `--project` default cannot resolve irrigation's board (it has no `.spark/board.json`) → the refuter's placement in
  `check_spine`'s simulation stage, where the resolved board and `--firmware` already meet, plus an optional `--chip`.
- **C3 · the step from the image to the board** — **keep** as the smallest piece under P79 (the PO sets P79's shape); the
  page variant first (S); the script needs a minimum esptool version (3.3 cannot flash a C6); two bench facts (the write
  offset, the 4 MB image on a 16 MB N16R8) are — until the board is on the desk. This is the only change that touches
  RISKS-3's "proven by use".
- **C4 · a sixth check: the firmware against the pin map it imports** — **change**: name the cut (D the PO, 2026-09-29,
  `066c4af`: *"no AI bloat, nothing kept that nothing uses"*) and why it returns (a project has `firmware/pins.py` since P36;
  the cut check looked for `config.py`); say what kind of check it is — a use-against-map coverage observation, not the
  bin's three-statement triangle (with `import pins` there are no literals, M3); "has" = `pins` ∪ `pin_roles[*].gpio` or it
  refuses the XIAO's LED; fix K53 before the mutation proof; irrigation's `check_all` gains a second FAIL and the recorded
  outputs change (K68). M7 (the record's deep-sleep facts into `pins.py`'s header) is the cheaper first consumer of RC-4's
  facts and inside the 2026-10-01 boundary.
- **C5 · a scenario measured against the pin map** — **keep** as a NOTE (irrigation: 1 of 12; as a problem its simulation
  stage flips); add that an `expect-pin` must name a pin the STAND-IN knows.
- **C6 · the documents follow the code** — **change**: amend the two true-in-part sentences, do not delete them (M9); the
  "retired phrase" check does not exist in spark (`tools/check_docs.py` has no such list — it is the bin's
  `check-current-docs.py`) → a new S check, proposed as one.
- **Missing**: M4 (the role→tool table has no chip parameter — the mechanism under C2); M6 (the `deep_sleep` block has no
  schema, so absence and a typo look alike — any consumer must first trust the shape); M7.

### docs-and-recorded-outputs (7)

- **Change 1 · the gate counts outputs behind the shipped version** — **keep as a report line**; **drop the failing
  variant**: keyed on the version, a patch that changed no output (0.8.1 changed a name's casing) marks 44 blocks stale at
  once, and `developing.md:103` is a dated record by its own page (RISKS-14's class).
- **Change 2 · the README block ends where a shell can finish it; the gate runs it** — **keep**; **change**: keep the
  needs file in the project (P172's leak count), give the block a recorded output and show the tally's honest refusal as
  a recorded block (M8); four more subprocesses per gate run (the docs gate took 5.5 s for 7 files, E the diagnosis).
- **Change 3 · one recorder at each release; drift fails a check** — **change**: promote or delete the recorder that
  exists first (M1: `.superpowers/…/record.sh` 102 lines, `record-journey.sh` 176, 75 recorded outputs, all gitignored and
  path-bound); classify the 42 blocks (8 have no `sh` command above them; the live-board and `gh`-state blocks are not
  functions of plugin + store — M2, M3); hook `--check` into `check_commit.py` on a commit that changes `plugin.json`'s
  version, because "the release gate" does not exist (M4) — else it is DoD prose again, the failure being fixed. cog's
  `--check`/`--diff`/comment markers are H (the diagnosis's reading; 126 marker lines on pages agents read raw).
- **Change 4 · the own-board route recorded; three facts written where the steps are** — **keep**; cut the half already
  on the page (`how-it-works.md:172` names `vendor.arduino_variant`); `check_vendor_pins.py` stays recorded, not gate-run
  (network; its live run writes into the plugin's cache until board C7); the `--fetch` board refusal through the
  argument-refusal path (exit 2).
- **Change 5 · the gate reads the pages agents follow** — **keep**; **change**: name pages by relative path (M7) or three
  `SKILL.md`s and two `README.md`s are one name — a failure that no longer says where; do not import `routes()`'s sibling
  Makefiles into `doc_files`.
- **Change 6 · density and long lines** — **drop** the measure as a report line (noise nobody reads; README's long lines are
  table rows — 8 of 10, E the verifier); the PO decides whether "about 120" is a rule; the edits merge with Change 2 into
  one card for `README.md:111-158`.
- **Change 7 · one sentence on what spark has built** — **keep**; say "per store" (8 library records; 13 on his copy).
- **Missing**: M4 (a release gate — the one mechanism every docs change assumes); M6 (`failed_examples` isolates
  `SPARK_HOME` only; `HOME`, `TMPDIR`, `PATH` are the developer's — widen the isolation BEFORE widening what is marked
  `runs:`, or a block that reads `~/.claude` runs against the real home).

### The ten that matter most — my order, with the reason for each rank

Ranked by risk removed per unit of cost and by what unblocks the PO's declared next step (P100 round A, RISKS-1), with the
"do no harm" guards first. Decisions are named where a rank waits on one.

1. **The data pass and the decisions, before any code** — `function` on the six ESP SKUs and the owned sensors (SCD41,
   VEML7700, …) through `/spark:drawer` with his yes per entry (nmv C4's data half, M8); `git mv irrigation.requirements.json
   requirements.json` (M6); his decision on the S3's hold (RISKS-9) and on M2 (RISKS-10). Zero code; RISKS-2 shows the
   effect on the copy (2 → 6 boards); it is what blocks round A's matching today, and no change in the list does it.
2. **Store C1 + M1** — a `SPARK_HOME` that names nothing or is empty is refused; every answer names its store. S. Without
   it every later experiment (P100's rounds, the proofs of the other 55 changes) can be run on the wrong store and look
   right (F5, #101). The guard C2 needs this field to be visible, and the PO's choice between the two C2 mechanisms can
   follow.
3. **A dated full mutation sweep, then store C3's lock move + `init` under lock + the 12-row table** — the sweep
   (`tools/mutate.py tests/mutations/*.json`, time printed) before the first store commit, because the gate runs anchors
   only and the last dated sweep is of 2026-09-29 (RISKS-5); then the one-line lock move (K5, K7) and the per-row pins
   (K6). The `_HELD` writer check waits for the 33 wrappers.
4. **Board C1 + M6** — a bare-number label or key is refused at `--validate`. S, deterministic, no toolchain, on the
   "bring your own board" route the PO named first (D8); the one silent-fault class on that route with no check at all.
   The library file changes in the same commit (RISKS-12).
5. **Board C8 — the board skeleton from a drawer entry** (with C9's two spellings and C11's `TX`/`RX` data) — the PO's own
   "first fix" (D8), L, Design first. After rank 1, this is the wall round A meets (RISKS-2: the pick passes, the
   requirements refuse). Its per-chip table needs the agreement test from day one.
6. **Chain MC-6 as C1's first step, with MC-1 decided** — derive the rules' derived half where the picks already are
   (`--requirements`), so K46's "two checks could not look" after init goes, with no check becoming a writer; the
   decision on an empty rule list (RISKS-11) before it, or the first sensor-only project is exit 2 for ever. Chain C3's
   key before any seed reaches irrigation.
7. **Store C6 — holds listed, a release operation** — after the M2 decision (rank 1). The PO meets this on every second
   project on his one S3; the command goes into the sentence a person sees (K56). Under "derive" this rank becomes
   `--audit`'s disagreement lines instead.
8. **nmv C5 + C4's code half** — the skeleton carries every chain fact and research ends with `--audit`; `--match`
   counts the entries no need can reach. S; the one test that catches the next drift, and the line that tells the
   person the data pass is owed (rank 1's measure).
9. **Chain C5 + the five contract fixes (C7)** — one reader and one namer for the requirements file (three bugs, a
   removal); five S fixes each with its sentence. Pure diagnosability, nothing breaks, no decision needed.
10. **fw C3 (the page variant) + C2's 16-byte read** — the step from the image to the board, as a page with the two
    commands first, the chip refusal where the resolved board and the image meet. Every P100 round's pass line is
    "firmware that runs" and nothing in the documents reaches it (★C6); this is the only change that touches RISKS-3's
    "proven by use", and the cheapest shape of it.

Not in the ten, on purpose: store C4 as written (L; take the S alternative), store C13's digest half, store C12's spec
shrink, nmv C2's pair rule, nmv C7, fw C1(c), docs Change 1 as a failing check, docs Change 6, board C3's mounting holes,
chain C1a — each for the reason in its block above. Store C11 and docs Change 3 are right in direction and wait on a
definition ("proven") and a mechanism (a release gate) respectively.

### Pre-mortem — six months after these changes shipped, spark is no better. Why?

Each is a proposed cause (H unless pointed), with the guard that would have caught it.

1. **The agent was fixed, not the hobbyist.** All 74 rows were agents' observations (RISKS-4); the 56 fixes removed the
   stalls agents met; the first stranger stalled somewhere no agent did, and nobody knows where because no stranger run
   happened (R2.6 has no item). Guard: one stranger run (slice 5) scheduled as a card with a date, before the list is
   called done.
2. **Code shipped, data did not.** The 91 entries stayed silent, the S3 stayed held, the four boards stayed unfiled —
   because none of that is a code change and the board's cards were code changes. RISKS-2 is the counter-example: one
   data write moved more of the journey than any single change in the list. Guard: rank 1 above, as a card with the PO,
   measured by the same `--match` before and after.
3. **"Better" was never measured by the PO's own words.** No reader of `built`, no `ran` event, no tally for a person
   typing (RISKS-3); the count of closed cards rose; #17's three words stayed where they were. Guard: a card whose
   proof is one of the three words observed (a `built` line compared, a tally printed in a terminal, `--match` offering
   an owned part that was silent before).
4. **The L items never reached Build.** Ready 5, Build 2, 56 changes (RISKS-18): the S fixes flowed, the six L items
   (the board skeleton, the shelf's home, the recorder, the flash step, the firmware check, C1b) waited behind them, and
   the two walls round A meets after the data pass (K29, K3) were the L and the decision. Guard: six area cards, each
   with its one L story first in Design.
5. **A decision deferred inside a change was built to one reading.** The pair rule refused plant-alarm's file; the shelf
   offered placeholder footprints to every project; the never-reuse rule stranded a moved project — each reverted after
   a complaint, and after the third revert the PO trusted the list less (RISKS-8). Guard: §4's questions answered on the
   cards before Ready.
6. **The library file broke the bin's `make check`, and the bin pinned spark.** A validate rule merged without the
   library file's change (RISKS-12); the bin's `make check` went red on a Tuesday; the bin set `SPARK=` to an old
   checkout to keep working; spark lost the one real consumer that exercises `boards.py` from outside. Guard: the bin's
   eight `boards.py` invocations as spark tests (the 2026-09-30 doc asked for exactly this: "`boards.py`'s command line is
   a cross-repo contract with zero tests") and the same-commit rule.
7. **The refactor ran where the regime is weakest, with the gate reading green.** Twenty-three changes in `parts.py` and
   `needs.py` (RISKS-7); anchors stayed present while the paths they guarded moved; a full sweep was never run because it
   takes hours and the DoD says "when an epic is done" (RISKS-5); one regression escaped and was found by a person,
   which is the failure mode mutation testing exists to end. Guard: rank 3.
8. **The docs went stale again at 0.9.0** because the recorder was wired to a release gate that does not exist (docs M4),
   and the stale-count check was turned off after its 44 false alarms (RISKS-14). Guard: the check in `check_commit.py` on
   a version change, or none.
9. **Nothing touched hardware.** The flash step stayed a page; the one S3 stayed in the bin's hold; round A's pass line
   "firmware that runs" was replaced by a Wokwi pass, as the third cold test's was (PO-5/PO-6) — so whether spark's pin
   facts were right on a bench is still —. Guard: the PO's decision on the S3 (rank 1) and fw C3 in whatever shape.
10. **Nobody could tell a fixed row from an open one** (RISKS-19): the catalogue cited `a8aa34d` lines, the fixes cited
    card numbers, and the P178 council re-found eleven of the 74. Guard: a column per row — K id, test name, commit — kept
    as fixes land.

## 3. What I could not check, and why

- **The real store** (`~/.local/share/spark`): never run against; `projects.json` was read once for RISKS-20. Every run
  was on the copy at `<scratch>/p158/risks/store`, which my run 4 then WROTE (four drawer entries gained `function`); the
  copy is no longer the real store's image and must not be used as one.
- **The exit codes of my seven runs** were not captured (a zsh `PIPESTATUS` slip printed `[exit ]`); the outputs are
  quoted verbatim and are unambiguous (`set`, `would set`, `refused, so nothing was written`).
- **A full mutation sweep** (RISKS-5): not run — 1,268 mutations at the suite's ~35 s each (the store diagnosis's
  `Ran 1699 tests in 34.627s`) is hours; the near-set shortcut shortens it by an amount —. Whether an undated sweep ran
  since 2026-09-29 is —; my grep covered `docs/observations/INDEX.md`, `scrum/README.md`, `scrum/SPRINT.md` and the git
  log's messages.
- **Today's anchor share in `parts.py`/`needs.py`** (RISKS-7): the 72-of-132 figure is the 2026-09-30 document's; the
  115 tables were not read for their `file` fields.
- **The bin's `make check`**: not run — it would re-resolve `.spark/board.json` inside the bin (a write under
  `~/Development/smartbin-local`, forbidden); its spark lines were read.
- **The counts "23 touch `parts.py`/`needs.py`" and "about 23 carry a decision"**: my reading of the change blocks, not
  a tool's; another reader may count a block differently.
- **How many of the board's 17 Done items closed since 2026-10-05**: the listing gives the status, not the date.
- **Wokwi, hardware, the install path, the conversations**: none run (D4; nothing on a bench; no stranger).
- **cog's `--check`/`--diff` and comment markers**: H from the docs diagnosis's reading; not tried.
- **esptool's C6 chip id**: 13 is H (the fw refuter: esptool 3.3 has only `ESP32C6BETAROM`, id 7).
- **Whether the PO owns a µA-capable meter** (tech lead Q6) and whether the DFR0975 is a post-2219 unit: —, as before.
- **The P178 design**: nothing on disk; #123 and this council's §2 are the only statements.

## 4. Questions for the decider

| question | what it decides |
| --- | --- |
| Do you release the S3 (and the LiPo) from the bin for P100's rounds, run the rounds on a second board you own once it has a record (board C8), or on a scratch copy of the store? | whether round A is blocked by a finding or by your choice (RISKS-9); which of C6 / C8 is first |
| Is a hold DERIVED from each listed project's `needs.json` on read (no `used_in`, no `--release`, a gone folder holds nothing) or STORED and released by an operation (`--release`, `--forget-project`, `--audit` naming disagreements)? | store C5 (the id), C6, the `--audit` lines; testability favours derive, "the bin keeps this one without touching its design" favours stored (M2) |
| The real-store guard: a flag you set once (`SPARK_STORE=real`; everything else refused) or a rule on the project's folder (under the temp root)? The first covers the copy-under-home class; the second only the recorded incident (RISKS-14). | store C2's shape; whether agents' scratch copies under `~/Development` can still reach the real store |
| An EMPTY rule list after the records were looked at: `rules-vs-netlist` answers `ok` with `checked: 0` and the reason, or stays could-not-run (W1's letter)? | chain C1 in either form; whether the first sensor-only board is exit 2 for ever (RISKS-11) |
| A `pin_order` without its proof: an owed fact (buildable, warned, marked — #102's words) or a contract failure (as `validate` says since P81)? | chain C4's table and `--requirements`' policy; whether the catalog's 17 "owed" records can build at all (MC-3) |
| What does "proven in one project" mean before a project's own record goes onto the shelf for every project — a `built` line, a `ran` line, your yes? | store C11's shelving half; whether four placeholder footprints reach every project (RISKS-8) |
| Does the drawer's data pass — `function` on the 91 silent entries, proposed by the agent from each label, written after your yes — happen before the code changes, as a card with you? | rank 1; whether round A's matching can offer what you own (RISKS-2) |
| A need that the board itself serves (WiFi on the S3): picked (reserving nothing), or marked served by the board pick? | board C10's last paragraph; what the build's verdict says about `report` |
| A design quantity (four valves): one need per instance (works today, M7) or a `count` on a need (a schema change)? | nmv C7 — build or drop |
| Is `boards.py`'s command line a contract spark tests (the bin's eight invocations as tests), and does a library board-file rule always land with the library file's change in one commit? | whether board C1/C3/C9/C11/C12 can merge without the bin going red (RISKS-12) |
| Do you want a dated full mutation sweep before the first store/parts commit and after the last, as a card with its time printed? | whether RISKS-5/7 is accepted or closed; a few hours of machine time |
| The docs: a report line or a failing check for recorded outputs behind the version; cog or spark's own recorder; and does `check_commit.py` become the release gate on a `plugin.json` change? | docs Changes 1 and 3; whether "re-record at release" has a mechanism (M4) |
| Is one stranger run (slice 5: a person outside the project, README only, own machine and board, a diary nobody helps with) scheduled as a card with a date, before this list is called done? | whether "better" can be claimed for the primary persona at all (RISKS-4) |
| For the next version's store: a single database file (SQLite) for the small tables, git as transport, or per-entry files with digests and a merge rule (what spark half has)? The first is the wrong shape for a synced folder by SQLite's own page (RISKS-17). | the P178 council's frame; your relayed question of 2026-10-10 |

## 5. Searches

| query or fetch, verbatim | decision served | used or not |
| --- | --- | --- |
| WebFetch `https://www.sqlite.org/howtocorrupt.html` (prompt: quote the passages on network filesystems, backup/sync software, cloud-synced folders) | whether the P178 council should weigh a single SQLite file for a store the PO may sync (his relayed question of 2026-10-10) | used — RISKS-17: §2.1 and §1.2 quoted; no statement about cloud-synced folders on the page |
| no web search | — | — |

Reads that were not searches: `gh project item-list 2 --owner xmejkal --format json`, `gh issue list --state open`,
`gh issue view` ×22 (all read-only, 2026-10-10); the files named in the header; the store copy; the `.superpowers/`
discovery inputs of 2026-10-08 for the #101 incident's folder (RISKS-14).

## Appendix — my runs, in order (sanitised; every spark command on the copy, with the three-word prefix)

```text
cp -R ~/.local/share/spark <scratch>/p158/risks/store                       → 33M (du -sh)
SPARK_HOME=<scratch>/store HOME=<scratch>/home TMPDIR=<scratch>/tmp env | grep SPARK_HOME   → SPARK_HOME=<scratch>/store
1  parts.py --needs-set <scratch>/proj-data needs.json                      → set board: does null → "compute"; what null → "microcontroller"; condition null → "runs MicroPython"
2  parts.py --match <scratch>/proj-data                                     → owned 1 firebeetle2-esp32s3 (library) … free 0 · owned 1 xiao-esp32-c6 (library) … free 0  stops at the footprint stage (P121)
3  parts.py --drawer-set functions.json --dry-run                           → would set dfrobot-dfr1075/-dfr1117/-dfr0994/-dfr0575: function null → [{"does": "compute", "what": "microcontroller"}]
4  parts.py --drawer-set functions.json                                     → set … (the four entries) — THE COPY IS WRITTEN HERE
5  parts.py --match <scratch>/proj-data                                     → owned 2 dfrobot-dfr0575 (drawer) … free 2 · owned 1 dfrobot-dfr0994 … free 1 · owned 2 dfrobot-dfr1075 … free 2 · owned 3 dfrobot-dfr1117 … free 3 · the two library boards as before
6  parts.py --pick <scratch>/proj-data board=dfrobot-dfr1075 --dry-run      → would set dfrobot-dfr1075: used_in null → {"proj-data": 1} · dfrobot-dfr1075: a board needs a board file — a record in boards/ — before spark can build with it · would list proj-data on your projects · would write to your history: 1 reused
7  parts.py --pick <scratch>/proj-data board=firebeetle2-esp32s3 --dry-run  → refused, so nothing was written: firebeetle2-esp32s3 — 1 owned, held by smartbin-local — 1 picked here
env -u TMPDIR python3 -I -c 'import tempfile,os; print(tempfile.gettempdir()); print(os.path.realpath("/tmp"))'   → /tmp · /private/tmp
python3 -I (json.load over tests/mutations/*.json)                          → 115 tables, 1268 mutations
grep -n -- --anchors tools/check_commit.py                                  → :143
gh project item-list 2 --owner xmejkal --format json --limit 200            → total items 101; Idea 82, Done 17, Discovery 2 (P100 #6, P158 #94)
gh issue list --repo xmejkal/spark --state open --limit 200                 → 81
```
