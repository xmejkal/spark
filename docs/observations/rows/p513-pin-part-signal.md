# P513 (#709): a requirements signal with a part's signal name and a pin sets that pin: rows

The plan's own checks, the plan council's findings (refuter and lens, round 1) and what the PR did with each, on
2026-11-02 in the PO's full auto mode. `acted` means the PR took it, `verified` that it holds and needs nothing here,
`raised` that a card or the PO takes it.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The card's "the assigner honours a named label" holds only in part: a strap pin by name is refused (close audit C4), and the GDI cable's DC is D2, GPIO3 | plan check | acted | The PO kept C4 (2026-11-02). The card's Done-when now pins 4 signals. P527 (#726) holds the connector case. A test pins the D2 refusal |
| 2 | The card's `design.py:376-382` is the compare at 377-383 | plan check | verified | off by one line, no change |
| 3 | A pin the board lacks was refused by name already (`assign_pins.py:249-251`) | plan check | verified | `test_a_pin_the_board_lacks_is_refused_by_name` pins the text |
| 4 | Do not pin a bus line: `line="SCLK"` is not in SHARED_LINES, so a pinned SCLK and a second SPI part are refused | refuter | acted | the Done-when pins TFT_BL, TFT_CS, TFT_RST and SD_CS only. The plan's "line is None once a pin is set" was wrong and is dropped. Row 13 corrects "refused": MOSI pinned to D13 was accepted, and the bus split |
| 5 | `sources` must keep the file's indices, or a second pin is reported as `signals[0]` | refuter | acted | `pin_part_signals` returns (index, entry) pairs. A test and a mutation row cover it |
| 6 | Unpinned, TFT_DC lands on A5 (GPIO11), not the cable's GPIO3. No doc may say the GDI display works through spark | refuter | acted | `test_the_four_gdi_pins_place_and_the_pin_map_names_them` asserts TFT_DC = 11. No doc claims the GDI display works |
| 7 | The C4 refusal must say what to do, without contradicting the board file ("usable as ordinary I/O once running") | lens | acted | `NAMED_STRAP_REFUSAL` keeps "the chip reads it at reset" as the reason and adds "drop `pin` … or see P527 (#726)". A test pins the text |
| 8 | A pinning entry with another key would be dropped without a word, which leaves a gap for Claude to fill | lens | acted | refused by name. `test_a_pinning_entry_with_another_key_is_refused_by_name` |
| 9 | Test 1b uses a different spelling of the name (Screen vs SCREEN_TFT_BL) | lens | acted | `test_an_instances_signal_is_pinned_by_its_instance_name` |
| 10 | `parts.signals_for`'s `pin_on_host` has no reader (no record, schema or doc) | lens, prune | acted | removed (2 lines). The suite is green |
| 11 | `assign` in `assign_pins.py` rose from 118 to 119 lines, which breaks R1 | push hook | acted | the message moved to the module constant `NAMED_STRAP_REFUSAL` |
| 12 | `journey/build.md:238` is `commands/build.md:238` (the row about two components of one name) | build | acted | the row in `commands/build.md` now says an entry with a `pin` is that signal's pin |
| 13 | `{"name": "MOSI", "pin": "D13"}` was accepted: MOSI on GPIO21, and a second SPI instance then took GPIO15 with exit 0, a split bus. Before the PR it was refused as "both MOSI" | PR review: refuter 3, reviewer 1 | acted | `pin_part_signals` refuses a pin on a bus line by name. `test_a_pin_on_a_bus_line_is_refused_by_name` runs with one and with two SPI parts. A mutation row covers it. The build page says a pin on a bus line is refused |
| 14 | The extra-key test covered only `needs`, so the mutant that also lets `bus` and `from` through survived | PR review: refuter 4 | acted | `test_a_pinning_entry_that_gives_a_bus_is_refused_too`, plus a mutation row |
| 15 | `{"name": "tft_bl", "pin": "D13"}` added a stray signal on GPIO21 and left TFT_BL unpinned | PR review: refuter 5 | acted | refused, naming `TFT_BL, dfr0664-tft-2in's TFT_BL`. A test and a mutation row cover it |
| 16 | The docs example reads as a GDI recipe, but DC cannot take the cable's D2 | PR review: reviewer 2 | acted | one clause on `commands/build.md`, `docs/guide/journey/build.md` and `skills/spark-design/SKILL.md`: no full GDI recipe until P527 (#726) |
| 17 | The slow build test did not say where TFT_DC lands | PR review: reviewer 3 | acted | `test_the_display_builds_with_its_four_gdi_pins_pinned` asserts `TFT_DC = 11` through `pin_module_for` |
| 18 | The bus refusal said a line "lands on the board's own I2S pins", but the FireBeetle 2 labels no I2S pins: its I2S goes through the GPIO matrix. `commands/build.md:47` said the same. | fix-commit refuter 6 | acted | the lead reworded both to the reason true for every bus: "an SPI bus line: the assigner places the bus, so drop `pin`". Tests and docs test pass, anchors refuse 119 |
| 19 | An unpinned `{"name":"tft_bl"}` still adds a stray signal and does not pin TFT_BL. | fix-commit refuter 7 | closed | the same before this PR: an entry with no `pin` is a hand-written signal. Row only — P776: stale note: Row only, same as before the PR. |
| 20 | No test covers `from` in the extra-key check, so a mutant that lets only `from` through survives. The capitals refusal is not in `commands/build.md`'s table row. | fix-commit refuter 7 | closed | row only: small, for the next card that touches `pin_part_signals` — P776: card #1081 (pin_part_signals test gap) |
