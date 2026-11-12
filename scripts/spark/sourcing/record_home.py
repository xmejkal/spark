"""
A part record's own home (P726 PR 3; the functions were `part_handlers`' since W6-S3b): where a record's file is and which
project's shelf copy follows it (`record_path`, `shelved_from`, §5.4 and §5.5), the copy made current again
(`refresh_shelf_copy`), a record with values set by name (`merge_values`), and the write of fields into that home
(`set_fields`), never into spark's library. A `RecordHome` Value enters when a third caller needs (path, source) as one.
"""

import json
from pathlib import Path

from spark.records import board_records, missing_facts, record_kind, store
from spark.records.record_kind import Answer, _parse, _problem, _write_record
from spark.sourcing import drawer, sourcing_codes
from spark.sourcing.part_facts import _shelf_copy, shelve
from spark.sourcing.part_records import PartError, validate


# --- MVP ---
def shelved_from(path):
    """The project a shelf copy says it was shelved from (its `based_on`, §5.5) — None for a catalog's copy, or no copy."""
    record = _parse(path) if Path(path).is_file() else None
    based_on = record.get("based_on") if isinstance(record, dict) else None
    named = based_on.get("project") if isinstance(based_on, dict) else None
    return named if isinstance(named, str) else None


def record_path(part_id, project, kind="part"):
    """
    A part record's own file, and the project whose shelf copy follows it (§5.4, §5.5): the nearest layer that has it, the
    catalog included, else a project on the person's list — except that a shelf copy of a listed project's record is not a
    home: that project's record is. A record found in the project given names that project too, when the shelf holds a copy
    of it shelved from there: the copy follows its record, however the record was reached. `kind` is "board" for a board's record (P464).
    """
    path, where = next(((path, where) for found_kind, found, where, path in drawer.linkable(project) if (found_kind, found) == (kind, part_id)),
                       (None, None))
    if path is not None and path.parent == store.place("shelf"):
        named = shelved_from(path)
        folder = store.projects().get(named) if named else None
        home = folder / "parts" / path.name if folder is not None else None
        return (home, named) if home is not None and home.is_file() else (path, None)
    named = store.find_listed_name(project) if where == "project" else None
    return path, named if named and shelved_from(store.place("shelf") / path.name) == named else None


def refresh_shelf_copy(path, record, project_name, dry_run):
    """
    The shelf copy of a project's record made current again (§5.5) — after a write, and when an earlier write left it behind
    (the record filled in its project while the copy stayed, so every retry said "nothing to change") — said in words:
    current, refreshed, would refresh, or not refreshed and why: a copy that would not meet the contract is not written.
    """
    copy = _shelf_copy(path, project_name, record)
    if _parse(store.place("shelf") / path.name) == copy:
        return "current"
    wrong = validate(copy, path)
    if wrong:
        return "shelf copy not refreshed: %s" % "; ".join(wrong)
    if dry_run:
        return "would refresh the shelf copy"
    shelve(path, project_name)
    return "shelf copy refreshed"


def merge_values(record, values):
    """`record` with `values` set, and the values it had: `facts` takes the written names over the held ones, the other names stay
    (P374); `legs` the same, leg by leg (P741)."""
    after, was = dict(record, **values), {key: record.get(key) for key in values}
    if isinstance(values.get("legs"), dict):
        held = record.get("legs") if isinstance(record.get("legs"), dict) else {}
        after["legs"], was["legs"] = dict(held, **values["legs"]), {pin: held.get(pin) for pin in values["legs"]}
    if isinstance(values.get("pin_roles"), dict):  # P464: role by role, so a role keeps its gpio and note
        after["pin_roles"], was["pin_roles"] = missing_facts.merged_roles(record, values)
    if isinstance(values.get("facts"), dict):
        held = record.get("facts") if isinstance(record.get("facts"), dict) else {}
        after["facts"], was["facts"] = dict(held, **values["facts"]), {name: held.get(name) for name in values["facts"]}
    return after, was


def set_fields(part_id, project, values, dry_run, refuse):
    """
    Set fields of a part record in its own home (§5.4) — the catalog's, a project's, or a listed project's behind a shelf
    copy — never spark's library, which is changed in spark's repository. A shelf copy that follows the record is made
    current whether or not this write changed anything (`refresh_shelf_copy`), and the answer says what became of it.
    `refuse(record, after, path)` says what is wrong with the result, and anything it says refuses the write.
    """
    path, source = record_path(part_id, project, "board" if "pin_roles" in values else "part")  # P464: only a level in pin_roles reaches a board
    if path is None:
        raise PartError("no record called %r — `parts.py --need` finds what exists", part_id,
                        code=sourcing_codes.NO_SUCH_PART)
    if path.parent.resolve() in (record_kind.LIBRARY.resolve(), board_records.LIBRARY.resolve()):
        return Answer(problems=[_problem(part_id, "%s is in spark's own library, which is changed in spark's repository, "
                                                  "not by parts.py" % part_id)])
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        return Answer(problems=[_problem(part_id, "%s is not a JSON object (%s) — repair the file by hand first" % (part_id, path))])
    after, was = merge_values(record, values)
    wrong = refuse(record, after, path)
    if wrong:
        return Answer(problems=[_problem(part_id, sentence) for sentence in wrong])
    changes = after != record
    if changes and not dry_run:
        _write_record(path, after)
    shelf_copy = refresh_shelf_copy(path, after, source, dry_run) if source else None
    said = ("  %s %s (%s): %s" % ("would set" if dry_run else "set", part_id, path, "; ".join(
                "%s %s → %s" % (key, json.dumps(was[key], ensure_ascii=False), json.dumps(value, ensure_ascii=False))
                for key, value in values.items()))
            if changes else "  nothing to change: %s (%s) already says this" % (part_id, path))
    return Answer({"part": part_id, "path": str(path), "was": was, "now": values, "written": not dry_run, "shelf_copy": shelf_copy},
                  [said] + (["  " + shelf_copy] if shelf_copy not in (None, "current") else []))
# --- end MVP ---
