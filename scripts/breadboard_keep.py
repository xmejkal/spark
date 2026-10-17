"""
A person's moves, kept across a rebuild (P273, #309). The drawn breadboard (`breadboard.json`) is a layout the person
may edit in Wokwi. This library reads the earlier file before the build writes the new one, keeps each part where the
person put it when it still fits, and names each part it could not keep and why. `breadboard.py` calls it; nothing
here writes a file.

    EarlierDiagram.read(path, surface_type)                         the file as parts by id
    KeepMovesFirstFitPartPlacement(geometry, earlier, catalog)      a Strategy for BreadboardPlanner
    name_parts_not_kept(earlier, layout, reasons, default_code)     [NotKeptResult]

Only parts other than a resistor are kept. A resistor's id is its order in the circuit, so an earlier "R1" can be a
different resistor now; jumpers are planned fresh from the placed parts.
"""

import collections
import json
from pathlib import Path

import breadboard_drawing

#: The codes of NotKeptResult. A code decides; the message beside it in MESSAGES is what a person reads.
NOT_IN_CIRCUIT = "not-in-circuit"
TYPE_CHANGED = "type-changed"
TURN_UNKNOWN = "turn-unknown"
PIN_OFF_HOLES = "pin-off-holes"
HOLE_TAKEN = "hole-taken"
ROW_SHARED = "row-shared"
NO_ROOM = "no-room"
RESISTOR_NOT_KEPT = "resistor-not-kept"
UNREADABLE = "unreadable"
CODES = (NOT_IN_CIRCUIT, TYPE_CHANGED, TURN_UNKNOWN, PIN_OFF_HOLES, HOLE_TAKEN, ROW_SHARED, NO_ROOM,
         RESISTOR_NOT_KEPT, UNREADABLE)
MESSAGES = {
    NOT_IN_CIRCUIT: "it is not in the new circuit",
    TYPE_CHANGED: "its Wokwi type changed from %s to %s",
    TURN_UNKNOWN: "its turn of %s degrees is not a quarter turn",
    PIN_OFF_HOLES: "its pin %s is not over a hole",
    HOLE_TAKEN: "hole %s is taken by %s",
    ROW_SHARED: "two of its pins share a row, or a row holds another part",
    NO_ROOM: "the half breadboard has no room with it kept, so spark placed it",
    RESISTOR_NOT_KEPT: "a resistor's place is not kept yet, so spark placed it",
    UNREADABLE: "the earlier diagram %s, so no part was kept",
}

#: The Wokwi type of a resistor: its id is its order in the circuit, so it is never kept.
RESISTOR_TYPE = "wokwi-resistor"
#: The turns whose pins `rotate()` can place.
QUARTER_TURNS_DEGREES = (0, 90, 180, 270)
#: Positions are compared as the file holds them, rounded to the thousandth of a px.
PLACE_DIGITS = 3


class NotKeptResult(collections.namedtuple("NotKeptResult", "subject code why")):
    """Result: one part (or the whole file) that a rebuild could not keep as the person left it, with a code from
    CODES and the reason a person reads."""

    __slots__ = ()

    @property
    def line(self):
        return "%s: %s" % (self.subject, self.why)


def _result(subject, code, *facts):
    return NotKeptResult(subject, code, MESSAGES[code] % facts if facts else MESSAGES[code])


class EarlierDiagram:
    """
    Value: the parts of the breadboard.json that the build wrote before, as the person left it: {id: the part's
    Wokwi entry}, without the breadboard itself. `why_unread` says why the file cannot be used, else None; `parts` is
    then empty.
    """

    def __init__(self, parts, why_unread=None):
        self.parts = parts
        self.why_unread = why_unread

    @classmethod
    def read(cls, path, surface_type):
        """The diagram in the file, or None when there is no file. A file that is not a diagram of a half breadboard
        gives a diagram with `why_unread`."""
        path = Path(path)
        if not path.is_file():
            return None
        try:
            return cls.parse(path.read_text(), surface_type)
        except (OSError, UnicodeDecodeError) as broken:
            return cls({}, "cannot be read (%s)" % broken)

    @classmethod
    def parse(cls, text, surface_type):
        parts, on_surface = {}, False
        try:
            for one in json.loads(text)["parts"]:
                if one["type"] == surface_type:
                    on_surface = True
                    continue
                float(one["left"]), float(one["top"])
                parts[one["id"]] = one
        except (ValueError, KeyError, TypeError) as broken:
            return cls({}, "is not a Wokwi diagram of spark's kind (%s: %s)" % (type(broken).__name__, broken))
        if not on_surface:
            return cls({}, "has no %s to put parts on" % surface_type)
        return cls(parts)


class KeepMovesFirstFitPartPlacement(breadboard_drawing.FirstFitPartPlacement):
    """
    Strategy: an earlier part keeps its place when it still fits, else spark's first fit. Built for one plan: it holds
    the reserved parts and the reasons until that plan ends. `reserve_first` claims each earlier part, in file order,
    whose id and Wokwi type are in the circuit, that is not a resistor, with a quarter turn, every pin over a free hole
    in a row of its own and every covered hole free; the first part in the file wins a hole. `reasons` is
    {part id: (code, message)} for each earlier part refused. A part that does not fit after a kept part is tried again
    from column 0. Raises NotDrawn as FirstFitPartPlacement does.
    """

    def __init__(self, geometry, earlier, catalog):
        super().__init__(geometry)
        self.earlier = earlier
        self.catalog = catalog
        self.reserved = {}
        self.reasons = {}

    def reserve_first(self, ledger):
        for part_id, part in self.earlier.parts.items():
            drawn = self.catalog.get(part_id)
            if drawn is None or drawn.type == RESISTOR_TYPE:
                continue
            refused = self._reserve(part_id, part, drawn, ledger)
            if refused:
                self.reasons[part_id] = refused

    def _reserve(self, part_id, part, drawn, ledger):
        """Claim the part's holes and remember it, or return (code, message) saying why not."""
        if part["type"] != drawn.type:
            return TYPE_CHANGED, MESSAGES[TYPE_CHANGED] % (part["type"], drawn.type)
        turn = part.get("rotate", 0)
        if turn not in QUARTER_TURNS_DEGREES:
            return TURN_UNKNOWN, MESSAGES[TURN_UNKNOWN] % turn
        turn, left, top = int(turn), float(part["left"]), float(part["top"])
        shape = self.geometry.part(drawn.type)
        turned = breadboard_drawing.rotate(shape["pins"], shape["center"], turn)
        holes = {pin: self.geometry.hole_at(left + x, top + y) for pin, (x, y) in turned.items()}
        off = next((pin for pin, hole in holes.items() if hole is None), None)
        if off is not None:
            return PIN_OFF_HOLES, MESSAGES[PIN_OFF_HOLES] % off
        covered = self._covered(shape, turn, left, top, holes) if shape.get("covers_holes") else []
        for hole in list(holes.values()) + covered:
            if not ledger.is_free(hole):
                return HOLE_TAKEN, MESSAGES[HOLE_TAKEN] % (hole.name, ledger.taken[hole.name])
        groups = [hole.group for hole in holes.values()]
        if len(set(groups)) < len(groups) or not all(ledger.group_is_free(group) for group in groups):
            return ROW_SHARED, MESSAGES[ROW_SHARED]
        for pin, hole in holes.items():
            ledger.claim(hole, "%s %s" % (part_id, pin))
        for hole in covered:
            ledger.claim(hole, "%s, which covers it" % part_id)
        self.reserved[part_id] = breadboard_drawing.PlacedPart(part_id, drawn.type, drawn.attrs, left, top, turn, holes)
        return None

    def place(self, part_id, drawn, ledger, after=0, pinned=None):
        kept = self.reserved.pop(part_id, None)
        if kept:
            return kept
        try:
            return super().place(part_id, drawn, ledger, after, pinned)
        except breadboard_drawing.NotDrawn:
            if not after:
                raise
            return super().place(part_id, drawn, ledger, 0, pinned)


def name_parts_not_kept(earlier, layout, fresh, reasons, default_code=None):
    """
    [NotKeptResult], in the earlier file's order, for each earlier part that `layout` does not keep as the person left
    it. One that `layout` lacks is NOT_IN_CIRCUIT. One the placement refused is named with its reason from `reasons`
    ({part id: (code, message)}). One placed away from its earlier place is named only if the person moved it, that is,
    if its earlier place differs from where `fresh` (the layout planned with nothing kept) puts it: RESISTOR_NOT_KEPT
    for a resistor, else `default_code` (None names nothing). A part at its earlier place, and a part that is not in
    the earlier file, are never named.
    """
    placed = {one.id: one for one in layout.parts}
    fresh_places = {one.id: _place(one.left, one.top, one.rotate) for one in fresh.parts}
    named = []
    for part_id, part in earlier.parts.items():
        now = placed.get(part_id)
        before = _place(part["left"], part["top"], part.get("rotate", 0))
        if now is None:
            named.append(_result(part_id, NOT_IN_CIRCUIT))
        elif part_id in reasons:
            named.append(NotKeptResult(part_id, *reasons[part_id]))
        elif _place(now.left, now.top, now.rotate) != before and fresh_places.get(part_id) != before:
            code = RESISTOR_NOT_KEPT if now.type == RESISTOR_TYPE else default_code
            if code:
                named.append(_result(part_id, code))
    return named


def _place(left, top, turn):
    return round(float(left), PLACE_DIGITS), round(float(top), PLACE_DIGITS), turn
