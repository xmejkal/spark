"""
`parts.py --kept`: find a kept document by every word, with no network, and every fact resting on it, as an Operation on
the core (P726 PR 2). It was `part_handlers._op_kept`. It writes nothing.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer
from spark.sourcing import datasheets
from spark.sourcing.part_operation import PartOperation


# --- MVP ---
class FindKept(PartOperation):
    """Operation: `kept` as parts.py answers it: the kept documents every word fits, or that nothing does."""

    name = "kept"
    data_keys = ('found',)
    arguments = (Argument(("--kept",), "words", str, "find a kept document by every word, with no network, and every fact resting on it",
                          nargs="+", metavar="WORD"),
                 ANSWER_ARGUMENTS["project"], COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, words, project):
        found = datasheets.find_kept(words, project)
        return Answer({"found": found}, found or ["nothing kept matches %s — fetch it, or --keep a file you have" % " ".join(words)])
# --- end MVP ---
