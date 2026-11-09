"""
The record contract (W6-S3a, P720): what every JSON record spark keeps holds and owes, part or board. Where records
live (`LIBRARY`, `record_home`, `available`), the keys and verbs a record is held to, the type of each field `validate`
reads (`RECORD_TYPES`, `type_problems`), a document's shape and its citations, and the one reader and writer of a record
file (`_parse`, `_write_record`). Every finding is an `Answer` item made by `_problem`, `_cannot` or `_note`.

Moved whole from `parts.py`, which reads these names, as do `drawer`, `needs` and `board_records`. It imports `store`
alone of spark, so the records area reads nothing above it. `RecordKind` and `RecordFinder` (`areas/records.md`) come
with P391's card.
"""

import json
import re
from collections import namedtuple
from pathlib import Path

from spark.records import store

#: Parts ship with the plugin, and a project may keep its own in `parts/`. A project's own wins,
#: for the same reason a board definition does: what you verified yourself must not be replaced.
LIBRARY = Path(__file__).resolve().parents[3] / "parts"
DEFINITION_SUFFIX = ".json"

REQUIRED_KEYS = ("schema", "id", "name", "kind", "needs")

#: Fields a record no longer holds, each with where that fact lives now (P95, W16). Owning one is the person's
#: fact, not the part's: it is a drawer entry, and a photo of the one they own goes on that entry.
RETIRED = {"owned": "what you own is a drawer entry — /spark:drawer, `parts.py --drawer-set`",
           "photo": "a photo of the one you own goes on its drawer entry's `photos`, kept with `parts.py --keep`"}

#: What a part does (§5.6): the PO's 13 verbs. `drive` is the driver (an L9110S), `move` the thing driven (a motor).
VERBS = ("sense", "input", "indicate", "sound", "move", "drive", "power", "keep-time", "store", "compute",
         "communicate", "connect", "mount")


#: The facts the chain reads from a part record (§5.4): absent, the record owes them, and no build can place it.
CHAIN_FACTS = ("footprint", "pin_order", "pin_order_proof", "body_mm", "simulation")
#: What `--unverified` says after its list: a result goes back with `--fact-set`, under a row's `write` key.
WRITE_BACK_HINT = "write a checked result back with its source"


def _absent(key, value):
    if key == "body_mm":
        return not (isinstance(value, dict) and all(isinstance(value.get(side), (int, float)) for side in ("width", "height")))
    return value is None or value == [] or value == {} or value == ""


def owes(record):
    """What a part record owes (§5.4): each required key missing, and each fact the chain reads that is absent."""
    return ([key for key in REQUIRED_KEYS if key not in record] +
            [key for key in CHAIN_FACTS if _absent(key, record.get(key))])


def _shape_problems(check, record, path, what):
    """A check's problems — or, when the record is too malformed for the check to read, one saying so (§5.4: never a traceback)."""
    try:
        return check(record, path)
    except (AttributeError, TypeError, KeyError, ValueError) as wrong:
        return ["does not meet the %s's shape (%s)" % (what, wrong)]


#: What a pin's WIRING name may contain. Measured, not assumed: a probe board with six pin labels showed `IN+`, `OUT-`
#: and `A.B` unresolvable as tscircuit selectors while `V_IN`, `GND2` and `3V3` resolved. An MP1584 buck's pads are
#: silkscreened IN+ IN- OUT+ OUT-, and a record using those names produced four "could not find port" errors and a
#: regulator joined to nothing. The fix at the time renamed the pins and LOST the silkscreen — which is exactly the
#: failure `physical.pad_aliases` prevents on the board side. Parts had no equivalent.
#:
#: So an entry has a `pin` (what selectors use, restricted to this) and optionally `printed`
#: (what is silkscreened, unrestricted). The generated file shows both where they differ.
SELECTOR_SAFE = "^[A-Za-z0-9_]+$"


#: What one operation found (§6.4.1): its `data`, the lines a person reads without --json, and the rest of the
#: envelope. A handler returns one; `main` prints it either way and exits by its status. `notes` are said and never
#: fail ({subject, sentence}); `assumptions` are what the answer rests on that nobody has checked ({fact, basis, …}).
#: `diagnostics` are lines for stderr, with --json or without, so no handler prints (X2).
Answer = namedtuple("Answer", "data lines problems unchecked next truncated notes assumptions diagnostics",
                    defaults=(None, (), (), (), (), None, (), (), ()))


def _problem(subject, sentence, fix=None):
    return {"subject": subject, "sentence": sentence, "fix": fix}


def _cannot(sentence, fix=None):
    return {"sentence": sentence, "fix": fix}


def _note(line):
    """A note as a field (P124): `<subject>: <sentence>`, the way a handler prints one, split at its first colon."""
    subject, _, sentence = line.partition(": ")
    return {"subject": subject, "sentence": sentence} if sentence else {"subject": None, "sentence": line}


def _with_project(project):
    return ["--project", str(project)] if project else []


def available(project: Path = None) -> list:
    return sorted(store.records("parts", LIBRARY, project))

#: The three lists in a record that hold pins. Written out three times before 2026-09-29, and the missing-pin rule was
#: applied to one of them for a week while the other two were read with `entry["pin"]` — G15. A fourth list added to the
#: schema now has to be added here, and nowhere else.
PIN_LISTS = ("needs", "power", "unused_pins")


class ListOf:
    """A type in `RECORD_TYPES`: a list whose every item has the type `item`, or is null where `nulls` allows it."""

    def __init__(self, item, nulls=False):
        self.item, self.nulls = item, nulls


class MapOf:
    """A type in `RECORD_TYPES`: an object whose every value has the type `value`, whatever its keys."""

    def __init__(self, value):
        self.value = value


#: The type of each field that `validate`'s checks read (P263). An object here names the fields it checks, and a field
#: it does not name is free. A null field is absent, not wrong: that is for the checks that say what is owed or missing.
#: A null item in a list is wrong, unless the list allows it. A check that reads a new field adds its type here, or a
#: record of the wrong type crashes it into one shape line. `rail` is the one field read without an entry here: its own
#: check names a wrong one (P87), and the output check reads only a rail that is a string.
RECORD_TYPES = {
    "needs": ListOf({"signal": str, "pin": str, "bus": str, "direction": str, "needs": ListOf(str)}),
    "power": ListOf({"pin": str, "direction": str, "polarity": str}),  # `rail` has its own check (P87)
    "unused_pins": ListOf({"pin": str}),
    "host_parts": ListOf({"kind": str, "pin": str}),
    "sourcing": ListOf(dict),
    "facts": MapOf(dict),
    "documents": MapOf(dict),
    "pin_order": ListOf(str, nulls=True),  # a null is a pad with nothing on it
}

def _type_name(expected):
    return "a list" if isinstance(expected, ListOf) else "a string" if expected is str else "an object"


def type_problems(value, expected=None, where=""):
    """
    Each value in a part record whose type is not the one `RECORD_TYPES` says, as "needs[0] is 'a', but it is an
    object" — so a wrong entry is named, not hidden in one shape line by the first check that reads it (P263).
    """
    expected = RECORD_TYPES if expected is None else expected
    if value is None:
        return []
    if not (isinstance(value, expected) if isinstance(expected, type) else
            isinstance(value, list) if isinstance(expected, ListOf) else isinstance(value, dict)):
        return ["%s is %r, but it is %s" % (where, value, _type_name(expected))]
    if isinstance(expected, ListOf):
        return [problem for index, item in enumerate(value)
                for problem in (["%s[%d] is None, but it is %s" % (where, index, _type_name(expected.item))]
                                if item is None and not expected.nulls else
                                type_problems(item, expected.item, "%s[%d]" % (where, index)))]
    if isinstance(expected, MapOf):
        return [problem for key, inner in value.items()
                for problem in type_problems(inner, expected.value, "%s.%s" % (where, key))]
    if isinstance(expected, dict):
        return [problem for key, inner in expected.items()
                for problem in type_problems(value.get(key), inner, "%s.%s" % (where, key) if where else key)]
    return []


def document_problems(part: dict) -> list:
    """
    A record points at its kept sources from `documents`, which replaced `attachments` (P62a,
    W16: one format, no reader for both). Each entry names a URL, the file, and a checksum that
    is one — the store finds a file by it, so a wrong one is a pointer to nothing.
    """
    problems = []
    if "attachments" in part:
        problems.append("`attachments` was replaced by `documents` (P62a): the file goes to the "
                        "store, the record keeps the pointer — run parts.py --fetch to redo it")
    for key, entry in (part.get("documents") or {}).items():
        if not isinstance(entry, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256"))):
            problems.append("documents.%s has no sha256 that is one, so the store cannot find it" % key)
        elif not entry.get("file"):
            problems.append("documents.%s names no file" % key)
    problems += ["%s cites %r, which documents does not hold — a pointer to nothing" % (where, cited)
                 for where, cited in _citations(part) if not isinstance(cited, str) or cited not in (part.get("documents") or {})]
    return problems


def _citations(value, where=""):
    """(field, document key) for every `cites` in a record, at any depth."""
    found = []
    for name, inner in (value.items() if isinstance(value, dict) else []):
        here = "%s.%s" % (where, name) if where else name
        if name == "cites" and isinstance(inner, dict):
            found.append((where, inner.get("document")))
        elif isinstance(inner, dict):
            found += _citations(inner, here)
    return found


def record_home(part_id, project=None):
    """The folder a record lives in — the nearest layer that has it, the catalog included — or None."""
    found = store.records("parts", LIBRARY, project, drafts=True).get(part_id)
    return found[1].parent if found else None


def _parse(path):
    try:
        return json.loads(path.read_text())
    except ValueError:
        return None


def _write_record(path, record):
    """A record back to its own home, whole (§6.1): through the store when it lives there (contained, private), else to its file."""
    for name in ("shelf", "catalog"):
        if path.parent == store.place(name):
            return store.write_json(name, path.stem, record)
    return store.write_file(path, json.dumps(record, indent=2, ensure_ascii=False) + "\n")
