#!/usr/bin/env python3
"""
The tools spark depends on: what is here, what is missing, and the choices. This is what /spark:setup runs:

    tools.py --status [--project DIR]                  the picture: [ok  ] [????] [off ] [!   ]
    tools.py --install NAME... [--project DIR]         install the named tools, their needs first
    tools.py --on NAME | --off NAME                    turn an integration on (and install it) or off
    tools.py --use ROLE=TOOL | --pin NAME=VERSION      point a job at another tool; pin a version

A choice is written to the person's file, or to the project's with --project (--personal overrides). The library is
`spark/records/tool_finder.py` (P719): one merged list of the tools, `find`, `status`, `plan` and `install`.
(Not to be confused with the repository's `tools/` folder, which holds the developers' own tools.)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN  # noqa: E402
from spark.core.text_guards import flat_line  # noqa: E402
from spark.records import records_codes  # noqa: E402
from spark.records.tool_finder import (DOWNLOADS, PERSONAL, PROJECT_FILE, ToolProblem, choose, install,  # noqa: E402
                                       merged, new_entry_problem, off_sentence, pin, plan, run_checked, status,
                                       to_install, use)


MARKS = {"ok": "[ok  ]", "missing": "[????]", "off": "[off ]", "person": "[!   ]"}


def print_status(project, personal):
    """The picture, one row per line; returns how many rows read missing — a broken entry counts, though nothing installs it."""
    print(flat_line("  spark's tools — personal: %s · project: %s\n", personal or PERSONAL, Path(project) / PROJECT_FILE if project else "(none)"))
    rows = status(project, personal)
    for state, label, text in rows:
        print(flat_line("  %s %-17s %s", MARKS[state], label, text))
    missing = to_install(project, personal)
    if missing:
        print("\n  %d to install: %s" % (len(missing), " ".join(missing)))
    return sum(1 for state, _, _ in rows if state == "missing")


def main(argv=None, run=None):
    parser = argparse.ArgumentParser(prog="tools.py", description="The tools spark depends on: what is here, "
                                     "what is missing, and the choices — what /spark:setup runs.")
    does = parser.add_mutually_exclusive_group(required=True)
    does.add_argument("--status", action="store_true")
    does.add_argument("--install", nargs="+", metavar="NAME")
    does.add_argument("--on", metavar="NAME")
    does.add_argument("--off", metavar="NAME")
    does.add_argument("--use", metavar="ROLE=TOOL")
    does.add_argument("--pin", metavar="NAME[.FIELD]=VERSION", help="e.g. tscircuit.core=0.0.2700 (FIELD defaults to version)")
    does.add_argument("--new", metavar="NAME=JSON", help="describe a tool of your own, e.g. "
                      'my-sim=\'{"kind": "path", "exe": "my-sim", "meets": ["wokwi-project"]}\'')
    parser.add_argument("--project", type=Path, help="the project: read its .spark/tools.json, and write a choice there")
    parser.add_argument("--personal", action="store_true", help="write a choice to the person's file even with --project")
    parser.add_argument("--dry-run", action="store_true", help="with --install: print each command and run nothing")
    args = parser.parse_args(argv)
    project = args.project
    where = PERSONAL if (args.personal or not project) else Path(project) / PROJECT_FILE
    scope = "user" if where == PERSONAL else "project"
    try:
        if args.status:
            return EXIT_COULD_NOT_RUN if print_status(project, None) else EXIT_OK
        if args.install and args.dry_run:
            for step in plan(args.install, project, None):
                if step["problem"]:
                    print(flat_line("  cannot:    %s", step["problem"]))
                elif step["here"]:
                    print(flat_line("  already here: %s (%s)", step["name"], step["here"]))
                else:
                    print(flat_line("  would run: %s%s", " ".join(step["argv"]), "   ← chosen by this project's .spark/tools.json"
                        " — check it before you say yes" if step["from_project"] else ""))
                    if step["fetch"]:
                        print(flat_line("             keeps it as %s if its sha256 is %s...", DOWNLOADS / step["fetch"][0], step["fetch"][2][:12]))
                    if step["from_project"]:
                        print("             (from .spark/tools.json)")
        elif args.install:
            for argv_ran in install(args.install, project, None, run):
                print(flat_line("  ran: %s", " ".join(argv_ran)))
        elif args.on:
            choose([args.on, "on"], True, where)
            if merged(project)["tools"].get(args.on, {}).get("on") is False:
                raise ToolProblem("%s is still off: %s", args.on, off_sentence(args.on, project), code=records_codes.TOOL_OFF)
            for argv_ran in install([args.on], project if scope == "project" else None, None, run):
                print(flat_line("  ran: %s", " ".join(argv_ran)))
            print(flat_line("  %s is on (%s)", args.on, where))
        elif args.off:
            entry = merged(project)["tools"].get(args.off, {})
            choose([args.off, "on"], False, where)
            if entry.get("kind") == "mcp" and entry.get("mcp"):
                try:
                    (run or run_checked)(["claude", "mcp", "remove", "--scope", scope, args.off])
                except (OSError, subprocess.CalledProcessError):
                    print(flat_line("  %s was not registered with Claude Code at %s scope — nothing to remove", args.off, scope))
            elif entry.get("owner") == "spark":
                print(flat_line("  %s is spark's own server and stays loaded with the plugin — disable it in /mcp", args.off))
            print(flat_line("  %s is off (%s)", args.off, where))
        elif args.use:
            role, _, tool_name = args.use.partition("=")
            print(flat_line("  %s → %s (%s)", role, tool_name, use(role, tool_name, project if scope == "project" else None, None)))
        elif args.new:
            name, _, text = args.new.partition("=")
            try:
                entry = json.loads(text)
            except ValueError as broken:
                raise ToolProblem("%s: the entry is not JSON (%s)", name, broken, code=records_codes.TOOL_ENTRY_BROKEN)
            problem = new_entry_problem(entry)
            if problem:
                raise ToolProblem("%s: %s — nothing written", name, problem, code=records_codes.TOOL_ENTRY_BROKEN)
            print(flat_line("  %s written (%s); point a job at it: /spark:setup use <role>=%s", name, choose([name], entry, where), name))
        elif args.pin:
            target, _, value = args.pin.partition("=")
            name, field, written = pin(target, value, project, where)
            print(flat_line("  %s %s pinned to %s (%s); to install it: tools.py --install %s%s",
                            name, field, value, written, name, " --project %s" % project if project else ""))
    except ToolProblem as problem:
        print("tools.py: %s" % problem, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if (args.on or args.off) and merged(project)["tools"].get(args.on or args.off, {}).get("kind") == "mcp":
        print("  Claude Code loads MCP servers when a session starts: restart it for this to take effect.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
