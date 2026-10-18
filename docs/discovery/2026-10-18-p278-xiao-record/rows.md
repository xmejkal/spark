# P278 findings rows

Rows from the councils, the review and the refuter of PR for #314. Status: raised, verified or rejected, acted.

| # | raised by | finding | status | acted |
| --- | --- | --- | --- | --- |
| 1 | tech lead 1 | two more stale tests need a board with no `power.io_volts`, not no header | verified | helper takes the field: `board_missing("power.io_volts")` |
| 2 | refuter 1 | "fixtures already agree" was false; the shipped build puts the button on D7, the LED on D10 | verified | sentence dropped; a shipped build is not compared with the fixtures |
| 3 | refuter 1 | the pin map gains `BUTTON_PULL = "up"` from `internal_pull_up_ohms` | verified | test pins it; named in the PR |
| 4 | tech lead 2 | `footprint_module` null would fail `--for-fab` for every project through the library walk | verified | the shipped name `XIAO-ESP32-C6-SMD` is kept |
| 5 | review, PO | **PO decision:** `XIAO-ESP32-C6-SMD` names no file in this repository (the generated footprint is `XiaoEsp32C6` from the DIP header), and the fab gate trusts the name, so it does not prove a footprint was drawn and checked | open | card suggested: draw and check the XIAO footprint, or let the gate accept a generated one |
| 6 | refuter 2 | the agreement of `deep_sleep` and `flash_mb` was made by editing the bench fixture, which removed its honest marks (`UNVERIFIED`, `simulated_by_wokwi: null`) and its soc_caps cite | verified, accepted | the card's done-when says they agree; the library block is the verified one (MicroPython v1.29), so the fixture took it. The tests check drift, not truth. PO may prefer the opposite direction |
| 7 | refuter 2 | the library's `pin_roles` are older than the fresh record's: GPIO17 (D7/RX) is not in `console_uart`, no `TX`/`RX` pins, and `assign_pins` put the button on D7 | verified | not changed (out of the card's five fields); card suggested: bring `pin_roles` to the fresh record's, then re-run the pin map |
| 8 | refuter 1 | the `deep_sleep` comment cited soc_caps v5.5.2, which is not a kept document | verified | cite now names v5.5.1 and says the v5.5.2 read is not kept |
| 9 | review | `test_a_library_board_with_no_header_geometry...` was true by construction | verified | now asserts `footprint_gaps` and that `pads` refuses |
| 10 | review | the cite test walked only `power` | verified | walks the whole record |
| 11 | review | `board_library` leaked its temp folder outside the suite | verified | imports `suite_temp` |
| 12 | review | test files import `board_library` inside test bodies in four files | verified, left | style only |
| 13 | PO assistant | the fab-gate change would be a product decision | accepted | avoided by row 4; the question stays in row 5 |
| 14 | tech lead 2 | three of the 15 tests cannot patch `boards.LIBRARY` (child process, direct file read, `--project`) | verified | project board file, a deep copy, `--project` of the scratch library |
