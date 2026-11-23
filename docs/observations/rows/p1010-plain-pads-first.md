# P1010: plain pads before the I2C and SPI pads, and the pin map says why a signal takes a bus pad: rows

Card: [P1010 #1469](https://github.com/xmejkal/spark/issues/1469), from the walk P934 (2026-11-22). The PO's decision
of 2026-11-22: "Plain pads before bus pads". It reverses his P780 order of 2026-11-13
([P780 #1078](https://github.com/xmejkal/spark/issues/1078)). The plan council: round 1 a lens (Sonnet) and the refuter
(Opus) on main 98d96bdd, round 2 the refuter (Opus) with a prototype. The build adds its own rows. This file holds the
acted, raised and rejected findings only, and the closed ones that a later reader needs. A "row" in the last column is a
row of `tests/mutations/p1010-plain-pads-first.json`, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `pin_assigner.py` has 587 of its 600 lines, and `assign` is pinned at 116 lines (R1) | round 1 lens, refuter | acted | the order is in the new `scripts/spark/design/pad_order.py` (the Strategy `PadOrder`). `pin_assigner.py` has 584 lines and `assign` 115. The long comment on the bus penalty is two lines that point at `pad_order` |
| 2 | "kept" must come from `pin["can"] - needs`, or a signal that needs adc treats every ADC1 pad as kept | round 1 refuter | acted | `PadOrder.reasons`. Row 5 plants the other reading, and `test_the_pad_order_puts_plain_then_spi_then_i2c_then_the_kept_pads_by_cost` goes red |
| 3 | the order applies to every signal: a signal that needs adc or wake also prefers a pad with no bus role, and the why of such a signal on a bus pad names the bus | round 1 refuter | acted | `PadOrder.rank` takes the needs. `test_a_signal_that_needs_adc_takes_a_pad_with_no_bus_role_before_an_i2c_pad` (the S3). `_why({"adc"}, SDA)` names I2C in the helper test |
| 4 | the why keeps the spare abilities of the pad | round 1 refuter | acted | the bus-pad sentence ends "though it could still pwm" (the C6's MISO) |
| 5 | a direct test of `PadOrder.rank` and of the why, and a test that a kept bus pad sorts after a plain kept pad | round 1 lens | acted | `TheHelpersEachHaveANameTest`: four new tests. See row 19 of this file for the kept bus pad |
| 6 | P957's test loses its scenario: the new map routes with no false pour short | plan, round 1 refuter | acted | see row 12 of this file (R4) |
| 7 | the expectations that change by the PO's decision: the P780 test and the two docstrings that quote P780's order | round 1 refuter | acted | `TheWalksBoardTest.test_the_led_takes_a_wake_pin_and_leaves_the_i2c_pins_free`: the LED from IO21 to IO13, and not on 21, 22 or 32. The docstrings of `TheWalksBoardTest` and `ABusPinComesAfterThePlainPinsTest` say the P1010 order and keep P780's as history |
| 8 | retire the `sprint-3-p3.json` rows "spi" and "i2c" at 15 | round 1 refuter | rejected | dropped because round 2 (R1) showed that `test_the_bus_penalty_is_a_tie_breaker_smaller_than_one_ability` still catches both. No row is retired |
| 9 | the docs and notes that say P780's order: `commands/build.md`, `skills/spark-design/SKILL.md`, the comment and the two role strings in `board_rules.py`, the bus notes of `boards/firebeetle2-esp32s3.json` and `boards/xiao-esp32-c6.json` | round 1 lens | acted | each says the new order in short sentences. `sprint-3-p3.json` rows 5 and 6 are re-aimed at the new role strings, with their mutants kept |
| 10 | R2: the why of a plain signal on a bus pad says that the free pads with no bus role are kept for another job, names them and keeps the spare abilities. It never says that no such pad was left | round 2 refuter | acted | `PadOrder.kept_words`. On the C6 walk: "(adc: D6, A1, A2 and D12; console_uart: TX and RX)". It says "every pin with no bus role that could serve is taken" only when no such pad is free, which is then true. Rows 7 and 8 |
| 11 | R3: the why of a plain signal on a pad with no bus role says "the cheapest pin left with no bus role", because a bus pad can cost less | round 2 refuter | acted | the words appear only when a free bus pad costs less, the one case where "the cheapest pin left" is false (D11 at 16 while MISO, SDA and SCL cost 13). See row 15 of this file. Row 9 |
| 12 | R4: P957's temp copy pins all four control lines, and its assertion stays | round 2 refuter | acted | the temp copy's `signals` holds EPD_CS D3, EPD_DC D7, EPD_RST SDA and EPD_BUSY SCL. The shared fixture is not changed. Run alone with the real board engine: OK in 5.7 s. On the new order without the pins it failed with `10 trace(s), 0 errors, tsci 0.0.2600` |
| 13 | R5: `PadOrder` takes the cost function and `CONFLICTING_ROLES` as arguments, so no import cycle, and `_why` calls `PadOrder.why`, so the p971 row keeps its anchor | round 2 refuter | acted | `PAD_ORDER = pad_order.PadOrder(_cost, CONFLICTING_ROLES)` in `pin_assigner.py`. `pad_order.py` imports nothing. The line `why = _why(needs, pin)` is unchanged |
| 14 | R6: `TheDesignAreaTest.MODULES` gains `pad_order`, and the map page is regenerated | round 2 refuter | acted | red first, then the module. `python3 tools/map.py --write` names `tests/test_assign_pins.py` for `pad_order.py`, because the direct test builds a `PadOrder` |
| 15 | R3 as written would move the why of every plain signal on a pad with no bus role: four design goldens and `docs/guide/journey/firmware.md` quote "the cheapest pin left could still pwm" on the S3, and the brief says that any other test that goes red stops the build | build | acted | the conditional words of row 11 of this file. The design, breadboard and records goldens ran OK, and no quoted text changed |
| 16 | the why of a bus pad needs the free pads, but `_why(needs, pin)` keeps its two arguments for the p971 anchor, and `assign` has no line to spare | build | acted | the free pads ride on the pin's dict: `pin = dict(usable[label], free=usable)`, the same line count. `assignments` copies its keys by name, so `free` never reaches the map. Row 11 |
| 17 | R2's "(an ADC1 reading, a wake)": a pad that wastes only wake is never kept by the rule, so no free pad is kept for a wake | build | acted | the why names the reason of each kept pad: "adc" when the signal would waste it, then each conflicting role by its name |
| 18 | a bus pad with something else wired to it must keep the assigner's "already wired here" words. No shipped board has one | build | acted | `PadOrder.why` returns None for such a pad. The helper test asserts it, and row 10 plants the other way |
| 19 | the plan's test "a kept bus pad sorts after a plain kept pad" cannot catch the row "the bus tier also on kept pads": with that mutant the S3's SDA still sorts after A0 | build | acted | `test_a_kept_bus_pad_is_ordered_by_its_cost_among_the_kept_pads` asserts A0, then SDA, then TX (the console, 48). Row 6 goes red only on that test |
| 20 | the plan's test 3 says "the third free plain signal lands on MISO". With D3, D7 and D11 named and no SPI part, SCK and MOSI are free too | build | acted | `test_spi_comes_before_i2c`: three plain signals take MISO, MOSI and SCK, and SDA and SCL stay free. Rows 1, 2 and 12 make it red |
| 21 | `test_a_signal_that_needs_adc_takes_a_pad_with_no_bus_role_before_an_i2c_pad` passes on main too: on the S3 the bus penalty already orders pads that waste the same | build | closed | it pins the property the PO asked for. No shipped board has an adc signal that the bus tier moves (R8: no adc or wake signal moved on 7 boards) |
| 22 | the walk's fixture `tests/data/breadboard/epaper-c6` has no `joined_pads`, and the store record has | plan | closed | `pins` and `pin_roles` of the fixture and of the store's `firebeetle2-esp32c6` are equal (compared in the build). `PlainPadsFirstTest.setUp` sets the store's joins, as the P971 test does |
| 23 | the store's board records still say P780's order in their bus notes | plan | rejected | dropped because the store is the PO's and the plan puts it out of scope. The PR names it for him, with the demo walk `p934-display2` and its `firmware/pins.py` |
| 24 | each new or re-aimed row is planted by hand and red | build | closed | the 12 rows of this table and `sprint-3-p3.json` rows 5 and 6: each red on `tests.test_assign_pins`, `tests.test_parts` and `tests.test_boards`, and the tree restored after each |
| 25 | `--anchors` refuses no row that main accepts | build | closed | main 98d96bdd: `4508 mutation(s) in 384 table(s): 33 would be refused`. The branch: `4520 mutation(s) in 385 table(s): 33 would be refused`, the same 33 rows |

The C6 walk's map, `assign_pins.py requirements.json` on the fixture with the e-paper's record, measured 2026-11-23:

```text
signal       before (main 98d96bdd)               after
SCLK, MOSI   SCK (GPIO23), MOSI (GPIO22)          same
EPD_CS       D3 (GPIO14)                          same
EPD_DC       D7 (GPIO18)                          same
EPD_RST      SDA (GPIO19)                         D11 (GPIO7)
EPD_BUSY     SCL (GPIO20)                         MISO (GPIO21)
still free   D6, A1, A2, D12, D11, TX, RX, MISO   D6, A1, A2, D12, TX, RX, SDA, SCL
```

The T-Display (`tests/data/boards/lilygo-t-display.json`): with a button and an LED, the LED moves from IO21 (SDA) to
IO13. With the P798 walk's three parts nothing moves.
