"""
The frontends of the core (P442, W3-3). `run_operation` runs one Operation for any frontend and turns a SparkError or a
crash into a result. `run_cli` is the CLI frontend: it parses, runs, renders with one of the two Renderers and prints. A
script's `main` calls `run_cli` and nothing else, so an agent or an MCP tool can call the core without it.
"""

import argparse
import json
from pathlib import Path
import sys
import traceback
from collections import namedtuple

from spark.core import codes, outcomes
from spark.core.clock import SystemClock
from spark.core.errors import CodedMessageError, SparkError
from spark.core.events import TerminalReporter
from spark.core.operation import JSON_DEST, JSON_FLAG
from spark.core.privacy import MaskingReporter, Privacy
from spark.core.result import Finding, OperationResult
from spark.core.text_guards import guard_lines, printable

# --- MVP ---
#: Value: what a CLI says of itself in `--help`: its file name, one sentence, and the text after the arguments. `tool` is
#: the envelope's `tool`, the script that answered (P707): a CLI with several Operations gives its own name (`parts`), and
#: None means the Operation's name, as the one-Operation CLIs print it. `bad_argument_fix` is the fix sentence of a bad
#: argument when the CLI has a better one than `BAD_ARGUMENT_FIX` (parts.py's describe route, P726 PR 3); None takes the default.
HelpText = namedtuple("HelpText", "prog description epilog tool bad_argument_fix", defaults=(None, None))
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
#: The run of a CLI: the Privacy step (pass-through unless the Operation has a `privacy_for`) and no trace.
DEFAULT_RUN = RunOptions(Privacy(), None, SystemClock())


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
            target.add_argument(*argument.flags, dest=argument.dest, action="store_true", help=argument.help, required=argument.required)
        else:
            counted = {key: value for key, value in (("nargs", argument.nargs), ("metavar", argument.metavar)) if value is not None}
            counted.update({"action": "append"} if argument.repeats else {})
            target.add_argument(*argument.flags, dest=argument.dest, type=argument.kind, default=argument.default, help=argument.help,
                                required=argument.required, choices=argument.choices, **counted)
    return parser


def load_payloads(operation, values, stdin):
    """
    The parsed `values` with each payload token replaced by the JSON it names (P726 PR 3): for an Argument with `payload`,
    the file at that token, or `stdin` for `-`, read and parsed; a one-value flag (`nargs` None) holds the token itself, a
    counted flag holds a list and the token sits at the index. A None (the flag not given) stays. The frontend reads, the
    Operation takes a value: reading stdin is the interface's job (P721 row 6). A file that cannot be read or is not JSON
    raises `CodedMessageError` with `codes.INPUT_UNREADABLE`.
    """
    for argument in operation.arguments:
        if argument.payload is None or values.get(argument.dest) is None or values[argument.dest] is argument.default:
            continue  # the flag was not given (None, or the Argument's own default object)
        token = values[argument.dest] if argument.nargs is None else values[argument.dest][argument.payload]
        try:
            loaded = json.loads(stdin.read() if token == "-" else Path(token).read_text())
        except (OSError, ValueError) as broken:
            raise CodedMessageError("%s is not readable JSON: %s", "stdin" if token == "-" else token, broken, code=codes.INPUT_UNREADABLE) from None
        if argument.nargs is None:
            values[argument.dest] = loaded
        else:
            values[argument.dest][argument.payload] = loaded
    return values


def _privacy_and_reporter(operation, values, as_json):
    """The run's Privacy and Reporter: the Operation's `privacy_for(project)` masks the result and each Event (P677), else
    the default passes everything through; the reporter prints events on stdout, on stderr with --json (P507)."""
    privacy, reporter = DEFAULT_RUN.privacy, TerminalReporter.for_json(as_json)
    if operation.privacy_for:
        privacy = operation.privacy_for(values.get("project"))
        reporter = MaskingReporter(reporter, privacy)
    return privacy, reporter


def _unreadable_payload(prog, unreadable):
    """The result of a payload the frontend could not read (P726 PR 3): one could-not-run Finding with the error's code and
    the sentence as a diagnostics line (`<prog>: <sentence>`), never the usage: a broken file is not a wrong flag."""
    return OperationResult(findings=[Finding(outcomes.COULD_NOT_RUN, None, unreadable.code, str(unreadable), None)],
                           diagnostics=["%s: %s" % (prog, unreadable)])


def run_cli(text, operation, argv=None, *, outside_builder, outside=None):
    """
    The exit code of `operation` run as a CLI. It parses `argv` (sys.argv without the script when None) from the
    Operation's arguments and answers a bad flag with the Renderer's `render_bad_argument` under --json (an envelope with
    `bad_argument`, or None for a flat Operation: then the usage), the usage on stderr without (P433). The envelope's `tool`
    is `text.tool`, or the Operation's name when the CLI gave none (P707). It builds the
    outside with `outside_builder(project, effects, reporter, values)`, the effects those of `operation.effects_of(values)`
    and `values` the parsed arguments plus `json`, from which a frontend picks what the Operation never builds itself (the
    ReplyStrategy of `--replies`, and no terminal under --json, P737), unless a test gave `outside`, the reporter `TerminalReporter.for_json(as_json)`
    (P507: the events on stdout, on stderr with --json), runs,
    prints the rendering on stdout as it is (--json keeps every value raw, and the report's lines guard themselves) and
    the diagnostics on stderr through `guard_lines`, and returns the exit code of the result's status. The one place in
    the core that prints (rule X2). The Operation's `privacy_for(project)` gives the run's Privacy (P677), which masks
    the result and, through a MaskingReporter, each Event; None passes everything through.
    """
    parser, renderer, tool = parser_for(text, operation), operation.json_renderer, text.tool or operation.name
    argv = sys.argv[1:] if argv is None else list(argv)
    try:
        values = vars(parser.parse_args(argv))
    except outcomes.BadArgumentError as bad:
        refused = OperationResult(findings=[Finding(outcomes.COULD_NOT_RUN, None, codes.BAD_ARGUMENT, str(bad), text.bad_argument_fix or BAD_ARGUMENT_FIX % text.prog)])
        line = renderer.render_bad_argument(refused, tool, operation.name) if JSON_FLAG in argv else None
        if line is None:
            parser.exit_with_usage(guard_lines(str(bad) + (" — " + text.bad_argument_fix if text.bad_argument_fix else "")))
        print(line)
        return outcomes.EXIT_COULD_NOT_RUN
    as_json = values.pop(JSON_DEST, False)
    privacy, reporter = _privacy_and_reporter(operation, values, as_json)
    try:
        values = load_payloads(operation, values, sys.stdin)
        result = run_operation(operation, values, outside, lambda effects: outside_builder(values.get("project"), effects, reporter, dict(values, **{JSON_DEST: as_json})),
                               DEFAULT_RUN._replace(privacy=privacy))
    except CodedMessageError as unreadable:
        result = _unreadable_payload(text.prog, unreadable)
    said = renderer.render(result, tool, operation.name) if as_json else TextReport.render(result)
    if said:
        print(said)
    if result.diagnostics:
        print(guard_lines("\n".join(result.diagnostics)), file=sys.stderr)
    return outcomes.EXIT_FOR[result.status()]
# --- end MVP ---
