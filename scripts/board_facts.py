"""
What spark put on a board, said in two places (P215 step 3, D22, D23, D44).

A library. On the board: `FactsFile` copies a small facts file, FACTS_FILE, with mpremote after the flash and reads it
back, so the image stays the one that passed. It names spark's version, the project, the board type, the MAC, the
image's sha256 and each file's sha256. In the person's store: `record_deploy` keeps one record per physical board, by
its MAC, with each deploy, its verdict and whose yes it was.
"""

import hashlib
import json
import tempfile
from pathlib import Path

import store
from board_connection import BoardUnreachableError, BoardCodeError

#: The facts file's path on the board. No passed run names it, so the board's log names its sha256 (D45).
FACTS_FILE = "spark.json"
PLUGIN_JSON = Path(__file__).resolve().parent.parent / ".claude-plugin" / "plugin.json"


def facts(project, board, mac, image, files, moment):
    """The facts file's content: what spark put on this board, from records it holds, at `moment` (a datetime)."""
    return {"spark": json.loads(PLUGIN_JSON.read_text())["version"], "project": Path(project).resolve().name,
            "board": board, "mac": mac, "image_sha256": hashlib.sha256(Path(image).read_bytes()).hexdigest(),
            "files": files, "deployed": moment.isoformat(timespec="seconds")}


def facts_text(said):
    """The facts as the file holds them: sorted keys, so the same facts are the same bytes."""
    return json.dumps(said, indent=1, sort_keys=True) + "\n"


class FactsFile:
    """The facts file on one board, through its BoardConnection (board_connection.py)."""

    def __init__(self, connection):
        self.connection = connection

    def write(self, said):
        """None when the facts file is on the board and reads back the same, else why not."""
        text = facts_text(said)
        with tempfile.TemporaryDirectory() as scratch:
            local = Path(scratch) / FACTS_FILE
            local.write_text(text)
            try:
                self.connection.copy_to_board(local, FACTS_FILE)
                back = self.connection.read_file(FACTS_FILE)
            except (BoardUnreachableError, BoardCodeError) as cannot:
                return "mpremote could not copy it: %s" % cannot
        return None if back.strip() == text.strip() else "it read back different from what was copied"


def record_deploy(facts, verdict, who):
    """
    The store's record of this board, by its MAC, with this deploy added: the project, the image's sha256, the date,
    the verdict and `who`, the phrase for whose yes it was (ConsentStrategy.who). Returns the record's path.
    """
    key = store.slug(facts["mac"])
    deploy = {"project": facts["project"], "image_sha256": facts["image_sha256"], "deployed": facts["deployed"],
              "verdict": verdict, "yes": who}
    with store.locked():
        path = store.place("boards") / (key + ".json")
        try:
            record = json.loads(path.read_text()) if path.is_file() else {"mac": facts["mac"], "deploys": []}
        except ValueError:
            record = None
        if not isinstance(record, dict) or not isinstance(record.get("deploys"), list):
            raise store.StoreProblem("%s is not a board record, so it was left as it is" % path)
        record["board"] = facts["board"]
        record["deploys"].append(deploy)
        store.write_json("boards", key, record)
    return path
