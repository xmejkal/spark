"""
The drawn breadboard as one scene (P969, #1388): `BreadboardScene`, everything a view of the breadboard draws, each
thing with its place, made once by `BreadboardSceneMaker` before any view. The maker reads the board's marks
(`board_marks`), routes the jumpers (a `wire_routing.JumperRouter`), picks each wire's colour (`wiring_steps`), and
places the pills (`wire_pills`), the captions (`part_captions`) and each pad's label (a `PadLabelLayout`) through a
`LabelMeasure`, the room a label takes as one view draws it. It also says each pad's state (in use or free), makes
each part's picture from the `part_pictures.PartPictures` it is given, and writes each part's line of the note
(`PartNotes`). So no view places a label or decides a pad's state or a warning: `svg_diagram` draws the scene in px,
and a view in characters reads the same scene through its grid (`SceneGrid`). Nothing here draws.
"""

import collections
import math

from spark.breadboard import part_pictures, wire_routing, wiring_steps
from spark.breadboard.board_marks import BoardMarks, BoardPalette
from spark.breadboard.part_captions import PartCaption, PartNotes
from spark.breadboard.spacing import BodyBox, rotate
from spark.breadboard.wire_pills import WIRE_SIZES_PX, PillLayout, wire_boxes


class LabelMeasure:
    """Strategy: the room a label takes on the drawn breadboard as one view draws it, in the scene's px, so that the
    maker places every pill, caption and pad label for that view: `pill(words)` gives (width, height) of a wire's pill
    with these words, along its words and across them; `caption(words)` gives (size, width) of a part's caption, its
    height and its width; `pad_label()` gives (gap, middle) of a pad's label: the room between the pad and the near end
    of its words, along them, and how far its baseline lies from the middle of its letters, across them."""

    def pill(self, words):
        raise NotImplementedError

    def caption(self, words):
        raise NotImplementedError

    def pad_label(self):
        raise NotImplementedError


class PxLabelMeasure(LabelMeasure):
    """Strategy: the labels as the SVG draws them, in its px: a pill PILL_HEIGHT high, with DISC_ROOM for the white
    disc with its number, END_ROOM after its words, and PER_CHARACTER a character of its words (6.1 px bold); a
    caption at the palette's `caption_size`, CAPTION_PER_CHARACTER of it a character plus CAPTION_ROOM of it; a pad's
    label PAD_GAP from its pad, its baseline PAD_MIDDLE from the middle of its letters."""

    #: The pill's height, the room its disc takes, the room after its words, and the width a character of its words takes,
    #: in px: the old page's at spark's pitch (the visual spec, section 7, P953).
    PILL_HEIGHT, DISC_ROOM, END_ROOM, PER_CHARACTER = 9.6, 9.6, 3.6, 3.57
    #: The width a character of a caption takes, and the room added to its words' width, each times its size. Chrome
    #: draws the fixtures' names 0.50 to 0.54 of the size a character wide.
    CAPTION_PER_CHARACTER, CAPTION_ROOM = 0.55, 0.5
    #: The room between a pad and its label, and how far a label's baseline lies from the middle of its letters, in px.
    PAD_GAP, PAD_MIDDLE = 5, 2

    def __init__(self, caption_size):
        self.caption_size = caption_size

    def pill(self, words):
        return self.DISC_ROOM + self.END_ROOM + self.PER_CHARACTER * len(words), self.PILL_HEIGHT

    def caption(self, words):
        return self.caption_size, (self.CAPTION_PER_CHARACTER * len(words) + self.CAPTION_ROOM) * self.caption_size

    def pad_label(self):
        return self.PAD_GAP, self.PAD_MIDDLE


#: Where a drawn part's pad labels go, the `labels` of its part_px: beside each pad, inside a board's body; or from a
#: row of pads along an edge into the module's body, turned along the column (P945).
LABELS_BESIDE, LABELS_INTO_BODY = "beside", "into-body"

#: Value: where one pad's label goes in the part's own frame: its anchor point, its `text-anchor` and its turn in degrees.
LabelPlace = collections.namedtuple("LabelPlace", "x y anchor rotate")


class PadLabelLayout:
    """Strategy: where a drawn part's pad label goes, beside its pad, in the part's own frame, its gap from the pad and
    its middle from the `measure` (a LabelMeasure). `place(x, y, part_px, turn)` gives the LabelPlace of the pad at
    (x, y) of a part turned by `turn` degrees on the sheet. One reading direction (P953): a label's own turn plus the
    part's is 0 or -90, so every turned label reads bottom to top; a place that would read the other way is turned half
    round about the middle of its letters, its anchor flipped."""

    def __init__(self, measure):
        self.gap, self.middle = measure.pad_label()

    def place(self, x, y, part_px, turn):
        place = self._place(x, y, part_px)
        if (turn + place.rotate) % 360 in (0, 270):
            return place
        radians = math.radians(place.rotate)
        up_x, up_y = round(math.sin(radians)), -round(math.cos(radians))  # the text's up, in the part's frame
        return LabelPlace(place.x + 2 * self.middle * up_x, place.y + 2 * self.middle * up_y,
                          {"start": "end", "end": "start"}[place.anchor], place.rotate - 180)

    def _place(self, x, y, part_px):
        """The LabelPlace in the part's frame, before the reading direction."""
        raise NotImplementedError


class BesideLabels(PadLabelLayout):
    """Strategy: a board's pads in two rows down its sides: each label beside its pad, toward the board's middle."""

    def _place(self, x, y, part_px):
        inward = x < part_px["center"][0]
        return LabelPlace(x + (self.gap if inward else -self.gap), y + self.middle, "start" if inward else "end", 0)


class IntoBodyLabels(PadLabelLayout):
    """Strategy: a module's one row of pads along an edge: each label runs along the pad's column into the body, below a pad on the
    top edge and above one on the bottom edge, turned a quarter so that labels one pitch apart do not overlap."""

    def _place(self, x, y, part_px):
        if y < part_px["center"][1]:
            return LabelPlace(x + self.middle, y + self.gap, "end", -90)
        return LabelPlace(x + self.middle, y - self.gap, "start", -90)


#: The states of a pin's dot, in the legend's order: its row joins a wire or another part, its row joins nothing, or
#: something on the board is already wired to it. spark draws no pad held yet: that needs the board record's onboard
#: roles (P950).
PAD_USED, PAD_FREE, PAD_HELD = "used", "free", "held"


class PadLabel(collections.namedtuple("PadLabel", "pad word place at state doubtful")):
    """Value: one pad's label: the pad's key in the part's record, its word in the steps' words
    (`wiring_steps.pad_word`, P953), its LabelPlace in the part's own frame (for a view that turns the part), `at`, its
    anchor point on the sheet, the part turned and placed (for a view that draws on the sheet's grid), the pad's state
    (PAD_USED or PAD_FREE, as its dot), and `doubtful` when the record doubts the pad's place. `no_net()` is True for a
    pad with no net, whose label is drawn muted."""

    #: The word of a pad with no net.
    NO_NET = "NC"

    def no_net(self):
        return self.word == self.NO_NET


class SceneGrid(collections.namedtuple("SceneGrid", "x0 y0 step low high")):
    """Value: the half-pitch grid of one scene: `cell(x, y)` and `point(cell)` turn px into cells and back, from the
    first column and row a, as the router's TrackGrid does; `low` and `high` are the cells of the corners of its
    extent, which holds everything the scene draws."""

    @classmethod
    def of(cls, surface, boxes):
        """The grid of the surface whose extent holds every BodyBox of `boxes`."""
        step = surface.pitch / 2
        x0, y0 = min(hole.x for hole in surface.terminal), min(surface.letters_y.values())
        low = (math.floor((min(box.left for box in boxes) - x0) / step), math.floor((min(box.top for box in boxes) - y0) / step))
        high = (math.ceil((max(box.right for box in boxes) - x0) / step), math.ceil((max(box.bottom for box in boxes) - y0) / step))
        return cls(x0, y0, step, low, high)

    def cell(self, x, y):
        return round((x - self.x0) / self.step), round((y - self.y0) / self.step)

    def point(self, cell):
        return self.x0 + cell[0] * self.step, self.y0 + cell[1] * self.step


#: Value: one part in the scene: its PlacedPart, its BodyBox, its Caption, its Picture (`part_pictures`), its line of
#: the note ("" when it has none), {pin: PAD_USED or PAD_FREE} of its holes, its PadLabels (none unless it is drawn
#: from its record) and its USB end's mark, a BodyBox in its own frame (None unless it is a board drawn from its record).
ScenePart = collections.namedtuple("ScenePart", "part body caption picture note pads labels usb_mark")
#: Value: one jumper in the scene: its Jumper, its JumperPath in px, the grid's cell of each of the path's points, its
#: colour's word (`wiring_steps.JumperColors`) and its WirePill.
SceneJumper = collections.namedtuple("SceneJumper", "jumper path cells color pill")


class BreadboardScene(collections.namedtuple("BreadboardScene", "layout marks parts jumpers joined grid")):
    """
    Value: everything a view of one drawn breadboard draws, each with its place in px: the BreadboardLayout it was made
    from, the breadboard's BoardMarks, each part (ScenePart) and each jumper (SceneJumper) in the
    layout's order, the hole groups that join something (`joined`), and its SceneGrid. `wire_notes()` gives the
    sentences of the wires drawn dashed and of those not drawn; `notes()` gives the lines of the note under the
    drawing, each part's and then the wires'.
    """

    #: What the note says of the wires drawn dashed, and of the wires not drawn, filled with their numbers.
    DASHED_NOTE = ("wire %s bends more than 4 times to go around the parts and is drawn dashed",
                   "wires %s bend more than 4 times to go around the parts and are drawn dashed")
    NOT_DRAWN_NOTE = ("wire %s finds no way around the parts and is not drawn", "wires %s find no way around the parts "
                      "and are not drawn")

    def wire_notes(self):
        """The note's sentences of the wires drawn dashed and of the wires not drawn, each by its step's number."""
        said = []
        for fallback, words in ((wire_routing.BENDS, self.DASHED_NOTE), (wire_routing.NO_WAY, self.NOT_DRAWN_NOTE)):
            steps = sorted(jumper.jumper.step for jumper in self.jumpers if jumper.path.fallback == fallback)
            if steps:
                numbers = ", ".join(map(str, steps[:-1])) + " and %d" % steps[-1] if len(steps) > 1 else str(steps[0])
                said.append(words[len(steps) > 1] % numbers)
        return said

    def notes(self):
        """The note's lines: each part's line that says something, then the wires' sentences in one line."""
        wired = self.wire_notes()
        return [part.note for part in self.parts if part.note] + ([", ".join(wired)] if wired else [])


class BreadboardSceneMaker:
    """
    Service: makes the BreadboardScene of a layout, once, before any view: the board's marks at the `palette`'s sizes,
    each part's body, each jumper's way from the `router` (a JumperRouter, swapped here and never in a view), each
    wire's colour from `colors`, then each pill (PillLayout), each caption (PartCaption) and each pad's label (the
    PadLabelLayout its part_px's `labels` names), placed through the `measure` (a LabelMeasure; PxLabelMeasure, the
    SVG's, by default); each pad's state, and each part's picture from `pictures` (a PartPictures; spark's pictograms
    by default) with its line of the note (PartNotes).
    """

    def __init__(self, colors=None, router=None, palette=None, measure=None, pictures=None):
        self.colors = colors or wiring_steps.JumperColors()
        self.router = router or wire_routing.TrackJumperRouter()
        self.palette = palette or BoardPalette.load()
        self.measure = measure or PxLabelMeasure(self.palette.sizes["caption"])
        self.pictures = pictures or part_pictures.PictogramPartPictures()
        self.pill_layout = PillLayout(WIRE_SIZES_PX.under_stroke, WIRE_SIZES_PX.end_dot + WIRE_SIZES_PX.end_ring / 2, self.measure)
        self.label_layouts = {LABELS_BESIDE: BesideLabels(self.measure), LABELS_INTO_BODY: IntoBodyLabels(self.measure)}

    def make(self, layout):
        surface = layout.geometry.surface
        marks = BoardMarks(surface, self.palette.sizes)
        bodies = [BodyBox.of(part, layout.geometry.part(part.type)) for part in layout.parts]
        obstacles = marks.obstacles(bodies)
        paths = self.router.route(layout, obstacles)
        pills = self.pill_layout.place(layout.jumpers, paths,
                                       obstacles._replace(marks=obstacles.marks + marks.sign_boxes()))
        captions = PartCaption(self.measure, surface.pitch).place(layout.parts, bodies, bodies + list(
            obstacles.marks + marks.sign_boxes()) + wire_boxes(layout.jumpers, paths, pills))
        grid = SceneGrid.of(surface, [marks.box()] + bodies + [pill.box() for pill in pills.values()]
                            + [caption.box() for caption in captions.values()]
                            + [BodyBox(x, y, x, y) for path in paths.values() for x, y in path.points])
        joined = frozenset(self._joined_groups(layout))
        parts = tuple(self._part(part, layout.geometry.part(part.type), body, captions[part.id], joined)
                      for part, body in zip(layout.parts, bodies))
        return BreadboardScene(layout, marks, parts, self._jumpers(layout, paths, pills, grid), joined, grid)

    def _part(self, part, part_px, body, caption, joined):
        """The ScenePart of one part: its picture and its line of the note, each pin's state (in use when its hole's
        group joins something), its pad labels and its USB end's mark."""
        picture = self.pictures.picture(part.type, part.record)
        pads = {pin: PAD_USED if hole.group in joined else PAD_FREE for pin, hole in part.holes.items()}
        return ScenePart(part, body, caption, picture, PartNotes.line(part, part_px, picture), pads,
                         self._labels(part, part_px, pads), self._usb_mark(part_px))

    def _labels(self, part, part_px, pads):
        """The PadLabel of each pad of a part drawn from its record (P412, P945), in its part_px's order, placed by the
        PadLabelLayout its `labels` names; none for any other part."""
        if not part_px.get("pad_labels"):
            return ()
        layout, labels = self.label_layouts[part_px.get("labels", LABELS_BESIDE)], []
        for pad, (x, y) in part_px["pins"].items():
            place = layout.place(x, y, part_px, part.rotate)
            ((at_x, at_y),) = rotate({pad: (place.x, place.y)}, part_px["center"], part.rotate).values()
            labels.append(PadLabel(pad, wiring_steps.pad_word(pad), place, (part.left + at_x, part.top + at_y),
                                   pads.get(pad, PAD_FREE), pad in part_px["doubtful"]))
        return tuple(labels)

    @staticmethod
    def _usb_mark(part_px):
        """The mark at a board's USB end, in its own frame, when it is drawn from its record and its part_px asks for
        one: 34 px wide and 12 high, at the middle of its bottom edge, named in no word, since its place is not
        verified. None for any other part."""
        if not (part_px.get("pad_labels") and part_px.get("usb_mark")):
            return None
        cx, height = part_px["center"][0], part_px["size"][1]
        return BodyBox(cx - 17, height - 12, cx + 17, height)

    def _jumpers(self, layout, paths, pills, grid):
        """The SceneJumper of each jumper, in the layout's order, with its colour's word."""
        colors = self.colors.of({jumper.step: jumper.role for jumper in layout.jumpers})
        return tuple(SceneJumper(jumper, paths[jumper.step], tuple(grid.cell(x, y) for x, y in paths[jumper.step].points),
                                 colors[jumper.step], pills[jumper.step]) for jumper in layout.jumpers)

    @staticmethod
    def _joined_groups(layout):
        """The hole groups that join something: the group of each jumper's end, and each group with pins of two parts."""
        parts_in = collections.defaultdict(set)
        for part in layout.parts:
            for hole in part.holes.values():
                parts_in[hole.group].add(part.id)
        ends = {hole.group for jumper in layout.jumpers for hole in (jumper.one, jumper.other)}
        return ends | {group for group, parts in parts_in.items() if len(parts) > 1}
