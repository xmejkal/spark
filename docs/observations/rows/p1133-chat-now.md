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
| 9 | The plan said the p1140 row on `with_requirements_now` keeps its anchor | build | acted | v2-1 moved it, and the review's refactor (row 11) moved it again, onto `return requirements_now(sentence.by, written)`. The p1043 rows on `with_deploy_now` kept their anchors, as planned |
| 10 | the build's review ran: the architecture lens and the refuter, both on Opus, 2026-11-26. The refuter compared 34 project states on both trees (136 of 136 files identical) and probed every (phase, status): the only difference is the named swapped case | the review | acted | rows 11 to 15 |
| 11 | v2-1 asked for one lookup on the last sentence, but `chat_offer_of` ran in three places, and the order `guide_of` overwrote the dict decided which sentence won | the lens | acted | `with_deploy_now` and `with_requirements_now` take and give a NowSentence; `now_sentence` gives the first; `now_of` builds the dict once with the one `chat_offer_of`. The P1122, P1140 and P977 rows on those lines are re-anchored, and each is caught by hand |
| 12 | the NowSentence comment and the names page name two pickers | the lens | acted | both name `guide.requirements_now` and the one lookup on the last sentence |
| 13 | the v2-3 test's comment says "one entry per branch", but the pickers give 45 pairs over every phase and status | the lens | acted | the comment says the set is the pairs of the phases with a chat offer, as in the plan's table; row 11 of the table proves it catches a stray key |
| 14 | rows-file row 9 contradicted itself about which rows kept their anchors | the lens and the refuter | acted | row 9 rewritten |
| 15 | with `deploy=None`, `guide_of` reads the deploy twice, and `with_requirements_now` reads `is_as_written` again after the phase reader | the lens, older than this card | rejected | the product path passes the one DeployState (`show_flow.py:122`), so the second read happens only in tests that pass none; `is_as_written` is the one rule, read by each of its two readers as P1140 decided |
| 16 | the refuter's pass on the fix commit: the guide's `now` and `no_open_phase` over 17,568 cases, `show`, `--json` and `page` on 7 projects, and every mutation anchor | the refuter's pass on the fix commit | acted | no difference between f5a5ffc1 and the fix, and the three re-anchored rows are caught when planted; nothing more to change |
