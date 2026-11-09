"""
The reach as an Operation on the core (P657, W4-3): run one line on the board on USB, cure it once when its USB output died at
power-on, and say whether the board answered. reach.py is its CLI, and its `--json` line is the flat one the bench log reads
(`FlatJsonLine`), so no golden changed. The time of `at` is the outside's clock, and a stop has no data, so no line.
"""

from spark.bench import board_codes
from spark.bench import board_doctor
from spark.bench import board_look
from spark.bench import board_reach
from spark.records import board_records
import tools
from spark.bench.firmware_platform import MicroPythonPlatform
from spark.bench import bench_privacy
from spark.bench.stops import stop_result
from spark.core import outcomes
from spark.core.renderers import FlatJsonLine
from spark.core.operation import BOARD, COMMON_ARGUMENTS, READS, RUNS, Argument, Operation
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import printable

# --- MVP ---
#: The lines of a stop name the script that printed them before the core, so they read the same from every frontend.
SCRIPT = "reach.py"
#: What reach says after the board answered: mpremote's exec stops the firmware that ran (reach-test.md).
FIRMWARE_STOPPED_MESSAGE = "the firmware is stopped: press R or replug to run it"
#: How `at` writes the moment of the run, as `time.strftime` wrote it: the date, the time and the zone as +hhmm.
AT_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


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


class ReachBoard(Operation):
    """
    Operation: the reach. It finds the one board on USB (or takes `--port`), runs `board_reach.reach` and, when mpremote
    never got in, asks the board doctor. `platform_for(project, find_tool)` builds the FirmwarePlatform (default:
    MicroPythonPlatform). A board that answered is no Finding; one that did not, a cure that cannot run, a tool problem and
    a look that stopped are one unchecked Finding each, and the data of a stop is None (nothing on stdout).
    """

    name = "reach"
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder whose tools list names mpremote (default: here)"),
                 COMMON_ARGUMENTS["port"], COMMON_ARGUMENTS["json"]._replace(help="print one line of JSON for the bench log"),
                 Argument(("--cure-first",), "cure_first", bool, "open the port with DTR and RTS off before the only try (the bench's cold arm)"))
    effects = (READS, RUNS, BOARD)
    privacy_for = staticmethod(bench_privacy.privacy_for)
    json_renderer = FlatJsonLine

    def __init__(self, platform_for=None):
        self.platform_for = platform_for or MicroPythonPlatform

    def run(self, project, port, cure_first, *, outside):
        platform = self.platform_for(project, outside.find_tool)
        try:
            finder = platform.make_port_finder(outside.run)
            port = port or finder.require_one_port(SCRIPT)
            probe = platform.make_console_probe(port, outside.run)
        except (tools.ToolProblem, board_look.LookStopError) as cannot:
            return stop_result(cannot, SCRIPT, project, port)
        if cure_first and probe is None:
            return OperationResult(None, [Finding(outcomes.COULD_NOT_RUN, None, board_codes.NO_PROBE, board_reach.NO_PROBE_MESSAGE, "")],
                                   diagnostics=["%s: %s" % (SCRIPT, board_reach.NO_PROBE_MESSAGE)])
        result = board_reach.reach(platform.make_connection(platform.make_shell_command(), port, outside.run), probe, cure_first=cure_first)
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
