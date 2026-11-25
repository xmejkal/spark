# P1122: Claude's jobs as chat offers with a tell, shown under "Ask Claude": rows

Card: [P1122 #1652](https://github.com/xmejkal/spark/issues/1652), with [P1115 #1644](https://github.com/xmejkal/spark/issues/1644)
and [P1128 #1659](https://github.com/xmejkal/spark/issues/1659) riding. The plan (revision 3) had two council rounds,
each a lens (Sonnet) and the refuter (Opus). This file holds the acted, raised and rejected findings only. A "row" in the
last column is a row of a `tests/mutations/` table, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Two rows of `p1102-design-basis.json`, "from_page ignores SENDABLE" and "from_page ignores IN_CHAT", plant one mutant once `from_page` reads the row of `OFFER_KINDS` | build | acted | Merged into row 6, "from_page ignores the row's from_page", which T6's swap of build's row catches. The plan's new p1122 row of the same mutant is that row, so it is not written twice |
| 2 | D3's last row is untested for the firmware: a `CHAT_NOW` that maps a firmware with problems to `write-firmware` survives the tests | PR review, refuter (Opus), with the everyday lens | acted | `TheChatOfferTest.test_a_firmware_with_problems_or_that_could_not_run_names_none`, with a Phase value because `FirmwareReader` gives no such status. Row 14 plants the mutant |
| 3 | In `docs/guide/agents/flow.md`, "Such an offer's `<li>`" follows the new Copy sentence, so it points at the chat offer | PR review, everyday lens (Sonnet) | acted | "A sendable offer's `<li>`" |
| 4 | D2 keeps chat offers out of `Phase.offers`, against the architect's "a chat job is an Offer with `from_page` false". `show --json` gives the key but no label or tell | PR review, architecture lens (Opus) | raised | A misfit for the PO. His answer (2026-11-25): merge as it is, and decide at [P836 #1198](https://github.com/xmejkal/spark/issues/1198) how the other interfaces read chat offers |
| 5 | The rule behind `chat_offer` walks the same branches as `who_and_sentence` and `deploy_now` | PR review, architecture lens | raised | [P1133 #1668](https://github.com/xmejkal/spark/issues/1668). Not in this PR: the refuter showed the fix changes about 13 return lines and five rows' anchors. The literal D3 tests catch a drift until then |
| 6 | "Can the page send it" is written four ways | PR review, architecture lens | raised | [P1134 #1669](https://github.com/xmejkal/spark/issues/1669), beside P1082 #1587. All four were on main before this PR, and this PR made one simpler |
| 7 | "A tell means `from_page` false" is not tested | PR review, architecture lens | rejected | `TheOfferKindsTableTest` asserts it for every kind |
| 8 | `flow_codes.FLASH_NOT_FINISHED` repeats `board_log`'s value with no equality test | PR review, architecture lens | rejected | dropped because the behavior tests read a real board log and fail on a drift (the refuter planted it) |
| 9 | The glossary lacks *chat offer*, `tell`, `OFFER_KINDS` and `CHAT_NOW` | PR review, everyday lens | rejected | `docs/guide/patterns-and-names.md:40` holds all four |
| 10 | Small ones: `flow_page.py` imports the private `_text`, its docstring names `SvgInliner`; two clipboard paths in the script; Copy fails silently; a comment repeats `_ask`'s docstring; emptying `CHAT_KEYS` survives | PR review, both lenses and the refuter | rejected | dropped because each is a nit with no wrong behavior. The clipboard paths do different jobs, and the tell stays selectable when a copy fails |
