# P461: the image fits the flash of the board it goes on

Findings of P461 (#629), 2026-10-31, Prague, built on main 4226627a. The review rows follow after the review.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The fake build must be at least 0x8C00 bytes to hold a table | plan council round 1 | verified, acted | `tests/micropython_fakes.py` `fake_interpreter` (default 0x9000) replaces every `b"\xe9" + b"\x00" * N` fake that reaches `image()` |
| 2 | `read` refuses an offset past 0x8000 and a build too short for its table | plan council round 1 | verified, acted | `PartitionTable.read`; tests at offset 0x8001 and at sizes 0x8C00 and 0x8BFF |
| 3 | Table format literals come from ESP-IDF v5.5.2, "vfs" and its size from MicroPython | plan council round 1 | verified, acted | cited by file and line in `tests/test_flash_image.py` and `tests/micropython_fakes.py` |
| 4 | The real S3, ESP32 and C6 v1.29.0 interpreters take the new table | plan council round 2 | verified | builder's scratch check: 4 entries, MD5 matches, littlefs mounts with 512 blocks and refuses 3,584, the bytes outside the table are unchanged |
| 5 | Plan step 4: `test_look.py:61`, `test_deploy_service.py:127`, `test_deploy_gate.py:1109`, `test_run_scenario.py:802,834` build a short fake | plan | rejected | they patch `interpreter_for` and use `self.micropython` from `test_deploy.py:67` or `test_run_scenario.py:383`, so one change there covers them; `test_deploy_json.py:328` needs no fake |
| 6 | Plan step 6: `docs/guide/agents.md:650` holds a stale copy of the look's sentence | plan | rejected | it describes the check ("the image holds `firmware/` as it is now"), which stays true; the stub in `tests/test_board_look.py:821-823` was the second copy and changed |
| 7 | Tests that built the image at offset 0x1000 from a fake with the table at 0x8000 of the interpreter | builder | acted | the table sits at 0x8000 of the flash, so such a fake is `fake_interpreter(offset=0x1000)`; `test_flash_image.py`, `test_image_evidence.py` and `test_run_scenario.py` pass the offset |
| 8 | Tests that compared the image to the whole interpreter | builder | acted | the table's 0xC00 bytes differ now, so they compare the bytes before it (and in one test after it) |
| 9 | Wokwi with the new table | plan | closed, unchecked | the PO ruled out paid Wokwi runs on 2026-10-31; the PR says so |
| 10 | Mutation table `tests/mutations/p461-vfs-partition.json`, 14 rows | plan step 8 | raised | runs once after the review fixes |
