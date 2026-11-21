"""
What the breadboard prints on itself (P969, #1388): `BoardPalette`, the picture's look as data, and `BoardMarks`, the
board's body, its gap band, its rail holes, its row letters, its column numbers, each rail's line and each rail's + or -
sign, each with its place and its box in px, and each mark's baseline from the drop of the scene's label measure
(`label_measure`). The facts are made from the surface, the sizes and the measure alone, with no picture drawn, so the
router, the pills and any other view read the marks one way. `svg_diagram` draws them; `wire_routing` keeps its wires clear of them.
"""

import collections
import json
from pathlib import Path

from spark.breadboard import wire_routing
from spark.breadboard.drawing import BREADBOARDS_FILE
from spark.breadboard.spacing import BodyBox


class BoardPalette(collections.namedtuple("BoardPalette", "colors sizes")):
    """Value: the breadboard picture's look (P953): `colors`, {what: hex}, and `sizes`, {what: px}, the `palette` and
    `sizes_px` of data/breadboards.json. Another look is another file, with no code."""

    @classmethod
    def load(cls, path=BREADBOARDS_FILE):
        data = json.loads(Path(path).read_text())
        return cls(data["palette"], data["sizes_px"])


class BoardMarks(collections.namedtuple("BoardMarks", "surface sizes measure")):
    """Value: the marks printed on one breadboard `surface`, at the `sizes` of a BoardPalette (px): the body, the gap
    band between its halves, the rail holes and which rail is +, the row letters and column numbers (`texts`), each
    rail's line (`rail_lines`) and its sign (`signs`), each mark's baseline through the drop of the `measure` (a
    `label_measure.LabelMeasure`), and the boxes that a wire (`obstacles`) and a pill (`sign_boxes`) keep clear of.
    It draws nothing."""

    def box(self):
        """The board's body: every hole and `board_pad` round them."""
        holes, pad = self.surface.holes, self.sizes["board_pad"]
        return BodyBox(min(hole.x for hole in holes) - pad, min(hole.y for hole in holes) - pad,
                       max(hole.x for hole in holes) + pad, max(hole.y for hole in holes) + pad)

    def gap_band(self):
        """The band across the board's body between its two halves, `gap_band` high, about the middle between the last
        top row and the first bottom row."""
        surface, box = self.surface, self.box()
        top, bottom = surface.top_letters, [letter for letter in surface.letters_y if letter not in surface.top_letters]
        middle = (surface.letters_y[top[-1]] + surface.letters_y[bottom[0]]) / 2
        return BodyBox(box.left, middle - self.sizes["gap_band"] / 2, box.right, middle + self.sizes["gap_band"] / 2)

    def rail_holes(self):
        """The holes of the rails: those in no column."""
        return [hole for hole in self.surface.holes if not hole.column]

    @staticmethod
    def plus(rail):
        """True for a + rail (its name ends in p: tp, bp)."""
        return rail.endswith("p")

    def baseline(self, middle, size):
        """The baseline, a y, of a mark `size` px high whose letters' middle lies at `middle`: the measure's drop below
        it."""
        return middle + self.measure.mark_drop(size)

    def texts(self):
        """(text, x, y of its middle, font size) of each row letter, at the left edge, then each column number (1 and
        every `numbers_every`), above the top rails and below the bottom rails."""
        surface, sizes = self.surface, self.sizes
        left = min(hole.x for hole in surface.terminal) - surface.pitch
        letters = [(letter, left, y, sizes["letters"]) for letter, y in surface.letters_y.items()]
        columns = sorted({hole.column: hole.x for hole in surface.terminal}.items())
        said = [(column, x) for column, x in columns if column == 1 or column % sizes["numbers_every"] == 0]
        return letters + [(str(column), x, y, sizes["numbers"]) for y in (
            min(hole.y for hole in surface.holes) - surface.pitch, max(hole.y for hole in surface.holes) + surface.pitch)
            for column, x in said]

    def rail_lines(self):
        """(its rail, its holes' y, its line's y, left, right) of each rail: the line lies on the side of its holes away
        from the other rail of its pair."""
        rail_holes, found = self.rail_holes(), []
        for rail in self.surface.rails:
            row = [hole for hole in rail_holes if hole.group == rail]
            partner = next((hole.y for hole in rail_holes if hole.group != rail and hole.group[0] == rail[0]), None)
            away = (1 if row[0].y > partner else -1) if partner is not None else (-1 if self.plus(rail) else 1)
            found.append((rail, row[0].y, row[0].y + away * self.sizes["rail_line_off"],
                          min(hole.x for hole in row), max(hole.x for hole in row)))
        return found

    def signs(self):
        """(its rail, x, baseline) of each rail's sign, at the rail's left end, its letters' middle on its holes."""
        size = self.sizes["rail_sign"]
        return [(rail, left - self.surface.pitch, self.baseline(row_y, size)) for rail, row_y, _, left, _ in self.rail_lines()]

    def obstacles(self, bodies):
        """The Obstacles a wire keeps clear of: the board, the `bodies`, each letter's and number's box (0.6 of its
        size wide a character, 0.8 of it high), and each rail's line."""
        marks = [BodyBox(x - 0.3 * size * len(text), y - 0.4 * size, x + 0.3 * size * len(text), y + 0.4 * size)
                 for text, x, y, size in self.texts()]
        return wire_routing.Obstacles(self.box(), tuple(bodies), tuple(marks),
                                      tuple((y, left, right) for _, _, y, left, right in self.rail_lines()))

    def sign_boxes(self):
        """The box of each rail's + or - sign, which a pill keeps clear of (a wire may pass it, so `obstacles` leaves
        it out): 0.6 of its size wide, from 0.4 of its size above the middle of its letters, its rail's holes, to 0.6
        below, whatever the measure's drop."""
        size = self.sizes["rail_sign"]
        return tuple(BodyBox(x - 0.3 * size, middle - 0.4 * size, x + 0.3 * size, middle + 0.6 * size)
                     for (_, middle, *_), (_, x, _) in zip(self.rail_lines(), self.signs()))
