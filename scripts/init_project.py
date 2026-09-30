#!/usr/bin/env python3
"""
Everything a project needs before any check can run.

    init_project.py                        # here
    init_project.py --project ../thing --board firebeetle2-esp32s3

Two of the deterministic checks and every reviewer need `.spark/rules.json` and
`.spark/project.json`, and nothing created them. `findings.py` told people to "Run `spark init`",
which existed only inside that error message — so the first thing a second project hit was a
remedy that did not exist.

WHAT IT WRITES, AND WHAT IT REFUSES TO WRITE
`rules.json` holds the things no netlist records: which nets are an I2C bus, which pins must never
float, and what each rail actually carries. The net NAMES come from the built design, because they
are already there and typing them again is a chance to get one wrong. **Every value is null.**

That is the whole design. An init that guessed `max_current_a` from a part name would poison the
one check that does arithmetic, in a tool whose entire thesis is that an unchecked thing must not
look like a checked one. A null here is not a gap in the output — it is the output. `check_physics`
reads a null rail and reports "no maximum current stated, so nothing here can be verified", which
is the correct answer until somebody measures it.

`project.json` is the brief: what the design must do, what parts are already owned, what has been
decided. No script reads it. The reviewers do, and it is what they judge consequence against — a
finding is only "bad" relative to something the project promised.
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import boards  # noqa: E402
from design import CIRCUIT_PATHS  # noqa: E402

from outcomes import EXIT_OK, EXIT_COULD_NOT_RUN, EXIT_PROBLEMS as EXIT_NOTHING_TO_DO  # noqa: E402

#: Where a built netlist usually is, so the rails can be named from the design rather than typed.

#: Nets whose name says they are a bus. A weak signal deliberately: it seeds the list, and a
#: wrong guess here is visible and harmless, unlike a wrong current.
I2C_NAMES = ("SDA", "SCL")


def nets_in(circuit_path):
    """Every net the built design has, so rails are named from what exists."""
    if not circuit_path or not Path(circuit_path).is_file():
        return []
    elements = json.loads(Path(circuit_path).read_text())
    return sorted({element.get("name") for element in elements
                   if element.get("type") == "source_net" and element.get("name")})


def design_in(project):
    """
    Every part record this project's requirements name, and a note for each file that would not read.

    Every requirements file, not one, for the reason `check_all` reads them all: a project may
    hold two boards, and a rule from the other one simply matches no component in this netlist.
    A file that cannot be read is a NOTE rather than an empty list — silence here is how a rules
    file comes out blank and looks deliberate.
    """
    import design
    part_list, notes = [], []
    for requirements in sorted(Path(project).glob("*requirements.json")):
        try:
            part_list += design.parts_of(design.read(requirements), Path(project))
        except design.DesignError as broken:
            notes.append("%s could not be read, so no rule was seeded from it: %s"
                         % (requirements.name, broken))
    return part_list, notes


def declared_inputs(part_list):
    """
    Every input pin the design's own records declare, as ["Component", "PIN"].

    `must_not_float` was written `[]` and stayed `[]`, so `compare_design` had no rule to apply
    and answered that it compared nothing — on the RC car, on the irrigation controller, on every
    project this tool has ever set up. An empty list and "nobody filled it in" were the same
    thing on disk.

    A record already says which of its pins are inputs, and an input that connects to nothing is
    exactly the defect the rule exists for. Names come from the GENERATOR's own
    `component_name`, so a rule is keyed by the string that actually reached the netlist — an
    instance name is not a record id (`59b7a0b`).
    """
    import emit_board
    pins = []
    for part in part_list:
        for need in part.get("needs") or []:
            if need.get("direction") == "in" and need.get("pin"):
                pins.append([emit_board.component_name(part), need["pin"]])
    return sorted(pins)


def i2c_lines(part_list):
    """
    The I2C lines THIS board has to pull up, as "Component.PIN", and the modules that bring their own.

    Not every bus line is the host's problem, and seeding them all would have been a false alarm
    on a correct board. The irrigation controller's DS3231 module says in its own record: "Add NO
    pull-ups: the module carries 4.7 k on SDA and SCL." Naming its lines here would make
    `compare_design` report a bus nothing pulls up, on a bus that is pulled up.

    The records already draw the line: a part that needs the HOST to pull its bus up declares a
    `host_parts` pull-up on that pin — the VL6180X breakout does, for exactly this reason — and a
    part that carries its own declares none. So an empty list means "nothing here for this board
    to do", and the second return value is what says so by name.

    Named as `Component.PIN` rather than as a net, because spark's own generator wires every
    signal pin-to-pin and no net is ever called SDA. That was the other half of why this list
    stayed empty and unusable.
    """
    import emit_board
    host_pulls, carried = [], []
    for part in part_list:
        pulled = {p["pin"] for p in (part.get("host_parts") or []) if p.get("kind") == "pullup"}
        for need in part.get("needs") or []:
            if need.get("bus") != "i2c" or not need.get("pin"):
                continue
            where = "%s.%s" % (emit_board.component_name(part), need["pin"])
            (host_pulls if need["pin"] in pulled else carried).append(where)
    return sorted(host_pulls), sorted(carried)


def rules_for(nets, part_list=()):
    """
    The rules skeleton. Every value null, every key explained.

    The `//` keys are how this project documents JSON, and they matter more here than anywhere
    else: someone filling this in is being asked for numbers they may have to go and measure,
    and a bare `null` with no explanation is a thing people delete rather than fill.
    """
    buses, carried = i2c_lines(part_list)
    #: A net actually CALLED SDA is still a bus, and a hand-written board.tsx has them (the smart
    #: bin does). Both sources, because neither covers the other.
    buses += [net for net in nets if net.upper() in I2C_NAMES]
    rails = {}
    for net in nets:
        if net in buses:
            continue
        rails[net] = {
            "nominal_volts": None,
            "max_current_a": None,
            "//max_current_a": ("The most this rail ever carries, including inrush and stall. "
                                "Left null, every trace on it is reported as unverifiable "
                                "rather than passed — which is correct until you measure it."),
            "capacitor_chemistry": None,
            "//capacitor_chemistry": "electrolytic, ceramic, tantalum or polymer; decides derating",
            "served_by_pour": None,
            "//served_by_pour": "true if this net is a copper pour, which no width rule can size",
        }

    return {
        "//": ("Things no netlist format records. Written by spark init from the nets in the "
               "built design; every value is null until someone establishes it."),
        "i2c_buses": sorted(set(buses)),
        "//i2c_buses": ("Where an I2C bus is, as a net name or as Component.PIN. Seeded from the "
                        "part records: a line is here when a module needs THIS board to pull it "
                        "up. " + ("Empty because every I2C device in this design carries its own "
                                  "pull-ups (%s) — nothing for this board to do, which is not the "
                                  "same as nobody having looked."
                                  % ", ".join(sorted({line.split(".")[0] for line in carried}))
                                  if carried and not buses else
                                  "Add or remove as the design actually is.")),
        "must_not_float": declared_inputs(part_list),
        "//must_not_float": ('Pins that must never be left floating, as ["Component", "PIN"] '
                             'pairs. An H-bridge input is the usual one: floating, it can turn '
                             'both halves on. Seeded from every pin the design\'s own part '
                             'records declare as an input — an empty list means the records '
                             'declare none, not that nobody filled it in.'),
        "physics": {
            "trace_temperature_rise_c": 10,
            "//trace_temperature_rise_c": ("How much warmer a trace may run than ambient. 10 is "
                                           "the usual conservative choice and is a DECISION, "
                                           "not a measurement — change it deliberately."),
            "i2c_hz": None,
            "i2c_bus_capacitance_pf": None,
            "//i2c_bus_capacitance_pf": ("Total bus capacitance: cable, fan-out and every "
                                         "device pin. Decides whether the pull-ups are strong "
                                         "enough for the clock you chose."),
            "rails": rails,
        },
        "fabrication": {},
        "//fabrication": ("What YOUR board house can make, by the names in the plugin's "
                          "data/fabrication.json — min_annular_ring_mm, min_via_hole_mm, "
                          "min_via_pad_mm, board_thickness_mm, copper_thickness_mm and the "
                          "rest. Empty means the plugin's defaults for a cheap two-layer "
                          "process. Stating one moves both the check and the generator that "
                          "draws for it, because they read the same number."),
    }


PROJECT_TEMPLATE = {
    "//": ("The brief. No script reads this; the reviewers do, and it is what they judge "
           "consequence against — a finding is only 'bad' relative to something you promised."),
    "goal": None,
    "must": [],
    "//must": ('What the design has to do, in terms that can be violated. "Runs a year on one '
               'charge" can be checked against a current budget; "low power" cannot.'),
    "parts_on_hand": [],
    "//parts_on_hand": "What you already own, so nothing recommends buying it again.",
    "prefer": None,
    "//prefer": "Whose modules to research first, in order: [\"dfrobot\", \"seeed\"].",
    "sellers": None,
    "//sellers": ("Where you buy, local first, in order — [\"laskakit\", \"gme\", \"hadex\", \"botland\", "
                  "\"tme\"] for Czechia. Modules come from their makers; simple parts (connectors, "
                  "discretes) take their facts from the maker's datasheet and are bought here."),
    "decided": [],
    "//decided": ("Choices already made and not up for re-litigation, each with why. This is "
                  "what stops a reviewer proposing the option you already rejected."),
}


def nulls_in(node, path=""):
    """Every unanswered field, so the output can end by naming them."""
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key.startswith("//"):
                continue
            here = "%s.%s" % (path, key) if path else key
            if value is None:
                found.append(here)
            else:
                found += nulls_in(value, here)
    return found


def has_answers(path, template):
    """
    Whether a file someone was told to hand-write has been hand-written.

    Fewer nulls than the template means a person answered something. A file that cannot be read
    counts as answered too: whatever is in it, it is not ours to replace.
    """
    try:
        return set(nulls_in(json.loads(path.read_text()))) < set(nulls_in(template))
    except (OSError, ValueError):
        return True


def write(path, payload, force, brief=False):
    """
    Write, or say why not. `--force` rewrites what this tool derived — never a brief with
    answers in it: `init --force` was the only way to re-seed the rails from a new build, and it
    replaced the hand-written `project.json` with the blank template on the way (intake R13; the
    person who hit it had a backup from one command earlier).
    """
    if path.exists():
        if brief and has_answers(path, payload):
            return False, ("%s has answers in it and was kept — a brief is yours; --force "
                           "rewrites only what this tool derived" % path.name)
        if not force:
            return False, "%s already exists, left alone" % path.name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return True, "wrote %s" % path.name


#: The tscircuit the documents were measured on, and the one a new project gets. Pinned exactly,
#: because `"*"` fetched 0.0.2687, which fails this plugin's own documented example with
#: `Port [Mcu.pin17] is not connected to net [V33] by a PCB trace` while this version builds it to
#: 15 traces and no errors (backlog P33; the wildcard was P28's own fix, one night old). To move
#: it: build the documented example with the new version, update the output block in
#: `commands/build.md`, and change this — the suite holds the two to each other.
PINNED_TSCI = "0.0.2600"


def package_file(project):
    """
    What `npx tsci build` needs in a project. Without a package file it walks up looking for a
    root, reaches the home folder and dies on a protected directory; with one, it resolves the
    board's imports from the project and needs the cli installed there (irrigation diary I9 —
    both were met in one evening). The one command never meets either: it builds in a temp
    directory, where a global tsci resolves from its own install. Never rewritten: a person may
    add to it. `npm install` once, then `npx tsci build`.
    """
    return {"name": project.name, "private": True, "dependencies": {"@tscircuit/cli": PINNED_TSCI},
            "//": "written by /spark:init: `npm install` once, then `npx tsci build board.tsx` works here. "
                  "The version is pinned to the one spark's documents were measured on; see init_project.PINNED_TSCI."}


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="init_project.py",
        description="Create the files every check and reviewer needs, with nothing guessed.")
    parser.add_argument("--project", default=".", help="the project to set up (default: here)")
    parser.add_argument("--board", help="board id to make active; omit to see what is available")
    parser.add_argument("--circuit", help="a built netlist to name the rails from")
    parser.add_argument("--force", action="store_true", help="overwrite files that exist")
    args = parser.parse_args(argv)

    project = Path(args.project).resolve()
    if not project.is_dir():
        print("no directory at %s" % project, file=sys.stderr)
        return EXIT_COULD_NOT_RUN

    circuit = args.circuit
    if not circuit:
        for pattern in CIRCUIT_PATHS:
            matches = sorted(project.glob(pattern))
            if len(matches) > 1:
                # `matches[0]` — the first in sorted order — until 2026-09-29. On a two-board
                # project that silently seeded the rules from whichever design sorted first and
                # reported "named N rail(s) from circuit.json", naming no path. The rails of one
                # board then became the rules for both.
                #
                # `check_all` calls the same two matches ambiguous and refuses. Two halves of one
                # tool disagreeing about whether choosing is allowed is worse than either answer.
                print("%d built designs here, and this would seed the rails from ONE of them:\n"
                      "  %s\n"
                      "  The rails of one board are not the rules for both. Name one with "
                      "--circuit, or run this in each design's own project."
                      % (len(matches), "\n  ".join(str(m.relative_to(project))
                                                   for m in matches)), file=sys.stderr)
                return EXIT_COULD_NOT_RUN
            if matches:
                circuit = str(matches[0])
                break

    nets = nets_in(circuit)
    part_list, notes = design_in(project)
    written = []

    for path, payload, brief in ((project / ".spark" / "rules.json", rules_for(nets, part_list), False),
                                 (project / ".spark" / "project.json", PROJECT_TEMPLATE, True)):
        did, note = write(path, payload, args.force, brief=brief)
        notes.append(note)
        if did:
            written.append((path, payload))
    notes.append(write(project / "package.json", package_file(project), force=False)[1])

    if args.board:
        available = boards.available(project)
        if args.board not in available:
            print("no board called %r. Available: %s"
                  % (args.board, ", ".join(available) or "none"), file=sys.stderr)
            return EXIT_COULD_NOT_RUN
        did, note = write(project / "boards" / "active.json",
                          {"schema": 1, "board": args.board}, args.force)
        notes.append(note)

    print("spark init in %s" % project)
    for note in notes:
        print("  %s" % note)
    if circuit:
        print("  named %d rail(s) from %s" % (len(nets), Path(circuit).name))
    else:
        print("  no built design found, so the rails are empty — build, then re-run with --force")
    if not args.board:
        print("  no board chosen. Available: %s"
              % (", ".join(boards.available(project)) or "none"))

    unanswered = [(path, nulls_in(payload)) for path, payload in written]
    total = sum(len(fields) for _, fields in unanswered)
    if total:
        print("\n%d field(s) nobody has answered. Nothing here is guessed, and a check reading a "
              "null\nreports it as unverifiable rather than passing it:\n" % total)
        for path, fields in unanswered:
            for field in fields:
                print("  %s  %s" % (path.name, field))

    if not written and not args.board:
        print("\nnothing to do — everything already exists. --force rewrites it.")
        return EXIT_NOTHING_TO_DO
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
