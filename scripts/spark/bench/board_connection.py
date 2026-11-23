"""
The one mpremote connection to a board (P215, the bench council's step 1).

A library. `BoardConnection` runs mpremote on one port: code on the board, a file copied to it, a file read back, and
the line that opens its REPL. Its two errors keep mpremote's own words. `BoardUnreachableError`: mpremote could not
talk to the board, for example "could not enter raw repl" (docs/observations/2026-10-14-p215-bench.md).
`BoardCodeError`: the board answered, and the code raised there. board_facts.py and ready_probe.py use it, so a later reconnect strategy
changes one class.
"""

import subprocess

from spark.firmware.scenario_steps import printed_text

#: How MicroPython starts the report of an exception that the board's code raised. mpremote 1.29.0 prints that report
#: to stdout and exits 1, and its own failures to stderr (mpremote/commands.py:489-492, read 2026-10-14).
BOARD_TRACEBACK = "Traceback"
#: What mpremote says when the board did not answer its raw REPL, as part of its last line
#: `mpremote.transport.TransportError: could not enter raw repl` (docs/observations/2026-10-15-p235-reach-test.md).
RAW_REPL_REFUSED = "could not enter raw repl"
#: What mpremote 1.29 says when it could not open the port at all: another program holds it, or it is gone
#: (`failed to access <port> (it may be in use by another program)`, transport_serial.py:104). Nothing ran then.
PORT_NOT_OPENED = "failed to access"
#: How long one mpremote call may take before the board counts as not answering, in seconds.
DEFAULT_TIMEOUT_S = 20
#: The USB id that `mpremote devs` lists for Espressif's own USB-Serial/JTAG (the FireBeetle 2 C6 on the P1007 bench,
#: 2026-11-22: `/dev/cu.usbmodem1101 ... 303a:1001 Espressif USB JTAG/serial debug unit`).
USB_SERIAL_JTAG = "303a:1001"
#: How long the quiet connection sends nothing after its open, in seconds. The open restarts the C6, and a byte sent
#: during that boot left its MicroPython deaf to the host until a ROM download. 2.5 s reached the raw REPL in 9 of 9
#: runs on the P1007 bench (2026-11-22, 15:08 to 15:13 CET, comment on #1466).
SETTLE_S = 2.5
#: How long the quiet connection waits for a port that vanished during the settle, in seconds. In 1 of 9 bench runs the
#: restart enumerated the USB device again, as board_console.PORT_BACK_S waits for after the P251 cure.
PORT_BACK_S = 10
#: Run with mpremote's Python, in place of `python -m mpremote` (P1007): mpremote itself with two changes. Its open
#: leaves DTR and RTS off, as board_console's reads do. And it sends nothing for the settle before it enters the raw
#: REPL, with one reopen of a port that vanished meanwhile: a failed reopen says mpremote's `failed to access`. When the
#: raw REPL still fails, one line `spark: the 2.5 s settle heard ...` goes to stderr before mpremote's traceback (P1022):
#: the last 400 bytes of each read of the settle, and a vanished port with its seconds. A success writes no line, so a
#: board's traceback stays BoardCodeError. argv: the settle, the wait for the port, then mpremote's own arguments.
QUIET_MPREMOTE = """import os, sys, time, serial
from mpremote import main as mpremote_main
from mpremote.transport_serial import SerialTransport
settle, port_back = float(sys.argv.pop(1)), float(sys.argv.pop(1))
opened, entered = serial.Serial.open, SerialTransport.enter_raw_repl
def quiet_open(port):
    port.dtr = port.rts = False
    opened(port)
def drain(port, heard):
    time.sleep(settle)
    heard.append(repr(port.read(port.in_waiting)[-400:]))
def settled_enter(transport, *args, **kwargs):
    heard, began = [], time.monotonic()
    try:
        drain(transport.serial, heard)
    except (OSError, serial.SerialException):
        end = time.monotonic() + port_back
        while not os.path.exists(transport.device_name) and time.monotonic() < end:
            time.sleep(0.1)
        time.sleep(0.5)
        try:
            transport.serial.close()
            transport.serial.open()
            heard.append("(its port vanished and came back after %g s)" % round(time.monotonic() - began, 1))
            drain(transport.serial, heard)
        except (OSError, serial.SerialException) as gone:
            sys.stderr.write("failed to access %s (it vanished and did not come back: %s)\\n" % (transport.device_name, gone))
            sys.exit(1)
    try:
        return entered(transport, *args, **kwargs)
    except Exception:
        sys.stderr.write("spark: the %g s settle heard %s\\n" % (settle, " ".join(heard)))
        raise
serial.Serial.open, SerialTransport.enter_raw_repl = quiet_open, settled_enter
sys.argv[0] = "mpremote"
sys.exit(mpremote_main.main())
"""


def _last_line(text):
    """The last line that holds something, or ''."""
    return next((line.strip() for line in reversed(text.splitlines()) if line.strip()), "")


class BoardUnreachableError(Exception):
    """Error: mpremote could not talk to the board. The message is mpremote's last line, `output` all it printed."""

    def __init__(self, why, output=""):
        super().__init__(why)
        self.output = output


class BoardCodeError(Exception):
    """Error: the board answered, and the code raised there. The message is the board's last line, `output` all it
    printed."""

    def __init__(self, output, exit_code):
        super().__init__(_last_line(output) or "exit %d" % exit_code)
        self.output = output


class BoardConnection:
    """Adapter: mpremote on one board's port. `mpremote` is its command (tool_finder.command_for), `run` runs a command.
    Raises BoardUnreachableError and BoardCodeError."""

    def __init__(self, mpremote, port, run=subprocess.run, timeout_s=DEFAULT_TIMEOUT_S):
        self.command = list(mpremote) + (["connect", port] if port else [])
        self.run, self.timeout_s = run, timeout_s

    def run_code(self, code, keep_running_for=None):
        """
        What the board printed while it ran `code`. With `keep_running_for` seconds, code that still runs then is left
        running, and what it printed until then is the answer. Without it, no answer in timeout_s is
        BoardUnreachableError.
        """
        try:
            return self._mpremote(["exec", code], keep_running_for or self.timeout_s, ran_code=True)
        except subprocess.TimeoutExpired as going:
            if keep_running_for:
                return printed_text(going.stdout)
            raise BoardUnreachableError("no answer in %d s" % self.timeout_s, printed_text(going.stdout)) from None

    def copy_to_board(self, local, remote):
        """Copy the file at `local` to `remote` on the board's filesystem."""
        self._mpremote(["fs", "cp", str(local), ":" + remote], self.timeout_s)

    def read_file(self, remote):
        """The text of `remote` on the board's filesystem."""
        return self._mpremote(["fs", "cat", ":" + remote], self.timeout_s)

    def reset(self):
        """Restart the chip with `mpremote reset`, which runs machine.reset(), so the firmware starts from boot (P252)."""
        self._mpremote(["reset"], self.timeout_s)

    def repl_command(self):
        """The command that opens the board's REPL, where a person sees the firmware start."""
        return self.command + ["repl"]

    def _mpremote(self, arguments, timeout_s, ran_code=False):
        """What mpremote printed. A board's traceback with nothing from mpremote itself is BoardCodeError."""
        try:
            done = self.run(self.command + arguments, capture_output=True, text=True, timeout=timeout_s, check=True)
        except subprocess.CalledProcessError as failed:
            out, err = printed_text(failed.stdout), printed_text(failed.stderr)
            if ran_code and not err.strip() and BOARD_TRACEBACK in out:
                raise BoardCodeError(out, failed.returncode) from None
            raise BoardUnreachableError(_last_line(err) or _last_line(out) or "exit %d" % failed.returncode,
                                   out + err) from None
        except subprocess.TimeoutExpired:
            if ran_code:
                raise
            raise BoardUnreachableError("no answer in %d s" % timeout_s) from None
        except OSError as cannot:
            raise BoardUnreachableError(str(cannot)) from None
        return printed_text(done.stdout)


class QuietBoardConnection(BoardConnection):
    """
    Adapter: a BoardConnection for a board on Espressif's USB-Serial/JTAG (P1007). Each call runs mpremote in its own
    Python `python` through QUIET_MPREMOTE, so mpremote's words and exit codes stay as they are. Each call restarts the
    board, waits SETTLE_S, and may wait PORT_BACK_S more, so its time limit holds both. When the raw REPL fails after
    the settle, mpremote's output also holds what the settle heard (P1022). `repl_command` stays mpremote's.
    """

    #: The seconds a call may spend before the board can answer: the settle, and a vanished port's wait and settle.
    EXTRA_S = 2 * SETTLE_S + PORT_BACK_S + 1

    def __init__(self, mpremote, python, port, run=subprocess.run, timeout_s=DEFAULT_TIMEOUT_S):
        super().__init__(mpremote, port, run, timeout_s + self.EXTRA_S)
        self.repl = self.command + ["repl"]
        self.command = (list(python) + ["-c", QUIET_MPREMOTE, str(SETTLE_S), str(PORT_BACK_S)]
                        + (["connect", port] if port else []))

    def run_code(self, code, keep_running_for=None):
        """BoardConnection.run_code, with EXTRA_S added to `keep_running_for`."""
        return super().run_code(code, keep_running_for and keep_running_for + self.EXTRA_S)

    def repl_command(self):
        """mpremote's own REPL command, unchanged: the person's console."""
        return self.repl


class RetryingBoardConnection:
    """
    Decorator: a BoardConnection that, when mpremote could not enter the raw REPL, lets `probe` cure the board once and
    runs the code again (P251). `probe` is a board_console.ConsoleProbe, or None for no cure. `last_cure` is the Cure of
    the last run_code, or None when it needed none. The other methods pass through.
    """

    def __init__(self, connection, probe):
        self.connection, self.probe, self.last_cure = connection, probe, None

    def run_code(self, code, keep_running_for=None):
        """What the board printed while it ran `code`, as BoardConnection.run_code, after one cure when it needed one."""
        self.last_cure = None
        try:
            return self.connection.run_code(code, keep_running_for)
        except BoardUnreachableError as refused:
            if self.probe is None or RAW_REPL_REFUSED not in str(refused):
                raise
        self.last_cure = self.probe.cure()
        return self.connection.run_code(code, keep_running_for)

    def copy_to_board(self, local, remote):
        """BoardConnection.copy_to_board, with no cure."""
        return self.connection.copy_to_board(local, remote)

    def read_file(self, remote):
        """BoardConnection.read_file, with no cure."""
        return self.connection.read_file(remote)

    def reset(self):
        """BoardConnection.reset, with no cure."""
        return self.connection.reset()

    def repl_command(self):
        """BoardConnection.repl_command."""
        return self.connection.repl_command()
