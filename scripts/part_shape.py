"""
The shape of a part (P412, epic P446): where its pins sit and how big it is, in millimetres, read from a record, and the
same shape projected to the pixels the drawn breadboard plans with.

    find_part_px(board)  ->  (part_px, the name of the source that placed it); find_source gives the source itself

The frame, written down once: the board seen from above, component side up, USB-C at the bottom, the origin at the
top-left corner of the PCB, y down, in mm. The outline is the PCB only, not the USB-C overhang. `emit_footprint.pads`
counts from the centre with y up, so `RecordShapeSource` flips it: x + W/2, H/2 - y.

A shape holds facts only. Each group of facts carries the provenance of `provenance.fact_problems`: a value, whether it
is verified, its source, and why it matters when it is not. Wokwi's files are "the board's Wokwi definition" and a stand-in
there never shows a board it is not.
"""

import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import breadboard_drawing  # noqa: E402
import emit_footprint  # noqa: E402
from breadboard_drawing import NotDrawn  # noqa: E402

#: Pixels per millimetre: Wokwi draws 96 px to the inch.
PX_PER_MM = 96 / 25.4
#: The word that names a part_px drawn from a record (`part_px["source"]`), as the drawing reads it.
RECORD = breadboard_drawing.RECORD_SOURCE

#: Value: a part in mm: its outline `size` (width, height), its `pins` {label: (x, y)}, the pad `ground` stands for, and
#: its fact `groups` {name: {value, verified, source, why_it_matters, note}}.
PartShape = collections.namedtuple("PartShape", "size pins ground groups")


def _px(mm):
    return round(mm * PX_PER_MM, 3)


def project_to_px(shape):
    """The `part_px` of a shape: the dict the planner and the renderers read. It scales to px, derives the `center` the
    turn goes about and says the body covers the holes under it. `notes` holds the sentence and the why of each group
    that is not verified, in the order the shape lists them."""
    width, height = shape.size
    notes = [{"group": name, "sentence": group["note"], "why": group["why_it_matters"]}
             for name, group in shape.groups.items() if group["verified"] is False]
    return {"size": [_px(width), _px(height)], "center": [_px(width / 2), _px(height / 2)], "covers_holes": True,
            "pins": {label: [_px(x), _px(y)] for label, (x, y) in shape.pins.items()},
            "doubtful": list(shape.groups.get("doubtful_pads", {}).get("value") or []), "ground": shape.ground,
            "source": RECORD, "notes": notes}


class ShapeSource:
    """Strategy: where one board's part_px comes from."""

    #: What `find_part_px` answers with beside the part_px.
    NAME = ""

    def place_part(self, board):
        """The part_px of this board, or None when this source declines it (the next source is asked)."""
        raise NotImplementedError

    def pin_names(self, board):
        """{pin as the steps print it: pin of the part}, for the pins that part_px holds."""
        raise NotImplementedError


class WokwiGeometryShapeSource(ShapeSource):
    """Strategy: a board with a measured entry in data/wokwi-geometry.json that is not a stand-in. The measured px dict
    is returned as it is, so a board drawn from it keeps its bytes."""

    NAME = "wokwi"
    #: The board record's `wokwi_pin_naming` when its Wokwi pins carry the printed labels, so a drawing can find them.
    PIN_NAMING_SILKSCREEN = "silkscreen"

    def __init__(self, parts=None):
        self._parts = parts

    def _measured(self, board):
        parts = self._parts
        if parts is None:
            parts = json.loads(Path(breadboard_drawing.WOKWI_GEOMETRY_FILE).read_text())["parts"]
        found = parts.get(board.get("wokwi_part_type")) if board.get("wokwi_part_type") else None
        return found if isinstance(found, dict) else None

    def place_part(self, board):
        return None if board.get("wokwi_is_stand_in") else self._measured(board)

    def pin_names(self, board):
        measured = self._measured(board)
        if measured is None or board.get("wokwi_pin_naming") != self.PIN_NAMING_SILKSCREEN:
            return {}
        return {pin: pin for pin in measured["pins"]}


class RecordShapeSource(ShapeSource):
    """Strategy: a board whose own record holds what its pads and outline need. It never declines: a record that lacks a
    fact or disagrees with itself is refused with a code, so a board is never drawn wrong."""

    NAME = RECORD

    def find_shape(self, board):
        """The PartShape of this board's record, or NotDrawn with a code and a subject."""
        gaps = emit_footprint.geometry_gaps(board)
        if gaps:
            raise NotDrawn("the board file lacks %s" % ", ".join(gaps), breadboard_drawing.NO_HEADER_FACT, gaps[0].split(" ")[0])
        physical = board["physical"]
        wrong = emit_footprint.wrong_kind(physical)
        if wrong:
            raise NotDrawn(emit_footprint.DISAGREES_MESSAGE % wrong, breadboard_drawing.HEADER_DISAGREES)
        try:
            placed = emit_footprint.pads(board)
        except (ValueError, KeyError, TypeError) as exc:
            raise NotDrawn(emit_footprint.DISAGREES_MESSAGE % exc, breadboard_drawing.HEADER_DISAGREES) from exc
        width, height = physical["width_mm"], physical["height_mm"]
        pins = {}
        for label, x, y in placed:
            if label in pins:
                raise NotDrawn("two pads of the board file are called %s" % label, breadboard_drawing.DUPLICATE_PAD_LABEL, label)
            pins[label] = (round(x + width / 2, 4), round(height / 2 - y, 4))
        doubtful = physical["header"].get("doubtful_pads")
        if not isinstance(doubtful, list):
            raise NotDrawn("the board file does not say which pads are doubtful: physical.header.doubtful_pads",
                           breadboard_drawing.NO_DOUBTFUL_PAD_FACT)
        grounds = [name for name, pad in (board.get("power_pads") or {}).items()
                   if isinstance(pad, dict) and pad.get("rail") == "ground" and name not in doubtful]
        if len(grounds) != 1 or grounds[0] not in pins:
            raise NotDrawn("the board's ground pads, less the doubtful ones, are not exactly one: %s" % (", ".join(grounds) or "none"),
                           breadboard_drawing.GROUND_NOT_ONE, ", ".join(grounds) or None)
        return PartShape((width, height), pins, grounds[0], self._groups(len(pins), doubtful))

    @staticmethod
    def _groups(pad_count, doubtful):
        """The fact groups, each with its provenance: the pads are the record's own, the row side is the footprint code's
        convention, and a doubtful pad is the record's own doubt."""
        groups = {
            "pads": {"value": pad_count, "verified": True, "source": "the board file's physical header and header_order"},
            "row_side": {"value": "row 0 on the left, USB-C down", "verified": False,
                         "source": "emit_footprint.pads, which puts row 0 at -x",
                         "why_it_matters": "a mirrored board shows on the bench: the pins sit on the other side",
                         "note": "row side not verified"}}
        if doubtful:
            groups["doubtful_pads"] = {
                "value": list(doubtful), "verified": False, "source": "the board file's physical.header.doubtful_pads",
                "why_it_matters": "a jumper to a pad silkscreened NC does nothing",
                "note": "%s doubtful" % (" and ".join(doubtful) if len(doubtful) < 3 else
                                         "%s and %s" % (", ".join(doubtful[:-1]), doubtful[-1]))}
        return groups

    def place_part(self, board):
        return project_to_px(self.find_shape(board))

    def pin_names(self, board):
        shape = self.find_shape(board)
        return dict({label: label for label in shape.pins}, GND=shape.ground)


def sources_for(parts=None):
    """The sources in the order they are asked: Wokwi's measured board first (from `parts`, else from the file), so a
    board with a complete record that Wokwi also draws right keeps its measured numbers, and a stand-in is never drawn."""
    return (WokwiGeometryShapeSource(parts), RecordShapeSource())


SHAPE_SOURCES = sources_for()


def find_source(board, sources=SHAPE_SOURCES):
    """(the first source that places this board, its part_px), or NotDrawn when none does."""
    for source in sources:
        part_px = source.place_part(board)
        if part_px is not None:
            return source, part_px
    raise NotDrawn("nothing says how to draw the board %s" % board.get("id"))


def find_part_px(board, sources=SHAPE_SOURCES):
    """(part_px, the name of the source that placed it) of this board."""
    source, part_px = find_source(board, sources)
    return part_px, source.NAME
