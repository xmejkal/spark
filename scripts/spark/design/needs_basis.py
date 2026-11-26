"""
The goal and the must lines a project's needs were written from (P1027). A record beside the needs, `.spark/needs-basis.json`,
holds the sha256 of the brief's goal and of its must lines as they were when `parts.py --needs-set` wrote the needs or a
review noted them. The needs phase of `flow.py show` compares it with the brief now: a change makes the needs out of date.
Since slice 2 it also notes the ids of the needs (`needs`): a noted need that needs.json no longer holds is a dropped need,
and the idea phase asks about the must lines it served. Only a review clears a drop.
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
#: The key of the noted needs (slice 2): a list of plain ids. A record of slice 1 has none, and that is no BROKEN record.
NEEDS = "needs"
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
    change. None for a brief with a problem, with no goal or with a blank goal."""
    if brief.problem or not brief.has_goal:
        return None
    return {GOAL_SHA256: hashlib.sha256(brief.goal.encode("utf-8")).hexdigest(), MUST_SHA256: parts_sha256(sorted(brief.must))}


def changed(held, now):
    """The parts of two stamps that differ, in order, from ("goal", "must"). Equal stamps give []."""
    return [part for part, key in PARTS if held[key] != now[key]]


def noted_ids(noted, items, after):
    """The ids a `--needs-set` of `items` notes, sorted: those of the needs `after`, and on a write that is no review also
    the `noted` ids (a list, or None) that `after` lacks, so only a review (`[]`) clears a dropped need."""
    kept = noted or [] if items != [] else []
    return sorted({need["id"] for need in after} | set(kept))


def due_stamp(project, items, after):
    """The stamp a `--needs-set` of `items`, which leaves the needs `after`, notes: the brief's now and the noted ids, when
    the write is a review (`[]`) or defines a need, and the record differs. With no need after it, only a review over a
    held record notes (`needs: []`, so a drop of the last need clears). Else None. A brief that cannot be read gives none,
    so it never fails the write."""
    review = items == []
    if not (review or any(key in item for item in items for key in DEFINING)):
        return None
    basis = NeedsBasisStore(project)
    held, noted = basis.held(), basis.noted()
    if not after and not (review and isinstance(held, dict)):
        return None
    try:
        now = stamp_of(Brief.from_project(project))
    except (OSError, RecursionError):
        return None
    ids = noted_ids(noted, items, after)
    return dict(now, **{NEEDS: ids}) if now and (held != now or noted != ids) else None


def dropped(project, ids_now):
    """The noted ids that `ids_now` lacks, sorted: the needs dropped after the must lines were last gone through. No
    record, a BROKEN one or one with no noted needs (slice 1's) gives []."""
    return sorted(set(NeedsBasisStore(project).noted() or []) - set(ids_now))


def is_ids(value):
    """True for a list of plain ids, the shape of the noted needs."""
    return isinstance(value, list) and all(isinstance(each, str) and store.PLAIN.fullmatch(each) for each in value)


class NeedsBasisStore:
    """Store: the record `.spark/needs-basis.json` of one project: `held` reads it and `save` writes it, through the store's
    one atomic write. The writer writes it after needs.json, so a failed write leaves the needs out of date (the safe side)."""

    def __init__(self, project):
        self.path = Path(project) / BASIS_FILE

    def held(self):
        """The record as {goal_sha256, must_sha256}; None when there is none; BROKEN for one that is no JSON of its shape
        (a missing key, a value that is not 64 hex digits, another schema, noted needs that are no list of ids) or cannot
        be read."""
        record = self._record()
        return {key: record[key] for _part, key in PARTS} if isinstance(record, dict) else record

    def noted(self):
        """The noted ids of the record; None when there is no record, it is BROKEN or it notes none (slice 1's)."""
        record = self._record()
        return record.get(NEEDS) if isinstance(record, dict) else None

    def _record(self):
        """The whole record when it fits its shape, else None (no file) or BROKEN."""
        if not self.path.exists():
            return None
        try:
            record = json.loads(self.path.read_text(encoding="utf-8"))
            given = {key: record[key] for _part, key in PARTS}
            fits = record["schema"] == SCHEMA and all(isinstance(value, str) and HEX.fullmatch(value) for value in given.values())
            fits = fits and (NEEDS not in record or is_ids(record[NEEDS]))
        except (OSError, ValueError, KeyError, TypeError):
            return BROKEN
        return record if fits else BROKEN

    def save(self, stamp):
        """Write the record of `stamp`. OSError when it cannot."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        store.write_file(self.path, json.dumps(dict(stamp, schema=SCHEMA), indent=1, sort_keys=True) + "\n")
# --- end MVP ---
