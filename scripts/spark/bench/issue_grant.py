"""
The grant as an Operation on the core (P657, W4-3): read the board on USB once, ask the person for the yes in their own
terminal, and keep a grant for a time limit. grant.py --minutes is its CLI. The restart notice is an Event of the look, the
yes comes through the outside's `make_consent` (it declares ASKS), and a closed gate is a Finding of the gate's own exit code.
"""

import shlex
from pathlib import Path

from spark.bench import board_doctor
from spark.bench import board_grant
from spark.bench import board_look
import boards
from spark.bench import flasher
import store
import tools
from spark.bench.deploy_gate import GateClosedError, format_rerun_line
from spark.bench.deploy_stages import STAGE_LOOK
from spark.bench.firmware_platform import MicroPythonPlatform
from spark.bench import bench_privacy
from spark.bench.stops import stop_result
from spark.core import outcomes
from spark.core.renderers import FlatJsonLine
from spark.core.events import Event
from spark.core.operation import ASKS, BOARD, COMMON_ARGUMENTS, READS, RUNS, Argument, Operation
from spark.core.privacy import PastedLine
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import guard_lines, guard_sentence, printable

# --- MVP ---
#: The lines of a refusal name the script that printed them before the core, so they read the same from every frontend.
SCRIPT = "grant.py"
#: The script a person runs in their own terminal, by its path (P283): the rerun line names it.
GRANT_SCRIPT = Path(__file__).resolve().parents[2] / SCRIPT
RESTART = ("the board restarts while it is read: a running program stops and starts again. Nothing is erased or "
           "written. If it then waits in download mode, press its %(reset)s once%(orientation)s.")
SCOPE_HELP = ("with --minutes: what the grant allows. live (default) lets Claude run code on the board. deploy lets Claude "
              "erase it and write a passed image with deploy.py, with no yes typed for each deploy")
DEPLOY_NOTICE = ("  Claude can now run deploy.py on this board with no yes from you, and it erases ALL of the board's "
                 "flash each time, until that time. To end it sooner, run: rm %s")


class IssueGrant(Operation):
    """
    Operation: the grant. `platform_for(project, find_tool)` builds the FirmwarePlatform (default: MicroPythonPlatform). It reads
    the board once (the board restarts, and an Event says so), asks `outside.make_consent(line)` and keeps the grant. A closed
    gate is one Finding of the gate's exit code: a problem for 1, an unchecked item for 2; a tool, the store or the look that stops is
    one unchecked item. It has no `--json`, so its data (the grant) is for an agent or an MCP tool.
    """

    name = "issue-grant"
    arguments = (Argument(("--minutes",), "minutes", int, "give a grant for this many minutes from your yes (1 to 1440)", required=True),
                 Argument(("--scope",), "scope", str, SCOPE_HELP, board_grant.SCOPE_LIVE, choices=board_grant.SCOPES),
                 COMMON_ARGUMENTS["project"]._replace(help="the project folder whose tools list names mpremote and esptool (default: here)"),
                 COMMON_ARGUMENTS["port"])
    effects = (READS, RUNS, BOARD, ASKS)
    privacy_for = staticmethod(bench_privacy.privacy_for)
    json_renderer = FlatJsonLine

    def __init__(self, platform_for=None):
        self.platform_for = platform_for or MicroPythonPlatform

    def run(self, minutes, scope, project, port, *, outside):
        platform = self.platform_for(project, outside.find_tool)
        places = boards.ButtonPlaces.of_project(project)
        try:
            finder = platform.make_port_finder(outside.run)
            reader = platform.make_board_reader(outside.run, flasher.EsptoolFlasher.boot_hint_for(places))
            grant = board_grant.GrantService(finder, reader, now=outside.clock.now).issue(
                port, minutes, outside.make_consent(self._rerun_line(minutes, scope, project, port)),
                before_look=lambda: self._tell_restart(outside, places), scope=scope)
        except GateClosedError as closed:
            # P430: the closed gate's sentence holds the rerun line: the project path and the port, quoted as that line quotes them
            said = guard_sentence("%s: %s" % (SCRIPT, closed), shlex.quote(str(project.resolve())), shlex.quote(port) if port else None)
            return OperationResult(None, [Finding(outcomes.STATUS_FOR[closed.code], None, closed.reason, str(closed), "")], diagnostics=[said])
        except (tools.ToolProblem, board_look.LookStop, store.StoreProblem) as cannot:  # P499: a store that refuses
            return stop_result(cannot, SCRIPT, project, port, lambda stop: board_doctor.stop_answer(SCRIPT, stop, platform, outside.run))
        lines = [guard_lines("  granted (%s): board %s (token %s) until %s" % (grant.scope, grant.mac, grant.board_token, grant.expires_at))]
        if grant.scope == board_grant.SCOPE_DEPLOY:
            grant_file = store.place("grants") / (board_grant.GrantStore.key(grant.mac, grant.scope) + ".json")
            lines.append(PastedLine(DEPLOY_NOTICE % shlex.quote(printable(str(grant_file)))))  # P430: one line; P677: its rm line runs
        return OperationResult(grant._asdict(), lines=lines)

    @staticmethod
    def _rerun_line(minutes, scope, project, port):
        """The line that runs this grant again, for the person's own terminal."""
        return format_rerun_line(GRANT_SCRIPT, (["--scope", scope] if scope != board_grant.SCOPE_LIVE else [])
                                 + ["--minutes", minutes, "--project", project.resolve()] + (["--port", port] if port else []))

    @staticmethod
    def _tell_restart(outside, places):
        """The look begins, and the person reads that the board restarts (an Event, so the terminal indents it)."""
        outside.report(Event.begin(STAGE_LOOK))
        text = RESTART % {"reset": places.reset, "orientation": places.orientation}
        outside.report(Event.line(STAGE_LOOK, guard_sentence(text, places.reset, places.orientation)))  # P430: button words are data
# --- end MVP ---
