"""
spark's drawing of a part from its measured features (P956 #1362): `FeaturesDrawing().svg(record, shape)` gives an SVG in
the part's frame, in mm, of plain shapes only (`part_pictures.PLAIN_SHAPES`): the outline in the board's colour
(`physical.colour`), each feature of `physical.features` in the record's order by the shape of its kind, the pads of the
frame as gold discs, then the labels. Each kind is drawn by one small Strategy (`FeatureShape`), found by its kind in
`SHAPES`. Every number is written to two decimals, so the same record gives the same bytes. It draws no glow, no shadow
and no vendor's bytes. `picture_makers.FeaturesPictureMaker` asks it.
"""

#: The PCB's colour when the record states none: the palette's of the PO's pixel-games wiring page (P946).
PCB_COLOUR = "#16202a"
#: The colour of a gold contact: a pad, an LED's or a contact's end.
GOLD = "#e1b737"
#: The colour of a passive part's tinned ends and a chip's leads.
TIN = "#c8c8c8"
#: The pitch of a chip's leads and of an FPC's contacts, in mm.
LEAD_PITCH_MM = 0.5
#: The count a jst, an fpc or a passives feature has when it states none.
DEFAULT_COUNT = 2


def _n(value):
    """A number as the drawing writes it: two decimals at most, with no trailing zero."""
    text = ("%.2f" % value).rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def rect(box, fill, rx=None):
    """A rect element of `box` (x, y, w, h in mm) in `fill`, its corners rounded by `rx` when it is above 0."""
    corner = ' rx="%s"' % _n(rx) if rx else ""
    return '<rect x="%s" y="%s" width="%s" height="%s"%s fill="%s" />' % (tuple(_n(number) for number in box) + (corner, fill))


def circle(cx, cy, r, fill):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s" />' % (_n(cx), _n(cy), _n(r), fill)


def shade(colour, factor):
    """`colour` (#rrggbb) darker (factor below 1) or lighter (above 1)."""
    channels = [int(colour[at:at + 2], 16) for at in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(value * factor if factor <= 1 else value + (255 - value) * (factor - 1))))
                                   for value in channels)


def _escaped(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _along(feature, count, length):
    """`count` places spread along the feature's long side, each `length` long: (x, y, w, h) of the slot each sits in,
    across the whole short side."""
    x, y, w, h = (feature[key] for key in ("x", "y", "w", "h"))
    long_side = max(w, h)
    step = long_side / count
    slots = []
    for number in range(count):
        start = number * step + (step - length) / 2
        slots.append((x + start, y, length, h) if w >= h else (x, y + start, w, length))
    return slots


class FeatureShape:
    """Strategy: how one kind of feature is drawn: `draw(feature)` gives its elements as SVG text."""

    def draw(self, feature):
        raise NotImplementedError


class PlainShape(FeatureShape):
    """Strategy: a connector: a plain rect in its colour, with corners rounded by `round_by` of its short side."""

    def __init__(self, round_by=0.0):
        self.round_by = round_by

    def draw(self, feature):
        x, y, w, h = (feature[key] for key in ("x", "y", "w", "h"))
        return [rect((x, y, w, h), feature["colour"], min(w, h) * self.round_by)]


class ChipShape(FeatureShape):
    """Strategy: a chip: its body, and tin leads at 0.5 mm along the sides `leads` names in the frame (four by default)."""

    #: How far a lead stands out of the body, and how far it reaches in, in mm.
    OUT, IN = 0.2, 0.25

    def draw(self, feature):
        x, y, w, h = (feature[key] for key in ("x", "y", "w", "h"))
        leads = feature.get("leads", "four")
        drawn = [rect((x, y, w, h), feature["colour"], min(w, h) * 0.05)]
        size = self.OUT + self.IN
        if leads in ("four", "top-bottom"):
            for edge in (y - self.OUT, y + h - self.IN):
                drawn += [rect((at - 0.125, edge, 0.25, size), TIN) for at in self._places(x, w)]
        if leads in ("four", "left-right"):
            for edge in (x - self.OUT, x + w - self.IN):
                drawn += [rect((edge, at - 0.125, size, 0.25), TIN) for at in self._places(y, h)]
        return drawn

    @staticmethod
    def _places(start, length):
        """The centres of the leads along one side, 0.5 mm apart, a pitch clear of each corner."""
        count = max(int((length - 2 * LEAD_PITCH_MM) / LEAD_PITCH_MM) + 1, 0)
        first = start + (length - (count - 1) * LEAD_PITCH_MM) / 2
        return [first + number * LEAD_PITCH_MM for number in range(count)]


class UsbShape(FeatureShape):
    """Strategy: a USB socket: a rounded metal shell in its colour, with a darker slot inside."""

    def draw(self, feature):
        x, y, w, h = (feature[key] for key in ("x", "y", "w", "h"))
        inset = min(w, h) * 0.18
        return [rect((x, y, w, h), feature["colour"], min(w, h) * 0.12),
                rect((x + inset, y + inset, w - 2 * inset, h - 2 * inset), shade(feature["colour"], 0.75), min(w, h) * 0.08)]


class ButtonShape(FeatureShape):
    """Strategy: a push button: its body, with a lighter round cap."""

    def draw(self, feature):
        x, y, w, h = (feature[key] for key in ("x", "y", "w", "h"))
        return [rect((x, y, w, h), feature["colour"], min(w, h) * 0.1),
                circle(x + w / 2, y + h / 2, min(w, h) * 0.32, shade(feature["colour"], 1.35))]


class LedShape(FeatureShape):
    """Strategy: an SMD LED: its body, with two gold end pads along its long side."""

    def draw(self, feature):
        x, y, w, h = (feature[key] for key in ("x", "y", "w", "h"))
        end = max(w, h) * 0.25
        ends = [(x, y, end, h), (x + w - end, y, end, h)] if w >= h else [(x, y, w, end), (x, y + h - end, w, end)]
        return [rect((x, y, w, h), feature["colour"])] + [rect(box, GOLD) for box in ends]


class CountedShape(FeatureShape):
    """Strategy: a housing in its colour with `count` contacts along its long side (`DEFAULT_COUNT` with none): a jst's dark pins
    or an fpc's gold contacts at 0.5 mm."""

    def __init__(self, contact, pitch=None):
        self.contact, self.pitch = contact, pitch

    def draw(self, feature):
        x, y, w, h = (feature[key] for key in ("x", "y", "w", "h"))
        count = feature.get("count", DEFAULT_COUNT)
        long_side, short_side = max(w, h), min(w, h)
        width = self.pitch * 0.5 if self.pitch else long_side / count * 0.35
        drawn = [rect((x, y, w, h), feature["colour"], short_side * 0.05)]
        spread = self.pitch * count if self.pitch else long_side
        offset = (long_side - spread) / 2
        for number in range(count):
            centre = offset + (number + 0.5) * spread / count
            if w >= h:
                drawn.append(rect((x + centre - width / 2, y + h * 0.3, width, h * 0.4), self.contact))
            else:
                drawn.append(rect((x + w * 0.3, y + centre - width / 2, w * 0.4, width), self.contact))
        return drawn


class InductorShape(FeatureShape):
    """Strategy: a power inductor: its body, with gold end caps at the two ends of its long side."""

    def draw(self, feature):
        x, y, w, h = (feature[key] for key in ("x", "y", "w", "h"))
        return [rect((x, y, w, h), feature["colour"], min(w, h) * 0.08)] + [rect(end, GOLD) for end in _ends(x, y, w, h, 0.12)]


class PassivesShape(FeatureShape):
    """Strategy: a group of `count` small resistors or capacitors side by side along the long side, each a body in the colour with
    two tin ends at the ends of its own long side."""

    def draw(self, feature):
        count = feature.get("count", DEFAULT_COUNT)
        drawn = []
        for slot in _along(feature, count, max(feature["w"], feature["h"]) / count * 0.7):
            drawn += [rect(slot, feature["colour"])] + [rect(end, TIN) for end in _ends(*slot, 0.28)]
        return drawn


def _ends(x, y, w, h, part):
    """The two end boxes of a box, each `part` of its long side."""
    if w >= h:
        return [(x, y, w * part, h), (x + w - w * part, y, w * part, h)]
    return [(x, y, w, h * part), (x, y + h - h * part, w, h * part)]


class HoleShape(FeatureShape):
    """Strategy: a mounting hole: a disc of diameter `w` in its colour."""

    def draw(self, feature):
        return [circle(feature["x"] + feature["w"] / 2, feature["y"] + feature["h"] / 2, feature["w"] / 2, feature["colour"])]


class LabelShape(FeatureShape):
    """Strategy: silkscreen text in its colour, 0.8 of the box's short side high: upright in a box at least as wide as tall, else
    sideways, read from below (turned by -90 degrees)."""

    def draw(self, feature):
        x, y, w, h = (feature[key] for key in ("x", "y", "w", "h"))
        cx, cy = x + w / 2, y + h / 2
        turn = "" if w >= h else ' transform="rotate(-90 %s %s)"' % (_n(cx), _n(cy))
        return ['<text x="%s" y="%s" font-size="%s" font-family="sans-serif" font-weight="700" text-anchor="middle" '
                'dominant-baseline="central" fill="%s"%s>%s</text>' % (_n(cx), _n(cy), _n(min(w, h) * 0.8), feature["colour"],
                                                                        turn, _escaped(feature["text"]))]


#: The shape each kind is drawn by: one for every kind of `record_kind.FEATURE_KINDS`.
SHAPES = {"chip": ChipShape(), "usb": UsbShape(), "button": ButtonShape(), "led": LedShape(),
          "jst": CountedShape("#3a3a3a"), "fpc": CountedShape(GOLD, LEAD_PITCH_MM), "connector": PlainShape(0.05),
          "crystal": PlainShape(0.15), "inductor": InductorShape(), "passives": PassivesShape(), "hole": HoleShape(),
          "label": LabelShape()}


class FeaturesDrawing:
    """Service: the SVG of a part from its record's measured features and its frame (`part_shape.PartShape`)."""

    def __init__(self, shapes=None):
        self.shapes = shapes or SHAPES

    def svg(self, record, shape):
        width, height = shape.size
        physical = record["physical"]
        colour = physical.get("colour") if isinstance(physical.get("colour"), dict) else {}
        corner = physical.get("corner_radius_mm")
        corner = corner if isinstance(corner, (int, float)) and not isinstance(corner, bool) and corner > 0 else None
        header = physical.get("header") if isinstance(physical.get("header"), dict) else {}
        pad = header.get("pad_mm") if isinstance(header.get("pad_mm"), (int, float)) and not isinstance(header.get("pad_mm"), bool) else None
        features = physical["features"]
        drawn = [rect((0, 0, width, height), colour.get("value") or PCB_COLOUR, corner)]
        for feature in (feature for feature in features if feature["kind"] != "label"):
            drawn += self.shapes[feature["kind"]].draw(feature)
        if pad:
            drawn += [circle(x, y, pad / 2, GOLD) for x, y in shape.pins.values()]
        for feature in (feature for feature in features if feature["kind"] == "label"):
            drawn += self.shapes["label"].draw(feature)
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" width="%smm" height="%smm">\n%s\n</svg>\n'
                % (_n(width), _n(height), _n(width), _n(height), "\n".join(drawn)))
