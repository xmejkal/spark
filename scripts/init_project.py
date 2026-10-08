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

`project.json` is the brief: the goal, what the design must do (`must`), whose modules to research
first (`prefer`), where the person buys (`sellers`), and what has been decided. `parts.py` reads `prefer`
and `sellers`; the `spark-review` skill hands the reviewers the `must` list, and it is what they judge
consequence against — a finding is only "bad" relative to something the project promised.
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import boards  # noqa: E402
import store  # noqa: E402
import tools  # noqa: E402
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
    "//": ("The brief. parts.py reads `prefer` and `sellers`; the spark-review skill hands the reviewers "
           "`must`, and it is what they judge consequence against — a finding is only 'bad' relative "
           "to something you promised."),
    "goal": None,
    "must": [],
    "//must": ('What the design has to do, in terms that can be violated. "Runs a year on one '
               'charge" can be checked against a current budget; "low power" cannot.'),
    "prefer": None,
    "//prefer": "Whose modules to research first, in order: [\"dfrobot\", \"seeed\"].",
    "sellers": None,
    "//sellers": ("Where you buy, local first, in order — e.g. [\"laskakit\", \"tme\"] in Czechia, "
                  "[\"adafruit\", \"digikey\"] in the US. Modules come from their makers; simple parts "
                  "(connectors, discretes) take their facts from the maker's datasheet and are bought here."),
    "decided": [],
    "//decided": ("Choices already made and not up for re-litigation, each with why. Kept for you and for any "
                  "agent that reads this file: no script reads it, and the spark-review skill hands the "
                  "reviewers only `must`, so it does not stop a reviewer proposing an option you already rejected."),
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


def not_yet_stated(existing, derived):
    """
    What the part records suggest that a rules file does not already say, as sentences.

    `merged` keeps a list somebody has filled in, because it is theirs — a rule they deleted stays
    deleted. But a list filled in BEFORE the records could seed it never learns the rest: the
    irrigation controller had four valve inputs written by hand and would never have gained the
    DS3231's clock line or the mode button. Keeping theirs is right; staying quiet about the
    difference is the silent-skip this repository refuses everywhere else (W1).
    """
    said = []
    for key in ("must_not_float", "i2c_buses"):
        have = existing.get(key) or []
        if not have:
            continue  # merged() filled it; nothing to say
        missing = [entry for entry in (derived.get(key) or []) if entry not in have]
        for entry in missing:
            where = ".".join(entry) if isinstance(entry, list) else entry
            said.append("%s: the part records also name %s, which this file does not. Add it, or "
                        "leave it out deliberately." % (key, where))
    return said


def merged(existing, derived):
    """
    What this tool derived, folded into what a person has already answered. Theirs always wins.

    `--force` used to REPLACE the rules file, and the documents tell people to use it: *"no built
    design found, so the rails are empty — build, then re-run with --force"*. So the one workflow
    this tool prescribes destroyed the answers it had just asked for. Reproduced 2026-09-30 on a
    copy of the RC car: `i2c_hz` set to 400000 came back `null`, and a rail current of 0.5 A came
    back nulls (backlog P53). The brief was protected by `has_answers`; the rules file, which is
    the one holding measurements somebody had to go and take, was not.

    The rule, applied at every depth: a value the file STATES is kept. A key that is missing, or
    holds `null`, or holds an empty list where the derivation found something, is filled in. A
    key the person added and this tool knows nothing about is left where it is. `//` notes take
    the derived text, because they are this tool's own documentation and they improve.
    """
    if not isinstance(existing, dict) or not isinstance(derived, dict):
        return existing
    result = dict(existing)
    for key, value in derived.items():
        if key.startswith("//"):
            result[key] = value
        elif key not in result or result[key] is None:
            result[key] = value
        elif isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merged(result[key], value)
        elif isinstance(result[key], list) and not result[key] and value:
            # An empty list is "nobody filled this in", which is exactly what P45 set out to end.
            result[key] = value
    return result


def write(path, payload, force, brief=False, merge=False, unstated=None):
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
        if merge:
            was = json.loads(path.read_text())
            if unstated is not None:
                unstated.extend(not_yet_stated(was, payload))
            payload = merged(was, payload)
            path.write_text(json.dumps(payload, indent=2) + "\n")
            return True, ("merged into %s — every answer already in it was kept" % path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return True, "wrote %s" % path.name


#: What a new project installs. TWO packages, and the second is the one that decides anything.
#:
#: `@tscircuit/cli` declares **`tscircuit: "*"` as a peer dependency**, and npm installs the newest
#: core that satisfies it. So the CLI's version has never determined the build, and pinning the CLI
#: alone cannot: `@tscircuit/cli@0.1.2113` installed fresh on 2026-09-30 reported core `0.0.2687`,
#: while the same CLI version installed here weeks ago reports `0.0.2600`. The core was never in
#: the package file at all, so every project spark has ever created fetched whatever was newest.
#:
#: P33 measured the right number and attached it to the wrong package. It found core `0.0.2600`
#: builds this plugin's documented example and `0.0.2687` does not — still true, reproduced
#: 2026-09-30: on `0.0.2687` the example stops at `1 error(s): pcb_port_not_connected_error`, and
#: on `0.0.2600` it builds to 15 traces and no errors. But it wrote `0.0.2600` as the version of
#: `@tscircuit/cli`, which numbers its releases `0.1.2xxx` and whose `0.0.x` line stopped at
#: `0.0.394`. `npm install` then failed for everyone: `No matching version found for
#: @tscircuit/cli@0.0.2600`. It went unseen because a global CLI was already on PATH here,
#: installed back when `0.0.2600` was the newest core (backlog P51).
#:
#: To move them: build the documented example in a project with **no global `tsci`**, calling
#: `./node_modules/.bin/tsci` explicitly, update the output block in `commands/build.md`, and
#: change both — the suite holds them to each other and to the document.
#: Both now live in the tools list (data/tools.json → "tscircuit": version, core), where a project or a
#: person can move them in one line (P82); these names stay for the code and the tests that read them.
#: spark's own defaults only — a person's or a project's pin is theirs, not what the documents were
#: measured on, and reading the merged list at import made a broken personal file crash every script
#: that imports this one (the final review of P82).
_TSCIRCUIT = tools._read(tools.DEFAULTS)["tscircuit"]
PINNED_TSCI = _TSCIRCUIT["version"]

#: The `tscircuit` core every number in the documents was measured on. Pinned as a direct
#: dependency, because the CLI's peer range accepts anything and would take the newest.
PINNED_CORE = _TSCIRCUIT["core"]


def package_file(project):
    """
    What `npx tsci build` needs in a project. Without a package file it walks up looking for a
    root, reaches the home folder and dies on a protected directory; with one, it resolves the
    board's imports from the project and needs the cli installed there (irrigation diary I9 —
    both were met in one evening). The one command never meets either: it builds in a temp
    directory, where a global tsci resolves from its own install. Never rewritten: a person may
    add to it. `npm install` once, then `npx tsci build`.
    """
    pinned = tools.merged(project)["tools"]["tscircuit"]  # a project's own pin wins (P82)
    return {"name": project.name, "private": True,
            "dependencies": {"@tscircuit/cli": pinned["version"], "tscircuit": pinned["core"]},
            "//": "written by /spark:init: `npm install` once, then `npx tsci build board.tsx` works here. "
                  "BOTH are pinned: the cli, and the `tscircuit` core it takes as a `*` peer dependency "
                  "and would otherwise fetch newest. Every number in spark's documents was measured on "
                  "this core; see init_project.PINNED_TSCI and PINNED_CORE."}


def boards_offered(project):
    """
    The boards to choose from, as both "Available:" lines say them: those that build first, then each that stops at the
    footprint stage, said as such (C-7, F12) — offered, never hidden, since such a board is still a choice for pin-map work.
    """
    offered = boards.available(project)
    stops = {board_id: boards.footprint_stop(board_id, project) for board_id in offered}
    said = [", ".join(board_id for board_id in offered if not stops[board_id])]
    said += ["%s %s" % (board_id, stops[board_id]) for board_id in offered if stops[board_id]]
    return "; ".join(part for part in said if part) or "none"


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="init_project.py",
        description="Create the files every check and reviewer needs, with nothing guessed.")
    parser.add_argument("--project", default=".", help="the project to set up (default: here)")
    parser.add_argument("--board", help="board id to make active; omit to see what is available")
    parser.add_argument("--circuit", help="a built netlist to name the rails from")
    parser.add_argument("--force", action="store_true",
                        help="work on files that exist too: merge what is derived into rules.json (answers stay), "
                             "rewrite project.json only if it has no answers, set boards/active.json when --board "
                             "names one; package.json is never rewritten")
    args = parser.parse_args(argv)

    project = Path(args.project).resolve()
    if not project.is_dir():
        print("no directory at %s" % project, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    try:
        tools.merged(project)  # before anything is written: a tools file that cannot be read is named
    except tools.ToolProblem as broken:
        print("init_project.py: %s" % broken, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    try:
        listed = "on your projects list as %r" % store.add_project(project)
    except store.StoreProblem as refused:
        listed = "not on your projects list: %s" % refused

    circuit, ambiguous = args.circuit, None
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
                # The RAILS cannot be chosen between; everything derived from the part
                # RECORDS can, because a record says the same thing whichever board was built.
                # This used to refuse outright and write nothing, so a two-board project could
                # never get its floating-input rules at all — and the RC car, which carries the
                # canonical example of one in its L9110S, had `must_not_float: []` for two
                # sprints (backlog P53).
                ambiguous = ("%d built designs here, so the rails were NOT seeded — the rails of "
                             "one board are not the rules for both:\n    %s\n  Name one with "
                             "--circuit, or run this in each design's own project. Everything "
                             "that comes from the part records was seeded."
                             % (len(matches), "\n    ".join(str(m.relative_to(project))
                                                           for m in matches)))
                circuit = None
                break
            if matches:
                circuit = str(matches[0])
                break

    nets = nets_in(circuit)
    part_list, notes = design_in(project)
    notes.append(listed)
    unstated = []
    if ambiguous:
        notes.append(ambiguous)
    written = []

    for path, payload, brief, merge in ((project / ".spark" / "rules.json", rules_for(nets, part_list), False, True),
                                 (project / ".spark" / "project.json", PROJECT_TEMPLATE, True, False)):
        did, note = write(path, payload, args.force, brief=brief, merge=merge,
                          unstated=unstated)
        notes.append(note)
        if did:
            written.append((path, payload))
    notes.append(write(project / "package.json", package_file(project), force=False)[1])
    notes.extend(unstated)

    if args.board:
        if args.board not in boards.available(project):
            print("no board called %r. Available: %s" % (args.board, boards_offered(project)), file=sys.stderr)
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
        print("  no board chosen. Available: %s" % boards_offered(project))

    unanswered = [(path, nulls_in(payload)) for path, payload in written]
    total = sum(len(fields) for _, fields in unanswered)
    if total:
        print("\n%d field(s) nobody has answered. Nothing here is guessed, and a check reading a "
              "null\nreports it as unverifiable rather than passing it:\n" % total)
        for path, fields in unanswered:
            for field in fields:
                print("  %s  %s" % (path.name, field))

    if not written and not args.board:
        print("\nnothing to do — everything already exists. "
              "--force merges what is derived into rules.json and keeps your answers.")
        return EXIT_NOTHING_TO_DO
    # Part of the job could not be done, and W1 applies to this tool as much as to a check: the
    # rails are unseeded and the exit code says so, even though everything else was written.
    return EXIT_COULD_NOT_RUN if ambiguous else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
