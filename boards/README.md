# Board definitions

> The schema and the contract are spark's. The steps are the smart bin's: they name a Makefile, `make check` and `config.py`,
> which a spark project does not have. With spark's own scripts, see [Your own dev board](../docs/guide/how-it-works.md#your-own-dev-board).

One file per board, holding everything the rest of the project needs to know about which
microcontroller this is: the silkscreen-to-GPIO map, which pins can wake it, which have an ADC,
which have a second job, which MicroPython build it runs, and what it is physically — its
footprint in the PCB design and its size on screen.

It exists because that knowledge was in six places — the firmware, the PCB design, the
simulator's part type, the pin-map checker, the placement code and a pile of comments — and six
copies of a fact are five chances to be wrong.

```text
spark/boards/                  the shipped LIBRARY — verified definitions, adopt without copying
  firebeetle2-esp32s3.json
  xiao-esp32-c6.json

your-project/
  boards/active.json           <- which board. THE one place it is chosen.
  boards/<id>.json             optional: your own definition. Yours always wins.
  .spark/board.json            GENERATED. The resolved, validated board every consumer reads.
```

A project needs **one file** to adopt a library board:

```json
{ "schema": 1, "board": "firebeetle2-esp32s3" }
```

A definition you verified yourself always beats a shared one, so a project's own `boards/<id>.json`
overrides the library. Nothing you have checked can be replaced by a plugin update.

## Switching board

```sh
boards.py --list          # what is available, and whether it is yours or the library's
$EDITOR boards/active.json # change the one line
boards.py --resolve       # -> .spark/board.json, validated
make check                # what still disagrees
```

Nothing else names a board. The resolver validates the active one and writes it to
`.spark/board.json`; Make, the firmware's spec generator and the simulator's diagram generator
all read that single file.

That indirection earns its place: the search and the schema check used to exist twice, once in
Python and once partially in TypeScript, and the shared library would have forced the second copy
to learn about a second directory. Resolving once means a consumer reads a file instead of
re-implementing a lookup.

## Adding a board

1. **Write `boards/<id>.json`.** Copy the closest existing one. `id` must match the filename and be a plain key:
   lower-case letters, digits and `-`. The `pins` keys, the `power_pads` keys and their rails, and
   `physical.footprint_export` are names — letters, digits and `_` — because the board is written with them as code;
   `physical.header.drill_mm` is a number. `boards.py --validate` refuses anything else.
2. **Get the pin map from the vendor's Arduino variant header**, not from a pinout picture:
   `espressif/arduino-esp32` → `variants/<board>/pins_arduino.h`. Pinout diagrams are drawn by
   marketing; the header is what the toolchain compiles against. Cross-check it against the
   vendor wiki and record both under `sources`.
3. **Get the chip's capabilities from `soc_caps.h`** in `espressif/esp-idf`:
   `SOC_RTCIO_PIN_COUNT` gives the wake-capable range, `SOC_PM_SUPPORT_EXT0_WAKEUP` says whether
   `esp32.wake_on_ext0` exists, `SOC_PM_SUPPORT_EXT1_WAKEUP_MODE_PER_PIN` whether wake pins may
   have different polarities. Guessing any of these costs a bench session.
4. **Check it**: `boards.py --validate`. The contract is enforced, not documented.
5. **Rework `config.py`'s pin assignments.** Which function sits on which pin is a design
   decision, not a board fact — see below.
6. **Swap the footprint in `board.tsx`** to the one named in `physical.footprint_export`.
   Until `footprint_module` and `footprint_export` are filled in, `--validate --for-fab` fails
   and `make` refuses to export gerbers, which is deliberate: an unverified footprint is the one
   mistake here that costs money.

## What is a board fact, and what is not

The line that keeps this file honest:

- **A board fact** is true of the hardware whatever you build with it — D9 is GPIO0, GPIO11 is
  on ADC2, GPIO38 cannot wake the chip. These go in `boards/<id>.json`.
- **A design decision** is a choice you made — which pin the OPEN button is on, whether buttons
  are wired to GND or 3V3 (and therefore `config.WAKE_ON_HIGH`). These go in `config.py`.

`wake_on_high` was briefly in a board file during the S3 switch and had to come out: it follows
from how the buttons are wired, not from the board. A board file that accumulates decisions
stops being swappable, which is the whole point of the directory.

Steps 1–4 are mechanical. Step 5 is real work, and no amount of structure avoids it: moving to a
board with more wake-capable pins is precisely the kind of change that should make you revisit
the pin map rather than transplant it. Going from the XIAO ESP32-C6 to the FireBeetle 2 ESP32-S3
took the wake-capable pin count from 3 usable to 22, which changed every assignment.

## Flash size

`flash_mb` is the flash in MB: one number, or a list when one record covers SKUs with different flash (the FireBeetle
2: `[16, 4]`). Write its `//flash_mb` source beside it. `board_look.py` compares what esptool reads from a board with it. A record without `flash_mb` makes the flash field
unknown, and that is a warning.

## Button places

`physical.buttons` says where the BOOT and RESET buttons are. Each hint that tells a person to press one reads it.
Write `seen_from` (how to hold the board), then `boot` and `reset`, each with its `silkscreen` letter and its `place`.
Write its `//buttons` source beside it. Write it only from a photo of a board you hold or from the maker's page. A
record without it, or with a part missing, gives the plain hint: "the BOOT button" and "RESET", with no place.

```json
"buttons": {
  "seen_from": "the metal shield facing you, USB-C at the top",
  "boot":  {"silkscreen": "B", "place": "top right, beside the USB-C"},
  "reset": {"silkscreen": "R", "place": "top left, beside the USB-C"}
}
```

## The board's own parts

A board that carries its own LED, buttons, display or battery-level pin names them in `pin_roles`, under `onboard_led`,
`onboard_button`, `onboard_display` or `onboard_battery_sense`. Each entry holds a `gpio` list and a `note` that says where the facts come from.
Three things follow from such an entry:

- `firmware/pins.py` names the part when the entry has exactly one GPIO (`ONBOARD_LED = 15`) or has `labels` (one line per
  label). An entry with an empty `gpio` list, or with several GPIOs and no `labels`, is legal, but `pins.py` names no pin of it.
- `/spark:idea` offers the board for a need that the part serves, such as "indicate light" for the LED. It offers the
  part only when `pins.py` names its pins, so an entry with no name for its pins is not offered.
- The build says that a passed run does not test the part.

An entry may also hold these keys:

- `active_level`: 0 or 1, the level that lights the LED or that a pressed button reads.
- `labels`: `{"S1": 0, "S2": 35}`. A label is capital letters and digits, and not `ON`. Each value is one of the entry's
  `gpio`. `pins.py` gets a line `ONBOARD_BUTTON_S1 = 0` per label. The note and the record's `documents` cite the labels.
- `facts`: `{"width": {"value": 135, "verified": false, "source": "…", "why_it_matters": "…"}}`. A name is lower-case
  letters and underscores, and not `on`. Each fact follows the part records' rule: a value, `verified` and a `source`,
  and a `why_it_matters` when the value is not verified. `pins.py` gets `ONBOARD_DISPLAY_WIDTH = 135`, with the source
  and "not verified" in the comment. Only a finite number or a word becomes a line, and `--validate` refuses a value that
  is a list, an object, or not finite.

```json
"onboard_display": {
  "gpio": [19, 18, 5, 16, 23, 4],
  "labels": {"MOSI": 19, "SCLK": 18, "CS": 5, "DC": 16, "RST": 23, "BL": 4},
  "facts": {"driver": {"value": "ST7789", "verified": true, "source": "documents.lilygo-t-display-readme, Pinout table"}},
  "note": "The TFT on SPI, from the pinout table of documents.lilygo-t-display-readme."
}
```

A battery-level pin is one GPIO that a divider from the battery is wired to, with the divider as a fact:
`"onboard_battery_sense": {"gpio": [34], "facts": {"divider": {"value": 2, "verified": true, "source": "…"}}, "note": "…"}`.
`pins.py` gets `ONBOARD_BATTERY_SENSE = 34` and `ONBOARD_BATTERY_SENSE_DIVIDER = 2`. The `divider` is the ratio: the battery
voltage divided by the pin voltage. The assigner keeps the pin free for
longer than a plain one, and says so when it must use it. `/spark:idea` offers the board for a `sense` need of `battery level`.
The build says that a passed run does not test the battery reading, because spark adds no battery to the diagram.

`--validate` refuses a `gpio` that is not a list of GPIO numbers, a label or a fact name that breaks these rules, and a
fact without its source. The T-Display record in `tests/data/boards/` is the one example today.

### The charger, the regulator and the battery input

These parts have no pin, so they are facts in the board's `power` block, not entries of `pin_roles`. Each fact holds a
`value`, `verified` and a `source`, as every fact does, and a `why_it_matters` when the value is not verified:

- `charger`: the chip that charges the battery, such as `TP4054`.
- `regulator`: the chip that makes the 3.3 V rail.
- `battery_input`: where the battery plugs in, in words. Say "pads" when the board has pads and no connector.

`/spark:idea` offers the board for a need of `power` / `charger`, `power` / `voltage regulator` or `connect` / `battery
input`. The offer reads the value only, so it does not say whether the fact is verified. `pins.py` names nothing for
these facts. `--validate` refuses a power fact with no source, a value that is a list, an object or a blank word, and a
`power` block that is not an object. The offer words are `onboard charger`, `onboard voltage regulator` and `onboard
battery input`. A need of `power` / `battery` means the cell, and no board part matches it.

## Simulation

`wokwi_part_type` names the part the generated Wokwi diagram uses. If Wokwi has no model of the
exact board, a same-silicon devkit stands in and `wokwi_is_stand_in` says so — the diagram
addresses pins by GPIO number, so a stand-in costs the silkscreen labels in the picture, and the board's own LED and button
where the devkit has only bare header pins (P483).
A stand-in's `documents["wokwi-board"]` entry cites the stand-in's own file, so a GPIO it reaches is a header pin and the limits say so.

Wokwi custom boards exist but are a browser-only feature (F1 → "Load custom board file"):
`wokwi.toml` has no board key, and the simulator loads boards from a bundle Wokwi hosts. Getting
a board supported headlessly means a PR to `wokwi/wokwi-boards`.
