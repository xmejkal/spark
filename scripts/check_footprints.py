#!/usr/bin/env python3
"""
Will this board be buildable, and will the parts go in it?

    check_footprints.py dist/board/circuit.json

Everything here was a real defect on a real board that passed DRC, passed every consistency
check, rendered correctly and would have been ordered. They share a shape: each is a number that
was right for a different question.

  * A 32-pin module footprint drilled 0.9 mm, copied from the vendor's own drawing. That is the
    vendor's finished hole for the vendor's own obround pad. A standard 2.54 mm header pin is
    0.64 mm square, so 0.905 mm across the diagonal, and after plating a 0.9 mm drill finishes
    near 0.84 mm. The module would not have seated, and 32 reamed holes is a scrapped board.
  * 220 uF and 470 uF on 0805 lands. No such part exists in that package at any voltage.
  * Vias at the tool's default 0.2 mm hole and 0.3 mm pad — an 0.05 mm annular ring, below the
    minimum of every cheap process, and an advanced-process upcharge besides.
  * Two mechanically identical 2-pin connectors 8 mm apart, one carrying a 6 V motor supply and
    the other a class-D amplifier output. Swapping them destroys the amplifier.

None of this needs a language model. Each is arithmetic against a published limit, which is why
it is a script: it is faster, it is free, and it cannot change its mind.

WHAT IT IS NOT
It is not a DRC and does not try to be — spacing, clearance and short detection belong in the
layout tool that already does them. This checks the things a DRC has no opinion about, because
they depend on what goes INTO the hole rather than on the copper around it.
"""

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2

#: A standard 0.64 mm square header pin, across the diagonal — the dimension that has to fit,
#: and the one people forget because the pin is quoted by its side.
HEADER_PIN_SIDE_MM = 0.64
HEADER_PIN_DIAGONAL_MM = HEADER_PIN_SIDE_MM * math.sqrt(2)

#: Plating grows into the hole from every side, so the finished hole is smaller than the drill.
PLATING_THICKNESS_MM = 0.03

#: What a cheap two-layer process guarantees. Below these an order is quoted higher, bounced for
#: engineering review, or silently altered into something nobody checked clearances against.
MIN_ANNULAR_RING_MM = 0.25
MIN_VIA_HOLE_MM = 0.3
MIN_VIA_PAD_MM = 0.6

#: The largest capacitance that exists in a given package, across all chemistries and voltages,
#: generously rounded up. A plausibility band, not a catalogue: the point is to catch 220 uF on
#: an 0805, not to adjudicate 22 uF against 24.
MAX_CAPACITANCE_F = {
    "0402": 10e-6, "0603": 47e-6, "0805": 100e-6, "1206": 220e-6,
    "1210": 470e-6, "1812": 1000e-6,
}

#: What a chip resistor of each size can dissipate, in watts.
PACKAGE_POWER_W = {"0402": 0.063, "0603": 0.1, "0805": 0.125, "1206": 0.25,
                   "1210": 0.5, "2010": 0.75, "2512": 1.0}


class Finding:
    def __init__(self, rule, subject, detail, fix=None, severity="problem"):
        self.rule, self.subject, self.detail, self.fix = rule, subject, detail, fix
        #: "problem" — this would fail at assembly. "could-not-run" — a rule could not read the
        #: element, which is not the same as the element being fine. There was no severity here
        #: at all, so the second kind had nowhere to go and left through a bare `continue`.
        self.severity = severity

    def as_data(self):
        return {"rule": self.rule, "subject": self.subject, "detail": self.detail,
                "fix": self.fix, "severity": self.severity}


def package_of(footprint):
    """`res0805`, `0805`, `cap0805` -> `0805`. None when it is not a chip package."""
    if not footprint:
        return None
    for package in sorted(set(MAX_CAPACITANCE_F) | set(PACKAGE_POWER_W), key=len, reverse=True):
        if package in footprint:
            return package
    return None


#: The pitch of a standard pin header, and how far off it a footprint may be and still be one.
HEADER_PITCH_MM = 2.54
#: Tight, because a radial electrolytic's 2.50 mm lead pitch is only 0.04 mm away and its leads
#: are round and thin. 0.02 separates them.
HEADER_PITCH_TOLERANCE_MM = 0.02
#: And a header has at least three pins. A two-hole part on roughly the right pitch is far more
#: likely to be a capacitor than a 2-pin header, and a missed 2-pin header costs much less than
#: a check nobody trusts.
HEADER_MIN_PINS = 3


def is_header(holes):
    """
    Does this look like a pin header — that is, does a 0.64 mm square pin go in it?

    Decided from the GEOMETRY, not the footprint's name. Holes on a 2.54 mm pitch take header
    pins; a JST's 2.0 mm pitch and an electrolytic's lead spacing do not, and their leads are
    round and thinner. The first version of this check asked the question of every plated hole
    on the board and reported four connectors and a capacitor as unbuildable — a check that
    cries wolf is one that gets switched off, which is worse than not having written it.
    """
    if len(holes) < HEADER_MIN_PINS:
        return False
    for index, (x, y) in enumerate(holes):
        for other_x, other_y in holes[index + 1:]:
            if abs(math.dist((x, y), (other_x, other_y)) - HEADER_PITCH_MM) \
                    <= HEADER_PITCH_TOLERANCE_MM:
                return True
    return False


def check_through_hole_drills(circuit):
    """
    Every plated hole that a header pin goes into has to admit one.

    Reported per component rather than per hole: 32 identical messages about one footprint is
    how a real finding gets scrolled past.
    """
    finished_min = HEADER_PIN_DIAGONAL_MM + 2 * PLATING_THICKNESS_MM
    by_component = defaultdict(set)
    positions = defaultdict(list)
    for element in circuit:
        if element.get("type") != "pcb_plated_hole":
            continue
        drill = element.get("hole_diameter")
        if drill is None:
            continue
        by_component[element.get("pcb_component_id")].add(drill)
        positions[element.get("pcb_component_id")].append(
            (element.get("x", 0), element.get("y", 0)))

    findings = []
    names = component_names(circuit)
    for component_id, drills in sorted(by_component.items(), key=lambda pair: str(pair[0])):
        smallest = min(drills)
        if smallest >= finished_min or not is_header(positions[component_id]):
            continue
        findings.append(Finding(
            "through-hole-drill", names.get(component_id, str(component_id)),
            "drills %.2f mm, which finishes near %.2f mm after plating. A 2.54 mm header pin is "
            "%.2f mm square and %.3f mm across the diagonal, so it does not go in"
            % (smallest, smallest - 2 * PLATING_THICKNESS_MM,
               HEADER_PIN_SIDE_MM, HEADER_PIN_DIAGONAL_MM),
            fix="drill at least %.1f mm. If this footprint came from a vendor drawing, that "
                "number is their finished hole for their own pad, not a hole for a pin in yours"
                % (math.ceil(finished_min * 10) / 10)))
    return findings


def check_annular_rings(circuit):
    """Pad minus hole, halved. Too little and the ring tears off the barrel."""
    findings = []
    names = component_names(circuit)
    seen = set()
    for element in circuit:
        if element.get("type") != "pcb_plated_hole":
            continue
        hole, pad = element.get("hole_diameter"), element.get("outer_diameter")
        if hole is None or pad is None:
            continue
        ring = (pad - hole) / 2
        owner = names.get(element.get("pcb_component_id"), "?")
        if ring < MIN_ANNULAR_RING_MM and (owner, round(ring, 3)) not in seen:
            seen.add((owner, round(ring, 3)))
            findings.append(Finding(
                "annular-ring", owner,
                "pad %.2f mm around a %.2f mm hole leaves %.3f mm of ring, under the %.2f mm "
                "a cheap process guarantees" % (pad, hole, ring, MIN_ANNULAR_RING_MM),
                fix="grow the pad to at least %.2f mm" % (hole + 2 * MIN_ANNULAR_RING_MM)))
    return findings


def check_vias(circuit):
    """Vias left at a tool's default are usually below what a cheap process will quote."""
    sizes = {(element.get("hole_diameter"), element.get("outer_diameter"))
             for element in circuit if element.get("type") == "pcb_via"}
    findings = []
    for hole, pad in sorted(s for s in sizes if s[0] is not None and s[1] is not None):
        if hole >= MIN_VIA_HOLE_MM and pad >= MIN_VIA_PAD_MM:
            continue
        ring = (pad - hole) / 2
        findings.append(Finding(
            "via-class", "%.2f/%.2f mm vias" % (hole, pad),
            "hole %.2f mm and pad %.2f mm, a %.3f mm ring. A cheap two-layer process wants "
            "%.1f/%.1f mm" % (hole, pad, ring, MIN_VIA_HOLE_MM, MIN_VIA_PAD_MM),
            fix="set the via size explicitly. Left at a default this is an upcharge at best, "
                "and at worst the fab enlarges them into clearances nobody checked"))
    return findings


def check_package_holds_the_value(circuit):
    """A part of that value does not exist in that package."""
    findings = []
    footprints = footprint_by_component(circuit)
    for element in circuit:
        if element.get("type") != "source_component":
            continue
        name = element.get("name")
        package = package_of(footprints.get(element.get("source_component_id")))
        if package is None:
            continue

        if element.get("ftype") == "simple_capacitor":
            value = element.get("capacitance")
            largest = MAX_CAPACITANCE_F.get(package)
            if value and largest and value > largest:
                findings.append(Finding(
                    "package-holds-value", name,
                    "%g uF in a %s, where the largest part of any chemistry is about %g uF"
                    % (value * 1e6, package, largest * 1e6),
                    fix="use a larger package, or a through-hole electrolytic. A land with no "
                        "part that fits it is a BOM line that cannot be sourced"))
    return findings


def check_cross_pluggable_connectors(circuit, watch_distance_mm=25.0):
    """
    Two identical connectors close together, either of which physically accepts the other's plug.

    Only reported when they are near each other, because that is when it happens: a person
    holding two indistinguishable plugs over two indistinguishable sockets.
    """
    placements = {}
    names = component_names(circuit)
    footprints = footprint_by_component(circuit)
    source_of = {element["pcb_component_id"]: element.get("source_component_id")
                 for element in circuit if element.get("type") == "pcb_component"}

    for element in circuit:
        if element.get("type") != "pcb_component":
            continue
        footprint = footprints.get(source_of.get(element["pcb_component_id"]))
        if not footprint or "jst" not in footprint and "conn" not in footprint:
            continue
        centre = element.get("center") or {}
        placements[names.get(element["pcb_component_id"], "?")] = (
            footprint, centre.get("x", 0), centre.get("y", 0))

    findings = []
    entries = sorted(placements.items())
    for index, (name, (footprint, x, y)) in enumerate(entries):
        for other_name, (other_footprint, other_x, other_y) in entries[index + 1:]:
            if footprint != other_footprint:
                continue
            distance = math.dist((x, y), (other_x, other_y))
            if distance > watch_distance_mm:
                continue
            findings.append(Finding(
                "cross-pluggable", "%s and %s" % (name, other_name),
                "both are %s and sit %.0f mm apart, so either plug fits either socket"
                % (footprint, distance),
                fix="use a different series or pin count for one of them, or move them apart. "
                    "Keying is cheaper than the part that gets destroyed"))
    return findings


def component_names(circuit):
    """pcb_component_id -> the name a person uses."""
    source_names = {element["source_component_id"]: element.get("name")
                    for element in circuit if element.get("type") == "source_component"}
    return {element["pcb_component_id"]: source_names.get(element.get("source_component_id"))
            for element in circuit if element.get("type") == "pcb_component"}


def footprint_by_component(circuit):
    """source_component_id -> footprinter string."""
    return {element.get("source_component_id"): element.get("footprinter_string")
            for element in circuit if element.get("type") == "pcb_component"}


def check_what_was_not_examined(circuit):
    """
    Plated holes the rules above could not read, counted rather than dropped.

    Both hole rules begin `if drill is None: continue` and `if hole is None or pad is None:
    continue`. On the board this tool was written for that silently skipped 10 of 70 plated
    holes — and four of them are `pill`, the obround shape whose vendor-drawn finished hole is
    named in this module's own docstring as the flagship defect. The tool then printed
    "buildable — holes take their pins".

    A rule that cannot read an element has not approved it. Reported per shape, because the shape
    is what would have to be taught.
    """
    unread_drill = defaultdict(int)
    unread_ring = defaultdict(int)
    for element in circuit:
        if element.get("type") != "pcb_plated_hole":
            continue
        shape = element.get("shape") or "unspecified"
        if element.get("hole_diameter") is None:
            unread_drill[shape] += 1
        if element.get("hole_diameter") is None or element.get("outer_diameter") is None:
            unread_ring[shape] += 1

    findings = []
    for rule, unread, what in (("through-hole-drill", unread_drill, "drill diameter"),
                               ("annular-ring", unread_ring, "hole and pad diameter")):
        if not unread:
            continue
        findings.append(Finding(
            rule, "%d plated hole(s)" % sum(unread.values()),
            "carry no %s, so this rule never examined them: %s"
            % (what, ", ".join("%d x %s" % (count, shape)
                               for shape, count in sorted(unread.items()))),
            fix="an obround or rectangular-pad hole states its size differently from a round "
                "one. Until this rule reads those shapes, they are unchecked — not approved.",
            severity="could-not-run"))
    return findings


def run(circuit):
    return (check_through_hole_drills(circuit)
            + check_annular_rings(circuit)
            + check_vias(circuit)
            + check_package_holds_the_value(circuit)
            + check_cross_pluggable_connectors(circuit)
            + check_what_was_not_examined(circuit))


def problems_in(findings):
    return [f for f in findings if f.severity == "problem"]


def unchecked_in(findings):
    return [f for f in findings if f.severity == "could-not-run"]


def render(findings, design):
    problems, unchecked = problems_in(findings), unchecked_in(findings)

    lines = []
    if problems:
        lines.append("%s: %d thing(s) that would survive DRC and fail at assembly\n"
                     % (design, len(problems)))
    for finding in problems + unchecked:
        marker = "  [%s]" % finding.rule if finding.severity == "problem" \
            else "  [%s, NOT EXAMINED]" % finding.rule
        lines.append("%s %s: %s" % (marker, finding.subject, finding.detail))
        if finding.fix:
            lines.append("      %s" % finding.fix)

    if not problems:
        # "buildable" used to be printed whenever the problem list was empty, including when a
        # rule had quietly skipped a tenth of the holes on the board.
        lines.insert(0, "%s: %s" % (design, "buildable — holes take their pins, packages hold "
                                    "their values" if not unchecked else
                                    "no problems in what could be examined — see below for what "
                                    "could not"))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_footprints.py",
        description="Check that a board can actually be built and populated.")
    parser.add_argument("circuit", help="the built netlist, usually dist/board/circuit.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    path = Path(args.circuit)
    if not path.is_file():
        print("no built design at %s — build it first" % path)
        return EXIT_COULD_NOT_RUN

    findings = run(json.loads(path.read_text()))
    problems, unchecked = problems_in(findings), unchecked_in(findings)
    status = "problems" if problems else ("could-not-run" if unchecked else "ok")
    if args.json:
        print(json.dumps({"tool": "check_footprints", "status": status,
                          "findings": [f.as_data() for f in findings]}, indent=2))
    else:
        print(render(findings, path.name))
    if problems:
        return EXIT_PROBLEMS
    return EXIT_COULD_NOT_RUN if unchecked else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
