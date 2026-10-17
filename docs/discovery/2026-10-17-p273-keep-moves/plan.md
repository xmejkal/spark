# P273 slice 1: the next build keeps the moves

> **Move a part in `breadboard.json`, change the requirements, build again: the part stays where you put it. When it
> cannot stay, the build says which part and why.** No jumper is kept in this slice, and no resistor.

[P273, #309](https://github.com/xmejkal/spark/issues/309). The PO: "it should stay where we move it". Input: the
[spike's finding](../2026-10-17-p273-edit-spike/finding.md), which recommends this slice. Done when: edit, rebuild, the
move survives or is named, in 3 of 3 cases.

## Council

Round 1 (tech lead on Sonnet, refuter on Opus) changed the plan in 9 places:

- Resistors are never reserved (both found rule 1 and the old rule 2 contradict; a kept "R1" can be another resistor,
  and one reading miswired a build). A resistor is named `reset` only when its place differs from the earlier one.
- A kept plan that has no room falls back to a fresh plan and names the parts that moved (the refuter: a part moved
  14 columns made the build fail and delete the edit with nothing said).
- A turn that is not 0, 90, 180 or 270 is refused with its own code (the refuter: 45 degrees was kept with legs off).
- A fresh part that does not fit after a far-right kept part is retried from column 0 (tech lead: `after`).
- `PartPlacement` gets a no-op `reserve_first(ledger)` hook, called once at the top of `plan()`; no state between
  plans. The earlier part's holes are derived from left, top and turn; the breadboard part is skipped.
- The entry's `did` is `move not kept`, since `not kept` already means a whole destination (refuter).
- Codes are one tuple, a test checks each has a message; `unreadable` only when a file exists.
- Tests added: two kept parts in one row, a far-right kept part, a changed breadboard type. Out of scope, now a
  follow-up: a refused or failed build still deletes `breadboard.json` (`_left_from_earlier`).
- The rejected: `after` out of order and the unchanged rebuild are fine (refuter ran both).

Round 2 not run yet.

## What changes for a person

`check_spine.py requirements.json --keep .` (and `breadboard.py`) read the earlier `breadboard.json` before they write
the new one. A part with the same id and Wokwi type keeps its place when it still fits. A part that does not keep its
place is named in the output, one line each, and placed by spark's first fit. A part the new circuit no
longer has is named too. Nothing is named on a rebuild with no move.

## The three cases (tests on copies of `button-light-xiao`)

| Case | Edit, then requirements change | Result |
| --- | --- | --- |
| a, the move survives | button moved 4 columns right, then the LED is added | the button stays; the LED and R1 go in after it |
| b, named: gone | LED and R1 moved, then the LED is removed | both named `not in the circuit` |
| c, named: cannot stay | LED moved off every hole, or onto the button's holes | named with the hole, and placed fresh |

Also tested: a changed Wokwi type is named, a moved resistor is named `not kept yet`, an unreadable earlier file is
named, a rebuild with no move writes the same bytes, and `keep_breadboard` carries each name as a `move not kept` entry.
Variants of the fixture come from real `--keep` builds (`button-only-xiao`, `led-only-xiao`, trimmed as the fixture is).

## The merge rule (from the finding, rules 1, 3 and 5; rules 2 and 4 wait)

1. Before any part goes in, reserve each earlier part whose id and Wokwi type are in the new circuit, at its earlier
   place (left, top, turn of 0, 90, 180 or 270), if every pin is over a free hole, no hole it covers is taken, and
   each pin has a row of its own. Earlier parts are checked in file order against the ledger, so the first wins. A
   resistor is never reserved.
2. Every other part goes through `FirstFitPartPlacement`; one that does not fit after a kept part is retried from
   column 0. If the kept plan still has no room, the whole plan is made again with nothing kept and the parts that
   moved are named `no room`.
3. Jumpers are planned fresh from the placed parts, as today. They follow a moved part, so a build stays wired.
4. Name each earlier part that moved and is not kept, with a code and a reason; a part that is where spark puts it
   anyway is not named.

## Classes (new module `scripts/breadboard_keep.py`)

```
PartPlacement (breadboard_drawing)            Strategy, exists
  |-- FirstFitPartPlacement                    exists, unchanged
  `-- KeepMovesPartPlacement                   NEW Strategy: reserve earlier parts, else first fit
         uses  EarlierDiagram                  NEW Value: the earlier parts by id, or why it is unread
         gives NotKeptResult(subject, code, why)   NEW Result, one per part not kept
```

Wiring (existing code, a few lines each): `breadboard._plan_layout(read, placement=None)` passes the placement to
`BreadboardPlanner`. `breadboard._plan_once(read, earlier)` builds the placement and adds `not_kept` to
`PlannedLayout`. `breadboard.write()` reads the earlier file before it writes and adds `not_kept` to `WriteResult`.
`check_spine.keep_breadboard` turns each into a `move not kept` entry; `breadboard.main` prints it on stderr.

```
person edits breadboard.json in Wokwi            requirements change
              \                                       /
   check_spine --keep -> breadboard.write(req, sheet, circuit)
         |  read earlier breadboard.json  (before it is overwritten)
         |  _plan_once(read, earlier)
         |     BreadboardPlanner(placement=KeepMovesPartPlacement)
         |        place(part): first call reserves the earlier parts, then each part is
         |        reserved-or-first-fit  --> BreadboardLayout
         |     placement.not_kept(layout) --> [NotKeptResult]
         |  render sheet + breadboard.json + breadboard.svg from ONE layout
         `-> WriteResult(sheet, drawings, why, not_kept) --> `not kept` entries
```

## Names, checked against developing.md's table

| Name | Role | Why this name |
| --- | --- | --- |
| `KeepMovesPartPlacement` | Strategy | what varies (keeps moves), then the base's whole name |
| `EarlierDiagram` | Value | the diagram the person edited; docstring says Value |
| `NotKeptResult` | Result | what `not_kept()` returns; ends in `Result` |
| `read_earlier_diagram`, `why_not_keep` | functions | start with a verb, or `why_` and return a reason or None |
| `NOT_IN_CIRCUIT`, `TYPE_CHANGED`, ... | codes | the code decides; the text is a `_MESSAGE` beside it (P260) |

One word for one thing: the person's file is the "earlier diagram"; a place a part is refused is "not kept".

## Choices made without the PO

- Jumpers and resistors are left for follow-ups; a moved resistor is named, not silently reset.
- The file read is the Wokwi renderer's `breadboard.json` beside the sheet. A file that is not spark's diagram is named
  `unreadable` and the build goes on with a fresh plan.
- `breadboard.svg` and the sheet come from the same kept layout.

## Follow-ups to propose, not built

1. Keep a moved jumper's holes and route (finding rule 4).
2. Keep a moved resistor, after resistor ids come from the circuit name (`LedRed5mmSeriesA`), not their order.
3. Read a diagram edited and exported from Wokwi's web editor (the way back is not tested).
4. Warn when a kept part far right pushes new parts to the board's edge.
5. A refused or failed build still deletes `breadboard.json` (`_left_from_earlier`): keep the person's file.

## Docs and gates

`--help` of `breadboard.py` and `check_spine.py`, `docs/guide/agents.md`, `commands/build.md`, `docs/guide/journey.md`;
the README row and `tools/journey.py` only if a status changes. Mutation table `tests/mutations/p273-keep-moves.json`.
