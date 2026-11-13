#!/usr/bin/env python3
"""
Does the built board obey physics, or only itself?

    check_physics.py dist/board/circuit.json --rules .spark/rules.json

The check is `spark/checks/physics_check.py`, which says why it exists. This CLI parses the arguments and prints.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.checks.physics_check import render, run_on_files  # noqa: E402
from spark.core.outcomes import EXIT_OK as EXIT_OK, EXIT_PROBLEMS as EXIT_PROBLEMS, EXIT_COULD_NOT_RUN as EXIT_COULD_NOT_RUN, EXIT_FOR  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_physics.py",
        description="Check a built board against physics rather than against itself.")
    parser.add_argument("circuit", help="the built netlist, usually dist/board/circuit.json")
    parser.add_argument("--rules", help="JSON naming rails, currents and voltages. Run alone, physics "
                        "reads no part records, so no resistor clears by the rail-span bound; "
                        "check_all --project reads them. A top level that is no object, a value that is no finite number or is below its lowest: exit 2, naming the file")
    parser.add_argument("--json", action="store_true", help="the result as data")
    args = parser.parse_args(argv)

    result = run_on_files(args.circuit, args.rules)
    print(json.dumps(result, indent=2) if args.json else render(result))
    return EXIT_FOR[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
