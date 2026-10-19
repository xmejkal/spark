# P327 plan: Wi-Fi hot and cold on the XIAO ESP32-C6

Tags: [M] measured (command named), [E] estimate to check, [P] proposal.

## 1. What the person does and sees
The person says "the LED blinks faster as I get closer to my router". They plug in the XIAO, type the network name on the console, and walk. The console prints a scan line every few seconds and the LED speeds up when the signal grows. [P]

## 2. Parts
None. The board's own LED is GPIO15 [M: `/usr/bin/grep -n -A3 onboard_led boards/xiao-esp32-c6.json`]. No wiring, no resistor, so no breadboard sheet is needed. The firmware imports `pins.ONBOARD_LED` [M: `~/Development/blink-c6/firmware/pins.py`]. The LED's polarity is not in the record [M: `scripts/assign_pins.py:420`]. A blink only toggles, so it does not matter.

## 3. The walk
1. `/spark:init` then `/spark:setup` [M: `commands/init.md:30`].
2. Skip `/spark:idea`. No need maps to a part. The PO's blink-c6 project has a hand-written `requirements.json` with `"board": "xiao-esp32-c6", "board_only": true, "parts": []` [M: `cat ~/Development/blink-c6/requirements.json`]. I propose the same. If `/spark:idea` runs, expect it to offer an LED to buy [E].
3. `check_spine.py requirements.json --keep .` [M: `commands/build.md:69`]. With `board_only`, the parts, schematic, footprint and build stages are `skipped` and the simulation stage says "the board alone" [M: `scripts/check_spine.py:372`, `scripts/check_spine.py:557`]. This is where the path leaves normal. Nothing to wire, so the drawing has no wiring and the sheet is of little use [E].
4. The conversation writes `firmware/` and `sim/scenarios/*.scenario.yaml`. Then `import_firmware.py`, then `run_scenario.py` (spends Wokwi minutes, ask first) [M: `commands/build.md:226`].
5. `look.py --json`, then `deploy.py --json --token <token>` [M: `commands/deploy.md:16`].

## 4. The firmware (all [P] unless marked)
- Scan with `network.WLAN(network.STA_IF).scan()`. It returns tuples with SSID and RSSI [E, MicroPython docs]. A scan blocks, about 1 to 3 s [E]. So the loop scans every 3 s and blinks between scans. The LED pauses during a scan. This is a likely surprise.
- Mapping: clamp RSSI to -90..-30 dBm, then period = 1000 ms at -90, falling linearly to 100 ms at -30. These numbers are guesses for the bench to tune.
- Smoothing: average of the last 3 scans. A missing network counts as -90.
- Console: `scan: 7 networks`, then `MyRouter -61 dBm avg -63 blink 480 ms`. Lines are printed because a scenario waits on them (the ready contract) [M: `commands/build.md:245`].
- Choosing: a constant `TARGET = "..."` in the firmware, and typing `ssid <name>` or `list` on the console. The loop reads the console without waiting, as blink-c6 does [M: `~/Development/blink-c6/firmware/blink.py` header].
- Pure functions (`period_for(rssi)`, `smooth`) are importable and tested on the Mac.

## 5. The scenario
spark's repo says nothing of Wi-Fi in Wokwi [M: `/usr/bin/grep -rniE "wifi|wlan|wokwi-guest" scripts commands docs/guide` found only an ADC note]. Outside knowledge [E]: Wokwi simulates Wi-Fi on ESP32 with a network called Wokwi-GUEST. Whether it works on the C6 and returns a scan result is unknown. Check it first with a 10-line scan-only firmware.
Smallest honest scenario, if the scan lists Wokwi-GUEST:
`wait-serial: "Wokwi-GUEST"`, `write-serial: "ssid Wokwi-GUEST\n"`, `wait-serial: "blink "`.
It proves scan, choice and a printed period. It cannot prove walking closer, since the signal is fixed [E]. The mapping is proved by Mac tests of the pure functions. The scenario's `set-control` moves parts only, and no part is here [M: `commands/build.md:254`]. If the scan comes back empty, the scenario asserts `scan: 0 networks` and says so. That is a weaker pass and the notes must say it.

## 6. Deploy and bench
Deploy as in section 3. The bench: type the router's name, stand next to it, walk away and back. Pass if the period falls near the router and grows far away, and the list shows other flats' networks. Note the pause during scans.

## 7. Change by words
"Blink a bit faster, and a different network." Edit `TARGET` or the mapping, rerun the scenario, `look.py`, `deploy.py`. A second deploy needs a new token and a yes [M: `commands/deploy.md:23`].

## 8. Predictions (how to see each)
1. `import_firmware.py` fails on `import network`. The stand-in holds only `machine` [M: `ls scripts/stand_in` printed `machine.py`]. See: run it.
2. Wokwi's C6 gives no Wi-Fi or an empty scan [E]. See: the scan-only firmware.
3. The scan pause makes the LED stutter [E]. See: the bench.
4. `/spark:idea` offers parts for a partless goal [E]. See: run it once.
5. Wokwi-GUEST's strength is fixed, so a pass says little. See: the log.

## 9. Gaps and fixes (card proposals, not filed)
- A `network` stand-in in `scripts/stand_in/` with a scan list set by tests. Way round: import `network` inside `run()`, which weakens the import check.
- `/spark:idea` with an `--on-board` path for goals with no parts. Way round: write `requirements.json` by hand.
- The board record holds no Wi-Fi facts (antenna, scan notes). Records grow by need [AGENTS.md], so add none yet.

## 10. Done when
Matches the card: the LED blinks faster as the chosen network's signal grows, the console lists networks with strength, it ran through spark, and the notes say what the simulation did and where spark stopped.

## 11. Size and time [E]
Firmware about 120 lines, scenario 8 lines, Mac tests 30 lines. One session, about 2 hours with the bench. Expect one extra hour if Wokwi has no C6 Wi-Fi.
