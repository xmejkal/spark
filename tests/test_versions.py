"""P471 (#642): versions.release_tuple and versions.is_older, as a table. Pure: no patch."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import versions  # noqa: E402


class ReleaseTupleTest(unittest.TestCase):
    def test_a_pre_release_is_its_release_and_trailing_zeros_drop(self):
        for version, expected in (("4.12.0", (4, 12)), ("5.0", (5,)), ("5.0.0", (5,)), ("5.0.0b1", (5,)),
                                  ("5.0.dev0", (5,)), ("5.0.post1", (5,)), ("5.5.0", (5, 5)), ("10.0", (10,)),
                                  ("5.1b2", (5, 1)), ("", None), (None, None), ("abc", None)):
            with self.subTest(version):
                self.assertEqual(versions.release_tuple(version), expected)


class IsOlderTest(unittest.TestCase):
    def test_older_against_a_floor_of_5_0(self):
        for version, expected in (("4.12.0", True), ("4.9.dev0", True), ("5.0", False), ("5.0.0", False),
                                  ("5.0.0b1", False), ("5.0.dev0", False), ("5.0.post1", False), ("5.5.0", False),
                                  ("10.0", False), ("", False), (None, False), ("abc", False)):
            with self.subTest(version):
                self.assertIs(versions.is_older(version, "5.0"), expected)

    def test_a_missing_or_digitless_floor_refuses_nothing(self):
        for floor in ("", None, "dev"):
            with self.subTest(floor):
                self.assertIs(versions.is_older("4.12.0", floor), False)


if __name__ == "__main__":
    unittest.main()
