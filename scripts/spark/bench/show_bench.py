"""
The bench's show as an Operation on the core (P919, #1301): each board on USB with its deploys by project, its last
deploy, the projects that keep it and its grants, from spark's store. It runs only `mpremote devs`, which opens no
port, so a running program goes on. `bench.py show` is its CLI. A part that it could not check is one unchecked item,
with the port as its subject, and the data still holds what was read.
"""

from spark.bench import bench_privacy
from spark.bench import bench_service
from spark.bench import board_codes
from spark.bench import board_grant
from spark.bench import board_look
from spark.bench import known_board
from spark.bench.firmware_platform import MicroPythonPlatform
from spark.bench.stops import stop_result
from spark.core import outcomes
from spark.core.operation import COMMON_ARGUMENTS, READS, RUNS, Operation
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import printable
from spark.records import deploy_record_store
from spark.records import store
from spark.records import tool_finder

# --- MVP ---
#: The lines of a stop name the script that printed them.
SCRIPT = "bench.py"
NO_BOARD_LINE = "No board on USB."
COUNT_LINES = ("1 board on USB. No port was opened.", "%d boards on USB. No port was opened.")
#: The last line: what the names are. A registered project's name comes with its tool (P920).
NAMES_LINE = ('The names after "deploys from" are folder names, as spark\'s deploys recorded them, or registered names '
              'with "by" and the tool that recorded them.')
#: A part's line: its label, padded so that the values stand in one column.
PART_LINE = "  %-13s %s"
LABEL = {bench_service.KEPT_FOR: "kept for", bench_service.LAST_DEPLOY: "last deploy",
         bench_service.DEPLOYS_FROM: "deploys from", bench_service.GRANTS: "grants"}
NO_DEPLOY = board_look.NONE_RECORDED_NOTE
NO_PROJECT = "no project (look.py keeps a board for a project)"
#: What each code says of a part that was not checked: its board_codes sentence, but where that one is another
#: script's (a kept board "for this project", the "last deploy" alone), and what the person does about it.
REASON = dict(((code, board_codes.CODES[code]) for code in (board_codes.CANNOT_TELL_BOARD, board_codes.NOT_A_GRANT)),
              **{board_codes.KNOWN_BOARD_UNREADABLE: "spark's record of a kept board cannot be read",
                 board_codes.LAST_DEPLOY_NOT_CHECKED: "spark's record of this board's deploys cannot be read"})
FIX = {board_codes.CANNOT_TELL_BOARD: "run look.py in the project that uses this board: it reads the board and keeps it",
       board_codes.KNOWN_BOARD_UNREADABLE: known_board.UNREADABLE_FIX,
       board_codes.LAST_DEPLOY_NOT_CHECKED: "repair or remove that file, then run bench.py show again",
       board_codes.NOT_A_GRANT: "remove that file, or give a new grant with grant.py"}
#: How a grant row reads, by its state: LIVE and ENDED add the end of the grant, in the machine's zone.
GRANT_WORDS = {bench_service.LIVE: "holds until %s", bench_service.ENDED: "ended %s", bench_service.NONE: "none",
               bench_service.NOT_A_GRANT: outcomes.NOT_CHECKED_MESSAGE % REASON[board_codes.NOT_A_GRANT],
               bench_service.NO_ZONE: "its time has no zone, so it was not trusted",
               bench_service.NOT_CHECKED: outcomes.NOT_CHECKED_MESSAGE % REASON[board_codes.CANNOT_TELL_BOARD]}
TIMED = (bench_service.LIVE, bench_service.ENDED)


def _not_checked(board, part):
    """The line of a part of `board` that was not checked, by the code of its first Unchecked item."""
    return outcomes.NOT_CHECKED_MESSAGE % REASON[next(item.code for item in board.unchecked if item.part == part)]


def _grant_said(grant):
    words = GRANT_WORDS[grant.state]
    return "%s: %s" % (grant.scope, words % board_grant.say_in_local_zone(grant.expires_at) if grant.state in TIMED else words)


def _deploys_said(board):
    """The deploys by project, NO_DEPLOY for none, or why they were not checked."""
    if board.deploys_from is None:
        return _not_checked(board, bench_service.DEPLOYS_FROM)
    return ", ".join("%s%s (%d, last %s)" % (each["project"], ", by %s" % each["made_by"] if each["made_by"] else "", each["deploys"],
                                             deploy_record_store.date_said(each["last"])) for each in board.deploys_from) or NO_DEPLOY


def _kept_said(board):
    """The projects that keep the board, NO_PROJECT for none, or why that is not known."""
    if board.identity.kept_for is None:
        return _not_checked(board, bench_service.KEPT_FOR)
    return ", ".join("%s (since %s)" % (known.project, known.since_said()) for known in board.identity.kept_for) or NO_PROJECT


def say_board(board):
    """The lines of one ConnectedBoard: its port and name, then the deploys, the last deploy, the kept projects and the
    grants. The MAC shows by its last two bytes only."""
    row, (mac, _, name, _) = board.row, board.identity
    lines = ["%s   %s" % (row.device, "%s, MAC ends %s" % (name or row.product, known_board.mac_ends(mac)) if mac else row.product),
             PART_LINE % (LABEL[bench_service.DEPLOYS_FROM], _deploys_said(board)),
             "  " + board_look.say_last_deploy(board.last_deploy),
             PART_LINE % (LABEL[bench_service.KEPT_FOR], _kept_said(board)),
             PART_LINE % (LABEL[bench_service.GRANTS], "; ".join(_grant_said(grant) for grant in board.grants))]
    return [printable(line) for line in lines]


def describe(result):
    """The lines a person reads, for a BenchResult: the count, then each board, then what the names are."""
    if not result.boards:
        return [NO_BOARD_LINE]
    lines = [COUNT_LINES[0] if len(result.boards) == 1 else COUNT_LINES[1] % len(result.boards)]
    for board in result.boards:
        lines += [""] + say_board(board)
    return lines + [NAMES_LINE]


def findings_of(result):
    """One unchecked Finding per part of a board that was not checked, the board's port its subject. The sentence names
    the file to repair when there is one: the kept files that cannot be read belong to no single board."""
    found = []
    for board in result.boards:
        for item in board.unchecked:
            paths = [item.path] if item.path else result.kept_unreadable if item.code == board_codes.KNOWN_BOARD_UNREADABLE else []
            sentence = "%s: %s" % (LABEL[item.part], outcomes.NOT_CHECKED_MESSAGE % REASON[item.code])
            found.append(Finding(outcomes.COULD_NOT_RUN, board.row.device, item.code,
                                 sentence + (": %s" % ", ".join(str(path) for path in paths) if paths else ""), FIX[item.code]))
    return found


class ShowBench(Operation):
    """
    Operation: each board on USB with what spark's store holds of it. `records`, `known` and `grants` are the
    DeployRecordStore, KnownBoardStore and GrantStore (None: the store's own), and `platform_for(project, find_tool)`
    builds the FirmwarePlatform (default: MicroPythonPlatform), whose port finder alone it asks for. `--project` only finds
    the tools list. A stop runs no board doctor, because the doctor can open a port.
    """

    name = "show-bench"
    summary = "each board on USB with its deploys, the projects that keep it and its grants, from spark's store; it opens no port"
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the folder whose tools list names mpremote (default: here; any folder runs)"),
                 COMMON_ARGUMENTS["json"])
    effects = (READS, RUNS)
    data_keys = ("boards",)
    privacy_for = staticmethod(bench_privacy.privacy_for)

    def __init__(self, records=None, known=None, grants=None, platform_for=None):
        self.records, self.known, self.grants = records, known, grants
        self.platform_for = platform_for or MicroPythonPlatform

    def run(self, project, *, outside):
        try:
            finder = self.platform_for(project, outside.find_tool).make_port_finder(outside.run)
            result = bench_service.BenchService(finder, self.known, self.records, self.grants, outside.clock.now).show()
        except (tool_finder.ToolError, board_look.LookStopError, store.StoreError) as cannot:
            return stop_result(cannot, SCRIPT, project, None)._replace(data={"boards": None})
        return OperationResult({"boards": [board.to_dict() for board in result.boards]}, findings_of(result), lines=describe(result))
# --- end MVP ---
