"""
`parts.py --signals`: the signals these parts ask for, as assign_pins.py input, as an Operation on the core (P726 PR 2). It
was `part_handlers._op_signals`. It writes nothing.
"""

import json

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer
from spark.sourcing.part_facts import signals_for
from spark.sourcing.part_operation import PartOperation


# --- MVP ---
class ListSignals(PartOperation):
    """Operation: `signals` as parts.py answers it: the signals as JSON, in the text too; a part nobody has is a problem on
    the ids given."""

    name = "signals"
    arguments = (Argument(("--signals",), "part_ids", str, "the signals these parts ask for, as assign_pins.py input", nargs="+", metavar="PART"),
                 ANSWER_ARGUMENTS["project"], COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, part_ids, project):
        found = {"signals": signals_for(part_ids, project)}
        return Answer(found, [json.dumps(found, indent=2)])
# --- end MVP ---
