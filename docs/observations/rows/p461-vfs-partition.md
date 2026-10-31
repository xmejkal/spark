# P461: the image fits the flash of the board it goes on

Findings of P461 (#629), 2026-10-31, Prague, built on main 4226627a. Rows 1-10 are the build, rows 11-22 the review (Sonnet reviewer and Opus refuter) and its fix round, rows 23-27 the fix-commit refuter (Opus) and the mutation runs.

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
| 10 | Mutation table `tests/mutations/p461-vfs-partition.json`, 14 rows | plan step 8 | raised | grew to 20 rows in the fix round; runs once after it, by a separate agent |
| 11 | The offset guard's test cannot see its mutant: at 0x8001 the "too short" refusal fires first | review | acted | test at offsets 0x8001 and 0x10000 on a 0x20000-byte fake, asserting "starts past the partition table"; rows `if False:` and `< -1` |
| 12 | The ffat row survives: an ffat past 0x200000 is refused by the other check | review | acted | test with an ffat ending at 0x1f1000 asserting its own wording; the ffat row and a new `entry != self.FILESYSTEM` -> `False` row (caught by the different-vfs test) |
| 13 | A shift after the table goes unseen (`interpreter[self.SIZE:]` planted, all green) | refuter | acted | the fake pads with `position % 251`; one test compares every byte before and after the table at offsets 0 and 0x1000; rows for the shifted slice and for `start = TABLE_OFFSET` |
| 14 | `placed_in` overflows the table silently (95-96 source entries; 94 leave no end marker) | review | acted | `with_filesystem` refuses when entries + MD5 entry would fill 0xC00; test at 93 and 94 entries before the vfs; row `>=` -> `>` |
| 15 | A non-UTF-8 label raises the bare codec message | review | acted | `read` catches `UnicodeDecodeError` and raises a sentence with an action; test |
| 16 | The look's sentence names too few causes | review | acted | now "(firmware/, the board's MicroPython or how spark builds images changed since)"; tests updated, the board_look stub names no cause |
| 17 | No test holds real table bytes | review | acted | `S3_TABLE`, the 128 bytes from ESP32_GENERIC_S3-20260824-v1.29.0.bin (sha256 in the comment); parsed, and kept byte for byte in the image |
| 18 | The 0xff padding after the MD5 is not pinned by a row | review | acted | the existing MD5-entry test catches `b"\x00"`; row added |
| 19 | `SIZE` and `ENTRY` are vague; three blank lines in `test_flash_image.py` | review | acted | renamed `TABLE_SIZE` and `ENTRY_FORMAT`; blank lines removed; row anchors fixed |
| 20 | `read` stops at the MD5 entry, the bootloader reads on: an entry after the MD5 is dropped without a word | refuter | raised (LATER) | no build has one today |
| 21 | Flags are written as 0 and read flags are kept only in the tuple; `<= 0`, and a last slot never read, escaped the refuter's planted set | refuter | raised (LATER) | no build has these today |
| 22 | Wokwi with the new table stays unchecked | plan | closed | as row 9 |
| 23 | The non-text label test passes for the wrong reason: the flipped byte also breaks the MD5, whose sentence also names micropython.org/download | fix-commit refuter | verified, acted | the test builds its table with no MD5 entry and asserts "is not text"; new mutation row `.decode(errors="replace")`, caught |
| 24 | The PR body named two causes in the look's sentence, three interpreters, and the hook count of the old head | fix-commit refuter | acted | PR body corrected: three causes, four interpreters in the store, the hook on db55b827 |
| 25 | `micropython_fakes.py` claimed a pattern that never repeats within a table, but `% 251` repeats every 251 bytes | fix-commit refuter | acted | the docstring says a copy shifted by anything but a multiple of 251 shows; the refuter measured the real shifts at 138 and 58 mod 251 |
| 26 | The test comments counted three v1.29.0 builds, the store holds four with the same table | fix-commit refuter | acted | `tests/test_flash_image.py:36,47`, `tests/micropython_fakes.py:12` |
| 27 | Mutation runs: 20 planted, 20 caught (1,227 s) on db55b827; the decode row after it, 1 planted, 1 caught (481 s) | mutation-tester, lead | verified | `python3 tools/mutate.py tests/mutations/p461-vfs-partition.json --copy`; the decode row alone from a one-row copy of the table |
