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
