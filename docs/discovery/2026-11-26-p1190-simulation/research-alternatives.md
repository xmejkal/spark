# Research: the alternatives to Wokwi

A research agent (Sonnet) read these pages on 2026-11-26, one or two searches per alternative. It updated the
finding of 2026-10-18 ([P295](../2026-10-18-p295-own-simulator/finding.md)) and did not repeat what still holds.
A fact marked "not confirmed" was not found on a primary page. The brief cites a fact from here as E only after the
refuter or the session re-read its source (verification.md).

## What changed since 2026-10-18

- Espressif's QEMU release `esp-develop-9.2.2-20261109` (9 Nov 2026) adds "initial support for ESP32-C6" and other
  chips. GPIO is unchanged: strap values only.
- Renode 1.17.1 (23 Nov 2026) still ships no ESP32 board.
- Velxio is now a real project, v3.0.5 (2 Sep 2026), with ESP32-S3 and C3 and an outside API.
- Two Python libraries that fake MicroPython's `machine` turned up: mockro and micropython-mock-machine.
- SimulIDE's ESP32 support is still a proof of concept.
- Not read again, so the old finding holds: Wokwi's engine is unknown, the MicroPython unix port has no `Pin`, and
  the reading that a GPL program run as a separate process leaves spark MIT is unverified.

## The table

| # | Alternative | Licence | Latest version (date) | Chips | Pins and buses from outside | MicroPython | Cost | Cannot catch |
|---|---|---|---|---|---|---|---|---|
| 1 | Espressif QEMU | GPL v2 | esp-develop-9.2.2-20261109 (9 Nov 2026) | ESP32, S3, C3. C6 "initial support" | GPIO strap only. GPIO matrix, I2C and general SPI not done. ADC not listed. Serial works | not confirmed | free, a release binary or a source build | no pin, so no LED, button, display or sensor |
| 2 | lcgamboa's QEMU fork and PICSimLab | PICSimLab GPL-2.0, the fork's licence not confirmed | PICSimLab v0.9.3 (20 Sep 2026). The fork has no releases | ESP32 and C3. S3 and C6 not named | pin hooks inside PICSimLab, no remote API found | not confirmed | free, build both | S3, C6 |
| 3 | Renode | MIT | 1.17.1 (23 Nov 2026) | no ESP32 board. Xtensa LX7 tables as "groundwork" | none, no platform | no | free | everything: no platform |
| 4 | Velxio | AGPLv3 core, commercial licence offered | v3.0.5 (2 Sep 2026) | ESP32, S3, C3. C6 not supported | yes: GPIO in and out, ADC, I2C answers, SPI events, from Python and a WebSocket | in a language list on Espressif's blog. How an image loads: not confirmed | self-hosted in Docker, the first QEMU build takes 15 to 30 minutes. A hosted tier is paid | C6, one ESP32 per process, no BLE, touch or DAC |
| 5 | SimulIDE | not confirmed | 2.0.0 test builds | ESP32, experimental | GPIO and I2C, one way only | not confirmed | free | "a proof of concept, not really usable" |
| 6a | mockro | MIT | 0.1.0 (30 Jul 2026) | none, no chip | fakes `machine`, `network`, `bluetooth`, `framebuf`. Class detail not confirmed | runs MicroPython-style code under CPython | free, a pytest plugin | timing, interrupts, the chip |
| 6b | micropython-mock-machine | MIT per its docs | not confirmed | none | `register_as_machine()`. Class list not confirmed | same as 6a | free | same as 6a |
| 6c | MicroPython unix port | MIT | v1.29.0 | none | no concrete `Pin` | the real interpreter | free | no hardware |
| 7 | ESP-IDF Linux target | not read | not read | none | none | does not run MicroPython | free | not relevant to spark's firmware |
| 8 | Cirkit Designer | not confirmed | not confirmed | ESP32-S3 in the browser, Rust and WebAssembly | not confirmed | not confirmed | not confirmed | not confirmed |

Proteus is paid, and Tinkercad has no ESP32. Both lines come from the agent's general knowledge, not read today.

## Sources, per alternative

1. Espressif QEMU. The release page names the C6 ([releases](https://github.com/espressif/qemu/releases)). The
   toolchain README lists ESP32, S3 and C3 ([README](https://github.com/espressif/esp-toolchain-docs/blob/main/qemu/README.md)).
   It marks GPIO as "strap only", and I2C and general SPI as not done. The same page says that
   Espressif does not provide support for QEMU.
2. PICSimLab. The [releases page](https://github.com/lcgamboa/picsimlab/releases) gives v0.9.3 (20 Sep 2026). Its
   notes name the ESP32 DevKit and the ESP32-C3-DevKitC-02. The [repository](https://github.com/lcgamboa/picsimlab) is
   GPL-2.0 and uses the fork `lcgamboa/qemu`, branch `picsimlab-esp32`, which has no releases.
3. Renode. [1.17.1](https://github.com/renode/renode/releases) adds Xtensa LX7 tables as "groundwork for ESP32-S2 and
   ESP32-S3 support". A community S3 port of 2023 is unfinished.
4. Velxio. The [Espressif blog, July 2026](https://developer.espressif.com/blog/2026/07/velxio-browser-based-esp32-simulation/)
   lists S3 and C3 boards and names the C6 only for later emulators in the browser. The outside API is in
   [ESP32_EMULATION.md](https://raw.githubusercontent.com/davidmonterocrespo24/velxio/master/docs/ESP32_EMULATION.md):
   `bridge.set_pin`, `set_adc`, `set_i2c_response`, `send_serial_bytes`, and the events `gpio_change`, `i2c_event` and
   `spi_event`. That page names no MicroPython. The AGPL lets spark call it as a separate process, but spark must not
   copy its code into the MIT repository. No lawyer read this question.
5. SimulIDE. Its forum calls the ESP32 support "just a proof of concept, not really usable"
   ([thread, Sep 2025](https://simulide.com/p/forum/topic/esp-32-support)).
6. The fakes. [mockro](https://pypi.org/pypi/mockro/json) 0.1.0 is MIT.
   [micropython-mock-machine](https://planetinnovation.github.io/micropython-mock-machine) says MIT. Its PyPI page did
   not load, so its version and classes are not confirmed. Nobody tried whether either one fits an ST7789 or an
   e-paper driver. Spark still owns the outside parts, such as the LED and the button.
7. ESP-IDF's Linux target builds C code for the computer. It does not run MicroPython, so it is not relevant.
8. Cirkit Designer: one search result on hackster.io, whose page returned 403. Nothing else is confirmed.

## Five lines for the strategy seam

1. A board Wokwi lacks: no open option drives the pins of a C6 today. QEMU boots the C6 with no GPIO, I2C or SPI.
   Velxio covers the ESP32, S3 and C3 only.
2. For an S3 or C3 board, self-hosted Velxio is the only candidate with an outside API. It is AGPL and heavy to set
   up, so it can run only as a separate process.
3. A run with no paid minutes: a logic-level backend on spark's own stand-in is the cheapest, as in option B of the
   2026-10-18 finding. A maintained fake of `machine` can carry its generic part.
4. So the seam can hold three strategies: Wokwi, the stand-in at logic level, and later Velxio or QEMU. The C6 stays
   open until QEMU drives its pins.
5. Before any plan rests on Velxio: confirm that it loads a MicroPython image, and what an ST7789 or an e-paper part
   needs there.
