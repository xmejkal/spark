# P287: a rebuild keeps a moved jumper and a moved resistor

> **Move a jumper or a resistor in `breadboard.json`, change the requirements, build again: it stays where you put
> it, or the build names it and says why. Slice 1 kept parts (PR #339); this slice keeps the other two things a
> person moves.**

[P287, #340](https://github.com/xmejkal/spark/issues/340), the next slice of P273 (#309). The PO: "it should stay
where we move it". Input: [slice 1's plan](../2026-10-17-p273-keep-moves/plan.md) and the
[spike](../2026-10-17-p273-edit-spike/finding.md) (cases b, b2, b3, c). Done when: each spike case for a jumper and a
resistor survives or is named.

## Council

Round 1 (tech lead, refuter): one word, `jumper`; a resistor shares `_reserve` with a `pinned` argument; the ledger for
jumpers is a copy of the holes taken before any jumper; matching is one-to-one on unordered rows against the planned
jumpers; the naming rule became quiet (the refuter saw 3 of 4 untouched jumpers named); two tests dropped; gates listed.
Round 2 (tech lead, PO-assistant): `_reserve` skips the free-group test for the pinned pin; the jumper placement keeps
its own `reasons`; `connections` may be absent and a connection may have 3 items; `Surface` gets a hole-by-name
lookup; an empty end row counts as the person's only at or left of the earlier file's last part column (a board-pad
row beyond it is the build's); messages are plain sentences; `JUMPER_NOT_ON_BOARD`; choices and tests-first added.

## The safety rule that makes this small

A kept jumper only takes the holes of a planned jumper's two rows (the jumpers of the kept pass, which carry rows and
a step; their holes are claimed again). So a kept jumper never changes a connection. A kept resistor has its joined pin
in the row it joins and its other pin in a free row; jumpers follow whatever rows result. The SVG ignores a route.

## What changes for a person

1. A jumper moved to other holes of the rows it joins (spike b, b2, c) keeps its holes, its route and its direction.
   The colour is still the step's.
2. A resistor keeps its place when its joined pin is still in the row it joins, and its other pin is free (spike
   resistor). It is checked when placed, because the row it joins is known only then. Resistors are placed in circuit
   order, so for two resistors the earlier one in the circuit wins a hole.
3. An earlier jumper in neither the new layout nor the fresh plan is named (`jumper 4b.j-24b.f: the new layout has no jumper between those two rows, so spark drew its own`), but only when each of its end rows is held in the earlier file by parts that are still where they were, or is empty
   and at or left of the file's last part column (a board-pad row lies beyond it and moves with the parts). A jumper of a part that moved, or that the circuit lost, is explained by that
   part's own line. So spike b3 (an empty row) and c (the circuit stopped joining it) are named, and a requirements
   change does not list the jumpers of a removed part.
4. A resistor that cannot stay is named: `R1: its pin 2 is no longer in the row it joins, so spark placed it` (spike c-part).

## Cases (tests on copies of `button-light-xiao`)

| Case | Edit, then change | Result |
| --- | --- | --- |
| b, same row | jumper end moved to another hole of its row, with a route; LED removed | holes and route kept |
| b2, other row | GND jumper end moved to the button B row; LED removed | kept (the new circuit joins those rows) |
| b3, empty row | jumper end moved to a row no part holds | named `rows-not-joined`; planned jumper drawn |
| c, circuit breaks it | LED, R1 and a jumper moved; button removed | LED, R1 kept; the jumper the circuit no longer joins named |
| c-part | LED moved, R1 left | R1 named `pin-off-row`, placed by first fit |
| resistor | R1 moved along its row, its jumper moved with it | both kept |

Also: a jumper onto a hole a part holds or the board covers (`hole-taken`), two earlier jumpers on one pair of rows
(first in the file wins), a jumper written the other way round (direction kept), a connection to a part pin (named
`jumper-not-on-board`), a malformed connection (file unreadable), an unchanged rebuild (same bytes, nothing named), a
requirements change with no edit (nothing named for a lost part's jumpers), and every merged diagram joins the same
rows as the planned one. The old test that wants `resistor-not-kept` is replaced.

## Classes (`breadboard_drawing.py`, `breadboard_keep.py`)

```
PartPlacement -- FirstFitPartPlacement -- KeepMovesFirstFitPartPlacement   slice 1; _reserve(.., pinned) also serves place()
JumperPlacement                  NEW Strategy: place_jumpers(layout, ledger) -> layout; no-op; last line of plan()
  `-- KeepMovesJumperPlacement   NEW: an earlier jumper takes the holes of the planned jumper with the same two rows
Jumper(one, other, step, route=())   gains route (a tuple of strings); the Wokwi renderer writes it
HoleLedger(surface, taken=None)      gains a start state
EarlierJumper(one, other, route)     NEW Value: one connection of the earlier file (EarlierDiagram.jumpers, .surface_id)
name_jumpers_not_kept(earlier, layout, fresh, reasons, geometry, default_code) -> [NotKeptResult]   NEW function
```

```
plan(): parts, resistors -> parts_only = copy of the holes taken -> planned jumpers (as today)
        -> jumper_placement.place_jumpers(layout, HoleLedger(surface, parts_only))
KeepMoves...: pass 1, each earlier jumper in file order: both ends on holes, its two rows = an unmatched planned
              jumper's two rows, both holes free -> claim them; pass 2: the others take their first free hole in
              their rows (no new row); nothing kept = the layout as it was
```

## Names, checked against developing.md's table

| Name | Role | Why |
| --- | --- | --- |
| `JumperPlacement` | Strategy | base, as `PartPlacement` |
| `KeepMovesJumperPlacement` | Strategy | what varies, then the base's whole name |
| `EarlierJumper` | Value | facts of one connection, no actions |
| `name_jumpers_not_kept` | function | verb first, beside `name_parts_not_kept` |
| `ROWS_NOT_JOINED`, `JUMPER_NOT_ON_BOARD`, `PIN_OFF_ROW` | codes | a code decides, `MESSAGES` is read (P260) |
| `RESISTOR_NOT_KEPT` | removed | a resistor has the codes of other parts |

## Choices made without the PO

- A kept jumper keeps its holes, route and direction (a route is relative to its first end) and the step's colour.
- A resistor keeps its place when that is legal for whatever `R1` is now (ids are by order).
- Colour: the step's, not the person's (the choice most likely to change). Two earlier jumpers on one pair of rows:
  the first in the file wins. A connection to a part pin is named, not kept.
- A malformed connection (not a list of strings) makes the earlier file unreadable, as a malformed part does; a missing
  `connections` key, or a connection with no route, is fine.
- After a requirements change, a jumper whose rows the new circuit no longer joins is named even if nobody moved it
  (the build cannot tell; the refuter's run found it, and a test says so).
- A board-pad jumper whose free row moved because a part was added or removed is drawn fresh (known limit, follow-up 7).
- A new part placed by first fit can take a kept resistor's holes before it is checked; the resistor is then named.

## Follow-ups to propose, not built

1. Keep a jumper's colour. 2. Stable resistor ids from the circuit name. 3. Name the jumpers of a part that moved, as
one line. 4. Read a diagram exported from Wokwi's web editor. 5. Draw a route in the SVG. 6. A far-right kept part
crowding the board. 7. Match a board-pad jumper by its part end alone.

## Docs and gates

`--help` of `breadboard.py` (line 25) and `check_spine.py`, the docstrings of `breadboard_keep.py` and
`name_parts_not_kept`, `docs/guide/agents.md`, `commands/build.md`, `docs/guide/journey.md`. The old resistor test and
`tests/mutations/p273-keep-moves.json` row 14 change. Mutation table `tests/mutations/p287-keep-jumpers.json`;
re-anchor with `python3 tools/mutate.py --anchors`. Observation rows from AT420 (AT403 to AT419 are P239 PR 7's). No step changes status, so the README and
`tools/journey.py` stay. Tests come first: the cases table, as failing tests, then the code.
