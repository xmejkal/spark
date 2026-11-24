"""
The reach as an Operation on the core (P657, W4-3): run one line on the board on USB, cure it once when its USB output died at
power-on, and say whether the board answered. reach.py is its CLI, and its `--json` line is the flat one the bench log reads
(`FlatJsonLine`), so no golden changed. The time of `at` is the outside's clock, and a stop has no data, so no line, but
an open board question (P892), whose line holds `reached` false, the port, the product, `open` and `known_board`.
"""

from spark.bench import board_codes
from spark.bench import board_doctor
from spark.bench import board_look
from spark.bench import board_reach
from spark.bench import known_board
from spark.bench import stops
from spark.records import board_records
from spark.records import tool_finder
from spark.bench.firmware_platform import MicroPythonPlatform
from spark.bench import bench_privacy
from spark.bench.stops import stop_result
from spark.core import codes, outcomes
from spark.core.errors import SparkError
from spark.core.renderers import FlatJsonLine
from spark.core.operation import ASKS, BOARD, COMMON_ARGUMENTS, READS, RUNS, Argument, Operation
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import printable

# --- MVP ---
#: The lines of a stop name the script that printed them before the core, so they read the same from every frontend.
SCRIPT = "reach.py"
#: What reach says after the board answered: mpremote's exec stops the firmware that ran (reach-test.md).
FIRMWARE_STOPPED_MESSAGE = "the firmware is stopped: press R or replug to run it"
#: How `at` writes the moment of the run, as `time.strftime` wrote it: the date, the time and the zone as +hhmm.
AT_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
REPLIES_HELP = ("your own file with the yes to the board question (P892): its true value lets reach.py run its line on a board "
                "that spark cannot tell from another board. One yes is for one run")


def describe(port, result):
    """The lines a person reads, for a ReachResult."""
    cure = result.cure
    first = {None: "none: the cure came first", True: "did not answer", False: "answered"}[result.first_try_failed]
    out = ["port    %s" % port, "first   %s" % first]
    if cure is not None:
        heard = ("restart heard" if cure.restart_heard else "boot tail heard, no rst: line" if cure.boot_heard
                 else "no restart heard")
        out.append("cure    %s, the port %s" % (heard,
                                                "was back" if cure.port_back else "was not back"))
        out += ["        its read failed: %s" % cure.why] if cure.why else []
        out += ["        %s" % line for line in (cure.heard.strip() or "nothing heard").splitlines()]
    out.append("reached" if result.reached else "not reached: %s" % result.why)
    if result.reached and result.why:
        out.append(result.why)
    if result.reached:
        out.append(FIRMWARE_STOPPED_MESSAGE)
    return ["  " + line for line in out]


def data_of(port, result, cure_first, doctor, at):
    """The data of a reach, for the bench log: the result, the port, the arm, `doctor` (the board doctor's result when
    mpremote never got in, else null) and `at`, the time it was written."""
    fields = result._asdict()
    fields["cure"] = result.cure._asdict() if result.cure is not None else None
    fields["doctor"] = board_doctor.as_dict(doctor) if doctor is not None else None
    return dict(fields, port=port, cure_first=cure_first, at=at)


#: What the reach does, the paragraphs of reach.py's `--help` before its exit codes, line breaks and all (P855).
DETAILS = """It runs print("reached") on the board with mpremote's exec. When mpremote says "could not enter raw repl", it
opens the port once with DTR and RTS off, which restarted a XIAO ESP32-C6 whose USB output died at power-on, waits until
the port is there again, and runs the line once more. It says whether the board answered, whether a cure ran and what
the board printed during it. The exec stops the firmware that ran: press R or replug to run it again.

It is the PO's bench tool for P251. Claude's live try, behind a grant and with a reset at the end, is live.py (P247).
With --cure-first it opens the port with DTR and RTS off before the only try: the bench's cold arm. With two or more boards on USB, --port is needed.

Before the line runs, reach.py asks the board question (P892). It lists the boards with `mpremote devs`, also for a
--port, and a /dev/tty. port is its /dev/cu. port. A --port that the list does not hold stops with port_not_listed
before the question, and nothing ran on the board. On the board that spark keeps for the project, known by its USB
serial, it asks nothing. Another board, told apart by its USB serial, stops with other_board, and a board with a USB
serial in a project that keeps no board stops with no_known_board. Both name look.py, and nothing ran on the board. A
board that spark cannot tell by its USB serial is asked on every run, in your terminal, or by --replies with your own
file that holds {"replies": {"reach.run_on_board.<id>": true}}: a board with no serial and, while the kept board's
record trusts no USB serial (it showed none, or one that its firmware set), a board on Espressif's own USB whose
serial does not start with the kept MAC. One yes or one no is for one run. A no is answered_no, and nothing ran on the
board. With --json an open question prints one line: reached false, port, product, open and known_board. Every other
stop prints nothing on stdout. For other_board, no_known_board and answered_no, the last line on stderr is the stop's
fix, after its sentence.

When mpremote cannot open the port or enter the board's REPL, the board doctor (P282) runs two checks: whether `mpremote devs` lists the
port, and two seconds of the console with the port's lock. It prints mpremote's own error, each check's fact,
and one next step for your hands, as the last line. Its look at the console can restart the board."""


class ReachBoard(Operation):
    """
    Operation: the reach. It lists the boards and finds the one on USB, or the row of `--port`. A port that the list does
    not hold stops with port_not_listed before the board question (P1056). After its refusal of `--cure-first` with no probe
    it asks the board question by the REACH touch (`known` is the KnownBoardStore, None: the store's own), runs
    `board_reach.reach` and, when mpremote never got in, asks the board doctor. `platform_for(project, find_tool)` builds
    the FirmwarePlatform (default: MicroPythonPlatform). A board that answered is no Finding; one that did not, a cure that
    cannot run, a tool problem, a look that stopped and a stop of the board question are one unchecked Finding each. The
    data of a stop is None (nothing on stdout), but for an open board question.
    """

    name = "reach"
    summary = "Run one line on the board on USB, and cure it once when its USB output died at power-on: the PO's bench tool (P251)."
    details = DETAILS
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder whose tools list names mpremote (default: here)"),
                 COMMON_ARGUMENTS["port"], COMMON_ARGUMENTS["json"]._replace(help="print one line of JSON for the bench log"),
                 Argument(("--cure-first",), "cure_first", bool, "open the port with DTR and RTS off before the only try (the bench's cold arm)"),
                 COMMON_ARGUMENTS["replies"]._replace(help=REPLIES_HELP))
    effects = (READS, RUNS, BOARD, ASKS)
    privacy_for = staticmethod(bench_privacy.privacy_for)
    json_renderer = FlatJsonLine

    def __init__(self, platform_for=None, known=None):
        self.platform_for = platform_for or MicroPythonPlatform
        self.board_question = known_board.KnownBoardService(known or known_board.KnownBoardStore(), known_board.REACH)  # P892

    def run(self, project, port, cure_first, replies=None, *, outside):
        platform = self.platform_for(project, outside.find_tool)
        try:
            finder = platform.make_port_finder(outside.run)
            row = finder.require_one_board(SCRIPT, port)  # P892, P1056: a named port the list does not hold stops with port_not_listed
            named, port = port, port or row.device
            probe = platform.make_console_probe(port, outside.run)
        except (tool_finder.ToolError, board_look.LookStopError) as cannot:
            return stop_result(cannot, SCRIPT, project, port)
        if cure_first and probe is None:
            return OperationResult(None, [Finding(outcomes.COULD_NOT_RUN, None, board_codes.NO_PROBE, board_reach.NO_PROBE_MESSAGE, "")],
                                   diagnostics=["%s: %s" % (SCRIPT, board_reach.NO_PROBE_MESSAGE)])
        try:
            self.board_question.require(project, named, row, outside.replies, replies)
        except known_board.BoardQuestionError as stopped:  # the line of an open question only (P892, decision 5)
            return stops.question_result(stopped, SCRIPT, dict(stopped.data, reached=False) if stopped.code == codes.NEEDS_REPLY else None)
        except SparkError as unreadable:  # the kept record or the replies file
            return stop_result(unreadable, SCRIPT, project, port)
        result = board_reach.reach(platform.make_connection(platform.make_shell_command(), port, outside.run, row.usb), probe, cure_first=cure_first)
        diagnostics = []
        try:
            doctor = (None if result.entered else
                      board_doctor.BoardDoctorService.for_board(finder, probe).examine(port, platform.find_tool("board-shell"), result.why))
        except board_doctor.UnknownStepError as cannot:
            diagnostics.append("%s: no doctor: %s" % (SCRIPT, cannot))  # P430: the tools list's words: run_cli guards the stderr lines
            doctor = None
        places = board_records.ButtonPlaces.of_project(project)
        lines = describe(port, result) + (["  " + line for line in board_doctor.describe(doctor, places)] if doctor else [])
        fix = board_doctor.step_sentence(doctor.next_step, places) if doctor and doctor.next_step else ""
        findings = [] if result.reached else [Finding(outcomes.COULD_NOT_RUN, None, board_codes.NOT_REACHED, result.why, fix)]
        # P430: the port, the cure's read and the board's reply are data, each line shown guarded
        return OperationResult(data_of(port, result, cure_first, doctor, outside.clock.now().strftime(AT_FORMAT)), findings,
                               lines=[printable(line) for line in lines], diagnostics=diagnostics)
# --- end MVP ---
