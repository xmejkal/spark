"""
Proof that the sweep of old scratch folders removes ours and only ours (P435).

    python3 -m unittest tests.test_scratch
"""

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import scratch  # noqa: E402

DAY = scratch.OLD_AFTER_SECONDS


def planted(parent, name, age):
    """A folder `name` with a file in it, last touched `age` seconds before now."""
    folder = Path(parent) / name
    folder.mkdir()
    (folder / "f.txt").write_text("x")
    when = time.time() - age
    os.utime(folder, (when, when))
    return folder


class RemoveOldFoldersTest(unittest.TestCase):
    def setUp(self):
        self.parent = tempfile.mkdtemp()

    def sweep(self, **more):
        return scratch.remove_old_folders(self.parent, "spark-tests-", time.time(), **more)

    def test_old_goes_and_the_rest_stays(self):
        old = planted(self.parent, "spark-tests-old", 2 * DAY)
        new = planted(self.parent, "spark-tests-new", 60)
        other = planted(self.parent, "tmpXYZ", 2 * DAY)
        plain = Path(self.parent) / "spark-tests-file"
        plain.write_text("x")
        os.utime(plain, (time.time() - 2 * DAY,) * 2)
        self.assertEqual(self.sweep(), ["spark-tests-old"])
        self.assertEqual([old.exists(), new.exists(), other.exists(), plain.exists()], [False, True, True, True])

    def test_a_link_stays_and_its_target_survives(self):
        target = planted(self.parent, "target", 2 * DAY)
        link = Path(self.parent) / "spark-tests-link"
        link.symlink_to(target)
        self.assertEqual(self.sweep(), [])
        self.assertEqual([link.is_symlink(), (target / "f.txt").exists()], [True, True])

    def test_another_owner_stays(self):
        folder = planted(self.parent, "spark-tests-old", 2 * DAY)
        self.assertEqual(self.sweep(owner=os.lstat(folder).st_uid + 1), [])
        self.assertTrue(folder.exists())

    def test_the_age_edge(self):
        planted(self.parent, "spark-tests-edge", DAY - 5)
        self.assertEqual(self.sweep(), [])
        planted(self.parent, "spark-tests-over", DAY + 5)
        self.assertEqual(self.sweep(), ["spark-tests-over"])

    def test_a_missing_parent_removes_nothing(self):
        self.assertEqual(scratch.remove_old_folders(self.parent + "/none", "spark-tests-", time.time()), [])


if __name__ == "__main__":
    unittest.main()
