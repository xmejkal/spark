#!/usr/bin/env python3
"""Let Claude run code on one board for a time limit: one yes typed in your own terminal (P253), and the check a later call makes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.bench import build_project_outside_world
from spark.bench.check_grant import CheckGrant
from spark.bench.issue_grant import IssueGrant
from spark.core.cli import HelpText, run_cli

#: The flag that picks the check. argparse takes a prefix of it too (`--ch`), so `operation_for` does.
CHECK_FLAG = "--check"

EPILOG = """grant.py --minutes N reads the board on USB once with esptool (the board restarts), and asks you in your own
terminal to let Claude run code on that board for N minutes from your yes (1 to 1440, one day). A pipe, a heredoc or
Claude Code's ! is no terminal, so grant.py gives no grant there. Your yes is kept in your store as a file named by the
MAC with dashes, for example grants/8c-bf-ea-xx-xx-xx.json, with the MAC, the board's token (the first half of look.py's
token), who said yes and when it ends. A new grant replaces the old one. To end a grant early, delete that file. The
file is a plain file in your store: anything that can write your store can write it.

grant.py --check says whether the board on USB has a grant now. It runs only `mpremote devs`, which lists the boards and
never opens a port, so the running program goes on. It knows the board by its USB serial, which is the MAC on a board
with a built-in USB port, like the ESP32-C6's. A board on a USB bridge chip gets no grant, and the sentence says why.

While the grant lasts, live.py runs Claude's code on the board (P247). With two or more boards on USB, --port is
needed.

grant.py --scope deploy --minutes N gives a deploy grant: for N minutes from your yes, Claude may run deploy.py
on this board and erase ALL of its flash, with no yes typed for each deploy. Its question says so. The file is
grants/<MAC with dashes>-deploy.json, so a live grant and a deploy grant stand side by side. A deploy grant covers
only a deploy whose look matched the board record (no warning, no unknown field, no stop) and that does not pass
--ignore-older-runs; deploy.py asks you in your terminal for anything else. Delete the file to end it. It needs no
built-in USB port: deploy.py finds it by the MAC its own look reads. --check looks for a live grant only.

When esptool's read of the board fails, the board doctor (P282) runs two checks: whether `mpremote devs` lists the
port, and two seconds of the console with the port's lock. It prints esptool's own error line, each check's fact,
and one next step for your hands, as the last line. Its look at the console can restart the board.

Exit codes: 0 the grant was given or is valid, 1 refused (no grant, it ended, the person answered no, the serial is not
the MAC), 2 grant.py could not run (no board, two boards, the MAC not read, --minutes out of range, no terminal), and the
last line says why. With --check --json, a run that could not look prints why "could not run" too."""


def operation_for(argv):
    """The Operation `argv` asks for: CheckGrant when an item is `--check` or a prefix of it longer than `--` (argparse's
    abbreviations take `--ch`), else IssueGrant. Each has its own arguments, so each mode's `--help` lists its own."""
    return CheckGrant if any(len(item) > len("--") and CHECK_FLAG.startswith(item) for item in argv) else IssueGrant


def main(argv=None, outside=None, operation=None):
    """Issue or check a grant. `outside` is the OutsideWorld a test gives (a run builds the project's), `operation` the
    CheckGrant or IssueGrant a test gives with its Fakes. Returns the exit code."""
    argv = sys.argv[1:] if argv is None else list(argv)
    return run_cli(HelpText("grant.py", __doc__.strip(), EPILOG), operation or operation_for(argv)(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
