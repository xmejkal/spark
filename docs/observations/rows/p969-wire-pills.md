# P969 PR 2: the wire pills' places leave the SVG renderer: rows

Card: [P969 #1388](https://github.com/xmejkal/spark/issues/1388). This file holds the acted, raised and rejected
findings of PR 2's build only; the plan's revisions decide where they differ from the plan. 2026-11-21.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `WirePill`, `PillLayout`, `_pieces` and `_length` move verbatim to `wire_pills`; `WireSizes` and `WIRE_SIZES_PX = WireSizes(4.0, 2.2, 3.0, 0.8)` replace the four `_PX` class constants; `wire_boxes(jumpers, paths, pills, sizes)` takes over `_wire_boxes` | the plan, section 4 | acted | `scripts/spark/breadboard/wire_pills.py`; `svg_diagram` imports `WIRE_SIZES_PX`, `PillLayout` and `wire_boxes` and draws |
| 2 | the plan's re-anchors name `p947-lanes-and-wires.json` row 12 and `p953-pills.json` rows 1, 3, 4 and 8; revision 8 adds row 13 of the p947 table, whose find held `self.UNDER_STROKE_PX` and `self.WIRE_STROKE_PX` | the plan, revision 8 | acted | p947 rows 12 (file moved) and 13 (find and replace read `WIRE_SIZES_PX.under_stroke` and `.stroke`); p953 rows 1, 3, 4 (file moved) and 8 (file moved, find is the `WIRE_SIZES_PX` line); `tools/mutate.py --anchors` on every table: the 20 refusals all lie in files this PR does not touch (store, bench, build, tools), none in the breadboard area |
| 3 | the area inventory of `test_architecture` (`MODULES`) does not list a new breadboard module | PR 1's row 9 | acted | `wire_pills` added to the list and its comment; "twenty-four modules" |
| 4 | the pill test (`test_every_pill_finds_a_free_place_on_every_fixture`) and `HALF_STROKE` read `wire_pills`; only their import changed | the plan | acted | `tests/test_breadboard_svg.py`, `tests/test_wire_routing.py` |
| 5 | the plan names no new row for PR 2; a row on `wire_boxes`' reach (`reach = 0`) was planted once by hand in the tree and no test of `test_golden_breadboard`, `test_breadboard_svg`, `test_wire_routing` or `test_picture_makers` failed | the build | raised | dropped because no test pins a caption's clearance of a wire's under-stroke on any fixture; no row was written for a fault nothing catches. A card for that test is the lead's to file |
| 6 | the labels' way (PR 3's maker with a label-measure Strategy), the scene and the sheet's single scene do not move in PR 2 | the plan, revisions 12 and 13 | raised | to PR 3 and PR 4 of P969 #1388 |
| 7 | `test_self_confirmation` refused the first push: a test reads `wire_pills.WIRE_SIZES_PX` (`HALF_STROKE`, and the new sizes test); the old class constant was no module constant, so it was never listed | the build, the hook | acted | `wire_pills.WIRE_SIZES_PX` listed with its reason, as the plan named no such line |
