# P1020: the inflow and the retro's age in the status and the day close: rows

Card: [P1020 #1487](https://github.com/xmejkal/spark/issues/1487). Plan v2, 2026-11-22. The plan council: round 1 a
lens (Sonnet) and the refuter (Opus) on v1, round 2 the refuter (Opus) on v2. The build adds its own rows. This file
holds the acted, raised and rejected findings only, and the closed ones that a later reader needs.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | v1 made the counts outside the status's `try`, and asked for them when `gather` had failed, so an offline start waited twice | round 1, the lens 1 and the refuter 1 | acted | `main` calls `inflow_and_retro` only after `gather` succeeded. `test_a_status_whose_boards_were_not_read_asks_no_inflow` pins that `inflow_counts` is never called then |
| 2 | the tests that drive `main` would call the real gh for the inflow | round 1, the lens 2 | acted | they patch `inflow_counts`, as they patch `gather`. The PR lists each one |
| 3 | a close over a count not read would post a false AT_RISK that stays on the board | round 1, the lens 3 | acted | `main` prints the line not made, posts nothing and exits 1. `test_a_close_over_an_inflow_not_read_says_could_not_run_posts_nothing_and_fails`, row 10 of `tests/mutations/p1020-inflow-and-retro.json` |
| 4 | "flow" names the area `scripts/spark/flow` | round 1, the lens 4 | acted | the words are the inflow and the retro's age |
| 5 | `--date` leaves open what the two lines count from | round 1, the lens 5 | acted | they count from today, as the flight and the waits do. The `--date` help and the close help say so |
| 6 | the new lines' place, the disk line last, and a retro dated after today were not said | round 1, the lens 6 and the refuter | acted | the lines come before the disk line. A D below 0 does not slip. `test_the_two_lines_come_after_the_missing_close_and_before_the_disk_line_marked_when_they_slip`, `test_a_retro_seven_days_old_does_not_slip_eight_does_and_one_dated_tomorrow_does_not` |
| 7 | the docs list and the helps were incomplete | round 1, the lens 7 and the refuter | acted | the helps, the module docstring, `scrum/README.md`, `docs/guide/developing.md`, `docs/guide/agents/scripts.md` and the session-status design say the two lines |
| 8 | `ask` from board_read has no timeout of its own | round 1, the lens 8 | acted | `inflow_counts` calls `_gh` with the caller's timeout |
| 9 | equal numbers in the tests let a swap of filed and closed pass | round 1, the lens 10 | acted | the tests use 192 and 100. Row 5 of the table swaps them and goes red |
| 10 | the inflow's failures are caught as board_read catches them | round 1, the refuter 3 | acted | `inflow_counts` catches `FAILURES` and raises `Unreadable(cause(error))`. `test_an_inflow_that_cannot_be_read_is_unreadable_with_its_cause` |
| 11 | a fixture in the file's own order is needed, or a tie broken by place passes | round 1, the refuter 4, and round 2, fix 5 | acted | the fixture puts R4 before R3, and R11 before R10. Rows 6 and 7 go red |
| 12 | GitHub reads search dates in UTC, so the window ends on the UTC date | round 1, the refuter 5 and the lens 9 | acted | the seam `utc_today()`. `test_the_status_asks_the_inflow_over_the_utc_date_within_the_status_timeout`, row 13 |
| 13 | seven more tests drive `main` after `gather` succeeded, and a fake gh raises `StopIteration`, not in `FAILURES` | round 2, the refuter 1 | acted | each one patches `inflow_counts`. The status's guard catches `Exception` |
| 14 | the two lines go before `return lines + ([disk] if disk else [])`, a p435 anchor that stays as it is | round 2, the refuter 2 | acted | the line is unchanged. `--anchors` says 33 refused, as on main |
| 15 | the close's refusal must say the line not made, not `board: could-not-run`, and must not copy an anchored line | round 2, the refuter 3 | acted | it prints `filed in 7 days: could-not-run — <cause>`. No anchored line is copied: `--anchors` refuses no new row |
| 16 | the status's inflow must use `STATUS_TIMEOUT` | round 2, the refuter 5 | acted | `test_a_stalled_inflow_gives_up_within_the_status_timeout`, row 14 |
| 17 | the PR quotes real numbers, not a could-not-run line | round 2, the refuter 7 | acted | the PR quotes the grep's output |
| 18 | the existing close help test pins "at risk when the gate finds a problem or a wait is older than three days", so the new rule cannot join that sentence | the build | acted | the close help says the new rule in a sentence of its own |
| 19 | `docs/guide/developing.md` went 2 lines over its budget of 379 | the build | acted | the paragraph was cut to fit. The budget stays |
| 20 | GitHub accepts `first:0` on a search with two aliases | the build | closed | `gh api graphql` on 2026-11-22 answered 193 filed and 101 closed for 11-16..11-22. Round 1 measured 192, and one card was filed since |
| 21 | a test of `utc_today()`'s own body would compare it with `datetime.now(timezone.utc).date()` | the build | rejected | that is an arithmetic identity of the function, which the test rules forbid. The tests patch the seam, and row 13 pins that `main` uses it |
| 22 | the close finds a line not made by its text `: could-not-run — ` | the build | rejected | a second return value would add a shape for one caller. `inflow_and_retro_lines` is the one writer of that text, and rows 8 to 10 pin it |
| 23 | three more defects than the plan's nine and round 2's two: a retro not read taken as no slip, the age counted the wrong way, and the `!` dropped | the build | acted | rows 9, 3 and 12, each planted by hand and red |
