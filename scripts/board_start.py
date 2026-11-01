"""
After the write: find the board's port, and wait until the firmware really starts (P462, #630).

A library. `BoardStartService` lists the boards on USB (mpremote `devs`, which opens no port) and finds the board by its
MAC, because the port's USB id and name can change when the chip restarts: the FireBeetle 2 listed as 303a:1001 in the
ROM's download mode and as 303a:4001 under MicroPython, on the same name `/dev/cu.usbmodem1101` (P472 bench,
docs/discovery/2026-10-31-p472-no-hands/bench.log). A restart counts only when mpremote answers after it: esptool's own
restart left that board in download mode, with the port gone and back as for a real start.
"""

import collections

import board_codes
import board_look
import download_mode

#: How long the port may take to be listed after the write, in seconds. One bench observation: after esptool's restart
#: command started, the FireBeetle 2 was listed again after at most 7 s, in both tries (bench.log 23:29:16 to 23:29:23,
#: and 23:29:34 to 23:29:41). It counts from esptool's exit; the board log keeps the seconds that one deploy took.
PORT_WAIT_S = 7
#: How often the list is asked for, in seconds: spark's own pace (one `mpremote devs` takes about half a second), no board fact.
POLL_S = 0.5
#: The USB id MicroPython's own port has (the P472 bench: 303a:4001 for the S3 under MicroPython). A console read there
#: is not done: esptool's DTR/RTS reset of that port left the board silent in P472's try 6, and a TinyUSB DTR/RTS pattern
#: starts the bootloader (micropython v1.29.0 shared/tinyusb/mp_usbd_cdc.c:173-206).
MICROPYTHON_USB = "303a:4001"
#: What the board log keeps of a restart: the firmware answered after it, or the board still waited in download mode.
COUNTED = "reset seen: the firmware answered\n"
NOT_COUNTED_LOG = "a restart in download mode, not counted\n"
PORT_BACK = "port back on %s after %d s\n"

#: Result: how the wait for a start ended. `code` is None when mpremote answered after a restart, else a board_codes
#: code (DOWNLOAD_MODE_STAYED or PORT_GONE); `port` is the port that answered or is listed, None when it is gone;
#: `sentence` says what the person does, empty when `code` is None.
BoardStartResult = collections.namedtuple("BoardStartResult", "code port sentence")


def console_may_be_read(row, looked_port):
    """True when the console of the Port `row` may be read: it is on the port the look used, and not MicroPython's own."""
    return row.device == looked_port and row.usb != MICROPYTHON_USB


def _key(text):
    """A serial or MAC as they are compared: lower case, with no colon."""
    return (text or "").lower().replace(":", "")


class BoardStartService:
    """Service: find one board's port and wait for its start. `finder` lists the boards (board_look.PortFinder), `mac` is
    the board's MAC from the look, `clock` has `monotonic` and `sleep`, `places` (boards.ButtonPlaces) names RESET in
    what the person reads. It keeps `heard`, the lines for the board log, in time order."""

    def __init__(self, finder, mac, clock, places):
        self.finder, self.mac, self.clock, self.places = finder, _key(mac), clock, places
        self.heard = []

    def _listed(self, hint):
        """The Port row the board is listed on now: the row whose serial starts with the MAC (MicroPython's serial is the MAC
        and two more bytes, micropython v1.29.0 ports/esp32/usb.c:67-73), else the row named `hint` (a bridge chip's serial
        is not the MAC). None when neither is listed, or when the list failed this time (`failed` says which)."""
        self.failed = False
        try:
            rows = self.finder.nodes()
        except board_look.LookStop:
            self.failed = True
            return None
        by_mac = [row for row in rows if self.mac and _key(row.serial).startswith(self.mac)]
        return (by_mac or [row for row in rows if row.device == hint] or [None])[0]

    def find_port(self, hint):
        """The Port row the board is listed on, waiting at most PORT_WAIT_S for it. None when it is not listed in that time."""
        begin = self.clock.monotonic()
        while True:
            found = self._listed(hint)
            if found or self.clock.monotonic() - begin >= PORT_WAIT_S:
                break
            self.clock.sleep(POLL_S)
        if found:
            self.note(PORT_BACK % (found.device, self.clock.monotonic() - begin))
        return found

    def note(self, text):
        """Keep a line for the board log."""
        self.heard.append(text)

    def gone_result(self):
        """The result for a board that is not listed."""
        return BoardStartResult(board_codes.PORT_GONE, None, download_mode.port_gone(self.places))

    def wait_for_start(self, port, read, show_line, timeout_s=download_mode.RESET_WAIT_S):
        """Wait at most `timeout_s` for the port to go and come back, and call `read(port)` each time it does: it says
        whether mpremote answered. A restart after which it does not answer is shown to the person (`show_line`) and the
        wait goes on. A BoardStartResult."""
        end, gone = self.clock.monotonic() + timeout_s, False
        while self.clock.monotonic() < end:
            row = self._listed(port)
            if row is None:
                gone = True
            elif gone:
                gone, port = False, row.device
                if read(port):
                    self.note(COUNTED)
                    return BoardStartResult(None, port, "")
                self.note(NOT_COUNTED_LOG)
                show_line("  " + download_mode.not_counted(self.places))
            self.clock.sleep(POLL_S)
        row = self._listed(port)
        if row is None and self.failed:  # a failed list is not a gone port: ask once more
            row = self._listed(port)
        if row is None:
            return self.gone_result()
        return BoardStartResult(board_codes.DOWNLOAD_MODE_STAYED, row.device, download_mode.no_reset(self.places))
