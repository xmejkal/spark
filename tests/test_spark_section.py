"""
Proof that `build/spark_section.SparkSection` splices spark's block between two marker lines in a person's text, once for
every file that holds one (`AGENTS.md`, `.gitignore`), and leaves the person's text around the markers as it is.

    python3 -m unittest tests.test_spark_section
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.build.spark_section import SparkSection  # noqa: E402

SECTION = SparkSection("# begin", "# begin. spark writes this", "# end")
BLOCK = "# begin. spark writes this\nA\nB\n# end\n"


class ThePlacementTest(unittest.TestCase):
    def test_the_block_goes_to_the_end_after_one_blank_line(self):
        self.assertEqual(SECTION.placed("mine\n", "A\nB\n"), ("mine\n\n" + BLOCK, None))

    def test_a_text_with_no_trailing_newline_gets_one_before_the_blank_line(self):
        self.assertEqual(SECTION.placed("mine", "A\nB\n"), ("mine\n\n" + BLOCK, None))

    def test_an_empty_text_gets_the_block_after_one_blank_line(self):
        self.assertEqual(SECTION.placed("", "A\nB\n"), ("\n" + BLOCK, None))

    def test_an_old_section_is_replaced_between_the_markers_only(self):
        old = "top\n# begin. spark writes this\nold\n# end\nbottom\n"
        self.assertEqual(SECTION.placed(old, "A\nB\n"), ("top\n" + BLOCK + "bottom\n", None))

    def test_an_old_begin_line_with_other_words_is_found_by_its_prefix(self):
        old = "top\n# begin. an older spark said this\nold\n# end\nbottom\n"
        self.assertEqual(SECTION.placed(old, "A\nB\n"), ("top\n" + BLOCK + "bottom\n", None))

    def test_a_begin_with_no_end_below_it_gives_a_reason_and_no_text(self):
        text, reason = SECTION.placed("# begin\nold\n", "A\n")
        self.assertIsNone(text)
        self.assertIn("no end marker", reason)

    def test_an_end_above_the_begin_is_no_end(self):
        text, reason = SECTION.placed("# end\n# begin\nold\n", "A\n")
        self.assertIsNone(text)
        self.assertIn("no end marker", reason)

    def test_a_marker_named_inside_a_sentence_is_no_marker(self):
        text, reason = SECTION.placed("see the # begin and # end lines\n", "A\n")
        self.assertIsNone(reason)
        self.assertTrue(text.endswith("\n# begin. spark writes this\nA\n# end\n"), text)

    def test_the_crlf_of_a_person_stays_outside_the_block(self):
        text, _ = SECTION.placed("a\r\nb\r\n", "A\n")
        self.assertTrue(text.startswith("a\r\nb\r\n\n# begin"), repr(text))


if __name__ == "__main__":
    unittest.main()
