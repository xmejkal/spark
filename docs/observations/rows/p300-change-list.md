# P300 change list: findings rows

The plan councils of P300 (#366). Plan: [`plan.md`](../../discovery/2026-10-18-p300-change-list/plan.md).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | A rebuild after a new part prints `move not kept` for two jumpers spark drew (8b.j-17b.g, 12t.a-17b.h) | repro agent | acted | `_is_explained_by_edit` line 363; plan step 5 replaces the guess with `drawn_jumpers` |
| 2 | #351: a jumper moved into an empty row that a new part takes is dropped with no line | repro agent | acted | line 364; plan step 5; P292 #351 closes with the PR |
| 3 | The first draft's example of four lines was invented; the real run gives 7 lines and no rail | refuter, round 1 | acted | expected lines come from a real run |
| 4 | A step class beside `Seated` duplicates it | lenses, round 1 | acted | the record stores `Seated` facts, no new step class |
| 5 | A board jumper from a free row that later joins a part's row reads as remove + add | lenses, round 1 | acted | one subject key for a jumper, whatever the act |
| 6 | A resistor tag renumbers with circuit order, so the same resistor reads as remove + add | lenses and refuter, round 1 | acted | a resistor end is keyed by its job, not its tag |
| 7 | `WiringChange` held English words | lenses, round 1 | acted | codes and fields; `ChangeList` writes the words |
| 8 | Code `MOVE` reads like `MOVE_NOT_KEPT` | lenses, round 1 | acted | `added`, `removed`, `rerouted`, `changed`; a bench line says "Move the … jumper" |
| 9 | `check_spine --json` keeps only `file, did, why`, and already drops `part` and `code` of move-not-kept entries | lenses round 1, round 2 | acted | `--json` keeps every field but `line` |
| 10 | A kept person's jumper in `drawn_jumpers` is taken for spark's at the next build | refuter, round 1 | acted | `drawn_jumpers` holds only spark's own jumpers |
| 11 | A failed build that removes the record brings the old guess back | refuter, round 1 | acted | a failed build never removes the record; the guess is deleted |
| 12 | Two jumpers can share a color after the palette wraps | lenses, round 1 | rejected | a line names both ends, so they are told apart (refuter) |
| 13 | Kept jumpers change color on the new sheet with no line | lenses and refuter, round 1 | acted | split to P316 #395; the record carries the bench color forward |
| 14 | A record written after the drawings goes stale when a drawing write fails | round 2 | acted | the record is written right after the sheet |
| 15 | A color line without a drawing names a color the sheet never showed | round 2 | acted | colors only when the earlier sheet showed them |
| 16 | `WiringChanges` and `WiringChange` differ by one letter | round 2 | acted | a function, `changes_between` |
| 17 | A first-build line and the old guess for old projects are more than the card needs | round 2 | acted | no section on a first build; the guess is deleted |
| 18 | The PO: a part can also be changed; jumpers should not overlap in the picture, and editor-like jumper editing, maybe not in the MVP | the PO, after round 2 | acted | `changed` line for a new resistor value; P317 #396 in Idea under P293 |
| 19 | The lines of the second-LED test match a real rebuild (button + LED, then a second LED, in a scratch copy): 7 lines, 5 added and 2 rerouted, and the colors match the earlier `breadboard.json` (GND purple, button B magenta) | the build, 2026-10-18 | verified | `tests/test_breadboard_changes.py`; the lines are in `docs/guide/journey.md` |
| 20 | A resistor end had no field for its job or value, so a key without the tag needed a parse of its words | the build | acted | `End` gained `job` and `value`, both defaulted, set only for resistors in `breadboard._wiring` |
| 21 | Three old tests encoded the deleted guess: a known limit that named an unmoved jumper, and two that left a person's jumper unnamed beyond the last part | the build | acted | they now say the opposite: a person's jumper is always named, a jumper spark drew never |
| 22 | `changes_between` takes the Seated steps and the colors, not only the steps, because an added jumper shows its new color | the build | acted | a small change to the plan's signature; `describe` is the one place that reads a Seated step |
| 23 | Two ends with the same key (two resistors with one job on one pin) would collapse into one step in the diff | the build | raised | no real circuit has it today; a card if a part ever asks for two |
| 24 | `wiring-record.json` repeats nine fields for every step, so it is long for a small project | the build | raised | fine for now; shrink it only if a person reads it, and the guide says not to edit it |
| 25 | `tests/test_self_confirmation.py` fails a test that reads a module constant such as `ADDED` | the push hook | acted | the new tests name the codes as literals |
| 26 | The mutation tester was not run on `breadboard_changes.py` and the keep change | the build | raised | the council runs it before the PR (plan, Verification) |
| 27 | A resistor leg and a supply that moved read as "Move the jumper …" | lenses, review round | acted | each kind has its own words; tests for a leg and a supply |
| 28 | A new jumper and a moved jumper can both be called magenta in one list | lenses, review round | acted | a new jumper whose color clashes with a removed or moved jumper names no color; docs say so |
| 29 | Build 3 of a project built before the record gave 3 false `move not kept` lines | refuter | acted | with no record, a jumper that equals the fresh plan's counts as spark's; a build 2 and build 3 test |
| 30 | A line said "(it went to a free rail. Mark it GND)" | refuter | acted | the record keeps the rail words and the mark apart; only the first arrival says to mark |
| 31 | A renumbered resistor read "to the row of R1 end 1 (it went to the row of R1 end 1)" | lenses | acted | a resistor end is named with its job in a change line |
| 32 | A removed resistor gave one line for each end | lenses | acted | one line: "Take out R1, 330Ω in series with …" |
| 33 | "a orange jumper", "a 820Ω resistor" | lenses | acted | an article function with tests |
| 34 | The record file could be half written | refuter | acted | `WiringRecord.write` writes a temporary file and replaces |
| 35 | The new-value code `changed` and the kept entry key `change` and `part` mixed words | lenses | acted | code `swapped`; both kinds of kept entry use `code` and `subject`; `--json` never carried `part`, so no reader breaks |
| 36 | "Nothing to change on the bench." had no bullet | lenses | acted | it has the same "- " bullet |
| 37 | The mutation tester found three escapes in `changes_between` (rail mark order, take-out before swap, the mark on the first line only) | mutation tester | acted | three tests; the table is `tests/mutations/p300-change-list.json` |
| 38 | Removing a part prints `move not kept` for parts nobody moved | PR review | rejected | outside this branch: main does the same; the coordinator files a card |
