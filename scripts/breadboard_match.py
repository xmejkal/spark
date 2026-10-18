"""
The drawing check (P279, #317): the drawn breadboard joins the points of circuit.json, and nothing more. The planner
draws from the steps, and since P273 it keeps the moves a person made, so the build asks the drawing it is about to
write which holes it joins, and names each end that differs. `breadboard.py` calls it; nothing here writes a file.

    DrawnNets(layout, geometry).differences(points, catalog)    [DrawingDiffersResult], empty when they match

A net here is the groups the drawing joins: by a jumper, or inside one part (`joined_pins` in
data/wokwi-geometry.json, the pushbutton's two sides of one contact). Only the pins that the points name are checked:
a wire into the row of a pin in no point is not seen.
"""

import collections

import breadboard_drawing

#: The codes of DrawingDiffersResult. A code decides; the message beside it in MESSAGES is what a person reads.
NOT_JOINED = "not-joined"
JOINED_TO_OTHER = "joined-to-other"
CODES = (NOT_JOINED, JOINED_TO_OTHER)
MESSAGES = {
    NOT_JOINED: "%s is not joined to %s in the drawing",
    JOINED_TO_OTHER: "%s is joined to %s in the drawing, and they are two points",
}


class DrawingDiffersResult(collections.namedtuple("DrawingDiffersResult", "subject code why")):
    """Result: one end the drawing joins differently from the points, with a code from CODES and the reason a person
    reads."""

    __slots__ = ()

    @property
    def line(self):
        return self.why


class DrawnNets:
    """Value: which groups of the breadboard one layout joins, by its jumpers and inside its parts."""

    def __init__(self, layout, geometry):
        self.placed = {part.id: part for part in layout.parts}
        self._parent = {}
        for jumper in layout.jumpers:
            self._join(jumper.one.group, jumper.other.group)
        for part in layout.parts:
            for pins in (geometry.data["parts"].get(part.type) or {}).get("joined_pins", ()):
                groups = [part.holes[pin].group for pin in pins if pin in part.holes]
                for group in groups[1:]:
                    self._join(groups[0], group)

    def net_of(self, group):
        """The net of one group: the same value for every group joined with it."""
        while self._parent.get(group, group) != group:
            group = self._parent[group]
        return group

    def _join(self, one, other):
        one, other = self.net_of(one), self.net_of(other)
        if one != other:
            self._parent[other] = one

    def differences(self, points, catalog):
        """[DrawingDiffersResult], in the order of the points: each end not joined to its point's first end, then each
        end joined to an earlier point, one per pair of points."""
        found, owner, said = [], {}, set()
        for number, point in enumerate(points):
            ends = [(end, self.net_of(breadboard_drawing.end_group(end, self.placed, catalog))) for end in point.ends]
            if not ends:
                continue
            first, first_net = ends[0]
            found += [DrawingDiffersResult(end.name, NOT_JOINED, MESSAGES[NOT_JOINED] % (end.name, first.name))
                      for end, net in ends[1:] if net != first_net]
            for end, net in ends:
                other, other_end = owner.setdefault(net, (number, end))
                if other != number and (other, number) not in said:
                    said.add((other, number))
                    found.append(DrawingDiffersResult(end.name, JOINED_TO_OTHER,
                                                      MESSAGES[JOINED_TO_OTHER] % (end.name, other_end.name)))
        return found
