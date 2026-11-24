# P1110 and P1111: a crash or a Ctrl-C in the verify leaves its board log, and a gone image keeps the answer: rows

Cards: [P1110 #1634](https://github.com/xmejkal/spark/issues/1634) and [P1111 #1636](https://github.com/xmejkal/spark/issues/1636),
two stories in one PR. New logic: a plan and its plan check (the refuter on Opus, H1 to H9), then the build. This file
holds the acted, raised and rejected findings only (rules.md). 2026-11-24.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | D1: the verify runs only after every flash command exited 0, so its log's verdict is `ready unknown`, never `flash not finished` | plan check | acted | `VERIFY_NOT_FINISHED_LOG` takes `ready_probe.UNKNOWN`; T1, row 2 |
| 2 | D2: the causes `crash` and `interrupted` name no stage and have no read-back; exactly three expected strings change, and no assertion gets weaker | plan check | acted | `flow_codes.CAUSE_WORDS`; T5, rows 6 and 7 |
| 3 | D3: a verify that did not finish keeps no store record, so the look names the older deploy | plan check | raised | card [P1112 #1638](https://github.com/xmejkal/spark/issues/1638) |
| 4 | D4: the one handler is a context manager that re-raises the very object, a KeyboardInterrupt too, and keeps G20 | plan check | acted | `DeployService.logs_what_ends`; T1 to T3 `assertIs`; P1096's T11 unchanged but for the rename |
| 5 | H1: `p239-pr8.json` row 1 loses its anchor | plan check | acted | its find is `        return planned._replace(image_sha256=image_sha256)\n`; planted, caught |
| 6 | H2: `p239-pr7.json` row 15 loses its anchor | plan check | acted | `flasher commands mpremote notes image_sha256`, swapped as before; planted, caught |
| 7 | H3: the three changed strings, and the page helper keeps its ON THE BOARD assertion | plan check | acted | `test_flow.py` (the crash test's pair) and `test_deploy_json.py` (two calls): "spark crashed during the flash" → "spark crashed during the deploy", "a Ctrl-C interrupted the flash" → "a Ctrl-C interrupted the deploy". `assert_show_and_the_next_page_say` takes the ON THE BOARD line as a parameter |
| 8 | H4: `CAUSE_WORDS` are at `flow_codes.py:108-109`, and P1096's rows file has 17 rows | plan check | acted | read against the real lines; P1096 row 10, now under the `if`, keeps its anchor and its `pass` compiles; `--anchors` proves every row |
| 9 | H5: P1092 row 18's find is the whole FLASH entry, as `NOT_FINISHED_UNLOGGED_LINE),` is inside `VERIFY_NOT_FINISHED_UNLOGGED_LINE),` | plan check | acted | rows 17 and 18 find the dict's FLASH entry; planted, caught |
| 10 | H6: keep `raw=True` on the verify's log line | plan check | acted | `say_not_finished` says either stage's logged line with `raw=True` |
| 11 | H7: the comment that lists why a look gives no token names the gone image | plan check | acted | `board_codes.py`, above `STOP_FOUND, NO_MAC` |
| 12 | H8: a Ctrl-C between the end of the flash loop and the verify's `with` still writes no log | plan check | raised | accepted, dropped because the window holds only `keep_yes` and the verify's BEGIN and why lines, with no wait and no board I/O |
| 13 | H9: the builder runs `tools/map.py --write`, and finds out whether a test compares the `--help` text | plan check | acted | map.md's test columns follow the tests' imports; `test_deploy.TheHelpTest` pins only the paragraphs' order, and no golden holds the `--help` |
| 14 | T6 was green when written: steps 1 and 2 hold both of its fixes | the builder | acted | planting row 8 makes T6 and T8 fail, so both pin P1111's fix |
