"""
After a flash: do the board's files match the expected hashes, and does the firmware print `ready`? (P215, D33)

A library. `ReadyProbe` runs code on the board twice, through its BoardConnection. First it hashes each file that
the evidence names (a passed run's log, or firmware/), on the board itself. Then it imports `main`, as the board does
at boot, and reads its output for READY_WAIT_S seconds. Ready is seen only when both agree. The output counts as
`ready` only when a line has `ready` as its first word (scenario_steps.has_ready_line, P1025). So `ready, cpu 80 MHz`
counts, and `not ready` and `already` do not. When mpremote cannot reach the board, it is unknown, never seen. So is a
passed run's log from before P215, which names no files.
"""

import collections

from spark.bench.board_connection import BoardUnreachableError, BoardCodeError
from spark.firmware.scenario_steps import READY, has_ready_line

#: How long the board's output is read for `ready`, in seconds. The firmware keeps running after it, so mpremote is
#: stopped at the end, and what it printed until then is the board's log.
READY_WAIT_S = 20
#: The first word of each line HASH_FILES prints, and `ReadyProbe` reads the hashes by it.
HASH_LINE = "file"
#: Run on the board: one line per file, `file <sha256 or missing> <path>`. %r is the list of paths.
HASH_FILES = """import hashlib, binascii
for p in %%r:
    try:
        h = hashlib.sha256()
        with open(p, 'rb') as f:
            while True:
                b = f.read(512)
                if not b:
                    break
                h.update(b)
        print('%s', binascii.hexlify(h.digest()).decode(), p)
    except OSError:
        print('%s', 'missing', p)
""" % (HASH_LINE, HASH_LINE)

SEEN, NOT_SEEN, UNKNOWN = "ready seen", "ready not seen", "ready unknown"
#: The verdict of a deploy that a registered project recorded (P920): spark read nothing from the board.
NOT_READ = "ready not read"


class ReadyResult(collections.namedtuple("ReadyResult", "verdict sentence log")):
    """Result: what `ReadyProbe.check` returns. `verdict` is SEEN, NOT_SEEN or UNKNOWN, `sentence` says why, and `log` is
    what the board printed (the board's log). `files_read` is True when the board printed its files' hashes (P1022), as
    every verdict but UNKNOWN says: an UNKNOWN after the hashes gives it. It is an attribute, so a ReadyResult still
    unpacks to three. `_replace` keeps it, and copy and pickle keep it with the instance's other attributes."""

    def __new__(cls, verdict, sentence, log, files_read=None):
        ready = super().__new__(cls, verdict, sentence, log)
        ready.files_read = verdict != UNKNOWN if files_read is None else files_read
        return ready

    def _replace(self, **changes):
        """A ReadyResult with `changes`, and the same `files_read`."""
        return ReadyResult(*super()._replace(**changes), files_read=self.files_read)


class ReadyProbe:
    """Adapter: the two reads on one board, through its BoardConnection (board_connection.py)."""

    def __init__(self, connection):
        self.connection = connection

    def check(self, expected):
        """A ReadyResult for the files `expected` {path: sha256}: SEEN, NOT_SEEN or UNKNOWN."""
        if not expected:
            return ReadyResult(UNKNOWN, "the passed run's log names no files (an older spark): run its scenario again", "")
        try:
            hashes = self.connection.run_code(HASH_FILES % sorted(expected))
        except (BoardUnreachableError, BoardCodeError) as cannot:
            return ReadyResult(UNKNOWN, "mpremote could not read the board's files: %s" % cannot, cannot.output)
        read = dict(line.split(" ", 2)[1:][::-1] for line in hashes.splitlines() if line.startswith(HASH_LINE + " "))
        differ = [path for path in sorted(expected) if read.get(path) != expected[path]]
        stopped = None
        try:
            said = self.connection.run_code("import main", keep_running_for=READY_WAIT_S)
        except BoardCodeError as raised:  # the board answered the hashes, so the firmware stopped
            said, stopped = raised.output, str(raised)
        except BoardUnreachableError as cannot:
            return ReadyResult(UNKNOWN, "mpremote could not start the firmware: %s" % cannot, hashes + cannot.output, True)
        log = hashes + said
        if differ:
            return ReadyResult(NOT_SEEN, "the board's %s %s not the files of the image" % (
                ", ".join(differ), "is" if len(differ) == 1 else "are"), log)
        if stopped is not None:
            return ReadyResult(NOT_SEEN, "the firmware stopped with an error: %s" % stopped, log)
        if not has_ready_line(said):
            return ReadyResult(NOT_SEEN, "the firmware printed no %r in %d s" % (READY, READY_WAIT_S), log)
        return ReadyResult(SEEN, "the firmware printed %r and the board's %d files match the image" % (
            READY, len(expected)), log)
