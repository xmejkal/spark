"""
The outside an Operation reaches (P442, W3-3). `OutsideWorld` holds it as callables, so a test gives a Fake, a frontend
gives the real one, and no Operation imports subprocess or the tools list itself, or prints (P507: it reports an Event).
`clock` and `make_consent` came with deploy (P655); the other fields (`write`, `fetch`, `environ`) enter with their first Operation.
"""

import subprocess
from collections import namedtuple

from spark.core.clock import SystemClock
from spark.core.codes import UNDECLARED_EFFECT
from spark.core.errors import SparkError
from spark.core.operation import ASKS, RUNS

# --- MVP ---
#: Value: `run` runs a program as `subprocess.run` does, and `find_tool` gives the `Tool` for a role or a tool's
#: name, or raises `ToolError`; `find_tool(name, project=None)` asks the shared tools lists without the project's;
#: `report(event)` gives an `events.Event` to the Reporter the frontend picked (P507), and is not an effect: every Operation has it.
#: `clock` has `now`, `monotonic` and `sleep` (`clock.SystemClock`). `make_consent(line)` gives the ConsentStrategy that asks
#: the person for the yes, given the line that runs the Operation again in the person's own terminal; it needs ASKS (P657).
#: `replies(question)` is a `replies.ReplyStrategy`'s `reply`: the Reply to a Question, or None for "not now" (P737); it needs
#: ASKS too, and its default refuses, so the two callers that build the tuple positionally stand.
#: Each is the real thing, a Fake or a refusing stub, as `build_outside_world` chose.
UNDECLARED_FIX = "a defect in spark: report it, with the command"


def refuse_replies(question):
    """The `replies` of an Operation whose effects hold no ASKS: a SparkError with code `undeclared_effect`, and nobody is asked."""
    raise SparkError("the operation declares no `%s` effect, so it cannot ask %r", ASKS, question.key, code=UNDECLARED_EFFECT, fix=UNDECLARED_FIX)


OutsideWorld = namedtuple("OutsideWorld", "run find_tool report clock make_consent replies", defaults=(refuse_replies,))


class ProgramRunner:
    """Adapter: `run` runs a program on this machine, as `subprocess.run` does; the one place in the core that may (rule T1).
    `echo_fd` is the file descriptor a child's stdout goes to when the caller neither captures it nor gives `stdout` (E2:
    fd 2 under `--json`, so the flash tool's own output stays out of the envelope), or None: as it is."""

    def __init__(self, echo_fd=None):
        self.echo_fd = echo_fd

    def run(self, command, **options):
        if self.echo_fd is not None and "stdout" not in options and not options.get("capture_output"):
            options["stdout"] = self.echo_fd
        return subprocess.run(command, **options)


def refuse_run(command, **options):
    """The `run` of an Operation whose effects hold no RUNS: a SparkError with code `undeclared_effect`, and no program runs."""
    raise SparkError("the operation declares no `%s` effect, so it cannot run %r", RUNS, command, code=UNDECLARED_EFFECT, fix=UNDECLARED_FIX)


def refuse_consent(line):
    """The `make_consent` of an Operation whose effects hold no ASKS: a SparkError with code `undeclared_effect`, and nobody is asked."""
    raise SparkError("the operation declares no `%s` effect, so it cannot ask the person for a yes", ASKS, code=UNDECLARED_EFFECT, fix=UNDECLARED_FIX)


def build_outside_world(effects, reporter, find_tool=None, make_consent=None, replies=None):
    """The OutsideWorld for these effects: `run` is a ProgramRunner's, echoing where the Reporter says, with RUNS and `refuse_run`
    without; `make_consent` the given one with ASKS and `refuse_consent` without; `replies` the given ReplyStrategy's `reply`
    with ASKS and `refuse_replies` without; `find_tool` the given one; `report` the given Reporter's; `clock` the computer's
    (a test `_replace`s it with a FakeClock, P737 took the parameter out: rule R3)."""
    return OutsideWorld(ProgramRunner(reporter.echo_fd()).run if RUNS in effects else refuse_run, find_tool, reporter.report,
                        SystemClock(), make_consent if ASKS in effects and make_consent else refuse_consent,
                        replies=replies.reply if ASKS in effects and replies else refuse_replies)
# --- end MVP ---
