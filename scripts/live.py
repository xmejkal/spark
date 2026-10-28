#!/usr/bin/env python3
"""Run a short piece of code on the running board inside a grant, say whether the board ran it, and reset it (P247)."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import board_doctor
import board_grant
import board_live
import board_look
import boards
import tools
from board_connection import BoardConnection
from board_console import ConsoleProbe
from outcomes import COULD_NOT_RUN, EXIT_COULD_NOT_RUN
from restricted_pins import BrokenRecordError
from text_guards import guard_sentence, printable

EPILOG = """live.py --code 'print(1)' runs the code on the board on USB with mpremote's exec, after two checks that do not
touch the board. First, the board must have a grant now: the person runs %s in their own terminal,
and live.py checks it with `mpremote devs` only. Second, the code must not write a number that the project's board
record names as a usb or flash pin (pin_roles), so time.sleep(12) is refused on a XIAO ESP32-C6 too. A refusal sends
nothing to the board.

If mpremote cannot enter the board's raw REPL, live.py cures the board once, as reach.py does, and tries again. When
it still cannot get in, it names both causes: a dead USB output, or firmware that does not read its console. The exec
stops the firmware that ran. So unless mpremote said it could not open the port or enter the raw REPL, live.py restarts the chip with
`mpremote reset`, even after code that never ends, and the firmware starts from boot. A pin that the code set and the firmware never sets
can keep its value through that reset (P252's bench), so live.py lists the GPIO numbers written in the code. That list
over-claims: print(1) lists GPIO1.

The record is the project's active board (boards/active.json). live.py does not match it against the board on USB.

--json prints one line with every field, null where it has none: answer (ran, raised, not_reached, refused_no_grant,
refused_pin, refused_no_parse, or could-not-run, the word outcomes.py shares), grant_why (grant.py's code when the grant refused), why, output, cure, reset (done, failed or null),
pins_checked (false when the record names no usb or flash pin) and gpio_numbers_in_code, with port.

When mpremote cannot open the port or enter the board's REPL, the board doctor (P282) runs two checks: whether `mpremote devs` lists the
port, and two seconds of the console with the port's lock. It prints mpremote's own error, each check's fact,
and one next step for your hands, as the last line. Its look at the console can restart the board. --json carries it as doctor.

Exit codes: 0 the board ran the code, 1 refused or the code raised, 2 the board did not answer, the reset failed, or
live.py could not run, and the last line says why. With two or more boards on USB, --port is needed.""" % board_grant.GRANT_COMMAND


def describe(result, places=boards.ButtonPlaces.EMPTY):
    """The lines a person reads, for a LiveTryResult. `places` names the buttons the doctor's steps mention."""
    out = ["answer  %s" % result.answer]
    out += ["why     %s" % result.why] if result.why else []
    out += ["output  %s" % line for line in result.output.splitlines()]
    out += ["reset   %s" % result.reset] if result.reset else []
    out += ["pins    %s" % board_live.NO_RESTRICTED_PINS_MESSAGE] if not result.pins_checked else []
    if result.gpio_numbers_in_code:
        out.append("gpio    the code writes %s, each a GPIO of this board"
                   % ", ".join(str(gpio) for gpio in result.gpio_numbers_in_code))
    if result.doctor:
        out += board_doctor.describe(result.doctor, places)
    # --- MVP --- the board's reply and the doctor's lines are data, one line each, shown guarded (P430)
    return "\n".join("  " + printable(line) for line in out)


def to_json(port, result):
    """One line of JSON for a LiveTryResult, with the port."""
    fields = result._asdict()
    fields["cure"] = result.cure._asdict() if result.cure is not None else None
    fields["doctor"] = board_doctor.as_dict(result.doctor) if result.doctor is not None else None
    return json.dumps(dict(fields, port=port))


def main(argv=None, run=subprocess.run, probe=None, now=board_grant.read_local_time):
    """Run one live try. `run` is how a command runs, `probe` the console probe (default: ConsoleProbe for mpremote's
    Python), `now` the clock. Returns the exit code."""
    parser = argparse.ArgumentParser(prog="live.py", description=__doc__.strip(), epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--code", required=True, help="the code to run on the board, e.g. 'print(1)'")
    parser.add_argument("--project", type=Path, default=Path("."),
                        help="the project folder whose boards/active.json names the board and whose tools list names mpremote (default: here)")
    parser.add_argument("--port", help="the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more boards on USB "
                        "(one board on two nodes named by its serial counts once)")
    parser.add_argument("--json", action="store_true", help="print one line of JSON")
    args = parser.parse_args(argv)
    port = args.port
    try:
        shell = tools.find("board-shell", args.project)
        finder = board_look.PortFinder(shell, run)
        port = port or finder.require_one_port("live.py")
        probe = probe or ConsoleProbe.for_tool(shell, port, run)
        doctor = board_doctor.BoardDoctorService.for_board(finder, probe)
        service = board_live.LiveTryService(board_grant.GrantService(finder, now=now),
                                            BoardConnection(tools.command_for(shell), port, run), probe,
                                            boards.load(args.project), doctor, shell)
        result = service.run(args.code, port)
    except (tools.ToolProblem, board_look.LookStop, boards.BoardError, BrokenRecordError) as cannot:
        if args.json:
            empty = dict.fromkeys(board_live.LiveTryResult._fields)
            print(json.dumps(dict(empty, answer=COULD_NOT_RUN, why=str(cannot), port=port)))
        # --- MVP --- the sentence can hold the port and the project path as typed: put on one line, then guarded; --json above keeps it raw (P430)
        print(guard_sentence("live.py: %s" % cannot, port, args.project), file=sys.stderr)
        return EXIT_COULD_NOT_RUN
    print(to_json(port, result) if args.json else describe(result, boards.ButtonPlaces.of_project(args.project)))
    return board_live.exit_code(result)


if __name__ == "__main__":
    sys.exit(main())
