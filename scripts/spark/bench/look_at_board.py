"""
The look as an Operation on the core (P442, W3-3): read the board on USB without changing it, compare it with the
project's board record, and give a token. look.py is its CLI. The lines, the findings and the next step are the ones
look.py printed before it (board_look.report_lines and board_envelope's look items), so no golden changed; a crash, now a
`crash` envelope and exit 2, is the one new output.
"""

from spark.bench import board_codes
from spark.bench import board_doctor
from spark.bench import board_envelope
from spark.bench import board_look
from spark.bench.deploy_stages import DeployPhase
from spark.records import board_records
from spark.bench.firmware_platform import MicroPythonPlatform
from spark.bench.image_evidence import IGNORE_OLDER_RUNS_FLAG, NO_SIMULATION_FLAG, evidence_for
from spark.bench import bench_privacy
from spark.core import outcomes
from spark.core.events import Event
from spark.core.operation import BOARD, COMMON_ARGUMENTS, READS, RUNS, Argument, Operation
from spark.core.result import Finding, NextStep, OperationResult
from spark.core.text_guards import guard_sentence

# --- MVP ---
#: The lines of a stop name the script that printed them before the core (board_doctor.stop_answer), so they read the
#: same from every frontend.
SCRIPT = "look.py"
#: The group of the two flags that pick the evidence: they exclude each other.
EVIDENCE_GROUP = "evidence"
#: What the look does, the paragraphs of look.py's `--help` before its `--json` and exit codes, line breaks and all
#: (P481). Its two `--json` mentions stay until the other CLIs move (P481 PR 2).
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

With two or more boards on USB, --port is needed: the look lists them and reads none. --ignore-older-runs gives a token
even when a log in sim/runs/ tested another image, as deploy.py --ignore-older-runs flashes it. --no-simulation gives a
token for an image that no simulation tested: firmware/ has a main.py, every .py file compiles, no run in sim/runs/ failed on the image and the image holds
firmware/ as it is now. Else it prints why not, and the command that builds the image. deploy.py needs the same flag.

When esptool's read of the board fails, the board doctor (P282) runs two checks: whether `mpremote devs` lists the
port, and two seconds of the console with the port's lock. It prints esptool's own error line, each check's fact,
and one next step for your hands, as the last line. Its look at the console can restart the board."""


class LookAtBoard(Operation):
    """
    Operation: the look. It builds the evidence (image_evidence), the LookService (board_look.looker) and runs it, and
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
    arguments = (COMMON_ARGUMENTS["project"], COMMON_ARGUMENTS["port"],
                 Argument((IGNORE_OLDER_RUNS_FLAG,), "ignore_older_runs", bool,
                          "give a token even when a log in sim/runs/ tested another image (default: no token)", group=EVIDENCE_GROUP),
                 Argument((NO_SIMULATION_FLAG,), "no_simulation", bool,
                          "give a token for an image that no simulation tested, when firmware/ has a main.py, "
                          "compiles and is what the image holds (default: a passed run must name the image)", group=EVIDENCE_GROUP),
                 COMMON_ARGUMENTS["json"])
    effects = (READS, RUNS, BOARD)
    privacy_for = staticmethod(bench_privacy.privacy_for)

    def __init__(self, records=None):
        self.records = records

    def run(self, project, port, ignore_older_runs, no_simulation, *, outside):
        evidence = evidence_for(project, no_simulation, ignore_older_runs, find_tool=outside.find_tool, run=outside.run)
        platform = MicroPythonPlatform(project, outside.find_tool)
        # P507: after the evidence and the platform, which touch no board, and right before the esptool read
        outside.report(Event.begin(DeployPhase.LOOK))
        try:
            report = board_look.looker(platform, outside.run, self.records).run(project, port, evidence)
        except board_look.LookStopError as stop:
            return self._stopped(stop, platform, port, outside)
        return self._found(report, project.resolve(), evidence)

    @staticmethod
    def _found(report, project, evidence):
        """The result of a LookReport: the lists LookReport.status counts, as Findings, and the deploy step with a token."""
        findings = [Finding(outcomes.PROBLEMS, "stop", stop.code, stop.sentence, "deploy.py will refuse") for stop in report.stops]
        findings += [Finding(outcomes.PROBLEMS, "flash", board_codes.FLASH_DIFFERS, warning, "deploy.py asks the person to accept it")
                     for warning in report.warnings]
        findings += [Finding(outcomes.COULD_NOT_RUN, None, board_codes.FIELD_UNKNOWN, "%s unknown: %s" % each,
                             "unknown is not a pass: deploy.py names it and asks the person") for each in report.unknown.items()]
        no_token = report.no_token_reason()
        if no_token:
            findings.append(Finding(outcomes.COULD_NOT_RUN, None, no_token.code, "no token: %s" % no_token.sentence, "fix that, then run look.py again"))
        if report.last_deploy_not_checked():
            findings.append(Finding(outcomes.COULD_NOT_RUN, None, board_codes.LAST_DEPLOY_NOT_CHECKED,
                                    "last deploy not checked: %s" % report.last_deploy.why, report.last_deploy_fix()))
        token = report.token()
        following = [NextStep(**board_envelope.deploy_step(
            project, token, report.port, evidence,
            "erases ALL of the flash, then writes the image. Relay the warnings first. " + board_envelope.yes_rule(evidence)))] if token else []
        return OperationResult(report.to_dict(), findings, following, board_look.report_lines(report))

    @staticmethod
    def _stopped(stop, platform, port, outside):
        """The result of a LookStopError: one unchecked Finding, the doctor's facts in `data`, its lines as the diagnostics."""
        lines, doctor = board_doctor.stop_answer(SCRIPT, stop, platform, outside.run)
        places = board_records.ButtonPlaces.of_project(platform.project)
        # the port and the button words, each on one line (P430); a tool problem's path is flat already (P444)
        said = guard_sentence("\n".join(lines), port, places.boot, places.reset, places.orientation)
        return OperationResult({"doctor": board_doctor.as_dict(doctor)} if doctor else None,
                               [Finding(outcomes.COULD_NOT_RUN, None, stop.reason, str(stop), board_envelope.doctor_fix(doctor, places))],
                               diagnostics=said.split("\n"))
# --- end MVP ---
