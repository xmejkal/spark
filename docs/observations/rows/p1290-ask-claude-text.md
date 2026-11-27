# P1290: "Ask Claude" as text with Copy: rows

Card: [P1290 #1856](https://github.com/xmejkal/spark/issues/1856). The plan writer (Opus) revised the plan after a lens and
the refuter; the delegated council (the PO assistant, the tech lead and the architect, all on Opus) gave eight fixes.
Rows 1 to 9 are the plan's, rows 10 to 17 the delegated council's. This file holds the acted, raised and rejected findings
only. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Copy is silent on a refusal of the clipboard and with no clipboard | refuter 6 | acted | `NOT_COPIED_SAYS` reaches the script as `not_copied`; `page_script.test.js` has three tests of a refused Copy |
| 2 | NEXT repeats "Ask Claude" over the block that holds the ask | UX lens 1 | acted | `next_words.next_words` gives NEXT's words over a tell; `tests/test_next_words.py` (f) checks each picker case |
| 3 | the confirm's docstring promises the wait, which the confirm does not hold | UX lens 2 | acted | `flow_page.page_words` docstring says where the wait stands: `intro` and, after Send, `waiting` |
| 4 | the council's line numbers for `copyTell` and the docstring moved | plan | acted | the plan cites `page_script.ts:553-559` and `flow_page.py:71` |
| 5 | `flow_codes.py` has 598 lines and R1 fails above 600 | plan refuter 1 | acted | the page-only words went to `next_words.py`; `flow_codes.py` is 599 lines |
| 6 | the guard is a string match on the sentence | plan lens 4, refuter 4 | acted | one rule `tell_of(now)`, which `_ask` and `next_words` share; the two jobs are chosen by `now["steps"]` |
| 7 | the names `NOW_ASK` and `TWO_JOBS_ASK_NOW` repeat "ask" | plan lens 2 | acted | `NOW_WITH_TELL` and `TWO_JOBS_WITH_TELL_NOW` |
| 8 | `docs/guide/agents/flow.md:165` says NEXT is the guide's sentence | plan refuter 2 | acted | the line names the words over a tell |
| 9 | the cost in the simulation's tell | council refuter 10, UX lens 1 | rejected | a tell names the job (flow_codes.py, the offer kinds); NEXT, which the person reads, carries the cost now, and `SCENARIO_WHY` makes Claude ask before each run |
| 10 | two jobs say "ask Claude to write the firmware" over a tell | PO assistant 1 | acted | the two-jobs words say "and get the firmware from Claude." |
| 11 | `next_words` is missing from `TheFlowAreaTest.MODULES` | architect 1 | acted | listed between `guide` and `no_model` |
| 12 | "Spark cannot see your wiring." is written twice | architect 2 | acted | `WIRING_UNSEEN_MESSAGE` on the tuple line with `TWO_JOBS_START` and `WOKWI_COST_MESSAGE`; "No scenario is written yet" has no constant, since the CLI sentence and NEXT's words differ and the line is full |
| 13 | the docstrings of `next_words` miss the call rule, the steps invariant and NOW_BUTTON | architect 3 | acted | the module and function docstrings say them |
| 14 | the page budgets of flow.md (399 of 400) and patterns-and-names.md (272 of 272) fail the push | tech lead 1 | acted | each edit is inside an existing line; `wc -l` shows 399 and 272 |
| 15 | script tests (a) and (b) cannot catch a disabled Copy | tech lead 2 | acted | both tests check `[textContent, disabled]` |
| 16 | two mutation rows share one anchor | tech lead 3 | acted | each anchor carries its own context; the JS mutants were run by hand against `page_script.test.js` and all fail it |
| 17 | `copyCommand` of `/spark:page` says nothing on success or on a refusal | refuter | raised | P1339 [#1921](https://github.com/xmejkal/spark/issues/1921) |
| 18 | the deploy's NOW sentences still say "Ask Claude" over the look's tell | plan | raised | P1338 [#1920](https://github.com/xmejkal/spark/issues/1920) |
| 19 | `flow_codes.py` stands at 599 of 600 lines: the next card that adds a line must move words out first | build | raised | named in the PR body; no card needed |
