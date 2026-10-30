# P434 rule kinds: findings rows

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `fab.process` returns the stated value unchecked at fab.py:37 | card | verified | held, at fab.py:36-39; the line is off by one. Plans drift in line numbers |
| 2 | A text `drill_step_mm` is a TypeError in `emit_footprint.render`, blamed on the board by `why_header_disagrees` | card | verified, acted | now refused by `fab.read_rules` when the rules file is read; `emit_footprint.main` exits could-not-run naming the file and the field |
| 3 | A 400-digit `width_mm` reaches the footprint stage of the spine as a "crashed" stage | plan | rejected | wrong: `emit_board.place` (`/ 2` on the width) raises the OverflowError first, so the spine stops at the schematic stage as `emit_board.py crashed`. The CLI and `part_shape` sites are refused by `kind_problem`; the schematic site is not. The spine test for the huge width was dropped. Proposed card: `emit_board` reads the board's width and height through `emit_footprint.kind_problem` |
| 4 | `emit_footprint.main` called `design.rules_in` outside its try | plan | verified, acted | a rules file of the wrong kind would have been a traceback; now inside a try, exit 2 |
| 5 | `check_footprints.main` read the rules file raw | plan | verified, acted | now `fab.read_rules`, exit 2 with the sentence on stdout; imports `fab` only |
| 6 | JSON `NaN` and `Infinity` parse, so `drill_step_mm: NaN` was a ValueError blamed on the board and `inf` gave a NaN hole silently; `true` gave a 1 mm step silently | plan | verified, acted | all refused by `fab.is_finite_number` |
| 7 | A zero or negative `fabrication` value (ZeroDivisionError, a wrong hole) | plan | closed | out of this card; proposed card: a per-key table, since `annular_ring_margin_mm` may be 0 |
| 8 | Other raw readers of rules.json (check_physics.py, compare_design.py) | plan | closed | out of this card; proposed card: every reader goes through `fab.read_rules` |
| 9 | A top level that is no object, or a null `fabrication` | council | acted | a top level that is no object is refused; `fabrication: null` stays the default (pinned by a test) |
