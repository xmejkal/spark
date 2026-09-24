#!/usr/bin/env python3
"""
Does the fab package order the parts the schematic actually specifies?

    check_bom.py board-gerbers.zip
    check_bom.py board-gerbers.zip --circuit dist/board/circuit.json

Nothing else compares these two. `make check` proves the firmware, the board, the bench scripts
and the simulation agree — and every one of those reads the *design*. The BOM is the one artifact
that leaves the design behind and becomes an order, and it was never checked against anything.

It needed to be. In the exported package, `SenseFilterCap` (1uF) and the four 100nF decoupling
capacitors were all assigned LCSC part **C14663**. One part number cannot be two capacitances, so
at least one of those five components would have arrived wrong — and the 1uF is the one the
design's own comment says sets the sense filter's corner at 159 Hz. With 100nF it is 1.6 kHz, and
the stall detector averages PWM ripple instead of motor current.

The checks here are deliberately the ones that need no supplier lookup, so they run offline and
cannot rot when a catalogue changes:

  * one supplier part number used for two different values is a contradiction on its face;
  * a supplier footprint that disagrees with the footprint in the design is tscircuit telling you
    the part it matched is not the part you drew;
  * a passive with a value but no supplier part is an unbuildable line in the order;
  * a three-pin semiconductor with no supplier part at all, because its FOOTPRINT does not
    say which pad is the gate. That one is not hypothetical: this project's high-side switch
    was drawn as a bare `sot23` with no part number, and the tool bound pad 1 to the drain
    while every real SOT-23 P-FET is gate, source, drain. Fitting any actual part would have
    put the load on the gate and a GPIO on the drain. It had no VALUE either, so the rule
    above exempted it.

What it deliberately does NOT do is claim a part number is correct. Proving that needs the
supplier's catalogue, and a check that silently stops verifying when a network call fails is
worse than no check.
"""

import csv
import io
import json
import sys
import zipfile
from pathlib import Path

BOM_NAME = "bom.csv"

EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2

#: Design warnings that stop being warnings once the package is an order.
FATAL_AT_FAB = ("supplier_footprint_mismatch_warning",)


def read_bom(package: Path):
    with zipfile.ZipFile(package) as archive:
        names = [n for n in archive.namelist() if n.endswith(BOM_NAME)]
        if not names:
            raise SystemExit("no %s in %s" % (BOM_NAME, package.name))
        text = archive.read(names[0]).decode()
    return list(csv.DictReader(io.StringIO(text)))


def check_duplicate_parts(rows):
    """One supplier part number standing for two different values cannot be right."""
    problems = []
    values_by_part = {}
    for row in rows:
        part = (row.get("JLCPCB Part #") or "").strip()
        value = (row.get("Value") or "").strip()
        if not part or not value:
            continue
        values_by_part.setdefault(part, {}).setdefault(value, []).append(row["Designator"])

    for part, by_value in sorted(values_by_part.items()):
        if len(by_value) > 1:
            detail = "; ".join(
                "%s = %s" % (", ".join(sorted(designators)), value)
                for value, designators in sorted(by_value.items()))
            problems.append(
                "supplier part %s is ordered for %d different values: %s. "
                "At most one of them can be the part that arrives."
                % (part, len(by_value), detail))
    return problems


#: Packages whose FOOTPRINT does not say what each pad does, so the part number is the only
#: thing that can. A 0603 is symmetric and a header is mechanical — either is safe to fit from
#: the drawing alone. A three-pin semiconductor is not: SOT-23 MOSFETs are gate-source-drain,
#: SOT-23 BJTs are base-emitter-collector, and a regulator is something else again.
SEMICONDUCTOR_PACKAGES = (
    "sot23", "sot-23", "sot223", "sot-223", "sot89", "sot323", "sot363",
    "sod123", "sod323", "sod523", "to220", "to-220", "to252", "dpak", "to92", "to-92",
)


def check_missing_parts(rows):
    """
    A line with a value nobody can source.

    Deliberately keyed on having a VALUE rather than on a list of component names. Hand-fitted
    things — plug-in modules, connectors, a header — carry no value, and a part the designer
    marked as not-placed is not in the BOM at all. So "has a value but no supplier part" is
    exactly the unbuildable line, on any project, with nothing to configure.

    The first version of this carried a regex of one project's component names. It was dead
    code: every designator it listed was already skipped for having no value.
    """
    problems = []
    for row in rows:
        supplier = (row.get("JLCPCB Part #") or "").strip()
        value = (row.get("Value") or "").strip()
        footprint = (row.get("Footprint") or "").strip().lower()

        if value and not supplier:
            problems.append(
                "%s has a value (%s) but no supplier part, so it cannot be ordered or placed"
                % (row["Designator"], value))
        elif not supplier and any(package in footprint for package in SEMICONDUCTOR_PACKAGES):
            # The exemption above is for hand-fitted things whose footprint says everything:
            # a header, a connector, a module. A semiconductor is the opposite — its FOOTPRINT
            # does not say which pad is the gate. A real SOT-23 P-FET is gate-source-drain, and
            # the tool that drew this board bound pad 1 to the drain, so fitting any actual part
            # puts the load on the gate and a GPIO on the drain. Nothing else catches that,
            # because the line has no value either and so was exempt from the rule above.
            problems.append(
                "%s is a %s with no supplier part. Its footprint does not say which pad is "
                "which — a SOT-23 MOSFET is gate, source, drain in an order the package does "
                "not encode — so until a real part is named, nothing can check that the design "
                "connects to the pads that part actually has"
                % (row["Designator"], footprint))
    return problems


def check_design_warnings(circuit_path: Path):
    """
    Warnings the design already emitted that are fatal once this becomes an order.

    A missing circuit raises rather than returning nothing. It returned `[]`, so a mistyped path
    dropped every fatal-at-fab warning in silence — and the test named
    `test_a_missing_circuit_is_not_treated_as_clean` asserted precisely that empty list, under a
    comment saying it must not report zero problems as if it had looked. The name was right and
    the assertion was its opposite.
    """
    if not circuit_path.is_file():
        raise FileNotFoundError(
            "no circuit at %s, so the design's own fab warnings were never read" % circuit_path)
    problems = []
    for element in json.loads(circuit_path.read_text()):
        if element.get("type") in FATAL_AT_FAB:
            problems.append("the design itself warns: %s" % element.get("message", element["type"]))
    return problems


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(
        prog="check_bom.py",
        description="Check that a fab package orders the parts the schematic specifies.")
    parser.add_argument("package", help="the exported fab package, e.g. board-gerbers.zip")
    parser.add_argument("--circuit", help="the built netlist, for warnings that are fatal at fab")
    args = parser.parse_args(argv)

    package = Path(args.package)
    if not package.is_file():
        print("no fab package at %s — export it first" % package)
        return EXIT_COULD_NOT_RUN

    rows = read_bom(package)
    problems = check_duplicate_parts(rows) + check_missing_parts(rows)
    if args.circuit:
        problems += check_design_warnings(Path(args.circuit))

    print("%s: %d line(s) checked against the design" % (BOM_NAME, len(rows)))
    if not problems:
        print("   the order matches the schematic.")
        return EXIT_OK

    print("\n%d problem(s) — this package would build a different circuit:\n" % len(problems))
    for problem in problems:
        print("  - %s" % problem)
    return EXIT_PROBLEMS


if __name__ == "__main__":
    sys.exit(main())
