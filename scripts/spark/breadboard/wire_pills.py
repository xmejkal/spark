"""
Where each jumper's pill goes on the drawn breadboard (P969, #1388): `WirePill`, the label on a wire with its step's
number and the two pads it joins (P953), `PillLayout`, the Service that places each in step order clear of everything,
`WireSizes`, the wire's sizes in px, and `wire_boxes`, the boxes a wire, its end dots and its pill take. The places are
made from the jumpers, their paths and the obstacles alone, with no picture drawn, so the picture and any other view
read them one way. `svg_diagram` draws them; `wire_routing` gives the paths.
"""

import collections

from spark.breadboard.spacing import BodyBox

#: Value: a wire's sizes, in px: the white under-stroke, the colored stroke, and the end dot with its white ring.
WireSizes = collections.namedtuple("WireSizes", "under_stroke stroke end_dot end_ring")

#: A wire's sizes in the SVG's px: the praised page's 7.5, 4, 5.5 and 1.5 at its 18 px pitch, times 9.6 / 18 (the
#: visual spec, P953).
WIRE_SIZES_PX = WireSizes(4.0, 2.2, 3.0, 0.8)


class WirePill(collections.namedtuple("WirePill", "step words x y turned free width height")):
    """
    Value: one jumper's pill (P953), the PO's "7  SDI to D11": its step's number at its left end, then its words
    (`Jumper.pill_words`). (x, y) is its centre in px; `turned` when it lies along a column, turned a quarter back so
    it reads bottom to top; `free` is False when no place clear of everything was found and it sits on the middle of
    its wire's longest run. `width`, along its words, and `height`, across them, are the room it takes in px, as the
    view's label measure gives them (P969, `breadboard_scene.LabelMeasure`).
    """

    def box(self):
        """Its BodyBox as drawn: turned along a column when `turned`."""
        across, along = (self.height, self.width) if self.turned else (self.width, self.height)
        return BodyBox(self.x - across / 2, self.y - along / 2, self.x + across / 2, self.y + along / 2)


class PillLayout:
    """
    Service: where each jumper's pill goes (P953), in step order, over the jumpers, their paths and the obstacles it
    is given, each pill as big as the label `measure` says; the scene maker builds one, and no caller swaps it. A pill lies on a straight piece of its own wire,
    centred on its line: first the runs across, longest first, then the runs along a column, turned. On a piece it
    starts at the middle and slides along it, SLIDE px at a time either way, until it is clear of every body and
    printed letter, number or rail sign, every end dot, every other wire and every pill placed before it, by CLEAR px. A pill
    keeps CLEAR px plus half the white under-stroke from each end of its piece, so it never hides a bend. A wire too
    short to hold it (a stub into a rail) gets it across beside a piece, 2 CLEAR off its wire or its end dot, or past
    an end of the wire, along its last piece. A wire with no such place gets its pill on the middle of its longest
    run, not `free`.
    """

    #: How far a pill slides at a time, and the space it keeps from everything it must not touch, in px.
    SLIDE, CLEAR = 1.2, 1.0

    def __init__(self, under_stroke, end_dot, measure):
        """`under_stroke` is the wire's white under-stroke's width and `end_dot` the radius of an end's dot with its
        ring, in px: how far a wire and a dot reach. `measure` (a LabelMeasure) gives each pill's width and height."""
        self.reach, self.dot, self.measure = under_stroke / 2, end_dot, measure

    def place(self, jumpers, paths, obstacles):
        """{step: WirePill} of every jumper, `paths` its JumperPaths and `obstacles` the drawing's
        `wire_routing.Obstacles`, whose bodies and marks (the rail signs among them) a pill keeps clear of."""
        blocked = list(obstacles.bodies) + list(obstacles.marks)
        dots = [(hole.x, hole.y) for jumper in jumpers for hole in (jumper.one, jumper.other)]
        pills = {}
        for jumper in sorted(jumpers, key=lambda one: one.step):
            others = [piece for step, path in paths.items() if step != jumper.step for piece in _pieces(path.points)]
            placed = [one.box() for one in pills.values()]
            pills[jumper.step] = next((pill for pill in self._tries(jumper, paths[jumper.step].points)
                                       if self._clear(pill.box(), blocked, dots, others, placed)),
                                      None) or self._fallback(jumper, paths[jumper.step].points)
        return pills

    def _tries(self, jumper, points):
        """Each place to try, in order: on each run across, longest first, then on each run along a column, turned; on
        each, from its middle out. Then, for a wire too short to hold it (a stub into a rail), across beside each
        piece, longest first: either side of a piece along a column, above or below one across. Then past each end,
        along the wire's last piece there."""
        pieces = sorted(_pieces(points), key=lambda piece: (piece[0][1] != piece[1][1], -_length(piece)))
        pill = self._pill(jumper)
        for (x1, y1), (x2, y2) in pieces:
            turned = x1 == x2
            low, high = sorted((y1, y2) if turned else (x1, x2))
            room = (high - low - pill.width) / 2 - self.reach - self.CLEAR
            for offset in self._slides(room):
                middle = (low + high) / 2 + offset
                yield pill._replace(x=x1, y=middle, turned=True) if turned else pill._replace(x=middle, y=y1)
        for (x1, y1), (x2, y2) in sorted(pieces, key=lambda piece: -_length(piece)):
            along = x1 == x2
            low, high = sorted((y1, y2) if along else (x1, x2))
            for offset in self._slides((high - low) / 2 if along else (high - low - pill.width) / 2):
                middle = (low + high) / 2 + offset
                for side, reach in ((side, reach) for reach in (self.reach, self.dot) for side in (-1, 1)):
                    away = side * ((pill.width if along else pill.height) / 2 + reach + 2 * self.CLEAR)
                    yield pill._replace(x=x1 + away, y=middle) if along else pill._replace(x=middle, y=y1 + away)
        for (x1, y1), (x2, y2) in [(points[1], points[0]), (points[-2], points[-1])] if len(points) > 1 else ():
            turned, sign = x1 == x2, 1 if (y2 - y1 if x1 == x2 else x2 - x1) > 0 else -1
            past = sign * (pill.width / 2 + self.dot + 2 * self.CLEAR)
            yield pill._replace(x=x2, y=y2 + past, turned=True) if turned else pill._replace(x=x2 + past, y=y2)

    def _slides(self, room):
        """The offsets from a piece's middle that keep the pill on it, nearest first."""
        count = int(room // self.SLIDE) if room >= 0 else -1
        return [sign * index * self.SLIDE for index in range(count + 1) for sign in ((1, -1) if index else (1,))]

    def _clear(self, box, blocked, dots, pieces, pills):
        clear = self.CLEAR
        return not (any(box.meets(other, clear) for other in blocked + pills)
                    or any(box.meets(BodyBox(x, y, x, y), self.dot + clear) for x, y in dots)
                    or any(box.meets(BodyBox(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])),
                                     self.reach + clear) for a, b in pieces))

    def _pill(self, jumper):
        """The jumper's pill at (0, 0), across, free, as big as the measure says."""
        return WirePill(jumper.step, jumper.pill_words, 0, 0, False, True, *self.measure.pill(jumper.pill_words))

    def _fallback(self, jumper, points):
        """The pill on the middle of the wire's longest run, or of the line between its holes when it is not drawn."""
        pieces = _pieces(points) or [((jumper.one.x, jumper.one.y), (jumper.other.x, jumper.other.y))]
        (x1, y1), (x2, y2) = max(pieces, key=_length)
        return self._pill(jumper)._replace(x=(x1 + x2) / 2, y=(y1 + y2) / 2, turned=x1 == x2 and y1 != y2, free=False)


def _pieces(points):
    return [piece for piece in zip(points, points[1:]) if piece[0] != piece[1]]


def _length(piece):
    (x1, y1), (x2, y2) = piece
    return abs(x2 - x1) + abs(y2 - y1)


def wire_boxes(jumpers, paths, pills, sizes=WIRE_SIZES_PX):
    """The BodyBoxes of the wires, which a caption keeps clear of: each piece with its white under-stroke, each end
    dot with its ring, and each pill."""
    reach, dot = sizes.under_stroke / 2, sizes.end_dot + sizes.end_ring / 2
    return ([BodyBox(min(a[0], b[0]) - reach, min(a[1], b[1]) - reach, max(a[0], b[0]) + reach,
                     max(a[1], b[1]) + reach) for path in paths.values() for a, b in _pieces(path.points)]
            + [BodyBox(hole.x - dot, hole.y - dot, hole.x + dot, hole.y + dot)
               for jumper in jumpers for hole in (jumper.one, jumper.other)]
            + [pill.box() for pill in pills.values()])
