# P483 FireBeetle definition: rows

What the P483 build, the plan council and the refuter found. Card: #662.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The FireBeetle record cites no `wokwi-board`, so the limits say "names no Wokwi definition" | planner fact 3 | verified | now one `documents["wokwi-board"]` entry: wokwi-boards commit 962b19d5, sha256 8a0630d3...eb50d, 3376 bytes, retrieved 2026-11-01 |
| 2 | The S3 devkit file has pins "21" and "47" that target GPIO21 and GPIO47 | planner fact 5 | verified | the test definition mirrors them; the real file is kept in the store by `parts.py --keep FILE --url URL` |
| 3 | The devkit file has no `serialInterface`, so P468 (#636) gets pins but no serial facts from it | planner fact 8 | raised | comment on #636 |
| 4 | Refuter 1: with the file kept, `onboard_limits` would return `[]` and hide that pins 21 and 47 are header pins on the devkit | refuter | acted | `SimulatedPart.is_stand_in` from `wokwi_is_stand_in` (True only), `STAND_IN` sentence in `why_not_simulated`; boards.py stays at 969 lines |
| 5 | Refuter 2: `keep_local` takes `path.name` and needs `--url`, so the downloaded file must carry the entry's name | refuter | acted | store step names the file `wokwi-esp32-s3-devkitc-1.board.json` and passes `--url` |
| 6 | Round 2: name the field `is_stand_in`, test that a non-stand-in keeps its old texts, note that the sentence holds only while no part is wired to that GPIO | plan council | acted | field name, test `test_a_part_that_is_no_stand_in_keeps_its_old_texts`, docstring note |
| 7 | The stand-in sentence is wrong once P484 (#663) wires a real part to GPIO21 or GPIO47 | plan | raised | P484 rewords it |
| 8 | `tools/mutate.py --anchors` refuses 120 rows on main, not 119 | build | verified | 120 without the P483 table, 120 with it: the table adds none |
| 9 | No command fetches a board document; the store step is a curl then `--keep` | planner fact 7 | raised | a `--keep-source URL` command is a later row |
