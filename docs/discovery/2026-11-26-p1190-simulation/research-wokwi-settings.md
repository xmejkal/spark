# Research: what Wokwi lets a person set for a simulation

For the PO's answer to Q6 (D16), 2026-11-26: "Well, basically what wokwi has, pease research what all wokwi allows to
set for the simulation and we should also allow it, so yes, a temperature or values in general, but really also to
set up how its simulated the chip or part, maybe even the steps". A research agent (Sonnet) read each page once on
2026-11-26. "Not confirmed" means the page read did not state the fact.

## 1. Per part, in diagram.json (https://docs.wokwi.com/diagram-format)

- Each part has `id`, `type`, and optional `left`, `top`, `rotate`, `hide` and `attrs`. A connection is two pins, a
  colour and a placement.
- `serialMonitor` (https://docs.wokwi.com/guides/serial-monitor): `display` (auto, always, never, plotter,
  terminal), `newline` (lf, cr, crlf, none), `convertEol`, `collapse`.
- Examples of `attrs`, each from https://docs.wokwi.com/parts/ and the part's type:
  - `wokwi-dht22`: `temperature` (default 24 C) and `humidity` (default 40 %). Sliders show while it runs.
  - `wokwi-potentiometer`: `value` 0 to 1023. Its scenario control is `position`, 0.0 to 1.0.
  - `wokwi-pushbutton`: `color`, `xray`, `label`, `key` and `bounce` (on by default, "0" turns it off).
  - `wokwi-photoresistor-sensor`: `lux` (default 500), `threshold`, `rl10`, `gamma`. Its scenario control is `lux`.
  - `wokwi-ntc-temperature-sensor`: `temperature` (default 24) and `beta` (default 3950). No control is documented.
- A list of every part and its attrs on one page: not confirmed. Each part has its own page.

## 2. The board and the project

- The ESP32 family's attrs (https://docs.wokwi.com/guides/esp32): `flashSize`, `psramSize`, `psramType`,
  `serialInterface`, `firmwareOffset`, `macAddress`, `chipRevision` (P4 only), and `cpuFrequency`. The default
  `cpuFrequency` "auto" caps the CPU at about 8 MHz, and it changes the instruction speed only, not the timing of the
  peripherals.
- wokwi.toml (https://docs.wokwi.com/vscode/project-config): `firmware`, `elf`, `gdbServerPort`,
  `rfc2217ServerPort`, `vcdFile`, `[[net.forward]]`, `[[chip]]` (`name` and `binary`, with the `.chip.json` beside
  it), `[[sdcard]]`.

## 3. Scenario steps (https://docs.wokwi.com/wokwi-ci/automation-scenarios)

`delay`, `wait-serial`, `write-serial`, `set-control` (`part-id`, `name`, `value`), `expect-pin` (`part-id`, `name`,
`value`), `take-screenshot`, `touch`, `touch-press`, `touch-move`, `touch-release`. The page lists no other kind.

## 4. Custom chips (https://docs.wokwi.com/chips-api/chip-json, https://docs.wokwi.com/chips-api/attributes)

- chip.json: `name`, `author`, `pins`, `controls` (id, label, type "range", min, max, step), `display`.
- Attributes: the chip's C code declares each one with a default (`attr_init`, `attr_init_float`). A person sets it
  in the chip part's `attrs` in diagram.json. A `controls` entry lets a person change it while the simulation runs.

## 5. The run (https://docs.wokwi.com/wokwi-ci/cli-usage)

`--timeout` (default 30000 simulated ms), `--timeout-exit-code`, `--interactive`, `--scenario`, `--expect-text`,
`--fail-text`, `--serial-log-file`, `--vcd-file`, the screenshot options, the heap options (they need the ELF), and
the SD card options. A per-part "simulation mode" setting: not confirmed.

## For spark's editor

- Values (A): a part's `attrs` (a temperature, a humidity, a level, a light, a bounce), a chip's attributes, and the
  run's timeout and expected text.
- How a part or the chip is simulated (B): the ESP32's `cpuFrequency`, `psramType`, `serialInterface` and
  `flashSize`, a button's `bounce`, which chip binary stands for a part, and the SD card.
- Steps (C): the ten step kinds above. A `set-control` names a control of the part, and the control names are on
  each part's page, so spark needs one table of control names per part.
