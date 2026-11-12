"""
What a set-only write says (P726 PR 3; the functions were `part_handlers`' and `goal_handlers`' since W6-S3b): one line per
change (`change_line`), the lines of a write, refused or made (`write_lines`), the drawer write's Answer (`drawer_answer`,
§5.2) and the line a project file gets when it starts naming drawer entries (`names_your_entries`, shared by `--pick` and
`--requirements`, C-17, F16).
"""

import json
from pathlib import Path

from spark.core.text_guards import printable
from spark.records.record_kind import Answer
from spark.sourcing import drawer
from spark.sourcing.part_facts import shelvable


# --- MVP ---
def change_line(change, dry_run):
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


def write_lines(changes, problems, dry_run, said=()):
    """
    What a set-only write did or would do (§5.2), said one way for the drawer and the needs file: each change — marked
    `not written:` when anything was refused, because then nothing is written — what else the write has to say, then each refusal; or
    that nothing changes.
    """
    lines = [("  not written: " + change_line(change, False).strip()) if problems else change_line(change, dry_run)
             for change in changes] + list(said)
    lines += ["  refused, so nothing was written: %s — %s" % (p["subject"], p["sentence"]) for p in problems]
    return lines or ["  nothing to change"]


def drawer_answer(changes, questions, problems, dry_run):
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
                  write_lines(made, problems, dry_run, said), problems=problems)


def names_your_entries(file_name, new_keys, dry_run):
    """
    What a write says once when a project file starts naming drawer entries by their keys — each a key made from the person's
    label (C-17; F16): needs.json for --pick, requirements.json for --requirements, worded alike. Nothing when no key is new.
    """
    return ["  %s %s your drawer entr%s %s — a key made from your label, in the project's own file" % (file_name, "would name" if dry_run else
        "names", "y" if len(new_keys) == 1 else "ies", ", ".join(sorted(new_keys)))] if new_keys else []
# --- end MVP ---
