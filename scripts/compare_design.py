#!/usr/bin/env python3
"""
Compare a written rule against the design that was actually built.

    compare_design.py dist/board/circuit.json

The check is `spark/checks/rules_check.py`, which says why it exists. This CLI parses the arguments and prints.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.checks.rules_check import compare, render  # noqa: E402
from spark.core.outcomes import EXIT_FOR  # noqa: E402


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(
        prog="compare_design.py",
        description="Compare written rules against the design that was built.")
    parser.add_argument("circuit", help="the built netlist, usually dist/board/circuit.json")
    parser.add_argument("--rules", help="JSON naming what to check (default: .spark/rules.json); a file that is refused (no finite number, below its lowest) exits 2")
    parser.add_argument("--json", action="store_true",
                        help="the result as data, for a caller that is not a person")
    args = parser.parse_args(argv)

    default_rules = Path(args.circuit).parent.parent.parent / ".spark/rules.json"
    result = compare(args.circuit, args.rules or default_rules)

    print(json.dumps(result, indent=2) if args.json else render(result))
    return EXIT_FOR[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
