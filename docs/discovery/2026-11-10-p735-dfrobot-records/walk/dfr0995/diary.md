# Walk P735: DFR0995 1.47" 172x320 IPS LCD, diary (2026-11-10, 09:30-09:37 CET)

Record: walk/dfr0995/project/parts/dfr0995-lcd-1in47.json
All parts.py calls had `SPARK_HOME=$HOME/.local/share/spark` inline and `--project <project>`.

## Steps
1. `parts.py --drawer`: listed `1.47" 172×320 IPS LCD Display Module  2  -` (no part record linked).
2. `parts.py --need small colour display`: "nothing in the library matches 'small colour display'".
3. `parts.py --kept DFR0995`: "nothing kept matches DFR0995".
4. `parts.py --kept ST7789`: found the sibling record dfr0664-tft-2in's 3 kept documents. used shelf/dfr0664-tft-2in.json as the model for a display record.
5. Read drawer/dfrobot-dfr0995.json: count 2, maker dfrobot, number DFR0995.
6. `parts.py --skeleton dfr0995-lcd-1in47 --kind display --vendor dfrobot`: "wrote …/parts/dfr0995-lcd-1in47.json: every null is a fact to record".
7. WebSearch "DFR0995 1.47" 172x320 IPS LCD wiki.dfrobot.com" (search 1): retailer pages only, no wiki hit. one retailer named the wiki URL.
8. curl https://wiki.dfrobot.com/SKU_DFR0995_1.47inches_IPS_LCD_Display_Module (fetch 1): 200, redirected to https://wiki.dfrobot.com/dfr0995/. spec table, pinout table, 4 downloads (dimension PNG, schematic PDF, STP zip, library zip).
9. Read scripts/spark/sourcing/datasheets.py to learn what `--fetch` downloads (the URLs in `sources` and in fact sources ending .pdf/.jpg/.png/.webp/.svg).
10. Wrote the 5 URLs into `sources`, then `parts.py --fetch dfr0995-lcd-1in47` (fetches 2-5): kept the schematic PDF, dimension PNG, pinout PNG and product JPG. `documents` filled with title/version null.
11. `parts.py --read <schematic.pdf> --want pin_order supply_range_v on_board_pulls`: all three "NOT FOUND", "read those pages as images".
12. pdftoppm on the schematic, then read the image: J1 1 BLK..8 VCC. P1 18-pin GDI. U1 regulator VCC→3V. U3 6-channel buffer. pulls R5, R10, R1/R3. 390R series. MH1, MH2.
13. sips downscale of the dimension PNG (7970x7796), then read: 44.5 x 19.5, Ø2 x2 holes.
14. Read the pinout PNG and the product JPG.
15. curl https://wiki.dfrobot.com/dfr0995/docs/19750 (fetch 6): GDI and SPI wiring tables for the FireBeetle ESP32-E. GDL constructor `DFRobot_ST7789_172x320_HW_SPI`.
16. curl STP zip (fetch 7): DFR0995_3D_3DM.stp, 9.2 MB, 13141 B_SPLINE, 0 CIRCLE, 0 CYLINDRICAL_SURFACE: hole positions cannot be read without CAD. Deleted from scratch.
17. WebSearch "DFRobot GDI General Display Interface 18 pin FPC pitch 0.5mm" (search 2): pointed at product-2073.
18. WebFetch https://www.dfrobot.com/product-2073.html (fetch 8): "Interface: 18PIN (Reverse)", "Pin Pitch: 0.5mm", SKU FIT0682.
19. grep scripts for `gdi_`: no reader, so I kept the GDI pinout out of `facts`.
20. Filled the record (python, json), removed the `sourcing` block and filled the documents' title/version from what each prints.
21. `parts.py --validate`: "dfr0995-lcd-1in47 ok", exit 0.
22. `parts.py --sources dfr0995-lcd-1in47`: 7 x "ok", exit 0.
23. `parts.py --unverified dfr0995-lcd-1in47`: "8 thing(s)" unchecked (output line 1), exit 0.
24. `parts.py --show … | grep conflict`: no CONFLICT lines.

## Bugs
- `--skeleton` writes `"sourcing": []` and `"//sourcing": "… {seller, url, price_czk, checked}…"`, but research.md and the agent rules say no seller listings and no prices. The skeleton asks for what the contract forbids.
- `--unverified` drops my `why_it_matters` for pin_order and prints a generic one ("a pin order read wrong reverses a supply or swaps a signal"), losing the record's specific "VCC on BLK, GND on DC".
- `--fetch` titles a key `61568405ff77f1944899d596020e1af6` (the hash file name of DFRobot's CN image host), a key that tells a reader nothing.
- `--read` on a schematic answers "3 fact(s) not on a table row: read those pages as images" but renders nothing. Rendering it is on the agent (pdftoppm, which spark does not name).

## Gaps in the flow
- research.md does not say how to put a URL into `--fetch`'s reach. I read datasheets.py to learn that `sources` URLs with .pdf/.png/.jpg are fetched.
- `--fetch` cannot keep a .zip (KEEPABLE has no .zip), so DFRobot's STP zip and library zip cannot be kept in the store. The PO's "STEP" has no route.
- No step or tool reads a dimension PNG or an 8000-px drawing. I downscaled it with macOS `sips` by hand.
- The schema reference (part-data.md) is one worked LED. Nothing names the display-kind facts (driver chip, resolution, backlight), so I copied the keys from dfr0664-tft-2in.
- `footprint` is a bare string with no `verified` or source. `pinrow8` silently claims a 2.54 mm pitch DFRobot never publishes, and `--unverified` cannot list it. I put the warning in `host_requirements`.
- A module with two connectors (8-pin header and 18-pin GDI FPC) has one `pin_order`. The second connector has no field.
- The drawer entry points at no part record, and nothing in the flow links the new record back to the drawer entry (no `--drawer-set` step in research.md).
- `--need small colour display` found nothing, though the library holds dfr0664-tft-2in (kind display). Words like "colour"/"screen" do not reach "display"/"TFT", so the reuse step can miss a sibling.
- DFRobot's own texts conflict (spec "Operating Voltage 3.3V" against pinout "VCC DC3.3V-5V". example wiring BLK→13/D7 against code `TFT_BL D4`). The record has no "conflict" marker, only verified:false plus prose.
- `--sources` re-requests every URL (7 requests) on top of the fetch budget. The budget rule does not say whether those count.

## No place in the record
- Product picture: https://dfimg.dfrobot.com/enshop/DFR0995/DFR0995_Main_01_1200x630.jpg (kept, sha256 cdf4ca0f…). The back render with silkscreen is https://img.dfrobot.com.cn/wiki/60c1e008bddfc41c3293de80/61568405ff77f1944899d596020e1af6.png (kept). In `documents` only, with no field saying "this is the picture".
- Schematic: https://dfimg.dfrobot.com/wiki/19389/DFR0995_1-47-inch-display_schematics_V1.0.pdf (kept, V1.0 2022/6/20). It shows: J1 8-pin header. P1 18-pin GDI. U1 regulator VCC→3V (part not named). U3 16-pin 6-channel buffer on 3V (part not named). U2 12-pin panel FPC (GND, LEDK, LEDA, VDD, GND, GND, D/C, CS, SCL, SDA, RES, GND). backlight low-side NPN Q1 via R2 10R, base R3 1k from BLK, R1 10k to VCC. pull-ups R5 10k RES, R10 100k CS. 390R series R4, R6-R9. MH1, MH2 holes. FD1, FD2 fiducials. Cited in facts, but there is no `schematic` field.
- Board outline: 44.5 x 19.5 mm, PCB 1.6 mm, 4.7 mm overall (glass 1.5 above the board), rounded corners. Source: the dimension PNG https://dfimg.dfrobot.com/wiki/19389/DFR0995_1-47-inch-display_dimension_V1.0.png. Only width/height have a field (body_mm). thickness/height has none.
- Display area: active 32.35 x 17.39 mm. glass 33.8 x 19.1 mm, starting 4.4 mm from the left edge. Same PNG. the wiki text says "Display Area 19.1mm×33.8mm".
- Mounting holes: 2, Ø2 mm ("Ø2 x2"), on the long-axis centreline (9.75 mm from either long edge), centres 2 mm from the left edge and 40.5 mm apart (so at x = 2.0 and 42.5 mm). Same PNG.
- Header: 8 pads in one row along a long edge on the back, silkscreen left to right BLK DC RES CS MOSI SCLK GND VCC, J1 pin 1 = BLK (schematic). From the pinout PNG and the schematic. Pitch and positions are not published (see Not found).
- GDI connector: 18-pin FPC, 0.5 mm pitch, reverse cable (https://www.dfrobot.com/product-2073.html, FIT0682 cable page, not the DFR0995 page). Bottom-left of the back, labelled "General Display Interface" (pinout PNG). Pin order from the schematic P1: 1 VCC, 2 BLK, 3 GND, 4 SCLK, 5 MOSI, 6 (MISO position, no net), 7 DC, 8 RES, 9 CS, 10 SDCS, 11 FCS, 12 TCS, 13 SCL, 14 SDA, 15 INT, 16 BUSY/TE, 17 GPIO1 (X), 18 GPIO2 (X). Pins 6 and 10-18 have no net on this module. Read from the image, unverified.
- Panel FPC U2: 12 pins (listed above), soldered under the glass. Schematic only.
- Backlight: "3 White LED Parallel", brightness 600 cd/m² typ, -20..+70 °C (wiki spec table).
- STEP: https://dfimg.dfrobot.com/wiki/19389/DFR0995_1-47-inch-display_stpfile_V1.0.zip (DFR0995_3D_3DM.stp, 2022-06-17, B-spline surfaces only). It cannot be kept (.zip).
- Library: DFRobot_GDL (https://github.com/dfrobot/DFRobot_GDL), class DFRobot_ST7789_172x320_HW_SPI (wiki docs/19750). It is firmware, so it stays out of the record by rule.

## Not found
- Header pitch and pad positions: not on the wiki page, the dimension PNG (top and side views only, no header) or the schematic. The STEP has the geometry, but only as B-splines (no circles to read). The included "1×8 pin header" (retailer search snippets) suggests 2.54 mm, unconfirmed.
- Which long edge the header sits on relative to the holes: the pinout render shows it along the top edge of the back. there is no dimensioned drawing.
- GDI connector position in mm: not dimensioned anywhere.
- Supply current (full screen and peak): not on the wiki or the schematic.
- Part numbers of the regulator U1 and the buffer U3, so no dropout, max input or logic thresholds.
- Header pitch/positions for a KiCad footprint: DFRobot ships no footprint.

## Counts
- Searches: 2 of 8.
- Fetches: 8 of 12 (wiki page, 4 documents via --fetch, example page, STP zip, FIT0682 page), plus 7 URL checks by `--sources`.
- Wall time: about 7 minutes (09:30-09:37 CET).
