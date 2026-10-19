# P351 tech-lead lens: walk 1 rows

Verified means I read the code. "Unconfirmed" means I did not.

| Row | Verified? | Sort | Change or card | Test |
|---|---|---|---|---|
| 1 | Yes. check_all.py:399-406 lists boards.available(), the whole library, not the project's board | Fix now | Print the active board first and the library count apart ("board xiao-esp32-c6, library 2"). Refactor: one helper that names the active board, used by notes | check_all test on the boards note text from a XIAO project |
| 2 | Not read. Needs idea/match code | New card | "an indicate need sees only parts → the board's own LED is offered as a pick when the record names one" | Later, with the card |
| 3 | Follows row 2 (check_spine verdict from picks) | Same card as 2 | none | none |
| 4 | Yes, by design (drawer hold) | No change | Closed in the row already | none |
| 5 | Yes. assign_pins.py:420 says polarity is not in the record, and boards/xiao-esp32-c6.json:151-155 has onboard_led gpio 15 with no level | Fix now | Add `"active_level": 0` to `pin_roles.onboard_led` with its source. assign_pins writes `ONBOARD_LED_ON = 0` beside ONBOARD_LED when the record has it, else keeps today's note. A fact, not behaviour | test_assign_pins near :506: pins text holds ONBOARD_LED_ON = 0 for XIAO, none for a record without the field |
| 6 | Partly. check_spine.py:251 looks for $serialMonitor. The converter (tools/circuit-to-wokwi/dist/converter.mjs:6793) adds it only if the part has pins named TX and RX. Whether the XIAO part has them I did not confirm. P213 b2 passed, so the cause is unconfirmed | New card | "the XIAO's Wokwi part shows no serial monitor wire → find the part's pin names (D6/D7?) and map them, or say the scenario still hears" | Converter test with the XIAO part |
| 7 | Yes (gate in deploy_gate.py) | Existing card | P337 #431. It already holds the PO's words | none |
| 8 | Not read. Follows from a copy outside spark | Existing card | P337 #431, since a path into the board without a run is its subject. If P337 says no, a card "a copy leaves the board's old spark.json → deploy clears stale files" | none |
| 9 | Not reproduced. One event | No change | Note on P248 #270 (bounded console read). A repeat gets a card | none |
| 10 | Yes. The record has `physical.buttons` boot place only (json:26-30), no GPIO | Fix now, joined to P332 #426 | Add `pin_roles.boot_button.gpio [9]` with source. Do not build the built-in parts list here, that is #426. pins.py then writes `BOOT_BUTTON = 9` | test_assign_pins: pins text holds BOOT_BUTTON = 9 |
| 11 | Yes. flasher.py:40 IMAGE_OFFSET = "0x0" | Existing card | P335 #429 | none |
| 12 | Card exists | Existing card | P349 #445 | none |
| 13 | Yes. stand_in/machine.py:52 raises ImportError for PWM, and the test at test_import_firmware.py:118 expects it | Fix now | Add a small `PWM` class (freq, duty, duty_u16, deinit, remembers its last duty). Facts-only, no timing. Update the docstring (line 6) and the :118 test, which uses PWM as its example, to use I2C | New test: firmware with PWM(Pin(15)) imports, and duty is remembered. The old test uses I2C |
| 14 | Yes, no bounded read exists | Existing card | P248 #270. Add the walk's port-busy message as its evidence | none |

## Facts need a source (rows 5 and 10)
- Seeed XIAO ESP32-C6 wiki: https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/ (already cited in the record at line 6). I did not fetch it. The PO's bench result (LED_ON = 0, B = GPIO9, 2026-10-19) is the second source. Cite the printed version, page and sha256 per "keeping sources". Mark the level "bench-confirmed, wiki unread" until someone reads the wiki.
- Seeed schematic: the second page, only if the wiki is silent on polarity.

## Names
- One word for one thing: the record uses `onboard_led`, pins.py uses ONBOARD_LED. Keep `active_level` (0 or 1) and pins.py `ONBOARD_LED_ON`. Do not coin LED_ON. Use `boot_button` / `BOOT_BUTTON`, matching "boot" in `physical.buttons`.

## Order of fix PRs
1. Row 13, the PWM stand-in. It blocks Claude's firmware import now, and it is self-contained.
2. Rows 5 and 10 together as one record-and-pins PR (about 40 lines). Both read the same board record and the same pins writer. Land the sources first.
3. Row 1, the boards line. Pure wording, last.
Then new cards: rows 2 and 3 (one card), row 6.
