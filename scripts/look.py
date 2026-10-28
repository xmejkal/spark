#!/usr/bin/env python3
"""Read the board on USB without changing it, compare it with the project's board record, and print a token (P219)."""

import argparse
import subprocess
import sys
from pathlib import Path

import board_doctor
import board_envelope
import board_look
import boards
from image_evidence import IGNORE_OLDER_RUNS_FLAG, NO_SIMULATION_FLAG, evidence_for
from outcomes import EXIT_COULD_NOT_RUN, AnsweringParser, BadArgument
from text_guards import guard_lines, guard_sentence

EPILOG = """It reads the board with `mpremote devs` (the list of boards on USB) and `esptool flash_id`. It writes nothing,
erases nothing and changes no flash. The board restarts while esptool reads it: a running program stops and starts again.
Nothing else on the board is touched. The board's record is the one requirements.json names. The look compares the chip
and the flash size, and prints each as same, differs or unknown. It also prints the board's MAC.

The verdict: another chip, or a flash smaller than the image, is a stop (deploy.py will refuse). A flash that differs
but holds the image, or a field that is unknown, is a warning that the person must accept. The token is two halves of 4
hex digits: one from the board's MAC and one from the image (the one a passed run names, or with --no-simulation, the
image file). It shows that a look was made on this board for this image. It is not the yes and it is not a secret. With
no MAC, no image or no evidence for the image, there is no token, and the line says why.

With two or more boards on USB, --port is needed: the look lists them and reads none. --ignore-older-runs gives a token
even when a log in sim/runs/ tested another image, as deploy.py --ignore-older-runs flashes it. --no-simulation gives a
token for an image that no simulation tested: firmware/ has a main.py, every .py file compiles, no run in sim/runs/ failed on the image and the image holds
firmware/ as it is now. Else it prints why not, and the command that builds the image. deploy.py needs the same flag.

When esptool's read of the board fails, the board doctor (P282) runs two checks: whether `mpremote devs` lists the
port, and two seconds of the console with the port's lock. It prints esptool's own error line, each check's fact,
and one next step for your hands, as the last line. Its look at the console can restart the board.

--json prints one envelope on stdout (docs/guide/agents.md): the look in `data`, the stops and warnings as `problems`, the
unknown fields, a missing token and a last deploy it could not check as `unchecked`, and, when there is a token, the deploy step with `needs_yes`. The
board doctor's lines still go to stderr. Every `problems` and `unchecked` item has a `code` (scripts/board_codes.py). A bad flag with
--json prints an envelope (status could-not-run, code bad_argument, exit 2); without --json it prints the usage and the error on stderr and
exits 2. Exit codes do not change; the envelope's status is the exit code's.

Exit codes: 0 every field matches, there is a token and the last deploy was checked, 1 a field differs or the look found a stop, 2 it could not run
or could not check something (a field unknown, no token, a last deploy it could not check), and the sentence says why."""


def main(argv=None, run=subprocess.run):
    """Print the look. `run` is how a command runs. Returns the exit code."""
    parser = AnsweringParser(prog="look.py", description=__doc__.strip().split("\n\n")[0], epilog=EPILOG,
                             formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="the project folder with requirements.json and sim/ (default: here)")
    parser.add_argument("--port", help="the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more boards on USB "
                        "(one board on two nodes named by its serial counts once)")
    which = parser.add_mutually_exclusive_group()
    which.add_argument(IGNORE_OLDER_RUNS_FLAG, action="store_true",
                       help="give a token even when a log in sim/runs/ tested another image (default: no token)")
    which.add_argument(NO_SIMULATION_FLAG, action="store_true",
                       help="give a token for an image that no simulation tested, when firmware/ has a main.py, "
                       "compiles and is what the image holds (default: a passed run must name the image)")
    parser.add_argument("--json", action="store_true", help="print one envelope on stdout (docs/guide/agents.md)")
    argv = sys.argv[1:] if argv is None else list(argv)
    try:
        args = parser.parse_args(argv)
    except BadArgument as bad:  # P433: with --json an envelope, else the usage on stderr as argparse prints it
        if "--json" not in argv:
            parser.exit_with_usage(guard_lines(str(bad)))
        _print_json(board_envelope.bad_argument_envelope("look", bad))
        return EXIT_COULD_NOT_RUN
    evidence = evidence_for(args.project, args.no_simulation, args.ignore_older_runs)
    try:
        report = board_look.looker(args.project, run).run(args.project, args.port, evidence)
    except board_look.LookStop as stop:
        lines, doctor = board_doctor.stop_answer("look.py", stop, args.project, run)
        places = boards.ButtonPlaces.of_project(args.project)
        # --- MVP --- the port and the board record's button words as typed or written, each on one line (P430)
        print(guard_sentence("\n".join(lines), args.port, places.boot, places.reset, places.orientation),
              file=sys.stderr)
        if args.json:
            _print_json(board_envelope.look_stop_envelope(stop, doctor, places))
        return EXIT_COULD_NOT_RUN
    if args.json:
        _print_json(board_envelope.look_envelope(report, args.project.resolve(), evidence))
    else:
        print("\n".join(board_look.report_lines(report)))
    return report.exit_code()


def _print_json(envelope):
    print(board_envelope.dumps(envelope))


if __name__ == "__main__":
    sys.exit(main())
