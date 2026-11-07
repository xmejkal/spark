"""
The deploy as an Operation on the core (P655, W4-2, E2): put the flash image onto the board, after the look, the token
and the person's yes. deploy.py is its CLI. Every line a person read while deploy.py ran is an Event now, each phase
reports a BEGIN, and the result is `board_envelope.deploy_result`, so no golden changed; a crash after the gate, which
says the board may be erased, is the one new output.
"""

import shlex
from collections import namedtuple
from pathlib import Path

import board_codes
from spark.bench import board_doctor
from spark.bench import board_envelope
from spark.bench import board_grant
from spark.bench import board_look
from spark.bench import deploy_gate
from spark.bench import ready_probe
import store
import tools
from spark.bench.board_console import LEAVE_CONSOLE
from spark.bench.deploy_stages import STAGE_FLASH, STAGE_GATE, STAGE_LOOK, STAGE_PLAN, STAGE_VERIFY
from spark.bench.deploy_service import DeployService, FlashError
from spark.bench.firmware_platform import MicroPythonPlatform
from spark.bench.image_evidence import IGNORE_OLDER_RUNS_FLAG, NO_SIMULATION_FLAG, evidence_for
from project_image import DeployError
from spark.bench import bench_privacy
from spark.bench.stops import reason_of
from spark.core import codes, outcomes
from spark.core.cli import CRASH_MESSAGE, CRASHED_MESSAGE, traceback_lines
from spark.core.events import BEGIN, Event, Reporter
from spark.core.operation import ASKS, BOARD, COMMON_ARGUMENTS, DELETES, READS, RUNS, WRITES, Argument, Operation
from spark.core.outcomes import EXIT_COULD_NOT_RUN, EXIT_OK, EXIT_PROBLEMS
from spark.core.result import Finding, NextStep, OperationResult

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


def who_said_yes(consent):
    """Whose yes it was, as a phrase, read once. getpass can find no user (OSError since Python 3.13, KeyError before
    it), and then the phrase says so; the store record names the error itself."""
    try:
        return consent.who
    except (OSError, KeyError) as cannot:
        return "not known (%s)" % cannot


class StageTrackingReporter(Reporter):
    """Decorator: a Reporter that keeps the code of the last BEGIN as `stage`, and passes every event on to `report_on`, the
    outside's report. So the result knows the stage the run reached, the service's BEGINs counted (P655)."""

    def __init__(self, report_on):
        self.report_on, self.stage = report_on, STAGE_PLAN

    def report(self, event):
        if event.kind == BEGIN:
            self.stage = event.code
        self.report_on(event)


#: Value: what the person asked of this deploy: the port, the token look.py printed, and whether it is a dry run.
Asked = namedtuple("Asked", "port token dry_run")
#: Value: what the result says of the board after a crash in `stage`: `data.board_state`, the words of the sentence, the fix.
CrashState = namedtuple("CrashState", "board_state words fix")
CRASH_STATES = {
    STAGE_FLASH: CrashState(board_envelope.MAY_BE_ERASED, "may be erased", "run look.py, then deploy again"),
    STAGE_VERIFY: CrashState(board_envelope.FLASHED_NOT_VERIFIED, "is flashed, not verified", "read the board with look.py; do not deploy again"),
}
CRASH_WHY_LOOK = "the deploy crashed: the board %s"


class DeployFlowService:
    """
    Service: one deploy from the plan to the record, phase by phase, over a DeployService built by `service_for`. Each phase
    returns the exit code when the run ends there, or None to go on. `reached()` is what the result reports, filled as the
    run goes; its `stage` is the StageTrackingReporter's. `diagnostics` are the stderr lines.
    """

    def __init__(self, service_for, outside, grants, asked):
        """`service_for(world)` builds the DeployService over `world`, the outside whose `report` tracks the stage. `asked`
        is the Asked of this run."""
        self.outside, self.grants, self.asked = outside, grants, asked
        self.stages = StageTrackingReporter(outside.report)
        self.service = service_for(outside._replace(report=self.stages.report))
        self._reached = {"project": self.service.project.resolve(), "evidence": self.service.evidence,
                         "token": asked.token, "port": asked.port, "dry_run": asked.dry_run}
        self.diagnostics, self.look, self.consent, self.planned = [], None, None, None

    def reached(self):
        """What the run reached so far, with the stage, for `board_envelope.deploy_result`."""
        return dict(self._reached, stage=self.stages.stage)

    def report(self, event):
        self.stages.report(event)

    def say(self, stage, text, raw=False):
        self.report(Event.line(stage, text, raw))

    def keep_yes(self):
        """The yes in `reached`, once there is one: only after the gate passed, or after a flash command ran."""
        if self.consent is not None and "consent" not in self._reached:
            self._reached.update(consent=self.consent, yes_kind=self.consent.yes_kind, who=who_said_yes(self.consent))

    def refuse(self, cannot):
        """The exit code of a refusal before the board was touched, said on stderr as `deploy.py: <why>`."""
        self._reached.update(refusal=str(cannot), reason=reason_of(cannot))
        self.diagnostics.append("%s: %s" % (SCRIPT, cannot))
        return EXIT_COULD_NOT_RUN

    def plan(self):
        """The plan's notes, then in a dry run each command the deploy would run and the REPL line, and the run ends."""
        self.report(Event.begin(STAGE_PLAN))
        try:
            planned = self._reached["plan"] = self.service.plan(self.asked.port)
        except (DeployError, tools.ToolProblem) as cannot:
            return self.refuse(cannot)
        for note in planned.notes:
            self.say(STAGE_PLAN, "note: %s" % note)
        if not self.asked.dry_run:
            return None
        for command in planned.commands:
            self.say(STAGE_PLAN, "would run: %s" % shlex.join(command), raw=True)  # P677: a command a person may run
        self.say(STAGE_PLAN, "board: not looked at: run look.py")
        self.say(STAGE_PLAN, WATCH % shlex.join(self.service.platform.make_connection(planned.mpremote, self.asked.port, self.outside.run).repl_command()),
                 raw=True)
        return EXIT_OK

    def look_and_flash(self):
        """The look and its lines, the yes, the gate, then the flash. A refusal is said on stderr; a failed read gets the
        doctor (P354); a closed gate gives the line to run in the terminal."""
        reached, token = self._reached, self.asked.token
        try:
            self.report(Event.begin(STAGE_LOOK))
            look = self.look = reached["report"] = self.service.look(self.asked.port)
            for line in board_look.report_lines(look, token=False, indent=""):
                self.say(STAGE_LOOK, line)
            reached["port"] = look.port
            self.report(Event.begin(STAGE_GATE))  # before the "standing yes" line, which is a gate line
            self.consent = self.choose_consent(look, token)
            self.planned = self.service.deploy(look, token, self.consent)
            self.keep_yes()  # only now is there a yes to report
        except (board_look.LookStopError, DeployError, tools.ToolProblem) as cannot:
            if isinstance(cannot, FlashError):
                self.keep_yes()
            reached.update(refusal=str(cannot), reason=reason_of(cannot))
            lines = ["%s: %s" % (SCRIPT, cannot)]
            if isinstance(cannot, board_look.LookStopError):
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
        project, evidence = self._reached["project"], self._reached["evidence"]
        line = rerun_line(project, token, look.port, evidence)
        if board_grant.grant_may_cover(look, evidence):
            line += grant_hint(project, look.port)
        chosen = self.grants.consent_for_deploy(look, evidence, self.outside.make_consent(line))
        if chosen.why not in WHY_NOT_SAID:
            # raw: the sentence may hold the grant line the person pastes (P677)
            self.say(STAGE_GATE, "standing yes: not used: %s" % (board_grant.DEPLOY_MESSAGE_FOR.get(chosen.why) or board_grant.MESSAGE_FOR[chosen.why]), raw=True)
        return chosen.consent

    def verify(self):
        """The board after the flash: the facts, ready, the board log, the store record, and the REPL line when ready is unknown."""
        reached = self._reached
        self.report(Event.begin(STAGE_VERIFY))
        result = reached["result"] = self.service.verify(self.look, self.planned)
        ready = result.ready
        if ready.verdict != ready_probe.SEEN:
            reached.update(refusal=ready.sentence, reason=(result.start and result.start.code) or board_codes.READY_UNKNOWN
                           if ready.verdict == ready_probe.UNKNOWN else board_codes.READY_NOT_SEEN)
        for line in (result.facts_line, DEPLOYED_LINE % (result.image_sha256, reached["who"]), "%s: %s" % (ready.verdict, ready.sentence)):
            self.say(STAGE_VERIFY, line)
        self.say(STAGE_VERIFY, "board log: %s" % result.log_path, raw=True)  # P677: a file a person opens, as data.board_log
        try:
            reached["store_record"] = str(self.service.record(result, self.consent))
            self.say(STAGE_VERIFY, "store record: %s" % reached["store_record"])
        except (OSError, KeyError, store.StoreProblem) as cannot:  # KeyError: getpass before Python 3.13
            reached["store_record_error"] = str(cannot)
            reached["notes"] = ["the store record was not written: %s" % cannot]
            self.say(STAGE_VERIFY, "store record: not written: %s" % cannot)
        if ready.verdict == ready_probe.UNKNOWN:
            if result.start is None or result.start.port:  # P462: with the port gone there is nothing to watch
                self.say(STAGE_VERIFY, WATCH % shlex.join(result.repl_command), raw=True)
            return EXIT_COULD_NOT_RUN
        return EXIT_OK if ready.verdict == ready_probe.SEEN else EXIT_PROBLEMS


class DeployImage(Operation):
    """
    Operation: the deploy. It builds the evidence (image_evidence), the platform and a DeployFlowService, and returns
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
    effects = (READS, RUNS, BOARD, DELETES, WRITES, ASKS)
    privacy_for = staticmethod(bench_privacy.privacy_for)

    def __init__(self, platform_for=None, grant_service=None, records=None):
        self.platform_for = platform_for or MicroPythonPlatform
        self.grant_service, self.records = grant_service, records

    def effects_of(self, values):
        if not values["dry_run"]:
            return self.effects
        return (READS, RUNS) if values["no_simulation"] else (READS,)

    def run(self, project, port, token, ignore_older_runs, no_simulation, dry_run, *, outside):
        evidence = evidence_for(project, no_simulation, ignore_older_runs, outside.find_tool)
        platform = self.platform_for(project, outside.find_tool)
        flow = DeployFlowService(lambda world: DeployService(project, platform, evidence, world, self.records), outside,
                                 self.grant_service or board_grant.GrantService(), Asked(port, token, dry_run))
        code = flow.plan()
        try:
            if code is None:
                code = flow.look_and_flash()
            if code is None:
                code = flow.verify()
        except Exception as crashed:  # noqa: BLE001  after the gate the board may be erased: the result must say so
            if flow.stages.stage not in CRASH_STATES:
                raise
            return self._crashed(flow, crashed)
        return board_envelope.deploy_result(flow.reached(), code, flow.diagnostics)

    def _crashed(self, flow, crashed):
        """The result of a crash after the gate passed: one unchecked Finding with code `crash` that names the board's state,
        the data reached with the yes and `board_state`, the look as the next step, and the traceback in the diagnostics."""
        flow.keep_yes()  # a crash in the flash loop still says whose yes it was
        reached, name = flow.reached(), type(crashed).__name__
        state = CRASH_STATES[reached["stage"]]
        data = dict(board_envelope.deploy_data(reached), board_state=state.board_state)
        finding = Finding(outcomes.COULD_NOT_RUN, reached["stage"], codes.CRASH, "%s; the board %s" % (CRASH_MESSAGE % name, state.words), state.fix)
        look = NextStep(**board_envelope.look_step(reached["project"], reached.get("port"), reached["evidence"], CRASH_WHY_LOOK % state.words))
        return OperationResult(data, [finding], [look],
                               diagnostics=flow.diagnostics + [CRASHED_MESSAGE % (self.name, name), state.fix] + traceback_lines(crashed))
# --- end MVP ---
