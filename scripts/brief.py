"""
The project's brief: what `.spark/project.json` says, read once.

    must     lines the design must meet (strings; anything else is dropped)
    prefer   vendors to research in, lower-cased, or None when the brief does not say
    sellers  where the person buys, lower-cased, or None when the brief does not say

`Brief.from_project` never raises: a missing file, bad JSON or a wrong shape reads as an empty brief.
"""

import json
from dataclasses import dataclass, field
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

    must: list = field(default_factory=list)
    prefer: tuple = None
    sellers: tuple = None

    @classmethod
    def from_project(cls, project):
        """The brief of this project folder (None reads as empty), from `.spark/project.json`."""
        if not project:
            return cls()
        try:
            data = json.loads((Path(project) / ".spark" / "project.json").read_text())
        except (OSError, ValueError):
            return cls()
        if not isinstance(data, dict):
            return cls()
        must = data.get("must")
        return cls(
            must=[each for each in must if isinstance(each, str)] if isinstance(must, list) else [],
            prefer=_names(data.get("prefer")),
            sellers=_names(data.get("sellers")),
        )
