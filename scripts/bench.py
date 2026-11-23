#!/usr/bin/env python3
"""The bench in spark's store: show each board on USB with what the store holds of it (P919), register a project that is
not spark's, and record that project's deploys (P920). No verb opens a port."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.bench import build_project_outside_world
from spark.bench.record_deploy import RecordDeploy
from spark.bench.register_project import RegisterProject
from spark.bench.show_bench import ShowBench
from spark.core.cli import HelpText, run_cli

#: The verbs, each the Operation it runs. With no verb word, bench.py shows.
VERBS = {"show": ShowBench, "register": RegisterProject, "record": RecordDeploy}
DEFAULT_VERB = "show"
#: The last paragraph of every verb's help.
VERBS_LINE = 'The verbs: bench.py {show,register,record}, show the default. "bench.py <verb> --help" prints that verb\'s own help.'

SHOW_NOTES = """bench.py show runs only `mpremote devs`, which lists the boards on USB and never opens a port, so a running
program goes on. It asks no question and writes nothing. For each board it reads three records in spark's store: the
deploys (boards/), the board that a look kept for a project (known-boards/) and the grants (grants/). Every value
comes from a record or from the list. The text prints the last two bytes of a MAC; --json carries it whole.

A board is named by a kept record whose USB serial or MAC part matches, else by the MAC part of its USB serial, which
is the serial's and was not read from the chip. Two clone boards with a bridge chip can share a serial: then both are
named alike. A board with no USB serial, a serial that its firmware set, or a bridge's serial that no project keeps
cannot be told apart, so its deploys and its deploy grant are not checked. look.py, run in the project that uses the
board, reads it and keeps it. The live grant is found by the USB serial, as grant.py --check finds it.

The names after "deploys from" are the project folder names that spark's deploys recorded, and the registered names
that bench.py record wrote, each with "by" and its tool. The two never merge. The date after "last" is the date of
the last-deploy line: in the machine's zone when the stored time has a zone, and as stored when it has none or is no
time. The date after "since" follows the same rule. --json keeps the stored text.

With --json it prints one envelope: data.boards (docs/guide/agents/bench.md).

Exit codes: 0 the list ran and every part of every board was read, also with no board on USB; 2 mpremote could not
list the boards (data.boards is null) or a part was not checked (each is an unchecked item, and data still holds what
was read), or an argument is wrong. Never 1: the view finds no problem."""

REGISTER_NOTES = """bench.py register writes the name once into spark's store (registered-projects.json), with its origin and its
tool, and writes the launcher (launcher/bench.py in the store). A tool outside spark runs the launcher with any python3
to reach bench.py record, always on the store the launcher lives in. Run it from a spark checkout that stays: the launcher runs this Python and this bench.py.

The same name with the same origin changes nothing, and with another --tool it replaces the tool. A name with another
origin, or a name on spark's projects list, is taken. Every run writes the launcher again, which repairs it.

With --json it prints one envelope: data.registered, data.changed and data.launcher (docs/guide/agents/bench.md).

Exit codes: 0 registered, or nothing changed; 2 not registered: the name is not plain or is taken, the origin or the
tool is blank, the store refused, or an argument is wrong; 2 also when the name was registered and the launcher was not
written (data.launcher is null): run the same command again. Never 1."""

RECORD_NOTES = """bench.py record adds one deploy of a registered project to the store's record of the board on USB (boards/).
It runs only `mpremote devs`, which never opens a port, and reads nothing from the board. The MAC is the first 12 hex
digits of the USB serial of a board on Espressif's own USB. Any other board is not recorded, and no kept board is read.
A serial that a firmware set and that starts with 12 hex digits passes as a MAC.

The entry holds the name, made_by (the registered tool), deployed (spark's clock, with its zone) and the verdict
"ready not read". Call it once for each deploy.

With --json it prints one envelope: data.entry, data.mac and data.device (docs/guide/agents/bench.md).

If no board is on USB, or the named port is not, and firmware/ of --project calls deepsleep, the fix says that the
board can be in deep sleep, as look.py's fix does (P1049). --json's `next` holds the look step, which needs the
person (P1048).

Exit codes: 0 recorded; 2 nothing was written: the name is not registered, no board or two boards are on USB, the
port is not listed, the board's serial holds no MAC, mpremote or the store failed, or an argument is wrong. Never 1."""
NOTES = {"show": SHOW_NOTES, "register": REGISTER_NOTES, "record": RECORD_NOTES}


def verb_of(argv):
    """The verb word `argv` asks for: its first word when it is a verb in VERBS, else DEFAULT_VERB."""
    return argv[0] if argv and argv[0] in VERBS else DEFAULT_VERB


def operation_for(argv):
    """(the Operation class `argv` asks for, argv without its verb word): the first word when it is a verb in VERBS, else
    `show` with argv as it is, so a word that is no verb fails in argparse."""
    verb = verb_of(argv)
    return VERBS[verb], argv[1:] if argv[:1] == [verb] else argv


def main(argv=None, outside=None):
    """Run the verb `argv` names and print its lines, or with --json its envelope. `outside` is the OutsideWorld a test
    gives. Returns the exit code."""
    argv = sys.argv[1:] if argv is None else list(argv)
    verb = verb_of(argv)
    operation, argv = operation_for(argv)
    return run_cli(HelpText("bench.py " + verb, None, NOTES[verb] + "\n\n" + VERBS_LINE, tool="bench"), operation(), argv,
                   outside_builder=build_project_outside_world, outside=outside)


if __name__ == "__main__":
    sys.exit(main())
