"""P418 (#546): the text guards of `scripts/text_guards.py`, each tested on what it must take out."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import text_guards  # noqa: E402


class OneLineTest(unittest.TestCase):
    def test_every_character_that_ends_a_line_comment_becomes_a_space(self):
        for ends in ("\n", "\r", "\x85", "\u2028", "\u2029", "\x00"):
            with self.subTest(ends=repr(ends)):
                self.assertEqual(text_guards.one_line("a%sb" % ends), "a b")


class GuardLinesTest(unittest.TestCase):
    """P423 (#556): the text a script prints, line by line, with each line's own newlines kept."""

    def test_the_newlines_of_the_text_stay(self):
        self.assertEqual(text_guards.guard_lines("a\nb"), "a\nb")
        self.assertEqual(text_guards.guard_lines("a\n"), "a\n")
        self.assertEqual(text_guards.guard_lines(""), "")

    def test_a_character_a_terminal_does_not_print_shows_as_a_question_mark(self):
        for hidden in ("\r", "\t", "\u202e", "\x1b", "\u2028", "\x00"):
            with self.subTest(hidden=repr(hidden)):
                self.assertEqual(text_guards.guard_lines("a%sb\nc%sd" % (hidden, hidden)), "a?b\nc?d")

    def test_a_text_that_is_not_a_string_is_not_turned_into_one(self):
        with self.assertRaises(AttributeError):
            text_guards.guard_lines(None)


class CleanTest(unittest.TestCase):
    def test_a_line_or_paragraph_separator_becomes_a_space(self):
        self.assertEqual(text_guards.clean("a\u2028b\u2029c"), "a b c")


if __name__ == "__main__":
    unittest.main()
