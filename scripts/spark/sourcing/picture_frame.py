"""
`parts.py --picture-frame`: the frame a part's picture is drawn on (P946 #1349), as an SVG in mm from the part's or the
board's record: its outline, and in a `data-guide` group a ring and the printed label at each pad. A person or an AI
draws the picture on it, leaves the guide out and keeps the result with `--keep-picture`. The text is the SVG alone, so
`> frame.svg` writes the file. It writes nothing.
"""

import json

from spark.breadboard import drawing, picture_makers
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, Argument
from spark.records import board_records
from spark.records.answer_operation import ANSWER_ARGUMENTS
from spark.records.record_kind import Answer, _problem
from spark.sourcing import sourcing_codes
from spark.sourcing.part_operation import PartOperation
from spark.sourcing.part_records import PartError, any_record


# --- MVP ---
class DrawPictureFrame(PartOperation):
    """Operation: `picture-frame` as parts.py answers it: the frame's SVG, its viewBox, and the maker and likeness it
    would carry; a record with no frame is a problem on its id that names the field it lacks."""

    name = "picture-frame"
    data_keys = ("svg", "view_box", "made_by", "likeness")
    arguments = (Argument(("--picture-frame",), "part_id", str, "the frame a part's picture is drawn on: an SVG in mm of its "
                          "outline and its pads, from its record or its board's", metavar="PART"),
                 ANSWER_ARGUMENTS["project"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS,)

    def build_answer(self, part_id, project):
        record = _record(part_id, project)
        try:
            shape = picture_makers.shape_of(record)
        except drawing.NotDrawnError as missing:
            return Answer(problems=[_problem(part_id, "%s has no frame: it lacks %s" % (part_id, missing.subject), code=missing.code)])
        if shape is None:
            return Answer(problems=[_problem(part_id, "%s has no frame: it has no physical block (physical)" % part_id,
                                             code=drawing.NO_DRAWING_FACT)])
        svg = picture_makers.FramePictureMaker.svg(shape)
        return Answer({"svg": svg, "view_box": [0, 0] + list(shape.size), "made_by": picture_makers.FramePictureMaker.NAME,
                       "likeness": "rough"}, [svg.rstrip("\n")])


def _record(part_id, project):
    """A part's record wherever it lives, else a board's, else the PartError of a part nobody has."""
    try:
        return any_record(part_id, project)
    except PartError as missing:
        found = board_records.records(project).get(part_id)
        if found is None or missing.code != sourcing_codes.NO_SUCH_PART:
            raise
        return json.loads(found[1].read_text(encoding="utf-8"))
# --- end MVP ---
