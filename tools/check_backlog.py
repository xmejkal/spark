#!/usr/bin/env python3
"""
W14 and the WIP limits on the spark project's open items (P102a; docs/2026-10-05-backlog-in-github-design.md §8).
Run by tools/check_commit.py at every push. With no network or no gh it says it could not look, and passes: the gate
must work offline.
"""

import json
import re
import subprocess
import sys

OWNER, TITLE = "xmejkal", "spark"
#: The stages that carry a limit (§3); Idea and Done carry none.
LIMITS = {"Discovery": 1, "Design": 1, "Ready": 3, "Build": 1, "Review": 1}
IN_FLIGHT = ("Discovery", "Design", "Build", "Review")
MOST_IN_FLIGHT = 2


def _section(body, name):
    body = (body or "").replace("\r\n", "\n")  # GitHub keeps a body's line endings as they were typed
    match = re.search(r"^### %s[ \t]*\n(.*?)(?=^### |\Z)" % re.escape(name), body, re.S | re.M)
    text = match.group(1).strip() if match else ""
    return "" if text == "_No response_" else text


def _name(entry):
    return "#%s %s" % (entry["content"].get("number"), entry["content"].get("title", ""))


def problems(items):
    """
    Every sentence the gate fails on: an item with no Needed by or no slice, and a broken WIP limit. Epics carry no limit;
    a task (a plan's step, a sub-issue of its story) rides on its story and is not judged on its own.
    """
    said, by_stage = [], {}
    for entry in items:
        status = entry.get("status")
        if status == "Done" or "task" in (entry.get("labels") or []):
            continue
        if "epic" not in (entry.get("labels") or []):
            by_stage.setdefault(status, []).append(entry)
        if not _section(entry["content"].get("body"), "Needed by"):
            said.append("%s: no `Needed by` — W14: an item names the design that needs it" % _name(entry))
        if not entry.get("slice"):
            said.append("%s: on no slice of the story map" % _name(entry))
    for stage, limit in LIMITS.items():
        held = by_stage.get(stage, [])
        if len(held) > limit:
            said.append("%s holds %d (%s) — its limit is %d: finish one before starting another"
                        % (stage, len(held), ", ".join("#%s" % e["content"].get("number") for e in held), limit))
    flying = [e for stage in IN_FLIGHT for e in by_stage.get(stage, [])]
    if len(flying) > MOST_IN_FLIGHT:
        said.append("%d in flight (%s) — at most %d: one being worked, one waiting"
                    % (len(flying), ", ".join("#%s" % e["content"].get("number") for e in flying), MOST_IN_FLIGHT))
    return said


def _gh(*args):
    return json.loads(subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60, check=True).stdout)


def fetch():
    """
    (the spark project's items, None), or (None, why) when gh or the network could not be reached. A project that gh
    can list but cannot find is a LookupError: the check must never quietly stop looking.
    """
    try:
        projects = _gh("project", "list", "--owner", OWNER, "--format", "json")["projects"]
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as unreachable:
        return None, type(unreachable).__name__
    number = next((p["number"] for p in projects if p["title"] == TITLE), None)
    if number is None:
        raise LookupError("no project titled %r under %s — the board cannot be checked" % (TITLE, OWNER))
    try:
        return _gh("project", "item-list", str(number), "--owner", OWNER, "--format", "json", "--limit", "500")["items"], None
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as unreachable:
        return None, type(unreachable).__name__


def main():
    try:
        items, why = fetch()
    except LookupError as gone:
        print("  backlog: %s" % gone)
        return 1
    if items is None:
        print("  backlog: skipped — gh or the network could not be reached (%s)" % why)
        return 0
    said = problems(items)
    print("  backlog: %d open, %s" % (sum(1 for e in items if e.get("status") != "Done"),
                                      "the limits hold" if not said else "%d problem(s)" % len(said)))
    for sentence in said:
        print("    " + sentence)
    return 1 if said else 0


if __name__ == "__main__":
    sys.exit(main())
