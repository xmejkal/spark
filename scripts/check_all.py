#!/usr/bin/env python3
"""
Every deterministic check, in one call, with one answer.

    check_all.py --circuit dist/board/circuit.json --rules .spark/rules.json

The check is `spark/checks/check.py`, which says why it exists, and its Operation `spark/checks/check_design.CheckDesign`
(P804). This CLI hands the arguments to the core, which parses them and prints.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spark.checks.check_design import CheckDesign  # noqa: E402
from spark.core.cli import HelpText, run_cli  # noqa: E402
from spark.core.outcomes import EXIT_OK as EXIT_OK, EXIT_PROBLEMS as EXIT_PROBLEMS, EXIT_COULD_NOT_RUN as EXIT_COULD_NOT_RUN  # noqa: E402
from spark.core.outside import build_bare_outside_world  # noqa: E402


def main(argv=None, outside=None):
    """Run every check and print the text, or with --json the document. `outside` is the OutsideWorld a test gives.
    Returns the exit code."""
    return run_cli(HelpText("check_all.py", "Run every deterministic check and answer once.", None), CheckDesign(), argv,
                   outside_builder=build_bare_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
