"""P1256 (#1815): `copyable(line, home)` of `scripts/spark/core/shell_line.py`, the rule a printed command passes before a
person pastes it. Each refusal has a test, and each near miss that must pass has one too. The home is a fake one with a
space, never the real home folder (tests/test_orphans.py keeps every test free of a home path)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from spark.core.shell_line import copyable  # noqa: E402

#: A fake home folder with a space in it.
HOME = Path("/tmp/a b")


class TheRuleRefusesTest(unittest.TestCase):
    def refused(self, *lines):
        for line in lines:
            with self.subTest(line=line):
                self.assertFalse(copyable(line, HOME))

    def test_an_unquoted_angle_bracket_is_a_redirection(self):
        self.refused("look.py --project <project>", "SPARK_HOME=<store> look.py", "look.py > out", "look.py 'a'<b")

    def test_a_line_end_breaks_the_line(self):
        self.refused("look.py\nrm x", "look.py\rrm x", "look.py 'a\nb'")

    def test_a_tilde_that_starts_a_quoted_word_is_not_the_home_folder(self):
        self.refused("look.py --project '~/lamp'", 'look.py --project "~/lamp"', "'~/lamp/x.py'")

    def test_an_unquoted_space_of_the_home_folder_splits_the_word(self):
        self.refused("/tmp/a b/x.py --project p", "x.py --project /tmp/a b/lamp")

    def test_a_bang_outside_single_quotes_is_history_expansion(self):
        self.refused("x.py --why hi!", 'x.py --why "hi!"', 'x.py "a\\!"')


class TheRulePassesTest(unittest.TestCase):
    def passed(self, *lines):
        for line in lines:
            with self.subTest(line=line):
                self.assertTrue(copyable(line, HOME))

    def test_a_placeholder_in_single_quotes(self):
        self.passed("parts.py --pick /p 'soil=<part>'", "init_project.py --answers '<answers.json>'",
                    "run_scenario.py 'sim/scenarios/<name>.scenario.yaml'", "x.py '<part>'")

    def test_an_angle_bracket_in_double_quotes_or_after_a_backslash_is_plain_text(self):
        self.passed('x.py "a<b"', "x.py a\\<b")

    def test_a_bang_in_single_quotes_or_after_a_backslash(self):
        self.passed("x.py '!'", "x.py hi\\!")

    def test_a_tilde_inside_a_quoted_word_or_unquoted(self):
        self.passed("x.py 'a~b'", "x.py ~/lamp", "x.py --project=~/lamp", "x.py a'~'")

    def test_the_home_folder_quoted_or_escaped(self):
        self.passed("'/tmp/a b/x.py' --project '/tmp/a b/lamp'", '"/tmp/a b/x.py"', "/tmp/a\\ b/x.py",
                    "SPARK_HOME='/tmp/a b/store' '/tmp/a b/x.py'")

    def test_a_home_with_no_space_never_refuses_by_itself(self):
        self.assertTrue(copyable("/tmp/ab/x.py --project /tmp/ab/lamp", Path("/tmp/ab")))

    def test_a_line_that_shlex_joins_passes(self):
        import shlex
        argv = [str(HOME / "x.py"), "--project", str(HOME / "lamp"), "<part>", "a!b", "$(rm)", "a;b", "a|b"]
        self.assertTrue(copyable("SPARK_HOME=%s %s" % (shlex.quote(str(HOME / "s")), shlex.join(argv)), HOME))
