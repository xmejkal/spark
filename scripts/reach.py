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

Before the line runs, reach.py asks the board question (P892). It lists the boards with `mpremote devs`, also for a
--port, and a /dev/tty. port is its /dev/cu. port. On the board that spark keeps for the project, known by its USB
serial, it asks nothing. Another board, told apart by its USB serial, stops with other_board, and a board with a USB
serial in a project that keeps no board stops with no_known_board. Both name look.py, and nothing ran on the board. A
board that spark cannot tell by its USB serial is asked on every run, in your terminal, or by --replies with your own
file that holds {"replies": {"reach.run_on_board.<id>": true}}: a board with no serial, a --port that the list does
not hold, and, while the kept board's record trusts no USB serial (it showed none, or one that its firmware set), a
board on Espressif's own USB whose serial does not start with the kept MAC. One yes or one no is for one run. A no is
answered_no, and nothing ran on the board. With --json an open question prints one line: reached false, port,
product, open and known_board. Every other stop prints nothing on stdout. For other_board, no_known_board and
answered_no, the last line on stderr is the stop's fix, after its sentence.

When mpremote cannot open the port or enter the board's REPL, the board doctor (P282) runs two checks: whether `mpremote devs` lists the
port, and two seconds of the console with the port's lock. It prints mpremote's own error, each check's fact,
and one next step for your hands, as the last line. Its look at the console can restart the board.

Exit codes: 0 the board answered, 2 it did not, reach.py could not run, or the board question stopped it
(other_board, no_known_board, needs_reply, answered_no), and the last line says why."""


def main(argv=None, outside=None, operation=None):
    """Run the reach and print its lines, or with --json its one line. `outside` is the OutsideWorld a test gives (a run
    builds the project's), `operation` the ReachBoard a test gives with its Fakes. Returns the exit code."""
    return run_cli(HelpText("reach.py", __doc__.strip(), EPILOG), operation or ReachBoard(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
