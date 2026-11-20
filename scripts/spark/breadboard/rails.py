"""
Power and ground on the drawn breadboard's rails (P953, #1359): which rail each signed mark takes (`RailSeating`), and
the rail holes a part's body covers, which no rail jumper may take (`rail_holes_under`), and a rail hole's words
(`hole_words`). `drawing`'s planner reads them. Nothing here imports `drawing`.
"""

import collections


class RailSeating:
    """
    Service: the rail each signed mark takes, built for one plan. A point's side is the side of the board (t or b, the
    last letter of a row's group) that holds most of its ends, on a tie its first end's side. The first mark of a sign
    takes that side's rail of the sign (+ is a "p" rail, - an "n" rail), a second the other side's, and a third gets
    none. No bridge joins the two sides' rails: the steps would have to say it.
    """

    #: The last letter of a rail of each sign.
    LETTERS = {"+": "p", "-": "n"}

    def __init__(self, surface):
        self.rails = list(surface.rails)
        self.used = []

    def group(self, mark, sign, sides):
        """The rail group `mark` takes, `sides` the side of each of its ends in step order; None when its sign has no
        free rail left."""
        counts = collections.Counter(sides)
        side = max(counts, key=lambda one: (counts[one], one == sides[0]))
        others = [rail[0] for rail in self.rails if rail[0] != side]
        for rail in [side + self.LETTERS.get(sign, "")] + [one + self.LETTERS.get(sign, "") for one in others]:
            if rail in self.rails and rail not in self.used:
                self.used.append(rail)
                return rail
        return None


def rail_holes_under(boxes, surface):
    """The rail holes that a body of `boxes` (BodyBoxes) covers or comes within half a pitch of, in surface order: a
    rail jumper takes none of them, so a person can reach its hole and its wire's leg clears the body."""
    near = surface.pitch / 2
    return [hole for hole in surface.holes if not hole.column and any(
        box.left - near < hole.x < box.right + near and box.top - near < hole.y < box.bottom + near for box in boxes)]


#: The words of a rail group's letters: its side, then its sign.
RAIL_SIDES, RAIL_SIGNS = {"t": "top", "b": "bottom"}, {"p": "+", "n": "-"}


def hole_words(hole):
    """What a person reads for a rail hole, by its side, sign and number (top + rail, hole 3 for tp.3); None for a
    group of no known rail name."""
    group, _, number = hole.name.partition(".")
    if len(group) == 2 and group[0] in RAIL_SIDES and group[1] in RAIL_SIGNS:
        return "%s %s rail, hole %s" % (RAIL_SIDES[group[0]], RAIL_SIGNS[group[1]], number)
    return None
