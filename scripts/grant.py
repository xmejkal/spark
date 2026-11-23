#!/usr/bin/env python3
"""
Give Claude a grant on one board for a time limit, or check one (P253).

Its `--help` sentence is the summary of the mode's Operation, IssueGrant's, CheckGrant's or DisallowDirectFlashing's
(P937, P1029), and EPILOG is the CLI's own text.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.bench import build_project_outside_world
from spark.bench.check_grant import CheckGrant
from spark.bench.direct_flashing import DISALLOW_FLAG, DisallowDirectFlashing
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

Before the read, grant.py asks the board question (P892), after its check of your terminal. On the board that spark
keeps for the project, known by its USB serial, it asks nothing. Another board, told apart by its USB serial, stops with
other_board, and a board with a USB serial in a project that keeps no board stops with no_known_board. Both name
look.py, and the board did not restart. A board that spark cannot tell by its USB serial is asked on every run, in your
terminal, or by --replies with your own file that holds {"replies": {"grant.read_board.<id>": true}}: a board with no
serial, and, while the kept board's record trusts no USB serial (it showed none, or one that its firmware set), a board
on Espressif's own USB whose serial does not start with the kept MAC. For a live grant, a board whose serial cannot be
its MAC (no serial, a bridge's serial, or a serial that a firmware set) is refused first with serial_not_mac, exit 1,
with no question and no read: only --scope deploy asks for it. A yes there lets grant.py read the board, and the grant
still asks its own yes. After the read, a MAC that is not the kept board's stops with other_board before that yes, and
no grant is kept. With no kept board and a board with no USB serial, a yes and a read give a deploy grant for a board
that no project keeps. A --port that the list does not hold stops with port_not_listed, and a /dev/tty. port is its
/dev/cu. port.

There are two no's. A no to the board question is answered_no with exit 2: the board was not read. A no to the grant's
own question, after the read, is answered_no with exit 1: the board did restart, and no grant is kept.

grant.py --check says whether the board on USB has a grant now. It runs only `mpremote devs`, which lists the boards and
never opens a port, so the running program goes on. It asks no board question. It knows the board by its USB serial,
which is the MAC on a board with a built-in USB port, like the ESP32-C6's. A board whose USB serial cannot be its MAC
(no serial, a USB bridge chip's serial, or a serial that a firmware set) gets no live grant: grant.py --minutes refuses
it from the list alone, before any question or read, and the sentence says why.

While the grant lasts, live.py runs Claude's code on the board (P247). With two or more boards on USB, --port is
needed.

grant.py --scope deploy --minutes N gives a deploy grant: for N minutes from your yes, Claude may run deploy.py
on this board and erase ALL of its flash, with no yes typed for each deploy. Its question says so. The file is
grants/<MAC with dashes>-deploy.json, so a live grant and a deploy grant stand side by side. A deploy grant covers
only a deploy whose look matched the board record (no warning, no unknown field, no stop) and that does not pass
--ignore-older-runs; deploy.py asks you in your terminal for anything else. Delete the file to end it. It needs no
built-in USB port: deploy.py finds it by the MAC its own look reads. --check looks for a live grant only.

grant.py --scope deploy --minutes N --no-simulation gives a deploy grant that also covers deploy.py --no-simulation:
Claude can then put firmware that no simulation tested on the board with no yes from you (direct flashing, P1029).
Without the flag, a deploy with no simulation always asks you. grant.py --disallow-direct-flashing writes the file
grants/direct_flashing_disallowed at once, with no question. While that file is there, no grant covers a deploy with
no simulation, and grant.py --no-simulation refuses with direct_flashing_disallowed, exit 1. To allow it again, delete
the file yourself. No Claude session writes, changes or deletes a file in the grants folder.

When esptool's read of the board fails, the board doctor (P282) runs two checks: whether `mpremote devs` lists the
port, and two seconds of the console with the port's lock. It prints esptool's own error line, each check's fact,
and one next step for your hands, as the last line. Its look at the console can restart the board.

If no board is on USB, or the named port is not, look at firmware/. When it calls deepsleep, the stop's last line, the
fix, says that the board can be in deep sleep. look.py's fix says the same (P1049). --json carries no fix yet (P1055).

Exit codes: 0 the grant was given or is valid, 1 refused (no grant, it ended, the person answered no to the grant, the
serial is not the MAC), 2 grant.py could not run (no board, two boards, the MAC not read, --minutes out of range, no
terminal) or the board question stopped it (other_board, no_known_board, needs_reply, answered_no to the board
question), and the last line says why. With --check --json, a run that could not look prints why "could not run" too."""


def operation_for(argv):
    """The Operation `argv` asks for: CheckGrant when an item is `--check` or a prefix of it longer than `--` (argparse's
    abbreviations take `--ch`), DisallowDirectFlashing for `--disallow-direct-flashing` or such a prefix (P1029), else
    IssueGrant. Each has its own arguments, so each mode's `--help` lists its own."""
    if any(len(item) > len("--") and CHECK_FLAG.startswith(item) for item in argv):
        return CheckGrant
    return DisallowDirectFlashing if any(len(item) > len("--") and DISALLOW_FLAG.startswith(item) for item in argv) else IssueGrant


def main(argv=None, outside=None, operation=None):
    """Issue or check a grant. `outside` is the OutsideWorld a test gives (a run builds the project's), `operation` the
    CheckGrant or IssueGrant a test gives with its Fakes. Returns the exit code."""
    argv = sys.argv[1:] if argv is None else list(argv)
    return run_cli(HelpText("grant.py", epilog=EPILOG), operation or operation_for(argv)(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
