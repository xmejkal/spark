# P323 council, tech lead (fit and consistency)

> **TL;DR.** Keep the target small: one outcome shape, one `main`, small Services, role-named classes, records as data. Do not rebuild the 2026-10-10 design (seven units, 108 cards, 21 decisions). Refactor by a rule inside each feature story, never as a block before walk 1. Judge it by six testable lines at the end.

## 1. What the architecture must serve

Backlog items it makes cheaper (numbers from the 2026-10-18 backlog):

- **AI-first `--json` (10, 11, and the "Claude's calls" table).** One envelope from `outcomes`, one thin `main` per script. Today 2 of 16 `--json` scripts print it. This is the biggest win, and it is the same work as fat-CLI removal.
- **`loop_status.py` (13).** Needs each stage to answer "done, stale or missing" from files. A stage table as data makes it a read, not a new procedure.
- **Change by words (14) and variants (23).** Need `requirements.json` edits to go through one small class that validates, not hand edits. This is the "record contract as one table" idea.
- **Rebuild lists (3) and the page (16, 17, 18, 19).** Need build in process, not a subprocess, so the planner's result (steps, moves, holes) is a Value that CLI, page and Claude all read. `check_spine.run` as a `BuildService` gives that. Renderers already exist, so the page is one more Renderer.
- **Console read (9), deploy gate by simulator grade (20).** Already sit on `FirmwarePlatform`, `ConsoleProbe` and the stand-in simulator. Keep these seams as they are.
- **Research and buzzer (15), RC car (22).** Need one validator for part and board records (`parts.validate` and `boards.validate` are two today) and public names for `_problem` and `_parse`.
- **Later firmware languages and MCP (v0.13).** `FirmwarePlatform` is the seam. MCP is a setting over the same envelope, built last.

Must not delay: walk 1 (items 1 to 5). No refactor may touch the build, sheet, look or deploy paths ahead of walk 1 unless a walk stall asks for it. Exception: refactors that are pure renames or constants and keep every output byte-identical.

## 2. Non-negotiables from AGENTS.md

1. The bar: each change moves a basic project nearer a breadboard with working firmware. A refactor must name the feature it makes cheaper.
2. Spark exports facts, never behaviour. No thresholds, timings, state tables or drivers in generated output.
3. One core, many interfaces. `main()` parses and prints. Agent prompts never repeat logic.
4. Records grow by need, with an origin. No speculative fields.
5. Free, few, local. One tool per job. No new service. No heavy install.
6. Public MIT. No vendor files, home paths or GPS photos. Sources cited with URL, version, page, sha256.
7. Spark is the product. A change does not update demo projects. A fixture is part of the change.
8. Plans shrink with distance. Refine only Ready and the next slice.
9. Journey current: the README table and `tools/journey.py` move in the same PR.
10. From the rules file: simple and small, one step at a time, new code is small classes, names say the role.

## 3. The 2026-10-10 design: what holds, what to drop

**Holds.**
- `outcomes` as the one answer shape in text and JSON, and one exit contract (0 ok, 1 problems, 2 could-not-run). A `could-not-run` or `skipped` is never a pass.
- One `main` helper (`cli`), so the exit contract lives once.
- Records as data with one table per record kind, read by validator, docs and editor.
- The assumption ledger idea (placeholder, stated limit, unverified fact) reaching the final verdict. Keep it as a field in the envelope, not a new unit, until a story needs it.
- "A mistake lands in one named place with one named reason."
- Two lanes (layer and fix), with a baseline run before output-changing work.
- The lesson on documents: length budget, short version, pointers instead of whole files.

**Drop.**
- The 108-card plan, card-day estimates and the 21-decision list. They lapsed and cost 45M tokens.
- `state` and the full build graph with staleness (`.spark/state/`, `stages.json`) as a first step. Take only what item 13 needs: derive done, stale or missing from files, no stored state.
- `where` as a unit of its own at first. Store and project paths already live in `store.py`. Add `where` only when a second place needs it.
- Generic board and fidelity levels (I5). Parked with the PO's own parking of unknown boards.
- The MCP face and the eval suite as iterations. Keep as the last slice, on trigger.
- A rewrite. P322 shows the good parts (deploy, breadboard drawing) already follow the target. Spread that pattern.

## 4. One vocabulary

Each term has one meaning. A name in code, docs, prompts and JSON uses it and no synonym.

| Term | One meaning |
|---|---|
| record | a JSON file of facts with an origin (part, board, chip) |
| part | a module or component record the drawer or library knows |
| board | the dev board record (chip, pins, power, physical) |
| drawer | what the person owns, in the store |
| store | the person's local folder (SPARK_HOME), never the repo |
| project | the person's folder with requirements, firmware, sim |
| requirements | the file that lists board and parts for a build |
| design | the netlist and pin map derived from requirements |
| build | requirements to design, sheet, diagram, checks |
| sheet | `breadboard.md`, the wiring steps |
| page | `page.html`, the one page to wire from |
| check | one deterministic test of a design, answers an outcome |
| outcome | ok, problems, could-not-run, skipped, with a code |
| envelope | the JSON form of an outcome, printed by every `--json` |
| run | one simulation scenario execution, with a log |
| image | the flash image that passed the simulation |
| look | the read-only board inspection before deploy |
| grant | the person's yes, kept per board |
| deploy | erase, write and read back an image |
| gate | a rule that opens or refuses the next step |
| platform | the firmware language bundle (MicroPython now) |
| adapter | wraps an outside program behind spark's interface |
| strategy | a swappable class for one decision |
| service | the class that runs one flow's steps |
| renderer | turns a value into text or a file and decides nothing |

Rule: a new term is added here with its one meaning before code uses it. Two words for one thing is a bug found in review.

## 5. Where over-engineering would hurt

- **A package restructure with a big-bang move.** Moving 59 modules into a package before walk 1 breaks imports in the bin and the plugin install path. Move last, if at all, by re-export.
- **Plugin registries and dependency injection frameworks.** A module constant list (as `DRAWING_RENDERERS`) is enough.
- **An abstraction for a second implementation that does not exist.** No `Board` interface for Arduino until one is on the card. Seams exist today only where there are two real implementations or a test fake.
- **Base classes for records.** Records are data and one table, not an object hierarchy.
- **Ledger, state and graph units** (section 3).
- **Rewriting parts.py in one go.** 1,899 lines. Split by extraction as stories touch it.
- **Class share as a goal.** 16% in classes is not a defect. Functions that are pure stay functions. Measure roles and fatness, not class percent.

## 6. How the PO judges the design: acceptance criteria

1. **One envelope.** Every `--json` script prints `outcomes.envelope`, and one test runs each and parses it. Target: 16 of 16.
2. **Thin mains.** Fat CLIs go from 3 to 0 and no `main()` exceeds 40 lines, by `measure.py`.
3. **No private imports across modules** (3 to 0) and no outcome literals (10 to 0).
4. **Roles stated.** Every class names a role from developing.md's table (56/103 to all).
5. **Walk 1 untouched.** The walk-1 path works after every slice, and the bin's checks pass at each merge.
6. **A seam test.** A second board record, a second renderer and a fake firmware platform each plug in with no edit to their callers. One test per seam proves it.

Also testable: the vocabulary table has no term used with two meanings in a grep of the docs and prompts.

## 7. Refactoring beside feature work

- **Rule for each story.** Before the feature, one small refactor in the code the story touches, so the feature lands in the target shape. After the story, one small refactor (the PO's rule). Both in the same PR and under 50 lines of moved code where possible, else a separate PR the same day.
- **Boy Scout limit.** Only the files the story edits. No sweeps across unrelated modules.
- **Capacity share.** About one slot in four for refactor-only cards from P322's five (constants, public names, role words, fat mains, BuildService). Before walk 1: zero, except the byte-identical ones (constants, public names, role words), which take a free slot beside the order, like P296.
- **WIP.** Refactor cards count in the existing limits (2 per working stage, 4 in flight). No separate lane. One refactor card in flight at most.
- **Order.** 1 constants, 2 public names, 3 role words (all safe and S), then `--json` envelope per script as items 10 and 11 land, then fat mains as stories touch them, then `BuildService` with item 3 (rebuild lists), then record validators with item 14.
- **Gate.** Every refactor PR runs the P100 baseline outputs for the three projects and shows no change, and `measure.py` score moves the right way in the PR text.
- **Stop line.** If a refactor needs more than M effort or changes output, it becomes a feature card with the PO's yes.
