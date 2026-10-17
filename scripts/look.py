#!/usr/bin/env python3
"""Read the board on USB without changing it, compare it with the project's board record, and print a token (P219)."""

import argparse
import subprocess
import sys
from pathlib import Path

import board_doctor
import board_look
from outcomes import EXIT_COULD_NOT_RUN

RESTART = "the board restarts while it is read: a running program stops and starts again. Nothing is erased or written."
TOKEN = "token  %s  for deploy.py --token. It is not your yes: deploy.py asks for that."
EPILOG = """It reads the board with `mpremote devs` (the list of boards on USB) and `esptool flash_id`. It writes nothing,
erases nothing and changes no flash. The board restarts while esptool reads it: a running program stops and starts again.
Nothing else on the board is touched. The board's record is the one requirements.json names. The look compares the chip
and the flash size, and prints each as same, differs or unknown. It also prints the board's MAC.

The verdict: another chip, or a flash smaller than the image, is a stop (deploy.py will refuse). A flash that differs but
holds the image, or a field that is unknown, is a warning that the person must accept. The token is two halves of 4
hex digits: one from the board's MAC and one from the image that a passed run names. It shows that a look was made on this
board for this image. It is not the yes and it is not a secret. With no MAC, no image or no passed run, there is no token,
and the line says why.

With two or more boards on USB, --port is needed: the look lists them and reads none. --ignore-older-runs gives a
token even when a log in sim/runs/ tested another image, as deploy.py --ignore-older-runs flashes it.

When esptool's read of the board fails, the board doctor (P282) runs two checks: whether `mpremote devs` lists the
port, and two seconds of the console with the port's lock. It prints esptool's own error line, each check's fact,
and one next step for your hands, as the last line. Its look at the console can restart the board.

Exit codes: 0 every field matches and there is a token, 1 a field differs or the look found a stop, 2 it could not run
or could not check something (a field unknown, no token), and the sentence says why."""


def lines(report, token=True):
    """The lines a person reads, for a Report. deploy.py prints them without the token line."""
    reading, name = report.reading, report.record["id"]
    shown = {"chip": reading.chip, "flash": "%s MB" % reading.flash_mb if reading.flash_mb is not None else None}
    out = [RESTART, "port   %s" % report.port, "mac    %s" % (reading.mac or "not read")]
    out += ["%-6s %-9s %s" % (field, report.fields[field], shown[field] or "not read") for field in shown]
    out += ["%s: deploy.py will refuse." % stop for stop in report.stops]
    out += ["%s. deploy.py will ask you to accept it." % warning for warning in report.warnings]
    if report.unknown:
        out.append("%d field%s unknown (%s): deploy.py will ask you to accept it."
                   % (len(report.unknown), "" if len(report.unknown) == 1 else "s",
                      ", ".join("%s: %s" % each for each in report.unknown.items())))
    if report.verdict == board_look.VERDICT_MATCH:
        out.append("all fields match the board record %s." % name)
    if token:
        mine = report.token()
        out.append(TOKEN % mine if mine else "no token: %s" % report.no_token_reason())
    return ["  " + line for line in out]


def main(argv=None, run=subprocess.run):
    """Print the look. `run` is how a command runs. Returns the exit code."""
    parser = argparse.ArgumentParser(prog="look.py", description=__doc__.strip().split("\n\n")[0], epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="the project folder with requirements.json and sim/ (default: here)")
    parser.add_argument("--port", help="the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more boards on USB")
    parser.add_argument("--ignore-older-runs", action="store_true",
                        help="give a token even when a log in sim/runs/ tested another image (default: no token)")
    args = parser.parse_args(argv)
    try:
        report = board_look.looker(args.project, run).run(args.project, args.port, args.ignore_older_runs)
    except board_look.LookStop as stop:
        print("\n".join(board_doctor.stop_lines("look.py", stop, args.project, run)), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    print("\n".join(lines(report)))
    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
