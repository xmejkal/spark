"""
Where a part's picture comes from (P946 #1349): an ordered list of exchangeable makers, each tried in turn, the first
that answers giving the picture. A maker says what it uses (`MakerUses`: tools, inputs, a cost, whether it asks first),
so a maker that needs a tool, a model or a service, or costs money, is one more entry in the list.

    PictureMakerChain([StoredPictureMaker(), FramePictureMaker()]).first(request)  ->  MadePictureResult(candidate, declines)

A picture is drawn in the part's frame (`part_shape`: the part from above, in mm), and spark draws the pads and their
labels over any picture. The build's order is `BUILD_MAKERS`. It writes no file.
"""

import collections
import hashlib

from spark.breadboard import part_pictures, part_shape
from spark.breadboard.feature_check import FeatureCheck
from spark.breadboard.features_picture import FeaturesDrawing
from spark.breadboard.picture_check import PictureCheck
from spark.records import board_records, record_kind, store

#: Value: what a maker uses to run: the tools.json entries it calls, the inputs it reads (words), the cost of one run
#: (None, or a sentence with the price) and whether it runs only on the person's yes.
MakerUses = collections.namedtuple("MakerUses", "tools inputs cost asks")
#: Value: what a maker is asked for: the part's record (a part's or a board's), the view, and its frame, a
#: `part_shape.PartShape` (None when the record holds no frame).
PictureRequest = collections.namedtuple("PictureRequest", "record view shape")
#: Value: a maker's answer: the picture's inner SVG and its viewBox, the maker's name, how near it is to the real part
#: (`record_kind.LIKENESS`), and its credit.
PictureCandidate = collections.namedtuple("PictureCandidate", "markup view_box made_by likeness credit")
#: Value: a maker that does not answer: its name, why, and each input it lacked, as the field or the command that gives it.
Decline = collections.namedtuple("Decline", "maker reason missing")
#: Result: the first candidate (None when no maker answered) and every Decline before it.
MadePictureResult = collections.namedtuple("MadePictureResult", "candidate declines")
#: The view the drawn breadboard shows.
BREADBOARD_TOP = "breadboard-top"


def shape_of(record):
    """The frame of a record: a board's from `RecordShapeSource` when it holds `physical.width_mm`, else a module's from
    `ModuleShapeSource`; None for a record with no physical block. A record that lacks a field of its frame raises
    NotDrawnError with the field as its subject."""
    physical = record.get("physical")
    if isinstance(physical, dict) and "width_mm" in physical:
        return part_shape.RecordShapeSource().find_shape(record)
    return part_shape.ModuleShapeSource().find_shape(record)


class PartPictureMaker:
    """Strategy: one way to make a part's picture. `uses()` gives its MakerUses; `make(request)` gives a PictureCandidate or
    a Decline, and never raises for an input that is missing or broken."""

    NAME = None

    def uses(self):
        raise NotImplementedError

    def make(self, request):
        raise NotImplementedError


class StoredPictureMaker(PartPictureMaker):
    """Strategy: the picture kept for the view in the record (`pictures.<view>`, `parts.py --keep-picture`): its
    `documents` entry, the file under that sha256 in the store, its bytes unchanged, and `PictureCheck` passed against
    the frame."""

    NAME = "stored"

    def uses(self):
        return MakerUses((), ("kept-file",), None, False)

    def make(self, request):
        record = request.record
        pictures = record.get("pictures") if isinstance(record.get("pictures"), dict) else {}
        block = pictures.get(request.view)
        if not isinstance(block, dict):
            return Decline(self.NAME, "no kept picture for %s" % request.view, (
                "pictures.%s: parts.py --keep-picture FILE --part %s --project ." % (request.view, record.get("id")),))
        documents = record.get("documents") if isinstance(record.get("documents"), dict) else {}
        entry = documents.get(block.get("document")) if isinstance(block.get("document"), str) else None
        if not board_records.names_a_kept_file(entry):
            return Decline(self.NAME, "the document %r names no kept file" % (block.get("document"),), ())
        try:
            data = (store.place("sources") / entry["sha256"] / entry["file"]).read_bytes()
        except (OSError, store.StoreError):
            return Decline(self.NAME, "the kept file is not in the store", ())
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            return Decline(self.NAME, "the kept file's bytes are not the ones kept", ())
        problems = PictureCheck(request.shape).problems(data) if request.shape else []
        if problems or request.shape is None:
            return Decline(self.NAME, "the picture breaks %s at %s" % problems[0][:2] if problems else "the record has no frame", ())
        picture = part_pictures.read_picture(data.decode("utf-8"))
        return PictureCandidate(picture.markup, picture.view_box, block.get("made_by"), block.get("likeness"), block.get("credit"))


class FramePictureMaker(PartPictureMaker):
    """Strategy: spark's frame of the part, from its record alone: the outline in mm, and in a `data-guide` group a ring
    and the printed label at each pad. A person or an AI draws the picture on it, and leaves the guide out."""

    NAME = "frame"

    def uses(self):
        return MakerUses((), ("physical",), None, False)

    def make(self, request):
        if request.shape is None:
            return Decline(self.NAME, "the record holds no frame", (
                "physical: research.py --part %s --project . asks for the physical facts" % request.record.get("id"),))
        picture = part_pictures.read_picture(self.svg(request.shape))
        return PictureCandidate(picture.markup, picture.view_box, self.NAME, "rough",
                                "spark's frame of %s" % request.record.get("id"))

    @staticmethod
    def svg(shape):
        """The frame as an SVG file's text, in mm."""
        width, height = shape.size
        pads = "".join('<circle cx="%g" cy="%g" r="0.8" fill="none" stroke="#c9a24b" stroke-width="0.2" />'
                       '<text x="%g" y="%g" font-size="1.2" font-family="sans-serif" text-anchor="middle" fill="#20262b">%s</text>'
                       % (x, y, x, y + 2.2, _escaped(label)) for label, (x, y) in shape.pins.items())
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" width="%gmm" height="%gmm">\n'
                '<rect x="0" y="0" width="%g" height="%g" fill="#ffffff" stroke="#20262b" stroke-width="0.2" />\n'
                '<g data-guide="pads">%s</g>\n</svg>\n' % (width, height, width, height, width, height, pads))


class FeaturesPictureMaker(PartPictureMaker):
    """Strategy: spark's drawing of the part from the features measured on the maker's top view (P956,
    `physical.features`, written by `parts.py --features-set`), in their colours (`features_picture.FeaturesDrawing`). It
    declines a record with no features, a feature that breaks the record's shape or a `FeatureCheck` rule, and a drawing
    that breaks `PictureCheck`, so the build can always paste what it gives."""

    NAME = "features"

    def __init__(self, drawing=None):
        self.drawing = drawing or FeaturesDrawing()

    def uses(self):
        return MakerUses((), ("physical", "features"), None, False)

    def make(self, request):
        record = request.record
        physical = record.get("physical") if isinstance(record.get("physical"), dict) else {}
        if not physical.get("features"):
            return Decline(self.NAME, "the record holds no measured features", (
                "physical.features: parts.py --features-set FILE --part %s --project ." % record.get("id"),))
        if request.shape is None:
            return Decline(self.NAME, "the record has no frame", ())
        wrong = record_kind.feature_problems(record)
        if wrong:
            return Decline(self.NAME, wrong[0], ())
        refused = FeatureCheck(request.shape, record).drawn_problems(physical["features"])
        if refused:
            return Decline(self.NAME, "%s breaks %s: %s" % (refused[0].feature, refused[0].code, refused[0].sentence), ())
        data = self.drawing.svg(record, request.shape).encode("utf-8")
        problems = PictureCheck(request.shape).problems(data)
        if problems:
            return Decline(self.NAME, "the drawing breaks %s at %s" % problems[0][:2], ())
        picture = part_pictures.read_picture(data.decode("utf-8"))
        return PictureCandidate(picture.markup, picture.view_box, self.NAME, "near", "spark's drawing of %d measured features of %s"
                                % (len(physical["features"]), record.get("id")))


def _escaped(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class PictureMakerChain:
    """Service: makers asked in their order; `first(request)` gives the MadePictureResult of the first that answers."""

    def __init__(self, makers):
        self.makers = list(makers)

    def first(self, request):
        declines = []
        for maker in self.makers:
            made = maker.make(request)
            if isinstance(made, Decline):
                declines.append(made)
                continue
            return MadePictureResult(made, tuple(declines))
        return MadePictureResult(None, tuple(declines))


#: Every maker by its name.
MAKERS = {"stored": StoredPictureMaker, "frame": FramePictureMaker, "features": FeaturesPictureMaker}
#: The order the build asks the makers in: a kept picture, then spark's drawing of the measured features (P956), else
#: the pictogram (P951 makes it a setting).
BUILD_MAKERS = ("stored", "features")


class MadePartPictures(part_pictures.PartPictures):
    """Decorator: a part's picture from the chain of makers when the record has a frame and a maker answers, else the
    `fallback`'s (spark's pictograms). A record that holds a picture for the view that no maker shows gets the fallback's
    picture with a note that says why, and so does a record whose measured features no maker draws (P956)."""

    def __init__(self, chain, fallback):
        self.chain, self.fallback = chain, fallback

    def picture(self, wokwi_type, record=None):
        fallback = self.fallback.picture(wokwi_type, record)
        if not isinstance(record, dict):
            return fallback
        try:
            shape = shape_of(record)
        except part_shape.NotDrawnError:
            return fallback
        result = self.chain.first(PictureRequest(record, BREADBOARD_TOP, shape)) if shape else MadePictureResult(None, ())
        if result.candidate:
            made = result.candidate
            return part_pictures.Picture(made.markup, made.view_box, made.credit)
        if isinstance(record.get("pictures"), dict) and BREADBOARD_TOP in record["pictures"]:
            why = "; ".join(decline.reason for decline in result.declines) or "the record holds no frame"
            return fallback._replace(note="%s: kept picture not shown (%s)" % (record.get("short_name") or record.get("id"), why))
        if isinstance(record.get("physical"), dict) and record["physical"].get("features"):
            why = next((decline.reason for decline in result.declines if decline.maker == FeaturesPictureMaker.NAME),
                       "no maker of the build draws them")
            return fallback._replace(note="%s: measured features not shown (%s)" % (record.get("short_name") or record.get("id"), why))
        return fallback
