# Mutation: p267-drawn-breadboard

12 planted, 6 caught, 6 escaped (tools/mutate.py --copy, 947 s).

## Escapes (missing tests)
- free_row may reuse column after (`column > after` -> `>=`): no test where a board-pad jumper row lands next to the last part's column.
- no empty column between parts (`SPACING_COLUMNS` -> 1): no test asserting the gap column between two placed parts.
- both-ends resistor allowed (`len(pinned) > 1` -> `> 5`): no test of a resistor whose two ends both join other rows, asserting NotDrawn.
- resistor not kept right of after (`after if not row else 0` -> `0`): no test of a resistor with no joined leg, asserting its column is right of the parts.
- stale drawing kept (breadboard.write no longer unlinks breadboard.json on NotDrawn): no test that writes a drawing, then builds an undrawable board, and asserts the file is gone.
- color palette off by one (`number %` instead of `(number - 1) %`): no test that StepColors.color(1) is "red" and color(9) wraps to "red".

## Caught
rotate counter-clockwise, rail groups ignored, pins may share a row, covered box not turned, M is thousand, _left_from_earlier not unlinking.

## Table
```json
[
{"file":"scripts/breadboard_drawing.py","name":"rotate counter-clockwise","find":"x, y = cx + cy - y, cy - cx + x","replace":"x, y = cx - cy + y, cy + cx - x"},
{"file":"scripts/breadboard_drawing.py","name":"rail groups ignored in x","find":" + (number - 1) // board[\"rail_group\"])","replace":")"},
{"file":"scripts/breadboard_drawing.py","name":"free_row may reuse column after","find":"hole.column > after and self.row_is_free","replace":"hole.column >= after and self.row_is_free"},
{"file":"scripts/breadboard_drawing.py","name":"pins may share a row","find":"or hole.row in {one.row for one in holes.values()}","replace":"or False"},
{"file":"scripts/breadboard_drawing.py","name":"covered box not turned","find":"(cy, cx) if degrees % 180","replace":"(cx, cy) if degrees % 180"},
{"file":"scripts/breadboard_drawing.py","name":"no empty column between parts","find":"+ self.SPACING_COLUMNS","replace":"+ 1"},
{"file":"scripts/breadboard_drawing.py","name":"both-ends resistor allowed","find":"if len(pinned) > 1:","replace":"if len(pinned) > 5:"},
{"file":"scripts/breadboard_drawing.py","name":"resistor not kept right of after","find":"after if not row else 0","replace":"0"},
{"file":"scripts/breadboard.py","name":"M is thousand","find":"\"M\": 1000000}","replace":"\"M\": 1000}"},
{"file":"scripts/breadboard.py","name":"stale drawing kept","find":"        if drawn.exists():\n            drawn.unlink()","replace":"        if drawn.exists():\n            pass"},
{"file":"scripts/check_spine.py","name":"stale file kept by _left_from_earlier","find":"    if path.exists():\n        path.unlink()","replace":"    if path.exists():\n        pass"},
{"file":"scripts/breadboard_steps.py","name":"color palette off by one","find":"self.PALETTE[(number - 1) % len(self.PALETTE)]","replace":"self.PALETTE[number % len(self.PALETTE)]"}
]
```

## Rerun after the fixes, 2026-10-16

The lead added a test for each escape, moved the table to `tests/mutations/p267-drawn-breadboard.json` and updated
the anchor of "stale drawing kept" to the new `unlink(missing_ok=True)`. `tools/mutate.py --copy` printed: "every
mutation was caught, and the suite is green with the files restored", 12 mutations in 277 s.
