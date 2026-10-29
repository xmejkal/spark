#!/usr/bin/env python3
"""
The child process of import_firmware.py (P59, P443): it imports one firmware module and says how that went.

    python3 -I -B import_child.py MODULE FOLDER...

MODULE is imported with the FOLDERs first on sys.path, in that order. import_firmware.py runs it with -I, so the
child's own folder and the current folder stay off sys.path, and a firmware cannot import this file.

Before the import, the child gives CPython's `time` the names MicroPython's has, so a display driver that sleeps in its
constructor imports. The values are fixed and do nothing. Real `time.sleep` and `time.time` stay real, and only this
child is patched:

    time.sleep_ms(ms), time.sleep_us(us)    return None at once, never a real sleep
    time.ticks_ms(), time.ticks_us()        return 0, "nothing has passed"
    time.ticks_add(t, delta)                returns t + delta, with no wrap at 2**30
    time.ticks_diff(a, b)                   returns a - b, MicroPython's order, with no wrap

Because ticks_ms() is always 0, a driver's wait loop on it times out here, and the timeout line blames the loop.
"""

import importlib
import sys
import time

#: MicroPython's time names, with the fixed values the child gives them.
MICROPYTHON_TIME = {
    "sleep_ms": lambda ms: None,
    "sleep_us": lambda us: None,
    "ticks_ms": lambda: 0,
    "ticks_us": lambda: 0,
    "ticks_add": lambda ticks, delta: ticks + delta,
    "ticks_diff": lambda end, start: end - start,
}


# --- MVP --- (P443)
def add_micropython_time(module):
    """Set MicroPython's time names on `module`, which is the `time` module in the child."""
    for name, function in MICROPYTHON_TIME.items():
        setattr(module, name, function)


def main(argv):
    add_micropython_time(time)
    sys.path[:0] = argv[1:]
    importlib.import_module(argv[0])


if __name__ == "__main__":
    main(sys.argv[1:])
