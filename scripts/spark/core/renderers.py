"""
The Renderers of an OperationResult (P657): `JsonEnvelope`, the default of `Operation.json_renderer`, `FlatJsonLine`,
which the bench scripts keep, `JsonDocument`, its indented sibling, which check_all keeps (P804), and `FullEnvelope`,
parts.py's envelope with every key (P707), each a `--json` line; and `TextReport`, the text view a person reads (P1032):
a result with a headline as a status line, the facts, the findings with their fix, a Note and the next step, painted
plain or, through rich when it imports, in colour.
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


class JsonDocument(FlatJsonLine):
    """Renderer: FlatJsonLine's indented sibling (P804): an OperationResult's `data` as one JSON document over several
    lines, as `json.dumps(data, indent=2)` writes it, which check_all prints with --json. An empty text when `data` is
    None, so nothing is printed, and a bad argument gets the usage, as FlatJsonLine's."""

    @staticmethod
    def render(result, tool, op):
        return "" if result.data is None else json.dumps(result.data, indent=2)


# --- MVP ---
#: The scripts folder: a step's op `<op>` runs `<SCRIPTS>/<op>.py`, the rule board_envelope.next_text uses.
SCRIPTS = Path(__file__).resolve().parents[2]
#: The symbol of each mark on the status line, when the stream can encode it.
MARK_SYMBOLS = {MARK_OK: "✓", MARK_STOP: "✗", MARK_WARNING: "!", MARK_UNCHECKED: "?"}
#: The ASCII word of each mark, for a stream whose encoding cannot encode the symbols (D8).
MARK_WORDS = {MARK_OK: "OK", MARK_STOP: "STOP", MARK_WARNING: "WARN", MARK_UNCHECKED: "?"}
#: The rich style of each role of a span (D6): the mark's colour, bold headings and command, dim fixes and Note.
STYLES = {"mark-" + MARK_OK: "bold green", "mark-" + MARK_STOP: "bold red", "mark-" + MARK_WARNING: "bold yellow",
          "mark-" + MARK_UNCHECKED: "bold magenta", "status": "bold", "heading": "bold", "quiet": "dim", "command": "bold",
          "fact": None}
#: The section headings of the findings, in their order, by severity.
SECTIONS = ((outcomes.PROBLEMS, "Problems"), (outcomes.COULD_NOT_RUN, "Not checked"))
#: The Next section's line when there is no step: it points to the first item that says why.
NO_COMMAND_MESSAGE = "No command: the first item under %s above says why."
#: The Next heading's words for a step that needs the person, and for one that needs their yes.
YOU_MESSAGE, YES_MESSAGE = " you, in your own terminal.", " %s.py asks for your yes."


def step_command(step):
    """The one line a person runs for `step`: `NAME=value` for each variable of its env, then its script and argv, all
    shell-quoted and through `printable`, so a newline in an argument shows as `?` and never breaks the line."""
    names = ["%s=%s" % (name, shlex.quote(str(value))) for name, value in sorted((step.env or {}).items())]
    return printable(" ".join(names + [shlex.join([str(SCRIPTS / ("%s.py" % step.op))] + [str(each) for each in step.argv])]))


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


class TextReport:
    """Renderer: an OperationResult as a person reads it, as one text. It decides nothing again. A result with no
    headline gives its lines as they are; one with a headline gives the layout (P1032)."""

    @staticmethod
    def render(result, style=PLAIN, tool=None, importer=import_rich):
        """The text of `result` in `style`. `tool` is the op's name on the status line. A rich paint that raises gives
        the plain text."""
        if result.headline is None:
            return "\n".join(result.lines)
        lines = TextReport.layout(result, style, tool)
        try:
            return painter_for(style, importer).paint(lines)
        except Exception:  # noqa: BLE001  rich of another version may refuse a setting: the plain text stands
            return PlainPainter.paint(lines)

    @staticmethod
    def layout(result, style, tool):
        """The lines of the text view, each a list of (text, role) spans: the status line, the facts, then the findings,
        the Note and Next, each block after a blank line. A command is always the last line, alone."""
        headline = result.headline
        mark = (MARK_SYMBOLS if style.symbols else MARK_WORDS)[headline.mark]
        status = " %s: %s. %s" % (tool, result.status(), printable(headline.sentence))
        lines = [[(mark, "mark-" + headline.mark), (status, "status")], []]
        lines += [[(line, "fact")] for line in result.lines]
        notes = list(result.notes or ()) + list(headline.text_notes)
        blocks = [TextReport.findings_block(result.findings),
                  TextReport.section("Note", [[("    " + printable(note), "quiet")] for note in notes]), TextReport.next_block(result)]
        for block in blocks:
            lines += [[]] + block if block else []
        return lines

    @staticmethod
    def section(heading, items):
        """A heading and its items, or nothing when it has none."""
        return [[("  " + heading, "heading")]] + items if items else []

    @staticmethod
    def findings_block(findings):
        """The Problems and the Not checked sections: each finding's sentence, then its fix on a `fix:` line."""
        block = []
        for severity, heading in SECTIONS:
            items = []
            for found in [each for each in findings if each.severity == severity]:
                items.append([("    - " + printable(found.sentence), "fact")])
                items += [[("      fix: " + printable(found.fix), "quiet")]] if found.fix else []
            block += TextReport.section(heading, items)
        return block

    @staticmethod
    def next_block(result):
        """Next: per step a heading, its why and its command, the command last; with no step, the line that points to the
        first finding, and nothing when there is no finding either."""
        block = []
        for step in result.next:
            said = (YOU_MESSAGE if step.needs_yes or step.needs_person else "") + (YES_MESSAGE % step.op if step.needs_yes else "")
            block += [[("  Next:", "heading"), (said, "fact")], [("    why: " + printable(step.why), "fact")],
                      [("    " + step_command(step), "command")]]
        if block:
            return block
        severities = {each.severity for each in result.findings}
        first = next((heading for severity, heading in reversed(SECTIONS) if severity in severities), None)
        return [[("  Next:", "heading")], [("    " + NO_COMMAND_MESSAGE % first, "fact")]] if first else []
# --- end MVP ---
