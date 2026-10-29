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
import xml.etree.ElementTree as ElementTree
from pathlib import Path

import breadboard_steps
import part_pictures

WOKWI_GEOMETRY_FILE = Path(__file__).resolve().parent.parent / "data" / "wokwi-geometry.json"

#: Value: one hole, its Wokwi name (12t.a, tp.3), its center in px, its group (the holes joined with it inside the
#: board: a breadboard row such as 12t, or a rail such as tp), and its column (from 1; a rail hole has none, 0).
Hole = collections.namedtuple("Hole", "name x y group column")
#: What the planner draws for one component: its Wokwi type and attrs, and {its pin as the steps name it: Wokwi pin}.
DrawnPart = collections.namedtuple("DrawnPart", "type attrs pins")
#: One component on the breadboard: its id, type, attrs, top-left corner in px, its turn, and {Wokwi pin: Hole}.
PlacedPart = collections.namedtuple("PlacedPart", "id type attrs left top rotate holes")
#: One jumper between two holes, drawn in the color of the step it belongs to, with the bends of its route as Wokwi
#: writes them (strings such as "v-20"), empty when it runs straight.
Jumper = collections.namedtuple("Jumper", "one other step route", defaults=((),))
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

    def __init__(self, surface, taken=None):
        self.surface = surface
        self.taken = dict(taken or {})

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

    def reserve_first(self, ledger):
        """Called once, with the plan's ledger, before the first part is placed. A strategy that keeps parts where an
        earlier plan put them claims their holes here. The default claims nothing."""

    def place(self, part_id, drawn, ledger, after=0, pinned=None):
        raise NotImplementedError


class JumperPlacement:
    """Strategy: which holes the jumpers take, once the parts are placed and each jumper has its two rows."""

    def place_jumpers(self, layout, ledger):
        """The layout with its jumpers' holes chosen. `ledger` holds the holes the parts take and no jumper's. The
        default keeps the holes the planner took."""
        return layout


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
        part_px = self.geometry.part(drawn.type)
        wanted = [pin for pin in drawn.pins.values() if pin not in part_px["pins"]]
        if wanted:
            raise NotDrawn("data/wokwi-geometry.json has no pin %s on %s" % (wanted[0], drawn.type))
        for degrees in self.TURNS_DEGREES:
            turned = rotate(part_px["pins"], part_px["center"], degrees)
            first = pinned[0] if pinned else next(iter(turned))
            candidates = [hole for hole in self.geometry.surface.by_gap if not pinned or hole.group == pinned[1]]
            for start in candidates:
                left, top = start.x - turned[first][0], start.y - turned[first][1]
                holes = self._fit(turned, left, top, ledger, after, pinned)
                if holes is None:
                    continue
                covered = self._covered(part_px, degrees, left, top, holes) if part_px.get("covers_holes") else []
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

    def _covered(self, part_px, degrees, left, top, holes):
        """The holes under the part's body, besides its own pins: its box, turned, about its center."""
        cx, cy = part_px["center"]
        half_w, half_h = (cy, cx) if degrees % 180 else (cx, cy)
        mine = {hole.name for hole in holes.values()}
        return [hole for hole in self.geometry.surface.terminal if hole.name not in mine
                and abs(hole.x - (left + cx)) < half_w and abs(hole.y - (top + cy)) < half_h]


class BreadboardPlanner:
    """Pure: the steps, the geometry and what to draw for each component in, a BreadboardLayout out."""

    #: Columns from one part's last pin to the next part's first: one empty column between them, for the jumpers.
    SPACING_COLUMNS = 2

    def __init__(self, geometry, catalog, placement=None, jumper_placement=None):
        self.geometry = geometry
        self.catalog = catalog
        self.placement = placement or FirstFitPartPlacement(geometry)
        self.jumper_placement = jumper_placement or JumperPlacement()

    def plan(self, steps):
        """Each part placed in step order, then each resistor with a leg in the row it joins, then each jumper."""
        ledger = HoleLedger(self.geometry.surface)
        self.placement.reserve_first(ledger)
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
        parts_only = HoleLedger(self.geometry.surface, ledger.taken)
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
        return self.jumper_placement.place_jumpers(
            BreadboardLayout(self.geometry.surface.type, list(placed.values()), jumpers), parts_only)

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
                joined = [(self._pin(end), self._group_of(anchor, placed, {})) for end, anchor in pinned]
                placed[component] = self.placement.place(component, drawn, ledger, after if not joined else 0,
                                                         joined[0] if joined else None)
            waiting = [one for one in waiting if one[0] not in placed]

    def _drawn(self, component):
        return drawn_part(component, self.catalog)

    def _group_of(self, end, placed, groups):
        return end_group(end, placed, self.catalog, groups)

    def _pin(self, end):
        return end_pin(end, self.catalog)


def drawn_part(component, catalog):
    """What the catalog draws for one component, or NotDrawn naming it."""
    drawn = catalog.get(component)
    if drawn is None:
        raise NotDrawn("nothing says how to draw %s in Wokwi" % component)
    return drawn


def end_pin(end, catalog):
    """The Wokwi pin of one end, or NotDrawn naming it."""
    pin = drawn_part(end.component, catalog).pins.get(end.pin)
    if pin is None:
        raise NotDrawn("which Wokwi pin is %s is not known" % end.name)
    return pin


def end_group(end, placed, catalog, groups=None):
    """The group an end sits in: its pin's group, or the free group its board pad's jumper took (`groups`, which the
    planner fills as it draws). The planner and the drawing check (`breadboard_match`) both ask it."""
    if groups and end.name in groups:
        return groups[end.name]
    if end.component not in placed:
        raise NotDrawn("%s is joined before it is placed" % end.name)
    return placed[end.component].holes[end_pin(end, catalog)].group


class WokwiBreadboardDiagram:
    """Renderer: a BreadboardLayout as a Wokwi diagram, each jumper in its step's color. Its constructor takes the
    colors, so the sheet and the diagram share one palette. Every drawing renderer has the four class attributes
    below and `text(layout)`, which `breadboard.DRAWING_RENDERERS` and the build read."""

    #: The file it writes, beside the sheet.
    FILE_NAME = "breadboard.json"
    #: What the build calls the file in a line that says it was not written or was removed.
    NOUN = "drawn breadboard"
    #: What the build says beside the file's path when it wrote it.
    PURPOSE_MESSAGE = "an example layout of the steps on a breadboard: paste it into a new project on wokwi.com"
    #: What the sheet says about the file, under its steps.
    SHEET_MESSAGE = ("An example layout is in breadboard.json: paste it into the diagram.json of a new project on "
                     "wokwi.com.")

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
                        jumper.other.name), self.colors.color(jumper.step), list(jumper.route)] for jumper in layout.jumpers]
        return {"version": 1, "author": "spark", "editor": "wokwi", "parts": parts, "connections": connections,
                "dependencies": {}}

    def text(self, layout):
        """The diagram as the file holds it: the same layout gives the same bytes."""
        return json.dumps(self.render(layout), indent=2, ensure_ascii=False) + "\n"


def _round_px(value):
    """A position as the file holds it: rounded once, here, and whole when it is whole."""
    value = round(value, 3)
    return int(value) if value == int(value) else value


class SvgBreadboardDiagram:
    """
    Renderer: a BreadboardLayout as an SVG picture in Wokwi's px, for the sheet to show (P268, #302): the breadboard's
    holes and rails, each part as its picture at its holes, turned about its measured center as Wokwi turns it, with
    a dot on each pin and its id, then each jumper as a line in its step's color with its number. Built with
    ElementTree, so every text is escaped, and rounded once, so the same layout gives the same bytes.
    """

    FILE_NAME = "breadboard.svg"
    NOUN = "breadboard picture"
    PURPOSE_MESSAGE = "a picture of the same layout, which breadboard.md shows"
    SHEET_MESSAGE = "![The layout on a breadboard](breadboard.svg)"
    #: The space around the outermost holes, in px.
    MARGIN_PX = 14

    def __init__(self, geometry, colors=None, pictures=None):
        self.geometry = geometry
        self.colors = colors or breadboard_steps.StepColors()
        self.pictures = pictures or part_pictures.PictogramPartPictures()

    def text(self, layout):
        ElementTree.register_namespace("", part_pictures.SVG_NAMESPACE)
        surface = self.geometry.surface
        width = _round_px(max(hole.x for hole in surface.holes) + 2 * self.MARGIN_PX)
        height = _round_px(max(hole.y for hole in surface.holes) + self.MARGIN_PX)
        root = ElementTree.Element(_svg("svg"), {"width": str(width), "height": str(height),
                                                   "viewBox": "0 0 %s %s" % (width, height)})
        ElementTree.SubElement(root, _svg("rect"), {"width": str(width), "height": str(height), "rx": "6",
                                                    "fill": "#f4f4f4"})
        holes = "".join("M%s %sh0" % (_round_px(hole.x), _round_px(hole.y)) for hole in surface.holes)
        ElementTree.SubElement(root, _svg("path"), {"d": holes, "stroke": "#a8a8a8", "stroke-width": "3.5",
                                                    "stroke-linecap": "round"})
        for rail in surface.rails:
            row = [hole for hole in surface.holes if hole.group == rail]
            # a red line above each + rail and a blue one below each - rail, as Wokwi draws them
            first, last = min(hole.x for hole in row), max(hole.x for hole in row)
            outer = -1 if rail.endswith("p") else 1
            y = _round_px(row[0].y + outer * 5)
            ElementTree.SubElement(root, _svg("line"), {"x1": str(_round_px(first)), "y1": str(y),
                                                        "x2": str(_round_px(last)), "y2": str(y), "stroke-width": "1",
                                                        "stroke": "#e53935" if rail.endswith("p") else "#1e88e5"})
        for part in layout.parts:
            self._part(root, part)
        for jumper in layout.jumpers:
            self._jumper(root, jumper)
        for part in layout.parts:
            self._label(root, part)  # last, so no wire or other part covers a pin or a name
        return ElementTree.tostring(root, encoding="unicode") + "\n"

    def _part(self, root, part):
        part_px = self.geometry.part(part.type)
        picture = self.pictures.picture(part.type)
        cx, cy = part_px["center"]
        group = ElementTree.SubElement(root, _svg("g"), {
            "transform": "translate(%s %s) rotate(%s %s %s)" % (_round_px(part.left), _round_px(part.top),
                                                                part.rotate, _round_px(cx), _round_px(cy))})
        width, height = part_px["size"]
        x, y, view_width, view_height = picture.view_box
        inner = ElementTree.SubElement(group, _svg("g"), {"transform": "scale(%s %s) translate(%s %s)" % (
            _round_px(width / view_width), _round_px(height / view_height), _round_px(-x), _round_px(-y))})
        for child in ElementTree.fromstring('<g xmlns="%s">%s</g>' % (part_pictures.SVG_NAMESPACE, picture.markup)):
            inner.append(child)
        if picture.credit:
            ElementTree.SubElement(group, _svg("title")).text = picture.credit

    def _label(self, root, part):
        for hole in part.holes.values():
            ElementTree.SubElement(root, _svg("circle"), {"cx": str(_round_px(hole.x)), "cy": str(_round_px(hole.y)),
                                                          "r": "2.5", "fill": "#2e7d32"})
        cx, cy = self.geometry.part(part.type)["center"]
        label = ElementTree.SubElement(root, _svg("text"), {
            "x": str(_round_px(part.left + cx)), "y": str(_round_px(part.top + cy)), "font-size": "8",
            "font-family": "sans-serif", "text-anchor": "middle", "fill": "#1a1a1a", "stroke": "#ffffff",
            "stroke-width": "2.5", "paint-order": "stroke"})
        label.text = part.id

    def _jumper(self, root, jumper):
        """One jumper along the holes: out of its first hole along the column, across between two rows of holes, and
        into its last hole. Its bends sit half a pitch off the holes, so no bend looks like a joint with a hole of
        another group."""
        color = self.colors.color(jumper.step)
        one, other = jumper.one, jumper.other
        half = self.geometry.data["breadboard"]["pitch"] / 2
        across = other.y - half if other.y > one.y else other.y + half
        ElementTree.SubElement(root, _svg("path"), {
            "d": "M%s %sL%s %sL%s %sL%s %s" % (
                _round_px(one.x), _round_px(one.y), _round_px(one.x), _round_px(across), _round_px(other.x),
                _round_px(across), _round_px(other.x), _round_px(other.y)),
            "fill": "none", "stroke": color, "stroke-width": "2.5", "stroke-linecap": "round",
            "stroke-linejoin": "round"})
        number = ElementTree.SubElement(root, _svg("text"), {
            "x": str(_round_px(one.x + 3)), "y": str(_round_px(across - 2)), "font-size": "9",
            "font-family": "sans-serif", "font-weight": "bold", "fill": color})
        number.text = str(jumper.step)


def _svg(tag):
    return "{%s}%s" % (part_pictures.SVG_NAMESPACE, tag)
