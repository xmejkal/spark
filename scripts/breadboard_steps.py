"""
The wiring of one build as numbered steps, one connection each, and as a mermaid diagram whose edges are those steps
(P202, #161). `breadboard.py` builds it from the built circuit; this module knows nothing of circuits, records or the
drawer.

Each part goes into the breadboard first, each pin in its own row, because its pins then sit in fixed rows. Then each
point gets an anchor (its first part pin, else its first resistor end, else its board pin, or a rail when its ends do
not fit one row), and every other end joins the anchor in one step: a jumper, or a resistor leg. Spark claims no row
numbers, no rail colour and no side of the gap, because it does not know them.
"""

import collections

#: What an end is: a pad of the board, a pin of a part, or one end of a resistor a part asks for.
BOARD, PART, RESISTOR = "board", "part", "resistor"

#: One end of a connection: its kind, the component it belongs to (one diagram box each), its short name in the
#: diagram and the words the steps say.
End = collections.namedtuple("End", "kind component node text")
#: One connection point: its ends (the board's first), the supply from off the board on it, and whether it goes on a rail.
StepPoint = collections.namedtuple("StepPoint", "ends supply rail")


class BreadboardSteps:
    """Value: the steps and the diagram of one build, from the parts to place and the points to join."""

    def __init__(self, parts, points):
        self.parts = list(parts)
        self.points = list(points)

    def _walk(self):
        """[(the step's words, (one node, the other) or None)], in order: each part placed, then each point joined."""
        walked = [("Put %s in the breadboard, each pin in its own row." % part, None) for part in self.parts]
        for point in self.points:
            if point.rail:
                anchor, others = None, point.ends
            else:
                anchor = next((end for kind in (PART, RESISTOR, BOARD) for end in point.ends if end.kind == kind), None)
                others = [end for end in point.ends if end is not anchor]
                if anchor.kind == RESISTOR:
                    walked.append(("Put %s, in a free row." % anchor.text, None))
            rail = point.rail and (point.supply or _rail_name(point))
            for number, end in enumerate(others):
                if rail:
                    there = ("a free rail. Mark it %s" % rail) if number == 0 else "the %s rail" % rail
                    target = "rail:" + rail
                else:
                    there, target = _where(anchor), anchor.node
                if end.kind == RESISTOR:
                    words = "Put %s, in %s." % (end.text, there)
                elif end.kind == BOARD:
                    words = "Run a jumper from %s to %s." % (end.text, there)
                else:
                    words = "Run a jumper from the row of %s to %s." % (end.text, there)
                walked.append((words, (end.node, target)))
            if point.supply:
                there = ("the %s rail" % rail) if rail else _where(anchor)
                walked.append(("Connect the %s supply, from off the board, to %s. Check its voltage first (Before you "
                               "power it)." % (point.supply, there), ("supply:" + point.supply,
                                                                        "rail:" + rail if rail else anchor.node)))
        return walked

    def list_steps(self):
        """The numbered steps, as Markdown lines."""
        return ["%d. %s" % (number, words) for number, (words, _) in enumerate(self._walk(), 1)]

    def draw_mermaid(self):
        """A mermaid flowchart: a box per component, a node per end, a rail or a supply as a node, and one edge per
        step that joins two things, labelled with its number."""
        ids = {}

        def node(name):
            return ids.setdefault(name, "n%d" % (len(ids) + 1))

        boxes = collections.OrderedDict()
        for point in self.points:
            for end in point.ends:
                boxes.setdefault(end.component, []).append(end.node)
        lines = ["```mermaid", "flowchart LR"]
        for number, (component, names) in enumerate(boxes.items(), 1):
            lines.append('  subgraph g%d["%s"]' % (number, _quote(component)))
            lines += ['    %s["%s"]' % (node(name), _quote(name)) for name in dict.fromkeys(names)]
            lines.append("  end")
        edges = [(number, joined) for number, (_, joined) in enumerate(self._walk(), 1) if joined]
        for name in dict.fromkeys(name for _, joined in edges for name in joined if name not in ids):
            kind, _, label = name.partition(":")
            lines.append('  %s["%s"]' % (node(name), _quote("%s %s" % (label, kind))))
        lines += ['  %s ---|"%d"| %s' % (node(one), number, node(other)) for number, (one, other) in edges]
        return "\n".join(lines + ["```"])


def _where(anchor):
    """Where an end joins the anchor, as the steps say it: a board pad itself, else the row the anchor sits in."""
    return anchor.text if anchor.kind == BOARD else "the row of %s" % anchor.node


def _rail_name(point):
    """What a rail is marked with: the board pad on it (GND), else its first end."""
    return next((end.node[len("board "):] for end in point.ends if end.kind == BOARD), point.ends[0].node)


def _quote(text):
    """Text a mermaid label holds: its own double quotes as the entity mermaid reads."""
    return text.replace('"', "#quot;")
