#!/usr/bin/env python3
"""Run one line on the board on USB, and cure it once when its USB output died at power-on: the PO's bench tool (P251)."""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import board_look
import board_reach
import tools
from board_connection import BoardConnection
from board_console import ConsoleProbe
from image_check import runnable
from outcomes import EXIT_COULD_NOT_RUN, EXIT_OK

#: What reach.py says after any run: mpremote's exec stops the firmware that ran (reach-test.md).
FIRMWARE_STOPPED_MESSAGE = "the firmware is stopped: press R or replug to run it"
EPILOG = """It runs print("reached") on the board with mpremote's exec. When mpremote says "could not enter raw repl", it
opens the port once with DTR and RTS off, which restarted a XIAO ESP32-C6 whose USB output died at power-on, waits until
the port is there again, and runs the line once more. It says whether the board answered, whether a cure ran and what
the board printed during it. The exec stops the firmware that ran: press R or replug to run it again.

It is the PO's bench tool for P251. With --cure-first it opens the port with DTR and RTS off before the only try: the
bench's cold arm. With two or more boards on USB, --port is needed.

Exit codes: 0 the board answered, 2 it did not, or reach.py could not run, and the last line says why."""


def lines(port, result):
    """The lines a person reads, for a ReachResult."""
    cure = result.cure
    out = ["port    %s" % port, "first   %s" % ("did not answer" if result.first_try_failed else "answered")]
    if cure is not None:
        heard = (cure.heard or "").strip() or "nothing"
        out.append("cure    %s" % ("could not read the port: %s" % cure.why if cure.heard is None else
                                   "restart heard" if cure.restart_heard else "no restart heard"))
        out += ["        %s" % line for line in heard.splitlines()] if cure.heard is not None else []
    out.append("reached" if result.reached else "not reached: %s" % result.why)
    if result.reached and result.why:
        out.append(result.why)
    out.append(FIRMWARE_STOPPED_MESSAGE)
    return ["  " + line for line in out]


def as_json(port, result):
    """One line of JSON for the bench log: the result, the port, and `at`, the time it was written."""
    fields = result._asdict()
    fields["cure"] = result.cure._asdict() if result.cure is not None else None
    return json.dumps(dict(fields, port=port, at=time.strftime("%Y-%m-%dT%H:%M:%S%z")))


def main(argv=None, run=subprocess.run, probe=None):
    """Run the reach. `run` is how a command runs, `probe` the console probe (default: ConsoleProbe for mpremote's
    Python). Returns the exit code."""
    parser = argparse.ArgumentParser(prog="reach.py", description=__doc__.strip(), epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="the project folder whose tools list names mpremote (default: here)")
    parser.add_argument("--port", help="the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more boards on USB")
    parser.add_argument("--json", action="store_true", help="print one line of JSON for the bench log")
    parser.add_argument("--cure-first", action="store_true",
                        help="open the port with DTR and RTS off before the only try (the bench's cold arm)")
    args = parser.parse_args(argv)
    try:
        shell = tools.find("board-shell", args.project)
        port = args.port or board_look.PortFinder(shell, run).require_one_port("reach.py")
    except (tools.ToolProblem, board_look.LookStop) as cannot:
        print("reach.py: %s" % cannot, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    probe = probe or ConsoleProbe.for_tool(shell, port, run)
    if args.cure_first and probe is None:
        print("reach.py: %s" % board_reach.NO_PROBE_MESSAGE, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    result = board_reach.reach(BoardConnection(runnable(shell), port, run), probe, cure_first=args.cure_first)
    print(as_json(port, result) if args.json else "\n".join(lines(port, result)))
    return EXIT_OK if result.reached else EXIT_COULD_NOT_RUN


if __name__ == "__main__":
    sys.exit(main())
