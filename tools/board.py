#!/usr/bin/env python3
"""
The state of the work at every session start, and the day-close (P102c; docs/2026-10-05-session-status-design.md).

    board.py status [--when-in DIR ...]          # both boards in a dozen lines; nothing outside the named folders
    board.py close [--date D] [--dry-run] LINE|- # the day-close, as a status update on the spark board

It reads the boards through the PO's own gh login and stores nothing: one GraphQL query per 100 items of a board, page
after page until the whole board is read (GitHub allows 5,000 GraphQL points an hour, shared with everything else),
REST for pull requests. The working days come from local git, so
being offline costs the status, never the session: every call gives up after STATUS_TIMEOUT seconds.
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_backlog  # noqa: E402

OWNER = "xmejkal"
#: Each board: its name in the status, its project number, the repository it holds (P102a's spec §2).
BOARDS = (("spark", 2, "spark"), ("bin", 1, "sisuo-brain-transplant"))
#: More days than this waiting on the PO is named (the weekly look, P102a's spec §3).
WAIT_TOO_LONG = 3
UNDATED = "9999-12-31"  #: an undated wait sorts after every dated one
READY_LOW = 2  #: at two the PO is asked to order Ready (the spec's cadences: "Ready is down to two")
TRIAL_CHECK = "2026-11-02"
#: Seconds each gh call may take at a session start before the status is skipped; a close may wait longer.
STATUS_TIMEOUT = 8
CLOSE_TIMEOUT = 60


def to_items(project):
    """
    The board's issues in the shape check_backlog reads, with when each card's Status last changed and the number of the
    story each is a sub-issue of (None for an issue with no parent story, or whose parent story is closed:
    check_backlog.open_parent).
    """
    items = []
    for node in project["items"]["nodes"]:
        content = node.get("content") or {}
        if "number" not in content or "repository" not in content:
            continue  # a draft or a pull request on the board is no backlog item
        item = {"labels": [label["name"] for label in content["labels"]["nodes"]],
                "parent": check_backlog.open_parent(content.get("parent")),
                "content": {"number": content["number"], "title": content["title"], "body": content.get("body") or "",
                            "repo": content["repository"]["name"]}}
        for value in node["fieldValues"]["nodes"]:
            name = ((value or {}).get("field") or {}).get("name", "").lower()
            if name:
                item[name] = value.get("name", value.get("date"))
                if name == "status":
                    item["status_changed"] = value.get("updatedAt")
        items.append(item)
    return items


def age(iso, today):
    """Whole days from an ISO date or timestamp to today."""
    return (today - dt.date.fromisoformat(iso[:10])).days


def _short(item):
    return "%s (#%s)" % (item["content"]["title"].split(" — ")[0], item["content"]["number"])


def _lane_marks(item):
    """
    What a card in flight is besides a card, from its labels: the expedite lane's holder, a bench session. The label is
    echoed on whichever board's card carries it; the gate leaves out of its total only the bin's bench cards.
    """
    labels = item.get("labels", [])
    return "".join(" (%s)" % mark for mark in (check_backlog.EXPEDITE, check_backlog.BENCH) if mark in labels)


def in_flight(items, today):
    """
    The cards in a working stage, with their stage and days there, counted as the check counts them (one rule) — with
    one difference the line itself says: a card labelled `bench` is listed and marked, though the gate leaves a bin's
    bench card out of its total (a bench session is the PO's hands); the card labelled `expedite` is marked, so the
    lane's holder shows.
    """
    return ["%s %s %d d%s" % (i["status"], _short(i), age(i["status_changed"], today), _lane_marks(i)) for i in items
            if i.get("status") in check_backlog.IN_FLIGHT and check_backlog.counts(i)]


def _waits(items, today):
    """
    (Waiting since, sentence) for each open card waiting on someone; more than WAIT_TOO_LONG days is marked. The status
    heads the list "waits on the PO", so a wait on anyone else says who: `A (#1) on Anna since …`.
    """
    said = []
    for i in items:
        if not i.get("waiting on") or i.get("status") == "Done":
            continue
        on = "" if i["waiting on"] == "the PO" else " on %s" % i["waiting on"]
        since = i.get("waiting since")
        if since:
            days = age(since, today)
            said.append((since, "%s%s since %s, %d d%s" % (_short(i), on, since, days, " !" if days > WAIT_TOO_LONG else "")))
        else:
            said.append((UNDATED, _short(i) + on))
    return said


def all_waiting(boards, today):
    """Every wait on either board, oldest first (the spec, §1), an undated one last; the bin's are named by their board."""
    said = sorted((since, _on_board(name, text)) for name, items in boards for since, text in _waits(items, today))
    return [text for _, text in said]


def ready(items):
    """The Ready column in the board's own order, which is the PO's (W11)."""
    return [_short(i) for i in items if i.get("status") == "Ready"]


def missing_close(work_days, close_days, today):
    """The last working day before today when no close covers it, or None (only that day: a restart needs one line)."""
    last = max((day for day in work_days if day < today), default=None)
    if last is not None and (not close_days or max(close_days) < last):
        return last
    return None


def unread(name, project):
    """
    Why the board was read only in part — its pages held fewer items than its totalCount says it holds — or None when
    every item came. gather() raises it: a status over part of a board is could-not-run, never "the limits hold" (W1).
    """
    held, read = project["items"]["totalCount"], len(project["items"]["nodes"])
    return "the %s board holds %d items, %d were read" % (name, held, read) if held > read else None


def work_days(dirs, since):
    """
    The days since `since` with a commit on any branch in the git folders among dirs — a branch-only day is a working
    day too, and local git answers offline (the PO, 2026-10-05). A date alone means that date at the current time of day
    to git, which would lose the first day's morning, so the window opens at midnight. A hook's GIT_* variables would
    point git at another repository, so they are left out.
    """
    own, days = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, set()
    for folder in dirs:
        listed = subprocess.run(["git", "-C", str(Path(folder).expanduser()), "log", "--all", "--since=%s 00:00" % since.isoformat(),
                                 "--format=%cd", "--date=format-local:%Y-%m-%d"],
                                capture_output=True, text=True, timeout=STATUS_TIMEOUT, env=own)
        if not listed.returncode:
            days |= {dt.date.fromisoformat(line) for line in listed.stdout.split()}
    return days


def inside(cwd, dirs):
    """Whether cwd lies within one of dirs."""
    here = Path(cwd).resolve()
    return any(here == Path(d).expanduser().resolve() or Path(d).expanduser().resolve() in here.parents for d in dirs)


def _on_board(name, said):
    """A sentence about a card, named by its board unless it is spark's."""
    return ("" if name == "spark" else name + " ") + said


def _boards_join(boards, each, today):
    return [_on_board(name, said) for name, items in boards for said in each(items, today)]


def status_lines(boards, prs, closes, worked, today):
    """
    The status, both boards: boards [(name, items)], prs [(repo, number, title, draft)], closes [(date, first line)],
    worked {date}. The bin's cards count in the verdict as at the gate (the flight total, the lane, an undated wait);
    with no bin among the boards that is said, and spark's cards are counted alone. UnknownStage (check_backlog) for a
    card in a stage the gate does not know or a board with no Status on any card: the caller says could-not-run (P167).
    """
    spark = dict(boards)["spark"]
    # Where a card stands is the gate's one rule (check_backlog.stage_of): a stage it does not know, or a board with no
    # Status on any card, is UnknownStage out of here — main() prints could-not-run — and a card with no Status is said.
    unstaged = check_backlog.no_stage(spark, dict(boards).get("bin"))
    verdict = check_backlog.problems(spark, bin_items=dict(boards).get("bin"))
    unread_bin = [] if dict(boards).get("bin") is not None else [check_backlog.BIN_UNREAD % "no bin board was given"]
    lines = ["spark — %d open, %s · trial check %s" % (sum(1 for i in spark if i.get("status") != "Done"),
                                                        "the limits hold" if not verdict else "%d problem(s)" % len(verdict),
                                                        TRIAL_CHECK)]
    lines += ["  ! " + sentence for sentence in [*verdict, *([unstaged] if unstaged else []), *unread_bin]]
    lines.append("  in flight: " + (", ".join(_boards_join(boards, in_flight, today)) or "nothing"))
    lines.append("  waits on the PO: " + (", ".join(all_waiting(boards, today)) or "nothing"))
    lines.append("  Ready: " + (", ".join(ready(spark)) or "empty — the PO refills it"))
    if 0 < len(ready(spark)) <= READY_LOW:
        lines.append("  ! Ready is down to %d — propose an order for the PO" % len(ready(spark)))
    lines.append("  open PRs: " + (", ".join("%s #%s %s%s" % (repo, number, title[:48], " (draft)" if draft else "")
                                             for repo, number, title, draft in prs) or "none"))
    if closes:
        day, line = max(closes)
        lines.append("  last close %s: %s" % (day.isoformat(), line))
    gap = missing_close(worked, {day for day, _ in closes}, today)
    if gap:
        lines.append("  ! the day of %s has no close — write it first" % gap.isoformat())
    return lines


#: One page of a board: GitHub hands a project's items over 100 at a time, so read_board() asks page after page with
#: `after` set to the last page's endCursor until hasNextPage is false (P168). The id and status updates come with every
#: page; the first page's are kept.
QUERY = """query($login:String!,$number:Int!,$after:String){user(login:$login){projectV2(number:$number){id
 items(first:100,after:$after){totalCount pageInfo{hasNextPage endCursor} nodes{content{... on Issue{number title body repository{name} labels(first:10){nodes{name}} parent{number closed}}}
  fieldValues(first:20){nodes{
   ... on ProjectV2ItemFieldSingleSelectValue{name updatedAt field{... on ProjectV2FieldCommon{name}}}
   ... on ProjectV2ItemFieldDateValue{date field{... on ProjectV2FieldCommon{name}}}}}}}
 statusUpdates(first:20,orderBy:{field:CREATED_AT,direction:DESC}){nodes{startDate status body}}}}}"""
POST = ("mutation($p:ID!,$d:Date!,$s:ProjectV2StatusUpdateStatus!,$b:String!){createProjectV2StatusUpdate("
        "input:{projectId:$p,startDate:$d,status:$s,body:$b}){statusUpdate{id}}}")


def closes_from(project):
    """The board's day-closes: (start date, first line), skipping updates made by hand with no start date."""
    said = []
    for update in project["statusUpdates"]["nodes"]:
        if update.get("startDate"):
            lines = (update.get("body") or "").strip().splitlines()
            said.append((dt.date.fromisoformat(update["startDate"]), lines[0] if lines else ""))
    return said


def close_update(line, boards, close_days, day, today):
    """(status, body) of a day's close: at risk when a limit breaks or the PO has been waited on too long; one a day."""
    if day in close_days:
        raise ValueError("%s is closed already — one close a day" % day.isoformat())
    spark = dict(boards)["spark"]
    waits = all_waiting(boards, today)
    risky = bool(check_backlog.problems(spark, bin_items=dict(boards).get("bin"))) or any(w.endswith("!") for w in waits)
    body = "\n\n".join([line.strip(), "in flight: " + (", ".join(_boards_join(boards, in_flight, today)) or "nothing"),
                        "waits on the PO: " + (", ".join(waits) or "nothing")])
    return ("AT_RISK" if risky else "ON_TRACK"), body


def _gh(*args, timeout=CLOSE_TIMEOUT):
    try:
        done = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError("gh did not answer in %d s" % timeout) from None
    if done.returncode:
        raise RuntimeError((done.stderr.strip().splitlines() or ["gh failed"])[0])
    return json.loads(done.stdout) if done.stdout.strip() else None


#: The most pages read_board() turns: 50 of 100 is the gate's MOST_ITEMS, and a hasNextPage that never falls cannot
#: hold a session start forever — the board is then read in part, and unread() says so.
MOST_PAGES = 50


def read_board(number, timeout):
    """
    The project numbered `number` under OWNER, whole: its first page's id and status updates, and every page's items
    joined under "items" (P168). Each page is one QUERY, asked `after` the cursor the last one ended on; a board whose
    pages held fewer items than its totalCount — MOST_PAGES turned, or a page GitHub cut — is RuntimeError, unread()'s line.
    """
    first = page = _page(number, None, timeout)
    nodes = list(page["items"]["nodes"])
    while page["items"]["pageInfo"]["hasNextPage"] and len(nodes) < MOST_PAGES * 100:
        page = _page(number, page["items"]["pageInfo"]["endCursor"], timeout)
        nodes += page["items"]["nodes"]
    first["items"]["nodes"] = nodes
    return first


def _page(number, after, timeout):
    """One page of the project numbered `number`: the first when `after` is None, else the one after that cursor."""
    cursor = ["-f", "after=" + after] if after else []
    return _gh("api", "graphql", "-f", "query=" + QUERY, "-F", "login=" + OWNER, "-F", "number=%d" % number, *cursor,
               timeout=timeout)["data"]["user"]["projectV2"]


def gather(timeout=CLOSE_TIMEOUT):
    """
    Both boards, their open PRs, the spark board's closes and id. A board read only in part (unread()) is RuntimeError:
    the status and the close say could-not-run over it, and judge nothing (W1).
    """
    boards, prs, closes, project_id = [], [], [], None
    for name, number, repo in BOARDS:
        project = read_board(number, timeout)
        short = unread(name, project)
        if short:
            raise RuntimeError(short)
        boards.append((name, to_items(project)))
        if name == "spark":
            project_id, closes = project["id"], closes_from(project)
        prs += [(name, pr["number"], pr["title"], pr["draft"])
                for pr in _gh("api", "repos/%s/%s/pulls?state=open" % (OWNER, repo), timeout=timeout)]
    return boards, prs, closes, project_id


#: What each verb's --help says it does, each claim read off the code below (P146 council, C3): status_lines() for what
#: the status prints, close_update() for when a close is at risk and the day it refuses, main() for the exit codes.
STATUS_HELP = ("print the state of both boards: the gate's verdict, the cards in flight (expedite and bench marked), "
               "every wait oldest first ('!' past three days), Ready in the PO's order (a warning when down to one or "
               "two), open PRs, the last close and a working day left without one. A board it could not read makes the "
               "whole status one line, could-not-run with its cause; it always exits 0, since a session "
               "start must never fail")
CLOSE_HELP = ("post the day's one status update to spark's board: the line, then what is in flight and what waits on the "
              "PO. It is at risk when the gate finds a problem or a wait is older than three days, else on track. It "
              "refuses a day already closed (exit 1), and exits 1 with could-not-run when the boards could not be read")


def main(argv=None):
    parser = argparse.ArgumentParser(description="The state of both boards, spark's and the bin's, at a session start, "
                                                 "and the day-close as a status update on spark's board (P102c). It "
                                                 "reads through the PO's own gh login and stores nothing.")
    verbs = parser.add_subparsers(dest="verb", required=True)
    verbs.add_parser("status", help=STATUS_HELP, description=STATUS_HELP).add_argument(
        "--when-in", nargs="+", metavar="DIR", help="the PO's project folders: nothing shows outside them, and their git "
                                                    "history gives the working days (default: the current folder's)")
    close = verbs.add_parser("close", help=CLOSE_HELP, description=CLOSE_HELP)
    close.add_argument("line", help="the day's one line, or - to read it from stdin")
    close.add_argument("--date", help="the day to close, YYYY-MM-DD (default: today), for a day missed: the update's "
                                      "start date. What it shows is still today's flight and waits")
    close.add_argument("--dry-run", action="store_true",
                       help="print the update and post nothing (a day already closed is still refused)")
    args = parser.parse_args(argv)
    if args.verb == "status" and args.when_in and not inside(os.getcwd(), args.when_in):
        return 0
    today = dt.date.today()
    if args.verb == "status":
        try:
            boards, prs, closes, _ = gather(STATUS_TIMEOUT)
            since = max((day for day, _ in closes), default=today - dt.timedelta(days=14))
            print("\n".join(status_lines(boards, prs, closes, work_days(args.when_in or [os.getcwd()], since), today)))
        except Exception as broken:  # a session start must never fail (the spec, §2); W1: a look not made is could-not-run
            print("board: could-not-run — %s" % (broken or type(broken).__name__))
        return 0
    try:
        boards, prs, closes, project_id = gather()
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError, KeyError, TypeError) as unreachable:
        print("board: could-not-run — %s" % unreachable)
        return 1
    day = dt.date.fromisoformat(args.date) if args.date else today
    try:
        state, body = close_update(sys.stdin.read() if args.line == "-" else args.line, boards,
                                   {d for d, _ in closes}, day, today)
    except ValueError as refused:
        print("close: refused — %s" % refused)
        return 1
    except check_backlog.UnknownStage as unplaced:  # a stage the gate does not know: nothing judged, nothing posted (P167)
        print("board: could-not-run — %s" % unplaced)
        return 1
    print("close %s (%s):\n%s" % (day.isoformat(), state, body))
    if args.dry_run:
        print("(dry run — nothing posted)")
        return 0
    _gh("api", "graphql", "-f", "query=" + POST, "-f", "p=" + project_id, "-f", "d=" + day.isoformat(),
        "-f", "s=" + state, "-f", "b=" + body)
    print("posted on the spark board")
    return 0


if __name__ == "__main__":
    sys.exit(main())
