"""
The project's brief: what `.spark/project.json` says, read on each call.

    goal     what the person wants, in their words (a string), or None when the brief does not say (P777)
    must     lines the design must meet (strings; anything else is dropped)
    prefer   vendors to research in, lower-cased, or None when the brief does not say
    sellers  where the person buys, lower-cased, or None when the brief does not say
    problem  None, or why a file that exists could not give a brief: PROBLEM_BAD_JSON, PROBLEM_NOT_OBJECT or PROBLEM_MUST_NOT_LIST
             (P345). The other fields are the empty brief then, apart from `prefer` and `sellers` when only `must` was wrong.

`Brief.from_project` gives an empty brief for a missing file or a non-file, and an empty brief with `problem` set for bad JSON,
JSON that is not an object, or a `must` that is not a list.
An unreadable file raises OSError, and deeply nested JSON raises RecursionError, as the old readers did.
"""

import json
from dataclasses import dataclass
from pathlib import Path

#: Why a brief that exists is no brief (Brief.problem). A missing file, a directory and a FIFO are "no brief" and give no problem.
PROBLEM_BAD_JSON, PROBLEM_NOT_OBJECT, PROBLEM_MUST_NOT_LIST = "bad-json", "not-object", "must-not-list"


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
    goal: str = None
    sellers: tuple = None
    problem: str = None

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
            return cls(problem=PROBLEM_BAD_JSON)
        if not isinstance(data, dict):
            return cls(problem=PROBLEM_NOT_OBJECT)
        must, goal = data.get("must"), data.get("goal")
        return cls(
            goal=goal if isinstance(goal, str) else None,
            must=tuple(each for each in must if isinstance(each, str)) if isinstance(must, list) else (),
            prefer=_names(data.get("prefer")),
            sellers=_names(data.get("sellers")),
            problem=PROBLEM_MUST_NOT_LIST if "must" in data and not isinstance(must, list) else None,
        )

    @classmethod
    def read(cls, project):
        """(the brief, why it cannot be read) of this project folder (P1142). `why` is None, the `problem` word, or the text of
        an OSError or a RecursionError that `from_project` raises. The brief is the empty one when it cannot be read."""
        try:
            brief = cls.from_project(project)
        except (OSError, RecursionError) as unread:
            return cls(), str(unread)
        return brief, brief.problem

    @property
    def has_goal(self):
        """True when the goal is a text with a character other than white space (P1142)."""
        return bool(self.goal and self.goal.strip())


# --- MVP ---
@dataclass(frozen=True)
class UnnamedMust:
    """Value: the must lines of the brief that no passed scenario named (image_evidence finds them, board_look reads them). `lines` is a list. `caveats` are the not-checked sentences for what could not be compared (a log that cannot say, a brief that cannot be read)."""

    lines: list
    caveats: tuple = ()
# --- end MVP ---
