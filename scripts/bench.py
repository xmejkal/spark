#!/usr/bin/env python3
"""Show each board on USB with what spark's store holds of it: its deploys by project, the projects that keep it and its
grants (P919). It opens no port."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.bench import build_project_outside_world
from spark.bench.show_bench import ShowBench
from spark.core.cli import HelpText, run_cli

#: The verbs, each the Operation it runs. With no verb word, bench.py shows.
VERBS = {"show": ShowBench}
DEFAULT_VERB = "show"

EPILOG = """bench.py show runs only `mpremote devs`, which lists the boards on USB and never opens a port, so a running
program goes on. It asks no question and writes nothing. For each board it reads three records in spark's store: the
deploys (boards/), the board that a look kept for a project (known-boards/) and the grants (grants/). Every value
comes from a record or from the list. The text prints the last two bytes of a MAC; --json carries it whole.

A board is named by a kept record whose USB serial or MAC part matches, else by the MAC part of its USB serial, which
is the serial's and was not read from the chip. Two clone boards with a bridge chip can share a serial: then both are
named alike. A board with no USB serial, a serial that its firmware set, or a bridge's serial that no project keeps
cannot be told apart, so its deploys and its deploy grant are not checked. look.py, run in the project that uses the
board, reads it and keeps it. The live grant is found by the USB serial, as grant.py --check finds it.

The names after "deploys from" are the project folder names that each deploy recorded.

With --json it prints one envelope: data.boards (docs/guide/agents/bench.md).

Exit codes: 0 the list ran and every part of every board was read, also with no board on USB; 2 mpremote could not
list the boards (data.boards is null) or a part was not checked (each is an unchecked item, and data still holds what
was read), or an argument is wrong. Never 1: the view finds no problem."""


def operation_for(argv):
    """(the Operation class `argv` asks for, argv without its verb word): the first word when it is a verb in VERBS, else
    `show` with argv as it is, so a word that is no verb fails in argparse."""
    return (VERBS[argv[0]], argv[1:]) if argv and argv[0] in VERBS else (VERBS[DEFAULT_VERB], argv)


def main(argv=None, outside=None):
    """Run the verb `argv` names and print its lines, or with --json its envelope. `outside` is the OutsideWorld a test
    gives. Returns the exit code."""
    operation, argv = operation_for(sys.argv[1:] if argv is None else list(argv))
    return run_cli(HelpText("bench.py", __doc__.strip(), EPILOG, tool="bench"), operation(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
