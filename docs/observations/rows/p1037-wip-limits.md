# P1037: spark's limits become Build 5, flight 7 and Review 3: rows

Card: [P1037 #1520](https://github.com/xmejkal/spark/issues/1520). This file holds the acted, raised and rejected findings
only. The change has no new code path, so its review was one refuter on Opus. 2026-11-23.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a page, a help text, a test or a tool still states the old numbers as current | the review, the refuter | rejected | only history keeps them: scrum/README.md's 2026-10-06 trial and the P978 notes in the W6 and LANES comments. The `--help` is built from LANES and LIMITS |
| 2 | the PO's rules file still says "in flight (5 and 2, P918, P978)" | the review, the refuter | raised | outside the tree, his file to change: named to the PO in spark-main's reply |
| 3 | the LIMITS comment says "Every working stage takes 2" beside "Review takes 3" | the review, the refuter | acted | fixed: the comment now says Discovery and Design take 2 |
| 4 | `BIN_FIFTH` in tests/test_board.py is the eighth card in flight | the review, the refuter | acted | fixed: renamed `BIN_EIGHTH` |
| 5 | a test lost its boundary when its fixture moved to the new limits | the review, the refuter | rejected | each limit changed by one up and down in a scratch worktree failed tests in both modules (7 to 23 in test_check_backlog, 1 to 4 in test_board) |
| 6 | the PR adds refused mutation anchors | the review, the refuter | rejected | `mutate.py --anchors tests/mutations/*.json` gives the same 33 refused on main and on the PR, and `diff` finds the outputs identical |
