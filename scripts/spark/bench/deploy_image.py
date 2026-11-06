"""
The deploy as an Operation on the core (P655, W4-2, E2): put the flash image onto the board, after the look, the token
and the person's yes. deploy.py is its CLI. Every line a person read while deploy.py ran is an Event now, each phase
reports a BEGIN, and the result is `board_envelope.deploy_result`, so no golden changed; a crash after the gate, which
says the board may be erased, is the one new output.
"""

import shlex
from pathlib import Path

import board_codes
import board_doctor
import board_envelope
import board_grant
import board_look
import deploy_gate
import ready_check
import store
import tools
from board_console import LEAVE_CONSOLE
from board_envelope import STAGE_FLASH, STAGE_GATE, STAGE_LOOK, STAGE_PLAN, STAGE_VERIFY
from deploy_service import DeployService, FlashError
from firmware_platform import MicroPythonPlatform
from image_evidence import IGNORE_OLDER_RUNS_FLAG, NO_SIMULATION_FLAG, evidence_for
from project_image import DeployError
from spark.core import codes, outcomes
from spark.core.cli import CRASH_MESSAGE, CRASHED_MESSAGE, traceback_lines
from spark.core.events import BEGIN, Event
from spark.core.operation import BOARD, COMMON_ARGUMENTS, DELETES, READS, RUNS, WRITES, Argument, Operation
from spark.core.outcomes import EXIT_COULD_NOT_RUN, EXIT_OK, EXIT_PROBLEMS
from spark.core.outside import OutsideWorld
from spark.core.result import Finding, OperationResult

# --- MVP ---
#: The lines of a refusal name the script that printed them before the core, so they read the same from every frontend.
SCRIPT = "deploy.py"
#: The scripts a person runs in their own terminal, by their path (P283): the rerun line and the grant line name them.
DEPLOY_SCRIPT = Path(__file__).resolve().parents[2] / SCRIPT
GRANT_SCRIPT = DEPLOY_SCRIPT.with_name("grant.py")
#: The group of the two flags that pick the evidence: they exclude each other.
EVIDENCE_GROUP = "evidence"
#: The line after a deploy that names the image on the board and whose yes erased it (P213, card A).
DEPLOYED_LINE = "image sha256: %s, yes: %s"
#: The last line: how the person sees the firmware start.
WATCH = ("then, to see it start: %%s, press Ctrl-C, then Ctrl-D: the firmware prints `ready`. Then %s: an open "
         "console holds the port, and the next deploy cannot open it" % LEAVE_CONSOLE)
#: The fix of a crash after the gate: the board's state is not known until the look reads it.
CRASH_AFTER_GATE_FIX = "run look.py, then deploy again"
#: What the person did not get told of a grant that was not used: with no grant, the no-terminal text says it all.
WHY_NOT_SAID = (None, board_grant.WHY_NO_GRANT)


def rerun_line(project, token, port, evidence):
    """The line that runs this deploy again, for the person's own terminal."""
    return deploy_gate.format_rerun_line(DEPLOY_SCRIPT, board_envelope.deploy_argv(project.resolve(), token, port, evidence))


def grant_argv(project, port, minutes="N"):
    """The arguments of grant.py that give a deploy grant for this board."""
    return ["--scope", board_grant.SCOPE_DEPLOY, "--minutes", minutes, "--project", str(project.resolve()), "--port", port]


def grant_hint(project, port):
    """The text added to the no-terminal line when a deploy grant could make the yes unnecessary: the line the person
    runs once in their own terminal to give it."""
    line = deploy_gate.format_rerun_line(GRANT_SCRIPT, grant_argv(project, port))
    return ("\nOr, to let Claude deploy this board for N minutes (1 to 1440) with no yes each time, run this once. It "
            "allows an erase of ALL of the flash and any passed image of any project:\n  %s" % line)


def reason_of(refusal):
    """The board_codes code for a refusal that deploy catches: the `reason` of a LookStop or a DeployError (a FlashError
    too), and tool_missing for a tools.ToolProblem (P433)."""
    return board_codes.TOOL_MISSING if isinstance(refusal, tools.ToolProblem) else refusal.reason


def who_said_yes(consent):
    """Whose yes it was, as a phrase, read once. getpass can find no user (OSError since Python 3.13, KeyError before
    it), and then the phrase says so; the store record names the error itself."""
    try:
        return consent.who
    except (OSError, KeyError) as cannot:
        return "not known (%s)" % cannot


class DeployRun:
    """
    Service: one deploy from the plan to the record, phase by phase, over a DeployService. Each phase returns the exit
    code when the run ends there, or None to go on. `reached` is what the result reports, filled as the run goes; its
    `stage` follows each BEGIN that passes through `report`, the service's too. `diagnostics` are the stderr lines.
    """

    def __init__(self, project, evidence, platform, outside, grants, records):
        self.outside, self.grants = outside, grants
        self.reached = {"project": project.resolve(), "evidence": evidence, "stage": STAGE_PLAN}
        self.diagnostics, self.look, self.consent, self.planned = [], None, None, None
        self.service = DeployService(project, platform, evidence, OutsideWorld(outside.run, outside.find_tool, self.report,
                                                                               outside.clock, outside.make_consent), records)

    def report(self, event):
        """The outside's report, and a BEGIN also moves `reached["stage"]`."""
        if event.kind == BEGIN:
            self.reached["stage"] = event.code
        self.outside.report(event)

    def say(self, stage, text):
        self.report(Event.line(stage, text))

    def refuse(self, cannot):
        """The exit code of a refusal before the board was touched, said on stderr as `deploy.py: <why>`."""
        self.reached.update(refusal=str(cannot), reason=reason_of(cannot))
        self.diagnostics.append("%s: %s" % (SCRIPT, cannot))
        return EXIT_COULD_NOT_RUN

    def plan(self, port, dry_run):
        """The plan's notes, then with `dry_run` each command the deploy would run and the REPL line, and the run ends."""
        self.report(Event.begin(STAGE_PLAN))
        try:
            planned = self.reached["plan"] = self.service.plan(port)
        except (DeployError, tools.ToolProblem) as cannot:
            return self.refuse(cannot)
        for note in planned.notes:
            self.say(STAGE_PLAN, "note: %s" % note)
        if not dry_run:
            return None
        for command in planned.commands:
            self.say(STAGE_PLAN, "would run: %s" % shlex.join(command))
        self.say(STAGE_PLAN, "board: not looked at: run look.py")
        self.say(STAGE_PLAN, WATCH % shlex.join(self.service.platform.make_connection(planned.mpremote, port, self.outside.run).repl_command()))
        return EXIT_OK

    def gate(self, port, token):
        """The look, its lines, the yes, the gate and the flash. A refusal is said on stderr; a failed read gets the doctor (P354)."""
        reached = self.reached
        try:
            self.report(Event.begin(STAGE_LOOK))
            look = self.look = reached["report"] = self.service.look(port)
            for line in board_look.report_lines(look, token=False, indent=""):
                self.say(STAGE_LOOK, line)
            reached["port"] = look.port
            consent = self.consent = self.choose_consent(look, token)
            self.report(Event.begin(STAGE_GATE))
            self.planned = self.service.deploy(look, token, consent)
            reached.update(consent=consent, yes_kind=consent.yes_kind, who=who_said_yes(consent))  # only now is there a yes to report
        except (board_look.LookStop, DeployError, tools.ToolProblem) as cannot:
            if isinstance(cannot, FlashError):
                reached.update(consent=consent, yes_kind=consent.yes_kind, who=who_said_yes(consent))
            reached.update(refusal=str(cannot), reason=reason_of(cannot))
            lines = ["%s: %s" % (SCRIPT, cannot)]
            if isinstance(cannot, board_look.LookStop):
                lines, reached["doctor"] = board_doctor.stop_answer(SCRIPT, cannot, self.service.platform, self.outside.run)
            self.diagnostics += lines
            return EXIT_COULD_NOT_RUN
        except deploy_gate.GateClosedError as shut:
            reached.update(refusal=str(shut), reason=shut.reason, next_op=shut.next_op)
            if shut.next_op == deploy_gate.NEXT_DEPLOY:
                reached["run_in_terminal"] = rerun_line(reached["project"], token, look.port, reached["evidence"])
                if board_grant.grant_may_cover(look, reached["evidence"]):
                    reached["grant_argv"] = grant_argv(reached["project"], look.port, "60")
            self.diagnostics.append("%s: %s" % (SCRIPT, shut))
            return shut.code
        return None

    def choose_consent(self, look, token):
        """The ConsentStrategy for this deploy, after the look: the standing yes of a valid deploy grant when the look
        matched and the evidence allows it (a passed run's, with no ignored older run), else the outside's, which asks the
        person. One line says why the grant was not used, unless there is none."""
        project, evidence = self.reached["project"], self.reached["evidence"]
        line = rerun_line(project, token, look.port, evidence)
        if board_grant.grant_may_cover(look, evidence):
            line += grant_hint(project, look.port)
        chosen = self.grants.consent_for_deploy(look, evidence, self.outside.make_consent(line))
        if chosen.why not in WHY_NOT_SAID:
            self.say(STAGE_GATE, "standing yes: not used: %s" % (board_grant.DEPLOY_MESSAGE_FOR.get(chosen.why) or board_grant.MESSAGE_FOR[chosen.why]))
        return chosen.consent

    def verify(self):
        """The board after the flash: the facts, ready, the board log, the store record, and the REPL line when ready is unknown."""
        reached = self.reached
        self.report(Event.begin(STAGE_VERIFY))
        result = reached["result"] = self.service.verify(self.look, self.planned)
        ready = result.ready
        if ready.verdict != ready_check.SEEN:
            reached.update(refusal=ready.sentence, reason=(result.start and result.start.code) or board_codes.READY_UNKNOWN
                           if ready.verdict == ready_check.UNKNOWN else board_codes.READY_NOT_SEEN)
        for line in (result.facts_line, DEPLOYED_LINE % (result.image_sha256, reached["who"]),
                     "%s: %s" % (ready.verdict, ready.sentence), "board log: %s" % result.log_path):
            self.say(STAGE_VERIFY, line)
        try:
            reached["store_record"] = str(self.service.record(result, self.consent))
            self.say(STAGE_VERIFY, "store record: %s" % reached["store_record"])
        except (OSError, KeyError, store.StoreProblem) as cannot:  # KeyError: getpass before Python 3.13
            reached["store_record_error"] = str(cannot)
            reached["notes"] = ["the store record was not written: %s" % cannot]
            self.say(STAGE_VERIFY, "store record: not written: %s" % cannot)
        if ready.verdict == ready_check.UNKNOWN:
            if result.start is None or result.start.port:  # P462: with the port gone there is nothing to watch
                self.say(STAGE_VERIFY, WATCH % shlex.join(result.repl_command))
            return EXIT_COULD_NOT_RUN
        return EXIT_OK if ready.verdict == ready_check.SEEN else EXIT_PROBLEMS


class DeployImage(Operation):
    """
    Operation: the deploy. It builds the evidence (image_evidence), the platform and a DeployRun, and returns
    `board_envelope.deploy_result`. `platform_for(project, find_tool)` is a `_for` builder of the FirmwarePlatform
    (default: MicroPythonPlatform), `grant_service` the board_grant.GrantService that finds a deploy grant and `records`
    the DeployRecordStore (None for the store's own, built per run): the collaborators a test swaps whole. The dry run
    declares READS alone (RUNS with --no-simulation, whose compile check runs a child), so `outside.run` refuses.
    """

    name = "deploy"
    arguments = (COMMON_ARGUMENTS["project"]._replace(help="the project folder with sim/ and requirements.json (default: here)"),
                 COMMON_ARGUMENTS["port"]._replace(help="the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more "
                                                   "boards on USB: the look lists them"),
                 Argument(("--token",), "token", str, "the token look.py printed for this board and this image"),
                 Argument((IGNORE_OLDER_RUNS_FLAG,), "ignore_older_runs", bool,
                          "flash even when a log in sim/runs/ tested another image, and name it in a note (default: refuse)", group=EVIDENCE_GROUP),
                 Argument((NO_SIMULATION_FLAG,), "no_simulation", bool,
                          "flash an image that no simulation tested: firmware/ must have a main.py, compile and be what the "
                          "image holds. Needs look.py --no-simulation. The person's typed yes names the caveat", group=EVIDENCE_GROUP),
                 Argument(("--dry-run",), "dry_run", bool, "print each command and run nothing"),
                 COMMON_ARGUMENTS["json"]._replace(help="print one envelope on stdout, the lines a person reads on stderr (docs/guide/agents/json.md)"))
    effects = (READS, RUNS, BOARD, DELETES, WRITES)

    def __init__(self, platform_for=None, grant_service=None, records=None):
        self.platform_for = platform_for or MicroPythonPlatform
        self.grant_service, self.records = grant_service, records

    def effects_of(self, values):
        if not values["dry_run"]:
            return self.effects
        return (READS, RUNS) if values["no_simulation"] else (READS,)

    def run(self, project, port, token, ignore_older_runs, no_simulation, dry_run, *, outside):
        evidence = evidence_for(project, no_simulation, ignore_older_runs, outside.find_tool)
        going = DeployRun(project, evidence, self.platform_for(project, outside.find_tool), outside,
                          self.grant_service or board_grant.GrantService(), self.records)
        going.reached.update(token=token, port=port, dry_run=dry_run)
        code = going.plan(port, dry_run)
        try:
            if code is None:
                code = going.gate(port, token)
            if code is None:
                code = going.verify()
        except Exception as crashed:  # noqa: BLE001  after the gate the board may be erased: the result must say so
            if going.reached["stage"] not in (STAGE_FLASH, STAGE_VERIFY):
                raise
            return self._crashed(going, crashed)
        return board_envelope.deploy_result(going.reached, code, going.diagnostics)

    @staticmethod
    def _crashed(going, crashed):
        """The result of a crash after the gate passed: one unchecked Finding with code `crash`, the data reached with the
        board's state, and the traceback in the diagnostics, as the core's crash prints it."""
        name = type(crashed).__name__
        data = dict(board_envelope.deploy_data(going.reached), board_state=board_envelope.MAY_BE_ERASED)
        return OperationResult(data, [Finding(outcomes.COULD_NOT_RUN, going.reached["stage"], codes.CRASH, CRASH_MESSAGE % name, CRASH_AFTER_GATE_FIX)],
                               diagnostics=going.diagnostics + [CRASHED_MESSAGE % (SCRIPT, name), CRASH_AFTER_GATE_FIX] + traceback_lines(crashed))
# --- end MVP ---
