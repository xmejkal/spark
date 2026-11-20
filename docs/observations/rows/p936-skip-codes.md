# P936 PR 3: the build's two skips have codes, and each stage entry with a code carries it in --json: rows

Card: [P936 #1332](https://github.com/xmejkal/spark/issues/1332). The PO's decisions, 2026-11-20: "Yes, give them
codes" (before 17:26 Prague) and "Every stage with a code" (before 20:09 Prague). A plan, then its check (a lens on
Sonnet and the refuter on Opus), then a build to the checked plan. This file holds the acted, raised and rejected
findings only. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | no build stage's code reaches any JSON, so a code on a skip alone helps no agent; which entries carry it is the PO's | plan | acted | the PO: "Every stage with a code"; `said_of` writes `code` after `detail` on each stage that has one, an ok entry is as it was (`check-spine-ok.json` unchanged) |
| 2 | build_codes' docstring says only the sheet's `not written` entry writes its code into --json | plan check | acted | it names `stages[].code` (P936) beside `kept` |
| 3 | test_check_spine's method docstring still says `ended` raises for an ending "neither skipped nor coded" | plan check | acted | "an ending with no code (P936)" |
| 4 | the `board_only` fix must not assume that firmware/pins.py exists | plan check, refuter | acted | "firmware/pins.py, written with --keep, holds the pin map"; the meaning says "name no part", so it stays apart from `board_only_with_parts` |
| 5 | the CODES entries of the two Codes are a second literal of their meaning | plan check | acted | `BOARD_ONLY: BOARD_ONLY.meaning`, `EVERY_PART_SKIPPED: EVERY_PART_SKIPPED.meaning` |
| 6 | a reader of the build's stages breaks on the new key | plan check, refuter | rejected | the refuter read them: `.spark/build.json` stays `{name, status}`, flow reads name and status, the JSON contract pins top-level keys, check_all, deploy and snapshot read no stage code |
| 7 | data/chips.json says twice that the ESP32-C3's adc_channel.h is not yet kept | plan | acted | both sentences cut; the store holds the file with sha256 c79100bb…6258, and its line 25 is the cited `#define ADC2_CHANNEL_0_GPIO_NUM 5` |
| 8 | the plan says `skipped board_only: …` is said once in --help | build | acted | four stages end with it, so the test pins four, and `every_part_skipped` once |
| 9 | the plan's mutation row 6 (the help says every code as a design error) is P852's row "the help says a skip as a design error", whose line this PR replaced | build | acted | P852's row anchored again on the new line, so no two rows plant one defect; P852's guard row anchored on `if ending.code is None:`. `--anchors` refuses the same 20 rows as main |
| 10 | `tools/mutate.py --retarget` moves the rows of a moved file, not a changed line | build | acted | the two P852 rows edited by hand, then `--anchors` |
| 11 | the PR's review: merge, no finding | review, lens | acted | merged after the refuter's one fix |
| 12 | tests/test_chip_table.py:4 still says the C3's adc_channel.h "is not yet kept" | review, refuter | acted | the docstring says the kept adc_channel.h |
| 13 | --help may cut the board_only fix sentence | review, lens | rejected | the refuter: --help prints only the meaning, never a fix; both meanings print in full |
| 14 | a reader breaks on the new `code` key | review, refuter | rejected | a real board-only build and a full build both exit 0; `.spark/build.json` stays `{name, status}`; flow.py runs with and without --json; the snapshot records the unchanged text |
