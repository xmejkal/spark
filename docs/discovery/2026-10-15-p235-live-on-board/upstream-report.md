# Draft: report to MicroPython (not posted; waits on the PO's OK)

Title: ESP32-C6 (XIAO): USB-Serial-JTAG output stays dead after some power-on boots, input still works

Board: Seeed XIAO ESP32-C6, firmware "MicroPython v1.29.0 on 2026-08-24; Seeed XIAO ESP32C6 with ESP32-C6".
Host: macOS (Darwin 24.6.0), pyserial, mpremote 1.29.0. The board is on the Mac's own USB port.

What happens: after a cable replug (a power-on boot), `main.py` runs. On some boots, the host reads no byte from the
USB-Serial-JTAG console. Input still works: code sent in the raw REPL runs (it toggled the on-board LED on GPIO15, and
the LED blinked). `mpremote exec` fails with `TransportError: could not enter raw repl` and prints `b''`.
A soft reset (Ctrl-D) does not bring the output back. A chip reset from the USB side does: opening the port with DTR
and RTS set to False gave `rst:0x15 (USB_UART_HPSYS)`, and after that boot the output works.

How often: 1, 3, 6 and 1 silent boots in rounds of 10, 10, 10 and 4 replugs, with the try 10 s after the port appears.

To reproduce: a `main.py` that loops and polls `sys.stdin` without blocking. Replug the cable 10 times. After each
replug, wait 10 s and run `mpremote connect <port> exec "print(1)"`.

Possibly related: a report of no USB output after power-on with input accepted, fixed by
`CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y` (seen at https://notes.alelec.net/assets/mpy-triage/pair/3132.html). In our
case the output works on most boots.
