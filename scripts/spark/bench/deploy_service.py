"""
The flow of a deploy, without a terminal (P239 PR 8): plan, look, gate, flash, then the facts, ready and the log.

`DeployService` prints nothing and never exits. A line the person must see while a step runs is an Event it reports
through `outside.report` (E2, P655); the rest comes back in a `DeployResult`; a refusal is an exception (`LookStopError`,
`DeployError`, `ToolError`, `deploy_gate.GateClosedError`). The DeployImage Operation chooses the yes and builds the
result.
"""

import collections
import contextlib
import hashlib
import shlex
import subprocess

from spark.bench import board_codes
from spark.bench import board_connection
from spark.bench.deploy_stages import DeployPhase
from spark.bench import board_facts
from spark.records import board_records
from spark.bench import board_look
from spark.bench import board_log
from spark.bench.board_log import BoardLog, write_board_log
from spark.bench import board_start
from spark.bench import deploy_gate
from spark.records import deploy_record_store
from spark.bench import download_mode
from spark.bench import image_evidence
from spark.bench import ready_probe
from spark.firmware import sleep_calls
from spark.firmware.project_image import DeployError
from spark.core import codes
from spark.core.events import Event

#: Value: what `plan` returns. `flasher` is the Flasher, `commands` are the flash commands it builds, `mpremote` is
#: the board shell's command, and `notes` are sentences for the person. `image_sha256` is the image that `deploy` gave the
#: flash commands, None from `plan`: the verify's board log names it when the verify does not finish (P1110).
DeployPlan = collections.namedtuple("DeployPlan", "flasher commands mpremote notes image_sha256", defaults=(None,))
#: Result: what `verify` returns. `facts` are the board's facts, `ready` is a ReadyResult, `log_path` the board log's file.
#: `repl_command` is the argv that opens the board's REPL.
#: `start` is None when no wait for a start came (the board answered), else a board_start.BoardStartResult: its `code` is
#: None when mpremote answered after a restart, else download_mode_stayed or port_gone (P462).
#: `console` is what the board's console printed after the flash, "" for nothing, or None when it was not read (P1022).
#: `facts_line` is a board_facts.FactsLine. `own_usb` is True when the board's USB is the chip's own, and
#: `keeps_boot_entry` when the restart after the write cannot leave a download mode entered with BOOT (P1022 slice 3).
DeployResult = collections.namedtuple("DeployResult", "facts facts_line ready log_path repl_command start image_sha256 console "
                                      "own_usb keeps_boot_entry", defaults=(None, None, None, False, False))


def _keeps_boot_entry(planned, row):
    """True when the plan's flasher cannot leave a BOOT entry and the board's port is Espressif's USB-Serial/JTAG."""
    return bool(planned.flasher.keeps_boot_entry and row and row.usb == board_connection.USB_SERIAL_JTAG)


#: The board log's sentence of a flash that did not finish (P1092), by its reason. board_codes' own grant_ended sentence
#: says "before the erase", which is true at the gate and false here: the first erase ran. The crash's is its own (P1096):
#: the core's meaning points to a traceback on stderr, and a person reads the log days later. These sentences name the
#: flash on purpose, while flow_codes.CAUSE_WORDS say "during the deploy": the verify's log has its own (P1110).
NOT_FINISHED_SENTENCES = {board_codes.FLASH_FAILED: board_codes.CODES[board_codes.FLASH_FAILED],
                          board_codes.GRANT_ENDED: "the yes ended before the erase's retry",
                          board_codes.INTERRUPTED: board_codes.CODES[board_codes.INTERRUPTED],
                          codes.CRASH: "spark crashed during the flash, so the board may be erased and not written"}
#: The board log's facts line of a flash that did not finish: no facts file went on the board.
NOT_FINISHED_FACTS = "facts file: not written: the flash did not finish"
#: Value: what the board log of a stage that did not finish after the yes says: its verdict, its sentence by the reason
#: (a reason not there keeps what ended it) and its facts line (P1110).
NotFinishedLog = collections.namedtuple("NotFinishedLog", "verdict sentences facts")
FLASH_NOT_FINISHED_LOG = NotFinishedLog(board_log.FLASH_NOT_FINISHED, NOT_FINISHED_SENTENCES, NOT_FINISHED_FACTS)
#: The verify's (P1110): the flash finished and passed esptool's hash check, and spark did not finish reading the board
#: back, so ready is unknown, never "flash not finished". Its facts line never says more than spark knows.
VERIFY_NOT_FINISHED_SENTENCES = {
    codes.CRASH: "spark crashed while it read the board after the flash, so ready is not known",
    board_codes.INTERRUPTED: "a Ctrl-C interrupted the read of the board after the flash, so ready is not known"}
VERIFY_NOT_FINISHED_FACTS = "facts file: not known: the read after the flash did not finish"
VERIFY_NOT_FINISHED_LOG = NotFinishedLog(ready_probe.UNKNOWN, VERIFY_NOT_FINISHED_SENTENCES, VERIFY_NOT_FINISHED_FACTS)


class FlashError(DeployError):
    """Error: a flash command failed, so the board may be erased and not written. Its `reason` is flash_failed, or the
    gate's grant_ended when the yes ended before the retry. `log_path` is the board log that DeployService.deploy wrote
    for it (P1092), or None with `log_error` saying why none was written; `image_sha256` is the image the flash was given,
    and `moment` the board log's, `verdict` its verdict (P1112). The handler sets the same on a crash and a Ctrl-C in the flash
    loop (P1096) and the verify (P1110)."""

    log_path = log_error = image_sha256 = moment = verdict = None


def not_finished_reason(ended):
    """The board log's reason of a flash that `ended` ended (P1096): a FlashError's own, interrupted for a Ctrl-C, else
    the core's crash."""
    if isinstance(ended, FlashError):
        return ended.reason
    return board_codes.INTERRUPTED if isinstance(ended, KeyboardInterrupt) else codes.CRASH


def ended_after_the_yes(raised):
    """True when the flash loop's or the verify's handler, DeployService.logs_what_ends, handled `raised` (P1096, P1110):
    only it sets the attribute `image_sha256`, the one channel of this mark. A crash outside them, and a bug in the log
    write that replaced what ended the stage, give False."""
    return getattr(raised, "image_sha256", None) is not None


def every_read(reads):
    """The last of `reads`, each (the facts, a board_facts.FactsLine, a ReadyResult), with the facts file written and the board's
    files read when any read did (P1022): a read again after P245 can fail where the first read worked. `lost_board` is the
    last read's. So is `code` (P1043), but never FILES_UNREAD after a read that read the files: that read's code stays."""
    facts, line, ready = reads[-1]
    read_before = [read[2] for read in reads if read[2].files_read]
    code = read_before[-1].code if read_before and ready.code == board_codes.FILES_UNREAD else ready.code
    return (facts, board_facts.FactsLine(line, any(read[1].written for read in reads), line.heard),
            ready_probe.ReadyResult(*ready, files_read=any(read[2].files_read for read in reads), lost_board=ready.lost_board).coded(code))


class DeployService:
    """Service: the steps of one deploy of `project`, over a FirmwarePlatform. `outside` is the OutsideWorld: its `run` runs a
    command, its `clock` has `now`, `monotonic` and `sleep`, and its `report` takes each Event a person reads while a step
    runs. `records` keeps the deploy (default: the store's DeployRecordStore). `evidence` (an ImageEvidence) holds for every
    step. Its methods raise `DeployError`, `ToolError`, `board_look.LookStopError` or `deploy_gate.GateClosedError` to
    say why a step cannot go on; they never print and never exit."""

    #: (project, BoardLog) -> the board log's path: board_log's own; a test sets another on the instance (P1092).
    write_log = staticmethod(write_board_log)

    def __init__(self, project, platform, evidence, outside, records=None):
        self.project, self.platform, self.evidence = project, platform, evidence
        self.run, self.clock, self.report = outside.run, outside.clock, outside.report
        self.records = records or deploy_record_store.DeployRecordStore()
        self.sleeps = sleep_calls.deep_sleep_calls(project)  # P1022 slice 3: read once, from firmware/

    def plan(self, port=None):
        """
        A DeployPlan (the flash commands, the shell's command, notes) for this project. Nothing runs here. A DeployError or
        a ToolError says why the image cannot go on the board yet: what costs nothing is checked before the tools.
        A run log that tested another image refuses the flash, unless the evidence makes it a note.
        """
        image = image_evidence.image_of(self.project, self.evidence)
        why = self.evidence.why_not_ready(image)
        if why:
            raise DeployError(why + self.evidence.way_out(image), reason=board_codes.EVIDENCE_REFUSES)
        project_flasher = self.platform.make_flasher()
        shell_command = self.platform.make_shell_command()
        notes = self.evidence.notes(image)
        return DeployPlan(project_flasher, project_flasher.build_commands(image.path, port), shell_command, notes)

    def find_row(self, port=None):
        """The Port row of the board the deploy reads, found as the look finds it (P892): the one board on USB, or the row of a
        named `port`, None when the list does not hold it (a /dev/tty. alias is its /dev/cu. port). A named port costs one
        more `mpremote devs`. Raises LookStopError to say why not: no board on USB, or two with no port named."""
        return board_look.looker(self.platform, self.run, self.records).finder.find_row(port)

    def look(self, port=None, listed=None):
        """The LookReport of the board on USB, its last deploy read from `records`, the store this service writes to (P458).
        `listed` is the row `find_row` gave, so the one board is not listed again. Raises LookStopError to say why not."""
        return board_look.looker(self.platform, self.run, self.records).run(self.project, port, self.evidence, listed=listed)

    def deploy(self, look, token, consent):
        """
        Pass the gate, then run the flash commands, erase first. Returns the DeployPlan it ran. `look` is the LookReport,
        `consent` the person's yes. It reports the gate's yes line, a BEGIN of the flash and a line per command (E2).
        GateClosedError, DeployError and tool_finder.ToolError say why nothing, or not everything, was flashed. A FlashError
        says that the flash did not finish after the yes: it comes with the board log that says so (P1092). A crash and a
        Ctrl-C in the loop get the same log, and go on unchanged (P1096; build_record.py's handler is the precedent).
        """
        image = image_evidence.image_of(self.project, self.evidence)
        image_path = image.path.relative_to(self.project)
        deploy_gate.require_open_gate(look, token, consent, image_path, look.question_caveats())
        if consent.yes_kind == deploy_gate.GRANT:
            self.report(Event.line(DeployPhase.GATE, "yes: %s" % consent.who))
        planned = self.plan(look.port)
        if look.token() != token:  # AT116: the image changed while the person answered
            raise DeployError("the image changed after your yes: run look.py again. not flashed.", reason=board_codes.IMAGE_CHANGED)
        consent.require_ready()  # a deploy grant can end while the plan reads the image
        image_sha256 = image.sha256  # read once, after the token's check: the image the flash commands are given
        self.report(Event.begin(DeployPhase.FLASH))
        with self.logs_what_ends(look, image_sha256, FLASH_NOT_FINISHED_LOG):
            for index, command in enumerate(planned.commands):
                self.report(Event.line(DeployPhase.FLASH, "running: %s" % shlex.join(command), raw=True))  # P677: a command
                try:
                    self._run_flash(command, planned.flasher, consent, retry=index == 0)
                except (OSError, subprocess.CalledProcessError) as failed:
                    hint = planned.flasher.boot_hint
                    raise FlashError("`%s` failed (%s)%s" % (shlex.join(command), failed, ": " + hint if hint else ""),
                                     reason=board_codes.FLASH_FAILED)
        return planned._replace(image_sha256=image_sha256)

    @contextlib.contextmanager
    def logs_what_ends(self, look, image_sha256, logged):
        """The one handler of a stage after the yes (P1096, P1110): what ends the block, a crash, a Ctrl-C or an error, gets
        the board log `logged` (a NotFinishedLog) of the image `image_sha256`, with `log_path`, `image_sha256`, `moment` and
        `verdict` (the log's, which the store entry says too, P1112) set on it, then goes on unchanged."""
        try:
            yield
        except (Exception, KeyboardInterrupt) as ended:  # P1092, P1096: the newest board log must not name the deploy before
            now = self.clock.now()  # once: the board log and the store record share it
            ended.log_path, ended.image_sha256, ended.moment = self.log_not_finished(look, image_sha256, ended, now, logged), image_sha256, now
            ended.verdict = logged.verdict  # P1112: one source for the board log's verdict and the store entry's
            raise  # P1096, P1110: what ended the flash or the verify goes on

    def log_not_finished(self, look, image_sha256, failed, moment, logged):
        """The path of the board log of a stage that did not finish after the yes (P1092, P1110), written at `moment`: the
        NotFinishedLog `logged` and the reason of `failed` (a FlashError, a crash or a Ctrl-C, P1096) as its line 4. A crash
        keeps its class name only, as its message can hold a home path (D5). None when an OSError or a ValueError kept it
        from being written: `failed.log_error` then says why, and the flash's own error stays the answer. On purpose, a
        TypeError or a KeyError is a bug: it replaces what ended the flash, keeps it as its __context__, and the run
        crashes at stage flash, whose board_state stays may_be_erased (F13). After a Ctrl-C, such a bug ends the run with
        exit 2, not 130."""
        reason = not_finished_reason(failed)
        said = str(failed) if isinstance(failed, FlashError) else type(failed).__name__
        log = BoardLog(moment, look.port, image_sha256, board_facts.FactsLine(logged.facts, False),
                       logged.verdict, logged.sentences.get(reason, said), said + "\n",
                       self.evidence.simulation, reason)
        try:
            return self.write_log(self.project, log)
        except (OSError, ValueError) as unwritten:
            failed.log_error = str(unwritten)
            return None

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
        `ready`, with the recovery for a board in download mode (P243 to P245, P462). Writes the board log, also when a crash
        or a Ctrl-C ends the read (P1110). Raises DeployError when the passed run's log cannot be read, and ToolError when a
        tool is missing: after the flash they are not turned into a sentence. `planned` is the DeployPlan `deploy` returned.
        """
        with self.logs_what_ends(look, planned.image_sha256, VERIFY_NOT_FINISHED_LOG):  # P1110: a crash or a Ctrl-C
            image = image_evidence.image_of(self.project, self.evidence)  # fresh: the flash and the person's wait are behind us
            expected = self.evidence.expected_files(image)
            moment = self.clock.now()  # once: the facts file and the board log share it
            starter = board_start.BoardStartService(self.platform.make_port_finder(self.run), look.reading.mac, self.clock,
                                                    board_records.ButtonPlaces.of_project(self.project))
            row = starter.find_port(look.port)
            port, reads = row and row.device, []  # P1022: every read of the board, for the facts copies' block and the fix

            def read(on):  # P1007: the USB id the port has at this read picks the connection
                connection = on and self.platform.make_connection(planned.mpremote, on, self.run, starter.usb_of(on) or (row and row.usb))
                board = self._read_board(image, look, connection, expected, moment)
                reads.append(board)
                return board

            board, start = read(port), None
            if port is None:
                start = starter.gone_result()
            elif (board[2].verdict == ready_probe.UNKNOWN and expected  # P243: silent after the flash, maybe in download mode
                  and board_start.console_may_be_read(row, look.port)):
                board, start = self._after_silence(starter, row, board, read)
            facts, facts_line, ready = every_read(reads)  # board is the last of them
            if start and start.code:
                ready = ready._replace(sentence=start.sentence)
            image_sha256 = image.sha256  # read once: the board log and the result name the same image (P213)
            log_path = self.write_log(self.project, BoardLog(moment, look.port, image_sha256,
                                                              facts_line, ready.verdict, ready.sentence,
                                                              "".join(starter.heard) + ready.log + "".join(read[1].heard for read in reads), self.evidence.simulation,
                                                              (start and start.code) or ready.code))
        shown_on = start.port if start else port  # the REPL names the port the board answered on, or none when it is gone
        repl = self.platform.make_connection(planned.mpremote, shown_on, self.run).repl_command()
        result = DeployResult(facts, facts_line, ready, log_path, repl, start, image_sha256)._replace(console=starter.console)
        return result._replace(own_usb=download_mode.own_usb_of(self.project, row and row.usb), keeps_boot_entry=_keeps_boot_entry(planned, row))

    def _after_silence(self, starter, row, board, read):
        """(the board read last, a BoardStartResult or None) for a board that stayed silent on the Port `row` after the flash: the
        console tells download mode from a late start. In download mode the person presses RESET and the wait counts only a
        restart that mpremote answers after (`read(port)` reads the board again)."""
        port = row.device
        probe = self.platform.make_console_probe(port, self.run)
        if not probe:
            return board, None
        waits, console = probe.waits_in_download_mode()
        starter.console = console
        if not console.read:  # P1022: an unread port's sentence is no console text; the board log keeps it below
            starter.console = None
        starter.note("console with DTR and RTS off: %s\n" % (console.strip() or "nothing"))
        if waits:
            self.report(Event.line(DeployPhase.VERIFY, download_mode.press_reset(starter.places)))
            latest = [board]
            start = starter.wait_for_start(port, lambda on: latest.append(read(on)) or latest[-1][2].verdict != ready_probe.UNKNOWN,
                                           self.report, usb=row.usb)
            return latest[-1], start
        if download_mode.booted(console):  # P245: mpremote asked while the board still restarted
            starter.note(download_mode.first_read(board[2]))  # P1025: the first read's words stay in the board log
            starter.note(download_mode.READ_AGAIN + "\n")
            return read(port), None
        return board, None

    def record(self, result, consent):
        """Keep this deploy in the store's record of the board and return its path. OSError and store.StoreError say
        why it was not written. Whose yes it was is read here, as the old main read it."""
        return self.records.write_deploy(result.facts, result.ready.verdict, consent.who)

    def record_not_finished(self, look, image_sha256, moment, who, verdict):
        """Keep a flash or a verify that did not finish after the yes in the store's record of the board, with the board
        log's `verdict`: FLASH_NOT_FINISHED (P1097), so the look and the erase question say that the board may be erased,
        or ready unknown for a verify (P1112). Returns its path. A verify's entry does not read the image file, so a file
        deleted since the flash does not hide it. `moment` is the board log's, `who` the phrase for whose yes it was: "not known (...)" when the login could
        not be read, because the erase is a fact to keep (the review of #1635). OSError and store.StoreError say why it
        was not written, and a DeployError when a flash's image cannot be read now."""
        # the image the flash was given, and no banner: none was written to the board (P1096, G4)
        if verdict == board_log.FLASH_NOT_FINISHED:  # P1111: a flash that did not finish still says an image it cannot read
            facts = dict(self._facts_of(image_evidence.image_of(self.project, self.evidence), look, (), moment),
                         image_sha256=image_sha256, micropython_banner=None)
        else:  # P1112: a verify's entry needs no read of the file, which may be gone by now
            facts = dict(board_facts.facts_without_image(self.project, self.platform.board_of(), look.reading.mac, moment,
                                                         self.evidence.simulation), image_sha256=image_sha256)
        return self.records.write_deploy(facts, verdict, who)

    def _read_board(self, image, report, connection, expected, moment):
        """(the facts, the facts line, a ReadyResult) of the board on `connection` after a flash: the facts, then ready. With
        none (the port is gone) nothing is read, because mpremote would choose a board of its own: the facts are made and not written."""
        if connection is None:
            return (self._facts_of(image, report, expected, moment), board_facts.FactsLine("facts file: not written: the board's port is gone", False),
                    ready_probe.ReadyResult(ready_probe.UNKNOWN, "", ""))
        facts, facts_line = self._put_facts(image, report, connection, expected, moment)
        return facts, facts_line, self.platform.make_ready_probe(connection).check(expected, sleeps=self.sleeps.places)

    def _facts_of(self, image, report, expected, moment):
        """The facts that spark puts on the board (D22)."""
        return board_facts.facts(self.project, self.platform.board_of(), report.reading.mac, image.path, expected, moment,
                                 self.evidence.simulation)

    def _put_facts(self, image, report, connection, expected, moment):
        """(the facts, the board log's line about the facts file, a board_facts.FactsLine): copied to the board and read back (D22)."""
        said = self._facts_of(image, report, expected, moment)
        facts_file = board_facts.ReadingFile(connection, self.clock.sleep)
        why = facts_file.write(said)
        if why:
            return said, board_facts.FactsLine("facts file: not written: %s" % why, False, facts_file.heard)
        retried = " (written on a retry after: %s)" % facts_file.first_failure if facts_file.first_failure else ""
        return said, board_facts.FactsLine("facts file %s sha256: %s%s" % (board_facts.FACTS_FILE,
                                           hashlib.sha256(board_facts.facts_text(said).encode()).hexdigest(), retried),
                                           True, facts_file.heard)
