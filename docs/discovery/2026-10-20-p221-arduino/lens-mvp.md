# P221 lens: the MVP and its cost (and the user/AI experience)

Card [P221 #203](https://github.com/xmejkal/spark/issues/203). Lens: MVP and cost. 2026-10-20. Sources read: AGENTS.md,
`docs/discovery/2026-10-17-p218-finish/platforms.md`, P323 design (branch `origin/p323-target-architecture`), walk 1 record
(`docs/observations/2026-10-19-p326-walk1.md`), `scripts/firmware_platform.py`, `gh pr list --state merged`.
Marks: (V) verified in a file or command this run; (U) unverified, a guess or from the platforms.md council.

> **TL;DR.** Yes, "same, but Arduino" is possible, and the MVP is small: one board (XIAO ESP32-C6), one project
> (button + LED), four new things: a `pins.h` renderer, a sketch folder layout, a compile stage, and a deploy that proves
> the flash by the serial `ready` line instead of hashing files. About **5 Arduino PRs after 5 refactor PRs (10 to 15 in all)**, 3 to 5 weeks (U); four of the five refactors pay off without Arduino. Biggest risk: the C6 toolchain on the person's Mac, not spark's code.

## 1. The smallest end-to-end slice

The person says "Arduino" at `/spark:init` (or in the requirements). Then:

| Step | What happens (MVP) | New or reused |
|---|---|---|
| Pick | `requirements.json` gets `platform: arduino` (P323 puts the key in requirements, V) | new key |
| Build | the same `assign_pins` result is rendered as `firmware/pins.h` (`constexpr int BUTTON = 9;`), beside or instead of `pins.py` | new renderer, same facts |
| Sketch | the conversation writes `firmware/<name>/<name>.ino` (object-oriented C++, small classes) from `pins.h`. Spark writes no behaviour | new layout, Claude writes |
| Check | `arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32C6 --output-dir build/` replaces `import_firmware.py`. "It compiles" is the only claim | new stage |
| Image | the compile output already holds bootloader, partitions and app. Merge to one image at 0x0 (`esptool merge_bin`, or the `*.merged.bin` the compile writes (U)) | new, small |
| Deploy | `look.py` (reused, V), the person's yes (reused), esptool erase and write at 0x0 (reused, `flasher.EsptoolFlasher`), reset, read serial until `ready` | flash reused, verify new |
| Ready line | the sketch prints `ready` on Serial at the end of `setup()`. The deploy JSON says `ready seen`, same shape as MicroPython's | same contract |

Reuse is real: `FirmwarePlatform` (V, `scripts/firmware_platform.py`, P239 PR 8) was built as the seam. It has factories
for flasher, shell, connection, ready check and console probe. `FirmwarePlatform.arduino(project)` is a second classmethod
(its docstring says so, V). The shell and connection become null objects for a compiled platform.

## 2. OUT of the MVP

| Out | Why |
|---|---|
| Simulation (Wokwi) for Arduino | the PO runs Wokwi only rarely (walk 1 row 6, V). Platforms.md question 1 (does wokwi-cli accept the C6 .bin) stays a later spike (U). See risk 2 for the deploy gate |
| Mac-side "import" test, host unit tests | no equivalent. Compile-only is the whole check. A `native` test is a later card |
| PlatformIO | stock espressif32 lacks C6 (platforms.md, U); a fork risk. One tool per job (AGENTS.md): arduino-cli only |
| ESP-IDF, Rust, CircuitPython | heavy install or large. Not one more than Arduino now |
| REPL, `live.py`, `reach.py`, board console | no REPL on Arduino. They answer "not for this platform" with a code. Serial read only |
| Other boards (FireBeetle, T-Display) | one board first; the second board proves the board-record key map |
| Pin guard for C++ (`restricted_pins`) | the check parses Python `Pin(n)`. For C++, use pins.h only and skip the guard, state it in the output (a `skipped` is not a pass, per agents.md) |

## 3. Work in PRs: refactor first, Arduino second (PO scope, 2026-10-20)

Rule: each touched part becomes a clean seam while MicroPython runs through it (its tests stay green). Arduino is then
the second strategy and adds no `if platform` in callers. Spark's usual PR (V, last 40 merged): 250 to 750 added lines for
code with tests; 100 to 200 for docs and rows.

| # | Refactor PR (MicroPython only, no new feature) | Size (U) | Pays off without Arduino? |
|---|---|---|---|
| R1 | `PinMapRenderer` seam: `pin_module` and `PIN_MODULE_HEADER` leave `assign_pins.py` (V, 510 lines) for a renderer class; `check_spine` reads the marker from it | ~300 | Yes: shrinks the 510-line script, one core (AGENTS.md) |
| R2 | Board record: `micropython_port` becomes `firmware_images` map, records migrated, one reader in `boards.py` | ~400 | Yes: removes a key named after one tool (names say the role) |
| R3 | `FirmwareLayout` and `FirmwareBuilder` seam: `run_scenario`, `import_firmware`, `flash_image` ask the platform for "where main is" and "make the image" instead of knowing `firmware/main.py` | ~500 | Partly: `flash_image` (158 lines) and `run_scenario` (262) get thinner; the gain is real but smaller |
| R4 | Finish `FirmwarePlatform`: `FirmwareCheck` and `FirmwareVerifier` as classes (import-with-stand-in; hash then ready) and null `BoardShell`, so `deploy.py` and `ready_check.py` hold no mpremote text | ~450 | Yes: P239 PR 8 left this half done (V, factories exist); makes deploy testable with fakes |
| R5 | Deploy gate: name the proof an image carries (`simulated`, later `compiled`) as a value, not an implied rule in `deploy_gate.py` | ~250 | Yes: walk 1's block (V) is this gate; the PO decides the rule |

R1 to R5 total about 1,900 lines, 5 PRs (range 4 to 6). If P323's package move lands first, R1 to R4 may merge into it
(U): do not run both on the same files at once (finish before switching, rules).

| # | Arduino PR (second strategy through the seams) | Size (U) |
|---|---|---|
| A0 | Fact check and bench: arduino-cli installed, one hand compile and one hand esptool flash on the C6 (cheap truth test) | docs, ~150 |
| A1 | `platform` key in requirements, `compiler` tool role, C++ renderer and `pins.h`, same-facts test (platforms.md Q2) | ~350 |
| A2 | Arduino `FirmwareBuilder`: layout, compile, merge to one image, named result | ~400 |
| A3 | Arduino `FirmwarePlatform`: serial-`ready` verifier with build id, null shell, compile-only check, `compiled` gate proof | ~400 |
| A4 | Docs, journey table, `tools/journey.py`, agents.md, Miro (same PR rule) | ~250 |
| + | Real-XIAO walk and its 1 to 3 fix PRs (bench time of the PO) | 1 to 3 |

**Estimate: refactor 5 PRs (4 to 6) plus Arduino 5 PRs (4 to 6) plus 1 to 3 walk fixes: 10 to 15 PRs, median 12.** Without the
refactor first, Arduino alone is 4 to 8 PRs (median 6) but leaves `if platform` branches in callers (U). So the refactor
roughly doubles the count and buys a clean second strategy. R1, R2, R4 and R5 are worth doing even if Arduino never ships;
R3 is the one that only pays with a second platform. Walk-fix PRs wait on bench time, which sets the date (V: walk 1
needed the PO and no breadboard). Calendar (U): refactor 1.5 to 2.5 weeks, Arduino 1.5 to 3 more.

## 4. The three biggest risks

1. **The C6 toolchain on the person's Mac.** arduino-cli needs the esp32 core 3.x for C6 (platforms.md, U). The core is a
   large download (U, the size is not measured). It collides with "a user installs nothing heavy" in AGENTS.md. Mitigate:
   `/spark:setup` shows the command and size and asks first; PR 1 measures it on this Mac.
2. **Deploy gate and proof.** Today `deploy.py` flashes only an image that passed a simulation run (walk 1 row 6, V:
   "spark had no path to the board"). With simulation out of the MVP, an Arduino image has no pass to show. Either the
   gate learns a "compiled, not simulated" token with an honest name, or the PO's rule on Wokwi changes. This is a PO
   decision, not a code detail, and it also bites MicroPython today. Also: no hash-on-board, so "the image is on the board"
   rests on serial `ready` only. A sketch left from the last flash could print `ready` too (U). Fix: the sketch prints a
   build id that deploy knows (the image's sha256 prefix), compared on the serial line. This adds a line to the contract
   and is the one spark-owned fact in the sketch, so it fits "facts, not behaviour" (U, a design call).
3. **Claude writes C++ that does not compile, and the loop costs tokens.** MicroPython walk 1 had no compile step, and the
   import check was a seconds-long Mac test. A C++ compile of the core is 10 to 60 seconds and its errors are long (U).
   Without a Mac-side run, the first real test is the board. The walk 1 effect code (PWM) already broke the stand-in
   `machine`; the same gap shows in C++ as a missing library. Mitigate: compile errors reach Claude cut to the first 40
   lines, and the sketch uses only the core (no libraries) in the MVP.

## 5. The experience, for the person and for Claude

Person: says "Arduino" once, then the same words as now: init, idea, build, firmware, deploy. The sheet and the wiring do
not change. What they lose: the REPL's instant "change a line and see it". Each change is compile (10 to 60 s, U) plus
flash plus reset, so a change by words is roughly a minute where MicroPython copied files in seconds (walk 1 row 9,
copy and reset, V that it worked; the time was not recorded). A person who wants to play with live values gets worse.
What they gain: real object-oriented C++ with types, a build that fails before the board sees it, and speed at run time (U).

Claude: fewer tools to call at deploy (no mpremote), more text per turn at build (a longer sketch, longer errors).
Two new codes help it: `needs_compiler` (tool missing) and `not_for_platform` (live, reach). Walk 1's lesson stays: a
`could-not-run` is not a pass, so the check output must say "compiled" and not "checked".

## 6. Tokens and time per walk (U)

Firmware text 1.5 to 2 times longer (a sketch plus classes). The check is a 10 to 60 s compile with long errors (cut them).
A change by words is about 1 min (compile, flash, reset) against seconds for a copy. The first walk adds 10 to 20 percent
tokens and 10 to 20 minutes for the core download and first compile; later compiles use the cache. Walk 1 recorded no total
time (V), so there is no baseline to compare with.

## 7. Answer to the PO's question

Yes for the facts (pins, diagram, sheet, checks, board record, the `ready` proof stay, V platforms.md). No for the language,
tree, image and REPL features. No REPL: replaced by compile, flash, read serial; `live` and `reach` answer with a code.

## 8. What waits on the PO

- Decide the deploy gate (R5, and it blocks A3) for a compiled-but-not-simulated image (risk 2). This blocks PR 5.
- OK to measure the arduino-cli esp32 core size and install it on his Mac (PR 1; a cost to name first).
- Bench time for the one hand flash in PR 1 and the walk after PR 5.
