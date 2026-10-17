# P273 slice 1: the next build keeps the moves

> **Move a part in `breadboard.json`, change the requirements, build again: the part stays where you put it. When it
> cannot stay, the build says which part and why. 3 of 3 cases: one survives, two are named. A moved jumper and a
> moved resistor are not kept yet.**

[P273, #309](https://github.com/xmejkal/spark/issues/309). The PO: "it should stay where we move it". Input: the
[spike's finding](../2026-10-17-p273-edit-spike/finding.md), which recommends this slice. Done when: edit, rebuild, the
move survives or is named, in 3 of 3 cases. The spike's pass for case c rested on a moved jumper; here case c is the
spike's c-part row (a moved part is named). Jumpers are planned fresh from the placed parts, so a moved part's old
jumpers are re-routed to its new rows, as in the spike's case a.

## Council

Round 1 (tech lead and refuter) changed: resistors are never reserved (a kept "R1" can be another resistor); a kept
plan with no room falls back to the fresh plan and names the moved parts (a moved part used to fail the build and
delete the edit); a turn that is not 0, 90, 180 or 270 is refused (45 degrees was kept with legs off); the `did` word
is `move not kept`, since `not kept` already means a whole destination; a hook `reserve_first(ledger)` replaces "the
first call reserves"; new tests for rows shared, a far-right kept part and a changed breadboard type. Rejected by
running it: out-of-order `after`, and bytes changing on an unchanged rebuild.
Round 2 (tech lead and PO-assistant) changed: the placement subclasses `FirstFitPartPlacement` and reuses its fit
code; the fresh plan is made first, so the fallback is free and runs only when the fresh plan works; the retry from
column 0 sits inside `place()`; the plan is cut to about 90 lines; the data-loss risk of a failed build becomes a
question for the PO.

## What changes for a person

`check_spine.py requirements.json --keep .` (and `breadboard.py`) read the earlier `breadboard.json` before they write
the new one. A part with the same id and Wokwi type keeps its place when it still fits. A part that moved and cannot
stay is named, one line each, and placed by first fit. A part the new circuit lacks is named. A rebuild with no move
names nothing, and writes the same bytes.

## The three cases (tests on copies of `button-light-xiao`)

| Case | Edit, then requirements change | Result |
| --- | --- | --- |
| a, survives | button moved 4 columns right, then the LED is added | the button stays; LED and R1 go in after it |
| b, named: gone | LED and R1 moved, then the LED is removed | both named `not in the circuit` |
| c, named: cannot stay | LED moved off every hole, or onto the button's holes | named with the hole; placed fresh |

Also tested: a changed Wokwi type, a 45-degree turn, two kept parts in one row (the first in the file wins), a kept
part far right, a changed breadboard type, a moved resistor, an unreadable earlier file, the fallback, `keep_breadboard`
entries. Variants of the fixture come from real `--keep` builds (`button-only-xiao`, `led-only-xiao`).

## The merge rule (finding rules 1, 3 and 5; 2 and 4 wait)

1. Plan fresh first (today's plan; its error stands). Then plan again with `KeepMovesFirstFitPartPlacement`.
2. `reserve_first` claims each earlier part, in file order, whose id and Wokwi type are in the circuit, that is not a
   resistor, whose turn is 0, 90, 180 or 270, whose pins are over free holes, one row each, and whose covered holes are
   free. A part that fails is refused with a code. Its holes come from left, top and turn, as `rotate()` and
   `hole_at()` give them.
3. Every other part goes to first fit; one that does not fit after a kept part is retried from column 0.
4. If the kept plan raises `NotDrawn`, the fresh layout is used and a moved part gets `no room`.
5. Name each earlier part not in the layout (`not in the circuit`), each part the placement refused (also an
   unmoved one that lost a hole to a moved one), and each resistor or `no room` part whose earlier place differs
   from where the fresh plan puts it. A kept part, and a part the person did not move, are not named.

## Classes (new module `scripts/breadboard_keep.py`)

```
PartPlacement (breadboard_drawing)   Strategy; NEW no-op reserve_first(ledger), called once at the top of plan()
  `-- FirstFitPartPlacement          exists
        `-- KeepMovesFirstFitPartPlacement   NEW Strategy: reserve earlier parts, else first fit (one per plan)
EarlierDiagram                       NEW Value: earlier parts by id (type, left, top, turn), or why unread
NotKeptResult(subject, code, why)    NEW Result: one per part named
name_parts_not_kept(earlier, layout, fresh, reasons, default_code) -> [NotKeptResult]
```

```
check_spine --keep -> breadboard.write(req, sheet, circuit)
   read earlier breadboard.json (before it is overwritten) -> EarlierDiagram
   _plan_once(read, earlier): fresh = plan(); kept = plan(KeepMoves...)  (NotDrawn: fresh, "no room")
   name_parts_not_kept(...) -> PlannedLayout(layout, why, not_kept)
   sheet, breadboard.json, breadboard.svg all from that one layout
   -> WriteResult(sheet, drawings, why, not_kept) -> `move not kept` entries / stderr lines
```

## Names, checked against developing.md's table

| Name | Role | Why |
| --- | --- | --- |
| `KeepMovesFirstFitPartPlacement` | Strategy | what varies, then the base's whole name |
| `EarlierDiagram` | Value | the diagram the person edited |
| `NotKeptResult` | Result | what `name_parts_not_kept` returns |
| `name_parts_not_kept` | function | starts with a verb |
| `NOT_IN_CIRCUIT`, `TYPE_CHANGED`, ... | codes | one tuple; the code decides, a `_MESSAGE` beside it is read (P260) |

## Choices made without the PO

- Resistors and jumpers are follow-ups. A resistor is named whenever its place differs, even if it did not move,
  because the build cannot tell; the message says so.
- A file that is not spark's diagram is named `unreadable`, and the build goes on with a fresh plan.
- Docs say "a part other than a resistor stays", never "a move stays".

## Question for the PO

A refused or failed build (`_left_from_earlier`) deletes `breadboard.json`, edit included. Example: you move the LED,
then break `requirements.json`; the next `--keep` removes your file. Fix in this slice, or the next? Default: next.

## Follow-ups to propose, not built

1. Keep a moved jumper's holes and route. 2. Keep a moved resistor, after resistor ids come from the circuit name.
3. Read a diagram edited and exported from Wokwi's web editor. 4. Warn when a kept part far right crowds the board.
5. Keep the person's file when a build fails.

## Docs and gates

`--help` of `breadboard.py` and `check_spine.py`, `docs/guide/agents.md`, `commands/build.md`, `docs/guide/journey.md`;
the README row and `tools/journey.py` if a status changes. Mutation table `tests/mutations/p273-keep-moves.json`.
