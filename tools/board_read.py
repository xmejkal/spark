#!/usr/bin/env python3
"""
The one reader of the GitHub Projects boards (P811), shared by the pre-push gate (check_backlog.py) and the status and
day-close (board.py). It asks GitHub's GraphQL API for what the limits and the status need and nothing more: one query
per 100 items of a board, page after page until the whole board is read (P168), each field by its name. A page costs 1
point of the 5,000 an hour that GitHub allows the account, and every answer carries what it cost (rateLimit), so a
caller can say what a read spent. Stdlib only; it imports neither of its two callers.

    from board_read import read_board, to_items, unread
    project = read_board(2, ask)            # ask(*gh_args) -> the answer as JSON; spent=[] collects the costs
    cards, short = to_items(project), unread("the spark board", project)

Every failure to read — gh missing, refused, timed out, an answer that is no JSON or not the board's shape — is one
error, Unreadable, whose message is the cause as a could-not-run line says it (cause()).
"""

import subprocess

OWNER = "xmejkal"
#: How a board read in part is said: "holds 12 items, 10 were read" (unread()).
SHORT = "holds %d items, %d were read"
#: How a board whose items held no issue at all is said (unread()): judging it would be "0 open, the limits hold" over
#: a board nobody read (W1), so it is a partial read too.
NO_CARDS = "holds %d items and none of them was read as an issue"
#: The most pages read_board() turns, counted as pages asked, not items read: 50 pages of 100 items. A hasNextPage that
#: never falls — an empty page with a cursor — cannot hold a push or a session start forever; the board is then short.
MOST_PAGES = 50
#: What every answer says it cost, so a caller can say what a read spent (P811).
RATE = "rateLimit{cost remaining limit}"
#: The projects of OWNER by title: the gate finds its boards by their titles, not their numbers.
PROJECTS = "query($login:String!){%s user(login:$login){projectsV2(first:100){nodes{number title}}}}" % RATE
#: One page of a board (P168, P811): the project's id and status updates (board.py's close posts to the id and reads its
#: day-closes from the updates), and 100 items, each an issue's number, title, body, repository, labels and parent story,
#: and the four fields the limits and the status read, each asked by its name — a renamed field answers null, which is
#: a card with no Status (check_backlog.no_status_on). A draft or a pull request answers an empty content.
QUERY = """query($login:String!,$number:Int!,$after:String){%s user(login:$login){projectV2(number:$number){id
 items(first:100,after:$after){totalCount pageInfo{hasNextPage endCursor} nodes{content{... on Issue{number title body repository{name} labels(first:10){nodes{name}} parent{number closed}}}
  status:fieldValueByName(name:"Status"){... on ProjectV2ItemFieldSingleSelectValue{name updatedAt}}
  slice:fieldValueByName(name:"Slice"){... on ProjectV2ItemFieldSingleSelectValue{name}}
  waitingOn:fieldValueByName(name:"Waiting on"){... on ProjectV2ItemFieldSingleSelectValue{name}}
  waitingSince:fieldValueByName(name:"Waiting since"){... on ProjectV2ItemFieldDateValue{date}}}}
 statusUpdates(first:20,orderBy:{field:CREATED_AT,direction:DESC}){nodes{startDate status body}}}}}""" % RATE
#: Each field of QUERY's nodes and the key a card carries it under (the shape check_backlog reads), with the key of its
#: value.
FIELDS = (("status", "status", "name"), ("slice", "slice", "name"), ("waitingOn", "waiting on", "name"),
          ("waitingSince", "waiting since", "date"))
#: What a read could not use: a missing gh, a refusal, a timeout, an answer that was no JSON or not the board's shape.
FAILURES = (OSError, subprocess.SubprocessError, RuntimeError, ValueError, KeyError, TypeError, AttributeError)


class Unreadable(RuntimeError):
    """A board, or the project list, that could not be read; its message is the cause (cause())."""


def cause(error):
    """
    Why gh could not be asked, as a could-not-run line says it: the first line gh wrote on stderr that says anything
    ("To get started with GitHub CLI, please run:  gh auth login" — gh's own line), else the message of a RuntimeError
    that gives one (board.py's gh says gh's first line so), else the exception's name — a missing gh, a timeout with
    nothing said, an answer that was no JSON, a key it lacked.
    """
    said = getattr(error, "stderr", None) or ""
    if isinstance(said, bytes):  # a timed-out run's output comes back as bytes whatever text= said
        said = said.decode(errors="replace")
    first = next((line.strip() for line in said.splitlines() if line.strip()), None)
    if first is None and isinstance(error, RuntimeError) and str(error):
        first = str(error)
    return first or type(error).__name__


def open_parent(parent):
    """
    The number of the story a task rides on, from GitHub's `parent { number closed }` (None when it has none), else None
    for a closed parent too: a finished story holds no place in a limit, so its task is the open work and counts as a card
    of its own (P146). The gate and the status read this one rule, so they cannot disagree about who rides.
    """
    if not parent or parent.get("closed"):
        return None
    return parent.get("number")


def _asked(ask, spent, *args):
    """`ask`'s answer's data, its rateLimit added to `spent` when it carries one; any failure is Unreadable."""
    try:
        data = ask("api", "graphql", *args)["data"]
    except FAILURES as error:
        raise Unreadable(cause(error)) from None
    if spent is not None and isinstance(data, dict) and data.get("rateLimit"):
        spent.append(data["rateLimit"])
    return data


def projects(ask, spent=None):
    """{title: number} of OWNER's projects, from one PROJECTS query; Unreadable when it could not be read."""
    data = _asked(ask, spent, "-f", "query=" + PROJECTS, "-F", "login=" + OWNER)
    try:
        return {p["title"]: p["number"] for p in data["user"]["projectsV2"]["nodes"]}
    except FAILURES as error:
        raise Unreadable(cause(error)) from None


def _page(number, after, ask, spent):
    """One page of the project numbered `number`: the first when `after` is None, else the one after that cursor."""
    cursor = ["-f", "after=" + after] if after else []
    data = _asked(ask, spent, "-f", "query=" + QUERY, "-F", "login=" + OWNER, "-F", "number=%d" % number, *cursor)
    try:
        project = data["user"]["projectV2"]
        if project is None:  # GitHub answers a number with no project as null: say which, not a TypeError
            raise Unreadable("no project numbered %d under %s" % (number, OWNER))
        project["items"]["totalCount"], project["items"]["pageInfo"]["hasNextPage"]  # the shape, or Unreadable here
        return project
    except FAILURES as error:
        raise Unreadable(cause(error)) from None


def read_board(number, ask, spent=None):
    """
    The project numbered `number` under OWNER, whole: its first page's id and status updates, and every page's items
    joined under "items" (P168). Each page is one QUERY asked through `ask` (gh's arguments in, the answer's JSON out),
    `after` the cursor the last one ended on, MOST_PAGES at most; each page's cost is added to `spent` when given. A board
    whose pages held fewer items than its totalCount comes back short: unread() says so.
    """
    first = page = _page(number, None, ask, spent)
    nodes, pages = list(page["items"]["nodes"]), 1
    while page["items"]["pageInfo"]["hasNextPage"] and pages < MOST_PAGES:
        page = _page(number, page["items"]["pageInfo"]["endCursor"], ask, spent)
        nodes += page["items"]["nodes"]
        pages += 1
    first["items"]["nodes"] = nodes
    return first


def to_items(project):
    """
    The board's issues in the shape check_backlog reads — status, slice, waiting on, waiting since, labels, the open
    parent story's number (open_parent) and content {number, title, body, repo} — with when each card's Status last
    changed. A draft or a pull request on the board is no backlog item and is skipped (P811). Unreadable for a node that
    is not the board's shape.
    """
    items = []
    try:
        for node in project["items"]["nodes"]:
            content = node.get("content") or {}
            if "number" not in content or "repository" not in content:
                continue  # a draft or a pull request on the board is no backlog item
            item = {"labels": [label["name"] for label in content["labels"]["nodes"]],
                    "parent": open_parent(content.get("parent")),
                    "content": {"number": content["number"], "title": content["title"], "body": content.get("body") or "",
                                "repo": content["repository"]["name"]}}
            for field, key, value in FIELDS:
                item[key] = (node.get(field) or {}).get(value)
            item["status_changed"] = (node.get("status") or {}).get("updatedAt")
            items.append(item)
    except FAILURES as error:
        raise Unreadable(cause(error)) from None
    return items


def unread(subject, project):
    """
    How the board was read only in part — `subject` and SHORT: "the spark board holds 130 items, 1 were read", "it holds
    25 items, 2 were read" — or NO_CARDS when items came and none of them was an issue, or None when every item came.
    The gate and the status say could-not-run over spark's board with it (W1), and set the bin's aside with it.
    """
    nodes = project["items"]["nodes"]
    held, read = project["items"]["totalCount"], len(nodes)
    if held > read:
        return "%s %s" % (subject, SHORT % (held, read))
    if nodes and not to_items(project):
        return "%s %s" % (subject, NO_CARDS % read)
    return None
