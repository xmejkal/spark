"""
The outside an Operation reaches (P442, W3-3). `OutsideWorld` holds it as callables, so a test gives a Fake, a frontend
gives the real one, and no Operation imports subprocess or the tools list itself. Only what `look` uses is here; the other
fields (`write`, `fetch`, `environ`, `clock`, `consent`) enter with their first Operation.
"""

import subprocess
from collections import namedtuple

from spark.core.codes import UNDECLARED_EFFECT
from spark.core.errors import SparkError
from spark.core.operation import RUNS

# --- MVP ---
#: Value: `run` runs a program as `subprocess.run` does, and `find_tool` gives the `tools.Tool` for a role or a tool's
#: name, or raises `tools.ToolProblem`. Each is the real thing, a Fake or a refusing stub, as `build_outside_world` chose.
OutsideWorld = namedtuple("OutsideWorld", "run find_tool")


class ProgramRunner:
    """Adapter: `run` runs a program on this machine, as `subprocess.run` does; the one place in the core that may (rule T1)."""

    run = staticmethod(subprocess.run)


def refuse_run(command, **options):
    """The `run` of an Operation whose effects hold no RUNS: a SparkError with code `undeclared_effect`, and no program runs."""
    raise SparkError("the operation declares no `%s` effect, so it cannot run %r", RUNS, command, code=UNDECLARED_EFFECT,
                     fix="a defect in spark: report it, with the command")


def build_outside_world(effects, find_tool=None):
    """The OutsideWorld for these effects: `run` is the real one with RUNS and `refuse_run` without; `find_tool` the given one."""
    return OutsideWorld(ProgramRunner.run if RUNS in effects else refuse_run, find_tool)
# --- end MVP ---
