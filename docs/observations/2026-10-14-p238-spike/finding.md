# P238 spike, first round: the XIAO ESP32-C6's console after a reset

Claude ran these rows on the PO's XIAO ESP32-C6 on 2026-10-14 (`/dev/cu.usbmodem101`, MicroPython v1.29.0, Seeed
build, the button-light firmware, nothing wired). Each row restarts the board and sends bytes. Nothing was erased or
written. The scripts are beside this file. Card: [P238, #235](https://github.com/xmejkal/spark/issues/235).

## The short version

One cause is proven: when MicroPython's input buffer is full, a Ctrl-C never gets through. The rest is not
stable. The same sequence gave the MicroPython prompt in one run and nothing in the next, so this round found no
sequence that works every time.

## Proven

- Code (MicroPython v1.29.0, `ports/esp32/usb_serial_jtag.c`, `usb_serial_jtag_handle_rx`): the board reads from the
  USB port only as many bytes as its input buffer has room for, and it looks for Ctrl-C only among the bytes it read.
  The button-light firmware never reads its input, so every byte that is not Ctrl-C stays in the buffer.
- Bench, row E3: after 300 bytes of `a`, Ctrl-C got no answer, and a second Ctrl-C neither. Before that, rows E1 and
  E2 got the prompt, also after 10 s of waiting.
- Code (same file, `usb_serial_jtag_tx_strn`): output that the computer does not take within 200 ms is dropped.
- Bench: opening the port does not restart the board (4 opens, no boot text). The suspect is ruled out.
- Bench: after esptool's reset, the ROM did not answer esptool with `--before no-reset`, so the board was not waiting
  in download mode.

## Not stable

- After esptool's reset, mpremote failed in every try (rows E5, E5b), at once and after 5 s, and pyserial read
  nothing for 3 s (E6).
- After a reset by RTS with the port open, the board printed `ready` every time. A Ctrl-C then gave the prompt in
  some runs and nothing in others: in the same session (E1 yes, run 5 no), after a reopen (E4b no, run 5 yes).
- mpremote after a reset by RTS with the port open and then closed: no answer after 0, 1 or 3 s.
- During two resets with the port open, macOS dropped the device ("Device not configured").

## What this means for spark

deploy.py's after-flash steps depend on a Ctrl-C reaching a running firmware. On this board that is not
reliable. A wait and a retry alone will not make it pass every time. Ways that do not depend on luck:

1. Keep mpremote's words and say `ready unknown` honestly. This is step 1 of the synthesis and is needed in any case.
2. Read the board before its firmware runs: restart it with the port open, and read `ready` from the boot output in
   the same session. That proves the firmware starts, but it does not check the files.
3. A firmware that reads its input, so the buffer never fills (the conversation writes the firmware, not spark).
4. A second round of this spike with 20 tries per row, to measure how often each sequence works.

## Round 2, 2026-10-14 afternoon, on the blink project (P236)

Short version: 15 of 15 esptool resets booted the firmware when nothing else held the port. Download mode came only
when the chip was already in it, or when a probe opened the port at a reset. The fix does not need the exact cause:
after a flash, deploy.py tells download mode apart from a silent board and asks the person to press R.

1. The blink firmware reads its input, so idea 3 above is in place. Its console answers typed lines.
2. The first flash (13:50) followed the PO's presses of BOOT and R. After esptool's reset, mpremote heard nothing.
   A probe that opened the port with DTR and RTS off read `waiting for download`. A press of R booted the firmware.
3. Two later deploys (14:03 and 14:12, the board running its firmware before each) said `ready seen` by themselves.
4. A script ran `esptool chip-id` and then opened the port with DTR and RTS off, read 4 s and sent Enter. Three runs
   from the running firmware, and three pairs of `--after no-reset` then a normal reset: all 15 reads show the ROM boot
   lines, then `ready`. Even after `--after no-reset`, the chip restarted, so opening the port restarted it.
5. While the PO's mpremote held the port, esptool failed with "Could not exclusively lock port", and one esptool reset
   froze his mpremote session.

What is proven: on the XIAO C6's USB-Serial-JTAG port, opening the port can restart the chip, and a chip that waits in
download mode stays silent for mpremote ("could not enter raw repl", nothing received). Not proven: which line states
choose download mode. Espressif documents that the USB-Serial-JTAG peripheral maps DTR and RTS to the boot pin and the
reset; the exact sequence was not measured here.

The proposed fix (a story, not part of this spike): after the flash, when mpremote hears nothing, deploy.py reads the
console with DTR and RTS off. If it reads `waiting for download`, it says "press the board's R (reset) button once" and
waits for the port to come back, then runs the ready check. A board that says nothing at all stays `ready unknown`.
