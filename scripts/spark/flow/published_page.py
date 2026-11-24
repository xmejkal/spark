"""
The record of the Artifact a project's page is published as (P829 PR 4): `.spark/page.json`, the id only. `flow.py page
--artifact` writes it, and `show_flow.reading_of` reads it for `data.artifact` (P1060). It lives apart from the page's
writer, so `show_flow` imports it with no cycle.
"""

import json
import re
from pathlib import Path

from spark.records import store

# --- MVP ---
#: The record of the Artifact the page is published as (P829 PR 4), from the project's folder: its id only, never a path.
PUBLISHED_FILE = Path(".spark") / "page.json"
#: An Artifact's id (its slug) as the Artifact tools answer it: a UUID in lower case. Its own pattern, not the request id's
#: (run_request imports the build, which imports this module). Read with `fullmatch`: `$` alone lets a trailing newline in.
ARTIFACT_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class PublishedPageStore:
    """Store: `.spark/page.json` of one project, the id of the Artifact its page is published as (P829 PR 4). `read`
    gives the id, or None when there is no record or spark cannot use it; `write` keeps `{"artifact": id}`, the id only,
    through the store's one atomic write. An OSError from the write is the caller's."""

    def __init__(self, project):
        self.path = Path(project) / PUBLISHED_FILE

    def read(self):
        """The id the record holds, or None: no record, no JSON object, or an id that is no Artifact id."""
        try:
            held = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        artifact = held.get("artifact") if isinstance(held, dict) else None
        return artifact if isinstance(artifact, str) and ARTIFACT_PATTERN.fullmatch(artifact) else None

    def write(self, artifact):
        """Keep `artifact`, an Artifact id, as the project's published page."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        store.write_file(self.path, json.dumps({"artifact": artifact}) + "\n")
# --- end MVP ---
