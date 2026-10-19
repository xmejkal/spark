# P328 phone nearby: implementation plan

Tags: [M] measured with the command named, [E] estimate to check, [P] proposal.

## 0. The Bluetooth check (first, 5 minutes)
Seeed's build SEEED_XIAO_ESP32C6 may lack the bluetooth module [E]. The record names this build [M: `grep micropython_port boards/xiao-esp32-c6.json`]. Check on the board: `import bluetooth`, then `bluetooth.BLE().active(True)`. Either the PO types them in `python3 -m mpremote connect <port> repl`, or he gives a live grant in his own terminal and Claude runs `live.py --code` with the same two statements [M: docs/guide/agents.md on live.py]. The code holds no pin number, so live.py will not refuse it [M: same page]. The firmware stops while it runs. The board needs MicroPython already [E: earlier walks flashed it].
- Branch A, no error: go on.
- Branch B, ImportError: stop and tell the PO. Two ways [P]. Switch the record to ESP32_GENERIC_C6, which has BLE [E]. That undoes his P229 choice, so he decides. Or the walk ends with the finding "this build has no Bluetooth".

## 1. What the person does and sees
The PO says "light the LED while my phone is close, print the signal". He starts a free advertiser app on the phone [E: nRF Connect, name SPARKPHONE]. The LED lights within about a metre [E]. The console prints a line a second.

## 2. Parts
The XIAO alone. The LED is GPIO15 [M: `grep -n -A3 onboard_led boards/xiao-esp32-c6.json`], active low [E: Seeed wiki, not in the record]. No resistor.

## 3. The walk
1. `/spark:idea`, or a hand-written `requirements.json` with `"board_only": true`, as P236 did [M: docs/guide/journey.md, "The first flash"]. Whether idea writes it is unknown [E].
2. `check_spine.py requirements.json --keep .` writes `firmware/pins.py` with `ONBOARD_LED` [M: commands/build.md].
3. Claude writes `firmware/main.py` in the conversation.
4. `run_scenario.py sim/scenarios/phone-nearby.scenario.yaml`, after the PO agrees to the Wokwi minutes.
5. `look.py --json`, then `deploy.py --json --token <t>`. The PO types yes in his terminal.

## 4. The firmware [P]
- Recognition: phones randomize their address [E], so ignore it. Match the advertised name SPARKPHONE. Fallback: a fixed service UUID. An iPhone may stop advertising in the background [E], so keep the screen on.
- Rejected: the board advertises and the phone connects. MicroPython gives no RSSI of a live connection [E].
- Scan: continuous passive scan, 30 ms window. Each match gives an RSSI [E].
- Smoothing: median of the last 5 matches [E]. RSSI jumps 5 to 10 dB [E].
- Hysteresis: on at -65 dBm or stronger, off at -75 or weaker [E]. The PO tunes it from readings at 0.5 m and 3 m.
- No match for 5 s means off.
- Console: `ready` once the scan runs, `rssi -62 avg -64` each second, `LED on`, `LED off`, `phone lost`. A typed `rssi -60` feeds the logic as a sample. The loop reads the console without waiting, as the blink does [M: docs/guide/journey.md, P215 run].
- If `import bluetooth` fails, as in Wokwi, print `ble: none` and use the console feed only [E].

## 5. The scenario and the gate
Wokwi does not simulate Bluetooth [E]. A board-alone project has no part to set. So the scenario uses `write-serial` steps [E: named in docs/discovery/2026-10-18-p295-own-simulator/finding.md, no spark scenario uses one]. It sends weak samples, strong samples (expect `LED on`), a middle sample (still on), weak again (expect `LED off`), then silence (expect `phone lost`). That tests threshold, hysteresis, smoothing and console. It cannot test scanning, the name match, the radio or the real pin. An `expect-pin` on a board LED may not work [E].
The gate cannot know what a scenario covers. It flashes any image whose log says passed on its sha256 [M: `sed -n 50,75p scripts/project_image.py`]. So a pass with the radio replaced opens it like any other. The console feed ships on the board too, because the tested image is the flashed one.

## 6. Deploy and the bench check
Deploy as in step 5. Then the PO starts the app, sees `ready` and the `rssi` lines, walks away and watches `LED off`, comes back and watches `LED on`. No `rssi` line for a minute means recognition failed.

## 7. A change by words
"Light at 2 metres, not 1": Claude changes the two numbers, the scenario samples follow, then run, look, second deploy. The new image has a new sha256, so the old pass no longer counts [M: ProjectImage.why_untested].

## 8. Predictions
1. Branch A [E 70%]. See: step 0.
2. The scenario passes on the first or second run [E]. See: its log.
3. Name matching works on Android and fails on a backgrounded iPhone [E]. See: try both.
4. RSSI at 1 m varies 10 dB or more with how the phone is held [E]. See: the console.
5. The first thresholds are wrong [E]. See: readings at 0.5 and 3 m.
6. The LED is active low [E]. See: the first `LED on` line against the light.

## 9. Gaps in spark [P], not filed
- A log cannot say what its scenario left out. Fix: a `not covered:` line in the log. Round: say it in the notes.
- No record of which modules a MicroPython build holds. Fix: a `micropython_modules` field with a source. Round: step 0.
- No pin assert for an on-board LED in a board-alone simulation [E]. Round: `wait-serial` proves the decision, not the pin.
- `parts.py --requirements` may not write `board_only` [E]. Round: a hand-written file.

## 10. Done when
Step 0 is answered. On branch A the LED follows the phone on the bench, the console shows the RSSI, the scenario passed with the radio replaced, and the notes list what it did not cover. On branch B the notes hold the finding and the PO's choice.

## 11. Size and time [E]
About 120 lines of firmware and 30 of scenario. Step 0: 5 minutes. Writing and simulation: 1 hour. Bench and tuning: 45 minutes. One session.
