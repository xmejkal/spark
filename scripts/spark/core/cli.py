"""
The frontends of the core (P442, W3-3). `run_operation` runs one Operation for any frontend and turns a SparkError or a
crash into a result. `run_cli` is the CLI frontend: it parses, runs, renders with one of the two Renderers and prints. A
script's `main` calls `run_cli` and nothing else, so an agent or an MCP tool can call the core without it.
"""

import argparse
import sys
import traceback
from collections import namedtuple

from spark.core import codes, outcomes
from spark.core.errors import SparkError
from spark.core.operation import JSON_DEST, JSON_FLAG
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import guard_lines

# --- MVP ---
#: Value: what a CLI says of itself in `--help`: its file name, one sentence, and the text after the arguments.
HelpText = namedtuple("HelpText", "prog description epilog")
#: The sentence of a crash's Finding holds the class only, because the message can carry a home path.
CRASH_MESSAGE = "%s: the traceback is on stderr"
CRASH_FIX = "report this to the spark maintainers with the stderr traceback"
#: The first diagnostics line of a crash: the op and the class, before the traceback.
CRASHED_MESSAGE = "%s: crashed, %s"
BAD_ARGUMENT_FIX = "%s --help lists the arguments"


class JsonEnvelope:
    """Renderer: an OperationResult as the one envelope line a CLI prints with --json. It decides nothing again."""

    @staticmethod
    def render(result, tool, op):
        return outcomes.dumps(result.to_envelope(tool, op))


class TextReport:
    """Renderer: an OperationResult's lines as a person reads them, as one text. It decides nothing again."""

    @staticmethod
    def render(result):
        return "\n".join(result.lines)


def run_operation(operation, values, outside):
    """The OperationResult of `operation.run(**values, outside=outside)`. A SparkError is one Finding of its status. Any
    other exception is a crash: one unchecked Finding with code `crash` and the class in its sentence, and the traceback
    in `diagnostics`, never in the envelope (an exception's message can carry a home path)."""
    try:
        return operation.run(**values, outside=outside)
    except SparkError as refused:
        return OperationResult(findings=[Finding(refused.status, None, refused.code, str(refused), refused.fix)])
    except Exception as crashed:  # noqa: BLE001  the core's one catch-all: a crash is answered as could-not-run, never hidden
        name = type(crashed).__name__
        return OperationResult(findings=[Finding(outcomes.COULD_NOT_RUN, None, codes.CRASH, CRASH_MESSAGE % name, CRASH_FIX)],
                               diagnostics=[CRASHED_MESSAGE % (operation.name, name)] + traceback.format_exc().rstrip("\n").split("\n"))


def parser_for(text, operation):
    """The AnsweringParser of a CLI: each Argument as argparse takes it, and a `group` as one mutually exclusive group."""
    parser = outcomes.AnsweringParser(prog=text.prog, description=text.description, epilog=text.epilog,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    groups = {}
    for argument in operation.arguments:
        if argument.group and argument.group not in groups:
            groups[argument.group] = parser.add_mutually_exclusive_group()
        target = groups[argument.group] if argument.group else parser
        if argument.kind is bool:
            target.add_argument(*argument.flags, dest=argument.dest, action="store_true", help=argument.help)
        else:
            target.add_argument(*argument.flags, dest=argument.dest, type=argument.kind, default=argument.default, help=argument.help)
    return parser


def run_cli(text, operation, argv=None, *, outside_builder, outside=None):
    """
    The exit code of `operation` run as a CLI. It parses `argv` (sys.argv without the script when None) from the
    Operation's arguments and answers a bad flag with a `bad_argument` envelope under --json, or the usage on stderr
    without (P433). It builds the outside with `outside_builder(project, effects)` unless a test gave `outside`, runs,
    prints the rendering on stdout as it is (--json keeps every value raw, and the report's lines guard themselves) and
    the diagnostics on stderr through `guard_lines`, and returns the exit code of the result's status. The one place in
    the core that prints (rule X2).
    """
    parser = parser_for(text, operation)
    argv = sys.argv[1:] if argv is None else list(argv)
    try:
        values = vars(parser.parse_args(argv))
    except outcomes.BadArgument as bad:
        if JSON_FLAG not in argv:
            parser.exit_with_usage(guard_lines(str(bad)))
        refused = OperationResult(findings=[Finding(outcomes.COULD_NOT_RUN, None, codes.BAD_ARGUMENT, str(bad), BAD_ARGUMENT_FIX % text.prog)])
        print(JsonEnvelope.render(refused, operation.name, operation.name))
        return outcomes.EXIT_COULD_NOT_RUN
    as_json = values.pop(JSON_DEST)
    result = run_operation(operation, values, outside or outside_builder(values.get("project"), operation.effects))
    said = JsonEnvelope.render(result, operation.name, operation.name) if as_json else TextReport.render(result)
    if said:
        print(said)
    if result.diagnostics:
        print(guard_lines("\n".join(result.diagnostics)), file=sys.stderr)
    return outcomes.EXIT_FOR[result.status()]
# --- end MVP ---
