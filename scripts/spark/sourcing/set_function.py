"""
`parts.py --function-set`: what a part does, set in the record's own home, as an Operation on the core (P726 PR 3). It was
`parts._op_function_set`. Never spark's library. The CLI reads the file and hands the list in (`Argument.payload`).
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.part_records import function_problems
from spark.sourcing.record_home import set_fields


# --- MVP ---
class SetFunction(PartOperation):
    """Operation: `function-set` as parts.py answers it: what was set, or why the write was refused; a part nobody has is a
    problem on its id."""

    name = "function-set"
    arguments = (Argument(("--function-set",), "part_and_function", str,
                          "set what a part does — a JSON [{does, what}] in FILE (- for stdin) — in the record's own home (--project picks the project's copy); never spark's library",
                          nargs=2, metavar=("PART", "FILE"), payload=1),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, part_and_function, project, dry_run):
        part_id, function = part_and_function
        answer = set_fields(part_id, project, {"function": function}, dry_run, lambda record, after, path:
                            function_problems(after) if function else ["a function is a non-empty list [{does, what}]"])
        return answer._replace(data=dict(answer.data, was=answer.data["was"]["function"], now=function)) if answer.data else answer
# --- end MVP ---
