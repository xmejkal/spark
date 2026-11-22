#!/usr/bin/env python3
"""
The state of the work at every session start, and the day-close (P102c; docs/2026-10-05-session-status-design.md).

    board.py status [--when-in DIR ...]          # both boards in a dozen lines; nothing outside the named folders
    board.py close [--date D] [--dry-run] LINE|- # the day-close, as a status update on the spark board

It reads the boards through the PO's own gh login and stores nothing: board_read.py's one GraphQL query per 100 items
of a board, page after page until the whole board is read, 1 point a page (GitHub allows 5,000 GraphQL points an hour,
shared with everything else), REST for pull requests. The working days come from local git, so
being offline costs the status, never the session: every call gives up after STATUS_TIMEOUT seconds.

Both verbs also print two lines (P1020): the inflow, "filed in 7 days: N, closed: M", from one more GraphQL query of two
searches, and the retro's age, "last retro: R11, D days ago", from scrum/RETROSPECTIVES.md. Either one slipping puts
the close at risk.
"""

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_backlog  # noqa: E402
from board_read import FAILURES, Unreadable, cause, read_board, to_items, unread  # noqa: E402
from spark.core.outcomes import COULD_NOT_RUN  # noqa: E402

OWNER = "xmejkal"
#: Each board: its name in the status, its project number, the repository it holds (P102a's spec §2).
BOARDS = (("spark", 2, "spark"), ("bin", 1, "sisuo-brain-transplant"))
#: More days than this waiting on the PO is named (the weekly look, P102a's spec §3).
WAIT_TOO_LONG = 3
UNDATED = check_backlog.UNDATED  #: an undated wait sorts after every dated one, as in the gate's waiting sentence
READY_LOW = 2  #: at two the PO is asked to order Ready (the spec's cadences: "Ready is down to two")
TRIAL_CHECK = "2026-11-02"
#: Seconds each gh call may take at a session start before the status is skipped; a close may wait longer.
STATUS_TIMEOUT = 8
CLOSE_TIMEOUT = 60
#: The inflow counts the issues filed and closed in this many calendar days, today included (P1020).
INFLOW_DAYS = 7
#: A retro older than this many days puts the close at risk (P1020, the PO in R11.1).
RETRO_DAYS = 7
#: The inflow's one query: two searches by their aliases, each asking only for its count.
INFLOW = ("query($filed:String!,$closed:String!){filed:search(type:ISSUE,query:$filed,first:0){issueCount} "
          "closed:search(type:ISSUE,query:$closed,first:0){issueCount}}")
#: A retro's heading in scrum/RETROSPECTIVES.md: "## R11 — 2026-11-22, on 33 days after R10".
RETRO_HEADING = re.compile(r"^## (R(\d+)) — (\d{4}-\d{2}-\d{2})", re.MULTILINE)
RETROS = Path(__file__).resolve().parent.parent / "scrum" / "RETROSPECTIVES.md"


def age(iso, today):
    """Whole days from an ISO date or timestamp to today."""
    return (today - dt.date.fromisoformat(iso[:10])).days


def _short(item):
    return "%s (#%s)" % (item["content"]["title"].split(" — ")[0], item["content"]["number"])


def _flight_marks(item):
    """
    What a card in flight is besides a card: from its labels, the expedite's holder and a bench session; from its
    wait, a card that waits on the PO, which the gate counts apart (check_backlog.waits_apart, the one rule; a bench
    session that waits carries the mark too, and the gate counts it in no total). A label
    is echoed on whichever board's card carries it; the gate leaves out of its total only the bin's bench cards.
    """
    labels = item.get("labels", [])
    marks = [mark for mark in (check_backlog.EXPEDITE, check_backlog.BENCH) if mark in labels]
    if check_backlog.waits_apart(item):
        marks.append("waits on %s" % check_backlog.THE_PO)
    return "".join(" (%s)" % mark for mark in marks)


def in_flight(items, today):
    """
    The cards in a working stage, with their stage and days there, counted as the check counts them (one rule) — with
    one difference the line itself says: a card labelled `bench` is listed and marked, though the gate leaves a bin's
    bench card out of its total (a bench session is the PO's hands); the card labelled `expedite` is marked, so the
    expedite's holder shows; and a card that waits on the PO is listed and marked, though the gate counts it in its
    lane's waiting total and not in the flight (a bench session in no total).
    """
    return ["%s %s %d d%s" % (i["status"], _short(i), age(i["status_changed"], today), _flight_marks(i)) for i in items
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
        on = "" if i["waiting on"] == check_backlog.THE_PO else " on %s" % i["waiting on"]
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


def status_lines(boards, prs, closes, worked, today, bin_why="no bin board was given", disk=None, inflow_and_retro=None):
    """
    The status, both boards: boards [(name, items)], prs [(repo, number, title, draft)], closes [(date, first line)],
    worked {date}. The bin's cards count in the verdict as at the gate (the spark lane's flight, the expedite, an undated wait);
    with no bin among the boards that is said with `bin_why` — gather()'s cause for setting it aside — and spark's cards
    are counted alone. UnknownStage (check_backlog) for a card in a stage the gate does not know or a spark board with
    no Status on any card: the caller says could-not-run (P167). `inflow_and_retro` is inflow_and_retro_lines()'s list
    or None: its lines come after the board's, a line that slips marked '!' (P1020). `disk` is the disk line
    (disk_status) or None; it comes last.
    """
    spark = dict(boards)["spark"]
    # Where a card stands is the gate's one rule (check_backlog.stage_of): a stage it does not know, or a board with no
    # Status on any card, is UnknownStage out of here — main() prints could-not-run — and a card with no Status is said.
    unstaged = check_backlog.no_stage(spark, dict(boards).get("bin"))
    verdict = check_backlog.problems(spark, bin_items=dict(boards).get("bin"))
    unread_bin = [] if dict(boards).get("bin") is not None else [check_backlog.BIN_UNREAD % bin_why]
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
    lines += [("  ! " if slips else "  ") + said for said, slips in inflow_and_retro or []]
    return lines + ([disk] if disk else [])


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


def close_update(line, boards, close_days, day, today, inflow_and_retro=()):
    """
    (status, body) of a day's close: at risk when a limit breaks, the PO has been waited on too long, or a line of
    `inflow_and_retro` (inflow_and_retro_lines()) slips; its lines end the body (P1020). One close a day.
    """
    if day in close_days:
        raise ValueError("%s is closed already — one close a day" % day.isoformat())
    spark = dict(boards)["spark"]
    waits = all_waiting(boards, today)
    risky = bool(check_backlog.problems(spark, bin_items=dict(boards).get("bin"))) or any(w.endswith("!") for w in waits)
    risky = risky or any(slips for _, slips in inflow_and_retro)
    body = "\n\n".join([line.strip(), "in flight: " + (", ".join(_boards_join(boards, in_flight, today)) or "nothing"),
                        "waits on the PO: " + (", ".join(waits) or "nothing"), *(said for said, _ in inflow_and_retro)])
    return ("AT_RISK" if risky else "ON_TRACK"), body


def _gh(*args, timeout=CLOSE_TIMEOUT):
    try:
        done = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError("gh did not answer in %d s" % timeout) from None
    if done.returncode:
        raise RuntimeError((done.stderr.strip().splitlines() or ["gh failed"])[0])
    return json.loads(done.stdout) if done.stdout.strip() else None


def gather(timeout=CLOSE_TIMEOUT, ask=None, now=None):
    """
    (both boards, their open PRs, the spark board's closes, its id, why the bin's board was set aside or None, the
    inflow). The spark
    board read only in part (unread()) is RuntimeError: the status and the close say could-not-run over it, and judge
    nothing (W1). The bin's board is read for the spark lane's flight, the expedite and its waits alone, so one read in part, or
    with no Status on any card (check_backlog.no_status_on), is left out of the boards and its cause handed back —
    spark's cards are counted alone and the bin's unread line says why, as the gate does it (check_backlog.fetch):
    one convention for the bin's failing, so the two readers cannot disagree over it. The inflow (inflow_of(), P1020)
    is asked last, so a board not read asks no search and waits no second time. Every read goes through `ask` (gh's
    arguments in, the answer's JSON out; default: gh, giving up after `timeout` seconds). `now` is the clock, an aware
    datetime (default: the real one), which sets the inflow's UTC date.
    """
    ask = ask or (lambda *args: _gh(*args, timeout=timeout))
    boards, prs, closes, project_id, bin_why = [], [], [], None, None
    for name, number, repo in BOARDS:
        project = read_board(number, ask)
        items = to_items(project)
        if name == "spark":
            short = unread("the spark board", project)
            if short:
                raise RuntimeError(short)
            project_id, closes = project["id"], closes_from(project)
        else:
            bin_why = unread("it", project)
            if bin_why is None and check_backlog.no_status_on(items):
                bin_why = check_backlog.BIN_NO_STATUS % len(items)
        if name == "spark" or bin_why is None:
            boards.append((name, items))
        prs += [(name, pr["number"], pr["title"], pr["draft"])
                for pr in ask("api", "repos/%s/%s/pulls?state=open" % (OWNER, repo))]
    return boards, prs, closes, project_id, bin_why, inflow_of(utc_today(now), ask)


def utc_today(now=None):
    """
    The date in UTC of `now`, an aware datetime (default: the clock). GitHub reads a search's dates in UTC, so the
    inflow's window ends on it (P1020).
    """
    return (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc).date()


def inflow_counts(day, ask):
    """
    (filed, closed): the issues of spark's repository filed and closed in the INFLOW_DAYS days that end on `day`, a UTC
    date, from one GraphQL query (INFLOW) asked through `ask`. `is:issue` leaves the pull requests out. Any failure is
    Unreadable with its cause, as board_read says it.
    """
    window = "%s..%s" % ((day - dt.timedelta(days=INFLOW_DAYS - 1)).isoformat(), day.isoformat())
    asked = "repo:%s/spark is:issue %s:%s"
    try:
        data = ask("api", "graphql", "-f", "query=" + INFLOW, "-f", "filed=" + asked % (OWNER, "created", window),
                   "-f", "closed=" + asked % (OWNER, "closed", window))["data"]
        return data["filed"]["issueCount"], data["closed"]["issueCount"]
    except FAILURES as error:
        raise Unreadable(cause(error)) from None


def inflow_of(day, ask):
    """
    inflow_counts(), or the cause it could not be read. A fake or broken gh can raise anything, and the status must
    never fail over the inflow (a fake gh raises StopIteration).
    """
    try:
        return inflow_counts(day, ask)
    except Exception as error:  # any failure is the line's cause, never a traceback
        return cause(error)


def last_retro(text):
    """(name, date) of the newest retro in RETROSPECTIVES.md's text, by its date, then its number; None with none."""
    found = [(dt.date.fromisoformat(date), int(number), name) for name, number, date in RETRO_HEADING.findall(text)]
    if not found:
        return None
    date, _, name = max(found)
    return name, date


def read_retro(path=RETROS):
    """last_retro() of the file at `path`, or the cause: a file not read, or one with no retro heading."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return "%s: %s" % (path.name, error.strerror or type(error).__name__)
    return last_retro(text) or "no heading '## R<n> — <date>' in %s" % path.name


def inflow_and_retro_lines(inflow, retro, today):
    """
    [(line, slips)]: the inflow's line and the retro's age line (P1020). `inflow` is (filed, closed) or the cause it
    could not be read, `retro` (name, date) or the cause. More filed than closed slips, and so does a retro more than
    RETRO_DAYS days before `today`. A look not made is could-not-run and slips (W1).
    """
    if isinstance(inflow, str):
        said = [("filed in %d days: %s — %s" % (INFLOW_DAYS, COULD_NOT_RUN, inflow), True)]
    else:
        filed, closed = inflow
        said = [("filed in %d days: %d, closed: %d" % (INFLOW_DAYS, filed, closed), filed > closed)]
    if isinstance(retro, str):
        said.append(("last retro: %s — %s" % (COULD_NOT_RUN, retro), True))
    else:
        name, date = retro
        days = (today - date).days
        said.append(("last retro: %s, %d days ago" % (name, days), days > RETRO_DAYS))
    return said


def not_made(said):
    """The lines of inflow_and_retro_lines() that could not be made: the close posts nothing over them."""
    return [line for line, _ in said if ": %s — " % COULD_NOT_RUN in line]


GB = 10**9
#: Under this much free disk, the session start says so (P435): a mutation run or a store copy can fill the rest.
LOW_DISK_BYTES = 10 * GB


#: The codes after `disk:`; an agent keys on these and not on the English after the dash.
DISK_LOW = "low"


# --- MVP ---
def disk_line(free_bytes):
    """
    The one line that warns of low disk, or None when there is enough. The code after `disk:` is DISK_LOW. The number is
    floored to 0.1 GB, so a disk just under the limit never reads as the limit.
    """
    if free_bytes >= LOW_DISK_BYTES:
        return None
    return "disk: %s — %.1f GB free, under %d GB" % (DISK_LOW, free_bytes // (GB // 10) / 10, LOW_DISK_BYTES // GB)


# --- MVP ---
def disk_status(folder=None):
    """
    The disk line for the disk that holds `folder` (default: the temp folder); could-not-run with its cause when the disk
    cannot be read (W1). Finding the temp folder is inside the guard too.
    """
    try:
        return disk_line(shutil.disk_usage(folder or tempfile.gettempdir()).free)
    except OSError as unread:
        return "disk: %s — %s" % (COULD_NOT_RUN, unread.strerror or type(unread).__name__)


#: What each verb's --help says it does, each claim read off the code below (P146 council, C3): status_lines() for what
#: the status prints, close_update() for when a close is at risk and the day it refuses, main() for the exit codes.
STATUS_HELP = ("print the state of both boards: the gate's verdict, the cards in flight (expedite and bench marked), "
               "every wait oldest first ('!' past three days), Ready in the PO's order (a warning when down to one or "
               "two), open PRs, the last close and a working day left without one. A card in flight that waits on the PO "
               "is marked '(waits on the PO)': the gate counts it apart from the cards in work. A board it could not read, "
               "or a card "
               "in a stage the gate does not know, makes the whole status one line, could-not-run with its cause; cards "
               "with no Status are said; the bin's board read in part, or with no Status on any card, is set aside and "
               "said, and spark's cards are counted alone. After the board's lines come two more: 'filed in 7 days: N, "
               "closed: M' counts the issues of spark's repository filed and closed in the last 7 days in UTC, and "
               "'last retro: R11, D days ago' names the newest retro in scrum/RETROSPECTIVES.md. Each is marked '!' "
               "when it puts the close at risk or could not be read (could-not-run). "
               "With under 10 GB free in the temp folder's disk, a last line "
               "'disk: low — …' says so. It always exits 0, since a session start must never fail")
CLOSE_HELP = ("post the day's one status update to spark's board: the line, then what is in flight and what waits on the "
              "PO; a card in flight that waits on him carries the mark '(waits on the PO)'. It is at risk when the gate "
              "finds a problem or a wait is older than three days, else on track. It is at risk too when more cards "
              "were filed than closed in 7 days or the last retro is more than 7 days old, and the update ends with "
              "those two lines (see status). It "
              "refuses a day already closed (exit 1), and exits 1 with could-not-run when the boards could not be read "
              "or a card is in a stage the gate does not know, or the inflow or the last retro could not be read")


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
                                      "start date. What it shows is still today's flight and waits, and the inflow "
                                      "and the retro's age still count from today")
    close.add_argument("--dry-run", action="store_true",
                       help="print the update and post nothing (a day already closed is still refused)")
    args = parser.parse_args(argv)
    if args.verb == "status" and args.when_in and not inside(os.getcwd(), args.when_in):
        return 0
    today = dt.date.today()
    if args.verb == "status":
        disk = disk_status()  # its own guard: a disk not read never hides the board's lines
        try:
            boards, prs, closes, _, bin_why, inflow = gather(STATUS_TIMEOUT)
            since = max((day for day, _ in closes), default=today - dt.timedelta(days=14))
            seen = inflow_and_retro_lines(inflow, read_retro(), today)
            print("\n".join(status_lines(boards, prs, closes, work_days(args.when_in or [os.getcwd()], since), today,
                                         bin_why=bin_why or "no bin board was given", disk=disk,
                                         inflow_and_retro=seen)))
        except Exception as broken:  # a session start must never fail (the spec, §2); W1: a look not made is could-not-run
            print("board: could-not-run — %s" % (broken or type(broken).__name__))
            if disk:
                print(disk)
        return 0
    try:
        boards, prs, closes, project_id, _, inflow = gather()
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError, KeyError, TypeError) as unreachable:
        print("board: could-not-run — %s" % unreachable)
        return 1
    seen = inflow_and_retro_lines(inflow, read_retro(), today)
    unmade = not_made(seen)
    if unmade:  # a short gh failure must not post an AT_RISK that stays on the board (W1)
        print("\n".join(unmade))
        return 1
    day = dt.date.fromisoformat(args.date) if args.date else today
    try:
        state, body = close_update(sys.stdin.read() if args.line == "-" else args.line, boards,
                                   {d for d, _ in closes}, day, today, inflow_and_retro=seen)
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
