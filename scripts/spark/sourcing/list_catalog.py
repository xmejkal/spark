"""
`parts.py --catalog`: every record research has kept, chosen or not, as an Operation on the core (P726 PR 2). It was
`part_handlers._op_catalog`. A record that does not parse is listed BROKEN and is a problem. It writes nothing.
"""

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, Argument
from spark.records import records_codes, store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _problem
from spark.sourcing import datasheets
from spark.sourcing.part_facts import _row
from spark.sourcing.part_operation import PartOperation


# --- MVP ---
class ListCatalog(PartOperation):
    """Operation: `catalog` as parts.py answers it: one row per kept record, the broken ones named, a count, paged from
    `--from`."""

    name = "catalog"
    data_keys = ('records', 'broken')
    arguments = (Argument(("--catalog",), "catalog", bool, "every record research has kept, chosen or not"),
                 ANSWER_ARGUMENTS["start"], COMMON_ARGUMENTS[JSON_DEST])

    def build_answer(self, start, catalog=True):
        records, broken = datasheets.catalog_records()
        listing = [{"id": part_id, "kind": record["kind"], "name": record["name"]} for part_id, record in records.items()]
        shown, truncated = store.page_with_store(listing, start, "catalog", ["--catalog"])
        lines = [_row(r["id"], r["kind"], r["name"]) for r in listing]
        lines += [_row(name, "BROKEN", "does not parse, or names no schema/id/name/kind") for name in broken]
        lines.append("  %d record(s), %d broken" % (len(records), len(broken)))
        return Answer({"records": shown, "broken": broken}, lines, truncated=truncated,
                      problems=[_problem(name.split(" — ")[0], "a broken catalog record: %s" % name, code=records_codes.RECORD_FILE_BROKEN)
                                for name in broken])
# --- end MVP ---
