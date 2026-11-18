"""
The stops of the bench Operations (P657, W4-3): the board_codes code that a refusal is answered with, so grant, live, reach
and deploy name one stop by one code, and the result of a stop before the board answered. An Operation puts the code in its Finding.
"""

from spark.bench import board_codes
from spark.bench import board_envelope
from spark.bench import board_look
from spark.records import board_records
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
    the Finding's and a second line. `doctor_for(stop)`, when given, is asked for a LookStopError and answers (lines,
    DoctorProbeResult or None) as `board_doctor.stop_answer` does: the doctor's lines then replace the sentence, as look.py's stop does."""
    doctor, places = None, board_records.ButtonPlaces.of_project(project)
    if doctor_for is not None and isinstance(cannot, board_look.LookStopError):
        lines, doctor = doctor_for(cannot)
        said = guard_sentence("\n".join(lines), port, places.boot, places.reset, places.orientation)
    else:
        said = guard_sentence("%s: %s" % (script, cannot), port, project)
    fix = cannot.fix if isinstance(cannot, SparkError) else board_envelope.doctor_fix(doctor, places)
    finding = Finding(outcomes.COULD_NOT_RUN, None, reason_of(cannot), str(cannot), fix)
    return OperationResult(None, [finding], diagnostics=said.split("\n") + (["%s: %s" % (script, fix)] if isinstance(cannot, SparkError) else []))


def question_result(stopped, script, data=None):
    """The OperationResult of a known_board.BoardQuestionError `stopped` (P892 part 2): its Findings, `data` (None: nothing on
    stdout), and its lines on stderr, each after `<script>: `. The line with the JSON to paste is a PastedLine, so Privacy
    leaves the key and the line whole (P677)."""
    pasted = [found.fix for found in stopped.findings if found.code == codes.NEEDS_REPLY]
    lines = [PastedLine("%s: %s" % (script, line)) if line in pasted else "%s: %s" % (script, line) for line in stopped.lines if line]
    return OperationResult(data, list(stopped.findings), diagnostics=lines)
# --- end MVP ---
