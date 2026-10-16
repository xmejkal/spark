#!/usr/bin/env python3
"""
The breadboard sheet: from the board that was built, what to put on a breadboard and how to wire it.

    breadboard.py requirements.json                 print the sheet and write breadboard.md beside the file
    breadboard.py requirements.json --out FILE      write it there instead

Example, in a project after `/spark:build` (`check_spine.py requirements.json --keep .` writes the sheet itself):

    python3 "$CLAUDE_PLUGIN_ROOT/scripts/breadboard.py" requirements.json

What it writes, each time from scratch:
  - the parts: the board, each part with how many, each resistor a part asks for (R1, R2, …, through-hole) and what
    it is for, and whether you have each: yours (your drawer holds it for this project), in your drawer (you own it,
    not held here), to get; blank when the project is not on your list (/spark:init puts it there);
  - the wiring (P202): numbered steps, one connection each, by the board's printed label and each part's pin and leg
    (the board and each part in first, each pin in its own row, then each wire to its point's anchor: a part's pin row,
    else a resistor end's row, else a free row for a board pin's jumper, or a rail for a point with more ends than a row
    holds); a mermaid diagram whose numbered lines are those steps; and the points, one per
    line, as the check list after wiring (breadboard_steps.py holds the step rule);
  - beside the sheet, breadboard.json (P267): the steps on a Wokwi half breadboard, each jumper in its step's color,
    to paste into a new project on wokwi.com. Only a board in data/wokwi-geometry.json is drawn (the XIAO ESP32-C6
    today), and rails are not drawn yet; otherwise the sheet says what is missing, and an old drawing is removed;
  - before you power it: each part's CONFLICT lines, the pins its record says must not float, and its warnings.

It reads the built circuit (dist/board/circuit.json), the same file every check reads, so the sheet is the board that
was built. A circuit from a failed build, or from another requirements file, is refused: build again.

Exit 0: the sheet was written; 2: it could not be (nothing built, a stale or failed build, a file it cannot write).
"""

import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import assign_pins  # noqa: E402
import breadboard_drawing  # noqa: E402
import breadboard_steps  # noqa: E402
import design  # noqa: E402
import drawer  # noqa: E402
import emit_board  # noqa: E402
import parts  # noqa: E402
import store  # noqa: E402
from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN  # noqa: E402

#: Where the build keeps what it built, relative to the project (`check_spine.py … --keep .`).
CIRCUIT = Path("dist") / "board" / "circuit.json"
#: What a build that finished was built from, written beside its circuit by `check_spine --keep` (the refuter, P191).
BUILT_FROM = CIRCUIT.parent / "built-from.json"
SHEET = "breadboard.md"
#: What the drawn breadboard is, as the build and this script say it beside its path.
#: The component every generated design calls its dev board (emit_board, the converter's BOARD mapping).
BOARD_COMPONENT = "Mcu"
#: The holes of one breadboard row on one side of the gap: a point with more ends goes on a rail. The board covers the
#: rows beside its own pins, so a board pin's point is a jumper to a free row, which takes one of its holes.
ROW_HOLES = 5
#: What each kind of passive a part asks for does, said the way a person reads it.
PURPOSE = {"pullup": "pull-up on", "pulldown": "pull-down on", "series": "in series with", "divider": "divider on"}
LEGEND = ("*have*: yours = your drawer holds it for this project · in your drawer = you own it, not held here · "
          "to get = not in your drawer · blank = this project is not on your list (`/spark:init` puts it there)")

#: The views of the wiring steps the sheet shows, in order: (heading, one line that says how to read it, renderer).
WIRING_VIEWS = (
    ("Steps", "One connection per step. The board's pins take the rows beside them, so a board pin always gets a jumper.",
     breadboard_steps.NumberedList()),
    ("Diagram", "Each line is one step, with its number.", breadboard_steps.MermaidDiagram()),
)

#: The board record's `wokwi_pin_naming` when its Wokwi pins carry the printed labels, so a drawing can find them.
PIN_NAMING_SILKSCREEN = "silkscreen"
#: The one palette of step colors, for the sheet's color line and the drawing's jumpers alike.
STEP_COLORS = breadboard_steps.StepColors()
#: The drawings written beside the sheet, in order: each a renderer of one planned layout (P270). A new drawing is a
#: new entry here, and nothing else changes.
DRAWING_RENDERERS = (breadboard_drawing.WokwiBreadboardDiagram(STEP_COLORS),)
#: Ohms by a resistance's suffix, for the value Wokwi's resistor takes.
OHMS = {"": 1, "k": 1000, "M": 1000000}

#: One connection point: the (component, port) pairs it joins, and the names of the nets on it.
Point = collections.namedtuple("Point", "members nets")


class NotBuilt(Exception):
    """There is no built circuit to read, or it is not this design's."""


def points(circuit):
    """
    Every connection point of the built circuit. Traces join ports and nets; a point is what they join, followed through
    both (netlist.py keeps a pin-to-pin trace's net apart from a named one on purpose; a breadboard row does not). A port
    alone on a named net is a point too: a supply that comes from off the board.
    """
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


def printed_label(board, port):
    """
    What the board's silkscreen prints beside one of its pads: a label its header rows list, a pad or power pad of its
    file, or the printed spelling of an alias (MISO is printed MI); never a bare pin number. Every ground pad is GND.
    """
    physical = board.get("physical") or {}
    rows = [label for row in (physical.get("header_order") or {}).values() if isinstance(row, list) for label in row]
    aliases = physical.get("pad_aliases") or {}
    known = set(rows) | set(board.get("pins") or {}) | set(board.get("power_pads") or {}) | set(aliases.values())
    hints = port.get("port_hints") or []
    label = next((aliases.get(hint, hint) for hint in hints if hint in known or hint in aliases), None) or next(
        (hint for hint in hints if not re.fullmatch(r"pin\d+|\d+", hint)), port.get("name"))
    return "GND" if re.fullmatch(r"GND\d*", label) else label


def _passives(design_parts):
    """{component name of a passive a part asks for: what it is for}, from the parts' records."""
    found = {}
    for part in design_parts:
        for host_part in part.get("host_parts") or []:
            phrase = PURPOSE.get(host_part["kind"], host_part["kind"] + " on")
            for name in emit_board.host_part_names(part, host_part):
                found[name] = "%s %s %s" % (phrase, emit_board.component_name(part), host_part["pin"])
    return found


def record_built_from(requirements_path, out):
    """Write what a build that finished was built from; `check_spine --keep` calls it, and the sheet compares it."""
    Path(out).write_text(json.dumps({"requirements": json.loads(Path(requirements_path).read_text())}, indent=1) + "\n")


def _check_fresh(circuit, design_parts, circuit_path, requirements_path):
    """
    Refuse a circuit that is not a finished build of this design: not a circuit, a failed build, a build of other
    requirements (the board swapped, a part added), or one that never recorded what it was built from.
    """
    again = "build again: `check_spine.py %s --keep .`" % requirements_path.name
    built_from = circuit_path.parent / BUILT_FROM.name
    if not built_from.is_file():
        raise NotBuilt("%s records no finished build (no %s beside it): %s" % (circuit_path, BUILT_FROM.name, again))
    try:
        recorded = json.loads(built_from.read_text()).get("requirements")
        current = json.loads(requirements_path.read_text())
    except (ValueError, AttributeError) as broken:
        raise NotBuilt("%s cannot be read (%s): %s" % (built_from, broken, again)) from broken
    if recorded != current:
        raise NotBuilt("%s was built from other requirements than %s: %s" % (circuit_path, requirements_path.name, again))
    if not isinstance(circuit, list) or not all(isinstance(element, dict) for element in circuit):
        raise NotBuilt("%s is not a built circuit: %s" % (circuit_path, again))
    failed = sorted({e["type"] for e in circuit if re.fullmatch(r"source_\w+_error", e.get("type") or "")})
    if failed:
        raise NotBuilt("the last build failed (%s): %s" % (", ".join(failed), again))
    wanted = ({BOARD_COMPONENT} | {emit_board.component_name(part) for part in design_parts}
              | set(_passives(design_parts)))
    built = {e["name"] for e in circuit if e.get("type") == "source_component"
             and e.get("ftype") in ("simple_chip", "simple_resistor")}
    if wanted != built:
        raise NotBuilt("%s was built from other requirements (in the build only: %s; in the file only: %s): %s"
                       % (circuit_path, ", ".join(sorted(built - wanted)) or "nothing",
                          ", ".join(sorted(wanted - built)) or "nothing", again))


#: What the parts table's `have` column says of a part: the words the sheet prints, and the codes `_have` decides on.
HAVE_YOURS, HAVE_IN_DRAWER, HAVE_TO_GET = "yours", "in your drawer", "to get"


def _have(requirements_path, record_ids):
    """{record id: yours | in your drawer | to get}, from the drawer; None when the project is not on the list."""
    name = store.project_name(requirements_path.resolve().parent)
    if not name:
        return None
    said = {record_id: HAVE_TO_GET for record_id in record_ids}
    for entry in drawer.entries().values():
        target = entry.get("is") if isinstance(entry.get("is"), dict) else {}
        if entry.get("skip"):
            continue
        for record_id in (value for value in target.values() if value in said):
            if (entry.get("used_in") or {}).get(name):
                said[record_id] = HAVE_YOURS
            elif said[record_id] == HAVE_TO_GET and entry.get("count", 1):
                said[record_id] = HAVE_IN_DRAWER
    return said


def _natural(text):
    """D3 before D10: digits compared as numbers."""
    return [int(piece) if piece.isdigit() else piece for piece in re.split(r"(\d+)", text)]


def _parts_table(board, design_parts, resistors, supplies, have):
    """The parts to buy or take from the drawer, as Markdown rows: equal parts and equal resistors totalled."""
    status = (lambda record_id: have.get(record_id, HAVE_TO_GET)) if have is not None else (lambda record_id: "")
    rows = ["| qty | part | for | have |", "| --- | --- | --- | --- |",
            "| 1 | %s | the board | %s |" % (board.get("name"), status(board.get("id")))]
    by_record = collections.OrderedDict()
    for part in design_parts:
        by_record.setdefault(part["id"], (part, []))[1].append(emit_board.component_name(part))
    rows += ["| %d | %s | %s | %s |" % (len(names), part.get("name"), ", ".join(sorted(names)), status(record_id))
             for record_id, (part, names) in by_record.items()]
    by_value = collections.OrderedDict()
    for tag, value, purpose in resistors.values():
        by_value.setdefault(value, []).append("%s %s" % (tag, purpose))
    rows += ["| %d | %s resistor, through-hole | %s | %s |" % (len(uses), value, "; ".join(uses), status(None))
             for value, uses in by_value.items()]
    rows += ["| | what feeds %s: a supply from off the board, not part of this list | %s | |"
             % (net, ", ".join(sorted(users))) for net, users in supplies.items()]
    return rows + ["| | a breadboard and jumper wires | | %s |" % status(None), "", LEGEND]


def _supplies(circuit):
    """{net name: the parts on it} for each point that carries a named net and no board pin: a supply from off the board."""
    found = {}
    for point in points(circuit):
        if point.nets and not any(component["name"] == BOARD_COMPONENT for component, _ in point.members):
            for net in point.nets:
                found.setdefault(net, set()).update(component["name"] for component, _ in point.members)
    return found


def _wiring(board, circuit, design_parts, resistors):
    """The wiring: one numbered line per connection point, board labels first, and the same points as steps."""
    records = {emit_board.component_name(part): part for part in design_parts}

    def end(component, port):
        """One end of a connection, as a person finds it on the bench. Every end of a part or a resistor reads
        differently (a resistor by its tag), so the board's ground pads are the only ends that read the same, and they
        are one."""
        if component["name"] == BOARD_COMPONENT:
            pad = printed_label(board, port)
            label = "board %s" % pad
            return breadboard_steps.End(breadboard_steps.BOARD, breadboard_steps.THE_BOARD, label, label, pad)
        if component["name"] in resistors:
            tag, value, purpose = resistors[component["name"]]
            number = re.sub(r"\D", "", port.get("name") or "") or port.get("name")
            return breadboard_steps.End(breadboard_steps.RESISTOR, tag, "%s end %s" % (tag, number),
                                        "%s (%s %s), end %s" % (tag, value, purpose, number), number)
        leg = (records.get(component["name"]) or {}).get("legs", {}).get(port.get("name"))
        short = "%s %s" % (component["name"], port.get("name"))
        return breadboard_steps.End(breadboard_steps.PART, component["name"], short,
                                    short + (" (%s)" % leg if leg else ""), port.get("name"))

    said = []
    for point in points(circuit):
        ends = list(dict.fromkeys(end(component, port) for component, port in point.members))
        ends.sort(key=lambda one: (one.kind != breadboard_steps.BOARD, _natural(one.words)))
        line = " · ".join(one.words for one in ends)
        on_board = ends[0].kind == breadboard_steps.BOARD
        if on_board and len(ends) == 1:
            continue  # a board pad nothing else joins is no wire: 3V3, once the firmware pulls the button up (P204)
        supply = " / ".join(point.nets) if point.nets and not on_board else None
        if supply:
            line += " · the %s supply, from off the board, not part of the parts list" % supply
        # a board pin's end is its jumper's end, in a hole of the free row; a supply's wire takes a hole too
        rail = len(ends) + bool(supply) > ROW_HOLES
        if rail:
            line += (" — more ends than one breadboard row holds: join %s to a rail and put the others on that rail"
                     % ends[0].words if on_board else " — put these ends on one rail")
        said.append((on_board, line, breadboard_steps.StepPoint(ends, supply, rail)))
    said.sort(key=lambda one: (not one[0], _natural(one[1])))
    placed = {one.component for _, _, step_point in said for one in step_point.ends}
    steps = breadboard_steps.BreadboardSteps(
        [breadboard_steps.THE_BOARD] + [name for name in records if name in placed], [step_point for _, _, step_point in said])
    return ["%d. %s" % (number, line) for number, (_, line, _) in enumerate(said, 1)], steps


def _unwired(board, design):
    """A line for each signal the requirements add that no part takes: its pin is spent, and nothing is on it yet."""
    own = [signal for signal in design.signals if not signal.get("from")]
    if not own:
        return []
    assignments, _ = assign_pins.assign(design.board, design.signals)
    aliases = (board.get("physical") or {}).get("pad_aliases") or {}
    return ["- %s: board %s, nothing wired to it yet (the requirements add this signal)"
            % (a["signal"], aliases.get(a["pin"], a["pin"])) for a in assignments if a["signal"] in {s["name"] for s in own}]


def _before_power(design_parts, supplies):
    """What each part's record says must be true before power is applied: its CONFLICTs, its floating pins, its
    warnings, in the record's own words; and the supplies from off the board, whose voltage this sheet does not set."""
    lines, seen = [], set()
    lines += ["- %s comes from off the board, and this sheet does not say its voltage: check it against the supply "
              "range of %s (`parts.py --show`) before you connect it" % (net, ", ".join(sorted(users)))
              for net, users in supplies.items()]
    for part in design_parts:
        name = emit_board.component_name(part)
        lines += ["- **CONFLICT** on %s: %s" % (name, conflict) for conflict in parts.pull_conflicts(part)]
        lines += ["- %s %s has no resistor: the firmware must pull it up with Pin.PULL_UP, as `pins.py` says (P204)"
                  % (name, pin) for pin in part.get("_firmware_pulls", [])]
        lines += ["- %s %s: %s" % (name, pin["pin"], pin.get("note", "")) for pin in part.get("unused_pins") or []]
        if part["id"] not in seen:
            seen.add(part["id"])
            lines += ["- %s: %s" % (part.get("name"), requirement) for requirement in part.get("host_requirements") or []]
    shows = ", ".join("`parts.py --show %s`" % record_id for record_id in sorted({part["id"] for part in design_parts}))
    return lines + ["", "Each record whole, with what it asks of the board: %s." % shows]


#: What one build gives the sheet and the drawing: the design, its circuit, its resistors and its steps.
Read = collections.namedtuple("Read", "built circuit resistors point_lines steps")


def _read_build(requirements_path, circuit_path=None):
    """The built design and its steps, for a requirements file whose project has been built with --keep."""
    requirements_path = Path(requirements_path)
    circuit_path = Path(circuit_path) if circuit_path else requirements_path.resolve().parent / CIRCUIT
    if not circuit_path.is_file():
        raise NotBuilt("nothing is built at %s yet: run `check_spine.py %s --keep .` first"
                       % (circuit_path, requirements_path.name))
    built = design.load(requirements_path)
    try:
        circuit = json.loads(circuit_path.read_text())
    except ValueError as broken:
        raise NotBuilt("%s is not JSON (%s): build again" % (circuit_path, broken)) from broken
    _check_fresh(circuit, built.parts, circuit_path, requirements_path)
    passives = _passives(built.parts)
    resistors = collections.OrderedDict(
        (c["name"], ("R%d" % number, c.get("display_resistance") or "", passives.get(c["name"], "")))
        for number, c in enumerate((c for c in circuit if c.get("type") == "source_component"
                                    and c.get("ftype") == "simple_resistor"), 1))
    point_lines, steps = _wiring(built.board, circuit, built.parts, resistors)
    return Read(built, circuit, resistors, point_lines, steps)


def _to_ohms(resistance):
    """'330Ω' or '10kΩ' as Wokwi's resistor value, in ohms."""
    found = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([kM]?)\s*Ω?", resistance or "")
    if not found:
        return ""
    ohms = float(found.group(1)) * OHMS[found.group(2)]
    return str(int(ohms)) if ohms == int(ohms) else str(ohms)


def _describe_parts(read, geometry):
    """{component as the steps name it: how Wokwi draws it}, from the records. A board whose Wokwi pins are not its
    printed labels names no pins, so the drawing says which pin it cannot find."""
    board = read.built.board
    catalog = {}
    if board.get("wokwi_part_type"):
        pins = (geometry.data["parts"].get(board["wokwi_part_type"]) or {}).get("pins") or {}
        named = board.get("wokwi_pin_naming") == PIN_NAMING_SILKSCREEN
        catalog[breadboard_steps.THE_BOARD] = breadboard_drawing.DrawnPart(board["wokwi_part_type"], {},
                                                        {pin: pin for pin in pins} if named else {})
    for part in read.built.parts:
        wokwi = (part.get("simulation") or {}).get("wokwi") or {}
        if wokwi.get("part"):
            catalog[emit_board.component_name(part)] = breadboard_drawing.DrawnPart(
                wokwi["part"], wokwi.get("attrs") or {}, wokwi.get("pins") or {})
    for tag, value, _ in read.resistors.values():
        catalog[tag] = breadboard_drawing.DrawnPart("wokwi-resistor", {"value": _to_ohms(value)}, {"1": "1", "2": "2"})
    return catalog


def _plan_layout(read):
    geometry = breadboard_drawing.WokwiGeometry.load()
    return breadboard_drawing.BreadboardPlanner(geometry, _describe_parts(read, geometry)).plan(read.steps)


def drawing(requirements_path, circuit_path=None, read=None):
    """The Wokwi diagram's text, or NotDrawn with what stopped it."""
    wokwi = next(renderer for renderer in DRAWING_RENDERERS
                 if isinstance(renderer, breadboard_drawing.WokwiBreadboardDiagram))
    return wokwi.text(_plan_layout(read or _read_build(requirements_path, circuit_path)))


#: One plan of the layout for a sheet and its drawings: the layout, or why it could not be planned.
PlannedLayout = collections.namedtuple("PlannedLayout", "layout why")


def _plan_once(read):
    try:
        return PlannedLayout(_plan_layout(read), None)
    except breadboard_drawing.NotDrawn as stopped:
        return PlannedLayout(None, str(stopped))


def sheet(requirements_path, circuit_path=None, read=None, planned=None):
    """The sheet, as Markdown, for a requirements file whose project has been built with --keep (or its circuit).
    `planned` is the layout `write()` already planned, so the sheet says what the drawings show."""
    requirements_path = Path(requirements_path)
    read = read or _read_build(requirements_path, circuit_path)
    planned = planned or _plan_once(read)
    built, circuit, resistors, steps = read.built, read.circuit, read.resistors, read.steps
    supplies = _supplies(circuit)
    have = _have(requirements_path, {part["id"] for part in built.parts} | {built.board.get("id")})
    lines = ["# Breadboard: %s, on a %s" % (requirements_path.resolve().parent.name, built.board.get("name")), "",
             "## Parts", ""]
    lines += _parts_table(built.board, built.parts, resistors, supplies, have)
    lines += ["", "## Wiring"]
    for heading, intro, renderer in WIRING_VIEWS:
        lines += ["", "### " + heading, "", intro, ""] + renderer.render(steps)
    if planned.layout:
        colors = "Each jumper has its step's color: %s." % ", ".join(
            "%d %s" % (jumper.step, STEP_COLORS.color(jumper.step)) for jumper in planned.layout.jumpers)
        lines += ["", " ".join([renderer.SHEET_MESSAGE for renderer in DRAWING_RENDERERS] + [colors])]
    else:
        lines += [""] + ["%s not written: %s." % (renderer.FILE_NAME, planned.why) for renderer in DRAWING_RENDERERS]
    lines += ["", "### Points", "", "After the steps, each line is one point: its ends must be joined, and nothing else.",
              ""]
    lines += read.point_lines
    unwired = _unwired(built.board, built)
    lines += (["", "Not wired:", ""] + unwired) if unwired else []
    lines += ["", "## Before you power it", ""] + _before_power(built.parts, supplies)
    return "\n".join(lines) + "\n"


#: Result: what write() wrote: the sheet's path, [(path, renderer)] for each drawing written, and why none was (the
#: plan fails for every drawing at once), else None.
WriteResult = collections.namedtuple("WriteResult", "sheet drawings why")


def write(requirements_path, out, circuit_path=None):
    """Write the sheet to `out`, and each drawing beside it when the layout can be planned; what `check_spine --keep`
    calls beside the kept board. The layout is planned once. A drawing left from an earlier build is removed, since it
    describes another one."""
    read = _read_build(requirements_path, circuit_path)
    planned = _plan_once(read)
    paths = [(Path(out).parent / renderer.FILE_NAME, renderer) for renderer in DRAWING_RENDERERS]
    try:
        # every text is rendered before any file is written, so a renderer that fails leaves no new sheet either
        texts = [renderer.text(planned.layout) for renderer in DRAWING_RENDERERS] if planned.layout else []
    except Exception:
        for path, _ in paths:
            path.unlink(missing_ok=True)
        raise
    Path(out).write_text(sheet(requirements_path, read=read, planned=planned))
    if not planned.layout:
        for path, _ in paths:
            path.unlink(missing_ok=True)
        return WriteResult(Path(out), [], planned.why)
    try:
        for (path, _), text in zip(paths, texts):
            path.write_text(text)
    except Exception:
        for path, _ in paths:
            path.unlink(missing_ok=True)  # an old drawing describes another build: never leave it beside a new sheet
        raise
    return WriteResult(Path(out), paths, None)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="breadboard.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("requirements", help="the project's requirements.json, after a build with --keep")
    parser.add_argument("--out", help="where to write the sheet (default: breadboard.md beside the requirements file)")
    args = parser.parse_args(argv)
    requirements = Path(args.requirements)
    out = Path(args.out) if args.out else requirements.resolve().parent / SHEET
    try:
        written = write(requirements, out)
    except (NotBuilt, design.DesignError, store.StoreProblem, OSError) as stopped:
        print("breadboard.py: could not run — %s" % stopped, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    print(written.sheet.read_text(), end="")
    print("wrote %s" % written.sheet, file=sys.stderr)
    for path, renderer in written.drawings:
        print("wrote %s — %s" % (path, renderer.PURPOSE_MESSAGE), file=sys.stderr)
    if written.why:
        for renderer in DRAWING_RENDERERS:
            print("%s not written: %s" % (renderer.FILE_NAME, written.why), file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
