"""
The drawn breadboard as a picture (P268, #302): `SvgBreadboardDiagram`, the Renderer of a breadboard's scene as
`breadboard.svg`, the breadboard under the parts in the old wiring page's look (`BoardBackground`, which draws
the holes and the gap band from the surface, and the marks that `board_marks` made, P969, with their `BoardPalette`,
P953), and each jumper's pill. `breadboard_scene` makes the scene (P969): it routes each jumper (`wire_routing`), places
each pill (`wire_pills`), each part's caption (`part_captions`) and each pad's label, picks each wire's colour, says each
pad's state, and writes each part's line of the note, so this module places no label and decides no state or warning:
it draws the scene in px, on a canvas framed round it with the note under it. Moved out of `drawing`, whose planner it
reads. `sheet` makes the scene once, for this picture and the Wokwi diagram, and writes the file.
"""

import collections
import xml.etree.ElementTree as ElementTree

from spark.breadboard import part_pictures
from spark.breadboard.board_marks import BoardPalette
from spark.breadboard.breadboard_scene import PAD_FREE, PAD_HELD, PAD_USED
from spark.breadboard.drawing import _round_px
from spark.breadboard.part_captions import PartCaption
from spark.breadboard.spacing import BodyBox
from spark.breadboard.wire_pills import WIRE_SIZES_PX

#: Value: what the dot on a part's pin says, its fill and the legend's words (P949, the praised page's colours), by the
#: pad's state (`breadboard_scene`), in the legend's order.
PadMark = collections.namedtuple("PadMark", "fill words")
PAD_MARKS = {PAD_USED: PadMark("#ffd34d", "pad in use"), PAD_FREE: PadMark("#c9a24b", "pad free"),
             PAD_HELD: PadMark("#5bc0eb", "pad held: do not use")}


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

    def draw(self, root, marks):
        """The board of `marks` (a BoardMarks): its body, the gap band and the holes from its surface, then the marks."""
        colors, sizes = self.palette
        surface, box = marks.surface, marks.box()
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
    Renderer: a BreadboardScene as an SVG picture in Wokwi's px, for the sheet to show (P268, #302; `text(scene)`, the
    scene the sheet made once, P969): a white page, the
    breadboard in its `palette`'s look (BoardBackground, P953), each part as the scene's picture at its holes, turned about its measured center as Wokwi turns it, with
    a dot on each pin in its state's colour (`PAD_MARKS`), and its caption outside its body, then each jumper on the way the scene maker's router gave it
    (P953: around the parts, on tracks between the holes) as the praised page draws a wire: a white under-stroke, the
    color of what it carries on top (its word in `palette`'s `wires`) and a dot at each end, with its pill where
    the scene puts it: its step's number and the two pads it joins (WirePill). A wire
    that needs more bends is drawn dashed, and the note says so, as it says of a wire with no way at all. A part drawn from its record also gets its pad labels where
    the scene placed them, in the part's own frame, and a board its USB end's mark. The note under the picture holds the
    scene's lines (`notes()`). Built with ElementTree, so every text is escaped, and rounded once, so the same layout gives the
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
    #: The dashes of a wire that needs more bends than a wire may have.
    DASHES = "4 2"
    #: A pill's disc: its radius and its centre from the pill's left end, and the gap between the disc and the words,
    #: in px (the visual spec, section 7, P953).
    DISC_R, DISC_AT, WORDS_GAP = 3.4, 4.8, 1.6

    def __init__(self, palette=None):
        self.palette = palette or BoardPalette.load()

    def why_not_written(self, layout):
        """None: the picture is written for any layout."""
        return None

    def text(self, scene):
        """The picture of a BreadboardScene, which places the wires, the pills, the captions and the pad labels, says
        each pad's state and holds each part's picture and the note's lines: this draws them."""
        ElementTree.register_namespace("", part_pictures.SVG_NAMESPACE)
        layout = scene.layout
        notes = scene.notes()
        left, top, width, height = self._canvas(scene, len(notes))
        root = ElementTree.Element(_svg("svg"), {"width": str(width), "height": str(height),
                                                   "viewBox": "%s %s %s %s" % (left, top, width, height),
                                                   "font-family": self.FONT})
        _element(root, "rect", x=left, y=top, width=width, height=height, fill=self.palette.colors["page"])
        BoardBackground(self.palette).draw(root, scene.marks)
        for part in scene.parts:
            self._part(root, part.part, layout.geometry, part.picture)
        self._wires(root, scene)
        for part in scene.parts:
            self._label(root, part, layout.geometry)  # last, so no wire or other part covers a pin
        self._words(root, [part.caption for part in scene.parts], notes, (left + self.MARGIN_PX, top + height))
        return ElementTree.tostring(root, encoding="unicode") + "\n"

    def _canvas(self, scene, note_lines):
        """(left, top, width, height) of the canvas, rounded: the board's body, every part's body (a body may hang past
        the holes: a module seated by one edge, a board's USB end), every wire, pill and caption, with MARGIN_PX round
        them, and NOTE_PX a line of the note under them."""
        boxes = [scene.marks.box()] + [part.body for part in scene.parts]
        boxes += [BodyBox(min(x for x, _ in one.path.points), min(y for _, y in one.path.points),
                          max(x for x, _ in one.path.points), max(y for _, y in one.path.points))
                  for one in scene.jumpers if one.path.points]
        boxes += [one.pill.box() for one in scene.jumpers] + [part.caption.box() for part in scene.parts]
        left, top = min(box.left for box in boxes) - self.MARGIN_PX, min(box.top for box in boxes) - self.MARGIN_PX
        width = _round_px(max(box.right for box in boxes) + self.MARGIN_PX - left)
        height = _round_px(max(box.bottom for box in boxes) + self.MARGIN_PX - top + self.NOTE_PX * note_lines)
        return _round_px(left), _round_px(top), width, height

    def _words(self, root, captions, notes, corner):
        """Each part's caption, its record's name in the title colour or an id muted, then the note's lines up from the
        canvas's bottom left `corner`, its margin in: the parts' lines, then the wires'."""
        colors, sizes = self.palette
        for caption in captions:
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

    def _pad_labels(self, root, part, part_px):
        """A ScenePart's pad labels (P412, P945), each where the scene placed it, with a dashed ring on a doubtful pad,
        then its USB end's mark when it has one. Drawn in the part's own frame, so it turns with the part. A label is
        bold yellow on a pad in use, muted on a pad with no net (NC), else dim, each with the palette's thin dark
        outline."""
        colors, sizes = self.palette
        group = ElementTree.SubElement(root, _svg("g"), {"transform": self._turn(part.part, part_px), "class": "pad-labels"})
        for label in part.labels:
            place = label.place
            if label.doubtful:
                x, y = part_px["pins"][label.pad]
                ElementTree.SubElement(group, _svg("circle"), {
                    "cx": str(_round_px(x)), "cy": str(_round_px(y)), "r": "4", "fill": "none", "stroke": "#e65100",
                    "stroke-width": "1", "stroke-dasharray": "2 1.5"})
            look = {"font-size": sizes["pad_label_used"], "font-weight": "700", "fill": colors["pad_used"]} if label.state == PAD_USED else {
                "font-size": sizes["pad_label"], "fill": colors["pad_none" if label.no_net() else "pad_free"]}
            text = _element(group, "text", label.word, x=place.x, y=place.y, stroke=colors["pad_halo"], **dict(
                look, **{"text-anchor": place.anchor, "stroke-width": sizes["pad_halo"], "paint-order": "stroke"}))
            if place.rotate:
                text.set("transform", "rotate(%s %s %s)" % (place.rotate, _round_px(place.x), _round_px(place.y)))
        if part.usb_mark:
            mark = part.usb_mark
            ElementTree.SubElement(group, _svg("rect"), {
                "x": str(_round_px(mark.left)), "y": str(_round_px(mark.top)), "width": str(_round_px(mark.right - mark.left)),
                "height": str(_round_px(mark.bottom - mark.top)), "rx": "3", "fill": "#cfd8dc", "stroke": "#455a64",
                "stroke-width": "1"})

    def _label(self, root, part, geometry):
        """A ScenePart's pad labels, when it has any, and the dot on each of its pins in its state's colour."""
        if part.labels:
            self._pad_labels(root, part, geometry.part(part.part.type))
        for pin, hole in part.part.holes.items():
            state = part.pads[pin]
            ElementTree.SubElement(root, _svg("circle"), {"cx": str(_round_px(hole.x)), "cy": str(_round_px(hole.y)),
                                                          "r": "2.5", "fill": PAD_MARKS[state].fill, "stroke": "#20262b",
                                                          "stroke-width": "0.6", "data-pad": state})

    def _wires(self, root, scene):
        """Each jumper of the scene on its way, its colour's word drawn in the palette's hex (`wires`), with its pill."""
        hexes = self.palette.colors["wires"]
        for one in scene.jumpers:
            self._jumper(root, one.jumper, one.path, hexes[one.color], one.pill)

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

    def _pill(self, group, pill, color):
        """A WirePill drawn across, in its wire's color with a white edge: the white disc with the step's number in the
        wire's color, then the words in white; turned a quarter back about its centre when it lies along a column."""
        left, top = pill.x - pill.width / 2, pill.y - pill.height / 2
        drawn = _element(group, "g", **{"class": "pill"})
        if pill.turned:
            drawn.set("transform", "rotate(-90 %s %s)" % (_round_px(pill.x), _round_px(pill.y)))
        _element(drawn, "rect", x=left, y=top, width=pill.width, height=pill.height, rx=pill.height / 2, fill=color,
                 stroke="#ffffff", **{"stroke-width": 0.53})
        _element(drawn, "circle", cx=left + self.DISC_AT, cy=pill.y, r=self.DISC_R, fill="#ffffff")
        _element(drawn, "text", str(pill.step), x=left + self.DISC_AT, y=pill.y + 1.9, fill=color,
                 **{"font-size": 5.3, "font-weight": "800", "text-anchor": "middle"})
        _element(drawn, "text", pill.words, x=left + self.DISC_AT + self.DISC_R + self.WORDS_GAP, y=top + 7.0,
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
