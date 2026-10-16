"""
The wiring of one build as numbered steps, one connection each, and as a mermaid diagram whose edges are those steps
(P202, #161). `breadboard.py` builds it from the built circuit; this module knows nothing of circuits, records or the
drawer.

The board and each part go into the breadboard first, each pin in its own row, because their pins then sit in fixed
rows. Then each point gets an anchor (its first part pin, else its first resistor end, else a free row for its board
pin's jumper, or a rail when its ends do not fit one row), and every other end joins the anchor in one step: a jumper,
or a resistor leg. Spark claims no row numbers, no rail colour and no side of the gap, because it does not know them.

`BreadboardSteps.walk()` is the one source. A renderer (`NumberedList`, `MermaidDiagram`, a later drawing such as
P267) takes the steps and gives lines; it never decides the wiring again, and a new one needs no change here.
"""

import collections

#: What an end is: a pad of the board, a pin of a part, or one end of a resistor a part asks for.
BOARD, PART, RESISTOR = "board", "part", "resistor"
#: The component the board is, as an End and a placing step name it; a step says it as "the board".
BOARD_COMPONENT = "board"
#: Which end anchors a point first: a part's pin sits in a fixed row, a resistor end goes anywhere, and a board pad
#: needs a jumper to a free row.
ANCHOR_ORDER = (PART, RESISTOR, BOARD)

#: One end of a connection: its kind, the component it belongs to (one diagram box each), its short name (in the
#: diagram, and where another end joins it), the full words a step says when it moves this end, and its pin on the
#: component (the board's printed label, the part's pin, the resistor's end number), which a drawing looks up.
End = collections.namedtuple("End", "kind component name words pin")
#: One connection point: its ends (the board's first), the supply from off the board on it, and whether it goes on a rail.
StepPoint = collections.namedtuple("StepPoint", "ends supply rail")
#: One step: its words, and the two diagram names it joins (None for a step that only places something).
Step = collections.namedtuple("Step", "words edge")
#: What a step does: put a component in, set a point's anchor up, join an end to the anchor, or connect a supply.
PLACE, SETUP, JOIN, SUPPLY = "place", "setup", "join", "supply"
#: One step with what it is about: what it does, its subject (the component placed, the End set up or joined, the
#: supply's name) and its point's anchor (None for a placing step). A drawing reads these, never the step's words.
Seated = collections.namedtuple("Seated", "step act subject anchor")
#: Where a point's ends meet: in the row of one end, or on a rail with a mark.
ROW, RAIL = "row", "rail"
Seat = collections.namedtuple("Seat", "kind end mark")


class Anchor:
    """Strategy: where one point's ends meet. Each says the step that sets it up, where the n-th other end goes, and
    which ends join it."""

    name = None

    def setup(self):
        """[Step]: what puts the anchor itself in, before any end joins it."""
        return []

    def destination(self, first):
        """Where an end goes, in a step's words; `first` is the first end to arrive."""
        raise NotImplementedError

    def others(self, ends):
        """The ends that join the anchor, one step each."""
        return list(ends)

    def seat(self):
        """Seat: where the ends meet, as a value a drawing reads."""
        raise NotImplementedError


class RowAnchor(Anchor):
    """A point whose ends meet in the row of one of them: a part's pin, a resistor end, or a board pad's jumper."""

    def __init__(self, end):
        self.end = end
        self.name = end.name

    def setup(self):
        if self.end.kind == RESISTOR:
            return [Step("Put %s, in a free row." % self.end.words, None)]
        if self.end.kind == BOARD:
            return [Step("Run a jumper from %s to a free row." % self.end.words, None)]
        return []

    def destination(self, first):
        if self.end.kind == BOARD:
            return "the row of the jumper from %s" % self.name
        return "the row of %s" % self.name

    def others(self, ends):
        return [end for end in ends if end is not self.end]

    def seat(self):
        return Seat(ROW, self.end, None)


class RailAnchor(Anchor):
    """A point with more ends than one row holds, whose ends meet on a rail marked with its name."""

    def __init__(self, mark):
        self.mark = mark
        self.name = "%s rail" % mark

    def destination(self, first):
        """The first end to arrive marks a free rail; the rest find it by its mark."""
        return ("a free rail. Mark it %s" % self.mark) if first else "the %s rail" % self.mark

    def seat(self):
        return Seat(RAIL, None, self.mark)


def anchor_for(point):
    """The anchor of one point: a rail when the caller said so (it owns the row size), else its best end."""
    if point.rail:
        board_pads = [end.name[len("board "):] for end in point.ends if end.kind == BOARD]
        return RailAnchor(point.supply or (board_pads[0] if board_pads else point.ends[0].name))
    return RowAnchor(next(end for kind in ANCHOR_ORDER for end in point.ends if end.kind == kind))


def move(end, destination):
    """The words that bring one end to its destination: a resistor leg goes in, everything else gets a jumper."""
    if end.kind == RESISTOR:
        return "Put %s, in %s." % (end.words, destination)
    if end.kind == BOARD:
        return "Run a jumper from %s to %s." % (end.words, destination)
    return "Run a jumper from the row of %s to %s." % (end.words, destination)


class BreadboardSteps:
    """Value: the steps of one build, from what to place (the board, then each part) and the points to join."""

    def __init__(self, placed, points):
        self.placed = list(placed)
        self.points = list(points)

    def walk(self):
        """[Step], in order: each thing placed, then each point's anchor set up and its other ends joined, then its
        supply."""
        return [seated.step for seated in self.anchored()]

    def anchored(self):
        """[Seated]: the steps of walk(), in its order, each with what it does, its subject and its anchor."""
        walked = [Seated(Step("Put %s in the breadboard, each pin in its own row."
                              % ("the board" if one == BOARD_COMPONENT else one), None), PLACE, one, None)
                  for one in self.placed]
        for point in self.points:
            anchor = anchor_for(point)
            walked += [Seated(step, SETUP, anchor.seat().end, anchor) for step in anchor.setup()]
            walked += [Seated(Step(move(end, anchor.destination(number == 0)), (end.name, anchor.name)), JOIN, end,
                              anchor) for number, end in enumerate(anchor.others(point.ends))]
            if point.supply:
                walked.append(Seated(Step("Connect the %s supply, from off the board, to %s. Check its voltage first "
                                          "(Before you power it)." % (point.supply, anchor.destination(False)),
                                          ("%s supply" % point.supply, anchor.name)), SUPPLY, point.supply, anchor))
        return walked

    def boxes(self):
        """{component: [the short names of its ends]}, in the order the points name them: a diagram's boxes."""
        found = collections.OrderedDict()
        for point in self.points:
            for end in point.ends:
                found.setdefault(end.component, {})[end.name] = None
        return collections.OrderedDict((component, list(names)) for component, names in found.items())


class NumberedList:
    """Renderer: the steps as numbered Markdown lines."""

    def render(self, steps):
        return ["%d. %s" % (number, step.words) for number, step in enumerate(steps.walk(), 1)]


class MermaidDiagram:
    """Renderer: a mermaid flowchart. A box per component, a node per end, a rail or a supply as a node, and one edge
    per step that joins two things, labelled with its number."""

    def render(self, steps):
        ids = {}

        def node(name, indent):
            return '%s%s["%s"]' % (indent, ids.setdefault(name, "n%d" % (len(ids) + 1)), _quote(name))

        lines = ["```mermaid", "flowchart LR"]
        for number, (component, names) in enumerate(steps.boxes().items(), 1):
            lines += ['  subgraph g%d["%s"]' % (number, _quote(component))]
            lines += [node(name, "    ") for name in names] + ["  end"]
        edges = [(number, step.edge) for number, step in enumerate(steps.walk(), 1) if step.edge]
        lines += [node(name, "  ") for name in dict.fromkeys(name for _, edge in edges for name in edge)
                  if name not in ids]
        lines += ['  %s ---|"%d"| %s' % (ids[one], number, ids[other]) for number, (one, other) in edges]
        return lines + ["```"]


def _quote(text):
    """Text a mermaid label holds: its own double quotes as the entity mermaid reads."""
    return text.replace('"', "#quot;")


class StepColors:
    """One color per step number, so a step's wire in a drawing and its line on the sheet match. Neighbouring steps
    differ. The palette wraps after its last color, so step 9 has step 1's color again: the number tells them apart."""

    PALETTE = ("red", "orange", "gold", "green", "cyan", "blue", "purple", "magenta")

    def color(self, number):
        return self.PALETTE[(number - 1) % len(self.PALETTE)]
