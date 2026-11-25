"""
What spark put on a board (P215 step 3, D22, D23, D44).

A library. `ReadingFile` copies a small facts file, FACTS_FILE, with mpremote after the flash and reads it back, so the image
stays the one that passed. It names spark's version, the project, the board type, the MAC, the image's sha256, the MicroPython
banner the image holds (P779), each file's sha256 and what tested the image (`simulation`). The person's store keeps its own
record of each board: `deploy_record_store.py`.
"""

import hashlib
import json
import tempfile
import time
from pathlib import Path

from spark.bench.board_connection import RAW_REPL_REFUSED, BoardUnreachableError, BoardCodeError
from spark.firmware import image_builder

#: The facts file's path on the board. No passed run names it, so the board's log names its sha256 (D45).
FACTS_FILE = "spark.json"
PLUGIN_JSON = Path(__file__).resolve().parents[3] / ".claude-plugin" / "plugin.json"


def facts(project, board, mac, image, files, moment, simulation):
    """The facts file's content: what spark put on this board, from records it holds, at `moment` (a datetime). `simulation` is
    "passed" or "none": what tested the image (ImageEvidence.simulation). The image's sha256 and its MicroPython banner
    (image_builder.banner_in, None when it holds none, P779) are read from one read of the image file."""
    data = Path(image).read_bytes()
    return dict(facts_without_image(project, board, mac, moment, simulation), image_sha256=hashlib.sha256(data).hexdigest(),
                micropython_banner=image_builder.banner_in(data), files=files)


def facts_without_image(project, board, mac, moment, simulation):
    """The facts of `facts` that need no read of the image file, with no image sha256, no banner and no files (P1112)."""
    return {"spark": json.loads(PLUGIN_JSON.read_text())["version"], "project": Path(project).resolve().name,
            "board": board, "mac": mac, "image_sha256": None, "micropython_banner": None, "files": (),
            "simulation": simulation, "deployed": moment.isoformat(timespec="seconds")}


def facts_text(said):
    """The facts as the file holds them: sorted keys, so the same facts are the same bytes."""
    return json.dumps(said, indent=1, sort_keys=True) + "\n"


#: How long the facts copy waits before its one retry, when the board refused the raw REPL right after the deploy's
#: reset (P420, seen on the T-Display and in walk 1). A guess, to be measured on the bench.
FACTS_RETRY_WAIT_S = 2


#: What the board log keeps of each failed facts copy (P1022): which try, then all that mpremote printed, or "nothing".
FACTS_HEARD = "the facts copy, %s: mpremote printed:\n%s"


def ended(output):
    """`output` with one newline at its end, or "nothing" and a newline when it is empty (as download_mode.first_read ends a log)."""
    return output.rstrip("\n") + "\n" if output.strip() else "nothing\n"


class FactsLine(str):
    """
    Value: the board log's line about the facts file (P1022). It is a str, as board_codes' Code is, so the line that is
    said, `data.facts_line` and the board log stay as they were. `written` is True when the file is on the board and reads
    back the same. `heard` is what mpremote printed on each failed try (FACTS_HEARD), or "" for none.
    """

    def __new__(cls, text, written, heard=""):
        line = super().__new__(cls, text)
        line.written, line.heard = written, heard
        return line

    def __getnewargs__(self):
        """The arguments copy, deepcopy and pickle make the FactsLine again with."""
        return str(self), self.written, self.heard


class ReadingFile:
    """Adapter: the facts file on one board, through its BoardConnection (board_connection.py). `sleep` waits
    before the retry. After `write`, `heard` holds what mpremote printed on each failed try (P1022)."""

    def __init__(self, connection, sleep=time.sleep):
        self.connection, self.sleep, self.first_failure, self.heard = connection, sleep, None, ""

    def write(self, said):
        """None when the facts file is on the board and reads back the same, else why not. When the board refused the raw
        REPL, the copy and its read-back run once more after FACTS_RETRY_WAIT_S, and `first_failure` keeps why (P420). No
        other failure is retried: a full flash or a board that does not answer would fail again."""
        self.first_failure, self.heard = None, ""
        text = facts_text(said)
        with tempfile.TemporaryDirectory() as scratch:
            local = Path(scratch) / FACTS_FILE
            local.write_text(text)
            for retry in (False, True):
                try:
                    self.connection.copy_to_board(local, FACTS_FILE)
                    back = self.connection.read_file(FACTS_FILE)
                    break
                except (BoardUnreachableError, BoardCodeError) as cannot:
                    self.heard += FACTS_HEARD % ("the retry" if retry else "the first try", ended(cannot.output))
                    why = "mpremote could not copy it: %s" % cannot
                    if retry:
                        return "%s (the first try: %s)" % (why, self.first_failure)
                    if RAW_REPL_REFUSED not in str(cannot):
                        return why
                    self.first_failure = why
                    self.sleep(FACTS_RETRY_WAIT_S)
        if back.strip() == text.strip():
            return None
        why = "it read back different from what was copied"
        return "%s (the first try: %s)" % (why, self.first_failure) if self.first_failure else why
