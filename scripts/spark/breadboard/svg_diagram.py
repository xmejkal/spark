"""
The drawn breadboard as a picture (P268, #302): `SvgBreadboardDiagram`, the Renderer of a planned layout as
`breadboard.svg`, the breadboard under the parts in the old wiring page's look (`BoardPalette`, `BoardBackground`,
P953), the Strategies that place a drawn part's pad labels (P945), and the Strategy that gives each jumper its own
lane (P947). Moved out of `drawing`, whose planner and Wokwi diagram it reads. `sheet` writes the file; `part_shape`
names a part's label layout.
"""

import collections
import json
import xml.etree.ElementTree as ElementTree
from pathlib import Path

from spark.breadboard import part_pictures, wire_routing, wiring_steps
from spark.breadboard.drawing import BREADBOARDS_FILE, _round_px
from spark.breadboard.spacing import BodyBox

#: Where a drawn part's pad labels go, the `labels` of its part_px: beside each pad, inside a board's body; or from a
#: row of pads along an edge into the module's body, turned along the column (P945).
LABELS_BESIDE, LABELS_INTO_BODY = "beside", "into-body"


#: Value: where one pad's label goes in the part's own frame: its anchor point, its `text-anchor` and its turn in degrees.
LabelPlace = collections.namedtuple("LabelPlace", "x y anchor rotate")

#: Value: what the dot on a part's pin says, its fill and the legend's words (P949, the praised page's colours).
PadMark = collections.namedtuple("PadMark", "fill words")
#: The states of a pin's dot, in the legend's order: its row joins a wire or another part, its row joins nothing, or
#: something on the board is already wired to it. spark draws no pad held yet: that needs the board record's onboard
#: roles (P950).
PAD_USED, PAD_FREE, PAD_HELD = "used", "free", "held"
PAD_MARKS = {PAD_USED: PadMark("#ffd34d", "pad in use"), PAD_FREE: PadMark("#c9a24b", "pad free"),
             PAD_HELD: PadMark("#5bc0eb", "pad held: do not use")}


class PadLabelLayout:
    """Strategy: where a drawn part's pad label goes, beside its pad, in the part's own frame. `place(x, y, part_px)` gives
    the LabelPlace of the pad at (x, y)."""

    def place(self, x, y, part_px):
        raise NotImplementedError


class BesideLabels(PadLabelLayout):
    """Strategy: a board's pads in two rows down its sides: each label beside its pad, toward the board's middle."""

    def place(self, x, y, part_px):
        inward = x < part_px["center"][0]
        return LabelPlace(x + (5 if inward else -5), y + 2, "start" if inward else "end", 0)


class IntoBodyLabels(PadLabelLayout):
    """Strategy: a module's one row of pads along an edge: each label runs along the pad's column into the body, below a pad on the
    top edge and above one on the bottom edge, turned a quarter so that labels one pitch apart do not overlap."""

    def place(self, x, y, part_px):
        if y < part_px["center"][1]:
            return LabelPlace(x - 2, y + 5, "start", 90)
        return LabelPlace(x - 2, y - 5, "end", 90)


class BoardPalette(collections.namedtuple("BoardPalette", "colors sizes")):
    """Value: the breadboard picture's look (P953): `colors`, {what: hex}, and `sizes`, {what: px}, the `palette` and
    `sizes_px` of data/breadboards.json. Another look is another file, with no code."""

    @classmethod
    def load(cls, path=BREADBOARDS_FILE):
        data = json.loads(Path(path).read_text())
        return cls(data["palette"], data["sizes_px"])


class BoardBackground:
    """
    Renderer helper: the breadboard under the parts, as the old wiring page draws it (P953): the board's body with its
    edge, the gap's band between the two halves, the terminal holes and the rail holes as small squares, each rail's
    line and its + or - sign at its left end, the row letters at the left edge, and the column numbers (1 and every
    `numbers_every`) above the top rails and below the bottom rails. A rail's line lies on the side of its holes away
    from the other rail of its pair, so the two lines frame the pair as on a real board: red outside the + rail, blue
    outside the - rail.
    """

    #: The signs at the left end of a + and a - rail.
    PLUS, MINUS = "+", "−"

    def __init__(self, palette):
        self.palette = palette

    def box(self, surface):
        """The board's body: every hole and `board_pad` round them."""
        pad = self.palette.sizes["board_pad"]
        return BodyBox(min(hole.x for hole in surface.holes) - pad, min(hole.y for hole in surface.holes) - pad,
                       max(hole.x for hole in surface.holes) + pad, max(hole.y for hole in surface.holes) + pad)

    def draw(self, root, surface):
        colors, sizes = self.palette
        box = self.box(surface)
        width, height = str(_round_px(box.right - box.left)), str(_round_px(box.bottom - box.top))
        _element(root, "rect", x=box.left, y=box.top, width=width, height=height, rx=sizes["board_rx"],
                 fill=colors["board"], stroke=colors["edge"], **{"stroke-width": sizes["edge_width"]})
        top, bottom = surface.top_letters, [letter for letter in surface.letters_y if letter not in surface.top_letters]
        middle = (surface.letters_y[top[-1]] + surface.letters_y[bottom[0]]) / 2
        _element(root, "rect", x=box.left, y=middle - sizes["gap_band"] / 2, width=width, height=sizes["gap_band"],
                 fill=colors["gap"])
        rail_holes = [hole for hole in surface.holes if not hole.column]
        for holes, color, size in ((surface.terminal, colors["hole"], sizes["hole"]),
                                   (rail_holes, colors["rail_hole"], sizes["rail_hole"])):
            if holes:
                _element(root, "path", d="".join("M%s %sh0" % (_round_px(hole.x), _round_px(hole.y)) for hole in holes),
                         stroke=color, **{"stroke-width": size, "stroke-linecap": "square"})
        self._rails(root, surface)
        for text, x, y, size in self.texts(surface):
            _element(root, "text", text, x=x, y=y + size * 0.35, fill=colors["grid_text"], **{"font-size": size,
                                                                                            "text-anchor": "middle"})

    def texts(self, surface):
        """(text, x, y of its middle, font size) of each row letter, at the left edge, then each column number (1 and
        every `numbers_every`), above the top rails and below the bottom rails."""
        sizes = self.palette.sizes
        left = min(hole.x for hole in surface.terminal) - surface.pitch
        letters = [(letter, left, y, sizes["letters"]) for letter, y in surface.letters_y.items()]
        columns = sorted({hole.column: hole.x for hole in surface.terminal}.items())
        said = [(column, x) for column, x in columns if column == 1 or column % sizes["numbers_every"] == 0]
        return letters + [(str(column), x, y, sizes["numbers"]) for y in (
            min(hole.y for hole in surface.holes) - surface.pitch, max(hole.y for hole in surface.holes) + surface.pitch)
            for column, x in said]

    def rail_lines(self, surface):
        """(its rail, its holes' y, its line's y, left, right) of each rail: the line lies on the side of its holes away
        from the other rail of its pair."""
        rail_holes = [hole for hole in surface.holes if not hole.column]
        found = []
        for rail in surface.rails:
            row = [hole for hole in rail_holes if hole.group == rail]
            partner = next((hole.y for hole in rail_holes if hole.group != rail and hole.group[0] == rail[0]), None)
            away = (1 if row[0].y > partner else -1) if partner is not None else (-1 if rail.endswith("p") else 1)
            found.append((rail, row[0].y, row[0].y + away * self.palette.sizes["rail_line_off"],
                          min(hole.x for hole in row), max(hole.x for hole in row)))
        return found

    def obstacles(self, surface, bodies):
        """The Obstacles a wire keeps clear of: the board, the `bodies`, each letter's and number's box (0.6 of its
        size wide a character, 0.8 of it high), and each rail's line."""
        marks = [BodyBox(x - 0.3 * size * len(text), y - 0.4 * size, x + 0.3 * size * len(text), y + 0.4 * size)
                 for text, x, y, size in self.texts(surface)]
        return wire_routing.Obstacles(self.box(surface), tuple(bodies), tuple(marks),
                                      tuple((y, left, right) for _, _, y, left, right in self.rail_lines(surface)))

    def _rails(self, root, surface):
        colors, sizes = self.palette
        for rail, row_y, y, left, right in self.rail_lines(surface):
            plus = rail.endswith("p")
            color = colors["plus" if plus else "minus"]
            _element(root, "line", x1=left, y1=y, x2=right, y2=y,
                     stroke=color, **{"stroke-width": sizes["rail_line"], "stroke-opacity": sizes["rail_line_opacity"]})
            _element(root, "text", self.PLUS if plus else self.MINUS, x=left - surface.pitch,
                     y=row_y + sizes["rail_sign"] * 0.35, fill=color,
                     **{"font-size": sizes["rail_sign"], "font-weight": "700", "text-anchor": "middle"})


class SvgBreadboardDiagram:
    """
    Renderer: a BreadboardLayout as an SVG picture in Wokwi's px, for the sheet to show (P268, #302): a white page, the
    breadboard in its `palette`'s look (BoardBackground, P953), each part as its picture at its holes, turned about its measured center as Wokwi turns it, with
    a dot on each pin, used or free (`PAD_MARKS`), and its name, then each jumper on the way its `router` gives it
    (P953: around the parts, on tracks between the holes) as the praised page draws a wire: a white under-stroke, the
    color of what it carries on top and a dot at each end, with its number over the middle of its longest run. A wire
    that needs more bends is drawn dashed, and the note says so, as it says of a wire with no way at all. A part drawn from its record also gets its pad labels, placed by the
    PadLabelLayout its part_px names (`label_layouts`, keyed by the part_px's `labels`). Built with ElementTree, so every text is escaped, and rounded once, so the same layout gives the
    same bytes. The canvas holds the board's body, every part's body and every wire, with MARGIN_PX round them, in Wokwi's px, so
    its view box may start left of or above 0. The root sets the font once. Each jumper's group carries `data-step`, its step's
    number, and each part's group `data-part`, its id, so a player finds them (P949); a key is never an `id`.
    """

    FILE_NAME = "breadboard.svg"
    NOUN = "breadboard picture"
    PURPOSE_MESSAGE = "a picture of the same layout, which breadboard.md shows"
    SHEET_MESSAGE = "![The layout on a breadboard](breadboard.svg)"
    #: The space round the board and every part's body, in px: two pitches, as on the old page.
    MARGIN_PX = 19.2
    #: The room under the holes for each line of the note: the unverified facts of the parts, then the wires', in px.
    NOTE_PX = 14
    #: The one font of every text spark writes, set on the root.
    FONT = "Helvetica,Arial,sans-serif"
    #: A wire's sizes, in px: the white under-stroke, the colored stroke, and the end dot with its white ring. The
    #: praised page's 7.5 and 4 are for its 18 px pitch; these fit spark's 9.6 px one.
    UNDER_STROKE_PX, WIRE_STROKE_PX, END_DOT_PX, END_RING_PX = 5, 2.5, 3, 1

    #: The dashes of a wire that needs more bends than a wire may have.
    DASHES = "4 2"
    #: What the note says of the wires drawn dashed, and of the wires not drawn, filled with their numbers.
    DASHED_NOTE = ("wire %s bends more than 4 times to go around the parts and is drawn dashed",
                   "wires %s bend more than 4 times to go around the parts and are drawn dashed")
    NOT_DRAWN_NOTE = ("wire %s finds no way around the parts and is not drawn", "wires %s find no way around the parts "
                      "and are not drawn")

    def __init__(self, colors=None, pictures=None, label_layouts=None, router=None, palette=None):
        self.colors = colors or wiring_steps.JumperColors()
        self.router = router or wire_routing.TrackJumperRouter()
        self.pictures = pictures or part_pictures.PictogramPartPictures()
        self.label_layouts = label_layouts or {LABELS_BESIDE: BesideLabels(), LABELS_INTO_BODY: IntoBodyLabels()}
        self.palette = palette or BoardPalette.load()

    def why_not_written(self, layout):
        """None: the picture is written for any layout."""
        return None

    def text(self, layout):
        ElementTree.register_namespace("", part_pictures.SVG_NAMESPACE)
        surface = layout.geometry.surface
        pictures = {part.id: self.pictures.picture(part.type, part.record) for part in layout.parts}
        background = BoardBackground(self.palette)
        # a body may hang past the holes (a module seated by one edge, a board's USB end): the canvas holds it
        boxes = [background.box(surface)] + [BodyBox.of(part, layout.geometry.part(part.type)) for part in layout.parts]
        paths = self.router.route(layout, background.obstacles(surface, boxes[1:]))
        boxes += [BodyBox(min(x for x, _ in path.points), min(y for _, y in path.points), max(x for x, _ in path.points),
                          max(y for _, y in path.points)) for path in paths.values() if path.points]
        notes = [", ".join(said) for said in (self._notes(layout, pictures), self._wire_notes(paths)) if said]
        left, top = min(box.left for box in boxes) - self.MARGIN_PX, min(box.top for box in boxes) - self.MARGIN_PX
        width = _round_px(max(box.right for box in boxes) + self.MARGIN_PX - left)
        height = _round_px(max(box.bottom for box in boxes) + self.MARGIN_PX - top + self.NOTE_PX * len(notes))
        left, top = _round_px(left), _round_px(top)
        root = ElementTree.Element(_svg("svg"), {"width": str(width), "height": str(height),
                                                   "viewBox": "%s %s %s %s" % (left, top, width, height),
                                                   "font-family": self.FONT})
        _element(root, "rect", x=left, y=top, width=width, height=height, fill=self.palette.colors["page"])
        background.draw(root, surface)
        for part in layout.parts:
            self._part(root, part, layout.geometry, pictures[part.id])
        self._wires(root, layout, paths)
        joined = self._joined_groups(layout)
        for part in layout.parts:
            self._label(root, part, layout.geometry, joined)  # last, so no wire or other part covers a pin or a name
        for index, line in enumerate(notes):  # the parts' notes, then the wires'
            note = ElementTree.SubElement(root, _svg("text"), {
                "x": str(_round_px(left + self.MARGIN_PX)),
                "y": str(_round_px(top + height - 4 - self.NOTE_PX * (len(notes) - 1 - index))), "font-size": "8",
                "fill": "#5d4037"})
            note.text = line
        return ElementTree.tostring(root, encoding="unicode") + "\n"

    @staticmethod
    def _notes(layout, pictures):
        """The note line's sentences: each drawn part's unverified groups, then each picture's own note (P946)."""
        return [note["sentence"] for part in layout.parts for note in layout.geometry.part(part.type).get("notes", [])] + [
            picture.note for picture in pictures.values() if picture.note]

    @staticmethod
    def _turn(part, part_px):
        """The transform that puts a part's own frame where Wokwi shows it: moved to its corner, turned about its center."""
        cx, cy = part_px["center"]
        return "translate(%s %s) rotate(%s %s %s)" % (_round_px(part.left), _round_px(part.top), part.rotate,
                                                      _round_px(cx), _round_px(cy))

    def _part(self, root, part, geometry, picture):
        part_px = geometry.part(part.type)
        group = ElementTree.SubElement(root, _svg("g"), {"transform": self._turn(part, part_px), "data-part": part.id})
        width, height = part_px["size"]
        x, y, view_width, view_height = picture.view_box
        inner = ElementTree.SubElement(group, _svg("g"), {"transform": "scale(%s %s) translate(%s %s)" % (
            _round_px(width / view_width), _round_px(height / view_height), _round_px(-x), _round_px(-y))})
        for child in ElementTree.fromstring('<g xmlns="%s">%s</g>' % (part_pictures.SVG_NAMESPACE, picture.markup)):
            inner.append(child)
        if picture.credit:
            ElementTree.SubElement(group, _svg("title")).text = picture.credit

    def _pad_labels(self, root, part, part_px):
        """A part drawn from its record (P412, P945): each pad's label where its PadLabelLayout puts it, a dashed ring on a
        doubtful pad, and on a board a mark at the USB end (named in no word, since its place is not verified). Drawn in
        the part's own frame, so it turns with the part."""
        cx, _ = part_px["center"]
        height = part_px["size"][1]
        layout = self.label_layouts[part_px.get("labels", LABELS_BESIDE)]
        group = ElementTree.SubElement(root, _svg("g"), {"transform": self._turn(part, part_px)})
        for pad, (x, y) in part_px["pins"].items():
            if pad in part_px["doubtful"]:
                ElementTree.SubElement(group, _svg("circle"), {
                    "cx": str(_round_px(x)), "cy": str(_round_px(y)), "r": "4", "fill": "none", "stroke": "#e65100",
                    "stroke-width": "1", "stroke-dasharray": "2 1.5"})
            place = layout.place(x, y, part_px)
            attributes = {"x": str(_round_px(place.x)), "y": str(_round_px(place.y)), "font-size": "6",
                          "text-anchor": place.anchor, "fill": "#ffffff",
                          "stroke": "#0d47a1", "stroke-width": "1.5", "paint-order": "stroke"}
            if place.rotate:
                attributes["transform"] = "rotate(%s %s %s)" % (place.rotate, _round_px(place.x), _round_px(place.y))
            ElementTree.SubElement(group, _svg("text"), attributes).text = pad
        if part_px.get("usb_mark"):
            ElementTree.SubElement(group, _svg("rect"), {
                "x": str(_round_px(cx - 17)), "y": str(_round_px(height - 12)), "width": "34", "height": "12", "rx": "3",
                "fill": "#cfd8dc", "stroke": "#455a64", "stroke-width": "1"})

    @staticmethod
    def _joined_groups(layout):
        """The hole groups that join something: the group of each jumper's end, and each group with pins of two parts."""
        parts_in = collections.defaultdict(set)
        for part in layout.parts:
            for hole in part.holes.values():
                parts_in[hole.group].add(part.id)
        ends = {hole.group for jumper in layout.jumpers for hole in (jumper.one, jumper.other)}
        return ends | {group for group, parts in parts_in.items() if len(parts) > 1}

    def _label(self, root, part, geometry, joined):
        part_px = geometry.part(part.type)
        if part_px.get("pad_labels"):
            self._pad_labels(root, part, part_px)
        for hole in part.holes.values():
            state = PAD_USED if hole.group in joined else PAD_FREE
            ElementTree.SubElement(root, _svg("circle"), {"cx": str(_round_px(hole.x)), "cy": str(_round_px(hole.y)),
                                                          "r": "2.5", "fill": PAD_MARKS[state].fill, "stroke": "#20262b",
                                                          "stroke-width": "0.6", "data-pad": state})
        cx, cy = part_px["center"]
        label = ElementTree.SubElement(root, _svg("text"), {
            "x": str(_round_px(part.left + cx)), "y": str(_round_px(part.top + cy)), "font-size": "8",
            "text-anchor": "middle", "fill": "#1a1a1a", "stroke": "#ffffff",
            "stroke-width": "2.5", "paint-order": "stroke"})
        label.text = part_px.get("name") or part.id

    def _wire_notes(self, paths):
        """The note's sentences of the wires drawn dashed and of the wires not drawn, each by its step's number."""
        said = []
        for fallback, words in ((wire_routing.BENDS, self.DASHED_NOTE), (wire_routing.NO_WAY, self.NOT_DRAWN_NOTE)):
            steps = sorted(step for step, path in paths.items() if path.fallback == fallback)
            if steps:
                numbers = ", ".join(map(str, steps[:-1])) + " and %d" % steps[-1] if len(steps) > 1 else str(steps[0])
                said.append(words[len(steps) > 1] % numbers)
        return said

    def _wires(self, root, layout, paths):
        """Each jumper on its way and in its color, then every step number, over every wire so that none hides one."""
        colors = self.colors.of({jumper.step: jumper.role for jumper in layout.jumpers})
        for jumper in layout.jumpers:
            self._jumper(root, jumper, paths[jumper.step], colors[jumper.step])
        for jumper in layout.jumpers:
            if paths[jumper.step].points:
                self._number(root, jumper, paths[jumper.step], colors[jumper.step])

    def _jumper(self, root, jumper, path, color):
        """One jumper as one group: its way from its first hole to its other, drawn twice (white under, its color on top,
        dashed when it bends more than a wire may), with a dot at each end. A jumper with no way gets its dots alone."""
        group = ElementTree.SubElement(root, _svg("g"), {"class": "wire", "data-step": str(jumper.step)})
        route = "M" + "L".join("%s %s" % point for point in path.points)
        for stroke, width in (("#ffffff", self.UNDER_STROKE_PX), (color, self.WIRE_STROKE_PX)) if path.points else ():
            drawn = ElementTree.SubElement(group, _svg("path"), {
                "d": route, "fill": "none", "stroke": stroke, "stroke-width": str(width), "stroke-linecap": "round",
                "stroke-linejoin": "round"})
            if path.fallback and stroke == color:
                drawn.set("stroke-dasharray", self.DASHES)
        for hole in (jumper.one, jumper.other):
            ElementTree.SubElement(group, _svg("circle"), {
                "cx": str(_round_px(hole.x)), "cy": str(_round_px(hole.y)), "r": str(self.END_DOT_PX), "fill": color,
                "stroke": "#ffffff", "stroke-width": str(self.END_RING_PX)})

    @staticmethod
    def _number(root, jumper, path, color):
        """A jumper's step number over the middle of its longest run, with a white halo: just above a run across, just
        beside one along a column."""
        (x1, y1), (x2, y2) = max(zip(path.points, path.points[1:]),
                                 key=lambda piece: abs(piece[1][0] - piece[0][0]) + abs(piece[1][1] - piece[0][1]))
        across = y1 == y2
        number = ElementTree.SubElement(root, _svg("text"), {
            "x": str(_round_px((x1 + x2) / 2 + (0 if across else 3))),
            "y": str(_round_px((y1 + y2) / 2 + (-3 if across else 3))), "font-size": "9", "font-weight": "bold",
            "text-anchor": "middle" if across else "start", "fill": color,
            "stroke": "#ffffff", "stroke-width": "2.5", "paint-order": "stroke"})
        number.text = str(jumper.step)


def _svg(tag):
    return "{%s}%s" % (part_pictures.SVG_NAMESPACE, tag)


def _element(parent, tag, text=None, **attributes):
    """One SVG element under `parent`, each number rounded once (`_round_px`), with its text when it has one."""
    element = ElementTree.SubElement(parent, _svg(tag), {
        key: str(_round_px(value)) if isinstance(value, (int, float)) else value for key, value in attributes.items()})
    if text is not None:
        element.text = text
    return element
