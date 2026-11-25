# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item. -->

The cards come from the architect's synthesis (`council/synthesis.md` part 6) and the tech lead's TL-18. The numbers are spark-main's to give when it files them. Slice 5 (the store pages) and the paused work stay one line each in the epic until the PO orders them (plans shrink with distance).

## P?: a need with no fitting part has no way out on the page → the Parts moment offers "Ask Claude" to research a part the person names, with a sentence spark fills from its records (slice 0, the walking skeleton)
- type: story <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1697: "We should also have pages for editing records and possibly for researching when adding new parts"; and at the P934 walk, #1445: "what if it's not in the store ? I can still have it and want to add it" <!-- REQUIRED:needed-by -->
- value proven by: a walk row on the DFR0928 (in the drawer, count 1, no record): `flow.py show --json` lists the offer's key and its sentence for the need; after the research and `/spark:page` the part is a pick, and the board builds; `run_cost.py` counts the run <!-- REQUIRED:value-proven-by -->
- depends on: — (spark-main may refine P992 #1445 into this card in place of a new number) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: `--describe` hides that research asks and fetches, so no test can keep it off the page → `--describe` prints a word for an Operation that asks, lists `research-part`, and a test pins that no such Operation enters the page's allow-list (beside slice 0)
- type: chore <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, rules.md: "Every plan and every PR with new logic says how it fits the core" <!-- REQUIRED:needed-by -->
- value proven by: `parts.py --describe --json` shows `research-part` with its asks and network words; a test fails when an Operation that asks or fetches enters `STEP_OPERATIONS` <!-- REQUIRED:value-proven-by -->
- depends on: — (spark-main may fold it into P1082 #1587) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): chore <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: a fact nobody has checked is settled only when Claude writes a file by hand → the page offers "Ask Claude" for a picked part's unchecked facts, and the dry run names where the write lands (slice 1)
- type: story <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1697: "When I want to edit a record and change something there"; and 2026-11-22, #1461: "lets make it so that its always offering the new findings to be stored to the store in general" <!-- REQUIRED:needed-by -->
- value proven by: `parts.py --unverified dfr0664-tft-2in` prints 9 before and fewer after; each new fact holds a source that names who, when and how <!-- REQUIRED:value-proven-by -->
- depends on: the slice 0 story (the same flow change); the decider's Q5 and Q6 answers; absorbs P1002 #1461 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: a build reads current after a part record it read has changed → the build record stamps each record it read, and the build phase says out of date (slice 1)
- type: story <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1696: "Somwe files might need to be regenerated, etc."; and #1700: "what changes influence in later steps" <!-- REQUIRED:needed-by -->
- value proven by: a row from a real run: change one fact with `--fact-set`, and `flow.py show` names the build as out of date; build again, and it reads current <!-- REQUIRED:value-proven-by -->
- depends on: — (change 6 of the P1160 #1696 finding; the decider's Q7 answer sets its order) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: identify from photos starts only from a typed command, and nothing says what a photo can settle → the "Not here?" tile offers it with the way to shoot and a sentence spark fills (slice 2)
- type: story <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1697: "researching when adding new parts, based on photos" <!-- REQUIRED:needed-by -->
- value proven by: a walk row on one module with no known marking: the record passes `--validate` on the first try, with a size from a ruler shot (USER-14 names the four breaks to watch) <!-- REQUIRED:value-proven-by -->
- depends on: the slice 0 story <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: spike: nobody knows what a find by criteria returns or costs for a module → one real need run two ways, with the candidates and the tokens counted (slice 3)
- type: spike <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1697: "just finding online a part/board/module that could do what we need, setting up criteria" <!-- REQUIRED:needed-by -->
- value proven by: a finding with each way's candidates, their fits and lacks lines, and `run_cost.py`'s count for each run <!-- REQUIRED:value-proven-by -->
- depends on: the decider's Q9 and Q10 answers; its token cost named and asked before the run <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: a need with no part has no find, and a candidate not chosen is written by hand → "Ask Claude: find online" for a need, with the criteria read from the need, and a catalog write Operation (slice 3)
- type: story <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1697: "finding online a part/board/module that could do what we need, setting up criteria"; and in the P934 walk: "ask if I want it to search for alternatives online" <!-- REQUIRED:needed-by -->
- value proven by: a walk row: two candidates show before any record, and `parts.py --catalog` lists the one not chosen, written by the Operation <!-- REQUIRED:value-proven-by -->
- depends on: the slice 0 story and the slice 3 spike <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: spike: an edit is confirmed only in the chat, and a page read before a record changed would overwrite it → a staged edit that the page confirms by its key, with a check of the value it read (slice 4)
- type: spike <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1697: "pages for editing records" <!-- REQUIRED:needed-by -->
- value proven by: a finding with an experiment in a scratch folder: a stale page's confirm is refused, and P1122's test still passes <!-- REQUIRED:value-proven-by -->
- depends on: the slice 1 stories; P1152 #1688 for the kept step; only if the decider chooses B at Q2 <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: `--promote` copies a project's record into spark's own library and checks no `verified` flag, against the rule that the library changes only in spark's repository → promote refuses or names an unverified record, and research.md says what it does (found on the way)
- type: story <!-- REQUIRED:item-type -->
- needed by: the coordinator's rule (rules.md, "Suggest cards for found bugs"): a bug a review finds outside the scope becomes a proposed card; the code: scripts/spark/sourcing/part_facts.py:154-177 against commands/research.md:111-112 <!-- REQUIRED:needed-by -->
- value proven by: a test: `--promote` of a record with an unverified fact is refused or names it, and `parts.py --validate` on spark's library still passes <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): bug <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — (a bug outside P1161) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): ask the decider: v0.10 The basic journey or another <!-- REQUIRED:spark-process:slice -->

## Lines for the epic, not cards

- Slice 5, the store pages get a home (StorePart's "Not known yet", a drawer entry's edit, research with no project), after the decider's Q4 answer.
- Paused: board record edits (after P230 #218), pins on a picture (P276 #312), a numeric filter over records, a source-kind field per fact, a photo upload.
- Raised to P735 #1010's first step: the research agents write whole records with the Write tool, outside any Operation (synthesis M1).
- A chore when a slice touches the prompt: rules repeated across prompts (brief C20).
- Canvas fixes for the next canvas edit: StoreAdd's "every fact marked not checked", and StorePart's NOW card that sends two "not published" facts to a datasheet (brief C21, ★C16).

## Board actions
<!-- Each action, taken or pending, with its D. -->
- file the items above as sub-issues of P1161 #1697, each on its slice · pending: needs the decider's yes to this list, then spark-main files them <!-- REQUIRED:board-actions -->
- refine P992 #1445 into the slice 0 story, or close it as absorbed · pending: the decider's Q3 answer, then spark-main
- close P1002 #1461 as absorbed by the slice 1 story · pending: the decider's Q3 answer, then spark-main
- a comment on #1697 that links the brief · pending: spark-main, at the day close
