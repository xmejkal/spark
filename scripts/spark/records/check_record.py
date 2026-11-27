"""
The check record of a project (P1209, #1758): what a check Operation keeps of its last answer, `<project>/.spark/<op>.json`,
named by the op that wrote it (`check-firmware`, and `check-design` since P1255). `CheckRecordStore` writes and reads it; the
flow reads it to say the checks' state, and no gate reads it. `answer_saved` and `answer_not_saved` are the one keep step
that both check Operations call.

The record: `{"schema", "op", "at", "inputs", "inputs_sha256", "status", "data", "lines"}`. `inputs` are the paths the
check read, each a file or a folder: relative to the project, or `<root>:<path>` in one of `ROOTS` (P1255, which amends
P1209's v2-1, `p1209-plan.md:432-434`): `spark:` for spark's own folder (the library's boards) and `store:` for the
person's store (the shelf's boards). Never an absolute path, so no home path lands in a tracked `.spark/` file.
`input_name` tries the project first, then `spark:`, then `store:`. `inputs_sha256` is the sha256 of each file under
them, by its name: the walk is `folder_walk.files_under`'s (every file but `__pycache__`), a missing input adds
`folder_walk.MISSING` under its own name, and the files the Store's `leave_out` names (the secrets files) are in it with
neither their path nor their sha256. Another machine or another store reads a root input's record as older. A record whose inputs no longer hash to it reads as older (`current` False), never as
current. The precedent is `build/build_record.BuildRecordStore`; this one follows the reader rule of `core/outcomes`, as
`deploy_record_store.LastDeploy` does, and computes `current` itself, so every reader says the same of it.
"""

import collections
import hashlib
import json
from pathlib import Path, PurePosixPath

from spark.core import outcomes
from spark.records import store
from spark.records.folder_walk import MISSING, files_under

# --- MVP ---
#: The folder of the project's own records, and the record's schema.
SPARK_FOLDER, SCHEMA = ".spark", 1
#: The keys of a record, each one a reader needs.
KEYS = ("schema", "op", "at", "inputs", "inputs_sha256", "status", "data", "lines")
#: Why a record is not-checked, one sentence each.
WHY_NO_JSON = "the check record is no JSON"
WHY_SHAPE = "the check record is of another shape (%s)"
WHY_INPUT = "the check record names an input outside the project and its roots (%s)"
WHY_NO_INPUTS = "the check record names no input"
WHY_CANNOT_READ = "the check record cannot be read (%s)"
WHY_UNREADABLE = "its files cannot be read (%s)"
#: What a run that could not keep its check record says, as a note and a line, with the class of what failed (P1209).
NOT_KEPT_SENTENCE = "did not keep the check record: %s"
#: The roots an input may name besides the project, `<root>:<path>` (P1255): each gives its folder when called.
ROOTS = {"spark": lambda: store.PLUGIN, "store": store.home}


class CheckRecord(collections.namedtuple("CheckRecord", "name state why at current status data lines inputs",
                                         defaults=(None,) * 7)):
    """Value. What the check record `name` says: `state` one of the three words of `outcomes`. With outcomes.RECORDED,
    `at`, `status`, `data`, `lines` and `inputs` are the record's, and `current` says whether the inputs still hash to it.
    With outcomes.NOT_CHECKED, `why` is the reason. The rest are None."""

    def to_dict(self):
        return dict(self._asdict())


def record_file(name):
    """The check record of the op `name`, as a path in the project: `.spark/<name>.json`."""
    return "%s/%s.json" % (SPARK_FOLDER, name)


def is_plain_input(text, roots=ROOTS):
    """True for an input a record may name: a relative path to something inside the project, or `<root>:<path>` for a
    root of `roots`, with no `..` part. The text is split at its first `:`, so `home:x` and `C:/x` are refused. `.`, `./`
    and an empty path name the project (or the root) itself, so they are no input."""
    if not isinstance(text, str) or "\\" in text:
        return False
    root, colon, rest = text.partition(":")
    if colon and root not in roots:
        return False
    path = PurePosixPath(rest if colon else text)
    return bool(path.parts) and not path.is_absolute() and ".." not in path.parts


def where_of(project, name, roots=ROOTS):
    """(the folder the input `name` is in, the prefix of its files' names): its root's folder and `<root>:` for a root
    input, else `project` and no prefix."""
    root, colon, _ = name.partition(":")
    return (Path(roots[root]()), root + colon) if colon else (Path(project), "")


def input_name(project, path, roots=ROOTS):
    """The name a record gives the file or folder `path`: its path in `project`, else `<root>:<path>` in the first of
    `roots` that holds it, else None. Both sides are resolved, so a folder given through a link (`/var` and `/private/var`)
    is still the project. A name that is no plain input (the project itself, a colon in a name) is None."""
    path = Path(path).resolve()
    for prefix, folder in [("", Path(project))] + [(root + ":", Path(found())) for root, found in roots.items()]:
        try:
            name = prefix + path.relative_to(folder.resolve()).as_posix()
        except ValueError:
            continue
        return name if is_plain_input(name, roots) else None
    return None


def inputs_sha256(project, inputs, leave_out=None, roots=ROOTS):
    """{name: sha256 hex} of each file under each of `inputs`: a file as itself, a folder by its files (`files_under`), a
    missing input as MISSING under its own name. A file's name is its path in the project, or in its root with the root's
    prefix (`where_of`). A file `leave_out(name)` names is left out whole. OSError when a file cannot be read."""
    hashed = {}
    for name in inputs:
        folder, prefix = where_of(project, name, roots)
        where = folder / name[len(prefix):]
        files = [where] if where.is_file() else files_under(where) if where.is_dir() else None
        if files is None:
            hashed[name] = hashlib.sha256(MISSING).hexdigest()
            continue
        for file in files:
            relative = prefix + file.relative_to(folder).as_posix()
            if not (leave_out and leave_out(relative)):
                hashed[relative] = hashlib.sha256(file.read_bytes()).hexdigest()
    return dict(sorted(hashed.items()))


def shape_problem(record, name, roots=ROOTS):
    """Why `record` is no check record of op `name` over `roots`, or None when it is one."""
    if not isinstance(record, dict):
        return WHY_SHAPE % "no object"
    missing = [key for key in KEYS if key not in record]
    if missing:
        return WHY_SHAPE % ("no " + ", ".join(missing))
    if type(record["schema"]) is not int or record["schema"] != SCHEMA or record["op"] != name:  # JSON's true is no 1
        return WHY_SHAPE % ("schema %r, op %r" % (record["schema"], record["op"]))
    if record["inputs"] == []:
        return WHY_NO_INPUTS
    if not isinstance(record["inputs"], list) or not all(is_plain_input(each, roots) for each in record["inputs"]):
        return WHY_INPUT % record["inputs"]
    typed = (("at", str), ("inputs_sha256", dict), ("status", str), ("data", dict), ("lines", list))
    wrong = [key for key, kind in typed if not isinstance(record[key], kind)]
    if not wrong and not all(isinstance(line, str) for line in record["lines"]):
        wrong = ["lines"]  # a line that is no text would crash the sentence that joins them
    return WHY_SHAPE % ("wrong " + ", ".join(wrong)) if wrong else None


class CheckRecordStore:
    """
    Store: the check record `<project>/.spark/<name>.json` of one check Operation, `name` its op (a `store.PLAIN` id, else
    ValueError). `save` writes it through the store's one atomic write, into the `.spark/` of a project that exists, and
    never makes the project folder. `read` gives the CheckRecord and never raises. `leave_out` is the rule of the files
    the record never names (a callable of a path in the project), the same on both sides. `roots` are the roots its
    inputs may name (ROOTS; a test gives its own).
    """

    def __init__(self, project, name, leave_out=None, roots=ROOTS):
        if not isinstance(name, str) or not store.PLAIN.fullmatch(name):
            raise ValueError("a check record's name is a plain id, not %r" % (name,))
        self.project, self.name, self.leave_out, self.roots = Path(project), name, leave_out, roots
        self.path = self.project / record_file(name)

    def save(self, inputs, at, answer):
        """Write the record of `answer` ({status, data, lines}) at the time `at` (with its zone), over `inputs`, hashed now.
        OSError when it cannot: the project is not there, `.spark` is no folder, or the write fails. ValueError for no
        inputs or an input that is not plain (`is_plain_input`): a programmer's error, as a name that is no plain id is."""
        if not inputs or not all(is_plain_input(each, self.roots) for each in inputs):
            raise ValueError("a check record's inputs are plain paths in the project, not %r" % (inputs,))
        (self.project / SPARK_FOLDER).mkdir(exist_ok=True)  # no parents: a mistyped project is never made
        record = {"schema": SCHEMA, "op": self.name, "at": at, "inputs": list(inputs),
                  "inputs_sha256": inputs_sha256(self.project, inputs, self.leave_out, self.roots),
                  "status": answer["status"], "data": answer["data"], "lines": list(answer["lines"])}
        store.write_file(self.path, json.dumps(record, indent=1, sort_keys=True, ensure_ascii=False) + "\n")

    def read(self):
        """The CheckRecord of this project: none-recorded with no file, not-checked with `why` for a file that cannot be read,
        is no JSON or is of another shape, or inputs that cannot be read, else recorded, with `current`."""
        try:
            if not self.path.exists():  # raises under a .spark/ that cannot be searched
                return CheckRecord(self.name, outcomes.NONE_RECORDED)
            data = self.path.read_bytes()
        except OSError as failed:
            return CheckRecord(self.name, outcomes.NOT_CHECKED, WHY_CANNOT_READ % type(failed).__name__)
        try:
            record = json.loads(data.decode("utf-8"))
        except (ValueError, RecursionError):  # a UnicodeDecodeError is a ValueError
            return CheckRecord(self.name, outcomes.NOT_CHECKED, WHY_NO_JSON)
        why = shape_problem(record, self.name, self.roots)
        if why:
            return CheckRecord(self.name, outcomes.NOT_CHECKED, why)
        try:
            now = inputs_sha256(self.project, record["inputs"], self.leave_out, self.roots)
        except OSError as failed:
            return CheckRecord(self.name, outcomes.NOT_CHECKED, WHY_UNREADABLE % type(failed).__name__)
        return CheckRecord(self.name, outcomes.RECORDED, None, record["at"], now == record["inputs_sha256"],
                           record["status"], record["data"], record["lines"], record["inputs"])


def answer_saved(records, result, inputs, at, answer):
    """The OperationResult `result` with `data.written` True once the CheckRecordStore `records` saved `answer` over
    `inputs` at `at`. A save that fails (OSError) gives `answer_not_saved` with NOT_KEPT_SENTENCE and the class of what
    failed, and the result stands."""
    try:
        records.save(inputs, at, answer)
    except OSError as failed:
        sentence = NOT_KEPT_SENTENCE % type(failed).__name__
        return answer_not_saved(result, record_file(records.name), sentence)
    return result._replace(data=dict(result.data, written=True))


def answer_not_saved(result, subject, sentence):
    """`result` with `data.written` False and, when `sentence` is given, that sentence as its last line and as a note of
    `subject` (the record's path in the project). A run that has nothing to say (no project named) passes None."""
    if sentence is None:
        return result._replace(data=dict(result.data, written=False))
    return result._replace(data=dict(result.data, written=False), lines=list(result.lines) + [sentence],
                           notes=list(result.notes or []) + [{"subject": subject, "sentence": sentence}])
# --- end MVP ---
