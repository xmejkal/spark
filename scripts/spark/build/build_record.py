"""
The record of a project's last build (P825): `check_spine.py --keep` writes `<project>/.spark/build.json`, and `flow.py
show` reads it to say whether the build is done, failed or older than requirements.json. A library for `kept_files` and
the flow area.
"""

import contextlib
import hashlib
import json
import os
from pathlib import Path

from spark.records import records_codes, store
from spark.core.clock import SystemClock
from spark.core.replies import TextFileWriter
from spark.core.zone_time import stamp

# --- MVP ---
#: Where the record is kept, relative to the project.
BUILD_RECORD_FILE = Path(".spark") / "build.json"
#: The record's schema. A reader refuses no other yet: it reads the keys it knows.
SCHEMA = 1
#: The record's key for the sha256 of each file spark wrote (P874), by its name in the project.
WRITTEN_SHA256 = "written_sha256"
#: The record's key for whether the last build wrote `dist/` (P816): false means a `dist/` there is an earlier build's.
DIST_WRITTEN = "dist_written"
#: What a reader of `dist/` says when the last build did not write it (P816): the build's time.
EARLIER_DIST = "the last build, %s, did not write dist/: build again with check_spine.py --keep before you rely on this circuit"
#: The files whose sha256 the record holds: spark replaces one only when it is still the bytes spark wrote. A footprint's `.tsx` is not here.
OWN_FILES = ("board.tsx",)
#: Where the previous version of a replaced file is kept, relative to the project.
PREVIOUS_DIR = Path(".spark") / "previous"
#: The end of the name of a file made beside its target before it is put in place.
STAGE_SUFFIX = ".new"
#: What a stage that is in the way says: the file's path and what to do (P874).
STAGE_IN_THE_WAY = "%s is in the way: delete it if it is not yours"


def sha256_of(path):
    """The sha256 of the file at `path`, as hex. OSError when it cannot be read."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_build_record(record):
    """Whether `record` has the shape a reader may use (P886): an object whose `stages`, when there, is a list of objects, whose
    `missing_facts` is a list and whose `requirements` is a string. A key that is missing or null is fine."""
    if not isinstance(record, dict):
        return False
    stages, facts, named = record.get("stages"), record.get("missing_facts"), record.get("requirements")
    return (stages is None or (isinstance(stages, list) and all(isinstance(stage, dict) for stage in stages))) \
        and (facts is None or isinstance(facts, list)) \
        and (named is None or isinstance(named, str))


class BuildRecordStore:
    """
    Store: the record of a project's last build, `<project>/.spark/build.json`: `{"schema", "status", "stages": [{name,
    status, and code when the stage did not end ok (P977)}], "missing_facts", "requirements", "requirements_sha256", "written_sha256", "dist_written", "at"}`. `write` adds the schema and the time, from
    `clock` (SystemClock), through `writer` (TextFileWriter); a test gives a fake of each. `read` raises store.StoreError
    for a file that is no JSON or is no build record (`is_build_record`), and OSError for one it cannot open.
    """

    def __init__(self, project, writer=None, clock=None):
        self.path = Path(project) / BUILD_RECORD_FILE
        self.writer, self.clock = writer or TextFileWriter(), clock or SystemClock()

    def read(self):
        """The record as a dict, or None when the project has none yet."""
        if not self.path.is_file():
            return None
        try:
            record = json.loads(self.path.read_text(encoding="utf-8"))
        except (ValueError, RecursionError) as broken:  # a record nested too deep is no JSON a reader can use
            raise store.StoreError("%s is not JSON (%s): build again with --keep", self.path, broken, code=records_codes.RECORD_FILE_BROKEN)
        if not is_build_record(record):
            raise store.StoreError("%s is no build record: build again with --keep", self.path, code=records_codes.RECORD_FILE_BROKEN)
        return record

    def written_sha256(self):
        """The sha256 of each file spark wrote, `{name: hex}`: empty when there is no record, no such key, a key that is no map, or
        a record that cannot be read. A name that is missing is unknown, and spark leaves that file alone."""
        try:
            held = (self.read() or {}).get(WRITTEN_SHA256)
        except (store.StoreError, OSError):
            return {}
        return {name: digest for name, digest in held.items() if isinstance(digest, str)} if isinstance(held, dict) else {}

    def write(self, record):
        """Write `record` with the schema first and the time last. Returns the path. OSError when it cannot be written."""
        self.writer.write(self.path, json.dumps(dict({"schema": SCHEMA}, **record, at=stamp(self.clock.now())), indent=1) + "\n")
        return self.path


def earlier_dist(project):
    """The sentence that names `project`'s `dist/` as one the last build did not write (P816), or None: no record, one it
    cannot read, one without the key (it says nothing), a build that wrote `dist/`, or no `dist/`."""
    try:
        record = BuildRecordStore(project).read() or {}
    except (OSError, store.StoreError):
        return None
    if record.get(DIST_WRITTEN) is False and (Path(project) / "dist").is_dir():
        return EARLIER_DIST % record.get("at")
    return None


class StageTakenError(FileExistsError):
    """Error: a stage's name is already taken by a file, a link or a folder; `filename` is the stage's path, and it says so."""

    def __str__(self):
        return STAGE_IN_THE_WAY % self.filename


class StagedFile:
    """
    Adapter: a copy of `source` made beside its target under the name `staged` (P874), then put in place whole by
    `commit`. `make` creates the stage exclusively and follows no link, so a file or a link already at that name is
    never written through or removed: it raises OSError. `remove` takes away only a stage this object made. `from_bytes`
    makes a stage from bytes in hand (P875): it has no source.
    """

    def __init__(self, source, staged, data=None):
        self.source, self.staged, self.data, self.made = Path(source) if source is not None else None, Path(staged), data, False

    @classmethod
    def from_bytes(cls, staged, data):
        """A stage that holds `data` once made."""
        return cls(None, staged, data)

    def make(self):
        """Create the stage and copy the bytes of the source into it. OSError when the name is taken or the copy fails."""
        try:
            descriptor = os.open(self.staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)  # O_EXCL also refuses a link at the name
        except FileExistsError as taken:
            raise StageTakenError(taken.errno, taken.strerror, str(self.staged)) from None
        self.made = True
        with os.fdopen(descriptor, "wb") as out:
            out.write(self.source.read_bytes() if self.data is None else self.data)

    def commit(self, target):
        """Replace `target` with the stage in one step. OSError leaves both as they were."""
        os.replace(self.staged, target)
        self.made = False

    def remove(self):
        """Remove the stage when this object made it and it is still there; no error."""
        if self.made:
            self.made = False
            with contextlib.suppress(OSError):
                self.staged.unlink()


class PreviousVersionFiles:
    """
    Adapter: the previous version of a file spark replaced (P874), `<project>/.spark/previous/<name>.txt`. One path for each
    name, so a newer copy lands on the older one and only the newest stays. The name ends in `.txt` so that tscircuit never
    reads it as a board. `stage` copies it beside the path and `commit` puts it in place, so a caller can swap its own file
    in between and commit only when that worked.
    """

    def __init__(self, project):
        self.project = Path(project)

    def path_of(self, name):
        """Where the previous version of the file `name` is kept."""
        return self.project / PREVIOUS_DIR / (name + ".txt")

    def stage(self, file):
        """The StagedFile that holds the bytes of `file` beside its previous-version path. OSError when it cannot be made."""
        path = self.path_of(Path(file).name)
        if path.parent.is_symlink():
            raise OSError("%s is a link, so the previous version is not written through it" % path.parent)
        path.parent.mkdir(parents=True, exist_ok=True)
        copy = StagedFile(file, path.with_name(path.name + STAGE_SUFFIX))
        try:
            copy.make()
        except OSError:
            copy.remove()
            raise
        return copy

    def commit(self, copy):
        """Put the staged copy at its previous-version path and return the path. When that fails, the copy stays where it
        is and its path is returned, so the old bytes are not lost."""
        path = self.path_of(copy.source.name)
        try:
            copy.commit(path)
        except OSError:
            copy.made = False  # it stays: it holds the old bytes
            return copy.staged
        return path
# --- end MVP ---
