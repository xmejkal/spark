# P287: a rebuild keeps a moved jumper and a moved resistor

> **Move a jumper or a resistor in `breadboard.json`, change the requirements, build again: it stays where you put
> it, or the build names it and says why. Slice 1 kept parts (PR #339); this slice keeps the other two things a
> person moves.**

[P287, #340](https://github.com/xmejkal/spark/issues/340), the next slice of P273 (#309). The PO: "it should stay
where we move it". Input: [slice 1's plan](../2026-10-17-p273-keep-moves/plan.md) and the
[spike](../2026-10-17-p273-edit-spike/finding.md) (cases b, b2, b3, c). Done when: each spike case for a jumper and a
resistor survives or is named.

## Council

(filled after each round)

## The safety rule that makes this small

A kept jumper only takes the holes of a jumper the fresh plan already has: it must join the same two rows. So a kept
jumper never changes a connection. The same holds for a kept resistor: its joined leg must lie in the row it joins and
its other leg in a free row; jumpers follow whatever rows result.

## What changes for a person

1. A jumper moved to other holes of the rows it joins (spike b, b2, c) keeps its holes and its route (the bends in
   the file). The colour is still the step's.
2. A resistor moved so its joined leg is still in the row it joins keeps its place. It is checked when placed, not
   reserved at the start, because the row it joins is known only then.
3. Each earlier jumper that is in neither the new layout nor the fresh plan is named, one line:
   `jumper 4b.j-24b.f: the new plan joins no jumper between rows 4b and 24b` (spike b3, and c when the new circuit
   breaks it). A jumper that is the fresh plan's own is never named, so a rebuild with no change names nothing.
4. A resistor that cannot stay is named: `its leg 2 is no longer in the row it joins` (spike c-part).

## Cases (tests on copies of `button-light-xiao`)

| Case | Edit, then change | Result |
| --- | --- | --- |
| b, same row | jumper end moved to another hole of its row; LED removed | holes and route kept |
| b2, other row | GND jumper end moved to the button B row; LED removed | kept (the new circuit joins those rows) |
| b3, empty row | jumper end moved to a row no part holds | named `rows-not-joined`; fresh jumper |
| c, circuit breaks it | LED, R1 and jumpers moved; button removed | LED and R1 kept; the jumper the circuit no longer joins is named |
| c-part | LED moved, R1 left | R1 named `leg-off-row`, placed fresh (as in the spike) |
| resistor | R1 moved along its row, its jumper moved with it | both kept |

Also: a hole taken by a part or covered by the board, two earlier jumpers on one pair of rows (first in the file
wins), a wire that is not between two holes, a route that is not a list, a row with no hole left, a jumper written
the other way round, an unchanged rebuild (same bytes), the kept plan falling back to the fresh one (jumpers named
`no-room`).

## Classes (`breadboard_drawing.py`, `breadboard_keep.py`)

```
PartPlacement -- FirstFitPartPlacement -- KeepMovesFirstFitPartPlacement   slice 1; place() now also keeps a resistor
JumperPlacement                  NEW Strategy: place_jumpers(layout, ledger) -> layout; no-op; end of plan()
  `-- KeepMovesJumperPlacement   NEW: an earlier wire takes the holes of the fresh jumper with the same two rows
Jumper(one, other, step, route=())   gains route; the renderer writes it
HoleLedger(surface, taken=None)      gains a start state: the holes of the parts, before any jumper
EarlierWire(one, other, route)       NEW Value: one connection of the earlier file (EarlierDiagram.wires, .surface_id)
name_jumpers_not_kept(earlier, layout, fresh, reasons, default_code) -> [NotKeptResult]    NEW function
```

```
plan(): parts, resistors -> bare = holes taken so far -> fresh jumpers (as today)
        -> jumper_placement.place_jumpers(layout, HoleLedger(surface, bare))
KeepMoves...: each earlier wire, in file order: its two rows = a fresh jumper's two rows, both holes free -> claim
              (pass 1); then every other jumper takes its first free holes (pass 2); no wire kept = layout as it was
```

## Names, checked against developing.md's table

| Name | Role | Why |
| --- | --- | --- |
| `JumperPlacement` | Strategy | base, as `PartPlacement` |
| `KeepMovesJumperPlacement` | Strategy | what varies, then the base's whole name |
| `EarlierWire` | Value | facts of one connection, no actions |
| `name_jumpers_not_kept` | function | verb first, beside `name_parts_not_kept` |
| `ROWS_NOT_JOINED`, `WIRE_OFF_HOLES`, `LEG_OFF_ROW` | codes | a code decides, `MESSAGES` is read (P260) |
| `RESISTOR_NOT_KEPT` | removed | a resistor now has the codes of other parts |

## Choices made without the PO

- A kept jumper keeps its holes, its route and its direction (a route is relative to its first end), and the step's
  colour. A colour the person changed is lost.
- A resistor keeps its place when that is legal for whatever `R1` is now (ids are by order, not stable). Jumpers
  follow the rows, so no connection can change.
- A jumper to a free row (a board pad, `claim_free_group`) is not matched by rows, so it is named when moved.

## Follow-ups to propose, not built

1. Keep a jumper's colour. 2. Stable resistor ids from the circuit name. 3. Quiet naming of a jumper nobody moved when
the circuit drops it. 4. Read a diagram exported from Wokwi's web editor. 5. A far-right kept part crowding the board.

## Docs and gates

`--help` of `breadboard.py` and `check_spine.py`, `docs/guide/agents.md`, `commands/build.md`, `docs/guide/journey.md`.
Mutation table `tests/mutations/p287-keep-jumpers.json`; re-anchor with `python3 tools/mutate.py --anchors`. Rows
from AT420.
