# P158 part 2 — judge 3 of 3

Written 2026-10-10 by judge 3, against spark 0.8.1 at main `5acbe42` (E `git log -1` → `5acbe42 2026-10-10 22:26:37
+0200 Merge pull request #129`). Scores the three approaches in this folder — A1 *the smallest layer*, A2 *the chain as a
build graph*, A3 *data first* — with the maintainer who must change and test the code in mind first, then the whole. The
other two judges scored in parallel; nothing here was coordinated with them. Decides nothing: what only the PO can take
is under *For the PO*.

**Tags.** E a pointer (file:line at `5acbe42`; a command and what it printed; a card), H a claim with its source, D a
decision (who, when), — unknown. "00" is `design/00-system-as-is.md`; "part 1" is `proposal.md`; CH-n, K-n, Q-n are part
1's ids; D-A*n*, QA2-*n*, QA3-*n* are the approaches' own questions.

**What I read.** Whole: 00, A1, A2, A3. Of part 1: the header, §2 (the eight shapes, removals, store levels, exit codes,
seams, recorded documents), §3's priority rule and *How the list becomes cards*, §4, §5, the CH-65 block, and the CH
headings (72 changes, E `grep "^#### "`). Code at the pointers the approaches cite, listed under *Errors found*; the
2026-09-30 note (`docs/2026-09-30-refactoring-architecture.md:55-135`); `scrum/VISION.md:28-40`;
`docs/guide/agents.md:68-73`, `:244-256`; `README.md:82-92`. The bin, read only: `Makefile:10-20`, `:45-56`, `:92-98`,
`:178-235`; `ls -a .spark/`.

**What I ran**, read-only, nothing against any store: two small scripts in `<scratch>` that read `tests/mutations/*.json`
and attribute each `scripts/` row to its enclosing function by `ast` (`python3 -I`, `PYTHONDONTWRITEBYTECODE=1`); greps
and `sed -n` over spark's tree; a count of `parts/*.json` facts; `git check-ignore -v .spark/state.json` in the bin
(printed nothing); `gh issue view 11`, `103`, `124 --repo xmejkal/spark --json …` (read-only). Results are quoted where
used. Nothing was written under `~/Development` but this file.

## Scores

| approach | testable | diagnosable | simple | iterative | modular | free & local | humans & agents | fixes part 1 (addressed / 72) | migration risk (5 = lowest) | total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 · the smallest layer | 4 | 5 | 4 | 5 | 4 | 5 | 5 | 3 (47 / 72) | 4 | **39** |
| A2 · the chain as a build graph | 5 | 4 | 3 | 4 | 4 | 5 | 4 | 3 (47 / 72) | 2 | **34** |
| A3 · data first | 5 | 5 | 3 | 4 | 5 | 4 | 5 | 5 (72 / 72) | 1 | **37** |

The "fixes" counts are read from each approach's own §11 table by script (E my run: A1 `A 16, P 31, N 25`; A2 `18
structural, 1 structural in its envelope and exit halves, 26 a place, 1 a dependency, 1 complementary, 25 not addressed`;
A3 72 rows, each with a unit and an iteration). "Addressed" counts every row that is not "not addressed"; a row that
only gives a change its place is counted, and the justifications say how many each approach actually does.

## Justifications

### A1 · the smallest layer

- **Testable 4.** Every new unit has a pure seam — `where.resolve(env, cwd, …)` built from a dict, `outcomes` functions,
  `state` on a temp project with a fake clock — plus one subprocess invariant over 16 `main`s × 4 malformed inputs and
  four named ledger-invariant tests with 13 per-basis subtests (A1 §2 U2–U4, §5.2, §8.1); one point off because the
  inheritance and staleness it rests on need each body to list every file it loaded in `answer.read`, and no test
  checks that list is complete (A1 U3/U4 name none; A2 U5's read-audit is the missing seam).
- **Diagnosable 5.** One item shape `{kind, subject, where, sentence, fix}` with a single locator grammar
  (`<root>:<path>[#pointer|:line]`), a crash mapped to the innermost `scripts/` frame with its traceback filed and named,
  and `state.py` printing `stale @ run N — requirements.json changed` (A1 §3.1–3.2, U4 Errors, §4.4).
- **Simple 4.** It removes eight JSON shapes, two status words, the no-selection exit 1, 37 raw reads and seven plugin
  spellings and keeps each script's `render()` and argparse, as the 2026-09-30 note asks (A1 §9; E
  `2026-09-30-refactoring-architecture.md:112-113`); one point off because it adds a project state file beside
  `history.jsonl` and folds `check_all`'s `unmeasured[]` — which also carries buildability advisories — into one
  `unmeasured` assumption basis, giving one word two meanings (E `check_all.py:240`, see *Errors found*).
- **Iterative 5.** I0–I7 each end with the suite green and the bin, irrigation and plant-alarm run on scratch copies
  against a pass line written before the run, and the placeholders spark already makes move into `assumptions` in I1,
  before any inheritance exists (A1 §10).
- **Modular 4.** Five units, each with purpose, interface, errors, dependencies and seam, layered 0–4 with an
  import-direction test (A1 §2); one point off because it leaves `parts.py` and the nine-module cycle as they are and
  only freezes today's 17 function-local edges (A1 §1.1; 00 "one component of nine").
- **Free & local 5.** Standard library only; schemas are generated for editors and the suite while spark's validators
  stay the enforcer, and the MCP adapter is a standard-library stdio loop, a `bundled` tools entry off by default (A1 U5,
  §3.8, §7).
- **Humans & agents 5.** All 16 `main`s go through one `cli.run`, text and JSON are rendered from one `Answer`, and the
  MCP adapter runs the same script as a subprocess and returns its envelope unchanged — literally the same scripts
  (A1 U4, §3.5, §7).
- **Fixes part 1: 3.** 47 of 72 addressed — 16 done by the layer, 31 given a place or a report — and 25 left to part 1
  as written (A1 §11; my count of its table reproduces its own `A 16, P 31, N 25`).
- **Migration risk 4.** It moves 63 anchor rows by its own count, which reproduces (E my run: 51 inside `main()`s, 12 in
  the eight helpers it names), keeps every script and pins the bin's value stdout byte for byte; one point off because
  its I3 also changes functions holding at least 20 more rows (E my run: `check_spine.run` 9, `sim_project.limits_of` 4,
  `check_all.placeholder_components_in` 2, five others 1 each) and two effects on the bin go unnamed in its §12 — five
  value footers on stderr through `$(shell …)` (E bin `Makefile:49-53`; H GNU Make's `$(shell)` captures stdout only)
  and a new untracked `.spark/state.json` written by `boards.py --resolve`, the `board` stage (E bin `ls -a .spark/` →
  `board.json cache project.json rules.json`; `git check-ignore` printed nothing).

### A2 · the chain as a build graph

- **Testable 5.** The runner is tested on fake nodes by nine named tests (early cutoff, mtime-only checkout, kept edit,
  missing decision, raise, cycle, busy, status writes nothing), the ledger by property tests over seeded random graphs,
  and the one way content hashing can lie by a read-audit seam over the real nodes (A2 U2, U4, U5, §8).
- **Diagnosable 4.** `--plan` and `--status` say per node why it will run (`stale: <artefact> changed (<old 8> → <new
  8>)`) and problems carry `where {node, file, key, subject, line}` (A2 §3.1, §4.4); one point off because a node that
  raises becomes kind `crash` with no frame and no traceback location stated (A2 U4 Errors).
- **Simple 3.** It removes two orchestrators, the temp work folder, `--keep`/`--sim-dir`, `CHAIN_FACTS` and four
  placeholder channels (A2 §9), but adds a runner, a chain table, eight kinds, five plan actions, six node states,
  targets with floors, three generic board records and five new nodes; exit 0 also covers "a `--plan` that ran nothing"
  (A2 §3.2), and one `outcomes.render` replaces the per-script prose renderers the 2026-09-30 note keeps (E
  `2026-09-30-refactoring-architecture.md:112-113`; A2 §9 row 2).
- **Iterative 4.** I0–I8 each carry a hypothesis, a measure and a pass line, but the ledger is filled only in I4, and I3
  changes where every run writes (A2 §10 table).
- **Modular 4.** The runner knows nothing about electronics, every node has one `node(ctx) -> envelope` interface and
  `chain` is the only composition root (A2 U4–U6); one point off because `parts.py` and the import cycle stay (A2 §9
  "Kept").
- **Free & local 5.** Its own runner over the standard library's `graphlib` and `hashlib`, with make, doit, snakemake,
  redo, just and ninja each judged and refused on the standard-library rule, and hashing measured at 11.9 ms for 53
  files (A2 U4 table; E its runs).
- **Humans & agents 4.** One `check_spine` CLI and one renderer for both readers; one point off because the bin keeps
  four direct check calls beside `--target checks` (two routes to one verdict) and the MCP face calls nodes in process
  instead of the scripts (A2 §4.2, §7).
- **Fixes part 1: 3.** 47 of 72 addressed — 19 structurally, 26 as a place, 1 dependency, 1 complementary — and 25 not
  addressed (A2 §11; my count reproduces its own).
- **Migration risk 2.** It rewrites `check_spine.run` (48 anchor rows, and the simulation stage no test reaches without
  `tsci` — 00 V16) and deletes `check_all.py` (13 rows), 154 rows in the chain's scripts in all (E my run reproduces
  154), makes every project run write `board.tsx`, `dist/`, `sim/` in place (A2 §12 risk 1), and leaves undefined what a
  first run does to an existing output with no run record: §4.4's table says "never ran → runs it" and defines "kept"
  only against a recorded hash, while §12 says the person's `board.tsx` is kept.

### A3 · data first

- **Testable 5.** Eight named seams that hold for every future unit — among them "no schema vocabulary is restated in
  scripts" and "every schema property is read by a stage or a named reader" — a fidelity property test over every row
  of `data/stages.json`, and deterministic evals in which every recorded documentation block is a step (A3 §2.4, §5.2,
  §8).
- **Diagnosable 5.** `where` carries an RFC 6901 pointer, the record, the stage and the line; refusal sentences come from
  the schema's `x-spark-refuse`; a crash names the last `scripts/` frame with the traceback under `SPARK_DEBUG=1`; and
  `status` lists each stage with its reason (A3 §3.1, §3.7, L6 `cli`, §4.3).
- **Simple 3.** "One home per fact" removes six placeholder mechanisms, nine shapes, three layer walks and every
  vocabulary literal (A3 §9), but adds 13 schemas, its own JSON-Schema subset validator, three data tables, a new record
  kind, a provenance sidecar, a lockfile and a state file, about 37 modules in place of 25 (A3 §12 risk 7), and states
  the board in `.spark/lock.json` for some projects and `boards/active.json` for others (QA3-3).
- **Iterative 4.** I0–I8 each carry a pass line, and the ledger is filled from the mechanisms spark already has as early
  as I2; one point off because I3–I5 are each L and I4 retires `parts.py` as a command with every page in one commit
  (A3 §10.1).
- **Modular 5.** Layers L0–L7 with an import-direction test, and the record contract (`records`, `rules`) moved below
  everything that imported `parts` for it, which dissolves the nine-module cycle instead of freezing it (A3 §2.3).
- **Free & local 4.** Standard library only, with no run-time `jsonschema` because its current release pulls in compiled
  `rpds-py` (A3 §3.7, E PyPI read by A3); one point off because its own subset validator becomes a second tool to
  maintain beside one that exists, cross-checked only where `jsonschema` happens to be installed (A3 §12 risk 5).
- **Humans & agents 5.** One `spark.py`, whose argparse, `--describe` and MCP tool list are all generated from one
  `data/operations.json`, with MCP calling the same registry functions (A3 §6.2, §7).
- **Fixes part 1: 5.** All 72 placed in a unit and an iteration, including CH-64, which it schedules as a fix inside
  `cost.py` (A3 §11).
- **Migration risk 1.** It retires `parts.py` as a command and moves its contract out (266 + 196 rows sit in `parts.py`
  and `needs.py`, E 00), edits every page in one commit, adds a fab floor that turns every hand-written board without
  provenance red, and adds files to every project (A3 §10.2, §12 risks 2, 8, 9).

## Winner

**A1, the smallest layer — 39 against A3's 37 and A2's 34.**

Why, for the maintainer first:

1. **The blast radius is the smallest one that still lands the whole design.** 63 rows moved, plus about 20 in functions
   I3 touches (E my run), against A2's rewrite of the two orchestrators (154 rows in the chain's scripts) and A3's
   retirement of `parts.py` (462 rows). It keeps every script, its argparse and its prose, which is what the 2026-09-30
   note said must not move (E `:112-113`), and it is the only angle whose 00 "Keep" list survives untouched.
2. **It meets the PO's direction of 2026-10-09** — *"start finishing more and not starting new epics or bigger things"*
   (D) — with iterations of M to L that each close cards already on the board (#11's three unmet lines, #52, #53, #65,
   #101, #114; A1 §10).
3. **It covers all four flow options as layers on one mechanism, not as rewrites.** Option 1 is `STAGES`, the state file
   and the ledger (I3). Option 2 is I6's `--rerun` over the same digests. Option 3 is I7's adapter over the same
   envelope. Option 4 is §8's two tiers. A2's build graph and A3's schemas both remain reachable from A1's end state:
   A1's state already hashes inputs, and A1's `PHYSICAL_KEYS` table is the source a board schema is generated from.
4. **Every unit can be tested without a toolchain**, and the outcome invariant is a subprocess test, which reaches the
   traceback path a `main(argv)` call cannot (A1 U4; 00: 30 `subprocess.run` calls in 10 of 36 test files).

**Then the whole.** A1 is weakest exactly where the others are strongest, and the graft below is meant to close those
gaps. It does only 16 of the 72 changes itself. It cannot carry a C6 project to the simulation (A1 §5.1: *"the library
XIAO cannot play it yet"*). It has no test that its inheritance sees every read. And it leaves the board-and-part
contracts in two loaders. **The margin depends on the maintainer-first weighting.** Drop the migration-risk column and
A3 leads by one point (36 to 35). The win rests on the instruction to judge for the person who must change and test the
code, and on the PO's 2026-10-09 direction.

## Graft

Onto A1, each named with its source:

1. **A2 U5, the read-audit seam** (`test_every_node_reads_only_the_record_keys_it_declares`), used in reverse for A1.
   `read_json` and `store.records` record what a body actually loaded, and a test asserts `answer.read` ⊇ that set. This
   closes the one gap in A1's testability, since staleness and inheritance are only as true as `answer.read`.
2. **A2 U4's runner tests, as I6's pass lines:** `test_identical_output_bytes_stop_the_cascade`,
   `test_a_checkout_that_changes_only_mtimes_reruns_nothing`, `test_a_file_edited_after_spark_wrote_it_is_kept_and_named`,
   `test_status_writes_nothing`. Add A2 §4.4's **"kept"** state for an output whose hash differs from the recorded one.
   Also define the case A2 leaves open: an existing output with no run record is a source, never overwritten.
3. **A2 U4's `busy` kind on the project lock**, naming the holder's pid and start time. A1's state lock serialises two
   agents but says nothing to the one that waits.
4. **A2 §3.3's self-ignored `.spark/state/` folder**, carrying its own `.gitignore` of `*`, as an option for A1's D-A2.
   It touches no person's ignore file, and it answers the bin's new untracked `.spark/state.json` found above.
5. **A2 §3.3's code identity as an input to staleness, or at least as a printed reason.** A1 §4.4 says a run on another
   spark version is not stale, so a generator bug fixed by an update leaves every output "current". Which form (whole
   spark or per stage) is QA2-7's decision.
6. **A2 §4.2's rule for safe defaults:** a default is safe only when it cannot change what connects to what. It gives
   A1's D-A4 and §5.1 a stated boundary for which placeholders may flow.
7. **A3 §5.1's two measured runs as I0 fixtures, and A3 §5.2's `test_fab_refuses_an_assumed_header` in A1's I4.** In A3's
   run 2, a board with invented header geometry passed `--validate --for-fab` and the chain, exit 0, with no word about
   it. A1's `placeholder` map in U5 is the mechanism, and these fixtures prove it.
8. **A3 §3.8's `default_when_owed` with `records.generic_header`, behind its QA3-6.** With it, a board whose header is
   owed — the XIAO — reaches the simulation at target `sim`, ledgered and silkscreened `PLACEHOLDER`. That is the C6 path
   A1 §5.1 says it cannot give, and it fills the C6 case of the PO's 2026-10-10 "always simulates or tells you".
9. **A3 §2.1's chip columns** (image chip id, MicroPython port, the Wokwi boards in order of preference) **as columns of
   A1's `data/wokwi-boards.json`**, not as a new record kind. This closes CH-13's image half, which A1 leaves to the
   change.
10. **A3 §2.4 seams 6 and 7 as tests of A1's U5 generator:** no vocabulary is restated as a literal in `scripts/` (P46's
    "ledger of literals"), and every board-table key has a reader.
11. **A3 §5.2 rule 6, the artefacts carry the ledger:** a header comment in `board.tsx`, the footprint module and
    `pins.py`, and one line per stand-in in `WHAT-THIS-CANNOT-SHOW.md`. A ledger that only lives in an envelope is lost
    the moment a Gerber leaves spark.
12. **A3 §6.4's replacement rule table** (board or module × Wokwi has it / same silicon / nothing) **as the content of
    CH-30**, in place of A1 §6.4's prose. That includes "closest board = the first same-chip board whose pins cover
    every GPIO the design uses", which is CH-31's per-GPIO rule.
13. **A3 §8's recorded block as an eval step, and its "eval owed" report line** when a page's digest changes. This
    becomes the CH-40 mechanism in A1's I0, plus a model tier that is reported and never blocks.
14. **A3 §10.3's card table**, for the cards A1 names only in its reading list: #96 P160, #99 P162, #93 P157, #70 P136,
    #17 P94, #19 P87, #118 P175, #119 P176 (E my grep: one mention each in A1).
15. **A field for advisories in envelope v2.** None of the three has one. `check_footprints`' advisories (made as
    drawn, under the board house's recommendation; *"said and does not fail"*, P57) ride today in `check_all`'s
    `unmeasured[]` (E `check_all.py:236-240`). A1 would relabel them as `unmeasured` assumptions, and A2 and A3 drop the
    key.

## Refuse

| idea | approach, section | why |
| --- | --- | --- |
| outputs written into the project by default; `--keep` and `--sim-dir` removed | A2 §4.4, U7, §9 | it changes what a read-only look does to a person's tree (A2 §12 risk 1) and makes parallel agents collide in one project (risk 2), and a state record does not need it, because A1's state records what a run read and wrote without moving where it writes |
| `check_spine.run` rewritten as a runner over a node table in I2, before any state exists | A2 I2, U4, U5 | it re-anchors 48 rows and rewrites the simulation stage that no test reaches without `tsci` and a converter — the one place the 2026-09-30 note forbade without a simulator in the loop (E `2026-09-30-refactoring-architecture.md`, "Do not refactor"; 00 V16 holds) — and A1's I6 reaches the same reruns on the same digests with no rewrite |
| `check_all.py` deleted in favour of `--target checks` | A2 I6, QA2-5 | the review skill, README's Checks row and the pages name it (E `README.md:74`), and the bin's four direct calls stay anyway, which leaves two routes to one verdict; the gain is a name |
| one generic text renderer replacing each script's prose, and argparse generated from a table | A2 U1 `render`; A3 §3.1 `render_text`, §2.1 `data/operations.json` | the 2026-09-30 note keeps "the 16 `render()` blocks and the argparse blocks … the prose is the product" (E `:112-113`), and neither approach re-examines that line; A1 meets "every field printed" with a shared footer under each script's own prose |
| `spark.py` replacing `parts.py` as a command, with the contract moved out | A3 L6, I3–I4, QA3-4 | 462 anchor rows (E 00), every page in one commit, and part 1 found that no K row needs the split (part 1 §2.5, Q12); K64 stays the PO's trade, after a dated sweep if at all |
| a run-time JSON-Schema subset validator of spark's own | A3 L0 `schema`, §3.7 | it adds a second enforcer beside spark's sentence-giving validators and a specification to track; A1's schemas, generated for editors and the suite with the validators as enforcer, are part 1's Q15 (a) with nothing new to maintain — unless the PO picks Q15 (c) |
| a new record kind `soc` in a new `socs/` folder | A3 §2.1, QA3-5 | a table under `data/` carries the same chip facts (graft 9) without a contract, a layer row and a validator of its own |
| a provenance sidecar for every value of every record | A3 §3.5 | part of it the PO decided would grow by need (D 2026-10-06, #17 decision 1); for this epic only board geometry needs a fidelity statement, which A1's `placeholder` map gives |
| `.spark/lock.json` stating the board, with `boards/active.json` read only where there is no lock | A3 §3.6, QA3-3 | two statements of one choice, chosen by project type — the "one way to do each thing" criterion's own failure; the bin's Makefile depends on `boards/active.json` (E bin `Makefile:94`) |
| `check_all`'s `unmeasured[]` folded whole into an `unmeasured` assumption basis | A1 §2 "The producers", §9 | it carries buildability advisories too (E `check_all.py:240`); split them first (graft 15) |

## For the PO

The decisions below come from the three approaches together. Each one is his, and none is taken here.

1. **Which approach is the base**, and whether the grafts above go with it. This judge's lean is A1 with grafts 1–15.
2. **May an assumption change the exit code, and to what?** A1 D-A4: never, except under a named target, and then
   `problems`, exit 1. A2 §3.2: a target's floor makes it `problems`, exit 1. A3 §3.2 and QA3-2: a value below a target's
   run floor is `could-not-run`, exit 2. This is W1's letter set against "it looked and found the input not good enough".
3. **The fidelity words.** A1 has `placeholder · unstated · stated · checked · proven`, A2 has `placeholder · stated ·
   datasheet · measured`, and A3 has `owed · assumed · stated · checked · proven`. Separately, may `origin` take a fifth
   value, `assumed`, beside his four of 2026-10-06? That is QA3-1.
4. **The generic board.** The options are a role on an existing library board, with no C6 until CH-66 (A1 D-A5), one
   generic record per ESP32 family, used when a requirements file names none (A2 QA2-4), or generated from a chip record
   (A3 §5.3). Two narrower questions follow from it. Should a board whose header is owed get generic geometry at target
   `sim`, silkscreened `PLACEHOLDER` (A3 QA3-6)? And should the safe-defaults boundary be "nothing that changes
   connectivity" (A2 QA2-3)?
5. **The state file in git:** committed, ignored by the person, or a self-ignored folder (A1 D-A2; A2 §3.3).
6. **Staleness on a spark update:** not stale (A1 §4.4), the whole of spark's code as one hash (A2 QA2-7 (a)), or a
   revision per stage (QA2-7 (b)).
7. **The closed `kind` set:** six (A1, part 1's CH-46), six plus `decision` and `busy` (A2), or six plus `fact` and
   `placeholder` (A3).
8. **Envelope v2's item fields:** keep `sentence`/`fix` and add `kind` and `where` (A1 D-A1), rename them to `where`/`why`
   (A2 QA2-9), or make `fix` an object `{say, argv}` (A3 §3.1).
9. **The order:** the net and the layer first, part 1's ranks interleaved by iteration (A1 D-A8, A2 QA2-6), or part 1's
   tiers with the layer built as each change needs it (part 1 Q42). Part 1 states that enabling work is not a ranking
   key (part 1 §3).
10. **Q12, the `parts.py` split.** A3 makes it by consequence of I3–I4. A1 and A2 leave it out.
11. **Q15, schema enforcement.** The options are editors and suite only (A1, part 1's lean), a `jsonschema` dependency,
    or a validator of spark's own (A3).
12. **The model tier of the evals.** Its token cost, who scores it, and whether an "owed" eval blocks Review (A3 QA3-7;
    A1 §8.2 runs it per iteration from I5).
13. **Whether the 2026-09-30 premise "no framework is coming" is restated.** 00 V14 finds it overtaken by `parts.py`'s own
    framework and by his 2026-10-04 decision for one envelope printer. Each approach adds a little framework (`cli.run`,
    a runner, a generated CLI), and only A1 names a stopping rule for its own (A1 §12).

## Errors found

These are claims I checked against the code or the cited document and found wrong. Each pointer is at `5acbe42` unless
another file is named.

| approach · where | the claim | what the code or document says |
| --- | --- | --- |
| A1 §12, row "`cli.run` grows into a framework" | the 2026-09-30 note's warning signs at `:126-130` are "no base class for checks or stages, no `checks/` package, no scheduler before I6" | E `2026-09-30-refactoring-architecture.md:128-130`: "a base class for `Finding`, a `checks/` package (the route tests key on filenames in five places), or any diff touching the three big files without an item behind it". Neither "stages" nor "scheduler" appears; A1's version widens the source's words |
| A1 §2 "The producers", row `unmeasured`; §9 row on `unmeasured[]` | `check_all`'s `unmeasured[]` (`check_all.py:149`, `:240`) is the `unmeasured` channel, so the field goes into the assumptions | E `check_all.py:240`: `unmeasured=of(ADVISORY)`, under the comment *"An advisory — made as drawn, under what the board house recommends — is said and does not fail (P57)"* (`:236-238`); `ADVISORY` is `check_footprints.py:50`. Only `:149` is physics' needs-measurement. Folding both makes an advisory an assumption |
| A1 §1, §10 | "It moves 63 of the 989 mutation rows" (with "a floor: rows in renderers and tests are not counted") | 51 + 12 reproduce (E my run). But A1's own I3 changes functions that hold at least 20 more rows, none of them a renderer or a test: `check_spine.run` 9, `sim_project.limits_of` 4, `check_all.placeholder_components_in` 2, and one each in `check_spine.simulation_could_not_look`, `simulation_detail`, `emit_board.placeholders`, `check_spine.render`, `check_all.render` (E my run) |
| A2 §1, §2 U4 ("judged against what exists") | "spark promises 'nothing outside its standard library' (E `docs/guide/agents.md:70`, `README.md:85`)" | E `agents.md:70-71` goes on: *"except `flash_image.py`, which needs `littlefs-python`"*. `README.md:84-85` names Python 3.9 and Node 20 and says nothing of the standard library. The rule holds for the runner; the quotation leaves out the exception |
| A2 §3.4 | "`verified: true` reads as `origin: maker` (its alias, CH-65's own plan)" | E `proposal.md:2207-2209` (CH-65): "`verified` read as an alias for one release, then removed". It names no origin word, so "maker" is A2's own choice |
| A3 §2.2 L2 `records` | "`parts.digest`, `owes`, `broken_problems`, `function_of` (`parts.py:72-130`)" | E `parts.py:909`: `def digest`. The range holds `function_of` (`:72`), `CHAIN_FACTS` (`:98`), `owes` (`:107`), `_about` (`:113`) and `broken_problems` (`:127`) |
| A3 §2.2 L2 `fidelity`, §9 item 1 | `check_all.placeholder_components_in` at `check_all.py:152-214` | E `check_all.py:152` starts it and `:187` starts `rail_loads_in`; the range takes in a second function |
| A3 §6.3 (and A1 §6.3) | "git is already required (`gh` in `check_vendor_pins.py:66-68`, the gate's `git archive`)" / "through git, which spark already requires (STORE-14)" | E `README.md:84-91` ("Before you start") lists Python, Node and what `/spark:setup` installs, and no git. `gh` is needed only for a live `check_vendor_pins` (E `agents.md:72-73`), and `git archive` is the maintainer's pre-push gate (00 "The gate"). For a hobbyist this is a premise, not a fact, and part 1's §2.3 shares it |

**Checked and held** (so the reader need not recheck them):

- 37 raw `json.loads(…read_text…)` sites in 16 scripts (E `grep`).
- `store.PLUGIN` is read by no script (E `grep`; only one mutation row names it).
- 43 library part facts: 34 `verified: true`, 9 `false`, 0 carrying `origin`. The XIAO's `physical` holds
  `footprint_export, footprint_module, height_mm, width_mm, wokwi_size_px` (E my count).
- 154 rows in A2's seven chain scripts (E my run).
- `wokwi-mcp` is `kind: mcp, on: false` (E `data/tools.json:164-167`).
- `--assume-missing-sizes` is always passed by the chain (E `check_spine.py:360`).
- The bin captures five `boards.py` values with `$(shell …)` (E bin `Makefile:49-53`).
- `outcomes.py:9-13` sanctions the local aliases.
- `boards.py:537-539` maps every `BoardError` to `EXIT_INVALID`.
- `boards.active_id` reads only `board` (E `boards.py:196-210`), so A1's added `placeholder` key is additive.
- `emit_board` refuses a board with no `footprint_export` before any simulation stage (E `emit_board.py:1063-1066`) —
  A3's "PCB-first" finding.
- `check_footprints.run` turns each placeholder's findings into one could-not-run (E `check_footprints.py:460-493`).
- `emit_board` recomputes the pin map (E `emit_board.py:1055`), as A2 says.
- `tests/test_boards.py:314` is `TheCommandLineTheSmartBinDependsOnTest`.

## Searches

none. No web or MCP search. Read-only `gh issue view` of #11 (CLOSED, "P43 — What an agent reads back"), #103 (OPEN, "P166
— QA we can trust", which A2 reuses) and #124 (CLOSED, P179).

## Found on the way

- E · `check_all`'s `unmeasured[]` key carries two different things: physics' needs-measurement findings
  (`check_all.py:149`) and buildability advisories (`:240`). An agent reading the key cannot tell an unmeasured figure
  from a board-house recommendation. It is not in part 1 (E `grep -i advisor proposal.md` → nothing) and not in
  `docs/observations/INDEX.md` (E the same grep).
- E · The bin has a `.spark/` folder with no ignore rule for new files in it (E bin `ls -a .spark/`, `git check-ignore -v
  .spark/state.json` → nothing). Any design that writes a state file there makes the bin's `git status` dirty after a
  `make`. This was raised against A1 above, and it applies to every design that records runs in the project.
- H (GNU Make's documented `$(shell)`: stdout is captured, stderr passes through) · Anything a value operation prints on
  stderr reaches the terminal on every `make` invocation in the bin, because the five `$(shell boards.py …)` lines are
  evaluated at parse time (E bin `Makefile:49-53`). A test that pins stdout byte for byte cannot see it.
- E · `assign_pins.py:434` prints "could not load the design" on stdout, not stderr, so under `--json` the could-not-run
  case is prose on stdout. 00 records `:434`'s exit 2 and the `:438` note; whether part 1 lists the `:434` channel: —.
- E · The 2026-09-30 note's "Do not refactor … the 16 `render()` blocks and the argparse blocks" (`:112-113`) is not
  re-checked in 00's V1–V18 table, which checks the other "Do not refactor" items (V13, V15, V16). A2 and A3 both cross
  it without citing it.
- E · Of the cards the brief names, A2 cites none of #101 P164, #93 P157, #19 P87, #22 P91, #118 P175 and #119 P176 (E my
  grep, 0 mentions each), so any plan built on A2 must place them from A3 §10.3 or part 1's card table.
