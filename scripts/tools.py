#!/usr/bin/env python3
"""
The tools spark depends on, found from one merged list (P82, docs/2026-10-03-tools-design.md).

spark's dependencies were decided in seven places, each with its own lookup and its own error
message. Now one list says what each tool is for, how to find it, how to install it and which
contract it meets: spark's defaults in data/tools.json, the person's in
~/.local/share/spark/tools.json, the project's in .spark/tools.json — merged entry by entry and
field by field, the project winning. Every script asks `find`; nothing else names a tool.

A missing tool is a ToolProblem whose sentence says what installs it. Nothing here installs.
(Not to be confused with the repository's `tools/` folder, which holds the developers' own tools.)
"""

import importlib.util
import json
import shutil
import sys
from collections import namedtuple
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import boards  # noqa: E402

PLUGIN = SCRIPTS.parent
DEFAULTS = PLUGIN / "data" / "tools.json"
SPARK_HOME = Path.home() / ".local" / "share" / "spark"
PERSONAL = SPARK_HOME / "tools.json"
DOWNLOADS = SPARK_HOME / "downloads"
PROJECT_FILE = Path(".spark") / "tools.json"
#: Keys of a tools file that are not tools.
RESERVED = ("roles", "contracts")
#: The install managers tried in order, each with the program that has to be there for it to apply.
MANAGERS = (("npm", "npm"), ("pip", "python3"), ("brew", "brew"), ("download", None))  # a download needs only spark

Tool = namedtuple("Tool", "name role entry command")


class ToolProblem(Exception):
    """A tool spark cannot use — missing, refused, turned off, or a list it cannot read. The message is the whole sentence."""


def _read(path):
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text())
    except ValueError as broken:
        raise ToolProblem("%s is not JSON (%s) — fix it or delete it" % (path, broken))
    if not isinstance(data, dict):
        raise ToolProblem("%s holds a %s; a tools file is an object" % (path, type(data).__name__))
    return data


def merged(project=None, personal=None):
    """The three layers as one list: tools merged field by field, roles key by key, the project winning."""
    lists = {"tools": {}, "roles": {}, "contracts": {}}
    paths = [DEFAULTS, Path(personal) if personal else PERSONAL]
    if project:
        paths.append(Path(project) / PROJECT_FILE)
    for path in paths:
        data = _read(path)
        for key, value in data.items():
            if key.startswith("//") or key in RESERVED:
                continue
            if not isinstance(value, dict):
                raise ToolProblem("%s: the entry %r is not an object" % (path, key))
            lists["tools"].setdefault(key, {}).update(value)
        lists["roles"].update(data.get("roles") or {})
        if path == DEFAULTS:
            lists["contracts"].update(data.get("contracts") or {})
    return lists


def install_line(entry):
    """The one command that installs this tool here, with its version filled in — or None."""
    install = entry.get("install") or {}
    for manager, needs in MANAGERS:
        if manager in install and (needs is None or shutil.which(needs)):
            return install[manager].format(version=entry.get("version", ""), core=entry.get("core", ""))
    return None


def locate(entry, project):
    """The command that runs this tool, by its kind — or None when it is not here."""
    kind = entry.get("kind", "path")
    if kind == "python":
        return [sys.executable] if importlib.util.find_spec(entry["module"]) else None
    if kind == "download":
        path = DOWNLOADS / entry["file"]
        return [str(path)] if path.is_file() else None
    if kind == "bundled":
        path = PLUGIN / entry["file"]
        return [str(path)] if path.is_file() else None
    exe = entry["exe"]
    if kind == "npm" and project:
        for directory in boards.walk_up(Path(project)):
            local = directory / "node_modules" / ".bin" / exe
            if local.is_file():
                return [str(local)]
    found = shutil.which(exe)
    if found:
        return [found]
    for also in entry.get("also") or []:
        path = Path(also).expanduser()
        if path.is_file():
            return [str(path)]
    return None


def version_note(name, reported, field="version", project=None, personal=None):
    """'' when the reported version is the one the list states for this field, else the one line to print."""
    stated = merged(project, personal)["tools"].get(name, {}).get(field)
    if not stated or reported in (None, "unknown version") or str(reported) == str(stated):
        return ""
    return "; spark was measured on %s %s %s" % (name, field, stated)


def find(name, project=None, personal=None):
    """A role or a tool's name -> the Tool to run, or a ToolProblem saying why not and what to do."""
    lists = merged(project, personal)
    role = name if name in lists["roles"] else None
    tool_name = lists["roles"].get(name, name)
    entry = lists["tools"].get(tool_name)
    if entry is None:
        raise ToolProblem("%s: no tool called %r in any tools file" % (name, tool_name))
    contract = lists["contracts"].get(role) if role else None
    if contract and contract not in (entry.get("meets") or []):
        raise ToolProblem("%s: %s does not say it meets %r, so this step will not use it"
                          % (role, tool_name, contract))
    if entry.get("on") is False:
        raise ToolProblem("%s is turned off — turn it on: /spark:setup add %s" % (tool_name, tool_name))
    if entry.get("kind", "path") in ("path", "npm") and not entry.get("exe"):
        raise ToolProblem("%s: no way to find it — the entry names no exe" % tool_name)
    command = locate(entry, project)
    if command is None:
        line = install_line(entry)
        raise ToolProblem("%s (%s) is not installed — install: %s"
                          % (role or tool_name, tool_name, line or "see its entry in %s" % DEFAULTS))
    return Tool(tool_name, role, entry, command)
