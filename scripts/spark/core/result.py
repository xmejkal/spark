"""
What an Operation returns (P442, W3-3): a Finding per thing it found, a NextStep per step an agent may take, and the
OperationResult that holds them with the data, the lines a person reads and the diagnostics. The status is never
declared: `OperationResult.status()` asks `outcomes.status_of`, so `ok` stays unreachable while anything is unchecked.
"""

from collections import namedtuple

from spark.core import outcomes

# --- MVP ---
#: Value: one thing an Operation found. `severity` is `outcomes.PROBLEMS` (it looked and found this) or
#: `outcomes.COULD_NOT_RUN` (it could not look at this). `subject` says what a problem is about; it is None for an
#: unchecked item, which the envelope prints without one. `code` is the word an agent decides on, `fix` what to do.
Finding = namedtuple("Finding", "severity subject code sentence fix")
#: Value: a step an agent may take next, with the fields of `outcomes.step`, which prints it. `needs_person` is None
#: unless the person's hands come first.
NextStep = namedtuple("NextStep", "op argv why effects needs_yes needs_person", defaults=((), False, None))


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
        """The `outcomes.envelope` of this result. A problem is `subject, code, sentence, fix` and an unchecked item
        `code, sentence, fix`, in this key order, because the goldens compare bytes."""
        problems = [{"subject": found.subject, "code": found.code, "sentence": found.sentence, "fix": found.fix}
                    for found in self._of(outcomes.PROBLEMS)]
        unchecked = [{"code": found.code, "sentence": found.sentence, "fix": found.fix} for found in self._of(outcomes.COULD_NOT_RUN)]
        return outcomes.envelope(tool, op, self.data, problems, unchecked, [outcomes.step(*step) for step in self.next], notes=self.notes)

    def _of(self, severity):
        return [found for found in self.findings if found.severity == severity]
# --- end MVP ---
