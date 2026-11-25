"""
What an Operation returns (P442, W3-3): a Finding per thing it found, a NextStep per step an agent may take, and the
OperationResult that holds them with the data, the lines a person reads and the diagnostics. The status is never
declared: `OperationResult.status()` asks `outcomes.status_of`, so `ok` stays unreachable while anything is unchecked.
A Refusal is the sentence with its code that a refusal returns before there is an OperationResult (P684, P693).
"""

from collections import namedtuple

from spark.core import outcomes
from spark.core.codes import fix_of


# --- MVP ---
class Finding(namedtuple("Finding", "severity subject code sentence fix")):
    """
    Value: one thing an Operation found. `severity` is `outcomes.PROBLEMS` (it looked and found this) or
    `outcomes.COULD_NOT_RUN` (it could not look at this). `subject` says what a problem is about; it is None for most
    unchecked items, which the envelope prints without one, and a name for one that says what it lacks (P464). `code` is
    the word an agent decides on, `sentence` the text of this case and `fix` what to do.
    """

    __slots__ = ()

    @classmethod
    def of(cls, severity, subject, code, sentence, fix=None):
        """The Finding with the fix that `codes.fix_of` gives (P853)."""
        return cls(severity, subject, code, sentence, fix_of(code, fix))


#: Value: a step an agent may take next, with the fields of `outcomes.step`, which prints it. `needs_person` is None
#: unless the person's hands come first. `env` is None unless the step needs variables set, such as the store (P473).
NextStep = namedtuple("NextStep", "op argv why effects needs_yes needs_person env", defaults=((), False, None, None))


class Refusal(str):
    """
    Value: a refusal's sentence, the text a person reads, with its `code`. It is a str, so the text and every caller stay
    as they were. A `%` format or a `.strip()` gives a plain str back, so a site builds its Refusal from the final text.
    """

    code: str

    def __new__(cls, text, code):
        refusal = super().__new__(cls, text)
        refusal.code = code
        return refusal


def step_dicts(steps):
    """The NextSteps as the envelope's `next` holds them, each through `outcomes.step` with its env (P1035: the flat line too)."""
    return [outcomes.add_env(outcomes.step(s.op, s.argv, s.why, s.effects, s.needs_yes, s.needs_person), s.env) for s in steps]


def envelope_item(finding):
    """One Finding as the envelope's item, the one renderer of every interface: `subject, code, sentence, fix` for a
    problem, and the same for an unchecked item that has a subject, else `code, sentence, fix`, because the goldens compare bytes."""
    item = {"code": finding.code, "sentence": finding.sentence, "fix": finding.fix}
    return dict(subject=finding.subject, **item) if finding.subject is not None or finding.severity == outcomes.PROBLEMS else item


def output_schema():
    """The JSON Schema of the envelope every Operation answers with (P605): its keys are the keys of `outcomes.envelope`,
    so the schema cannot drift from what a run prints. `notes` and `assumptions` are keys only for a tool that passes them."""
    return {"type": "object", "required": list(outcomes.envelope(None, None)),
            "properties": {"envelope": {"const": 1}, "status": {"enum": [outcomes.OK, outcomes.PROBLEMS, outcomes.COULD_NOT_RUN]}}}


#: The four marks of a headline (P1032): what the text view's status line shows first, a symbol or its word.
MARK_OK, MARK_STOP, MARK_WARNING, MARK_UNCHECKED = "ok", "stop", "warning", "unchecked"
#: The mark each status gives when nothing finer is known: a problem is a stop, and could-not-run is not checked.
MARK_OF_STATUS = {outcomes.OK: MARK_OK, outcomes.PROBLEMS: MARK_STOP, outcomes.COULD_NOT_RUN: MARK_UNCHECKED}


class Headline(namedtuple("Headline", "sentence mark text_notes blocker verdict_fixes", defaults=((), None, ()))):
    """
    Value: the text view's status line of a result (P1032): its `sentence`, its `mark` (one of the four MARK_ words) and
    `text_notes`, the text view's own notes, which the JSON never holds. `blocker` is the code of the finding that says
    why there is no next step, or None: the text lists it first in its section, and Next points at it. `verdict_fixes`
    are the fixes that only restate the verdict, which the text view prints with no `fix:` line (the JSON keeps them).
    """

    __slots__ = ()

    @staticmethod
    def of_status(status):
        """The default mark of `status`: ok, stop for problems, unchecked for could-not-run."""
        return MARK_OF_STATUS[status]


class OperationResult(namedtuple("OperationResult", "data findings next lines diagnostics notes truncated assumptions headline",
                                 defaults=(None, (), (), (), (), None, None, None, None))):
    """
    Result: what `Operation.run` returns. `data` is the answer as JSON values, `findings` the Findings, `next` the
    NextSteps, `lines` the report a person reads (stdout in a CLI), `diagnostics` the lines for the person beside the
    answer, such as the board doctor's or a crash's traceback (stderr in a CLI, a log in a server), and `notes` what
    was said and never failing, or None. `truncated` is `outcomes.page`'s note when a listing was cut, else None, and
    `assumptions` what the answer rests on that nobody has checked, or None (P707: both keys of `outcomes.envelope`, for
    `audit` and the Operations P726 moves onto the core). `headline` is the text view's status line, a Headline (P1032):
    None prints the lines as they are. `to_envelope` never reads it, so the JSON keeps its bytes.
    """

    def status(self):
        """The one outcome, `outcomes.status_of` over the findings: `ok` is unreachable while one of them is unchecked."""
        return outcomes.status_of(self._of(outcomes.PROBLEMS), self._of(outcomes.COULD_NOT_RUN))

    def first_fix(self):
        """The fix of the first Finding that has one, else None: what a flat line carries as `fix` (P1055)."""
        return next((found.fix for found in self.findings if found.fix), None)

    def to_envelope(self, tool, op):
        """The `outcomes.envelope` of this result, each item made by `envelope_item`."""
        problems = [envelope_item(found) for found in self._of(outcomes.PROBLEMS)]
        unchecked = [envelope_item(found) for found in self._of(outcomes.COULD_NOT_RUN)]
        return outcomes.envelope(tool, op, self.data, problems, unchecked, step_dicts(self.next),
                                 self.truncated, notes=self.notes, assumptions=self.assumptions)

    def _of(self, severity):
        return [found for found in self.findings if found.severity == severity]
# --- end MVP ---
