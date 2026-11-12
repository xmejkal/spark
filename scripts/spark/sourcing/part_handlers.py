"""
The helpers of the parts writes and of the goal Operations (W6-S3b, P721; P726 PR 2): the vendors to research in and the
sellers (`vendor_order`, `sellers`) read the project's `Brief`; a set-only write says what it did one way (`_change_line`,
`_write_lines`, `_drawer_answer`); a write that sets a record in its own home (`_set_in_home`) finds that home behind a
shelf copy (`_record_path`, `_shelved_from`) and refreshes the copy (`_refresh_shelf_copy`). The fifteen `_op_` handlers
that were here are Operations on the core since P726 PR 2, one module each (`sourcing_operations.OPERATIONS`); the CLI's
payload handlers still call these helpers until PR 3, which decides this module's name. It imports the records area and the
sourcing modules below it, never `parts.py`.
"""

import json
from pathlib import Path

from spark.core.text_guards import printable
from spark.records import board_records, missing_facts, record_kind, store
from spark.records.brief import Brief
from spark.records.record_kind import (
    Answer, _parse, _problem, _write_record)
from spark.sourcing import drawer, sourcing_codes
from spark.sourcing.part_facts import (
    _shelf_copy, shelvable, shelve)
from spark.sourcing.part_records import PartError, validate


#: Vendors to research in, in order, when a project's brief does not say. DFRobot first because
#: its wiki carries a pinout table and a dimension drawing for every module; Seeed next for the
#: same reason. A project overrides this in `.spark/project.json` → `prefer`.
DEFAULT_VENDOR_ORDER = ("dfrobot", "seeed")


def vendor_order(project=None):
    """The vendors to research in, from the project's brief, else the default."""
    return Brief.from_project(project).prefer or DEFAULT_VENDOR_ORDER


def sellers(project=None):
    """
    Where the person buys, local first, from the project's brief — or nothing, which the
    researcher reports as "no sellers named" rather than choosing a shop for them.
    """
    return Brief.from_project(project).sellers or ()


def _change_line(change, dry_run):
    """
    One set-only write's change (§5.2), the drawer's and the needs file's alike: '  new soil-probe: soil probe × 8 — is
    part sen0193-soil-moisture' for a new drawer entry (× ? when its count was left out), else '  set soil: mark null →
    "have"', every value from what it was. A new entry's key and label pass `printable` here, because a newline in them
    would start a line. A set line's values are JSON, which escapes a newline, and `_say` guards the rest.
    """
    if change["new"] and "entry" in change:
        now, linked = change["now"], change["now"].get("is")
        return printable("  %s %s: %s × %s%s" % ("would add" if dry_run else "new", change["entry"], now.get("label"), now.get("count", "?"),
                                                " — is %s %s" % next(iter(linked.items())) if linked else ""))
    return "  %s %s: %s" % ("would set" if dry_run else "set", change.get("entry") or change.get("need"), "; ".join(
        "%s %s → %s" % (key, json.dumps(change["was"].get(key), ensure_ascii=False), json.dumps(value, ensure_ascii=False))
        for key, value in change["now"].items()))


def _write_lines(changes, problems, dry_run, said=()):
    """
    What a set-only write did or would do (§5.2), said one way for the drawer and the needs file: each change — marked
    `not written:` when anything was refused, because then nothing is written — what else the write has to say, then each refusal; or
    that nothing changes.
    """
    lines = [("  not written: " + _change_line(change, False).strip()) if problems else _change_line(change, dry_run)
             for change in changes] + list(said)
    lines += ["  refused, so nothing was written: %s — %s" % (p["subject"], p["sentence"]) for p in problems]
    return lines or ["  nothing to change"]


def _drawer_answer(changes, questions, problems, dry_run):
    """What a drawer write did or would do (§5.2): all of it, or — when anything is refused — none of it."""
    if not problems and not dry_run:
        drawer.apply(changes)
    made = [change for change in changes if change["now"]]
    wanted = [change["shelve"] for change in made if change["shelve"]]
    shelved = [Path(path).stem for path, project in wanted if shelvable(path, project)]
    left = [Path(path).stem for path, project in wanted if not shelvable(path, project)]
    said = ["  ? %s" % q["sentence"] for q in questions] + [
        "  %s %s on your shelf, so every project finds it%s" % (
            "would put" if dry_run or problems else "put", Path(path).stem,
            "" if project else ". Its folder is on no list, so a later change to the record there does not reach this copy")
        for path, project in wanted if shelvable(path, project)] + [
        "  not shelved: %s — it does not meet the part contract yet, so it stays in its project and the entry still links to it"
        % stem for stem in left]
    return Answer({"changes": [{key: change[key] for key in ("entry", "new", "was", "now")} for change in made],
                   "questions": questions, "shelved": shelved, "not_shelved": left, "written": not (problems or dry_run)},
                  _write_lines(made, problems, dry_run, said), problems=problems)


def _shelved_from(path):
    """The project a shelf copy says it was shelved from (its `based_on`, §5.5) — None for a catalog's copy, or no copy."""
    record = _parse(path) if Path(path).is_file() else None
    based_on = record.get("based_on") if isinstance(record, dict) else None
    named = based_on.get("project") if isinstance(based_on, dict) else None
    return named if isinstance(named, str) else None


def _record_path(part_id, project, kind="part"):
    """
    A part record's own file, and the project whose shelf copy follows it (§5.4, §5.5): the nearest layer that has it, the
    catalog included, else a project on the person's list — except that a shelf copy of a listed project's record is not a
    home: that project's record is. A record found in the project given names that project too, when the shelf holds a copy
    of it shelved from there: the copy follows its record, however the record was reached. `kind` is "board" for a board's record (P464).
    """
    path, where = next(((path, where) for found_kind, found, where, path in drawer.linkable(project) if (found_kind, found) == (kind, part_id)),
                       (None, None))
    if path is not None and path.parent == store.place("shelf"):
        named = _shelved_from(path)
        folder = store.projects().get(named) if named else None
        home = folder / "parts" / path.name if folder is not None else None
        return (home, named) if home is not None and home.is_file() else (path, None)
    named = store.find_listed_name(project) if where == "project" else None
    return path, named if named and _shelved_from(store.place("shelf") / path.name) == named else None


def _refresh_shelf_copy(path, record, project_name, dry_run):
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


def _set_by_name(record, values):
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


def _set_in_home(part_id, project, values, dry_run, refuse):
    """
    Set fields of a part record in its own home (§5.4) — the catalog's, a project's, or a listed project's behind a shelf
    copy — never spark's library, which is changed in spark's repository. A shelf copy that follows the record is made
    current whether or not this write changed anything (`_refresh_shelf_copy`), and the answer says what became of it.
    `refuse(record, after, path)` says what is wrong with the result, and anything it says refuses the write.
    """
    path, source = _record_path(part_id, project, "board" if "pin_roles" in values else "part")  # P464: only a level in pin_roles reaches a board
    if path is None:
        raise PartError("no record called %r — `parts.py --need` finds what exists", part_id,
                        code=sourcing_codes.NO_SUCH_PART)
    if path.parent.resolve() in (record_kind.LIBRARY.resolve(), board_records.LIBRARY.resolve()):
        return Answer(problems=[_problem(part_id, "%s is in spark's own library, which is changed in spark's repository, "
                                                  "not by parts.py" % part_id)])
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        return Answer(problems=[_problem(part_id, "%s is not a JSON object (%s) — repair the file by hand first" % (part_id, path))])
    after, was = _set_by_name(record, values)
    wrong = refuse(record, after, path)
    if wrong:
        return Answer(problems=[_problem(part_id, sentence) for sentence in wrong])
    changes = after != record
    if changes and not dry_run:
        _write_record(path, after)
    shelf_copy = _refresh_shelf_copy(path, after, source, dry_run) if source else None
    said = ("  %s %s (%s): %s" % ("would set" if dry_run else "set", part_id, path, "; ".join(
                "%s %s → %s" % (key, json.dumps(was[key], ensure_ascii=False), json.dumps(value, ensure_ascii=False))
                for key, value in values.items()))
            if changes else "  nothing to change: %s (%s) already says this" % (part_id, path))
    return Answer({"part": part_id, "path": str(path), "was": was, "now": values, "written": not dry_run, "shelf_copy": shelf_copy},
                  [said] + (["  " + shelf_copy] if shelf_copy not in (None, "current") else []))
