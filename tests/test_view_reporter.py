"""P478 (#656): the text view of a run's events. `TextViewReporter` prints a LINE as `TerminalReporter` does and a heading
`[n/N] name` for a BEGIN of one of the Operation's stages, `view_for` decides terminal, pipe or --json once per run, and
`run_cli` finishes the Reporter after every run."""

import contextlib
import io
import re
import sys
import types
import unittest
from collections import namedtuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from fakes import FakeOutsideWorld  # noqa: E402
from spark.core.cli import HelpText, run_cli  # noqa: E402
from spark.core.events import Event, Reporter, TerminalReporter  # noqa: E402
from spark.core.operation import COMMON_ARGUMENTS, READS, Argument, Operation  # noqa: E402
from spark.core.privacy import MaskingReporter, Privacy  # noqa: E402
from spark.core.renderers import PlainPainter, RichPainter, import_rich, painter_for  # noqa: E402
from spark.core.result import OperationResult  # noqa: E402
from spark.core.text_style import TextStyle  # noqa: E402
from spark.core.view_reporter import TextViewReporter  # noqa: E402
from suite_runs import needs_rich  # noqa: E402

#: An SGR code, the only escape code the coloured form may add.
SGR = re.compile(r"\x1b\[[0-9;]*m")
COLOUR = TextStyle(True, True, True)
#: A stage row as the view reads it: only its `name`.
Row = namedtuple("Row", "name summary")
PLAN_LOOK = (Row("plan", "why plan"), Row("look", "why look"))
LINES = (Event.line("look", "one line"), Event.line("look", "first\nsecond\nthird"), Event.line("look", "a \x1b[2J raw /p", raw=True))


def shown(reporter, events):
    for event in events:
        reporter.report(event)
    return reporter.stream.getvalue()


class TheLinesTest(unittest.TestCase):
    """A LINE keeps the bytes it had before the text view (test 1), and --json prints no heading (test 3)."""

    def test_a_line_prints_the_bytes_the_terminal_reporter_prints(self):
        for event in LINES:
            with self.subTest(event=event):
                self.assertEqual(shown(TextViewReporter(io.StringIO(), PlainPainter, ()), [event]),
                                 shown(TerminalReporter(io.StringIO()), [event]))

    def test_the_terminal_reporter_prints_nothing_for_a_begin(self):
        self.assertEqual(shown(TerminalReporter(io.StringIO()), [Event.begin("plan"), Event.begin("look")]), "")


class TheHeadingsTest(unittest.TestCase):
    """A BEGIN of the nth of N stages prints `[n/N] name`, a blank line before each heading but the first (test 2)."""

    def test_each_stage_gets_its_number_and_a_blank_line_before_all_but_the_first(self):
        said = shown(TextViewReporter(io.StringIO(), PlainPainter, PLAN_LOOK),
                     [Event.begin("plan"), Event.line("plan", "a"), Event.begin("look"), Event.line("look", "b")])
        self.assertEqual(said, "[1/2] plan\n  a\n\n[2/2] look\n  b\n")

    def test_a_begin_in_no_stage_and_a_run_with_no_stages_print_nothing(self):
        self.assertEqual(shown(TextViewReporter(io.StringIO(), PlainPainter, PLAN_LOOK), [Event.begin("gate")]), "")
        self.assertEqual(shown(TextViewReporter(io.StringIO(), PlainPainter, ()), [Event.begin("plan"), Event.begin("look")]), "")

    def test_a_kind_it_does_not_know_prints_nothing(self):
        self.assertEqual(shown(TextViewReporter(io.StringIO(), PlainPainter, PLAN_LOOK), [Event("wait", "plan", "x")]), "")

    def test_a_stage_name_with_an_escape_code_shows_it_as_a_question_mark(self):
        said = shown(TextViewReporter(io.StringIO(), PlainPainter, (Row("a\x1b[2Jb", ""),)), [Event.begin("a\x1b[2Jb")])
        self.assertEqual(said, "[1/1] a?[2Jb\n")


class TheFinishTest(unittest.TestCase):
    """`finish` says the run is over: a Decorator passes it on, and run_cli calls it once per run (test 14)."""

    def test_the_masking_reporter_passes_finish_echo_fd_and_the_stream(self):
        finished = []

        class Inner(Reporter):
            stream = "the stream"

            def finish(self):
                finished.append(1)

            def echo_fd(self):
                return 7
        masking = MaskingReporter(Inner(), Privacy())
        masking.finish()
        self.assertEqual((finished, masking.echo_fd(), masking.stream), ([1], 7, "the stream"))

    def test_run_cli_finishes_once_after_the_run_and_before_it_prints_a_crash_too(self):
        for what in ("ok", "crash"):
            with self.subTest(what=what):
                calls, out = [], io.StringIO()

                def builder(project, effects, reporter, values):
                    reporter.finish = lambda: calls.append(("finish", out.getvalue()))
                    return FakeOutsideWorld(reporter=reporter)
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                    run_cli(HelpText("said.py"), Said(calls), ["--what", what], outside_builder=builder)
                self.assertEqual(calls, ["run", ("finish", "")])


class Said(Operation):
    """Operation: one that says a line and returns it, or crashes."""

    name = "said"
    arguments = (Argument(("--what",), "what", str, "ok or crash", "ok"), COMMON_ARGUMENTS["json"])
    effects = (READS,)

    def __init__(self, calls):
        self.calls = calls

    def run(self, what, *, outside):
        self.calls.append("run")
        if what == "crash":
            raise RuntimeError("boom")
        return OperationResult({}, lines=["the answer"])


class TheRichHeadingTest(unittest.TestCase):
    """On a terminal with colour the heading is bold, and the text without its codes is the plain text (test 4)."""

    @needs_rich
    def test_the_heading_is_bold_and_the_plain_form_is_the_coloured_one_without_codes(self):
        events = [Event.begin("plan"), Event.line("plan", "a"), Event.begin("look")]
        coloured = shown(TextViewReporter(io.StringIO(), painter_for(COLOUR, import_rich), PLAN_LOOK), events)
        self.assertIn("\x1b[1m[1/2] plan", coloured)
        self.assertEqual(SGR.sub("", coloured), shown(TextViewReporter(io.StringIO(), PlainPainter, PLAN_LOOK), events))

    def test_a_rich_that_raises_gives_the_plain_heading(self):
        def console(**settings):
            raise TypeError("__init__() got an unexpected keyword argument 'soft_wrap'")
        painter = RichPainter(types.SimpleNamespace(Console=console, Text=object))
        self.assertEqual(shown(TextViewReporter(io.StringIO(), painter, PLAN_LOOK), [Event.begin("look")]), "[2/2] look\n")


if __name__ == "__main__":
    unittest.main()
