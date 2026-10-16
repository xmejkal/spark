"""
Pictures of parts (P268, #302): what a drawing shows for one part. spark's own pictograms come first; pictures from
online come later as a second source with the same method, so no drawing changes for them.

    PictogramPartPictures().picture("wokwi-led")  ->  Picture(markup, view_box, credit)

A pictogram is a plain SVG in data/pictograms/, named by the part's Wokwi type, with a viewBox and plain shapes only:
no id, defs, style, use or url(, so one file can be pasted many times into one drawing. A type with no pictogram gets
module.svg, a labeled box.
"""

import collections
import re
import xml.etree.ElementTree as ElementTree
from pathlib import Path

PICTOGRAMS = Path(__file__).resolve().parent.parent / "data" / "pictograms"
#: The pictogram of a part type spark has no picture for.
FALLBACK = "module"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"

#: Value: one part's picture: its inner SVG markup, its viewBox as (x, y, width, height), and the credit a drawing
#: prints for it ("" for spark's own pictograms).
Picture = collections.namedtuple("Picture", "markup view_box credit")


class PartPictures:
    """Strategy: where a part's picture comes from."""

    def picture(self, wokwi_type):
        """Picture for a part of this Wokwi type."""
        raise NotImplementedError


class PictogramPartPictures(PartPictures):
    """spark's own plain pictograms, from data/pictograms/, one file per Wokwi type."""

    def __init__(self, folder=PICTOGRAMS):
        self.folder = Path(folder)
        self.found = {}

    def picture(self, wokwi_type):
        if wokwi_type not in self.found:
            path = self.folder / ("%s.svg" % wokwi_type)
            self.found[wokwi_type] = read_pictogram(path if path.is_file() else self.folder / ("%s.svg" % FALLBACK))
        return self.found[wokwi_type]


def read_pictogram(path):
    """Picture from one pictogram file: its root's children as markup, and its viewBox."""
    root = ElementTree.fromstring(Path(path).read_text())
    view_box = tuple(float(number) for number in re.split(r"[\s,]+", root.get("viewBox").strip()))
    ElementTree.register_namespace("", SVG_NAMESPACE)
    markup = "".join(ElementTree.tostring(child, encoding="unicode") for child in root)
    return Picture(markup, view_box, "")
