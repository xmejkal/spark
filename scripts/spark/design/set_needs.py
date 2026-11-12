"""
`parts.py --needs-set`: a project's needs set from a JSON list, as an Operation on the core (P726 PR 3). It was
`parts._op_needs_set`. Every write sets, never adds. The CLI reads the file and hands the list in (`Argument.payload`).
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.records.answer_operation import ANSWER_ARGUMENTS, AnswerOperation
from spark.records.record_kind import Answer
from spark.sourcing.write_answers import write_lines
from spark.design import needs


# --- MVP ---
class SetNeeds(AnswerOperation):
    """Operation: `needs-set` as parts.py answers it: each change made or refused, and whether the file was written."""

    name = "needs-set"
    data_keys = ('changes', 'written')
    arguments = (Argument(("--needs-set",), "project_and_items", str,
                          "set a project's needs from a JSON list in FILE (- for stdin): every write sets, never adds",
                          nargs=2, metavar=("PROJECT", "FILE"), payload=1),
                 ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, project_and_items, dry_run):
        target, items = project_and_items
        after, changes, problems = needs.plan_set(target, items)
        written = not (problems or dry_run)
        if written and changes:
            needs.write(target, after)
        return Answer({"changes": changes, "written": written}, write_lines(changes, problems, dry_run), problems=problems)
# --- end MVP ---
