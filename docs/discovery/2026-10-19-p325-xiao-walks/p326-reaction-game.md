# P326 plan: reaction game on the XIAO ESP32-C6

Tags: M measured (command named), E estimate, P proposal. Every M ran in a scratch project with an empty `SPARK_HOME`.

## 1. What the person does and sees (P)
The console says `round 1 of 5, get ready`. After a random wait the board's LED lights and the console says `go`. A press prints `reaction 243 ms`. A press too early prints `false start` and the round repeats. After five rounds it prints `best 198 ms`.

## 2. Parts and wiring
- The XIAO, one button, two jumpers, no LED part, no resistor. The drawer holds `6-6-tactile-buttons-a-bag`, linked to `tactile-button`. (M: read the file in the store's `drawer/`)
- Pins: `assign_pins.py requirements.json --emit-pins firmware/pins.py` gave `BUTTON = 17` (pad D7), `BUTTON_PULL = "up"` and `ONBOARD_LED = 15`. (M) Wiring is D7 to one leg and GND to the other.
- The pull-up is the chip's own, 45 kOhm. (M: `boards/xiao-esp32-c6.json`)
- The sheet starts "Put the board in the breadboard". (M: `check_spine.py requirements.json --keep .`) Whether a breadboard exists, and whether pins are soldered, are unknown. Ask first.

## 3. The walk (P)
1. `init_project.py --project . --board xiao-esp32-c6` (M)
2. `/spark:idea` with "a reaction game", then `parts.py --requirements <project>`.
3. `check_spine.py requirements.json --keep .` (M: 6 s, exit 0)
4. The conversation writes `firmware/game.py`, `firmware/main.py` and `tests/test_game.py`. Then `import_firmware.py` and `check_all.py --project .`.
5. The conversation writes the scenario. After a yes, `run_scenario.py sim/scenarios/reaction-game.scenario.yaml --timeout-ms 90000`. It spends Wokwi minutes and needs the token. (M: set in the Mac's environment)
6. The PO wires from `breadboard.md`. Then `look.py --json` and `deploy.py --json --token <token>` in his own terminal.

## 4. The firmware, as the conversation would write it (P)
- A `Game` class (proposed name) takes a clock and a random source, so the Mac tests it.
- Wait 2 to 5 s at random. A press then prints `false start` and repeats that round without counting it.
- Then the LED goes on and `go` prints. A press prints `reaction N ms`. No press in 3 s prints `too slow`.
- After each round the LED goes off and the firmware waits for release. Debounce is 40 ms (unverified in the record).
- After round 5 it prints `best N ms`.
- `LED_ON` is one constant. The record holds no polarity. (M: the comment in `pins.py`)
- The loop polls the console without waiting and prints `ready` once. Without that, deploy ends `ready unknown`. (M: `docs/guide/journey.md`)

## 5. The Wokwi scenario (P)
It waits for `get ready`, presses at once and expects `false start`. It releases, waits for `go`, presses, expects `reaction`, releases, and repeats until `best`. It presses on the `go` line, never after a time. The press is `set-control` on `tactilebutton`, as in the button-light scenario. (M)

Wokwi cannot cover:
- the random wait, which the scenario follows only by its lines
- timing precision, since a simulated reaction is near zero
- the LED, since GPIO15 is no header pin for `expect-pin`, so the `go` line stands in

## 6. Deploy and bench check (P)
`look.py` first, since the board restarts. `deploy.py` flashes only the image that passed. If it says download mode, press R, top left. At the bench the PO plays five rounds and checks that the LED lights at `go` and not inverted, and that an early press is a false start.

## 7. The change by words (P)
"Add a second button that restarts the game." It needs no resistor. Two unnamed buttons stop the build: "give one of them a name of its own". (M) With `BtnReact` and `BtnRestart` (proposed names) the rebuild printed 7 bench changes, one being "Run a cyan jumper from board D10 to the row of BtnRestart A". (M: `check_spine.py` on that file) Then second deploy.

## 8. Predictions
1. Checks end `????` with exit 2, because physics cannot look at a null `regulator_3v3_a`. (M: `check_all.py --project .`)
2. The rename breaks the firmware. `BUTTON` became `BTNREACT_BUTTON` (proposed name) in `pins.py`. (M) See `import_firmware.py`.
3. The LED may light inverted. See it at the bench.
4. `/spark:idea` may call the LED need unserved, since only the board has it. (E) See the `--requirements` notes.
5. A step may time out if Wokwi runs slower than the waits. (E) See the log's verdict line.
6. The build warns "no serial monitor is wired". (M) The blink-c6 scenario passed anyway on 2026-10-19. (M: `~/Development/blink-c6/sim/runs/typed-lines-change-the-blink.log`)

## 9. Gaps and smallest fixes (proposals, not filed)
- No onboard LED polarity in the record. Fix: one field with a source and a bench check. Way round: the constant.
- A need cannot be served by the board's own LED. Way round: leave the need out.
- No scenario reads GPIO15. Way round: serial lines.
- The sheet assumes a breadboard. Fix: a sheet for jumpers alone.
- A rename changes pin names silently. Fix: name the first button from the start.

## 10. Done when
The card's words: the LED lights after a random wait, a press prints the time, an early press is a false start, five rounds give a best score. Every step ran through spark, then one change by words and a second deploy. The predictions are dated first and scored after.

## 11. Size and time (E)
Estimate: firmware about 90 lines, tests 50, scenario 40, and the walk about 3 hours.
