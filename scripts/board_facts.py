"""
What spark put on a board (P215 step 3, D22, D23, D44).

A library. `FactsFile` copies a small facts file, FACTS_FILE, with mpremote after the flash and reads it back, so the image
stays the one that passed. It names spark's version, the project, the board type, the MAC, the image's sha256, each file's
sha256 and what tested the image (`simulation`). The person's store keeps its own record of each board:
`deploy_record_store.py`.
"""

import hashlib
import json
import tempfile
import time
from pathlib import Path

from board_connection import RAW_REPL_REFUSED, BoardUnreachableError, BoardCodeError

#: The facts file's path on the board. No passed run names it, so the board's log names its sha256 (D45).
FACTS_FILE = "spark.json"
PLUGIN_JSON = Path(__file__).resolve().parent.parent / ".claude-plugin" / "plugin.json"


def facts(project, board, mac, image, files, moment, simulation):
    """The facts file's content: what spark put on this board, from records it holds, at `moment` (a datetime). `simulation` is
    "passed" or "none": what tested the image (ImageEvidence.simulation)."""
    return {"spark": json.loads(PLUGIN_JSON.read_text())["version"], "project": Path(project).resolve().name,
            "board": board, "mac": mac, "image_sha256": hashlib.sha256(Path(image).read_bytes()).hexdigest(),
            "files": files, "simulation": simulation, "deployed": moment.isoformat(timespec="seconds")}


def facts_text(said):
    """The facts as the file holds them: sorted keys, so the same facts are the same bytes."""
    return json.dumps(said, indent=1, sort_keys=True) + "\n"


#: How long the facts copy waits before its one retry, when the board refused the raw REPL right after the deploy's
#: reset (P420, seen on the T-Display and in walk 1). A guess, to be measured on the bench.
FACTS_RETRY_WAIT_S = 2


class FactsFile:
    """The facts file on one board, through its BoardConnection (board_connection.py). `sleep` waits before the retry."""

    def __init__(self, connection, sleep=time.sleep):
        self.connection, self.sleep, self.first_failure = connection, sleep, None

    def write(self, said):
        """None when the facts file is on the board and reads back the same, else why not. When the board refused the raw
        REPL, the copy and its read-back run once more after FACTS_RETRY_WAIT_S, and `first_failure` keeps why (P420). No
        other failure is retried: a full flash or a board that does not answer would fail again."""
        self.first_failure = None
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
