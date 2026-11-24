# P1102: the design basis, generated from the code: rows

Card: [P1102 #1622](https://github.com/xmejkal/spark/issues/1622), PR #1639. The plan council: round 1 a lens (Sonnet)
and the refuter (Opus) on main 933e2c89, round 2 the refuter (Opus) on the changed parts. The PR review: a lens
(Sonnet) and the refuter (Opus). This file holds the acted, raised and rejected findings only. A "row" in the last
column is a row of `tests/mutations/p1102-design-basis.json`, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Each Operation has a `summary` of its own | plan | rejected | Round 1's refuter: 32 of 50 have `summary = None`. The tool reads `describe_operations.summary_of`. T5, row 9 |
| 2 | "basis" alone already means whether the needs fit the goal (`needs-basis.json`) | plan round 1 | acted | The term is always "design basis". Unbuilt steps are `unbuilt:*`, and a key's prefix is a group |
| 3 | The page sends an offer only when its kind is in `SENDABLE`, its op is in `STEP_OPERATIONS` and its kind is not in `IN_CHAT` | plan rounds 1 and 2, PR refuter | acted | `from_page` reads all three lists through their modules. T6 swaps each list. Rows 6, 7 and 10 |
| 4 | A reader's `BY` is only the usual actor | plan round 1 | acted | The key is `usual_by`, and the page says that `guide.now.by` holds the actual one. T2, row 2 |
| 5 | P54 refused 13 reads of the code's own constants in the tests | build | acted | T2, T4, T10 and T11 pin literals. `flow_codes.SENDABLE` and `run_request.IN_CHAT` get an AGREEMENT reason |
| 6 | The two new `MAY_READ` entries loosen P54's guard | spark-main | rejected | The PR refuter: the tool's `OFFER_STEPS` is written by hand and not built from either list, so a new kind in either list fails T6 |
| 7 | T5 compares a summary with the same `summary_of` that the tool calls, which P54 does not see | PR refuter | acted | Sameness with `--describe` on purpose. The page says that the summary is the one `--describe` prints. T1 holds the text |
| 8 | The card asks for each phase with its statuses and its offers. The design basis lists them as groups | PR refuter | acted, in part | Each offer now names the phase whose reader makes it (T6). Which statuses a phase can show is not listed: the page says that each phase reader decides it. Raised: [P1105 #1625](https://github.com/xmejkal/spark/issues/1625) decides whether the check needs it |
| 9 | `of(root)` never reads its root | PR lens | acted | `DesignBasis.of()` takes no root. `main` keeps its root for the write (T9) |
| 10 | "Keys" means two things on the page, and two words are not defined | PR lens | acted | "Data keys" on the page. The intro is a list that defines a phase reader and "From the page" |
| 11 | The intro said that the offers are read from the code | PR refuter | acted | It says that the offer kinds, labels and phases are written in the tool and checked against the code |
| 12 | Two maps keyed by offer kind repeat each other | PR lens | acted | One `Offer` per kind: phase, label and step |
| 13 | `main` reads the code before it parses its arguments | PR lens | acted | It parses first, as map.py does |
| 14 | A help text with a double space fails T5 though the tool is right | PR refuter | acted | T5 joins the expected sentence's words as the tool does |
| 15 | "Effects: none" reads wrong for an op that only reads, and Network shows twice | PR refuter | acted | "none, it only reads". Network stays in the JSON and in the effect words |
| 16 | Nothing checks that `HAND_WRITTEN` changes when a moment changes | PR refuter | dropped | The code holds no second source for the date. The PR diff shows a changed moment to the review |
| 17 | developing.md's new sentence makes line 5 long | PR lens | dropped | The page is at its budget of 379 lines, so the sentence stays on line 5 |
