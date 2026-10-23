# Walk 2 map and predictions: button and LED on the XIAO ESP32-C6 (P378)

Written 2026-10-22 (Prague), before walk 2. Scored after the walk by someone who did not write it.

Card: https://github.com/xmejkal/spark/issues/484. Parent walk: P100 (https://github.com/xmejkal/spark/issues/6).
Miro frame: "P378 Walk 2: button and LED on the XIAO (map, 2026-10-22)" on the hub board. Walk 1 is
`docs/observations/2026-10-19-p326-walk1.md`. The walk-1 fixes P352, P353 and P354 are closed. P355 (#453) is open.

Marks: (M) I measured it on 2026-10-22 in a scratch folder (nothing in the PO's store changed, nothing
deployed). (E) I expect it, and I did not measure it.

## 1. The walk in steps

The PO uses the board's own B button (GPIO9) and its user LED (GPIO15). No breadboard parts. Target: 0 steps
outside spark.

| # | step | what the PO does | what spark has today | where it can stall |
| --- | --- | --- | --- | --- |
| 1 | Init | `/spark:init` in a new folder, with the XIAO | `init_project.py --board` writes every file (M, scratch run) | The board comes from a flag. The questions can skip it. `check_all` can list two board definitions (E) |
| 2 | Idea | Says "a button that lights an LED", through `/spark:idea` | Needs, drawer match, picks. The board record names `onboard_button` and `onboard_led` (M) | P355 is open: no pick offers the board's own LED. No pick offers the own button at all. The need stays unserved |
| 3 | Requirements | Gets `requirements.json` | `parts.py --requirements` writes it. `board_only: true` is read only by the build (M: `grep`) | The idea step does not write `board_only`. Without it the build ends `????` (M) |
| 4 | Build | `/spark:build --keep` | The board-only chain runs end to end, exit 0 (M). `pins.py` names `ONBOARD_LED = 15`, `ONBOARD_LED_ON = 0`, `ONBOARD_BUTTON = 9` (M) | No `ONBOARD_BUTTON_ON` line and no pull-up line (M). The firmware must guess the pressed level |
| 5 | Firmware | Claude writes `main.py` in `firmware/` | `import_firmware.py` with a stand-in `machine` that has PWM (M: `stand_in/machine.py`) | A feature the new code uses can be missing from the stand-in (this stopped walk 1) |
| 6 | Checks | `check_all.py --project .` | Runs and finds nothing (M: "nothing found by the 1 check(s) that completed, of 5") | Four checks say "not asked for". The PO can read that as a pass of five |
| 7 | Scenario | Claude writes one scenario, the PO agrees to the minutes | `run_scenario.py`, the board alone in Wokwi, 0 wires (M) | No serial monitor is wired (M). No scenario reads GPIO15. The PO runs Wokwi only rarely |
| 8 | Wiring | Reads the sheet | None. No sheet, no picture, no page for a board-only build (M) | The PO has nothing to read here |
| 9 | Look | `look.py --no-simulation` | Reads the board on USB, compares with the record, prints a token. The flag exists (M: `deploy.py --help`) | The board can sit in a held console (P354 names the way out). Download mode: see walk 1's page, `p326-reaction-game.md` |
| 10 | Deploy | `flash_image.py`, then `deploy.py --no-simulation --token` | Erases after a typed yes, writes, reads back. Needs a real terminal for the yes (M: help) | The PO types the yes in his own terminal. The flow can lead him to a tool outside spark |
| 11 | Lit LED | Presses B, sees the LED | Level 0 lights it, from the walk-1 bench (M: record note) | Pressed level of B is not in the record. Holding B at reset: see the record's `onboard_button` note |
| 12 | Change | "Add a second LED" | A rebuild lists bench changes, a `changed` line each (M: `check_spine.py --help`) | The board has one user LED. A second one is an outside part: a resistor, jumpers, a breadboard. The PO can have no resistor |
| 13 | Rebuild | `/spark:build --keep` again | With `led-red-5mm` the sheet lists LED, 330 ohm resistor, breadboard and jumpers, 6 steps (M) | `board_only` must go and the part must come. The records can disagree on one edit |
| 14 | Second deploy | look, then deploy again | Same path as step 10 | A deploy with no simulation names a caveat. The yes is typed again |

## 2. Predictions

1. `/spark:init` writes every file with no stop. (M) Look: `init_project.py --project . --board xiao-esp32-c6`.
2. `/spark:idea` leaves the light need unserved, because P355 is open. (E) Look: `parts.py --match`, issue #453.
3. `/spark:idea` offers no pick for the board's own button. (E) Look: `parts.py --match` for an input need.
4. The requirements file for a board-only project is written by hand, because `parts.py` never writes `board_only`. (M) Look: `grep board_only scripts/parts.py` finds nothing.
5. A requirements file with no parts and no `board_only` builds to `????`. (M) Look: `check_spine.py` on it.
6. With `board_only: true` the build exits 0 and writes no sheet, no picture and no page. (M) Look: the `--keep` output.
7. `pins.py` holds `ONBOARD_LED = 15`, `ONBOARD_LED_ON = 0` and `ONBOARD_BUTTON = 9`, and no `ONBOARD_BUTTON_ON`. (M) Look: `firmware/pins.py`.
8. The firmware has to hold the pressed level of B by itself. (M) Look: the record's `onboard_button`, no `active_level`.
9. `import_firmware.py` passes on the first try. (E) Look: its exit code. PWM is in the stand-in (M).
10. `check_all.py --project .` ends with "nothing found by the 1 check(s) that completed, of 5". (M) Look: its last line.
11. The Wokwi run does not happen in the walk, because the PO runs it only rarely. (E) Look: `sim/runs/`. If it is skipped, score 12 as not run.
12. If a scenario runs, its log has a `ready` line and no GPIO15 line. (E) Look: the log.
13. `look.py --no-simulation` matches the XIAO record (chip esp32c6, 4 MB flash) and prints a token. (E) Look: its output.
14. `deploy.py --no-simulation` finishes with `ready seen`, after at most one retry. (E) Look: its envelope, `simulation: none`.
15. The LED lights at the first press, with no inversion. (E) Look: the bench. Level 0 is measured (M) in walk 1.
16. A press of B while the board restarts enters the bootloader once. (E) Look: the bench, the `look.py` output.
17. "Add a second LED" ends with an outside part: a resistor and jumpers. (E) Look: the rebuild's `breadboard.md`. Its sheet for `led-red-5mm` on the XIAO lists them today (M).
18. If 17 holds, the PO has no resistor at hand, and the second LED waits. (E) Look: the walk's diary. If 17 does not hold, score 18 as not run.
19. The rebuild names its bench changes, and at least one is "put R1 in a free row". (E) Look: the rebuild's `changed` lines.
20. The walk has 1 or more steps outside spark (the 0 target is missed). (E) Look: the diary.
21. The walk takes 45 to 90 minutes. (E) Look: the diary's times.

## 3. Score after the walk

Scored by someone who did not write the predictions. A Sonnet 5.5 agent scored them for P400 (#516) on 2026-10-23,
from walk 2's diary and files. The full evidence is in
`docs/observations/2026-10-23-p400-walk2-council/predictions-score.md`. Of 21: 9 held, 3 did not hold, 4 partly held
and 5 were not tested.

| # | held / did not hold | evidence |
| --- | --- | --- |
| 1 | held | Diary 20:54: init wrote every file, and nothing stalled. |
| 2 | partly | `--match` offered no board LED (G7), but the pick gave "light" to the board. |
| 3 | held | G7: `--match` offered neither the board's LED nor its BOOT button. |
| 4 | did not hold | `--requirements` wrote `"board_only": true` (O6). P387 (PR #503) merged after the map. |
| 5 | not tested | The walk's file held `board_only` from the start. |
| 6 | held | Diary 21:28: the build wrote no sheet, no page and no `dist/`. |
| 7 | partly | `pins.py` holds the three names, and also `ONBOARD_BUTTON_ON = 0` (P388). |
| 8 | did not hold | `firmware/light.py` reads `pins.ONBOARD_BUTTON_ON` (O10). P388 (PR #500) merged after the map. |
| 9 | held | Diary 01:15: `import_firmware.py` printed "ok" at the first run. |
| 10 | held | Diary 20:55 and 21:30: vendor-truth passed, and four checks were "not asked for". |
| 11 | did not hold | The Wokwi run happened and passed (diary 01:15), but it pressed no button. |
| 12 | held | The scenario waits only for "ready", and no step reads GPIO15. |
| 13 | held | Diary 06:52: the chip and the flash were "same", with no warnings. |
| 14 | partly | "ready seen" after one refused try (S4), but the log says `simulation: passed`, not `none`. |
| 15 | held | Diary 06:55: the person pressed B and said "Done, it works". |
| 16 | not tested | No diary row has a press of B during a restart. |
| 17 | not tested | Nobody asked for a second LED. |
| 18 | not tested | It depends on 17. |
| 19 | not tested | No rebuild ran. |
| 20 | held | At least three steps ran outside spark (G4, G23, and the GitHub look at 06:44). |
| 21 | partly | Three sittings of 36, 4 and 11 minutes, but the wall clock ran 601 minutes. |

## 4. Gaps and smallest fixes (proposals, not filed)

- The idea step has no way to write a board-only project. Fix: when every need is the board's own part, `parts.py
  --requirements` writes `board_only: true`. Way round: write the file by hand (the build page shows it).
- No pick for the board's own button. P355 covers only the LED. Fix: widen P355 to both, from `pin_roles`.
- The record holds no pressed level for B. Fix: add `active_level` to `onboard_button`, with a bench check and a
  source, as P353 did for the LED. Way round: the firmware reads the level once at start with the button released.
- A board-only build gives the PO no page to read at the wiring step. Fix: one line in the build output and the
  journey page, "nothing to wire, use the board's own B and LED".
- `check_all` reads "nothing found" next to four "not asked for". Fix: for a board-only project, say in one line
  why the four are not asked. Not a pass of five.
- The second LED needs a part the PO can lack. Fix: the idea step asks "do you own a resistor" before it picks
  an outside LED. Way round: use PWM on the same LED for "a second effect".
