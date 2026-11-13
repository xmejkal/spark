#!/usr/bin/env python3
"""
Every deterministic check, in one call, with one answer.

    check_all.py --circuit dist/board/circuit.json --rules .spark/rules.json

The check is `spark/checks/check.py`, which says why it exists. This CLI parses the arguments and prints.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.checks.check import render_every_check, run_every_check  # noqa: E402
from spark.core.outcomes import EXIT_OK as EXIT_OK, EXIT_PROBLEMS as EXIT_PROBLEMS, EXIT_COULD_NOT_RUN as EXIT_COULD_NOT_RUN  # noqa: E402
from spark.core.outcomes import EXIT_FOR  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_all.py",
        description="Run every deterministic check and answer once.")
    parser.add_argument("--project",
                        help="the folder the requirements file and the kept build (--keep) are in; every input is "
                             "discovered by convention and each resolved path is printed. The rules, parts and boards "
                             "come from the project the build reads: the nearest one up from the folder")
    parser.add_argument("--boards", nargs="*", default=[],
                        help="board definitions to verify against their vendor headers")
    parser.add_argument("--circuit", help="the built netlist")
    parser.add_argument("--rules", help="the project's rules file")
    parser.add_argument("--package", help="the exported fab package")
    parser.add_argument("--json", action="store_true",
                        help="for a caller that is not a person: one JSON document with the status, "
                             "`unmeasured` (how many ? lines the answer rests on) and each check's result")
    args = parser.parse_args(argv)

    result = run_every_check(args)
    print(json.dumps(result, indent=2) if args.json else render_every_check(result, args.project))
    return EXIT_FOR[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
