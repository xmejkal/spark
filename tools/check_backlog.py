#!/usr/bin/env python3
"""
W14 and the WIP limits on the spark project's open items (P102a; docs/2026-10-05-backlog-in-github-design.md §3 and
§8; raised on 2026-10-06 at the PO's word, P146, and again that evening to two per working stage and four in flight).
Run by tools/check_commit.py at every push. With no network or no gh it says it could not look, and passes: the gate
must work offline. A board it reads but whose tasks' parent stories it cannot is not offline: it counts every task as
riding on its story and says so in a sentence, which fails the push — a look that was only partial must not read as a
pass (W1).
"""

import json
import re
import subprocess
import sys

OWNER, TITLE = "xmejkal", "spark"
#: The stages that carry a limit (§3); Idea and Done carry none. Every working stage takes 2, the PO's call of
#: 2026-10-06 evening (P146); Ready is a queue, not work, and stays at 5.
LIMITS = {"Discovery": 2, "Design": 2, "Ready": 5, "Build": 2, "Review": 2}
IN_FLIGHT = ("Discovery", "Design", "Build", "Review")
#: Where an epic is the work itself; from Build on, its stories carry the limit.
UPSTREAM = ("Discovery", "Design")
#: The most cards the four working stages may hold together: the PO's call of 2026-10-06 evening, after the first day
#: at the cap of 3 (P146). Four stages of two would hold eight, so this is the limit that binds first.
MOST_IN_FLIGHT = 4
#: What fetch() puts before an error's name in its second value when the items were read and only their parents were
#: not; main() hears it and tells problems() (P146).
PARENTS_UNREAD = "parents:"


def _section(body, name):
    body = (body or "").replace("\r\n", "\n")  # GitHub keeps a body's line endings as they were typed
    match = re.search(r"^### %s[ \t]*\n(.*?)(?=^### |\Z)" % re.escape(name), body, re.S | re.M)
    text = match.group(1).strip() if match else ""
    return "" if text == "_No response_" else text


def _name(entry):
    return "#%s %s" % (entry["content"].get("number"), entry["content"].get("title", ""))


def counts(entry):
    """
    Whether an open card counts against the limits: a task rides on its story, so it does not count — unless it has no
    parent story at all, when it is a card of its own (P146); an epic counts only in Discovery and Design, where it is
    the work itself — from Build on, its stories carry the limit. board.py reads the same rule.
    """
    labels = entry.get("labels") or []
    if "task" in labels:
        return entry.get("parent") is None
    return "epic" not in labels or entry.get("status") in UPSTREAM


def problems(items, bin_items=(), parents_read=True):
    """
    Every sentence the gate fails on: an item with no Needed by or no slice, and a broken WIP limit. An epic counts only
    in Discovery and Design; a task (a plan's step, a sub-issue of its story) rides on its story and is not judged on
    its own — unless it has no parent story, when it is a card like any other (counts()). `parents_read` is False when
    the tasks' parents could not be looked up: every task then rides, and the first sentence says so instead of
    guessing. `bin_items` is the bin's board, accepted and not read yet.
    """
    said, by_stage = [], {}
    for entry in items:
        status = entry.get("status")
        rides = "task" in (entry.get("labels") or []) and (entry.get("parent") is not None or not parents_read)
        if status == "Done" or rides:
            continue  # a riding task is its story's; a parentless one is judged like any card
        if counts(entry):
            by_stage.setdefault(status, []).append(entry)
        if not _section(entry["content"].get("body"), "Needed by"):
            said.append("%s: no `Needed by` — W14: an item names the design that needs it" % _name(entry))
        if not entry.get("slice"):
            said.append("%s: on no slice of the story map" % _name(entry))
    for stage, limit in LIMITS.items():
        held = by_stage.get(stage, [])
        if len(held) > limit:
            said.append("%s holds %d (%s) — its limit is %d: %s"
                        % (stage, len(held), ", ".join("#%s" % e["content"].get("number") for e in held), limit,
                           "the PO moves one back to Idea" if stage == "Ready" else "finish one before starting another"))
    flying = [e for stage in IN_FLIGHT for e in by_stage.get(stage, [])]
    if len(flying) > MOST_IN_FLIGHT:
        said.append("%d in flight (%s) — at most %d: finish one before starting another"
                    % (len(flying), ", ".join("#%s" % e["content"].get("number") for e in flying), MOST_IN_FLIGHT))
    if not parents_read and any("task" in (e.get("labels") or []) for e in items if e.get("status") != "Done"):
        said.insert(0, "tasks' parent stories could not be read — every task counted as riding on a story")
    return said


def _gh(*args):
    return json.loads(subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60, check=True).stdout)


PARENTS_QUERY = "query { repository(owner: \"%s\", name: \"%s\") { %s } }"


def parents(numbers):
    """
    ({task number: its parent issue's number or None}, None), or ({}, why) when GitHub could not be asked. One call for
    all the tasks.
    """
    if not numbers:
        return {}, None
    fields = " ".join("t%d: issue(number: %d) { parent { number } }" % (n, n) for n in numbers)
    try:
        answer = _gh("api", "graphql", "-f", "query=" + PARENTS_QUERY % (OWNER, TITLE, fields))
        found = answer["data"]["repository"]
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError) as unreachable:
        return {}, type(unreachable).__name__
    return {n: ((found.get("t%d" % n) or {}).get("parent") or {}).get("number") for n in numbers}, None


def fetch():
    """
    (the spark project's items, None), or (None, why) when gh or the network could not be reached. A project that gh
    can list but cannot find is a LookupError: the check must never quietly stop looking. Each item carries "parent",
    the number of the story it is a sub-issue of, asked for the open tasks alone — the one kind of card a parent changes
    the counting of. When only that question fails, the items come back whole with PARENTS_UNREAD and the error's name
    as the second value, and every parent is None.
    """
    try:
        projects = _gh("project", "list", "--owner", OWNER, "--format", "json")["projects"]
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as unreachable:
        return None, type(unreachable).__name__
    number = next((p["number"] for p in projects if p["title"] == TITLE), None)
    if number is None:
        raise LookupError("no project titled %r under %s — the board cannot be checked" % (TITLE, OWNER))
    try:
        items = _gh("project", "item-list", str(number), "--owner", OWNER, "--format", "json", "--limit", "500")["items"]
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as unreachable:
        return None, type(unreachable).__name__
    tasks = [e["content"]["number"] for e in items if "task" in (e.get("labels") or []) and e.get("status") != "Done"]
    found, why = parents(tasks)
    for entry in items:
        entry["parent"] = found.get(entry["content"].get("number"))
    return items, None if why is None else PARENTS_UNREAD + why


def main():
    try:
        items, why = fetch()
    except LookupError as gone:
        print("  backlog: %s" % gone)
        return 1
    if items is None:
        print("  backlog: skipped — gh or the network could not be reached (%s)" % why)
        return 0
    said = problems(items, parents_read=not (why or "").startswith(PARENTS_UNREAD))
    print("  backlog: %d open, %s" % (sum(1 for e in items if e.get("status") != "Done"),
                                      "the limits hold" if not said else "%d problem(s)" % len(said)))
    for sentence in said:
        print("    " + sentence)
    return 1 if said else 0


if __name__ == "__main__":
    sys.exit(main())
