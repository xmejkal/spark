# P215 council, hardware and firmware lens: why mpremote gets no bytes after the flash

E = read in a source. H = a guess. esptool paths are under `~/.local/lib/python3.10/site-packages/`.

## Facts

1. E: esptool 5.5.0 `--after` defaults to `hard-reset`. The modes are hard-reset, soft-reset, no-reset, no-reset-stub,
   watchdog-reset (`esptool/__init__.py:427-432`).
2. E: for USB-Serial/JTAG the docs say the peripheral reads RTS as a core reset, and the reset does not re-sample the
   strapping pins. `--after watchdog-reset` is the documented way to a full reset.
   https://docs.espressif.com/projects/esptool/en/latest/esp32s3/esptool/advanced-options.html
3. E: esptool's own code knows the USB chips "disappear from the bus during reset" and uses a 0.2 s hold and a 0.2 s
   post-release wait (`esptool/reset.py:131-141`, `esp_pylib/serial_reset.py:394-416`).
4. E, and the likely cause: the post-write reset calls `esp.hard_reset()` with no argument (`esptool/cmds.py:2832`).
   `uses_usb` then defaults to False (`esptool/loader.py:2180`), so esptool resets with a 0.1 s hold and no wait after
   release, then closes the port. The 0.2 s wait exists but is not used on this path.
5. E: the C6 reset reason on the bench, `rst:0x15 (USB_UART_HPSYS)`, matches the RTS core reset (TRM table 32.3-2:
   RTS=1, DTR=0 resets the SoC). https://documentation.espressif.com/esp32-c6_technical_reference_manual_en.html#page=1029
6. E: the TRM says the host "should show a new serial port moments later" after a connect. No document gives a
   re-enumeration time in ms. Espressif gives only esptool's 0.2 s. A number from us would be H.
7. E: ESP-IDF says: when the host does not read, the chip's TX waits once 50 ms and then drops output. The PC terminal
   "waits for the chip to ingest" bytes sent to it, unlike a UART bridge.
   https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/api-guides/usb-serial-jtag-console.html#limitations
8. E (by a fetch summary, line numbers approximate): MicroPython v1.29.0 `ports/esp32/usb_serial_jtag.c` ~97-109 waits
   at most 200 ms for a writable TX FIFO, then sets `terminal_connected = false` and drops the output. It sets it true
   again when the FIFO is writable. RX bytes go into a ring buffer, and Ctrl-C raises the keyboard interrupt (~49-70).
   So output while no host listens is lost. Input sent before the console is up is not safe to count on. (H: the
   bytes are lost, since the source holds no host-connected check on RX.)
9. E: mpremote 1.29.0 opens the port with pyserial defaults (DTR and RTS asserted on open). It never toggles them
   itself (`mpremote/transport_serial.py:52-100`). `connect` has a `wait` count of 1 s retries, but only for an open
   that fails with OSError, not for an open that works and returns silence.
10. E: `enter_raw_repl` sends `\r\x03`, drains, sends `\r\x01`, and reads up to `timeout_overall=10` s for the raw REPL
    banner. If nothing comes, it prints `b''` and raises "could not enter raw repl" (`transport_serial.py:178-210`).
    There is no retry in mpremote.
11. H: the port that deploy.py hands to mpremote is the device node from before the reset. macOS re-created the node
    while esptool's close and mpremote's open raced it. A handle on the old node reads nothing. This fits "worked at
    once after macOS dropped and re-added the device" (bench note, step 9).
12. H: the board was in a good state throughout (it printed `ready` after an RTS pulse). The fault is host side
    timing and a stale handle, not the image.

## What the fix should do

- Do not trust the first mpremote call after esptool. Wait, then probe, then do the work.
- Wait for the port: poll `serial.tools.list_ports` for the VID:PID 303a:1001 (and the same serial number, the MAC)
  for up to about 10 s. If the node vanished, wait until it is back. If it never vanished, settle 1 s (H) and go on.
- Probe: run `mpremote connect <port> exec "pass"` as a loop with a per-try timeout of about 5 s, for a total of about
  20 s. Re-resolve the port by VID:PID and serial on each try, because the node can change.
- Consider esptool `--after watchdog-reset` (documented, fact 2) as an option to test at the bench. Mark it untested
  until the PO runs it. A hard-reset plus wait stays the default.
- Keep mpremote's stderr in the error. The current `could not enter raw repl` plus `b''` line is the evidence.
- Keep `ready unknown` as the verdict when the probe loop ends without an answer. A timeout is not a pass.
