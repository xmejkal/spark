"""
The stops of the bench Operations (P657, W4-3): the board_codes code that a refusal is answered with, so grant, live, reach
and deploy name one stop by one code, the result of a stop before the board answered, and the result of a stop of the board
question (P892). An Operation puts the code in its Finding.
"""

from spark.bench import board_codes
from spark.bench import board_envelope
from spark.bench import board_look
from spark.records import board_records
from spark.records import records_codes
from spark.records import store
from spark.records import tool_finder
from spark.design.restricted_pins import BrokenRecordError
from spark.core import codes, outcomes
from spark.core.errors import SparkError
from spark.core.privacy import PastedLine
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import guard_sentence

# --- MVP ---
#: The refusals that carry no `reason` of their own, by class, with the code each gets.
CODE_OF_CLASS = ((tool_finder.ToolError, board_codes.TOOL_MISSING), (store.StoreError, board_codes.STORE_PROBLEM),
                 (board_records.BoardError, board_codes.BOARD_RECORD_UNUSABLE),
                 (BrokenRecordError, board_codes.BOARD_RECORD_UNUSABLE))
#: The codes of a tools file spark cannot read or that is no tools list (P1058): a ToolError of one keeps that code, and
#: stop_result gives it that Code's fix, read from here and never from the error. Any other ToolError is tool_missing.
TOOLS_FILE_CODES = (records_codes.FILE_REFUSED, records_codes.TOOLS_LIST_BROKEN)


def reason_of(refusal):
    """The board_codes code for a refusal that a bench Operation catches: the code of its class in CODE_OF_CLASS, the `code`
    of a SparkError (the kept board's record, P892), else the `reason` of a LookStopError, a GateClosedError or a DeployError
    (a FlashError too) (P433, P657)."""
    for kind, code in CODE_OF_CLASS:
        if isinstance(refusal, kind):
            return code
    return refusal.code if isinstance(refusal, SparkError) else refusal.reason


def stop_result(cannot, script, project, port, doctor_for=None):
    """The OperationResult of a stop before the board answered: no data (a caller `_replace`s it), one unchecked Finding with the stop's code, and
    its line on stderr as `<script>: <cannot>`, the port and the project put on one line first (P430). A SparkError's fix is
    the Finding's and a second line. A ToolError of a tools file (TOOLS_FILE_CODES) keeps its code, and that Code's fix is
    the Finding's, while stderr keeps its one line (P1058); reason_of folds this in later (P1083). `doctor_for(stop)`,
    when given, is asked for a LookStopError and answers (lines, DoctorProbeResult or None) as `board_doctor.stop_answer`
    does: `board_envelope.stop_said` then says the stop as look.py does, the doctor's lines or the asleep fix of a firmware that deep-sleeps, `port` being the port the person named (P1049).
    UNPARSED, a fact with no step, never takes the stop's own words. grant.py and bench.py record give it; live.py and
    reach.py not yet (P1057). After the asleep fix, `next` holds the look step that needs the person (P1048)."""
    places, sentence = board_records.ButtonPlaces.of_project(project), str(cannot)
    tools_file = _tools_file_code(cannot)
    fix, steps = (cannot.fix if isinstance(cannot, SparkError) else tools_file.fix if tools_file else ""), []
    if doctor_for is not None and isinstance(cannot, board_look.LookStopError):
        answer = doctor_for(cannot)
        lines, sentence, fix = board_envelope.stop_said(script, cannot, answer, port, project)
        if not (answer[1] or fix.startswith(board_envelope.ASLEEP_KNOWS)):  # the review of #1569: UNPARSED keeps the old stop
            lines, sentence, fix = answer[0], str(cannot), ""
        steps = board_envelope.asleep_next(fix, project.resolve())
        # no `project` here: these lines hold it only in a tool problem, whose path is flat already (P444), as in look.py
        said = guard_sentence("\n".join(lines), port, places.boot, places.reset, places.orientation)
    else:
        said = guard_sentence("%s: %s" % (script, cannot), port, project)
    finding = Finding(outcomes.COULD_NOT_RUN, None, tools_file or reason_of(cannot), sentence, fix)
    return OperationResult(None, [finding], steps, diagnostics=said.split("\n") + (["%s: %s" % (script, fix)] if isinstance(cannot, SparkError) else []))


def _tools_file_code(cannot):
    """The Code of TOOLS_FILE_CODES that a ToolError `cannot` carries, else None: any other refusal (P1058)."""
    if isinstance(cannot, tool_finder.ToolError):
        return next((code for code in TOOLS_FILE_CODES if code == cannot.code), None)
    return None


def undoctored(script):
    """The `doctor_for` of a stop_result whose script runs no doctor (bench.py record): the answer that
    board_doctor.stop_answer gives a stop with no port, so the stop is said as look.py says it (P1049)."""
    return lambda stop: (["%s: %s" % (script, stop)], None)


def question_result(stopped, script, data=None):
    """The OperationResult of a known_board.BoardQuestionError `stopped` (P892 part 2): its Findings, `data` (None: nothing on
    stdout), and its lines on stderr, each after `<script>: `: each Finding's sentence and fix, then the error's `more`. The
    fix of an open question holds the JSON to paste, so it is a PastedLine, and Privacy leaves the key and the line whole (P677)."""
    lines = []
    for found in stopped.findings:
        fix = "%s: %s" % (script, found.fix)
        lines += ["%s: %s" % (script, found.sentence)] + ([PastedLine(fix) if found.code == codes.NEEDS_REPLY else fix] if found.fix else [])
    return OperationResult(data, list(stopped.findings), diagnostics=lines + ["%s: %s" % (script, line) for line in stopped.more])
# --- end MVP ---
