"""
A stand-in for wokwi-cli in the tests (P130), so no Wokwi CI minute is spent. Like wokwi-cli, it writes the board's serial
output (FAKE_WOKWI_SERIAL) to the serial log it is given and echoes it on stdout, prints its progress (FAKE_WOKWI_OUT) on
stdout and its errors (FAKE_WOKWI_ERR) on stderr, and exits with FAKE_WOKWI_EXIT. It keeps its arguments and the scenario
it was handed in the file FAKE_WOKWI_SEEN names. FAKE_WOKWI_NOISE adds a byte that is not UTF-8 to the serial output.
"""

import json
import os
import sys

args = sys.argv[1:]


def after(flag):
    return args[args.index(flag) + 1]


serial = os.environ.get("FAKE_WOKWI_SERIAL", "").encode() + (b"\xff\n" if os.environ.get("FAKE_WOKWI_NOISE") else b"")
with open(after("--serial-log-file"), "wb") as log:
    log.write(serial)
if os.environ.get("FAKE_WOKWI_SEEN"):
    with open(after("--scenario")) as scenario, open(os.environ["FAKE_WOKWI_SEEN"], "w") as seen:
        json.dump({"args": args, "scenario": scenario.read()}, seen)
print("Wokwi CLI v0.0.0 (fake)", flush=True)
sys.stdout.buffer.write(serial)
sys.stdout.buffer.flush()
print(os.environ.get("FAKE_WOKWI_OUT", ""))
print(os.environ.get("FAKE_WOKWI_ERR", ""), file=sys.stderr)
sys.exit(int(os.environ.get("FAKE_WOKWI_EXIT", "0")))
