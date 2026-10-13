# P228: the read-only bench on the XIAO ESP32-C6

Read 2026-10-13, 16:22 to 16:23 UTC, by Claude on the PO's Mac, with the PO's Seeed XIAO ESP32-C6 (D13, D14). By the command list
below, nothing was erased or written, and no Wokwi minute was spent. Tools: esptool v5.5.0, mpremote 1.29.0.

## Short version

The board reads as an ESP32-C6FH4, revision v0.1, with 4 MB flash inside the chip, and secure boot and flash
encryption off. Every esptool read restarts the board, and a plain listen most likely does too. A read that names the wrong chip (`--chip esp32s3`)
refuses with exit 2 and touches nothing. The board does not run MicroPython. It boots firmware that stayed silent for
8 s, of unknown origin. The USB serial number is the MAC, so the host names the board before any byte is sent.

## The raw outputs

The files in [`p228/`](p228/) are the outputs as printed, kept as test data for spark's look command. Two things are
masked for the public repository: home paths read `~`, and the last three bytes of the MAC read `xx:xx:xx`.

| file | what ran | result |
| --- | --- | --- |
| `01-host.txt` | `ioreg` and `mpremote devs`, no contact with the board | `303a:1001`, "Espressif USB JTAG/serial debug unit", serial number = the base MAC |
| `02-mpremote.txt` | `mpremote connect … exec` for `sys.implementation`, `os.uname()`, `os.statvfs('/')`, `os.listdir('/')` | exit 1, "could not enter raw repl", 0 bytes back |
| `03-esptool.txt` | `chip-id`, `flash-id`, `read-mac`, `get-security-info` | 4 of 4 exit 0 |
| `04-wrong-chip.txt` | `--chip esp32s3 read-mac`, then `mpremote devs` | exit 2, "This chip is ESP32-C6, not ESP32-S3. Wrong chip argument?". The port is back with no button press |
| `05-listen.txt` | 8 s on the port, nothing sent | 123 bytes: the bootloader's lines, then silence |

## What the reads show, by assumption

- A4 (esptool refuses another chip, writes nothing): holds on this board. The refusal comes at connect, before the
  stub is uploaded. Measured, 1 run.
- A5 (esptool 5.5.0 prints chip, flash size and MAC in a form the core can parse): holds. Each value is on its own
  `Label: value` line: `Chip type`, `Features`, `USB mode`, `BASE MAC`, `Detected flash size`. Measured, 1 run.
- A6 (a read-only look leaves the board running, with no button press): partly. After the reads, the port was back with no
  button press (one check). But each esptool read ends with "Hard resetting via RTS pin". When the port was opened to listen, bootloader
  lines appeared (`05-listen.txt`), about 20 s after the last esptool reset. So the open most likely restarted the
  board. One run, not proven. A running gadget restarts on every look.
- A7 (the facts catch the wrong board): partly. Chip and flash size match `boards/xiao-esp32-c6.json` (`chip`
  `esp32c6`). The 4 MB comes from esptool only. Seeed's own figure was not read here. The package name `ESP32-C6FH4` is a stronger fact than the record holds: no field says
  "in-package flash". Revision and wiring are not readable.
- A10 (the USB serial number is the MAC): holds in the state the board was in, with non-MicroPython firmware.
  `mpremote devs` shows it. It was not measured under MicroPython.
- A11 (revision by eye): not read. The chip reports `revision v0.1`, which is the chip's, not the board's.

## Notes for building the look into spark

These are facts for P219's design (D37: the look is its own command), not a design.

1. One esptool call gives the whole look. `flash-id` prints chip type, features, USB mode, crystal, the MAC and the
   flash size (`03-esptool.txt`).
2. Parse lines, not positions. The values are `Label:   value` lines. `MAC` on the C6 is the 8-byte EUI-64
   (`…:ff:fe:…`). `BASE MAC` is the 6-byte one that the USB serial number and `mpremote devs` show. The look must
   compare `BASE MAC`.
3. The port list is a free first step. `mpremote devs` gives the port, the MAC and `303a:1001` with no contact. With
   two or more boards (D25) this is where the person picks one.
4. Every esptool contact restarts the board, and a listen most likely does too. The look must say so before it runs (D37).
5. "Not MicroPython" is a finding, not an error. mpremote's exit 1 with 0 bytes was seen with non-MicroPython firmware.
   A busy board can give the same.
   The look reports "other firmware", which D34 uses to offer a backup.
6. The wrong-chip refusal costs one call and exits 2. The look can name the record's chip and let esptool refuse, or
   detect the chip and compare. Detection probably gives the better message, untested.
7. Silent firmware tells nothing about its origin. Only a facts file (D22) can say what spark put there.
8. Gaps in the record: no field for flash in the package or on a module, and no field for the chip package
   (`ESP32-C6FH4`). Both are readable, so a check can compare them (P94: checks read facts in records).
9. Seen by the PO, not recorded: through the hub the board got power (its orange light blinked) but showed no USB
   device. On the Mac's own port it appeared. The look's "no board found" message can name both causes.
