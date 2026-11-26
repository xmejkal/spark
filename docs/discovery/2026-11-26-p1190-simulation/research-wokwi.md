# Research: what Wokwi gives free and what it charges for

A research agent (Sonnet) read these pages on 2026-11-26, one or two searches per question. Each fact has its source.
A fact marked "not confirmed" was not found on a primary page. The brief cites a fact from here as E only after the
refuter or the session re-read its source (verification.md).

## 1. The paid part and offline use

- Plans, annual billing (https://wokwi.com/pricing, no page date printed): Community EUR 0 a month, Hobby EUR 5.6,
  Hobby+ EUR 8.1, Pro EUR 20 per seat.
- CI minutes on the pricing page: only Pro names a number, 2000 a month. Hobby and Hobby+ CI minutes: not confirmed.
  The "fast build minutes" are a separate item: 100 on Hobby, 500 on Hobby+, 1000 on Pro.
- The free plan: 50 minutes of simulation time per rolling 30 days (https://docs.wokwi.com/wokwi-ci/getting-started).
- What spends a minute: the docs say usage is the sum of the simulated time of all tests. The page does not say that
  wall time is excluded. Each CI session also has a wall-clock cap: 5 minutes on Free and Hobby, 10 on Hobby+, 50 on
  Pro (same source).
- Offline or local: the CI docs describe no offline mode. The simulation runs on Wokwi's cloud. The pricing page lists
  a Private IoT Gateway (Hobby, Hobby+, Pro) and a "VS Code offline plug-in" (Pro). Whether either runs the CLI
  without minutes: not confirmed.

## 2. Custom chips

- Languages: "any language that compiles to WebAssembly", with Rust and AssemblyScript as its examples, and the docs recommend C for
  now (https://docs.wokwi.com/chips-api/getting-started). Zig and Verilog: not confirmed. The beta label of the Chips
  API: from a search result only, not confirmed on the page.
- What a chip can model: the docs link API pages for GPIO, Analog, Time (timers), UART, I2C, SPI, Attributes and
  Framebuffer (same source). Official examples include SPI, UART and I2C chips, an I2C EEPROM and a framebuffer chip.
  Others are the SSD1306, SH1107 and IL9163 displays, LM75A, DS18B20, a CD4051B analog mux and a PCA9685.
- Controls: `controls` is an optional array in chip.json, each item with id, label, type, min, max and step. Only
  `"range"` (a slider) is listed as valid (https://docs.wokwi.com/chips-api/chip-json). The chip reads the value
  through the Attributes API. Spark's own `parts/vl6180x-breakout/chip/vl6180x.chip.json` also uses a `"boolean"`
  control ("Unplug the sensor"), which that page does not list.
- `wokwi-cli chip compile`: no page read names it or says whether it needs a token. Spark's `data/tools.json:40`
  says "compiling custom chips (free, local)".

## 3. Custom boards

- A custom board is possible in the web editor: a folder with `board.json` and `board.svg`, and a
  `wokwi-custom-board` part in diagram.json (https://github.com/wokwi/wokwi-boards, last push 2026-10-23, read with
  `gh api`, with the example `boards/esp32-devkit-v1/board.json`).
- The same through wokwi-cli in a project folder: not confirmed.
- A custom board that reuses an existing chip such as the ESP32-C6 with its own pin layout: not confirmed.

## 4. Parts with built-in controls

- DHT22: sliders for temperature and humidity in the editor's popup. The attributes `temperature` (default 24 C) and
  `humidity` (default 40 %) set the start values (https://docs.wokwi.com/parts/wokwi-dht22).
- A scenario's `set-control` step: `set-control: {part-id: dht, name: humidity, value: 39}`
  (https://docs.wokwi.com/wokwi-ci/automation-scenarios). That page lists these parts with automation controls: push
  button, potentiometer, MPU6050, analog joystick, HX711 and photoresistor (lux). DHT22 and the ultrasonic sensor are
  not in that list. The control names are on each part's page, not read.

## 5. wokwi-cli beyond a scenario run

- From https://docs.wokwi.com/wokwi-ci/cli-usage (no page date printed): `init`, a run, `lint` (reads diagram.json for faults and
  fetches board definitions from the Wokwi registry by default), `--interactive`, screenshots, `--vcd-file`.
- The page says to set `WOKWI_CLI_TOKEN`. It does not say which commands need it, or which spend minutes.
- `mcp` is an experimental MCP server and needs `WOKWI_CLI_TOKEN` (https://docs.wokwi.com/wokwi-ci/mcp-support).
- Which of these run free: not confirmed for any of them.

## 6. Custom chips other people wrote

Read with `gh api` on 2026-11-26.

- https://github.com/drf5n/Wokwi-Chip-L298N: MIT, last push 2024-10-07, an L298N motor driver. The same author has a
  TB6612FNG chip.
- https://github.com/wokwi/inverter-chip: MIT, last push 2024-06-21, Wokwi's own example.
- https://github.com/RLight-sleepy/PH-4502C-Custom-Chip: MIT, last push 2026-07-04, a pH sensor board.
- https://github.com/topics/wokwi-custom-chip: many repositories, mostly 74-series logic. Some have no licence, some
  AGPL-3.0. Check the licence before any reuse.
- E-paper chips: none found.

## Free and paid, in five lines

1. Free: the Community plan, with 50 simulated minutes of CI per rolling 30 days.
2. Free: a custom chip in C, Rust or AssemblyScript, with slider controls. Whether its compile needs a token: not
   confirmed on a Wokwi page.
3. Lint, VCD, screenshots, interactive runs and `set-control` exist. Which of them need a token or minutes: not
   confirmed.
4. Paid: Pro, EUR 20 per seat a month, 2000 CI minutes and an offline plug-in for VS Code.
5. Not confirmed: a local run without minutes, and a custom board on the ESP32-C6.
