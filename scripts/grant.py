#!/usr/bin/env python3
"""Let Claude run code on one board for a time limit: one yes typed in your own terminal (P253), and the check a later call makes."""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

import board_doctor
import board_grant
import board_look
import boards
import flasher
import store
import tools
from deploy_gate import GateClosedError, TerminalConsentStrategy, format_rerun_line
from outcomes import EXIT_COULD_NOT_RUN, EXIT_OK, EXIT_PROBLEMS

RESTART = ("the board restarts while it is read: a running program stops and starts again. Nothing is erased or "
           "written. If it then waits in download mode, press its RESET once.")
EPILOG = """grant.py --minutes N reads the board on USB once with esptool (the board restarts), and asks you in your own
terminal to let Claude run code on that board for N minutes from your yes (1 to 1440, one day). A pipe, a heredoc or
Claude Code's ! is no terminal, so grant.py gives no grant there. Your yes is kept in your store as a file named by the
MAC with dashes, for example grants/8c-bf-ea-cc-97-70.json, with the MAC, the board's token (the first half of look.py's
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


def describe(result):
    """The line a person reads, for a GrantCheckResult."""
    if result.granted:
        return "  granted: board %s until %s" % (result.grant.mac, board_grant.say_in_local_zone(result.grant.expires_at))
    return "  not granted: %s" % board_grant.MESSAGE_FOR[result.why]


def to_json(result):
    """One line of JSON for a GrantCheckResult: granted, why (a code or null), and the grant's fields or null."""
    grant = result.grant._asdict() if result.grant is not None else None
    return json.dumps({"granted": result.granted, "why": result.why, "grant": grant})


def main(argv=None, run=subprocess.run, consent=None, now=board_grant.read_local_time):
    """Issue or check a grant. `run` is how a command runs, `consent` how the person says yes (default: a real
    terminal), `now` the clock. Returns the exit code."""
    parser = argparse.ArgumentParser(prog="grant.py", description=__doc__.strip(), epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--minutes", type=int, help="give a grant for this many minutes from your yes (1 to 1440)")
    mode.add_argument("--check", action="store_true", help="say whether the board on USB has a live grant now")
    parser.add_argument("--scope", choices=board_grant.SCOPES, default=board_grant.SCOPE_LIVE,
                        help="with --minutes: what the grant allows. live (default) lets Claude run code on the "
                        "board. deploy lets Claude erase it and write a passed image with deploy.py, with no yes "
                        "typed for each deploy")
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="the project folder whose tools list names mpremote and esptool (default: here)")
    parser.add_argument("--port", help="the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more boards on USB")
    parser.add_argument("--json", action="store_true", help="with --check, print one line of JSON")
    args = parser.parse_args(argv)
    if args.json and not args.check:
        parser.error("--json goes with --check only")
    if args.check and args.scope != board_grant.SCOPE_LIVE:
        parser.error("--scope goes with --minutes only: --check looks for a live grant")
    try:
        finder = board_look.PortFinder(tools.find("board-shell", args.project), run)
        if args.check:
            result = board_grant.GrantService(finder, now=now).check(args.port)
            print(to_json(result) if args.json else describe(result))
            return EXIT_OK if result.granted else EXIT_PROBLEMS
        hint = flasher.EsptoolFlasher.boot_hint_for(boards.ButtonPlaces.of_project(args.project))
        reader = board_look.EsptoolReader(tools.find("flasher", args.project), run, hint)
        line = format_rerun_line(__file__, (["--scope", args.scope] if args.scope != board_grant.SCOPE_LIVE else [])
                                 + ["--minutes", args.minutes, "--project", args.project.resolve()]
                                 + (["--port", args.port] if args.port else []))
        grant = board_grant.GrantService(finder, reader, now=now).issue(
            args.port, args.minutes, consent or TerminalConsentStrategy(line), before_look=lambda: print("  " + RESTART),
            scope=args.scope)
    except GateClosedError as closed:
        print("grant.py: %s" % closed, file=sys.stderr)
        return closed.code
    except (tools.ToolProblem, board_look.LookStop) as cannot:
        if args.json:
            print(to_json(board_grant.GrantCheckResult(False, None, board_grant.WHY_COULD_NOT_RUN)))
        if isinstance(cannot, board_look.LookStop):
            print("\n".join(board_doctor.stop_lines("grant.py", cannot, args.project, run)), file=sys.stderr)
        else:
            print("grant.py: %s" % cannot, file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    print("  granted (%s): board %s (token %s) until %s" % (grant.scope, grant.mac, grant.board_token, grant.expires_at))
    if grant.scope == board_grant.SCOPE_DEPLOY:
        grant_file = store.place("grants") / (board_grant.GrantStore.key(grant.mac, grant.scope) + ".json")
        print("  Claude can now run deploy.py on this board with no yes from you, and it erases ALL of the board's "
              "flash each time, until that time. To end it sooner, run: rm %s" % shlex.quote(str(grant_file)))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
