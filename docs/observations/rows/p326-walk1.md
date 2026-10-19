# P326 walk 1: findings rows

Gaps, bugs and things to consider from walk 1, the reaction game on the XIAO ESP32-C6 (2026-10-19). The walk record
is `docs/observations/2026-10-19-p326-walk1.md`.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `check_all.py` lists two board definitions (the FireBeetle too) for a project that uses only the XIAO | walk, init | raised | `check_all.py --project .` resolution block |
| 2 | `--match` offers no "board's own LED" for an indicate need, though the board record names one | walk, idea | raised | the light need got LED matrices and a 5 mm LED |
| 3 | The build says "not every need is on the board: light (no pick)", though the board's LED serves the need | walk, build | raised | `check_spine.py` verdict; follows from row 2 |
| 4 | The drawer held the one XIAO for plant-alarm, an older project, so the pick was refused until the PO freed it | walk, idea | closed | expected behavior; the PO said yes and the hold moved |
| 5 | The board record does not hold the onboard LED's polarity, so firmware guesses the level that lights it | walk, build | raised | `firmware/pins.py`: "its polarity is not in the board record" |
| 6 | The simulation line warns that no serial monitor is wired for the XIAO's Wokwi part | walk, build | raised | `check_spine.py` simulation line; P213 b2 passed a scenario on this board all the same |
| 7 | `deploy.py` flashes only an image that passed a Wokwi run, and the PO wants Wokwi only rarely, because the minutes cost | the PO, walk | acted | his words on P337 #431; tonight the walk copied the firmware with `mpremote`, outside spark |
| 8 | The copy outside spark leaves the board's old `spark.json` and `blink.py`, so the facts file on the board describes the blink deploy | walk, bench | raised | `mpremote fs ls` after the copy |
| 9 | `mpremote exec` failed once with "could not enter raw repl" while the old blink firmware ran; `look.py` then worked, and a second `mpremote` call worked | walk, bench | raised | the first call before `look.py` |
| 10 | The PO has no breadboard at hand, so the walk uses the XIAO's own B (BOOT) button; the board record has the button's place but not its GPIO, so `pins.py` cannot name it | walk, bench | raised | `boards/xiao-esp32-c6.json` `physical.buttons`; built-in parts in `pins.py` is P332 #426 |
| 11 | spark lists no MicroPython build for the original ESP32, and `flasher.py` writes every image at `0x0` | walk, T-Display question | raised | `data/tools.json`, `scripts/flasher.py` `IMAGE_OFFSET`; P335 #429 |
| 12 | The PO wants spark to find and fetch the right build itself: the most specific first, then more and more generic, done by an agent | the PO, walk | acted | P349 #445, his words |
| 13 | spark's stand-in `machine` has `Pin` only, so `import_firmware.py` stops on any firmware that uses `PWM` (a dimmed LED) | walk, change by words | raised | "effects raised: ImportError: spark's stand-in machine (scripts/stand_in/machine.py) has Pin only, not PWM" |
| 14 | Claude cannot read the person's console, so the walk depends on the person pasting what it printed; a copy fails while that console holds the port | walk, bench | raised | "failed to access /dev/cu.usbmodem1101 (it may be in use by another program)"; P248 #270 is a bounded console read |
| 15 | The T-Display (CP2104) shows as two ports, `/dev/cu.SLAB_USBtoUART` and `/dev/cu.usbserial-0206D76B` | TTGO experiment | raised | `ls /dev/cu.*`; P333 #427 |
| 16 | The pinned driver st7789py (commit 7265925) does not import on the board's MicroPython v1.18: it uses `const()` on strings; it needed a hand patch | TTGO experiment | raised | "SyntaxError: constant must be an integer"; a driver record must name the oldest MicroPython it runs on, P336 #430 |
| 17 | The board's v1.18 is a pre-release (v1.18-307) whose `.mpy` variant matches no `mpy-cross` on PyPI (1.12 is v5, 1.19.1 v6 flags differ) | TTGO experiment | raised | "incompatible .mpy file", then "invalid syntax for number"; a reflash to v1.29 removes it, P335 #429 and P349 #445 |
| 18 | After the driver loads, the largest free RAM block is about 32 KB of 82 KB free, so a full-screen buffer (64.8 KB) does not fit; a 240x68 band does | TTGO experiment | raised | measured on the board; the driver record wants a memory fact beside speed (P336) |
| 19 | The display's pins are a note in the T-Display record, not pin roles, so firmware types them by hand | TTGO experiment | raised | `lilygo-t-display.json` `//pins`; P332 #426 |
