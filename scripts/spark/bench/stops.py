"""
The stops of the bench Operations (P657, W4-3): the board_codes code that a refusal is answered with, so grant, live, reach
and deploy name one stop by one code, and the result of a stop before the board answered. An Operation puts the code in its Finding.
"""

import board_codes
from spark.bench import board_envelope
from spark.bench import board_look
import boards
import store
import tools
from restricted_pins import BrokenRecordError
from spark.core import outcomes
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import guard_sentence

# --- MVP ---
#: The refusals that carry no `reason` of their own, by class, with the code each gets.
CODE_OF_CLASS = ((tools.ToolProblem, board_codes.TOOL_MISSING), (store.StoreProblem, board_codes.STORE_PROBLEM),
                 (boards.BoardError, board_codes.BOARD_RECORD_UNUSABLE), (BrokenRecordError, board_codes.BOARD_RECORD_UNUSABLE))


def reason_of(refusal):
    """The board_codes code for a refusal that a bench Operation catches: the code of its class in CODE_OF_CLASS, else the
    `reason` of a LookStop, a GateClosedError or a DeployError (a FlashError too) (P433, P657)."""
    for kind, code in CODE_OF_CLASS:
        if isinstance(refusal, kind):
            return code
    return refusal.reason


def stop_result(cannot, script, project, port, doctor_for=None):
    """The OperationResult of a stop before the board answered: no data (a caller `_replace`s it), one unchecked Finding with the stop's code, and
    its line on stderr as `<script>: <cannot>`, the port and the project put on one line first (P430). `doctor_for(stop)`,
    when given, is asked for a LookStop and answers (lines, BoardDoctorResult or None) as `board_doctor.stop_answer` does: the
    doctor's lines then replace the sentence, as look.py's stop does."""
    doctor, places = None, boards.ButtonPlaces.of_project(project)
    if doctor_for is not None and isinstance(cannot, board_look.LookStop):
        lines, doctor = doctor_for(cannot)
        said = guard_sentence("\n".join(lines), port, places.boot, places.reset, places.orientation)
    else:
        said = guard_sentence("%s: %s" % (script, cannot), port, project)
    finding = Finding(outcomes.COULD_NOT_RUN, None, reason_of(cannot), str(cannot), board_envelope.doctor_fix(doctor, places))
    return OperationResult(None, [finding], diagnostics=said.split("\n"))
# --- end MVP ---
