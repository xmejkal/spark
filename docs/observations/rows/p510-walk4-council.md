# Walk 4: gap rows (P510 council)

The gaps of spark walk 4 (card P509 #704, epic #467), on 2026-11-01 in Prague, from 19:16 to 21:58 CET. The diary is `~/Development/spark-walks/walk4/walk4-diary.md`, and it is whole in the first comment of P510 (#705). Spark was main at `8595309b`. Each claim is the first sentence or two of the diary's gap. Status `raised` means that nobody checked it after the walk. The column "where it went" names a proposed card below (C1 to C11), or "row only". No card is filed: a council replans them, as P480 did for walk 3.

## Short version

> The walk reached both goals on the bench: the button changed the LED's effect in Wokwi and on the board, and then a GDI display replaced the LED and ran 10 games. Spark carried the first goal end to end. The display went around spark at 4 points: the part's removal, the GDI pins, a build defect and the deploy of a native driver.

The top card is C1, a build defect: no SPI part can be built on the FireBeetle 2 today. The person said `we definitelly should fix this`. Next comes C2, a module on a fixed connector such as GDI. Then C6, an automatic deploy with no terminal step and no buttons, the person's I3. The speed work on the games ran the ladder of P336 (#430) on the bench: framebuf and SPI in Python reached 1 to 13 frames per second in play, and a firmware build with the s3lcd C driver ran smoothly. So P336's order holds, and C8 is what spark lacks to carry the last rung.

## Rows

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The idea page reads the brief from `.spark/project.json`, which `/spark:init` writes, in step S, but it runs `/spark:init` only in step L. | diary G1, step 1 | raised | C5 |
| 2 | The `--needs-set` dry run names each field it sets, but not the file it writes or whether it lists the project. | diary G2, step 1 | raised | C5 |
| 3 | Walk 3 ended, but its hold on a FireBeetle 2 stays. When a project ends, no spark step frees its holds. | diary G3, step 2 | raised | C4 |
| 4 | The refusal does not say which of the 2 owned boards is on USB. A hold counts pieces, not boards by MAC. | diary G4, step 2 | raised | C4 |
| 5 | `--match` lists `xiao-esp32-c6-fresh (button-light)` for all 3 needs with no word on what it is. | diary G5, step 2, open since walk 2 G8 | raised | row only |
| 6 | The refused pick offers 2 fixes, free a hold or pick another part, but not the third, raise the owned count. | diary G6, step 3 | raised | C4 |
| 7 | `parts.py --drawer` prints labels, counts and holds, but not the entry keys that `--drawer-set` needs. | diary G7, step 3 | raised | C4 |
| 8 | `check_all.py` still calls the 4 skipped checks `not asked for`. The real cause is that nothing is built yet. | diary G8, step 5, open since walk 2 G1 | raised | row only |
| 9 | The goal that the person gave at the start did not reach the brief. | diary G9, step 5 | raised | C5 |
| 10 | The stages disagree about the Wokwi run: `--match` and `--pick` said that no scenario can press the button, and the build wired a stand-in that a scenario pressed. | diary G10, step 6 | raised | C7 |
| 11 | The build's verdict ends with no next step, so a new user does not know that the firmware comes next. | diary G11, step 7 | raised | C5 |
| 12 | `run_scenario.py` has no dry run of its free checks. | diary G12, step 8 | raised | C9 |
| 13 | Spark has no command that presses a button or reads the LED on the Mac. | diary G13, step 8, open since walk 3 G31 | raised | C9 |
| 14 | The editor flags MicroPython's names as unknown in every firmware file. | diary G14, step 8, near walk 3 G21 | raised | C9 |
| 15 | The look still cannot read this board without the person's hands on BOOT and RESET. | diary G15, step 10 | raised | C6 |
| 16 | The doctor's 2 s of console silence does not tell a running firmware from a board that does not answer. | diary G16, step 10, open since walk 3 G16 | raised | C6 |
| 17 | The look lists a must line about the order of the work as untested. Spark cannot mark a must line that no scenario can test. | diary G17, step 11 | raised | C7 |
| 18 | The person's bench result lives only in the conversation and the diary. | diary G18, step 14, open since walk 3 G37 | raised | C7 |
| 19 | The need's condition `plugs into the board's GDI connector` changed nothing in `--match`. | diary G19, step 15 | raised | C2 |
| 20 | Spark knows nothing about the FireBeetle 2's GDI connector. The board record and the `parts/` library never name GDI. | diary G20, step 15 | raised | C2 |
| 21 | The 4 owned displays are drawer entries with labels only, so adding a module starts with `/spark:research` and the web. | diary G21, step 15 | raised | row only |
| 22 | On this board, the GDI backlight pin and the onboard LED are the same GPIO21, and no record said so. | diary G22, step 17 | raised | C2 |
| 23 | Spark has no way to say that a module plugs into a fixed connector. | diary G23, step 17 | raised | C2 |
| 24 | The library board record does not name its GDI connector P2 or its camera connector P1. | diary G24, step 17 | raised | C2 |
| 25 | Wokwi has no part for the display's ST7789 at 240x320, so the display is tested only on the board. | diary G25, step 17 | raised | C7 |
| 26 | Spark cannot drop a part from a project: `--pick . light=` is refused, and no flag removes a need. | diary G26, step 18 | raised | C3 |
| 27 | Spark's pin map for the display disagrees with the GDI cable on 5 of 8 signals, and `requirements.json` cannot pin a part's signals. | diary G27, step 18 | raised | C2 |
| 28 | The pick and the requirements said nothing about the display's `simulation` skip. | diary G28, step 18 | raised | C7 |
| 29 | The first build of a SPI part on the FireBeetle 2 breaks: `board.tsx` traces to `MOSI` and `MISO`, and the footprint names those pads `MO` and `MI` from `pad_aliases`. | diary G29, step 19 | raised | C1 |
| 30 | The build's verdict and its `--json` say `source_trace_not_connected_error` with no trace named. | diary G30, step 19 | raised | C1 |
| 31 | After the light need left, `pins.py` still names `ONBOARD_LED`, so the old LED firmware still imports. | diary G31, step 20 | raised | C3 |
| 32 | Spark's `framebuf` stand-in sits in `scripts/stand_in/fallback/`, apart from `machine`. | diary G32, step 20 | raised | C9 |
| 33 | With `--no-simulation`, the look listed no limits and no unnamed must lines, though nothing tested the display's must line. | diary G33, step 21 | raised | C7 |
| 34 | The board record knows GPIO0 as the BOOT pin only in a strapping note, so `pins.py` has no name for the second button. | diary G34, step 23 | raised | C10 |
| 35 | After a deploy, spark keeps only the console lines of its short read. No spark step records a later line. | diary G35, step 31 | raised | C6 |
| 36 | A look can leave the board out of download mode, so deploy.py's own look fails. | diary G36, step 37 | raised | C6 |
| 37 | The N16R8's 8 MB of PSRAM stays off, because the record names one `micropython_port` for both SKUs. | diary G37, step 39 | raised | C8 |
| 38 | `flash_image.py --micropython` takes an outside interpreter silently, and only the look's refusal names spark's own way, the project's tools list. | diary G38, step 40 | raised | C8 |
| 39 | The look does not say which MicroPython build the image holds. | diary G39, step 42 | raised | C8 |
| 40 | With the PSRAM build, deploy.py ended in `ready unknown` 3 times, because the port came back late. | diary G40, step 43 | raised | C6 |
| 41 | P472 found how to enter download mode with no hands. The look and deploy.py still ask for BOOT and RESET, 11 presses in this walk. | diary G41, step 54 | raised | C6 |
| 42 | `flash_image.py` refuses an image whose partition table declares its own `vfs` (s3lcd's 14 MB), so spark cannot carry a native driver build. | diary G42, step 57 | raised | C8 |
| 43 | Spark's Mac stand-ins know no C driver module, so `import s3lcd` must sit inside a function. | diary G43, step 57 | raised | C9 |
| 44 | The s3lcd build reports a fixed USB serial, not the MAC, and spark finds the board by its MAC. | diary G44, step 58 | raised | C8 |
| 45 | With the s3lcd build, the USB port goes away at the driver's start. Then spark cannot read the board back. | diary G45, step 59 | raised | C8 |
| 46 | The s3lcd image went on the board outside spark, so the store record does not know what runs on the board. | diary G46, step 62 | raised | C8 |

## Ideas and asks

1. I1 (steps 3 and 4), the person: `there should be test options or presets or something` and `to be able to test from clean or weith already having it etc`. Goes to C4.
2. I2 (step 32): native drivers run inside a custom MicroPython image. Goes to C8 and C11.
3. I3 (step 54), the person: `change the system so that there's also an option to do all yourself without me having to switch to the other terminal and paste things ? And deally also without pressing the buttons on the board ... I wantto be able to keep this half manual way, but the fully automatic would be great`. Goes to C6.
4. A1 (step 9), the person: `Iwant to test adding a GDI display and displaying something, to test the whole module adding scenario`. Done in the walk, and it found C1 and C2.

## Proposed cards

1. C1, bug, the person's words: `we definitelly should fix this`. The board emitter traces SPI signals by the pin name (`MOSI`, `MISO`). The FireBeetle 2's footprint names those pads `MO` and `MI` in `physical.pad_aliases`. So no SPI part builds on this board. The fix reads `pad_aliases` in the emitter, as `assign_pins.py` and `breadboard.py` do. The verdict names the trace that did not connect (G30). It is done at the point that a project with `dfr0664-tft-2in` builds end to end on the FireBeetle 2.
2. C2, a module on a fixed connector. The board record names its connectors: GDI P2 with 18 pins and camera P1 with 24 pins, each pin with its signal and GPIO. It names the GPIOs they share: GDI BL with the onboard LED on GPIO21, and GDI with the camera on IO1, IO2 and IO7. A part record says that it plugs into one (`dfr0664-tft-2in` into GDI). The requirements can pin a part through the connector, `assign_pins.py` honors it, and the pick warns about a shared pin. A need's condition is read or said to be ignored (G19). This is the "GDI plug" fact of the PO's 2026-10-31 words, and it fits P464's missing-fact result. From G19, G20, G22, G23, G24 and G27, with the pin tables in the diary.
3. C3, remove a part. A command drops a need or a pick, with a dry run, and releases its hold. A board's own part can leave the circuit while it stays on the board, so `pins.py` stops naming it, or marks it unused. The build or the import test then names firmware that still uses it. From G26 and G31.
4. C4, walk presets and holds. A test preset starts a walk from a known store: clean, or with a free board, as the person asked (I1). A project that ends frees its holds. A refused pick also offers to raise the owned count. `--drawer` prints the entry keys. A hold can name a board by MAC. From I1, G3, G4, G6 and G7.
5. C5, the first steps for a new user. The idea run writes the goal into the brief from the start, or init runs first, so the brief is not empty at step S. The build's verdict names the next step: the firmware, which the conversation writes. The `--needs-set` dry run names the file it writes. From G1, G2, G9 and G11.
6. C6, an automatic mode beside the half-manual one, the person's I3. One standing yes in the person's terminal covers every deploy of the project for N minutes. It also covers an image with no simulation. The half-manual way stays. The look and deploy.py enter download mode with no hands by `machine.bootloader()`, as P472 found, and start the firmware with `--after watchdog-reset`. deploy.py waits for a slow port before it says `ready unknown`. A watch step keeps later console lines in the board log. This is close to P469 (#637), in flight. From I3, G15, G16, G35, G36, G40 and G41.
7. C7, one honest word about what a run tests. `--match`, `--pick` and the build say the same thing about the Wokwi stand-ins. The pick names a part's `simulation` skip. A must line that no run can test (an order of work) can be marked so. A bench result for a must line has a place in the store. The look with `--no-simulation` lists the must lines and limits too. From G10, G17, G18, G25, G28 and G33. G18 is walk 3's G37, still open.
8. C8, the project's own MicroPython build. The board record names the PSRAM build for the N16R8 SKU (`ESP32_GENERIC_S3-SPIRAM_OCT`), or asks which SKU it is. The look and the board log name the interpreter that the image holds. `flash_image.py --micropython` says that the build is not the tools list's, or points to `tools.py --new`. `flash_image.py` sizes the file system to the `vfs` that the image declares, so a native driver build (s3lcd) can be carried. If a build reports a fixed USB serial, the look and deploy.py find the board by another fact than the MAC. They also say that the firmware took the USB port away. A flash outside spark leaves a trace or a warning. This is the last rung of P336 (#430). From I2, G37, G38, G39, G42, G44, G45 and G46.
9. C9, free firmware tests on the Mac. A command presses a pin and reads a pin or a PWM duty. All stand-ins sit in one documented place, with a way to stand in for a C module such as `s3lcd`. Type stubs quiet the editor. `run_scenario.py` runs only its free checks with a dry run. From G12, G13, G14, G32 and G43. It extends walk 3's C8.
10. C10, the BOOT button as a second onboard button. The FireBeetle 2 record names GPIO0's button with its level and its bootloader caveat, so `pins.py` names `ONBOARD_BUTTON_BOOT` and `--match` offers it. From G34.
11. C11, a card of its own, the person's words at 21:58 and 22:00: `just out of curiosity I still want to continue on this c driver` and `this c driver game tuning let's put into another separate card, so I can work on it before we go on, after the gaps and findings have beeen triaged`. Order: after the council triaged walk 4 and refined its cards on top of the backlog, before the next spark card. The work lives in its own project outside spark, with the 10 games and a fork of s3lcd (MIT). Its goals: double buffering, where Python draws while DMA sends through `esp_lcd`'s done callback. Tearing sync on the GDI's BUSY-TE pin (IO14), for the blink. Hardware scrolling with MV off for the strip (ST7789V2 datasheet p.211). Game frames with no garbage, for the freezes. A USB console that stays alive, so that spark can read the board. It builds with the ESP-IDF that the person says is installed. A research step comes first: the current s3lcd forks, the ESP-IDF version for MicroPython v1.29, and who did double buffering or tearing sync with `esp_lcd`. Its findings return to C8 and P336 (#430). Spark exports facts, never drivers, so the driver stays a third-party build that spark pins and carries.

## Compared with the board

An agent compared C1 to C11 with the open cards and with walk 3's replan (P480) at 22:05. Claude checked that each card named here exists with that title. Its notes are `walk4-compare-notes.md`. Six of the 11 cards extend an open card, so the council can merge them rather than file new ones.

1. C1 is new. No open card holds the `pad_aliases` defect.
2. C2 extends P460 (#628), the open spike on the GDI and camera connectors. The walk's pin tables, G22 and G27 go there, and P460's line "after the FireBeetle walk" is now stale.
3. C3 is new.
4. C4 extends P466 (#634) for G3, G4 and maybe I1. G6 and G7 have no card.
5. C5 is mostly new. P488 (#667) touches G2.
6. C6 extends P469 (#637) for the look and deploy parts (G15, G16, G36, G41). P469's "done when" does not name `machine.bootloader()` yet. The one standing yes (I3) is new.
7. C7 extends P490 (#669) for G18 and P409 (#535) for G25. G17 and G33 are new.
8. C8 extends P336 (#430) for G42, G44 and G45, and P349 (#445) for G37, G38 and G39.
9. C9 extends P492 (#671) and P399 (#515) for G12. The agent was unsure of the home for G13, G32 and G43.
10. C10 is a small new story, near P467 (#635).
11. C11 is new and lives outside spark. It returns its findings to P336 (#430).

Rows open since earlier walks: G8 sits in P118 (#52), and G18 in P490 (#669). G5, G13 and G16 have no card yet.

## Analysis

The walk changed three journeys. Adding a module now has a known shape: research writes the record, then the pick, the requirements and the build. It broke at the build (C1) and could not express a connector (C2). Removing a part is a new journey, and spark has no step for it (C3). Changing only the firmware ran many times: rebuild the image, look, typed yes, deploy. Each round cost the person a terminal paste and the buttons, which is the cost that I3 and C6 remove.

The walk also showed what spark did well. The board record's facts were right: the LED and button levels, the pins, the BOOT strap note and the SKU note on PSRAM. The look's refusal of an image with an unlisted interpreter led to spark's own tools list way. The gate in deploy.py held every time. The board doctor named a missing board clearly (O6).

Some gaps repeat from walks 2 and 3: G5, G8, G13, G16 and G18. The council can ask why they stay open, and whether a row that waits three walks needs a card or a "won't fix".

The firmware work showed a limit that spark must not hide. Pure MicroPython drawing on this display reached 1 to 13 frames per second in play, and a C driver ran smoothly. Spark's principle stays: it exports facts, never behaviour, so it never writes the driver. But it must carry a pinned third-party image with a driver, and C8 is that step.
