# P891: a dist copy that fails is its own entry, and the replaced board stays known: rows

Card: [P891 #1263](https://github.com/xmejkal/spark/issues/1263), an XS bug. One plan check (no council round) and a build
to the plan, with the coordinator's rulings. This file holds the acted and raised findings only (rules.md). 2026-11-18.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | row 14 of `p874-own-board.md`: the board is replaced and the `dist/` copy then raises, so the record keeps the old sha256 and every later build says `left alone` | plan refuter, round 2 (P874) | acted | `kept_into` catches the `OSError` around the `dist/` copy only and returns the entries it holds plus one `not kept` entry for `dist`; the failing test showed `left alone` on main |
| 2 | a first write has the same fault (`wrote`, then the `dist/` failure, so the record holds no sha256) | plan check | acted | the same fix; `test_a_first_board_written_before_a_dist_copy_that_fails_is_recorded_and_later_replaced` |
| 3 | row 28 of `p874-own-board.md`: a dangling link at `board.tsx` is written through and said as `wrote` | PR refuter (P874), the card's note | acted | `kept_into` treats a link as there (`is_symlink`), so it is `left alone` and nothing is written where it points; `test_a_dangling_link_at_board_tsx_is_left_alone_and_nothing_is_written_outside` |
| 4 | the two `"wrote"` literals beside the constant `WROTE` in `why_no_page` and `_breadboard_tab` | the card's note | acted | both use `WROTE`; the `find` text of two rows of `p271-page.json` follows (same meaning) |
| 5 | a second `.tsx` whose copy fails after the board was replaced loses the board's entry the same way | plan check | raised | a card, filed by the coordinator before the merge. The plan said "dropped because a footprint's name sorts before `board.tsx`". That is not enforced: `footprint_export` is letters, digits and `_` (`board_rules.footprint_export_problems`), so `xiao.tsx` sorts after `board.tsx`. A footprint copy fails only when the folder cannot be written, which would usually fail the board's own write first (`left alone`), so the case is narrow; not reproduced |
| 6 | the move of `StagedFile` to `spark/core` is not done here | the card's note | raised | a card, filed by the coordinator before the merge |
