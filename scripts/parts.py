#!/usr/bin/env python3
"""
What a part asks of the board it plugs into, and what is actually known about it.

    parts.py --list
    parts.py --show l9110s-module
    parts.py --validate
    parts.py --unverified <part> [part ...]   what nobody has checked yet about those parts

A part library is easy to get wrong in a way that is worse than not having one. The temptation is a schema covering
everything a part might have — and since a motor driver's facts (input thresholds, current) have nothing in common with
a rangefinder's (an I2C address, a calibration), that schema degenerates into `{"name": ..., "notes": ...}`: a directory
of documentation pretending to be configuration.

So this splits them.

**`needs` is a real schema**, because it IS uniform: every part asks its host for some pins, and each pin either needs a
capability or does not. That is exactly what `assign_pins.py` consumes, and it is the reason this file exists rather
than a folder of markdown.

**`facts` is deliberately open**, and every entry carries three things: a value, where it came from, and whether anyone
has actually checked. A fact with `verified: false` is not a defect — most parts arrive with several — but it must be
VISIBLE, because the unverified ones are what decide whether a design works. On the project this came from, the single
most consequential number in the whole build was an audio module's idle current, which nobody had measured and every
document quietly assumed.

This file is the CLI (W6-S3b, P721; P726 PR 3): the ordered registry of the thirty Operations `parts.py` offers, the route
from a flag to its Operation (exact flag, else a unique prefix, as argparse picks a long option), the one flag shape the CLI
owns (`--needs-drop PROJECT NEED` runs the idea area's `DropNeed`) and `main`, which hands the argv to `run_cli`. Every
operation is an Operation on the core: the design area's (`design_operations.OPERATIONS`), the sourcing area's
(`sourcing_operations.OPERATIONS`) and `--describe`, the core's `DescribeOperations` over this registry. A flag that names a
JSON file (`--drawer-set FILE`, `--fact-set PART FILE`) is read by the core's CLI adapter and handed to the Operation as a
value (`Argument.payload`): reading stdin is the interface's job (P721 row 6).
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from spark.core.outcomes import EXIT_OK as EXIT_OK, EXIT_PROBLEMS as EXIT_INVALID, EXIT_COULD_NOT_RUN as EXIT_COULD_NOT_RUN, EXIT_FOR  # noqa: E402, F401
from spark.core.cli import HelpText, run_cli, run_operation  # noqa: E402
from spark.core.describe_operations import OPERATION_LINE, DescribeOperations, effect_words_of, options_of, summary_of  # noqa: E402
from spark.core.operation import COMMON_ARGUMENTS, JSON_DEST, READS, WRITES, Argument  # noqa: E402
from spark.core.events import Reporter  # noqa: E402
from spark.core.outside import build_bare_outside_world  # noqa: E402
from spark.records.answer_operation import ANSWER_ARGUMENTS, AnswerOperation  # noqa: E402
from spark.records.record_kind import Answer  # noqa: E402
from spark.sourcing import sourcing_operations  # noqa: E402
from spark.design import design_operations  # noqa: E402
from spark.idea.drop_need import DropNeed  # noqa: E402


# --- MVP ---
class DropNeedFlag(AnswerOperation):
    """
    Operation: the CLI's flag shape of the idea area's `DropNeed` (an Adapter at the edge, P726 PR 3): `--needs-drop PROJECT
    NEED` runs `DropNeed` with `--project PROJECT --need NEED` through `run_operation` and answers as every parts.py
    Operation does (`Answer.from_result`), as the handler did since P514.
    """

    name = "needs-drop"
    data_keys = ('project', 'need', 'dropped', 'released', 'written')
    arguments = (Argument(("--needs-drop",), "project_and_need", str,
                          "drop a need and its pick from .spark/needs.json and release only the holds of the dropped pick (every other hold stays); --dry-run "
                          "says what it would do; history stays, and requirements.json is not changed: a note says when it still lists the part",
                          nargs=2, metavar=("PROJECT", "NEED")),
                 ANSWER_ARGUMENTS["dry_run"], COMMON_ARGUMENTS[JSON_DEST])
    effects = (READS, WRITES)

    def effects_of(self, values):
        return (READS,) if values["dry_run"] else self.effects

    def build_answer(self, project_and_need, dry_run):
        target, need = project_and_need
        result = run_operation(DropNeed(), {"project": Path(target), "need": need, "dry_run": dry_run},
                               build_outside=lambda effects: build_bare_outside_world(None, effects, Reporter()))
        return Answer.from_result(result)


#: The order `--describe` lists the operations in: the order of the old table, so the page and the golden read as before.
ORDER = ("list", "show", "validate", "signals", "unverified", "need", "skeleton", "sources", "fetch", "keep", "read", "kept", "promote",
         "catalog", "drawer", "drawer-set", "drawer-import", "function-set", "fact-set", "audit", "needs", "needs-set", "match", "offer",
         "pick", "needs-drop", "requirements", "step", "tally", "describe")
#: Every Operation parts.py offers, by the `op` it prints, in `ORDER`: the ONE registry the route and `--describe` read, so
#: what an agent reads about an operation cannot drift from what runs (§6.4.3). `list-boards` is boards.py's and stays out.
OPERATIONS = {name: {**design_operations.OPERATIONS, **sourcing_operations.OPERATIONS, DropNeedFlag.name: DropNeedFlag,
                     DescribeOperations.name: DescribeOperations}[name] for name in ORDER}
#: The flags, for the prefix rule.
FLAGS = ["--" + name for name in OPERATIONS]
#: What parts.py says of itself, and the fix of an argv that names no operation.
HELP = HelpText("parts.py", "What a part needs, and what is known about it.", "", tool="parts",
                bad_argument_fix="parts.py --describe --json lists every operation and its arguments")


def asked_on_the_core(argv):
    """The Operation `argv` asks for, picked as argparse picks a long option (P726): an item (its text before `=`) that equals
    a flag, else one longer than `--` that is a prefix of exactly one flag (`--need` is a prefix of `--needs`, so the exact
    match comes first; `--ne` fits several and goes to the describe parser, which refuses it as an unrecognized argument).
    None when `argv` names no operation."""
    for item in argv:
        flag = item.split("=", 1)[0]
        if flag in FLAGS:
            return OPERATIONS[flag[2:]]
        fitting = [known for known in FLAGS if known.startswith(flag)] if len(flag) > len("--") else []
        if len(fitting) == 1:
            return OPERATIONS[fitting[0][2:]]
    return None


def catalog_epilog():
    """The text under `parts.py --help`: every operation with its summary and effects, and the options the operations share,
    so a reader of the describe route sees what the Operations offer (each Operation's own `--help` lists its arguments)."""
    lines = ["operations (each takes --help):"]
    lines += [OPERATION_LINE % ("--" + op, summary_of(cls), "  [%s]" % ", ".join(effect_words_of(cls)) if effect_words_of(cls) else "")
              for op, cls in OPERATIONS.items()]
    return "\n".join(lines + ["", "options, by the operations that take them:"] + [OPERATION_LINE % (flag, help, "") for flag, help in options_of(OPERATIONS).items()])


def on_the_core(argv):
    """The exit code of the Operation `argv` asks for, run through `run_cli` with parts.py's `tool`; an argv that names no
    operation goes to `--describe`: an unknown flag is its `bad_argument` with the describe fix, and no argument at all
    lists the operations (P707, P726)."""
    operation = asked_on_the_core(argv)
    if operation in (None, DescribeOperations):
        return run_cli(HELP._replace(epilog=catalog_epilog()), DescribeOperations(OPERATIONS), argv, outside_builder=build_bare_outside_world)
    return run_cli(HELP, operation(), argv, outside_builder=build_bare_outside_world)


def main(argv=None):
    return on_the_core(sys.argv[1:] if argv is None else list(argv))
# --- end MVP ---


if __name__ == "__main__":
    sys.exit(main())
