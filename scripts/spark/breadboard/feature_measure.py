"""
A part's main features measured on the maker's top view (P956 #1362): `FeatureMeasurer.measure(record, shape)` gives the
features in mm in the part's frame (`part_shape`: from above, the USB end at the bottom, the origin top-left, y down),
with the anchors that prove the turn and the scale, or a `picture_makers.Decline`.

    FileFeatureMeasurer("c6-features.json").measure(record, shape)  ->  MeasuredFeatures(features, anchors, colour, source)

A person or the conversation reads the picture and writes what it sees in the picture's own pixels: the outline of the
PCB, which edge of the picture is the USB end, two anchors or more at pads, and a box and a colour for each feature. Spark
scales each axis by the outline and turns the picture by 0, 90, 180 or 270 degrees, never mirrored, so no hand
arithmetic can put a part on the wrong side. The picture is a component-side top view: a mirrored picture turns into a
mirrored frame, and only the anchors (`feature_check.FeatureCheck`) catch it. It writes nothing.
"""

import collections
import json
import math
from pathlib import Path

from spark.breadboard.picture_makers import Decline, MakerUses

#: Value: what a measurer gives: the features as the record holds them (in mm, each with its source and verified false),
#: the anchors as (pad, x_mm, y_mm), the board's colour as `physical.colour` holds it (None when the file gives none),
#: and the source sentence of the measurement.
MeasuredFeatures = collections.namedtuple("MeasuredFeatures", "features anchors colour source")
#: For each picture edge that is the USB end: the place in the frame, as fractions (across, along), of the place in the
#: picture, as fractions (u, v) of the outline. Each is a turn; none mirrors.
TURNS = {"bottom": lambda u, v: (u, v), "top": lambda u, v: (1 - u, 1 - v),
         "left": lambda u, v: (v, 1 - u), "right": lambda u, v: (1 - v, u)}
#: The fields a feature of the file may carry beyond its box, as the record holds them.
KIND_FIELDS = ("text", "leads", "count")
#: A chip's leads named by the frame's sides, swapped by a quarter turn.
QUARTER_TURNED_LEADS = {"top-bottom": "left-right", "left-right": "top-bottom"}


class FeatureMeasurer:
    """Strategy: one way to measure a part's features. `uses()` gives its `picture_makers.MakerUses`; `measure(record,
    shape)` gives MeasuredFeatures or a Decline, and never raises for an input that is missing or broken. A measurer that
    reads with a vision model is a second subclass: its `uses()` names the tool and the cost, and it asks first."""

    NAME = None

    def uses(self):
        raise NotImplementedError

    def measure(self, record, shape):
        raise NotImplementedError


class FileFeatureMeasurer(FeatureMeasurer):
    """Strategy: the features a person or the conversation wrote in a features file, in the pixels of a picture that the
    record keeps as a `documents` entry: `{picture: {document, outline_px: [left, top, right, bottom], usb_edge},
    measured_by, colour, anchors: [{pad, x_px, y_px}], features: [{name, kind, x_px, y_px, w_px, h_px, colour, ...}]}`."""

    NAME = "file"

    def __init__(self, path):
        self.path = Path(path)

    def uses(self):
        return MakerUses((), ("features-file", "documents"), None, False)

    def measure(self, record, shape):
        try:
            held = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as broken:
            return Decline(self.NAME, "the features file %s cannot be read: %s" % (self.path, broken), ())
        try:
            return self._measured(record, shape, held)
        except (KeyError, TypeError, ValueError, IndexError, AttributeError) as wrong:
            return Decline(self.NAME, "the features file %s lacks a field or holds one of the wrong kind: %s" % (self.path, wrong), ())

    def _measured(self, record, shape, held):
        picture = held["picture"]
        documents = record.get("documents") if isinstance(record.get("documents"), dict) else {}
        entry = documents.get(picture["document"])
        if not isinstance(entry, dict):
            return Decline(self.NAME, "the record's documents hold no %r: keep the picture first" % (picture["document"],),
                           ("documents.%s" % picture["document"],))
        if picture["usb_edge"] not in TURNS:
            return Decline(self.NAME, "usb_edge is %r, but it is the picture's edge that is the USB end: %s"
                           % (picture["usb_edge"], ", ".join(TURNS)), ())
        quarter = picture["usb_edge"] in ("left", "right")
        place = _Placer(_numbers(picture["outline_px"], 4), TURNS[picture["usb_edge"]], shape.size)
        measured = "measured by %s on documents.%s (%s, sha256 %s)" % (
            held["measured_by"], picture["document"], entry.get("url") or entry.get("file"), str(entry.get("sha256"))[:12])
        outline = "%s px" % ",".join(_px(number) for number in picture["outline_px"])
        features = [self._feature(feature, place, measured, outline, quarter) for feature in held["features"]]
        anchors = tuple((anchor["pad"],) + place.point(*_numbers((anchor["x_px"], anchor["y_px"]), 2)) for anchor in held["anchors"])
        colour = None
        if held.get("colour") is not None:
            colour = {"value": held["colour"], "verified": False, "source": "%s, the board's colour" % measured}
        return MeasuredFeatures(features, anchors, colour, "%s, the outline %s, turned with %s as the USB end"
                                % (measured, outline, picture["usb_edge"]))

    @staticmethod
    def _feature(feature, place, measured, outline, quarter):
        """One feature of the file as the record holds it: its box in mm in the frame, its source, verified false. A
        chip's leads are named by the frame's sides, so a quarter turn swaps top-bottom and left-right."""
        box = _numbers((feature["x_px"], feature["y_px"], feature["w_px"], feature["h_px"]), 4)
        x, y, w, h = place.box(*box)
        made = {"name": feature["name"], "kind": feature["kind"], "x": x, "y": y, "w": w, "h": h, "colour": feature["colour"]}
        made.update((field, feature[field]) for field in KIND_FIELDS if field in feature)
        if quarter and made.get("leads") in QUARTER_TURNED_LEADS:
            made["leads"] = QUARTER_TURNED_LEADS[made["leads"]]
        made.update(verified=False, source="%s, box %s px of the outline %s" % (measured, ",".join(_px(number) for number in box), outline))
        return made


class _Placer:
    """Service: the picture's pixels to the frame's mm: each axis scaled by the outline, then turned."""

    def __init__(self, outline, turn, size):
        left, top, right, bottom = outline
        if right <= left or bottom <= top:
            raise ValueError("outline_px is not [left, top, right, bottom] with right > left and bottom > top")
        self.outline, self.turn, self.size = outline, turn, size

    def point(self, x_px, y_px):
        left, top, right, bottom = self.outline
        across, along = self.turn((x_px - left) / (right - left), (y_px - top) / (bottom - top))
        return round(across * self.size[0], 2), round(along * self.size[1], 2)

    def box(self, x_px, y_px, w_px, h_px):
        if w_px <= 0 or h_px <= 0:
            raise ValueError("a box has a width or a height of 0 px or less")
        (x1, y1), (x2, y2) = self.point(x_px, y_px), self.point(x_px + w_px, y_px + h_px)
        return min(x1, x2), min(y1, y2), round(abs(x2 - x1), 2), round(abs(y2 - y1), 2)


def _numbers(values, count):
    """`values` as `count` finite floats, else ValueError."""
    numbers = [float(value) for value in values if not isinstance(value, bool)]
    if len(numbers) != count or len(values) != count or not all(math.isfinite(number) for number in numbers):
        raise ValueError("%r is not %d numbers" % (values, count))
    return numbers


def _px(number):
    return ("%.1f" % number).rstrip("0").rstrip(".")
