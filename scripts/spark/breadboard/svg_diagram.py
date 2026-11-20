"""
The drawn breadboard as a picture (P268, #302): `SvgBreadboardDiagram`, the Renderer of a planned layout as
`breadboard.svg`, and the Strategies that place a drawn part's pad labels (P945). Moved out of `drawing`, whose planner
and Wokwi diagram it reads. `sheet` writes the file; `part_shape` names a part's label layout.
"""

import collections
import xml.etree.ElementTree as ElementTree

from spark.breadboard import part_pictures, wiring_steps
from spark.breadboard.drawing import _round_px, rotate

#: Where a drawn part's pad labels go, the `labels` of its part_px: beside each pad, inside a board's body; or from a
#: row of pads along an edge into the module's body, turned along the column (P945).
LABELS_BESIDE, LABELS_INTO_BODY = "beside", "into-body"


#: Value: where one pad's label goes in the part's own frame: its anchor point, its `text-anchor` and its turn in degrees.
LabelPlace = collections.namedtuple("LabelPlace", "x y anchor rotate")


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


class SvgBreadboardDiagram:
    """
    Renderer: a BreadboardLayout as an SVG picture in Wokwi's px, for the sheet to show (P268, #302): the breadboard's
    holes and rails, each part as its picture at its holes, turned about its measured center as Wokwi turns it, with
    a dot on each pin and its name, then each jumper as a line in the color of what it carries, with its number. A part drawn from
    its record also gets its pad labels, placed by the PadLabelLayout its part_px names (`label_layouts`, keyed by the
    part_px's `labels`). Built with ElementTree, so every text is escaped, and rounded once, so the same layout gives the
    same bytes. The canvas holds every hole and every part's body.
    """

    FILE_NAME = "breadboard.svg"
    NOUN = "breadboard picture"
    PURPOSE_MESSAGE = "a picture of the same layout, which breadboard.md shows"
    SHEET_MESSAGE = "![The layout on a breadboard](breadboard.svg)"
    #: The space around the outermost holes, in px.
    MARGIN_PX = 14
    #: The room under the holes for the note of a board whose facts are not all verified, in px.
    NOTE_PX = 14

    def __init__(self, colors=None, pictures=None, label_layouts=None):
        self.colors = colors or wiring_steps.JumperColors()
        self.pictures = pictures or part_pictures.PictogramPartPictures()
        self.label_layouts = label_layouts or {LABELS_BESIDE: BesideLabels(), LABELS_INTO_BODY: IntoBodyLabels()}

    def why_not_written(self, layout):
        """None: the picture is written for any layout."""
        return None

    @staticmethod
    def _far_corner(part, part_px):
        """(x, y) of the right and lower edges of a part's body as it is turned and placed."""
        width, height = part_px["size"]
        corners = rotate({"0": (0, 0), "1": (width, 0), "2": (0, height), "3": (width, height)}, part_px["center"],
                         part.rotate).values()
        return part.left + max(x for x, _ in corners), part.top + max(y for _, y in corners)

    def text(self, layout):
        ElementTree.register_namespace("", part_pictures.SVG_NAMESPACE)
        surface = layout.geometry.surface
        notes = [note["sentence"] for part in layout.parts for note in layout.geometry.part(part.type).get("notes", [])]
        # a body that covers holes may hang past them (a module seated by one edge); a small part stays in the margin
        corners = [self._far_corner(part, layout.geometry.part(part.type)) for part in layout.parts
                   if layout.geometry.part(part.type).get("covers_holes")]
        width = _round_px(max([max(hole.x for hole in surface.holes) + 2 * self.MARGIN_PX]
                              + [x + self.MARGIN_PX for x, _ in corners]))
        height = _round_px(max([max(hole.y for hole in surface.holes) + self.MARGIN_PX]
                               + [y + self.MARGIN_PX for _, y in corners]) + (self.NOTE_PX if notes else 0))
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
            self._part(root, part, layout.geometry)
        colors = self.colors.of({jumper.step: jumper.role for jumper in layout.jumpers})
        for jumper in layout.jumpers:
            self._jumper(root, jumper, layout.geometry.surface.pitch, colors[jumper.step])
        for part in layout.parts:
            self._label(root, part, layout.geometry)  # last, so no wire or other part covers a pin or a name
        if notes:
            note = ElementTree.SubElement(root, _svg("text"), {
                "x": str(self.MARGIN_PX), "y": str(_round_px(height - 4)), "font-size": "8", "font-family": "sans-serif",
                "fill": "#5d4037"})
            note.text = ", ".join(notes)
        return ElementTree.tostring(root, encoding="unicode") + "\n"

    @staticmethod
    def _turn(part, part_px):
        """The transform that puts a part's own frame where Wokwi shows it: moved to its corner, turned about its center."""
        cx, cy = part_px["center"]
        return "translate(%s %s) rotate(%s %s %s)" % (_round_px(part.left), _round_px(part.top), part.rotate,
                                                      _round_px(cx), _round_px(cy))

    def _part(self, root, part, geometry):
        part_px = geometry.part(part.type)
        picture = self.pictures.picture(part.type)
        group = ElementTree.SubElement(root, _svg("g"), {"transform": self._turn(part, part_px)})
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
                          "font-family": "sans-serif", "text-anchor": place.anchor, "fill": "#ffffff",
                          "stroke": "#0d47a1", "stroke-width": "1.5", "paint-order": "stroke"}
            if place.rotate:
                attributes["transform"] = "rotate(%s %s %s)" % (place.rotate, _round_px(place.x), _round_px(place.y))
            ElementTree.SubElement(group, _svg("text"), attributes).text = pad
        if part_px.get("usb_mark"):
            ElementTree.SubElement(group, _svg("rect"), {
                "x": str(_round_px(cx - 17)), "y": str(_round_px(height - 12)), "width": "34", "height": "12", "rx": "3",
                "fill": "#cfd8dc", "stroke": "#455a64", "stroke-width": "1"})

    def _label(self, root, part, geometry):
        part_px = geometry.part(part.type)
        if part_px.get("pad_labels"):
            self._pad_labels(root, part, part_px)
        for hole in part.holes.values():
            ElementTree.SubElement(root, _svg("circle"), {"cx": str(_round_px(hole.x)), "cy": str(_round_px(hole.y)),
                                                          "r": "2.5", "fill": "#2e7d32"})
        cx, cy = part_px["center"]
        label = ElementTree.SubElement(root, _svg("text"), {
            "x": str(_round_px(part.left + cx)), "y": str(_round_px(part.top + cy)), "font-size": "8",
            "font-family": "sans-serif", "text-anchor": "middle", "fill": "#1a1a1a", "stroke": "#ffffff",
            "stroke-width": "2.5", "paint-order": "stroke"})
        label.text = part_px.get("name") or part.id

    def _jumper(self, root, jumper, pitch, color):
        """One jumper along the holes: out of its first hole along the column, across between two rows of holes, and
        into its last hole. Its bends sit half a pitch off the holes, so no bend looks like a joint with a hole of
        another group."""
        one, other = jumper.one, jumper.other
        half = pitch / 2
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
