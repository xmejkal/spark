"""
A person's moves, kept across a rebuild (P273, #309). The drawn breadboard (`breadboard.json`) is a layout the person
may edit in Wokwi. This library reads the earlier file before the build writes the new one, keeps each part where the
person put it when it still fits, and names each part it could not keep and why. `breadboard.py` calls it; nothing
here writes a file.

    EarlierDiagram.read(path, surface_type)                         the file as parts and jumpers by id
    KeepMovesFirstFitPartPlacement(geometry, earlier, catalog)      a Strategy for BreadboardPlanner
    KeepMovesJumperPlacement(geometry, earlier)                     a Strategy for BreadboardPlanner
    name_parts_not_kept(earlier, layout, fresh, reasons, default_code)                [NotKeptResult]
    name_jumpers_not_kept(earlier, layout, fresh, reasons, geometry, drawn, default_code)  [NotKeptResult]

A part keeps its place when it still fits. A resistor is checked when it is placed, because the row it joins is known
only then; its id is its order in the circuit, so an earlier "R1" can be a different resistor now, and its place is
kept only if it is legal for this one. A jumper keeps its holes, route and direction when its two rows are the two
rows of a jumper the plan draws, so a kept jumper never changes what is connected. A jumper spark drew itself, which
the wiring record says (P300), is never named when a new circuit leaves it out; a jumper the person moved always is.
"""

import collections
import json
import math
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
PIN_OFF_ROW = "pin-off-row"
ROWS_NOT_JOINED = "rows-not-joined"
JUMPER_NOT_ON_BOARD = "jumper-not-on-board"
UNREADABLE = "unreadable"
CODES = (NOT_IN_CIRCUIT, TYPE_CHANGED, TURN_UNKNOWN, PIN_OFF_HOLES, HOLE_TAKEN, ROW_SHARED, NO_ROOM, PIN_OFF_ROW,
         ROWS_NOT_JOINED, JUMPER_NOT_ON_BOARD, UNREADABLE)
MESSAGES = {
    NOT_IN_CIRCUIT: "it is not in the new circuit",
    TYPE_CHANGED: "its Wokwi type changed from %s to %s",
    TURN_UNKNOWN: "its turn of %s degrees is not a quarter turn",
    PIN_OFF_HOLES: "its pin %s is not over a hole",
    HOLE_TAKEN: "hole %s is taken by %s",
    ROW_SHARED: "two of its pins share a row, or a row holds another part",
    NO_ROOM: "the half breadboard has no room with it kept, so spark placed it",
    PIN_OFF_ROW: "its pin %s is no longer in the row it joins, so spark placed it",
    ROWS_NOT_JOINED: "no jumper of the new layout is left to join rows %s and %s, so spark drew its own",
    JUMPER_NOT_ON_BOARD: "it does not join two holes of the breadboard, so spark drew its own",
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


class EarlierJumper(collections.namedtuple("EarlierJumper", "one other route")):
    """Value: one connection of the earlier file, as the person left it. Its ends are hole names (4b.j) when they lie
    on the breadboard, else the file's own text (board:D8); `route` is the tuple of strings Wokwi writes for its bends."""

    __slots__ = ()

    @property
    def subject(self):
        return "jumper %s-%s" % (self.one, self.other)


class EarlierDiagram:
    """
    Value: the parts and jumpers of the breadboard.json that the build wrote before, as the person left it: `parts` is
    {id: the part's Wokwi entry}, without the breadboard itself, and `jumpers` is [EarlierJumper] in file order.
    `why_unread` says why the file cannot be used, else None; both are then empty.
    """

    def __init__(self, parts, why_unread=None, jumpers=()):
        self.parts = parts
        self.why_unread = why_unread
        self.jumpers = list(jumpers)

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
        parts, on_surface, surface_id = {}, False, None
        try:
            data = json.loads(text)
            for one in data["parts"]:
                if one["type"] == surface_type:
                    if float(one["left"]) != 0 or float(one["top"]) != 0:
                        return cls({}, "has its breadboard moved from 0, 0, so its parts are not where the build "
                                       "draws them")
                    on_surface, surface_id = True, surface_id or one["id"]
                    continue
                if not math.isfinite(float(one["left"])) or not math.isfinite(float(one["top"])):
                    raise ValueError("a position that is not a number")
                parts.setdefault(one["id"], one)
        except (ValueError, KeyError, TypeError) as broken:
            return cls({}, "is not a Wokwi diagram of spark's kind (%s: %s)" % (type(broken).__name__, broken))
        if not on_surface:
            return cls({}, "has no %s to put parts on" % surface_type)
        try:
            jumpers = [_jumper_of(item, surface_id) for item in data.get("connections", [])]
        except (ValueError, TypeError) as broken:
            return cls({}, "is not a Wokwi diagram of spark's kind (%s: %s)" % (type(broken).__name__, broken))
        return cls(parts, None, jumpers)


def _jumper_of(item, surface_id):
    """The EarlierJumper of one connection [end, end, color, route]; the color and route may be missing. Raises
    ValueError for anything else."""
    if not (isinstance(item, list) and len(item) >= 2 and all(isinstance(end, str) for end in item[:2])):
        raise ValueError("a connection that is not a list of two ends")
    route = item[3] if len(item) > 3 else []
    if not (isinstance(route, list) and all(isinstance(bend, str) for bend in route)):
        raise ValueError("a route that is not a list of strings")
    prefix = surface_id + ":"
    ends = [end[len(prefix):] if end.startswith(prefix) else end for end in item[:2]]
    return EarlierJumper(ends[0], ends[1], tuple(route))


def pin_holes(geometry, shape, turn, left, top):
    """{Wokwi pin: the Hole under it, or None} for a part of this shape turned and placed so."""
    turned = breadboard_drawing.rotate(shape["pins"], shape["center"], turn)
    return {pin: geometry.hole_at(left + x, top + y) for pin, (x, y) in turned.items()}


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
            placed, refused = self._keep(part_id, part, drawn, ledger)
            if refused:
                self.reasons[part_id] = refused
            else:
                self.reserved[part_id] = placed

    def _keep(self, part_id, part, drawn, ledger, pinned=None):
        """(the part placed where it was, None) with its holes claimed, or (None, (code, message)) saying why not.
        `pinned` (Wokwi pin, group) is a resistor's pin that must lie in the row it joins, which already holds other
        pins; every other pin needs a row of its own that holds nothing."""
        if part["type"] != drawn.type:
            return None, (TYPE_CHANGED, MESSAGES[TYPE_CHANGED] % (part["type"], drawn.type))
        turn = part.get("rotate", 0)
        if turn not in QUARTER_TURNS_DEGREES:
            return None, (TURN_UNKNOWN, MESSAGES[TURN_UNKNOWN] % turn)
        turn, left, top = int(turn), float(part["left"]), float(part["top"])
        shape = self.geometry.part(drawn.type)
        holes = pin_holes(self.geometry, shape, turn, left, top)
        off = next((pin for pin, hole in holes.items() if hole is None), None)
        if off is not None:
            return None, (PIN_OFF_HOLES, MESSAGES[PIN_OFF_HOLES] % off)
        if pinned and holes[pinned[0]].group != pinned[1]:
            return None, (PIN_OFF_ROW, MESSAGES[PIN_OFF_ROW] % pinned[0])
        covered = self._covered(shape, turn, left, top, holes) if shape.get("covers_holes") else []
        for hole in list(holes.values()) + covered:
            if not ledger.is_free(hole):
                return None, (HOLE_TAKEN, MESSAGES[HOLE_TAKEN] % (hole.name, ledger.taken[hole.name]))
        groups = [hole.group for hole in holes.values()]
        alone = [hole.group for pin, hole in holes.items() if not pinned or pin != pinned[0]]
        if len(set(groups)) < len(groups) or not all(ledger.group_is_free(group) for group in alone):
            return None, (ROW_SHARED, MESSAGES[ROW_SHARED])
        for pin, hole in holes.items():
            ledger.claim(hole, "%s %s" % (part_id, pin))
        for hole in covered:
            ledger.claim(hole, "%s, which covers it" % part_id)
        return breadboard_drawing.PlacedPart(part_id, drawn.type, drawn.attrs, left, top, turn, holes), None

    def place(self, part_id, drawn, ledger, after=0, pinned=None):
        kept = self.reserved.pop(part_id, None)
        if kept is None and drawn.type == RESISTOR_TYPE and part_id in self.earlier.parts:
            kept, refused = self._keep(part_id, self.earlier.parts[part_id], drawn, ledger, pinned)
            if refused:
                self.reasons[part_id] = refused
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
    ({part id: (code, message)}). One placed away from its earlier place is named only if the person moved it, that is, if its earlier
    place differs from where `fresh` (the layout planned with nothing kept) puts it: `default_code` (None names
    nothing). A part at its earlier place, and a part that is not in
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
            if default_code:
                named.append(_result(part_id, default_code))
    return named


def _place(left, top, turn):
    return round(float(left), PLACE_DIGITS), round(float(top), PLACE_DIGITS), turn


class KeepMovesJumperPlacement(breadboard_drawing.JumperPlacement):
    """
    Strategy: an earlier jumper keeps its holes, route and direction when its two rows are the two rows of a planned
    jumper that no earlier jumper has taken yet and both its holes are free. The first in the file wins a pair of rows
    and a hole. Every other jumper takes its first free hole in its own rows, so no jumper changes a row, and nothing
    kept leaves the layout as it was. `reasons` is {EarlierJumper.subject: (code, message)} for each earlier jumper
    that is not in the layout; two earlier jumpers with the same ends share one entry. Built for one plan.
    """

    def __init__(self, geometry, earlier):
        self.geometry = geometry
        self.earlier = earlier
        self.reasons = {}

    def place_jumpers(self, layout, ledger):
        holes = {hole.name: hole for hole in ledger.surface.holes}
        kept = {}
        for wire in self.earlier.jumpers:
            ends = (holes.get(wire.one), holes.get(wire.other))
            if None in ends:
                self.reasons[wire.subject] = (JUMPER_NOT_ON_BOARD, MESSAGES[JUMPER_NOT_ON_BOARD])
                continue
            rows = {end.group for end in ends}
            index = next((i for i, planned in enumerate(layout.jumpers)
                          if i not in kept and {planned.one.group, planned.other.group} == rows), None)
            taken = next((end for end in ends if not ledger.is_free(end)), None)
            if index is None:
                self.reasons[wire.subject] = (ROWS_NOT_JOINED, MESSAGES[ROWS_NOT_JOINED] % tuple(
                    end.group for end in ends))
            elif taken:
                self.reasons[wire.subject] = (HOLE_TAKEN, MESSAGES[HOLE_TAKEN] % (taken.name, ledger.taken[taken.name]))
            else:
                for end in ends:
                    ledger.claim(end, wire.subject)
                kept[index] = (wire, ends)
        if not kept:
            return layout
        jumpers = []
        for index, planned in enumerate(layout.jumpers):
            if index in kept:
                wire, ends = kept[index]
                jumpers.append(planned._replace(one=ends[0], other=ends[1], route=wire.route))
            else:
                by = "jumper %d" % planned.step
                jumpers.append(planned._replace(one=ledger.claim_free_hole(planned.one.group, by),
                                                other=ledger.claim_free_hole(planned.other.group, by)))
        return layout._replace(jumpers=jumpers)


def name_jumpers_not_kept(earlier, layout, fresh, reasons, geometry, drawn, default_code=None):
    """
    [NotKeptResult], in the earlier file's order, for each earlier jumper that is in neither `layout` nor `fresh` (the
    layout planned with nothing kept, which holds the jumpers the build drew before), with its reason from `reasons`
    ({subject: (code, message)}) else `default_code` (None names nothing). `drawn` is the set of hole pairs (frozensets)
    that spark drew itself at the last build, from the wiring record, or None when there is no record. A jumper in
    `drawn` is spark's: a new circuit leaves it out and it is never named. Any other jumper is the person's and is
    named whenever it is not kept. With no record, nothing is known to be spark's, so a jumper refused for rows no
    planned jumper joins, or by the default, is not named.
    """
    holes = {hole.name: hole for hole in geometry.surface.holes}
    pairs = {frozenset((jumper.one.name, jumper.other.name)) for planned in (layout, fresh)
             for jumper in planned.jumpers}
    named = []
    for wire in earlier.jumpers:
        pair = frozenset((wire.one, wire.other))
        if pair in pairs:
            continue
        if wire.one not in holes or wire.other not in holes:
            named.append(NotKeptResult(wire.subject, JUMPER_NOT_ON_BOARD, MESSAGES[JUMPER_NOT_ON_BOARD]))
            continue
        if drawn is not None and pair in drawn:
            continue
        code, why = reasons.get(wire.subject) or (default_code, default_code and MESSAGES[default_code])
        if code is None or drawn is None and code in (ROWS_NOT_JOINED, default_code):
            continue
        named.append(NotKeptResult(wire.subject, code, why))
    return named
