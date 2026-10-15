# P251's PR review (#280), 2026-10-15

A review lens (Sonnet, S), a refuter (Opus, X) and the mutation tester (Opus) read the PR after the code. Each line is
one finding in short.

| id | finding | verdict |
| --- | --- | --- |
| S1 | `restarted` matched `rst:` inside words such as `first:` | acted (`shows_restart`, the ROM's `rst:0x..` only) |
| S2 | `--cure-first` printed a first try that never ran | acted (`first_try_failed` None, "the cure came first", `cure_first` in the JSON) |
| S3 | "the firmware is stopped" printed although no exec ran | acted (only after a reach) |
| S4 | `--cure-first` with no probe, a failed cure read, and a loose "cure" assert were untested | acted |
| S5 | the cure's read error was lost from `why` | acted (`why_of`) |
| S6 | the pass-through methods had no docstrings | acted |
| S7 | `restarted`, `lines` and `as_json` do not start with a verb | acted (`shows_restart`, `describe`, `to_json`) |
| S8 | a missing board and a silent board look alike | rejected: the first failure is not the raw-REPL refusal then, so no cure runs |
| X1 | the read script lost every byte when the port dropped, `rst:` too | acted (it prints what it read in `finally`; the cure keeps it) |
| X2 | the retry came at once after the port was back | acted (`PORT_SETTLE_S = 2`, a guess the bench tests; `port_back` in `Cure`) |
| X3 | every failed retry blamed the board | acted (the two causes only after a second raw-REPL refusal) |
| X4 | an answer without `reached` counted as a reach | acted |
| X5 | deploy's behaviour did not change in the move | note |
| X6 | the tests only fed in the `Cure` they asserted | acted (a real probe through `reach()`) |
| M1 | 12 planted, 11 caught; the escape: `--cure-first` with no probe | acted (a test; the table in `tests/mutations/p251-reach.json`, 18 rows, all 18 caught after the fixes) |
