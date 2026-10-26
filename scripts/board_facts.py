"""
What spark put on a board, said in two places (P215 step 3, D22, D23, D44).

A library. On the board: `FactsFile` copies a small facts file, FACTS_FILE, with mpremote after the flash and reads it
back, so the image stays the one that passed. It names spark's version, the project, the board type, the MAC, the
image's sha256, each file's sha256 and what tested the image (`simulation`). In the person's store: `record_deploy` keeps one record per physical board, by
its MAC, with each deploy, its verdict, its simulation and whose yes it was.
"""

import datetime
import hashlib
import json
import tempfile
import time
from pathlib import Path

import store
import zone_time
from text_guards import printable
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


def record_deploy(facts, verdict, who):
    """
    The store's record of this board, by its MAC, with this deploy added: the project, the image's sha256, the date,
    the verdict and `who`, the phrase for whose yes it was (ConsentStrategy.who). Returns the record's path.
    """
    key = store.slug(facts["mac"])
    deploy = {"project": facts["project"], "image_sha256": facts["image_sha256"], "deployed": facts["deployed"],
              "verdict": verdict, "simulation": facts["simulation"], "yes": who}
    with store.locked():
        path = record_path(facts["mac"])
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


# --- MVP ---
#: What the store says of the board on USB (LastDeploy.state): a deploy is recorded, none is, or spark did not check.
RECORDED, NONE_RECORDED, NOT_CHECKED = "recorded", "none-recorded", "not-checked"
WHY_NO_MAC = "the board's MAC was not read"
WHY_UNREADABLE = "spark's record of it cannot be read"
ZONE_NOT_STORED = "(zone not stored)"


class LastDeploy:
    """Value. What spark's store says of the board on USB. `project`, `verdict` and `deployed` are as `record_deploy` stored
    them, with RECORDED. `why` is the reason, with NOT_CHECKED. The rest are None."""

    def __init__(self, state, project=None, verdict=None, deployed=None, why=None):
        self.state, self.project, self.verdict, self.deployed, self.why = state, project, verdict, deployed, why

    def time_said(self):
        """The stored time. With a zone it is said in the machine's zone. With none it is as stored, and says so,
        because a zone is never given to a time that has none. A time that does not parse is as stored."""
        iso = self.deployed[:-1] + "+00:00" if self.deployed.endswith("Z") else self.deployed  # 3.10 reads no Z
        try:
            if datetime.datetime.fromisoformat(iso).tzinfo is None:
                return "%s %s" % (self.deployed, ZONE_NOT_STORED)
            return zone_time.say_in_local_zone(iso)
        except (ValueError, OverflowError):  # a time that does not parse, or one the machine's zone cannot hold
            return self.deployed

    def line(self):
        """The look's line."""
        if self.state == RECORDED:
            said = printable("%s, %s, %s (its store record, not read from the board)" % (self.project, self.verdict, self.time_said()))
        elif self.state == NONE_RECORDED:
            said = "none in its store record (it keeps only its own deploys)"
        else:
            said = "not checked: %s" % self.why
        return "spark's last deploy here: " + said

    def in_question(self):
        """The words the deploy question puts in its erase sentence."""
        if self.state == RECORDED:
            return printable("spark's store record names %s as its last deploy here, %s, %s" % (self.project, self.time_said(), self.verdict))
        if self.state == NONE_RECORDED:
            return "spark's store record names no deploy here"
        return "spark did not read its record of this board: %s" % self.why

    def to_dict(self):
        return {"state": self.state, "why": self.why, "project": self.project, "verdict": self.verdict,
                "deployed": self.deployed}


def record_path(mac):
    """The path of the store's record of the board with this MAC: what record_deploy writes and read_last_deploy reads."""
    return store.place("boards") / (store.slug(mac) + ".json")


def read_last_deploy(mac):
    """The LastDeploy of the board with this `mac`, from the record `record_deploy` writes. It never raises: what it cannot
    read is NOT_CHECKED with the reason, and never a missing deploy."""
    if not mac:
        return LastDeploy(NOT_CHECKED, why=WHY_NO_MAC)
    path = record_path(mac)
    try:
        if not path.exists() and not path.is_symlink():  # a folder or a broken link in its place is no "none"
            return LastDeploy(NONE_RECORDED)
        record = json.loads(path.read_text())
    except (OSError, ValueError, RecursionError):
        return LastDeploy(NOT_CHECKED, why=WHY_UNREADABLE)
    deploys = record.get("deploys") if isinstance(record, dict) else None
    newest = deploys[-1] if isinstance(deploys, list) and deploys else None  # record_deploy appends
    kept = [newest.get(key) for key in ("project", "verdict", "deployed")] if isinstance(newest, dict) else []
    if not kept or not all(isinstance(each, str) and each.strip() for each in kept):
        return LastDeploy(NOT_CHECKED, why=WHY_UNREADABLE)
    return LastDeploy(RECORDED, *kept)
# --- end MVP ---
