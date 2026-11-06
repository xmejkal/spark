"""
The frontends of the core (P442, W3-3). `run_operation` runs one Operation for any frontend and turns a SparkError or a
crash into a result. `run_cli` is the CLI frontend: it parses, runs, renders with one of the two Renderers and prints. A
script's `main` calls `run_cli` and nothing else, so an agent or an MCP tool can call the core without it.
"""

import argparse
import json
import sys
import traceback
from collections import namedtuple

from spark.core import codes, outcomes
from spark.core.clock import SystemClock
from spark.core.errors import SparkError
from spark.core.events import TerminalReporter
from spark.core.operation import JSON_DEST, JSON_FLAG
from spark.core.privacy import Privacy
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import guard_lines, printable

# --- MVP ---
#: Value: what a CLI says of itself in `--help`: its file name, one sentence, and the text after the arguments.
HelpText = namedtuple("HelpText", "prog description epilog")
#: The sentence of a crash's Finding holds the class only, because the message can carry a home path.
CRASH_MESSAGE = "%s: the traceback is on stderr"
CRASH_FIX = "report this to the spark maintainers with the stderr traceback"
#: The first diagnostics line of a crash: the op and the class, then the fix, then the traceback under Python's heading.
CRASHED_MESSAGE = "%s: crashed, %s"
#: How Python starts a frame's chunk of a traceback; the other chunks are one sentence each.
FRAME_START = '  File "'
BAD_ARGUMENT_FIX = "%s --help lists the arguments"
#: The diagnostics line of a trace that raised: the class only, as a crash's sentence.
TRACE_FAILED_MESSAGE = "trace: %s raised, the result stands"
#: Value: how one run is done (P605, a parameter object). `privacy` masks the result and the values, `trace` is called
#: once per run with the name, the masked values, the masked result and the seconds, or None, and `clock` times the run.
RunOptions = namedtuple("RunOptions", "privacy trace clock")
#: The run of a CLI: the Privacy step and no trace.
DEFAULT_RUN = RunOptions(Privacy(), None, SystemClock())


class JsonEnvelope:
    """Renderer: an OperationResult as the one envelope line a CLI prints with --json. It decides nothing again."""

    @staticmethod
    def render(result, tool, op):
        return outcomes.dumps(result.to_envelope(tool, op))

    @staticmethod
    def render_bad_argument(result, tool, op):
        """The line a bad argument gets under --json: the envelope. A Renderer that has none returns None (FlatJsonLine)."""
        return JsonEnvelope.render(result, tool, op)


class FlatJsonLine:
    """Renderer: an OperationResult as the one flat line of JSON the bench scripts print with --json (P657): its `data` as
    `json.dumps` writes it, with no envelope, and an empty text when `data` is None, so nothing is printed. A bad argument
    gets no line of its own: the usage on stderr, as argparse prints it."""

    @staticmethod
    def render(result, tool, op):
        return "" if result.data is None else json.dumps(result.data)

    @staticmethod
    def render_bad_argument(result, tool, op):
        return None


class TextReport:
    """Renderer: an OperationResult's lines as a person reads them, as one text. It decides nothing again."""

    @staticmethod
    def render(result):
        return "\n".join(result.lines)


def run_operation(operation, values, outside=None, build_outside=None, options=DEFAULT_RUN):
    """The OperationResult of `operation.run(**values, outside=outside)` (see `_guarded_result`), masked by `options.privacy`
    (P605). Then `options.trace`, when given, sees the run once: the name, the masked values, the masked result and the
    seconds of `options.clock`. A trace that raises adds one diagnostics line, and the result stands."""
    started = options.clock.monotonic()
    result = _guarded_result(operation, values, outside, build_outside)
    seconds = options.clock.monotonic() - started
    masked = options.privacy.mask_result(result)
    if options.trace is None:
        return masked
    try:
        options.trace(operation.name, options.privacy.mask_values(values), masked, seconds)
    except Exception as failed:  # noqa: BLE001  a tracer never changes the answer
        return masked._replace(diagnostics=list(masked.diagnostics) + [TRACE_FAILED_MESSAGE % printable(type(failed).__name__)])
    return masked


def _guarded_result(operation, values, outside, build_outside):
    """The OperationResult of `operation.run(**values, outside=outside)`, `outside` built by
    `build_outside(operation.effects_of(values))` when None. A
    SparkError is one Finding of its status. Any other exception, the builder's too, is a crash: one unchecked Finding with
    code `crash` and the class in its sentence, and in `diagnostics` the op and the class, the fix, and the traceback,
    never in the envelope (an exception's message can carry a home path, so it goes to stderr, on one line)."""
    try:
        return operation.run(**values, outside=outside or build_outside(operation.effects_of(values)))
    except SparkError as refused:
        return OperationResult(findings=[Finding(refused.status, None, refused.code, str(refused), refused.fix)])
    except Exception as crashed:  # noqa: BLE001  the core's one catch-all: a crash is answered as could-not-run, never hidden
        name = printable(type(crashed).__name__)
        return OperationResult(findings=[Finding(outcomes.COULD_NOT_RUN, None, codes.CRASH, CRASH_MESSAGE % name, CRASH_FIX)],
                               diagnostics=[CRASHED_MESSAGE % (operation.name, name), CRASH_FIX] + traceback_lines(crashed))


def traceback_lines(crashed):
    """The traceback of `crashed` as lines, its causes and contexts too, as Python prints them: a frame's chunk line by
    line, every other chunk (the heading, a cause sentence, the exception's own line) as one line through `printable`,
    so a message with a newline cannot fake a line of what the person reads."""
    lines = []
    for chunk in traceback.TracebackException.from_exception(crashed).format():
        text = chunk.strip("\n")
        lines += [printable(line) for line in text.split("\n")] if text.startswith(FRAME_START) else [printable(text)]
    return lines


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
            target.add_argument(*argument.flags, dest=argument.dest, type=argument.kind, default=argument.default, help=argument.help,
                                required=argument.required, choices=argument.choices)
    return parser


def run_cli(text, operation, argv=None, *, outside_builder, outside=None):
    """
    The exit code of `operation` run as a CLI. It parses `argv` (sys.argv without the script when None) from the
    Operation's arguments and answers a bad flag with the Renderer's `render_bad_argument` under --json (an envelope with
    `bad_argument`, or None for a flat Operation: then the usage), the usage on stderr without (P433). It builds the outside with `outside_builder(project, effects, reporter)`, the effects those of
    `operation.effects_of(values)`, unless a test gave `outside`, the
    reporter `TerminalReporter.for_json(as_json)` (P507: the events on stdout, on stderr with --json), runs,
    prints the rendering on stdout as it is (--json keeps every value raw, and the report's lines guard themselves) and
    the diagnostics on stderr through `guard_lines`, and returns the exit code of the result's status. The one place in
    the core that prints (rule X2).
    """
    parser, renderer = parser_for(text, operation), operation.json_renderer or JsonEnvelope
    argv = sys.argv[1:] if argv is None else list(argv)
    try:
        values = vars(parser.parse_args(argv))
    except outcomes.BadArgument as bad:
        refused = OperationResult(findings=[Finding(outcomes.COULD_NOT_RUN, None, codes.BAD_ARGUMENT, str(bad), BAD_ARGUMENT_FIX % text.prog)])
        line = renderer.render_bad_argument(refused, operation.name, operation.name) if JSON_FLAG in argv else None
        if line is None:
            parser.exit_with_usage(guard_lines(str(bad)))
        print(line)
        return outcomes.EXIT_COULD_NOT_RUN
    as_json = values.pop(JSON_DEST, False)
    reporter = TerminalReporter.for_json(as_json)
    result = run_operation(operation, values, outside, lambda effects: outside_builder(values.get("project"), effects, reporter))
    said = renderer.render(result, operation.name, operation.name) if as_json else TextReport.render(result)
    if said:
        print(said)
    if result.diagnostics:
        print(guard_lines("\n".join(result.diagnostics)), file=sys.stderr)
    return outcomes.EXIT_FOR[result.status()]
# --- end MVP ---
