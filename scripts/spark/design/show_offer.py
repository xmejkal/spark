"""
`parts.py --offer`: what one offer says of itself, for the chooser to read (P211), as an Operation on the core (P726). It
was `goal_handlers._op_offer`. It writes nothing.
"""

from pathlib import Path

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records.answer_operation import AnswerOperation
from spark.records.record_kind import Answer, _problem
from spark.design import design_codes, needs
from spark.design.find_offers import PROJECT_HELP

# --- MVP ---
#: The sentence of a key nothing live has.
OFFER_UNKNOWN_SENTENCE = "no record and no live drawer entry called %r — `--need` and `--drawer` list what exists"


class ShowOffer(AnswerOperation):
    """Operation: `offer` as parts.py answers it: the whole text of one offer, the record's id or the drawer entry's key,
    or one problem when nothing live has that key."""

    name = "offer"
    arguments = (Argument(("--offer",), "key", str, "what one offer says of itself, for the chooser to read: a record's id or a drawer entry's "
                          "key — about, description, tags, what it does, its names, power and size. --project reads the project's own records",
                          metavar="KEY"),
                 Argument(("--project",), "project", Path, PROJECT_HELP),
                 COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, key, project):
        found = needs.offer(key, project)
        if found is None:
            return Answer(problems=[_problem(key, OFFER_UNKNOWN_SENTENCE % key, code=design_codes.OFFER_UNKNOWN)])
        return Answer({"offer": found.as_dict()}, found.describe().splitlines())  # the text once: in the lines, not again in data
# --- end MVP ---
