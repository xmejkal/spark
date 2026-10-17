#!/usr/bin/env python3
"""Let Claude run code on one board for a time limit: one yes typed in your own terminal (P253), and the check a later call makes."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import board_grant
import board_look
import tools
from deploy_gate import GateClosedError, TerminalConsentStrategy
from outcomes import EXIT_COULD_NOT_RUN, EXIT_OK, EXIT_PROBLEMS

RESTART = "the board restarts while it is read: a running program stops and starts again. Nothing is erased or written."
EPILOG = """grant.py --minutes N reads the board on USB once with esptool (the board restarts), and asks you in your own
terminal to let Claude run code on that board until a time N minutes from now. A pipe, a heredoc or Claude Code's ! is
no terminal, so Claude cannot give itself a grant. Your yes is kept in your store as grants/<the MAC>.json, with the MAC,
the board's token (the first half of look.py's token), who said yes and when it ends. A new grant replaces the old one.
To end a grant early, delete that file.

grant.py --check says whether the board on USB has a grant now. It runs only `mpremote devs`, which lists the boards and
never opens a port, so the running program goes on. It knows the board by its USB serial, which is the MAC on a board
with a built-in USB port, like the ESP32-C6's. A board on a USB bridge chip gets no grant, and the sentence says why.

No code runs on the board yet: P247 adds the live try behind this grant. With two or more boards on USB, --port is
needed.

Exit codes: 0 the grant was given or is valid, 1 refused (no grant, it ended, you answered no), 2 grant.py could not
run, and the last line says why."""


def describe(result):
    """The line a person reads, for a GrantCheckResult."""
    if result.granted:
        return "  granted: board %s until %s" % (result.grant.mac, result.grant.expires_at)
    return "  not granted: %s" % board_grant.MESSAGE_FOR[result.why]


def to_json(result):
    """One line of JSON for a GrantCheckResult: granted, why (a code or null), and the grant's fields or null."""
    grant = result.grant._asdict() if result.grant is not None else None
    return json.dumps({"granted": result.granted, "why": result.why, "grant": grant})


def main(argv=None, run=subprocess.run, consent=None, now=board_grant.utc_now):
    """Issue or check a grant. `run` is how a command runs, `consent` how the person says yes (default: a real
    terminal), `now` the clock. Returns the exit code."""
    parser = argparse.ArgumentParser(prog="grant.py", description=__doc__.strip(), epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--minutes", type=int, help="give a grant for this many minutes (a whole number, 1 or more)")
    mode.add_argument("--check", action="store_true", help="say whether the board on USB has a grant now")
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="the project folder whose tools list names mpremote and esptool (default: here)")
    parser.add_argument("--port", help="the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more boards on USB")
    parser.add_argument("--json", action="store_true", help="with --check, print one line of JSON")
    args = parser.parse_args(argv)
    try:
        finder = board_look.PortFinder(tools.find("board-shell", args.project), run)
        if args.check:
            result = board_grant.GrantService(finder, now=now).check(args.port)
            print(to_json(result) if args.json else describe(result))
            return EXIT_OK if result.granted else EXIT_PROBLEMS
        reader = board_look.EsptoolReader(tools.find("flasher", args.project), run)
        print("  " + RESTART)
        line = " ".join(["grant.py", "--minutes", str(args.minutes)] + (["--port", args.port] if args.port else []))
        grant = board_grant.GrantService(finder, reader, now=now).issue(
            args.port, args.minutes, consent or TerminalConsentStrategy(line))
    except GateClosedError as closed:
        print("grant.py: %s" % closed, file=sys.stderr)
        return closed.code
    except (tools.ToolProblem, board_look.LookStop) as cannot:
        print("grant.py: %s" % cannot, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    print("  granted: board %s (token %s) until %s" % (grant.mac, grant.board_token, grant.expires_at))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
