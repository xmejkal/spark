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

from spark.design import loader  # noqa: E402
from spark.checks.check import CheckedFolder, inputs_for, render, run, unmeasured_in, verdict  # noqa: E402
from spark.core.outcomes import EXIT_OK as EXIT_OK, EXIT_PROBLEMS as EXIT_PROBLEMS, EXIT_COULD_NOT_RUN as EXIT_COULD_NOT_RUN  # noqa: E402
from spark.core.outcomes import COULD_NOT_RUN, EXIT_FOR  # noqa: E402


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

    checked, refusal = CheckedFolder.named(args.project)
    if refusal:
        if args.json:
            print(json.dumps({"tool": "check_all", "status": COULD_NOT_RUN, "reason": refusal}, indent=2))
        else:
            print("  [????] check_all          %s" % refusal)
        return EXIT_FOR[COULD_NOT_RUN]
    inputs, resolved, ambiguous = inputs_for(args, checked)
    results = run(inputs, ambiguous)
    overall = verdict(results)

    if args.json:
        answer_json = {"tool": "check_all", "status": overall, "unmeasured": unmeasured_in(results),
                       "resolved": resolved, "results": results}
        if checked:
            # the project the build reads (P319), resolved as `design.project_for` resolves it; null for none, never
            # the plugin's own folder
            answer_json["project"] = None if loader.is_library(checked.project) else str(checked.project.resolve())
        print(json.dumps(answer_json, indent=2))
    else:
        if resolved:
            # Printed every time, not on a flag. Silently picking up a stale artifact is the one
            # way discovery is worse than the five paths it replaces.
            print("  resolved from %s:" % args.project)
            for note in resolved:
                print("    %s" % note)
            print()
        print(render(results))
    return EXIT_FOR[overall]


if __name__ == "__main__":
    sys.exit(main())
