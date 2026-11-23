"""
The goal and the must lines a project's needs were written from (P1027). A record beside the needs, `.spark/needs-basis.json`,
holds the sha256 of the brief's goal and of its must lines as they were when `parts.py --needs-set` wrote the needs or a
review noted them. The needs phase of `flow.py show` compares it with the brief now: a change makes the needs out of date.
Nothing here edits the needs, the brief or a part record. A project with no record is one written before P1027.
"""

import hashlib
import json
import re
from pathlib import Path

from spark.design.entry_origin import parts_sha256
from spark.records import store
from spark.records.brief import Brief

# --- MVP ---
#: The record beside the needs, from the project's folder, and the keys it holds.
BASIS_FILE = Path(".spark") / "needs-basis.json"
SCHEMA, GOAL_SHA256, MUST_SHA256 = 1, "goal_sha256", "must_sha256"
#: The parts of a stamp, in the order a change names them.
PARTS = (("goal", GOAL_SHA256), ("must", MUST_SHA256))
#: What `held` gives for a record that is no JSON of its shape or cannot be read.
BROKEN = "broken"
#: A hash the record holds: 64 hex digits.
HEX = re.compile(r"[0-9a-f]{64}")
#: The keys of a `--needs-set` item that define a need: a write with one of them, or an empty list (a review), notes the stamp.
DEFINING = ("does", "what", "condition")
#: The line of a `--needs-set` that notes the stamp: "noted" or "would note".
NOTED_LINE = "  %s the goal and the must lines these needs were written from (.spark/needs-basis.json)"


def stamp_of(brief):
    """{goal_sha256, must_sha256} of a Brief: the goal's UTF-8 bytes as they are, the must lines sorted, so their order is no
    change. None for a brief with a problem or with no goal."""
    if brief.problem or brief.goal is None:
        return None
    return {GOAL_SHA256: hashlib.sha256(brief.goal.encode("utf-8")).hexdigest(), MUST_SHA256: parts_sha256(sorted(brief.must))}


def changed(held, now):
    """The parts of two stamps that differ, in order, from ("goal", "must"). Equal stamps give []."""
    return [part for part, key in PARTS if held[key] != now[key]]


def due_stamp(project, items, after):
    """The stamp a `--needs-set` of `items`, which leaves the needs `after`, notes: the brief's now, when the needs are not
    empty, the write is a review (`[]`) or defines a need, and the record differs. Else None. A brief that cannot be read
    gives none, so it never fails the write."""
    if not after or not (items == [] or any(key in item for item in items for key in DEFINING)):
        return None
    try:
        now = stamp_of(Brief.from_project(project))
    except (OSError, RecursionError):
        return None
    return now if now and NeedsBasisStore(project).held() != now else None


class NeedsBasisStore:
    """Store: the record `.spark/needs-basis.json` of one project: `held` reads it and `save` writes it, through the store's
    one atomic write. The writer writes it after needs.json, so a failed write leaves the needs out of date (the safe side)."""

    def __init__(self, project):
        self.path = Path(project) / BASIS_FILE

    def held(self):
        """The record as {goal_sha256, must_sha256}; None when there is none; BROKEN for one that is no JSON of its shape
        (a missing key, a value that is not 64 hex digits, another schema) or cannot be read."""
        if not self.path.exists():
            return None
        try:
            record = json.loads(self.path.read_text(encoding="utf-8"))
            given = {key: record[key] for _part, key in PARTS}
            fits = record["schema"] == SCHEMA and all(isinstance(value, str) and HEX.fullmatch(value) for value in given.values())
        except (OSError, ValueError, KeyError, TypeError):
            return BROKEN
        return given if fits else BROKEN

    def save(self, stamp):
        """Write the record of `stamp`. OSError when it cannot."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        store.write_file(self.path, json.dumps(dict(stamp, schema=SCHEMA), indent=1, sort_keys=True) + "\n")
# --- end MVP ---
