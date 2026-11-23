"""
The deploy as an Operation on the core (P655, W4-2, E2): put the flash image onto the board, after the look, the token
and the person's yes. deploy.py is its CLI. Every line a person read while deploy.py ran is an Event now, each phase
reports a BEGIN, and the result is `board_envelope.deploy_result`. A crash after the gate, which says the board may be
erased, and the one `why:` line after each BEGIN (P476) are the new output.
"""

import shlex
from collections import namedtuple
from pathlib import Path

from spark.bench import board_codes
from spark.bench import board_doctor
from spark.bench import board_envelope
from spark.bench import board_grant
from spark.bench import board_look
from spark.bench import deploy_gate
from spark.bench import download_mode
from spark.bench import known_board
from spark.bench import ready_probe
from spark.records import board_records
from spark.records import store
from spark.records import tool_finder
from spark.bench.board_console import LEAVE_CONSOLE
from spark.bench.deploy_stages import DEPLOY_STAGES, PHASE_WHY, DeployPhase
from spark.bench.deploy_service import DeployService, FlashError
from spark.bench.firmware_platform import MicroPythonPlatform
from spark.bench.image_evidence import IGNORE_OLDER_RUNS_FLAG, NO_SIMULATION_CAVEAT, NO_SIMULATION_FLAG, SIMULATION_NONE, evidence_for
from spark.firmware.project_image import DeployError
from spark.bench import bench_privacy
from spark.bench.stops import reason_of
from spark.core import codes, outcomes
from spark.core.cli import CRASH_MESSAGE, CRASHED_MESSAGE, traceback_lines
from spark.core.errors import SparkError
from spark.core.events import BEGIN, Event, Reporter
from spark.core.operation import ASKS, BOARD, COMMON_ARGUMENTS, DELETES, READS, RUNS, WRITES, Argument, Operation
from spark.core.outcomes import EXIT_COULD_NOT_RUN, EXIT_OK, EXIT_PROBLEMS
from spark.core.replies import RepliesStore
from spark.core.renderers import StatusLine
from spark.core.result import Finding, Headline, NextStep, OperationResult

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
#: The help of the deploy's --replies (P892): the agent's own file, after the person's yes to the board question.
REPLIES_HELP = ('a file of your own with the person\'s yes to the deploy\'s board question, {"replies": {"<key>": true}}. One yes '
                "answers one deploy: the deploy sets it back to null before it reads. The erase asks its own yes")
#: Why the look is the next step after a stop at the board (P892), by the stop's code, and after a read of another board.
LOOK_WHY = {board_codes.OTHER_BOARD: "the board on USB is not this project's kept board: the look asks the person before it reads it",
            board_codes.NO_KNOWN_BOARD: "spark keeps no board for this project yet: the look asks the person once and keeps it"}
LOOK_WHY_AFTER_READ = "the board read is not this project's kept board: plug in the kept board, or read this one with the look"
#: The refusals from the look to the flash that one handler says (P354, P892).
REFUSALS = (board_look.LookStopError, DeployError, tool_finder.ToolError, SparkError)


def rerun_line(project, token, port, evidence):
    """The line that runs this deploy again, for the person's own terminal."""
    return deploy_gate.format_rerun_line(DEPLOY_SCRIPT, board_envelope.deploy_argv(project.resolve(), token, port, evidence))


def grant_argv(project, port, evidence, minutes="N"):
    """The arguments of grant.py that give a deploy grant for this board, with --no-simulation for an image that no
    simulation tested (P1029)."""
    return ["--scope", board_grant.SCOPE_DEPLOY, "--minutes", minutes, "--project", str(project.resolve()), "--port", port] + (
        [NO_SIMULATION_FLAG] if evidence.simulation == SIMULATION_NONE else [])


def grant_hint(project, port, evidence):
    """The text added to the no-terminal line when a deploy grant could make the yes unnecessary: the line the person
    runs once in their own terminal to give it."""
    line = deploy_gate.format_rerun_line(GRANT_SCRIPT, grant_argv(project, port, evidence))
    allows = (" and any passed image of any project" if evidence.simulation != SIMULATION_NONE else
              ", any passed image of any project, and firmware that no simulation tested")
    return ("\nOr, to let Claude deploy this board for N minutes (1 to 1440) with no yes each time, run this once. It "
            "allows an erase of ALL of the flash%s:\n  %s" % (allows, line))


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
        self.report_on, self.stage = report_on, DeployPhase.PLAN

    def report(self, event):
        if event.kind == BEGIN:
            self.stage = event.code
        self.report_on(event)


class WhyLineReporter(Reporter):
    """Decorator: a Reporter that passes every event on to `report_on`, and after the BEGIN of a stage reports one LINE that says
    why the stage happens (P476), from `PHASE_WHY`. Any other event passes as it is."""

    def __init__(self, report_on):
        self.report_on = report_on

    def report(self, event):
        self.report_on(event)
        if event.kind == BEGIN and event.code in PHASE_WHY:
            self.report_on(Event.line(event.code, PHASE_WHY[event.code]))


#: Value: what the person asked of this deploy: the port, the token look.py printed, whether it is a dry run, and the
#: replies file or None.
Asked = namedtuple("Asked", "port token dry_run replies")
#: Value: what the result says of the board after a crash in `stage`: `data.board_state`, the words of the sentence, the fix.
CrashState = namedtuple("CrashState", "board_state words fix")
CRASH_STATES = {
    DeployPhase.FLASH: CrashState(board_envelope.MAY_BE_ERASED, "may be erased", "run look.py, then deploy again"),
    DeployPhase.VERIFY: CrashState(board_envelope.FLASHED_NOT_VERIFIED, "is flashed, not verified", "read the board with look.py; do not deploy again"),
}
CRASH_WHY_LOOK = "the deploy crashed: the board %s"
#: The headline of a crash after the gate (P478, D7): the board's state in CRASH_STATES' words.
CRASH_HEADLINE = "The board %s: deploy crashed."


class DeployFlowService:
    """
    Service: one deploy from the plan to the record, phase by phase, over a DeployService built by `service_for`. Each phase
    returns the exit code when the run ends there, or None to go on. `reached()` is what the result reports, filled as the
    run goes; its `stage` is its `tracker`'s, the StageTrackingReporter. Its stderr lines go to `outside.add_diagnostics` as they are
    said (P938).
    """

    def __init__(self, service_for, outside, grants, asked, board_question):
        """`service_for(world)` builds the DeployService over `world`, the outside whose `report` tracks the stage. `asked`
        is the Asked of this run, `board_question` the known_board.KnownBoardService that judges the board before the read."""
        self.outside, self.grants, self.asked, self.board_question = outside, grants, asked, board_question
        self.tracker = StageTrackingReporter(WhyLineReporter(outside.report).report)
        self.service = service_for(outside._replace(report=self.tracker.report))
        self._reached = {"project": self.service.project.resolve(), "evidence": self.service.evidence,
                         "token": asked.token, "port": asked.port, "dry_run": asked.dry_run}
        self.look, self.consent, self.planned, self.judged = None, None, None, None

    def reached(self):
        """What the run reached so far, with the stage, for `board_envelope.deploy_result`."""
        return dict(self._reached, stage=self.tracker.stage)

    def report(self, event):
        self.tracker.report(event)

    def say(self, stage, text, raw=False):
        self.report(Event.line(stage, text, raw))

    def keep_yes(self):
        """The yes in `reached`, once there is one: only after the gate passed, or after a flash command ran."""
        if self.consent is not None and "consent" not in self._reached:
            self._reached.update(consent=self.consent, yes_kind=self.consent.yes_kind, who=who_said_yes(self.consent))

    def refuse(self, cannot):
        """The exit code of a refusal before the board was touched, said on stderr as `deploy.py: <why>`."""
        self._reached.update(refusal=str(cannot), reason=reason_of(cannot))
        self.outside.add_diagnostics(["%s: %s" % (SCRIPT, cannot)])
        return EXIT_COULD_NOT_RUN

    def plan(self):
        """The plan's notes, then in a dry run each command the deploy would run and the REPL line, and the run ends."""
        self.report(Event.begin(DeployPhase.PLAN))
        try:
            planned = self._reached["plan"] = self.service.plan(self.asked.port)
        except (DeployError, tool_finder.ToolError) as cannot:
            return self.refuse(cannot)
        for note in planned.notes:
            self.say(DeployPhase.PLAN, "note: %s" % note)
        if not self.asked.dry_run:
            return None
        for command in planned.commands:
            self.say(DeployPhase.PLAN, "would run: %s" % shlex.join(command), raw=True)  # P677: a command a person may run
        self.say(DeployPhase.PLAN, "board: not looked at: run look.py")
        self.say(DeployPhase.PLAN, WATCH % shlex.join(self.service.platform.make_connection(planned.mpremote, self.asked.port, self.outside.run).repl_command()),
                 raw=True)
        return EXIT_OK

    def ask_for_board(self):
        """The board question before the read (P892), after the BEGIN of the look: the replies file's deploy keys set back to
        null (one yes answers one deploy), a project with no board record stopped before any question, then the board on
        USB judged by the deploy's Touch. A stop ends the run; None goes on to the read."""
        self.report(Event.begin(DeployPhase.LOOK))
        try:
            if self.asked.replies:
                RepliesStore(self.asked.replies).clear(known_board.DEPLOY.prefix)
            board_look.LookService.record_of(self.service.project)
            row = self.service.find_row(self.asked.port)
            self.judged = self.board_question.judge(self.service.project, self.asked.port, row, self.outside.replies)
        except REFUSALS as cannot:
            return self.refuse_at_look(cannot)
        if not self.judged.code:
            return None
        port, question = self.asked.port or row.device, self.judged.question
        return self.stop_at_board(self.judged.findings(known_board.DEPLOY), [question.why] if self.judged.code == codes.NEEDS_REPLY else [],
                                  port=port, board_question=self.judged.data(port),
                                  next_op=deploy_gate.NEXT_LOOK if self.judged.code in LOOK_WHY else None, next_why=LOOK_WHY.get(self.judged.code))

    def stop_at_board(self, findings, more=(), **reached):
        """The exit code of a stop at the board (P892): `findings` and `reached` kept for the result, then each sentence and
        fix said as a line of the look, then `more`. The fix of an open question holds the JSON to paste, so its line is raw
        (P677)."""
        self._reached.update(reached, findings=findings, refusal=findings[-1].sentence, reason=findings[-1].code)
        for found in findings:
            self.say(DeployPhase.LOOK, found.sentence)
            self.say(DeployPhase.LOOK, found.fix, raw=found.code == codes.NEEDS_REPLY)
        for line in more:
            self.say(DeployPhase.LOOK, line)
        return EXIT_COULD_NOT_RUN

    def other_after_read(self, look):
        """The Finding of a board read that is not the kept board (P892): it did restart, and the deploy keeps nothing."""
        return known_board.other_after(self.judged.known, look.port, look.reading.mac, known_board.DEPLOY.after_fix)

    def refuse_at_look(self, cannot):
        """The exit code of a refusal at the look or after it, said on stderr: a LookStopError with the doctor's lines (P354), a
        SparkError (the kept record, the replies file) as one Finding with its own code and fix (P892), any other as
        `deploy.py: <why>`. A FlashError keeps the yes that ran it."""
        reached = self._reached
        if isinstance(cannot, FlashError):
            self.keep_yes()
        reached.update(refusal=str(cannot), reason=cannot.code if isinstance(cannot, SparkError) else reason_of(cannot))
        if isinstance(cannot, SparkError):
            reached["findings"] = [Finding(cannot.status, self.tracker.stage, cannot.code, str(cannot), cannot.fix)]
        lines = ["%s: %s" % (SCRIPT, cannot)]
        if isinstance(cannot, board_look.LookStopError):
            lines, reached["doctor"] = board_doctor.stop_answer(SCRIPT, cannot, self.service.platform, self.outside.run)
            # P1022, P1049: a firmware that deep-sleeps, said as look.py says it; `fix` can also be the doctor's step
            lines, sentence, fix = board_envelope.stop_said(SCRIPT, cannot, (lines, reached["doctor"]), self.asked.port, self.service.project)
            if fix:
                reached.update(refusal=sentence, fix=fix)
                reached["asleep_next"] = board_envelope.asleep_next(fix, reached["project"], reached["evidence"])  # P1048
        self.outside.add_diagnostics(lines)
        return EXIT_COULD_NOT_RUN

    def look_and_flash(self):
        """The read and its lines, the check that the board read is the kept board (P892), the yes, the gate, then the flash. A
        refusal is said on stderr; a failed read gets the doctor (P354); a closed gate gives the line to run in the terminal."""
        reached, token = self._reached, self.asked.token
        try:
            look = self.look = reached["report"] = self.service.look(self.asked.port, listed=self.judged.row)
            for line in board_look.report_lines(look, token=False, indent=""):
                self.say(DeployPhase.LOOK, line)
            reached["port"] = look.port
            if known_board.differs(self.judged.known, look.reading.mac):  # whatever the reply was, before the erase's question
                return self.stop_at_board([self.other_after_read(look)], next_op=deploy_gate.NEXT_LOOK, next_why=LOOK_WHY_AFTER_READ)
            self.report(Event.begin(DeployPhase.GATE))  # before the "standing yes" line, which is a gate line
            self.consent = self.choose_consent(look, token)
            self.planned = self.service.deploy(look, token, self.consent)
            self.keep_yes()  # only now is there a yes to report
        except REFUSALS as cannot:
            return self.refuse_at_look(cannot)
        except deploy_gate.GateClosedError as shut:
            reached.update(refusal=str(shut), reason=shut.reason, next_op=shut.next_op)
            if shut.next_op == deploy_gate.NEXT_DEPLOY:
                reached["run_in_terminal"] = rerun_line(reached["project"], token, look.port, reached["evidence"])
                reached["grant_may_answer"] = self.grants.refusal_of(reached["evidence"]) is None  # P1029: board_envelope.yes_rule
                if self.grants.may_cover(look, reached["evidence"]):
                    reached["grant_argv"] = grant_argv(reached["project"], look.port, reached["evidence"], "60")
            self.outside.add_diagnostics(["%s: %s" % (SCRIPT, shut)])
            return shut.code
        return None

    def choose_consent(self, look, token):
        """The ConsentStrategy for this deploy, after the look: the standing yes of a valid deploy grant when the look
        matched and the evidence allows it (a passed run's, with no ignored older run), else the outside's, which asks the
        person. One line says why the grant was not used, unless there is none."""
        project, evidence = self._reached["project"], self._reached["evidence"]
        line = rerun_line(project, token, look.port, evidence)
        if self.grants.may_cover(look, evidence):
            line += grant_hint(project, look.port, evidence)
        chosen = self.grants.consent_for_deploy(look, evidence, self.outside.make_consent(line))
        if chosen.why not in WHY_NOT_SAID:
            # raw: the sentence may hold the grant line the person pastes (P677)
            self.say(DeployPhase.GATE, "standing yes: not used: %s" % (board_grant.DEPLOY_MESSAGE_FOR.get(chosen.why) or board_grant.MESSAGE_FOR[chosen.why]), raw=True)
        return chosen.consent

    def verify(self):
        """The board after the flash: the facts, ready, the board log, the store record, and the REPL line when ready is unknown."""
        reached = self._reached
        self.report(Event.begin(DeployPhase.VERIFY))
        result = reached["result"] = self.service.verify(self.look, self.planned)
        ready = result.ready
        if ready.verdict != ready_probe.SEEN:
            reached.update(refusal=ready.sentence, reason=(result.start and result.start.code) or board_codes.READY_UNKNOWN
                           if ready.verdict == ready_probe.UNKNOWN else board_codes.READY_NOT_SEEN)
        for line in (result.facts_line, DEPLOYED_LINE % (result.image_sha256, reached["who"]), "%s: %s" % (ready.verdict, ready.sentence)):
            self.say(DeployPhase.VERIFY, line)
        self.say(DeployPhase.VERIFY, "board log: %s" % result.log_path, raw=True)  # P677: a file a person opens, as data.board_log
        try:
            reached["store_record"] = str(self.service.record(result, self.consent))
            self.say(DeployPhase.VERIFY, "store record: %s" % reached["store_record"])
        except (OSError, KeyError, store.StoreError) as cannot:  # KeyError: getpass before Python 3.13
            reached["store_record_error"] = str(cannot)
            reached["notes"] = ["the store record was not written: %s" % cannot]
            self.say(DeployPhase.VERIFY, "store record: not written: %s" % cannot)
        if ready.verdict == ready_probe.UNKNOWN:
            if reached["reason"] == board_codes.READY_UNKNOWN:  # P1022: what spark knows, what it did not do, what to try
                places = board_records.ButtonPlaces.of_project(self.service.project)
                reached["fix"] = board_envelope.ready_unknown_fix(result, places, self.service.sleeps)
                self.say(DeployPhase.VERIFY, reached["fix"])
            if result.start is None or result.start.port:  # P462: with the port gone there is nothing to watch
                self.say(DeployPhase.VERIFY, WATCH % shlex.join(result.repl_command), raw=True)
            return EXIT_COULD_NOT_RUN
        return EXIT_OK if ready.verdict == ready_probe.SEEN else EXIT_PROBLEMS


#: What the deploy does, the paragraphs of deploy.py's `--help` before its `--json` and exit codes, line breaks and all
#: (P855).
DETAILS = """It flashes only an image that a passed run names (sim/runs/*.log), and no log there may name another image
(--ignore-older-runs flashes anyway).

--no-simulation flashes an image that no simulation tested, as the board is the test. Build the image first with
`flash_image.py --project . --files firmware -o <the image: sim/flash-with-firmware.bin until a scenario run writes
the `firmware = ` line of sim/wokwi.toml>`. Then look.py and deploy.py both need
--no-simulation. deploy.py refuses when firmware/main.py is missing, a .py file under firmware/ does not compile (or kills
the compiler, or takes over 30 s), a run in
sim/runs/ failed on this image, or the image is not firmware/ as it is now. It does not run the firmware, so a
firmware that fails on the board shows only after the flash. The question starts with "%s". A typed yes
answers it, or a deploy grant given with --no-simulation (P1029). The spark.json, the board log, the store record and the --json data say
`simulation: none`. It cannot be given with --ignore-older-runs.

It erases the board's flash first. If the erase stops with esptool's exit 2,
it makes one retry after 5 s and prints `retry in 5 s: ...` (P290).
When the board refuses mpremote's raw REPL for the facts copy after the flash, that copy gets one retry after 2 s (P420).

The gate: run look.py first and pass its token. deploy.py looks at the board again (the board restarts) and refuses a
stop (another chip, a flash too small for the image) or a token that is not this board's and this image's. Then it
asks in your terminal, naming every warning: type yes to accept them and erase. Only a real terminal can answer.
A pipe, a script or Claude Code's ! is none, so deploy.py prints the line to run in your own terminal window. It
starts with SPARK_HOME=<your store> when this run had one, so the new window finds the same MicroPython build and
grants. With --json, each step in `next` carries the same store as `env` for a caller to set. "Go ahead"
in a chat is not the yes, and the token is not the yes. --dry-run never touches USB: it does not look.

The board question (P892): the read restarts the board, so before it deploy.py judges the board on USB as look.py does,
and never keeps or replaces a board. The board that look.py kept for this project is read with no question. Another
board stops with other_board, and with no kept board a board that shows a USB serial stops with no_known_board: both
before any read, with no question, and the next step is look.py. A board that spark cannot tell before a read (no USB
serial, with a kept board a serial that its firmware set, a --port that the list does not hold) is asked on every
deploy, with --port too: in your terminal, or by `true` under its deploy.read_board key in the --replies file. One yes
answers one deploy: the deploy sets its deploy. keys back to null before it reads. A yes to the look's key does not
answer it, and a deploy grant does not answer it either. After the read, a MAC that is not the kept board's stops with
other_board before the erase's question, whatever the reply was. With no terminal and no deploy grant, the run then
stops at the erase's yes, and the line to run in your own terminal asks the board question once more.

The one other yes is a deploy grant: you ran `grant.py --scope deploy --minutes N` once in your own terminal, for this
board's MAC. While it lasts, deploy.py takes it as the yes, prints `yes: standing yes typed by ...` and erases with no
question, but only when the look matched the board record (no warning, no unknown field, no stop) and
--ignore-older-runs is not given. --no-simulation needs a grant given with --no-simulation, and no grant answers it
while the file grants/direct_flashing_disallowed is in your store (P1029). Then the token and the check that the image did not change still hold.
For anything else, or with no grant or an ended one, deploy.py asks in the terminal as above and says why it did not use
the grant. The grant covers any passed image of any project on that board. The store's record names whose yes it was.

After the flash it copies spark.json to the board: spark's version, the project, the board type, the MAC, the image's
sha256, each file's sha256 and `simulation` (passed or none). The board log names the file's sha256 and the simulation,
and the store's boards/<MAC>.json adds this deploy with its verdict, its simulation and whose yes it was. Then it reads
the board: ready seen means the board's files match the evidence's sha256s and the firmware printed a line that
starts with the word `ready` within %d s.
The board's log goes to sim/runs/board/. A firmware that stops with an error is not seen. If mpremote cannot reach the
board, for example because its port changed after the flash, or the passed run's log is from before P215 and names no
files, ready is unknown, never seen. The write restarts the chip with esptool's `--after watchdog-reset` (esptool's troubleshooting
page says the ESP32-S3 then leaves download mode; not yet run on a board that was entered with BOOT; the C6 and the classic ESP32 fall
back to a hard reset), and deploy.py finds the board's port again by its MAC,
for the port can change its name and its USB id. If ready is unknown and the passed log names files, deploy.py reads the
look's port with DTR and RTS off, unless that is 303a:4001 (MicroPython's own USB). If it reads `waiting for download`, the board waits in its download mode: deploy.py asks you to
press the board's RESET once (with its place when the board record has it) and waits %d s. A restart counts only when
mpremote answers after it: a restart that left the board in download mode is said and not counted. At the end of the wait
ready is unknown with the code `download_mode_stayed`, or `port_gone` when the port was not listed or did not come back
(then there is no REPL line). If it reads a line whose first word is the firmware's `ready`, the board finished its
restart late, and deploy.py reads it again at once. The board log keeps the first read's words too. What the port printed, `nothing`, or why it could not be read goes in the board log.

When ready is unknown and the passed log names files, deploy.py prints one more line (P1022). It says what spark knows:
the write passed esptool's hash check, whether the board's files were read, what the console printed, and whether
spark.json was written. It says what spark did not do: no second flash and no second erase. Then it says what to try, in
order: look.py after a minute, then RESET once and live.py, then the REPL line. With --json the unchecked item's fix is
the same text, and `next` holds the look, live and watch steps. The board log keeps what mpremote printed on each
failed facts copy.

A firmware that deep-sleeps (P1022 slice 3): when the deploy's look finds no board and firmware/ calls deepsleep, it
says what look.py says. With --port, the board doctor can find the named port not on USB. If firmware/ then calls
deepsleep, the doctor's next line is the same fix, and it opens with the named port (P1049). With --json, `next` then
holds the look step, which needs the person: the same look, run once after the person did step 1 or 2 (P1048). A
`ready` line that the firmware printed before mpremote lost the board counts as ready seen when the board's files match
and firmware/ calls deepsleep; --json says `data.ready.lost_board`. Without a call it is ready unknown, and a file that differs is not
seen. The ready unknown fix names the deepsleep calls, and on an ESP32-C6 over USB-Serial/JTAG it says that a
download mode entered with BOOT outlasts esptool's restart: press RESET.

Each stage starts with a heading, `[n/5] <stage>`, and a `why:` line (plan, look, gate, flash, verify). The run ends
with one status line, bold on a terminal, its mark in colour: `✓ deploy: ok. Flashed, and the board printed ready.`
With --json there is no heading and no status line: stdout holds the envelope, and stderr the other lines as before.""" % (
    NO_SIMULATION_CAVEAT, ready_probe.READY_WAIT_S, download_mode.RESET_WAIT_S)


class DeployImage(Operation):
    """
    Operation: the deploy. It builds the evidence (image_evidence), the platform and a DeployFlowService, and returns
    `board_envelope.deploy_result`. Before its read it asks the board question by the deploy's Touch (P892): the kept board
    is read with no question, another board and no kept board stop before any read and send to the look, and a board that
    spark cannot tell is asked on every deploy, with --port too. `platform_for(project, find_tool)` is a `_for` builder of
    the FirmwarePlatform (default: MicroPythonPlatform), `grant_service` the board_grant.GrantService that finds a deploy
    grant, `records` the DeployRecordStore (None for the store's own, built per run) and `known` the KnownBoardStore (None:
    the store's own): the collaborators a test swaps whole. The dry run
    declares READS alone, so `outside.run` refuses; with --no-simulation it declares RUNS too, and the compile check's child
    runs for real through `outside.run`, in a dry run as well (P458).
    """

    name = "deploy"
    summary = "Put the flash image onto the board: one that a passed run names (P192), or, with --no-simulation, firmware/ (P337)."
    details = DETAILS
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
                 COMMON_ARGUMENTS["replies"]._replace(help=REPLIES_HELP),
                 COMMON_ARGUMENTS["json"]._replace(help="print one envelope on stdout, the lines a person reads on stderr (docs/guide/agents/json.md)"))
    effects = (READS, RUNS, BOARD, DELETES, WRITES, ASKS)
    privacy_for = staticmethod(bench_privacy.privacy_for)
    #: The text view numbers its headings from these rows, and ends with the status line alone: the events said the rest (P478).
    stages = DEPLOY_STAGES
    text_renderer = StatusLine

    def __init__(self, platform_for=None, grant_service=None, records=None, known=None):
        self.platform_for = platform_for or MicroPythonPlatform
        self.grant_service, self.records, self.known = grant_service, records, known or known_board.KnownBoardStore()

    def effects_of(self, values):
        if not values["dry_run"]:
            return self.effects
        return (READS, RUNS) if values["no_simulation"] else (READS,)

    def run(self, project, port, token, dry_run, replies=None, *, outside, **evidence):
        """`evidence` holds the two flags of EVIDENCE_GROUP, `ignore_older_runs` and `no_simulation`."""
        picked = evidence_for(project, evidence["no_simulation"], evidence["ignore_older_runs"], find_tool=outside.find_tool, run=outside.run)
        platform = self.platform_for(project, outside.find_tool)
        flow = DeployFlowService(lambda world: DeployService(project, platform, picked, world, self.records), outside,
                                 self.grant_service or board_grant.GrantService(), Asked(port, token, dry_run, replies),
                                 known_board.KnownBoardService(self.known, known_board.DEPLOY))
        code = flow.plan()
        try:
            if code is None:
                code = flow.ask_for_board()
            if code is None:
                code = flow.look_and_flash()
            if code is None:
                code = flow.verify()
        except Exception as crashed:  # noqa: BLE001  after the gate the board may be erased: the result must say so
            if flow.tracker.stage not in CRASH_STATES:
                raise
            return self._crashed(flow, crashed)
        return board_envelope.deploy_result(flow.reached(), code)

    def _crashed(self, flow, crashed):
        """The result of a crash after the gate passed: one unchecked Finding with code `crash` that names the board's state,
        the data reached with the yes and `board_state`, the look as the next step, the traceback in the diagnostics, and
        the headline that names the board's state (P478)."""
        flow.keep_yes()  # a crash in the flash loop still says whose yes it was
        reached, name = flow.reached(), type(crashed).__name__
        state = CRASH_STATES[reached["stage"]]
        data = dict(board_envelope.deploy_data(reached), board_state=state.board_state)
        finding = Finding(outcomes.COULD_NOT_RUN, reached["stage"], codes.CRASH, "%s; the board %s" % (CRASH_MESSAGE % name, state.words), state.fix)
        look = NextStep(**board_envelope.look_step(reached["project"], reached.get("port"), reached["evidence"], CRASH_WHY_LOOK % state.words))
        return OperationResult(data, [finding], [look], diagnostics=[CRASHED_MESSAGE % (self.name, name), state.fix] + traceback_lines(crashed),
                               headline=Headline(CRASH_HEADLINE % state.words, Headline.of_status(outcomes.COULD_NOT_RUN)))
# --- end MVP ---
