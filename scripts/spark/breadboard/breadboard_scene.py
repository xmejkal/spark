"""
The drawn breadboard as one scene (P969, #1388): `BreadboardScene`, everything a view of the breadboard draws, each
thing with its place, made once by `BreadboardSceneMaker` before any view. The maker reads the board's marks
(`board_marks`), routes the jumpers (a `wire_routing.JumperRouter`), picks each wire's colour (`wiring_steps`), and
places the pills (`wire_pills`) and the captions (`part_captions`) through a `LabelMeasure`, the room a label takes as
one view draws it. So no view places a pill or a caption: `svg_diagram` draws the scene in px, and a view in
characters reads the same scene through its grid (`SceneGrid`). The pad labels are not in the scene yet: `svg_diagram`
places them. Nothing here draws.
"""

import collections
import math

from spark.breadboard import wire_routing, wiring_steps
from spark.breadboard.board_marks import BoardMarks, BoardPalette
from spark.breadboard.part_captions import PartCaption
from spark.breadboard.spacing import BodyBox
from spark.breadboard.wire_pills import WIRE_SIZES_PX, PillLayout, wire_boxes


class LabelMeasure:
    """Strategy: the room a label takes on the drawn breadboard as one view draws it, in the scene's px, so that the
    maker places every pill and caption for that view: `pill(words)` gives (width, height) of a wire's pill with these
    words, along its words and across them; `caption(words)` gives (size, width) of a part's caption, its height and
    its width."""

    def pill(self, words):
        raise NotImplementedError

    def caption(self, words):
        raise NotImplementedError


class PxLabelMeasure(LabelMeasure):
    """Strategy: the labels as the SVG draws them, in its px: a pill PILL_HEIGHT high, with DISC_ROOM for the white
    disc with its number, END_ROOM after its words, and PER_CHARACTER a character of its words (6.1 px bold); a
    caption at the palette's `caption_size`, CAPTION_PER_CHARACTER of it a character plus CAPTION_ROOM of it."""

    #: The pill's height, the room its disc takes, the room after its words, and the width a character of its words takes,
    #: in px: the old page's at spark's pitch (the visual spec, section 7, P953).
    PILL_HEIGHT, DISC_ROOM, END_ROOM, PER_CHARACTER = 9.6, 9.6, 3.6, 3.57
    #: The width a character of a caption takes, and the room added to its words' width, each times its size. Chrome
    #: draws the fixtures' names 0.50 to 0.54 of the size a character wide.
    CAPTION_PER_CHARACTER, CAPTION_ROOM = 0.55, 0.5

    def __init__(self, caption_size):
        self.caption_size = caption_size

    def pill(self, words):
        return self.DISC_ROOM + self.END_ROOM + self.PER_CHARACTER * len(words), self.PILL_HEIGHT

    def caption(self, words):
        return self.caption_size, (self.CAPTION_PER_CHARACTER * len(words) + self.CAPTION_ROOM) * self.caption_size


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


#: Value: one part in the scene: its PlacedPart, its BodyBox and its Caption.
ScenePart = collections.namedtuple("ScenePart", "part body caption")
#: Value: one jumper in the scene: its Jumper, its JumperPath in px, the grid's cell of each of the path's points, its
#: colour's word (`wiring_steps.JumperColors`) and its WirePill.
SceneJumper = collections.namedtuple("SceneJumper", "jumper path cells color pill")


class BreadboardScene(collections.namedtuple("BreadboardScene", "layout marks parts jumpers joined grid")):
    """
    Value: everything a view of one drawn breadboard draws, each with its place in px: the BreadboardLayout it was made
    from, the breadboard's BoardMarks, each part (ScenePart) and each jumper (SceneJumper) in the
    layout's order, the hole groups that join something (`joined`), and its SceneGrid. `wire_notes()` gives the
    sentences of the wires drawn dashed and of those not drawn.
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


class BreadboardSceneMaker:
    """
    Service: makes the BreadboardScene of a layout, once, before any view: the board's marks at the `palette`'s sizes,
    each part's body, each jumper's way from the `router` (a JumperRouter, swapped here and never in a view), each
    wire's colour from `colors`, then each pill (PillLayout) and each caption (PartCaption), placed through the
    `measure` (a LabelMeasure; PxLabelMeasure, the SVG's, by default).
    """

    def __init__(self, colors=None, router=None, palette=None, measure=None):
        self.colors = colors or wiring_steps.JumperColors()
        self.router = router or wire_routing.TrackJumperRouter()
        self.palette = palette or BoardPalette.load()
        self.measure = measure or PxLabelMeasure(self.palette.sizes["caption"])
        self.pill_layout = PillLayout(WIRE_SIZES_PX.under_stroke, WIRE_SIZES_PX.end_dot + WIRE_SIZES_PX.end_ring / 2, self.measure)

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
        parts = tuple(ScenePart(part, body, captions[part.id]) for part, body in zip(layout.parts, bodies))
        return BreadboardScene(layout, marks, parts, self._jumpers(layout, paths, pills, grid),
                               frozenset(self._joined_groups(layout)), grid)

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
