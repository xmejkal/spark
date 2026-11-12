"""
`parts.py --list`: every record a project can build with, and where it comes from, as an Operation on the core (P726 PR 2).
It was `part_handlers._op_list`. It writes nothing.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records import record_kind, store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _with_project
from spark.sourcing.part_facts import _row
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.part_records import load


# --- MVP ---
class ListParts(PartOperation):
    """Operation: `list` as parts.py answers it: one row per record (id, kind, layer, name), paged from `--from`; a record
    off the contract is a problem on it (`load`)."""

    name = "list"
    data_keys = ('parts',)
    arguments = (Argument(("--list",), "list", bool, "every record a project can build with, and where it comes from"),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["start"], COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, project, start, list=True):
        listing = []
        for part_id, (layer, path) in store.records("parts", record_kind.LIBRARY, project).items():
            record = load(part_id, project)
            listing.append({"id": part_id, "kind": record["kind"], "name": record["name"], "layer": layer, "from": str(path.parent)})
        shown, truncated = store.page_with_store(listing, start, "list", ["--list"] + _with_project(project))
        lines = [_row(p["id"], p["kind"], "%-9s %s" % (p["layer"], p["name"])) for p in listing]
        return Answer({"parts": shown}, lines, truncated=truncated)
# --- end MVP ---
