"""
The wiring of one build as numbered steps, one connection each, and as a mermaid diagram whose edges are those steps
(P202, #161). `breadboard.py` builds it from the built circuit; this module knows nothing of circuits, records or the
drawer.

Each part goes into the breadboard first, each pin in its own row, because its pins then sit in fixed rows. Then each
point gets an anchor (its first part pin, else its first resistor end, else its board pin, or a rail when its ends do
not fit one row), and every other end joins the anchor in one step: a jumper, or a resistor leg. Spark claims no row
numbers, no rail colour and no side of the gap, because it does not know them.

`BreadboardSteps.walk()` is the one source: a renderer (the numbered list, `MermaidDiagram`, a later drawing) reads
its steps and never decides the wiring again.
"""

import collections

#: What an end is: a pad of the board, a pin of a part, or one end of a resistor a part asks for.
BOARD, PART, RESISTOR = "board", "part", "resistor"
#: Which anchor a point gets first: a part's pin sits in a fixed row, a resistor end goes anywhere.
ANCHOR_ORDER = (PART, RESISTOR, BOARD)

#: One end of a connection: its kind, the component it belongs to (one diagram box each), its short name in the
#: diagram and the words the steps say.
End = collections.namedtuple("End", "kind component node text")
#: One connection point: its ends (the board's first), the supply from off the board on it, and whether it goes on a rail.
StepPoint = collections.namedtuple("StepPoint", "ends supply rail")
#: One step: its words, and the two diagram nodes it joins (None for a step that only places something).
Step = collections.namedtuple("Step", "words joined")


class RowAnchor:
    """Strategy: a point whose ends meet in the row of one end."""

    def __init__(self, end):
        self.end = end
        self.node = end.node

    def place(self):
        """The step that puts the anchor itself in, when no earlier step did: a resistor end, in a free row."""
        return [Step("Put %s, in a free row." % self.end.text, None)] if self.end.kind == RESISTOR else []

    def where(self, first):
        """Where another end joins: a board pad itself, else the row the anchor sits in."""
        return self.end.text if self.end.kind == BOARD else "the row of %s" % self.node

    def others(self, ends):
        return [end for end in ends if end is not self.end]


class RailAnchor:
    """Strategy: a point with more ends than one row holds, which meet on a rail marked with its name."""

    def __init__(self, name):
        self.name = name
        self.node = "%s rail" % name

    def place(self):
        return []

    def where(self, first):
        """The first end to arrive marks a free rail; the rest find it by its mark."""
        return ("a free rail. Mark it %s" % self.name) if first else "the %s rail" % self.name

    def others(self, ends):
        return list(ends)


def anchor_for(point):
    """The anchor of one point: a rail when the caller said so (it owns the row size), else its best end."""
    if point.rail:
        board_pads = [end.node[len("board "):] for end in point.ends if end.kind == BOARD]
        return RailAnchor(point.supply or (board_pads[0] if board_pads else point.ends[0].node))
    return RowAnchor(next(end for kind in ANCHOR_ORDER for end in point.ends if end.kind == kind))


def join(end, there):
    """The words that bring one end to a place: a resistor leg goes in, everything else gets a jumper."""
    if end.kind == RESISTOR:
        return "Put %s, in %s." % (end.text, there)
    if end.kind == BOARD:
        return "Run a jumper from %s to %s." % (end.text, there)
    return "Run a jumper from the row of %s to %s." % (end.text, there)


class BreadboardSteps:
    """Value: the steps of one build, from the parts to place and the points to join."""

    def __init__(self, parts, points):
        self.parts = list(parts)
        self.points = list(points)

    def walk(self):
        """[Step], in order: each part placed, then each point joined to its anchor, then its supply."""
        walked = [Step("Put %s in the breadboard, each pin in its own row." % part, None) for part in self.parts]
        for point in self.points:
            anchor = anchor_for(point)
            walked += anchor.place()
            walked += [Step(join(end, anchor.where(number == 0)), (end.node, anchor.node))
                       for number, end in enumerate(anchor.others(point.ends))]
            if point.supply:
                walked.append(Step("Connect the %s supply, from off the board, to %s. Check its voltage first (Before "
                                   "you power it)." % (point.supply, anchor.where(False)),
                                   ("%s supply" % point.supply, anchor.node)))
        return walked

    def list_steps(self):
        """The numbered steps, as Markdown lines."""
        return ["%d. %s" % (number, step.words) for number, step in enumerate(self.walk(), 1)]

    def draw_mermaid(self):
        return MermaidDiagram(self).draw()


class MermaidDiagram:
    """Renderer: a mermaid flowchart of the steps. A box per component, a node per end, a rail or a supply as a node,
    and one edge per step that joins two things, labelled with its number."""

    def __init__(self, steps):
        self.steps = steps
        self.ids = {}

    def _id(self, name):
        return self.ids.setdefault(name, "n%d" % (len(self.ids) + 1))

    def _node(self, name, indent):
        return '%s%s["%s"]' % (indent, self._id(name), _quote(name))

    def draw(self):
        boxes = collections.OrderedDict()
        for point in self.steps.points:
            for end in point.ends:
                boxes.setdefault(end.component, {})[end.node] = None
        lines = ["```mermaid", "flowchart LR"]
        for number, (component, names) in enumerate(boxes.items(), 1):
            lines += ['  subgraph g%d["%s"]' % (number, _quote(component))]
            lines += [self._node(name, "    ") for name in names] + ["  end"]
        edges = [(number, step.joined) for number, step in enumerate(self.steps.walk(), 1) if step.joined]
        lines += [self._node(name, "  ") for name in dict.fromkeys(name for _, joined in edges for name in joined)
                  if name not in self.ids]
        lines += ['  %s ---|"%d"| %s' % (self._id(one), number, self._id(other)) for number, (one, other) in edges]
        return "\n".join(lines + ["```"])


def _quote(text):
    """Text a mermaid label holds: its own double quotes as the entity mermaid reads."""
    return text.replace('"', "#quot;")
