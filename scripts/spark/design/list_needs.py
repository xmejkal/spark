"""
`parts.py --needs`: a project's needs, what each does, its condition, its mark and its picks (P1141), as an Operation on
the core (P726). It was `goal_handlers._op_needs`. It writes nothing.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records.answer_operation import AnswerOperation
from spark.records.record_kind import Answer
from spark.design import needs

# --- MVP ---
#: The one line when a project has no needs yet.
NO_NEEDS_LINE = "  no needs yet — /spark:idea writes them"
#: The words of a need's picks (P1141): the key of each part it picks.
PICKED = "  picked: %s"


def picked_words(need):
    """The words of the need's picks, each pick's key (a record's id, or a drawer entry's key), or "" with no pick."""
    keys = [next(iter(pick.values())) for pick in need.get("pick") or []]
    return PICKED % ", ".join(keys) if keys else ""


class ListNeeds(AnswerOperation):
    """Operation: `needs` as parts.py answers it: one line per need, with its picks, or the one line that says there are none yet."""

    name = "needs"
    data_keys = ('needs',)
    arguments = (Argument(("--needs",), "project", str, "a project's needs: what each does, its condition, its mark, its picks", metavar="PROJECT"),
                 COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, project):
        listed = needs.read(project)
        return Answer({"needs": listed}, ["  %-10s %s / %s%s%s" % (n["id"], n.get("does"), n.get("what"),
                                                                   "  (%s)" % n["condition"] if n.get("condition") else "",
                                                                   "  [%s]" % n["mark"] if n.get("mark") else "")
                                                       + picked_words(n) + ("  [aside]" if n.get("aside") else "") for n in listed]
                      or [NO_NEEDS_LINE])
# --- end MVP ---
