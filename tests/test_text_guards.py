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


if __name__ == "__main__":
    unittest.main()
