"""
The check record of a project (P1209, #1758): what a check Operation keeps of its last answer, `<project>/.spark/<op>.json`,
named by the op that wrote it (`check-firmware`; `check-design` for P1255). `CheckRecordStore` writes and reads it; the flow
reads it to say the free checks' state, and no gate reads it.

The record: `{"schema", "op", "at", "inputs", "inputs_sha256", "status", "data", "lines"}`. `inputs` are the paths the
check read, relative to the project, each a file or a folder. `inputs_sha256` is the sha256 of each file under them, by its
path in the project: the walk is `folder_walk.files_under`'s (every file but `__pycache__`), a missing input adds
`folder_walk.MISSING` under its own path, and the files the Store's `leave_out` names (the secrets files) are in it with
neither their path nor their sha256. A record whose inputs no longer hash to it reads as older (`current` False), never as
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
WHY_INPUT = "the check record names an input outside the project (%s)"
WHY_NO_INPUTS = "the check record names no input"
WHY_CANNOT_READ = "the check record cannot be read (%s)"
WHY_UNREADABLE = "its files cannot be read (%s)"


class CheckRecord(collections.namedtuple("CheckRecord", "name state why at current status data lines inputs",
                                         defaults=(None,) * 7)):
    """Value. What the check record `name` says: `state` one of the three words of `outcomes`. With outcomes.RECORDED,
    `at`, `status`, `data`, `lines` and `inputs` are the record's, and `current` says whether the inputs still hash to it.
    With outcomes.NOT_CHECKED, `why` is the reason. The rest are None."""

    def to_dict(self):
        return dict(self._asdict())


def is_plain_input(text):
    """True for an input a record may name: a relative path to something inside the project, with no `..` part. `.`, `./`
    and an empty path name the project itself, so they are no input."""
    if not isinstance(text, str) or "\\" in text:
        return False
    path = PurePosixPath(text)
    return bool(path.parts) and not path.is_absolute() and ".." not in path.parts


def inputs_sha256(project, inputs, leave_out=None):
    """{path in the project: sha256 hex} of each file under each of `inputs`: a file as itself, a folder by its files
    (`files_under`), a missing input as MISSING under its own path. A file `leave_out(path)` names is left out whole.
    OSError when a file cannot be read."""
    project, hashed = Path(project), {}
    for name in inputs:
        where = project / name
        files = [where] if where.is_file() else files_under(where) if where.is_dir() else None
        if files is None:
            hashed[name] = hashlib.sha256(MISSING).hexdigest()
            continue
        for file in files:
            relative = file.relative_to(project).as_posix()
            if not (leave_out and leave_out(relative)):
                hashed[relative] = hashlib.sha256(file.read_bytes()).hexdigest()
    return dict(sorted(hashed.items()))


def shape_problem(record, name):
    """Why `record` is no check record of op `name`, or None when it is one."""
    if not isinstance(record, dict):
        return WHY_SHAPE % "no object"
    missing = [key for key in KEYS if key not in record]
    if missing:
        return WHY_SHAPE % ("no " + ", ".join(missing))
    if type(record["schema"]) is not int or record["schema"] != SCHEMA or record["op"] != name:  # JSON's true is no 1
        return WHY_SHAPE % ("schema %r, op %r" % (record["schema"], record["op"]))
    if record["inputs"] == []:
        return WHY_NO_INPUTS
    if not isinstance(record["inputs"], list) or not all(is_plain_input(each) for each in record["inputs"]):
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
    the record never names (a callable of a path in the project), the same on both sides.
    """

    def __init__(self, project, name, leave_out=None):
        if not isinstance(name, str) or not store.PLAIN.fullmatch(name):
            raise ValueError("a check record's name is a plain id, not %r" % (name,))
        self.project, self.name, self.leave_out = Path(project), name, leave_out
        self.path = self.project / SPARK_FOLDER / (name + ".json")

    def save(self, inputs, at, answer):
        """Write the record of `answer` ({status, data, lines}) at the time `at` (with its zone), over `inputs`, hashed now.
        OSError when it cannot: the project is not there, `.spark` is no folder, or the write fails. ValueError for no
        inputs or an input that is not plain (`is_plain_input`): a programmer's error, as a name that is no plain id is."""
        if not inputs or not all(is_plain_input(each) for each in inputs):
            raise ValueError("a check record's inputs are plain paths in the project, not %r" % (inputs,))
        (self.project / SPARK_FOLDER).mkdir(exist_ok=True)  # no parents: a mistyped project is never made
        record = {"schema": SCHEMA, "op": self.name, "at": at, "inputs": list(inputs),
                  "inputs_sha256": inputs_sha256(self.project, inputs, self.leave_out),
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
        why = shape_problem(record, self.name)
        if why:
            return CheckRecord(self.name, outcomes.NOT_CHECKED, why)
        try:
            now = inputs_sha256(self.project, record["inputs"], self.leave_out)
        except OSError as failed:
            return CheckRecord(self.name, outcomes.NOT_CHECKED, WHY_UNREADABLE % type(failed).__name__)
        return CheckRecord(self.name, outcomes.RECORDED, None, record["at"], now == record["inputs_sha256"],
                           record["status"], record["data"], record["lines"], record["inputs"])
# --- end MVP ---
