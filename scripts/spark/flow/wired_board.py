"""
Whether the person's breadboard can be wired (P1044, #1534): two witnesses say so, the kept wiring sheet (breadboard.md,
current or stale, by its file's last change) and the newest board log (`deploy_reading`'s DeployState, read once per
run). Spark never says that the board is wired. With a witness, the parts phase opens with one dated line, and each pick
and build offer's effect starts with a fixed sentence that has no date, so a date never changes the fingerprint. A
board-only project has nothing to wire and gets neither. It reads and never writes. `show_flow.phases_of` applies it, and
the guide answers `data.guide.wired`.

Two meanings stand apart (P1270): a *witness* (P1044) shows that the board can be wired, and a *follow-up* shows that someone
acted after the sheet: a check record or a board log later than it (`rewire_count`). A follow-up is never a claim that the
board is wired.
"""

import datetime
from collections import namedtuple
from pathlib import Path

from spark.core.outcomes import COULD_NOT_RUN, PROBLEMS, RECORDED
from spark.breadboard import bench_changes
from spark.core.zone_time import MONTHS, stamp
from spark.flow import flow_codes, phase_readers

# --- MVP ---
#: Value: the witnesses of a board that can be wired, each a time with its zone or None: `sheet_at`, the kept sheet's
#: last change, and `deploy_at`, the newest board log's time (`data.deploy.at`).
WiredBoard = namedtuple("WiredBoard", "sheet_at deploy_at")
NOT_WIRED = WiredBoard(None, None)


def read_wired(project, deploy):
    """The WiredBoard of `project`, from its kept sheet's mtime and the run's DeployState `deploy`. It never raises: a
    sheet that cannot be read is no witness, and a log that cannot be read has no `logged` (the deploy phase says why)."""
    sheet = Path(project) / phase_readers.HELD_FILES[flow_codes.BREADBOARD]
    try:
        sheet_at = stamp(datetime.datetime.fromtimestamp(sheet.stat().st_mtime)) if sheet.is_file() else None
    except OSError:
        sheet_at = None
    return WiredBoard(sheet_at, deploy.logged.at if deploy.logged is not None else None)


#: The `chosen_by` value of the rewire's NOW sentence (P1270): no status word, the breadboard keeps none.
REWIRE = "rewire"
#: What the rewire's NOW sentence says, with the count in words: one change or many.
REWIRE_NOW = ("breadboard.md lists %s under Changes since, for a breadboard wired from the earlier sheet. If you have not made "
              "them yet, unplug the USB cable and make them. Ask Claude to check the firmware's pin names against "
              "pins.py. Spark cannot see your wiring.")
ONE_CHANGE, MANY_CHANGES = "%d change", "%d changes"


def rewire_sentence(count):
    """The rewire's NOW text for `count` listed changes: "1 change" or "3 changes"."""
    return REWIRE_NOW % ((ONE_CHANGE if count == 1 else MANY_CHANGES) % count)


def is_after(moment, since):
    """True when the time `moment` is later than `since`, both ISO with their zones; a time that does not parse, or that
    carries no zone against one that does, is not after."""
    try:
        return datetime.datetime.fromisoformat(moment) > datetime.datetime.fromisoformat(since)
    except (TypeError, ValueError):
        return False


def rewire_count(project, board, check):
    """The count of the changes breadboard.md lists (`bench_changes.listed_count`) while no follow-up came after the sheet
    (P1270): None when the sheet cannot be read, lists none, or a follow-up is later than `board.sheet_at`. A follow-up is the
    newest board log (`board.deploy_at`) or the check-firmware CheckRecord `check`, current or older (its `at`). It reads
    only breadboard.md, from what it is given, and never a board log of its own."""
    try:
        count = bench_changes.listed_count((Path(project) / phase_readers.HELD_FILES[flow_codes.BREADBOARD]).read_text())
    except (OSError, ValueError):
        return None
    follow_ups = [board.deploy_at, check.at if check.state == RECORDED else None]
    if not count or not board.sheet_at or any(is_after(each, board.sheet_at) for each in follow_ups):
        return None
    return count


def day_of(iso):
    """The day of the time `iso` in the machine's zone, as "22 Nov 2026"; a time that does not parse, as written."""
    try:
        moment = datetime.datetime.fromisoformat(iso).astimezone()
    except ValueError:
        return iso
    return "%d %s %d" % (moment.day, MONTHS[moment.month - 1], moment.year)


def wired_text(board):
    """The parts phase's line: each witness's sentence with its day, the sheet first, then the step."""
    said = [flow_codes.WIRED_SHEET_MESSAGE % day_of(board.sheet_at)] if board.sheet_at else []
    said += [flow_codes.WIRED_DEPLOY_MESSAGE % day_of(board.deploy_at)] if board.deploy_at else []
    return " ".join(said + [flow_codes.WIRED_STEP_MESSAGE])


def wired_offer(offer):
    """`offer` with its kind's fixed sentence first in its effect: a pick or a build."""
    kind = flow_codes.kind_of(offer.key)
    if kind not in flow_codes.WIRED_EFFECT:
        return offer
    return offer._replace(effect=" ".join((flow_codes.WIRED_EFFECT[kind], offer.effect)))


def with_wired(project, phases, board):
    """The Phases of `project` as a WiredBoard `board` says them: unchanged for NOT_WIRED, and for a board-only project,
    which has no part and so nothing wired (the review of #1609). Else the wired text is a line of the parts phase, its
    first, or its last while it holds problems or could not run (its first line is the Finding's sentence), and each
    pick's and build's effect opens with its fixed sentence."""
    if board == NOT_WIRED or phase_readers.is_board_only(project):
        return phases
    text, wired = wired_text(board), []
    for phase in phases:
        phase = phase._replace(offers=[wired_offer(offer) for offer in phase.offers])
        if phase.phase == flow_codes.PARTS:
            phase = phase._replace(says=phase.says + [text] if phase.status in (PROBLEMS, COULD_NOT_RUN) else [text] + phase.says)
        wired.append(phase)
    return wired


def wired_data(board):
    """`data.guide.wired`: `{sheet_at, deploy_at}`, or None when spark saw no witness."""
    return None if board == NOT_WIRED else board._asdict()
# --- end MVP ---
