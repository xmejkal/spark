"""
Whether the person's breadboard can be wired (P1044, #1534): two witnesses say so, the kept wiring sheet (breadboard.md,
current or stale, by its file's last change) and the newest board log (`deploy_reading`'s DeployState, read once per
run). Spark never says that the board is wired. With a witness, the parts phase opens with one dated line, and each pick
and build offer's effect starts with a fixed sentence that has no date, so a date never changes the fingerprint. A
board-only project has nothing to wire and gets neither. It reads and never writes. `show_flow.phases_of` applies it, and
the guide answers `data.guide.wired`.
"""

import datetime
from collections import namedtuple
from pathlib import Path

from spark.core.outcomes import COULD_NOT_RUN, PROBLEMS
from spark.core.zone_time import stamp
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


def day_of(iso):
    """The day of the time `iso` in the machine's zone, as "22 Nov 2026"; a time that does not parse, as written."""
    try:
        moment = datetime.datetime.fromisoformat(iso).astimezone()
    except ValueError:
        return iso
    return "%d %s" % (moment.day, moment.strftime("%b %Y"))


def wired_text(board):
    """The parts phase's line: each witness's sentence with its day, the sheet first, then the step."""
    said = [flow_codes.WIRED_SHEET_MESSAGE % day_of(board.sheet_at)] if board.sheet_at else []
    said += [flow_codes.WIRED_DEPLOY_MESSAGE % day_of(board.deploy_at)] if board.deploy_at else []
    return " ".join(said + [flow_codes.WIRED_STEP_MESSAGE])


def wired_offer(offer):
    """`offer` with its kind's fixed sentence first in its effect: a pick or a build."""
    kind = offer.key.split(":", 1)[0]
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
