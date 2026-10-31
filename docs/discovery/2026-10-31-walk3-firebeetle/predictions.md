# Walk 3 predictions: the FireBeetle 2 on a breadboard (P365)

> Walk 3 puts a button and an LED on a full-size breadboard, with the DFRobot FireBeetle 2 ESP32-S3.
> Spark builds the chain, the sheet and the pin map today (proved by a dry run). It stops on 3 things: the board is
> held by smartbin-local, the simulation hides its stand-in board, and the drawer holds no resistor.

Written 2026-10-31 (Prague), before the walk. Refs P100 #6 (the MVP) and the walks epic #467. Walk 2 is the model:
`docs/discovery/2026-10-22-p378-walk2/predictions.md`.

Marks. **(D)** proved by a dry run on 2026-10-31. It ran in a scratch project and a scratch copy of the store. No USB,
no Wokwi run, no board. **(R)** read from code or the board record only. Nothing was deployed.

Facts for all steps. The sheet draws 63 columns and no rails. The board record has `wokwi_is_stand_in: true`, no
`physical.buttons`, and `pins` D3 = GPIO38 and A5 = GPIO11.

| # | step | prediction (2026-10-31) | mark |
| --- | --- | --- | --- |
| 1 | Init | `init_project.py --board firebeetle2-esp32s3` writes every file with no stop and says "no built design found, so the rails are empty". | D |
| 2 | Drawer | The drawer holds the FireBeetle (1, "held by smartbin-local") and the tactile buttons. It holds no LED, no resistor, no breadboard and no jumper. | D |
| 3 | Idea | `--match` offers the board's own LED (GPIO21) and own button (GPIO47) before `led-red-5mm` and `tactile-button`. A pick of the FireBeetle is refused: "1 owned, held by smartbin-local". Spark prints the fix. | D |
| 4 | Research | Not needed. The button, the LED and the board all have records. | D |
| 5 | Requirements | After the picks, `--requirements` writes `board`, `tactile-button`, `led-red-5mm` and no `board_only`. | D |
| 6 | Build | `check_spine.py requirements.json --keep .` exits 0 in about 8 s, with "the chain runs end to end". It writes `breadboard.md`, `breadboard.svg`, `page.html`, `firmware/pins.py` and `sim/`. | D |
| 7 | Pin map | `BUTTON = 38`, `BUTTON_PULL = "up"`, `STATUS_LED = 11`, `ONBOARD_LED = 21`, `ONBOARD_BUTTON = 47`. No polarity line for the onboard LED. | D |
| 8 | Sheet | 9 steps. Parts: a 330 ohm R1, the LED, the button, "a breadboard and jumper wires" (all "to get" except the button). Jumpers: A5 to R1, D3 to the button, GND (pad GND2) to the LED cathode. The picture caveat reads "pads not verified, row side not verified, USB end not verified, GND1 and GND3 doubtful". Its text says "no Wokwi diagram for this board". | D |
| 9 | Fit | The board pins sit 9 holes apart, so on a normal breadboard each row of the board keeps 3 to 4 free holes. The first sheet step says "each pin in its own row". The sheet states no column numbers. | R |
| 10 | Checks | First run: exit 2, "nothing found by the 2 check(s) that completed, of 5" (physics has no rails). After `init_project.py --force`: "nothing found by the 4 check(s) that completed, of 5, resting on 4 ? line(s)". It names the internal pull-up of the button as a line "no netlist shows". | D |
| 11 | Firmware | Claude writes `firmware/light.py` and `main.py`, and `import_firmware.py` prints `ok` at the first run. A stand-in `machine` has `Pin` with `PULL_UP`. | D |
| 12 | Simulate | The diagram uses `board-esp32-s3-devkitc-1` for the FireBeetle, and a `wokwi-pushbutton`, `wokwi-led` and `wokwi-resistor`. `WHAT-THIS-CANNOT-SHOW.md` and the build output do NOT say that the board is a stand-in. They name only the LED, the button and "onboard GPIOs not checked". A scenario can press the button, unlike walk 2. It spends Wokwi minutes, so the PO is asked first. The firmware must print `ready`. | D (diagram, notes), R (run) |
| 13 | Image | `flash_image.py --project . --files firmware -o fw.bin` writes 4096 KB: MicroPython (`ESP32_GENERIC_S3` v1.29.0) at 0x0, the files at 0x200000. A 16 MB board gets the 4 MB layout. The octal PSRAM stays unused. | D |
| 14 | Bench look | `look.py --no-simulation` reads chip `esp32s3` and flash 16 MB (or 4 MB), both in the record's `flash_mb [16, 4]`, and prints a token. If the board waits in download mode, the hint says only "the board's reset button", with no place, because the record has no `physical.buttons`. | R |
| 15 | Deploy | `deploy.py --no-simulation --token T` asks for a typed yes in a real terminal, erases, writes, reads back. The log says `simulation: none`. | R |
| 16 | Lit LED | After wiring per the sheet, a press of the button lights the LED on GPIO11 (pull-up, so pressed = 0, LED on = 1). If the sheet's row side is wrong, or R1 is missing, it does not light. | R |
| 17 | Change | "Blink while held" is firmware only. No hardware change, so no rebuild of the sheet. `light.py` changes, `flash_image.py` runs again, and `look.py` prints a new token. | R |
| 18 | Second deploy | Same path as step 15, one more typed yes, a new token. | R |
| 19 | Outside spark | 1 or more steps happen outside spark: the PO finds a resistor and a jumper kit, and checks the board's pin sides by eye. | R |

## Known risks before the walk

1. **The FireBeetle is held, so the pick fails.** The real store's drawer entry `dfrobot-dfr0975` has
   `used_in: smartbin-local` (D: `--pick` printed "refused, so nothing was written: firebeetle2-esp32s3 - 1 owned,
   held by smartbin-local"). A small fix exists and spark prints it: a file for `--drawer-set` that drops
   `used_in`, after a dry run. It changes the PO's store, so he decides. The other path is to free the board in
   smartbin-local.
2. **The drawer holds no resistor, LED, breadboard or jumper** (D: step 2). The sheet lists them as "to get". Walk 1
   found that the PO had no resistors. Without R1 the LED must not be wired. No code fix. Check the kit before the
   walk. One spare 330 ohm resistor ends this risk.
3. **The simulation hides that the board is a stand-in** (D: the three lines of `WHAT-THIS-CANNOT-SHOW.md`). A pass
   proves the firmware only. A small fix exists. When the record has `wokwi_is_stand_in`, print one line from
   the record's `//wokwi_part_type` sentence. Pins 38 and 11 were not looked up in Wokwi's own board file.
4. **The breadboard picture is not trusted.** Its own caption lists four doubts: pads, row side, USB end, and
   GND1 and GND3 (the record's `doubtful_pads`, P412). The picture also draws the button on the board's outline,
   and the page has no numbered columns. The PO follows the 9 steps, not the picture. The fix is the bench: one look
   at the USB end and one continuity check of GND2.
5. **The pin map has no polarity for the onboard LED** (D: `ONBOARD_LED = 21` with the note "Its polarity is not in
   the board record"). The walk's own LED is external, so this does not stop it. If the PO uses the board's
   LED instead, the firmware guesses. A small fix exists: one bench press, then a record line (the walk 2 pattern, P388).
6. **A download-mode hint has no button place** (R: the record has no `physical.buttons`, and the XIAO's has). On a
   first flash the PO can need to find BOOT and RESET alone. A small fix is a `buttons` entry in the record.
7. **`check_all` ends at exit 2 until init runs twice** (D: step 10). The first run has no rails. The second
   (`--force`) fixes it. It reads as a failure to the PO. A small fix is for the build to say so.
8. **The matches offer the board's own LED and button first** (D: step 3). A pick of the board for "light" skips the
   breadboard LED. When Claude asks, the PO says "led-red-5mm".
9. **Not proved:** `look.py` and `deploy.py` on an S3 (they touch USB), the Wokwi run, and the typed yes in a real
   terminal. S3 native USB can show another port name than the XIAO's. `look.py` lists the ports.
