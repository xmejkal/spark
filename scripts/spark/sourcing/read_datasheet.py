"""
`parts.py --read`: read a datasheet page by page and stop where every wanted fact is on a table row, as an Operation on the
core (P726 PR 2). It was `part_handlers._op_read`; `datasheets.read_datasheet` does the reading and builds the Answer. It
writes nothing.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.sourcing import datasheets
from spark.sourcing.part_operation import PartOperation

# --- MVP ---
#: The help of the options `--read` reads, worded as parts.py's OPTIONS rows (parts.py reads them here).
WANT_HELP = "with --read: the facts to find, named as records name them (forward_voltage_v …)"
LABEL_HELP = "with --read: extra words a datasheet uses for a fact"


def words_by_fact(labels):
    """The `--label FACT=WORD|WORD` flags as the reader takes them: each fact's extra words, lower-case, blanks dropped."""
    by_fact = {}
    for given in labels or []:
        fact, _, words = given.partition("=")
        by_fact[fact] = [word.strip().lower() for word in words.split("|") if word.strip()]
    return by_fact


class ReadDatasheet(PartOperation):
    """Operation: `read` as parts.py answers it: the facts found with their pages, a fact not on a table row a problem;
    `--label FACT=WORD|WORD` adds the maker's own words for a fact, once per flag."""

    name = "read"
    arguments = (Argument(("--read",), "datasheet", str, "read a datasheet page by page and stop where every --want fact is on a table row",
                          metavar="PDF"),
                 Argument(("--want",), "wanted", str, WANT_HELP, nargs="+", metavar="FACT"),
                 Argument(("--label",), "labels", str, LABEL_HELP, metavar="FACT=WORD|WORD", repeats=True),
                 ANSWER_ARGUMENTS["project"], COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, datasheet, wanted, labels, project):
        return datasheets.read_datasheet(datasheet, wanted or [], words_by_fact(labels), project)
# --- end MVP ---
