# P510 technology lens (Sonnet 5.5)

> C1 (board emitter ignores `pad_aliases`) is real, reproduced, and a 3-line fix builds the walk's project end to end. The gaps I checked all hold.
> C1 is wider than the FireBeetle 2: the XIAO ESP32-C6 record aliases its SPI and I2C pins too. C6 asks for one thing the code already does.

Code: branch `p510-walk4-council`, main at `8595309b`. Evidence tags: [ran] I ran it, [read] I read the line.

## Findings

| # | finding | evidence | card or plan | proposal | severity |
|---|---|---|---|---|---|
| 1 | C1 reproduced. The emitter writes the trace from the pin NAME, not the pad name. | [ran] `SPARK_HOME=~/.local/share/spark check_spine.py requirements.json --keep .` on a copy of walk 4: `[!!] build 2 error(s): source_trace_not_connected_error`. `dist/board/circuit.json`: `Could not find port for selector ".Mcu > .MOSI"` and `.MISO`. [read] `scripts/emit_board.py:812-813` writes `entry["pin"]` raw. The footprint has `portHints={["MI"]}` and `["MO"]` (FireBeetle2Esp32S3.tsx:22-23). The board record `boards/firebeetle2-esp32s3.json` has `pad_aliases {MISO: MI, MOSI: MO, SS: A4}`. | C1 | One fix at the one line (finding 2). | high |
| 2 | A 3-line fix in a scratch copy makes the chain run end to end. | [ran] In `signal_lines` take `board`, write `physical.pad_aliases.get(entry["pin"], entry["pin"])` at line 812, and pass `board` at `emit_board.py:1048`. Result: `[ok] build 12 trace(s), 0 errors`, `[ok] simulation 2 wire(s)`, "the chain runs end to end". Scratch copy deleted. | C1 | Take the fix. The alias lookup now sits in 4 places (`assign_pins.py:418`, `breadboard.py:150` and `:315`, `emit_board.py`). Move it to one `boards.pad_of(board, pin)` helper in the same PR. | high |
| 3 | C1 is wider than the FireBeetle 2. The XIAO C6 record aliases `SDA SCL SS MOSI MISO SCK A0 A1 A2` to D-labels, and its `header_order` uses only D-labels. | [read] `boards/xiao-esp32-c6.json` `physical.pad_aliases` and `header_order`. Every one of those 9 pin names is a key in `pins`. Not built, so "the XIAO build breaks the same way" is not checked. | C1 | Add a test per shipped board: for every trace `emit_board` writes, the pad exists in `header_order`. That test would have caught this and may find a XIAO defect. | high |
| 4 | No test covers the alias at the emitter. `tests/test_emit_board.py` has no `pad_aliases` case. `tests/test_assign_pins.py:554` has one for the pins file only. | [read] grep `pad_aliases` in tests. | C1 | Add a regression case: a board with `pad_aliases {MOSI: MO}` must give `.Mcu > .MO`. | medium |
| 5 | G30 holds. The build verdict is `"%d error(s): %s"` with the error types only. | [read] `check_spine.py:496`. [ran] output above. | C1 | Add the selector message from `circuit.json` to the stage detail (the first 2 errors). Small, same PR or its own XS. | medium |
| 6 | C6 asks to "start the firmware with `--after watchdog-reset`". `deploy.py` already does it. | [read] `deploy.py:95`. | C6 | Cut that clause from C6. | low |
| 7 | `machine.bootloader()` is not in the code yet, only in P472's finding. | [read] grep: only `docs/discovery/2026-10-31-p472-no-hands/finding.md:6,21,85`. It exists for S2, S3, C2, C3, P4 only (finding.md:58). | C6 | C6 is two cards: the S3 path (mpremote call) and the standing yes. The C6 chip needs the esptool reset, a different path. | medium |

## Gap check, G1 to G46 against the code

Holds = the code matches the claim. "Not checked" = needs a run or a bench.

- G1, G2, G9, G11 (idea page, brief, verdict next step): not checked in code. They are text of skills and pages.
- G3, G4, G6, G7 (holds, refusal, `--drawer` keys): holds in part. `parts.py:2117` `_op_pick` and `needs.plan_pick` give no third fix. `store.holders_of` (`drawer.py:327`) counts pieces. Not run.
- G5, G10, G28, G25 (`--match` text, Wokwi stand-ins): not checked.
- G8: holds. `check_all.py:466` prints "not asked for" for every skipped check.
- G12, G13: holds. `run_scenario.py` has no `dry` text. Its only press is the `set-control` step (`:54`). No Mac button press command.
- G14, G32, G43: holds. `scripts/stand_in/` holds `machine.py` and `fallback/framebuf.py` and `micropython.py`. No C module stand-in. Editor stubs not checked.
- G15, G36, G41: holds in part. `download_mode.py` is a library for the C6 BOOT+R case. No `machine.bootloader()` call anywhere in `scripts/` (finding 7).
- G16: partly. The doctor takes a `silent_step` from the tools list (`board_doctor.py:15`). The 2 s value not checked.
- G17, G33: not checked. `look.py:28` handles unnamed must lines. The no-simulation path not run.
- G18: not checked.
- G19: holds. `condition` is checked as words (`needs.py:33`) and printed (`parts.py:2053,2073`). No matcher reads it.
- G20, G22, G24: holds. No file in `boards/` or `parts/` contains "GDI". Case-insensitive grep.
- G21, G23, G27: G23 holds (no connector field anywhere). G27 not run. The walk's own pin tables are the evidence.
- G26: holds. `needs.plan_pick` refuses a pick whose id is not a record or drawer entry (`:406`). `light=` splits to an empty id. No remove flag found in `parts.py` (grep `drop`, `remove`).
- G29: holds. Finding 1.
- G30: holds. Finding 5.
- G31: holds by design. `assign_pins.onboard_lines` (`:432`) writes every on-board part of the board record. My build of the walk's project still printed `ONBOARD_LED (GPIO21)` and `ONBOARD_BUTTON (GPIO47)` under "cannot show".
- G34: holds. `onboard_button` exists (`firebeetle2-esp32s3.json:250`, the user button GPIO47). GPIO0 appears only in the `strapping` note and the `pins` comment.
- G35: not checked. No log writer found in `board_console.py`.
- G37: holds. The record has one `micropython_port: "ESP32_GENERIC_S3"` (line 7) and the `sku` note (line 9) names N16R8 and N4.
- G38: holds. `flash_image.py:255-256`: a given path returns an `Interpreter` with no check against the tools list.
- G39, G44, G45, G46: not checked. They need a bench or the look code.
- G40: partly. `deploy.py:95-102` knows `ready unknown`, `download_mode_stayed` and `port_gone`. The late port is not waited for in a loop I could find.
- G42: holds. `flash_image.py` `PartitionTable.with_filesystem` raises on any `vfs` or `ffat` entry other than its fixed 2 MB `FILESYSTEM` at `FILESYSTEM_OFFSET`. The error text says "use the build for the board's chip".

## C1 to C11

| card | verdict | why and the new text |
|---|---|---|
| C1 board emitter ignores `pad_aliases` | keep, rewrite | Rewrite "The change": `emit_board.signal_lines` writes the pad name from one `boards.pad_of(board, pin)` helper that `assign_pins`, `breadboard` and `emit_board` share. The build verdict names the first 2 traces that did not connect (G30). Done when: (1) `dfr0664-tft-2in` on the FireBeetle 2 builds with 0 errors, (2) a test checks that every trace pad of every shipped board is in `header_order`, (3) the verdict shows the selector. Size: XS to S. Do it first. |
| C2 module on a fixed connector | merge into P460 (#628) | Design card, not a fix. It needs the architecture lens. Do not start before C1. |
| C3 remove a part | split | (a) `--pick` with an empty id or a `--drop NEED` flag with a dry run: small, testable. (b) "board part leaves the circuit but stays on the board": needs a record fact, so a design. Do (a) first. |
| C4 presets and holds | split | Holds freed at project end, and MAC in a hold, go to P466 (#634). `--drawer` printing entry keys (G7) is XS and testable alone. The test preset (I1) is a separate idea. |
| C5 first steps | keep, trim | Only the verdict's next step and the dry-run file name are code. Both are text and small. Move the goal-in-brief item to the skill text. |
| C6 automatic mode | split | Drop the `--after watchdog-reset` clause (finding 6). (a) S3 no-hands path with `machine.bootloader()` (extend P469 #637, done when the look and deploy enter download mode on the S3 with no key press, bench-tested). (b) The standing yes for N minutes is a safety design, not a technology fix. (c) Port wait and the watch log are separate small cards. |
| C7 one word about what a run tests | merge into P490 (#669) and P409 (#535) | Too many items for one card. G17 and G33 are small and testable alone. |
| C8 own MicroPython build | split | (a) Read the image's own `vfs` and accept it, G42. Testable with a fixture table. (b) Name PSRAM build in the record (G37). (c) Say that `--micropython` is outside the list (G38). (d) Find the board by another fact than the MAC (G44). One card for all of these is too big. |
| C9 free firmware tests on the Mac | merge into P492 (#671) and P399 (#515) | Type stubs and a C-module stand-in hook are separate. The stand-in hook is the part that spark needs. |
| C10 BOOT as a second button | keep | Record fact plus `onboard_lines` reuse. Small. Done when `pins.py` names `ONBOARD_BUTTON_BOOT` for the FireBeetle 2 with the bootloader caveat. |
| C11 C driver spike | keep, outside spark | Not checked. It returns to P336 (#430). |

## New cards

1. **P? , every shipped board's trace pads exist in its footprint → a check that stops C1 from coming back.** Need: C1 passed `check_spine` stages 1 to 3 and failed only at the build, 5 s later, with no name. Done when: a test or a check reads each board record, builds its trace list for a SPI/I2C/SS part and fails on a pad that is not in `header_order`. The XIAO C6 is covered (finding 3).
2. **P? , the build verdict hides the failing trace → it names the first 2 selectors from `circuit.json`.** Need: G30. Done when: `check_spine --json` and the text verdict carry the selector message.

## Not checked

- G1, G2, G5, G9, G10, G11, G17, G18, G21, G25, G27, G28, G33, G35, G39, G44, G45, G46 in code. They are text of pages or bench facts.
- Whether the XIAO C6 SPI/I2C build breaks the same way. I did not build it.
- The `tsci` version used (0.0.2600) matches the walk's. I did not compare other versions.
- Card sizes beyond the code I read. I did not read card bodies.
