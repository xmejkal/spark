# P388 button level in the XIAO record: findings rows

Findings from building P388 (2026-10-22, Prague). It closes row 3 of `p378-walk2-map.md`. One agent (Sonnet 5.5) wrote them.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The code already wrote `ONBOARD_BUTTON_ON` from `active_level`, so the card was a record change plus a test | card, code | verified | `onboard_lines` in `scripts/assign_pins.py`, P353 |
| 2 | The B button reads 0 when pressed: net BOOT on pin 15 (GPIO9) has a 10K pull-up R17 to 3V3 and the switch K2 to GND | Seeed schematic v1.0, sheet 04 ESP32 C6 (file page 5), sha256 510f3f91...80dad7 | verified | `boards/xiao-esp32-c6.json` `onboard_button`, cited as `xiao-c6-schematic-v1-0`. No bench reading yet |
| 3 | The same sheet shows the LED D4 with its anode on 3V3 through R25 and its cathode on GPIO15, so 0 lights it. That agrees with the walk-1 bench | Seeed schematic, sheet 04 | verified | the stale "schematic not read" in the LED note is fixed in this PR |
| 4 | The 15 pF capacitor C22 sits on the BOOT net with R17, so a bounce is likely in firmware | schematic | raised | a debounce is for the firmware to write. The record holds no timing, by the rule that spark exports facts only |
| 5 | The review (Sonnet 5.5): the predictions file is dated before the walk, so it takes no edit. The LED note lacked its file page. Row 4 held a "may" | review | acted | the predictions edit is taken back, the page added, row 4 reworded |
