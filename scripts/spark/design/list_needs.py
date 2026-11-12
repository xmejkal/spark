"""
`parts.py --needs`: a project's needs, what each does, its condition and its mark, as an Operation on the core (P726). It
was `goal_handlers._op_needs`. It writes nothing.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records.answer_operation import AnswerOperation
from spark.records.record_kind import Answer
from spark.design import needs

# --- MVP ---
#: The one line when a project has no needs yet.
NO_NEEDS_LINE = "  no needs yet — /spark:idea writes them"


class ListNeeds(AnswerOperation):
    """Operation: `needs` as parts.py answers it: one line per need, or the one line that says there are none yet."""

    name = "needs"
    data_keys = ('needs',)
    arguments = (Argument(("--needs",), "project", str, "a project's needs: what each does, its condition, its mark", metavar="PROJECT"),
                 COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, project):
        listed = needs.read(project)
        return Answer({"needs": listed}, ["  %-10s %s / %s%s%s" % (n["id"], n.get("does"), n.get("what"),
                                                                   "  (%s)" % n["condition"] if n.get("condition") else "",
                                                                   "  [%s]" % n["mark"] if n.get("mark") else "") for n in listed]
                      or [NO_NEEDS_LINE])
# --- end MVP ---
