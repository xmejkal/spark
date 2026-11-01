"""
One board's console, read with the port opened so that the open does not choose the boot mode (P243, P251).

A library. `ConsoleProbe` reads what the board prints with DTR and RTS off, through the Python that mpremote runs on,
which has pyserial. deploy.py uses it to find a board that waits in download mode (P243; board_start.py waits for its
restart, P462). P251 moved it here from download_mode.py and uses the same open as a cure: on the XIAO C6 that open
restarted a board whose USB output died at power-on (docs/observations/2026-10-15-p235-reach-test.md, AT187).
"""

import datetime
import os
import re
import subprocess
import time
from collections import namedtuple

from download_mode import DOWNLOAD_MODE
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
#: The ROM's last line of a boot, `entry 0x4086b910`, alone on its line. Heard without RESTART it is a boot tail: the
#: read began after the first lines, or the lines were older output still in a buffer, so it is not proof that the
#: cure restarted the board (P251's bench, AT233).
BOOT_END = re.compile(r"^entry 0x[0-9a-f]+\s*$", re.MULTILINE)
#: What the probe says of a port it could not read (P244): a could-not-run, never a silent console.
UNREAD = "could not read the port: %s"
#: The console script's exit code when another program holds the port's lock, as mpremote and esptool do while they run
#: (mpremote 1.29 transport_serial.py:52 opens with exclusive=True). pyserial 3.5 keeps the lock's errno (serialposix.py:387).
EXIT_PORT_BUSY = 3
#: How the person leaves mpremote's console and frees the port. mpremote 1.29 quits on Ctrl-] or Ctrl-X (repl.py:14);
#: in walk 1, Ctrl-C and Ctrl-D did not leave it, and Ctrl-X did (docs/observations/rows/p326-walk1.md, row 14).
LEAVE_CONSOLE = "leave mpremote's console with Ctrl-X"
#: The kinds of a console read: it read the port, another program held it, or it could not read it for another reason.
KIND_READ, KIND_BUSY, KIND_UNREAD = "read", "busy", "unread"
#: Run with mpremote's Python: print what the port says in `seconds`, opened with DTR and RTS off, so that opening
#: it does not choose the boot mode, and with the port's lock, so that a port another program holds is told apart
#: (P282). argv: the port, the seconds.
READ_CONSOLE = """import errno, sys, time, serial
s = serial.Serial()
s.port, s.baudrate, s.timeout, s.dtr, s.rts, s.exclusive = sys.argv[1], 115200, 0.1, False, False, True
try:
    s.open()
except serial.SerialException as cannot:
    sys.stderr.write(str(cannot) + "\\n")
    sys.exit(%d if cannot.errno in (errno.EAGAIN, errno.EWOULDBLOCK) else 1)
""" % EXIT_PORT_BUSY + """out, end = b"", time.monotonic() + float(sys.argv[2])
try:
    while time.monotonic() < end:
        out += s.read(512)
    s.close()
finally:
    sys.stdout.write(out.decode("utf-8", "replace"))
"""


#: Result: the kind of a console read (KIND_READ, KIND_BUSY or KIND_UNREAD), what the port printed (also when the read
#: failed part way), and why it failed, or None.
ConsoleReadResult = namedtuple("ConsoleReadResult", "kind printed why")
#: Value: what the cure's open heard (all of it, also when the read failed part way), why the read failed or None,
#: whether the board printed a restart, whether the port was there again after the wait, and whether it heard the end
#: of a boot (a restart, or only its tail).
Cure = namedtuple("Cure", "heard why restart_heard port_back boot_heard", defaults=(False,))


def shows_restart(console):
    """True when `console` holds the ROM's line of a restart."""
    return RESTART.search(console) is not None


def shows_boot(console):
    """True when `console` holds the ROM's line of a restart or of a boot's end."""
    return shows_restart(console) or BOOT_END.search(console) is not None


class SystemClock:
    """Adapter: the computer's own clock. `now` is the time in the machine's zone, with the zone (P291): the zone a person
    reads, and a stored time carries it."""

    monotonic, sleep = staticmethod(time.monotonic), staticmethod(time.sleep)

    @staticmethod
    def now():
        return datetime.datetime.now().astimezone()


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
        """The ConsoleReadResult of reading the port for READ_S seconds, with its lock."""
        try:
            done = self.run(self.python + ["-c", READ_CONSOLE, self.port, str(READ_S)], capture_output=True, text=True,
                            timeout=READ_S + 10, check=True)
        except subprocess.CalledProcessError as failed:
            why = ((failed.stderr or "").strip().splitlines() or [str(failed)])[-1]
            kind = KIND_BUSY if failed.returncode == EXIT_PORT_BUSY else KIND_UNREAD
            return ConsoleReadResult(kind, printed_text(failed.stdout or ""), why)
        except subprocess.TimeoutExpired as failed:
            return ConsoleReadResult(KIND_UNREAD, printed_text(failed.stdout or ""), str(failed))
        except (OSError, subprocess.SubprocessError) as failed:
            return ConsoleReadResult(KIND_UNREAD, "", str(failed))
        return ConsoleReadResult(KIND_READ, printed_text(done.stdout), None)

    def cure(self):
        """The Cure of a board whose USB output died at power-on (P251): the open with DTR and RTS off, which restarted
        the XIAO C6 in AT187, and what it printed. Then a wait of at most PORT_BACK_S until the port is there again, and
        PORT_SETTLE_S more. It never waits for the port to go: the restart comes during the read."""
        _, heard, why = self.console()
        end = self.clock.monotonic() + PORT_BACK_S
        while not self.port_exists(self.port) and self.clock.monotonic() < end:
            self.clock.sleep(POLL_S)
        port_back = self.port_exists(self.port)
        if port_back:
            self.clock.sleep(PORT_SETTLE_S)
        return Cure(heard, why, shows_restart(heard), port_back, shows_boot(heard))

    def waits_in_download_mode(self):
        """(True when the console says DOWNLOAD_MODE, what it printed). A port it could not read is never download
        mode, and what it says is UNREAD with the reason, never an empty console (P244)."""
        read = self.console()
        if read.kind != KIND_READ:
            return False, UNREAD % read.why
        return DOWNLOAD_MODE in read.printed, read.printed
