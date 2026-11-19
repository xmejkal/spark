#!/usr/bin/env python3
"""The reach's CLI (P251): its `--help` sentence and paragraphs are ReachBoard's (P855), and EPILOG is the CLI's own text."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.bench import build_project_outside_world
from spark.bench.reach_board import ReachBoard
from spark.core.cli import HelpText, run_cli

#: The CLI's own text in `--help`, after ReachBoard's details (P855): its exit codes.
EPILOG = """Exit codes: 0 the board answered, 2 it did not, reach.py could not run, or the board question stopped it
(other_board, no_known_board, needs_reply, answered_no), and the last line says why."""


def main(argv=None, outside=None, operation=None):
    """Run the reach and print its lines, or with --json its one line. `outside` is the OutsideWorld a test gives (a run
    builds the project's), `operation` the ReachBoard a test gives with its Fakes. Returns the exit code."""
    return run_cli(HelpText("reach.py", epilog=EPILOG), operation or ReachBoard(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
