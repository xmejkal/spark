"""
What spark's store keeps of each physical board, by its MAC (P215 step 3, D22, D23, D44; P431, OC5).

A library, for `deploy_service.DeployService` (it writes the record after a deploy) and `board_look` (it reads the last
deploy). `DeployRecordStore` keeps one record per board, with each deploy, its verdict, its simulation, whose yes it
was and the MicroPython banner of its image (P779). `LastDeploy` is what the store says of the board on USB. It holds the
reasons (`WHY_NO_MAC`, `WHY_UNREADABLE`) and the zone note of a time, and no line or question words:
`board_look.say_last_deploy` is the look's line and `deploy_gate.say_last_deploy_in_question` is the deploy question's.
What is on the board itself, the facts file, is `board_facts`.
"""

import collections
import datetime
import json

from spark.core import outcomes
from spark.records import records_codes
from spark.records import store
from spark.core import zone_time


# --- MVP ---
WHY_NO_MAC = "the board's MAC was not read"
WHY_UNREADABLE = "spark's record of it cannot be read"
ZONE_NOT_STORED = "(zone not stored)"


class LastDeploy(collections.namedtuple("LastDeploy", "state project verdict deployed why record_path micropython_banner",
                                         defaults=(None,) * 6)):
    """Value. What spark's store says of the board on USB. `state` is one of the three words of `outcomes` (the reader rule is
    there). `project`, `verdict` and `deployed` are as `write_deploy` stored them, with outcomes.RECORDED. `why` is the reason,
    with outcomes.NOT_CHECKED. The rest are None. `record_path` is the path of the record the store read (None when no MAC
    named one); it is not in `to_dict` (P458). `micropython_banner` is the MicroPython banner of the image that deploy put
    there, as the store kept it, or None: a deploy before P779 kept none, and an image may hold none."""

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

    def to_dict(self):
        return {"state": self.state, "why": self.why, "project": self.project, "verdict": self.verdict,
                "deployed": self.deployed, "micropython_banner": self.micropython_banner}


class DeployRecordStore:
    """
    Store. The person's record of each physical board, one file per MAC in `boards/`, written after a deploy (`write_deploy`)
    and read by the look (`read_last_deploy`). It keeps nothing in memory; `LookAtBoard(records=)` and `DeployImage(records=)`
    take it as a collaborator, and build the store's own when given None (P475, P458).
    """

    @staticmethod
    def _key(mac):
        """The name of the board's record inside the store's `boards` place: the one rule that `find_path` and `write_deploy` share."""
        return store.slug(mac)

    def find_path(self, mac):
        """The path of the store's record of the board with this MAC: what write_deploy writes and read_last_deploy reads."""
        return store.place("boards") / (self._key(mac) + ".json")

    def read_last_deploy(self, mac):
        """The LastDeploy of the board with this `mac`, from the record `write_deploy` writes. It never raises: what it cannot
        read is outcomes.NOT_CHECKED with the reason, and never a missing deploy."""
        if not mac:
            return LastDeploy(outcomes.NOT_CHECKED, why=WHY_NO_MAC)
        path = self.find_path(mac)
        try:
            if not path.exists() and not path.is_symlink():  # a folder or a broken link in its place is no "none"
                return LastDeploy(outcomes.NONE_RECORDED, record_path=path)
            record = json.loads(path.read_text())
        except (OSError, ValueError, RecursionError):
            return LastDeploy(outcomes.NOT_CHECKED, why=WHY_UNREADABLE, record_path=path)
        deploys = record.get("deploys") if isinstance(record, dict) else None
        newest = deploys[-1] if isinstance(deploys, list) and deploys else None  # write_deploy appends
        kept = [newest.get(key) for key in ("project", "verdict", "deployed")] if isinstance(newest, dict) else []
        if not kept or not all(isinstance(each, str) and each.strip() for each in kept):
            return LastDeploy(outcomes.NOT_CHECKED, why=WHY_UNREADABLE, record_path=path)
        banner = newest.get("micropython_banner")  # P779: a deploy before it kept none, and that is no unreadable record
        return LastDeploy(outcomes.RECORDED, *kept, record_path=path,
                          micropython_banner=banner if isinstance(banner, str) and banner.strip() else None)

    def write_deploy(self, facts, verdict, who):
        """
        The store's record of this board, by its MAC, with this deploy added: the project, the image's sha256, the date,
        the verdict, `who`, the phrase for whose yes it was (ConsentStrategy.who), and the image's MicroPython banner, read
        from the image file at the deploy (null when the facts hold none, P779). Returns the record's path.
        """
        deploy = {"project": facts["project"], "image_sha256": facts["image_sha256"], "deployed": facts["deployed"],
                  "verdict": verdict, "simulation": facts["simulation"], "yes": who,
                  "micropython_banner": facts.get("micropython_banner")}
        with store.locked():
            path = self.find_path(facts["mac"])
            try:
                record = json.loads(path.read_text()) if path.is_file() else {"mac": facts["mac"], "deploys": []}
            except ValueError:
                record = None
            if not isinstance(record, dict) or not isinstance(record.get("deploys"), list):
                raise store.StoreError("%s is not a board record, so it was left as it is", path, code=records_codes.NOT_A_BOARD_RECORD)
            record["board"] = facts["board"]
            record["deploys"].append(deploy)
            store.write_json("boards", self._key(facts["mac"]), record)
        return path
# --- end MVP ---
