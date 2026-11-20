"""
The shape of a part (P412, epic P446): where its pins sit and how big it is, in millimetres, read from a record, and the
same shape projected to the pixels the drawn breadboard plans with.

    find_part_px(board)  ->  (part_px, the name of the source that placed it); find_source gives the source itself

The frame, written down once: the board seen from above, component side up, USB-C at the bottom, the origin at the
top-left corner of the PCB, y down, in mm. The outline is the PCB only, not the USB-C overhang. `footprint_emitter.pads`
counts from the centre with y up, so `RecordShapeSource` flips it: x + W/2, H/2 - y.

A shape holds facts only. Each group of facts carries the provenance of `provenance.fact_problems`: a value, whether it
is verified, its source, and why it matters when it is not. Wokwi's files are "the board's Wokwi definition" and a stand-in
there never shows a board it is not.
"""

import collections
import json
import math
from pathlib import Path

from spark.breadboard import drawing, svg_diagram
from spark.breadboard.drawing import NotDrawnError
from spark.design import footprint_emitter

#: Pixels per millimetre: Wokwi draws 96 px to the inch.
PX_PER_MM = 96 / 25.4
#: The name of the source that draws a board from its own record, and the word `part_px["source"]` carries for it.
RECORD = "record"
#: The one edge `footprint_emitter.pads` knows to be flush: its pads count from the +y end.
FLUSH_EDGE = "+y"

#: Value: a part in mm: its outline `size` (width, height), its `pins` {label: (x, y)}, the pad `ground` stands for, and
#: its fact `groups` {name: {value, verified, source, why_it_matters, note, words}}: `words` names the group in the
#: picture's note line of its part (P953).
PartShape = collections.namedtuple("PartShape", "size pins ground groups")


def _px(mm):
    return round(mm * PX_PER_MM, 3)


def project_to_px(shape, usb_mark=True, labels=svg_diagram.LABELS_BESIDE, full_surface=True):
    """The `part_px` of a shape: the dict the planner and the renderers read. It scales to px and derives the `center` the
    turn goes about. `covers_holes` is a drawing convention, not a measured fact: the body of a board hides the holes under
    it. `notes` holds the sentence, the words that the picture's note says it by (P953) and the why of each group that is
    not verified, in the order the shape lists them. The
    flags say what this source can do, so no caller compares a source's name: `wokwi_part` (Wokwi has a part with these
    pins), `pad_labels` (the picture names each pad), `full_surface` (the board is drawn on the 63-column breadboard),
    `usb_mark` (the picture marks a USB end: a board's) and `labels` (where a pad's label goes, a key of
    `drawing.PAD_LABEL_LAYOUTS`)."""
    width, height = shape.size
    notes = [{"group": name, "sentence": group["note"], "words": group["words"], "why": group["why_it_matters"]}
             for name, group in shape.groups.items() if group["verified"] is False]
    return {"size": [_px(width), _px(height)], "center": [_px(width / 2), _px(height / 2)], "covers_holes": True,
            "pins": {label: [_px(x), _px(y)] for label, (x, y) in shape.pins.items()},
            "doubtful": list(shape.groups.get("doubtful_pads", {}).get("value") or []), "ground": shape.ground,
            "source": RECORD, "notes": notes, "wokwi_part": False, "pad_labels": True, "full_surface": full_surface,
            "usb_mark": usb_mark, "labels": labels}


class ShapeSource:
    """Strategy: where one board's part_px comes from."""

    #: What `find_part_px` answers with beside the part_px.
    NAME = ""

    def describe_part(self, board):
        """The part_px of this board, or None when this source declines it (the next source is asked)."""
        raise NotImplementedError

    def find_pin_names(self, board):
        """{pin as the steps print it: pin of the part}, for the pins that part_px holds."""
        raise NotImplementedError


class WokwiGeometryShapeSource(ShapeSource):
    """Strategy: a board with a measured entry in data/wokwi-geometry.json that is not a stand-in. The measured px dict
    is returned as it is, so a board drawn from it keeps its bytes and has no flags (a missing flag is the Wokwi default)."""

    NAME = "wokwi"
    #: The board record's `wokwi_pin_naming` when its Wokwi pins carry the printed labels, so a drawing can find them.
    PIN_NAMING_SILKSCREEN = "silkscreen"

    def __init__(self, parts=None):
        self._parts = parts

    def _measured(self, board):
        parts = self._parts
        if parts is None:
            parts = json.loads(Path(drawing.WOKWI_GEOMETRY_FILE).read_text())["parts"]
        found = parts.get(board.get("wokwi_part_type")) if board.get("wokwi_part_type") else None
        return found if isinstance(found, dict) else None

    def describe_part(self, board):
        return None if board.get("wokwi_is_stand_in") else self._measured(board)

    def find_pin_names(self, board):
        measured = self._measured(board)
        if measured is None or board.get("wokwi_pin_naming") != self.PIN_NAMING_SILKSCREEN:
            return {}
        return {pin: pin for pin in measured["pins"]}


class RecordShapeSource(ShapeSource):
    """Strategy: a board whose own record holds what its pads and outline need. It never declines: a record that lacks a
    fact or disagrees with itself is refused with a code and the field, so a board is never drawn wrong."""

    NAME = RECORD

    @staticmethod
    def _disagrees(field, said):
        return NotDrawnError(footprint_emitter.DISAGREES_MESSAGE % said, drawing.HEADER_DISAGREES, field)

    def _refuse_odd_header(self, physical):
        """What `footprint_emitter.pads` would place wrongly or place twice: more than two rows, a row count that disagrees with
        the pin counts, a pitch of nothing, an edge it does not handle."""
        header = physical["header"]
        sizes = (("physical.width_mm", physical["width_mm"]), ("physical.height_mm", physical["height_mm"]),
                 ("physical.header.pitch_mm", header["pitch_mm"]), ("physical.header.row_spacing_mm", header["row_spacing_mm"]),
                 ("physical.header.first_pad_from_edge_mm", header["first_pad_from_edge_mm"]))
        for field, value in sizes:  # a size is a finite number above nothing: a negative one mirrors the board
            if not math.isfinite(value) or value <= 0:
                raise self._disagrees(field, "%s is not a finite number above 0" % field)
        rows = header["rows"]
        for field, ok in (("rows", type(rows) is int and rows == len(header["pins"])), ("pins", len(header["pins"]) <= 2),
                          ("flush_edge", header.get("flush_edge") == FLUSH_EDGE)):
            if not ok:
                raise self._disagrees("physical.header.%s" % field, "physical.header.%s does not fit the rest of the header" % field)

    def _refuse_pads_outside(self, physical, placed):
        """A pad outside the outline: the field that puts it out. Across the board, the row spacing; along it, where the first
        pad starts, else the pitch."""
        width, height = physical["width_mm"], physical["height_mm"]
        for _, x, y in placed:
            top = height / 2 - y
            if not 0 <= x + width / 2 <= width:
                raise self._disagrees("physical.header.row_spacing_mm", "a pad lies outside the board across its width")
            if not 0 <= top <= height:
                first = physical["header"]["first_pad_from_edge_mm"]
                raise self._disagrees("physical.header.%s" % ("first_pad_from_edge_mm" if first > height else "pitch_mm"),
                                      "a pad lies outside the board along its length")

    def find_shape(self, board):
        """The PartShape of this board's record, or NotDrawnError with a code and a subject."""
        missing = footprint_emitter.geometry_missing(board)
        if missing:
            raise NotDrawnError("the board file lacks %s" % ", ".join(footprint_emitter.geometry_gaps(board)),
                           drawing.NO_HEADER_FACT, missing[0][0])
        physical = board["physical"]
        wrong = footprint_emitter.kind_problem(physical)
        if wrong:
            raise self._disagrees(*wrong)
        self._refuse_odd_header(physical)
        try:
            placed = footprint_emitter.pads(board)
        except (ValueError, KeyError, TypeError) as exc:
            raise self._disagrees("physical.header.pins" if isinstance(exc, ValueError) else "physical.header", exc) from exc
        self._refuse_pads_outside(physical, placed)
        width, height = physical["width_mm"], physical["height_mm"]
        pins = {}
        for label, x, y in placed:
            if label in pins:
                raise NotDrawnError("two pads of the board file are called %s" % label, drawing.DUPLICATE_PAD_LABEL, label)
            pins[label] = (round(x + width / 2, 4), round(height / 2 - y, 4))
        if len(set(pins.values())) != len(pins):
            along = len({x for _, x, _ in placed}) == len({pins[label][0] for label in pins})  # one row's pads meet: the pitch
            raise self._disagrees("physical.header.%s" % ("pitch_mm" if along else "row_spacing_mm"), "two pads sit at one place")
        doubtful = physical["header"].get("doubtful_pads")
        if not isinstance(doubtful, list):
            raise NotDrawnError("the board file does not say which pads are doubtful: physical.header.doubtful_pads "
                                "(write [] when none is doubtful, after checking)", drawing.NO_DOUBTFUL_PAD_FACT)
        # GND is the first ground pad of power_pads that is not doubtful: every ground pad the record names is one net (P955).
        grounds = [name for name, pad in (board.get("power_pads") or {}).items()
                   if isinstance(pad, dict) and pad.get("rail") == "ground" and name not in doubtful]
        if not grounds or any(name not in pins for name in grounds):
            raise NotDrawnError("no ground pad is left once the doubtful ones are out, or a ground pad is no pad of the header: %s"
                                % (", ".join(grounds) or "none"), drawing.GROUND_NOT_ONE, ", ".join(grounds) or None)
        return PartShape((width, height), pins, grounds[0], self._with_row_side(self._groups(len(pins), doubtful), physical))

    def _with_row_side(self, groups, physical):
        """`groups` with the row side the record states (`physical.header.row_side`, P946): verified when the record says
        so with a source; a stated side that is not the drawing's refuses the board. A record that states none, or states
        it in no object, keeps the convention, unverified."""
        row_side = physical["header"].get("row_side")
        if not isinstance(row_side, dict):
            return groups
        if row_side.get("value") != groups["row_side"]["value"]:
            raise self._disagrees("physical.header.row_side", "physical.header.row_side is not where the drawing puts "
                                                              "row 0 (%s)" % groups["row_side"]["value"])
        if row_side.get("verified") is True and isinstance(row_side.get("source"), str) and row_side["source"]:
            groups["row_side"] = dict(groups["row_side"], verified=True, source=row_side["source"])
        return groups

    @staticmethod
    def _groups(pad_count, doubtful):
        """The fact groups, each with its provenance. None is verified here: no fact of the record says a pad is where the
        drawing puts it (the FireBeetle's own record calls two pads unresolved), the row side and the USB end are the
        footprint code's convention, and a doubtful pad is the record's own doubt. `find_shape` takes the row side as
        verified when the record's `physical.header.row_side` says so, with its source (P946)."""
        groups = {
            "pads": {"value": pad_count, "verified": False, "source": "the board file's physical header and header_order",
                     "why_it_matters": "a pad label read wrong wires the wrong pin, and no fact of the record says the pads are checked",
                     "note": "pads not verified", "words": "pads"},
            "row_side": {"value": "row 0 on the left", "verified": False,
                         "source": "footprint_emitter.pads, which puts row 0 at -x",
                         "why_it_matters": "a mirrored board shows on the bench: the pins sit on the other side",
                         "note": "row side not verified", "words": "row side"},
            "usb_end": {"value": "at the end away from the first pads", "verified": False,
                        "source": "footprint_emitter.pads, which puts the first pads at the +y end",
                        "why_it_matters": "the pins may sit at the other end of the board",
                        "note": "USB end not verified", "words": "USB end"}}
        if doubtful:
            groups["doubtful_pads"] = {
                "value": list(doubtful), "verified": False, "source": "the board file's physical.header.doubtful_pads",
                "why_it_matters": "a jumper to a pad silkscreened NC does nothing",
                "note": "%s doubtful" % (" and ".join(doubtful) if len(doubtful) < 3 else
                                         "%s and %s" % (", ".join(doubtful[:-1]), doubtful[-1])),
                "words": "the pads in a dashed ring"}
        return groups

    def describe_part(self, board):
        return project_to_px(self.find_shape(board))

    def find_pin_names(self, board):
        """Every pad but the doubtful ones, and GND for the first ground pad of power_pads that is not doubtful. A step to a doubtful pad finds no pin and is refused."""
        shape = self.find_shape(board)
        doubtful = shape.groups.get("doubtful_pads", {}).get("value") or []
        return dict({label: label for label in shape.pins if label not in doubtful}, GND=shape.ground)


class OneRowHeaderPlacer:
    """
    Strategy: the pads of a module with one straight row of header pins along an edge, as a ModuleShapeSource places
    them. `place(header, size, labels)` gives [(label, x_mm, y_mm)] in the module's frame, which is the board's frame
    turned to a module: the module seen from above as it sits in the breadboard, the header's edge at the top, the
    origin at the top-left corner of the outline, y down, in mm.

    `flush_edge` and `first_pad_from_edge_mm` mean what they mean on a board: the first pad (the first label) sits that
    far from that edge, "-x" the left one and "+x" the right one, and pad n sits n pitches further along. They are read
    on the face whose silkscreen names the pads (`face`), with the header at the top. A header on the back faces the
    breadboard, so from above its order is mirrored: x becomes width - x. The row's pad centres sit half a pitch inside
    the header's edge: the record holds no number for it, so this is an assumption, which a picture of the module (P946)
    corrects.
    """

    #: The edges a module's row may count from, and the sign of the step from one pad to the next, on the face read.
    EDGES = {"-x": 1, "+x": -1}
    #: The faces a header may sit on: the one seen from above, and the one toward the breadboard, whose order mirrors.
    FRONT, BACK = "front", "back"

    def place(self, header, size, labels):
        width, _ = size
        pitch, first = header["pitch_mm"], header["first_pad_from_edge_mm"]
        start = first if header["flush_edge"] == "-x" else width - first
        step = pitch * self.EDGES[header["flush_edge"]]
        placed = []
        for number, label in enumerate(labels):
            x = start + step * number
            placed.append((label, width - x if header["face"] == self.BACK else x, pitch / 2))
        return placed


class ModuleShapeSource(ShapeSource):
    """
    Strategy: a module with no Wokwi part whose record holds a `physical` block: its outline from `body_mm`, its one row
    of pads from `physical.header` through the placer it is given (an `OneRowHeaderPlacer` by default), each pad named by
    its printed label (`needs[].printed` and `power[].printed`, else the pin of `pin_order`). It declines (None) a record
    with no `physical` block. A record that lacks a field the drawing needs, or disagrees with itself, raises
    NotDrawnError with a code and the field, so a module is never drawn wrong. It has no ground and no doubtful pad.
    """

    NAME = RECORD
    #: The fields the drawing needs, in the order a missing one is named.
    NEEDED = ("body_mm.width", "body_mm.height", "pin_order", "physical.header.rows", "physical.header.pins",
              "physical.header.pitch_mm", "physical.header.flush_edge", "physical.header.first_pad_from_edge_mm",
              "physical.header.face")

    def __init__(self, placer=None):
        self.placer = placer or OneRowHeaderPlacer()

    @staticmethod
    def _field(record, field):
        value = record
        for key in field.split("."):
            value = value.get(key) if isinstance(value, dict) else None
        return value

    @staticmethod
    def _disagrees(field, said):
        return NotDrawnError(footprint_emitter.DISAGREES_MESSAGE % said, drawing.HEADER_DISAGREES, field)

    @staticmethod
    def printed_labels(record):
        """{pin of pin_order: the label printed beside its pad}: a need's or a supply's `printed`, else the pin itself."""
        printed = {entry.get("pin"): entry["printed"] for key in ("needs", "power") for entry in record.get(key) or []
                   if isinstance(entry, dict) and isinstance(entry.get("printed"), str) and entry["printed"]}
        return {pin: printed.get(pin, pin) for pin in record.get("pin_order") or []}

    def _refuse_odd(self, record, header, labels):
        """A header this drawing does not handle, or one that disagrees with the record's own pins."""
        for field in ("body_mm.width", "body_mm.height", "physical.header.pitch_mm", "physical.header.first_pad_from_edge_mm"):
            value = self._field(record, field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise self._disagrees(field, "%s is not a finite number above 0" % field)
        for field, ok in (("rows", header["rows"] == 1 and type(header["rows"]) is int),
                          ("pins", header["pins"] == [len(labels)]),
                          ("flush_edge", isinstance(header["flush_edge"], str) and header["flush_edge"] in OneRowHeaderPlacer.EDGES),
                          ("face", isinstance(header["face"], str) and header["face"] in (OneRowHeaderPlacer.FRONT, OneRowHeaderPlacer.BACK))):
            if not ok:
                raise self._disagrees("physical.header.%s" % field, "physical.header.%s does not fit the rest of the header" % field)

    def find_shape(self, record):
        """The PartShape of this module's record, None with no physical block, or NotDrawnError with a code and a subject."""
        if record.get("physical") is None:
            return None
        missing = next((field for field in self.NEEDED if self._field(record, field) is None), None)
        if missing:
            raise NotDrawnError("the part record lacks %s" % missing, drawing.NO_HEADER_FACT, missing)
        if None in record["pin_order"]:  # a pad with nothing on it has no label to draw: P947 may name one
            raise NotDrawnError("the part record's pin_order holds a pad with no pin", drawing.NO_HEADER_FACT, "pin_order")
        header, size = record["physical"]["header"], (record["body_mm"]["width"], record["body_mm"]["height"])
        labels = list(self.printed_labels(record).values())
        if len(set(labels)) != len(labels):
            label = next(label for label in labels if labels.count(label) > 1)
            raise NotDrawnError("two pads of the part record are called %s" % label, drawing.DUPLICATE_PAD_LABEL, label)
        self._refuse_odd(record, header, labels)
        pins = {}
        for label, x, y in self.placer.place(header, size, labels):
            if not 0 <= x <= size[0]:
                raise self._disagrees("physical.header.first_pad_from_edge_mm", "a pad lies outside the module along its edge")
            pins[label] = (round(x, 4), round(y, 4))
        return PartShape(size, pins, None, self._groups(record, len(pins), header["face"]))

    @staticmethod
    def _groups(record, pad_count, face):
        """The fact groups, verified only when the record's physical_proof says so."""
        proof = record.get("physical_proof") if isinstance(record.get("physical_proof"), dict) else {}
        verified, source = proof.get("verified") is True, proof.get("source") or "the part record's physical block"
        why = proof.get("why_it_matters") or "a pad read wrong wires the wrong pin"
        name = record.get("short_name") or record.get("id")
        groups = {"pads": {"value": pad_count, "verified": verified, "source": source, "why_it_matters": why,
                           "note": "%s pads not verified" % name, "words": "pads"}}
        if face == OneRowHeaderPlacer.BACK:
            groups["face"] = {"value": "header on the back, labels mirrored from the front", "verified": verified,
                              "source": source, "why_it_matters": "a mirrored module wires each pin to its neighbour's row",
                              "note": "%s header side not verified" % name, "words": "header side"}
        return groups

    def describe_part(self, record):
        shape = self.find_shape(record)
        if shape is None:
            return None
        part_px = project_to_px(shape, usb_mark=False, labels=svg_diagram.LABELS_INTO_BODY, full_surface=False)
        return dict(part_px, name=record.get("short_name") or record.get("id"))

    def find_pin_names(self, record):
        """{pin as the steps print it: its pad's printed label}, for every pin of pin_order."""
        return self.printed_labels(record)


def sources_for(parts=None):
    """The sources in the order they are asked: Wokwi's measured board first (from `parts`, else from the file), so a
    board with a complete record that Wokwi also draws right keeps its measured numbers, and a stand-in is never drawn."""
    return (WokwiGeometryShapeSource(parts), RecordShapeSource())


SHAPE_SOURCES = sources_for()


def find_source(board, sources=SHAPE_SOURCES):
    """The first source that describes this board, or NotDrawnError when none does."""
    for source in sources:
        if source.describe_part(board) is not None:
            return source
    raise NotDrawnError("nothing says how to draw the board %s" % board.get("id"), drawing.NO_DRAWING_FACT, board.get("id"))


def find_part_px(board, sources=SHAPE_SOURCES):
    """(part_px, the name of the source that described it) of this board."""
    source = find_source(board, sources)
    return source.describe_part(board), source.NAME
