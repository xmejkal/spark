"""
A part record's own home (P726 PR 3; the functions were `part_handlers`' since W6-S3b): where a record's file is and which
project's shelf copy follows it (`record_path`, `shelved_from`, §5.4 and §5.5; never a record only another listed project
holds, P987; an orphan copy is adopted by the one listed project that holds it, `orphan_home`, P1006), the copy made current again
(`refresh_shelf_copy`), a record with values set by name (`merge_values`), and the write of fields into that home
(`set_fields`), never into spark's library. A `RecordHome` Value enters when a third caller needs (path, source) as one.
"""

import json
import shlex
from pathlib import Path

from spark.records import board_records, missing_facts, record_kind, store
from spark.core.text_guards import printable
from spark.records.record_kind import Answer, _parse, _problem, _write_record
from spark.sourcing import drawer, sourcing_codes
from spark.sourcing.part_facts import _shelf_copy, shelf_of, shelve
from spark.sourcing.part_records import PartError


# --- MVP ---
def shelved_from(path):
    """The project a shelf copy says it was shelved from (its `based_on`, §5.5) — None for a catalog's copy, or no copy."""
    record = _parse(path) if Path(path).is_file() else None
    based_on = record.get("based_on") if isinstance(record, dict) else None
    named = based_on.get("project") if isinstance(based_on, dict) else None
    return named if isinstance(named, str) else None


def record_path(part_id, project, kind="part"):
    """
    A part record's own file, and the project whose shelf copy follows it (§5.4, §5.5): the nearest layer that has it
    (`drawer.find_nearest_records`: the project given, the shelf, spark's library, the catalog), or (None, None) when no
    layer and no listed project has it — except that a shelf copy of a listed project's record is not a home: that
    project's record is. A record found in the project given names that project too, when the shelf holds a copy of it
    shelved from there: the copy follows its record, however the record was reached. `kind` is "board" for a board's
    record (P464). Raises PartError `other_project_record` when only another project on the person's list holds it (P987):
    a writer changes only the project the run names, or the project a shelf copy came from. It never writes.
    """
    where, path = drawer.find_nearest_records(kind, project).get(part_id, (None, None))
    if path is None:
        listed = next(((name, found_path) for found_kind, found, name, found_path in drawer.linkable(project)
                       if (found_kind, found) == (kind, part_id)), None)
        if listed is not None:
            folder = listed[1].parent.parent
            raise PartError("%s is only in %s (%s), another project on your list: spark writes only the project --project names",
                            part_id, listed[0], folder, code=sourcing_codes.OTHER_PROJECT_RECORD, subject=part_id,
                            fix=sourcing_codes.OTHER_PROJECT_RECORD_FOLDER.fix % shlex.quote(printable(str(folder))))
    shelf = store.place("board-shelf" if kind == "board" else "shelf")  # P989: a board file's shelf is the shelf's boards/
    if path is not None and path.parent == shelf:
        named = shelved_from(path) or orphan_home(path, kind)
        folder = store.projects().get(named) if named else None
        home = folder / ("boards" if kind == "board" else "parts") / path.name if folder is not None else None
        return (home, named) if home is not None and home.is_file() else (path, None)
    named = store.find_listed_name(project) if where == "project" else None
    return path, named if named and named in (shelved_from(shelf / path.name), orphan_home(shelf / path.name, kind)) else None


def orphan_home(copy_path, kind="part"):
    """
    The listed project an orphan shelf copy belongs to (P1006), or None. A copy is an orphan when it names no project (no
    `based_on`: it was shelved while its folder was on no list), no catalog record has its id (a catalog copy names no
    project by design), and exactly one project on the person's list holds the record, so that project is its home.
    """
    record = _parse(copy_path) if Path(copy_path).is_file() else None
    if not isinstance(record, dict) or "based_on" in record:
        return None
    if kind != "board" and (store.place("catalog") / Path(copy_path).name).is_file():
        return None
    folder = "boards" if kind == "board" else "parts"
    holders = [name for name, root in store.projects().items() if (Path(root) / folder / Path(copy_path).name).is_file()]
    return holders[0] if len(holders) == 1 else None


def refresh_shelf_copy(path, record, project_name, dry_run):
    """
    The shelf copy of a project's record made current again (§5.5) — after a write, and when an earlier write left it behind
    (the record filled in its project while the copy stayed, so every retry said "nothing to change") — said in words:
    current, refreshed, would refresh, or not refreshed and why: a copy that would not meet the contract is not written.
    """
    copy, (shelf, contract, _) = _shelf_copy(path, project_name, record), shelf_of(path)
    if _parse(store.place(shelf) / path.name) == copy:
        return "current"
    wrong = contract(copy, path)
    if wrong:
        return "shelf copy not refreshed: %s" % "; ".join(wrong)
    if dry_run:
        return "would refresh the shelf copy"
    shelve(path, project_name)
    return "shelf copy refreshed"


#: Said by a run that lists a folder and adopts an orphan copy of its records (P1006).
ADOPTED = "  adopted the shelf copy of %s: it was shelved while this folder was on no list, and now follows its record here"


def list_project(folder):
    """
    Put `folder` on the person's list (`store.add_project`) and adopt the orphan shelf copies of its records (P1006): each
    copy `orphan_home` gives this project is refreshed from the record, with `based_on`. Returns (name, [ids adopted]).
    """
    name, adopted = store.add_project(folder), []
    for kind, sub in (("part", "parts"), ("board", "boards")):
        shelf = store.place("board-shelf" if kind == "board" else "shelf")
        for path in sorted((Path(folder) / sub).glob("*.json")):
            record = _parse(path)
            if isinstance(record, dict) and orphan_home(shelf / path.name, kind) == name \
                    and refresh_shelf_copy(path, record, name, False) == "shelf copy refreshed":
                adopted.append(path.stem)
    return name, adopted

def merge_values(record, values):
    """`record` with `values` set, and the values it had: `facts` takes the written names over the held ones, the other names stay
    (P374); `legs` the same, leg by leg (P741); `pictures` view by view (P946); `joined_pads` into `physical.header` (P962)."""
    after, was = dict(record, **values), {key: record.get(key) for key in values}
    if isinstance(values.get("legs"), dict):
        held = record.get("legs") if isinstance(record.get("legs"), dict) else {}
        after["legs"], was["legs"] = dict(held, **values["legs"]), {pin: held.get(pin) for pin in values["legs"]}
    if isinstance(values.get("pin_roles"), dict):  # P464: role by role, so a role keeps its gpio and note
        after["pin_roles"], was["pin_roles"] = missing_facts.merged_roles(record, values)
    if missing_facts.JOINED_PADS in values:  # P962: the pads a board joins live in its header, replaced as a whole
        physical = record.get("physical") if isinstance(record.get("physical"), dict) else {}
        header = physical.get("header") if isinstance(physical.get("header"), dict) else {}
        del after[missing_facts.JOINED_PADS]
        after["physical"] = dict(physical, header=dict(header, joined_pads=values[missing_facts.JOINED_PADS]))
        was[missing_facts.JOINED_PADS] = header.get(missing_facts.JOINED_PADS)
    for field in ("facts", "pictures"):
        if isinstance(values.get(field), dict):
            held = record.get(field) if isinstance(record.get(field), dict) else {}
            after[field], was[field] = dict(held, **values[field]), {name: held.get(name) for name in values[field]}
    return after, was


def in_library(path):
    """True for a record in spark's own library, which is changed in spark's repository, never by parts.py."""
    return Path(path).parent.resolve() in (record_kind.LIBRARY.resolve(), board_records.LIBRARY.resolve())


#: Why a record in spark's own library is not written, filled with its id.
LIBRARY_REFUSAL = "%s is in spark's own library, which is changed in spark's repository, not by parts.py"


def library_problem(part_id):
    """The one refusal of a record in spark's own library (P964): a problem item on the id, with `library_record` and its fix."""
    return _problem(part_id, LIBRARY_REFUSAL % part_id, fix=sourcing_codes.LIBRARY_RECORD.fix, code=sourcing_codes.LIBRARY_RECORD)


def set_fields(part_id, project, values, dry_run, refuse):
    """
    Set fields of a part record in its own home (§5.4) — the catalog's, a project's, or a listed project's behind a shelf
    copy — never spark's library, which is changed in spark's repository. A shelf copy that follows the record is made
    current whether or not this write changed anything (`refresh_shelf_copy`), and the answer says what became of it.
    `refuse(record, after, path)` says what is wrong with the result, and anything it says refuses the write. Values that
    hold a key of `missing_facts.BOARD_WRITE_KEYS` reach a board's record (P464, P962), others a part's; `write_fields`
    writes a home already found.
    """
    board = any(key in values for key in missing_facts.BOARD_WRITE_KEYS)
    return write_fields(part_id, record_path(part_id, project, "board" if board else "part"), values, dry_run, refuse)


def write_fields(part_id, home, values, dry_run, refuse):
    """`set_fields` into `home`, the (path, project whose shelf copy follows it) of `record_path`: a board's record when
    the caller found a board's (P956). A home with no path raises PartError, as `set_fields`."""
    path, source = home
    if path is None:
        raise PartError("no record called %r — `parts.py --need` finds what exists", part_id,
                        code=sourcing_codes.NO_SUCH_PART)
    if in_library(path):
        return Answer(problems=[library_problem(part_id)])
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
