"""
Pictures of parts (P268, #302): what a drawing shows for one part. A part's picture is looked up by its record id first,
then by its Wokwi type (P946): the FireBeetle's type is a stand-in that other boards share.

    PictogramPartPictures().picture("wokwi-led", record)  ->  Picture(markup, view_box, credit, note)

A pictogram is a plain SVG in data/pictograms/, named by the record's id or by the part's Wokwi type, with a viewBox and
plain shapes only (`PLAIN_SHAPES`): no id, defs, style, use or url(, so one file can be pasted many times into one
drawing. Its first `<title>` is its credit. A part with no pictogram gets module.svg, a labeled box. `MadePartPictures`
puts a picture that a chain of makers gives (`picture_makers`) before the pictograms.
"""

import collections
import re
import xml.etree.ElementTree as ElementTree
from pathlib import Path

PICTOGRAMS = Path(__file__).resolve().parents[3] / "data" / "pictograms"
#: The pictogram of a part type spark has no picture for.
FALLBACK = "module"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
#: The plain shapes: the only elements a picture that stands in a page may hold (P949). None runs a script, loads a
#: file or holds a style; the pictograms use svg, g, path, rect and circle.
PLAIN_SHAPES = ("svg", "g", "path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text", "tspan", "title")
#: The only attributes such a picture may hold, by lowercase name: the geometry and the presentation that spark's
#: breadboard and its pictograms draw with, and the breadboard's keys. No `style`, no `href`, no handler.
PLAIN_ATTRIBUTES = ("x", "y", "width", "height", "viewbox", "cx", "cy", "r", "rx", "ry", "d", "points", "x1", "y1", "x2",
                    "y2", "transform", "fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin",
                    "stroke-dasharray", "opacity", "fill-opacity", "stroke-opacity", "paint-order", "font-size",
                    "font-family", "font-weight", "text-anchor", "dominant-baseline", "class", "data-step", "data-part",
                    "data-pad")
#: Words that make a kept attribute's value load or run something in CSS, lowercase, and the backslash of a CSS escape.
UNPLAIN_VALUES = ("url(", "image-set", "javascript:", "expression", "\\")

#: Value: one part's picture: its inner SVG markup, its viewBox as (x, y, width, height), the credit a drawing prints
#: for it ("" for spark's own pictograms), and the note the drawing adds under it ("" for none, P946).
Picture = collections.namedtuple("Picture", "markup view_box credit note", defaults=("",))


class PartPictures:
    """Strategy: where a part's picture comes from."""

    def picture(self, wokwi_type, record=None):
        """Picture for a part of this Wokwi type and this record (None for a part with none)."""
        raise NotImplementedError


class PictogramPartPictures(PartPictures):
    """spark's own plain pictograms, from data/pictograms/: the one named by the record's id, else by the Wokwi type, else
    module.svg."""

    def __init__(self, folder=PICTOGRAMS):
        self.folder = Path(folder)
        self.pictures_by_name = {}

    def picture(self, wokwi_type, record=None):
        record_id = record.get("id") if isinstance(record, dict) else None
        names = ([record_id] if isinstance(record_id, str) and re.fullmatch(r"[a-z0-9][a-z0-9_-]*", record_id) else []) + [
            wokwi_type, FALLBACK]
        name = next(name for name in names if (self.folder / ("%s.svg" % name)).is_file())
        if name not in self.pictures_by_name:
            self.pictures_by_name[name] = read_picture((self.folder / ("%s.svg" % name)).read_text(encoding="utf-8"))
        return self.pictures_by_name[name]


def read_picture(text):
    """Picture from one SVG's text: its root's children as markup, less its first `<title>`, which is its credit, and its
    viewBox. A pictogram and a kept picture (`picture_makers`) are read alike."""
    root = ElementTree.fromstring(text)
    view_box = tuple(float(number) for number in re.split(r"[\s,]+", root.get("viewBox").strip()))
    ElementTree.register_namespace("", SVG_NAMESPACE)
    title = root.find("{%s}title" % SVG_NAMESPACE)
    markup = "".join(ElementTree.tostring(child, encoding="unicode") for child in root if child is not title)
    return Picture(markup, view_box, (title.text or "").strip() if title is not None else "")
