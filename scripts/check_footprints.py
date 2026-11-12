#!/usr/bin/env python3
"""
Will this board be buildable, and will the parts go in it?

    check_footprints.py dist/board/circuit.json

The check is `spark/checks/build_check.py`, which says why it exists. This CLI parses the arguments and prints.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.checks import check_codes  # noqa: E402
from spark.checks.build_check import built_design, problems_in, refusal_said, render, rules_asked, run, unchecked_in  # noqa: E402
from spark.core.result import Refusal  # noqa: E402
from spark.core.outcomes import EXIT_OK as EXIT_OK, EXIT_PROBLEMS as EXIT_PROBLEMS, EXIT_COULD_NOT_RUN as EXIT_COULD_NOT_RUN, EXIT_FOR, status_of  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_footprints.py",
        description="Check that a board can actually be built and populated.")
    parser.add_argument("circuit", help="the built netlist, usually dist/board/circuit.json")
    parser.add_argument("--rules", help="the project's .spark/rules.json, whose `fabrication` "
                                        "section says what ITS board house can make "
                                        "(a value that is no finite number or is below its lowest is refused: exit 2)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    path, missing = built_design(args.circuit)
    rules, why = rules_asked(args.rules) if not missing else (None, None)
    if missing or why:
        print(refusal_said(missing or why, args.json))
        return EXIT_COULD_NOT_RUN
    try:
        circuit = json.loads(path.read_text())
    except ValueError as broken:  # P688: a circuit that is not JSON is a refusal, not a traceback
        print(refusal_said(Refusal("%s is not JSON: %s" % (path.name, broken), check_codes.CIRCUIT_NOT_JSON), args.json))
        return EXIT_COULD_NOT_RUN
    findings = run(circuit, rules=rules)
    problems, unchecked = problems_in(findings), unchecked_in(findings)
    status = status_of(problems, unchecked)
    if args.json:
        print(json.dumps({"tool": "check_footprints", "status": status,
                          "findings": [f.as_data() for f in findings]}, indent=2))
    else:
        print(render(findings, path.name))
    return EXIT_FOR[status]


if __name__ == "__main__":
    sys.exit(main())
