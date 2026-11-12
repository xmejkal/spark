"""
`parts.py --keep`: put a file you already have into your store, as an Operation on the core (P726 PR 2). It was
`part_handlers._op_keep`. A JPEG loses its location (EXIF GPS) before it is kept (P75), and the line that says so is said
before a store's refusal (P423). The dry run answers the entry and keeps nothing.
"""

import json
from pathlib import Path

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.core.text_guards import printable
from spark.records import records_codes, store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _cannot
from spark.sourcing import datasheets
from spark.sourcing.part_operation import PartOperation

# --- MVP ---
#: The help of `--url`, worded as parts.py's OPTIONS row (parts.py reads it here).
URL_HELP = "with --keep: where the file came from, if anyone knows"


class KeepFile(PartOperation):
    """Operation: `keep` as parts.py answers it: the documents entry of the kept copy, as JSON in the text too; a missing
    file, a name the store refuses and a store that cannot be written are could-not-run items, each with its code."""

    name = "keep"
    data_keys = ('document', 'location_removed', 'written')
    arguments = (Argument(("--keep",), "file", str, "put a file you already have into your store; answers its documents entry", metavar="FILE"),
                 Argument(("--url",), "url", str, URL_HELP),
                 ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, file, url, dry_run):
        path = Path(file)
        if not path.is_file():
            return Answer(unchecked=[_cannot("--keep: no file at %s" % path, code=records_codes.FILE_REFUSED)])
        located = path.name.lower().endswith((".jpg", ".jpeg")) and datasheets.without_location(path.read_bytes())[1]
        said = (["  removed the location (EXIF GPS) from %s before keeping it" % printable(path.name)]
                if located else ())
        try:  # P423: a store that refuses the file, or cannot be written, refuses it after the line was said
            entry = datasheets.keep_local(path, url, dry_run=dry_run)
        except store.StoreError as refused:
            return Answer(unchecked=[_cannot(str(refused), code=refused.code)], diagnostics=said)
        except OSError as unwritable:
            return Answer(unchecked=[_cannot("--keep: %s" % unwritable, code=records_codes.FILE_REFUSED)], diagnostics=said)
        return Answer({"document": entry, "location_removed": located, "written": not dry_run},
                      [json.dumps(entry, indent=2, ensure_ascii=False)], diagnostics=said)
# --- end MVP ---
