"""
The flow of a deploy, without a terminal (P239 PR 8): plan, look, gate, flash, then the facts, ready and the log.

`DeployService` prints nothing and never exits. A line the person must see while a step runs is an Event it reports
through `outside.report` (E2, P655); the rest comes back in a `DeployResult`; a refusal is an exception (`LookStopError`,
`DeployError`, `tools.ToolProblem`, `deploy_gate.GateClosedError`). The DeployImage Operation chooses the yes and builds the result.
"""

import collections
import hashlib
import shlex
import subprocess

import board_codes
from spark.bench.deploy_stages import DeployPhase
from spark.bench import board_facts
import boards
from spark.bench import board_look
from spark.bench import board_start
from spark.bench import deploy_gate
import deploy_record_store
from spark.bench import download_mode
from spark.bench import ready_probe
from project_image import DeployError, ProjectImage
from spark.core.events import Event

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
    """Service: the steps of one deploy of `project`, over a FirmwarePlatform. `outside` is the OutsideWorld: its `run` runs a
    command, its `clock` has `now`, `monotonic` and `sleep`, and its `report` takes each Event a person reads while a step
    runs. `records` keeps the deploy (default: the store's DeployRecordStore). `evidence` (an ImageEvidence) holds for every
    step. Its methods raise `DeployError`, `tools.ToolProblem`, `board_look.LookStopError` or `deploy_gate.GateClosedError` to
    say why a step cannot go on; they never print and never exit."""

    def __init__(self, project, platform, evidence, outside, records=None):
        self.project, self.platform, self.evidence = project, platform, evidence
        self.run, self.clock, self.report = outside.run, outside.clock, outside.report
        self.records = records or deploy_record_store.DeployRecordStore()

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
        """The LookReport of the board on USB. Raises LookStopError to say why not."""
        return board_look.looker(self.platform, self.run).run(self.project, port, self.evidence)

    def deploy(self, look, token, consent):
        """
        Pass the gate, then run the flash commands, erase first. Returns the DeployPlan it ran. `look` is the LookReport,
        `consent` the person's yes. It reports the gate's yes line, a BEGIN of the flash and a line per command (E2).
        GateClosedError, DeployError and tools.ToolProblem say why nothing, or not everything, was flashed.
        """
        image_path = ProjectImage(self.project).path.relative_to(self.project)
        deploy_gate.require_open_gate(look, token, consent, image_path, look.question_caveats())
        if consent.yes_kind == deploy_gate.GRANT:
            self.report(Event.line(DeployPhase.GATE, "yes: %s" % consent.who))
        planned = self.plan(look.port)
        if look.token() != token:  # AT116: the image changed while the person answered
            raise DeployError("the image changed after your yes: run look.py again. not flashed.", reason=board_codes.IMAGE_CHANGED)
        consent.require_ready()  # a deploy grant can end while the plan reads the image
        self.report(Event.begin(DeployPhase.FLASH))
        for index, command in enumerate(planned.commands):
            self.report(Event.line(DeployPhase.FLASH, "running: %s" % shlex.join(command), raw=True))  # P677: a command
            try:
                self._run_flash(command, planned.flasher, consent, retry=index == 0)
            except (OSError, subprocess.CalledProcessError) as failed:
                hint = planned.flasher.boot_hint
                raise FlashError("`%s` failed (%s)%s" % (shlex.join(command), failed, ": " + hint if hint else ""),
                                 reason=board_codes.FLASH_FAILED)
        return planned

    def _run_flash(self, command, flasher, consent, retry):
        """Run one flash command; the flash tool's own output goes where `outside.run` echoes it. With `retry`, a stop with the
        flasher's RETRY_EXIT_CODE runs it once more, after the flasher's wait, while the yes still holds (P290: the erase
        right after the look's reset)."""
        try:
            self.run(command, check=True)
        except subprocess.CalledProcessError as failed:
            if not retry or failed.returncode != flasher.RETRY_EXIT_CODE:
                raise
            self.report(Event.line(DeployPhase.FLASH, flasher.RETRY_LINE % {
                "wait": flasher.RETRY_WAIT_S, "command": shlex.join(command), "code": failed.returncode}))
            self.clock.sleep(flasher.RETRY_WAIT_S)
            try:
                consent.require_ready()
            except deploy_gate.GateClosedError as shut:  # the first try ran: the board may be erased
                raise FlashError("`%s` failed (%s), and its retry did not run: %s" % (shlex.join(command), failed, shut),
                                 reason=shut.reason)  # the yes ended: grant_ended
            self.run(command, check=True)

    def verify(self, look, planned):
        """
        Read the board after the flash: find its port by the MAC, copy the facts file, check each file's sha256 and wait for
        `ready`, with the recovery for a board in download mode (P243 to P245, P462). Writes the board log. Raises DeployError
        when the passed run's log cannot be read, and tools.ToolProblem when a tool is missing: after the flash they are not
        turned into a sentence. `look` is the LookReport, `planned` the DeployPlan that `deploy` returned. Returns a DeployResult.
        """
        image = ProjectImage(self.project)  # fresh: the flash and the person's wait are behind us
        expected = self.evidence.expected_files(image)
        moment = self.clock.now()  # once: the facts file and the board log share it
        starter = board_start.BoardStartService(self.platform.make_port_finder(self.run), look.reading.mac, self.clock,
                                                boards.ButtonPlaces.of_project(self.project))
        row = starter.find_port(look.port)
        port = row and row.device

        def read(on):
            return self._read_board(image, look, on and self.platform.make_connection(planned.mpremote, on, self.run), expected, moment)

        board, start = read(port), None
        if port is None:
            start = starter.gone_result()
        elif (board[2].verdict == ready_probe.UNKNOWN and expected  # P243: silent after the flash, maybe in download mode
              and board_start.console_may_be_read(row, look.port)):
            board, start = self._after_silence(starter, row, board, read)
        facts, facts_line, ready = board
        if start and start.code:
            ready = ready._replace(sentence=start.sentence)
        image_sha256 = image.sha256  # read once: the board log and the result name the same image (P213)
        log_path = write_board_log(self.project, BoardLog(moment, look.port, image_sha256,
                                                          facts_line, ready.verdict, ready.sentence,
                                                          "".join(starter.heard) + ready.log, self.evidence.simulation))
        shown_on = start.port if start else port  # the REPL names the port the board answered on, or none when it is gone
        repl = self.platform.make_connection(planned.mpremote, shown_on, self.run).repl_command()
        return DeployResult(facts, facts_line, ready, log_path, repl, start, image_sha256)

    def _after_silence(self, starter, row, board, read):
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
            self.report(Event.line(DeployPhase.VERIFY, download_mode.press_reset(starter.places)))
            latest = [board]
            start = starter.wait_for_start(port, lambda on: latest.append(read(on)) or latest[-1][2].verdict != ready_probe.UNKNOWN,
                                           self.report, usb=row.usb)
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
                    ready_probe.ReadyResult(ready_probe.UNKNOWN, "", ""))
        facts, facts_line = self._put_facts(image, report, connection, expected, moment)
        return facts, facts_line, self.platform.make_ready_probe(connection).check(expected)

    def _facts_of(self, image, report, expected, moment):
        """The facts that spark puts on the board (D22)."""
        return board_facts.facts(self.project, self.platform.board_of(), report.reading.mac, image.path, expected, moment,
                                 self.evidence.simulation)

    def _put_facts(self, image, report, connection, expected, moment):
        """(the facts, the board log's line about the facts file): copied to the board and read back (D22)."""
        said = self._facts_of(image, report, expected, moment)
        facts_file = board_facts.ReadingFile(connection, self.clock.sleep)
        why = facts_file.write(said)
        if why:
            return said, "facts file: not written: %s" % why
        retried = " (written on a retry after: %s)" % facts_file.first_failure if facts_file.first_failure else ""
        return said, "facts file %s sha256: %s%s" % (board_facts.FACTS_FILE,
                                                    hashlib.sha256(board_facts.facts_text(said).encode()).hexdigest(), retried)
