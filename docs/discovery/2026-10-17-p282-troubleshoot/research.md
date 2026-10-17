# P282 research: what to do when a board does not answer

The research for P282 (#326), 2026-10-17. One Sonnet agent read the primary sources, and the plan council's refuter
(Opus) checked them against esptool's installed source and the bench logs. Each fact names its source. A step that
only the bench backs says so, with its count.

## Short version

- esptool decides its own reset, and it has no error code per kind of failure. spark shows esptool's `ERROR:` line
  and never decides on it.
- Espressif documents manual download mode for a board that disappears. For a listed board that stays silent, spark's
  steps come from its own bench logs, each with n.
- mpremote documents no failure modes at all.
- Doctor tools run named checks, and each check gives a status and one fix line.

## esptool 5.5.0

- On USB PID 0x1001 (the USB-Serial/JTAG port), esptool's `default-reset` uses `USBJTAGSerialReset`, a DTR and RTS
  pulse (installed source, `esptool/loader.py:850`). P238's bench saw no gain from a spark cure before it (15 of 15,
  docs/observations/2026-10-14-p238-spike/finding.md).
- A fatal error exits 2 (`esptool/__init__.py:1374`). A pyserial error exits 1 (`esp_pylib/logger.py:310`). No error
  kind is machine-readable. The first stderr line of the failure starts with `ERROR: `, and the last lines are a URL
  or a hint (the refuter reproduced this).
- `--before` modes: `default-reset`, `usb-reset`, `no-reset`, `no-reset-no-sync` (`esptool/__init__.py:422`).
- The esptool troubleshooting page for the ESP32-C6, "latest" (https://docs.espressif.com/projects/esptool/en/latest/esp32c6/troubleshooting.html):
  for "Failed to connect" it names the port, permissions and other programs on the port, a stable 3.3 V, the boot
  pins, other devices on the GPIOs, and a lower baud rate. Its USB-Serial/JTAG part ties manual download mode to a
  device that disappears.
- Boot mode selection, "latest" (https://docs.espressif.com/projects/esptool/en/latest/esp32c6/advanced-topics/boot-mode-selection.html):
  hold BOOT (GPIO9 low), press RESET, keep BOOT held while esptool starts.

## The ESP32-C6's USB-Serial/JTAG console

- The esp-idf guide, "latest" (https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/api-guides/usb-serial-jtag-console.html):
  the device disappears when the app reconfigures GPIO12/13 or disables the controller. In deep sleep it looks
  unplugged. In light sleep it can stay listed but unresponsive, and a replug cures it.
- A board that stays listed with a silent output after a power-on is in no Espressif document. The bench saw it
  (AT187, P251).

## mpremote 1.29.0

- The docs (https://docs.micropython.org/en/latest/reference/mpremote.html) describe `reset`, `soft-reset` and
  `resume`, and no failure modes: "could not enter raw repl" and "failed to access" are not documented.
- mpremote opens the port with an exclusive lock (`mpremote/transport_serial.py:52`), and so does esptool. spark's
  console read opened it without the lock, so it could not see a held port (the refuter reproduced this).

## Doctor tools

- `flutter doctor` (https://docs.flutter.dev/install/troubleshoot): each check gives ok, a warning or an error, and a
  failed check gives a fix line.
- `brew doctor` (https://docs.brew.sh/Manpage): named checks, `--list-checks`, a non-zero exit when a check finds
  something.

## What the bench backs (docs/observations)

| step | backed by | n |
| --- | --- | --- |
| press R for a board in download mode | P236 bench, AT157 | 1 |
| the port open restarted a silent C6 | P251 cure, AT187 | 1 per case |
| hold BOOT, press R, before esptool | p238 finding.md:52 | 1 |
| a replug reached the board | P235 reach test | 7 of 10 |

The guesses that the plan cut: a replug with BOOT held, and a reflash after a replug.
