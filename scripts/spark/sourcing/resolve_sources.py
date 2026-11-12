"""
`parts.py --sources`: ask every URL a record cites whether it answers, as an Operation on the core (P726 PR 2). It was
`part_handlers._op_sources`. The dry run lists the URLs and reaches nothing. It writes nothing; it reaches the network itself
(`datasheets.sources_resolve`), as the handler did, so it declares `fetches` and never calls `outside.fetch`.
"""

from spark.core.operation import COMMON_ARGUMENTS, FETCHES, JSON_DEST, READS, Argument
from spark.records import records_codes
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _problem
from spark.sourcing import datasheets
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.part_records import any_record


# --- MVP ---
class ResolveSources(PartOperation):
    """Operation: `sources` as parts.py answers it: ok or NO per URL, a URL that does not answer a problem on it; a record
    with no URL says so; a part nobody has is a problem on its id."""

    name = "sources"
    data_keys = ('part', 'sources')
    arguments = (Argument(("--sources",), "part_id", str, "ask every URL a record cites whether it answers", metavar="PART"),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, FETCHES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, part_id, project, dry_run):
        record = any_record(part_id, project)
        if dry_run:
            urls = datasheets.cited_urls(record)
            return Answer({"part": part_id, "sources": [{"url": url, "reachable": None} for url in urls]},
                          ["  would ask %s" % url for url in urls])
        answers = datasheets.sources_resolve(record)
        lines = ["  %s  %s" % ("ok  " if ok else "NO  ", url) for url, ok in answers] or \
            ["  %s cites no URL — every fact rests on prose sources a person has to find" % part_id]
        return Answer({"part": part_id, "sources": [{"url": url, "reachable": ok} for url, ok in answers]}, lines,
                      problems=[_problem(url, "does not answer", code=records_codes.URL_UNREACHABLE) for url, ok in answers if not ok])
# --- end MVP ---
