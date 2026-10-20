# P221 lens: the chain, file by file (Arduino C++ instead of MicroPython)

Read in the code: firmware_platform, flasher, flash_image, ready_check, board_connection, board_facts, import_firmware, sim_project,
run_scenario, deploy_service, restricted_pins, assign_pins (pin_module), check_spine (keep_pins), board_look (PortFinder), tools.json,
commands/*.md (grep only). Read from PR #414 (origin/p323-target-architecture): design.md D-table, section 2.1, the class diagram, line 182.
Everything marked "unverified" I did not open.

## Short answer
The chain is two halves. Up to the diagram and the breadboard sheet it is language-blind. From the pin map down (image, import test,
simulation image, deploy, ready read) it assumes a MicroPython file system and a REPL. Only one real seam exists today: `FirmwarePlatform`.
Everything else needs one, or leaks MicroPython by name.

## The chain, stage by stage
Verdicts: STAYS / STRATEGY (one core, a platform picks) / TWIN (MicroPython-only, Arduino needs its own) / SKIP (not in an MVP).

| Stage | Files | Verdict | Evidence | Refactor to a clean seam | Worth it for MicroPython alone? |
|---|---|---|---|---|---|
| Idea, parts, drawer, needs, cost | idea/research/drawer commands, parts.py, drawer.py, matching.py, needs.py, cost.py | STAYS | no firmware text in them (unverified: not opened) | none | n/a |
| Board record | boards.py, boards/*.json | STRATEGY | one key `micropython_port` boards/xiao-esp32-c6.json:9; read at flash_image.py:89 | `FirmwarePlatform` reads its own fact (`micropython_port`, `arduino_fqbn`); PR #414 line 182 says the same. Rest of the record stays | Yes: removes a MicroPython word from a board fact |
| Pin map | assign_pins.py:392 `pin_module`, :426 `PIN_MODULE_HEADER`; check_spine.py:88 `PIN_MODULE`, :890-925 `keep_pins`; commands/build.md:112-117 | STRATEGY | writes Python: `NAME = 12 # ...`, `_PULL = "up"`, text `Pin.PULL_UP` (:414); the "ours or a person's" test is a `#` header at check_spine.py:896; the name test is `isidentifier()` :408 | `PinMapRenderer` class: facts (signal, gpio, pad, why, pull) in, text out, plus file name and header marker. `pin_module` becomes `PythonPinMap`; `CppPinMap` writes `pins.h` (`constexpr int`). #414 puts it as `pin_map_text(design)` on the platform. The facts list is already built apart from the text (:405-423) | Yes: one function does facts and text now |
| Pin-map target path | check_spine.py:88 `firmware/pins.py` | STRATEGY | one constant | the renderer names its file (`pins.h`, in the sketch folder for Arduino) | Yes, small |
| Breadboard sheet | breadboard.py, breadboard_*.py | STAYS, one sentence | only breadboard.py:331 says `Pin.PULL_UP` and `pins.py` | the renderer gives the pull-up wording (`INPUT_PULLUP`) | Yes, small |
| Firmware tree | run_scenario.py:142 needs `firmware/main.py`; flash_image.py:37 `files_under`; import_firmware.py:42 `BOOT_FILES` | STRATEGY | main.py hard-coded in three modules | `FirmwareLayout` (boot file, source globs, what "nothing to import" means). Arduino: `firmware/firmware.ino` plus `pins.h`; the folder name must equal the .ino name | Yes: three modules share one fact |
| Mac check ("import it") | import_firmware.py:38-75 (`IMPORT_ONE`, `STAND_IN`), scripts/stand_in/machine.py | TWIN | imports every module on CPython with a fake `machine`; no C++ equivalent | `FirmwareCheck` strategy: MicroPython = import with stand-in; Arduino = `arduino-cli compile` (compile only, no host run). Output keys (`modules`, `problems`) stay | Yes: it becomes a named Strategy, the door already is thin-ish |
| Image build | flash_image.py:63 `image(interpreter, files)`, :74 `board_build`, :102 `interpreter_path`; tools.json:10 role `firmware-image`, :24 contract, :150-190 three interpreter entries, `littlefs` role :9 | TWIN | MicroPython .bin plus littlefs at 0x200000 (:31). Arduino has no filesystem and no interpreter: a compile (esp32 core) then merge bootloader+partitions+app | `FirmwareBuilder.make_image(project)` (#414 names it `make_image`). MicroPython: today's `image`. Arduino: new `compiler` role (arduino-cli) in tools.json, which already names roles by job (:3-16) | Yes: removes the `--micropython` flag from run_scenario |
| Simulation project | sim_project.py:167-201 `wokwi_toml`, `firmware_lines`, :185 `UNNAMED_FIRMWARE` | STAYS (two lines) | `firmware = <image>` and `elf = <same image>` (:177-178); Arduino needs `elf` to be the real .elf. diagram.json, chips, scenario YAML are language-blind (unverified for C6 on Wokwi) | builder returns (image, elf); `firmware_lines(image, elf=None)` | Yes, tiny |
| Run scenario | run_scenario.py:130-160 `ScenarioRun`, :142 main.py check, :150 `flash_image.image(...)`, :239 `--micropython`, :38 `READY`, :66 `with_ready_wait`, :87 `image_in`, :226 `file_hashes` | STRATEGY | wokwi-cli itself is language-blind; the class mixes check, image build and run | `SimulationEngine` (#414: `prepare`, `run`) with `WokwiCliEngine` as Adapter; `problem()` asks the platform's layout and builder. `READY` and the wait step stay | Yes: a core class plus a thin door, #414's shape |
| Ready proof, simulation | run_scenario.py:114-116 reads `ready` on serial | STAYS | text on serial, language-blind | none | n/a |
| Deploy: look | board_look.py:67 `PortFinder` runs `mpremote devs`; :117 `EsptoolReader` | STRATEGY | the port list uses the MicroPython tool; the chip read uses esptool and stays | `PortFinder` takes a "list ports" command from the platform (or pyserial). EsptoolReader, tokens, grant, gate stay | Yes, small |
| Deploy: flash | flasher.py:35-66 `EsptoolFlasher`, `IMAGE_OFFSET = "0x0"`; deploy_service.py:96-110; firmware_platform.py:34 | STAYS | erase plus write one image at 0x0 works for a merged Arduino image too. `Flasher` base already a Strategy (:18). deploy_service already takes the platform (deploy_service.py:70) | the merged-image step lives in the builder, not the flasher | n/a: seam exists |
| Deploy: put files, facts | board_facts.py:19 `FACTS_FILE spark.json`, :36-52 `FactsFile` via `copy_to_board`/`read_file`; deploy_service.py:150-193 | TWIN / SKIP | needs a file system on the board; Arduino has none (a LittleFS sketch would be firmware's work, unverified) | `BoardFactsWriter` strategy; Arduino version is "none: facts come from the flash read", or the firmware prints them on serial. MVP: skip, record "facts unavailable" | Yes: the deploy then says what it cannot prove |
| Deploy: ready read | ready_check.py:21-65 `HASH_FILES`, `ReadyCheck.check`; board_connection.py:50-103 `run_code`, `copy_to_board`, `read_file`, `reset`, `repl_command` | TWIN | hashes files on board, then `import main`, both through the raw REPL. Arduino: reset (DTR/RTS via esptool or pyserial), read serial for `ready` for N s. Hash check becomes "the flashed bytes read back equal the image" (esptool `verify_flash`, unverified) | `BoardConnection` split in two roles: `SerialReader` (reset, read) which every platform has, and `BoardShell` (exec, cp, cat) which MicroPython adds. `FirmwarePlatform` already holds `make_connection` and `make_ready_check` (firmware_platform.py:41-76) so the seam exists; only the Arduino implementations are missing | Yes: today `ReadyCheck` is typed to a REPL, so a REPL error and a serial error look alike |
| Download-mode recovery, console probe | deploy_service.py:162-175; board_console.py; download_mode.py | STAYS | reads the port with DTR/RTS off; no REPL (platform's `make_console_probe` takes a shell tool, firmware_platform.py:57 - the tool is mpremote for a flag only; unverified that pyserial can replace it) | probe takes a serial opener | Small |
| Live code, reach | live.py, board_live.py, reach.py, restricted_pins.py:12-30 | SKIP | run code on the board; `restricted_pins` parses Python with `ast` (:12) | `LiveTry` stays MicroPython-only; Arduino platform returns "no live" and `check`s say so. #414 puts them in `bench` | No: only worth it when Arduino lands |
| Tools, setup | data/tools.json, tools.py, commands/setup.md | STRATEGY | roles `flasher`, `board-shell` are job names (tools.json:15-16); `firmware-image` and its contract name MicroPython (:10, :24) | add roles `compiler` (arduino-cli) and `firmware-image` per platform; Arduino core 3.x for C6 (unverified, from platforms.md) | Yes: rename the contract by job |
| Docs and commands | commands/build.md:231-237, deploy.md:61-87, agents.md:117, :370 | STRATEGY | prose names mpremote, REPL, `--micropython` | one platform line in each page | Yes |

## Where the platform is chosen today
`deploy.py:171` hard-codes `FirmwarePlatform.micropython(args.project)`. `run_scenario.py` and `flash_image.py` do not use `FirmwarePlatform` at all
(they call `flash_image` directly), so two halves of the chain pick MicroPython in two places. PR #414 decides: one `platform` key in
requirements.json, default `micropython`, the only choice (design.md line 182, D-table row 54). Without that key no Arduino work can start.

## What the platform object must carry (compare #414)
#414 draws `FirmwarePlatform { make_flasher, make_connection, pin_map_text(design), make_image(project) }`. Today's class (firmware_platform.py:41)
has `make_flasher`, `make_shell_command`, `make_connection`, `make_ready_check`, `make_console_probe`. From the chain above it also needs:
`layout()`, `make_firmware_check()`, `make_facts_writer()`, and a flag `supports_live`. Four more parts than #414's sketch; each already
exists as a hard-coded call in one module. Tell #414's owner (unverified: I did not read #414 beyond the lines cited).

## MVP cut (this lens only; cost and board lenses may differ)
1. `platform: arduino` in requirements.json; one `ArduinoPlatform` in `FirmwarePlatform`'s shape.
2. `CppPinMap` renderer, `firmware/firmware.ino` plus `pins.h`. Check "ours" by a `//` header.
3. `arduino-cli compile` as check and as builder; merge to one image; `wokwi.toml` with `firmware` and `elf`.
4. Simulation unchanged except the two toml lines and the main.py precheck. The wokwi-cli run on the C6 is unproved (platforms.md question 1).
5. Deploy: look, gate, grant, esptool erase and write stay as they are. Ready read = reset and read serial for `ready`.
6. Skip: facts file on board, file-hash check, live code, reach, restricted-pin parse, PlatformIO, ESP-IDF.
What the person loses in the MVP: "import it on the Mac" becomes "it compiles"; no proof that the board's files match the passed run, only that
the flashed image bytes match (esptool read-back, unverified).

## Risks and unknowns
- Arduino sketches cannot be run on the Mac, so the only pre-simulation test is the compiler. Behaviour tests happen in Wokwi (a paid minute each).
- `ReadyResult` verdicts (SEEN/NOT_SEEN/UNKNOWN) and the `ready_check.py` log keys feed the deploy JSON; keep them (agents.md contract).
- Name check: the word "firmware" means the person's code (`firmware/`), the interpreter+files image (`flash_image`), and the platform
  (`FirmwarePlatform`). Pick one word each before Arduino (matches #414's "firmware names four things" row).

## Order if refactoring first (each step is useful for MicroPython alone)
1. `platform` key plus one place that picks it (deploy.py:171, run_scenario, flash_image).
2. `PinMapRenderer` out of `pin_module` (the smallest real seam; testable with the two renderers).
3. `FirmwareLayout` (the main.py constant in three modules).
4. Split `BoardConnection` into `SerialReader` and `BoardShell`.
5. `FirmwareBuilder` and `FirmwareCheck`; then `ArduinoPlatform` is additive.
