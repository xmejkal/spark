# Refuter report: P1199 layout core discovery

Opus, 2026-11-26, read on 1bf7a4af. The refuter agent is read-only, so it returned this report as text. The main
session saved it unchanged except for this header. Scratch work ran on `git archive` copies under the job folder,
which was deleted.

## The five verdicts that matter most

1. ★C11 is counted as evidence against A1, but it explains ★C10. You cannot see a move where no edit path exists. Brief line 96 and risks-and-tests.md lines 9 and 32 both make this mistake. A log of move wishes does not test the rival need: that his wired board stays put.
2. The folder ignores `bench_changes.py`. It already gives each step a stable key: "a resistor end by its job and end number, never its tag". It also says "the person picks their own free rows". That module is a rival to the premise. The proposed keys would also hold the same idea a second time.
3. The question numbers differ between files. risks-and-tests.md, items.md and story-map.md use the synthesis's numbers, and the brief and verification.md use the brief's. If the PO answers "Q3 (a)", the wrong items move.
4. `show-layout` gives "Hole names, no px" (synthesis.md:122), yet D-q5(a) says the page draws that JSON. The page would then need Wokwi's px geometry in JS, so the geometry would exist twice.
5. I reproduced ★C6 in part (TL-1, TL-2, the rank ties), but "9 of 9" is thinner than it sounds. 3 goldens are 2-line refusals and 1 (motor) draws no layout. So only 5 goldens draw a layout and 2 write breadboard.json. None of them holds a kept move.

## 1. The ★ claims

- ★C1 · partly. board_components.py:13: "Ordinal, not designed — they exist to produce something that does not overlap". But part_shape.py:23 says "from spark.design import footprint_emitter", so the breadboard draws a module with the PCB's pad code. Change "share no code" to "share no placement or routing code".
- ★C2 · partly. I reproduced the tests: "Ran 181 tests in 50.414s OK". But drawing.py:215 picks a rail hole by float distance: `min(free, key=lambda one: abs(one.x - x))`. TL-3 shows a float tie decides the hole there. So "break ties by rank" holds for placing parts only.
- ★C3 · partly. drawing.py:236: `def place(self, part_id, drawn, ledger, after=0, pinned=None):`, and measure.py:245: `PARAMETERS = 5`.
  - tests/architecture_baseline.json:48 already allows `FirstFitPartPlacement._fit` 6 parameters.
  - TL-8 fits a greedy goal as a chooser inside the per-part `place`.
  - Change "so a goal does not fit it" to "a goal cannot be a sixth parameter. A greedy goal fits as a chooser. Annealing does not."
- ★C4 · holds. wire_routing.py:141: "return self.within(cell) and cell not in self.blocked and cell not in self.holes". Also :205 "LEG_CLEARANCE = 2.5", and sheet.py:300 runs DrawnNets before the scene.
- ★C5 · holds, reproduced. wokwi-geometry.json:5: "the resistor's legs are 58.8 px apart, six pitches are 57.6". I read LED 10 px and button 67 px.
- ★C6 · holds where I reproduced it. tech-lead.md:10: "All 9 of 9 goldens are byte-identical."
  - Wrapping `_round_px` in px to mm to px left 9 of 9 goldens unchanged.
  - Storing mm at 4 decimals changed 0 goldens. At 3 decimals, 5 of the 5 drawn goldens changed.
  - Not reproduced: TL-3 and TL-4's 7 of 9, and the count of 10,192 numbers.
- ★C7 · could not reproduce. I wrote no synthetic surface. tech-lead.md:14 holds only as a citation.
- ★C8 · partly. kept_moves.py:172-173: "`reserve_first` claims each earlier part, in file order, whose id and Wokwi type are in the circuit, that is not a resistor". But the diff with a fresh plan (:244-252) only decides which parts are named, not which are held. Change "finds a move" to "names a move".
- ★C9 · holds. sheet.py:318-319: "except drawing.NotDrawnError: layout, default = fresh, kept_moves.NO_ROOM", and build_record.py:32: `OWN_FILES = ("board.tsx",)`.
- ★C10 · holds, reproduced: "listed 28 exist 23 bbjson ['reaction-game']". The period is missing. P273 has existed since 2026-10-17, about 40 days.
- ★C11 · holds. "There is no Wokwi diagram: Wokwi has no part for the board and epaper-2in9-bwr-mh-et-live. Use the picture." The misuse is in verdict 1.
- ★C12 · partly. README.md:127: "A breadboard wired from its sheet ran an e-paper clock on a FireBeetle 2 C6, `ready seen`, 2026-11-22 (P934)". The source shows one run worked. "Nobody is blocked" is the lens's inference, not the README's.
- ★C13 · holds. run_request.py:4-5: "The values of the step come from spark's own offer key, never from the request."
- ★C14 · holds. 8 of 8 part records carry `body_mm`, both boards carry `width_mm` and `height_mm`, and tactile-button.json:36 says `"footprint": "pushbutton",`.
- ★C15 · partly. The record says: "ProtoBoard Pro - Double Sided (100x75mm)", "count": 2.
  - The drawer also holds dfrobot-dfr0481.json, "Proto Board - FireBeetle Covers", count 1, function prototyping-board. The brief's "one perfboard" leaves it out, though his boards are FireBeetles.
  - The seller's page says only "standard 0.1" spacing" and lists mounting holes. It gives no hole count, so Q8 (b) cannot settle the count.
- ★C16 · partly. tech-lead.md:79: "26 AWG 9.8 mV at 1.5 A over 50 mm".
  - "Each loses under 7 mV" holds only for 24 AWG or thicker. A solder bridge is never 50 mm long.
  - My figure (H): 30 AWG wire-wrap gives about 25 mV.
  - 1.5 A is a regulator rating marked unverified, and EP-1 lists a JST PH contact at 2.0 A.
  - The conclusion (the join is a mechanical choice) still stands.
- ★C17 · partly. research.md:92 says four pages were read. Fritzing and DIY Layout Creator's licences come from an FAQ, a Debian copyright file and a wiki, not from a LICENSE file. perfwire's page, which I fetched, says "Placement goals (`--profile easy|analog|compact`)" and "`solver.py` places, wires, and audits". So perfwire does this epic's job. It is just not a library. It also has a NOTICE file to keep.
- ★C18 · partly. finding.md:8-9 says "**reuse** `diagram.json` as the one data file". D-q4(a) and D-q5(a) drop that point, yet both cite P294 as support.
- ★C19 · holds. measure.py:242 `MODULE_LINES = 600` and :510 `if lines > MODULE_LINES:`. `wc -l` gives 599.

## 2. What the brief dropped or overstated

- D-d overstates #311. It lists "Three join kinds" as already decided by the PO. #311 note 3 has him saying "I am not sure what the best practices are actually". The three kinds and "several amps" come from one search by the note's writer.
- The direction problem (synthesis:130) is missing from the brief. `surface_for`'s default builder makes `spark.layout` import `spark.breadboard`, and the breadboard imports the layout library. That is a cycle between the two packages. operation_catalogue.py:7-8 already has the seam for this: "a frontend that runs it hands the area's outside builder".
- The unit claim conflicts with Wokwi's half board. The half board's rails start at x 34 where the column lattice gives 35.6, and its rail rows are 10 px apart against a 9.6 px pitch. So "a position in mm is the cell times the pitch" (:76) cannot hold there.
- My control for scratch check 2 changed 2 goldens, not 3. Ties given to the last hole changed c6 and module only. The synthesis reports 3 of 9 (:85).
- Keying a join by its two ends (:110) is untested. wiring_steps.py:11 says "a jumper joins that row to the rail", so one end is a free row or a rail. The anchor of each point is also chosen per point, so ends can pair up differently after a circuit change.
- Q6 is not covered by the value test. On the full board today nothing is held: sheet.py:302 says "no Wokwi diagram is written, so no earlier one is kept". A log of move wishes misses the wish to keep things in place.

## 3. Rival explanations

- ★C10: no edit path on the board he used, and moves made on the bench itself. bench_changes says "the person picks their own free rows".
- ★C12: the perfboard is blocked by his own order. #311 note 1 says "the perfboard still comes after the editor that keeps moves". So waiting on this core means waiting on the perfboard too.
- A1's pass line: 3 drawn breadboards exist across 23 folders over about 40 days. "2 projects in 14 days" may be out of reach whatever the need.
- "181 tests pin": TL-11 says 58 of the 63 keep tests go through `sheet.write`. Those tests guard a refactor more than they block it.

## 4. Numbers missing a unit, population, period or provenance

- S, M and L have no unit.
- "62 s" has no machine in the brief. I got 50 s.
- "9 of 9" should say 5 drawn layouts.
- "1 of 23" has no period.
- "0.15 to 2.5 s" leaves out the M1 and Python 3.10 from the brief.
- "under 7 mV" has no wire gauge.
- "21.9 MB" has no version.
- "about five minutes" and "3 wishes in 14 days" have no source.

## Fit with the core and the PO's rule

- The surface kinds are listed three times: the `layout-surface` role, the `surface_for` builder and the `--goal` and setting members.
- A step number in the CLI is logic in an interface. The CLI would turn a step number into ends (synthesis:110). That belongs in the Operation.
- One edits record holds one surface kind. A project that has a breadboard and later a perfboard cannot keep both.
- What breaks for current users:
  - The rule that leaves breadboard.json alone goes (kept_files.py:429-431).
  - Nothing says what a build does to a hand-edited breadboard.json before the person says yes to the import.
  - A route drawn by hand in Wokwi is no longer kept.
  - Nobody measured the build's time.

Could not check:
- TL-3, TL-4, TL-5 and ARCH-11. I did not write the code to rerun them.
- Scratch check 1 (9,374 placements).
- The memory note behind D-h.
- The P1038 canvas, which needs a claude.ai sign-in.
- A source for wire ampacity.

## Searches

1. https://github.com/KeckuJp/perfwire
2. https://www.dfrobot.com/product-1214.html. This was the wrong product (FIT0400), so the fetch was wasted.
3. https://www.dfrobot.com/search-FIT0193.html
4. https://www.dfrobot.com/product-824.html
