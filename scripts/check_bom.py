#!/usr/bin/env python3
"""
Does the fab package order the parts the schematic actually specifies?

    check_bom.py board-gerbers.zip
    check_bom.py board-gerbers.zip --circuit dist/board/circuit.json

The check is `spark/checks/order_check.py`, which says why it exists. This CLI parses the arguments and prints.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.checks.order_check import (BOM_NAME, check_design_warnings, check_duplicate_parts, check_missing_parts,  # noqa: E402
                                      order_rows)
from spark.core.outcomes import EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN  # noqa: E402


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(
        prog="check_bom.py",
        description="Check that a fab package orders the parts the schematic specifies.")
    parser.add_argument("package", help="the exported fab package, e.g. board-gerbers.zip")
    parser.add_argument("--circuit", help="the built netlist, for warnings that are fatal at fab")
    args = parser.parse_args(argv)

    rows, refusal = order_rows(Path(args.package))
    if refusal:
        print(refusal)
        return EXIT_COULD_NOT_RUN

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
