# P1199 pre-analysis: is the breadboard planner and router well made, and what does a layout core in mm reuse?

Step 1 of the PO's cycle for [P1199 #1747](https://github.com/xmejkal/spark/issues/1747). Read on 2026-11-26 at
821eb588 (origin/main) by the layout-core session. This file judges the code. It decides nothing.

> TL;DR. The breadboard planner and its router are well made for one job: a drawn breadboard in Wokwi's px. They are
> pure, they refuse with codes, they break ties by rank and not by float, and 181 tests pin them. They are not yet a
> core. Three layout engines exist and share no code: the breadboard planner (px), the PCB's first-draft placement
> (mm, a fixed column) and tscircuit's autorouter. The perfboard has none. The parts a mm core reuses as they are:
> the hole group, the ledger, the body box, the turn, the three strategy interfaces and the A* track search. The parts
> that need a change: the unit, the Surface's breadboard words, the placement's single strategy with no goal, keep
> moves as a subclass, and the missing Operation and setting.

## 1. What exists today

```text
                       circuit.json, the steps (wiring_steps)
                                    |
           +------------------------+-------------------------+
           |                        |                         |
   BREADBOARD (px)            PCB (mm)                   PERFBOARD
   drawing.BreadboardPlanner   board_components.place()  (no code, P275 #311)
     Surface + HoleLedger        a fixed column,
     PartPlacement:              "Ordinal, not designed"
       FirstFitPartPlacement   tscircuit autorouter
       KeepMoves... (subclass)   (the traces, external)
     JumperPlacement:
       KeepMovesJumperPlacement
           |
   breadboard_scene.BreadboardSceneMaker
     JumperRouter: TrackJumperRouter (A*), LaneJumperRouter
           |
   renderers: WokwiBreadboardDiagram (breadboard.json), SvgBreadboardDiagram (breadboard.svg)
   check: drawing_match.DrawnNets (P279, the same-pins check)
```

| piece | where | what it does |
| --- | --- | --- |
| `Hole`, `Surface` | scripts/spark/breadboard/drawing.py:28, :106 | the holes of one board, each with a group (the holes joined inside the board) |
| `HoleLedger` | drawing.py:189 | the taken holes, a claim of a taken hole is refused with a code |
| `PartPlacement`, `FirstFitPartPlacement` | drawing.py:229, :249 | where a part goes and its turn: the first fit, left to right, no goal |
| `JumperPlacement` | drawing.py:240 | which holes the jumpers take once the parts are placed |
| `BreadboardPlanner` | drawing.py:328 | the steps in, a `BreadboardLayout` out |
| `BodyBox`, `BodySpacing`, `rotate` | scripts/spark/breadboard/spacing.py | a body as it lies, the free columns between bodies, a quarter turn |
| `JumperRouter`, `TrackJumperRouter`, `TrackRouting` | scripts/spark/breadboard/wire_routing.py:45, :168, :185 | each jumper's drawn way, A* on a half-pitch track grid |
| `KeepMovesFirstFitPartPlacement`, `KeepMovesJumperPlacement` | scripts/spark/breadboard/kept_moves.py:158, :262 | a person's moves in Wokwi kept across a rebuild |
| `DrawnNets` | scripts/spark/breadboard/drawing_match.py | the drawing joins the points of circuit.json and nothing else (P279, closed) |
| `place()` | scripts/spark/design/board_components.py:143 | the PCB's first draft in mm: the module down the left, the parts in a column |

The only caller of the planner is the build's sheet: `_plan_once` (scripts/spark/breadboard/sheet.py:290-325)
plans fresh, then plans again with the two keep-moves strategies. No Operation in the catalogue reaches the layout
(scripts/spark/operation_catalogue.py: no breadboard or layout table).

## 2. What is well made

- Pure and layered. The planner makes a value (`BreadboardLayout`), the scene maker makes the scene once, and each
  renderer only draws it (drawing.py:5-11, breadboard_scene.py:175-205). The router is swapped in the scene maker,
  "never in a view" (breadboard_scene.py:178).
- Strategy seams already exist: `PartPlacement`, `JumperPlacement` and `JumperRouter`, each with a default.
- Refusals are codes, each with one sentence (drawing.py:44-73). A caller never reads a message.
- Deterministic. The holes are ranked by letter, "never by float distance, whose ties would move a part"
  (drawing.py:132-138). Positions are rounded once (drawing.py:596-599).
- The router is honest about its limits. It counts the states it expanded (a budget a test pins in place of seconds)
  and the searches the budget cut short, "since such a stop is no proof that there is no way" (wire_routing.py:191-193).
  A jumper with no clean way is drawn dashed, and one with no way at all is named, not hidden (wire_routing.py:17-19).
- Its search is a sound A*. The estimate counts the cells and the bends the rest of the way must still take, so it
  never overestimates (wire_routing.py:261-270). It has costs for a cell, a cell off the board, a bend and a crossing.
- Tested. 181 tests in five modules pass in 62 s: test_wire_routing, test_breadboard_layout, test_breadboard_keep,
  test_breadboard_keep_jumpers, test_breadboard_match (`python3 -m unittest`, Python 3.10.0 from pyenv, 2026-11-26).

## 3. What keeps it from being a core

| # | the gap | evidence | what it costs a second surface |
| --- | --- | --- | --- |
| G1 | The unit is Wokwi's px. Hole centers, body boxes, the grid's step and the tolerance are px. The router imports drawing's private `_round_px`. | drawing.py:26-27, :145-148, wire_routing.py:26, data/wokwi-geometry.json (`pitch` 9.6, `tolerance_px`) | A perfboard or a PCB thinks in mm. Wokwi's pitch of 9.6 px is one 2.54 mm hole pitch, so the factor is one number (calculated: 2.54 / 9.6 = 0.2646 mm per px). |
| G2 | `Surface` speaks breadboard. Its constructor reads `letters_y`, `top_letters`, rails and rail blocks, and names groups such as `12t`. The gap ranking (`by_gap`) is a breadboard rule. Its own docstring says "on a perfboard later a single hole". | drawing.py:106-138 | The idea (a hole and its group of joined holes) fits a perfboard (a group of one) and a stripboard (a group per strip). The constructor does not. |
| G3 | One placement strategy and no goal. `FirstFitPartPlacement` takes the first turn and position left to right. Nothing chooses the smallest board or a spread. | drawing.py:249-297 | The PO's two goals (the smallest board, or spread over the whole board) have no seam to plug into. |
| G4 | The planner walks the sheet's steps. Parts are placed in step order, resistors in a special pass with a fixed length, and rails seated by sign. | drawing.py:338-372, :420-445 | A perfboard has no wiring order and no rails. The order and the resistor rule belong to the breadboard. |
| G5 | On a breadboard the router only draws. Which holes a jumper joins is chosen before it (`claim_free_hole`), and the route is a picture of a loose wire. | drawing.py:353-368, breadboard_scene.py:197 | On a perfboard the route is the connection. A bare wire along pads joins every pad it touches. A crossing needs an insulated jumper. Neighbouring pads join by a solder bridge (the PO's note on #311, 2026-11-26). The router's output becomes electrical, and the same-pins check must read it. |
| G6 | The router routes one jumper at a time, shortest span first, with no rip-up and reroute. A jumper with no way after three tries is not drawn. | wire_routing.py:218-225 | Fine for a picture. A perfboard needs every net joined, so a failed net needs a second pass (rip-up and reroute, or negotiated congestion, see research.md). How often a breadboard jumper falls back today: not measured. |
| G7 | Keep moves is a subclass of the first fit. It reads Wokwi's diagram format itself, and it finds the person's moves by a diff against a fresh plan. Because a resistor's id is its order, its place is kept only when it is legal for the new resistor. | kept_moves.py:89-149, :158-230, :233-255 | A new placement strategy (the smallest board) loses keep moves, since keep moves inherits from one strategy. It is also a second mechanism beside P1193's project timeline. breadboard.json carries no stamp (P1193 ★C15). |
| G8 | Two placements and two body models. The breadboard uses `BodyBox` in px from Wokwi's part sizes. The PCB uses `body_mm` from the part records and a fixed column. | spacing.py:21-44, board_components.py:12-18, :143-180 | "Nothing twice" fails today. 8 of 8 part records in `parts/` carry `body_mm`. Both board records carry `width_mm` and `height_mm` (`grep`, 2026-11-26). So a mm body model has its facts. |
| G9 | No Operation and no setting. The router's default is a constructor default in the scene maker, the placement's in the planner. No person or Claude can ask "move this part" or "plan for the smallest board" through the core. | breadboard_scene.py:186-187, drawing.py:332-336, operation_catalogue.py | The PO's rules (2026-11-26): every feature is an Operation that the CLI, Claude and later MCP reach. Every strategy is chosen by a setting with a default and a layer (P1194 #1740). |

## 4. What a stage-neutral layout core in mm reuses

The verdict per piece, for a later design to decide. "Keep" means the logic moves as it is, with only its unit
and names changed.

| piece today | verdict | as a core piece |
| --- | --- | --- |
| `Hole` (name, x, y, group, column) | keep, in mm | a hole on any surface |
| the group idea in `Surface` | keep | the holes the surface joins: a breadboard row, a rail, a strip, or one perfboard hole |
| `Surface`'s constructor | split | one maker per surface kind: breadboard from data/breadboards.json, perfboard from a drawer record (holes across and down, pitch, the PO's note 2 on #311), later a stripboard |
| `HoleLedger` | keep | the taken holes of one plan |
| `BodyBox`, `rotate` | keep, in mm | a body as it lies |
| `PartPlacement`, `JumperPlacement`, `JumperRouter` | keep as interfaces | one seam per strategy, chosen by a setting |
| `FirstFitPartPlacement` | keep as one strategy | beside a goal strategy (the smallest board, a spread) |
| the step order and the resistor pass in `BreadboardPlanner` | stays with the breadboard | the breadboard's own planner over the core |
| `TrackGrid`, `TrackRouting` (A*) | keep, with its costs as parameters | the router of every surface. Already in pitch units (the step is half a pitch), so only `_round_px` ties it to px |
| `KeepMoves...` | change | a decorator around any placement, fed by the kept moves of P1193's project timeline, not by a diff of Wokwi's file |
| `DrawnNets` (P279) | widen | the same-pins check over a layout's joined groups, which on a perfboard include the routes |
| the Wokwi and SVG renderers | stay at the edge | the only place px appears: px = mm × 96 / 25.4 |
| `board_components.place` | later, a client of the core | the PCB's placement draft as one more surface (the card's scope says "later") |

## 5. What this pre-analysis did not check

- How often a jumper falls back to a dashed way or to no way, over real projects. Not measured.
- Whether the router is fast enough for a perfboard of 30 × 70 holes. The budget is 60,000 states per search
  (wire_routing.py:207). No timing was run.
- Whether Wokwi accepts a part placed in mm and turned back into px with no drift. The tolerance is `tolerance_px` in
  data/wokwi-geometry.json. Not tested.
