# Draft: report to MicroPython (not posted; changed after the PO's OK at 09:07, needs his re-read)

Title: ESP32-C6 (XIAO): USB-Serial-JTAG output stayed dead after a power-on boot while input worked

Scope: one board, one Mac, one firmware, one morning (2026-10-15). Board: Seeed XIAO ESP32-C6, firmware "MicroPython
v1.29.0 on 2026-08-24; Seeed XIAO ESP32C6 with ESP32-C6" (its banner, read on that morning). Host: macOS (Darwin
24.6.0), pyserial, mpremote 1.29.0. The board was on the Mac's own USB port. The firmware's `main.py` imports a module
whose loop polls `sys.stdin` without blocking and drops what it reads.

What we saw: after a cable replug (a power-on boot), on some boots the host read no byte from the USB-Serial-JTAG
console, neither on open nor after Ctrl-C and Ctrl-A. On one such boot we sent code in the raw REPL anyway: it toggled
the on-board LED (GPIO15) 6 times, and the LED blinked 3 times. So the input reached the board and the code ran. On
that boot, `mpremote exec` failed twice with `TransportError: could not enter raw repl`. A soft reset (Ctrl-B, Ctrl-D)
did not bring the output back. Opening the port with DTR and RTS set to False restarted the chip
(`rst:0x15 (USB_UART_HPSYS)`), and after that boot the output worked.

We have not ruled out a loss on the Mac's side: the chip reset also makes the Mac enumerate the port again.

How often: a probe opened the port 10 s after it appeared, listened, sent Ctrl-C and Ctrl-A, and listened again. It
heard nothing on 1 of 10 replugs in a first round and on 6 of 10 in a second. Those two counts fit one rate near 0.35
by chance (Fisher exact p = 0.057).

What ran: the probe (pyserial, default open, then `\r\x03\r\x01`) and, before it, `mpremote connect <port> exec
"print(1)"` 10 s after each of 10 replugs (3 failures, not each checked for silence). We did not run a minimal
`main.py` of our own, so we cannot yet offer one.

Possibly related: a report of no USB output after power-on with input accepted, fixed by
`CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y` (seen at https://notes.alelec.net/assets/mpy-triage/pair/3132.html). In our
case the output works on most boots.
