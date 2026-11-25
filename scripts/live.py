#!/usr/bin/env python3
"""
Run a short piece of code on the board under a grant, then reset it (P247).

Its `--help` sentence and paragraphs are RunLiveCode's (P855), and EPILOG is the CLI's own text.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.bench import build_project_outside_world
from spark.bench.run_live_code import RunLiveCode
from spark.core.cli import HelpText, run_cli

#: The CLI's own text in `--help`, after RunLiveCode's details (P855): its --json and its exit codes.
EPILOG = """--json prints one line with every field, null where it has none: answer (ran, raised, not_reached, refused_no_grant,
refused_pin, refused_no_parse, or could-not-run, the word outcomes.py shares), grant_why (grant.py's code when the grant refused), why, output, cure, reset (done, failed or null),
pins_checked (false when the record names no usb or flash pin) and gpio_numbers_in_code, with port, then fix: the
words of the text's fix line, null when spark has no fix, which does not mean that nothing is wrong (P1055). A stop of
the board question adds open, product and known_board.

Exit codes: 0 the board ran the code, 1 refused or the code raised, 2 the board did not answer, the reset failed,
live.py could not run, or the board question stopped it (other_board, no_known_board, needs_reply, answered_no), and
the last line says why. With two or more boards on USB, --port is needed."""


def main(argv=None, outside=None, operation=None):
    """Run one live try and print its lines, or with --json its one line. `outside` is the OutsideWorld a test gives (a run
    builds the project's), `operation` the RunLiveCode a test gives with its Fakes. Returns the exit code."""
    return run_cli(HelpText("live.py", epilog=EPILOG), operation or RunLiveCode(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
