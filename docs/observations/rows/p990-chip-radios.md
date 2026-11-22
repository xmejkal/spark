# P990: a board offers its chip's radios for a radio need: rows

Card: [P990 #1443](https://github.com/xmejkal/spark/issues/1443). Seen in the p934-display2 walk: the need
communicate / wifi found no board. Two plan rounds: round 1 was a lens (Sonnet) and the refuter (Opus), and round 2 was
the refuter (Opus). Both rounds were delegated in auto mode, and the PO can change them. This file holds the acted,
raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the radios are the chip's, so a `radios` block in each board record repeats them and needs a write to the PO's record | plan lens and plan refuter | acted | the facts are in `data/chips.json`, read by `chip_table.radios`. Every board of the chip offers them, the PO's shelf FireBeetle 2 C6 too, with no store write |
| 2 | `ChipFact` and `_flag` hold only true or false, so a radio reader must not reuse `_flag` | plan refuter | acted | `ChipTable.radios(chip)` gives the names in `RADIOS` order whose value is `true`. A null, a false, "yes" or 1 gives nothing. Mutation rows 1 and 3 |
| 3 | `onboard_functions` reads `board["chip"]` and takes the words from a table beside `POWER_FUNCTIONS` | plan refuter | acted | `board_rules.RADIO_FUNCTIONS`, and `test_boards.TheBoardsChipRadiosTest.test_each_radio_of_the_chip_table_has_words` holds its names equal to `chip_table.RADIOS` |
| 4 | "Wi-Fi" splits into `wi` and `fi`, so the need `wifi` meets only "(WiFi)" | plan lens | acted | the words keep "(WiFi)". Mutation row 6 removes it, and the wifi need then finds no board |
| 5 | each radio fact cites a kept document with url, sha256, file and retrieved | plan refuter | acted | the C6 cites its held entry. New entries for the ESP32 and the S3 name the files kept on 2026-11-14. A fresh download of each URL on 2026-11-22 gave the same sha256. No vendor file is committed |
| 6 | the write path of version 1 (`--fact-set radios`, `radio_problems`, the PO's wait) is not needed | plan refuter | acted | the plan dropped it. No board record and no store file changes |
| 7 | a test that pins the facts of every chip fails on a stray radio fact | round 2 refuter 1 | acted | `test_the_c3_facts_are_the_sources` collects every fact other than `adc2_used_by_wifi` and `RADIOS`. `test_each_radio_fact_is_true_and_cites_its_chips_soc_caps_line` checks each radio fact of every chip |
| 8 | a candidate's `what` lists every function with the need's verb, so a C6 board shows all three radios | round 2 refuter 2 | acted | `test_needs.TheBoardsChipRadiosAreOfferedTest` expects the three names for the C6 boards and two for the S3. The text test quotes the line the run printed |
| 9 | on the walk, the wifi need also offers `lilygo-t-display` and `firebeetle2-esp32s3`, and `xiao-esp32-c6` is held by reaction-game. `--json` gives one need on its first page | round 2 refuter 3 | acted | the value proof read every page with `--from`. The walk offers `firebeetle2-esp32c6` (shelf, free 1), `lilygo-t-display`, `firebeetle2-esp32s3` and `xiao-esp32-c6` (free 0). Nothing in the store or the walk was written |
| 10 | does the hook map `data/chips.json` to a test? | round 2 refuter | acted | yes: `story_tests` finds the word "chips" in `test_chip_table`, `test_boards`, `test_matching`, `test_parts`, `test_assign_pins` and four more. The map now gives `board_rules.py` the test `test_boards` |
| 11 | a need of `wireless` finds no radio | builder | raised | dropped because the conversation writes a need in the words of `commands/idea.md`, and those words name the radio. `radio` alone meets every radio |
| 12 | for a zigbee need the S3 stays a candidate, with `what_matches: false` | builder | rejected | every board with the need's verb is a candidate. The score 0.0 and "[other words]" say it does not match. The test pins it |
| 13 | the ESP32's Bluetooth Classic (`SOC_BT_CLASSIC_SUPPORTED`, line 458) has no name, so an audio need can pick a board with LE only | builder | raised | dropped because no need asks for Bluetooth Classic today. The offer word says "LE" |
| 14 | a test read `chip_table.RADIOS` and `board_rules.RADIO_FUNCTIONS` with no reason, so it confirmed the code with its own names | the hook (`test_self_confirmation`) | acted | `test_chip_table` holds the radio names as its own literal. The check that each radio has words reads both tables, with a reason in `MAY_READ` |
