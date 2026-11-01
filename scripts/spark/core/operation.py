"""
The Operation (P442, W3-3): one job, with one public method, `run`. A CLI, an agent or an MCP tool calls it through
`spark.core.cli`, which parses its `arguments` and renders its result. The Operation itself parses and prints nothing.
"""

from collections import namedtuple
from pathlib import Path

# --- MVP ---
#: Value: one argument of an Operation, as argparse adds it. `flags` are its option strings, `dest` the keyword `run`
#: takes, `kind` the type of the value (`Path`, `str`) or `bool` for a flag that is on when given, `group` the name of
#: the group whose arguments exclude each other, or None.
Argument = namedtuple("Argument", "flags dest kind help default group", defaults=(None, None))

#: What an Operation does outside spark: it reads the project's files, runs a program, touches the board. A step's
#: `deletes` and `writes` (`outcomes.step`) enter with their first Operation.
READS, RUNS, BOARD = "reads", "runs", "board"
#: The flag that asks for the envelope. `run_cli` reads it, and the Operation never sees it.
JSON_FLAG, JSON_DEST = "--json", "json"
#: The arguments every Operation on a project takes, by `dest`, with the words of the first Operation, look.py. An
#: Operation that says one differently `_replace`s its `help`.
COMMON_ARGUMENTS = {
    "project": Argument(("--project",), "project", Path, "the project folder with requirements.json and sim/ (default: here)", Path(".")),
    "port": Argument(("--port",), "port", str, "the board's serial port, e.g. /dev/cu.usbmodem1101. Needed with two or more boards on USB "
                     "(one board on two nodes named by its serial counts once)"),
    JSON_DEST: Argument((JSON_FLAG,), JSON_DEST, bool, "print one envelope on stdout (docs/guide/agents/json.md)"),
}


class Operation:
    """
    Operation: one job, with one public method, `run`. A subclass gives `name` (the `op` the envelope prints), `arguments`
    (its Arguments, in the order the usage lists them) and `effects` (READS, RUNS, BOARD: what `build_outside_world` lets
    it reach). `run` takes each argument's `dest` as a keyword, except `json`, which is the frontend's, and `outside`, an
    OutsideWorld, and returns an OperationResult. It raises SparkError to answer with one Finding; anything else is a crash.
    """

    name = None
    arguments = ()
    effects = ()

    def run(self, *, outside, **values):
        raise NotImplementedError
# --- end MVP ---
