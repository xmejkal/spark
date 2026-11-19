# P923: bench.py show says a deploy's last date in the machine's zone: rows

Card: [P923 #1307](https://github.com/xmejkal/spark/issues/1307), a bug from the review of PR #1306. The plan is a
comment on the card. This file holds the acted, raised and rejected findings only. The review: one plan check and one
lens on Sonnet, and the refuter on Opus (7 verdicts: 4 holds, 2 partly, 1 refuted). 2026-11-19.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | on Python 3.11 and later a short stored text with no zone (`20261117`) prints `last 20261117 (`, a part of the zone note | the refuter, claim 3, run on 3.11 and 3.13 | acted | fixed: `show_bench._date_said` cuts at the stored text's length. On 3.13 a copy with the fix passed 11 tests and a copy without it failed 1 |
| 2 | no page says that a time that does not parse prints as stored | the lens, finding 2 | acted | fixed: the help text of `bench.py show` and `docs/guide/agents/bench.md` say it |
| 3 | "prints its date" on the agents' page can mean two dates, and "when the stored time has a zone" can read as no date otherwise | the lens, finding 3 | acted | fixed: both sentences name the date of `last` and both cases |
| 4 | the docstring of `time_said` says that the view shares the whole text, and the view takes only the date | the lens, finding 4 | acted | fixed: "the view takes its date from it" |
| 5 | the PR's body says the "kept for … (since …)" date is cut "in four places", and one of the four is that line | the refuter, claim 7 | acted | fixed: the body names the four lines and the card |
| 6 | `known.at[:10]` is printed in four lines and no line says it in the machine's zone | the plan check, question 4, and the lens, finding 1 | raised | a card: [P933 #1322](https://github.com/xmejkal/spark/issues/1322), in Idea |
| 7 | the tag "(P923)" stands inside a sentence of `_deploys_said`'s docstring | the lens, finding 5 | rejected | dropped because the fix of row 1 moved that sentence into `_date_said`, and the file's other docstrings carry their tags the same way |
