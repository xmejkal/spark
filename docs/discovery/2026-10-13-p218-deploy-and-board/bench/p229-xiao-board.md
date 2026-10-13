# P229: a board spark does not know, walked for real

Card: [P229, #217](https://github.com/xmejkal/spark/issues/217). Walked 2026-10-13 by Claude for the PO. The board is the
Seeed XIAO ESP32-C6. The bench project is `button-light` (a button and an LED).

## Short version

- The board file was written from Seeed's, Espressif's, MicroPython's and Wokwi's own sources. I did not open the
  shipped `boards/xiao-esp32-c6.json` until step 5.
- All four checks passed. The bench project builds end to end on the new board.
- The new file has 12 fields the same as the shipped one, 13 that differ and 13 that only it has.
- The path works, but a person stalls in five places. The three worst: no command and no store place for a board, a
  schema that is only explained in another board's comments, and `single_polarity_for_all_pins`, where the README's
  own advice gives the wrong answer for MicroPython.

## Files

| file | what it is |
| --- | --- |
| `boards/xiao-esp32-c6-fresh.json` (in the project) | the board file, written fresh |
| `button-light-s3/` (beside the project) | the S3 build, copied before anything changed |
| `<store>/sources/<sha256>/` | the 11 kept sources (below) |

## Step 1: what spark tells a person

I read `docs/guide/how-it-works.md`, section "Your own dev board", and `boards/README.md`. I copied
`boards/firebeetle2-esp32s3.json` as the guide says, and replaced every fact.

Where a person stalls or guesses:

1. There is no command for this. `/spark:research` covers modules only. The guide's five steps are the whole path.
2. `boards/README.md` "Adding a board" names a Makefile, `make check` and `config.py`. A spark project has none of
   them. The README warns about this in its first lines (P127), so a person has two sets of steps to reconcile.
3. The schema is not written down field by field. `wokwi_pin_naming` takes `"gpio"` or `"silkscreen"`, and only
   `tools/circuit-to-wokwi/lib/board.ts` says so. `wokwi_size_px` has no stated scale. `flush_edge` is read by no
   code. Which of `width_mm` and `height_mm` runs along the header rows is only in `scripts/emit_footprint.py`
   (`height_mm` does). `power_pads`, `power` and `documents` are explained only in the FireBeetle file's comments.
4. The copy carries about 30 comment keys about the FireBeetle. Each has to be read, then deleted or rewritten.
5. The copy source is not blind. The FireBeetle file's `//wake_capable_gpio` and `//deep_sleep` state XIAO facts
   ("only GPIO0-7 could wake the chip"). `boards/README.md` says the XIAO had "3 usable" wake pins. A person
   researching fresh reads the old answers first.
6. The guide says to keep sources as spark keeps them. No command does it for a board. `store.keep` exists only as
   a Python function, and `parts.py --fetch` reads part records only. I called `store.keep` from Python.
7. The project had no `.spark/` and no `boards/active.json`. The guide's step 1 says to run
   `init_project.py --board <id>` then. That worked, but it is easy to miss inside step 1's text.

## Step 2: the sources

All read 2026-10-13. Each file is kept in the store under its sha256.

| source | version | used for | sha256 (first 8) |
| --- | --- | --- | --- |
| [Seeed wiki, Getting Started](https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/) | "Last updated on Aug 5, 2024" | pin map table, size 21 x 17.8 mm, buttons, RF switch, 5V pin, deep sleep | 87ab9b88 |
| [Seeed schematic](https://files.seeedstudio.com/wiki/SeeedStudio-XIAO-ESP32C6/XIAO_ESP32_C6_v1.0_SCH_260114.pdf) | Rev V1.0, 2026-01-14, 5 sheets | U2 header pin order (sheet 03), buck SGM6029, charger 120 mA, LED and BOOT circuits (sheet 04), ESP32-C6FH4 | 510f3f91 |
| [Seeed pinout sheet](https://files.seeedstudio.com/wiki/SeeedStudio-XIAO-ESP32C6/res/XIAO_ESP32C6_Pinout.xlsx) | none printed | cross-check only | e2dae530 |
| [Seeed DIP footprint](https://github.com/Seeed-Studio/OPL_Kicad_Library) `XIAO-ESP32-C6-DIP.kicad_mod` | commit b0035c51 | holes: 2 x 7, 2.54 pitch, rows 15.24 mm apart, drill 0.889 | 5361d045 |
| [Espressif ESP32-C6 datasheet](https://documentation.espressif.com/esp32-c6_datasheet_en.pdf) | v1.5 | strapping pins p25 and Table 3-1 p33. USB, flash and UART pins p25. LP GPIO0-7 p22. ADC1_CH0-6 Table 2-8 p23. VDD Table 5-2 p64. Pull-up p65. TX peak Table 5-7 p66 | 372a5b42 |
| [arduino-esp32 `pins_arduino.h`](https://github.com/espressif/arduino-esp32/blob/3.3.12/variants/XIAO_ESP32C6/pins_arduino.h) | tag 3.3.12 | the label to GPIO map | 9cdb00a2 |
| [arduino-esp32 `variant.cpp`](https://github.com/espressif/arduino-esp32/blob/3.3.12/variants/XIAO_ESP32C6/variant.cpp) | tag 3.3.12 | GPIO3 and GPIO14 driven low at start | cb6b1b84 |
| [ESP-IDF `soc_caps.h`](https://github.com/espressif/esp-idf/blob/v5.5.1/components/soc/esp32c6/include/soc/soc_caps.h) | tag v5.5.1 | RTCIO count 8, no EXT0, EXT1 per pin, one ADC | 43e1668e |
| [MicroPython download](https://micropython.org/download/SEEED_XIAO_ESP32C6/) | lists v1.29.0 | Seeed's own build exists | 295caeb1 |
| [MicroPython `pins.csv`](https://github.com/micropython/micropython/blob/v1.29.0/ports/esp32/boards/SEEED_XIAO_ESP32C6/pins.csv) | tag v1.29.0 | cross-check of the pin map, names LED, BOOT, RF_SEL, RF_POWER | fa4b3b57 |
| [Wokwi board](https://github.com/wokwi/wokwi-boards/tree/4294fca6dce4c5e3d7393ceda312225ed861c997/boards/xiao-esp32-c6) `board.json` | commit 4294fca6 | part type, silkscreen pin names, size | e5200e01 |

The budget was 10 searches and 12 page fetches. I used 2 searches and 11 page fetches. I also made about 9 GitHub API
reads to list folders and read small repository files.

The four pin sources agree on all 22 labels. D3 is GPIO21, D6 is GPIO16 and D10 is GPIO18.

## Step 3: the board file

`boards/xiao-esp32-c6-fresh.json` in the project. Each fact without a source is marked in the file:

- `sku` is empty. The wiki page does not print it.
- `power.regulator_3v3_a` is null. The schematic names the buck but not its current rating.
- `power.deep_sleep_ua` is 15 and unverified. The wiki's table puts three boards side by side.
- Which end the USB-C is at comes from Wokwi's drawing and the wiki picture, not from Seeed's footprint.
- `console_uart`: whether the ROM prints on GPIO16 at reset on this board.
- `single_polarity_for_all_pins` is false for the silicon. Whether MicroPython can use that was not checked.
- `simulated_by_wokwi` is null. Not tested.
- `wokwi_size_px` is arithmetic on Wokwi's drawing at 96 dpi.

What spark does with a project board of the same id as a shipped one: `boards.records` calls `store.records`. It
reads the library first and then the project. The project's file then replaces the library's under the same key
(`scripts/store.py`, `layers` and `records`). The project's file wins silently. `boards.py --validate` prints
`(project)` beside the id, and that is the only sign. Boards have no shelf layer, so a board cannot live in the store.
Not tested, as asked.

## Step 4: the bench project moved to it

The S3 build was copied first to `button-light-s3/`, and `diff -rq` found no difference.

Setup, because the folder was not a spark project yet:

```text
$ python3 <spark>/scripts/init_project.py --board xiao-esp32-c6-fresh
  wrote active.json
  named 2 rail(s) from circuit.json
13 field(s) nobody has answered. ...
```

### Check 1: the contract. Passed, exit 0.

```text
$ python3 <spark>/scripts/boards.py --validate --project .
         firebeetle2-esp32s3 (library): ok
         xiao-esp32-c6 (library): ok
  active  xiao-esp32-c6-fresh (project): ok
```

It passed on the first run. No fix was needed.

### Check 2: the vendor's pins. Passed, exit 0.

```text
$ python3 <spark>/scripts/check_vendor_pins.py boards/xiao-esp32-c6-fresh.json
  xiao-esp32-c6-fresh      ok  (22 pins against espressif/arduino-esp32 variants/XIAO_ESP32C6/pins_arduino.h ... wrote <project>/.spark/cache/XIAO_ESP32C6.pins_arduino.h)
      note: the vendor also defines WIFI_ENABLE, WIFI_ANT_CONFIG, which this board file does not record
```

The check fetches the default branch, not a tag. Today that file was byte for byte the same as tag 3.3.12.

### Check 3: the footprint. Passed, exit 0.

```text
$ python3 <spark>/scripts/emit_footprint.py --board xiao-esp32-c6-fresh --project .
// The holes are 1.00 mm, NOT the 0.889 mm on the vendor drawing. ...
      <platedhole portHints={["D6"]} pcbX="-7.62mm" pcbY="7.62mm" ... />
      ...
      <platedhole portHints={["5V"]} pcbX="7.62mm" pcbY="-7.62mm" ... />
```

14 holes, rows 15.24 mm apart, the same places as Seeed's DIP footprint. It prints to the screen and writes no file.

### Check 4: the build. Passed, exit 0.

`requirements.json` now names `"board": "xiao-esp32-c6-fresh"`.

```text
$ python3 <spark>/scripts/check_spine.py requirements.json --keep .
  wrote XiaoEsp32C6.tsx
  left alone: board.tsx (delete it to have it regenerated)
  wrote dist ...
  wrote breadboard.md ...
  wrote firmware/pins.py ...
  wrote sim ...
  [ok  ] board            Seeed Studio XIAO ESP32-C6
  [ok  ] schematic        7 trace(s) written
  [ok  ] footprint        XiaoEsp32C6.tsx
  [ok  ] build            5 trace(s), 0 errors, tsci 0.0.2600
  [ok  ] simulation       5 wire(s) in the diagram
           no serial monitor is wired in the diagram (a board part with no pins named TX and RX, ...)
  the chain runs end to end
```

The result: the LED on D8 (GPIO19) and the button on D10 (GPIO18), both on the SPI pins. The diagram uses Wokwi's
real `board-xiao-esp32-c6`. The firmware (`light.py`, `main.py`) did not need a change. Nothing was flashed or
simulated.

## Step 5: the shipped file, field by field

Same 12, differ 13, only in one file 13 (all 13 are only in mine). Comment keys are left out.

| field | fresh | shipped | verdict |
| --- | --- | --- | --- |
| schema | 1 | 1 | same |
| id | xiao-esp32-c6-fresh | xiao-esp32-c6 | differs, on purpose |
| name | Seeed Studio XIAO ESP32-C6 | Seeed XIAO ESP32-C6 | differs. The wiki title says "Seeed Studio XIAO ESP32C6" |
| chip | esp32c6 | esp32c6 | same |
| micropython_port | SEEED_XIAO_ESP32C6 | ESP32_GENERIC_C6 | differs. MicroPython's download page lists "SEEED_XIAO_ESP32C6-20260824-v1.29.0.bin". Both builds run. Seeed's adds the board's pin names. No spark script reads this field |
| sku | [] | none | only in mine (empty) |
| sources | 5 entries | none | only in mine |
| documents | 11 kept sources | none | only in mine |
| wokwi_part_type | board-xiao-esp32-c6 | board-xiao-esp32-c6 | same |
| wokwi_pin_naming | silkscreen | silkscreen | same |
| wokwi_is_stand_in | false | none | only in mine |
| wokwi_power_pins | 3V3, GND, 5V | V33, GND, V5 | differs. Keys are the footprint's pad names. Mine come from the silkscreen in `header_order`. The shipped keys match a footprint that is not generated from header data. Wokwi's names (3V3, GND, 5V) are the same in both |
| power_pads | GND, 3V3, 5V | none | only in mine |
| physical.footprint_module | null | XIAO-ESP32-C6-SMD | differs. The shipped file names Seeed's SMD footprint. Mine draws holes from geometry |
| physical.footprint_export | XiaoEsp32C6 | XiaoRealFootprint | differs, a name only |
| physical.width_mm | 17.8 | 21.0 | differs. In `emit_footprint.py` the height runs along the rows. Seeed's DIP footprint puts the 7-pin rows along the 21 mm side. So 17.8 wide and 21 high is right for spark. The shipped values are the wiki's "21 x 17.8 mm" in print order |
| physical.height_mm | 21.0 | 17.8 | differs, the same reason |
| physical.wokwi_size_px | 68 x 88 | 70 x 90 | differs. Neither cites a source. Mine is Wokwi's 18.1 x 23.4 mm at 96 dpi |
| physical.header | 2 x 7, 2.54, 15.24, 0.889 | none | only in mine. This is why the shipped board stops at the footprint stage |
| physical.header_order | two rows of 7 | none | only in mine |
| physical.pad_aliases | 11 aliases | none | only in mine |
| pins (the 20 shared labels) | D0 to D10, A0 to A2, bus names | the same | same |
| pins TX, RX | 16, 17 | none | only in mine. `pins_arduino.h`: "TX = 16", "RX = 17" |
| wake_capable_gpio | 0 to 7 | 0 to 7 | same |
| adc_gpio | 0 to 6 | 0, 1, 2 | differs. The datasheet, Table 2-8 p23, gives ADC1_CH0 to CH6 on GPIO0 to 6. The shipped file lists only the header's. The FireBeetle file lists the chip's, so the convention is not fixed |
| pin_roles.strapping | 4, 5, 8, 9, 15 | 4, 5, 8, 9, 15 | same |
| pin_roles.onboard_led | 15 | 15 | same |
| pin_roles.spi | 18, 19, 20, 21 | 18, 20, 19, 21 | same set |
| pin_roles.i2c | 22, 23 | 22, 23 | same |
| pin_roles.console_uart | 16, 17 | 16 | differs. Datasheet p25: "GPIO16, GPIO17: UART0 interface". The shipped note is about the boot log on TX only |
| pin_roles.onboard_button | 9 | none | only in mine. Schematic sheet 04: K2 BOOT on GPIO9 |
| pin_roles.not_wake_capable | 16 to 23 | none | only in mine |
| deep_sleep.wake_api | esp32.wake_on_ext1 | esp32.wake_on_ext1 | same |
| deep_sleep.single_pin_api | null | none | only in mine |
| deep_sleep.single_polarity_for_all_pins | false | true | differs. The shipped file is right for spark. It cites "esp32.wake_on_ext1 takes one level for the whole mask (ports/esp32/modesp32.c, v1.29.0)". My false is the silicon's (soc_caps MODE_PER_PIN), and I had marked it unverified for MicroPython |
| deep_sleep.simulated_by_wokwi | null | false | differs. The shipped file cites an experiment. I tested nothing |
| vendor.arduino_variant | XIAO_ESP32C6 | XIAO_ESP32C6 | same |
| power | 6 facts, 4 verified | none | only in mine |

## Findings

Each is a gap a person or Claude met on this walk. E is the tag, with a pointer.

| tag | finding | pointer |
| --- | --- | --- |
| E1 | No command for a dev board. `/spark:research` covers modules only, so a board is written by hand from the guide | `commands/research.md`, guide "Your own dev board" |
| E2 | No store place for a board. Boards have two layers, project and library. A board researched once lives in one project | `scripts/store.py` `layers` |
| E3 | No command keeps a board's sources. I called `store.keep` from Python. `parts.py --fetch` reads parts only | `scripts/store.py` `keep`, `docs/archive/2026-10-01-keeping-sources.md` |
| E4 | The README's "Adding a board" steps are the smart bin's (Makefile, `config.py`) | `boards/README.md`, P127 |
| E5 | The schema is not written down. Allowed values of `wokwi_pin_naming` are only in TypeScript. The scale of `wokwi_size_px` is not stated. `flush_edge` is read by nothing. Which side is `height_mm` is only in code | `boards/README.md`, `tools/circuit-to-wokwi/lib/board.ts`, `scripts/emit_footprint.py` `pads` |
| E6 | The file a person is told to copy states the XIAO's answers in its comments. So does the README. A fresh research is not fresh | `boards/firebeetle2-esp32s3.json` `//wake_capable_gpio`, `boards/README.md` |
| E7 | A project board with a shipped id replaces the shipped one with no warning beyond `(project)` in `--validate` | `scripts/store.py` `records` |
| E8 | `check_vendor_pins.py` fetches the variant header from the default branch, and the cached copy has no version or date | `scripts/check_vendor_pins.py` `fetch_variant_header` |
| E9 | `single_polarity_for_all_pins` mixes two meanings. The README sends a person to `soc_caps.h`, which gives false for the C6. MicroPython's API makes it true. A person following the README writes the wrong value for spark's firmware | `boards/README.md` step 3, shipped `//single_polarity_for_all_pins` |
| E10 | The schema has no place for pads off the header (the four JTAG pads on the back, BAT+ and BAT-). `--validate` refuses a pin with no pad in `header_order` | `scripts/boards.py` `validate` |
| E11 | The rebuild left the old `board.tsx` (it still imports `FireBeetle2Esp32S3`) and `FireBeetle2Esp32S3.tsx` in the project. The guide's step 5 does not say to delete them | `check_spine.py` line "left alone: board.tsx" |
| E12 | The diagram has no serial monitor, because Wokwi's XIAO part has no pins named TX and RX. A scenario that waits for `ready` can hear nothing. Not run | `check_spine.py` simulation line |
| E13 | The assigner put both signals on SPI pins (D8, D10) while D0 to D2 had no role. The SPI role says plain signals take it last. Perhaps it saves the wake and ADC pins, but `pins.py` does not say so | `firmware/pins.py` |
| E14 | The shipped file's `width_mm` and `height_mm` are swapped against the rule in `emit_footprint.py`. It is harmless today because it has no header | shipped `physical` |
| E15 | `micropython_port` is read by no script, and the shipped one misses Seeed's own build | `scripts/`, MicroPython download page |
| E16 | `adc_gpio` means the chip's ADC pins on one board and the header's ADC pins on the other | both board files |

These rows go to `docs/observations/INDEX.md`. This walk did not write them there.

## What I did not check

- The board in hand. Nothing was flashed, measured or simulated. Which end the USB-C is at, and whether the silkscreen
  matches the pinout, need a look at the real board.
- The 3.3 V buck's current rating (SGM6029 datasheet not read).
- Whether the ROM prints on GPIO16 at reset on this board.
- MicroPython's `wake_on_ext1` levels on the C6 (not read, the shipped file cites it).
- The deep sleep figure. The wiki's table column order was not certain.
- What a project board with a shipped id does in practice. I read the code and did not test it.
- `boards.py --validate --for-fab` and the gerber path. Not asked, not run.
