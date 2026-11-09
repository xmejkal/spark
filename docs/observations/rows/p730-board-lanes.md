# P730 the gate counts a spark session and a sound session: rows

`tools/check_backlog.py` judges Ready and Build per session, by the card's slice (`SOUND_SLICES`, `SESSION_LIMITS`,
`session_of`). Card: [P730 #998](https://github.com/xmejkal/spark/issues/998). Rows 1 to 7 are the refuter's plan check
(Opus).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | P609 is an epic and holds no place, so the live board shows sound at 0 and 0 | plan refuter | acted | the plan's verification line says so; the live check below reads it |
| 2 | `tests/test_board.py:300` needs a change: Build's limit is now 2 for spark | plan refuter | acted | the test holds 2 in Build as on track and 3 as at risk |
| 3 | three more texts state the limits: `scrum/README.md` (two places) and `scrum/WORKING_AGREEMENTS.md` | plan refuter | acted | each says the split, the slices and that a card with no slice is spark's |
| 4 | `--help` fills from the table, so it must read `SESSION_LIMITS` | plan refuter | acted | `CHECKS` has a `%(sessions)s` line built from `SESSION_LIMITS`; the test pins "spark: Ready 4, Build 2; sound: Ready 1, Build 1" |
| 5 | "lane" already means the expedite lane in this file | plan refuter | acted | the code says "session"; the sentence says "(spark)" or "(sound)" |
| 6 | eight mutation rows lose their anchor | plan refuter | acted | ten did: `p102a-check-backlog` 1 ("a stage's limit is ignored"), `p146-process` 4 ("the stage loop ignores the lane", "an expedite lends Ready a place", "Ready reads as over at its limit", "Ready is never over"), `p146-wip-limits` 5 (Ready's and Build's limit rises and returns, "a stage at its limit reads as over"). `tests/mutations/p730-board-lanes.json` replaces them with 13 rows |
| 7 | the slice names are exact, `board.py` prints the gate's verdict with no count of its own, only `check_backlog.py` reads `LIMITS` | plan refuter | closed | confirmed, not redone |
| 8 | `docs/guide/developing.md` is at its budget of 379 lines | build | acted | the quoted sentence changed inside its two lines; the file still has 379 |
| 9 | the `LIMITS` values for Ready and Build are the sum of the sessions, so `--help` still prints "Ready 5, Build 3" | build | raised | a reader can take that for the spark limit; the added sessions line beside it names the split. Left as the plan says |
