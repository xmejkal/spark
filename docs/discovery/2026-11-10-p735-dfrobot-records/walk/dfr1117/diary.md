# Walk P735: DFR1117 Beetle ESP32-C6 Mini, diary (2026-11-10, 09:30 to about 10:00 CET)

Record: `project/boards/beetle-esp32-c6.json` (a board definition, not `parts/<id>.json`). The project is `$P` = `.../scratchpad/walk/dfr1117/project`. Every spark command ran with `SPARK_HOME=$HOME/.local/share/spark`.

## Steps
1. Read `commands/research.md`, `part-data.md`, `boards/README.md`, `boards/xiao-esp32-c6.json`, how-it-works "Your own dev board". Research.md has no word about boards.
2. `ls ~/.local/share/spark/boards/` returned `34-85-18-xx-xx-xx.json` and others: per-MAC deploy history, not board definitions.
3. `parts.py --need tiny ESP32-C6 board battery --project $P` returned "nothing in the library matches 'tiny ESP32-C6 board battery'".
4. `parts.py --kept DFR1117` and `--kept Beetle ESP32 C6` both returned "nothing kept matches …".
5. `parts.py --need ESP32-C6 --project $P` returned "nothing in the library matches 'ESP32-C6'", although library `boards/xiao-esp32-c6.json` is an ESP32-C6 board.
6. WebSearch "DFR1117 Beetle ESP32-C6 Mini wiki.dfrobot.com": only distributors came back, and the wiki URL was guessed: https://wiki.dfrobot.com/SKU_DFR1117_Beetle_ESP32_C6.
7. WebFetch on the wiki returned the specs and the doc links: schematic zip, dimension png, layout zip, datasheet zip. It also gave the V1.0/V1.1 differences, the LED on IO15 and BOOT on IO9.
8. `curl` downloaded the wiki HTML, the schematic zip, the dimension png, the datasheet zip and the pin diagram: all 200.
9. `parts.py --keep <file> --url <url> --project $P` ran ×7 (dimension, schematic zip, wiki HTML, pin diagram, datasheet zip, variant header, layout zip). Each printed a documents entry `{url, sha256, file, retrieved, title:null, version:null}`, exit 0.
10. `parts.py --read DFR1117-Schematics-V1.1.pdf --want charge_current_a regulator battery_input` returned "NOT FOUND ×3 … read those pages as images". I rendered the PDF with pdftoppm and read it as images.
11. `parts.py --read "TPS62A02DRLR Chip Datasheet.pdf" --want output_current_a …` returned "FOUND p4:40 [7.3 Recommended Operating Conditions] IOUT … TPS62A02 | 0 | 2 | A".
12. `parts.py --read "RT9080 Chip Datasheet.pdf" --want output_current_a` returned "LABEL ONLY p1:9 … up to 600mA of output current".
13. `parts.py --kept esp32-c6 datasheet` found the kept esp32-c6-datasheet-v1-5 (cited by xiao-esp32-c6), which I reused without a fetch.
14. `gh api repos/espressif/arduino-esp32/contents/variants` showed that `dfrobot_beetle_esp32c6` exists. I fetched its `pins_arduino.h` at tag 3.3.12 and kept it.
15. Downloaded the layout zip, which turned out to be DFRobot's KiCad footprint `Beetle ESP32-C6.kicad_mod` and symbol `beetle_esp32-c6.kicad_sym`.
16. Wrote `$P/boards/beetle-esp32-c6.json` by hand, modelled on the xiao and FireBeetle records.
17. `init_project.py --project $P --board beetle-esp32-c6` wrote active.json, .spark/, AGENTS.md and the CLAUDE files. It named 5 fields with no answer (goal, prefer, sellers, two physics fields), exit 0.
18. `boards.py --validate --project $P` returned "active beetle-esp32-c6 (project): ok".
19. `boards.py --validate --for-fab --project $P` returned "physical.footprint_module is not set: no verified footprint …". This is as intended.
20. `emit_footprint.py --board beetle-esp32-c6 --project $P` printed the tscircuit footprint, "holes are 1.00 mm, NOT the 0.9 mm on the vendor drawing", exit 0.
21. `check_vendor_pins.py $P/boards/beetle-esp32-c6.json` returned "MISMATCH (8 pins against … dfrobot_beetle_esp32c6/pins_arduino.h)", with one line per bare-number label ("vendor's header defines no pin called '4'"), exit 1.
22. `parts.py --validate --project $P` listed only parts records. It does not check the board.
23. `parts.py --unverified beetle-esp32-c6 --project $P` returned "parts.py: no part called 'beetle-esp32-c6'".
24. `parts.py --sources beetle-esp32-c6 --project $P` returned the same "no part called".
25. `boards.py --resolve --project $P` wrote `.spark/board.json`.

## Bugs
- `parts.py --need ESP32-C6` returned "nothing in the library matches", but the library ships `xiao-esp32-c6`, a tiny ESP32-C6 board with a charger. `--need` never searches boards, so reuse-first cannot find one.
- `parts.py --unverified <board>` and `--sources <board>` return "no part called …". Research step 4 has no board equivalent, and `boards.py` has no `--unverified` or `--sources`. A board's unconfirmed list cannot be printed.
- `check_vendor_pins.py` returns MISMATCH with exit 1 for a board whose silkscreen prints bare GPIO numbers (4, 5, 23 …). The variant header defines only LED_BUILTIN/TX/RX/SDA/SCL/SS/MOSI/MISO/SCK, so no label matches. The message asks for a comment. I did not test whether a `//pins` comment clears it (it already says "The silkscreen prints the GPIO number itself").
- `boards.py --validate` passes a stand-in board (`wokwi_is_stand_in: true`) that has no `documents["wokwi-board"]` and no `wokwi_power_pins`. boards/README says a stand-in's entry cites the stand-in's file. The rule is not enforced.

## Gaps in the flow
- research.md covers parts only: kinds indicator, button, connector, regulator and module, with records at `parts/<id>.json`. It does not cover a dev board. The board flow lives in boards/README.md (steps name a Makefile, config.py and `make check`) and in how-it-works "Your own dev board" ("copy the closest definition"). Neither tells you how to research one.
- research.md's `allowed-tools` lists no `boards.py`, `init_project.py`, `emit_footprint.py` or `check_vendor_pins.py`.
- `parts.py --skeleton` has no board kind. I copied the board record's shape from xiao and FireBeetle. I guessed three fields: `mounting_holes` `{count: 0}`, `corner_radius_mm`, and `flush_edge "+y"` as the end away from the USB-C.
- The `boards/` in the store holds per-MAC deploy history (`34-85-18-xx-xx-xx.json`), not definitions. The name suggests the second.
- `--fetch` works only from a parts record's documents. For a board I had to curl and then `--keep`, which needs a hand-made scratch dir.
- DFRobot ships documents as zips (schematic, datasheets, layout). `--keep` keeps the zip, because its sha256 matches the URL. `--read` needs a PDF, so a cite has to name "zip → inner file, page" by hand. No command reads inside a kept zip.
- `parts.py --read` cannot read a schematic, which has no table rows. Schematics must be rendered and read as images, and no spark command does that.
- A board record has no per-fact `verified` for physical facts, header_order or pins. A `//` note is the only place to say "read from the V1.0 footprint, unverified for V1.1". There is no `pin_order_proof` equivalent for `header_order`.
- No place to say which hardware revision a record holds for. FireBeetle has a `hardware_revisions` key, but no doc in the flow names it.
- `parts.py --keep` printed `title: null, version: null`. I typed the documents entries into the board file by hand. No command writes them into a board record.
- With numeric pin keys ("4": 4), the validator accepts them, since SELECTOR_SAFE allows digits only. Whether `pins.py`/firmware names survive a key that starts with a digit was NOT tested.
- `micropython_port` is left out (no source read). The validator does not ask for it. The likely build is `ESP32_GENERIC_C6`, but that is unverified.

## No place in the record
- Product picture: https://dfimg.dfrobot.com/enshop/image/data/DFR1117/DFR1117-260910%20(1)_1200x630.jpg.webp (from the wiki HTML's og:image).
- What the schematic shows (both PDFs in https://dfimg.dfrobot.com/wiki/19405/DFR1117_beetle-esp32-c6_schematics_V1.1.zip): one A4 sheet per revision.
  - ESP32-C6-FH4 with a 40 MHz crystal and a PCB antenna.
  - USB-C U6 with 5.1K CC pull-downs.
  - TP4057 charger, PROG 2K, charge LED4 'C' with 2.7K.
  - Battery divider 1M/1M to IO0.
  - Power path: VUSB through 1N5819W, BAT through the AO3407 P-FET.
  - Regulator: RT9080 (V1.0) or TPS62A02 with 1 µH (V1.1).
  - BOOT S1 on IO9, RST S2, LED1 on IO15, headers P3 and P4.
  - Test pads T1 IO15, T2 IO3, T3 USB_N, T4 USB_P. Fiducials FD7, FD8.
- Header hole positions from DFRobot's footprint (layout zip, KiCad mm, origin at the board's corner away from the USB-C, y negative toward the USB): left column x=1.345, pads 1-8 at y=-22.34, -19.80, -17.26, -14.72, -12.18, -9.64, -7.10, -4.56 = GND, 3V3, 4, 5, 23, 22, 21, 7. Right column x=19.125, pads 9-16 at y=-4.56 … -22.34 = 6, 20, 19, 16, 17, VIN, GND, BAT. Drill 0.9, pad Ø1.8, round. The columns are centred at x=10.235, not 10.25 (0.015 mm off). spark's emitter centres them.
- Which edge: the headers run along both long edges (25 mm). The USB-C sits at a 20.5 mm edge, between the B and R buttons (https://dfimg.dfrobot.com/wiki/19405/DFR1117_beetle-esp32-c6_dimension_V1.0.png).
- USB-C: a 16-pin USB 2.0 receptacle (A1/A4/A5/A6/A7/A8/A9/A12, B1/B4/B5/B6/B7/B8/B9/B12, shell), CC1 R19 and CC2 R21 at 5.1K to GND, D+/D- through 22 R to GPIO13/12 (schematic). Its part number, pitch and overhang are not given.
- Charge LED behaviour: off when not plugged in or fully charged, on while charging, blinking when no battery is connected (wiki).
- VIN is the USB VBUS net directly (schematic P4 pin 3 = VUSB). Feeding VIN with USB plugged in back-feeds the host. Spark prints only `host_requirements`, and a board record has none, so this warning sits in a `//` note that nothing prints.
- Back-side pads "3" and "15" (pin diagram, back view) = T2 IO3 and T1 IO15. The wiki's "13 IOs" = 11 header + these 2.
- Revision markers: schematic V1.0 2024-01-17 and V1.1 2024-12-06. The back silkscreen prints "Beetle ESP32-C6 V1.0.0" (pin diagram).
- Datasheet zip contents: ESP32-C6, RT9080 and TPS62A02DRLR datasheets (https://dfimg.dfrobot.com/wiki/19405/DFR1117_beetle-esp32-c6_datasheet_V1.0.zip).

## Not found
- STEP / 3D model: the wiki HTML has an empty `stpFiles` slot (`draftName:"DFR1117_beetle-esp32-c6_stpfile_", fileUrl:a`), so DFRobot publishes none.
- Battery JST connector: none on the board. The battery goes on the BAT/GND header pads (schematic P4, footprint, drawing), so there is no type, pin count or pitch to give.
- Mounting holes: none (footprint, drawing). Recorded as `mounting_holes.count: 0`.
- Board thickness and component height: not in the wiki, drawing or footprint.
- Which revision the PO's three boards are: needs a photo of the back.
- That V1.1 kept the V1.0 layout/footprint: only a V1.0 layout is published.
- The USB-C part number and its overhang past the board edge: the drawing shows the receptacle inside the outline. Not dimensioned.

## Counts
- Searches: 1 of 8.
- Fetches: 10 of 12 (WebFetch wiki 1, curl 5, gh api variants 1, curl variant header 1, curl layout zip 1, check_vendor_pins' own gh fetch 1).
- Wall time: about 30 min.
