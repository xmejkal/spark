# P1133: each NOW sentence picker returns the value it chose the sentence by, and one CHAT_NOW lookup reads it: rows

Card: [P1133 #1668](https://github.com/xmejkal/spark/issues/1668), under P1038 #1521, beside P1122 #1652. The plan had one
council (2026-11-26): the architecture lens (Opus) and the refuter (Opus), who built the plan in a scratch worktree. This
file holds the acted, raised and rejected findings only. A "row" in the last column is a row of
`tests/mutations/p1133-chat-now.json`, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | A deploy phase that is partial with no board log read by the guide said "could not run" beside the look's tell | plan council, the probe | acted | `TheChatOfferTest.test_a_deploy_phase_that_is_partial_with_no_board_log_says_could_not_run_and_names_none`, red before the change. Row 3 plants the mutant |
| 2 | The CHAT_NOW lookup and the NOW pickers walked the same branches | the card, P1122 row 5 | acted | `TheNowSentenceTest` and rows 1 to 9 |
| 3 | `with_requirements_now` (P1140) is a third picker: a stale parts list would carry a value that is not the sentence's | lens (A1) | acted | v2-1: `guide.requirements_now` gives a NowSentence chosen by `(requirements, stale)`, and `TheNowSentenceTest.test_a_stale_parts_list_is_a_picker_too_and_names_no_chat_offer` pins it. Row 10 plants the mutant |
| 4 | No test makes sure every CHAT_NOW key is a value a picker can return | lens (A3) | acted | v2-3: `TheNowSentenceTest.test_every_key_of_the_chat_offer_table_is_a_value_some_picker_returns`. Row 11 plants a key no picker returns |
| 5 | `chosen_by` beside `by` can read as "chosen by whom" | lens (A4) | rejected | The name stays. `docs/guide/patterns-and-names.md` and the NowSentence comment say it is a (phase, value) pair, never an actor |
| 6 | The deploy pair was built from the log's copy of the string `FLASH_NOT_FINISHED` | lens (A5) | acted | `deploy_now` writes `flow_codes.FLASH_NOT_FINISHED`, the constant its branch tested |
| 7 | `phase_steps.simulate_steps` and `scenario_steps` walk the simulate branches a third time, for the step | lens (A2) | raised | [P1244 #1801](https://github.com/xmejkal/spark/issues/1801) |
| 8 | Four citations of the plan were off | refuter | acted | Corrected in the build (`OfferKind` at flow_codes.py:150, 13 tests of `TheChatOfferTest`, the self-confirmation phrase, `flow.md:24`) |
| 9 | The plan said the p1043 row 11 and the p1140 row 7 keep their anchors | build | acted | They did not: the p1043 row still anchors because `with_deploy_now` keeps its `state = ...` line, and the p1140 row is re-anchored on the new `dict(said, says=told.says, chat_offer=chat_offer_of(told))` line, because of v2-1 |
