# P221 round 2: ESP-IDF and PlatformIO facts

2026-10-20. Facts for the XIAO ESP32-C6, each with a source. "UNVERIFIED" means no first-hand source was read.
Sources: Espressif docs MCP (docs.espressif.com, "latest" = v6.x), docs.wokwi.com, PlatformIO forum. Nothing was installed or run.

> **TL;DR.** ESP-IDF fits spark's deploy best: it builds a bootloader, partition table and app, merges them into one
> `.bin` at 0x0 with `idf.py merge-bin`, and the C6 console works over USB. PlatformIO is a build front end, not a
> third platform: its C6 support rides on espidf or on a third-party Arduino fork. Wokwi runs both, from `flasher_args.json`
> (IDF) or `firmware.bin` + `firmware.elf` (PIO).

## 1. Layout, minimal blink-and-button
- ESP-IDF (C or C++): `CMakeLists.txt` (`cmake_minimum_required`, `include($ENV{IDF_PATH}/tools/cmake/project.cmake)`,
  `project(name)`), `main/CMakeLists.txt` (`idf_component_register(SRCS "main.c" INCLUDE_DIRS ".")`), `main/main.c`
  (`app_main`), optional `sdkconfig.defaults`, optional `main/idf_component.yml` (only for registry components).
  The pytest guide shows the same `main/` + `CMakeLists.txt` shape:
  https://docs.espressif.com/projects/esp-idf/en/latest/esp32/contribute/esp-idf-tests-with-pytest.html
  The file names above are from general knowledge of IDF, UNVERIFIED in this run. `idf.py set-target esp32c6` once.
- PlatformIO: `platformio.ini` (`[env:x] platform=espressif32, board=..., framework=espidf|arduino`), `src/main.c(pp)`
  (Arduino: `setup`/`loop`; espidf: `app_main`), `include/`. UNVERIFIED in this run (general knowledge).
- Arduino as a component: IDF can pull `arduino-esp32` as a component; PIO selects it with `framework = arduino` (see 6).

## 2. Where a generated pin map fits (facts only)
- A header `pins.h` (`#define PIN_BUTTON 0`) works in all three: a C header is plain text for IDF, PIO and Arduino.
  This is the one form that is the same across platforms. Spark writes it, the conversation writes `main`.
- Kconfig / `sdkconfig.defaults` carries numbers too (`CONFIG_...=`), but it needs a `Kconfig.projbuild` and is IDF-only.
  A PIO build flag `-DPIN_BUTTON=0` in `platformio.ini` works too. Both are more moving parts than a header.
  Design judgement, not a sourced fact. Recommendation: one `pins.h`, include `pins.h` from `main`.

## 3. Build, outputs, one merged image
- Build: `idf.py build`; `idf.py merge-bin [-o file] [-f raw|hex|uf2]` writes one file `merged-binary.bin` in `build/`:
  https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/api-guides/tools/idf-py.html#merge-binaries-merge-bin
  It merges bootloader, partition table, app and other partitions; raw format flashes at 0x0 (`--flash-offset` changes it).
- C6 offsets: the bootloader is at 0x0 on the C6 (partition-table page, `primary` bootloader "located at the 0x0 address"),
  the partition table at 0x8000 (`CONFIG_PARTITION_TABLE_OFFSET`), the factory app at 0x10000:
  https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/api-guides/partition-tables.html
  Warning: the esptool C6 page's own `merge-bin` example puts the bootloader at 0x1000, which is the old ESP32 value.
  Do not copy it. Take offsets from `build/flasher_args.json` or `@flash_args`:
  https://docs.espressif.com/projects/esptool/en/latest/esp32c6/esptool/basic-commands.html#merge-binaries-for-flashing-merge-bin
- `esptool --chip esp32c6 merge-bin -o merged.bin @flash_args` (run in `build/`) is the esptool route. It also takes
  `--flash-mode/--flash-size/--flash-freq` and rewrites the header on the output.
- PIO: `pio run` writes `.pio/build/<env>/firmware.bin` (app only, 0x10000), plus bootloader and partition files.
  No built-in merged target. Wokwi's docs give an extra script that runs esptool `merge_bin` after every build and writes
  `firmware.merged.bin`: https://docs.wokwi.com/vscode/platformio . Flash offsets can be read from a verbose upload
  (forum: https://community.platformio.org/t/esp32-how-to-create-one-solid-firmware-package-that-will-include-bootloader-etc-in-a-single-file/24379).
  PIO's Arduino merged image on the C6: UNVERIFIED.

## 4. Flash and verify
- IDF: `idf.py flash` calls esptool underneath; the USB Serial/JTAG port puts the C6 into download mode by itself:
  https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/api-guides/usb-serial-jtag-console.html
- PIO: its upload uses esptool (`tool-esptoolpy` package, named in Wokwi's docs above). Direct statement: UNVERIFIED.
- Spark can keep its own esptool call: `write-flash 0x0 merged.bin` is the documented way to use a merged file
  (esptool page above). So the deploy stays unchanged for IDF and PIO as it is for Arduino.
- MD5 verification: esptool's `write-flash` verifies by default and `verify-flash` exists. Not re-read in this run,
  UNVERIFIED here; the finding.md already relies on `verify-flash`.

## 5. Console and the `ready` line
- C6 console: the default `CONFIG_ESP_CONSOLE_UART` is UART0 (`CONFIG_ESP_CONSOLE_UART_DEFAULT`). The size guide says
  "for targets that support USB-Serial-JTAG, both the USB-Serial-JTAG and UART console output are enabled by default"
  (the secondary, output-only console):
  https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/api-guides/performance/size.html#console
  So printing works on the XIAO's USB port with no change. Input (a REPL) needs
  `CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y` in `sdkconfig.defaults` (usb-serial-jtag-console page above). Secondary output is
  non-blocking only (kconfig `CONFIG_ESP_CONSOLE_SECONDARY`). The ROM prints to both UART0 and USB by default (datasheet 3.3).
- `ready` line: `printf("ready\n")` or `ESP_LOGI` after setup, in `app_main`. `ESP_LOGI` adds a prefix and colour codes;
  plain `printf` is safer for a parser. Judgement, not sourced.
- Monitor: `idf.py monitor`; PIO `pio device monitor`. Spark can read the port itself (as now for MicroPython).
- Boot noise: ROM and bootloader lines print before `ready` (bootloader log level can be lowered, bootloader page).

## 6. Install: size, time, free, versions
- ESP-IDF v6.0 (released 2026-03): EIM (ESP-IDF Installation Manager) is the recommended installer, GUI and CLI, via
  Homebrew: `brew install eim` / `brew install --cask eim-gui`; Python 3.10 minimum:
  https://developer.espressif.com/blog/2026/03/idf-v6-0-release/ and
  https://docs.espressif.com/projects/esp-idf/en/v6.0/esp32c5/get-started/macos-setup.html
  Free, local, no account. Disk size and install minutes: UNVERIFIED (not found; measure on a bench Mac).
  Heavy: it needs the IDF git tree, a RISC-V toolchain and Python env, bigger than PlatformIO Core alone. Estimate only.
- PlatformIO Core via `pip install platformio`: free, no account. Downloads toolchains on first build. Size/time UNVERIFIED.
- PIO and the C6: forum threads say official espressif32 supports the C6 with the espidf framework only (from
  espressif32 6.4.0); the official Arduino package (2.0.17, IDF 4.4.7) cannot do the C6. The workaround is the
  third-party pioarduino platform (Arduino core 3.x) plus a custom `seeed_xiao_esp32c6.json` board file:
  https://community.platformio.org/t/how-to-flash-xiao-seeed-esp32-c6/44742
  These threads are 2024 era. Today's (2026-10) state is UNVERIFIED. Risk: spark would depend on a third-party fork.
- Arduino as an IDF component: UNVERIFIED in this run (arduino-esp32 documents an "Arduino as an IDF component" mode).
  Arduino-cli (already in finding.md) remains the lighter Arduino path.

## 7. Wokwi
- IDF: `wokwi.toml` `firmware` = `build/flasher_args.json` (not a `.bin`), `elf` = `build/<project>.elf`; the diagram's
  board must match `idf.py set-target`: https://docs.wokwi.com/vscode/esp-idf . Espressif's C6 Wokwi page shows
  `wokwi-cli init`, and `idf.py wokwi` needs IDF 6.0+:
  https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/third-party-tools/wokwi.html
- PIO: `firmware` = `.pio/build/<env>/firmware.bin`, `elf` = `.pio/build/<env>/firmware.elf` (ESP32 boards), after `pio run`.
  Wokwi does not compile. https://docs.wokwi.com/vscode/platformio
- `wokwi-cli --expect-text "ready" --timeout 5000 --serial-log-file x.log` fits the `ready` line.
- Whether Wokwi simulates the C6 specifically for these builds: UNVERIFIED (docs list C6 in the Espressif page; the Wokwi
  C6 board part was not checked). Needs a `WOKWI_CLI_TOKEN` (a Wokwi account), which breaks "no account" for this step only.

## 8. Host tests
- IDF: Unity is bundled with IDF. The Linux target runs an IDF app on the Mac/Linux host (FreeRTOS Linux simulator,
  single core, `idf.py --preview set-target linux`), driven by pytest-embedded with `target='linux'`:
  https://docs.espressif.com/projects/esp-idf/en/latest/esp32/contribute/esp-idf-tests-with-pytest.html#single-dut-test-cases
  CMock for mocks (EDC22 talk: https://www.youtube.com/watch?v=HQcTWjOv8fM). Linux target on macOS (vs Linux only): UNVERIFIED.
  Drivers (GPIO etc.) are not available on Linux; logic that sits behind a thin pin interface is testable.
- PIO: `pio test -e native` with `platform = native` and Unity is the documented route. UNVERIFIED (search returned nothing).
- Both mean pure logic can be tested on the Mac without a board, if the firmware keeps logic apart from the driver calls.
  Spark writes facts only, so these tests belong to the conversation's firmware, not to spark.

## Open items (UNVERIFIED, for a bench or one more search)
Install size and time; PIO upload tool and merged image on the C6; esptool MD5 on write; Linux target on macOS;
PIO native test on this Mac; pioarduino status 2026-10; the Wokwi C6 board part for IDF builds.
