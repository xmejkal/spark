# P473 the store in a next step: rows

What the plan, the hook, the review and the mutation run found. Card: [P473 #647](https://github.com/xmejkal/spark/issues/647).
PR: https://github.com/xmejkal/spark/pull/832. Built in the PO's auto mode on 2026-11-05.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Plan round 1 (Fable 5.1), MUST: on this Mac a temp folder resolves from /var to /private/var, so the end-to-end test compares resolved paths | the plan | acted | the test resolves both sides |
| 2 | Plan round 1, MUST: `truncated.next` (`outcomes.py:158`) is a step with argv for `parts.py`, not a command list | the plan | acted | the paged answers carry `env` |
| 3 | Plan round 2 (Fable 5.1): no MUST. `deploy.py --dry-run --json` exits 0 or 2 by whether esptool is installed, so the test reads only `next[0]` | the plan | acted | the test asserts no exit code |
| 4 | The push hook refused the branch twice on R3: `outcomes.step` and `outcomes.page` rose from 6 to 7 parameters. The implementer had not run the architecture test, and the hook prints no failing test's name | the hook | acted | `outcomes.add_env` (cfee6042). Lesson: run `tests.test_architecture` before a push. A hook that names its failure would save a 5-minute rerun: a row for P495 #677 |
| 5 | The first fix put `page_with_store` in `parts.py` and raised it past its R1 baseline (2,375 lines) | `tests.test_architecture` | acted | the helper lives in `store.py`. `parts.py` stays at 2,373 lines |
| 6 | The Sonnet reviewer and the Fable refuter found no MUST. The refuter confirmed the claim by reproduction: an absolute, a relative and a spaced `SPARK_HOME`, deploy, the paged `parts.py --list` and the fact-set step | PR 832 | verified | |
| 7 | Both found that no test failed if `parts.py`'s steps lost `env` | PR 832 | acted | two assertions in `tests/test_parts.py` (00bd641f) |
| 8 | The refuter found that json.md overclaimed: a store found through `XDG_DATA_HOME` gives no `env` | PR 832 | acted | json.md says only `SPARK_HOME` rides the step |
| 9 | The reviewer's NIT: `outcomes.step(*step[:-1])` breaks unseen if a field is added | PR 832 | acted | result.py names NextStep's fields |
| 10 | The refuter's NITs, before this card: the look and deploy steps' argv lack `--json`, so a step followed word for word prints text. `SPARK_HOME=~/s` is not expanded. A text print of a parts.py step shows no `env` | PR 832 | closed | for the PO: one card for "a step followed as given answers in JSON" — P776: stale note: dropped by P776: a NIT the refuter named; the steps run |
| 11 | The mutation run (Sonnet) planted 13 defects, and the tests caught all 13. It ran a narrowed set of 826 tests in 52 s, because `mutate.py --tests` takes a folder and the whole suite takes 5 minutes a mutant | the mutation run | verified | for P495 #677: let `mutate.py` take test modules |
| 12 | The plan's approval is the PO's. In auto mode the card went from a plan with two council rounds to this PR, and the PO can still reject the plan here | the lead | raised | for the retro: does auto mode build an S card after its council, or stop at "plan ready"? — P776: waits on the PO: Auto mode plan approval is the PO's. — P776: waits on the PO: Auto mode plan approval is the PO's. |
