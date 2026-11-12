"""
`parts.py --show`: one record, wherever it lives, and its CONFLICT lines, as an Operation on the core (P726 PR 2). It was
`part_handlers._op_show`. A CONFLICT on verified facts is a problem (exit 1), on unverified ones an assumption (P124). It
writes nothing.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _problem
from spark.sourcing.part_facts import describe
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.part_records import any_record
from spark.sourcing.part_rules import conflicts_of


# --- MVP ---
class ShowPart(PartOperation):
    """Operation: `show` as parts.py answers it: the record described, each CONFLICT a problem or an assumption; a part
    nobody has is a problem on its id."""

    name = "show"
    arguments = (Argument(("--show",), "part_id", str, "one record, wherever it lives, and its CONFLICT lines: on verified facts a problem "
                          "(exit 1), on unverified ones an assumption", metavar="PART"),
                 ANSWER_ARGUMENTS["project"], COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, part_id, project):
        part, problems, assumptions = any_record(part_id, project), [], []
        for conflict in conflicts_of(part):
            where = "%s.%s" % (part_id, conflict["pin"])  # the part and the pin the CONFLICT is about
            if conflict["rests_on"]:
                assumptions.append({"fact": where, "basis": "unmeasured", "rests_on": conflict["rests_on"],
                                    "sentence": "CONFLICT: " + conflict["line"], "upgrade": conflict["upgrade"]})
            else:
                problems.append(_problem(where, "CONFLICT: " + conflict["line"], conflict["fix"]))
        return Answer({"record": part}, [describe(part)], problems=problems, assumptions=assumptions)
# --- end MVP ---
