# P1112: a verify that did not finish keeps a store entry: rows

Card: [P1112 #1638](https://github.com/xmejkal/spark/issues/1638), from P1110's D3. A small story: the plan council
(a lens on Sonnet, the refuter on Opus) found the rows below. This file holds the acted, raised and rejected findings
only (rules.md). 2026-11-25.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the plan cites 8f420154, and P478 moved lines (`self.stages` is `self.tracker`) | plan refuter | acted | built on f029d6a0; every find text holds |
| 2 | the store write of a verify that did not finish must not read the image, or a file deleted during the verify keeps the older deploy as the last one (R5) | plan lens, plan refuter | acted | `record_not_finished` builds a verify's facts with `board_facts.facts_without_image`; `test_a_verify_that_did_not_finish_keeps_its_entry_when_the_image_is_gone_by_then`; the flash keeps its read, which P1097 and P1111's tests pin |
| 3 | the words "written by the flasher, start not confirmed" and the card's "start not seen" | plan refuter | acted | delegated (the auto-mode council): the PO's to reverse; `flow.py show` already says "start not seen" for `ready unknown` by its cause |
| 4 | the store's words and `flow_codes.UNSURE_WORDS` can drift | plan lens | acted | `board_log.STORE_VERDICT_WORDS` is pinned equal by `test_the_store_s_words_of_ready_unknown_are_the_page_s`; mutation row 6 |
| 5 | a crash at the REPL command, after the verify's own board log, leaves no store entry | plan refuter | raised | card [P1125 #1655](https://github.com/xmejkal/spark/issues/1655); named in commands/deploy.md |
| 6 | the look says a verdict without its cause, `flow.py show` with it: two wordings | plan architect | raised | card [P1126 #1656](https://github.com/xmejkal/spark/issues/1656) |
| 7 | T1's Ctrl-C subtest leaves `self.unread` set for the next yes | plan refuter | acted | `self.unread = None` before each older deploy and after each stop |
| 8 | the plan's rows 3 to 5 name `VERDICT_WORDS` | plan architect | acted | the constant is `STORE_VERDICT_WORDS`, with a comment that gives the rule |
| 9 | `p779-board-record.json` row 7's find went with the split of `board_facts.facts` | the builder | acted | re-anchored on the call `micropython_banner=image_builder.banner_in(data)` |
| 10 | the verify entry's `simulation` and board id are not pinned: two mutants survive | PR refuter | acted | `test_a_verify_entry_keeps_the_stance_the_board_the_image_and_no_files` (passed and none evidence); mutation rows 8, 9, 10 and 11, planted and caught |
| 11 | `record_not_finished`'s else takes any verdict as a verify | PR lens | acted | `elif verdict == ready_probe.UNKNOWN`, else ValueError; `test_a_verdict_that_no_stage_gives_is_refused`; row 12 |
| 12 | T1's `deployed` assert only says "not the older date" | PR refuter | acted | compares with the newest board log's moment |
| 13 | the doc names only the REPL command as the window with no entry | PR refuter | acted | deploy.md names `own_usb_of`, `_keeps_boot_entry` and the lines before the store write; the same window is card P1125 |
| 14 | the image-gone test relied on an exception's `__bool__` | PR lens | acted | the fake board's `on_board` deletes the image and raises |
