"""
The look as an Operation on the core (P442, W3-3): read the board on USB without changing it, compare it with the
project's board record, and give a token. look.py is its CLI. The findings and the next step are the ones look.py
printed before it (board_envelope's look items); a crash is a `crash` envelope and exit 2. P1032 gave the look its text
view: a headline (`headline_of`) and the facts alone as its lines (`look_facts`), in two groups, Board and Image. Deploy
keeps board_look.report_lines.
"""

import functools
from collections import namedtuple

from spark.bench import board_codes
from spark.bench import board_doctor
from spark.bench import board_envelope
from spark.bench import board_grant
from spark.bench import board_look
from spark.bench import known_board
from spark.bench.known_board import CANNOT_TELL, NONE, OTHER
from spark.bench.deploy_stages import DeployPhase
from spark.records import board_records
from spark.bench.firmware_platform import MicroPythonPlatform
from spark.bench.image_evidence import IGNORE_OLDER_RUNS_FLAG, NO_SIMULATION_FLAG, evidence_for
from spark.bench import bench_privacy
from spark.core import codes
from spark.core import outcomes
from spark.core.errors import SparkError
from spark.core.events import INDENT, Event
from spark.core.operation import ASKS, BOARD, COMMON_ARGUMENTS, READS, RUNS, Argument, Operation
from spark.core.replies import RepliesStore
from spark.core.result import MARK_STOP, MARK_UNCHECKED, MARK_WARNING, Finding, Headline, NextStep, OperationResult
from spark.core.text_guards import guard_sentence, printable
from spark.firmware import sim_project
from spark.records import store

# --- MVP ---
#: The lines of a stop name the script that printed them before the core (board_doctor.stop_answer), so they read the
#: same from every frontend.
SCRIPT = "look.py"
#: The group of the two flags that pick the evidence: they exclude each other.
EVIDENCE_GROUP = "evidence"
#: The help of the look's --replies (P865): the agent's own file, after the person's yes in the conversation.
REPLIES_HELP = ('a file of your own with the person\'s yes to the look\'s open question, {"replies": {"<key>": true}}. One yes '
                "answers one look: the look sets it back to null before it reads")
#: Value: the values one look was run with that its next step runs again (P865): the project, the --port or None, and the
#: evidence flags by name.
LookRun = namedtuple("LookRun", "project port evidence")
#: What the open question's next step is.
ASK_AGAIN_WHY = "the same look, after the person's yes in the conversation"
#: The text view's headline of a look with a stop, filled with the first stop's sentence; a second stop is in Problems.
STOP_HEADLINE = "Stop: %s. deploy.py will refuse."
#: The headline of a look whose fields differ with no stop, filled with the fields and the board record's id.
WARNING_HEADLINE = "Warning: the %s differs from the board record %s."
#: The headline of a look whose only gap is a field it could not compare, filled with the record's id and each field's reason.
UNKNOWN_HEADLINE = "Unknown against the board record %s: %s."
#: What a warning or an unknown headline adds when the look has a token, so a deploy can follow.
ASK_MESSAGE = " deploy.py will ask you to accept it."
#: An unknown field's reason as the headline says it, where its words differ from the JSON's (the review of #1549, N2).
UNKNOWN_SAID = {"the board did not say": "the board did not say it"}
#: The fixes of the look's findings that only restate the verdict: the text view prints them with no `fix:` line, and the
#: JSON keeps them (the review of #1549, SF1; person-worded fixes are P1052 #1544).
STOP_FIX, WARNING_FIX = "deploy.py will refuse", "deploy.py asks the person to accept it"
UNKNOWN_FIX = "unknown is not a pass: deploy.py names it and asks the person"
VERDICT_FIXES = (STOP_FIX, WARNING_FIX, UNKNOWN_FIX)
#: The headline of a look whose fields all match, filled with the board record's id; its mark is the status's.
MATCH_HEADLINE = "The chip and the flash match the board record %s."
#: The headline of a look that read another board than the kept one, when it found no problem (round 1, item 6).
OTHER_BOARD_HEADLINE = "Another board than the one this project keeps: no token, and the kept board stays."
#: The label column of a fact line, so `micropython  ` (board_look.say_image_banner) lines up.
FACT = "%-12s %s"
#: A compared field's fact line: the field, the value read, and same, differs or unknown.
FIELD_FACT = "%-12s %-10s %s"
#: The indent of a fact under its group's heading.
ITEM = INDENT * 2
#: What the look does, the paragraphs of look.py's `--help` before its `--json` and exit codes, line breaks and all
#: (P481). Its two `--json` mentions stay in it, so that `--help` stays as it was (P855).
DETAILS = """It reads the board with `mpremote devs` (the list of boards on USB) and `esptool flash-id`. It writes nothing,
erases nothing and changes no flash. The board restarts while esptool reads it: a running program stops and starts again.
Nothing else on the board is touched. The board's record is the one requirements.json names. The look compares the chip
and the flash size, and prints each as same, differs or unknown. It also prints the board's MAC, and on its micropython
line the MicroPython banner of the image it would flash, read from the file, never from the board (P779).

The verdict: another chip, or a flash smaller than the image, is a stop (deploy.py will refuse). A flash that differs
but holds the image, or a field that is unknown, is a warning that the person must accept. The token is two halves of 4
hex digits: one from the board's MAC and one from the image (the one a passed run names, or with --no-simulation, the
image file). It shows that a look was made on this board for this image. It is not the yes and it is not a secret. With
no MAC, no image or no evidence for the image, there is no token, and the line says why.

For an image that a passed run tested, the look also prints what that run did not test (the caveats), and under "what this
simulation cannot show, so test it on the board:" the limits of the project that sim/WHAT-THIS-CANNOT-SHOW.md holds, read
from the limits section of every passed log. --json has them as data.limits, a list of {component, sentence}. With
--no-simulation no log is read: the limits come from the project's records (requirements.json's parts and board, what the pick
and the build read too), and a requirements file or board that does not load gives a caveat that contains "not checked:". An
empty list is not a pass: it never means the project has none.
Under "no scenario named these must lines, so test them on the board:" it lists each must line of .spark/project.json that no passed
scenario named in a step's own name: key (--json: data.unnamed_must); with --no-simulation, every must line. [] is not a pass: when a
log cannot say, a caveat that contains "not checked:" says so.

The first look on a board asks the person before it reads (P865): a question that names the port and the restart. A yes
in a terminal, or `true` in the --replies file, reads the board once and keeps it for this project in spark's store. A later
look reads that board with no question, and stops before the read when another board is on USB. A board with no USB
serial, or with a serial that its firmware set, is asked on every look. A --port that the list does not hold, or that it
shows with no USB serial, is read as before, with no question. Every other board is asked, with --port too.

With two or more boards on USB, --port is needed: the look lists them and reads none. --ignore-older-runs gives a token
even when a log in sim/runs/ tested another image, as deploy.py --ignore-older-runs flashes it. --no-simulation gives a
token for an image that no simulation tested: firmware/ has a main.py, every .py file compiles, no run in sim/runs/ failed on the image and the image holds
firmware/ as it is now. Else it prints why not, and the command that builds the image. deploy.py needs the same flag.

When esptool's read of the board fails, the board doctor (P282) runs two checks: whether `mpremote devs` lists the
port, and two seconds of the console with the port's lock. It prints esptool's own error line, each check's fact,
and one next step for your hands, as the last line. Its look at the console can restart the board.

When no board is on USB and the project's firmware calls deepsleep (read from firmware/, not from the board), the stop
line is `no board found.` and the last line, the fix, says that the board can be in deep sleep (P1022). It names the
calls, and says what to try in order: download mode with BOOT, a wait for the wake, then the cable. A firmware file
that does not parse is named. With --port, the board doctor can find the named port not on USB. If firmware/ then
calls deepsleep, the doctor's next line is the same fix, and it opens with the named port (P1049)."""


class LookAtBoard(Operation):
    """
    Operation: the look. It builds the evidence (image_evidence) and the LookService (board_look.looker), lists the boards,
    asks the person's yes before it reads a board it does not know (P865, `known` the KnownBoardStore, None: the store's
    own), runs the service, and
    returns the LookReport as an OperationResult: its stops and warnings are problems, its unknown fields, a missing token
    and a last deploy it could not check are unchecked, and a token brings the deploy step. A LookStopError is one unchecked
    Finding with the stop's reason, and the board doctor's lines are the diagnostics. It writes nothing on the board. It
    reports one BEGIN of the look, before the read (P507). `records` is the DeployRecordStore the look reads the last deploy
    from (None: the store's own), the collaborator a test swaps whole; the compile child of --no-simulation and the board tools
    run through `outside.run`, and the project's files are read direct (P458).
    """

    name = "look"
    summary = "Read the board on USB without changing it, compare it with the project's board record, and print a token (P219)."
    details = DETAILS
    arguments = (COMMON_ARGUMENTS["project"], COMMON_ARGUMENTS["port"], COMMON_ARGUMENTS["replies"]._replace(help=REPLIES_HELP),
                 Argument((IGNORE_OLDER_RUNS_FLAG,), "ignore_older_runs", bool,
                          "give a token even when a log in sim/runs/ tested another image (default: no token)", group=EVIDENCE_GROUP),
                 Argument((NO_SIMULATION_FLAG,), "no_simulation", bool,
                          "give a token for an image that no simulation tested, when firmware/ has a main.py, "
                          "compiles and is what the image holds (default: a passed run must name the image)", group=EVIDENCE_GROUP),
                 COMMON_ARGUMENTS["json"])
    effects = (READS, RUNS, BOARD, ASKS)
    privacy_for = staticmethod(bench_privacy.privacy_for)

    def __init__(self, records=None, known=None):
        self.records, self.known = records, known or known_board.KnownBoardStore()
        self.board_question = known_board.KnownBoardService(self.known, known_board.LOOK)  # P892: the look's rules and words

    def run(self, project, port, replies=None, *, outside, **evidence):
        """`evidence` holds the two flags of EVIDENCE_GROUP, `ignore_older_runs` and `no_simulation`."""
        picked = evidence_for(project, evidence["no_simulation"], evidence["ignore_older_runs"], find_tool=outside.find_tool, run=outside.run)
        platform = MicroPythonPlatform(project, outside.find_tool)
        # P507: after the evidence and the platform, which touch no board, and before the list and the esptool read
        outside.report(Event.begin(DeployPhase.LOOK))
        try:  # P865: one yes answers one look, also a look that stops before its question
            if replies:
                RepliesStore(replies).clear(known_board.KEY_PREFIX)
        except SparkError as refused:
            return self._said([Finding(refused.status, None, refused.code, str(refused), refused.fix)])
        try:
            service = board_look.looker(platform, outside.run, self.records)
            service.record_of(project)  # P865: a project with no board record stops before any question
            row = service.finder.find_row(port)
            passed = self._gate(LookRun(project, port, evidence), row, outside)
            if isinstance(passed, OperationResult):
                return passed
            report = service.run(project, port, picked, listed=row)
        except board_look.LookStopError as stop:
            return self._stopped(stop, platform, port, outside)
        grant_may_answer = board_grant.GrantService().refusal_of(picked) is None  # P1029: the store's file, for no simulation
        return self._after_read(self._found(report, project.resolve(), picked, grant_may_answer), report, passed, project, outside)

    def _gate(self, look, row, outside):
        """The board question before a read (P865, P892): a known_board.KnownBoardResult that lets the read go on, or the
        OperationResult that ends the look before any read. KnownBoardService judges by the look's Touch: a board that `tell`
        names SAME is read with no question, and so is a --port that the list does not hold or that shows no USB serial (the
        person named it). Every other board is asked, with --port too. An open question, a no, or a record that cannot be
        read ends the look. `look` is the run's LookRun."""
        try:
            judged = self.board_question.judge(look.project, look.port, row, outside.replies)
        except SparkError as refused:
            return self._said([Finding(refused.status, None, refused.code, str(refused), refused.fix)])
        if judged.code == codes.NEEDS_REPLY:
            return self._open(judged, look)
        return self._said(judged.findings(known_board.LOOK)) if judged.code else judged

    def _open(self, judged, look):
        """The result of an open question: its findings and `data` (known_board.KnownBoardResult), and the same look, with its
        --port and evidence flags, as the next step, which needs the person."""
        flags = [flag for flag, dest in ((IGNORE_OLDER_RUNS_FLAG, "ignore_older_runs"), (NO_SIMULATION_FLAG, "no_simulation")) if look.evidence.get(dest)]
        argv = [SCRIPT, "--project", str(look.project)] + (["--port", look.port] if look.port else []) + flags + ["--replies", "<your replies file>"]
        step = NextStep("look", argv, ASK_AGAIN_WHY, [READS, RUNS, BOARD], needs_person=True)
        return self._said(judged.findings(known_board.LOOK), judged.data(judged.row.device), [step], [judged.question.why])

    @staticmethod
    def _said(findings, data=None, following=(), more=()):
        """An OperationResult that ends the look before a read: each Finding's sentence and fix, then `more`, as its lines."""
        lines = [line for found in findings for line in (found.sentence, found.fix)] + list(more)
        return OperationResult(data, findings, list(following), [INDENT + printable(line) for line in lines if line])

    def _after_read(self, result, report, passed, project, outside):
        """The result after the read, and what it keeps (P865). A kept board whose MAC is not the MAC read is `other_board`:
        no deploy step, no token, and the record stays. A yes to a first look or to another board keeps the board read; with
        no MAC read nothing is kept, and a note says so. A yes to a board the look could not tell (a serial that its firmware
        set) is a yes to switch too: another MAC read replaces the record. A store that refuses the write is a note, never a failure."""
        mac, known = report.reading.mac, passed.known
        switch = passed.state == OTHER or (passed.state == CANNOT_TELL and passed.reply is not None)
        differs = known_board.differs(known, mac)
        if differs and not switch:
            other = known_board.OTHER_AFTER_MESSAGE % (report.port, known_board.mac_ends(mac), known_board.mac_ends(known.mac), known.since_said())
            fix = known_board.OTHER_AFTER_FIX if passed.state != CANNOT_TELL else known_board.OTHER_AFTER_PORT_FIX if passed.row \
                else known_board.OTHER_AFTER_UNLISTED_FIX % self.known.find_path(project)
            findings = list(result.findings) + [Finding(outcomes.COULD_NOT_RUN, "board", board_codes.OTHER_BOARD, other, fix)]
            status = outcomes.status_of(*([found for found in findings if found.severity == severity]
                                          for severity in (outcomes.PROBLEMS, outcomes.COULD_NOT_RUN)))
            return result._replace(data=dict(result.data, token=None), findings=findings, next=[], headline=headline_of(report, status, True))
        if passed.reply is None or not (passed.state in (NONE, OTHER) or differs):
            return result
        return result._replace(notes=[self._keep(report, passed, project, outside)])

    def _keep(self, report, passed, project, outside):
        """Keep the board just read as the project's board, and return the note that says so, or why it was not kept."""
        mac = report.reading.mac
        if not mac:
            return known_board.NOT_KEPT_NO_MAC_MESSAGE
        kept = known_board.KnownBoard(str(project.resolve()), mac, known_board.usb_key_to_keep(passed.row, mac), report.record["id"],
                                      passed.reply.answered_by, outside.clock.now().isoformat(timespec="seconds"))
        try:
            self.known.write(kept)
        except store.StoreError as refused:
            return known_board.NOT_KEPT_MESSAGE % refused
        old = passed.known
        if old and known_board.comparable_key(old.mac) != known_board.comparable_key(mac):
            return known_board.REPLACED_MESSAGE % (report.port, known_board.mac_ends(mac), known_board.mac_ends(old.mac))
        return known_board.KEPT_MESSAGE % (report.port, known_board.mac_ends(mac))

    @staticmethod
    def _found(report, project, evidence, grant_may_answer):
        """The result of a LookReport: the lists LookReport.status counts, as Findings, and the deploy step with a token.
        `grant_may_answer` says whether a deploy grant can answer the evidence (board_envelope.yes_rule)."""
        findings = [Finding(outcomes.PROBLEMS, "stop", stop.code, stop.sentence, STOP_FIX) for stop in report.stops]
        findings += [Finding(outcomes.PROBLEMS, "flash", board_codes.FLASH_DIFFERS, warning, WARNING_FIX)
                     for warning in report.warnings]
        findings += [Finding(outcomes.COULD_NOT_RUN, None, board_codes.FIELD_UNKNOWN, "%s unknown: %s" % each,
                             UNKNOWN_FIX) for each in report.unknown.items()]
        no_token = report.no_token_reason()
        if no_token:
            findings.append(Finding(outcomes.COULD_NOT_RUN, None, no_token.code, "no token: %s" % no_token.sentence, "fix that, then run look.py again"))
        if report.last_deploy_not_checked():
            findings.append(Finding(outcomes.COULD_NOT_RUN, None, board_codes.LAST_DEPLOY_NOT_CHECKED,
                                    "last deploy not checked: %s" % report.last_deploy.why, report.last_deploy_fix()))
        token = report.token()
        following = [NextStep(**board_envelope.deploy_step(
            project, token, report.port, evidence,
            "erases ALL of the flash, then writes the image. Relay the warnings first. " + board_envelope.yes_rule(evidence, grant_may_answer)))] if token else []
        result = OperationResult(report.to_dict(), findings, following, look_facts(report))
        return result._replace(headline=headline_of(report, result.status()))

    @staticmethod
    def _stopped(stop, platform, port, outside):
        """The result of a LookStopError: one unchecked Finding, the doctor's facts in `data`, its lines as the diagnostics."""
        answer = board_doctor.stop_answer(SCRIPT, stop, platform, outside.run)
        # P1022, P1049: a firmware that deep-sleeps gets the asleep fix, also as the doctor's next step on the --port port
        lines, sentence, fix = board_envelope.stop_said(SCRIPT, stop, answer, port, platform.project)
        places, doctor = board_records.ButtonPlaces.of_project(platform.project), answer[1]
        # the port and the button words, each on one line (P430); a tool problem's path is flat already (P444)
        said = guard_sentence("\n".join(lines), port, places.boot, places.reset, places.orientation)
        return OperationResult({"doctor": board_doctor.as_dict(doctor)} if doctor else None,
                               [Finding(outcomes.COULD_NOT_RUN, None, stop.reason, sentence, fix)],
                               diagnostics=said.split("\n"))


def headline_of(report, status, other_board=False):
    """The text view's Headline of a LookReport whose result has `status`: the first stop, else the fields that differ,
    else another board than the kept one (`other_board`), else the fields it could not compare, else the match, with the
    status's mark. A warning or an unknown field says that deploy.py will ask only when there is a token. Its blocker is
    the finding that says why there is no deploy step: the stop, the other board or the missing token. Its note is the
    restart notice, and its verdict fixes are VERDICT_FIXES."""
    name, no_token = report.record["id"], report.no_token_reason()
    blocker = report.stops[0].code if report.stops else board_codes.OTHER_BOARD if other_board else no_token and no_token.code
    ask = "" if other_board or no_token else ASK_MESSAGE
    said = functools.partial(Headline, text_notes=(board_look.RESTART_NOTICE,), blocker=blocker, verdict_fixes=VERDICT_FIXES)
    differs = [field for field, state in report.fields.items() if state == "differs"]
    if report.stops:
        return said(STOP_HEADLINE % report.stops[0].sentence, MARK_STOP)
    if differs:
        return said(WARNING_HEADLINE % (" and ".join(differs), name) + ask, MARK_WARNING)
    if other_board:
        return said(OTHER_BOARD_HEADLINE, MARK_UNCHECKED)
    if report.unknown:
        why = "; ".join("the %s: %s" % (field, UNKNOWN_SAID.get(reason, reason)) for field, reason in report.unknown.items())
        return said(UNKNOWN_HEADLINE % (name, why) + ask, MARK_UNCHECKED)
    return said(MATCH_HEADLINE % name, Headline.of_status(status))


def look_facts(report):
    """The facts of a LookReport, what was read and never a verdict, in two groups: Board (the port, the MAC, the
    compared fields, the last deploy) and Image (the banner, the simulation, its caveats and limits, the must lines no
    scenario named). Each line passes `printable`. deploy.py's board_look.report_lines says the same facts."""
    reading, also = report.reading, board_look.ALSO_ON % ", ".join(report.also_on) if report.also_on else ""
    shown = {"chip": reading.chip, "flash": "%s MB" % reading.flash_mb if reading.flash_mb is not None else None}
    board = [FACT % ("port", report.port + also), FACT % ("mac", reading.mac or "not read")]
    board += [FIELD_FACT % (field, shown[field] or "not read", report.fields[field]) for field in shown]
    board.append(board_look.say_last_deploy(report.last_deploy))
    image = [board_look.say_image_banner(report)] + ([FACT % ("simulation", report.simulation)] if report.simulation else [])
    image += report.caveats
    if report.limits:
        image += [board_look.LIMITS_HEADING_MESSAGE] + [board_look.say_limit(limit) for limit in report.limits]
    if report.unnamed_must:
        image += [board_look.MUST_UNNAMED_HEADING_MESSAGE] + [sim_project.LIMIT_PREFIX + line for line in report.unnamed_must]
    return [INDENT + "Board"] + [ITEM + printable(line) for line in board] + [INDENT + "Image"] + [ITEM + printable(line) for line in image]
# --- end MVP ---
