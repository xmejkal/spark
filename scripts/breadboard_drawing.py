"""
The drawn breadboard (P267, #300): the sheet's steps on a Wokwi half breadboard, each part's legs in holes and each
step's jumper in the step's color, written as `breadboard.json`, a second Wokwi diagram.

A pure planner turns the steps into holes, and a renderer turns the holes into a diagram. The planner reads the steps
from `BreadboardSteps.anchored()`, so it never decides the wiring again. Where Wokwi draws each pin and hole comes from
`data/wokwi-geometry.json`, measured once in Wokwi. A leg over a hole connects in Wokwi with no connection entry, so
only the jumpers are connections.

    BreadboardPlanner(geometry, catalog).plan(steps)  ->  BreadboardLayout  ->  WokwiBreadboardDiagram().render(layout)
"""

import collections
import json
from pathlib import Path

import breadboard_steps

GEOMETRY = Path(__file__).resolve().parent.parent / "data" / "wokwi-geometry.json"
FILE = "breadboard.json"

#: One hole: its Wokwi name (12t.a, tp.3), its center in px, and its row (the holes joined with it: 12t, or tp).
Hole = collections.namedtuple("Hole", "name x y row")
#: What the planner draws for one component: its Wokwi type and attrs, and {its pin as the steps name it: Wokwi pin}.
DrawnPart = collections.namedtuple("DrawnPart", "type attrs pins")
#: One component on the breadboard: its id, type, attrs, top-left corner in px, its turn, and {Wokwi pin: Hole}.
PlacedPart = collections.namedtuple("PlacedPart", "id type attrs left top rotate holes")
#: One jumper between two holes, drawn in the color of the step it belongs to.
Jumper = collections.namedtuple("Jumper", "one other step")
#: Value: the whole drawing as holes, which any renderer reads.
BreadboardLayout = collections.namedtuple("BreadboardLayout", "breadboard parts jumpers")


class NotDrawn(Exception):
    """The steps cannot be drawn: a fact the drawing needs is missing, or the half breadboard has no room."""


class WokwiGeometry:
    """Value: the measured geometry of Wokwi's half breadboard and parts (data/wokwi-geometry.json)."""

    def __init__(self, data):
        self.data = data
        board = data["breadboard"]
        self.type = board["type"]
        self.tolerance = data["tolerance_px"]
        self.holes = []
        for number in range(1, board["columns"] + 1):
            x = board["first_column_x"] + board["pitch"] * (number - 1)
            for letter, y in board["letters_y"].items():
                row = "%d%s" % (number, "t" if letter in board["top_letters"] else "b")
                self.holes.append(Hole("%s.%s" % (row, letter), x, y, row))
        for rail, y in board["rails_y"].items():
            for number in range(1, board["rail_holes"] + 1):
                x = board["first_rail_x"] + board["pitch"] * (number - 1 + (number - 1) // board["rail_group"])
                self.holes.append(Hole("%s.%d" % (rail, number), x, y, rail))
        self.terminal = [hole for hole in self.holes if hole.row not in board["rails_y"]]
        #: The terminal holes column by column, nearest the gap first: a part sits by the gap, clear of the rails.
        gap = (max(board["letters_y"][letter] for letter in board["top_letters"])
               + min(y for letter, y in board["letters_y"].items() if letter not in board["top_letters"])) / 2
        self.by_gap = sorted(self.terminal, key=lambda hole: (column(hole), abs(hole.y - gap), hole.y))
        self.rails = list(board["rails_y"])

    @classmethod
    def load(cls, path=GEOMETRY):
        return cls(json.loads(Path(path).read_text()))

    def part(self, wokwi_type):
        """{center, covers_holes, pins} of one Wokwi type, or NotDrawn naming it."""
        found = self.data["parts"].get(wokwi_type)
        if found is None:
            raise NotDrawn("no Wokwi pin positions for %s in data/wokwi-geometry.json" % wokwi_type)
        return found

    def hole_at(self, x, y):
        """The terminal hole whose center lies within the tolerance of (x, y), else None."""
        return next((hole for hole in self.terminal
                     if abs(hole.x - x) <= self.tolerance and abs(hole.y - y) <= self.tolerance), None)


def rotate(pins, center, degrees):
    """{pin: (x, y)} turned clockwise about the center, as Wokwi turns a part. Not rounded: round once, at the end."""
    cx, cy = center
    turned = {}
    for pin, (x, y) in pins.items():
        for _ in range(degrees // 90 % 4):
            x, y = cx + cy - y, cy - cx + x
        turned[pin] = (x, y)
    return turned


def column(hole):
    return int(hole.row[:-1]) if hole.row[-1] in "tb" else 0


class HoleLedger:
    """The taken holes. A claim of a taken hole is refused and names it."""

    def __init__(self, geometry):
        self.geometry = geometry
        self.taken = {}

    def claim(self, hole, by):
        if hole.name in self.taken:
            raise NotDrawn("hole %s is taken by %s, and %s needs it too" % (hole.name, self.taken[hole.name], by))
        self.taken[hole.name] = by

    def is_free(self, hole):
        return hole.name not in self.taken

    def row_is_free(self, row):
        return all(self.is_free(hole) for hole in self.geometry.holes if hole.row == row)

    def free_hole(self, row, by):
        """Claim the first free hole of one row, or NotDrawn: the row is full."""
        hole = next((hole for hole in self.geometry.holes if hole.row == row and self.is_free(hole)), None)
        if hole is None:
            raise NotDrawn("row %s has no free hole for %s" % (row, by))
        self.claim(hole, by)
        return hole

    def free_row(self, after, by):
        """Claim a hole in the first row right of column `after` with nothing in it, or NotDrawn: the board is full."""
        for hole in self.geometry.terminal:
            if column(hole) > after and self.row_is_free(hole.row):
                self.claim(hole, by)
                return hole
        raise NotDrawn("the half breadboard has no free row left for %s" % by)


class PartPlacement:
    """Strategy: where one part goes, and how it is turned."""

    def place(self, part_id, drawn, ledger, after=0, pinned=None):
        raise NotImplementedError


class FirstFitPlacement(PartPlacement):
    """
    The first turn and position, left to right, where every pin lies over a free hole, each pin in a row of its own
    that holds nothing else, and every hole the part covers is free. A board that straddles the gap fits only when
    turned, because its pins in one line would share a row. `pinned` (pin, row) puts one pin in a row that already
    holds something: a resistor's leg in the row of the pin it joins.
    """

    #: Flat first, so a resistor lies along a row of holes before it stands across the gap.
    TURNS = (0, 180, 90, 270)

    def __init__(self, geometry):
        self.geometry = geometry

    def place(self, part_id, drawn, ledger, after=0, pinned=None):
        shape = self.geometry.part(drawn.type)
        wanted = [pin for pin in drawn.pins.values() if pin not in shape["pins"]]
        if wanted:
            raise NotDrawn("data/wokwi-geometry.json has no pin %s on %s" % (wanted[0], drawn.type))
        for degrees in self.TURNS:
            turned = rotate(shape["pins"], shape["center"], degrees)
            first = pinned[0] if pinned else next(iter(turned))
            candidates = [hole for hole in self.geometry.by_gap if not pinned or hole.row == pinned[1]]
            for hole in candidates:
                left, top = hole.x - turned[first][0], hole.y - turned[first][1]
                holes = self._fit(turned, left, top, ledger, after, pinned)
                if holes is None:
                    continue
                covered = self._covered(shape, degrees, left, top, holes) if shape.get("covers_holes") else []
                if any(not ledger.is_free(one) or column(one) <= after for one in covered):
                    continue
                for pin, one in holes.items():
                    ledger.claim(one, "%s %s" % (part_id, pin))
                for one in covered:
                    ledger.claim(one, "%s, which covers it" % part_id)
                return PlacedPart(part_id, drawn.type, drawn.attrs, left, top, degrees, holes)
        raise NotDrawn("%s does not fit on the half breadboard" % part_id)

    def _fit(self, turned, left, top, ledger, after, pinned):
        holes = {}
        for pin, (x, y) in turned.items():
            hole = self.geometry.hole_at(left + x, top + y)
            if hole is None or not ledger.is_free(hole) or (column(hole) <= after and not pinned):
                return None
            if pinned and pin == pinned[0]:
                holes[pin] = hole
                continue
            if not ledger.row_is_free(hole.row) or hole.row in {one.row for one in holes.values()}:
                return None
            holes[pin] = hole
        return holes

    def _covered(self, shape, degrees, left, top, holes):
        """The holes under the part's body, besides its own pins: its box, turned, about its center."""
        cx, cy = shape["center"]
        half_w, half_h = (cy, cx) if degrees % 180 else (cx, cy)
        mine = {hole.name for hole in holes.values()}
        return [hole for hole in self.geometry.terminal if hole.name not in mine
                and abs(hole.x - (left + cx)) < half_w and abs(hole.y - (top + cy)) < half_h]


class BreadboardPlanner:
    """Pure: the steps, the geometry and what to draw for each component in, a BreadboardLayout out."""

    #: Columns from one part's last pin to the next part's first: one empty column between them, for the jumpers.
    SPACING = 2

    def __init__(self, geometry, catalog, placement=None):
        self.geometry = geometry
        self.catalog = catalog
        self.placement = placement or FirstFitPlacement(geometry)

    def plan(self, steps):
        """Each part placed in step order, then each resistor with a leg in the row it joins, then each jumper."""
        ledger = HoleLedger(self.geometry)
        seated = list(steps.anchored())
        placed, after = {}, 1
        for one in seated:
            if one.act == breadboard_steps.PLACE:
                component = "board" if one.subject == "the board" else one.subject
                placed[component] = self.placement.place(component, self._drawn(component), ledger, after)
                after = max(column(hole) for hole in placed[component].holes.values()) + self.SPACING
        for one in seated:
            if one.act != breadboard_steps.PLACE and one.anchor.seat().kind == breadboard_steps.RAIL:
                raise NotDrawn("%s goes on a rail, and rails are not drawn yet" % one.anchor.seat().mark)
        self._place_resistors(seated, placed, ledger, after)
        rows, jumpers = {}, []
        for number, one in enumerate(seated, 1):
            end = one.subject
            if one.act == breadboard_steps.SETUP and end.kind == breadboard_steps.BOARD:
                jumper = Jumper(ledger.free_hole(self._row(end, placed, rows), end.name),
                                ledger.free_row(after, end.name), number)
                rows[end.name] = jumper.other.row
                jumpers.append(jumper)
            elif one.act == breadboard_steps.JOIN and end.kind != breadboard_steps.RESISTOR:
                anchor = one.anchor.seat().end
                jumpers.append(Jumper(ledger.free_hole(self._row(end, placed, rows), end.name),
                                      ledger.free_hole(self._row(anchor, placed, rows), anchor.name), number))
        return BreadboardLayout(self.geometry.type, list(placed.values()), jumpers)

    def _place_resistors(self, seated, placed, ledger, after):
        """A resistor has a fixed length, so it goes in with the leg that joins a row already in that row."""
        resistors = collections.OrderedDict()
        for one in seated:
            if one.act in (breadboard_steps.SETUP, breadboard_steps.JOIN) and one.subject.kind == breadboard_steps.RESISTOR:
                pinned = resistors.setdefault(one.subject.component, [])
                if one.act == breadboard_steps.JOIN:
                    pinned.append((one.subject, one.anchor.seat().end))
        for component, pinned in resistors.items():
            if len(pinned) > 1:
                raise NotDrawn("both ends of %s join other rows, and a drawn resistor has a fixed length" % component)
            drawn = self._drawn(component)
            row = [(self._pin(end), self._row(anchor, placed, {})) for end, anchor in pinned]
            placed[component] = self.placement.place(component, drawn, ledger, after if not row else 0,
                                                     row[0] if row else None)

    def _drawn(self, component):
        drawn = self.catalog.get(component)
        if drawn is None:
            raise NotDrawn("nothing says how to draw %s in Wokwi" % component)
        return drawn

    def _row(self, end, placed, rows):
        """The row an end sits in: its pin's row, or the free row its board pad's jumper took."""
        if end.name in rows:
            return rows[end.name]
        if end.component not in placed:
            raise NotDrawn("%s is joined before it is placed" % end.name)
        return placed[end.component].holes[self._pin(end)].row

    def _pin(self, end):
        """The Wokwi pin of one end, or NotDrawn naming it."""
        pin = self._drawn(end.component).pins.get(end.pin)
        if pin is None:
            raise NotDrawn("which Wokwi pin is %s is not known" % end.name)
        return pin


class WokwiBreadboardDiagram:
    """Renderer: a BreadboardLayout as a Wokwi diagram, each jumper in its step's color."""

    def __init__(self, colors=None, breadboard_id="bb1"):
        self.colors = colors or breadboard_steps.StepColors()
        self.breadboard_id = breadboard_id

    def render(self, layout):
        parts = [{"type": layout.breadboard, "id": self.breadboard_id, "top": 0, "left": 0, "attrs": {}}]
        for part in layout.parts:
            drawn = {"type": part.type, "id": part.id, "top": _px(part.top), "left": _px(part.left)}
            drawn.update({"rotate": part.rotate} if part.rotate else {})
            drawn["attrs"] = dict(part.attrs or {})
            parts.append(drawn)
        connections = [["%s:%s" % (self.breadboard_id, jumper.one.name), "%s:%s" % (self.breadboard_id,
                        jumper.other.name), self.colors.color(jumper.step), []] for jumper in layout.jumpers]
        return {"version": 1, "author": "spark", "editor": "wokwi", "parts": parts, "connections": connections,
                "dependencies": {}}

    def text(self, layout):
        """The diagram as the file holds it: the same layout gives the same bytes."""
        return json.dumps(self.render(layout), indent=2, ensure_ascii=False) + "\n"


def _px(value):
    """A position as the file holds it: rounded once, here, and whole when it is whole."""
    value = round(value, 3)
    return int(value) if value == int(value) else value
