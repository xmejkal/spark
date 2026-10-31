# P472: download mode and start with no hands

Findings of P472 (#643), 2026-10-31, Prague, built on main da8b6950. The finding is `docs/discovery/2026-10-31-p472-no-hands/finding.md`. All rows are raised.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The board stayed silent after `esptool --before usb-reset --after watchdog-reset flash-id` against the running MicroPython at 23:30:14 | bench tries 6-10 | raised | bench.log; USB id 0x4001, no answer to mpremote, raw probe or esptool until 23:33. The PO presses RESET. Cause unknown, a bench try of the repeatable hang goes to P465 (#633) |
| 2 | The suspect for row 1 is the USB-JTAG sequence hitting MicroPython's DTR/RTS bootloader rule | finding, MicroPython mp_usbd_cdc.c lines 173-206 | raised | untried; P465 (#633) |
| 3 | The XIAO ESP32-C6 rows are untried: no C6 sat on the bench | finding | raised | LATER: a bench try on the XIAO C6 (new card to offer, not filed) |
| 4 | The classic ESP32 and bridge-chip rows are untried | finding | raised | LATER: a bench try on a bridge board (new card to offer, not filed) |
| 5 | The C6 has no `machine.bootloader()` in MicroPython v1.29.0 | finding, mpconfigport.h lines 406-418 | raised | from source; the C6 and classic ESP32 path (step 3) goes to P462 (#630) |
| 6 | On a C6 after a BOOT-button entry, esptool 5.5.0 turns the watchdog off, so only RESET or a power-up leaves download mode | finding, esp32c6.py lines 206-209 | raised | from source, untried; P462 (#630) |
| 7 | `--after watchdog-reset` after a BOOT-button entry on the S3 is untried | finding | raised | from source (esptool troubleshooting page); P462 (#630) |
| 8 | The DTR/RTS bootloader rule of the TinyUSB serial port is untried as a way in on its own | finding | raised | LATER: no mpremote needed; P462 (#630) may use it |
| 9 | A look needs download mode for flash-id, so it restarts the board (about 6 s back) | finding | raised | P469 (#637): two looks, mpremote with no restart and esptool with a stated restart |
| 10 | The deploy waits for the USB id and for `ready` after the write, with `--after watchdog-reset` on the S3 | finding | raised | P462 (#630) |
| 11 | The board record fact `chip` and the port's USB id decide the order of steps; a silent port after the restart reports `could-not-run` and names RESET | finding | raised | USB id as a fact for P465 (#633) |
| 12 | `--after soft-reset` is untried | finding | raised | LATER |
