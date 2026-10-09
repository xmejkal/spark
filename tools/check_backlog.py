#!/usr/bin/env python3
"""
W14 and the WIP limits on the spark project's open items (P102a; docs/2026-10-05-backlog-in-github-design.md §3 and
§8; raised on 2026-10-06 at the PO's word, P146, and again that evening to two per working stage and four in flight).
A card is asked for its Needed by and slice from Ready on — the commitment — not in Idea, Discovery or Design (P146).
A card that waits on someone is asked since when, in any open stage and a riding task too: a Waiting on with no Waiting
since is named (P146).
One card at a time may carry the label `expedite`, the PO's lane past a limit: it lets its working stage, and the flight,
hold one over, and Ready none — it enters Build; two open cards labelled so are named (P146, decision 4 of
docs/2026-10-06-process-design.md).
The bin's board is read too, for three things: its cards in a working stage fly in the same total as spark's (a session
labelled `bench` sits outside it), the lane is one lane across both boards, and a card of its that waits on someone is
asked since when like any (the spec, §1: "The bin's desk cards count in the same three. A bench session is your hands, so
it sits outside them"). They fill none of spark's stages and are asked for no Needed by or slice (P146).
Run by tools/check_commit.py at every push. With no network or no gh it says it could not look, and passes: the gate
must work offline. So does a look that was only partial — the board read, but not its tasks' parent stories (every task
is counted as riding on its story) or not the bin's board (spark's cards are counted alone): a line says so with the
cause, and the push goes through (W1: said, never read as checked). A bin board that was read is said too: the summary
line carries its open count.
"""

import argparse
import json
import re
import subprocess
import sys

OWNER, TITLE = "xmejkal", "spark"
#: The bin's project. Its cards in a working stage fly in the same total as spark's, and the expedite lane is one lane
#: across both boards (the spec §1: "The bin's desk cards count in the same three"); they fill none of spark's stages.
BIN_TITLE = "the bin"
#: What problems() marks a card of the bin's board with, so a sentence names it apart from spark's: `bin #12`, not `#12`.
BIN_BOARD = "bin"
#: What main() and the status say when the bin's board could not be read: spark's cards were counted alone, and the bin's
#: expedite and waits were not checked either. A could-not-look, not a failure — said with its cause, and the push goes
#: through (W1).
BIN_UNREAD = "the bin's board could not be read (%s) — its cards were not counted or checked"
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
#: The one lane past a limit, on the PO's word only (decision 4): a card labelled so may take its working stage, and the
#: flight, one over its limit. One card at a time — the gate fails on two (P146).
EXPEDITE = "expedite"
#: The bin's label for a bench session — the PO's own hands at the bench, which sits outside the limits (the spec, §1: "A
#: bench session is your hands, so it sits outside them"). A bin card labelled so does not fly in the total (P146).
BENCH = "bench"
#: What fetch() puts in a task's "parent" when GitHub could not be asked who it is. It is not None, so counts() and
#: problems() let the task ride on a story they cannot name — a check must not count a card whose parent it could not see
#: — and main() says so, with the cause (P146).
PARENT_UNREAD = "unread"


def _section(body, name):
    body = (body or "").replace("\r\n", "\n")  # GitHub keeps a body's line endings as they were typed
    match = re.search(r"^### %s[ \t]*\n(.*?)(?=^### |\Z)" % re.escape(name), body, re.S | re.M)
    text = match.group(1).strip() if match else ""
    return "" if text == "_No response_" else text


def _ref(entry):
    """A card as a sentence names it: `#12`, or `bin #12` for one of the bin's (problems() marks those, BIN_BOARD)."""
    return "%s#%s" % (BIN_BOARD + " " if entry.get("board") == BIN_BOARD else "", entry["content"].get("number"))


def _name(entry):
    return "%s %s" % (_ref(entry), entry["content"].get("title", ""))


def rides(entry):
    """
    Whether a card is a task riding on its story (or on a parent nobody could ask, PARENT_UNREAD): it is counted nowhere
    itself, asked for no Needed by or slice, and not the lane's holder — but its wait is asked, like every open card's.
    """
    return "task" in (entry.get("labels") or []) and entry.get("parent") is not None


def counts(entry):
    """
    Whether an open card counts against the limits: a task rides on its story, so it does not count — unless it has no
    parent story at all or only a closed one (open_parent), when it is a card of its own (P146), and one whose parent
    could not be asked (PARENT_UNREAD) rides; an epic counts only in Discovery and Design, where it is the work itself —
    from Build on, its stories carry the limit. board.py reads the same rule.
    """
    labels = entry.get("labels") or []
    if "task" in labels:
        return entry.get("parent") is None
    return "epic" not in labels or entry.get("status") in UPSTREAM


def problems(items, bin_items=()):
    """
    Every sentence the gate fails on: a card with no Needed by or no slice — asked from Ready on, the commitment
    (JUDGED), not in Idea, Discovery or Design — a card that waits on someone (any name) with no Waiting since, in any
    open stage and a riding task included (the status lists every open wait, so the gate asks for every open date), two
    open cards labelled expedite (whatever their stage or board), and a broken WIP limit. A working stage, or the
    flight, may hold one over its limit while exactly one of the cards it holds is the expedite; Ready, a queue the
    expedite never enters, may not. An epic counts only in Discovery and Design; a task (a plan's step, a sub-issue of
    its story) rides on its open story and is judged only on its wait — unless it has no open parent story, when it is a card
    like any other (counts()). A Done card is not judged at all.
    `bin_items` is the bin's board, or None when it could not be read (main() says so; nothing is said here). Its cards
    in a working stage that count (counts()) fly in the same total as spark's — all but a `bench` session, which sits
    outside the limits — and its expedite is the same lane; a card of its that waits on someone is asked since when, like
    any. They fill none of spark's stages and are asked for no Needed by or slice. A sentence names them `bin #12`.
    """
    said, by_stage = [], {}
    bin_cards = [dict(entry, board=BIN_BOARD) for entry in (bin_items or ())]  # copies: the caller's cards stay unmarked
    for entry in [*items, *bin_cards]:
        status = entry.get("status")
        if status == "Done":
            continue
        # The bin's cards fill none of spark's stages and are asked for no Needed by or slice; the wait is asked of both.
        from_spark = entry.get("board") != BIN_BOARD
        # The wait is asked of every open card, a riding task included: the status lists them all (board._waits).
        if entry.get("waiting on") and not entry.get("waiting since"):
            said.append("%s: waits on %s since nobody knows — set Waiting since" % (_name(entry), entry["waiting on"]))
        if rides(entry):
            continue  # a riding task is its story's; a parentless one is judged like any card
        if from_spark and counts(entry):
            by_stage.setdefault(status, []).append(entry)
        if from_spark and status in JUDGED:
            if not _section(entry["content"].get("body"), "Needed by"):
                said.append("%s: no `Needed by` — W14: an item names the design that needs it" % _name(entry))
            if not entry.get("slice"):
                said.append("%s: on no slice of the story map" % _name(entry))
    # A story and the task riding on it, both labelled, are one rush: the task is counted nowhere itself.
    rushed = [e for e in [*items, *bin_cards]
              if e.get("status") != "Done" and not rides(e) and EXPEDITE in (e.get("labels") or [])]
    if len(rushed) > 1:
        said.append("%d cards labelled expedite (%s) — one at a time, on the PO's word"
                    % (len(rushed), ", ".join(_ref(e) for e in rushed)))

    def over(held, limit):
        """Whether `held` breaks `limit`: one over is allowed while exactly one of its cards is the expedite."""
        allowance = 1 if sum(1 for e in held if EXPEDITE in (e.get("labels") or [])) == 1 else 0
        return len(held) > limit + allowance

    for stage, limit in LIMITS.items():
        held = by_stage.get(stage, [])
        # The expedite enters Build, so it lends a working stage a place; Ready is a queue it never enters: none.
        if (over(held, limit) if stage in IN_FLIGHT else len(held) > limit):
            said.append("%s holds %d (%s) — its limit is %d: %s"
                        % (stage, len(held), ", ".join(_ref(e) for e in held), limit,
                           "the PO moves one back to Idea" if stage == "Ready" else "finish one before starting another"))
    flying = [e for stage in IN_FLIGHT for e in by_stage.get(stage, [])]
    # A bench session is the PO's hands and sits outside the limits (the spec, §1): a bin card labelled so does not fly.
    flying += [e for e in bin_cards if e.get("status") in IN_FLIGHT and counts(e) and BENCH not in (e.get("labels") or [])]
    if over(flying, MOST_IN_FLIGHT):
        said.append("%d in flight (%s) — at most %d: finish one before starting another"
                    % (len(flying), ", ".join(_ref(e) for e in flying), MOST_IN_FLIGHT))
    return said


def open_parent(parent):
    """
    The number of the story a task rides on, from GitHub's `parent { number closed }` (None when it has none), else None
    for a closed parent too: a finished story holds no place in a limit, so its task is the open work and counts as a card
    of its own (P146). board.py reads the same rule, so the status and the gate cannot disagree about who rides.
    """
    if not parent or parent.get("closed"):
        return None
    return parent.get("number")


def _gh(*args):
    return json.loads(subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60, check=True).stdout)


def _cause(error):
    """
    Why gh could not be asked, as a could-not-run line says it: the first line gh wrote on stderr that says anything
    ("To get started with GitHub CLI, please run:  gh auth login" — gh's own line, as it prints it), else the exception's name — a missing gh, a timeout
    with nothing said, an answer that was no JSON. board.py's _gh says gh's first line the same way (P146 council, C2).
    """
    said = getattr(error, "stderr", None) or ""
    if isinstance(said, bytes):  # a timed-out run's output comes back as bytes whatever text= said
        said = said.decode(errors="replace")
    return next((line.strip() for line in said.splitlines() if line.strip()), type(error).__name__)


def parents(tasks):
    """
    ({(repository, number): its parent issue's number or None, a closed parent being none (open_parent)}, None), or
    ({}, why) when it could not be asked: gh failed
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
            fields = " ".join("t%d: issue(number: %d) { parent { number closed } }" % (n, n) for n in numbers)
            selections.append("%s: repository(owner: %s, name: %s) { %s }" % (alias, json.dumps(owner), json.dumps(name), fields))
        found = _gh("api", "graphql", "-f", "query=query { %s }" % " ".join(selections))["data"]
        return {(repository, number): open_parent(found[alias]["t%d" % number]["parent"])
                for alias, repository, numbers in groups for number in numbers}, None
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError, AttributeError) as unreachable:
        return {}, _cause(unreachable)


def _items(number):
    """The items of the project numbered `number` under OWNER, as gh prints them."""
    return _gh("project", "item-list", str(number), "--owner", OWNER, "--format", "json", "--limit", "500")["items"]


def fetch():
    """
    (the spark project's items, the bin project's items, why, the bin's why), or (None, None, why, None) when gh or the
    network could not be reached. A spark project that gh can list but cannot find is a LookupError: the check must never
    quietly stop looking. The bin's board is read for the flight total, the lane and its waits alone, so its failing — no project
    titled BIN_TITLE, or a listing that errors — costs nothing else: bin_items is None and the bin's why says what went
    wrong, for main() to say. An open task of either board carries "parent", the number of the story it is a sub-issue of
    (None when it has none or it is closed, open_parent()), asked in ONE call for both boards. The gate asks for no other item's parent — a parent
    changes how a task counts and nothing else — so theirs is None here, unlike board.to_items(), which gives every issue
    its parent. When only that question fails the items still come back, with every open task's parent PARENT_UNREAD:
    the why that comes with items is the parents', one that comes without is the whole look's.
    """
    try:
        projects = _gh("project", "list", "--owner", OWNER, "--format", "json")["projects"]
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as unreachable:
        return None, None, _cause(unreachable), None
    number = next((p["number"] for p in projects if p["title"] == TITLE), None)
    if number is None:
        raise LookupError("no project titled %r under %s — the board cannot be checked" % (TITLE, OWNER))
    try:
        items = _items(number)
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as unreachable:
        return None, None, _cause(unreachable), None
    bin_items, bin_why = None, "no project titled %r under %s" % (BIN_TITLE, OWNER)
    bin_number = next((p["number"] for p in projects if p["title"] == BIN_TITLE), None)
    if bin_number is not None:
        try:
            bin_items, bin_why = _items(bin_number), None
        except (OSError, subprocess.SubprocessError, ValueError, KeyError) as unreachable:
            bin_why = _cause(unreachable)
    cards = items + (bin_items or [])
    open_tasks = [(e["content"].get("repository"), e["content"].get("number")) for e in cards
                  if "task" in (e.get("labels") or []) and e.get("status") != "Done"]
    found, why = parents(open_tasks)
    if why:
        found = {task: PARENT_UNREAD for task in open_tasks}
    for entry in cards:
        entry["parent"] = found.get((entry["content"].get("repository"), entry["content"].get("number")))
    return items, bin_items, why, bin_why


#: What `--help` says the gate checks; the limits are filled in from LIMITS and MOST_IN_FLIGHT, so the help cannot drift
#: from the numbers the gate holds a board to.
CHECKS = """\
The pre-push gate over the two GitHub Projects boards, spark's and the bin's, read through the
PO's own gh login. tools/check_commit.py runs it at every push; it takes no arguments.

It fails on:
  - a stage over its WIP limit: %(limits)s;
  - more than %(most)d cards in flight: Discovery, Design, Build and Review together, across both
    boards;
  - two open cards labelled `expedite`. One card at a time may carry it, on the PO's word: its
    working stage, and the flight, may then hold one over their limit. Ready never;
  - a card that waits on someone (Waiting on) with no Waiting since, in any open stage, on either
    board, a task riding on its story included;
  - a card of spark's in Ready, Build or Review with no `Needed by` section or on no slice: the
    commitment starts at Ready, so Idea, Discovery and Design are not asked.

How cards count: an epic counts in Discovery and Design only, where it is the work itself; from
Build on its stories carry the limit. A task under an open story rides on it and counts nowhere;
a task with no parent story, or only a closed one, is a card of its own. The bin's cards in a
working stage fly in the same total as spark's (a bin card labelled `bench` sits outside it) and
fill none of spark's stages.
"""
#: The exit codes `--help` names (W1: a look that could not run says so, and is never read as checked).
EXIT_CODES = """\
exit codes:
  0  the limits hold — or could-not-run: gh or the network could not be reached, said with its
     cause, and the limits were not checked. A partial look (the tasks' parent stories or the
     bin's board unread) is said with its cause too.
  1  a problem, each named on a line of its own — or no project titled "spark" under %(owner)s.
  2  an argument the gate does not take.
"""


def _parser():
    """The gate's command line: no arguments; `--help` says what it checks and what its exit codes mean, and asks gh nothing."""
    return argparse.ArgumentParser(
        prog="check_backlog.py", formatter_class=argparse.RawDescriptionHelpFormatter,
        description=CHECKS % {"limits": ", ".join("%s %d" % limit for limit in LIMITS.items()), "most": MOST_IN_FLIGHT},
        epilog=EXIT_CODES % {"owner": OWNER})


def main(argv=()):
    """
    The gate, printed; its exit code. `argv` is the command line's arguments — none by default, so check_commit.py, which
    imports this and calls main() with a commit in its own sys.argv, is never read as asking the gate anything.
    """
    _parser().parse_args(list(argv))
    try:
        items, bin_items, why, bin_why = fetch()
    except LookupError as gone:
        print("  backlog: %s" % gone)
        return 1
    if items is None:
        print("  backlog: could-not-run — gh or the network could not be reached (%s); the limits were not checked" % why)
        return 0
    said = problems(items, bin_items)
    summary = "  backlog: %d open, %s" % (sum(1 for e in items if e.get("status") != "Done"),
                                         "the limits hold" if not said else "%d problem(s)" % len(said))
    if bin_items is not None:
        summary += "; the bin: %d open" % sum(1 for e in bin_items if e.get("status") != "Done")
    print(summary)
    for sentence in said:
        print("    " + sentence)
    if why:
        print("  backlog: tasks' parent stories could not be read (%s) — every task counted as riding on a story" % why)
    if bin_items is None:
        print("  backlog: " + BIN_UNREAD % bin_why)
    return 1 if said else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
