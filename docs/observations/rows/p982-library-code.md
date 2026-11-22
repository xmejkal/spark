# P982: research says `library_record` for a record of spark's library: rows

Card: [P982 #1424](https://github.com/xmejkal/spark/issues/1424). This file holds the acted, raised and rejected findings of the build. 2026-11-22.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | research's refusal keeps exit 2 and only its code changes | the build | acted | the exit code comes from the run's status (`could-not-run`, as for `no_such_part`), not from the code; `json.md` and `scripts.md` tie no exit to the word `bad_argument` for this refusal, so nothing else moves |
| 2 | `BAD_ARGUMENT_IN_LIBRARY` has no other use | the build | acted | grep over scripts, tests, docs, goldens and mutation rows found only research and a planted source line in `test_json_contracts.py`, now `LIBRARY_RECORD`; the constant is removed |
| 3 | the fix text of research's refusal changes to the code's own fix | the build | acted | `test_research.py` pins the new literal fix; `json.md` says research uses `library_record` |
