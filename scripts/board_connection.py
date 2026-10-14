"""
The one mpremote connection to a board (P215, the bench council's step 1).

A library. `BoardConnection` runs mpremote on one port: code on the board, a file copied to it, a file read back.
Its two errors keep mpremote's own words. `BoardUnreachable`: mpremote could not talk to the board, for example
"could not enter raw repl" (docs/observations/2026-10-14-p215-bench.md). `FirmwareStopped`: the board answered, and
the code raised there. board_facts.py and ready_check.py use it, so a later reconnect strategy changes one class.
"""

import subprocess

#: How mpremote names its own failure to talk to the board (mpremote 1.29.0, transport.py's TransportError).
TRANSPORT = "TransportError"
#: How MicroPython starts the report of an exception that the board's code raised.
RAISED = "Traceback"


def _text(output):
    """What a process printed, as text: subprocess hands it back as bytes, as text or as nothing."""
    return output.decode("utf-8", "replace") if isinstance(output, bytes) else (output or "")


class BoardUnreachable(Exception):
    """mpremote could not talk to the board. The message is mpremote's last line, `output` all it printed."""

    def __init__(self, why, output=""):
        super().__init__(why)
        self.output = output


class FirmwareStopped(Exception):
    """The board answered, and the code raised there. `output` is what the board printed, its traceback included."""

    def __init__(self, output, code):
        super().__init__("the code stopped with an error (mpremote exit %d)" % code)
        self.output, self.code = output, code


class BoardConnection:
    """mpremote on one board's port. `shell` is mpremote's command (image_check.runnable), `run` runs a command."""

    def __init__(self, shell, port, run=subprocess.run, wait=20):
        self.base = list(shell) + (["connect", port] if port else [])
        self.run, self.wait = run, wait

    def run_code(self, code, keep_running=False):
        """
        What the board printed while it ran `code`. With `keep_running`, code that still runs after `wait` seconds
        is left running, and what it printed until then is the answer. Without it, no answer in time is
        BoardUnreachable.
        """
        try:
            return self._mpremote("exec", code)
        except subprocess.TimeoutExpired as going:
            if keep_running:
                return _text(going.stdout)
            raise BoardUnreachable("no answer in %d s" % self.wait, _text(going.stdout)) from None

    def copy_to_board(self, local, remote):
        """Copy the file at `local` to `remote` on the board's filesystem."""
        self._mpremote("fs", "cp", str(local), ":" + remote)

    def read_file(self, remote):
        """The text of `remote` on the board's filesystem."""
        return self._mpremote("fs", "cat", ":" + remote)

    def _mpremote(self, *command):
        try:
            done = self.run(self.base + list(command), capture_output=True, text=True, timeout=self.wait, check=True)
        except subprocess.CalledProcessError as failed:
            said = _text(failed.stdout) + _text(failed.stderr)
            if RAISED in said and TRANSPORT not in said:
                raise FirmwareStopped(said, failed.returncode) from None
            last = (_text(failed.stderr).strip().splitlines() or ["exit %d" % failed.returncode])[-1]
            raise BoardUnreachable(last, said) from None
        except OSError as cannot:
            raise BoardUnreachable(str(cannot)) from None
        return _text(done.stdout)
