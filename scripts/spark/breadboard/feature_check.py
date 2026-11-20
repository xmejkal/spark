"""
The rules a part's measured features hold against its frame (P956 #1362): `FeatureCheck(shape, record).problems(measured)`,
each problem by its rule's code (`breadboard_codes.FEATURE_CODES`) and the feature it names.

Only the pads and the mounting holes can be checked against the maker's dimension drawing, through the record: each
anchor against the pad of its label, and each `hole` against `physical.mounting_holes`. A chip or a connector is checked
only against the outline and the pads, so a wrong place near no pad passes, and no rule can tell a bad measurement from
a real part beside a pad. The look is judged by eye: the conversation's render, then the person's.
"""

import collections
import math

from spark.breadboard import breadboard_codes as codes

#: Value: one way a measured feature breaks a rule: its code, the feature's name (or the anchor's pad), and the sentence.
FeatureProblem = collections.namedtuple("FeatureProblem", "code feature sentence")
#: How far an anchor or a hole may be from where the record's dimension drawing puts it, in mm.
DRAWING_TOLERANCE_MM = 0.5
#: How far a feature may sit past the outline before it is refused, in mm: up to it, the box is pulled back inside.
EDGE_TOLERANCE_MM = 0.5
#: How far a USB socket may hang past the frame's USB edge (the bottom), in mm: it is drawn there, not pulled back.
USB_OVERHANG_MM = 2.0
#: A pad's diameter when the record states none (`physical.header.pad_mm`), in mm.
DEFAULT_PAD_MM = 1.5


class FeatureCheck:
    """Service: the problems of measured features against a part's frame (`part_shape.PartShape`: its size and its pads)
    and its record (`physical.header.pad_mm`, `physical.mounting_holes`). Empty means they may be written and drawn."""

    def __init__(self, shape, record):
        self.size, self.pins = shape.size, shape.pins
        physical = record.get("physical") if isinstance(record.get("physical"), dict) else {}
        header = physical.get("header") if isinstance(physical.get("header"), dict) else {}
        pad = header.get("pad_mm")
        self.pad_radius = (pad if isinstance(pad, (int, float)) and not isinstance(pad, bool) and pad > 0 else DEFAULT_PAD_MM) / 2
        self.holes = self._hole_places(physical.get("mounting_holes"))

    def _hole_places(self, holes):
        """The centres of the mounting holes that the record's spacing gives, about the frame's centre; () with none."""
        spacing = [holes.get(key) for key in ("spacing_x_mm", "spacing_y_mm")] if isinstance(holes, dict) else []
        if len(spacing) != 2 or not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in spacing):
            return ()
        width, height = self.size
        return tuple((width / 2 + across * spacing[0] / 2, height / 2 + along * spacing[1] / 2)
                     for across in (-1, 1) for along in (-1, 1))

    def problems(self, measured):
        """Every problem of a measurement (`feature_measure.MeasuredFeatures`): its anchors, then each feature's."""
        return self.anchor_problems(measured.anchors) + self.drawn_problems(measured.features)

    def anchor_problems(self, anchors):
        """Each anchor that names no pad or lies off the drawing, and too few anchors to prove the turn and the scale."""
        found, placed = [], []
        for pad, x, y in anchors:
            if pad not in self.pins:
                found.append(FeatureProblem(codes.FEATURE_NO_ANCHOR, pad, "the anchor %s names no pad of the record" % pad))
                continue
            off = math.hypot(x - self.pins[pad][0], y - self.pins[pad][1])
            if off > DRAWING_TOLERANCE_MM:
                found.append(FeatureProblem(codes.FEATURE_OFF_DRAWING, pad, "the anchor %s lies %.2f mm from its pad in the "
                                            "record: the picture is turned, mirrored or scaled wrong" % (pad, off)))
            placed.append(self.pins[pad])
        width, height = self.size
        if not any(abs(a[0] - b[0]) >= width / 2 or abs(a[1] - b[1]) >= height / 2 for a in placed for b in placed):
            found.append(FeatureProblem(codes.FEATURE_NO_ANCHOR, None, "two anchors at least, at pads half the board apart "
                                        "across or along, prove the turn and the scale"))
        return found

    def drawn_problems(self, features):
        """Each feature that lies outside the outline, covers a pad, is a hole off the drawing or a label that is a pad's."""
        found = []
        for feature in features:
            outside = self._outside(feature)
            found += [outside] if outside else self._placed_problems(self.fitted(feature))
        return found

    def fitted(self, feature):
        """The feature with its box pulled back inside the outline (a USB socket keeps its overhang past the USB edge)."""
        width, height = self.size
        bottom = height + (USB_OVERHANG_MM if feature["kind"] == "usb" else 0)
        x = min(max(feature["x"], 0), max(width - feature["w"], 0))
        y = min(max(feature["y"], 0), max(bottom - feature["h"], 0))
        return dict(feature, x=round(x, 2), y=round(y, 2))

    def _outside(self, feature):
        width, height = self.size
        bottom = height + (USB_OVERHANG_MM if feature["kind"] == "usb" else EDGE_TOLERANCE_MM)
        past = max(-feature["x"] - EDGE_TOLERANCE_MM, -feature["y"] - EDGE_TOLERANCE_MM,
                   feature["x"] + feature["w"] - width - EDGE_TOLERANCE_MM, feature["y"] + feature["h"] - bottom)
        if past > 0:
            return FeatureProblem(codes.FEATURE_OUTSIDE, feature["name"], "%s lies %.2f mm too far past the outline"
                                  % (feature["name"], past))
        return None

    def _placed_problems(self, feature):
        found = []
        name, x, y, w, h = (feature[key] for key in ("name", "x", "y", "w", "h"))
        for pad, (cx, cy) in self.pins.items():
            if math.hypot(max(x - cx, 0, cx - x - w), max(y - cy, 0, cy - y - h)) < self.pad_radius:
                found.append(FeatureProblem(codes.FEATURE_OVER_PAD, name, "%s covers part of the pad %s" % (name, pad)))
                break
        if feature["kind"] == "hole" and self.holes:
            off = min(math.hypot(x + w / 2 - hx, y + h / 2 - hy) for hx, hy in self.holes)
            if off > DRAWING_TOLERANCE_MM:
                found.append(FeatureProblem(codes.FEATURE_OFF_DRAWING, name, "%s lies %.2f mm from the nearest mounting hole "
                                            "of physical.mounting_holes" % (name, off)))
        text = feature.get("text")
        if feature["kind"] == "label" and isinstance(text, str) and (text.strip() in self.pins or "http" in text.lower()):
            found.append(FeatureProblem(codes.FEATURE_PAD_LABEL, name, "%s says %r, which is a pad's label spark draws, or "
                                        "a web address" % (name, text)))
        return found
