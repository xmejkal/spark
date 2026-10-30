"""The error an Operation raises to answer instead of crashing (P442, W3-3): `run_operation` turns it into one Finding."""

from spark.core import outcomes
from spark.core.text_guards import ValueMessageError


# --- MVP ---
class SparkError(ValueMessageError):
    """
    Error: an Operation's answer that is no result, with its `code`, its `fix` and its `status` (`outcomes.COULD_NOT_RUN`
    unless `outcomes.PROBLEMS` is given). A ValueMessageError: the template is a constant and the values follow it, each
    put on one line. `run_operation` turns it into one Finding of that severity, so an envelope carries it as any item.
    """

    def __init__(self, template, *values, code, fix, status=outcomes.COULD_NOT_RUN):
        super().__init__(template, *values)
        self.code, self.fix, self.status = code, fix, status
# --- end MVP ---
