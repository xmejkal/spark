# P279 drawing check: findings rows

The plan councils of P279 (#317). Plan: [`plan.md`](../../discovery/2026-10-18-p279-drawing-check/plan.md).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `write()` renders the sheet before a new call could compute the differences | refuter, round 1 | acted | `_plan_once` computes `differs` on `PlannedLayout` |
| 2 | The pushbutton's two sides of one contact are joined only in a comment, so a wire into `1.r` is a short the check misses | refuter, round 1 | acted | `joined_pins` in `data/wokwi-geometry.json`, cited to Wokwi's part page; test on `14b` |
| 3 | `NOT_DRAWN` is unreachable once a layout exists | tech lead, round 1 | acted | dropped; `end_group` raises `NotDrawn` as the planner does |
| 4 | `_hole_of` would copy the planner's `_pin` and `_group_of` | tech lead, round 1 | acted | `end_pin`, `end_group`, `drawn_part` are module functions both call |
| 5 | `Mismatch` and `LayoutMatch` do not say their role | tech lead, round 1 | acted | `DrawnNets` (Value), `DrawingDiffersResult` (Result) |
| 6 | Verification by a hand edit of `breadboard.json` cannot work, because P273 refuses the move | tech lead, round 1 | acted | tests plant the defect in the layout |
| 7 | Lone board pads and the board's ground pads give false differences | refuter, round 1 | rejected | `_wiring` drops a lone pad; every GND pad is one end, `board GND` |
| 8 | The old row test also covers pins in no point, so replacing it weakens the suite | round 2 | acted | the old test stays; the limit is in the docstring and `agents.md` |
| 9 | The catalog and geometry exist only on the kept path of `_plan_once` | round 2 | acted | built once, before the first return with a layout |
| 10 | A sheet line per difference grows without bound | round 2 | acted | the first difference and a count |
| 11 | A pin in no point that shares a row with a point is not checked by the product | round 2 | raised | the row test covers the fixture; a later card if a real build needs it |
