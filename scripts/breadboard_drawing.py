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

WOKWI_GEOMETRY_FILE = Path(__file__).resolve().parent.parent / "data" / "wokwi-geometry.json"
DRAWING_FILE = "breadboard.json"

#: Value: one hole, its Wokwi name (12t.a, tp.3), its center in px, its group (the holes joined with it inside the
#: board: a breadboard row such as 12t, or a rail such as tp), and its column (from 1; a rail hole has none, 0).
Hole = collections.namedtuple("Hole", "name x y group column")
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


class Surface:
    """
    Value: the holes of a board and which are joined inside it, from data/wokwi-geometry.json. A group is the holes
    joined inside the board: on a breadboard a row of five or a rail, on a perfboard later a single hole. (netlist.py
    says net only once something is wired.)
    """

    def __init__(self, board):
        self.type = board["type"]
        self.holes = []
        for number in range(1, board["columns"] + 1):
            x = board["first_column_x"] + board["pitch"] * (number - 1)
            for letter, y in board["letters_y"].items():
                group = "%d%s" % (number, "t" if letter in board["top_letters"] else "b")
                self.holes.append(Hole("%s.%s" % (group, letter), x, y, group, number))
        for rail, y in board["rails_y"].items():
            for number in range(1, board["rail_holes"] + 1):
                x = board["first_rail_x"] + board["pitch"] * (number - 1 + (number - 1) // board["rail_block"])
                self.holes.append(Hole("%s.%d" % (rail, number), x, y, rail, 0))
        self.terminal = [hole for hole in self.holes if hole.column]
        self.rails = list(board["rails_y"])
        #: The terminal holes column by column, nearest the gap first and the side below the gap before the side above
        #: it at the same distance: ranked by letter, never by float distance, whose ties would move a part.
        top = board["top_letters"]
        bottom = [letter for letter in board["letters_y"] if letter not in top]
        rank = {letter: (index, 1) for index, letter in enumerate(reversed(top))}
        rank.update({letter: (index, 0) for index, letter in enumerate(bottom)})
        self.by_gap = sorted(self.terminal, key=lambda hole: (hole.column,) + rank[hole.name.rsplit(".", 1)[1]])

    def hole_at(self, x, y, tolerance):
        """The terminal hole whose center lies within the tolerance of (x, y), else None."""
        return next((hole for hole in self.terminal if abs(hole.x - x) <= tolerance and abs(hole.y - y) <= tolerance),
                    None)


class WokwiGeometry:
    """Value: where Wokwi draws each part's pins, and the surface of its half breadboard
    (data/wokwi-geometry.json)."""

    def __init__(self, data):
        self.data = data
        self.surface = Surface(data["breadboard"])
        self.tolerance = data["tolerance_px"]

    @classmethod
    def load(cls, path=WOKWI_GEOMETRY_FILE):
        return cls(json.loads(Path(path).read_text()))

    def part(self, wokwi_type):
        """{center, covers_holes, pins} of one Wokwi type, or NotDrawn naming it."""
        found = self.data["parts"].get(wokwi_type)
        if found is None:
            raise NotDrawn("no Wokwi pin positions for %s in data/wokwi-geometry.json" % wokwi_type)
        return found

    def hole_at(self, x, y):
        """The terminal hole under a pin at (x, y), within the measured tolerance, else None."""
        return self.surface.hole_at(x, y, self.tolerance)


def rotate(pins, center, degrees):
    """{pin: (x, y)} turned clockwise about the center, as Wokwi turns a part. Not rounded: round once, at the end."""
    cx, cy = center
    turned = {}
    for pin, (x, y) in pins.items():
        for _ in range(degrees // 90 % 4):
            x, y = cx + cy - y, cy - cx + x
        turned[pin] = (x, y)
    return turned


class HoleLedger:
    """The taken holes of one surface. A claim of a taken hole is refused and names it. (Its messages say row, the word
    a person reads on the sheet.)"""

    def __init__(self, surface):
        self.surface = surface
        self.taken = {}

    def claim(self, hole, by):
        if hole.name in self.taken:
            raise NotDrawn("hole %s is taken by %s, and %s needs it too" % (hole.name, self.taken[hole.name], by))
        self.taken[hole.name] = by

    def is_free(self, hole):
        return hole.name not in self.taken

    def group_is_free(self, group):
        return all(self.is_free(hole) for hole in self.surface.holes if hole.group == group)

    def claim_free_hole(self, group, by):
        """Claim the first free hole of one group, or NotDrawn: the group is full."""
        hole = next((hole for hole in self.surface.holes if hole.group == group and self.is_free(hole)), None)
        if hole is None:
            raise NotDrawn("row %s has no free hole for %s" % (group, by))
        self.claim(hole, by)
        return hole

    def claim_free_group(self, after, by):
        """Claim a hole in the first group right of column `after` with nothing in it, or NotDrawn: the board is
        full."""
        for hole in self.surface.terminal:
            if hole.column > after and self.group_is_free(hole.group):
                self.claim(hole, by)
                return hole
        raise NotDrawn("the half breadboard has no free row left for %s" % by)


class PartPlacement:
    """Strategy: where one part goes, and how it is turned."""

    def place(self, part_id, drawn, ledger, after=0, pinned=None):
        raise NotImplementedError


class FirstFitPartPlacement(PartPlacement):
    """
    The first turn and position, left to right, where every pin lies over a free hole, each pin in a group of its own
    that holds nothing else, and every hole the part covers is free. A board that straddles the gap fits only when
    turned, because its pins in one line would share a group. `pinned` (pin, group) puts one pin in a group that already
    holds something: a resistor's leg in the group of the pin it joins.
    """

    #: Flat first, so a resistor lies along a row of holes before it stands across the gap.
    TURNS_DEGREES = (0, 180, 90, 270)

    def __init__(self, geometry):
        self.geometry = geometry

    def place(self, part_id, drawn, ledger, after=0, pinned=None):
        shape = self.geometry.part(drawn.type)
        wanted = [pin for pin in drawn.pins.values() if pin not in shape["pins"]]
        if wanted:
            raise NotDrawn("data/wokwi-geometry.json has no pin %s on %s" % (wanted[0], drawn.type))
        for degrees in self.TURNS_DEGREES:
            turned = rotate(shape["pins"], shape["center"], degrees)
            first = pinned[0] if pinned else next(iter(turned))
            candidates = [hole for hole in self.geometry.surface.by_gap if not pinned or hole.group == pinned[1]]
            for start in candidates:
                left, top = start.x - turned[first][0], start.y - turned[first][1]
                holes = self._fit(turned, left, top, ledger, after, pinned)
                if holes is None:
                    continue
                covered = self._covered(shape, degrees, left, top, holes) if shape.get("covers_holes") else []
                if any(not ledger.is_free(hole) or hole.column <= after for hole in covered):
                    continue
                for pin, hole in holes.items():
                    ledger.claim(hole, "%s %s" % (part_id, pin))
                for hole in covered:
                    ledger.claim(hole, "%s, which covers it" % part_id)
                return PlacedPart(part_id, drawn.type, drawn.attrs, left, top, degrees, holes)
        raise NotDrawn("%s does not fit on the half breadboard" % part_id)

    def _fit(self, turned, left, top, ledger, after, pinned):
        holes = {}
        for pin, (x, y) in turned.items():
            hole = self.geometry.hole_at(left + x, top + y)
            if hole is None or not ledger.is_free(hole) or (hole.column <= after and not pinned):
                return None
            if pinned and pin == pinned[0]:
                holes[pin] = hole
                continue
            if not ledger.group_is_free(hole.group) or hole.group in {one.group for one in holes.values()}:
                return None
            holes[pin] = hole
        return holes

    def _covered(self, shape, degrees, left, top, holes):
        """The holes under the part's body, besides its own pins: its box, turned, about its center."""
        cx, cy = shape["center"]
        half_w, half_h = (cy, cx) if degrees % 180 else (cx, cy)
        mine = {hole.name for hole in holes.values()}
        return [hole for hole in self.geometry.surface.terminal if hole.name not in mine
                and abs(hole.x - (left + cx)) < half_w and abs(hole.y - (top + cy)) < half_h]


class BreadboardPlanner:
    """Pure: the steps, the geometry and what to draw for each component in, a BreadboardLayout out."""

    #: Columns from one part's last pin to the next part's first: one empty column between them, for the jumpers.
    SPACING_COLUMNS = 2

    def __init__(self, geometry, catalog, placement=None):
        self.geometry = geometry
        self.catalog = catalog
        self.placement = placement or FirstFitPartPlacement(geometry)

    def plan(self, steps):
        """Each part placed in step order, then each resistor with a leg in the row it joins, then each jumper."""
        ledger = HoleLedger(self.geometry.surface)
        seated = list(steps.anchored())
        placed, after = {}, 1
        for step in seated:
            if step.act == breadboard_steps.PLACE:
                placed[step.subject] = self.placement.place(step.subject, self._drawn(step.subject), ledger, after)
                after = max(hole.column for hole in placed[step.subject].holes.values()) + self.SPACING_COLUMNS
        for step in seated:
            if step.act != breadboard_steps.PLACE and step.anchor.seat().kind == breadboard_steps.RAIL:
                raise NotDrawn("%s goes on a rail, and rails are not drawn yet" % step.anchor.seat().mark)
            if step.act == breadboard_steps.SUPPLY:
                raise NotDrawn("the %s supply comes from off the board, and a supply is not drawn yet" % step.subject)
        self._place_resistors(seated, placed, ledger, after)
        groups, jumpers = {}, []
        for number, step in enumerate(seated, 1):
            end = step.subject
            if not step.jumper:
                continue
            if step.act == breadboard_steps.SETUP:
                jumper = Jumper(ledger.claim_free_hole(self._group_of(end, placed, groups), end.name),
                                ledger.claim_free_group(after, end.name), number)
                groups[end.name] = jumper.other.group
                jumpers.append(jumper)
            else:
                anchor = step.anchor.seat().end
                jumpers.append(Jumper(ledger.claim_free_hole(self._group_of(end, placed, groups), end.name),
                                      ledger.claim_free_hole(self._group_of(anchor, placed, groups), anchor.name), number))
        return BreadboardLayout(self.geometry.surface.type, list(placed.values()), jumpers)

    def _place_resistors(self, seated, placed, ledger, after):
        """A resistor has a fixed length, so it goes in with the leg that joins a row already in that row."""
        resistors = collections.OrderedDict()
        for step in seated:
            if (step.act in (breadboard_steps.SETUP, breadboard_steps.JOIN)
                    and step.subject.kind == breadboard_steps.RESISTOR):
                pinned = resistors.setdefault(step.subject.component, [])
                if step.act == breadboard_steps.JOIN:
                    pinned.append((step.subject, step.anchor.seat().end))
        waiting = list(resistors.items())
        while waiting:
            # a resistor whose leg joins another resistor's row waits until that resistor is in
            ready = [(component, pinned) for component, pinned in waiting
                     if all(anchor.component in placed for _, anchor in pinned)]
            if not ready:
                raise NotDrawn("%s joins a row that is never placed" % waiting[0][0])
            for component, pinned in ready:
                if len(pinned) > 1:
                    raise NotDrawn("both ends of %s join other rows, and a drawn resistor has a fixed length"
                                   % component)
                drawn = self._drawn(component)
                row = [(self._pin(end), self._group_of(anchor, placed, {})) for end, anchor in pinned]
                placed[component] = self.placement.place(component, drawn, ledger, after if not row else 0,
                                                         row[0] if row else None)
            waiting = [one for one in waiting if one[0] not in placed]

    def _drawn(self, component):
        drawn = self.catalog.get(component)
        if drawn is None:
            raise NotDrawn("nothing says how to draw %s in Wokwi" % component)
        return drawn

    def _group_of(self, end, placed, groups):
        """The row an end sits in: its pin's row, or the free row its board pad's jumper took."""
        if end.name in groups:
            return groups[end.name]
        if end.component not in placed:
            raise NotDrawn("%s is joined before it is placed" % end.name)
        return placed[end.component].holes[self._pin(end)].group

    def _pin(self, end):
        """The Wokwi pin of one end, or NotDrawn naming it."""
        pin = self._drawn(end.component).pins.get(end.pin)
        if pin is None:
            raise NotDrawn("which Wokwi pin is %s is not known" % end.name)
        return pin


class WokwiBreadboardDiagram:
    """Renderer: a BreadboardLayout as a Wokwi diagram, each jumper in its step's color. Its constructor takes the
    colors, so the sheet and the diagram share one palette."""

    def __init__(self, colors=None, breadboard_id="bb1"):
        self.colors = colors or breadboard_steps.StepColors()
        self.breadboard_id = breadboard_id

    def render(self, layout):
        parts = [{"type": layout.breadboard, "id": self.breadboard_id, "top": 0, "left": 0, "attrs": {}}]
        for part in layout.parts:
            drawn = {"type": part.type, "id": part.id, "top": _round_px(part.top), "left": _round_px(part.left)}
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


def _round_px(value):
    """A position as the file holds it: rounded once, here, and whole when it is whole."""
    value = round(value, 3)
    return int(value) if value == int(value) else value
