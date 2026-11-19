# P933: the kept-since date in the machine's zone: rows

Card: [P933 #1322](https://github.com/xmejkal/spark/issues/1322), from the review of P923. This file holds the acted,
raised and rejected findings only. The review: one lens on Sonnet and the refuter on Opus (5 claims: 4 hold, 1
refuted as worded). 2026-11-19.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the new finding test passes only in the Prague zone, because its class pins no zone | the refuter, finding 6, run under Los Angeles and Tokyo | acted | fixed: `pin_time_zone` in both new tests, and in test 19, which says "kept since" too and failed under Tokyo. Five test files pass under five zones |
| 2 | the PR says that `--json` is unchanged, and the sentences of look.py's and deploy.py's findings carry the new date | the refuter, claim c | acted | fixed: the PR says that the data is unchanged and the sentences change |
| 3 | the view test reads the sixth line by its position | the lens, question 5 | acted | fixed: it finds the "kept for" line by its label |
| 4 | on Python 3.10 `20261119T10Z` prints as stored, and 3.11 says it in the machine's zone | the refuter, note 7 | rejected | dropped because both follow the documented rule: a time that does not parse is said as stored |
