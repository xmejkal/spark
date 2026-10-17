# P273 spike: a person's breadboard edit across a rebuild

> **2 of 3 strictly, 3 of 3 if a moved jumper counts for case c.** The prototype, run after a real rebuild, kept a
> moved part and a moved jumper. When the new circuit broke a moved jumper, it named it. No requirements change on
> this fixture broke a moved part's kept position, because the rule reserves kept parts before new ones go in.

[P273, #309](https://github.com/xmejkal/spark/issues/309), D11 of [the P269 brief](../2026-10-16-p269-views-and-editors/brief.md).
Pass line, set 2026-10-16: in 3 of 3 cases the edit survives a rebuild after a requirements change, or is named.

## How it ran

[prototype.py](prototype.py) is spike code. Nothing in `scripts/` or `tests/` imports it, and it calls spark's planner
unchanged. All runs used copies of `tests/data/breadboard/button-light-xiao` in a scratch folder, a scratch
`SPARK_HOME` and `python3 -I`. Real `check_spine.py requirements.json --keep .` builds made the button-only and the
LED-only projects. The fixture's circuit is the build with both. The real rebuild writes its own `breadboard.json`,
and the edit survives only in the prototype's output. A copy of `breadboard.json` with changed coordinates and holes
stood in for a Wokwi edit. `same_connections_as_a_fresh_plan` was true in every run, but it reads rows only. It
ignores holes under the board's body and checks no route. No merged diagram went through a simulation or a diagram
check.

## The cases

| Case | The edit | Rebuild | Output | Verdict |
| --- | --- | --- | --- | --- |
| a, moved part | button moved 4 columns right, its jumpers left in the old rows | LED added | button kept at its new place. LED and R1 placed after it. The 2 stale jumpers named and routed to the new rows | pass, survives |
| b, jumper in its row | D10 jumper end `14t.a` to `14t.b`, route `["v-20","h40"]` | LED removed | kept with its route | pass, survives |
| b2, jumper to another row | GND jumper end from the LED K row `17b.g` to the button B row `12t.c` | LED removed | kept as `8b.j-12t.c` with its route, because the new circuit joins GND to button B | pass, survives |
| b3, jumper to an empty row | D10 jumper end `14t.a` to `15t.a` | LED removed | named: "one end is in a row that holds no pin", and planned fresh | named, but the edit itself broke the point |
| c, new circuit breaks a moved jumper | LED, R1 and their jumpers moved 2 columns right | button removed | LED and R1 kept. The LED-only build moved the LED from D8 to D10, so the moved jumper `4b.j-26b.f` is named: "the new circuit does not join R1:1 and board:D8" | pass for a jumper |
| c-part, a moved part | LED moved 2 columns, R1 left where it was | button removed | LED kept. R1 named: "its leg 2 is no longer in row 20b, which it joins", and placed fresh | named, but the edit broke it, not the new circuit |
| removed (old c) | LED and R1 moved | LED removed | both named "not in the new circuit". This name ignores whether a part was moved | named |
| type | button type changed to one spark has no geometry for | LED removed | named "its Wokwi type changed", placed fresh | named |

## The merge rule

1. Reserve each earlier part whose id and Wokwi type are in the new circuit, before any other part goes in. Its pins
   and the holes its body covers must be free. Each pin of a part other than a resistor needs a row of its own.
2. A resistor keeps its place only when its joined leg is still in the row it joins.
3. Place every other part by spark's first fit.
4. Know a jumper by what its two rows hold, as `{"board:D10", "TactileButton:1.l"}`. A new jumper takes the earlier
   holes and route of the jumper with the same ends, when those holes are free and in the rows the new plan gives.
5. Name every earlier part and jumper the new diagram does not keep, and why.

## Identity and hooks

- A part keeps its id from `emit_board.component_name(part)` (scripts/breadboard.py:370). A resistor does not: its id
  is `R` plus its order in the circuit (scripts/breadboard.py:341). The circuit's name (`LedRed5mmSeriesA`) is stable.
- A jumper has no id in Wokwi. The prototype names it by the part pins its rows hold. A jumper to a free row has none.
- `PartPlacement` is already a strategy (scripts/breadboard_drawing.py:148), and `BreadboardPlanner` takes one
  (scripts/breadboard_drawing.py:225). A `KeepEditsPlacement` fits there with no change to `plan()`.
- Jumpers need one step after `plan()` (scripts/breadboard_drawing.py:227) and a `route` field on `Jumper`
  (scripts/breadboard_drawing.py:31). Today `render()` writes every route as `[]` (scripts/breadboard_drawing.py:332).
- `_plan_layout` (scripts/breadboard.py:377) must read the earlier `breadboard.json` before `write()`
  (scripts/breadboard.py:438) overwrites it.

## Risks

- A kept part far to the right pushes new parts right (scripts/breadboard_drawing.py:235). In case a, R1 reached
  column 28 of 30. Free rows for board pads come after the last part too (scripts/breadboard_drawing.py:249).
- A jumper's color is its step's color, so a person's new color is lost when step numbers change.
- The first prototype forgot the holes under the board's body, and jumpers landed there. The connection check missed it.
- Moving a part in Wokwi leaves its jumpers in the old rows, so the edited diagram is miswired until the rebuild.

## Not tested

- A real drag in Wokwi's web editor, and how the edited `diagram.json` comes back into the project.
- A rail, a jumper to a free row, two parts of one record, and a rotation the geometry file has not measured.

## Recommendation for the story's plan

First slice: keep moved parts only. Add `KeepEditsPlacement`, read the earlier `breadboard.json` in `_plan_layout`,
and print each dropped part with its reason. Test it with cases a and c-part. Then keep jumper holes and routes.
Resistor ids by circuit name come before any slice that adds a part with a resistor.
