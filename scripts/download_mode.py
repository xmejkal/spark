"""
After a flash: does the board wait in download mode, and did the person press its reset button? (P243, #252)

A library. On the XIAO ESP32-C6 the first flash after BOOT and R left the chip in its ROM's download mode, which
prints `waiting for download` and is silent for mpremote (P238's spike, round 2,
docs/observations/2026-10-14-p238-spike/finding.md). This module holds the ROM's words and what deploy.py says about
them. board_console.py's `ConsoleProbe` reads the console and waits for the press of R (P251 moved it there).
"""

import boards
from run_scenario import READY

#: What the ESP32 ROM prints when it boots into download mode, as the XIAO C6 printed it on 2026-10-14 (AT157).
DOWNLOAD_MODE = "waiting for download"
#: What deploy.py asks the person to do, formatted by press_reset.
PRESS_RESET = "the board waits in download mode: press the board's %(reset)s once"
#: How long the person has to press R, in seconds.
RESET_WAIT_S = 60
#: What deploy.py says when no reset came, formatted by no_reset. The wait looks for the same port name only.
NO_RESET = ("the board waits in download mode, and its port did not go and come back in %(wait)d s: press its %(reset)s. "
            "If the port came back under another name, `python3 -m mpremote devs` lists the ports")
#: What the board log adds when the console heard the firmware's `ready`, and deploy.py read the board again (P245).
READ_AGAIN = "read again"


def press_reset(places=boards.ButtonPlaces.EMPTY):
    """PRESS_RESET with the RESET button's place from `places`, a boards.ButtonPlaces."""
    return PRESS_RESET % {"reset": places.reset}


def no_reset(places=boards.ButtonPlaces.EMPTY):
    """NO_RESET with the wait and the RESET button's place from `places`."""
    return NO_RESET % {"wait": RESET_WAIT_S, "reset": places.reset}


def booted(console):
    """True when a line of `console` is the firmware's `ready`: the board finished its restart after mpremote asked
    (P245, the 2026-10-15 bench)."""
    return READY in [line.strip() for line in console.splitlines()]
