# Round 0 runner's report — FireBeetle 2 ESP32-C6 (DFR1075) as documented (2026-10-09 18:15–18:29; saved by the controller from the agent's returned text, paths shortened)

## Summary
- Steps 1–4 pass on the final file: `boards.py --validate` and `--for-fab` exit 0, `emit_footprint.py` exits 0, `check_vendor_pins.py` exits 0.
- Step 5 stops at simulation, exit 1: board, schematic, footprint and build `[ok]`; the Wokwi stand-in (board-esp32-c6-devkitc-1) has no GPIO14 and the assigner put the LED on D3 = GPIO14. No document says how to state that a stand-in lacks a pin (G0.6).
- Spark's checks missed a pad merge (G0.3): a file whose pads were named by bare GPIO numbers passed validate, `--for-fab` and the footprint; the build joined 3V3 to the pad printed "17" (RX) and GND1 to "15" (the LED); the chain reported only an unrelated open terminal.
- A spark tool wrote into the plugin folder (G0.7): live `check_vendor_pins.py` created `<plugin>/.spark/cache/dfrobot_firebeetle2_esp32c6.pins_arduino.h` (untracked, not ignored) despite SPARK_HOME and HOME redirected; `--offline` later read it. The real store untouched; the scratch store stayed empty.
- Wall time 14 minutes. `init_project.py` not needed: the chain ran without `.spark/` or `package.json`, using the bin's tscircuit through PATH.

## Diary (time order; R = the scratch round0 folder; every spark command from R/project with SPARK_HOME, HOME, TMPDIR inside R)
- 18:15 Reading README, how-it-works, boards/README, commands.md, the S3 and XIAO board files, five --help runs (all exit 0). Expected a schema for `physical`; none (G0.2).
- 18:16 F1 the pin map: `gh api` on `espressif/arduino-esp32 variants/dfrobot_firebeetle2_esp32c6/pins_arduino.h` — the folder name guessed from the S3's (G0.1); exit 0, 56 lines. TX=16 RX=17 SDA=19 SCL=20 SS=5 MOSI=22 MISO=21 SCK=23 A1..A4=2..5 D2=8 D3=14 D6=1 D7=18 D9=9 D11=7 D12=6 D13=15 LED_BUILTIN=15; no A0, no D0/D1/D4/D5/D8/D10/D14.
- 18:16 F2 the DFRobot wiki (SKU_DFR1075 → served at /dfr1075/): links the dimension PDF, the schematics zip, the STP.
- 18:17 F3 the dimension drawing PDF (101,312 bytes): vector paths, no text layer — parsed with an own path parser; labels read off a 150 dpi render.
- 18:19 F4 the schematics zip (306,653): V1.0 (HM6245P3V3PR) and V1.1 (TPS62A02DRLR); header P2 1×18 and P1 1×14 match the drawing pad for pad; GPIO19 and GPIO20 each on two pads; the pad printed VIN is net VCC.
- 18:20 F5 soc_caps.h (ESP-IDF v5.5.2, esp32c6): SOC_RTCIO_PIN_COUNT 8; SOC_PM_SUPPORT_EXT1_WAKEUP_MODE_PER_PIN (1); no EXT0; SOC_ADC_PERIPH_NUM 1, SOC_ADC_MAX_CHANNEL_NUM 7.
- 18:20 F6 the ESP32-C6 datasheet v1.5 (86 pages).
- 18:22 Step 1 copy the S3 file → boards/firebeetle2-esp32c6.json, boards/active.json; validate on the unedited copy exit 1: `id is 'firebeetle2-esp32s3' but the file is named 'firebeetle2-esp32c6'…`.
- 18:24 validate after the C6 facts, exit 1: `pin_roles.jtag is not a role any script reads … Known: adc2_unusable_with_wifi, console_uart, i2c, not_wake_capable, onboard_button, onboard_led, spi, strapping` (and gdi_display) — the role list documented nowhere (G0.5). `//jtag` inside pin_roles refused (`needs both a 'gpio' list and a 'note'`); moved to a top-level `//pin_roles_not_read_by_spark` → `active firebeetle2-esp32c6 (project): ok`, exit 0; `--for-fab` ok — with no drill_mm, `regulator_3v3_a: null`, and pad labels "17", "14", …
- 18:24 Step 3 footprint exit 0; header reads `The holes are 1.00 mm, NOT the ? mm on the vendor drawing.`; `--json` printed TSX (G0.8); mounting holes not emitted.
- 18:25 Step 4 vendor pins: `firebeetle2-esp32c6 ok (20 pins against …pins_arduino.h)`, exit 0.
- 18:25 Step 5 chain, requirements `{"board": "firebeetle2-esp32c6", "parts": ["led-red-5mm"]}`: exit 1, `[!!] build LedRed5mmSeriesA.pin1 (a terminal connected to nothing)`; circuit.json: `Could not find port for selector ".Mcu > .D3"`; the 3V3 trace landed on `pin17_internal_1` (hints pin17, 17, 3V3), GND1 on `pin15_internal_1` — tscircuit read bare numbers as pin numbers and merged pads (G0.3).
- 18:26 pads renamed IO<n> with pad_aliases D3→IO14 …: all four steps ok; chain exit 1, the same D3 error; power traces clean; the alias carried nothing to the pad (G0.4). (The S3 footprint also gives its MI pad only ["MI"].)
- 18:27 pads named by pins_arduino.h's names (RX, TX, D2, D3 …), IO19/IO20 for the second SDA/SCL pads, SS→A4 the only alias: all four steps exit 0; chain: `[ok] build 5 trace(s), 0 errors, tsci 0.0.2621`; `[!!] simulation no diagram was produced` — `"14" is not a pin of board-esp32-c6-devkitc-1`, `"3V3.1" is not a pin` ×2; the converter listed the stand-in's pins (0–13, 15, 18–23, 3V3, 5V, GND.1–4, NC0, NC1, RST, RX, TX).
- 18:27 wokwi_power_pins fixed from that list (3V3, GND.1, GND.2, VIN→5V): only `"14" is not a pin…` remains. STOP (G0.6).
- 18:28 `--json`: status problems; board/schematic/footprint/build ok; simulation problems. The plugin cache write found (G0.7). 18:29 `--offline` passes from the cache the live run left in the plugin.

## What stands
R/project/boards/firebeetle2-esp32c6.json (sha256 4e5029ac…3872), boards/active.json, requirements.json, the generated board.tsx, FireBeetle2Esp32C6.tsx, dist/; earlier versions R/tmp/c6-digit-labels.json, c6-io-labels.json. Results on the final file as in the summary.

## Numbers and their provenance (D = dimension drawing V1.1.0, S = schematic V1.1, W = wiki, DS = C6 datasheet v1.5; 12.712 pt/mm calibrated on the 60 mm outline)
| field | value | provenance | source |
| --- | --- | --- | --- |
| width_mm | 25.4 | stated (measured 25.38) | D "25.40mm"; W |
| height_mm | 60.0 | stated; the scale reference | D, W |
| thickness_mm | 1.6 | stated | D |
| corner_radius_mm | 1.5 | measured (1.50 / 1.53) | D |
| header rows / pins | 2 / [18,14] | stated | S P2, P1; D |
| pitch_mm | 2.54 | measured (2.5399) | D |
| row_spacing_mm | 22.86 | measured 22.845 = 9 × 2.54 | D |
| pad_mm | 1.5 | measured (1.501) | D |
| drill_mm | none | not stated — the footprint used its own 1.00 | — |
| first_pad_from_edge_mm | 5.2 | measured (5.197) | D |
| mounting holes | 4 / 2.0 mm / 1.7 inset; 22.0 × 56.6 | stated / measured | D, S MH1–MH4 |
| wokwi_size_px | 70×160 | copied from the S3 file | — |
| pins (20) | as F1 | stated | pins_arduino.h; vendor pins ok |
| wake_capable_gpio | 0–7 | datasheet | soc_caps; DS Table 2-7 p22 |
| adc_gpio | 0–6 | datasheet | DS Table 2-9 p23; soc_caps |
| strapping | 4, 5, 8, 9, 15 | datasheet | DS p25 |
| onboard led / button | 15 / 9 | stated | pins_arduino.h; S |
| not_wake_capable | 8, 9, 14–23 | calculated | — |
| console uart / spi / i2c | 16, 17 / 22, 21, 23, 5 / 19, 20 | stated | S; pins_arduino.h |
| charge_current_a | 0.5 | stated; 0.54 calculated (1188V/R9, R9 2.2k) | W, S |
| module_peak_a | 0.354 | datasheet-max | DS Table 5-7 p66 |
| deep_sleep_ua | 36 | stated (the higher of two revisions; chip alone 7 datasheet-typ) | W; DS Table 5-11 p68 |
| io_volts | 3.3 | datasheet-typ (3.0–3.6) | DS Table 5-2, 5-4 |
| regulator_3v3_a | null | not read | — |
| R values in notes | — | from a picture (a schematic render) | S |
Carried without a fetch: micropython_port ESP32_GENERIC_C6, the single-polarity note, simulated_by_wokwi false (from spark's xiao-esp32-c6.json); wokwi_part_type board-esp32-c6-devkitc-1 from memory (the converter recognised it).

## Gaps
- G0.1 how to find the variant folder (guessed from the S3's naming).
- G0.2 the `physical` schema is undocumented (how-it-works says boards/README "has the schema"; it has none): flush_edge, row_<n>, drill_mm required?, nulls, mounting_holes/corner_radius unused by the footprint.
- G0.3 the naming rule misses `header_order`: bare-number labels pass every check, then tscircuit merges pads silently (3V3 with "17", GND1 with "15").
- G0.4 what `pad_aliases` does is undocumented; here it joined nothing.
- G0.5 the `pin_roles` list is closed but undocumented; `//` comments refused inside it.
- G0.6 the stand-in's pins are unknowable from the docs; no way to state a missing pin; the power-pin names learnt from the converter's error.
- G0.7 a live vendor check writes into the plugin folder, even with SPARK_HOME/HOME redirected.
- G0.8 `emit_footprint.py --json` prints TSX, not JSON.
- G0.9 keeping a board's documents is undocumented.
- G0.10 repeated and NC pads undocumented (one rail on two pads; GPIO19/20 twice; NC pads).

## Searches — fetches (6, all used); no web search, no Espressif-docs query
the arduino-esp32 variant via gh · the DFRobot wiki page · the dimension PDF · the schematics zip · soc_caps.h v5.5.2 via gh · the C6 datasheet v1.5. (check_vendor_pins fetched through gh three times on its own.) No Wokwi.
