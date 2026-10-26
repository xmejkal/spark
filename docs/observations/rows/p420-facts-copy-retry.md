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
