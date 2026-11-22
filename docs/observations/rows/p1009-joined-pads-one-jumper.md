# P1009: one jumper per group of joined pads: rows

Card: [P1009 #1468](https://github.com/xmejkal/spark/issues/1468). Seen in the p934-display2 walk, 2026-11-22 11:50
CET. The plan check: the refuter on Opus, one round (an XS card). This file holds the acted, raised and rejected
findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the sheet runs a jumper to 3V3 and another to 3V3_2, which the C6 joins inside itself | the walk, row 11 (the PO) | acted | `wiring_steps.joined_as_one`, through P971's `JoinedPads`. The walk's fixture with the C6's groups: 12 steps, not 13, and 10 drawn jumpers, not 11 |
| 2 | GND got one jumper by the luck of `pad_word`, not by the record | plan writer | raised | dropped because the result is right: `pad_word` says GND1 and GND2 both as `GND` before the groups are read, so the `[GND1, GND2]` group never matches and the two equal ends stay one. The groups act on pads whose words differ, such as 3V3 and 3V3_2 |
| 3 | a board end's bench key takes the joined note, so a rebuild tells the person to move a jumper that stayed | plan writer | acted | `bench_changes._end_key` keys a board end by its name. Row 6 |
| 4 | two board ends of one pad word on two rails merge even with no group | plan refuter 4 | acted | a pad in no group is its own key. Test of two rails, row 4 |
| 5 | a pad in no group merges with other ungrouped pads | plan refuter 1 | rejected | the refuter's own check: `group_of` gives `(pad,)` for such a pad |
| 6 | `_end_key` changes the keys of kept wiring records | plan refuter 3 | rejected | the refuter's own check: every board end has `name` equal to `words` today |
| 7 | the walk-c6 fixture's board record has no `joined_pads` | plan writer | raised | dropped because the tests add the groups in memory, and the old fixture keeps the case with no group. The MVP needs no more |
| 8 | "no jumper goes to 3V3_2" in breadboard-codes.md is false when 3V3_2 sits on another point | PR lens 1 | acted | fixed: the sentence is gone, and the paragraph on `joined_pads` says it for one point |
| 9 | the new tests sit after the `__main__` guard, so a run of the file as a script skips them | PR refuter 5 | acted | fixed: the class is above the guard |
| 10 | "the group's first pad in the sheet's order" is a loose name for the sort by words | PR refuter 2 | acted | fixed: "first by name" |
| 11 | the note leaks into a rail mark, a pill, a diagram node or before_power | PR refuter 3 | rejected | the refuter's own check: `joined_as_one` runs before the role and the rail, and those read `name`, not `words` |
| 12 | the wiring line says the note twice | PR refuter 3 | raised | dropped because it is true, and a shorter line touches every role line. The MVP needs no more |
