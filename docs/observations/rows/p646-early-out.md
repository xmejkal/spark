# P646 the early-out in the fire's LINEAR blend: rows

What the Mac count, the plan check, the PR review, the PR refuter and the board runs found. Card:
[P646 #865](https://github.com/xmejkal/spark/issues/865). PRs: [pixel-engine #2](https://github.com/xmejkal/pixel-engine/pull/2),
[pixel-games #42](https://github.com/xmejkal/pixel-games/pull/42). Bench rows: pixel-games `bench.md`, the P646 section.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | In the burning scene, a per-cell check skips 95 to 97% of the front pass's 38,400 cells (first heat with alpha 101) and 81 to 89% of the picture field pass's (first heat 1). A per-row trim skips almost as many, a whole-field band of rows 0 to 71% | the lead's Mac count (scratch `count646.py`, frames 200 to 1000) | acted | the plan picks the per-cell check, the smallest change that skips the most |
| 2 | The count used the limit 4T - 4, the code 4T - 3, so the count is a lower bound | the plan refuter (Fable) | acted | said in the plan and in `bench.md` |
| 3 | The skip is exact: an exhaustive check for T 0 to 256 and 3,000 random fields with holes in the alpha table gave 0 violations, and 4T - 3 is the largest safe limit | the plan refuter (Fable) | verified | the PR refuter repeated it on the built code (row 7) |
| 4 | A test whose cold cells are all 0 hides a skipped `up = m; m = down` shift, because the stale mix equals the real one | the plan refuter | acted | the cold cells take heats 1 to 100 |
| 5 | Setting `self.mode` after `setup` changes nothing (P601 row 15), so the probe must call `set_mode` | the plan refuter | acted | the probe's `setup` calls `set_mode(MODE)` and `begin()` |
| 6 | No test used a small first heat, such as the picture field's 1 | the PR reviewer (Sonnet) | acted | the boundary test runs at first heat 101 and 1 (9171377) |
| 7 | No output difference in 4,560 scenes against the old code (sizes 1 x 1 to 24 x 18, T 0 to 256, holes, fields all 0, all 255, random, near the threshold). 8 of 11 planted defects were caught; the other 3 only skip fewer cells, so they are equivalent | the PR refuter (Fable) | verified | pixel-games #42 |
| 8 | A dropped `up` in the check was caught only by random data, which depends on where the hot block falls | the PR refuter | acted | a fixed test with hot cells on the top and bottom rows. With cold heat 50 it still missed a dropped `up`, so the lead raised it to 90; both planted defects then failed it (9171377) |
| 9 | Linear draws 13.21 to 13.78 ms at 24 fps (runs 128 and 129), 1.7 to 1.8 ms less than P601's runs 124 and 125. It misses D5 by 0.28 ms at its slowest line, and by 0.78 ms with the 0.5 ms spare | the board, 2026-11-06 | acted | pixel-games `bench.md`, the P646 section |
| 10 | Picture draws 14.78 to 16.48 ms at 22 to 23 fps, 2.8 to 3.5 ms less. It misses D5 by up to 2.98 ms, by 3.48 ms with the spare | the board, 2026-11-06 | raised | for P601's SWAR and PIE experiment, timed against this code |
