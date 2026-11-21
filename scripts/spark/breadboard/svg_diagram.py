"""
The drawn breadboard as a picture (P268, #302): `SvgBreadboardDiagram`, the Renderer of a planned layout as
`breadboard.svg`, the breadboard under the parts in the old wiring page's look (`BoardBackground`, which draws
the holes and the gap band from the surface, and the marks that `board_marks` made, P969, with their `BoardPalette`, P953), the
Strategies that place a drawn part's pad labels (P945), and each jumper's pill, which `wire_pills` places and draws no
picture of (P969, `PillLayout`, `WirePill`, P953). Moved out of `drawing`, whose planner and Wokwi diagram it reads.
`sheet` writes the file; `part_shape` names a part's label layout; `wire_routing` gives each jumper its way; `part_captions` places each part's
caption and writes its line of the note.
"""

import collections
import math
import xml.etree.ElementTree as ElementTree

from spark.breadboard import part_pictures, wire_routing, wiring_steps
from spark.breadboard.board_marks import BoardMarks, BoardPalette
from spark.breadboard.drawing import _round_px
from spark.breadboard.part_captions import PartCaption, PartNotes
from spark.breadboard.spacing import BodyBox
from spark.breadboard.wire_pills import WIRE_SIZES_PX, PillLayout, wire_boxes

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
    """Strategy: where a drawn part's pad label goes, beside its pad, in the part's own frame. `place(x, y, part_px, turn)`
    gives the LabelPlace of the pad at (x, y) of a part turned by `turn` degrees on the sheet. One reading direction
    (P953): a label's own turn plus the part's is 0 or -90, so every turned label reads bottom to top; a place that would
    read the other way is turned half round about the middle of its letters, its anchor flipped."""

    #: How far a label's baseline lies from the middle of its letters, across its text, in px.
    MIDDLE = 2

    def place(self, x, y, part_px, turn):
        place = self._place(x, y, part_px)
        if (turn + place.rotate) % 360 in (0, 270):
            return place
        radians = math.radians(place.rotate)
        up_x, up_y = round(math.sin(radians)), -round(math.cos(radians))  # the text's up, in the part's frame
        return LabelPlace(place.x + 2 * self.MIDDLE * up_x, place.y + 2 * self.MIDDLE * up_y,
                          {"start": "end", "end": "start"}[place.anchor], place.rotate - 180)

    def _place(self, x, y, part_px):
        """The LabelPlace in the part's frame, before the reading direction."""
        raise NotImplementedError


class BesideLabels(PadLabelLayout):
    """Strategy: a board's pads in two rows down its sides: each label beside its pad, toward the board's middle."""

    def _place(self, x, y, part_px):
        inward = x < part_px["center"][0]
        return LabelPlace(x + (5 if inward else -5), y + self.MIDDLE, "start" if inward else "end", 0)


class IntoBodyLabels(PadLabelLayout):
    """Strategy: a module's one row of pads along an edge: each label runs along the pad's column into the body, below a pad on the
    top edge and above one on the bottom edge, turned a quarter so that labels one pitch apart do not overlap."""

    def _place(self, x, y, part_px):
        if y < part_px["center"][1]:
            return LabelPlace(x + self.MIDDLE, y + 5, "end", -90)
        return LabelPlace(x + self.MIDDLE, y - 5, "start", -90)


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

    def marks(self, surface):
        """The BoardMarks of the surface at this palette's sizes."""
        return BoardMarks(surface, self.palette.sizes)

    def draw(self, root, surface):
        colors, sizes = self.palette
        marks = self.marks(surface)
        box = marks.box()
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
        self._rails(root, marks)
        for text, x, y, size in marks.texts():
            _element(root, "text", text, x=x, y=y + size * 0.35, fill=colors["grid_text"], **{"font-size": size,
                                                                                            "text-anchor": "middle"})

    def _rails(self, root, marks):
        colors, sizes = self.palette
        for (rail, _, y, left, right), (_, x, baseline) in zip(marks.rail_lines(), marks.signs()):
            plus = rail.endswith("p")
            color = colors["plus" if plus else "minus"]
            _element(root, "line", x1=left, y1=y, x2=right, y2=y,
                     stroke=color, **{"stroke-width": sizes["rail_line"], "stroke-opacity": sizes["rail_line_opacity"]})
            _element(root, "text", self.PLUS if plus else self.MINUS, x=x, y=baseline, fill=color,
                     **{"font-size": sizes["rail_sign"], "font-weight": "700", "text-anchor": "middle"})


class SvgBreadboardDiagram:
    """
    Renderer: a BreadboardLayout as an SVG picture in Wokwi's px, for the sheet to show (P268, #302): a white page, the
    breadboard in its `palette`'s look (BoardBackground, P953), each part as its picture at its holes, turned about its measured center as Wokwi turns it, with
    a dot on each pin, used or free (`PAD_MARKS`), and its caption outside its body (PartCaption), then each jumper on the way its `router` gives it
    (P953: around the parts, on tracks between the holes) as the praised page draws a wire: a white under-stroke, the
    color of what it carries on top (its word in `palette`'s `wires`) and a dot at each end, with its pill where
    PillLayout puts it: its step's number and the two pads it joins (WirePill). A wire
    that needs more bends is drawn dashed, and the note says so, as it says of a wire with no way at all. A part drawn from its record also gets its pad labels, placed by the
    PadLabelLayout its part_px names (`label_layouts`, keyed by the part_px's `labels`), each in the steps' words and
    read bottom to top. The note under the picture holds a line per part (PartNotes), then the wires'. Built with ElementTree, so every text is escaped, and rounded once, so the same layout gives the
    same bytes. The canvas holds the board's body, every part's body, every wire, every pill and every caption, with MARGIN_PX round them, in Wokwi's px, so
    its view box may start left of or above 0. The root sets the font once. Each jumper's group carries `data-step`, its step's
    number, and holds its pill; each part's group carries `data-part`, its id, so a player finds them (P949); a key is never an `id`.
    """

    FILE_NAME = "breadboard.svg"
    NOUN = "breadboard picture"
    PURPOSE_MESSAGE = "a picture of the same layout, which breadboard.md shows"
    SHEET_MESSAGE = "![The layout on a breadboard](breadboard.svg)"
    #: The space round the board and every part's body, in px: two pitches, as on the old page.
    MARGIN_PX = 19.2
    #: The room under the holes for each line of the note, a pitch: the unverified facts of each part, then the wires',
    #: in px.
    NOTE_PX = 9.6
    #: The one font of every text spark writes, set on the root.
    FONT = "Helvetica,Arial,sans-serif"
    #: The word of a pad with no net, whose label is drawn muted.
    NO_NET = "NC"
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
        self.pill_layout = PillLayout(WIRE_SIZES_PX.under_stroke, WIRE_SIZES_PX.end_dot + WIRE_SIZES_PX.end_ring / 2)

    def why_not_written(self, layout):
        """None: the picture is written for any layout."""
        return None

    def text(self, layout):
        ElementTree.register_namespace("", part_pictures.SVG_NAMESPACE)
        surface = layout.geometry.surface
        pictures = {part.id: self.pictures.picture(part.type, part.record) for part in layout.parts}
        background = BoardBackground(self.palette)
        marks = background.marks(surface)
        # a body may hang past the holes (a module seated by one edge, a board's USB end): the canvas holds it
        boxes = [marks.box()] + [BodyBox.of(part, layout.geometry.part(part.type)) for part in layout.parts]
        obstacles = marks.obstacles(boxes[1:])
        paths = self.router.route(layout, obstacles)
        pills = self.pill_layout.place(layout.jumpers, paths,
                                       obstacles._replace(marks=obstacles.marks + marks.sign_boxes()))
        captions = PartCaption(self.palette.sizes["caption"], surface.pitch).place(layout.parts, boxes[1:], boxes[1:] + list(
            obstacles.marks + marks.sign_boxes()) + wire_boxes(layout.jumpers, paths, pills))
        boxes += [BodyBox(min(x for x, _ in path.points), min(y for _, y in path.points), max(x for x, _ in path.points),
                          max(y for _, y in path.points)) for path in paths.values() if path.points]
        boxes += [pill.box() for pill in pills.values()] + [caption.box() for caption in captions.values()]
        wired = self._wire_notes(paths)
        notes = PartNotes.lines(layout, pictures) + ([", ".join(wired)] if wired else [])
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
        self._wires(root, layout, paths, pills)
        joined = self._joined_groups(layout)
        for part in layout.parts:
            self._label(root, part, layout.geometry, joined)  # last, so no wire or other part covers a pin
        self._words(root, captions, notes, (left + self.MARGIN_PX, top + height))
        return ElementTree.tostring(root, encoding="unicode") + "\n"

    def _words(self, root, captions, notes, corner):
        """Each part's caption, its record's name in the title colour or an id muted, then the note's lines up from the
        canvas's bottom left `corner`, its margin in: the parts' lines, then the wires'."""
        colors, sizes = self.palette
        for caption in captions.values():
            _element(root, "text", caption.words, x=caption.x, y=caption.y,
                     fill=colors["title" if caption.named else "grid_text"],
                     **{"class": "caption", "font-size": caption.size, "font-weight": PartCaption.WEIGHT})
        for index, line in enumerate(notes):
            _element(root, "text", line, x=corner[0], y=corner[1] - 4 - self.NOTE_PX * (len(notes) - 1 - index),
                     fill=colors["grid_text"], **{"class": "note", "font-size": sizes["note"]})

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

    def _pad_labels(self, root, part, part_px, used):
        """A part drawn from its record (P412, P945): each pad's label where its PadLabelLayout puts it, a dashed ring on a
        doubtful pad, and on a board a mark at the USB end (named in no word, since its place is not verified). Drawn in
        the part's own frame, so it turns with the part. A label says the pad in the steps' words
        (`wiring_steps.pad_word`, P953): bold yellow on a pad in `used`, muted on a pad with no net (NC), else dim, each
        with the palette's thin dark outline."""
        cx, _ = part_px["center"]
        height = part_px["size"][1]
        colors, sizes = self.palette
        layout = self.label_layouts[part_px.get("labels", LABELS_BESIDE)]
        group = ElementTree.SubElement(root, _svg("g"), {"transform": self._turn(part, part_px), "class": "pad-labels"})
        for pad, (x, y) in part_px["pins"].items():
            if pad in part_px["doubtful"]:
                ElementTree.SubElement(group, _svg("circle"), {
                    "cx": str(_round_px(x)), "cy": str(_round_px(y)), "r": "4", "fill": "none", "stroke": "#e65100",
                    "stroke-width": "1", "stroke-dasharray": "2 1.5"})
            place, word = layout.place(x, y, part_px, part.rotate), wiring_steps.pad_word(pad)
            look = {"font-size": sizes["pad_label_used"], "font-weight": "700", "fill": colors["pad_used"]} if pad in used else {
                "font-size": sizes["pad_label"], "fill": colors["pad_none" if word == self.NO_NET else "pad_free"]}
            label = _element(group, "text", word, x=place.x, y=place.y, stroke=colors["pad_halo"], **dict(
                look, **{"text-anchor": place.anchor, "stroke-width": sizes["pad_halo"], "paint-order": "stroke"}))
            if place.rotate:
                label.set("transform", "rotate(%s %s %s)" % (place.rotate, _round_px(place.x), _round_px(place.y)))
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
        """A part's pad labels, when it is drawn from its record, and the dot on each of its pins, used or free."""
        part_px = geometry.part(part.type)
        if part_px.get("pad_labels"):
            self._pad_labels(root, part, part_px, {pin for pin, hole in part.holes.items() if hole.group in joined})
        for hole in part.holes.values():
            state = PAD_USED if hole.group in joined else PAD_FREE
            ElementTree.SubElement(root, _svg("circle"), {"cx": str(_round_px(hole.x)), "cy": str(_round_px(hole.y)),
                                                          "r": "2.5", "fill": PAD_MARKS[state].fill, "stroke": "#20262b",
                                                          "stroke-width": "0.6", "data-pad": state})

    def _wire_notes(self, paths):
        """The note's sentences of the wires drawn dashed and of the wires not drawn, each by its step's number."""
        said = []
        for fallback, words in ((wire_routing.BENDS, self.DASHED_NOTE), (wire_routing.NO_WAY, self.NOT_DRAWN_NOTE)):
            steps = sorted(step for step, path in paths.items() if path.fallback == fallback)
            if steps:
                numbers = ", ".join(map(str, steps[:-1])) + " and %d" % steps[-1] if len(steps) > 1 else str(steps[0])
                said.append(words[len(steps) > 1] % numbers)
        return said

    def _wires(self, root, layout, paths, pills):
        """Each jumper on its way, its color's word drawn in the palette's hex (`wires`), with its pill."""
        hexes = self.palette.colors["wires"]
        colors = self.colors.of({jumper.step: jumper.role for jumper in layout.jumpers})
        for jumper in layout.jumpers:
            self._jumper(root, jumper, paths[jumper.step], hexes[colors[jumper.step]], pills[jumper.step])

    def _jumper(self, root, jumper, path, color, pill):
        """One jumper as one group: its way from its first hole to its other, drawn twice (white under, its color on top,
        dashed when it bends more than a wire may), with a dot at each end, then its pill. A jumper with no way gets its
        dots and its pill alone."""
        group = ElementTree.SubElement(root, _svg("g"), {"class": "wire", "data-step": str(jumper.step)})
        route = "M" + "L".join("%s %s" % point for point in path.points)
        for stroke, width in (("#ffffff", WIRE_SIZES_PX.under_stroke), (color, WIRE_SIZES_PX.stroke)) if path.points else ():
            drawn = ElementTree.SubElement(group, _svg("path"), {
                "d": route, "fill": "none", "stroke": stroke, "stroke-width": str(_round_px(width)),
                "stroke-linecap": "round", "stroke-linejoin": "round"})
            if path.fallback and stroke == color:
                drawn.set("stroke-dasharray", self.DASHES)
        for hole in (jumper.one, jumper.other):
            ElementTree.SubElement(group, _svg("circle"), {
                "cx": str(_round_px(hole.x)), "cy": str(_round_px(hole.y)), "r": str(_round_px(WIRE_SIZES_PX.end_dot)),
                "fill": color, "stroke": "#ffffff", "stroke-width": str(WIRE_SIZES_PX.end_ring)})
        self._pill(group, pill, color)

    @staticmethod
    def _pill(group, pill, color):
        """A WirePill drawn across, in its wire's color with a white edge: the white disc with the step's number in the
        wire's color, then the words in white; turned a quarter back about its centre when it lies along a column."""
        left, top = pill.x - pill.width / 2, pill.y - pill.HEIGHT / 2
        drawn = _element(group, "g", **{"class": "pill"})
        if pill.turned:
            drawn.set("transform", "rotate(-90 %s %s)" % (_round_px(pill.x), _round_px(pill.y)))
        _element(drawn, "rect", x=left, y=top, width=pill.width, height=pill.HEIGHT, rx=pill.HEIGHT / 2, fill=color,
                 stroke="#ffffff", **{"stroke-width": 0.53})
        _element(drawn, "circle", cx=left + pill.DISC_AT, cy=pill.y, r=pill.DISC_R, fill="#ffffff")
        _element(drawn, "text", str(pill.step), x=left + pill.DISC_AT, y=pill.y + 1.9, fill=color,
                 **{"font-size": 5.3, "font-weight": "800", "text-anchor": "middle"})
        _element(drawn, "text", pill.words, x=left + pill.DISC_AT + pill.DISC_R + pill.WORDS_GAP, y=top + 7.0,
                 fill="#ffffff", **{"font-size": 6.1, "font-weight": "700"})


def _svg(tag):
    return "{%s}%s" % (part_pictures.SVG_NAMESPACE, tag)


def _element(parent, tag, text=None, **attributes):
    """One SVG element under `parent`, each number rounded once (`_round_px`), with its text when it has one."""
    element = ElementTree.SubElement(parent, _svg(tag), {
        key: str(_round_px(value)) if isinstance(value, (int, float)) else value for key, value in attributes.items()})
    if text is not None:
        element.text = text
    return element
