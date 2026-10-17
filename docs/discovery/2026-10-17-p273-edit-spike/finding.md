# P273 spike: a person's breadboard edit across a rebuild

> **Pass, 3 of 3.** A throwaway merge rule kept a moved part and a moved jumper across a real rebuild after a
> requirements change. It named every edit the new circuit did not hold. The real build needs one placement strategy,
> which the planner already takes, and one jumper step after the plan.

[P273, #309](https://github.com/xmejkal/spark/issues/309), D11 of [the P269 brief](../2026-10-16-p269-views-and-editors/brief.md).
Pass line, set 2026-10-16: in 3 of 3 cases the edit survives a rebuild after a requirements change, or is named.

## How it ran

[prototype.py](prototype.py) is spike code. Nothing in `scripts/` or `tests/` imports it, and it calls spark's planner
unchanged. All runs used copies of `tests/data/breadboard/button-light-xiao` in a scratch folder, a scratch
`SPARK_HOME` and `python3 -I`. The rebuilds were real: `check_spine.py requirements.json --keep .` built the button
alone, and the fixture's circuit is the build with both parts. A copy of `breadboard.json` with changed coordinates
and holes stood in for a Wokwi edit. Each run compares the merged diagram's connections with a fresh plan's.

## The cases

| Case | Earlier diagram (the edit) | Rebuild | Output | Verdict |
| --- | --- | --- | --- | --- |
| a, moved part | button only, button moved 4 columns right (`left` 105.8 to 144.2), its jumpers left in the old rows | LED added | button kept at 144.2. LED and R1 placed after it. Both stale jumpers named ("one end is in a row that holds no pin") and routed to the button's new rows. Connections equal a fresh plan | pass, survives |
| b, moved jumper | both parts, D10 jumper end moved from `14t.a` to `14t.b` with route `["v-20","h40"]` | LED removed | jumper kept as `6b.j-14t.b` with its route. Three LED jumpers named ("the new circuit does not join R1:1 and board:D8") | pass, survives |
| c, broken edit | both parts, LED and R1 moved 3 columns right with their jumpers | LED removed | "LedRed5mm: not in the new circuit", same for R1 and its three jumpers. Button and D10 jumper kept | pass, named |
| c2, extra | button's type changed to one spark has no geometry for | LED removed | "TactileButton: its Wokwi type changed", button placed fresh, its jumpers named | pass, named |

## The merge rule

1. Read the earlier `breadboard.json` into parts with holes and jumpers with holes and route.
2. Reserve each earlier part whose id and Wokwi type are in the new circuit, before any other part goes in. Its pins
   and the holes its body covers must be free. Each pin of a part other than a resistor needs a row of its own.
3. A resistor keeps its place only when its joined leg is still in the row it joins.
4. Place every other part by spark's first fit.
5. Know a jumper by what its two rows hold, as `{"board:D10", "TactileButton:1.l"}`. Give a new jumper the earlier
   holes and route of the jumper with the same ends, when those holes are free and in the rows the new plan gives.
6. Name every earlier part and jumper the new diagram does not keep, and why.

## Identity across builds

- A part keeps its id: `emit_board.component_name(part)` gives `TactileButton` (scripts/breadboard.py:370), and the
  board is `board`.
- A resistor does not. Its id is `R` plus its order in the circuit (scripts/breadboard.py:341). A new part that asks
  for a resistor renumbers the others. The circuit's own name (`LedRed5mmSeriesA`) is stable.
- A jumper has no id in Wokwi. The prototype names it by the two part pins its rows hold. A jumper to a free row (a
  board pad set up on its own) has no such pin, and this fixture has none, so that case is untested.

## The hook the real build needs

- `scripts/breadboard_drawing.py:148` `PartPlacement` is already a strategy, and `BreadboardPlanner` takes one
  (scripts/breadboard_drawing.py:225). A `KeepEditsPlacement` fits there with no change to `plan()`.
- Jumpers need one step after `plan()` (scripts/breadboard_drawing.py:227), and `Jumper` needs a `route` field
  (scripts/breadboard_drawing.py:31). Today `render()` writes every route as `[]` (scripts/breadboard_drawing.py:332),
  and the SVG draws its own path.
- `scripts/breadboard.py:377` `_plan_layout` must read the earlier `breadboard.json` before `write()`
  (scripts/breadboard.py:438) overwrites it. Today every build writes the file from scratch.

## Risks

- A kept part far to the right pushes new parts right, because the planner starts the next part two columns after the
  last one placed (scripts/breadboard_drawing.py:235). In case a, R1 reached column 28 of 30. Free rows for board
  pads come after the last part too (scripts/breadboard_drawing.py:249).
- A jumper's color is its step's color. A person's new color is lost, because step numbers change on a rebuild.
- The first prototype forgot the holes the board's body covers, and jumpers landed in holes under the board. The
  connection check passed anyway. A real check needs the covered holes too.
- Moving a part in Wokwi leaves its jumpers in the old rows. Case a shows the rule names and re-routes them, but the
  person's edited diagram was miswired until the rebuild.

## What this spike did not test

- A real drag in Wokwi's web editor, and how the person brings the edited `diagram.json` back into the project.
- Wokwi's own route format beyond two waypoints, and a jumper whose end the person moves to another row.
- A rail, a jumper to a free row, two parts of one record, and a rotation the geometry file has not measured.

## Recommendation for the story's plan

Smallest first slice: keep moved parts only. Add `KeepEditsPlacement` (reserve, then first fit), read the earlier
`breadboard.json` in `_plan_layout`, and print each dropped part with its reason. Test it with case a and case c on
this fixture. The second slice keeps jumper holes and routes and adds `route` to `Jumper`. Resistor ids by circuit
name come before any slice that adds a part with a resistor.
