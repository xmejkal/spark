#!/usr/bin/env python3
"""
A pin map and a module list, as a board file you can build.

    emit_board.py requirements.json > board.tsx
    emit_board.py requirements.json --assignment saved.json

This is the last step of "I have these modules, wire them up". Everything before it — which board,
what each module asks for, which pin each signal goes on — is settled by `boards.py`,
`parts.py` and `assign_pins.py`. This turns that into tscircuit.

WHAT IT IS HONEST ABOUT
The connections are derived and trustworthy: every trace comes from a pin assignment that was
checked against the board's own capabilities, and every module pin comes from a part definition
whose facts carry sources. Nothing here is guessed.

**The placement is not.** It is a first draft: modules in a column, connectors on an edge,
passives near what they serve. It has no opinion about which cable should exit where, what a
person has to reach, or what a lid slamming does to a hand-made lead. A real layout is a design
activity, and the generated file says so at the top rather than pretending otherwise.

So the output is a starting point that BUILDS and can be checked, not a finished board. That is
the useful thing: `tsci build` and the whole deterministic check suite can run on it immediately,
which is the difference between a draft you can iterate and a blank file.
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import assign_pins  # noqa: E402
import boards  # noqa: E402
import parts as parts_library  # noqa: E402

EXIT_OK, EXIT_COULD_NOT_RUN = 0, 2

#: Layout constants. Ordinal, not designed — they exist to produce something that does not
#: overlap, so the checks have a board to run on.
MARGIN_MM = 6
GAP_MM = 4
DEFAULT_BODY_MM = (16, 12)

#: Rails every design has, and what they are called.
RAIL_NETS = {"logic": "V33", "ground": "GND", "motor": "MOTOR6V", "speaker": "SPEAKER"}

#: Fabrication defaults, set rather than inherited.
#:
#: A tool's floor is what you get when nothing is stated, and on a real board that produced
#: 0.2 mm vias with a 0.05 mm annular ring — below every cheap process's minimum, and an
#: upcharge besides. Nobody chose it. A generated board should not hand anyone that.
VIA_HOLE_MM = 0.3
VIA_PAD_MM = 0.6
BOARD_THICKNESS_MM = 1.6

#: Rails the microcontroller module itself supplies, so a design made only of consumers still
#: has a source for them.
RAILS_THE_MODULE_PROVIDES = ("V33", "GND")


def body_of(part):
    body = part.get("body_mm") or {}
    return (body.get("width", DEFAULT_BODY_MM[0]), body.get("height", DEFAULT_BODY_MM[1]))


def has_an_outline(part):
    """Whether anyone has ever recorded how big this part is."""
    body = part.get("body_mm") or {}
    return isinstance(body.get("width"), (int, float)) and isinstance(
        body.get("height"), (int, float))


def parts_without_an_outline(part_list):
    """
    Parts whose size nobody has recorded.

    `body_of` substitutes DEFAULT_BODY_MM for these, which is how a rangefinder nobody had
    measured became 16 x 12 mm — and then `place()` proved the modules did not overlap, using a
    number that was invented two lines earlier. A layout is only as true as its smallest
    dimension, so this is a refusal rather than a default.
    """
    return [part["name"] for part in part_list if not has_an_outline(part)]


def component_name(part):
    """`l9110s-module` -> `L9110sModule`, so the name in the file reads like a component."""
    return "".join(word.capitalize() for word in part["id"].replace("_", "-").split("-"))


def place(board, part_list):
    """
    Somewhere for everything, and nothing on top of anything else.

    Deliberately simple: the module down the left, parts in a column to its right. It does not
    know which cable leaves where, which is exactly the kind of thing a person has to decide.
    """
    module_width = (board.get("physical") or {}).get("width_mm", 25)
    module_height = (board.get("physical") or {}).get("height_mm", 60)

    column_x = module_width + MARGIN_MM + GAP_MM
    widest = max([body_of(p)[0] for p in part_list] or [0])
    total_height = sum(body_of(p)[1] + GAP_MM for p in part_list)

    width = column_x + widest + MARGIN_MM
    height = max(module_height, total_height) + 2 * MARGIN_MM

    placements = {"Mcu": (-width / 2 + MARGIN_MM + module_width / 2, 0)}
    y = height / 2 - MARGIN_MM
    for part in part_list:
        part_height = body_of(part)[1]
        y -= part_height / 2
        placements[component_name(part)] = (-width / 2 + column_x + widest / 2, y)
        y -= part_height / 2 + GAP_MM
    return placements, width, height


def rails_without_a_source(part_list):
    """
    Rails that something consumes and nothing provides.

    A list of modules is a list of CONSUMERS. Nobody lists the battery connector among their
    parts, so a generated board wires a motor driver's VCC to a motor rail that has no other
    member — and a net with one member cannot be routed, so the board does not build.

    That is worth saying plainly rather than emitting a file that fails: the design genuinely
    needs a source for that rail and the module list did not contain one.
    """
    consumed = set()
    for part in part_list:
        for power in part.get("power") or []:
            net = RAIL_NETS.get(power.get("rail"))
            if net and net not in RAILS_THE_MODULE_PROVIDES:
                consumed.add(net)
    return sorted(consumed)


def emit(board, part_list, assignments, placements, width, height):
    by_signal = {entry["signal"]: entry for entry in assignments}

    lines = [
        "import { %s } from \"./%s\"" % ((board["physical"]["footprint_export"],) * 2),
        "",
        "/**",
        " * %s — generated from a module list." % board["name"],
        " *",
        " * The CONNECTIONS are derived and checked: every trace comes from a pin assignment",
        " * validated against this board's own wake, ADC and strapping constraints, and every",
        " * module pin comes from a part definition whose facts carry sources.",
        " *",
        " * The PLACEMENT is a first draft and nothing more. Modules sit in a column because that",
        " * does not overlap, not because it is right. Nothing here knows which cable should exit",
        " * where, what a person has to reach with a soldering iron once the tall parts are in, or",
        " * what a slamming lid does to a hand-made lead. Lay it out properly before ordering.",
        " *",
        " * Not decided here, and it must be: mounting holes, connector keying, and trace widths for",
        " * anything carrying real current.",
    ]

    # A warning on stderr is gone the moment the shell scrolls; the file is what someone opens in
    # six weeks. If a size was invented, the artifact says so where it cannot be missed.
    unsized = parts_without_an_outline(part_list)
    if unsized:
        lines += [
            " *",
            " * NOBODY HAS MEASURED: %s." % ", ".join(unsized),
            " * Each is drawn as a placeholder %g x %g mm and everything else is arranged around"
            % DEFAULT_BODY_MM,
            " * that, so 'nothing overlaps' here is evidence of nothing at all. Measure them, put",
            " * width and height in the part file with a source, and regenerate.",
        ]

    lines += [
        " */",
        "export default () => (",
        '  <board width="%gmm" height="%gmm" autorouter="auto"' % (width, height),
        '      thickness="%gmm"' % BOARD_THICKNESS_MM,
        '      minViaHoleDiameter="%gmm" minViaPadDiameter="%gmm"' % (VIA_HOLE_MM, VIA_PAD_MM),
        '      automaticPoursEnabled>',
        "    <%s name=\"Mcu\" pcbX={%g} pcbY={%g} />"
        % (board["physical"]["footprint_export"], *placements["Mcu"]),
        "",
    ]

    for part in part_list:
        name = component_name(part)
        labels = {need["pin"]: need["pin"] for need in part.get("needs") or []}
        labels.update({power["pin"]: power["pin"] for power in part.get("power") or []})
        pin_labels = ", ".join('pin%d: "%s"' % (index + 1, pin)
                               for index, pin in enumerate(labels))
        lines.append("    {/* %s */}" % part["name"])
        lines.append('    <chip name="%s" footprint="%s" pcbX={%g} pcbY={%g}'
                     % (name, part.get("footprint", "pinrow4"), *placements[name]))
        lines.append("      pinLabels={{ %s }} />" % pin_labels)

    lines.append("")
    lines.append("    {/* Signals, each on the pin assign_pins.py chose and for the reason it gave. */}")
    for part in part_list:
        name = component_name(part)
        for need in part.get("needs") or []:
            entry = by_signal.get(need["signal"])
            if not entry:
                continue
            lines.append('    <trace from=".Mcu > .%s" to=".%s > .%s" />  {/* %s */}'
                         % (entry["pin"], name, need["pin"], entry["why"]))

    lines.append("")
    lines.append("    {/* Power. Which rail each module pin belongs to comes from its part file. */}")
    for net in rails_without_a_source(part_list):
        lines.append("    {/* NOTHING ON THIS BOARD SOURCES net.%s. A module list is a list of" % net)
        lines.append("        consumers — whatever supplies this rail (a connector, a regulator,")
        lines.append("        a battery) has to be added, or the net has one member and will not")
        lines.append("        route. */}" )
    for part in part_list:
        name = component_name(part)
        for power in part.get("power") or []:
            net = RAIL_NETS.get(power.get("rail"))
            if not net:
                continue
            note = ("  {/* %s */}" % power["note"]) if power.get("note") else ""
            lines.append('    <trace from=".%s > .%s" to="net.%s" />%s'
                         % (name, power["pin"], net, note))

    # Requirements a part states about its host, carried into the file rather than left in a
    # library nobody opens. These are the things a generated board CANNOT do for you.
    requirements = [(part["name"], text)
                    for part in part_list for text in part.get("host_requirements") or []]
    if requirements:
        lines += ["", "    {/* What these parts require of this board, from their part files.",
                  "        None of it is done here — each one is a design decision:"]
        for part_name, text in requirements:
            lines.append("          - %s: %s" % (part_name, text))
        lines.append("     */}")

    lines += ["  </board>", ")"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="emit_board.py", description="Turn a module list and a pin map into a board file.")
    parser.add_argument("requirements")
    parser.add_argument("--project")
    parser.add_argument("--board")
    parser.add_argument("--assume-missing-sizes", action="store_true",
                        help="lay out around a guessed size for any part whose outline "
                             "nobody recorded, saying so in the generated file")
    args = parser.parse_args(argv)

    path = Path(args.requirements)
    if not path.is_file():
        print("no requirements at %s" % path, file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    wanted = json.loads(path.read_text())
    try:
        project = Path(args.project).resolve() if args.project else boards.project_root()
        board = boards.load(project, args.board or wanted.get("board"))
        part_list = [parts_library.load(part_id, project)
                     for part_id in wanted.get("parts", [])]
        signals = parts_library.signals_for(wanted.get("parts", []), project) + list(
            wanted.get("signals") or [])
        assignments, _ = assign_pins.assign(board, signals)
    except (boards.BoardError, parts_library.PartError, assign_pins.Impossible) as broken:
        print("cannot emit a board: %s" % broken, file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    if not (board.get("physical") or {}).get("footprint_export"):
        print("this board has no verified footprint, so a board file would reference nothing",
              file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    unsized = parts_without_an_outline(part_list)
    if unsized and not args.assume_missing_sizes:
        print("no outline recorded for: %s\n"
              "  Every placement below would be arranged around an invented size, and the board "
              "would then be declared not to overlap on the strength of it.\n"
              "  Measure them and put width/height in the part file with a source, or pass "
              "--assume-missing-sizes to proceed with the guess declared in the output."
              % ", ".join(unsized), file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    placements, width, height = place(board, part_list)
    sys.stdout.write(emit(board, part_list, assignments, placements, width, height))

    # To stderr, so it is visible even when stdout is being redirected into a file.
    for net in rails_without_a_source(part_list):
        print("note: nothing sources net.%s — add whatever supplies it, or that net has one "
              "member and the board will not route" % net, file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
