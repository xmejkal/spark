"""
The base of a sourcing Operation on the core (P726 PR 2): records' `AnswerOperation` with the one rule `parts.main` kept for
the part handlers: a `PartError` (no such part, a record off the contract, a promotion that would overwrite) is a problem on
the part the flag names, exit 1, never a could-not-run item. The flag is the first Argument, so its value is the subject: a
list joined with spaces, a str as it is, else none (`parts._part_problem`'s rule, which stays in the CLI for the payload
handlers until PR 3).
"""

from spark.records.answer_operation import AnswerOperation
from spark.records.record_kind import Answer, _problem
from spark.sourcing.part_records import PartError


# --- MVP ---
class PartOperation(AnswerOperation):
    """
    Operation: a parts.py handler of the sourcing area on the core. A subclass gives `name`, `arguments` (its flag first),
    `effects` and `build_answer`, as `AnswerOperation` asks; `answer_refusal` turns a `PartError` into a problem whose
    subject is the flag's value, and leaves every other coded refusal to the base.
    """

    def answer_refusal(self, broken, values):
        if not isinstance(broken, PartError):
            return super().answer_refusal(broken, values)
        value = values.get(self.arguments[0].dest)  # the str tokens alone: a loaded payload (PR 3) never names the part
        subject = " ".join(token for token in value if isinstance(token, str)) if isinstance(value, list) else (value if isinstance(value, str) else None)
        return Answer(problems=[_problem(subject, str(broken), code=broken.code)])
# --- end MVP ---
