#!/usr/bin/env python3
"""
The state of the work at every session start, and the day-close (P102c; docs/2026-10-05-session-status-design.md).

    board.py status [--when-in DIR ...]          # both boards in a dozen lines; nothing outside the named folders
    board.py close [--date D] [--dry-run] LINE|- # the day-close, as a status update on the spark board

It reads the boards through the PO's own gh login and stores nothing: one GraphQL query per board (GitHub allows 5,000
GraphQL points an hour, shared with everything else), REST for pull requests. The working days come from local git, so
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
TRIAL_CHECK = "2026-11-02"
#: Seconds each gh call may take at a session start before the status is skipped; a close may wait longer.
STATUS_TIMEOUT = 8
CLOSE_TIMEOUT = 60


def to_items(project):
    """
    The board's issues in the shape check_backlog reads, with when each card's Status last changed and the number of the
    story each is a sub-issue of (None for an issue with no parent story).
    """
    items = []
    for node in project["items"]["nodes"]:
        content = node.get("content") or {}
        if "number" not in content or "repository" not in content:
            continue  # a draft or a pull request on the board is no backlog item
        item = {"labels": [label["name"] for label in content["labels"]["nodes"]],
                "parent": (content.get("parent") or {}).get("number"),
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


def in_flight(items, today):
    """The cards in a working stage, with their stage and days there, counted as the check counts them (one rule)."""
    return ["%s %s %d d" % (i["status"], _short(i), age(i["status_changed"], today)) for i in items
            if i.get("status") in check_backlog.IN_FLIGHT and check_backlog.counts(i)]


def waiting(items, today):
    """The cards waiting on the PO, with since when; more than WAIT_TOO_LONG days is marked."""
    said = []
    for i in items:
        if i.get("waiting on") != "the PO" or i.get("status") == "Done":
            continue
        since = i.get("waiting since")
        if since:
            days = age(since, today)
            said.append("%s since %s, %d d%s" % (_short(i), since, days, " !" if days > WAIT_TOO_LONG else ""))
        else:
            said.append(_short(i))
    return said


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
    """A line when the board holds more cards than its one page read (GraphQL pages stop at 100), or None."""
    held, read = project["items"]["totalCount"], len(project["items"]["nodes"])
    return "the %s board holds %d items; status read the first %d" % (name, held, read) if held > read else None


def work_days(dirs, since):
    """
    The days since `since` with a commit on any branch in the git folders among dirs — a branch-only day is a working
    day too, and local git answers offline (the PO, 2026-10-05). A hook's GIT_* variables would point git at another
    repository, so they are left out.
    """
    own, days = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, set()
    for folder in dirs:
        listed = subprocess.run(["git", "-C", str(Path(folder).expanduser()), "log", "--all", "--since=%s" % since.isoformat(),
                                 "--format=%cd", "--date=format-local:%Y-%m-%d"],
                                capture_output=True, text=True, timeout=STATUS_TIMEOUT, env=own)
        if not listed.returncode:
            days |= {dt.date.fromisoformat(line) for line in listed.stdout.split()}
    return days


def inside(cwd, dirs):
    """Whether cwd lies within one of dirs."""
    here = Path(cwd).resolve()
    return any(here == Path(d).expanduser().resolve() or Path(d).expanduser().resolve() in here.parents for d in dirs)


def _boards_join(boards, each, today):
    return [("" if name == "spark" else name + " ") + said for name, items in boards for said in each(items, today)]


def status_lines(boards, prs, closes, worked, today, notes=()):
    """
    The status, both boards: boards [(name, items)], prs [(repo, number, title, draft)], closes [(date, first line)],
    worked {date}, notes [what could not be read]. The bin's cards in flight count in the verdict's total, as at the
    gate; with no bin among the boards that is said, and spark's cards are counted alone.
    """
    spark = dict(boards)["spark"]
    verdict = check_backlog.problems(spark, bin_items=dict(boards).get("bin"))
    unread_bin = [] if dict(boards).get("bin") is not None else [check_backlog.BIN_UNREAD % "no bin board was given"]
    lines = ["spark — %d open, %s · trial check %s" % (sum(1 for i in spark if i.get("status") != "Done"),
                                                        "the limits hold" if not verdict else "%d problem(s)" % len(verdict),
                                                        TRIAL_CHECK)]
    lines += ["  ! " + sentence for sentence in [*verdict, *notes, *unread_bin]]
    lines.append("  in flight: " + (", ".join(_boards_join(boards, in_flight, today)) or "nothing"))
    lines.append("  waits on the PO: " + (", ".join(_boards_join(boards, waiting, today)) or "nothing"))
    lines.append("  Ready: " + (", ".join(ready(spark)) or "empty — the PO refills it"))
    lines.append("  open PRs: " + (", ".join("%s #%s %s%s" % (repo, number, title[:48], " (draft)" if draft else "")
                                             for repo, number, title, draft in prs) or "none"))
    if closes:
        day, line = max(closes)
        lines.append("  last close %s: %s" % (day.isoformat(), line))
    gap = missing_close(worked, {day for day, _ in closes}, today)
    if gap:
        lines.append("  ! the day of %s has no close — write it first" % gap.isoformat())
    return lines


QUERY = """query($login:String!,$number:Int!){user(login:$login){projectV2(number:$number){id
 items(first:100){totalCount nodes{content{... on Issue{number title body repository{name} labels(first:10){nodes{name}} parent{number}}}
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
    waits = _boards_join(boards, waiting, today)
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


def gather(timeout=CLOSE_TIMEOUT):
    """Both boards, their open PRs, the spark board's closes and id, and what could not be read."""
    boards, prs, closes, project_id, notes = [], [], [], None, []
    for name, number, repo in BOARDS:
        project = _gh("api", "graphql", "-f", "query=" + QUERY, "-F", "login=" + OWNER, "-F", "number=%d" % number,
                      timeout=timeout)["data"]["user"]["projectV2"]
        boards.append((name, to_items(project)))
        notes += [note for note in [unread(name, project)] if note]
        if name == "spark":
            project_id, closes = project["id"], closes_from(project)
        prs += [(name, pr["number"], pr["title"], pr["draft"])
                for pr in _gh("api", "repos/%s/%s/pulls?state=open" % (OWNER, repo), timeout=timeout)]
    return boards, prs, closes, project_id, notes


def main(argv=None):
    parser = argparse.ArgumentParser(description="The state of the work, and the day-close (P102c).")
    verbs = parser.add_subparsers(dest="verb", required=True)
    verbs.add_parser("status").add_argument("--when-in", nargs="+", metavar="DIR",
                                            help="the PO's project folders: nothing shows outside them, and their git "
                                                 "history gives the working days (default: the current folder's)")
    close = verbs.add_parser("close")
    close.add_argument("line", help="the day's one line, or - to read it from stdin")
    close.add_argument("--date", help="the day to close, YYYY-MM-DD (default: today)")
    close.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.verb == "status" and args.when_in and not inside(os.getcwd(), args.when_in):
        return 0
    today = dt.date.today()
    if args.verb == "status":
        try:
            boards, prs, closes, _, notes = gather(STATUS_TIMEOUT)
            since = max((day for day, _ in closes), default=today - dt.timedelta(days=14))
            print("\n".join(status_lines(boards, prs, closes, work_days(args.when_in or [os.getcwd()], since), today, notes)))
        except Exception as broken:  # a session start must never fail (the spec, §2)
            print("board: skipped — %s" % (broken or type(broken).__name__))
        return 0
    try:
        boards, prs, closes, project_id, _ = gather()
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError, KeyError, TypeError) as unreachable:
        print("board: skipped — %s" % unreachable)
        return 1
    day = dt.date.fromisoformat(args.date) if args.date else today
    try:
        state, body = close_update(sys.stdin.read() if args.line == "-" else args.line, boards,
                                   {d for d, _ in closes}, day, today)
    except ValueError as refused:
        print("close: refused — %s" % refused)
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
