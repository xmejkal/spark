#!/usr/bin/env python3
"""
A design, loaded once: the requirements file, the project it belongs to, the board, the parts as
instances, and the rules.

Three scripts loaded a design on their own — `emit_board.main`, `check_all`'s placeholder list
and `check_spine` — and the copies disagreed in the ways copies do. `emit_board.main` resolved
the project on one line and passed the unresolved `--project` flag to the rules lookup seventy
lines later, so the documented invocation (inside the project, no flag) emitted every power
trace unsized, exit 0, and blamed the reader for it. `check_spine` resolved the project from the
current directory and the toolchain from the requirements file, so from anywhere else it could
not find the project's own parts. `check_all` copied the load-and-tag loop under
`except Exception: return ()`. And all three read the requirements JSON outside any `try`: a
malformed file was a traceback and exit 1, which in a three-valued tool reads as "problems
found". Sprint audit 2026-09-29, claims A2, A4, A8, A10.

So: one place. A design is loaded FROM ITS FILE. The project is the flag if given, else the
nearest project up from the file's own directory — not from wherever the command was typed.
Everything that can be wrong with the input is a `DesignError`, which callers turn into
`could-not-run`; nothing here raises anything else on bad input.

This module resolves and reads. It does not name components or signals for the netlist — that is
`emit_board`'s, because the name is decided by what the emitted file needs — and it does not
assign pins, because only the generator needs that.
"""

import json
import sys
from collections import namedtuple
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import boards  # noqa: E402
import parts as parts_library  # noqa: E402

#: What `load` returns. `parts` are the requested instances: each a copy of its record, with
#: `_instance` set when the requirements named it.
Design = namedtuple("Design", "path project requirements board parts rules")

#: Where a project keeps the rules its checks and its generator both read.
RULES_PATH = Path(".spark") / "rules.json"


class DesignError(Exception):
    """The input cannot be loaded, and this is why. Always a sentence, never a traceback."""


def read(path):
    """The requirements file as a dict, or a DesignError saying what is wrong with it."""
    path = Path(path)
    if not path.is_file():
        raise DesignError("no requirements at %s" % path)
    try:
        wanted = json.loads(path.read_text())
    except ValueError as broken:
        raise DesignError("%s is not JSON: %s" % (path, broken)) from broken
    except OSError as broken:
        raise DesignError("%s could not be read: %s" % (path, broken)) from broken
    if not isinstance(wanted, dict):
        raise DesignError("%s holds a %s; a requirements file is an object with `parts`"
                          % (path, type(wanted).__name__))
    return wanted


def project_for(path, project=None):
    """
    The project a requirements file belongs to.

    `--project` wins. Otherwise the nearest project UP FROM THE FILE — a design lives with its
    parts and its rules, and it does not stop belonging to them when the command is typed from
    `/tmp`.
    """
    if project:
        return Path(project).resolve()
    try:
        return boards.project_root(Path(path).resolve().parent)
    except boards.BoardError as broken:
        raise DesignError(str(broken)) from broken


def requested_parts(wanted):
    """
    The parts list, normalised to (part_id, instance name or None).

    An entry is either a bare id — `"l9110s-module"` — or an object naming the instance:
    `{"part": "tactile-button", "name": "BtnForward"}`. Five buttons without names is not a design
    anyway: you cannot write firmware against "button three".
    """
    entries = []
    for index, entry in enumerate(wanted.get("parts") or []):
        if isinstance(entry, dict):
            if not entry.get("part"):
                raise DesignError("parts[%d] names no `part`: %s" % (index, json.dumps(entry)))
            entries.append((entry["part"], entry.get("name")))
        elif isinstance(entry, str):
            entries.append((entry, None))
        else:
            raise DesignError("parts[%d] is a %s; an entry is a part id or {part, name}"
                              % (index, type(entry).__name__))
    return entries


def parts_of(wanted, project):
    """Each requested part as an instance: its record, plus `_instance` when it was named."""
    part_list = []
    try:
        for part_id, instance in requested_parts(wanted):
            part = dict(parts_library.load(part_id, project))
            if instance:
                part["_instance"] = instance
            part_list.append(part)
    except parts_library.PartError as broken:
        raise DesignError(str(broken)) from broken
    return part_list


def rules_in(project):
    """
    The project's rules, or an empty dict when it has none. Absent is not an error — `init`
    writes it. Present and unreadable IS one: a rules file nobody can parse must not quietly
    become "no rules", because the generated board would then say every width is unjustified
    while the file that justifies them sits right there.
    """
    path = Path(project) / RULES_PATH
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except (ValueError, OSError) as broken:
        raise DesignError("%s could not be read: %s" % (path, broken)) from broken


def load(path, project=None, board_id=None):
    """A design from its requirements file. Every way the input is wrong is a DesignError."""
    wanted = read(path)
    root = project_for(path, project)
    try:
        board = boards.load(root, board_id or wanted.get("board"))
    except boards.BoardError as broken:
        raise DesignError(str(broken)) from broken
    return Design(Path(path), root, wanted, board, parts_of(wanted, root), rules_in(root))
