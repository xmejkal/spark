# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item. -->

The cards come from the architect's synthesis (`council/synthesis.md` part 6) and the tech lead's TL-18, changed by the delegated council (D14, `council/delegated-answers.md`): six to file, one folded into P1082, two kept as epic lines. The numbers are spark-main's to give when it files them. Slice 5 (the store pages) and the paused work stay one line each in the epic until the PO orders them (plans shrink with distance).

## P?: a need with no fitting part has no way out on the page → the Parts moment offers "Ask Claude" to research a part the person names, with a sentence spark fills from its records (slice 0, the walking skeleton; P992 #1445 refined in place)
- type: story <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1697: "We should also have pages for editing records and possibly for researching when adding new parts"; and at the P934 walk, #1445: "what if it's not in the store ? I can still have it and want to add it" <!-- REQUIRED:needed-by -->
- value proven by: a walk row on the DFR0928 (in the drawer, count 1, no record): `flow.py show --json` lists the offer's key and its sentence for the need; after the research and `/spark:page` the part is a pick, and the board builds; `scripts/cost.py` counts the run on the main session's and the research agent's transcripts, summed,, because no command writes a research step that `run_cost.py` reads (★C9); the walk diary holds the A1 rows (D2, D3). The trigger also covers a pick that is a drawer entry with no record <!-- REQUIRED:value-proven-by -->
- depends on: the research run names its model and expected tokens before it starts, with no ask (D16); a test that the sentence carries only the chosen part's maker and part number (A9, D6); the drawer rule's new words read to the PO (D6). Filed as P992 #1445 refined in place, no new number (D5, D14) <!-- REQUIRED:depends-on -->
- status: filed D14, P992 #1445 (refined in place) <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: a fact nobody has checked is settled only when Claude writes a file by hand → the page offers "Ask Claude" for a picked part's unchecked facts, and the dry run names where the write lands (slice 1)
- type: story <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1697: "When I want to edit a record and change something there"; and 2026-11-22, #1461: "lets make it so that its always offering the new findings to be stored to the store in general" <!-- REQUIRED:needed-by -->
- value proven by: `parts.py --unverified dfr0664-tft-2in` prints 9 before and fewer after; each new fact holds a source that names who, when and how <!-- REQUIRED:value-proven-by -->
- depends on: the slice 0 story (the same flow change) and the stale stamp story (D9); its walk runs in the DFR0664's home project (D7); `SetFacts` names the project it wrote, so the page is written again; P1002 #1461 stays open and linked (D5) <!-- REQUIRED:depends-on -->
- status: filed D14, P1168 #1707 <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: a build reads current after a part record it read has changed → the build record stamps each record it read, in any layer, and the build phase says out of date (slice 1)
- type: story <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1696: "Somwe files might need to be regenerated, etc."; and #1700: "what changes influence in later steps" <!-- REQUIRED:needed-by -->
- value proven by: a row from a real run: change one fact with `--fact-set`, and `flow.py show` names the build as out of date; build again, and it reads current <!-- REQUIRED:value-proven-by -->
- depends on: — (change 6 of the P1160 #1696 finding). It merges before slice 1's offer ships (D9). Its plan names which copy of a record the build reads (A4), and what a build record written before the stamp reads as (the refuter) <!-- REQUIRED:depends-on -->
- status: filed D14, P1169 #1708 <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): spark-main chooses: build and core work does not fit "Views and editors" (D14) <!-- REQUIRED:spark-process:slice -->

## P?: identify from photos starts only from a typed command, and nothing says what a photo can settle → the "Not here?" tile offers it with the way to shoot and a sentence spark fills (slice 2)
- type: story <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1697: "researching when adding new parts, based on photos" <!-- REQUIRED:needed-by -->
- value proven by: a walk row on one module with no known marking: the record passes `--validate` on the first try, with a size from a ruler shot (USER-14 names the four breaks to watch) <!-- REQUIRED:value-proven-by -->
- depends on: the slice 0 story. Filed in Idea, unrefined (D14) <!-- REQUIRED:depends-on -->
- status: filed D14, P1170 #1709 <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: spike: nobody knows what a find by criteria returns or costs for a module → one real need run two ways, with the candidates and the tokens counted (slice 3)
- type: spike <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-11-25, #1697: "just finding online a part/board/module that could do what we need, setting up criteria" <!-- REQUIRED:needed-by -->
- value proven by: a finding with each way's candidates, their fits and lacks lines, and `scripts/cost.py`'s count for each run's transcript <!-- REQUIRED:value-proven-by -->
- depends on: D11, D12; filed in Idea (D14); its run names its model and expected tokens before it starts, with no ask (D16) <!-- REQUIRED:depends-on -->
- status: filed D14, P1171 #1710 <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1161 #1697 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P?: `--promote` copies a project's record into spark's own library and checks no `verified` flag, against the rule that the library changes only in spark's repository → promote refuses or names an unverified record, and research.md says what it does (found on the way)
- type: bug <!-- REQUIRED:item-type -->
- needed by: the coordinator's rule (rules.md, "Suggest cards for found bugs"): a bug a review finds outside the scope becomes a proposed card; the code: scripts/spark/sourcing/part_facts.py:154-177 against commands/research.md:111-112 <!-- REQUIRED:needed-by -->
- value proven by: a test: `--promote` of a record with an unverified fact is refused or names it, and `parts.py --validate` on spark's library still passes <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: filed D14, P1172 #1711 <!-- REQUIRED:item-status -->
- label (the repository's type label): bug <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — (a bug outside P1161) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): spark-main chooses (D14) <!-- REQUIRED:spark-process:slice -->

## Lines for the epic, not cards

- A line on P1082 #1587, not a card (D14): `--describe` prints a word for an Operation that asks, lists `research-part`, and a test pins that no such Operation enters the page's allow-list (brief C19).
- Slice 3, find online for a need: "Ask Claude: find online" with the criteria read from the need, two candidates before any record, and a catalog write Operation for the ones not chosen. Its shape waits on the spike's finding (D14).
- Slice 4, a staged edit that the page confirms by its key, with a check of the value it read. Only if the PO wants more than D4 (D14).
- Slice 5, the store pages get a home (StorePart's "Not known yet", a drawer entry's edit, research with no project), after the decider's Q4 answer.
- Paused: board record edits (after P230 #218), pins on a picture (P276 #312), a numeric filter over records, a source-kind field per fact, a photo upload.
- Filed by the PO's D17 as P1173 #1713 and P1174 #1714: the research agents write whole records and catalog records with the Write tool, outside any Operation (synthesis M1). The architect seat asks for a card of its own, a record-write Operation; the other two seats keep it in the find line. Also the misfit M3: the shelf and the catalog sit outside the Storage seam.
- A chore when a slice touches the prompt: rules repeated across prompts (brief C20).
- Canvas fixes for the next canvas edit: StoreAdd's "every fact marked not checked", and StorePart's NOW card that sends two "not published" facts to a datasheet (brief C21, ★C16).

## Board actions
<!-- Each action, taken or pending, with its D. -->
- file the new items above as sub-issues of P1161 #1697, each on its slice · D14 gives the yes (delegated); spark-main files them <!-- REQUIRED:board-actions -->
- refine P992 #1445 in place into the slice 0 story, and make it a sub-issue of P1161 · D5, D14; spark-main acts
- a comment on P1002 #1461 that links the slice 1 story; it stays open · D5; spark-main acts
- a line on P1082 #1587 for the describe guard · D14; spark-main acts
- a comment on #1697 that links the brief · pending: spark-main, at the day close
