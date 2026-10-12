"""
A stand-in for wokwi-cli in the tests (P130), so no Wokwi CI minute is spent. It writes FAKE_WOKWI_SERIAL to the serial
log it is given, keeps its arguments and the scenario it was handed in the file FAKE_WOKWI_SEEN names, and exits with
FAKE_WOKWI_EXIT.
"""

import json
import os
import sys

args = sys.argv[1:]


def after(flag):
    return args[args.index(flag) + 1]


with open(after("--serial-log-file"), "w") as serial:
    serial.write(os.environ.get("FAKE_WOKWI_SERIAL", ""))
if os.environ.get("FAKE_WOKWI_SEEN"):
    with open(after("--scenario")) as scenario, open(os.environ["FAKE_WOKWI_SEEN"], "w") as seen:
        json.dump({"args": args, "scenario": scenario.read()}, seen)
print("Wokwi CLI v0.0.0 (fake)", file=sys.stderr)
print(os.environ.get("FAKE_WOKWI_SAID", ""), file=sys.stderr)
sys.exit(int(os.environ.get("FAKE_WOKWI_EXIT", "0")))
