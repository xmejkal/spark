"""
The live try as an Operation on the core (P657, W4-3): run a short piece of code on the running board inside a grant, say
whether the board ran it, and reset it. live.py is its CLI, and its `--json` line is the flat one (`FlatJsonLine`): every field of
the LiveTryResult and the port, so no golden changed. The status comes from `board_live.exit_code`, so a failed reset
stays exit 2 whatever the answer was; a stop has the same fields, empty, with the answer `could-not-run`.
"""

import board_codes
from spark.bench import board_doctor
from spark.bench import board_envelope
from spark.bench import board_grant
from spark.bench import board_live
from spark.bench import board_look
import boards
import tools
from spark.bench.firmware_platform import MicroPythonPlatform
from restricted_pins import BrokenRecordError
from spark.bench import bench_privacy
from spark.bench import stops
from spark.core import outcomes
from spark.core.renderers import FlatJsonLine
from spark.core.operation import BOARD, COMMON_ARGUMENTS, READS, RUNS, Argument, Operation
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import printable

# --- MVP ---
#: The lines of a stop name the script that printed them before the core, so they read the same from every frontend.
SCRIPT = "live.py"


def describe(result, places=boards.ButtonPlaces.EMPTY):
    """The lines a person reads, for a LiveTryResult, each guarded (P430). `places` names the buttons the doctor's steps mention."""
    out = ["answer  %s" % result.answer]
    out += ["why     %s" % result.why] if result.why else []
    out += ["output  %s" % line for line in result.output.splitlines()]
    out += ["reset   %s" % result.reset] if result.reset else []
    out += ["pins    %s" % board_live.NO_RESTRICTED_PINS_MESSAGE] if not result.pins_checked else []
    if result.gpio_numbers_in_code:
        out.append("gpio    the code writes %s, each a GPIO of this board"
                   % ", ".join(str(gpio) for gpio in result.gpio_numbers_in_code))
    if result.doctor:
        out += board_doctor.describe(result.doctor, places)
    # P430: the board's reply and the doctor's lines are data, one line each
    return ["  " + printable(line) for line in out]


def data_of(port, result):
    """The data of a LiveTryResult, with the port: every field, null where it has none."""
    fields = result._asdict()
    fields["cure"] = result.cure._asdict() if result.cure is not None else None
    fields["doctor"] = board_doctor.as_dict(result.doctor) if result.doctor is not None else None
    return dict(fields, port=port)


class RunLiveCode(Operation):
    """
    Operation: the live try. `platform_for(project, find_tool)` builds the FirmwarePlatform (default: MicroPythonPlatform).
    It builds the LiveTryService over the grant check (the outside's clock), the connection, the probe and the board record,
    and runs it. An answer that is no `ran`, or a reset that failed, is one Finding of the status of `board_live.exit_code`,
    with the answer for its code (`reset_failed` after a failed reset). A tool, the look or the board record that stops
    is one unchecked item, and its data holds the empty fields.
    """

    name = "live"
    arguments = (Argument(("--code",), "code", str, "the code to run on the board, e.g. 'print(1)'", required=True),
                 COMMON_ARGUMENTS["project"]._replace(help="the project folder whose boards/active.json names the board and whose tools list "
                                                      "names mpremote (default: here)"),
                 COMMON_ARGUMENTS["port"], COMMON_ARGUMENTS["json"]._replace(help="print one line of JSON"))
    effects = (READS, RUNS, BOARD)
    privacy_for = staticmethod(bench_privacy.privacy_for)
    json_renderer = FlatJsonLine

    def __init__(self, platform_for=None):
        self.platform_for = platform_for or MicroPythonPlatform

    def run(self, code, project, port, *, outside):
        platform = self.platform_for(project, outside.find_tool)
        try:
            finder = platform.make_port_finder(outside.run)
            port = port or finder.require_one_port(SCRIPT)
            probe = platform.make_console_probe(port, outside.run)
            service = board_live.LiveTryService(board_grant.GrantService(finder, now=outside.clock.now),
                                                platform.make_connection(platform.make_shell_command(), port, outside.run), probe,
                                                boards.load(project), board_doctor.BoardDoctorService.for_board(finder, probe),
                                                platform.find_tool("board-shell"))
            result = service.run(code, port)
        except (tools.ToolProblem, board_look.LookStopError, boards.BoardError, BrokenRecordError) as cannot:
            empty = dict.fromkeys(board_live.LiveTryResult._fields)
            return stops.stop_result(cannot, SCRIPT, project, port)._replace(
                data=dict(empty, answer=outcomes.COULD_NOT_RUN, why=str(cannot), port=port))
        places = boards.ButtonPlaces.of_project(project)
        return OperationResult(data_of(port, result), self._findings(result, places), lines=describe(result, places))

    @staticmethod
    def _findings(result, places):
        """No Finding for a clean run; else one of the status of the exit code, coded by the answer or `reset_failed`."""
        status = outcomes.STATUS_FOR[board_live.exit_code(result)]
        if status == outcomes.OK:
            return []
        code = board_codes.RESET_FAILED if result.reset == board_live.RESET_FAILED_STATE else result.answer
        return [Finding(status, None, code, result.why or result.answer, board_envelope.doctor_fix(result.doctor, places))]
# --- end MVP ---
