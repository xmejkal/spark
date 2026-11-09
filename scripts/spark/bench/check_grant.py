"""
The grant check as an Operation on the core (P657, W4-3): say whether the board on USB has a live grant now, with
`mpremote devs` only. grant.py --check is its CLI, and its `--json` line is the flat one (`FlatJsonLine`): granted, why
(a WHY_ word or null) and the grant's fields or null, so no golden changed. A grant that is not there is one problem; a run that
could not look is one unchecked item, with `why` "could not run" in the data.
"""

from spark.bench import board_doctor
from spark.bench import board_grant
from spark.bench import board_look
from spark.records import store
from spark.records import tool_finder
from spark.bench.firmware_platform import MicroPythonPlatform
from spark.bench import bench_privacy
from spark.bench.stops import stop_result
from spark.core import outcomes
from spark.core.renderers import FlatJsonLine
from spark.core.operation import COMMON_ARGUMENTS, READS, RUNS, Argument, Operation
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import guard_lines

# --- MVP ---
#: The lines of a stop name the script that printed them before the core, so they read the same from every frontend.
SCRIPT = "grant.py"
#: The data of a check that could not look.
COULD_NOT_RUN_DATA = {"granted": False, "why": board_grant.WHY_COULD_NOT_RUN, "grant": None}


def describe(result):
    """The line a person reads, for a GrantCheckResult."""
    if result.granted:
        return "  granted: board %s until %s" % (result.grant.mac, board_grant.say_in_local_zone(result.grant.expires_at))
    return "  not granted: %s" % board_grant.MESSAGE_FOR[result.why]


def data_of(result):
    """The data of a GrantCheckResult: granted, why (a code or null), and the grant's fields or null."""
    return {"granted": result.granted, "why": result.why, "grant": result.grant._asdict() if result.grant is not None else None}


class CheckGrant(Operation):
    """
    Operation: the grant check. `platform_for(project, find_tool)` builds the FirmwarePlatform (default: MicroPythonPlatform).
    It runs only `mpremote devs`, so the running program goes on. `--check` is kept so that the flag parses: it picks this
    Operation (grant.operation_for). A grant that holds is no Finding; one that does not is one problem with the WHY_ word's code.
    """

    name = "check-grant"
    arguments = (Argument(("--check",), "check", bool, "say whether the board on USB has a live grant now"),
                 COMMON_ARGUMENTS["project"]._replace(help="the project folder whose tools list names mpremote (default: here)"),
                 COMMON_ARGUMENTS["port"], COMMON_ARGUMENTS["json"]._replace(help="print one line of JSON: granted, why and the grant"))
    effects = (READS, RUNS)
    privacy_for = staticmethod(bench_privacy.privacy_for)
    json_renderer = FlatJsonLine

    def __init__(self, platform_for=None):
        self.platform_for = platform_for or MicroPythonPlatform

    def run(self, project, port, *, outside, check=True):
        platform = self.platform_for(project, outside.find_tool)
        try:
            finder = platform.make_port_finder(outside.run)
            result = board_grant.GrantService(finder, now=outside.clock.now).check(port)
        except (tool_finder.ToolProblem, board_look.LookStopError, store.StoreProblem) as cannot:
            doctor_for = lambda stop: board_doctor.stop_answer(SCRIPT, stop, platform, outside.run)  # noqa: E731
            return stop_result(cannot, SCRIPT, project, port, doctor_for)._replace(data=dict(COULD_NOT_RUN_DATA))
        findings = [] if result.granted else [Finding(outcomes.PROBLEMS, None, board_grant.CODE_FOR_WHY[result.why],
                                                     board_grant.MESSAGE_FOR[result.why], "")]
        return OperationResult(data_of(result), findings, lines=[guard_lines(describe(result))])  # P430: the MAC is data
# --- end MVP ---
