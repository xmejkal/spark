"""
The project's brief: what `.spark/project.json` says, read on each call.

    must     lines the design must meet (strings; anything else is dropped)
    prefer   vendors to research in, lower-cased, or None when the brief does not say
    sellers  where the person buys, lower-cased, or None when the brief does not say

`Brief.from_project` gives an empty brief for a missing file, a non-file, bad JSON or JSON that is not an object.
An unreadable file raises OSError, and deeply nested JSON raises RecursionError, as the old readers did.
"""

import json
from dataclasses import dataclass
from pathlib import Path


# --- MVP ---
def _names(value):
    """A non-empty list of strings as a lower-cased tuple, else None."""
    if isinstance(value, list) and value and all(isinstance(each, str) for each in value):
        return tuple(each.lower() for each in value)
    return None


# --- MVP ---
@dataclass(frozen=True)
class Brief:
    """Value: what the brief of one project says (see the top of this file)."""

    must: tuple = ()
    prefer: tuple = None
    sellers: tuple = None

    @classmethod
    def from_project(cls, project):
        """The brief of this project folder (None reads as empty), from `.spark/project.json`."""
        if not project:
            return cls()
        path = Path(project) / ".spark" / "project.json"
        if not path.is_file():
            return cls()
        try:
            data = json.loads(path.read_text())
        except ValueError:
            return cls()
        if not isinstance(data, dict):
            return cls()
        must = data.get("must")
        return cls(
            must=tuple(each for each in must if isinstance(each, str)) if isinstance(must, list) else (),
            prefer=_names(data.get("prefer")),
            sellers=_names(data.get("sellers")),
        )
