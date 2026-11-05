# P517 the build names the firmware step: rows

What the plan check, the build, the review, the refuter and the mutation run found. Card: [P517 #713](https://github.com/xmejkal/spark/issues/713).
PR: https://github.com/xmejkal/spark/pull/833. The PO chose A on 2026-11-05: the step's `why` names `pins.py`.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Plan check (Fable 5.1), MUST: `check_spine.py` sits at its R1 baseline (1,028 lines), so every net line it gains fails `tests.test_architecture` | the plan | acted | the builders live in `board_envelope.py`, and check_spine pruned two lines for its two new ones |
| 2 | Plan check, MUST: `report()` has 5 parameters, the R3 limit | the plan | acted | `firmware_next_steps` derives the project from `args.requirements` |
| 3 | The plan said `store.format_rerun_line("look.py", ...)`, but that resolves against the current folder | the build | acted | it passes `Path(__file__).with_name("look.py")`. Plans hold wrong claims: the implementer checked this one in the code |
| 4 | The first tests used `mock.patch` on check_spine and broke architecture rule T2 | the build | acted | the tests call `report()` directly |
| 5 | The docs line budgets (json.md 427, agents.md 185) forced existing text shorter | the build | acted | the agents.md firmware rule went into item 6, not a new item |
| 6 | Review (Sonnet), SHOULD: no test sets `SPARK_HOME` or uses a project path with a space, so losing `env` or the quoting would pass | the review | acted | `test_the_step_carries_the_store_and_the_line_quotes_a_space` (a3072600) |
| 7 | Review, SHOULD: no test runs `main()` with `--keep` and a real requirements file, so `next` beside `kept` is not shown in the real flow | the review | rejected | the refuter ran it live on a real project and saw `next` beside the other keys. The unit tests pin the rule |
| 8 | Review, NIT: `next` comes after `unserved` in the JSON, the plan said before | the review | closed | harmless: the contract test sorts the keys. The code's order stays |
| 9 | Review, NIT: without `--keep` no `pins.py` exists, yet the `why` names it | the review | acted | json.md says the pin map is what `--keep` writes. The PO chose the card's words (A) |
| 10 | Refuter (Fable 5.1), SHOULD: the text line separated the `why` with ` -- `, so pasting the whole line made `look.py` fail with "unrecognized arguments" | the refuter | acted | the line uses ` — `, as `parts.py:2320` does (one word for one thing) |
| 11 | Refuter: every claim CONFIRMED live (text, `--json`, `SPARK_HOME`, a path with a space, another current folder, library, could-not-run and reference runs, the printed command runs). No MUST | the refuter | closed | no change |
| 12 | Mutation run on a3072600: 12 planted, 12 caught | `tools/mutate.py --copy` | closed | no escape |
| 13 | The mutation run took 2,637 s (44 min), because each of the 12 rows ran the whole suite. The agent hit its 30-minute limit before the run printed anything | the lead | raised | a row for P495 #677: run a table with `--tests` limited to the card's test files first, and pipe its output to a file, not through `tail` |
