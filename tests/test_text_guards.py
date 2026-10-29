"""P418 (#546): the text guards of `scripts/spark/core/text_guards.py`, each tested on what it must take out."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from spark.core import text_guards  # noqa: E402


class OneLineTest(unittest.TestCase):
    def test_every_character_that_ends_a_line_comment_becomes_a_space(self):
        for ends in ("\n", "\r", "\x85", "\u2028", "\u2029", "\x00"):
            with self.subTest(ends=repr(ends)):
                self.assertEqual(text_guards.one_line("a%sb" % ends), "a b")


class ListKeyProblemsTest(unittest.TestCase):
    """P374: a key at any depth with a control or bidi character, or no string, is refused with its path; a clean one is not."""

    def test_a_clean_value_has_no_problem(self):
        self.assertEqual(text_guards.list_key_problems("facts", {"a": {"b": [{"c": 1}], "d": "note\u202e"}}), [])
        self.assertEqual(text_guards.list_key_problems("facts", 5), [])

    def test_a_bad_key_is_named_by_its_path_at_every_depth(self):
        value = {"a": {"b": [{"c": 1}, {"no\u202ete": 2}]}, "x\x1b": 3, 7: 4}
        self.assertEqual([problem.split(" is a key")[0] for problem in text_guards.list_key_problems("facts", value)],
                         ["facts['a']['b'][1]['no\\u202ete']", "facts['x\\x1b']", "facts[7]"])


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


class GuardSentenceTest(unittest.TestCase):
    """P430 (#569): a sentence with a name in it, the name put on one line first."""

    def test_a_newline_in_the_name_shows_as_a_question_mark_and_the_sentences_own_newline_stays(self):
        self.assertEqual(text_guards.guard_sentence("no board on /dev/x\nGRANTED\nnext", "/dev/x\nGRANTED"),
                         "no board on /dev/x?GRANTED\nnext")

    def test_a_name_that_is_none_or_empty_changes_nothing(self):
        self.assertEqual(text_guards.guard_sentence("a\u202eb\nc", None, ""), "a?b\nc")

    def test_each_name_is_put_on_one_line(self):
        self.assertEqual(text_guards.guard_sentence("p\ne q\nr", "p\ne", "q\nr"), "p?e q?r")

    def test_a_path_is_put_on_one_line_too(self):
        self.assertEqual(text_guards.guard_sentence("bad json in /tmp/a\nb/x.json", Path("/tmp/a\nb")), "bad json in /tmp/a?b/x.json")


class PrintableTest(unittest.TestCase):
    def test_printable_shows_what_a_terminal_does_not_print_as_a_question_mark(self):
        self.assertEqual(text_guards.printable("a\nb\u202ec ok"), "a?b?c ok")


class CleanTest(unittest.TestCase):
    def test_a_line_or_paragraph_separator_becomes_a_space(self):
        self.assertEqual(text_guards.clean("a\u2028b\u2029c"), "a b c")


if __name__ == "__main__":
    unittest.main()
