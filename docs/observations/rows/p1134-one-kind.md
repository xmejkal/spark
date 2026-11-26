# P1134: one kind_of(key) and one is_sendable(key) in flow_codes: rows

Card: [P1134 #1669](https://github.com/xmejkal/spark/issues/1669), under P1038 #1521, beside P1082 #1587. The plan had one
council round, the architecture lens (Opus) and the refuter (Opus). This file holds the acted, raised and rejected findings
only. A "row" in the last column is a row of a `tests/mutations/` table, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The four places that answer "can the page send it" agree for every kind today, and their differences are on purpose (the op check, the chat check, the offered and stale checks) | plan, refuter (C8) | closed | The plan's two tables of what each place decides and answers per kind. Nothing changes in behaviour |
| 2 | A fifth spelling of `kind_of` stands in `wired_board.py:54` | lens, refuter (C1) | acted | `wired_offer` reads `flow_codes.kind_of(offer.key)` |
| 3 | `run_request` read the fixed `IN_CHAT` and the live `is_sendable`, so they could disagree | lens (C2) | acted | One `flow_codes.in_chat(key)`, `IN_CHAT` is gone. The step 2 test asserts `request_in_chat` under T6's swap. The p829 and p1122 rows on `IN_CHAT` are re-anchored on `in_chat`, and new row 8 plants `in_chat` true for an unknown kind, new row 9 a run that never asks it |
| 4 | `OfferKind.from_page` (by kind) and `STEP_OPERATIONS` (by op) hold one fact twice, and only T6 keeps them equal | lens (C3) | raised | A comment on P1082 #1587, posted by the PO. The names page says so too. Whether one derives from the other is P1082's |
| 5 | `from_page` means two things: the kind only (`OfferKind`) and the kind with its op on the allow-list (the design basis) | lens (C4) | acted | `docs/guide/patterns-and-names.md` says it in one clause |
| 6 | `LAST_REQUEST_KINDS` and `RAN_OK_SAYS` list the sendable kinds by hand and no test ties them to `SENDABLE` | lens (C5) | acted | `test_the_words_of_a_request_whose_offer_left_the_page_are_those_of_the_sendable_kinds`. It was green on its first run, which is the claim: the lists agree today |
| 7 | `tests/test_routes.py:346` names the old home of the rule | lens (C6) | acted | The comment names `flow_codes.is_sendable` |
| 8 | With the mutant `SENDABLE = tuple(OFFER_KINDS)` only step 1's literal test catches the p1122 row | refuter (C7) | acted | The row's name names `test_only_a_pick_the_parts_list_and_the_build_are_sendable` |
| 9 | The page script's `kindOf` is a cross-language twin of the one-line parse, and the fix touches the request row's shape and `/spark:page` | lens (C15) | raised | The Idea card P1226 [#1778](https://github.com/xmejkal/spark/issues/1778), filed before the merge |
| 10 | The plan's row 6 (`run_request` reads the tuple `SENDABLE`, not the live rule) is caught by `test_one_row_s_from_page_…` | plan, refuter (C12), measured by the build | rejected | After v2-2 the run asks `in_chat` first, so under the swap a flipped kind is refused as in the chat before the `is_sendable` clause is reached: the mutant survived by hand. The clause matters only for a kind spark does not know, which `test_an_offered_key_of_a_kind_the_page_never_runs_runs_nothing` and the p829 row "a kind the page never runs is run" catch. Row not written: 8 new rows, not 9 |
| 11 | The step 2 test cannot use `mock.patch.object` (the plan's choice): T2 refuses a new `mock.patch` in a test file | build | acted | The test swaps `flow_codes.OFFER_KINDS` by hand in a `try`/`finally`, as T6's `swapped` does |
