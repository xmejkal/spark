"""
`parts.py --fetch`: download the datasheets and images a record cites, into your store, as an Operation on the core (P726
PR 2). It was `part_handlers._op_fetch`. The dry run lists what it would fetch and reaches nothing. It reaches the network
itself (`datasheets.fetch_documents`), as the handler did, so it declares `fetches` and never calls `outside.fetch`.
"""

import json

from spark.core.operation import COMMON_ARGUMENTS, FETCHES, JSON_DEST, READS, WRITES, Argument
from spark.records import records_codes
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, DEFINITION_SUFFIX, _problem, record_home
from spark.sourcing import datasheets, sourcing_codes
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.part_records import PartError


# --- MVP ---
#: The sentence of a cited document whose download failed (P722): nothing was kept for it, and the run is problems.
DOWNLOAD_FAILED = "the download failed, so nothing was kept for it"


class FetchDocuments(PartOperation):
    """Operation: `fetch` as parts.py answers it: each kept document with its digest and URL, or what a dry run would
    fetch; a cited URL that did not answer is a problem on it with `url_unreachable` (P722); a URL already in `documents`
    is not fetched again and counts as kept; a record that cites no URL says so; a part nobody has is a problem on its id."""

    name = "fetch"
    data_keys = ('documents', 'would_fetch', 'failed')
    arguments = (Argument(("--fetch",), "part_id", str, "download the datasheets and images a record cites, into your store", metavar="PART"),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES, FETCHES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, part_id, project, dry_run):
        if dry_run:
            home = record_home(part_id, project)
            if home is None:
                raise PartError("no record called %r to fetch for", part_id, code=sourcing_codes.NO_SUCH_PART)
            wanted = [url for url, _ in datasheets.fetch_plan(json.loads((home / (part_id + DEFINITION_SUFFIX)).read_text()))]
            return Answer({"documents": None, "would_fetch": wanted, "failed": []}, ["  would fetch %s" % url for url in wanted]
                          or ["  %s cites no datasheet or image URL to keep" % part_id])
        kept = datasheets.fetch_documents(part_id, project)
        cited = [url for url, _ in datasheets.fetch_plan(json.loads((record_home(part_id, project) / (part_id + DEFINITION_SUFFIX)).read_text()))]
        failed = [url for url in cited if url not in {entry["url"] for entry in kept.values()}]
        lines = ["  %s/%s  <-  %s" % (entry["sha256"][:12], entry["file"], entry["url"]) for entry in kept.values()]
        lines += ["  NO  %s — %s" % (url, DOWNLOAD_FAILED) for url in failed]
        return Answer({"documents": kept, "would_fetch": [], "failed": failed}, lines or ["  %s cites no datasheet or image URL to keep" % part_id],
                      problems=[_problem(url, DOWNLOAD_FAILED, code=records_codes.URL_UNREACHABLE) for url in failed])
# --- end MVP ---
