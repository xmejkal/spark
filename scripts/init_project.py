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


def rules_for(nets):
    """
    The rules skeleton. Every value null, every key explained.

    The `//` keys are how this project documents JSON, and they matter more here than anywhere
    else: someone filling this in is being asked for numbers they may have to go and measure,
    and a bare `null` with no explanation is a thing people delete rather than fill.
    """
    buses = [net for net in nets if net.upper() in I2C_NAMES]
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
        "i2c_buses": buses,
        "//i2c_buses": ("Net names carrying an I2C bus. Seeded from nets called SDA/SCL — add "
                        "or remove as the design actually is."),
        "must_not_float": [],
        "//must_not_float": ('Pins that must never be left floating, as ["Component", "PIN"] '
                             'pairs. An H-bridge input is the usual one: floating, it can turn '
                             'both halves on.'),
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
    written, notes = [], []

    for path, payload, brief in ((project / ".spark" / "rules.json", rules_for(nets), False),
                                 (project / ".spark" / "project.json", PROJECT_TEMPLATE, True)):
        did, note = write(path, payload, args.force, brief=brief)
        notes.append(note)
        if did:
            written.append((path, payload))

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
