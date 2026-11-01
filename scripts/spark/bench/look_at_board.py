"""
The look as an Operation on the core (P442, W3-3): read the board on USB without changing it, compare it with the
project's board record, and give a token. look.py is its CLI. The lines, the findings and the next step are the ones
look.py printed before it (board_look.report_lines and board_envelope's look items), so no golden changed; a crash, now a
`crash` envelope and exit 2, is the one new output.
"""

import board_codes
import board_doctor
import board_envelope
import board_look
import boards
from firmware_platform import MicroPythonPlatform
from image_evidence import IGNORE_OLDER_RUNS_FLAG, NO_SIMULATION_FLAG, evidence_for
from spark.core import outcomes
from spark.core.operation import BOARD, COMMON_ARGUMENTS, READS, RUNS, Argument, Operation
from spark.core.result import Finding, NextStep, OperationResult
from spark.core.text_guards import guard_sentence

# --- MVP ---
#: The lines of a stop name the script that printed them before the core (board_doctor.stop_answer), so they read the
#: same from every frontend.
SCRIPT = "look.py"
#: The group of the two flags that pick the evidence: they exclude each other.
EVIDENCE_GROUP = "evidence"


class LookAtBoard(Operation):
    """
    Operation: the look. It builds the evidence (image_evidence), the LookService (board_look.looker) and runs it, and
    returns the LookReport as an OperationResult: its stops and warnings are problems, its unknown fields, a missing token
    and a last deploy it could not check are unchecked, and a token brings the deploy step. A LookStop is one unchecked
    Finding with the stop's reason, and the board doctor's lines are the diagnostics. It writes nothing on the board.
    """

    name = "look"
    arguments = (COMMON_ARGUMENTS["project"], COMMON_ARGUMENTS["port"],
                 Argument((IGNORE_OLDER_RUNS_FLAG,), "ignore_older_runs", bool,
                          "give a token even when a log in sim/runs/ tested another image (default: no token)", group=EVIDENCE_GROUP),
                 Argument((NO_SIMULATION_FLAG,), "no_simulation", bool,
                          "give a token for an image that no simulation tested, when firmware/ has a main.py, "
                          "compiles and is what the image holds (default: a passed run must name the image)", group=EVIDENCE_GROUP),
                 COMMON_ARGUMENTS["json"])
    effects = (READS, RUNS, BOARD)

    def run(self, project, port, ignore_older_runs, no_simulation, *, outside):
        evidence = evidence_for(project, no_simulation, ignore_older_runs, outside.find_tool)
        platform = MicroPythonPlatform(project, outside.find_tool)
        try:
            report = board_look.looker(platform, outside.run).run(project, port, evidence)
        except board_look.LookStop as stop:
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
        """The result of a LookStop: one unchecked Finding, the doctor's facts in `data`, its lines as the diagnostics."""
        lines, doctor = board_doctor.stop_answer(SCRIPT, stop, platform, outside.run)
        places = boards.ButtonPlaces.of_project(platform.project)
        # the port and the button words, each on one line (P430); a tool problem's path is flat already (P444)
        said = guard_sentence("\n".join(lines), port, places.boot, places.reset, places.orientation)
        return OperationResult({"doctor": board_doctor.as_dict(doctor)} if doctor else None,
                               [Finding(outcomes.COULD_NOT_RUN, None, stop.reason, str(stop), board_envelope.doctor_fix(doctor, places))],
                               diagnostics=said.split("\n"))
# --- end MVP ---
