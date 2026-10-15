"""
One board's console, read with the port opened so that the open does not choose the boot mode (P243, P251).

A library. `ConsoleProbe` reads what the board prints with DTR and RTS off, through the Python that mpremote runs on,
which has pyserial. deploy.py uses it to find a board that waits in download mode and to see the press of its R
button (P243). P251 moved it here from download_mode.py and uses the same open as a cure: on the XIAO C6 that open
restarted a board whose USB output died at power-on (docs/observations/2026-10-15-p235-reach-test.md, AT187).
"""

import os
import re
import subprocess
import time
from collections import namedtuple

from download_mode import DOWNLOAD_MODE, RESET_WAIT_S
from run_scenario import printed_text

#: How long the console is read, and how often the port is looked at, in seconds.
READ_S, POLL_S = 2, 0.1
#: How long the cure waits for the port to be there again after its open restarted the board, in seconds.
PORT_BACK_S = 10
#: How long the cure waits after the port is there, before mpremote opens it, in seconds. A guess that P251's bench
#: tests: the shown cures came 20 s or more before the next mpremote call (reach-test.md, 08:25 and 08:48).
PORT_SETTLE_S = 2
#: The ESP32 ROM's line of a restart, `rst:0x15 (USB_UART_HPSYS),boot:0x1e` on the XIAO C6 (AT187), and never a word
#: such as `first:` inside the firmware's own lines.
RESTART = re.compile(r"\brst:0x[0-9a-f]+")
#: What the probe says of a port it could not read (P244): a could-not-run, never a silent console.
UNREAD = "could not read the port: %s"
#: Run with mpremote's Python: print what the port says in `seconds`, opened with DTR and RTS off, so that opening
#: it does not choose the boot mode. argv: the port, the seconds.
READ_CONSOLE = """import sys, time, serial
s = serial.Serial()
s.port, s.baudrate, s.timeout, s.dtr, s.rts = sys.argv[1], 115200, 0.1, False, False
s.open()
out, end = b"", time.monotonic() + float(sys.argv[2])
try:
    while time.monotonic() < end:
        out += s.read(512)
    s.close()
finally:
    sys.stdout.write(out.decode("utf-8", "replace"))
"""


#: Value: what the cure's open heard (all of it, also when the read failed part way), why the read failed or None,
#: whether the board printed a restart, and whether the port was there again after the wait.
Cure = namedtuple("Cure", "heard why restart_heard port_back")


def shows_restart(console):
    """True when `console` holds the ROM's line of a restart."""
    return RESTART.search(console) is not None


class SystemClock:
    """Adapter: the computer's own clock."""

    monotonic, sleep = staticmethod(time.monotonic), staticmethod(time.sleep)


class ConsoleProbe:
    """Adapter: one board's console read with pyserial, in mpremote's Python `python`, and its port's path."""

    def __init__(self, python, port, run=subprocess.run, clock=None, port_exists=os.path.exists):
        self.python, self.port, self.run = list(python), port, run
        self.clock, self.port_exists = clock or SystemClock(), port_exists

    @classmethod
    def for_tool(cls, tool, port, run=subprocess.run):
        """The probe for the tools list's board-shell `tool`, or None when it is not a Python package or no port."""
        if tool.entry.get("kind") != "python" or not port:
            return None
        return cls(tool.command, port, run)

    def console(self):
        """(What the port printed in READ_S seconds, None), or (None, why) when it could not be read."""
        printed, why = self._read()
        return (None, why) if why else (printed, None)

    def _read(self):
        """(What the port printed, also when the read failed part way, why it failed or None)."""
        try:
            done = self.run(self.python + ["-c", READ_CONSOLE, self.port, str(READ_S)], capture_output=True, text=True,
                            timeout=READ_S + 10, check=True)
        except subprocess.CalledProcessError as failed:
            return printed_text(failed.stdout or ""), ((failed.stderr or "").strip().splitlines() or [str(failed)])[-1]
        except subprocess.TimeoutExpired as failed:
            return printed_text(failed.stdout or ""), str(failed)
        except (OSError, subprocess.SubprocessError) as failed:
            return "", str(failed)
        return printed_text(done.stdout), None

    def cure(self):
        """The Cure of a board whose USB output died at power-on (P251): the open with DTR and RTS off, which restarted
        the XIAO C6 in AT187, and what it printed. Then a wait of at most PORT_BACK_S until the port is there again, and
        PORT_SETTLE_S more. It never waits for the port to go: the restart comes during the read."""
        heard, why = self._read()
        end = self.clock.monotonic() + PORT_BACK_S
        while not self.port_exists(self.port) and self.clock.monotonic() < end:
            self.clock.sleep(POLL_S)
        port_back = self.port_exists(self.port)
        if port_back:
            self.clock.sleep(PORT_SETTLE_S)
        return Cure(heard, why, shows_restart(heard), port_back)

    def waits_in_download_mode(self):
        """(True when the console says DOWNLOAD_MODE, what it printed). A port it could not read is never download
        mode, and what it says is UNREAD with the reason, never an empty console (P244)."""
        said, why = self.console()
        if said is None:
            return False, UNREAD % why
        return DOWNLOAD_MODE in said, said

    def wait_for_reset(self, timeout_s=RESET_WAIT_S):
        """True when the port went away and came back within `timeout_s`, as it does when the board restarts."""
        end, gone = self.clock.monotonic() + timeout_s, False
        while self.clock.monotonic() < end:
            if not self.port_exists(self.port):
                gone = True
            elif gone:
                return True
            self.clock.sleep(POLL_S)
        return False
