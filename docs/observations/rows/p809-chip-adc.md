# P809: a board whose chip shares ADC2 with Wi-Fi names the ADC2 role, from a cited chip fact: rows

Card: [P809 #1145](https://github.com/xmejkal/spark/issues/1145), the PO's pick on 2026-11-14 ("a small chip table").
Size S: plan council (lens Sonnet, refuter Opus) in two rounds, then one lens and the refuter on the PR. This file holds
the acted, raised and rejected findings only (rules.md), with the build's own rows. 2026-11-14.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a record of a chip with ADC2 that names no ADC2 role is read as if every ADC pin reads with Wi-Fi on | card | acted | `board_rules.adc2_role_problems` in `RULES`, reading `chip_table` over `data/chips.json`; the plan is the session's own file, not in the repository |
| 2 | two ADC units alone would ask a board of the ESP32-P4, which has no Wi-Fi, for the role | build (plan) | acted | the P4's fact is false, cited to its soc_caps.h `SOC_ADC_PERIPH_NUM (2)` and the absent `SOC_WIFI_SUPPORTED` |
| 3 | soc_caps.h never says ADC2 conflicts with Wi-Fi, so a table built from it holds an inference | plan council round 1 (refuter) | acted | the true facts cite ESP-IDF v5.5.1 `adc_oneshot.rst` line 168, "ADC2 is also used by Wi-Fi", for esp32, esp32s2, esp32s3; kept in the store (sha256 66db4d85…) |
| 4 | the C3's line 169 says its ADC2 is not supported at all, which is a different fact from the role's | plan council round 1 (refuter) | raised | the C3's fact is null; card [P813 #1164](https://github.com/xmejkal/spark/issues/1164) |
| 5 | rules run when required keys are missing, so `board["chip"]` crashes on a board without one | plan council round 1 (refuter) | acted | the rule reads `board.get("chip")` and a dict `pin_roles` only; tested with no chip, a list chip and a number `pin_roles` |
| 6 | the test fixture's esp32 chip makes every pin-role test see one problem more, and a role in the fixture is replaced whole | plan council round 1 (refuter) | acted | `definition()` in test_boards.py takes chip esp32c6, a chip whose fact is false, with the reason in its docstring |
| 7 | a chip the table lacks gives the same "ok" as a checked one | plan council round 1 (lens) | acted | `--validate` prints `ADC2 role not checked: …` (`outcomes.NOT_CHECKED_MESSAGE`) under a board without the role; the exit code does not change; load stays quiet |
| 8 | the problem sentence must tell a writer how to fix the record | plan council round 1 (lens) | acted | it names the role, the ADC2 pins or `[]`, the note, and points at boards/README.md "ADC pins" |
| 9 | one word for one thing: the table fact and the method are named in the source's words | plan council round 1 (lens) | acted | `adc2_used_by_wifi` |
| 10 | a class is not needed for one question | plan council round 1 (lens) | rejected | the repo's rule is a small Value class; `ChipTable` is immutable and its `load()` is cached, so a board load reads the file once |
| 11 | drop the four one-unit chips no board uses | plan council round 1 (lens) | rejected | a chip the table lacks now prints a not-checked line, so each ESP-IDF v5.5.1 chip has its cited fact |
| 12 | `test_assign_pins.py:46` fails with an esp32 board | plan seed | rejected | its board is never validated (refuter) |
| 13 | a role with the wrong ADC2 pins is not caught | plan | raised | dropped because it needs each chip's ADC2 pin list, no board hit it, and records grow by need; README says the check does not read the pins |
| 14 | a role on a chip with no ADC2 is not caught | plan council round 1 (refuter) | raised | dropped because it is harmless: the board offers fewer ADC pins |
| 15 | `chip_table.FILE` read by a test fails test_self_confirmation, and the map is generated | plan council round 2 (refuter) | acted | `"chip_table.FILE": STRUCTURE` in test_self_confirmation.py; `tools/map.py --write`; `chip_table` joins test_architecture's records modules |
| 16 | the role's note at board_rules.py says more than line 168 does | plan council round 2 (refuter) | rejected | the note rests on the S3 datasheet v2.2, section 4.2.2.1 note (page 59), "cannot be used with Wi-Fi simultaneously", which firebeetle2 cites |
| 17 | the role name was a literal in the new rule | build | acted | `ADC2_UNUSABLE_WITH_WIFI` moves to board_rules, and board_records imports it, so `board_records.ADC2_UNUSABLE_WITH_WIFI` still works |
| 18 | the PR's rows | build | acted | `tests/mutations/p809-chip-adc.json`, 8 rows after the PR review's fixes, each planted by hand and red against its named test (8 of 8); `--anchors`: every anchor present once |
| 19 | a chip the table lacks is "looked, not there", which the reader rule calls NONE_RECORDED, not NOT_CHECKED | PR review (lens) | acted | `ChipTable.adc2_used_by_wifi` returns NONE_RECORDED; its docstring says why it has no READERS row (it reads no file that may be absent) |
| 20 | `_validate_all` decided what is not checked and looked the chip up a second time | PR review (lens, refuter) | acted | `board_rules.adc2_role_unchecked(board)` gives the why; `boards.py` only prints it |
| 21 | `--validate` said "not checked" for a C3 board that already names the role | PR review (refuter) | acted | no line when the record names the role; tested |
| 22 | the no-crash test proved only a list came back; no end-to-end failure, no load refusal, no S2 | PR review (lens) | acted | the test asserts no ADC2 problem and covers a dict chip and `pin_roles` null; new tests for `--validate` exit 1, `board_records.load` refusing, and the S2 and S3 |
| 23 | a flip of the S2 or S3 to false would pass every test | PR review (lens) | acted | test_chip_table pins the shipped `{chip: value}` map and that `load()` reads it |
| 24 | new lines over the repo's width, and blank lines between classes | PR review (lens) | acted | the Python lines are wrapped; the JSON lines stay long, as in the other data files |
| 25 | the problem sentence said the README names each chip's source, but it names only the ESP32's and the S3's | PR review (refuter) | acted | the sentence points at "boards/README.md, ADC pins" only |
| 26 | the records area page in docs/discovery does not list `chip_table` | PR review (refuter) | rejected | that page was stale before this PR (no `fact_needs` either); it is a discovery record, not a guide |
| 27 | four kept soc_caps.h files (esp32, s2, s3, c3) are cited by no row | PR review (lens) | rejected | they back the plan's checked facts, and P813 can cite the C3's |
