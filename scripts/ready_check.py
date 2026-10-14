"""
After a flash: do the board's files match the passed run's hashes, and does the firmware print `ready`? (P215, D33)

A library. `ReadyCheck` runs code on the board twice, through its BoardConnection. First it hashes each file that
the passed run's log names (run_scenario.file_hashes), on the board itself. Then it imports `main`, as the board does
at boot, and reads its output for READY_WAIT seconds. Ready is seen only when both agree. When mpremote cannot reach
the board, it is unknown, never seen. So is a passed run's log from before P215, which names no files.
"""

from board_connection import BoardUnreachable, CodeRaisedOnBoard
from run_scenario import READY

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


class ReadyCheck:
    """The two reads on one board, through its BoardConnection (board_connection.py)."""

    def __init__(self, connection):
        self.connection = connection

    def check(self, expected):
        """(verdict, sentence, the board's log) for the files `expected` {path: sha256}: SEEN, NOT_SEEN or UNKNOWN."""
        if not expected:
            return UNKNOWN, "the passed run's log names no files (an older spark): run its scenario again", ""
        try:
            hashes = self.connection.run_code(HASH_FILES % sorted(expected))
        except (BoardUnreachable, CodeRaisedOnBoard) as cannot:
            return UNKNOWN, "mpremote could not read the board's files: %s" % cannot, cannot.output
        read = dict(line.split(" ", 2)[1:][::-1] for line in hashes.splitlines() if line.startswith("file "))
        differ = [path for path in sorted(expected) if read.get(path) != expected[path]]
        stopped = None
        try:
            said = self.connection.run_code("import main", keep_running_for=READY_WAIT)
        except CodeRaisedOnBoard as raised:  # the board answered the hashes, so the firmware stopped
            said, stopped = raised.output, str(raised)
        except BoardUnreachable as cannot:
            return UNKNOWN, "mpremote could not start the firmware: %s" % cannot, hashes + cannot.output
        log = hashes + said
        if differ:
            return NOT_SEEN, "the board's %s %s not the files that passed" % (
                ", ".join(differ), "is" if len(differ) == 1 else "are"), log
        if stopped is not None:
            return NOT_SEEN, "the firmware stopped with an error: %s" % stopped, log
        if READY not in said:
            return NOT_SEEN, "the firmware printed no %r in %d s" % (READY, READY_WAIT), log
        return SEEN, "the firmware printed %r and the board's %d files match the run that passed" % (
            READY, len(expected)), log
