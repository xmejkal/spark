"""P1032 (#1512): the text view. `text_style_of` decides the style once per run from the stream and the environment, and
`TextReport` lays a result with a headline out as a status line, the facts, the findings with their fix, a Note and the
next step, the command alone on the last line. A result with no headline prints its lines as before."""

import io
import re
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from fakes import Stream  # noqa: E402
from spark.core import outcomes  # noqa: E402
from spark.core.renderers import PlainPainter, RichPainter, TextReport, painter_for  # noqa: E402
from spark.core.result import MARK_OK, MARK_STOP, MARK_UNCHECKED, MARK_WARNING, Finding, Headline, NextStep, OperationResult  # noqa: E402
from spark.core.text_style import PLAIN, TextStyle, text_style_of  # noqa: E402
from suite_runs import needs_rich  # noqa: E402

#: An SGR code, the only escape code the coloured form may add.
SGR = re.compile(r"\x1b\[[0-9;]*m")
COLOUR = TextStyle(True, True, True)
DEPLOY = str(ROOT.resolve() / "scripts" / "deploy.py")
STEP = NextStep("deploy", ["--project", "/p", "--token", "ab12-cd34"], "erases ALL of the flash", ["deletes", "writes"], True,
                None, {"SPARK_HOME": "/s"})
PROBLEM = Finding(outcomes.PROBLEMS, "flash", "flash_differs", "the flash differs", "deploy.py asks")
UNCHECKED = Finding(outcomes.COULD_NOT_RUN, None, "no_mac", "no token: why", None)


def a_result(findings=(PROBLEM, UNCHECKED), steps=(STEP,), mark=MARK_WARNING, sentence="Warning: one thing."):
    return OperationResult({"a": 1}, list(findings), list(steps), ["  Board", "    port  p"], notes=["a note"],
                           headline=Headline(sentence, mark, ("a text note",)))


def pipe_with(**environ):
    return text_style_of(io.StringIO(), environ)


def terminal_with(**environ):
    return text_style_of(Stream(tty=True), environ)


class TheStyleTest(unittest.TestCase):
    """The style is decided once per run: colour and motion only on a terminal with a usable TERM (P1032)."""

    def test_a_pipe_is_plain_whatever_term_says(self):
        self.assertEqual(pipe_with(TERM="xterm-256color")[:2], (False, False))

    def test_a_terminal_with_a_usable_term_has_colour_and_motion(self):
        self.assertEqual(terminal_with(TERM="xterm-256color"), TextStyle(True, True, True))

    def test_dumb_unknown_and_unset_term_are_plain_on_a_terminal(self):
        for environ in ({"TERM": "dumb"}, {"TERM": "unknown"}, {"TERM": ""}, {}):
            with self.subTest(environ=environ):
                self.assertEqual(terminal_with(**environ)[:2], (False, False))

    def test_no_color_set_and_not_empty_removes_colour_and_keeps_motion(self):
        self.assertEqual(terminal_with(TERM="xterm", NO_COLOR="1")[:2], (False, True))
        self.assertEqual(terminal_with(TERM="xterm", NO_COLOR="")[:2], (True, True))

    def test_force_color_adds_colour_never_motion_and_no_color_wins(self):
        self.assertEqual(pipe_with(FORCE_COLOR="1")[:2], (True, False))
        self.assertEqual(pipe_with(FORCE_COLOR="")[:2], (False, False))
        self.assertEqual(pipe_with(FORCE_COLOR="1", NO_COLOR="1")[:2], (False, False))
        self.assertEqual(terminal_with(TERM="dumb", FORCE_COLOR="1")[:2], (True, False))

    def test_claudecode_decides_nothing(self):
        self.assertEqual(pipe_with(CLAUDECODE="1"), pipe_with())
        self.assertEqual(terminal_with(TERM="xterm", CLAUDECODE="1"), terminal_with(TERM="xterm"))

    def test_a_stream_that_cannot_say_is_no_terminal(self):
        closed = io.StringIO()
        closed.close()
        self.assertEqual(text_style_of(closed, {"TERM": "xterm"})[:2], (False, False))

    def test_an_encoding_with_no_marks_gives_the_ascii_words(self):
        ascii_stream = io.TextIOWrapper(io.BytesIO(), encoding="ascii")
        style = text_style_of(ascii_stream, {})
        self.assertEqual(style, TextStyle(False, False, False))
        self.assertTrue(pipe_with().symbols, "a StringIO has no encoding, and it holds any character")
        for mark, word in ((MARK_OK, "OK"), (MARK_STOP, "STOP"), (MARK_WARNING, "WARN"), (MARK_UNCHECKED, "?")):
            with self.subTest(mark=mark):
                said = TextReport.render(a_result(mark=mark), style, "look")
                self.assertTrue(said.startswith("%s look: problems. Warning: one thing." % word), said)


class TheLayoutTest(unittest.TestCase):

    def test_a_result_with_no_headline_prints_its_lines_as_today_in_every_style(self):
        result = OperationResult({"a": 1}, [PROBLEM], [STEP], ["one", "two"], notes=["n"])
        for style in (PLAIN, COLOUR):
            with self.subTest(style=style):
                self.assertEqual(TextReport.render(result, style, "look"), "one\ntwo")

    def test_the_layout_holds_the_status_line_the_facts_each_section_and_the_step(self):
        self.assertEqual(TextReport.render(a_result(), PLAIN, "look").split("\n"), [
            "! look: problems. Warning: one thing.",
            "",
            "  Board",
            "    port  p",
            "",
            "  Problems",
            "    - the flash differs",
            "      fix: deploy.py asks",
            "  Not checked",
            "    - no token: why",
            "",
            "  Note",
            "    a note",
            "    a text note",
            "",
            "  Next: you, in your own terminal. deploy.py asks for your yes.",
            "    why: erases ALL of the flash",
            "    SPARK_HOME=/s %s --project /p --token ab12-cd34" % DEPLOY])
        no_step = TextReport.render(a_result(steps=()), PLAIN, "look").split("\n")
        self.assertEqual(no_step[-2:], ["  Next:", "    No command: the first item under Not checked above says why."])
        problem_only = TextReport.render(a_result(findings=[PROBLEM], steps=()), PLAIN, "look").split("\n")
        self.assertEqual(problem_only[-1], "    No command: the first item under Problems above says why.")
        no_finding = TextReport.render(a_result(findings=(), mark=MARK_OK, sentence="All match."), PLAIN, "look").split("\n")
        self.assertEqual(no_finding[0], "✓ look: ok. All match.")
        self.assertNotIn("  Problems", no_finding)
        self.assertNotIn("  Not checked", no_finding)
        self.assertEqual(no_finding[4:7], ["", "  Note", "    a note"])
        nothing = TextReport.render(a_result(findings=(), steps=(), mark=MARK_OK), PLAIN, "look").split("\n")
        self.assertEqual(nothing[-1], "    a text note", "with no step and no finding there is no Next")
        plain_step = TextReport.render(a_result(steps=[STEP._replace(needs_yes=False, env=None)]), PLAIN, "look").split("\n")
        self.assertEqual(plain_step[-3:], ["  Next:", "    why: erases ALL of the flash", "    %s --project /p --token ab12-cd34" % DEPLOY])
        person = TextReport.render(a_result(steps=[STEP._replace(needs_yes=False, needs_person="the person")]), PLAIN, "look")
        self.assertIn("\n  Next: you, in your own terminal.\n", person)

    def test_the_blocker_comes_first_and_next_points_at_its_section(self):
        # the review of #1549: refuter 1 (an unknown field with no token) and SF2 (a stop points at Problems)
        other = Finding(outcomes.COULD_NOT_RUN, None, "field_unknown", "flash unknown", None)
        result = a_result(findings=[PROBLEM, other, UNCHECKED], steps=())
        said = TextReport.render(result._replace(headline=result.headline._replace(blocker="no_mac")), PLAIN, "look").split("\n")
        unchecked = said.index("  Not checked")
        self.assertEqual(said[unchecked + 1:unchecked + 3], ["    - no token: why", "    - flash unknown"])
        self.assertEqual(said[-1], "    No command: the first item under Not checked above says why.")
        said = TextReport.render(result._replace(headline=result.headline._replace(blocker="flash_differs")), PLAIN, "look").split("\n")
        self.assertEqual(said[-1], "    No command: the first item under Problems above says why.")
        self.assertEqual([item["code"] for item in result.to_envelope("t", "o")["unchecked"]], ["field_unknown", "no_mac"])

    def test_a_fix_that_restates_the_verdict_has_no_fix_line_and_the_json_keeps_it(self):
        # the review of #1549, SF1: the text view's `fix:` label is true only for a fix that is no verdict
        result = a_result()
        said = TextReport.render(result._replace(headline=result.headline._replace(verdict_fixes=("deploy.py asks",))), PLAIN, "look")
        self.assertNotIn("fix: deploy.py asks", said)
        self.assertIn("    - the flash differs\n  Not checked", said)
        self.assertEqual(result.to_envelope("t", "o")["problems"][0]["fix"], "deploy.py asks")

    def test_the_command_is_one_line_even_with_a_space_a_newline_and_300_characters(self):
        long = "x" * 300
        said = TextReport.render(a_result(steps=[STEP._replace(argv=["--project", "a b\nc", long])]), PLAIN, "look").split("\n")
        self.assertEqual(said[-1], "    SPARK_HOME=/s %s --project 'a b?c' %s" % (DEPLOY, long))

    def test_an_escape_code_in_a_sentence_shows_as_a_question_mark_in_both_styles(self):
        escaped = Finding(outcomes.PROBLEMS, "flash", "flash_differs", "red \x1b[31mword", "fix \x1b[2J")
        result = a_result(findings=[escaped], sentence="Stop: \x1b[31mred.")._replace(notes=["note \x1b[1m"])
        for style in (PLAIN, COLOUR):
            with self.subTest(style=style):
                said = SGR.sub("", TextReport.render(result, style, "look"))
                self.assertNotIn("\x1b", said)
                for shown in ("Stop: ?[31mred.", "red ?[31mword", "fix: fix ?[2J", "note ?[1m"):
                    self.assertIn(shown, said)


class ThePaintersTest(unittest.TestCase):

    def test_painter_for_gives_plain_without_colour_and_when_rich_does_not_import(self):
        called = []

        def importer():
            called.append(1)
            return types.SimpleNamespace(Console=None, Text=None)

        def missing():
            raise ImportError("No module named 'rich'")
        self.assertIs(painter_for(PLAIN, importer), PlainPainter)
        self.assertEqual(called, [])
        self.assertIs(painter_for(COLOUR, missing), PlainPainter)
        self.assertIsInstance(painter_for(COLOUR, importer), RichPainter)

    def test_a_rich_that_raises_gives_the_plain_text(self):
        def console(**settings):
            raise TypeError("__init__() got an unexpected keyword argument 'soft_wrap'")  # rich 6.0.0
        old_rich = types.SimpleNamespace(Console=console, Text=object)
        result = a_result()
        self.assertEqual(TextReport.render(result, COLOUR, "look", painter_for(COLOUR, lambda: old_rich)), TextReport.render(result, PLAIN, "look"))

    @needs_rich
    def test_the_coloured_form_is_the_plain_form_plus_sgr_codes(self):
        result = a_result(steps=[STEP._replace(argv=["--project", "x" * 300])])
        coloured = TextReport.render(result, COLOUR, "look")
        self.assertTrue(SGR.search(coloured), coloured)
        self.assertEqual(SGR.sub("", coloured), TextReport.render(result, PLAIN, "look"))
        self.assertEqual(coloured.count("\n"), TextReport.render(result, PLAIN, "look").count("\n"))


if __name__ == "__main__":
    unittest.main()
