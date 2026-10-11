#!/usr/bin/env python3
"""
The breadboard sheet: from the board that was built, what to put on a breadboard and how to wire it.

    breadboard.py requirements.json                 print the sheet and write breadboard.md beside the file
    breadboard.py requirements.json --out FILE      write it there instead

Example, in a project after `/spark:build`:

    python3 "$CLAUDE_PLUGIN_ROOT/scripts/breadboard.py" requirements.json

Why: the build knows every part and every wire, and a person had neither: the resistors a part asks for lived only in
board.tsx, and the simulation's diagram named a stand-in devkit's GPIO numbers (P191, #143; the breadboard epic, P79).

How: the connections come from the built circuit (dist/board/circuit.json), the same file every check reads, so the
sheet says what was built. Each connection is one point: the board's printed label, and each part's pin with the leg
its record names. Put a point's ends in one breadboard row, or join them with a wire. The parts list comes from the
requirements, with each resistor a part asks for; a part your drawer holds for this project reads "yours".

Exit 0: the sheet was written; 2: it could not be, for example nothing is built yet.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import design  # noqa: E402
import drawer  # noqa: E402
import emit_board  # noqa: E402
import store  # noqa: E402
from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN  # noqa: E402

#: Where the build keeps what it built, relative to the project (`check_spine.py … --keep .`).
CIRCUIT = Path("dist") / "board" / "circuit.json"
SHEET = "breadboard.md"
#: The component every generated design calls its dev board (emit_board, the converter's BOARD mapping).
BOARD_COMPONENT = "Mcu"
#: What each kind of passive a part asks for does: the word on its end, and the phrase in the parts list.
PURPOSE = {"pullup": ("pull-up", "pull-up on"), "pulldown": ("pull-down", "pull-down on"),
           "series": ("", "in series with"), "divider": ("divider", "divider on")}


class NotBuilt(Exception):
    """There is no built circuit to read."""


def points(circuit):
    """
    Every connection point of the built circuit, each a list of (component, port) that share it. Traces join ports and
    nets; a point is what they join, followed through both (netlist.py keeps a pin-to-pin trace's net apart from a named
    one on purpose; a breadboard row does not).
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
    groups = {}
    for port in (e for e in circuit if e.get("type") == "source_port"):
        node = "port:" + port["source_port_id"]
        if node in parent:
            groups.setdefault(find(node), []).append((components[port["source_component_id"]], port))
    return [members for members in groups.values() if len(members) > 1]


def _board_label(board, port):
    """The board's printed label for one of its ports: a pad its file names, every ground pad as one GND."""
    pads = set(board.get("pins") or {}) | set(board.get("power_pads") or {})
    label = next((hint for hint in port.get("port_hints") or [] if hint in pads), port.get("name"))
    return "GND" if re.fullmatch(r"GND\d*", label) else label


def _purposes(parts):
    """{component name of a passive a part asks for: (the word on its end, what it does)}, from the parts' records."""
    found = {}
    for part in parts:
        for host_part in part.get("host_parts") or []:
            word, phrase = PURPOSE.get(host_part["kind"], (host_part["kind"], host_part["kind"] + " on"))
            for name in emit_board.host_part_names(part, host_part):
                found[name] = (word, "%s %s %s" % (phrase, emit_board.component_name(part), host_part["pin"]))
    return found


def _owned(requirements_path, board_id, part_ids):
    """{record id: "yours"} for what the drawer holds for this project; None when the project is not on the list."""
    name = store.project_name(requirements_path.resolve().parent)
    if not name:
        return None
    yours = {}
    for entry in drawer.entries().values():
        target = entry.get("is") if isinstance(entry.get("is"), dict) else {}
        for record_id in target.values():
            if (entry.get("used_in") or {}).get(name) and record_id in part_ids | {board_id}:
                yours[record_id] = "yours"
    return yours


def sheet(requirements_path, circuit_path=None):
    """The sheet, as Markdown, for a requirements file whose project has been built with --keep (or its circuit)."""
    requirements_path = Path(requirements_path)
    circuit_path = Path(circuit_path) if circuit_path else requirements_path.resolve().parent / CIRCUIT
    if not circuit_path.is_file():
        raise NotBuilt("nothing is built at %s yet: run `check_spine.py %s --keep .` first"
                       % (circuit_path, requirements_path.name))
    built = design.load(requirements_path)
    circuit = json.loads(circuit_path.read_text())
    records = {emit_board.component_name(part): part for part in built.parts}
    purposes = _purposes(built.parts)
    owned = _owned(requirements_path, built.board.get("id"), {part["id"] for part in built.parts})
    have = (lambda record_id: owned.get(record_id, "to get")) if owned is not None else (lambda record_id: "")

    def end(component, port):
        """One end of a connection, as a person finds it on the bench."""
        if component["name"] == BOARD_COMPONENT:
            return "board %s" % _board_label(built.board, port)
        if component.get("ftype") == "simple_resistor":
            word = purposes.get(component["name"], ("", ""))[0]
            return "%s%s, end %s" % (component.get("display_resistance") or "a resistor", " " + word if word else "",
                                     re.sub(r"\D", "", port.get("name") or "") or port.get("name"))
        leg = (records.get(component["name"]) or {}).get("legs", {}).get(port.get("name"))
        return "%s %s%s" % (component["name"], port.get("name"), " (%s)" % leg if leg else "")

    lines = ["# Breadboard: %s, on a %s" % (requirements_path.resolve().parent.name, built.board.get("name")), "",
             "## Parts", "", "| | part | for | |", "| --- | --- | --- | --- |",
             "| 1 | %s | the board | %s |" % (built.board.get("name"), have(built.board.get("id")))]
    lines += ["| 1 | %s | %s | %s |" % (part.get("name"), emit_board.component_name(part), have(part["id"]))
              for part in built.parts]
    lines += ["| 1 | %s resistor | %s | |" % (c.get("display_resistance"), purposes.get(c["name"], ("", ""))[1])
              for c in circuit if c.get("type") == "source_component" and c.get("ftype") == "simple_resistor"]
    lines += ["| | a breadboard and jumper wires | | |", "", "## Wiring", "",
              "Each line is one point: put its ends in one breadboard row, or join them with a wire.", ""]
    said = []
    for members in points(circuit):
        ends = list(dict.fromkeys(end(component, port) for component, port in members))
        said.append(" · ".join(sorted(ends, key=lambda one: (not one.startswith("board "), one))))
    lines += ["%d. %s" % (number, line)
              for number, line in enumerate(sorted(said, key=lambda line: (not line.startswith("board "), line)), 1)]
    return "\n".join(lines) + "\n"


def write(requirements_path, out, circuit_path=None):
    """Write the sheet to `out` and return the path; what `check_spine --keep` calls beside the kept board."""
    text = sheet(requirements_path, circuit_path)
    Path(out).write_text(text)
    return Path(out)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="breadboard.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("requirements", help="the project's requirements.json, after a build with --keep")
    parser.add_argument("--out", help="where to write the sheet (default: breadboard.md beside the requirements file)")
    args = parser.parse_args(argv)
    requirements = Path(args.requirements)
    try:
        text = sheet(requirements)
    except (NotBuilt, design.DesignError, store.StoreProblem, OSError, ValueError) as stopped:
        print("breadboard.py: could not run — %s" % stopped, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    out = Path(args.out) if args.out else requirements.resolve().parent / SHEET
    out.write_text(text)
    print(text, end="")
    print("wrote %s" % out, file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
