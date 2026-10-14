"""
After a flash: does the board wait in download mode, and did the person press its reset button? (P243, #252)

A library. On the XIAO ESP32-C6 the first flash after BOOT and R left the chip in its ROM's download mode, which
prints `waiting for download` and is silent for mpremote (P238's spike, round 2,
docs/observations/2026-10-14-p238-spike/finding.md). `DownloadModeProbe` reads the board's console with DTR and RTS
off, through the Python that mpremote runs on, which has pyserial. Then it waits until the port goes and comes back,
which is the board restarting after a press of its R button. deploy.py asks for the press and runs the ready check
again.
"""

import os
import subprocess
import time

from run_scenario import printed_text

#: What the ESP32 ROM prints when it boots into download mode, as the XIAO C6 printed it on 2026-10-14 (AT157).
DOWNLOAD_MODE = "waiting for download"
#: What deploy.py asks the person to do.
PRESS_RESET = "the board waits in download mode: press the board's R (reset) button once"
#: How long the console is read, how long the person has to press R, and how often the port is looked at, in seconds.
READ_S, RESET_WAIT_S, POLL_S = 2, 60, 0.1
#: What deploy.py says when no reset came. The wait looks for the same port name only.
NO_RESET = ("the board waits in download mode, and its port did not go and come back in %d s: press its R button. If "
            "the port came back under another name, `python3 -m mpremote devs` lists the ports" % RESET_WAIT_S)
#: What the probe says of a port it could not read (P244): a could-not-run, never a silent console.
UNREAD = "could not read the port: %s"
#: Run with mpremote's Python: print what the port says in `seconds`, opened with DTR and RTS off, so that opening
#: it does not choose the boot mode. argv: the port, the seconds.
READ_CONSOLE = """import sys, time, serial
s = serial.Serial()
s.port, s.baudrate, s.timeout, s.dtr, s.rts = sys.argv[1], 115200, 0.1, False, False
s.open()
out, end = b"", time.monotonic() + float(sys.argv[2])
while time.monotonic() < end:
    out += s.read(512)
s.close()
sys.stdout.write(out.decode("utf-8", "replace"))
"""


class SystemClock:
    """Adapter: the computer's own clock."""

    monotonic, sleep = staticmethod(time.monotonic), staticmethod(time.sleep)


class DownloadModeProbe:
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
        try:
            done = self.run(self.python + ["-c", READ_CONSOLE, self.port, str(READ_S)], capture_output=True, text=True,
                            timeout=READ_S + 10, check=True)
        except subprocess.CalledProcessError as failed:
            return None, ((failed.stderr or "").strip().splitlines() or [str(failed)])[-1]
        except (OSError, subprocess.SubprocessError) as failed:
            return None, str(failed)
        return printed_text(done.stdout), None

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
