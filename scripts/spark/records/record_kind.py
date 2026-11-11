"""
The record contract (W6-S3a, P720): what every JSON record spark keeps holds and owes, part or board. Where records
live (`LIBRARY`, `record_home`, `available`), the keys and verbs a record is held to, the type of each field `validate`
reads (`RECORD_TYPES`, `type_problems`), a document's shape and its citations, and the one reader and writer of a record
file (`_parse`, `_write_record`). Every finding is an `Answer` item made by `_problem`, `_cannot` or `_note`. `RecordKind`
(P724) validates one kind of record by its named rules, and `board_records.BOARD` and `part_records.PART` are its two.

Moved whole from `parts.py`, which reads these names, as do `drawer`, `needs` and `board_records`. It imports `store`
and the core alone of spark, so the records area reads nothing above it. `RecordFinder` (`areas/records.md`) comes with P342.
`Answer.to_result` and `from_result` (P726) are the seam between a handler's `Answer` and the core's `OperationResult`.
"""

import json
import re
from collections import namedtuple
from pathlib import Path

from spark.core import outcomes
from spark.core.result import Finding, NextStep, OperationResult
from spark.core.text_guards import guard_lines
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


#: What a refusal line on stderr starts with when an answer has no lines (parts.py's rule, P726: `Answer.to_result`).
REFUSED_PREFIX = "parts.py: "


class Answer(namedtuple("Answer", "data lines problems unchecked next truncated notes assumptions diagnostics",
                        defaults=(None, (), (), (), (), None, (), (), ()))):
    """
    Result: what one operation found (§6.4.1): its `data`, the `lines` a person reads without --json, and the rest of the
    envelope. A handler returns one; `main` prints it either way and exits by its status. `notes` are said and never
    fail ({subject, sentence}); `assumptions` are what the answer rests on that nobody has checked ({fact, basis, …}).
    `diagnostics` are lines for stderr, with --json or without, so no handler prints (X2). `text_lines` is the text
    printer's rule, `to_result` the OperationResult of this answer for the core, and `from_result` the way back (P726).
    """

    def text_lines(self):
        """
        The person's lines, then what the answer carries that they do not say yet: each problem and could-not-run item
        with its fix, each note and assumption, and the next steps (P124, #58). A line already said is not said again, so a
        handler that prints an item its own way keeps its wording; one that forgets an item no longer drops it.
        """
        lines = list(self.lines)
        said = lambda words: bool(words) and any(words in line for line in self.lines)  # noqa: E731 — the handler's own
        for heading, items in (("", self.problems), ("could not check: ", self.unchecked)):
            for item in items:
                if not (said(item["sentence"]) or said(item.get("subject"))):  # a handler may word an item its own way
                    lines.append("  %s%s%s" % (heading, "%s: " % item["subject"] if item.get("subject") else "", item["sentence"]))
                if item.get("fix") and not said(item["fix"]):
                    lines.append("  fix%s: %s" % (" for %s" % item["subject"] if item.get("subject") else "", item["fix"]))
        for note in self.notes:
            shown = "%s: %s" % (note["subject"], note["sentence"]) if note.get("subject") else note["sentence"]
            if not said(shown):
                lines.append("  " + shown)
        for assumption in self.assumptions:
            if not (said(assumption["fact"]) or said(assumption.get("sentence"))):
                lines.append("  ? %s%s%s" % (assumption["fact"], " = %s" % assumption["assumed"] if "assumed" in assumption else "",
                                             " — " + assumption["sentence"] if assumption.get("sentence") else ""))
            if assumption.get("upgrade") and not said(assumption["upgrade"]):
                lines.append("    to settle it: %s" % assumption["upgrade"])
        lines += ["  next: parts.py %s — %s" % (" ".join(step["argv"]), step["why"]) for step in self.next]
        return lines

    def to_result(self):
        """
        The OperationResult of this answer, parts.py's text rules kept: with lines, `text_lines` each guarded; with none,
        each problem and unchecked item is one stderr line (`REFUSED_PREFIX`, the sentence, ` — ` and the fix when there is
        one) in `diagnostics` after the answer's own, and the lines are what else the answer says. An item's `code` is
        its Finding's, None when it has none.
        """
        findings = [Finding(outcomes.PROBLEMS, item["subject"], item.get("code"), item["sentence"], item.get("fix")) for item in self.problems]
        findings += [Finding(outcomes.COULD_NOT_RUN, None, item.get("code"), item["sentence"], item.get("fix")) for item in self.unchecked]
        steps = [NextStep(step["op"], step["argv"], step["why"], step["effects"], step["needs_yes"], step.get("needs_person"), step.get("env"))
                 for step in self.next]
        said, diagnostics = self, list(self.diagnostics)
        if not self.lines:
            diagnostics += [REFUSED_PREFIX + item["sentence"] + (" — " + item["fix"] if item.get("fix") else "")
                            for item in list(self.problems) + list(self.unchecked)]
            said = self._replace(problems=(), unchecked=())
        return OperationResult(self.data, findings, steps, [guard_lines(line) for line in said.text_lines()], diagnostics,
                               self.notes, self.truncated, self.assumptions)

    @classmethod
    def from_result(cls, result):
        """The Answer of an OperationResult: each Finding an item by its severity, each NextStep a step dict, so a handler
        that runs an Operation on the core answers as the others do (`parts.py --needs-drop`, P514)."""
        return cls(result.data, result.lines,
                   problems=[_problem(found.subject, found.sentence, found.fix, found.code) for found in result.findings if found.severity == outcomes.PROBLEMS],
                   unchecked=[_cannot(found.sentence, found.fix, found.code) for found in result.findings if found.severity == outcomes.COULD_NOT_RUN],
                   next=[outcomes.add_env(outcomes.step(s.op, s.argv, s.why, s.effects, s.needs_yes, s.needs_person), s.env) for s in result.next],
                   truncated=result.truncated, notes=result.notes or (), assumptions=result.assumptions or (), diagnostics=result.diagnostics)


def _problem(subject, sentence, fix=None, code=None):
    """A problem item; `code` (P726) is in it only when given, so the envelopes of the handlers on parts.py do not change."""
    return dict({"subject": subject, "sentence": sentence, "fix": fix}, **({"code": code} if code is not None else {}))


def _cannot(sentence, fix=None, code=None):
    """A could-not-run item; `code` as `_problem`'s."""
    return dict({"sentence": sentence, "fix": fix}, **({"code": code} if code is not None else {}))


def _note(line):
    """A note as a field (P124): `<subject>: <sentence>`, the way a handler prints one, split at its first colon."""
    subject, _, sentence = line.partition(": ")
    return {"subject": subject, "sentence": sentence} if sentence else {"subject": None, "sentence": line}


def _with_project(project):
    return ["--project", str(project)] if project else []


def available(project: Path = None) -> list:
    return sorted(store.records("parts", LIBRARY, project))


#: The facts of one `RecordKind.validate` call that each rule reads (P724): the record's file, the keys it owes (whose
#: checks do not run) and whether it is held to the fab contract too. A weak name, kept: spark has no better word.
Validation = namedtuple("Validation", "path owed for_fab")


class RecordKind:
    """
    Strategy: one kind of record, a board or a part, and the contract it is held to (P724). Each kind is one instance
    (`board_records.BOARD`, `part_records.PART`), so a caller swaps one for the other. It is given the kind's name, its
    schema `version`, its `required` keys and its `rules`, each a function `(record, validation) -> list` of problems,
    which run in order after the two checks every kind shares. A rule in `stop_after` that finds a problem is the last
    to run, because the rules after it read what it checked. It raises what a rule raises on a record too malformed to
    read, which `_shape_problems` says as one line.
    """

    def __init__(self, kind, version, required, rules, stop_after=()):
        self.kind, self.version, self.required = kind, version, required
        self.rules, self.stop_after = tuple(rules), tuple(stop_after)

    def validate(self, record, path, owed=(), for_fab=False):
        """Every way `record` breaks the contract, as sentences. Empty means it holds. An `owed` key
        skips the shared version and required-key checks, and each rule that reads `validation.owed` (the part's do; no
        board rule does)."""
        validation = Validation(path, owed, for_fab)
        problems = self.version_problems(record, validation) + self.required_problems(record, validation)
        for rule in self.rules:
            found = rule(record, validation)
            problems += found
            if found and rule in self.stop_after:
                break
        return problems

    def version_problems(self, record, validation):
        """The schema version this code understands, or one problem; none when the record owes its `schema`."""
        if "schema" in validation.owed or record.get("schema") == self.version:
            return []
        return ["schema is %r, but this code understands only %d" % (record.get("schema"), self.version)]

    def required_problems(self, record, validation):
        """One problem per required key the record lacks and does not owe."""
        return ["missing required key %r" % key for key in self.required if key not in record and key not in validation.owed]


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
    documents = part.get("documents") or {}
    for key, entry in documents.items():
        if isinstance(entry, dict) and entry.get("kept") is False:  # P737: a document a page listed that the store cannot keep
            if not isinstance(entry.get("url"), str) or not entry["url"]:
                problems.append("documents.%s is not kept and names no url, so it points at nothing" % key)
            if "sha256" in entry:
                problems.append("documents.%s says kept: false and holds a sha256: one of the two is wrong" % key)
        elif not isinstance(entry, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256"))):
            problems.append("documents.%s has no sha256 that is one, so the store cannot find it" % key)
        elif not entry.get("file"):
            problems.append("documents.%s names no file" % key)
    for where, cited in _citations(part):
        if not isinstance(cited, str) or cited not in documents:
            problems.append("%s cites %r, which documents does not hold — a pointer to nothing" % (where, cited))
        elif isinstance(documents[cited], dict) and documents[cited].get("kept") is False:
            problems.append("%s cites %r, which is not kept, so nobody can read it there" % (where, cited))
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
