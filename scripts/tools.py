#!/usr/bin/env python3
"""
The tools spark depends on: what is here, what is missing, and the choices. This is what /spark:setup runs:

    tools.py --status [--project DIR]                  the picture: [ok  ] [????] [off ] [!   ]
    tools.py --install NAME... [--project DIR]         install the named tools, their needs first
    tools.py --on NAME | --off NAME                    turn an integration on (and install it) or off
    tools.py --use ROLE=TOOL | --pin NAME=VERSION      point a job at another tool; pin a version

A choice is written to the person's file, or to the project's with --project (--personal overrides). The library is
`spark/records/tool_finder.py` (P719): one merged list of the tools, `find`, `status`, `plan` and `install`; and
`spark/records/tool_choices.py` (P783): the choice's file, a tool turned on or off, a tool of the person's own written.
(Not to be confused with the repository's `tools/` folder, which holds the developers' own tools.)
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.core.outcomes import EXIT_OK, EXIT_COULD_NOT_RUN  # noqa: E402
from spark.core.text_guards import flat_line  # noqa: E402
from spark.records.tool_choices import choice_file, is_mcp_server, turn_off, turn_on, write_new_tool  # noqa: E402
from spark.records.tool_finder import (DOWNLOADS, PERSONAL, PROJECT_FILE, ToolError, install, pin, plan,  # noqa: E402
                                       status, to_install, use)


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
    where, scope = choice_file(project, args.personal)
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
            for argv_ran in turn_on(args.on, project, where, scope, run):
                print(flat_line("  ran: %s", " ".join(argv_ran)))
            print(flat_line("  %s is on (%s)", args.on, where))
        elif args.off:
            note = turn_off(args.off, project, where, scope, run)
            if note:
                print("  %s" % note)
            print(flat_line("  %s is off (%s)", args.off, where))
        elif args.use:
            role, _, tool_name = args.use.partition("=")
            print(flat_line("  %s → %s (%s)", role, tool_name, use(role, tool_name, project if scope == "project" else None, None)))
        elif args.new:
            name, written = write_new_tool(args.new, where)
            print(flat_line("  %s written (%s); point a job at it: /spark:setup use <role>=%s", name, written, name))
        elif args.pin:
            target, _, value = args.pin.partition("=")
            name, field, written = pin(target, value, project, where)
            print(flat_line("  %s %s pinned to %s (%s); to install it: tools.py --install %s%s",
                            name, field, value, written, name, " --project %s" % project if project else ""))
    except ToolError as problem:
        print("tools.py: %s" % problem, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    if (args.on or args.off) and is_mcp_server(args.on or args.off, project):
        print("  Claude Code loads MCP servers when a session starts: restart it for this to take effect.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
