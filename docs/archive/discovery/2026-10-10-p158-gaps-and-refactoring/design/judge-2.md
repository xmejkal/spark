# P158 part 2 — judge 2 of 3

Written 2026-10-10 by judge 2, against spark 0.8.1 at main `5acbe42` (E `git log -1` → `5acbe42 2026-10-10 22:26:37 +0200
Merge pull request #129`). I scored three architecture approaches for spark independently: A1 *the smallest layer*, A2
*the chain as a build graph* and A3 *data first*. I did not coordinate with the other judges. I judged with the AI agent at
the keyboard first and then the whole system, against the PO's criteria (a)–(h) in the brief. Nothing here is decided. §
"For the PO" lists what only he can decide.

**Tags.** E means a pointer: a file and line at `5acbe42`, or a command and what it printed. H means a claim with its
source. D means a decision, with who made it and when. — means unknown. `A1 §n`, `A2 §n` and `A3 §n` are sections of
`approach-A1-smallest-layer.md`, `approach-A2-build-graph.md` and `approach-A3-data-first.md`. "00" is
`00-system-as-is.md` and "part 1" is `proposal.md`.

**What I read.** All of 00. All of A1, A2 and A3. From part 1: §2 whole, §3's priority rule, the CH headings, the card
table and "What not to do". I read the code at the pointers listed under "Errors found". I read the bin's `Makefile` at
lines 10-55 and ran `git ls-files .spark` on it, both read-only. Cards: `gh issue view` for state and title of #5, #6, #7,
#8, #11, #16, #17, #19, #22, #23, #41, #44, #52, #53, #55, #58, #59, #61, #65, #69, #70, #84, #85, #89, #93, #94, #96, #99,
#101, #102, #114, #118, #119 and #123. All are OPEN except #11, which is CLOSED.

**What I ran.** Everything ran in `<scratch>` on a `git archive 5acbe42` of `scripts boards parts data`. Every command
set `SPARK_HOME`, `HOME` and `TMPDIR` as three separate words, each pointing at an empty folder of `<scratch>`. I did not
open, copy or touch the PO's real store. I wrote nothing under `~/Development` except this file. There were three runs:

- **R1.** `assign_pins.py requirements.json --json` on `commands/build.md`'s example, in a folder that is not a project.
  Exit 0. stdout is 6,446 bytes and 6,444 characters. A note of 174 bytes (172 characters) comes before the `{`. The
  `unverified` list holds 5 entries: 1,910 characters as compact JSON, 2,120 with `indent=2` as printed.
- **R2.** An `ast` pass that maps every row of `tests/mutations/*.json` on `scripts/` to the top-level function holding
  its `find` text. Result: 1,281 rows, 989 of them on `scripts/`, 0 not found. 51 rows sit inside a `main()` and 12
  inside A1's eight moved helpers. Rows in other functions: `check_spine.run` 9, `boards.validate` 9,
  `check_all.placeholder_components_in` 2, `check_spine.simulation_could_not_look` 1.
- **R3.** A count of each approach's §11 table by script. A1: A 16, P 31, N 25. A2: 18 structural, 1 structural in its
  envelope and exit halves only, 26 a place, 1 dependency, 1 complementary, 25 not addressed. A3: 72 rows, every one
  placed, with CH-64 marked "not a design question" but scheduled.

## Scores

| approach | testable | diagnosable | simple | iterative | modular | free and local | humans and agents | fixes part 1 | migration risk (5 = lowest) | total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 · the smallest layer | 5 | 5 | 4 | 5 | 4 | 5 | 4 | 3 (47/72) | 4 | **39** |
| A2 · the chain as a build graph | 5 | 5 | 3 | 4 | 4 | 5 | 5 | 3 (47/72) | 2 | **36** |
| A3 · data first | 4 | 4 | 2 | 3 | 5 | 5 | 5 | 5 (72/72) | 1 | **34** |

**How "fixes part 1" is scored.** The score is round(5 × addressed ÷ 72). A CH counts as addressed when the approach's
own §11 table does not mark it N or "not addressed" (E R3). A1 and A2 each address 47 and A3 addresses 72. The same
counts limited to mechanism are A1 16 (A) and A2 19 (structural, CH-21 included). A3's table does not separate mechanism
from scheduling. Many of its rows place part 1's own fix in an iteration: CH-64 is "a fix inside `cost.py`", and CH-58
is moved into a JSON reader. So its 72 measures coverage of the plan more than coverage by the design.

## Justifications

### A1 · the smallest layer

- **Testable 5.** Every invariant has a named test: the four ledger invariants, plus a subtest per basis (A1 §5.2). The
  outcome invariant runs as a subprocess over all 16 `main`s × 4 inputs, because only a subprocess can see a traceback
  (A1 §8.1). `Where` is built from a dict, so the 15 `patch.object` sites become fixtures (A1 §2 U2 seam).
- **Diagnosable 5.** One locator grammar, `<root>:<path>[#pointer|:line]`, with the roots `project`, `store`, `plugin`,
  `temp`, `arg` and `spark` (A1 §3.1). The `kind` is closed (A1 §3.2). A crash is reduced to the innermost frame under
  `scripts/` (A1 §2 U4). `context` names the spark, store and project that answered (A1 §3.1). `state.py` gives each
  stage's stale reason (A1 §4.4).
- **Simple 4.** It removes before it adds: eight JSON shapes, `mismatch`, `skipped` as a status, the 37 raw reads and
  seven spellings of the plugin folder (A1 §9), against three new modules. One exit code has one meaning (A1 §3.4). It
  loses a point for carrying two closed vocabularies (6 kinds, 13 bases) plus 5 levels (A1 §3.2-3.3). It also stores
  each run's assumptions in `state.json`, which A1 itself has to argue is not a second statement under W21 (A1 §3.6).
- **Iterative 5.** I0 is a net with a baseline and no behaviour change. Every iteration ends with the bin, irrigation
  and plant-alarm run on scratch copies against a pass line written beforehand (A1 §10). Where it cannot carry a board
  through the chain it says so instead of hiding it: the XIAO "cannot play it yet … said, not hidden" (A1 §5.1).
- **Modular 4.** U1–U5 each state a purpose, an interface, errors and a seam, and an import-direction test turns today's
  17 upward edges into a known list (A1 §2). By choice it leaves `parts.py`'s 28-operation framework and the nine-module
  cycle untouched (A1 §1.1).
- **Free and local 5.** Standard library only. Schemas are generated for editors, with no `jsonschema` at run time (A1
  §2 U5). The MCP adapter is standard-library Python over stdio and off by default as a `data/tools.json` entry (A1 §7).
- **Humans and agents 4.** Both use the same scripts, and the MCP adapter runs each script as a subprocess and returns
  its envelope unchanged (A1 §7). But each script keeps its own `render()` prose beside a shared footer (A1 §1, §3.5).
  Text and JSON still come from two code paths per script, so the class CH-16 names can recur through a new render line.
- **Fixes part 1: 3.** 47 of 72 addressed: A 16, P 31, N 25 (A1 §11; E R3).
- **Migration risk 4.** Every command and flag stays. The one break everyone meets is `--json` going from version 1 to
  2 in I1, with the pages changed in the same commit (A1 §12). Its anchor cost, "63 … a floor" (A1 §10), reproduces
  exactly (E R2). But 21 more rows sit in functions I3 and I4 rewrite (E R2), and one risk is missing (see "Errors
  found" 4).

### A2 · the chain as a build graph

- **Testable 5.** Property tests run over seeded random graphs (A2 §2 U2). Nine runner tests run on fake nodes, including
  early cutoff, mtime-only changes and "status writes nothing" (A2 §2 U4). The read-audit seam catches an undeclared
  input, the one way content hashing goes wrong (A2 §2 U5). Golden envelopes have their normalisation budget measured in
  I0 (A2 §10).
- **Diagnosable 5.** `where` is an object with node, file, key, subject and line. `kind` adds `decision` and `busy` (A2
  §3.1). `--status` names each stale artefact with its old and new hash, and a person's edit is "kept" and named (A2
  §4.4).
- **Simple 3.** One exit code still means one thing, and "below the floor" is problems (A2 §3.2). But it adds a generic
  runner, a chain table, a ledger module, 8 kinds, 4 levels, targets with floors, decision sources with a safe-default
  rule, and kept or merged artefact ownership (A2 §2-§4). It removes `check_all`, `--keep`, `--sim-dir` and the temp work
  folder (A2 §9). The mechanism count is the highest of the two runner-free alternatives.
- **Iterative 4.** I2 makes `check_spine.run` a loop over the node table, still in the temp folder and with no verdict
  change. This is a careful step (A2 §10). I3 then flips outputs to land in place and drops two flags in one iteration,
  and the plan runs to nine iterations (A2 §10, §12 risk 10).
- **Modular 4.** The runner "knows nothing about electronics" (A2 §2 U4). `chain` is the composition root (U5), and
  every node is `node(ctx) -> envelope` (U6). The 187-line `run` breaks into nodes. `parts.py` and the cycle stay (A2 §9
  "Kept").
- **Free and local 5.** A table weighs make, doit, snakemake, redo, just and ninja, and A2 adopts `graphlib` plus
  `hashlib` (A2 §2 U4; E A2's own `find_spec` runs). The MCP face is a `kind: mcp`, `on: false` entry, following the
  existing `wokwi-mcp` row (A2 §7; E `data/tools.json` `wokwi-mcp` → `mcp False ['wokwi-cli']`).
- **Humans and agents 5.** `render(envelope, as_json)` is the only printer (A2 §2 U1). The MCP face calls the same node
  function and is tested byte-identical (A2 §7). `--plan` and `--status` answer an agent's "what would run, and why"
  without writing anything (A2 §2 U7).
- **Fixes part 1: 3.** 47 of 72 addressed (A2 §11; E R3). Tier-1 changes left unaddressed include CH-12, CH-14, CH-18
  and CH-19.
- **Migration risk 2.** `check_spine` writes into the project by default, so a look changes the person's tree, and
  parallel agents that never collided now share one folder (A2 §12 risks 1-2). 154 anchor rows sit on the chain's
  scripts (A2 §12 risk 4). `check_all.py` is deleted (A2 §10 I6, QA2-5). The runner is new code every answer trusts (A2
  §12 risk 5).

### A3 · data first

- **Testable 4.** There are named tests for its seven ledger rules and eight seams (A3 §2.4, §5.2). Two are weak. The
  subset validator is only checked against `jsonschema` "where installed", and skipped otherwise (A3 §2.2 L0 `schema`,
  §12 risk 5). `test_no_schema_vocabulary_is_restated_in_scripts` searches `scripts/` for every enum literal, which hits
  words like `ok` or `gpio` that have other uses (A3 §2.4 seam 6).
- **Diagnosable 4.** `where` carries a JSON Pointer and a record reference (A3 §3.1). But the kind `fact` appears under
  exit 1 ("broken") and under exit 2 ("owed below the run floor"), and a placeholder below a floor is could-not-run (A3
  §3.2-3.3). An agent branching on the exit code is told "could not look" when spark looked and judged the fact too weak.
- **Simple 2.** It adds schemas, a home-grown subset validator, three data tables, a new `soc` record kind, a provenance
  sidecar, `lock.json` and `state.json`. That comes to "about 37 modules plus data files" (A3 §12 risk 7). Exit 2 gains
  a second meaning, "could not look at the level the target needs" (A3 §3.2).
- **Iterative 3.** I0–I2 are sound. I3 (schemas, fidelity, provenance on every library record, and the bin's fab gate
  depending on that provenance landing in the same commit) and I4 (`parts.py` retired as a command, every page changed
  in one commit) are each L and couple many changes (A3 §10.1, §12 risks 2 and 8).
- **Modular 5.** L0–L7 come with an import rule and its test. The record contract sits below every module that imported
  `parts` for it, so the nine-module cycle dissolves (A3 §2.2-2.3).
- **Free and local 5.** Its own validator replaces `jsonschema`, whose 4.26.0 pulls in `rpds-py` (A3 §3.7, E PyPI as
  quoted). Git is the global store, and sync libraries are judged one by one and refused (A3 §6.3).
- **Humans and agents 5.** Argparse, `--describe` and the MCP tool list are all generated from `data/operations.json`
  (A3 §2.1). `render_text(env)` renders the envelope field by field (A3 §3.1). A test checks that every `next[].argv`
  parses (A3 §3.1).
- **Fixes part 1: 5.** All 72 rows are placed (A3 §11; E R3). The caveat on what that number measures is under Scores.
- **Migration risk 1.** `parts.py` is retired as a command (A3 QA3-4), and 266 + 196 anchors move (A3 §10.2). A fab
  floor fails every hand-written board without provenance (A3 §12 risk 2). New files appear in every project (A3 §12 risk
  9). It contradicts the PO's "finish more" of 2026-10-09, which A3 itself flags (A3 §12 risk 12).

## Winner

**A1, the smallest layer, with the grafts below.**

**Why, with the AI agent first.**
- **I1 gives the agent everything at once.** Every one of the 16 `main`s answers in one envelope that carries `kind`,
  `where`, `fix`, a filled `next`, `context` and `assumptions`, and none ends in a traceback (A1 §3, §8.1). The agent
  learns no new command, and no flag it already uses disappears.
- **By I3 it can answer "where am I".** `state.py --json` says what ran, on which inputs, what is stale and why. The
  ledger travels by digest from the stage that made a placeholder to the final verdict (A1 §4.3-4.4, §5.2).
- **The PO's later flow options sit on the same data.** The build graph is I6, and it reuses the I3 digests. The MCP
  face is I7, and it carries the same envelope bytes. Nothing is rewritten (A1 §10).
- **It finishes work already decided and never built.** The 2026-09-30 note set two targets, `outcomes.report` and
  `outcomes.read_json`, and neither exists (00 V9, V11). The PO decided on "one envelope printer for every command" (D
  2026-10-04, store design §6.1). Doing these first follows the PO's "start finishing more and not starting new epics" (D
  2026-10-09).
- **It is honest about what it leaves undone.** It counts its 25 untouched changes and gives a reason for each (A1 §1.1,
  §11).

**Why not the others.**
- **A2 is the better end state for "run me to a target".** `--plan`, `--status`, `kind: decision` and per-key reads are
  real gains for an agent, and they can be grafted. Its runner, though, comes with a behaviour flip: outputs written in
  place and `--keep` removed. That flip is A2's own top risk (A2 §12 risks 1-2), and P158 does not need it.
- **A3's end state is the cleanest for agents.** One generated CLI and a schema for every record. But it reaches that
  state only through two L iterations that retire `parts.py` and move 462 anchor rows, the trade the PO left open as Q12.
  Its strongest contribution is evidence: the measured silent pass of an invented board (A3 §5.1). A1 must take that in.

**Where A1 is weakest.** It is weakest on the PO's 2026-10-10 "always simulates or tells you".
- A board with no header geometry still stops at `schematic`. A1 itself says the library XIAO cannot reach simulation
  (A1 §5.1). A3 shows the stop is general to every geometry-less board (A3 §5.1 run 1; E `emit_board.py:1063-1066`).
- A1 does "tell", and so meets the letter of the criterion. To "simulate" as well, it needs a mechanism for safe
  defaults: A2's rule on what a safe default is, plus A3's placeholder geometry with physical marking. Grafts 5-7 below
  supply it, under a decision only the PO can take (D3, D4).

## Graft

Each graft is named by approach and section, followed by where it lands in A1.

1. **A2 §2 U5, the read-audit seam.** In A1, inheritance by digest reads the paths each body reports in `answer.read`
   (A1 §2 U3, §4.3). A body that forgets to report a read inherits nothing and says nothing. During the journeys (A1
   §8.1), wrap the record loader and `read_json` and assert that every file read is in `answer.read`. Test:
   `test_every_body_reports_every_file_it_read`.
2. **A2 §2 U4 (the `keys` hash) and A3 §4.3 (pointer-scoped value digests).** Record a record's digest per stage over
   only the keys that stage reads, so a new `body_mm` stales `schematic` and leaves `pins` fresh. A1 digests whole
   records, so a part-record change stales "`pins` and after" (A1 §5.3 step 3). That over-reports for the agent and
   would over-run I6. Add the keys each stage reads to `STAGES` (A1 §4.1).
3. **A2 §3.1 and §4.2, the `kind: decision`.** Use it when a source only a person or the conversation makes is missing,
   with that source's command in `next`. For an agent this is the cleanest "stop and ask the person" signal. A1's six
   kinds would file the case under `input`. A2's `busy` kind is better carried as CH-3's own "a wait that says who holds
   it" (part 1 CH-3), so it adds no seventh word.
4. **A3 §5.1, runs 1 and 2, as I0 journey fixtures.** Run 1 is a placeholder board with no geometry. Run 2 is the same
   board with an invented header: it passes `--validate --for-fab` with exit 0, and the chain ends "the chain runs end to
   end" with no word about the placeholder. By part 1's own definition of silent this is a tier-1 fault part 1 does not
   carry (see For the PO, D14). A1's I4 and I5 then need a pass line on it: `--for pcb` refuses the invented header,
   naming the pointer.
5. **A3 §5.2 rule 6, placeholders carried in the artefact.** A comment at the head of `board.tsx` and of the footprint
   module names every assumption, and a placeholder footprint carries the silkscreen text `PLACEHOLDER — NOT THIS BOARD`.
   Then a Gerber exported outside spark still shows it. Today A1 keeps only the existing `board.tsx` comment (A1 §2 "The
   producers").
6. **A2 §4.2, the safe-default rule, if the PO says yes (D4).** "A default is safe only when it cannot change what
   connects to what." A size, a footprint's geometry, a stand-in or the absence of firmware may be assumed and recorded
   in the ledger. A pin order, a pin role, a part's needs or the goal never may. That is the boundary A1's I5 lacks.
7. **A3 §3.8 `default_when_owed`, under the same yes.** For target `simulate`, apply it to a board whose header is owed,
   with one function, `generic_header(pins)`, so the XIAO and any geometry-less board reach simulation with the guess in
   the ledger. It closes the gap A1 §5.1 names.
8. **A2 §4.4, the "kept" and "merged" artefact states.** A1's `edited-after` names an edit but not whose file it now
   is. Take A2's sentence: "it is yours now — spark builds it and does not overwrite it". Mark `sim/diagram.json` as
   `merged`, because the converter keeps the positions a person tuned (00, `merge.ts`). Without that, A1 would raise a
   false `edited-after` entry every time someone drags a part in the Wokwi editor.
9. **A2 §2 U4 tests, for `state.py`.** Add `test_a_checkout_that_changes_only_mtimes_reruns_nothing` and
   `test_status_writes_nothing`, so a `git checkout` or a folder sync never makes a stage read as stale, and asking about
   the state writes nothing.
10. **A2 §4.3 `ledger.owed_table`, the owed-facts table derived from stage reads.** A1's I5 needs a table of levels per
    target, which it leaves to P165 to write by hand (A1 §3.3, §10 I5). Deriving it from each `STAGES` row's declared
    reads also retires `CHAIN_FACTS` and `_about` (part 1 CH-37) from one table.
11. **A2 §3.3 `.spark/state/` with its own `.gitignore` holding `*`, if the PO picks "ignored" (D6).** The bin tracks
    `.spark/` (E `git -C ~/Development/smartbin-local ls-files .spark` → `board.json`, two cache headers,
    `project.json`, `rules.json`), and A1 writes `.spark/state.json` beside them on every recorded run (A1 §3.6). A
    self-ignoring folder keeps it out of the bin's `git status` without touching the person's ignore file.
12. **A2 §3.3 and §4.4, tool versions as recorded inputs.** Record the `tsci` and converter versions as inputs of
    `build` and `simulation`, and treat a change as a stale reason. A3's run used the project's own tsci 0.0.2621 over
    the pinned 0.0.2600, and only the stage line said so (A3 "Found on the way"). spark's own version stays printed and
    is not a stale reason (A1 §4.4).
13. **A2 §2 U4, `graphlib.TopologicalSorter` for A1's I6.** A1 reruns stale stages "in table order" (A1 §10 I6). The
    standard library already sorts the order, and A2's table of runners records why no outside runner is used.
14. **A3 §3.1, the test that every `next[].argv` parses.** A1 fills `next` from `STAGES` (A1 §4.2). Assert that each
    `argv` parses against the named script's own parser (`--describe`), so a filled `next` can never send an agent to a
    flag that does not exist.
15. **A3 §2.2 L6 `cli`, `SPARK_DEBUG=1`.** It prints the traceback on stderr on request, alongside A1's crash file in
    `TMPDIR` (A1 §2 U4). Agents set `TMPDIR` to scratch folders that are often deleted, which A1 lists as a risk (A1 §12,
    last row).
16. **A3 §6.3, the sync table, as input to P178's council (#123), not as code.** It is the most complete judgement of
    git, lockfile, submodule, annex, Dolt, SQLite, CouchDB, CRDTs, folder sync and merge-patch. A1 §6.3 and part 1 §2.3
    reach the same verdict with fewer rows.

## Refuse

1. **A2 §4.4 and §9: outputs in place by default, `--keep`, `--sim-dir` and the temp work folder removed (QA2-2
   (a)).**
   - A look would write into the person's tree.
   - Parallel agents, who never collide today, would share one folder (A2 §12 risks 1-2).
   - No CH needs it. The CH-35 fix ("build the kept file") works inside `--keep`.
2. **A2 §10 I6: deleting `check_all.py` (QA2-5 (a)).**
   - It is a public entry point named in pages and skills (00, "Who orchestrates").
   - Folding its runner onto `STAGES` while keeping the command meets W16 without breaking a habit.
3. **A2 §3.3: a hash over all of spark's code as a stale reason (QA2-7 (a)).**
   - Every spark update would rerun every stage once.
   - Record tool versions instead (graft 12) and print spark's own version.
4. **A3 QA3-4: retiring `parts.py` as a command in favour of `spark.py` within P158.**
   - 266 + 196 anchor rows would move (A3 §10.2), and every page would change in one commit.
   - Q12 is open, and "finish more" (D 2026-10-09) stands.
5. **A3 §3.7: a home-grown JSON Schema subset validator as the enforcer at run time.**
   - It is a second validation engine to keep correct, and its cross-check is skipped wherever `jsonschema` is absent (A3
     §12 risk 5).
   - Keep spark's validators as the enforcer and their sentences as the message, with schemas generated for editors (A1
     §2 U5, part 1 Q15 (a)).
6. **A3 §3.2-3.3: "below the target's floor" as could-not-run, and `fact` as one kind under two exit codes.**
   - A check that looked and found a fact too weak for the target has found something. That is problems, exit 1, as in
     A1 §3.3 and A2 §3.2.
   - Moving an unknown id to could-not-run goes against the PO's D of 2026-10-04 and stays with Q14.
7. **A3 §3.5: a provenance sidecar keyed by JSON Pointer.**
   - It would be a third provenance convention in a board file, and A3 itself found two already (A3 "Found on the way").
   - CH-65 (P151, #85) puts `origin` on facts first. A sidecar is a later answer if that proves too narrow.
8. **A2 §5.1 and QA2-4 (a): a requirements file that names no board silently using `generic-esp32s3`.**
   - A defaulted board makes the first ledger entry a choice nobody made.
   - A1's explicit `init_project.py --board <id> --as-placeholder` (A1 §5.1) keeps it a recorded choice. Whether generic
     records exist at all is D5.
9. **A3 §10.1 I6 and A2 §10 I7, the global store by git and copies as nodes, inside P158.** Both say these belong to
   P178's concept (#123). They are designed ahead of its council, and nothing in I0–I5 needs them.
10. **A3 §5.4 and I8, the generic firmware harness, inside P158.**
    - It is slice 3's (#7 P59, #8 P74), as A3 says.
    - P158's plan should give the harness only its inputs, the ledger entry `no-firmware` and the firmware levels (A1
      §5.1).

## For the PO

Each is a decision only the PO can take. Where an approach states a lean, it is cited. A lean of mine is labelled as a
proposal.

| # | decision | options | raised by | what rests on it |
| --- | --- | --- | --- | --- |
| D1 | The base approach for P158 part 2's plan, and whether 2026-09-30's "this is not a refactoring project" is restated | (a) A1 with the grafts above (proposed here); (b) A2; (c) A3; and restate the verdict or not | brief; 00 V14 | every card's shape |
| D2 | Order: the layer's I0–I1 before part 1's tier ranks, or part 1's ranks with the layer built as each change needs it | (a) layer first; (b) tier order; (c) I1 by rank (it carries CH-16, rank 1), then the PO picks | A1 D-A8, A2 QA2-6, part 1 Q42 | the first slice |
| D3 | May a run on placeholders end `ok`, exit 0, for a simulate target, with the ledger in the verdict and the count in the verdict sentence? | (a) yes, and a named target (`--for pcb`) turns entries below its level into problems; (b) a placeholder is always could-not-run unless a flag allows it | A1 D-A4, A2 §3.2, A3 QA3-2 | W1's reading; whether the PO's "tolerates problems but informs" holds |
| D4 | May spark assume a geometry (a generic header, an outline) for a simulate target, recorded in the ledger and marked on the silkscreen, while never guessing connectivity? This turns "never a guessed footprint" into "never an unledgered guess" | (a) yes, with A2's safe-default rule; (b) only the defaults that exist today (`--assume-missing-sizes`, placeholder footprints); (c) no | A2 QA2-3, A3 QA3-6 | whether a geometry-less board (the XIAO) can reach simulation (grafts 5-7) |
| D5 | The generic board | (a) a role on `boards/active.json` played by a library board (A1's lean); (b) one library record per ESP32 family (A2); (c) records generated from a chip-family `soc` record (A3); and in every case whether it is ever a default (Refuse 8 proposes never) | A1 D-A5, A2 QA2-4, A3 QA3-5 | the C6 path; new data to research |
| D6 | The project's run state in git | (a) ignored, in a self-ignoring folder (graft 11); (b) committed, self-checking by digest, changing on every run | A1 D-A2, A2 §3.3 | the bin's tracked `.spark/`; fresh-clone reruns |
| D7 | What makes a stage stale | (a) input content only (A1); (b) plus tool versions (graft 12); (c) plus a hash of all spark code (A2 QA2-7) | A1 §4.4, A2 QA2-7 | rerun cost after updates |
| D8 | The item fields of envelope 2 | (a) keep `subject`, `sentence`, `fix` and add `kind`, `where` (A1); (b) rename to `where`, `why`, `fix` (A2); (c) `fix` as `{say, argv}` (A3) | A1 D-A1, A2 QA2-9, A3 §3.1 | every reader of envelope 1, in one commit |
| D9 | One closed `kind` vocabulary and one fidelity ladder for every answer | the three approaches propose 6 and 8 and 8 words, and three ladders (see Found on the way); your four `origin` words of 2026-10-06 (#17) are fixed input | A1 D-A9, A2 §3.4, A3 §3.3-3.4 | envelope 2 publishes them in I1 |
| D10 | Q12, the `parts.py` split, stays out of P158 | all three keep it out (A3 only "by consequence" of QA3-4) | part 1 Q12 | 266 + 196 anchors |
| D11 | #11 (P43, closed with its three value lines unmet, 00): reopen it or cite it on I1's story | reopen / cite | A1 §10 I1, A2 §10 I1, A3 §10.3 | the card that proves I1 |
| D12 | How much ledger an intermediate stage prints in text | all entries, or counts plus its own new ones; the final verdict always prints all | A1 D-A6 | an agent's context budget; a person's terminal |
| D13 | The path resolver (#124's suggestion) as a module of its own (`where` or `paths`) or inside `store.py` | (a) module (A1 D-A7, A2 U3, A3 L1); (b) in `store` | A1 D-A7 | where P179's rule lives |
| D14 | Part 1 gains a CH for the invented-geometry silent pass (A3 §5.1 run 2): `--for-fab` exit 0 and "the chain runs end to end" for a board whose geometry is invented | rank it by part 1's keys (tier 1 by its own definition of silent), or fold it into CH-36 | A3 "Found on the way" | graft 4's pass line |
| D15 | When reruns run by themselves and when the MCP face comes | A1 I6 and I7: after I3, and when a consumer that is not Claude Code exists | the PO's options 2 and 3 (D 2026-10-10) | — |
| D16 | Model evals: their token cost, who scores them, and whether an owed eval blocks Review | report line; council reads; blocks | A1 §8.2, A2 §8, A3 QA3-7 | the "evals instead of prompt optimisation" option |

## Errors found

These are claims checked against the code or a run and found wrong or incomplete. Each item names the approach and the
section.

1. **A1 §2, "The producers", row `assumed-size`: "printed today as a comment in `board.tsx` and a stderr note".** There
   is no stderr note. With `--assume-missing-sizes`, the only sizes message, the refusal at `emit_board.py:1102-1108`, is
   skipped. The stderr notes after the emit (`:1124-1147`) are about unclaimed signals, unreceived outputs, unsourced
   rails and contention, never about sizes. The guess is declared only in `board.tsx` (`emit_board.py:591`). E my read
   of every `file=sys.stderr` in `emit_board.py`.
2. **A1 §1, "It moves 63 of the 989 mutation rows … where splitting … would move 462".** The 63 reproduces exactly: 51
   in `main`s and 12 in the eight helpers (E R2). §10 itself calls the 63 "a floor". The functions A1's own I3 and I4
   rewrite hold 21 more: `check_spine.run` 9, `boards.validate` 9, `check_all.placeholder_components_in` 2,
   `check_spine.simulation_could_not_look` 1 (E R2). So the comparison in §1 understates the layer's cost.
3. **A1 §2 U2, §3.1 and "Found on the way", M1's units.**
   - "172 bytes of prose before the `{`" is 172 characters and 174 bytes.
   - "6,444 bytes" is 6,444 characters and 6,446 bytes.
   - "5 entries in 1,910 JSON characters" is the compact serialisation. As printed (`indent=2`) it is 2,120, 00's figure.
   - E R1.
4. **A1 §10 I3 and §12, an omission.** "The whole" says the bin's lines only "gain ledger lines in text and `assumptions`
   in JSON". But A1's `cli.run` records every scripted stage run into `<project>/.spark/state.json` (A1 §3.6), and
   `board` is run by `boards.py --resolve` (A1 §4.1). The bin's `make` runs `--resolve` (E bin `Makefile`, the
   `--resolve > /dev/null` line A1 cites), and the bin tracks `.spark/` (E `git ls-files .spark` in the bin). So every
   `make` writes a new file into the bin's tracked folder. No row of A1 §12 lists this.
5. **A2 §2 U4: "spark's own [promise]: Python 3.9+ and nothing outside its standard library, E `docs/guide/agents.md:70`,
   `README.md:85`".**
   - `README.md:83-88` says "Python 3.9 or newer" and Node, nothing about the standard library.
   - `agents.md:70` states the promise with an exception that A2's sentence drops: "except `flash_image.py`, which needs
     `littlefs-python`".
6. **A2 §1 and §9, and A3 §2.1 and §9 item 9: "the 19 early returns" of `check_spine.run`.** `run` (`:319-505`) holds 19
   `return stages + […]`. The last, at `:504`, is the success return, so 18 are early (E my count). The count comes from
   00.
7. **A3 §2.2 L6 and §12 risk 1 cite `tests/test_boards.py:312-372` for the bin's command-line test.** The class starts
   at `:314` (E `grep -n "class TheCommandLine" tests/test_boards.py`). Part 1 has the same off-by-two. Trivial.

Checked and found right, for the record (E each read or run): A1's M3 counts; `boards.py:537-539`, where a missing
selection exits 1 after printing to stderr; `boards.py:150-152`, the rule that writes never fall back; `boards.py:67`
`REQUIRED_FOR_FAB`; `boards.py:391-399`, where `--for-fab` checks only that `footprint_module` and `footprint_export` are
present, which is consistent with A3's run 2; `check_vendor_pins.py:230` `mismatch`; `check_spine.py:358-361`, which
always passes `--assume-missing-sizes`, and `:374-375`, where stderr becomes PROBLEMS; `check_spine.py:546`, the header;
`check_spine.py:216-221` `CONVERTER_HAS_NO_PART`; `check_all.py:59`, `:428-441`; `outcomes.py:65-74`, envelope 1;
`parts.py:233` `Answer`; `:1553-1558` `_Parser`; `:2198-2201`, the lock for writes and the `globals()` dispatch;
`parts.py:98`, `:107`, `:834`, `:899`, `:909`; `store.py:27-30`, `:71-81`, `:96`, `:273`; `sim_project.py:173-176`; the
`wokwi-mcp` row in `data/tools.json`; `emit_board.py:1063-1066`, A3's run-1 sentence; A3's 43 part facts, of which 34 are
`verified: true`, 9 `false` and 0 carry `origin`; the bin's `Makefile:12-13` (A2's quote), `:28-32` (A3's "private
repository") and `:49-53` (A1's five captures); A2's 154 anchor rows on the chain's scripts (the sum of 00's per-script
counts); and each approach's §11 counts (R3).

## Searches

None: no web or MCP search. Read-only `gh issue view` for the cards listed under "What I read".

## Found on the way

- E · **The three approaches publish three different closed vocabularies.** `kind`: A1 has 6 (A1 §3.2); A2 has 8,
  adding `decision` and `busy` (A2 §3.1); A3 has 8, adding `fact` and `placeholder` (A3 §3.3). Fidelity ladders: A1 is
  placeholder/unstated/stated/checked/proven (A1 §3.3); A2 is placeholder/stated/datasheet/measured (A2 §3.4); A3 is
  owed/assumed/stated/checked/proven (A3 §3.4). Envelope 2 publishes whichever is chosen in its first iteration, so the
  plan must fix one before I1 (D9).
- E · **`check_spine` always passes `--assume-missing-sizes` (`check_spine.py:360`), and the chain's output then never
  names an assumed outline.** The only declaration is a comment inside `board.tsx` (`emit_board.py:591`); nothing goes
  to stderr, and so nothing reaches the verdict. Part 1's K47 (`catalogue.md:83`) names the flag and CH-37 carries K47;
  whether any CH makes the verdict name an assumed outline is — (`grep -c assume-missing-sizes proposal.md` → 0).
- E · **The bin tracks `.spark/`.** `git ls-files .spark` in `~/Development/smartbin-local` lists `board.json`, two
  `cache/*.pins_arduino.h`, `project.json` and `rules.json`. Any design that records runs under `<project>/.spark/`
  writes into a tracked folder of the bin; A2 alone puts its state in a self-ignored subfolder (A2 §3.3).
- E · **`boards.py --validate --for-fab` checks only that two `physical` keys are set (`boards.py:391-399`).** This
  confirms A3's run 2 by reading the code: an invented header passes. A3 already lists the finding.
- E · **00's "19 early returns" counts the success return** (`check_spine.py:504`); 18 are early. A2 and A3 inherit the
  number.
- E · **A2 cites `README.md:85` for a standard-library promise README does not make** (`README.md:83-88`).
- E · **The reproduction in `<scratch>` matches 00 to the byte.** `assign_pins.py --json` on the documented example
  outside a project printed 6,446 bytes, began with a 174-byte note before the JSON, and exited 0 (R1).
- H (my reading of the three §10s) · **Reopening or citing #11 (P43, closed with its value lines unmet) comes up three
  times as a decision** (A1 §10 I1, A2 §10 I1, A3 §10.3). It should be asked once, at I1 (D11).
