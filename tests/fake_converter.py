"""
A stand-in for the diagram converter (circuit-to-wokwi) in the design goldens (P699), so no golden runs node or the
real bundle. Like the converter, it is given `--circuit` or `--netlist`, `--out`, `--mapping` and `--chips`, and it
writes a diagram to `--out`: one canned diagram, the board, a red LED and a button, its serial port wired to Wokwi's
serial monitor. It prints nothing and exits 0.
"""

import json
import sys

DIAGRAM = {
    "version": 1,
    "author": "spark's fake converter",
    "editor": "wokwi",
    "parts": [
        {"type": "board-esp32-s3-devkitc-1", "id": "esp", "top": 0, "left": 0, "attrs": {}},
        {"type": "wokwi-led", "id": "LED1", "top": -60, "left": 120, "attrs": {"color": "red"}},
        {"type": "wokwi-pushbutton", "id": "BTN1", "top": 60, "left": 120, "attrs": {}},
    ],
    "connections": [
        ["esp:TX", "$serialMonitor:RX", "", []],
        ["esp:RX", "$serialMonitor:TX", "", []],
        ["esp:13", "LED1:A", "green", []],
        ["LED1:C", "esp:GND.1", "black", []],
        ["esp:4", "BTN1:1.l", "green", []],
        ["BTN1:2.l", "esp:GND.2", "black", []],
    ],
}

args = sys.argv[1:]
with open(args[args.index("--out") + 1], "w") as out:
    json.dump(DIAGRAM, out, indent=2)
    out.write("\n")
