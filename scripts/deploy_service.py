"""
The flow of a deploy, without a terminal (P239 PR 8): plan, look, gate, flash, then the facts, ready and the log.

`DeployService` prints nothing and never exits. A line the person must see while a step runs goes to `show_line`; the
rest comes back in a `DeployResult`; a refusal is an exception (`LookStop`, `DeployError`, `tools.ToolProblem`,
`deploy_gate.GateClosedError`). deploy.py parses the arguments, chooses the yes, prints and maps the exit code.
"""

import collections
import hashlib
import shlex
import subprocess
import time

import board_facts
import board_grant
import board_look
import deploy_gate
import download_mode
import ready_check
from project_image import DeployError, ProjectImage
from run_scenario import file_hashes

#: How a refusal for a run that tested another image ends: what to do instead (the PO, 2026-10-12: refuse by default).
OLDER_RUNS_WAY_OUT = (". If a log's scenario is gone, delete the log after the person says yes. To flash anyway, pass "
                      "--ignore-older-runs, and deploy.py names the log in a note")

#: Value: what `plan` returns. `flasher` is the Flasher, `commands` are the flash commands it builds, `mpremote` is
#: the board shell's command, and `notes` are sentences for the person.
DeployPlan = collections.namedtuple("DeployPlan", "flasher commands mpremote notes")
#: Result: what `verify` returns. `facts` are the board's facts, `ready` is a ReadyResult, `log_path` the board log's file.
#: `repl_command` is the argv that opens the board's REPL.
#: `reset_seen` is None when the person was never asked to press R, else whether the port came back.
DeployResult = collections.namedtuple("DeployResult", "facts facts_line ready log_path repl_command reset_seen", defaults=(None,))


class FlashError(DeployError):
    """Error: a flash command failed, so the board may be erased and not written."""


class BoardLog(collections.namedtuple("BoardLog", "moment port image_sha256 facts_line verdict sentence heard")):
    """Value: the facts of the board's log after a flash. `heard` is the console text, then what the board printed."""

    def text(self):
        """The log file's text."""
        return "# deploy %s on %s\nimage sha256: %s\n%s\n%s: %s\n\n%s\n" % (
            self.moment.isoformat(timespec="seconds"), self.port, self.image_sha256, self.facts_line, self.verdict,
            self.sentence, self.heard)


def write_board_log(project, log):
    """The board's log (a BoardLog) in sim/runs/board/ beside the run logs, whose *.log glob does not reach it. Returns
    its path."""
    path = project / "sim" / "runs" / "board" / ("%s.log" % log.moment.strftime("%Y-%m-%dT%H-%M-%S"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(log.text())
    return path


def newer_files(project, image):
    """The files under firmware/ changed after the image was made, as project paths. The board gets the image, not them."""
    made = image.stat().st_mtime
    return sorted(str(path.relative_to(project)) for path in (project / "firmware").rglob("*")
                  if path.is_file() and "__pycache__" not in path.parts and path.stat().st_mtime > made)


class DeployService:
    """Service: the steps of one deploy of `project`, over a FirmwarePlatform. `run` runs a command, `clock` reads the
    time (default: board_grant.read_local_time, called once), `probe` finds a board in download mode (default: the platform's).
    `ignore_older_runs` holds for every step. Its methods raise `DeployError`, `tools.ToolProblem`, `board_look.LookStop` or
    `deploy_gate.GateClosedError` to say why a step cannot go on; they never print and never exit."""

    #: How the service waits before its flasher's retry. A test replaces it.
    sleep = staticmethod(time.sleep)

    def __init__(self, project, platform, ignore_older_runs=False, run=subprocess.run, clock=None, probe=None, echo_to=None):
        self.project, self.platform, self.ignore_older_runs = project, platform, ignore_older_runs
        self.run, self.clock, self.probe = run, clock, probe
        self.echo_to = echo_to  # a file descriptor for the flash tool's own output (2 under --json), or None: as it is

    def plan(self, port=None):
        """
        A DeployPlan (the flash commands, the shell's command, notes) for this project. Nothing runs here. A DeployError or
        a tools.ToolProblem says why the image cannot go on the board yet: what costs nothing is checked before the tools.
        A run log that tested another image refuses the flash, unless `ignore_older_runs` makes it a note.
        """
        image = ProjectImage(self.project)
        why = image.why_untested()
        if why:
            raise DeployError(why)
        other = image.why_other_runs()
        if other and not self.ignore_older_runs:
            raise DeployError(other + OLDER_RUNS_WAY_OUT)
        project_flasher = self.platform.make_flasher()
        shell_command = self.platform.make_shell_command()
        changed = newer_files(self.project, image.path)
        notes = ["%s changed after this image was made: the board gets the image that passed, not the change. Run its "
                 "scenario again to test it." % ", ".join(changed)] if changed else []
        notes += [other] if other else []
        return DeployPlan(project_flasher, project_flasher.build_commands(image.path, port), shell_command, notes)

    def look(self, port=None):
        """The LookReport of the board on USB. Raises LookStop to say why not."""
        return board_look.looker(self.project, self.run).run(self.project, port, self.ignore_older_runs)

    def deploy(self, report, token, consent, show_line):
        """
        Pass the gate, then run the flash commands, erase first. Returns the DeployPlan it ran. `report` is the LookReport,
        `consent` the person's yes, `show_line` takes the lines to show while this runs. GateClosedError, DeployError and
        tools.ToolProblem say why nothing, or not everything, was flashed.
        """
        image_path = ProjectImage(self.project).path.relative_to(self.project)
        deploy_gate.require_open_gate(report, token, consent, image_path)
        if isinstance(consent, board_grant.StandingConsentStrategy):
            show_line("  yes: %s" % consent.who)
        planned = self.plan(report.port)
        if report.token() != token:  # AT116: the image changed while the person answered
            raise DeployError("the image changed after your yes: run look.py again. not flashed.")
        consent.require_ready()  # a deploy grant can end while the plan reads the image
        for index, command in enumerate(planned.commands):
            show_line("  running: %s" % shlex.join(command))
            try:
                self._run_flash(command, planned.flasher, consent, show_line, retry=index == 0)
            except (OSError, subprocess.CalledProcessError) as failed:
                hint = planned.flasher.BOOT_HINT
                raise FlashError("`%s` failed (%s)%s" % (shlex.join(command), failed, ": " + hint if hint else ""))
        return planned

    def _run_flash(self, command, flasher, consent, show_line, retry):
        """Run one flash command. With `retry`, a stop with the flasher's RETRY_EXIT_CODE runs it once more, after the
        flasher's wait, while the yes still holds (P290: the erase right after the look's reset)."""
        echo = {} if self.echo_to is None else {"stdout": self.echo_to}
        try:
            self.run(command, check=True, **echo)
        except subprocess.CalledProcessError as failed:
            if not retry or failed.returncode != flasher.RETRY_EXIT_CODE:
                raise
            show_line("  " + flasher.RETRY_LINE % {"wait": flasher.RETRY_WAIT_S, "command": shlex.join(command),
                                                   "code": failed.returncode})
            self.sleep(flasher.RETRY_WAIT_S)
            try:
                consent.require_ready()
            except deploy_gate.GateClosedError as shut:  # the first try ran: the board may be erased
                raise FlashError("`%s` failed (%s), and its retry did not run: %s" % (shlex.join(command), failed, shut))
            self.run(command, check=True, **echo)

    def verify(self, report, planned, show_line):
        """
        Read the board after the flash: copy the facts file, check each file's sha256 and wait for `ready`, with the
        recovery for a board in download mode (P243 to P245). Writes the board log. Raises DeployError when the passed run's log cannot be read, and
        tools.ToolProblem when a tool is missing: after the flash they are not turned into a sentence. `planned` the DeployPlan that `deploy` returned. Returns a DeployResult.
        """
        image = ProjectImage(self.project)  # fresh: the flash and the person's wait are behind us
        passed = image.find_passed_log()
        expected = file_hashes(passed) if passed else {}
        connection = self.platform.make_connection(planned.mpremote, report.port, self.run)
        moment = (self.clock or board_grant.read_local_time)()  # once: the facts file and the board log share it
        facts, facts_line, ready = self._read_board(image, report, connection, expected, moment)
        heard, reset_seen = "", None
        if ready.verdict == ready_check.UNKNOWN and expected:  # P243: silent after the flash, maybe in download mode
            probe = self.probe or self.platform.make_console_probe(report.port, self.run)
            if probe:  # P244: what the console said goes in the log, download mode or not
                waits, console = probe.waits_in_download_mode()
                heard = "console with DTR and RTS off: %s\n" % (console.strip() or "nothing")
                if waits:
                    show_line("  %s" % download_mode.PRESS_RESET)
                    reset = reset_seen = probe.wait_for_reset()
                    if reset:
                        facts, facts_line, ready = self._read_board(image, report, connection, expected, moment)
                    else:
                        ready = ready._replace(sentence=download_mode.NO_RESET)
                    heard += "reset seen\n" if reset else "no reset\n"
                elif download_mode.booted(console):  # P245: mpremote asked while the board still restarted
                    facts, facts_line, ready = self._read_board(image, report, connection, expected, moment)
                    heard += download_mode.READ_AGAIN + "\n"
        log_path = write_board_log(self.project, BoardLog(moment, report.port, image.sha256,
                                                          facts_line, ready.verdict, ready.sentence, heard + ready.log))
        return DeployResult(facts, facts_line, ready, log_path, connection.repl_command(), reset_seen)

    @staticmethod
    def record(result, consent):
        """Keep this deploy in the store's record of the board and return its path. OSError and store.StoreProblem say
        why it was not written. Whose yes it was is read here, as the old main read it."""
        return board_facts.record_deploy(result.facts, result.ready.verdict, consent.who)

    def _read_board(self, image, report, connection, expected, moment):
        """(the facts, the facts line, a ReadyResult) after a flash: the facts, then ready."""
        facts, facts_line = self._put_facts(image, report, connection, expected, moment)
        return facts, facts_line, self.platform.make_ready_check(connection).check(expected)

    def _put_facts(self, image, report, connection, expected, moment):
        """(the facts, the board log's line about the facts file): copied to the board and read back (D22)."""
        said = board_facts.facts(self.project, self.platform.board_of(), report.reading.mac, image.path, expected, moment)
        why = board_facts.FactsFile(connection).write(said)
        if why:
            return said, "facts file: not written: %s" % why
        return said, "facts file %s sha256: %s" % (board_facts.FACTS_FILE,
                                                  hashlib.sha256(board_facts.facts_text(said).encode()).hexdigest())
