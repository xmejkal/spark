# P472 finding: download mode and start with no hands (spike #643)

Date 2026-10-31 (Europe/Prague). Bench: the PO's FireBeetle 2 ESP32-S3 on `/dev/cu.usbmodem1101`.
It ran MicroPython v1.29.0 ESP32_GENERIC_S3. The tools were esptool 5.5.0 and mpremote 1.29.0. The full log is `bench.log` in this folder, tries 1 to 10.

> On the S3 with MicroPython's own USB port, a call to `machine.bootloader()` through mpremote enters
> download mode with no hands. Then esptool `--after hard-reset` or `--after watchdog-reset` starts MicroPython again.
> Both worked on the bench at 23:29. The button press was needed because the PO entered download mode with BOOT.
> BOOT holds the boot pin low, and the USB reset cannot clear it. The C6 and the bridge boards are untried.
> One try (esptool `--before usb-reset` against the running MicroPython) left the board silent. See "Bench state".

In short, MicroPython on the S3 can switch itself into download mode, and esptool can restart it afterward, all with no buttons.
Both steps worked on the bench at 23:29 Prague time. The one try that went wrong left the board silent, so the PO must press RESET, and the C6 and bridge rows stay untried.

## Table

Each cell says "tried on the bench" with a time, "from source" or "untried".

| Chip and USB kind | Enter download mode, no button | Start the firmware, no button |
|---|---|---|
| S3, MicroPython on its own USB port (TinyUSB, id 0x4001, the PO's FireBeetle 2) | `mpremote exec "import machine; machine.bootloader()"`, wait about 4 s, then esptool with `--before no-reset`. Tried on the bench 23:29:01 and 23:29:30. The esptool DTR/RTS reset fails here (tried on the bench 23:29:52). | `--after hard-reset` or `--after watchdog-reset`. Tried on the bench 23:29:16 and 23:29:34. MicroPython answered by 23:29:41. |
| S3, chip's USB-Serial/JTAG (id 0x1001: ROM download mode, or firmware that keeps that port) | The esptool default reset (the USB-JTAG sequence sets the download flag). From source (TRM table 33.4-3). The ROM-mode side was seen on the bench (chip-id at 23:29:10). | After a flag entry, hard-reset is enough (tried on the bench 23:29:34). After a BOOT-button entry, only `--after watchdog-reset` works. From source (esptool troubleshooting page). The watchdog after a button entry is untried. |
| S3 with a USB bridge chip (CH34x, CP210x) | The esptool default reset, through DTR and RTS wired to GPIO0 and EN. From source (esptool boot-mode-selection page). Untried. | `--after hard-reset` pulses EN, so the chip samples the pin again. From source. Untried. |
| C6, chip's USB-Serial/JTAG (Seeed XIAO ESP32-C6) | The esptool default reset (the USB-JTAG sequence). From source (C6 TRM table 32.4-1). MicroPython has no `machine.bootloader()` here. Untried. | After a software entry, `--after hard-reset`. After a BOOT-button entry, the page's remedy does not apply, because esptool 5.5.0 turns the C6 watchdog off. Only RESET or a power-up helps. From source, untried. |
| Classic ESP32 with a bridge | The esptool default reset (DTR to GPIO0, RTS to EN). From source. MicroPython has no `machine.bootloader()` here. Untried. | `--after hard-reset`. From source. Untried. |

Two C6 notes. The spike names a bench try on the XIAO, but no C6 sat on the bench tonight.
The C6 TRM and the esptool page describe the same flag mechanism as the S3. So the C6 probably behaves like the S3 in the 0x1001 row.

## Why the buttons were needed (the cause)

1. esptool cannot reach a running MicroPython by DTR/RTS. MicroPython owns the USB port as a TinyUSB serial port
   (USB product id 0x4001). Tried on the bench at 23:29:52: `esptool flash-id` against the running board ends with
   "Failed to connect ... No serial data received". This reproduces the P461 error.
2. A chip that entered download mode through the BOOT button keeps the boot pin sampled low. The chip's own USB port
   (USB-Serial/JTAG) can only do a core reset, which does not sample the pin again. So `--after hard-reset` leaves
   the chip in download mode (boot:0x23 in the 10-31 board log). Source: esptool troubleshooting, "Leaving Download
   Mode in USB-Serial/JTAG Mode", https://docs.espressif.com/projects/esptool/en/latest/esp32s3/troubleshooting.html#leaving-download-mode-in-usb-serial-jtag-mode
   (the esp32c6 page has the same text). Source: walk 3 diary items 21, 27 and 28 in `~/Development/spark-walks/walk3-rehearsal/`.
3. A chip that entered download mode by a software flag (no button) does not have this problem. The flag clears
   on the next reset. Tried on the bench at 23:29:41: after `machine.bootloader()`, `esptool --after hard-reset flash-id`
   ran, and MicroPython answered again with no button.

## What each esptool option does (esptool 5.5.0 source, site-packages/esptool)

- `--before default-reset` picks the sequence by USB product id (loader.py lines 850-851). Id 0x1001
  (USB-Serial/JTAG) gets the USB-JTAG sequence. Any other port gets the classic DTR/RTS bridge sequence.
- `--before usb-reset` forces the USB-JTAG sequence on any port.
- `--before no-reset` sends no DTR/RTS and only talks to a chip already in download mode.
- `--after hard-reset` pulses RTS. On the S3 it first clears the force-download flag (esp32s3.py lines 347-355).
- `--after watchdog-reset` does a full system reset through the watchdog (esp32s3.py lines 337-345, reset.py).
  This samples the boot pin again. The C6 and the classic ESP32 have no override, so they fall back to
  a hard reset (loader.py lines 2218-2222). The C6 USB bug is explained in esp32c6.py lines 206-209.
- `--after no-reset` stays in download mode. `--after soft-reset` runs user code (not tried).

## MicroPython side (v1.29.0 source)

- `machine.bootloader()` on ESP32 exists only for the S2, S3, C2, C3 and P4
  (ports/esp32/mpconfigport.h lines 406-418). It sets the force-download flag and restarts
  (ports/esp32/modmachine.c lines 275-288). On the S3 with USB it first switches to USB-Serial/JTAG.
  So it does not exist on the C6 or on the classic ESP32.
  Source: https://github.com/micropython/micropython/tree/v1.29.0.
- The TinyUSB serial port also starts the bootloader on a DTR/RTS pattern
  (shared/tinyusb/mp_usbd_cdc.c lines 173-206, `MICROPY_HW_USB_CDC_DTR_RTS_BOOTLOADER`). That is a second way in
  and needs no mpremote. Untried on its own.
- On the C6, MicroPython uses the chip's USB-Serial/JTAG port (mpconfigport.h lines 325-327). A chip with only one USB peripheral gets no TinyUSB.

## Bench state (what the spike left)

Tries 1 to 5 worked as the table says. Try 6 (23:30:14) ran `esptool --before usb-reset --after watchdog-reset flash-id`
against the running MicroPython. It failed to connect. After that, the board showed USB id 0x4001 in tries 6 to 10, until 23:33.
It did not answer mpremote (error text `could not enter raw repl`), a raw serial probe, or esptool.
Nobody knows whether the firmware hung or the macOS port wedged. The spike stopped there, as told.
The PO must press RESET on the FireBeetle 2. Nothing was written or erased on the board.
Do not use `--before usb-reset` on a running MicroPython until someone finds out why.
The suspect: the USB-JTAG sequence hits MicroPython's DTR/RTS bootloader rule while `machine.bootloader()` is already due.

## What spark can do (proposals for P462, P469, P465)

Spark does none of this today. Its deploy and look use the esptool default reset (`scripts/flasher.py`, `scripts/board_look.py`).
These steps are proposals. The order for the look and for deploy would follow the board record fact `chip` and the port's USB id (from `mpremote connect list`):

1. Read the port's USB id. Id 0x4001 on an S3 means a running MicroPython, or a bridge.
   Id 0x1001 means the chip's own port (ROM download, or a C6 running firmware).
2. On an S3, S2 or C3 where MicroPython answers, spark would send `machine.bootloader()` through mpremote.
   It would expect the mpremote error, because the port drops. It would wait until the port returns with id 0x1001.
   Then it would run esptool with `--before no-reset`.
3. On a C6 or a classic ESP32 (no `machine.bootloader()`), spark would run esptool with its default `--before`.
   On the C6 the USB-JTAG sequence probably works with the firmware running (from source). On a bridge board DTR/RTS works. Both untried.
4. After the read or the write, spark would use `--after hard-reset`. On the S3 it would use `--after watchdog-reset`.
   That samples the boot pin again, so it also covers a button entry. Then spark would wait for the port and read `ready` (P462).
5. If the port stays silent after step 4, spark would report `could-not-run`, never a pass, and name RESET as the hand step.
6. The look needs download mode for flash-id, so an esptool look restarts the board (about 6 s back).
   A look that must not restart can only use mpremote on the running MicroPython (P469).

## Cards that change

- P462 (#630, deploy waits for a real start): after the write, wait for the USB id and for `ready`. Use
  `--after watchdog-reset` on the S3. Step 2 above replaces the first "press BOOT" step on the S3.
- P469 (#637, a look without a restart): two looks. With mpremote on the running board, no restart. With esptool,
  a restart is certain, and the output says so.
- P465 (#633, diagnose a board that does not start): add the USB id as a fact (0x4001 running, 0x1001 download or
  C6, none or silent: stuck). A silent board with id 0x4001 happened tonight (try 6), and the hand step is RESET.
- New cards to offer, not filed: a bench try on the XIAO ESP32-C6, a bench try on a bridge board (classic ESP32),
  and a bench try of the repeatable `--before usb-reset` hang.

## Sources

- esptool 5.5.0 source: `~/.local/lib/python3.10/site-packages/esptool/{__init__.py 421-433, loader.py, reset.py, cmds.py, targets/esp32s3.py, targets/esp32c6.py}`
  and esp_pylib/serial_reset.py (usb_jtag_bootloader_reset, hard_reset).
- MicroPython v1.29.0: https://github.com/micropython/micropython/tree/v1.29.0 ports/esp32/{mpconfigport.h,modmachine.c,main.c},
  shared/tinyusb/mp_usbd_cdc.c, docs/library/machine.rst line 199 (`bootloader`).
- Espressif: ESP32-S3 TRM ch. 33.3 and 33.4 https://documentation.espressif.com/esp32-s3_technical_reference_manual_en.html#page=1247 and #page=1253.
  ESP32-C6 TRM ch. 32 https://documentation.espressif.com/esp32-c6_technical_reference_manual_en.html#page=1034.
  The esptool troubleshooting page (links above). The esptool advanced options
  https://docs.espressif.com/projects/esptool/en/latest/esp32c6/esptool/advanced-options.html.
- Bench: `bench.log` (this folder). `~/Development/spark-walks/walk3-rehearsal/walk3-rehearsal-diary.md` items 21 to 28 and `board-logs/`.
