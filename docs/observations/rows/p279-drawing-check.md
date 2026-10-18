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
| 11 | A pin in no point that shares a row with a point is not checked by the product | round 2 | acted | row 17: `joined-to-unused` |
| 12 | The journey paragraph is there twice | lens review, PR | acted | the copy is removed |
| 13 | `agents.md` leaves out the sheet's count | lens review, PR | acted | "the first and a count of the rest" |
| 14 | No test of the kept-layout branch, of "and N more", or of two ends that differ | lens review, PR | acted | two new tests in `test_breadboard_match.py` |
| 15 | `end_group` can raise `NotDrawn` inside the check, and nothing catches it | lens review, PR | rejected | the layout is planned from the same points and catalog; the docstring says so |
| 16 | `DrawingDiffersResult.line` only repeats `why` | lens review, PR | acted | `line` removed; callers read `why` |
| 17 | The check is silent on a short into a pin no point names: D8 to 3V3, D8 to D0, GND to 5V | refuter, PR | acted | code `joined-to-unused`; a pin of a named contact counts as its point's; test GND to 5V |
| 18 | README and `commands/build.md` claim more than the code checks, and the docstring says "nothing more" | refuter, PR | acted | row 17 closes the gap; the docstring says "no other pin" |
| 19 | A false difference on a fixture build, or a changed planner output | refuter, PR | rejected | 5 fixtures and 7 rebuild orders gave no difference; `breadboard.json` sha256 equal on main and the branch |
