"""
`parts.py --drawer`: what you own, as an Operation on the core (P726 PR 2). It was `part_handlers._op_drawer`. One line per
entry: label, count, the record it is, unsure, skip, who holds it; 20 at a time. It writes nothing.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.core.text_guards import printable
from spark.records import store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer
from spark.sourcing.drawer import listing as drawer_listing  # the Operation's own dest is `drawer`
from spark.sourcing.part_operation import PartOperation


# --- MVP ---
class ListDrawer(PartOperation):
    """Operation: `drawer` as parts.py answers it: the entries, a count, paged from `--from`."""

    name = "drawer"
    arguments = (Argument(("--drawer",), "drawer", bool, "what you own: label, count, the record it is, unsure, skip — 20 at a time"),
                 ANSWER_ARGUMENTS["start"], COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, start, drawer=True):
        entries = drawer_listing()
        shown, truncated = store.page_with_store(entries, start, "drawer", ["--drawer"])
        lines = ["  %-44s %6s  %-38s %s" % (str(e["label"])[:44], "?" if e["count"] is None else e["count"],
                                             "%s %s" % next(iter(e["is"].items())) if e["is"] else "—",
                                             "  ".join(filter(None, ["maybe owned — check the drawer" if e["unsure"] else ("skip: %s" % e["skip"] if e["skip"] else ""),
                                                                   "held by " + ", ".join(map(printable, e["held_by"])) if e["held_by"] else ""])))
                 for e in entries]
        lines.append("  %d entr%s" % (len(entries), "y" if len(entries) == 1 else "ies"))
        return Answer({"entries": shown}, lines, truncated=truncated)
# --- end MVP ---
