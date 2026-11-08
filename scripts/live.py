#!/usr/bin/env python3
"""Run a short piece of code on the running board inside a grant, say whether the board ran it, and reset it (P247)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.bench import board_grant
from spark.bench import build_project_outside_world
from spark.bench.run_live_code import RunLiveCode
from spark.core.cli import HelpText, run_cli

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


def main(argv=None, outside=None, operation=None):
    """Run one live try and print its lines, or with --json its one line. `outside` is the OutsideWorld a test gives (a run
    builds the project's), `operation` the RunLiveCode a test gives with its Fakes. Returns the exit code."""
    return run_cli(HelpText("live.py", __doc__.strip(), EPILOG), operation or RunLiveCode(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
