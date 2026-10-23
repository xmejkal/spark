# P400: walk 2's predictions, scored (P378)

> Of 21 predictions: 9 hit, 3 miss, 4 partly and 5 not tested.
> Predictions 4, 7 and 8 went stale. Two fixes (P388, P387) merged on 2026-10-22 after the map and before the walk.
> The map named 1 of the walk's 4 stalls. The Wokwi run it ruled out did happen, and that run pressed no button.

Scored by a scorer who did not write them (Sonnet 5.5, 2026-10-23). The predictions are in
`docs/discovery/2026-10-22-p378-walk2/predictions.md`. Its section 3 holds an empty score table, and this page does not fill it.
The evidence is walk 2's diary and the files in `/Users/petr/Development/spark-walks/walk2`. All times are Prague time.
Verdicts: hit, miss, partly, not tested. The mark is the page's own: M means measured, E means expected.

## The score

| # | mark | verdict | evidence |
| --- | --- | --- | --- |
| 1 | M | hit | Diary 20:54: `init_project.py --board xiao-esp32-c6` wrote every file, and the stalls column reads "None". All seven files it names are in the folder. |
| 2 | E | partly | `--match` offered no board LED (G7), so the gap held. But the person picked the board for "light" at 21:13, and `.spark/needs.json:15-25` shows it served. |
| 3 | E | hit | G7: `--match` offered neither the board's LED nor its BOOT button. The press need reached the board only by a pick (`.spark/needs.json:4-14`). |
| 4 | M | miss | `requirements.json:4` holds `"board_only": true`, and `--requirements` wrote it (diary 21:13, O6). P387 (PR #503, merged 2026-10-22 16:08) added that after the map. |
| 5 | M | not tested | The walk's file held `board_only` from the start, so no build ran without it. |
| 6 | M | hit | Diary 21:28: the build wrote no sheet, no page and no `dist/`. The folder holds none of them and no picture. The exit code is not in the diary. |
| 7 | M | partly | `firmware/pins.py` lines 4 to 6 hold `ONBOARD_LED = 15`, `ONBOARD_LED_ON = 0` and `ONBOARD_BUTTON = 9`. But line 7 holds `ONBOARD_BUTTON_ON = 0`. |
| 8 | M | miss | `firmware/light.py:30` reads `pins.ONBOARD_BUTTON_ON` (O10). P388 (PR #500, merged 2026-10-22 14:14) gave the board record a button `active_level` after the map. |
| 9 | E | hit | Diary 01:15: `import_firmware.py` imported `light` and `pins` and printed "ok". The diary logs one run, with no retry and no stall. |
| 10 | M | hit | Diary 20:55 and 21:30: vendor-truth passed and four checks read "not asked for" (G1, G22). The exact words of the last line are not in the diary: not checked. |
| 11 | E | miss | The run happened. Diary 01:15: `run_scenario.py` ran once and passed 8 seconds later. `sim/runs/the-firmware-starts.log:2` reads "verdict: passed". |
| 12 | E | hit | The log has `ready` at line 33. The scenario has one step, `wait-serial: "ready"` (scenario line 10), and none reads GPIO15. GPIO15 appears only in a comment (log line 10). |
| 13 | E | hit | Diary 06:52: chip ESP32-C6 and 4 MB flash both read "same", with no warnings and token `ae7b-b637`. The look also said "simulation: passed" (O12). |
| 14 | E | partly | `ready seen` is at `sim/runs/board/2026-10-23T06-55-29.log:5`, after one refused try (S4: exit 2, no terminal). But line 3 reads `simulation: passed`, not `none`. |
| 15 | E | hit | Diary 06:55: the person pressed B and said "Done, it works". The diary does not count presses. The board log stops at "LED off" (lines 10 and 11), before the press. |
| 16 | E | not tested | No diary row records a press of B during a restart. The recorded press came after the deploy ended. |
| 17 | E | not tested | The walk stopped after step 11. Nobody asked for a second LED, and the folder has no `breadboard.md`. |
| 18 | E | not tested | It depends on 17. No second LED was asked for, so no resistor question came up. |
| 19 | E | not tested | No rebuild ran, so no `changed` line exists. |
| 20 | E | hit | At least three steps ran outside spark. The brief was edited by hand (21:05, 21:13, G4). Claude wrote a Mac button test (01:12, G23). A GitHub look at Wokwi's part followed (06:44). |
| 21 | E | partly | The diary logs start times only. Its three sittings run 36, 4 and 11 minutes (51 in all), which fits 45 to 90. The wall clock runs 601 minutes, 20:54 to 06:55. |

## What the misses teach

About the predictions:

- A measure goes stale. Predictions 4, 7 and 8 were true when the map merged (PR #496, 2026-10-22 13:37). At that commit,
  `scripts/parts.py` held 0 `board_only` and the XIAO record held 1 `active_level`. Now they hold 3 and 2
  (`git show 0ffbcbf:...` and `grep -c`). The (M) mark did not help: 3 of the 7 (M) predictions hit, and 6 of the 14 (E)
  predictions hit.
- Two fixes merged after that and before the walk began at 20:54. P388 (PR #500, 14:14) gave the button an
  `active_level`. P387 (PR #503, 16:08) made `--requirements` write `board_only`.
- Two proposals in section 4 of the page match these two fixes. Whether the cards came from the page is not checked.
  The stale predictions are good news for spark.
- Next map: write the commit hash beside each (M), and run the (M) looks again just before the walk.
- The map named 1 of the walk's 4 stalls. S4, the yes in the person's own terminal, is in step 10.
- Three stalls were not named. S1 is the brief that does not reach idea (G6). S2 is the XIAO held by reaction-game.
  S3 is Wokwi's part with no button.
- Walk 1 already showed a hold on the XIAO (`docs/observations/2026-10-19-p326-walk1.md:34`). Every look in the map was
  a spark script for one project. Add a look at the drawer's holds and one at the simulator's part file.
- Five predictions are not tested (5, 16, 17, 18, 19). The walk stopped after step 11. The second LED, the rebuild and
  the second deploy stay unmeasured.
- A time claim needs an end row and a rule for breaks. The walk ran in three sittings, so prediction 21 is only partly
  scored.

About spark:

- Prediction 11 is the miss that teaches most. The scenario tests only the start
  (`sim/scenarios/the-firmware-starts.scenario.yaml:4`). Yet the look and the deploy report "simulation: passed"
  (O12, G23). Idea I5, each scenario names the must line it tests, is a comment on P345 (#440).
- Prediction 3 held. P355 (#453) is still open, and its title names only the LED (read 2026-10-23, comments not
  checked). The map proposed to widen it to the button.
- Predictions 7 and 8 show that P388 works. `pins.py` holds the level, and the firmware reads it (O10). One more step 4
  claim still holds. `pins.py` has no pull-up line, so `firmware/light.py:24` sets `Pin.PULL_UP` itself.
- A true (M) fact is not always a stall. The map said no serial monitor is wired (step 7). The build warned (G18),
  but the run heard `ready` anyway (log line 33).
