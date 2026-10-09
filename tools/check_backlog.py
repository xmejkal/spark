#!/usr/bin/env python3
"""
W14 and the WIP limits on the spark project's open items (P102a; docs/2026-10-05-backlog-in-github-design.md §3 and
§8; raised on 2026-10-06 at the PO's word, P146, and again that evening to two per working stage and four in flight).
A card is asked for its Needed by and slice from Ready on — the commitment — not in Idea, Discovery or Design (P146).
A card that waits on someone is asked since when, in any open stage: a Waiting on with no Waiting since is named (P146).
One card at a time may carry the label `expedite`, the PO's lane past a limit: it lets its stage, and the flight, hold
one over; two open cards labelled so are named (P146, decision 4 of docs/2026-10-06-process-design.md).
Run by tools/check_commit.py at every push. With no network or no gh it says it could not look, and passes: the gate
must work offline. So does a look that was only partial — the board read, but not its tasks' parent stories: every task
is counted as riding on its story, a line says so with the cause, and the push goes through (W1: said, never read as
checked).
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
#: From the commitment on (Ready, Build, Review) a card carries its Needed by and slice; in Idea, Discovery and Design
#: it decides whether to build, and the PO's order into Ready is what commits. P146, docs/2026-10-06-process-design.md:
#: the skeptic pass's item 6 ("the gate checks a slice from Ready on, not from Discovery on") and §1 ("Your order into
#: Ready commits"). A card with no Status, or one the gate does not know, is not asked either, like Idea.
JUDGED = ("Ready", "Build", "Review")
#: Where an epic is the work itself; from Build on, its stories carry the limit.
UPSTREAM = ("Discovery", "Design")
#: The most cards the four working stages may hold together: the PO's call of 2026-10-06 evening, after the first day
#: at the cap of 3 (P146). Four stages of two would hold eight, so this is the limit that binds first.
MOST_IN_FLIGHT = 4
#: The one lane past a limit, on the PO's word only (decision 4): a card labelled so may take its stage, and the flight,
#: one over its limit. One card at a time — the gate fails on two (P146).
EXPEDITE = "expedite"
#: What fetch() puts in a task's "parent" when GitHub could not be asked who it is. It is not None, so counts() and
#: problems() let the task ride on a story they cannot name — a check must not count a card whose parent it could not see
#: — and main() says so, with the cause (P146).
PARENT_UNREAD = "unread"


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
    parent story at all, when it is a card of its own (P146), and one whose parent could not be asked (PARENT_UNREAD)
    rides; an epic counts only in Discovery and Design, where it is the work itself — from Build on, its stories carry
    the limit. board.py reads the same rule.
    """
    labels = entry.get("labels") or []
    if "task" in labels:
        return entry.get("parent") is None
    return "epic" not in labels or entry.get("status") in UPSTREAM


def problems(items, bin_items=()):
    """
    Every sentence the gate fails on: a card with no Needed by or no slice — asked from Ready on, the commitment
    (JUDGED), not in Idea, Discovery or Design — a card that waits on someone (any name) with no Waiting since, in any
    open stage, two open cards labelled expedite (whatever their stage), and a broken WIP limit. A stage, or the flight,
    may hold one over its limit while exactly one of the cards it holds is the expedite. An epic counts only in
    Discovery and Design; a task (a plan's step, a sub-issue of its story) rides on its story and is not judged on its
    own — unless it has no parent story, when it is a card like any other (counts()). A Done card is not judged at all.
    `bin_items` is the bin's board, accepted and not read yet.
    """
    said, by_stage = [], {}
    for entry in items:
        status = entry.get("status")
        rides = "task" in (entry.get("labels") or []) and entry.get("parent") is not None
        if status == "Done" or rides:
            continue  # a riding task is its story's; a parentless one is judged like any card
        if counts(entry):
            by_stage.setdefault(status, []).append(entry)
        if status in JUDGED:
            if not _section(entry["content"].get("body"), "Needed by"):
                said.append("%s: no `Needed by` — W14: an item names the design that needs it" % _name(entry))
            if not entry.get("slice"):
                said.append("%s: on no slice of the story map" % _name(entry))
        if entry.get("waiting on") and not entry.get("waiting since"):
            said.append("%s: waits on %s since nobody knows — set Waiting since" % (_name(entry), entry["waiting on"]))
    rushed = [e for e in items if e.get("status") != "Done" and EXPEDITE in (e.get("labels") or [])]
    if len(rushed) > 1:
        said.append("%d cards labelled expedite (%s) — one at a time, on the PO's word"
                    % (len(rushed), ", ".join("#%s" % e["content"].get("number") for e in rushed)))

    def over(held, limit):
        """Whether `held` breaks `limit`: one over is allowed while exactly one of its cards is the expedite."""
        allowance = 1 if sum(1 for e in held if EXPEDITE in (e.get("labels") or [])) == 1 else 0
        return len(held) > limit + allowance

    for stage, limit in LIMITS.items():
        held = by_stage.get(stage, [])
        if over(held, limit):
            said.append("%s holds %d (%s) — its limit is %d: %s"
                        % (stage, len(held), ", ".join("#%s" % e["content"].get("number") for e in held), limit,
                           "the PO moves one back to Idea" if stage == "Ready" else "finish one before starting another"))
    flying = [e for stage in IN_FLIGHT for e in by_stage.get(stage, [])]
    if over(flying, MOST_IN_FLIGHT):
        said.append("%d in flight (%s) — at most %d: finish one before starting another"
                    % (len(flying), ", ".join("#%s" % e["content"].get("number") for e in flying), MOST_IN_FLIGHT))
    return said


def _gh(*args):
    return json.loads(subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60, check=True).stdout)


def parents(tasks):
    """
    ({(repository, number): its parent issue's number or None}, None), or ({}, why) when it could not be asked: gh failed
    or printed no JSON, the answer has nothing for a task, or a task has no usable repository or number to be asked by.
    `tasks` are (repository "owner/name", issue number) pairs: a project may hold issues of several repositories, and a
    number means nothing without its repository. One call for all of them — a selection per repository (aliased r0, r1,
    … in the order they first appear), a field per issue (t<number>) inside it.
    """
    if not tasks:
        return {}, None
    asked = {}
    for repository, number in tasks:
        asked.setdefault(repository, []).append(number)
    groups = [("r%d" % index, repository, numbers) for index, (repository, numbers) in enumerate(asked.items())]
    try:
        selections = []
        for alias, repository, numbers in groups:
            owner, name = repository.split("/", 1)
            fields = " ".join("t%d: issue(number: %d) { parent { number } }" % (n, n) for n in numbers)
            selections.append("%s: repository(owner: %s, name: %s) { %s }" % (alias, json.dumps(owner), json.dumps(name), fields))
        found = _gh("api", "graphql", "-f", "query=query { %s }" % " ".join(selections))["data"]
        return {(repository, number): (found[alias]["t%d" % number]["parent"] or {}).get("number")
                for alias, repository, numbers in groups for number in numbers}, None
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError, AttributeError) as unreachable:
        return {}, type(unreachable).__name__


def fetch():
    """
    (the spark project's items, None), or (None, why) when gh or the network could not be reached. A project that gh
    can list but cannot find is a LookupError: the check must never quietly stop looking. An open task carries "parent",
    the number of the story it is a sub-issue of (None when it has none). The gate asks for no other item's parent — a
    parent changes how a task counts and nothing else — so theirs is None here, unlike board.to_items(), which gives
    every issue its parent. When only that question fails the items still come back, as (items, why), with every open
    task's parent PARENT_UNREAD: a why that comes with items is the parents', one that comes without is the whole look's.
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
    open_tasks = [(e["content"].get("repository"), e["content"].get("number")) for e in items
                  if "task" in (e.get("labels") or []) and e.get("status") != "Done"]
    found, why = parents(open_tasks)
    if why:
        found = {task: PARENT_UNREAD for task in open_tasks}
    for entry in items:
        entry["parent"] = found.get((entry["content"].get("repository"), entry["content"].get("number")))
    return items, why


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
    if why:
        print("  backlog: tasks' parent stories could not be read (%s) — every task counted as riding on a story" % why)
    return 1 if said else 0


if __name__ == "__main__":
    sys.exit(main())
