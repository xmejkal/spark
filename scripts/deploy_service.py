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

import board_codes
import board_facts
import boards
import board_grant
import board_console
import board_look
import board_start
import deploy_gate
import deploy_record_store
import download_mode
import ready_check
from project_image import DeployError, ProjectImage

#: Value: what `plan` returns. `flasher` is the Flasher, `commands` are the flash commands it builds, `mpremote` is
#: the board shell's command, and `notes` are sentences for the person.
DeployPlan = collections.namedtuple("DeployPlan", "flasher commands mpremote notes")
#: Result: what `verify` returns. `facts` are the board's facts, `ready` is a ReadyResult, `log_path` the board log's file.
#: `repl_command` is the argv that opens the board's REPL.
#: `start` is None when no wait for a start came (the board answered), else a board_start.BoardStartResult: its `code` is
#: None when mpremote answered after a restart, else download_mode_stayed or port_gone (P462).
DeployResult = collections.namedtuple("DeployResult", "facts facts_line ready log_path repl_command start image_sha256",
                                      defaults=(None, None))


class FlashError(DeployError):
    """Error: a flash command failed, so the board may be erased and not written. Its `reason` is flash_failed, or the
    gate's grant_ended when the yes ended before the retry."""


class BoardLog(collections.namedtuple("BoardLog", "moment port image_sha256 facts_line verdict sentence heard simulation")):
    """Value: the facts of the board's log after a flash. `heard` is the console text, then what the board printed."""

    def text(self):
        """The log file's text."""
        return "# deploy %s on %s\nimage sha256: %s\nsimulation: %s\n%s\n%s: %s\n\n%s\n" % (
            self.moment.isoformat(timespec="seconds"), self.port, self.image_sha256, self.simulation, self.facts_line,
            self.verdict, self.sentence, self.heard)


def write_board_log(project, log):
    """The board's log (a BoardLog) in sim/runs/board/ beside the run logs, whose *.log glob does not reach it. Returns
    its path."""
    path = project / "sim" / "runs" / "board" / ("%s.log" % log.moment.strftime("%Y-%m-%dT%H-%M-%S"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(log.text())
    return path


class DeployService:
    """Service: the steps of one deploy of `project`, over a FirmwarePlatform. `run` runs a command, `clock` has `now`,
    `monotonic` and `sleep` (default: board_console.SystemClock), `records` keeps the deploy (default: the store's
    DeployRecordStore). `evidence` (an ImageEvidence) holds for every step. Its methods raise `DeployError`, `tools.ToolProblem`, `board_look.LookStop` or
    `deploy_gate.GateClosedError` to say why a step cannot go on; they never print and never exit."""

    def __init__(self, project, platform, evidence, run=subprocess.run, clock=None, echo_to=None, records=None):
        self.project, self.platform, self.evidence = project, platform, evidence
        self.run, self.clock = run, clock or board_console.SystemClock()
        self.records = records or deploy_record_store.DeployRecordStore()
        self.echo_to = echo_to  # a file descriptor for the flash tool's own output (2 under --json), or None: as it is

    def plan(self, port=None):
        """
        A DeployPlan (the flash commands, the shell's command, notes) for this project. Nothing runs here. A DeployError or
        a tools.ToolProblem says why the image cannot go on the board yet: what costs nothing is checked before the tools.
        A run log that tested another image refuses the flash, unless the evidence makes it a note.
        """
        image = ProjectImage(self.project)
        why = self.evidence.why_not_ready(image)
        if why:
            raise DeployError(why + self.evidence.way_out(image), reason=board_codes.EVIDENCE_REFUSES)
        project_flasher = self.platform.make_flasher()
        shell_command = self.platform.make_shell_command()
        notes = self.evidence.notes(image)
        return DeployPlan(project_flasher, project_flasher.build_commands(image.path, port), shell_command, notes)

    def look(self, port=None):
        """The LookReport of the board on USB. Raises LookStop to say why not."""
        return board_look.looker(self.platform, self.run).run(self.project, port, self.evidence)

    def deploy(self, report, token, consent, show_line):
        """
        Pass the gate, then run the flash commands, erase first. Returns the DeployPlan it ran. `report` is the LookReport,
        `consent` the person's yes, `show_line` takes the lines to show while this runs. GateClosedError, DeployError and
        tools.ToolProblem say why nothing, or not everything, was flashed.
        """
        image_path = ProjectImage(self.project).path.relative_to(self.project)
        deploy_gate.require_open_gate(report, token, consent, image_path, report.question_caveats())
        if isinstance(consent, board_grant.StandingConsentStrategy):
            show_line("  yes: %s" % consent.who)
        planned = self.plan(report.port)
        if report.token() != token:  # AT116: the image changed while the person answered
            raise DeployError("the image changed after your yes: run look.py again. not flashed.", reason=board_codes.IMAGE_CHANGED)
        consent.require_ready()  # a deploy grant can end while the plan reads the image
        for index, command in enumerate(planned.commands):
            show_line("  running: %s" % shlex.join(command))
            try:
                self._run_flash(command, planned.flasher, consent, show_line, retry=index == 0)
            except (OSError, subprocess.CalledProcessError) as failed:
                hint = planned.flasher.boot_hint
                raise FlashError("`%s` failed (%s)%s" % (shlex.join(command), failed, ": " + hint if hint else ""),
                                 reason=board_codes.FLASH_FAILED)
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
            self.clock.sleep(flasher.RETRY_WAIT_S)
            try:
                consent.require_ready()
            except deploy_gate.GateClosedError as shut:  # the first try ran: the board may be erased
                raise FlashError("`%s` failed (%s), and its retry did not run: %s" % (shlex.join(command), failed, shut),
                                 reason=shut.reason)  # the yes ended: grant_ended
            self.run(command, check=True, **echo)

    def verify(self, report, planned, show_line):
        """
        Read the board after the flash: find its port by the MAC, copy the facts file, check each file's sha256 and wait for
        `ready`, with the recovery for a board in download mode (P243 to P245, P462). Writes the board log. Raises DeployError
        when the passed run's log cannot be read, and tools.ToolProblem when a tool is missing: after the flash they are not
        turned into a sentence. `planned` the DeployPlan that `deploy` returned. Returns a DeployResult.
        """
        image = ProjectImage(self.project)  # fresh: the flash and the person's wait are behind us
        expected = self.evidence.expected_files(image)
        moment = self.clock.now()  # once: the facts file and the board log share it
        starter = board_start.BoardStartService(self.platform.make_port_finder(self.run), report.reading.mac, self.clock,
                                                boards.ButtonPlaces.of_project(self.project))
        row = starter.find_port(report.port)
        port = row and row.device

        def read(on):
            return self._read_board(image, report, on and self.platform.make_connection(planned.mpremote, on, self.run), expected, moment)

        board, start = read(port), None
        if port is None:
            start = starter.gone_result()
        elif (board[2].verdict == ready_check.UNKNOWN and expected  # P243: silent after the flash, maybe in download mode
              and board_start.console_may_be_read(row, report.port)):
            board, start = self._after_silence(starter, row, board, read, show_line)
        facts, facts_line, ready = board
        if start and start.code:
            ready = ready._replace(sentence=start.sentence)
        image_sha256 = image.sha256  # read once: the board log and the result name the same image (P213)
        log_path = write_board_log(self.project, BoardLog(moment, report.port, image_sha256,
                                                          facts_line, ready.verdict, ready.sentence,
                                                          "".join(starter.heard) + ready.log, self.evidence.simulation))
        shown_on = start.port if start else port  # the REPL names the port the board answered on, or none when it is gone
        repl = self.platform.make_connection(planned.mpremote, shown_on, self.run).repl_command()
        return DeployResult(facts, facts_line, ready, log_path, repl, start, image_sha256)

    def _after_silence(self, starter, row, board, read, show_line):
        """(the board read last, a BoardStartResult or None) for a board that stayed silent on the Port `row` after the flash: the
        console tells download mode from a late start. In download mode the person presses RESET and the wait counts only a
        restart that mpremote answers after (`read(port)` reads the board again)."""
        port = row.device
        probe = self.platform.make_console_probe(port, self.run)
        if not probe:
            return board, None
        waits, console = probe.waits_in_download_mode()
        starter.note("console with DTR and RTS off: %s\n" % (console.strip() or "nothing"))
        if waits:
            show_line("  %s" % download_mode.press_reset(starter.places))
            latest = [board]
            start = starter.wait_for_start(port, lambda on: latest.append(read(on)) or latest[-1][2].verdict != ready_check.UNKNOWN,
                                           show_line, usb=row.usb)
            return latest[-1], start
        if download_mode.booted(console):  # P245: mpremote asked while the board still restarted
            starter.note(download_mode.READ_AGAIN + "\n")
            return read(port), None
        return board, None

    def record(self, result, consent):
        """Keep this deploy in the store's record of the board and return its path. OSError and store.StoreProblem say
        why it was not written. Whose yes it was is read here, as the old main read it."""
        return self.records.write_deploy(result.facts, result.ready.verdict, consent.who)

    def _read_board(self, image, report, connection, expected, moment):
        """(the facts, the facts line, a ReadyResult) of the board on `connection` after a flash: the facts, then ready. With
        none (the port is gone) nothing is read, because mpremote would choose a board of its own: the facts are made and not written."""
        if connection is None:
            return (self._facts_of(image, report, expected, moment), "facts file: not written: the board's port is gone",
                    ready_check.ReadyResult(ready_check.UNKNOWN, "", ""))
        facts, facts_line = self._put_facts(image, report, connection, expected, moment)
        return facts, facts_line, self.platform.make_ready_check(connection).check(expected)

    def _facts_of(self, image, report, expected, moment):
        """The facts that spark puts on the board (D22)."""
        return board_facts.facts(self.project, self.platform.board_of(), report.reading.mac, image.path, expected, moment,
                                 self.evidence.simulation)

    def _put_facts(self, image, report, connection, expected, moment):
        """(the facts, the board log's line about the facts file): copied to the board and read back (D22)."""
        said = self._facts_of(image, report, expected, moment)
        facts_file = board_facts.FactsFile(connection, self.clock.sleep)
        why = facts_file.write(said)
        if why:
            return said, "facts file: not written: %s" % why
        retried = " (written on a retry after: %s)" % facts_file.first_failure if facts_file.first_failure else ""
        return said, "facts file %s sha256: %s%s" % (board_facts.FACTS_FILE,
                                                    hashlib.sha256(board_facts.facts_text(said).encode()).hexdigest(), retried)
