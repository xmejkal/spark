"""
The Renderers of an OperationResult (P657): `JsonEnvelope`, the default of `Operation.json_renderer`, `FlatJsonLine`,
which the bench scripts keep, `FixFlatJsonLine`, which adds `fix` for grant, live and reach (P1055), `JsonDocument`,
FlatJsonLine's indented sibling, which check_all keeps (P804), and `FullEnvelope`, parts.py's envelope with every key
(P707), each a `--json` line; and `TextReport`, the text view a person reads (P1032): a result with a headline as a
status line, the facts, the findings with their fix, a Note and the next step, painted plain or, through rich when it
imports, in colour, and `StatusLine`, the status line alone (P478).
"""

import io
import json
import shlex
import types
from pathlib import Path

from spark.core import outcomes
from spark.core.result import MARK_OK, MARK_STOP, MARK_UNCHECKED, MARK_WARNING, step_dicts
from spark.core.text_guards import printable
from spark.core.text_style import PLAIN


class JsonEnvelope:
    """Renderer: an OperationResult as the one envelope line a CLI prints with --json. It decides nothing again."""

    @staticmethod
    def render(result, tool, op):
        return outcomes.dumps(result.to_envelope(tool, op))

    @staticmethod
    def render_bad_argument(result, tool, op):
        """The line a bad argument gets under --json: the envelope. A Renderer that has none returns None (FlatJsonLine)."""
        return JsonEnvelope.render(result, tool, op)


class FullEnvelope:
    """Renderer: `JsonEnvelope`'s line with `notes` and `assumptions` as `[]` when the result has none, on a bad argument
    too (P707). parts.py's contract (P124): an agent reads the same eleven keys from every answer, a refusal or a crash
    included, which `run_cli` builds without notes."""

    @staticmethod
    def render(result, tool, op):
        said = result.to_envelope(tool, op)
        return outcomes.dumps(dict(said, **{key: [] for key in ("notes", "assumptions") if key not in said}))

    @staticmethod
    def render_bad_argument(result, tool, op):
        return FullEnvelope.render(result, tool, op)


class FlatJsonLine:
    """Renderer: an OperationResult as the one flat line of JSON the bench scripts print with --json (P657): its `data` as
    `json.dumps` writes it, with no envelope, and an empty text when `data` is None, so nothing is printed. A bad argument
    gets no line of its own: the usage on stderr, as argparse prints it. When the result names a step, `next` comes last
    (P1035), after a `next` that `data` holds already; a `data` that is no dict is printed as it is."""

    @staticmethod
    def render(result, tool, op):
        return "" if result.data is None else json.dumps(FlatJsonLine.with_next(result))

    @staticmethod
    def with_next(result):
        """`result.data` with the result's steps as its last key, `next`, after the steps `data` holds there already."""
        if not result.next or not isinstance(result.data, dict):
            return result.data
        data = dict(result.data)
        return dict(data, next=list(data.pop("next", [])) + step_dicts(result.next))

    @staticmethod
    def render_bad_argument(result, tool, op):
        return None


class FixFlatJsonLine(FlatJsonLine):
    """Renderer: FlatJsonLine with `fix`, the result's `first_fix()`, after `data`'s keys and before `next` (P1055).
    grant.py --check, live.py and reach.py print it. A `data` that is no dict is printed as FlatJsonLine prints it."""

    @staticmethod
    def render(result, tool, op):
        if not isinstance(result.data, dict):
            return FlatJsonLine.render(result, tool, op)
        return FlatJsonLine.render(result._replace(data=dict(result.data, fix=result.first_fix())), tool, op)


class JsonDocument(FlatJsonLine):
    """Renderer: FlatJsonLine's indented sibling (P804): an OperationResult's `data` as one JSON document over several
    lines, as `json.dumps(data, indent=2)` writes it, which check_all prints with --json. An empty text when `data` is
    None, so nothing is printed, and a bad argument gets the usage, as FlatJsonLine's."""

    @staticmethod
    def render(result, tool, op):
        return "" if result.data is None else json.dumps(result.data, indent=2)


# --- MVP ---
#: The scripts folder: a step's op runs `<SCRIPTS>/<script_of(op)>`.
SCRIPTS = Path(__file__).resolve().parents[2]
#: The script of each step op that is not `<op>.py` (P1081 #1585, P1078). Which script runs an op is the CLI frontend's
#: fact, which the Operation catalogue does not hold (P1077): `step_command` reads it through `script_of`, and the build's
#: and the follow-up's `next:` lines are `step_command`'s (P1256).
OP_SCRIPTS = {"pick": "parts.py", "requirements": "parts.py", "needs-drop": "parts.py", "move-hold": "parts.py",
              "build-board": "check_spine.py", "research-part": "research.py", "run-scenario": "run_scenario.py"}
#: The symbol of each mark on the status line, when the stream can encode it.
MARK_SYMBOLS = {MARK_OK: "✓", MARK_STOP: "✗", MARK_WARNING: "!", MARK_UNCHECKED: "?"}
#: The ASCII word of each mark, for a stream whose encoding cannot encode the symbols (D8).
MARK_WORDS = {MARK_OK: "OK", MARK_STOP: "STOP", MARK_WARNING: "WARN", MARK_UNCHECKED: "?"}
#: The rich style of each role of a span (D6): the mark's colour, bold headings and command, dim fixes and Note, and the
#: spinner's cyan frame (P478).
STYLES = {"mark-" + MARK_OK: "bold green", "mark-" + MARK_STOP: "bold red", "mark-" + MARK_WARNING: "bold yellow",
          "mark-" + MARK_UNCHECKED: "bold magenta", "status": "bold", "heading": "bold", "quiet": "dim", "command": "bold",
          "fact": None, "spinner": "cyan"}
#: The section headings of the findings, in their order, by severity.
SECTIONS = ((outcomes.PROBLEMS, "Problems"), (outcomes.COULD_NOT_RUN, "Not checked"))
#: The Next section's line when there is no step: it points to the first item that says why.
NO_COMMAND_MESSAGE = "No command: the first item under %s above says why."
#: The Next heading's words for a step that needs the person, and for one that needs their yes.
YOU_MESSAGE, YES_MESSAGE = " you, in your own terminal.", " %s.py asks for your yes."


def script_of(op):
    """The file name of the script in SCRIPTS that runs a step whose op is `op`: its OP_SCRIPTS entry, else `<op>.py`."""
    return OP_SCRIPTS.get(op, "%s.py" % op)


def step_command(step):
    """The one line a person runs for `step`: `NAME=value` for each variable of its env, then its script and argv, all
    shell-quoted and through `printable`, so a newline in an argument shows as `?` and never breaks the line."""
    names = ["%s=%s" % (name, shlex.quote(str(value))) for name, value in sorted((step.env or {}).items())]
    return printable(" ".join(names + [shlex.join([str(SCRIPTS / script_of(step.op))] + [str(each) for each in step.argv])]))


def import_rich():
    """rich's Console and Text, imported only here, so a pipe and Claude's shell never import rich (D4)."""
    from rich.console import Console
    from rich.text import Text
    return types.SimpleNamespace(Console=Console, Text=Text)


class PlainPainter:
    """Strategy: the layout's lines as plain text, the spans' texts joined."""

    @staticmethod
    def paint(lines):
        return "\n".join("".join(text for text, _ in line) for line in lines)


class RichPainter:
    """Strategy: the layout's lines in colour, through rich: one Text per line, built from spans and never from markup,
    printed with SGR codes and no wrap, so the plain text is this text with its codes removed."""

    def __init__(self, rich):
        self.rich = rich

    def paint(self, lines):
        console = self.rich.Console(file=io.StringIO(), force_terminal=True, color_system="standard", soft_wrap=True,
                                    highlight=False, emoji=False, markup=False)
        for line in lines:
            text = self.rich.Text()
            for part, role in line:
                text.append(part, STYLES[role])
            console.print(text)
        return console.file.getvalue().removesuffix("\n")


def painter_for(style, importer):
    """PlainPainter when `style` has no colour, and then `importer` is never called; else a RichPainter over what
    `importer()` gives, or PlainPainter when it raises (rich is not installed, or broken)."""
    if not style.colour:
        return PlainPainter
    try:
        return RichPainter(importer())
    except Exception:  # noqa: BLE001  an optional package never stops the text view
        return PlainPainter


def paint_or_plain(painter, lines):
    """The text of `lines` (each a list of (text, role) spans) as `painter` paints it, or the plain text when the paint
    raises: rich of another version may refuse a setting, and the plain text stands (P478: the one fallback)."""
    try:
        return painter.paint(lines)
    except Exception:  # noqa: BLE001  a paint that raises never stops the text view
        return PlainPainter.paint(lines)


class TextReport:
    """Renderer: an OperationResult as a person reads it, as one text. It decides nothing again. A result with no
    headline gives its lines as they are; one with a headline gives the layout (P1032)."""

    @classmethod
    def render(cls, result, style=PLAIN, tool=None, painter=None):
        """The text of `result` in `style`. `tool` is the op's name on the status line, and `painter` paints it (None:
        `painter_for(style, import_rich)`; the CLI gives the one its View chose, P478). A paint that raises gives the plain
        text."""
        if result.headline is None:
            return "\n".join(result.lines)
        return paint_or_plain(painter or painter_for(style, import_rich), cls.layout(result, style, tool))

    @staticmethod
    def status_line(result, style, tool):
        """The status line's spans: the headline's mark, then the op, the status word and the headline's sentence."""
        headline = result.headline
        mark = (MARK_SYMBOLS if style.symbols else MARK_WORDS)[headline.mark]
        return [(mark, "mark-" + headline.mark), (" %s: %s. %s" % (tool, result.status(), printable(headline.sentence)), "status")]

    @classmethod
    def layout(cls, result, style, tool):
        """The lines of the text view, each a list of (text, role) spans: the status line, the facts, then the findings,
        the Note and Next, each block after a blank line. A command is always the last line, alone."""
        headline = result.headline
        lines = [cls.status_line(result, style, tool), []]
        lines += [[(line, "fact")] for line in result.lines]
        notes = list(result.notes or ()) + list(headline.text_notes)
        blocks = [TextReport.findings_block(result.findings, headline),
                  TextReport.section("Note", [[("    " + printable(note), "quiet")] for note in notes]), TextReport.next_block(result)]
        for block in blocks:
            lines += [[]] + block if block else []
        return lines

    @staticmethod
    def section(heading, items):
        """A heading and its items, or nothing when it has none."""
        return [[("  " + heading, "heading")]] + items if items else []

    @staticmethod
    def findings_block(findings, headline):
        """The Problems and the Not checked sections: each finding's sentence, then its fix on a `fix:` line, unless the
        fix only restates the verdict (`headline.verdict_fixes`). The headline's blocker comes first in its section."""
        block = []
        for severity, heading in SECTIONS:
            items = []
            for found in sorted([each for each in findings if each.severity == severity], key=lambda each: each.code != headline.blocker):
                items.append([("    - " + printable(found.sentence), "fact")])
                items += [[("      fix: " + printable(found.fix), "quiet")]] if found.fix and found.fix not in headline.verdict_fixes else []
            block += TextReport.section(heading, items)
        return block

    @staticmethod
    def next_block(result):
        """Next: per step a heading, its why and its command, the command last; with no step, the line that points to the
        section of the headline's blocker (else Not checked, else Problems), and nothing when there is no finding either."""
        block = []
        for step in result.next:
            said = (YOU_MESSAGE if step.needs_yes or step.needs_person else "") + (YES_MESSAGE % step.op if step.needs_yes else "")
            block += [[("  Next:", "heading"), (said, "fact")], [("    why: " + printable(step.why), "fact")],
                      [("    " + step_command(step), "command")]]
        if block:
            return block
        severities = [each.severity for each in result.findings if each.code == result.headline.blocker][:1] or \
            {each.severity for each in result.findings}
        first = next((heading for severity, heading in reversed(SECTIONS) if severity in severities), None)
        return [[("  Next:", "heading")], [("    " + NO_COMMAND_MESSAGE % first, "fact")]] if first else []


class StatusLine(TextReport):
    """Renderer: a result with a headline as a blank line and its status line, nothing more (P478): the run's events said
    the facts, the findings and the commands as they came, so the verdict is the last line, where the eye rests. A
    result with no headline gives its lines as `TextReport` does."""

    @classmethod
    def layout(cls, result, style, tool):
        return [[], cls.status_line(result, style, tool)]
# --- end MVP ---
