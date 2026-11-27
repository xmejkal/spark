"""
After a flash: does the board wait in download mode, and did the person press its reset button? (P243, #252)

A library. On the XIAO ESP32-C6 the first flash after BOOT and R left the chip in its ROM's download mode, which
prints `waiting for download` and is silent for mpremote (P238's spike, round 2,
docs/observations/2026-10-14-p238-spike/finding.md). This module holds the ROM's words and what deploy.py says about
them. board_console.py's `ConsoleProbe` reads the console and waits for the press of R (P251 moved it there).
"""

from spark.bench.board_connection import USB_SERIAL_JTAG
from spark.records import board_records
from spark.firmware.scenario_steps import has_ready_line

#: What the ESP32 ROM prints when it boots into download mode, as the XIAO C6 printed it on 2026-10-14 (AT157).
DOWNLOAD_MODE = "waiting for download"
#: What deploy.py asks the person to do, formatted by press_reset.
PRESS_RESET = "the board waits in download mode: press the board's %(reset)s once%(orientation)s"
#: How long the person has to press R, in seconds.
RESET_WAIT_S = 60
#: What deploy.py says when no start came, formatted by no_reset (P462: the wait finds the port by the board's MAC).
NO_RESET = "the board still waits in download mode after %(wait)d s: press its %(reset)s%(orientation)s"
#: What deploy.py says when the port went and came back, and mpremote did not answer: a restart that left download
#: mode on (esptool's own did on the 2026-10-31 bench), formatted by not_counted.
NOT_COUNTED = "the board restarted and still waits in download mode: press its %(reset)s once%(orientation)s"
#: What deploy.py says when the board's port is gone, formatted by port_gone.
PORT_GONE = ("the board's port is gone: press its %(reset)s once%(orientation)s. If the port stays gone, unplug the board and "
             "plug it in, then run `%(devs)s` to see its port")
#: What the board log adds when the console heard the firmware's `ready`, and deploy.py read the board again (P245).
READ_AGAIN = "read again"
#: What the board log keeps of the first read when deploy.py reads the board again (P1025): its verdict and sentence,
#: then all that mpremote printed, with P1022's settle note, formatted by first_read.
FIRST_READ = "the first read: %s: %s\n"


def press_reset(places=board_records.ButtonPlaces.EMPTY):
    """PRESS_RESET with the RESET button's place from `places`, a board_records.ButtonPlaces."""
    return PRESS_RESET % {"reset": places.reset, "orientation": places.orientation}


def no_reset(places=board_records.ButtonPlaces.EMPTY):
    """NO_RESET with the wait and the RESET button's place from `places`."""
    return NO_RESET % {"wait": RESET_WAIT_S, "reset": places.reset, "orientation": places.orientation}


def not_counted(places=board_records.ButtonPlaces.EMPTY):
    """NOT_COUNTED with the RESET button's place from `places`."""
    return NOT_COUNTED % {"reset": places.reset, "orientation": places.orientation}


def port_gone(places=board_records.ButtonPlaces.EMPTY, devs="mpremote devs"):
    """PORT_GONE with the RESET button's place from `places`, and `devs`, the line that lists the ports (P1264: the one spark ran)."""
    return PORT_GONE % {"reset": places.reset, "orientation": places.orientation, "devs": devs}


def first_read(ready):
    """FIRST_READ for the first read's ReadyResult `ready`, then its log. The log ends its last line, so the board log's
    next line starts a line of its own (P1025)."""
    log = ready.log.rstrip("\n") + "\n" if ready.log else ""
    return FIRST_READ % (ready.verdict, ready.sentence) + log


def booted(console):
    """True when a line of `console` has the firmware's `ready` as its first word (scenario_steps.has_ready_line, P1025):
    the board finished its restart after mpremote asked (P245, the 2026-10-15 bench)."""
    return has_ready_line(console)


def own_usb_of(project, usb=None):
    """True when the board's USB plug is the chip's own, no USB bridge chip's (P1022 slice 3): the port's USB id `usb` is
    Espressif's USB-Serial/JTAG, or the project's board record has the pin role `usb` (board_rules: the chip's own USB D-
    and D+). False when neither holds or the record cannot be read."""
    if usb == USB_SERIAL_JTAG:
        return True
    try:
        roles = board_records.load(project).get("pin_roles")
    except (OSError, ValueError, AttributeError, board_records.BoardError):
        return False
    return isinstance(roles, dict) and isinstance(roles.get("usb"), dict)
