# P730 the gate counts a spark session and a sound session: rows

`tools/check_backlog.py` judges Ready and Build per session, by the card's slice (`SOUND_SLICES`, `SESSION_LIMITS`,
`session_of`). Card: [P730 #998](https://github.com/xmejkal/spark/issues/998). Rows 1 to 7 are the refuter's plan check
(Opus).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | P609 is an epic and holds no place, so the live board shows sound at 0 and 0 | plan refuter | acted | the plan's verification line says so; the live check below reads it |
| 2 | `tests/test_board.py:300` needs a change: Build's limit is now 2 for spark | plan refuter | acted | the test holds 2 in Build as on track and 3 as at risk |
| 3 | three more texts state the limits: `scrum/README.md` (two places) and `scrum/WORKING_AGREEMENTS.md` | plan refuter | acted | each says the split and the slices; only `WORKING_AGREEMENTS.md` says that a card with no slice is spark's |
| 4 | `--help` fills from the table, so it must read `SESSION_LIMITS` | plan refuter | acted | `CHECKS` has a `%(sessions)s` line built from `SESSION_LIMITS`; the test pins "spark: Ready 4, Build 2; sound: Ready 1, Build 1" |
| 5 | "lane" already means the expedite lane in this file | plan refuter | acted | the code says "session"; the sentence says "(spark)" or "(sound)" |
| 6 | eight mutation rows lose their anchor | plan refuter | acted | ten did: `p102a-check-backlog` 1 ("a stage's limit is ignored"), `p146-process` 4 ("the stage loop ignores the lane", "an expedite lends Ready a place", "Ready reads as over at its limit", "Ready is never over"), `p146-wip-limits` 5 (Ready's and Build's limit rises and returns, "a stage at its limit reads as over"). `tests/mutations/p730-board-lanes.json` replaces them with a table of rows (17 after the review round) |
| 7 | the slice names are exact, `board.py` prints the gate's verdict with no count of its own, only `check_backlog.py` reads `LIMITS` | plan refuter | closed | confirmed, not redone |
| 8 | `docs/guide/developing.md` is at its budget of 379 lines | build | acted | the quoted sentence changed inside its two lines; the file still has 379 |
| 9 | the `LIMITS` values for Ready and Build are the sum of the sessions, so `--help` still prints "Ready 5, Build 3" | build | acted | closed by the review round: `LIMITS` holds only Discovery, Design and Review, `STAGES` gives `KNOWN` its order, and `--help` names Ready and Build only through the sessions line |
| 10 | `scrum/README.md:117` said one of Build's two places is the sound session's | review | acted | it says Build takes three, two of them spark's and one the sound session's |
| 11 | `test_an_expedite_lends_ready_no_place` held 6 cards, so the mutant "an expedite lends Ready a place" survived | review | acted | the test holds 4 plain cards and the expedite: "holds 5 (...) — its limit is 4" |
| 12 | six kinds of row were lost with the removed ones (loop ignores the session, Ready over at its limit, Ready never over, old limits return, Build over at its limit), and the "+1" row changed both arms | review | acted | the table splits it: Build and Ready each have a late-by-one row, plus an at-the-limit row for each, "Ready is never over", "spark's Ready limit falls", and the two old limits. Catchers: `test_a_third_spark_card_in_build_is_named_with_its_session`, `test_a_fifth_spark_card_in_ready_is_named_with_its_session`, `test_a_second_item_in_build_passes_and_a_third_is_named_with_all_three`, `test_a_board_at_the_flight_cap_with_a_full_ready_passes`, `test_an_expedite_lends_ready_no_place`. No run |
| 13 | `session_of` stood among the private helpers | review | acted | it stands above `problems()`, after the card helpers `rides` and `counts` |
| 14 | `docs/2026-10-06-process-design.md:7,173` state the old numbers | review | rejected | the file is a dated decision, and it stays |
