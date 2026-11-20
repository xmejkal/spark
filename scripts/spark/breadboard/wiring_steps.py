"""
The wiring of one build as numbered steps, one connection each, and as a mermaid diagram whose edges are those steps
(P202, #161). `wiring()` builds it from the built circuit's points (`points()`), with each end named as a person finds
it on the bench: the board's printed label, a part's pin and leg, a resistor's tag. The steps know nothing of circuits,
records or the drawer.

The board and each part go into the breadboard first, each pin in its own row, because their pins then sit in fixed
rows. Then each point gets an anchor (its first part pin, else its first resistor end, else a free row for its board
pin's jumper, or a rail when its ends do not fit one row), and every other end joins the anchor in one step: a jumper,
or a resistor leg. Spark claims no row numbers, no rail colour and no side of the gap, because it does not know them.

`BreadboardSteps.numbered()` numbers the steps for the step list and the diagram, and gives the data a page reads
(P826); the drawing (`drawing.py`) and the bench changes (`bench_changes.py`) number `anchored()` themselves. A
renderer (`NumberedList`, `MermaidDiagram`, a later drawing such as P267) takes the steps and gives lines; it never
decides the wiring again, and a new one needs no change here.
"""

import collections
import re

from spark.records import board_pads
from spark.design import board_components
from spark.design import power_rails
from spark.sourcing import part_facts

#: What an end is: a pad of the board, a pin of a part, or one end of a resistor a part asks for.
BOARD, PART, RESISTOR = "board", "part", "resistor"
#: The board, as an End's component and a placing step name it; a step says it as "the board". (The circuit calls
#: the same board `sheet.BOARD_COMPONENT`, "Mcu".)
THE_BOARD = "board"
#: Which end anchors a point first: a part's pin sits in a fixed row, a resistor end goes anywhere, and a board pad
#: needs a jumper to a free row.
ANCHOR_ORDER = (PART, RESISTOR, BOARD)

#: One end of a connection: its kind, the component it belongs to (one diagram box each), its end label (in the
#: diagram, and where another end joins it), the full words a step says when it moves this end, and its pin on the
#: component (the board's printed label, the part's pin, the resistor's end number), which a drawing looks up. A
#: resistor end also says its job (what the part asks it to do) and its value, which stay the same when its tag renumbers.
#: `power_rail` is the rail its record gives the pin ("ground", "logic", ...), "" when the record says it is no power
#: pin, and None when no record says (P947).
End = collections.namedtuple("End", "kind component name words pin job value power_rail", defaults=("", "", ""))
#: What a point's jumpers carry, read from the ends' rails (P947): power, ground, a signal, or not known.
POWER, GROUND, SIGNAL, UNKNOWN = "power", "ground", "signal", "unknown"
#: The rail a record gives every ground pin.
GROUND_RAIL = "ground"
#: One connection point: its ends (the board's first), the supply from off the board on it, and whether it goes on a rail.
StepPoint = collections.namedtuple("StepPoint", "ends supply rail")
#: One step: its words, and the two diagram names it joins (None for a step that only places something).
WiringStep = collections.namedtuple("WiringStep", "words edge")
#: One step with its number, from 1: its words, and its edge (None for a step that only places something). What the step
#: list, the diagram and a page read (P826).
NumberedStep = collections.namedtuple("NumberedStep", "number words edge")
#: What a step does: put a component in, set a point's anchor up, join an end to the anchor, or connect a supply.
PLACE, SETUP, JOIN, SUPPLY = "place", "setup", "join", "supply"
#: One step with what it is about: what it does, its subject (the component placed, the End set up or joined, the
#: supply's name), its point's anchor (None for a placing step), whether it runs a jumper, and what its point carries
#: (`role_of`, None for a placing step). A drawing reads these, never the step's words.
Seated = collections.namedtuple("Seated", "step act subject anchor jumper role")
#: Where a point's ends meet: in the row of one end, or on a rail with a mark.
ROW, RAIL = "row", "rail"
Seat = collections.namedtuple("Seat", "kind end mark")


class Anchor:
    """Strategy: where one point's ends meet. Each says the step that sets it up, where the n-th other end goes, and
    which ends join it."""

    name = None

    def setup(self):
        """[WiringStep]: what puts the anchor itself in, before any end joins it."""
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
            return [WiringStep("Put %s, in a free row." % self.end.words, None)]
        if self.end.kind == BOARD:
            return [WiringStep("Run a jumper from %s to a free row." % self.end.words, None)]
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


def role_of(ends):
    """What a point carries, from its ends' rails: ground when one end is on the ground rail, power when one is on
    another rail, not known when no rail is and a record says nothing of an end, else a signal."""
    rails = [end.power_rail for end in ends]
    if GROUND_RAIL in rails:
        return GROUND
    if any(rails):
        return POWER
    return UNKNOWN if None in rails else SIGNAL


def needs_jumper(end):
    """Whether an end reaches its destination by a jumper: a resistor leg goes in itself, everything else does not."""
    return end.kind != RESISTOR


def move(end, destination):
    """The words that bring one end to its destination: a resistor leg goes in, everything else gets a jumper."""
    if not needs_jumper(end):
        return "Put %s, in %s." % (end.words, destination)
    if end.kind == BOARD:
        return "Run a jumper from %s to %s." % (end.words, destination)
    return "Run a jumper from the row of %s to %s." % (end.words, destination)


class BreadboardSteps:
    """Value: the steps of one build, from what to place (the board, then each part) and the points to join. `shorts`
    is {component: the name a person calls it by} (`board_components.short_names`, P945); a component not in it is
    called by its component name."""

    def __init__(self, placed, points, shorts=None):
        self.placed = list(placed)
        self.points = list(points)
        self.shorts = dict(shorts or {})

    def short_name(self, component):
        """The name a step calls a component by."""
        return self.shorts.get(component, component)

    def numbered(self):
        """[NumberedStep], in the order of anchored(), numbered from 1: each thing placed, then each point's anchor set up
        and its other ends joined, then its supply. The step list and the diagram take their numbers from here."""
        return [NumberedStep(number, seated.step.words, seated.step.edge)
                for number, seated in enumerate(self.anchored(), 1)]

    def anchored(self):
        """[Seated], in order, each step with what it does, its subject and its anchor. numbered() numbers them for the
        step list, the diagram and a page; a drawing numbers them itself."""
        walked = [Seated(WiringStep("Put %s in the breadboard, each pin in its own row."
                              % ("the board" if placed == THE_BOARD else self.short_name(placed)), None), PLACE, placed, None,
                                  False, None)
                  for placed in self.placed]
        for point in self.points:
            anchor = anchor_for(point)
            set_up = anchor.seat().end
            role = role_of(point.ends)
            walked += [Seated(step, SETUP, set_up, anchor, set_up.kind == BOARD, role) for step in anchor.setup()]
            walked += [Seated(WiringStep(move(end, anchor.destination(number == 0)), (end.name, anchor.name)), JOIN, end,
                              anchor, needs_jumper(end), role) for number, end in enumerate(anchor.others(point.ends))]
            if point.supply:
                walked.append(Seated(WiringStep("Connect the %s supply, from off the board, to %s. Check its voltage first "
                                          "(Before you power it)." % (point.supply, anchor.destination(False)),
                                          ("%s supply" % point.supply, anchor.name)), SUPPLY, point.supply, anchor,
                                     False, role))
        return walked

    def boxes(self):
        """{component: [the short names of its ends]}, in the order the points name them: a diagram's boxes."""
        found = collections.OrderedDict()
        for point in self.points:
            for end in point.ends:
                found.setdefault(end.component, {})[end.name] = None
        return collections.OrderedDict((component, list(names)) for component, names in found.items())


class NumberedList:
    """Renderer: the steps as numbered Markdown lines. Given `holes` (a `drawing.StepHoles` of the planned layout, P945),
    each step that the drawing places ends with the holes it uses."""

    #: What a step's holes add to its line, filled with the holes' words.
    HOLES_MESSAGE = " Holes: %s."

    def render(self, steps, holes=None):
        return ["%d. %s%s" % (step.number, step.words, self.HOLES_MESSAGE % holes.get(step.number)
                              if holes and holes.get(step.number) else "") for step in steps.numbered()]


class MermaidDiagram:
    """Renderer: a mermaid flowchart. A box per component, a node per end, a rail or a supply as a node, and one edge
    per step that joins two things, labelled with its number."""

    def render(self, steps, holes=None):
        """The diagram's lines. `holes` is taken as the step list takes it and not drawn: an edge is a step, not a hole."""
        ids = {}

        def node(name, indent):
            return '%s%s["%s"]' % (indent, ids.setdefault(name, "n%d" % (len(ids) + 1)), _quote(name))

        lines = ["```mermaid", "flowchart LR"]
        for number, (component, names) in enumerate(steps.boxes().items(), 1):
            lines += ['  subgraph g%d["%s"]' % (number, _quote(steps.short_name(component)))]
            lines += [node(name, "    ") for name in names] + ["  end"]
        edges = [(step.number, step.edge) for step in steps.numbered() if step.edge]
        lines += [node(name, "  ") for name in dict.fromkeys(name for _, edge in edges for name in edge)
                  if name not in ids]
        lines += ['  %s ---|"%d"| %s' % (ids[one], number, ids[other]) for number, (one, other) in edges]
        return lines + ["```"]


def _quote(text):
    """Text a mermaid label holds: its own double quotes as the entity mermaid reads."""
    return text.replace('"', "#quot;")


class JumperColors:
    """Strategy: one color per jumper by what it carries (P947), so its wire in a drawing and its line on the sheet
    match: red for power, black for ground, gray when no record says, and each signal jumper the next of SIGNALS in
    step order, so no two signals share a color while colors are left. SIGNALS wraps after its last; the number tells
    two apart."""

    BY_ROLE = {POWER: "red", GROUND: "black", UNKNOWN: "gray"}
    SIGNALS = ("green", "blue", "purple", "orange", "magenta", "cyan")

    def of(self, roles):
        """{step number: color} of the jumpers whose roles are `roles`, {step number: role}."""
        colors, signals = {}, 0
        for number in sorted(roles):
            colors[number] = self.BY_ROLE.get(roles[number])
            if colors[number] is None:
                colors[number] = self.SIGNALS[signals % len(self.SIGNALS)]
                signals += 1
        return colors


#: One connection point: the (component, port) pairs it joins, and the names of the nets on it.
Point = collections.namedtuple("Point", "members nets")
#: The holes of one breadboard row on one side of the gap: a point with more ends goes on a rail. The board covers the
#: rows beside its own pins, so a board pin's point is a jumper to a free row, which takes one of its holes.
ROW_HOLES = 5


def points(circuit):
    """Every connection point of the built circuit. Traces join ports and nets; a point is what they join, followed through
    both (netlist.py keeps a pin-to-pin trace's net apart from a named one on purpose; a breadboard row does not). A port
    alone on a named net is a point too: a supply that comes from off the board, unless a part makes that net
    (`off_board_supplies`)."""
    parent = {}

    def find(node):
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for element in circuit:
        if element.get("type") == "source_trace":
            joined = (["port:" + p for p in element.get("connected_source_port_ids") or []]
                      + ["net:" + n for n in element.get("connected_source_net_ids") or []])
            for other in joined[1:]:
                parent[find(other)] = find(joined[0])
    components = {e["source_component_id"]: e for e in circuit if e.get("type") == "source_component"}
    members, nets = collections.defaultdict(list), collections.defaultdict(list)
    for port in (e for e in circuit if e.get("type") == "source_port"):
        if "port:" + port["source_port_id"] in parent:
            members[find("port:" + port["source_port_id"])].append((components[port["source_component_id"]], port))
    for net in (e for e in circuit if e.get("type") == "source_net"):
        if "net:" + net["source_net_id"] in parent and net.get("name"):
            nets[find("net:" + net["source_net_id"])].append(net["name"])
    return [Point(found, sorted(nets[root])) for root, found in members.items() if len(found) > 1 or nets[root]]


def off_board_supplies(nets, parts):
    """The named nets of a point with no board pin that a supply from off the board must feed: every one but those a
    part of the design makes from power it draws on the board, such as an amplifier's outputs (P860)."""
    made = power_rails.rails_made_on_board(parts)
    return [net for net in nets if net not in made]


def printed_label(board, port):
    """What the board's silkscreen prints beside one of its pads: a label its header rows list, a pad or power pad of its
    file, or the printed spelling of an alias (MISO is printed MI); never a bare pin number. Every ground pad is GND."""
    physical = board.get("physical") or {}
    rows = [label for row in (physical.get("header_order") or {}).values() if isinstance(row, list) for label in row]
    pads = board_pads.BoardPads.from_record(board)  # --- MVP --- (P512)
    known = set(rows) | set(board.get("pins") or {}) | set(board.get("power_pads") or {}) | pads.alias_pads() | set(pads.aliases)
    hints = port.get("port_hints") or []
    label = next((pads.pad_of(hint) for hint in hints if hint in known), None) or next(
        (hint for hint in hints if not re.fullmatch(r"pin\d+|\d+", hint)), port.get("name"))
    return "GND" if re.fullmatch(r"GND\d*", label) else label


def board_rail(board, port, pad):
    """The rail of a board's pad, from its record's power_pads (P947): the rail of the first of the port's hints or its
    printed label that is a power pad, "" when none is, and None when the record has no power_pads or no rail there."""
    power_pads = board.get("power_pads")
    if not isinstance(power_pads, dict):
        return None
    found = next((name for name in list(port.get("port_hints") or []) + [pad] if name in power_pads), None)
    if found is None:
        return ""
    rail = power_pads[found].get("rail") if isinstance(power_pads[found], dict) else None
    return rail if isinstance(rail, str) and rail else None


def part_rail(record, pin, made=frozenset()):
    """The rail of a part's pin, from its record's power list (P947): the rail of the entry for the pin, "" when the
    list has none for it, and None when the record holds no power list (missing, empty or not a list) or no rail there.
    A side of a driven pair (a `polarity`) on a net made on this board (`made`, `power_rails.rails_made_on_board`) is
    "": an amplifier's speaker outputs carry a signal, never a supply. A regulator's output has no polarity and stays."""
    power = record.get("power")
    if not isinstance(power, list) or not power:
        return None
    entry = next((one for one in power if isinstance(one, dict) and one.get("pin") == pin), None)
    if entry is None or (entry.get("polarity") and power_rails.net_for(entry) in made):
        return ""
    rail = entry.get("rail")
    return rail if isinstance(rail, str) and rail else None


def _natural(text):
    """D3 before D10: digits compared as numbers."""
    return [int(piece) if piece.isdigit() else piece for piece in re.split(r"(\d+)", text)]


def wiring(board, circuit, design_parts, resistors, board_component):
    """The wiring: one numbered line per connection point, board labels first, and the same points as steps.
    `board_component` is the circuit's name for the board (`sheet.BOARD_COMPONENT`)."""
    records = {board_components.component_name(part): part for part in design_parts}
    shorts = board_components.short_names(design_parts)
    made = power_rails.rails_made_on_board(design_parts)

    def end(component, port):
        """One end of a connection, as a person finds it on the bench. Every end of a part or a resistor reads
        differently (a resistor by its tag), so the board's ground pads are the only ends that read the same, and they
        are one."""
        if component["name"] == board_component:
            pad = printed_label(board, port)
            label = "board %s" % pad
            return End(BOARD, THE_BOARD, label, label, pad, power_rail=board_rail(board, port, pad))
        if component["name"] in resistors:
            tag, value, purpose = resistors[component["name"]]
            number = re.sub(r"\D", "", port.get("name") or "") or port.get("name")
            return End(RESISTOR, tag, "%s end %s" % (tag, number), "%s (%s %s), end %s" % (tag, value, purpose, number),
                       number, purpose, value)
        record = records.get(component["name"]) or {}
        leg = record.get("legs", {}).get(port.get("name"))
        # a pin is said by the label printed beside it; its port name stays the key the drawing looks it up by
        printed = part_facts.printed_names(record).get(port.get("name"), port.get("name"))
        short = "%s %s" % (shorts.get(component["name"], component["name"]), printed)
        return End(PART, component["name"], short, short + (" (%s)" % leg if leg else ""), port.get("name"),
                   power_rail=part_rail(record, port.get("name"), made))

    said = [one for one in (_said(point, end, design_parts) for point in points(circuit)) if one]
    said.sort(key=lambda one: (not one[0], _natural(one[1])))
    placed = {one.component for _, _, step_point in said for one in step_point.ends}
    steps = BreadboardSteps(
        [THE_BOARD] + [name for name in records if name in placed], [step_point for _, _, step_point in said], shorts)
    return ["%d. %s" % (number, line) for number, (_, line, _) in enumerate(said, 1)], steps


def _said(point, end, parts):
    """Value: (whether it starts at the board, its wiring line, its StepPoint) for one point, each end named by `end`;
    None for a board pad nothing else joins, which is no wire: 3V3, once the firmware pulls the button up (P204)."""
    ends = list(dict.fromkeys(end(component, port) for component, port in point.members))
    ends.sort(key=lambda one: (one.kind != BOARD, _natural(one.words)))
    line = " · ".join(one.words for one in ends)
    on_board = ends[0].kind == BOARD
    if on_board and len(ends) == 1:
        return None
    supply = " / ".join(off_board_supplies(point.nets, parts)) or None if point.nets and not on_board else None
    if supply:
        line += " · the %s supply, from off the board, not part of the parts list" % supply
    # a board pin's end is its jumper's end, in a hole of the free row; a supply's wire takes a hole too
    rail = len(ends) + bool(supply) > ROW_HOLES
    if rail:
        line += (" — more ends than one breadboard row holds: join %s to a rail and put the others on that rail"
                 % ends[0].words if on_board else " — put these ends on one rail")
    return on_board, line, StepPoint(ends, supply, rail)
