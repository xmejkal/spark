"""
The one mpremote connection to a board (P215, the bench council's step 1).

A library. `BoardConnection` runs mpremote on one port: code on the board, a file copied to it, a file read back, and
the line that opens its REPL. Its two errors keep mpremote's own words. `BoardUnreachable`: mpremote could not talk to
the board, for example "could not enter raw repl" (docs/observations/2026-10-14-p215-bench.md). `CodeRaisedOnBoard`:
the board answered, and the code raised there. board_facts.py and ready_check.py use it, so a later reconnect strategy
changes one class.
"""

import subprocess

from run_scenario import printed_text

#: How MicroPython starts the report of an exception that the board's code raised. mpremote 1.29.0 prints that report
#: to stdout and exits 1, and its own failures to stderr (mpremote/commands.py:489-492, read 2026-10-14).
BOARD_TRACEBACK = "Traceback"
#: How long one mpremote call may take before the board counts as not answering, in seconds.
DEFAULT_TIMEOUT_S = 20


def _last_line(text):
    """The last line that holds something, or ''."""
    return next((line.strip() for line in reversed(text.splitlines()) if line.strip()), "")


class BoardUnreachable(Exception):
    """mpremote could not talk to the board. The message is mpremote's last line, `output` all it printed."""

    def __init__(self, why, output=""):
        super().__init__(why)
        self.output = output


class CodeRaisedOnBoard(Exception):
    """The board answered, and the code raised there. The message is the board's last line, `output` all it printed."""

    def __init__(self, output, exit_code):
        super().__init__(_last_line(output) or "exit %d" % exit_code)
        self.output = output


class BoardConnection:
    """mpremote on one board's port. `mpremote` is its command (image_check.runnable), `run` runs a command."""

    def __init__(self, mpremote, port, run=subprocess.run, timeout_s=DEFAULT_TIMEOUT_S):
        self.command = list(mpremote) + (["connect", port] if port else [])
        self.run, self.timeout_s = run, timeout_s

    def run_code(self, code, keep_running_for=None):
        """
        What the board printed while it ran `code`. With `keep_running_for` seconds, code that still runs then is left
        running, and what it printed until then is the answer. Without it, no answer in timeout_s is BoardUnreachable.
        """
        try:
            return self._mpremote(["exec", code], keep_running_for or self.timeout_s, ran_code=True)
        except subprocess.TimeoutExpired as going:
            if keep_running_for:
                return printed_text(going.stdout)
            raise BoardUnreachable("no answer in %d s" % self.timeout_s, printed_text(going.stdout)) from None

    def copy_to_board(self, local, remote):
        """Copy the file at `local` to `remote` on the board's filesystem."""
        self._mpremote(["fs", "cp", str(local), ":" + remote], self.timeout_s)

    def read_file(self, remote):
        """The text of `remote` on the board's filesystem."""
        return self._mpremote(["fs", "cat", ":" + remote], self.timeout_s)

    def repl_command(self):
        """The command that opens the board's REPL, where a person sees the firmware start."""
        return self.command + ["repl"]

    def _mpremote(self, arguments, timeout_s, ran_code=False):
        """What mpremote printed. A board's traceback with nothing from mpremote itself is CodeRaisedOnBoard."""
        try:
            done = self.run(self.command + arguments, capture_output=True, text=True, timeout=timeout_s, check=True)
        except subprocess.CalledProcessError as failed:
            out, err = printed_text(failed.stdout), printed_text(failed.stderr)
            if ran_code and not err.strip() and BOARD_TRACEBACK in out:
                raise CodeRaisedOnBoard(out, failed.returncode) from None
            raise BoardUnreachable(_last_line(err) or _last_line(out) or "exit %d" % failed.returncode,
                                   out + err) from None
        except subprocess.TimeoutExpired:
            if ran_code:
                raise
            raise BoardUnreachable("no answer in %d s" % timeout_s) from None
        except OSError as cannot:
            raise BoardUnreachable(str(cannot)) from None
        return printed_text(done.stdout)
