# P221 lens: the hidden ripple outside the deploy chain

Read with grep and a few `sed` reads over the tree (archive, observations, mutation tables excluded). "Unverified" = I did not open
the file around the hit. The three other lenses cover pins.py, flash_image, deploy, ready read: only named here when a silent wrong hides.
Seam that fixes most: ONE key, the project's platform, read from `boards/active.json` or the requirements file, by `FirmwarePlatform`.

## A. Silent wrong: a check says ok for what it cannot look at (worst, W1)

1. `scripts/import_firmware.py:11-20` (firmware import test, P59). Imports `firmware/*.py` with the `machine` stand-in
   (`scripts/stand_in/machine.py`). For an Arduino project `firmware/` holds `.ino`/`.cpp`: zero modules found. Risk: "0 imported, ok"
   reads as pass. Fix: platform picks the test ("compile only", or `skipped` with a reason). Zero files must be `could-not-run`.
   Unverified: what exit code it gives on an empty `firmware/`.
2. `scripts/restricted_pins.py:12,24-30` + `board_live.py` (live try guard, D14). Parses the code with Python `ast`; `DOES_NOT_PARSE`
   refuses non-Python. For C++ it refuses everything (safe), but a guard that parses only Python gives no protection once live code
   is C++. Fix: `live.py --code` stays MicroPython-only; platform says `live: unsupported` (a refusal, never a pass).
3. `scripts/live.py:21-41`, `reach.py:20-31`, `board_reach.py`, `board_live.py`, `board_console.py` (reach/live/doctor). All speak
   mpremote exec into a raw REPL. On an Arduino board there is no REPL: `could not enter raw repl` then the doctor "cure" fires
   (`reach.py` cure, `live.py:27-30` `mpremote reset`). Misleads: reach says the board is unreachable when it runs fine. Also
   `reach.py:20` "stops the firmware that ran". Fix: reach for Arduino = serial ping or `esptool chip_id`; `RunnerFor(platform)`.
4. `scripts/compare_design.py:211-231`, `scripts/check_all.py:130-131`, `scripts/init_project.py:105-108,187-188`
   (`rules.json` key `pulled_by_firmware`, text "set by the firmware with Pin.PULL_UP"). The check waives "no resistor" for a pin
   the firmware pulls up. The waiver is only true if the firmware does it. With a C++ `pins.h` that must say `INPUT_PULLUP`; if the
   pin map renderer omits the pull, check_all says ok and the button floats. Fix: renderer emits the pull for both languages; the
   waiver text names no API (`Pin.PULL_UP` is in `breadboard.py:331`, `assign_pins.py:414`, `compare_design.py:211`).
5. `scripts/check_spine.py:88,895-896,919` (`keep_pins`): "ours" = file starts with a `#` header (Python comment). A `pins.h`
   with `//` header is "a person's", so the build leaves a stale one: pins for another design. Fix: `PinMapRenderer` owns header
   and path (also in lens-chain).
6. `boards/xiao-esp32-c6.json:193-200`, `boards/firebeetle2-esp32s3.json:284-292` (`deep_sleep`: `wake_api: esp32.wake_on_ext1`,
   `//single_polarity_for_all_pins` "True of MicroPython's API, not of the silicon", `//micropython_low_level_wake_bug`).
   These are MicroPython API facts filed as board facts. For Arduino: `esp_sleep_enable_ext1_wakeup` has its own limits, so a C6
   claim "one polarity" or "Pin.irq silently does nothing" is wrong or unproven in C++. Fix: move under `micropython:`; key by
   platform. Same: `parts/tactile-button.json:54` advice cites `esp32.wake_on_ext1` (consumers read it as a fact).
   Consumer: `assign_pins.py` wake roles read `deep_sleep`; unverified whether it reads `wake_api`.
7. `commands/deploy.md:61-87` + `deploy_service.py` ready read: hashes "each file the passed run's log names" (file-system
   model). A C++ image is one `.bin`, no files: ready would be `unknown` forever, or a hash of nothing. Covered by lens-chain; here
   only the user-facing words: "unknown is not a pass" must still hold when the platform has no file list.

## B. Loud wrong: breaks visibly, wording lies

8. `scripts/tools.py:144,202`, `data/tools.json:9-24,119-190`, `commands/setup.md:51`. Tool roles: `firmware-image: micropython-*`,
   `littlefs`, `board-shell: mpremote`; the "for" text of mpremote says "MicroPython's REPL". Arduino needs `arduino-cli` or
   PlatformIO plus a core (~hundreds of MB; AGENTS.md "a user installs nothing heavy", "name any cost and ask first").
   `/spark:setup` lists ALL MicroPython builds for every user. Fix: tools per platform (`tools.json` role keys already allow it);
   setup shows only the chosen platform's. `look.py:15` and `board_look` use `mpremote devs` to list ports: the port finder
   should not need MicroPython (use `esptool`/pyserial).
9. `scripts/board_connection.py`, `board_doctor.py`, `look.py`, `download_mode.py`, `grant.py`, `board_grant.py` mention mpremote
   (grep). Unverified how much is a port listing (language-free) versus REPL. `board_doctor` "two checks: mpremote devs, 2 s of
   console" survives; its advice text names mpremote. Fix: wording from the platform.
10. `scripts/boards.py` (`micropython_port` as a board key), `tools/snapshot.py:75`, `tools/circuit-to-wokwi/lib/board.ts:32`
    (typed `micropython_port: string`, required). A board record without that key, for an Arduino-only board, may fail the type or
    `boards.py --get`. Fix: key optional; `boards.py --get platform_port` or per-platform block. Unverified: whether boards.py
    validates it as required.
11. `tools/circuit-to-wokwi/cli.ts:27-28`: comment names `firmware/micropython/sim/...` layout (a sisuo repo path), not logic.
    Cosmetic. `commands/build.md:271` cites sisuo `firmware/micropython/` scenarios as the example.
12. `scripts/sim_project.py` / `run_scenario.py` / `check_spine.py:347,506,653` `--firmware IMAGE`, `wokwi.toml`. Wokwi can run an
    Arduino `.bin`/`.elf`, so the sim stays possible; but "puts MicroPython and `firmware/` into one image" (`build.md:231-237`) is
    the build path. `sim/runs/*.log` stores "the sha256 of the image it tested": the log must also store the platform, or a rerun
    of a MicroPython log on an Arduino project passes the deploy gate. Fix: add `platform` to the log; `deploy_gate` compares it.
13. `scripts/emit_board.py`, `breadboard.py` (`firmware/pins.py` text in the sheet, `breadboard.py:10`) and `breadboard.expected.md`
    fixtures: the sheet says "the pins the firmware imports" (Python wording). Fix: file name from the platform.

## C. Agent and command prompts, docs, journey (wording, but they steer Claude)

14. `commands/build.md:3,50,108-117,159-160,175,231-237,296`, `skills/spark-design/SKILL.md:101`,
    `skills/spark-design/references/part-data.md:38`. All say `firmware/pins.py`, `import pins`, `--emit-pins firmware/pins.py`,
    "imports under CPython's tests and on MicroPython". The slash command is what Claude follows, so Claude writes Python even if
    the code can emit C++. Fix: one sentence "the platform in `<key>` names the file", then examples.
15. `agents/design-reviewer.md:14,43` (firmware-hardware dimension) and `skills/spark-review/SKILL.md:54` ("the firmware config"):
    language-neutral wording, but the reviewer reads `config.WAKE_ON_HIGH` style facts (`boards/README.md`). Unverified whether any
    prompt names `Pin(`. Low risk; add "C++ firmware files count" so it does not say "no firmware found".
16. `commands/idea.md:48`, `scripts/parts.py:563-570` (`simulation.wokwi.stand_in`): "stand-in" there is Wokwi's built-in part,
    NOT `scripts/stand_in/machine.py` (the Python `machine` stub). Same word, two things: a naming clash that gets worse if a C++ stub
    appears. Fix: call the Python one `host_stub`.
17. Part records (`parts/*.json`): grep found NO driver, library or micropython field. So the idea/parts step does not pick by
    MicroPython driver availability (good), but also has no place for "Arduino library X". Consequence: Arduino's biggest gain (libs)
    is invisible to spark. New optional field `drivers: {platform: name}` only when a stage needs it (AGENTS.md "records grow by need").
18. `docs/guide/agents.md`, `journey.md`, `how-it-works.md`, `developing.md`, `README.md:85-99,209`, `GLOSSARY.md` ("machine."):
    all describe the flow as MicroPython (littlefs, mpremote). `tools/check_docs.py:25-27` lists `pins.py`, `main.py`, `boot.py`
    as "project files" docs may name: a docs check that would reject `pins.h` as an unknown file. Fix: extend `PROJECT_FILES`.
    `tools/journey.py:20,38-42` is the picture: "Firmware: import_firmware.py", tested by `tests/test_journey.py` against README.
19. `scripts/init_project.py` writes `.spark/rules.json` and `project.json`: no `platform` key anywhere. This is where the one key
    should live (a brief fact the person chose), or the board record's `active.json`. Unverified which one lens-board proposes.

## D. Tests and fixtures that pin MicroPython (will fail loudly, cheap)

20. `tests/test_import_firmware.py`, `test_flash_image.py`, `test_deploy*.py`, `test_ready_check.py`, `test_board_*`, `test_tools.py`,
    `test_run_scenario.py`, `tests/data/breadboard/button-light/firmware/light.py`, `tests/data/snapshot/*/boards/*.json`
    (carry `micropython_port`), `tests/mutations/p59-*, p130-*, p215-*, p219-*` tables. A fixture that tests spark is part of the
    change (AGENTS.md). Count ~60 files name mpremote or micropython. They need no redesign: a second fixture project per platform.
21. `tools/pre-push` -> `check_commit.py`: only calls the check; no firmware assumption found (grep). `.claude/` hooks: not searched.

## Ranking by silent-wrong damage
1. #1 import test, zero files = ok. 2. #4 pull-up waiver without the pull. 3. #12 run log lacks platform, gate passes a wrong image.
4. #3 reach cure on a healthy Arduino board. 5. #6 MicroPython wake facts read as board facts. Then #5, #2, #7, #8.

## Smallest shared fix
One `platform` value (default `micropython`, so nothing existing changes), read by `FirmwarePlatform`, stored in the run log and the
rules file. Every row above then asks the platform for: file name, pull text, header marker, reader (REPL or serial), tool roles,
and wake facts. A platform with no answer returns `unsupported`, which each check must print as `skipped`, never `ok`.
Places found: 21 groups (about 45 files), 7 of them silent-wrong.
