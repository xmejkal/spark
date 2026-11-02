# P513 (#709): a requirements signal with a part's signal name and a pin sets that pin: rows

The plan's own checks, the plan council's findings (refuter and lens, round 1) and what the PR did with each, on
2026-11-02 in the PO's full auto mode. `acted` means the PR took it, `verified` that it holds and needs nothing here,
`raised` that a card or the PO takes it.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The card's "the assigner honours a named label" holds only in part: a strap pin by name is refused (close audit C4), and the GDI cable's DC is D2, GPIO3 | plan check | acted | The PO kept C4 (2026-11-02). The card's Done-when now pins 4 signals. P527 (#726) holds the connector case. A test pins the D2 refusal |
| 2 | The card's `design.py:376-382` is the compare at 377-383 | plan check | verified | off by one line, no change |
| 3 | A pin the board lacks was refused by name already (`assign_pins.py:249-251`) | plan check | verified | `test_a_pin_the_board_lacks_is_refused_by_name` pins the text |
| 4 | Do not pin a bus line: `line="SCLK"` is not in SHARED_LINES, so a pinned SCLK and a second SPI part are refused | refuter | acted | the Done-when pins TFT_BL, TFT_CS, TFT_RST and SD_CS only. The docs say "a bus line needs no pin". The plan's "line is None once a pin is set" was wrong and is dropped |
| 5 | `sources` must keep the file's indices, or a second pin is reported as `signals[0]` | refuter | acted | `pin_part_signals` returns (index, entry) pairs. A test and a mutation row cover it |
| 6 | Unpinned, TFT_DC lands on A5 (GPIO11), not the cable's GPIO3. No doc may say the GDI display works through spark | refuter | acted | `test_the_four_gdi_pins_place_and_the_pin_map_names_them` asserts TFT_DC = 11. No doc claims the GDI display works |
| 7 | The C4 refusal must say what to do, without contradicting the board file ("usable as ordinary I/O once running") | lens | acted | `NAMED_STRAP_REFUSAL` keeps "the chip reads it at reset" as the reason and adds "drop `pin` … or see P527 (#726)". A test pins the text |
| 8 | A pinning entry with another key would be dropped without a word, which leaves a gap for Claude to fill | lens | acted | refused by name. `test_a_pinning_entry_with_another_key_is_refused_by_name` |
| 9 | Test 1b uses a different spelling of the name (Screen vs SCREEN_TFT_BL) | lens | acted | `test_an_instances_signal_is_pinned_by_its_instance_name` |
| 10 | `parts.signals_for`'s `pin_on_host` has no reader (no record, schema or doc) | lens, prune | acted | removed (2 lines). The suite is green |
| 11 | `assign` in `assign_pins.py` rose from 118 to 119 lines, which breaks R1 | push hook | acted | the message moved to the module constant `NAMED_STRAP_REFUSAL` |
| 12 | `journey/build.md:238` is `commands/build.md:238` (the row about two components of one name) | build | acted | the row in `commands/build.md` now says an entry with a `pin` is that signal's pin |
