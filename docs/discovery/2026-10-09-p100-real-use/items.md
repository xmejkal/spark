# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

## P100's rounds as three stories under the epic (A owned parts, B new parts, C irrigation)
- type: story ×3 <!-- REQUIRED:item-type -->
- needed by: D6 (the PO, 2026-10-09) — each round has its own predictions, diary and pass line <!-- REQUIRED:needed-by -->
- value proven by: each round's diary with its predictions scored by someone who did not write them; A: `check_spine` exit 0 with every need on the board and the pass line observed on hardware; B: a cited record the person can read and a build using it; C: irrigation builds before and after its feature <!-- REQUIRED:value-proven-by -->
- depends on: Q3 (the board), Q1 (the pass lines) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P100 (#6) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 1b From a vague idea <!-- REQUIRED:spark-process:slice -->

## Irrigation's `check_all` FAIL since B13 (★C4, F1): four `must_not_float` entries on valve inputs the DFR0457 record calls an LED load — the rule or the project's data
- type: bug (or a data fix in irrigation)
- needed by: round C's baseline and the story map's scenario 4.2 ("no [FAIL]", marked yes on 2026-09-29; FAIL since spark 4daa58f of 2026-10-03)
- value proven by: `check_all.py --project .` on irrigation shows no `[FAIL]`, or its rules file says why a current-load input is not a CMOS input and the rule reads it — dated; the `check_spine` exit 1 (STATUS_LED) stays as documented
- depends on: —
- status: proposed
- label: bug
- parent: — (or P100 if round C takes it)
- slice: 4 v1 on two projects

## A silent pad merge: bare-number pad labels pass `--validate`, `--for-fab` and the footprint, then tscircuit joins 3V3 to pad "17" and GND1 to "15" (round 0, G0.3)
- type: bug
- needed by: anyone writing a board record from a vendor drawing whose pads are printed as GPIO numbers (the C6's are) — a short-class fault no check named
- value proven by: `boards.py --validate` refuses a `header_order` label that tscircuit would read as a pin number, with the rule in boards/README; the round-0 file with digit labels (`c6-digit-labels.json`, kept in the discovery folder's evidence) is refused
- depends on: —
- status: proposed
- label: bug
- parent: P100 (#6) — a round-0 finding
- slice: 4 v1 on two projects

## A live `check_vendor_pins.py` writes its cache into the PLUGIN folder, not the store (round 0, G0.7); a missing `SPARK_HOME` folder becomes a silent empty store (F5)
- type: bug ×2
- needed by: the store's one-home rule (P97) and the guard P164 asks for; the real store is the PO's
- value proven by: the cache lands under `SPARK_HOME` (or its path is documented) and `git status` in the plugin stays clean after a live vendor check; `parts.py` with a `SPARK_HOME` naming no folder says so and exits non-zero (or asks) instead of answering from an empty store
- depends on: —
- status: proposed
- label: bug
- parent: P164 (#?) or P178 (#123)
- slice: 1 Public

## Round 0's ten documentation gaps (G0.1–G0.10): the `physical` schema, `pad_aliases`, the `pin_roles` list, the stand-in's pins, repeated/NC pads, where a board's documents are kept, `emit_footprint.py --json`
- type: chore (docs) + one bug (`--json` prints TSX)
- needed by: "bring your own board" as documented — how-it-works.md:155-156 still says "this was not run for these docs"; round 0 ran it (council/round-0-runner.md)
- value proven by: a second person makes a board record from boards/README alone without hitting G0.1–G0.10; `emit_footprint.py --json` prints JSON
- depends on: —
- status: proposed
- label: chore
- parent: P100 (#6)
- slice: 2 Your own dev board

## The documented path to a running board (★C6): what a person does after `pins.py`
- type: story
- needed by: every round's pass line "firmware that runs"; P79 (#16, the bench step) owns the hardware half
- value proven by: a page a hobbyist follows from `pins.py` to code running on the FireBeetle (flash tool, port, the first line printed), run once
- depends on: P79's shape
- status: proposed
- label: story
- parent: P79 (#16)?
- slice: 5 A real stranger

## Four small defects from the user's walk (F2–F4, C10): the README idea block's missing `--step` marks; recorded outputs one version behind; `--tally` outside a session; `check_all` after a build exits 2 with inputs init leaves null
- type: bug ×4 (or one chore)
- needed by: a hobbyist typing the README (USER-14, USER-11, USER-12, USER-8)
- value proven by: the README block exits 0 as typed; the recorded blocks say 0.8.x; `--tally` says what it can count outside a session; `check_all` after `init` names what to fill
- depends on: —
- status: proposed
- label: bug
- parent: —
- slice: 1 Public

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- none taken for these items; pending the decider's yes to this list (core rule 8) — filing, sub-issues under #6, the slice for each · two issue comments WERE taken today for decisions, not items: #6 (D5, D6) and #123 (D8's requirement) — brief.md Board actions <!-- REQUIRED:board-actions -->
