# P1199 council: the tech lead, with the Physics lens

Opus, 2026-11-26. The lens agent is read-only, so it returned this report as text. The main session saved it
unchanged except for this line.

Read on 2026-11-26 at e138b9bd (branch p1199-layout-core), between about 13:00 and 13:27 CET. Measured on an Apple M1 with Python 3.10.0 from pyenv. Every scratch run patched code in memory or in a child process only. The tree was never changed.

## Findings

- TL-1 · Converting px to mm and back to px, just before the one rounding (`_round_px`), keeps every golden byte. All 9 of 9 goldens are byte-identical. Of 10,192 numbers (data/wokwi-geometry.json, data/breadboards.json, and every left, top and SVG decimal in tests/golden-breadboard), 0 change. · E measured. A scratch wrapper replaced `drawing._round_px` with `orig(v / K * K)`, K = 96 / 25.4, and ran each `golden_breadboard.CASES` entry through `golden_breadboard.run_script`, compared byte for byte with its golden. · supports only: a conversion at the edge, not a planner that computes in mm.
- TL-2 · An mm value stored with 3 decimals breaks the bytes, and 4 decimals keep them. Rounding the mm to 3 decimals changes 8,692 of 10,192 numbers. For example 26 px → 6.879 mm → 25.999 px. With 4 or 6 decimals, 0 change. Formula: the worst error is 0.00005 mm × 3.7795 px/mm = 0.00019 px, under the 0.0005 px that the 3-decimal px rounding hides. `footprint_emitter.pads` already rounds mm to 4 decimals (scripts/spark/design/footprint_emitter.py:261). · E measured, and calculated · supports only: a kept position in mm needs at least 4 decimals. A hole name needs no unit.
- TL-3 · A planner that computes in mm with plain floats changes 3 of the 6 goldens that exit 0 (variant C: holes, part corners and track points computed in mm, then turned into px). Today's px floats happen to settle two float ties in the code. (a) `HoleLedger.claim_free_hole` takes the rail hole nearest by float distance (drawing.py:215). Column 7, at 83.6 px, is exactly 48/5 px from rail holes 5 and 6. In px floats the distances tie and hole 5 wins. In mm floats hole 6 wins. Step 3 of breadboard-ok-c6 and breadboard-ok-module then says "hole 6". (b) `_along_the_holes` compares `x1 == x2` (wire_routing.py:364). On the full board, rail hole x is 102.80000000000001 and column hole x is 102.8. So today's goldens draw a zero-length doubled corner, `L102.8 46.2L102.8 46.2`: step 7 of breadboard-ok-firebeetle and step 9 of breadboard-ok-module. · E measured, and the `repr` of both floats printed · supports only: these two ties. The other px tolerances (spacing.py:45, wire_routing.py:96 and :102) flipped nothing in these goldens.
- TL-4 · Exact geometry with ties broken by rank keeps 7 of 9 goldens. The 2 that change differ by one SVG path each: the degenerate corner of TL-3(b) goes away. Exact rationals (`fractions.Fraction`) are too slow: 14.09 s against 0.41 s for button-light, and 11.03 s against 1.33 s for walk-c6. mm floats quantised to 6 decimals give the same 7 of 9 in 0.46 s and 1.51 s. That variant keys the nearest-hole choice on the rounded distance and makes the straight-leg test a rounded equality. · E measured, best of 3 child runs · supports only: no clean core keeps all 9 goldens. Either it reproduces a px float artefact or two goldens are re-accepted (Q1).
- TL-5 · The A* router is fast enough for a 30 × 70 grid at 10 to 20 two-pin connections, and stops joining all of them at 30 to 40. · E measured. The run called `TrackRouting` directly on a synthetic `Surface` of 2,100 holes. It had 6 bodies, random endpoints and seeds 1 to 3, with the breadboard rule set unchanged. Results:

| connections | time | states expanded | no way | drawn dashed | cut short by BUDGET |
| --- | --- | --- | --- | --- | --- |
| 10 | 0.15 to 0.59 s | 20k to 93k | 0 | 0 to 2 | 0 |
| 20 | 0.88 to 2.46 s | 134k to 372k | 0 | 3 to 9 | 0 |
| 30 | 2.64 to 4.85 s | 415k to 753k | 0 to 2 | 10 to 15 | 0 |
| 40 | 5.11 to 7.82 s | 796k to 1,215k | 1 to 9 | 16 to 20 | 0 to 2 |

  Each state cost about 6.5 µs (calculated). Supports only the search cost on that grid. Random endpoints are harsher than a placed circuit. A net of k pins is k − 1 connections, so 10 to 20 nets is about 15 to 40 connections (H).
- TL-6 · The breadboard router's model does not fit the back of a perfboard. Its wires run on odd cells between holes, and every hole cell is blocked (wire_routing.py:6-11, :141). On a perfboard a bare wire lies on the pads and joins every pad it touches, and there is no room between two pads (EP-3). The perfboard therefore needs a second grid model behind the same `JumperRouter` seam: routes on the pad lattice, any pad of another net blocked, and a crossing priced as an insulated jumper. The search, the costs and the budget can be reused. The route then becomes a connection, so the same-pins check must read it. Today `DrawnNets` joins only jumper ends and `joined_pins` (drawing_match.py:44-51). · E code read, and EP-3 calculated.
- TL-7 · The smallest version that joins every net, or names the one it could not, has three steps. First, one A* pass on the back, shortest span first, as today (wire_routing.py:218-225). Second, every connection that fails gets an insulated jumper on the parts side between its holes, or between free holes beside them joined by a bridge. That needs only two free holes. Third, a connection is named, with a code, only when no free hole is near an end. Rip-up and reroute, or PathFinder, only lower the jumper count. They are a later strategy behind a setting. · H: the tech lead's reading, from the PO's three joins (#311 note 3) and perfwire's jumpers that "land in free holes next to their target" (research.md:54) · supports only: completeness. The jumper count needs spike B.
- TL-8 · A goal placement over the existing ledger is S if it is greedy. Split `FirstFitPartPlacement.place` (drawing.py:265-297) into a generator of legal candidates (turn, corner, holes, covered holes) and a chooser. The chooser takes either the first candidate (today) or the one with the least cost, the candidate's rank breaking ties. "Smallest" costs the bounding box of the claimed holes in whole pitches. "Spread" costs the negative of the smallest gap, in pitches, to the bodies already placed on a board of fixed size. Integer costs give the same bytes for the same input, with no seed. Two blockers: (a) the planner hands each part `after` from `BodySpacing` (drawing.py:408-418), which forces left to right, so a goal on the breadboard must take over the spacing. (b) `place()` gets no nets, so no cost can count wire length. · E code read. The costs are H.
- TL-9 · Scoring every candidate needs a hole index first. `Surface.hole_at` scans every terminal hole (drawing.py:145-148): 59.6 µs on 2,100 holes. One 2-pin part tried at every hole and turn costs about 1.0 s, and a 14-pin board about 7.0 s (8,400 candidates × pins × 59.6 µs). `group_is_free` also scans every hole (drawing.py:206-207). A dict by grid cell and by group makes both lookups constant time. · E measured, and calculated.
- TL-10 · Annealing is M. It needs a seam that places the whole plan and then moves and swaps parts, which the per-part `PartPlacement.place`, called in step order, does not give. A keep decorator fixes the kept parts in `reserve_first` (drawing.py:232-234). A fixed seed holds only if the random generator is spark's own, or if only `random.random()` is used. Python promises only `seed()` and `random()` across versions (H: model knowledge of the Python docs, not read today). Which Python version spark pins: —.
- TL-11 · Turning keep moves into a decorator is S to M. `KeepMovesFirstFitPartPlacement` uses only `super().place`, FirstFit's private `_covered` and `self.geometry` (kept_moves.py:158-230). A decorator `KeptPlacement(inner, kept)` claims the kept parts, then calls `inner.reserve_first`. It calls `inner.place(…, after)`, then `inner.place(…, 0)` as a fallback. Five tests break, all by name: the 3 that `mock.patch.object(KeepMovesFirstFitPartPlacement, "place")` (tests/test_breadboard_keep.py:272, tests/test_breadboard_keep_jumpers.py:194, :202), and the 2 that call `FirstFitPartPlacement(GEOMETRY)._covered` if `_covered` moves (test_breadboard_keep.py:226, test_breadboard_keep_jumpers.py:108). The constructor call in sheet.py:315 also changes. The other 58 of the 63 tests (24 + 39) go through `sheet.write` and test behaviour. · E code read, and a grep count.
- TL-12 · Feeding keep moves from a kept edit is M, and it changes three behaviours that tests pin. (a) Today a move is found by comparing with a fresh plan, so a move to the place spark would pick is not seen as a move (kept_moves.py:233-255). As a fact, it is a move. (b) A resistor's id is its order, so a fact about "R1" can later name another resistor (kept_moves.py:13-15). The fact needs a stable key, such as the row or net it joins. (c) A kept jumper keeps Wokwi's route strings as they are (kept_moves.py:304), which ties it to px. The fact needs grid cells or no route. The exact shape is (part id, anchor pin, hole name, turn): a hole name needs no unit (TL-2). The Wokwi paste round trip can stay as an importer that turns an edited breadboard.json into facts. `pin_holes` (kept_moves.py:152-155) already maps px to holes. · E code read. The shape is H.
- TL-13 · With edits kept as facts, breadboard.json becomes a pure build output again. P1193 then needs no stamp on it (its ★C15) and no second mechanism: the edits record is the kept step. A take-back restores the record, and the next build plans again. · H: the tech lead's reading of the P1193 brief, lines 18 (D-d, "build outputs and the page are made again") and 117 (D6, "the person's layout files kept only with a stamp at slice 5"), and items.md:56 · needs P1193's kept-record slice, after its A2 spike (D16).
- TL-14 · No Operation reaches the layout, and the breadboard area has no OPERATIONS table. breadboard.py parses its own arguments with argparse (scripts/breadboard.py:43-60). The catalogue has no breadboard table (operation_catalogue.py:27-28). The sheet and its drawings are written by `BuildBoard` through kept_files (kept_files.py:251-262) and by breadboard.py. Four Operations fit operation.py as it is:

| op (name H) | arguments | effects | what it touches |
| --- | --- | --- | --- |
| show-layout | --project, --json | READS | the last build's layout: parts with holes and turn, jumpers with holes, not-kept codes, all in hole names, not px |
| plan-layout | --project, --goal (choices first-fit, smallest, spread; default from the setting) | READS, WRITES | breadboard.json, breadboard.svg, the sheet |
| move-part | --project, --part, --to HOLE, --turn (0, 90, 180, 270), --check | READS, WRITES | the edits record (a kept step), then the drawings again |
| move-wire | --project, --step N, --from HOLE, --to HOLE, --check | READS, WRITES | as move-part |

  A web page's batch of moves fits `Argument.payload` (operation.py:21-23) as one kept step. `written_project` (operation.py:108-112) returns the project, so the page is written again (P1069). The table goes into `TABLES` after "build". The effect word for a kept step is P1193's: —. · E code read. The names are H.
- TL-15 · The move Operations can give the reason before writing, which the Claude journey lacks today (jobs-and-journeys.md:60). `_keep` (kept_moves.py:186-215) already returns (code, message) for one part on a ledger. `--check` plans with the one new fact and prints that code. · E code read.
- TL-16 · An mm part model already exists for boards and modules drawn from their records. `part_shape.PartShape` holds the size and pins in mm, taken from `footprint_emitter.pads`, and `project_to_px` rounds them to px at 3 decimals (part_shape.py:23-38). The Wokwi parts (LED, resistor, button, XIAO) exist only in px (data/wokwi-geometry.json). The PCB's `place()` reads `body_mm` (board_components.py:12-30). So the core reads PartShape and `body_mm`, and converts Wokwi's px once. · E code read.
- TL-17 · 43 lines in the six modules that would form the core name px (grep). Five px literals carry the unit: `tolerance_px` 1.5 (drawing.py:158), `LEG_CLEARANCE` 2.5 (wire_routing.py:205), 0.5 (wire_routing.py:96, :102) and 0.01 (spacing.py:45). They feed the slice costs under question 6 below. · E grep.

### Cost per slice (sizes H, the tech lead's estimate from the code read)

| slice | size | depends on |
| --- | --- | --- |
| 1 exact geometry: break ties by rank (drawing.py:215), quantised equality (wire_routing.py:364), re-accept 2 goldens after reading the diff | S | — |
| 2 hole and group index, candidate generator, greedy smallest and spread, the goal setting | S to M | 1 |
| 3 the unit: one Surface maker per surface kind, Hole in mm, px only in the renderers and the Wokwi reader | M | 1 |
| 4 keep moves as a decorator fed by an edits record, plus a Wokwi importer | M | P1193's kept-record slice |
| 5 the breadboard area on the core, plus show-layout, move-part, move-wire | M to L | 4, and #94's breadboard PR |
| 6 perfboard record kind, surface, pad-lattice router with jumper fallback, same-pins check over joins | L | spikes B and C |
| 7 annealing with spark's own random generator | M | 2 |
| 8 web editors (P294's finding) | L | 5 |

### Spikes and what settles each claim

- Spike A (bytes in mm): done here as a scratch run (TL-1 to TL-4). To make it binding, it runs again against the real refactor.
- Spike B (perfboard router): pad-lattice A* with insulated-jumper fallback on button-light and one motor circuit. It counts connections joined, jumpers and seconds, against a pass line written before the run. Only a spike settles TL-7's jumper count and whether rip-up is needed.
- Spike C (the PO's board): calipers on FIT0193 (EP-4, EP-6).
- A read of the Python docs settles TL-10's guarantee about random numbers.
- A read cannot settle whether the PO wants "spread" on the breadboard, or how often he moves parts. That needs his account (Q3).

## Physics

- EP-1 · The currents that spark's records imply run from mA to about 1.5 A. No record holds a net's current. · E:
  - LED: 30 mA (datasheet-max, parts/led-red-5mm.json:76-79).
  - L9110S: 0.8 A per channel, continuous (stated, parts/l9110s-module.json `continuous_current_a`).
  - Speaker: 0.866 A RMS for 3 W into 4 Ω (calculated, √(3/4); the record's `why_it_matters`, parts/speaker-terminal.json).
  - FireBeetle 3V3 regulator: 1.5 A (stated, marked unverified; boards/firebeetle2-esp32s3.json `power.regulator_3v3_a`).
  - ESP32-S3 module peak: 0.355 A (stated, verified).
  - JST PH contact: 2.0 A (datasheet, parts/jst-ph-2-power-inlet.json).

  So a net's current must be derived from its largest consumer (calculated, no new rung).
- EP-2 · Below about 1.5 A, all three joins carry the current with negligible loss, so the join is a mechanical choice, not an electrical one. · calculated:
  - A 24 AWG (0.511 mm) bare copper wire has 82.1 mΩ/m. A 50 mm run drops 0.12 mV at 30 mA, 3.3 mV at 0.8 A and 6.2 mV at 1.5 A, and dissipates 9.2 mW at 1.5 A. 22 AWG drops 3.9 mV and 26 AWG 9.8 mV at 1.5 A over 50 mm.
  - A solder bridge 0.74 mm long, with a 1.0 × 0.5 mm cross-section, is 0.215 mΩ, or 0.32 mV at 1.5 A.
  - Inputs: copper 1.68e-8 Ω·m and Sn63Pb37 1.45e-7 Ω·m (H, handbook values, not read). AWG diameter by its definition, 0.127 × 92^((36 − n)/39) mm (calculated). The bridge shape is H.
  - Supports: no per-net wire-size rule for any part spark holds today. The "several amps" of #311 note 3 appears in no record. Wire ampacity above about 2 A is —.
- EP-3 · A bare wire cannot run between two pads on a 2.54 mm perfboard. With 1.8 mm pads (H, a typical size, not read) the gap is 0.74 mm, and a 24 AWG wire leaves 0.115 mm on each side (calculated). So back-side routes lie on the pad lattice (TL-6). The pad size of the PO's board is —.
- EP-4 · The PO's drawer holds one perfboard kind: DFRobot FIT0193, "ProtoBoard Pro - Double Sided (100x75mm)", count 2 (E ~/.local/share/spark/drawer/dfrobot-fit0193.json, read-only). Its record has no pitch, no hole counts, no pad size and no plating. At a 2.54 mm pitch it holds at most 40 × 30 holes (calculated: floor(100 / 2.54) + 1 and floor(75 / 2.54) + 1, with no margin). The brief's 30 × 70 example is bigger than his board.
- EP-5 · The lead facts a layout needs, and where they are today:

| fact | where | value · provenance |
| --- | --- | --- |
| board header pitch, row spacing, pad, drill | boards/firebeetle2-esp32s3.json, boards/xiao-esp32-c6.json `physical.header` | 2.54 mm. Rows 22.86 and 15.24 mm, which are 9 and 6 pitches (calculated). Pad 1.5 mm, drill 0.9 mm (stated, from vendor drawings) |
| module rows | parts/max98357a-dfr0954.json:215 | 15.24 mm, 2.54 mm pitch (stated, in a `//` comment only) |
| LED leads | parts/led-red-5mm.json:43 | 2.54 mm (datasheet, in a `//` comment only) |
| JST PH pitch | parts/jst-ph-2-power-inlet.json `pitch_mm` | 2.0 mm (datasheet, verified) = 0.787 pitch (calculated): it does not fit a 2.54 mm board |
| button leads | parts/tactile-button.json:36 | only the footprint string "pushbutton". The common 6 × 6 pattern, 6.5 × 4.5 mm (H), is off-grid |
| resistor lead span | no record. The breadboard draws Wokwi's legs (data/wokwi-geometry.json:5, :25) | 58.8 px = 15.557 mm = 6.125 pitches (calculated): a drawing convention, not a bent lead |
| perfboard pitch, pad size, hole counts | no record kind (#311 note 2) | — |
| a net's current | no record | derive from its parts (EP-1) |

  So the core needs a lead pattern in mm for each part. It exists for boards, is prose only for the LED and the module, and is missing for the button and the resistor. The core must also refuse, or warn about, a pitch that does not fit the grid.
- EP-6 · The cheapest rung for each open physical question:
  - FIT0193's pitch, pad size and hole counts: calipers (measured, minutes) or the seller's page (document).
  - The button's lead pattern: the datasheet of the PO's bag, or calipers.
  - A resistor's lead span on a perfboard: a convention to decide, for example 4 pitches for a 1/4 W resistor (H). A decision, not a fact.
  - A net's current: calculated from part records.
  - A run above 2 A: no record reaches it, so it waits.

## What I could not check, and why

- Whether Wokwi opens a file planned in mm. I did not open Wokwi. TL-1's bytes are identical, so Wokwi gets the same input.
- A router on the pad lattice. No such code exists. TL-5 times the breadboard rule set as a stand-in.
- How many nets the PO's real perfboard projects have. No perfboard project exists.
- Python's guarantee for random numbers across versions. I did not read the docs.
- P1193's Operation and effect word for a kept step. I read only the lines cited above.
- The web editors, the UX and the hosting. Other lenses cover them.
- Real pad sizes, wire ampacity and the button's lead pattern. Web search was not among my tools.

## Questions for the decider

1. May two goldens (firebeetle, module) change by one SVG path each, removing a zero-length doubled corner? · decides slice 1 and whether the mm core is clean · options: (a) accept after reading the diff, (b) reproduce the px float artefact · I would pick (a).
2. What unit does a kept edit use? · decides the edits record and the Operations' arguments · options: (a) a hole name and a turn, which is exact, (b) a position in mm with at least 4 decimals · I would pick (a).
3. Where do the goals apply first? · decides slice 2 and P953's 4-column body gap · options: (a) the perfboard gets goals and the breadboard keeps first fit, (b) the breadboard gets "fewest columns" too, and the goal may override the body gap · I would pick (a).
4. How complete must the first perfboard routing be? · decides slice 6 and spike B · options: (a) one pass plus an insulated-jumper fallback, with rip-up later behind a setting, (b) rip-up from the start · I would pick (a).
5. What happens to a part whose pitch does not fit the grid (JST PH 2.0 mm, the 6 × 6 button)? · decides the perfboard check · options: (a) refuse it with a code, (b) plan it with a bent-lead note · I would pick (a).
6. Do these settings, defaults and layers stand until P1194 holds them? · decides the setting names · proposed:
   - `layout.placement`: first-fit, smallest or spread. Default first-fit. Project layer, then user.
   - `layout.router`: track-astar or lane. Default track-astar. Project layer.
   - `perfboard.second_pass`: none or rip-up. Default none. Project layer.
   - `perfboard.pick`: smallest that fits. User layer.
   - The annealing seed: a code constant, not a setting.

   I would pick these as proposed.

## Searches

None. This lens had no web search tool. The physics constants in EP-2 and EP-3 are tagged H for that reason.
