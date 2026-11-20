"""
The way each jumper runs on the drawn breadboard (P953, #1359): around the parts, on tracks between the holes, never
over a part's body. `svg_diagram` draws each JumperPath that a JumperRouter gives it.

The grid (`TrackGrid`) has a cell every half a pitch, from the first column and row a. A hole lies on an even cell. A
track is an odd line: a horizontal track lies half a pitch off a row of holes, a vertical one half a pitch off a column,
so two wires on two tracks are one pitch apart. The grid reaches past the board on each side (left of column 1, above
the top numbers and below the bottom ones), so a wire can go round a part that reaches the board's end. A cell within
half a pitch of a part's body or of a printed letter or number is blocked, and a run never lies within half a pitch of a
rail's line.

`TrackJumperRouter` finds each path with A* (cost 1 a cell, 2 outside the board, 4 a bend, 6 a crossing), the
jumpers in the order of the lanes (shortest span first, then step), so runs nest. A wire leaves its hole half a pitch
along its column to a track, runs on tracks only, and comes into its other hole the same way; it has at most 4 bends,
shares no piece of a track with another wire, crosses another only at a right angle and at least a pitch from a bend
or an end of either, and lies in a band of at most 4 wires side by side. A jumper with no such path gets one with up to
8 bends, drawn dashed; one with none at all is not drawn, and the picture's note says so. `LaneJumperRouter` is the
older way (P947), one lane per jumper across, which may cross a part.
"""

import collections
import heapq
import math

from spark.breadboard.drawing import _round_px
from spark.breadboard.spacing import BodyBox

#: Value: one jumper's drawn way, its points in px from its first hole to its other (rounded once), the number of its
#: bends, and `fallback`: "" when it keeps every rule, BENDS when it needs more than MAX_BENDS, NO_WAY when no way was
#: found (no points: it is not drawn).
JumperPath = collections.namedtuple("JumperPath", "points bends fallback")
BENDS, NO_WAY = "bends", "no_way"

#: Value: what a wire keeps clear of in one drawing, as BodyBoxes in px: the board's body (`board`; a run off it costs
#: more), each part's body (`bodies`), each printed letter and number (`marks`), and each rail's line, (y, left, right)
#: (`lines`), which a run may cross but not lie along.
Obstacles = collections.namedtuple("Obstacles", "board bodies marks lines")

#: The four ways to move on the grid, in the order the search tries them: right, down, left, up.
MOVES = ((1, 0), (0, 1), (-1, 0), (0, -1))
HORIZONTAL, VERTICAL = "h", "v"


class JumperRouter:
    """Strategy: `route(layout, obstacles)` gives {step: JumperPath} for every jumper of the layout."""

    def route(self, layout, obstacles):
        raise NotImplementedError


class LaneJumperRouter(JumperRouter):
    """
    Strategy: the height of each jumper's run across (P947), so that no two jumpers share a drawn line. A run lies half
    a pitch off its far end's row, on the side of its first end (below the row when both ends share it), and further
    lines on that side are one pitch apart, so a run never lies on a row of holes. Jumpers take their lines shortest
    span first, then by step, so runs nest; each takes the first line where no run comes within one pitch of its
    span, a gap of one pitch included. When a leg would pass over another jumper's end in its column, or run along a
    leg already drawn there, the other side is tried first, then lines further out. It sees no part's body.
    """

    def route(self, layout, obstacles):
        across = self.lines(layout.jumpers, layout.geometry.surface.pitch)
        return {jumper.step: JumperPath(tuple((_round_px(x), _round_px(y)) for x, y in (
            (jumper.one.x, jumper.one.y), (jumper.one.x, across[jumper.step]), (jumper.other.x, across[jumper.step]),
            (jumper.other.x, jumper.other.y))), 2, "") for jumper in layout.jumpers}

    def lines(self, jumpers, pitch):
        """{step: the y of its run across}."""
        ends = [(hole.x, hole.y, jumper.step) for jumper in jumpers for hole in (jumper.one, jumper.other)]
        rows = [y for _, y, _ in ends]
        depths = len(jumpers) + int((max(rows) - min(rows)) / pitch) + 2 if rows else 0
        taken, legs, lines = [], [], {}
        for jumper in sorted(jumpers, key=lambda one: (abs(one.one.x - one.other.x), one.step)):
            low, high = sorted((jumper.one.x, jumper.other.x))
            free = [y for y in self._candidates(jumper, pitch, depths)
                    if not any(abs(y - y2) < pitch / 4 and low <= high2 + pitch and low2 <= high + pitch
                               for y2, low2, high2 in taken)]
            clear = [y for y in free if not self._crosses_an_end(jumper, y, ends) and not self._runs_along(jumper, y, legs)]
            lines[jumper.step] = (clear or free)[0]
            taken.append((lines[jumper.step], low, high))
            legs += [(hole.x, *sorted((hole.y, lines[jumper.step]))) for hole in (jumper.one, jumper.other)]
        return lines

    @staticmethod
    def _candidates(jumper, pitch, count):
        """The lines a jumper may take, in the order it tries them: its own side first, unless a leg there would pass over
        another jumper's end, then the other side."""
        one, other = jumper.one, jumper.other
        side = -1 if other.y > one.y else 1
        return [other.y + toward * (pitch / 2 + depth * pitch) for toward in (side, -side) for depth in range(count + 1)]

    @staticmethod
    def _runs_along(jumper, y, legs):
        """True when a leg of the jumper, from one of its holes to the run at `y`, overlaps a leg drawn in its column."""
        return any(abs(x - hole.x) < 0.5 and min(high, max(hole.y, y)) - max(low, min(hole.y, y)) > 0
                   for hole in (jumper.one, jumper.other) for x, low, high in legs)

    @staticmethod
    def _crosses_an_end(jumper, y, ends):
        """True when a leg of the jumper, from one of its holes to the run at `y`, passes over another jumper's end."""
        return any(abs(x - hole.x) < 0.5 and min(hole.y, y) < end_y < max(hole.y, y)
                   for hole in (jumper.one, jumper.other) for x, end_y, step in ends if step != jumper.step)


class TrackGrid:
    """
    Value: the half-pitch grid of one drawing. `cell(x, y)` and `point(cell)` turn px into cells and back. `free(cell)`
    is False on a hole, inside a body or a mark grown by half a pitch, or past the grid's extent, which is the board and
    every body with OUTER_TRACKS tracks round them. `beside_a_line(cell)` is True within half a pitch of a rail's line,
    and `outside(cell)` off the board's body.
    """

    #: The tracks the grid reaches past the board and every body, on each side.
    OUTER_TRACKS = 4

    def __init__(self, surface, obstacles):
        board, bodies, marks, lines = obstacles
        self.step = surface.pitch / 2
        self.x0, self.y0 = min(hole.x for hole in surface.terminal), min(surface.letters_y.values())
        self.board, self.bodies = board, list(bodies)
        boxes = [board] + self.bodies
        reach = (2 * self.OUTER_TRACKS + 1) * self.step
        self.low = self._cells(min(box.left for box in boxes) - reach, min(box.top for box in boxes) - reach, math.floor)
        self.high = self._cells(max(box.right for box in boxes) + reach, max(box.bottom for box in boxes) + reach, math.ceil)
        self.holes = {self.cell(hole.x, hole.y) for hole in surface.holes}
        self.blocked = set().union(*[self._within(box, self.step) for box in self.bodies + list(marks)])
        self.lines = set().union(*[self._within(BodyBox(left, y, right, y), self.step) for y, left, right in lines])

    def cell(self, x, y):
        return self._cells(x, y, round)

    def point(self, cell):
        return self.x0 + cell[0] * self.step, self.y0 + cell[1] * self.step

    def within(self, cell):
        u, v = cell
        return self.low[0] <= u <= self.high[0] and self.low[1] <= v <= self.high[1]

    def free(self, cell):
        return self.within(cell) and cell not in self.blocked and cell not in self.holes

    def beside_a_line(self, cell):
        return cell in self.lines

    def outside(self, cell):
        return not _strictly_in(self.board, self.point(cell), 0)

    def touches_a_body(self, cell, by):
        """True when the cell lies less than `by` px from a part's body."""
        return any(_strictly_in(box, self.point(cell), by) for box in self.bodies)

    def _cells(self, x, y, rounding):
        return rounding((x - self.x0) / self.step), rounding((y - self.y0) / self.step)

    def _within(self, box, by):
        """The cells less than `by` px from the box."""
        low, high = self._cells(box.left - by, box.top - by, math.floor), self._cells(box.right + by, box.bottom + by, math.ceil)
        return {(u, v) for u in range(low[0], high[0] + 1) for v in range(low[1], high[1] + 1)
                if _strictly_in(box, self.point((u, v)), by)}


def _strictly_in(box, point, by):
    x, y = point
    return box.left - by < x < box.right + by and box.top - by < y < box.bottom + by


class TrackJumperRouter(JumperRouter):
    """Strategy: each jumper on the tracks of a TrackGrid, around every body (the module's docstring has the rules and
    the costs). `routing(...)` gives the TrackRouting of one drawing, which also counts the states its searches took."""

    def route(self, layout, obstacles):
        return self.routing(layout, obstacles).paths

    @staticmethod
    def routing(layout, obstacles):
        return TrackRouting(layout, obstacles)


#: Value: one search's jumper, its holes' cells, the cells next to them along their column (`legs`), its most bends, and
#: `close`: True for a last try, drawn dashed, which may pass beside another jumper's end or run half a pitch from a wire.
Search = collections.namedtuple("Search", "step start goal legs most close")


class TrackRouting:
    """
    Value: one drawing's routing, worked out once when it is made: the grid, the cells each wire holds (`axes`, by
    axis), the cells a run along an axis may not enter (`near`: next to a run along that axis, end to end or side by
    side, so two runs keep a pitch apart), the cells a crossing may not take (`no_cross`, within a pitch of a bend or an
    end), and the cells beside each end hole (`rings`, which only its own jumper may take, as a wire there would touch
    the end's dot). `paths` is {step: JumperPath}; `expanded` counts the states the searches took, the budget a test
    pins in place of seconds; `cut_short` counts the searches BUDGET stopped before they found a way or ran out of
    states, since such a stop is no proof that there is no way.
    """

    #: The costs of the search: a cell on the board, a cell off it, a cell of a run beside a rail's line, a bend, a
    #: crossing.
    CELL, OUTSIDE, BESIDE_A_LINE, BEND, CROSS = 1, 2, 2, 4, 6
    #: The most bends of a wire, of a wire drawn dashed, and the most wires side by side in one band.
    MAX_BENDS, FALLBACK_BENDS, BAND = 4, 8, 4
    #: The tries for each jumper not yet routed, in order: (its most bends, its fallback, whether it may come close).
    TRIES = ((MAX_BENDS, "", False), (FALLBACK_BENDS, BENDS, False), (FALLBACK_BENDS, BENDS, True))
    #: How close to a part's body a wire's leg out of its hole may come, in px: the white under-stroke's half width.
    LEG_CLEARANCE = 2.5
    #: The most states one search may take before it gives up.
    BUDGET = 60000

    def __init__(self, layout, obstacles):
        self.grid = TrackGrid(layout.geometry.surface, obstacles)
        self.axes, self.near, self.no_cross, self.rings = {}, {}, set(), {}
        for jumper in layout.jumpers:
            for hole in (jumper.one, jumper.other):
                u, v = self.grid.cell(hole.x, hole.y)
                for du, dv in MOVES:
                    self.rings.setdefault((u + du, v + dv), set()).add(jumper.step)
        self.expanded, self.cut_short, self.paths = 0, 0, {}
        order = sorted(layout.jumpers, key=lambda one: (abs(one.one.x - one.other.x), one.step))
        for most, fallback, close in self.TRIES:
            for jumper in [one for one in order if one.step not in self.paths]:
                cells = self._search(self._of(jumper, most, close))
                if cells:
                    self.paths[jumper.step] = self._taken(jumper, cells, fallback)
        for jumper in order:
            self.paths.setdefault(jumper.step, JumperPath((), 0, NO_WAY))

    def _of(self, jumper, most, close):
        start, goal = self.grid.cell(jumper.one.x, jumper.one.y), self.grid.cell(jumper.other.x, jumper.other.y)
        legs = {(u, v + dv) for u, v in (start, goal) for dv in (1, -1)}
        return Search(jumper.step, start, goal, legs, most, close)

    def _search(self, search):
        """The cells of the cheapest way from the search's start to its goal, else None. A state is (u, v, the way it
        came, its bends, the cells since its last bend and since its last crossing, each counted to 2)."""
        heap, parents, costs, closed = [], {}, {}, set()
        for move in (1, 3):
            leg = _step(search.start, move)
            if self._leg_ok(leg, search):
                state = leg + (move, 0, 1, 2)
                parents[state], costs[state] = None, self.CELL
                heapq.heappush(heap, (self.CELL + self._estimate(state, search.goal), self.CELL) + state)
        taken = 0
        while heap and taken < self.BUDGET:
            _, cost, *state = heapq.heappop(heap)
            state = tuple(state)
            if state in closed:
                continue
            closed.add(state)
            taken += 1
            if state[:2] == search.goal:
                self.expanded += taken
                return [search.start] + self._back(state, parents)
            for nxt, extra in self._moves(state, search):
                if nxt not in closed and cost + extra < costs.get(nxt, cost + extra + 1):
                    parents[nxt], costs[nxt] = state, cost + extra
                    heapq.heappush(heap, (cost + extra + self._estimate(nxt, search.goal), cost + extra) + nxt)
        self.expanded += taken
        self.cut_short += bool(heap) and taken >= self.BUDGET
        return None

    def _estimate(self, state, goal):
        """The least the rest of the way can cost: a cell for each cell to the goal and a bend for each bend it must
        still take, since it comes into the goal along the goal's column."""
        u, v, came, *_ = state
        du, dv = goal[0] - u, goal[1] - v
        if came in (1, 3):
            bends = 0 if du == 0 and dv * MOVES[came][1] > 0 else 2
        else:
            bends = 1 if du * MOVES[came][0] > 0 else 3
        return abs(du) + abs(dv) + self.BEND * bends

    def _moves(self, state, search):
        """Each next state and what it costs: straight on, or a bend onto a track; never back. A run across lies on an
        odd row of cells; a run along a column on an odd column, or on its hole's column out of its first hole before
        its first bend, or into its last hole."""
        u, v, came, bends, straight, crossed = state
        for move, (du, dv) in enumerate(MOVES):
            axis = HORIZONTAL if dv == 0 else VERTICAL
            on_its_column = axis == VERTICAL and (u == search.goal[0] or (u == search.start[0] and bends == 0))
            if move == (came + 2) % 4 or ((v if axis == HORIZONTAL else u) % 2 == 0 and not on_its_column):
                continue
            turn = move != came
            if turn and (bends == search.most or crossed < 2 or not self._bend_ok((u, v), axis, search)):
                continue
            nxt = (u + du, v + dv)
            if nxt == search.goal:
                if axis == VERTICAL:
                    yield nxt + (move, bends + turn, 1, 2), self.CELL + self.BEND * turn
                continue
            if not self._open(nxt, axis, search):
                continue
            run = 1 if turn else min(straight + 1, 2)
            crossing = bool(self.axes.get(nxt))
            if crossing and (nxt in self.no_cross or run < 2):
                continue
            extra = (self.OUTSIDE if self.grid.outside(nxt) else self.CELL) + self.BEND * turn + self.CROSS * crossing
            extra += self.BESIDE_A_LINE * (axis == HORIZONTAL and self.grid.beside_a_line(nxt))
            yield (u + du, v + dv, move, bends + turn, run, 0 if crossing else min(crossed + 1, 2)), extra

    def _open(self, cell, axis, search):
        """True when a run along `axis` may enter the cell: a leg's cell clear for a leg, any other free on the grid,
        beside no other jumper's end, not next to another run along this axis, and no fifth wire in a band."""
        if cell in search.legs:
            return self._leg_ok(cell, search)
        return (self.grid.free(cell) and self._clear_of_ends(cell, search) and axis not in self.axes.get(cell, ())
                and (search.close or axis not in self.near.get(cell, ())) and not self._band_full(cell, axis))

    def _bend_ok(self, cell, axis, search):
        """A bend only on a cell no other wire holds, where a run along `axis` may start."""
        return not self.axes.get(cell) and (search.close or axis not in self.near.get(cell, ()))

    def _band_full(self, cell, axis):
        """True when BAND wires already lie side by side, a pitch apart, across `axis` at this cell."""
        du, dv = (0, 2) if axis == HORIZONTAL else (2, 0)
        count = 0
        for sign in (1, -1):
            k = 1
            while axis in self.axes.get((cell[0] + sign * k * du, cell[1] + sign * k * dv), ()):
                count, k = count + 1, k + 1
        return count >= self.BAND

    def _leg_ok(self, cell, search):
        """A leg out of a hole may cross this cell: on the grid, on no hole, clear of every body by LEG_CLEARANCE,
        beside no other jumper's end, and held by no wire."""
        return (self.grid.within(cell) and cell not in self.grid.holes and not self.grid.touches_a_body(cell, self.LEG_CLEARANCE)
                and self._clear_of_ends(cell, search) and not self.axes.get(cell) and (search.close or not self.near.get(cell)))

    def _clear_of_ends(self, cell, search):
        """True when the cell lies beside no other jumper's end, or the search may come close."""
        return search.close or self.rings.get(cell, set()) <= {search.step}

    @staticmethod
    def _back(state, parents):
        cells = []
        while state is not None:
            cells.append(state[:2])
            state = parents[state]
        return cells[::-1]

    def _taken(self, jumper, cells, fallback):
        """The cells of a found way taken: each held along its axis, its neighbours kept from another run along that
        axis, and a crossing kept a pitch from each bend and end. Gives its JumperPath."""
        for one, other in zip(cells, cells[1:]):
            axis = HORIZONTAL if one[1] == other[1] else VERTICAL
            for u, v in (one, other):
                self.axes.setdefault((u, v), set()).add(axis)
                for du, dv in MOVES if (u, v) not in (cells[0], cells[-1]) else ():  # an end's `rings` keep its sides
                    self.near.setdefault((u + du, v + dv), set()).add(axis)
        corners = [cell for before, cell, after in zip(cells, cells[1:], cells[2:])
                   if (cell[0] - before[0], cell[1] - before[1]) != (after[0] - cell[0], after[1] - cell[1])]
        for u, v in corners + [cells[0], cells[-1]]:
            self.no_cross |= {(u + du, v + dv) for du in (-1, 0, 1) for dv in (-1, 0, 1)}
        points = self._along_the_holes([(jumper.one.x, jumper.one.y)] + [self.grid.point(cell) for cell in corners]
                                       + [(jumper.other.x, jumper.other.y)], self.grid.point(cells[1])[1])
        return JumperPath(tuple((_round_px(x), _round_px(y)) for x, y in points), len(points) - 2, fallback)

    @staticmethod
    def _along_the_holes(points, first_track):
        """The points with each leg along its own hole's x. A rail hole of Wokwi's half board lies off the grid's
        columns (P953), so the corner beside it takes the hole's x; a way with no corner between two holes of different
        x gets two corners on the track next to its first hole (`first_track`, its y)."""
        if len(points) == 2:
            (x1, y1), (x2, y2) = points
            return points if x1 == x2 else [points[0], (x1, first_track), (x2, first_track), points[1]]
        points[1] = (points[0][0], points[1][1])
        points[-2] = (points[-1][0], points[-2][1])
        return points


def _step(cell, move):
    return cell[0] + MOVES[move][0], cell[1] + MOVES[move][1]


