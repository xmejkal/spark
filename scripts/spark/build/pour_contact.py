"""
A pour short that tsci reports, measured on the circuit's own copper (P957). The pinned tsci asks a geometry library
whether a trace's outline holds a corner of the pour, and that library calls a point inside when the trace's round end
comes within 1e-6 mm of the corner's edge line, even far from the trace. So a short to a trace is measured here: the
pour's rings against each piece of the trace's copper on the pour's layer. Spark drops it only when the copper keeps the
board's clearance, and names it with its gap. Anything it cannot measure keeps its error.
"""

import math
import re

#: tsci's words for a pour short: the pour, the other copper's id in brackets, the layer.
SHORT = re.compile(r"Copper pour (\S+) \(.*\) shorts to .* \((\S+)\) on (top|bottom) \(accidental copper contact\)")
#: What a dropped short says, in the build stage's detail.
DROPPED = "a pour short tsci reported is dropped: %s and %s on %s are %.4f mm apart, at least the board's clearance of %g mm"


class Unmeasurable(Exception):
    """A piece of the circuit spark does not read, so the error it would measure stays."""


def number(value):
    """A finite number, or Unmeasurable: never a bool, a text or a NaN."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise Unmeasurable(value)
    return float(value)


def xy(point):
    return number(point.get("x")), number(point.get("y"))


class PourContact:
    """One built circuit's pours and traces, read once; `disproved` asks it about each error the build stage counted."""

    def __init__(self, circuit):
        self.circuit = circuit

    def disproved(self, errors):
        """(the errors that stay, a note for each one dropped). The bar is the board's own clearance,
        `min_trace_to_pad_edge_clearance`: tsci cuts its pours 0.2 mm from other copper, a setting circuit.json does not
        hold, and straight pieces of a curved cut come out a little closer, so the bar is the board's lower rule."""
        kept, notes = [], []
        for error in errors:
            gap, bar = self.measured(error), self.clearance()
            if gap is None or bar is None or gap < bar:
                kept.append(error)
                continue
            pour, trace, layer = SHORT.fullmatch(error["message"]).groups()
            notes.append(DROPPED % (pour, trace, layer, gap, bar))
        return kept, notes

    def clearance(self):
        try:
            return number(self.one("pcb_board", "type", "pcb_board").get("min_trace_to_pad_edge_clearance"))
        except Unmeasurable:
            return None

    def measured(self, error):
        """The gap in mm between the pour and the trace `error` names, at most 0 when they touch; None for an error
        that is no pour short to a trace, or for copper spark does not read."""
        if error.get("type") != "pcb_placement_error":
            return None
        said = SHORT.fullmatch(str(error.get("message") or ""))
        if not said:
            return None
        pour_id, trace_id, layer = said.groups()
        try:
            pour = self.one("pcb_copper_pour", "pcb_copper_pour_id", pour_id)
            if pour.get("layer") != layer or pour.get("shape") != "brep":
                return None
            return gap(rings_of(pour), pieces(self.one("pcb_trace", "pcb_trace_id", trace_id).get("route"), layer))
        except (Unmeasurable, AttributeError, KeyError, TypeError):
            return None

    def one(self, kind, key, value):
        """The one element of type `kind` whose `key` is `value`; Unmeasurable when there is none or more than one."""
        found = [element for element in self.circuit if element.get("type") == kind and element.get(key) == value]
        if len(found) != 1:
            raise Unmeasurable(value)
        return found[0]


def rings_of(pour):
    """The pour's outer ring and its holes, each a list of (x, y). A vertex with any key but x and y (a bulge, an arc) is
    no straight edge, so Unmeasurable."""
    shape = pour["brep_shape"]
    rings = []
    for ring in [shape["outer_ring"]] + list(shape.get("inner_rings") or []):
        if any(set(vertex) != {"x", "y"} for vertex in ring["vertices"]):
            raise Unmeasurable(ring)
        rings.append([xy(vertex) for vertex in ring["vertices"]])
    return rings


def pieces(route, layer):
    """The trace's copper on `layer` as (start, end, radius): each wire between two route points, a via's disk (a piece
    with no length) and a through-pad's stroke. A via and a through-pad count on every layer, which can only add copper.
    A wire counts unless one of its ends is a wire on another layer."""
    found = []
    for point in route:
        kind = point.get("route_type")
        if kind == "via":
            radius = number(point.get("outer_diameter", point.get("via_diameter"))) / 2
            found.append((xy(point), xy(point), radius))
        elif kind == "through_pad":
            found.append((xy(point["start"]), xy(point["end"]), number(point.get("width")) / 2))
        elif kind != "wire":
            raise Unmeasurable(kind)
    for a, b in zip(route, route[1:]):
        if any(end.get("route_type") == "wire" and end.get("layer") != layer for end in (a, b)):
            continue
        start = a["end"] if a.get("route_type") == "through_pad" else a
        end = b["start"] if b.get("route_type") == "through_pad" else b
        found.append((xy(start), xy(end), number(a.get("width", b.get("width"))) / 2))
    return found


def gap(rings, copper):
    """The smallest distance from any piece's edge to the pour's edge; at most 0 when a piece's end lies inside the pour."""
    if not copper:
        raise Unmeasurable(copper)
    edges = [(ring[i - 1], ring[i]) for ring in rings for i in range(len(ring))]
    nearest = min(segment_distance(start, end, a, b) - radius for start, end, radius in copper for a, b in edges)
    if any(inside(point, rings) for start, end, _ in copper for point in (start, end)):
        return min(nearest, 0.0)
    return nearest


def inside(point, rings):
    """Whether `point` lies inside the pour: an even-odd count over all its rings, half-open, with no tolerance."""
    x, y = point
    crossings = 0
    for ring in rings:
        for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
            if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                crossings += 1
    return crossings % 2 == 1


def segment_distance(p, q, a, b):
    """The distance between segments pq and ab: 0 when they cross, else the nearest end to the other segment."""
    if side(p, q, a) * side(p, q, b) < 0 and side(a, b, p) * side(a, b, q) < 0:
        return 0.0
    return min(point_distance(p, a, b), point_distance(q, a, b), point_distance(a, p, q), point_distance(b, p, q))


def side(p, q, r):
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])


def point_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = dx * dx + dy * dy
    t = 0.0 if length == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)
