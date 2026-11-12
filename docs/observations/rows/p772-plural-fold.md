# P772 the plural fold maps a plural and its singular to one word: rows

Card: [P772 #1063](https://github.com/xmejkal/spark/issues/1063), chore, XS, logic, under P735. Plan
`~/.claude/plans/p772-plural-fold.md`. Rows 1 to 6 are the plan refuter (Opus), 7 and 8 the implementer. 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the plan credited Harman's S-stemmer with the length guard on `-ies`, but Harman's rule has none ("dies" would become "dy") | plan refuter | acted | the docstring credits Harman for `-ies` to `y` and names spark's guard on its own |
| 2 | a plural of a word in `-ie` folds wrong: "movies" to "movy", while "movie" stays "movie". Today they match | plan refuter | acted | a known trade, beside row 7. Of 1,034 words in 183 records, none ends in `-ies` with a singular in `-ie` |
| 3 | no test word ends in `-shes`, so dropping it from `HISSING_ES` would pass | plan refuter | acted | "brushes" in the test, and a mutation row for it |
| 4 | the new fold breaks a word that folds right today | plan refuter | rejected | 10 of 1,034 words change: 8 better (switches, touches, pushes, presses, reaches, watches, addresses, misses), 2 neutral (axes, series fold alike on both sides). `tools/match_eval.py` prints the same |
| 5 | `same_words` does not use the fold, so a fit's `exact` can still differ between "load switch" and "load switches" | plan refuter | raised | it decides `shown` past the first 8 rows and `--match`'s `what_matches`. The card asks only for the same score |
| 6 | the plan named no rows file and did not close P743's item | plan refuter | acted | this file, and p743 row 27 acted |
| 7 | "caches" folds to "cach" while "cache" stays "cache". Today they match | implementer | acted | a known trade: words in `-ches` (switches, inches, latches) outnumber words in `-che` in this domain |
| 8 | `tools/mutate.py --anchors tests/mutations/*.json` refuses 130 rows on main, many more than the seven noted on 2026-11-11 | implementer | raised | this branch refuses the same 130, so it adds none. For the next mutation sweep |
