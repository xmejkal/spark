"""
After a flash: do the board's files match the passed run's hashes, and does the firmware print `ready`? (P215, D33)

A library. `BoardReady` runs mpremote twice on the board's port. First it hashes each file that the passed run's log
names (run_scenario.file_hashes), on the board itself. Then it imports `main`, as the board does at boot, and reads its
output for READY_WAIT seconds. Ready is seen only when both agree. When mpremote cannot reach the board, it is unknown,
never seen. So is a passed run's log from before P215, which names no files.
"""

import subprocess

from run_scenario import READY, _text

#: How long the board's output is read for `ready`, in seconds. The firmware keeps running after it, so mpremote is
#: stopped at the end, and what it printed until then is the board's log.
READY_WAIT = 20
#: Run on the board: one line per file, `file <sha256 or missing> <path>`. %r is the list of paths.
HASH_FILES = """import hashlib, binascii
for p in %r:
    try:
        h = hashlib.sha256()
        with open(p, 'rb') as f:
            while True:
                b = f.read(512)
                if not b:
                    break
                h.update(b)
        print('file', binascii.hexlify(h.digest()).decode(), p)
    except OSError:
        print('file', 'missing', p)
"""

SEEN, NOT_SEEN, UNKNOWN = "ready seen", "ready not seen", "ready unknown"


class BoardReady:
    """The two reads on one board. `shell` is mpremote's command (image_check.runnable), `run` runs a command."""

    def __init__(self, shell, port, run=subprocess.run, wait=READY_WAIT):
        self.base = list(shell) + (["connect", port] if port else [])
        self.run, self.wait = run, wait

    def check(self, expected):
        """(verdict, sentence, the board's log) for the files `expected` {path: sha256}: SEEN, NOT_SEEN or UNKNOWN."""
        if not expected:
            return UNKNOWN, "the passed run's log names no files (an older spark): run its scenario again", ""
        try:
            hashes = self._exec(HASH_FILES % sorted(expected), timeout=self.wait)
        except (OSError, subprocess.SubprocessError) as cannot:
            return UNKNOWN, "mpremote could not read the board's files (%s)" % cannot, ""
        read = dict(line.split(" ", 2)[1:][::-1] for line in hashes.splitlines() if line.startswith("file "))
        differ = [path for path in sorted(expected) if read.get(path) != expected[path]]
        stopped = None
        try:
            said = self._exec("import main", timeout=self.wait)
        except subprocess.TimeoutExpired as running:
            said = _text(running.stdout)
        except subprocess.CalledProcessError as failed:  # the board answered the hashes, so the firmware stopped
            said, stopped = _text(failed.stdout) + _text(failed.stderr), failed.returncode
        except OSError as cannot:
            return UNKNOWN, "mpremote could not start the firmware (%s)" % cannot, hashes
        log = hashes + said
        if differ:
            return NOT_SEEN, "the board's %s %s not the files that passed" % (
                ", ".join(differ), "is" if len(differ) == 1 else "are"), log
        if stopped is not None:
            return NOT_SEEN, "the firmware stopped with an error (mpremote exit %d): see the board log" % stopped, log
        if READY not in said:
            return NOT_SEEN, "the firmware printed no %r in %d s" % (READY, self.wait), log
        return SEEN, "the firmware printed %r and the board's %d files match the run that passed" % (
            READY, len(expected)), log

    def _exec(self, code, timeout=None):
        """What `mpremote exec code` printed. CalledProcessError when mpremote failed, TimeoutExpired past `timeout`."""
        done = self.run(self.base + ["exec", code], capture_output=True, text=True, timeout=timeout, check=True)
        return _text(done.stdout)
