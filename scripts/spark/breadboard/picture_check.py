"""
The rules a part's picture holds before it is kept or drawn (P946 #1349): `PictureCheck(shape).problems(data)`, each
problem by its rule's code (`breadboard_codes.PICTURE_CODES`) and the element it stands on, as `svg/g[0]/image[0]`.

A picture is an SVG of the part's frame (its viewBox is the shape's size in mm), of plain shapes only
(`part_pictures.PLAIN_SHAPES`, the rule the page's inliner reads), with at most embedded JPEGs that carry no EXIF. It
holds no pad and no label of spark's: spark draws those over it. It reads the bytes only, never the page's text: base64
spells "http" by chance.
"""

import base64
import binascii
import collections
import re
import xml.etree.ElementTree as ElementTree

from spark.breadboard import breadboard_codes as codes
from spark.breadboard import part_pictures

#: Value: one way a picture breaks a rule: its code, the element as a path from the root, and the sentence.
PictureProblem = collections.namedtuple("PictureProblem", "code element sentence")
#: How far the viewBox's width and height may be from the frame's, in mm.
VIEW_BOX_TOLERANCE_MM = 0.1
#: The largest picture, in bytes: with no embedded JPEG, and with one or more.
MAX_BYTES, MAX_BYTES_WITH_IMAGE = 250000, 400000
#: The one link a picture may hold: a JPEG in the picture itself, as base64.
EMBEDDED_JPEG = re.compile(r"data:image/jpeg;base64,(?=.)(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?")
SVG = "{%s}" % part_pictures.SVG_NAMESPACE


def is_embedded_jpeg(value):
    """True when `value` is a JPEG embedded as a base64 data URI and nothing else: the one href a picture may hold, and the
    one the page's inliner lets stand (the same rule in both, P946)."""
    return isinstance(value, str) and EMBEDDED_JPEG.fullmatch(value) is not None


def repeated_names(attributes):
    """True when two attribute names are one name to HTML: equal once lowercased, without a namespace. HTML keeps the
    first of two, so a second one hides what the first does (the review of P946)."""
    names = [name.rsplit("}", 1)[-1].lower() for name in attributes]
    return len(set(names)) != len(names)


def is_href(name):
    """True for an attribute that HTML may read as a link: its lowercased name, without a namespace, ends in href."""
    return name.rsplit("}", 1)[-1].lower().endswith("href")


def jpeg_problem(href):
    """Why the JPEG of an embedded href is refused, or None: its bytes start a JPEG, and no APP1 segment (EXIF, which can
    say where a photo was taken) comes before its scan."""
    try:
        raw = base64.b64decode(href.split(",", 1)[1], validate=True)
    except (binascii.Error, ValueError):
        return "its JPEG is no base64"
    if raw[:2] != b"\xff\xd8":
        return "its bytes are no JPEG"
    at = 2
    while at + 4 <= len(raw):
        if raw[at] != 0xFF:
            return "its JPEG's segments are broken"
        if raw[at + 1] == 0xDA:
            return None
        if raw[at + 1] == 0xE1:
            return "its JPEG holds an APP1 segment (EXIF, which can say where the photo was taken)"
        at += 2 + int.from_bytes(raw[at + 2:at + 4], "big")
    return "its JPEG ends before its picture"


class PictureCheck:
    """Service: the problems of a picture's bytes against a part's frame, a `part_shape.PartShape` (its size in mm and its
    pads by label). Empty means the picture may be kept and drawn. It reads the bytes only and never raises."""

    def __init__(self, shape):
        self.size = shape.size
        self.labels = set(shape.pins)

    def problems(self, data):
        root, refused = self._root(data)
        if refused:
            return [refused]
        found = [problem for problem in (self._view_box(root), self._too_big(root, data)) if problem]
        return found + [problem for path, element in _walk(root, "svg") for problem in [self._element(path, element)] if problem]

    @staticmethod
    def _root(data):
        """(root, None), or (None, the problem) for bytes that are no SVG; a DOCTYPE or an entity is refused unparsed."""
        def not_svg(why):
            return None, PictureProblem(codes.PICTURE_NOT_SVG, "svg", "the picture is no SVG: %s" % why)
        if len(data) > MAX_BYTES_WITH_IMAGE:
            return None, PictureProblem(codes.PICTURE_TOO_BIG, "svg", "the picture is over %d bytes" % MAX_BYTES_WITH_IMAGE)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return not_svg("its bytes are no UTF-8")
        if "<!doctype" in text.lower() or "<!entity" in text.lower():
            return not_svg("it holds a DOCTYPE or an entity")
        try:
            root = ElementTree.fromstring(text)
        except ElementTree.ParseError as broken:
            return not_svg(str(broken))
        return (root, None) if root.tag == SVG + "svg" else not_svg("its root is %s" % root.tag)

    def _view_box(self, root):
        numbers = re.split(r"[\s,]+", (root.get("viewBox") or "").strip())
        try:
            x, y, width, height = (float(number) for number in numbers)
        except ValueError:
            x = y = width = height = None
        if x == 0 and y == 0 and all(abs(drawn - frame) <= VIEW_BOX_TOLERANCE_MM for drawn, frame in zip((width, height), self.size)):
            return None
        return PictureProblem(codes.PICTURE_VIEW_BOX, "svg", "the viewBox is not 0 0 %g %g, the frame's size in mm" % self.size)

    @staticmethod
    def _too_big(root, data):
        if len(data) <= MAX_BYTES or any(element.tag == SVG + "image" for element in root.iter()):
            return None
        return PictureProblem(codes.PICTURE_TOO_BIG, "svg", "a picture with no embedded JPEG is over %d bytes" % MAX_BYTES)

    def _element(self, path, element):
        """The first problem of one element, or None."""
        tag = element.tag[len(SVG):] if element.tag.startswith(SVG) else element.tag
        if tag not in part_pictures.PLAIN_SHAPES + ("image",) or any(step.startswith("title[") for step in path.split("/")[1:-1]):
            return PictureProblem(codes.PICTURE_ELEMENT, path, "%s is no plain shape" % tag)
        if "data-guide" in element.attrib:
            return PictureProblem(codes.PICTURE_GUIDE_LEFT, path, "the frame's guide is left in: the pads are spark's to draw")
        why = self._attribute_problem(tag, element.attrib)
        if why:
            return PictureProblem(codes.PICTURE_LINK if why[0] == "link" else codes.PICTURE_JPEG if why[0] == "jpeg"
                                  else codes.PICTURE_ATTRIBUTE, path, why[1])
        if "http" in (element.text or "").lower():
            return PictureProblem(codes.PICTURE_LINK, path, "a text holds a web address")
        if tag in ("text", "tspan") and (element.text or "").strip() in self.labels:
            return PictureProblem(codes.PICTURE_PAD_LABEL, path, "the text %s is a pad's label: spark draws it" % element.text.strip())
        return None

    @staticmethod
    def _attribute_problem(tag, attributes):
        """("link" | "jpeg" | "attribute", why) of the first attribute that breaks a rule, or None."""
        allowed = part_pictures.IMAGE_ATTRIBUTES if tag == "image" else part_pictures.PLAIN_ATTRIBUTES
        if repeated_names(attributes):
            return "attribute", "two attributes have one name once lowercased: HTML keeps the first"
        if tag == "image" and "href" not in attributes:
            return "link", "an image with no embedded JPEG"
        for name, value in attributes.items():
            if is_href(name):
                if name != "href" or tag != "image" or not is_embedded_jpeg(value):
                    return "link", "%s=%s... is no JPEG embedded on an image" % (name, value[:30])
                why = jpeg_problem(value)
                if why:
                    return "jpeg", why
            elif name.lower() not in allowed or any(word in value.lower() for word in part_pictures.UNPLAIN_VALUES + ("http",)):
                return "attribute", "the attribute %s may load or run something, or is not one a picture holds" % name
        return None


def _walk(element, path):
    """(path, element) of the element and each one under it, in document order; a path counts each tag among its siblings."""
    yield path, element
    seen = collections.Counter()
    for child in element:
        tag = child.tag[len(SVG):] if child.tag.startswith(SVG) else child.tag
        yield from _walk(child, "%s/%s[%d]" % (path, tag, seen[tag]))
        seen[tag] += 1
