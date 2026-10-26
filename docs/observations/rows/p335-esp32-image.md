# P335: the original ESP32's interpreter at 0x1000 inside the one image, findings rows

Findings from the two plan councils, the build and the review of P335 (2026-10-26, Prague). Round 1's 10 gaps and
round 2's 8 are in the approved plan's Council section, and only those that changed the code or stay open are rows
here.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The offset belongs to the downloaded file, not to the chip | plan, round 1 | acted | `data/tools.json` entry `micropython-esp32`, `"flash_offset": "0x1000"`, cited to https://micropython.org/download/ESP32_GENERIC/. Round 2 read the same page for v1.29.0 |
| 2 | A bad `flash_offset` would be a traceback | plan, round 1 | acted | `tools.flash_offset_problem` inside `entry_problem`, so `tools.find` refuses it; `flash_image.offset_of` runs the same rule on the `--micropython` path |
| 3 | `int(4096, 0)` raises TypeError | plan, round 2 | acted | the rule asks for a string first; `tests/test_tools.py` tries 4096, True, "-0x10" and "zero" |
| 4 | `tools.py` checks the upper bound of `flash_offset` | plan | rejected | `tools.py` would need the filesystem address of `flash_image`, which imports `tools`. `image()` refuses an interpreter that would pass 0x200000, with the exact boundary tested |
| 5 | A hand-given `--micropython` file cannot reach the board's entry without a second lookup | plan, round 2 | acted | `flash_image.build_entry` scans the lists once for both paths and never calls `tools.find` for a given file |
| 6 | `tests/mutations/sprint-10-p82-5.json`'s first `find` was stale before this change | plan, round 2 | acted | true: main's `scripts/flash_image.py:112` reads `tools.find("firmware-image", project)`, and the `find` string had no `project`, so `tools/mutate.py` refused the table. It now names the new line, and all 43 anchors of the four tables occur once |
| 7 | `tests/test_run_scenario.py` pinned the old refusal words "larger than" | build | acted | now asserts "would pass 0x200000, where the filesystem starts" |
| 8 | `Interpreter`'s docstring must say Value (`docs/guide/developing.md:259`) | review | acted | `scripts/flash_image.py`, `Interpreter` |
| 9 | The summary line "MicroPython at 0x1000-0x…" had no test | review | acted | `test_the_command_says_where_the_interpreter_starts_and_ends`, with 0x1000-0x13e8 and 0x0-0x3e8 for the 1000-byte fixture |
| 10 | Wokwi loads a padded image for an ESP32 part | plan, round 1 | raised | not tested: no simulation of an original ESP32 board ran. The walk (P338 #432) deploys without one, after the PO's yes |
| 11 | The board boots from the padded image written at 0x0 | plan | raised | the review found that esptool patches the header only at the bootloader offset, so a write at 0x0 is untouched. The walk's deploy proves it on the T-Display |
