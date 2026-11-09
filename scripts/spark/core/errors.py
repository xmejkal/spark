"""The errors that carry a code: CodedMessageError, a refusal with its code (P716), and SparkError, the error an Operation
raises to answer instead of crashing (P442, W3-3), which `run_operation` turns into one Finding."""

from spark.core import outcomes
from spark.core.text_guards import ValueMessageError


# --- MVP ---
class CodedMessageError(ValueMessageError):
    """Error: a ValueMessageError that names its `code`, the word an agent decides on, never the sentence (P716). Every
    raise must give it: `raise ToolError("%s: no tool called %r", name, tool, code=records_codes.UNKNOWN_TOOL)`."""

    def __init__(self, template, *values, code):
        super().__init__(template, *values)
        self.code = code


class SparkError(CodedMessageError):
    """
    Error: an Operation's answer that is no result, with its `code`, its `fix` and its `status` (`outcomes.COULD_NOT_RUN`
    unless `outcomes.PROBLEMS` is given). A ValueMessageError: the template is a constant and the values follow it, each
    put on one line. `run_operation` turns it into one Finding of that severity, so an envelope carries it as any item.
    """

    def __init__(self, template, *values, code, fix, status=outcomes.COULD_NOT_RUN):
        super().__init__(template, *values, code=code)
        self.fix, self.status = fix, status
# --- end MVP ---
