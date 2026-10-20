# P221 lens: the board side and the deploy without a REPL (Sonnet, 2026-10-20)

Summary: the deploy keeps its spine (esptool write, wait for `ready` on the serial console). Three steps that need the MicroPython
REPL disappear or move: the file copy, the file hashes on the board, and `import main`. Each has a cheaper compiled-firmware
substitute. What the person loses is the live loop (poke, edit, rerun), not the proof that the right image runs.
Claims marked (measured) were run on this Mac 2026-10-20; (unverified) were not.

## Step by step: what replaces what
| Today (file:role) | Arduino (arduino-cli) | Verdict |
|---|---|---|
| flash_image.py: MicroPython .bin + littlefs of firmware/ at 0x0 | `arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32C6 --export-binaries` writes bootloader, partitions, app, and a `*.merged.bin` (unverified for core 3.x on C6; `esptool merge-bin` is the fallback, and esptool 5.5.0 here has it, measured) | Replaced by a compile stage. No littlefs. |
| flasher.py EsptoolFlasher: erase_flash, write_flash 0x0 image | Same two commands with the merged image at 0x0 (the merged image is the whole flash from byte 0, like today's) | Stays unchanged |
| board_connection.py: `fs cp` of spark.json, `fs cat` read back | No filesystem to copy to. See "facts" below | Removed or moved |
| ready_check.py HASH_FILES: sha256 of each file on the board, run via raw REPL | Not possible on board. Substitute: `esptool verify-flash` (or `read-flash` + hash on the Mac) of the app region against the built image. This proves the bytes are the image, which is stronger than file hashes | Replaced by esptool; runs without the firmware running |
| ready_check.py `import main` + READY_WAIT_S read | Reset the chip (esptool `--after hard-reset` already does it; or DTR/RTS toggle with pyserial) and read the console for `ready` | Simpler: no REPL needed to start the firmware, it boots by itself |
| board_connection.reset(): `mpremote reset` | Hard reset by esptool, or pyserial RTS pulse. The C6 uses native USB-Serial/JTAG; a reset by RTS works there (unverified on this board, ConsoleProbe already opens with DTR/RTS off for the opposite reason) | Needs a small new class |
| board_console.py ConsoleProbe: pyserial run through mpremote's Python | Already pyserial. It runs under mpremote's Python only because that has pyserial. esptool depends on pyserial too, so esptool's Python has it (esptool needs pyserial: unverified in its metadata, but its code imports `serial`). The probe can use esptool's Python and drop mpremote | Stays, one line changes (which Python) |
| download_mode.py: `waiting for download`, press R, `ready` heard | Identical. It reads the ROM's words and the firmware's `ready` from the console, language-blind | Stays |
| deploy_service.py `_read_board` facts + hashes + ready | Reduce to: verify-flash, reset, wait for `ready`. DeployResult keeps its shape (`ready` verdict, `image_sha256`, log); `repl_command` becomes None or "serial monitor command" | Smaller |
| tools.json roles `flasher`, `board-shell` | `board-shell` has no Arduino meaning: make it a `console` role (pyserial). Add a `compiler` role (arduino-cli) | Roles by job: add two |

## The facts without spark.json
Today spark.json (project, board, mac, image sha256, file hashes, time) is copied to the board and read back. Options:
1. Do not put facts on the board. The Mac already holds the image sha256 (board_facts.record_deploy keys by MAC read by esptool).
   The proof is verify-flash against that sha256. The board holds nothing to drift. Simplest, and it matches "spark exports facts".
2. Compile a facts string in: a generated `spark_facts.h` (project, board, build time, a build id) and the sketch prints it with `ready`
   (`ready <build-id>`). Deploy reads it from the console. Cost: the image changes per build id, so the id must be derived from
   the sources, not the clock, or the image sha256 stops being reproducible. Only worth it to prove the running build (not just the flash).
3. NVS or a spare partition: needs a write step (esptool write_flash at a partition offset from a generated .bin, or `nvs_partition_gen`).
   More moving parts, and no reader on the board without firmware code. Reject for the MVP.
Recommendation: option 1, plus the build id in the `ready` line only if the PO wants "which build runs" proved on the console.

## `ready` and the console
- pyserial is already used (board_console.READ_CONSOLE). Baud 115200 is the same; native USB-CDC on the C6 ignores baud (unverified).
- Arduino C6 gotcha (unverified): with `USB CDC On Boot` disabled, `Serial` goes to UART0, not to the USB port, and the console is silent.
  The fqbn needs `:CDCOnBoot=cdc` (or the sketch uses `HWCDC`). Wrong option = a silent board that looks like a failed deploy. Pin it in the board record.
- Early boot: the ROM and the Arduino core print their own lines before `setup()`. `ready` must be printed by the sketch after setup, as today.
- An Arduino sketch that never calls `Serial.begin` prints nothing. The firmware rule (print `ready`) must be a generated header
  or a template, not left to the conversation (spark exports facts, the firmware prints them).

## Wokwi
Wokwi runs a `.bin` or `.elf` for ESP32 targets (docs.wokwi.com/vscode/project-config, per platforms.md). Whether wokwi-cli accepts the
C6 with an arduino-cli merged image is platforms.md's question 1 and is still unproved. The simulator loads the image from address 0,
the same as the flasher, so the one merged image serves both (today's design, kept). The `ready` check in the scenario is unchanged.

## What the person loses
- No REPL: no poke at a pin, no `print(sensor.read())` on a live board, no live edit of one file. reach.py, live.py, board_live.py (P235, P247) lose
  their reason. Replacement is read-only: serial monitor, and prints the firmware chooses to emit.
- The loop: MicroPython edit then `fs cp` then reset took seconds. Arduino is edit, compile, flash, wait for boot. Compile time:
  a cold first build of the core is minutes, an incremental sketch build is seconds to tens of seconds (typical figures, unverified here).
- Toolchain install (measured): `~/Library/Arduino15/packages/esp32` is 5.5 GB on this Mac, mostly tools (esp-rv32 2.0 GB, esp-x32 1.1 GB,
  per-chip libs ~220-240 MB each, c6-libs 242 MB). Part is likely older versions and chips the C6 does not need, so a fresh C6-only install is
  smaller (unverified; the download for one core is commonly quoted in the hundreds of MB to ~1 GB). arduino-cli itself is not installed here.
  Compare MicroPython: one ~2 MB .bin download. This collides with "a user installs nothing heavy" (AGENTS.md). KiCad-style optional would apply.
- The Mac-side import test (stand_in/machine.py) has no equivalent: "it imports" becomes "it compiles".
- Gained: speed on the board, types, no interpreter RAM overhead, real interrupts and timing. A compile catches typos that MicroPython finds only at run time.

## MVP for the board side (smallest that works end to end)
1. `compiler` role in tools.json (arduino-cli) and a pinned core version in the board record (`firmware_images` map, per platforms.md seam 7).
2. FirmwareBuilder: `arduino-cli compile` with fqbn + CDCOnBoot option, then merged .bin, sha256 of it.
3. EsptoolFlasher reused as is.
4. `ArduinoVerifier` (new, behind FirmwarePlatform.make_ready_check): `esptool verify-flash` then reset then read console for `ready` with
   the existing ConsoleProbe. Returns the same ReadyResult, so DeployService.verify and the board log change little.
5. board_facts: drop FactsFile for this platform; keep record_deploy by MAC.
FirmwarePlatform already has the seams (make_flasher, make_connection, make_ready_check, make_console_probe). Add `FirmwarePlatform.arduino()`;
make_connection returns a null connection whose `repl_command` is a monitor line. About a small-to-medium change confined to the deploy side;
the large cost is outside this lens (pin renderer, firmware layout, compile check).

## Refactor: the seams, by role (PO scope 2026-10-20)
Today `FirmwarePlatform` (firmware_platform.py) is a bag of five factories, and `DeployService.verify` still knows MicroPython
(facts file, file hashes, `expected` {path: sha256}). Arduino is the chance to move that knowledge behind four strategies.
| Seam (role name) | Question it answers | MicroPython strategy (today) | Arduino strategy |
|---|---|---|---|
| ImageBuilder | project to flashable image + its sha256 | flash_image.py: interpreter .bin + littlefs of firmware/ | arduino-cli compile, then merged .bin |
| ImageEvidence (PR #454, image_evidence.py) | what tested this image; which files should be on the board | PassedRunEvidence: a sim run passed on the image sha256; `expected_files` = per-file sha256 | Same class works if the run is by image sha256. `expected_files` returns {} (one blob, no files) |
| Flasher (exists) | commands that put the image on the board | EsptoolFlasher | Same class |
| BoardProof (new; replaces ReadyCheck + FactsFile) | is what runs on the board the image that passed | REPL: file sha256 on board, facts copy, `import main`, read ready | esptool verify-flash on the image, hard reset, read ready |
| ConsoleReader (exists as ConsoleProbe) | what did the board print; is it in download mode | pyserial via mpremote's Python | pyserial via esptool's Python; same code |
| BoardShell (optional) | run, copy, reset on the board | BoardConnection (mpremote) | none: a null object whose reset is a serial pulse |
Design notes:
- BoardProof returns the ReadyResult shape (verdict, sentence, log) that exists, so DeployResult, the board log and JSON stay stable.
  `ready` is the last step of both proofs and is the one shared step, so make ReadyCheck a part: `ConsoleReady(console).wait(READY, s)`.
- `DeployService.verify` becomes: `proof = platform.make_proof(...)`, `proof.check(image, evidence.expected_files(image))`, then the
  existing download-mode recovery. The recovery moves out of verify into a decorator `RecoveringProof` (like RetryingBoardConnection).
- Replace `FirmwarePlatform`'s five factory callables by one `FirmwarePlatform` with three members: `builder`, `flasher`, `proof`
  (+ `console`). Classmethods `micropython(project)` and `arduino(project)` assemble them. Callers ask for roles, never for mpremote.
- ImageEvidence already has the right shape: it holds settings, takes a fresh image, and returns files. Its `expected_files` is the one
  MicroPython-shaped method; name that explicitly (an empty dict is a valid answer, and today `{}` means "an older spark": give it a code, not a
  silent sentence, per no-magic-strings).
- Board record: `micropython_port` becomes `firmware_images: {micropython: ..., arduino: {fqbn, core}}` (platforms.md seam 7).
- Names: one word per thing. "proof" (on the board) vs "evidence" (before the flash) vs "ready" (the console line). Do not call all three "check".

## Risks to test on the bench (cheap spikes)
1. Does a merged image from the core's own `--export-binaries` boot at 0x0 on the C6? (unverified)
2. Does verify-flash work on the C6 over USB-Serial/JTAG after a hard reset without leaving download mode? The P243-P245 trouble (board stays in
   download mode after the first flash) is chip behaviour and will recur: the download_mode recovery must stay.
3. Is `ready` visible with the chosen CDCOnBoot option, and within READY_WAIT_S including the 2nd-stage bootloader?
4. Does `esptool read-flash` of the app region hash equal the image (the merged image's padding and the erased tail differ in size)?
   Verify only the image's length.

## Sources
- Repo: scripts/ready_check.py, deploy_service.py, board_connection.py, board_console.py, download_mode.py, flasher.py, firmware_platform.py; platforms.md.
- Measured: `du` of ~/Library/Arduino15/packages/esp32 and `esptool --help` (5.5.0) on this Mac, 2026-10-20.
- No web search run (token budget; the compile-time and install-size figures are the weak spots, marked unverified).
