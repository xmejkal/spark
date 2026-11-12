"""
`parts.py --unverified`: what nobody has checked about these parts, one assumption a fact, as an Operation on the core
(P726 PR 2). It was `part_handlers._op_unverified`. Each open fact says who reads it (P738) and the next step writes a
bench result back (`--fact-set`). It writes nothing.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.core.outcomes import add_env, step
from spark.records import store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.fact_needs import FactNeeds
from spark.records.record_kind import Answer, WRITE_BACK_HINT
from spark.sourcing.part_facts import unverified
from spark.sourcing.part_operation import PartOperation


# --- MVP ---
def _reader_line(need):
    """One reader of an open fact: who, and whether it reads the fact today or which card makes it read (P738)."""
    return "      read by %s (%s)" % (need.consumer, need.status if need.reads else "%s, %s" % (need.status, need.card))


class ListUnverified(PartOperation):
    """Operation: `unverified` as parts.py answers it: each unchecked fact with why it matters and who reads it, as an
    assumption, and the `--fact-set` step that writes a result back; a part nobody has is a problem on the ids given."""

    name = "unverified"
    arguments = (Argument(("--unverified",), "part_ids", str, "what nobody has checked about these parts, one assumption a fact",
                          nargs="+", metavar="PART"),
                 ANSWER_ARGUMENTS["project"], COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, part_ids, project):
        questions = unverified(part_ids, project)
        needs = FactNeeds.from_file()  # P738: who reads each open fact, joined on its `write` key, never on English
        lines = ["  everything these parts claim has been checked."] if not questions else \
            ["  %d thing(s) nobody has checked:\n" % len(questions)]
        assumptions = []
        for q in questions:
            lines.append("  %s.%s = %s" % (q["part"], q["fact"], q["assumed"]))
            if q["why_it_matters"]:
                lines.append("      %s" % q["why_it_matters"])
            entry = {"fact": "%s.%s" % (q["part"], q["fact"]), "basis": "unverified", "assumed": q["assumed"],
                     "sentence": q["why_it_matters"], "source": q["source"], "write": q["write"]}
            read_by = needs.of_fact(q["write"] or "")
            lines.extend(_reader_line(need) for need in read_by)
            if read_by:
                entry["read_by"] = [need.to_dict() for need in read_by]
            assumptions.append(entry)
        owners = [q["part"] for q in questions if q["write"]]  # a row with no `write` cannot go back by --fact-set
        follow = [add_env(step("fact-set", ["--fact-set", owners[0], "<file>"], WRITE_BACK_HINT, ["writes"]), store.read_given_env())] if owners else []
        return Answer({"parts": list(part_ids)}, lines, assumptions=assumptions, next=follow)
# --- end MVP ---
