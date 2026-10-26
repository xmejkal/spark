# P420: the facts copy right after the reset gets one retry, findings rows

Findings from the plan council and the build of P420 (2026-10-26, Prague, auto mode).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Retry the facts copy on any failure | plan | rejected | a full flash or a board that does not answer fails again, and "no answer" costs another 20 s. Only a raw REPL the board refused (`board_connection.RAW_REPL_REFUSED`) is retried. Test `test_only_a_refused_raw_repl_is_retried` |
| 2 | The read-back needs no retry | plan | rejected | `fs cat` enters the raw REPL too. The copy and its read-back are retried as a pair. A read-back that differs is never retried |
| 3 | 2 s is the right wait | plan | raised | a guess, marked so at `FACTS_RETRY_WAIT_S`. The bench can measure it. A board in download mode reads twice more, so it can cost up to 4 s more |
| 4 | `BoardCodeError` can come from a copy | plan council | raised | `copy_to_board` and `read_file` pass `ran_code=False`, so the real connection never raises it there. The `except` stays for a fake or a later connection |
| 5 | The look says whether the board holds `spark.json` | card | raised | the look never runs code on the board (`test_nothing_ever_runs_code_on_the_board`), and `fs cat` enters the raw REPL. The deploy's `facts_line` says it, and the store records the deploy. The card's "Done when" is changed. For the between-cards council: a bench step that reads `spark.json` |
| 6 | "second try" | plan | rejected | the repository's word is "retry" (`flasher.RETRY_WAIT_S`). The line says "(written on a retry after: ...)" |
| 7 | A failed retry still shows the first refusal | review | acted | it did not: the line said only the second reason, and the first refusal is the evidence the card was filed for. A failed retry now ends with "(the first try: ...)", and a retry that reads back different too. Two tests |
| 8 | "One retry" is per deploy | review | acted | per read of the board: `verify` reads again after download mode or an R press, and each read can retry once. agents.md says "for each read of the board" |
| 9 | The `BoardCodeError` clause in the retry rule matters | refuter | acted | it could never change the outcome: a `BoardCodeError` text never holds the raw-REPL words. Dropped. The `except` still catches it for the fakes |
| 10 | The human pages say the retry | review, refuter | acted | `commands/deploy.md` and `deploy.py`'s help have one sentence each. The README's Bench row is unchanged, because no status changed |
| 11 | mpremote prints the refusal as spark matches it | refuter | closed | mpremote 1.29.0 raises `TransportError("could not enter raw repl")`, lowercase, and the last stderr line holds it |
| 12 | The fakes' list handling is safe | review | raised | `uncopied` and `copy_raises` lists are consumed per call, including `fs cat`. Set per test, so no leak today. A class-level list would leak |
| 13 | The mutation run catches every planted defect | mutation-tester | acted | 9 planted, 8 caught on b979814. The escape, a `BoardCodeError` holding the raw-REPL words, is the clause row 9 dropped. On the final lines: 4 planted, 4 caught (426 s) |
