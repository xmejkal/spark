#!/usr/bin/env python3
"""Read the board on USB without changing it, compare it with the project's board record, and print a token (P219)."""

import sys

from spark.bench import build_project_outside_world
from spark.bench.look_at_board import LookAtBoard
from spark.core.cli import HelpText, run_cli

EPILOG = """It reads the board with `mpremote devs` (the list of boards on USB) and `esptool flash_id`. It writes nothing,
erases nothing and changes no flash. The board restarts while esptool reads it: a running program stops and starts again.
Nothing else on the board is touched. The board's record is the one requirements.json names. The look compares the chip
and the flash size, and prints each as same, differs or unknown. It also prints the board's MAC.

The verdict: another chip, or a flash smaller than the image, is a stop (deploy.py will refuse). A flash that differs
but holds the image, or a field that is unknown, is a warning that the person must accept. The token is two halves of 4
hex digits: one from the board's MAC and one from the image (the one a passed run names, or with --no-simulation, the
image file). It shows that a look was made on this board for this image. It is not the yes and it is not a secret. With
no MAC, no image or no evidence for the image, there is no token, and the line says why.

For an image that a passed run tested, the look also prints what that run did not test (the caveats), and under "what this
simulation cannot show, so test it on the board:" the limits of the project that sim/WHAT-THIS-CANNOT-SHOW.md holds, read
from the limits section of every passed log. --json has them as data.limits, a list of {component, sentence}. With
--no-simulation no log is read, so no limits are printed, and an empty list is not a pass: it never means the project has none.
Under "no scenario named these must lines, so test them on the board:" it lists each must line of .spark/project.json that no passed
scenario named in a step's own name: key (--json: data.unnamed_must). [] is not a pass: when a log cannot say, a caveat that contains
"not checked:" says so.

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
or could not check something (a field unknown, no token, a last deploy it could not check), and the sentence says why. A crash is 2 too: with --json
an envelope with one unchecked item, code crash; on stderr `look: crashed, <class>`, what to do, and the traceback. Without --json the same
on stderr and nothing on stdout."""


def main(argv=None, outside=None):
    """Print the look. `outside` is the OutsideWorld a test gives; a run builds the project's. Returns the exit code."""
    return run_cli(HelpText("look.py", __doc__.strip().split("\n\n")[0], EPILOG), LookAtBoard(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
