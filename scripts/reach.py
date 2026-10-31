#!/usr/bin/env python3
"""Run one line on the board on USB, and cure it once when its USB output died at power-on: the PO's bench tool (P251)."""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import board_doctor
import boards
import board_look
import board_reach
import tools
from board_connection import BoardConnection
from board_console import ConsoleProbe
from spark.core.outcomes import EXIT_COULD_NOT_RUN, EXIT_OK
from spark.core.text_guards import guard_lines, guard_sentence, printable

#: What reach.py says after the board answered: mpremote's exec stops the firmware that ran (reach-test.md).
FIRMWARE_STOPPED_MESSAGE = "the firmware is stopped: press R or replug to run it"
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


def describe(port, result):
    """The lines a person reads, for a ReachResult."""
    cure = result.cure
    first = {None: "none: the cure came first", True: "did not answer", False: "answered"}[result.first_try_failed]
    out = ["port    %s" % port, "first   %s" % first]
    if cure is not None:
        heard = ("restart heard" if cure.restart_heard else "boot tail heard, no rst: line" if cure.boot_heard
                 else "no restart heard")
        out.append("cure    %s, the port %s" % (heard,
                                                "was back" if cure.port_back else "was not back"))
        out += ["        its read failed: %s" % cure.why] if cure.why else []
        out += ["        %s" % line for line in (cure.heard.strip() or "nothing heard").splitlines()]
    out.append("reached" if result.reached else "not reached: %s" % result.why)
    if result.reached and result.why:
        out.append(result.why)
    if result.reached:
        out.append(FIRMWARE_STOPPED_MESSAGE)
    return ["  " + line for line in out]


def to_json(port, result, cure_first, doctor=None):
    """One line of JSON for the bench log: the result, the port, the arm, `doctor` (the board doctor's result when
    mpremote never got in, else null) and `at`, the time it was written."""
    fields = result._asdict()
    fields["cure"] = result.cure._asdict() if result.cure is not None else None
    fields["doctor"] = board_doctor.as_dict(doctor) if doctor is not None else None
    return json.dumps(dict(fields, port=port, cure_first=cure_first, at=time.strftime("%Y-%m-%dT%H:%M:%S%z")))


def main(argv=None, run=subprocess.run, probe=None):
    """Run the reach. `run` is how a command runs, `probe` the console probe (default: ConsoleProbe for mpremote's
    Python). Returns the exit code."""
    parser = argparse.ArgumentParser(prog="reach.py", description=__doc__.strip(), epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="the project folder whose tools list names mpremote (default: here)")
    parser.add_argument("--port", help="the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more boards on USB "
                        "(one board on two nodes named by its serial counts once)")
    parser.add_argument("--json", action="store_true", help="print one line of JSON for the bench log")
    parser.add_argument("--cure-first", action="store_true",
                        help="open the port with DTR and RTS off before the only try (the bench's cold arm)")
    args = parser.parse_args(argv)
    try:
        shell = tools.find("board-shell", args.project)
        finder = board_look.PortFinder(shell, run)
        port = args.port or finder.require_one_port("reach.py")
    except (tools.ToolProblem, board_look.LookStop) as cannot:
        # --- MVP --- data: device names, a tool's words and the project path as typed (P430)
        print(guard_sentence("reach.py: %s" % cannot, args.project), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    probe = probe or ConsoleProbe.for_tool(shell, port, run)
    if args.cure_first and probe is None:
        print("reach.py: %s" % board_reach.NO_PROBE_MESSAGE, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    result = board_reach.reach(BoardConnection(tools.command_for(shell), port, run), probe, cure_first=args.cure_first)
    try:
        doctor = (None if result.entered else
                  board_doctor.BoardDoctorService.for_board(finder, probe).examine(port, shell, result.why))
    except board_doctor.UnknownStepError as cannot:
        print(guard_lines("reach.py: no doctor: %s" % cannot), file=sys.stderr)  # --- MVP --- the tools list's words (P430)
        doctor = None
    if args.json:
        print(to_json(port, result, args.cure_first, doctor))
    else:
        lines = describe(port, result) + (["  " + line for line in board_doctor.describe(doctor, boards.ButtonPlaces.of_project(args.project))] if doctor else [])
        # --- MVP --- the port, the cure's read and the board's reply are data, each line shown guarded (P430)
        print("\n".join(printable(line) for line in lines))
    return EXIT_OK if result.reached else EXIT_COULD_NOT_RUN


if __name__ == "__main__":
    sys.exit(main())
