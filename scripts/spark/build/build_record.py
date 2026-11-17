"""
The record of a project's last build (P825): `check_spine.py --keep` writes `<project>/.spark/build.json`, and `flow.py
show` reads it to say whether the build is done, failed or older than requirements.json. A library for `kept_files` and
the flow area.
"""

import hashlib
import json
import os
import shutil
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
#: The files whose sha256 the record holds: spark replaces one only when it is still the bytes spark wrote. A footprint's `.tsx` is not here.
OWN_FILES = ("board.tsx",)
#: Where the previous version of a replaced file is kept, relative to the project.
PREVIOUS_DIR = Path(".spark") / "previous"


def sha256_of(path):
    """The sha256 of the file at `path`, as hex. OSError when it cannot be read."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class BuildRecordStore:
    """
    Store: the record of a project's last build, `<project>/.spark/build.json`: `{"schema", "status", "stages": [{name,
    status}], "missing_facts", "requirements", "requirements_sha256", "written_sha256", "at"}`. `write` adds the schema and the time, from
    `clock` (SystemClock), through `writer` (TextFileWriter); a test gives a fake of each. `read` raises store.StoreError
    for a file that is no JSON object, and OSError for one it cannot open.
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
        except ValueError as broken:
            raise store.StoreError("%s is not JSON (%s): build again with --keep", self.path, broken, code=records_codes.RECORD_FILE_BROKEN)
        if not isinstance(record, dict):
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


class PreviousVersionFiles:
    """
    Adapter: the previous version of a file spark replaced (P874), `<project>/.spark/previous/<name>.txt`. One path for each
    name, so a newer copy lands on the older one and only the newest stays. The name ends in `.txt` so that tscircuit never
    reads it as a board. The copy is made beside the path and put in place whole.
    """

    def __init__(self, project):
        self.project = Path(project)

    def path_of(self, name):
        """Where the previous version of the file `name` is kept."""
        return self.project / PREVIOUS_DIR / (name + ".txt")

    def keep(self, file):
        """Copy `file` to its previous-version path and return the path. OSError when it cannot be kept."""
        path = self.path_of(Path(file).name)
        staged = path.with_name(path.name + ".new")
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copyfile(file, staged)
            os.replace(staged, path)
        except OSError:
            staged.unlink(missing_ok=True)
            raise
        return path
# --- end MVP ---
