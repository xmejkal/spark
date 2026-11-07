#!/usr/bin/env python3
"""Run one line on the board on USB, and cure it once when its USB output died at power-on: the PO's bench tool (P251)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.bench import build_project_outside_world
from spark.bench.reach_board import ReachBoard
from spark.core.cli import HelpText, run_cli

EPILOG = """It runs print("reached") on the board with mpremote's exec. When mpremote says "could not enter raw repl", it
opens the port once with DTR and RTS off, which restarted a XIAO ESP32-C6 whose USB output died at power-on, waits until
the port is there again, and runs the line once more. It says whether the board answered, whether a cure ran and what
the board printed during it. The exec stops the firmware that ran: press R or replug to run it again.

It is the PO's bench tool for P251. Claude's live try, behind a grant and with a reset at the end, is live.py (P247).
With --cure-first it opens the port with DTR and RTS off before the only try: the bench's cold arm. With two or more boards on USB, --port is needed.

When mpremote cannot open the port or enter the board's REPL, the board doctor (P282) runs two checks: whether `mpremote devs` lists the
port, and two seconds of the console with the port's lock. It prints mpremote's own error, each check's fact,
and one next step for your hands, as the last line. Its look at the console can restart the board.

Exit codes: 0 the board answered, 2 it did not, or reach.py could not run, and the last line says why."""


def main(argv=None, outside=None, operation=None):
    """Run the reach and print its lines, or with --json its one line. `outside` is the OutsideWorld a test gives (a run
    builds the project's), `operation` the ReachBoard a test gives with its Fakes. Returns the exit code."""
    return run_cli(HelpText("reach.py", __doc__.strip(), EPILOG), operation or ReachBoard(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
