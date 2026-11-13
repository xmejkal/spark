"""
The choices a person makes on the tools lists, the steps /spark:setup runs on them: the file a choice is written to, a
tool turned on (and installed) or off, and a tool of the person's own described. `tool_finder` holds the lists and the
finding; this module writes the choices through its `choose` and `install`. Each function returns what the CLI
`scripts/tools.py` prints, and a refusal is a `ToolError` with its records code.
"""

import json
import subprocess
from pathlib import Path

from spark.core.text_guards import flat_line
from spark.records import records_codes
from spark.records import tool_finder
from spark.records.tool_finder import ToolError, choose, install, merged, new_entry_problem, off_sentence, run_checked


def choice_file(project, personal):
    """-> (the file a choice is written to, Claude Code's scope for it): the person's file and `user` with no project
    or with `personal`, else the project's .spark/tools.json and `project`. It reads `tool_finder.PERSONAL` when called,
    so a test that points it elsewhere is obeyed."""
    if personal or not project:
        return tool_finder.PERSONAL, "user"
    return Path(project) / tool_finder.PROJECT_FILE, "project"


def turn_on(name, project, where, scope, run=None):
    """Write `on` for the tool into `where`, then install it; return the commands run. A tool another file still turns
    off is a `tool_off` refusal, raised before anything installs."""
    choose([name, "on"], True, where)
    if merged(project)["tools"].get(name, {}).get("on") is False:
        raise ToolError("%s is still off: %s", name, off_sentence(name, project), code=records_codes.TOOL_OFF)
    return install([name], project if scope == "project" else None, None, run)


def turn_off(name, project, where, scope, run=None):
    """-> the sentence to print before the tool is said off, or None. Writes `off` for the tool into `where` and removes
    an MCP server from Claude Code at `scope`; the sentence says a server was not registered, or is spark's own."""
    entry = merged(project)["tools"].get(name, {})
    choose([name, "on"], False, where)
    if entry.get("kind") == "mcp" and entry.get("mcp"):
        try:
            (run or run_checked)(["claude", "mcp", "remove", "--scope", scope, name])
        except (OSError, subprocess.CalledProcessError):
            return flat_line("%s was not registered with Claude Code at %s scope — nothing to remove", name, scope)
    elif entry.get("owner") == "spark":
        return flat_line("%s is spark's own server and stays loaded with the plugin — disable it in /mcp", name)
    return None


def write_new_tool(spec, where):
    """Write a tool of the person's own, `NAME=JSON`, into `where`; -> (name, the file written). An entry that is not
    JSON, or one spark could not find, is a `tool_entry_broken` refusal, and nothing is written."""
    name, _, text = spec.partition("=")
    try:
        entry = json.loads(text)
    except ValueError as broken:
        raise ToolError("%s: the entry is not JSON (%s)", name, broken, code=records_codes.TOOL_ENTRY_BROKEN)
    problem = new_entry_problem(entry)
    if problem:
        raise ToolError("%s: %s — nothing written", name, problem, code=records_codes.TOOL_ENTRY_BROKEN)
    return name, choose([name], entry, where)


def is_mcp_server(name, project):
    """True for an MCP server, which Claude Code loads only when a session starts."""
    return merged(project)["tools"].get(name, {}).get("kind") == "mcp"
