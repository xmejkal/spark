"""
`parts.py --keep-picture`: put a part's picture into the store and name it in the part's record (P946 #1349), all or
nothing: the picture is checked against the part's frame (`picture_check.PictureCheck`) and the record is written dry
before the file is kept, so a refusal keeps nothing. The record gets the file's `documents` entry and its
`pictures.<view>` block in one write; `verified` is copied from the frame's size fact, never typed.
"""

from pathlib import Path

from spark.breadboard import drawing, picture_makers
from spark.breadboard.picture_check import PictureCheck
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument
from spark.records import records_codes, store
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import LIKENESS, PICTURE_VIEWS, Answer, _cannot, _parse, _problem, picture_problems
from spark.sourcing import datasheets, record_home, sourcing_codes
from spark.sourcing.keep_file import document_listing
from spark.sourcing.part_operation import PartOperation


# --- MVP ---
class KeepPicture(PartOperation):
    """Operation: `keep-picture` as parts.py answers it: the picture's block and its documents key; a missing file or a
    store that refuses it is a could-not-run item; a part with no record of its own, spark's library, a record with no
    frame, and each rule the picture breaks are problems, and nothing is kept."""

    name = "keep-picture"
    data_keys = ("record", "key", "view", "picture", "document", "written")
    arguments = (Argument(("--keep-picture",), "file", str, "keep a picture of a part (an SVG in its frame, see --picture-frame) "
                          "and name it in the part's record as its picture for a view", metavar="FILE"),
                 Argument(("--part",), "part_id", str, "with --keep-picture: the part record the picture is of (--project picks "
                          "the project's record; never spark's library)", required=True, metavar="PART"),
                 Argument(("--made-by",), "made_by", str, "with --keep-picture: who or what made it, one word: photo, drawing, "
                          "an AI's name", required=True, metavar="WORD"),
                 Argument(("--likeness",), "likeness", str, "with --keep-picture: how near it is to the real part",
                          required=True, choices=LIKENESS),
                 Argument(("--credit",), "credit", str, "with --keep-picture: one line that says who made it and from what",
                          required=True, metavar="LINE"),
                 Argument(("--view",), "view", str, "with --keep-picture: the view it shows", PICTURE_VIEWS[0], choices=PICTURE_VIEWS),
                 Argument(("--url",), "url", str, "with --keep-picture: where the file came from, if anyone knows"),
                 ANSWER_ARGUMENTS["project"], ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, file, part_id, project, dry_run, **given):
        path = Path(file)
        if not path.is_file():
            return Answer(unchecked=[_cannot("--keep-picture: no file at %s" % path, code=records_codes.FILE_REFUSED)])
        home, _ = record_home.record_path(part_id, project)
        record = _parse(home) if home is not None else None
        if not isinstance(record, dict):
            return Answer(problems=[_problem(part_id, "no record of a part called %r — `parts.py --need` finds what exists" % part_id,
                                             code=sourcing_codes.NO_SUCH_PART)])
        shape, why = _frame(record)
        if shape is None:
            return Answer(problems=[_problem(part_id, "%s has no frame to draw on: %s" % (part_id, why), code=drawing.NO_HEADER_FACT)])
        refused = PictureCheck(shape).problems(path.read_bytes())
        if refused:
            return Answer(problems=[_problem(problem.element, problem.sentence, code=problem.code) for problem in refused])
        block = {"made_by": given["made_by"], "likeness": given["likeness"], "credit": given["credit"],
                 "verified": _size_verified(record)}
        return self._keep(path, record, (part_id, project, given["view"], given["url"], dry_run), block)

    @staticmethod
    def _keep(path, record, where, block):
        """The record written dry, then the file kept, then the record written: all or nothing."""
        part_id, project, view, url, dry_run = where
        try:
            key, _, _, documents = document_listing(record, datasheets.keep_local(path, url, dry_run=True))
            values = {"documents": documents, "pictures": {view: dict(block, document=key)}}
            answer = record_home.set_fields(part_id, project, values, True, _refusal)
            if answer.problems or dry_run:
                return _said(answer, dict(values, key=key, view=view, record=part_id), documents[key], False)
            entry = datasheets.keep_local(path, url, dry_run=False)
            answer = record_home.set_fields(part_id, project, values, False, _refusal)
        except store.StoreError as refused:
            return Answer(unchecked=[_cannot(str(refused), code=refused.code)])
        return _said(answer, dict(values, key=key, view=view, record=part_id), entry, True)


def _said(answer, kept, entry, written):
    """The Answer of the write: its problems, or the picture's block and its documents entry."""
    if answer.problems:
        return Answer(problems=answer.problems)
    return Answer({"record": kept["record"], "key": kept["key"], "view": kept["view"], "picture": kept["pictures"][kept["view"]],
                   "document": entry, "written": written}, answer.lines)


def _refusal(record, after, path):
    """`set_fields`' refusal: a `documents` or a `pictures` held that is no object is repaired by hand first, and the
    picture's block must hold (`record_kind.picture_problems`)."""
    held = [field for field in ("documents", "pictures") if record.get(field) is not None and not isinstance(record.get(field), dict)]
    return ["%s: %s is not an object — repair the file by hand first" % (path.stem, field) for field in held] or picture_problems(after)


def _frame(record):
    """(the record's frame, None) or (None, why it has none: the field it lacks)."""
    try:
        shape = picture_makers.shape_of(record)
    except drawing.NotDrawnError as missing:
        return None, "it lacks %s" % missing.subject
    return (shape, None) if shape is not None else (None, "it has no physical block (physical)")


def _size_verified(record):
    """True only when the size the picture is drawn to is verified: a module's body_mm, a board's outline (never yet)."""
    body = record.get("body_mm")
    return isinstance(body, dict) and body.get("verified") is True
# --- end MVP ---
