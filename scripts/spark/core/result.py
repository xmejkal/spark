"""
What an Operation returns (P442, W3-3): a Finding per thing it found, a NextStep per step an agent may take, and the
OperationResult that holds them with the data, the lines a person reads and the diagnostics. The status is never
declared: `OperationResult.status()` asks `outcomes.status_of`, so `ok` stays unreachable while anything is unchecked.
A Refusal is the sentence with its code that a refusal returns before there is an OperationResult (P684, P693).
"""

from collections import namedtuple

from spark.core import outcomes

# --- MVP ---
#: Value: one thing an Operation found. `severity` is `outcomes.PROBLEMS` (it looked and found this) or
#: `outcomes.COULD_NOT_RUN` (it could not look at this). `subject` says what a problem is about; it is None for most
#: unchecked items, which the envelope prints without one, and a name for one that says what it lacks (P464). `code` is the word an agent decides on, `fix` what to do.
Finding = namedtuple("Finding", "severity subject code sentence fix")
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


class OperationResult(namedtuple("OperationResult", "data findings next lines diagnostics notes", defaults=(None, (), (), (), (), None))):
    """
    Result: what `Operation.run` returns. `data` is the answer as JSON values, `findings` the Findings, `next` the
    NextSteps, `lines` the report a person reads (stdout in a CLI), `diagnostics` the lines for the person beside the
    answer, such as the board doctor's or a crash's traceback (stderr in a CLI, a log in a server), and `notes` what
    was said and never failing, or None.
    """

    def status(self):
        """The one outcome, `outcomes.status_of` over the findings: `ok` is unreachable while one of them is unchecked."""
        return outcomes.status_of(self._of(outcomes.PROBLEMS), self._of(outcomes.COULD_NOT_RUN))

    def to_envelope(self, tool, op):
        """The `outcomes.envelope` of this result, each item made by `envelope_item`."""
        problems = [envelope_item(found) for found in self._of(outcomes.PROBLEMS)]
        unchecked = [envelope_item(found) for found in self._of(outcomes.COULD_NOT_RUN)]
        return outcomes.envelope(tool, op, self.data, problems, unchecked, [outcomes.add_env(outcomes.step(s.op, s.argv, s.why, s.effects, s.needs_yes, s.needs_person), s.env) for s in self.next], notes=self.notes)

    def _of(self, severity):
        return [found for found in self.findings if found.severity == severity]
# --- end MVP ---
