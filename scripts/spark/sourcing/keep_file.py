"""
`parts.py --keep`: put a file you already have into your store, as an Operation on the core (P726 PR 2). It was
`part_handlers._op_keep`. A JPEG loses its location (EXIF GPS) before it is kept (P75), and the line that says so is said
before a store's refusal (P423). The dry run answers the entry and keeps nothing. With `--part` (P784) the entry is listed
in that part record's `documents` too, through `record_home.set_fields`, so `--kept` finds the file by its URL and its
record: the record is checked before the file is kept, so a refusal keeps nothing (all or nothing, §6.4).
"""

import json
from pathlib import Path

from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.core.text_guards import printable
from spark.records import records_codes, store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _cannot, _parse, _problem
from spark.sourcing import datasheets, record_home
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.part_records import PartError

# --- MVP ---
#: The help of `--url`, worded as parts.py's OPTIONS row (parts.py reads it here).
URL_HELP = "with --keep: where the file came from, if anyone knows"
#: The help of `--part` (P784), worded as parts.py's OPTIONS row.
PART_HELP = ("with --keep: the part record this file is a document of; its documents entry is added there (--project picks the "
             "project's record; never spark's library), once per file's bytes: the same bytes listed already are not listed again")
#: The line of a file kept without `--part`: no record lists it, so `--kept` finds it by its name alone (P784).
NOT_LISTED = "  %s, but listed in no record: add --part <id> --project . to list it (a drawer photo needs none)"


class KeepFile(PartOperation):
    """Operation: `keep` as parts.py answers it: the documents entry of the kept copy, as JSON in the text too, and with
    `--part` the record and key it is listed under (the lines that say so are on stderr, so the text stays the entry's
    JSON); a missing file, a name the store refuses and a store that cannot be written are could-not-run items, each with
    its code; a part with no record, a record in spark's library or a `documents` that is no object is a problem on the
    part's id, and nothing is kept."""

    name = "keep"
    data_keys = ('document', 'location_removed', 'written', 'record', 'key')
    arguments = (Argument(("--keep",), "file", str, "put a file you already have into your store; answers its documents entry, "
                          "and with --part lists it in that record", metavar="FILE"),
                 Argument(("--url",), "url", str, URL_HELP),
                 Argument(("--part",), "part_id", str, PART_HELP, metavar="PART"),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, file, url, part_id, project, dry_run):
        path = Path(file)
        if not path.is_file():
            return Answer(unchecked=[_cannot("--keep: no file at %s" % path, code=records_codes.FILE_REFUSED)])
        located = path.name.lower().endswith((".jpg", ".jpeg")) and datasheets.without_location(path.read_bytes())[1]
        said = (["  removed the location (EXIF GPS) from %s before keeping it" % printable(path.name)]
                if located else ())
        listed = None
        try:  # P423: a store that refuses the file, or cannot be written, refuses it after the line was said
            if part_id:  # P784: the record first, from the dry keep's entry, so a refusal keeps nothing
                listed = list_document(part_id, project, datasheets.keep_local(path, url, dry_run=True), dry_run=True)
                if listed[0].problems:
                    return Answer(problems=listed[0].problems, diagnostics=said)
            entry = datasheets.keep_local(path, url, dry_run=dry_run)
        except store.StoreError as refused:
            return Answer(unchecked=[_cannot(str(refused), code=refused.code)], diagnostics=said)
        except OSError as unwritable:
            return Answer(unchecked=[_cannot("--keep: %s" % unwritable, code=records_codes.FILE_REFUSED)], diagnostics=said)
        if part_id and not dry_run:  # the written entry is the real keep's
            listed = list_document(part_id, project, entry, dry_run=False)
            if listed[0].problems:  # a record changed between the check and the write: the file is kept, and said so
                return Answer(problems=listed[0].problems, diagnostics=list(said) + [NOT_LISTED % "kept"])
        return Answer({"document": entry, "location_removed": located, "written": not dry_run,
                       "record": part_id if listed else None, "key": listed[1] if listed else None},
                      [json.dumps(entry, indent=2, ensure_ascii=False)],
                      diagnostics=list(said) + listed_lines(part_id, listed, dry_run))


def list_document(part_id, project, entry, dry_run):
    """
    (Answer, key, held): `entry` listed in the `documents` of `part_id`'s own record (P784), through `record_home.set_fields`,
    so a shelf copy's write goes to its project's record and spark's library is refused. `documents` is replaced whole, so
    what it holds is read from the file `set_fields` writes (`record_path`). The same bytes listed already (by sha256) are
    not listed again: `held` is that entry and `key` its key; else `held` is None and `key` a fresh one. A part with no
    record is a problem on its id, as the other refusals are.
    """
    path, _ = record_home.record_path(part_id, project)
    record = _parse(path) if path is not None else None
    documents = record.get("documents") if isinstance(record, dict) else None
    documents = documents if isinstance(documents, dict) else {}
    key, held = next(((name, one) for name, one in documents.items() if isinstance(one, dict) and one.get("sha256") == entry["sha256"]),
                     (datasheets.document_key(entry["file"], documents), None))
    try:
        answer = record_home.set_fields(part_id, project, {"documents": documents if held else dict(documents, **{key: entry})},
                                        dry_run, _documents_problems)
    except PartError as missing:
        return Answer(problems=[_problem(part_id, str(missing), code=missing.code)]), key, held
    return answer, key, held


def _documents_problems(record, after, path):
    """`set_fields`' refusal of a `documents` write: a `documents` that is there and no object is repaired by hand first."""
    held = record.get("documents")
    return [] if held is None or isinstance(held, dict) else ["%s: documents is not an object — repair the file by hand first" % path.stem]


def listed_lines(part_id, listed, dry_run):
    """The lines that say where a kept file is listed (P784): the key to cite it by, the entry that already lists the same
    bytes, or that no record lists it; and the shelf copy's sentence when there is one to say."""
    if listed is None:
        return [NOT_LISTED % ("would be kept" if dry_run else "kept")]
    answer, key, held = listed
    lines = (["  already listed in %s as %s (%s, from %s)" % (part_id, key, printable(str(held.get("file"))), printable(str(held.get("url") or "no URL")))]
             if held else ['  %s %s as %s: cite it as {"document": "%s", "at": "p<N>"}' % ("would list it in" if dry_run else "listed in", part_id, key, key)])
    shelf_copy = (answer.data or {}).get("shelf_copy")
    return lines + (["  " + shelf_copy] if shelf_copy not in (None, "current") else [])
# --- end MVP ---
