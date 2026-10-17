# Platform lens: what changes to serve Arduino, PlatformIO, ESP-IDF (P221 #203, epic P286 #336)

Summary: the board facts, the pin numbers, the diagram and the scenario YAML stay. The firmware's language (pins.py), the file tree, the
image build, the REPL tools and the "import it on the Mac" test all assume MicroPython and change. Wokwi itself is not the blocker.

## Change map (stage | file:line | MicroPython assumption | Arduino (arduino-cli) | PlatformIO | verdict)
| Stage | Where | Assumes | Arduino | PlatformIO | Verdict |
|---|---|---|---|---|---|
| Pin map | assign_pins.py:392-425 pin_module; check_spine.py:88 PIN_MODULE=firmware/pins.py; :860 | Output is a Python module `NAME = 12`; `_PULL = "up"` comment names `Pin.PULL_UP` | `pins.h` with `constexpr int NAME = 12;` | same `pins.h` in `include/`; or `-D` flags in platformio.ini | Facts stay (signal, gpio, pull). Rendering changes: one renderer per language |
| Pin map header | assign_pins.py:~430 PIN_MODULE_HEADER | `# ` comment, used to tell spark's file from a person's | `// ` header | same | Changes (per renderer) |
| Pin-code guard | restricted_pins.py:12-16; board_live.py | Parses `Pin(n)` in Python with ast | Needs a C++ parse, or drop for compiled platforms (no live code) | same | Changes (behaviour of a check); the restricted-pin facts stay |
| Firmware tree | run_scenario.py:142 needs firmware/main.py; import_firmware.py:12 (boot.py, main.py, lib/) | `firmware/main.py` boots on its own; files copied to flash | `<name>/<name>.ino` | `src/main.cpp`, `platformio.ini`, `include/` | Changes: a "firmware layout" per platform |
| Harness (Mac test) | import_firmware.py; scripts/stand_in/machine.py; tests/test_import_firmware.py | Imports modules with a fake `machine` on CPython | No equivalent: compile-only (`arduino-cli compile`) or host unit tests (PlatformIO `native` env) | `pio test -e native` with a fake Arduino.h; or compile-only | Changes. Largest loss: "import it" becomes "it compiles" |
| Build step | none today (MicroPython is a download) tools.json:10,24,150-162 | `firmware-image` = a prebuilt interpreter .bin | `arduino-cli compile --fqbn esp32:esp32:<board> --output-dir` (needs the esp32 core, 3.x for C6) | `pio run` (stock espressif32 lacks C6; community fork pioarduino carries it) | New stage; no code now |
| Image | flash_image.py:3-17,63-90; board record `micropython_port` boards/*.json:7 | Interpreter .bin + littlefs files in one image at partition offsets | Compile output already has bootloader, partitions, app; merge with `esptool merge_bin` (or the .ino.merged.bin) | `pio run` writes firmware.bin; flasher_args.json | flash_image.py is MicroPython-only. Board record needs `firmware_kind` or a map, not one `micropython_port` key |
| Wokwi project | sim_project.py:167-201 wokwi_toml, UNNAMED_FIRMWARE:185 | `firmware = "flash-with-firmware.bin"` | Same keys: `firmware` (.bin/.elf) plus optional `elf` | `firmware = .pio/build/<env>/firmware.bin`, `elf = ...firmware.elf` (Wokwi docs) | Stays: diagram.json, chips, scenario YAML. Only the two path lines change |
| Simulation run | run_scenario.py:12-16,115,142; DEFAULT_IMAGE:49 | Needs main.py; serial log joins MicroPython lines; `ready` text | wokwi-cli runs .bin/.elf; serial text same | same | Mostly stays (wokwi-cli is language-blind). Change: the main.py precheck, the image rebuild per run |
| Deploy: flash | deploy.py:9-20,50,108-110 IMAGE_OFFSET=0x0 | esptool erase + write one image at 0x0 | esptool write of the merged image (0x0), or `arduino-cli upload` | `pio run -t upload` | Stays if image is merged (esptool path). Uploader tools differ if not |
| Deploy: files | deploy.py:73,162,238; ready_check.py:21-65 | mpremote copies files, hashes them on board, `import main`, reads `ready` | No file copy (the app is in flash). Verify = read serial for `ready` after reset | same | Changes: hash-on-board check is MicroPython only; serial `ready` stays |
| Console/REPL | board_connection.py:6,20,58-65; board_console.py; reach.py; live.py; board_live.py (P235, P247) | mpremote raw REPL; run code on board; `mpremote reset` | No REPL. Serial monitor only (read). `live` has no meaning | same | Changes: live and reach become "read serial" only. REPL features are MicroPython-only |
| Board look, doctor | board_look.py (PortFinder uses `mpremote devs`; EsptoolReader), board_doctor.py, board_grant.py:13 | mpremote lists ports; esptool reads the chip | `arduino-cli board list` or pyserial/esptool | `pio device list` | EsptoolReader and the grant stay. PortFinder = a seam |
| Tools list | data/tools.json:15-16 `flasher`, `board-shell` | roles named after MicroPython tools | add `compiler` (arduino-cli) | add `compiler` (pio) | Roles are already by job: stays, add roles |
| Breadboard text | breadboard.py:312 | "pull it up with Pin.PULL_UP" | `pinMode(x, INPUT_PULLUP)` | same | Changes (wording per platform) |

Stays everywhere (facts): board records minus the one key (pins, roles, wake, restricted), parts, needs, pin assignment, diagram.json, breadboard sheet,
netlist, checks, scenario YAML, Wokwi chips, esptool read of the chip, the grant, the `ready` serial proof.

## Seams spark needs (named by role)
1. FirmwareLayout: where the files go and which one boots (main.py, .ino, src/main.cpp).
2. PinMapRenderer: facts in, one language out (Python, C++ header). Header marker per renderer.
3. FirmwareBuilder: turns the project into a flashable image (MicroPython: flash_image; Arduino/PlatformIO: compile then merge).
4. FirmwareCheck: what "the firmware is sound on the Mac" means (import with stand-in; compile; native test).
5. BoardShell: copy, run, reset on the board; null for compiled platforms.
6. FirmwareVerifier: how deploy proves the flash (hash files then ready; or ready alone).
7. Board record key: `micropython_port` becomes a map `firmware_images: {micropython: ..., arduino: fqbn}`.
Keep open now: do not add more `Pin(`/mpremote text outside renderers and shell classes; name the platform in the project record.

## Three questions the real spike still answers (pass line)
1. Does Wokwi run an arduino-cli build for the XIAO ESP32-C6 from the existing diagram.json and scenario? Pass: wokwi-cli exits 0 on the existing blink scenario with `firmware=...merged.bin` and the `ready` text seen. (Wokwi doc says ESP32 takes .bin/.elf; C6 chip support not proved here.)
2. Can one pins.h and one pins.py come from the same facts with no second source of truth? Pass: both render from one assign result; a test shows same name/gpio set; a sketch using pins.h compiles for the C6.
3. Can deploy prove an Arduino flash without a REPL? Pass: esptool writes the merged image on a real C6, board resets, serial shows `ready` within the wait, exit code and JSON match MicroPython's shape.

## Cost guess
- Arduino (arduino-cli): medium. Reasons: new build stage, image merge, renderer, layout, a compile check in place of import; deploy and Wokwi mostly reuse. Needs esp32 core 3.x for C6 (Arduino-ESP32 docs; one search, not read in full).
- PlatformIO: medium-large, a step above Arduino. Same work plus a toolchain config file, and stock platform-espressif32 lacks C6; the community pioarduino fork carries it (search result: cnx-software 2024-08-27). A free tool, but fork risk. Wokwi has a documented PlatformIO example.
- ESP-IDF: large. CMake project, sdkconfig, partition tables, `idf.py`, flasher_args.json (Wokwi accepts it). Pin header is C again. Heavy install, against "user installs nothing heavy".
- Others (Rust, CircuitPython): CircuitPython small-medium (near MicroPython: same renderer, other image); Rust large.
Sources: https://docs.wokwi.com/vscode/project-config ; https://docs.platformio.org/en/latest/boards/espressif32/esp32-c6-devkitc-1.html ; https://www.cnx-software.com/2024/08/27/platform-espressif32-fork-platformio-arduino-esp32-c6-esp32-c5-esp32-h2-esp32-p4/
