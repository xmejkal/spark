"""
The record of a project's last build (P825): `check_spine.py --keep` writes `<project>/.spark/build.json`, and `flow.py
show` reads it to say whether the build is done, failed or older than requirements.json. A library for `kept_files` and
the flow area.
"""

import hashlib
import json
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


def sha256_of(path):
    """The sha256 of the file at `path`, as hex. OSError when it cannot be read."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class BuildRecordStore:
    """
    Store: the record of a project's last build, `<project>/.spark/build.json`: `{"schema", "status", "stages": [{name,
    status}], "missing_facts", "requirements", "requirements_sha256", "at"}`. `write` adds the schema and the time, from
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

    def write(self, record):
        """Write `record` with the schema first and the time last. Returns the path. OSError when it cannot be written."""
        self.writer.write(self.path, json.dumps(dict({"schema": SCHEMA}, **record, at=stamp(self.clock.now())), indent=1) + "\n")
        return self.path
# --- end MVP ---
