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
from suite_runs import planted_folder as planted  # noqa: E402

DAY = scratch.OLD_AFTER_SECONDS


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
        plain.chmod(0o644)
        self.assertEqual(self.sweep(), ["spark-tests-old"])
        self.assertEqual([old.exists(), new.exists(), other.exists(), plain.exists()], [False, True, True, True])
        self.assertEqual(plain.stat().st_mode & 0o777, 0o644, "a plain file is not opened up")

    def test_a_link_stays_and_its_target_survives(self):
        target = planted(self.parent, "target", 2 * DAY)
        link = Path(self.parent) / "spark-tests-link"
        link.symlink_to(target)
        target.chmod(0o755)
        self.assertEqual(self.sweep(), [])
        self.assertEqual(target.stat().st_mode & 0o777, 0o755, "a link's target is not opened up")
        self.assertEqual([link.is_symlink(), (target / "f.txt").exists()], [True, True])

    def test_a_link_to_a_read_only_folder_is_not_opened_up(self):
        target = planted(self.parent, "target", 2 * DAY)
        target.chmod(0o555)
        self.addCleanup(target.chmod, 0o755)
        link = Path(self.parent) / "spark-tests-link"
        link.symlink_to(target)
        self.assertFalse(scratch.remove_tree(str(link)))
        self.assertEqual(target.stat().st_mode & 0o777, 0o555)

    def test_another_owner_stays(self):
        folder = planted(self.parent, "spark-tests-old", 2 * DAY)
        self.assertEqual(self.sweep(owner=os.lstat(folder).st_uid + 1), [])
        self.assertTrue(folder.exists())

    def test_the_age_edge(self):
        planted(self.parent, "spark-tests-edge", DAY - 5)
        self.assertEqual(self.sweep(), [])
        planted(self.parent, "spark-tests-over", DAY + 5)
        self.assertEqual(self.sweep(), ["spark-tests-over"])

    def test_exactly_a_day_old_stays(self):
        folder = Path(self.parent) / "spark-tests-exact"
        folder.mkdir()
        os.utime(folder, (1_000_000_000, 1_000_000_000))
        self.assertEqual(scratch.remove_old_folders(self.parent, "spark-tests-", 1_000_000_000 + DAY), [])
        self.assertEqual(scratch.remove_old_folders(self.parent, "spark-tests-", 1_000_000_001 + DAY), ["spark-tests-exact"])

    def test_a_read_only_folder_inside_goes_too(self):
        old = planted(self.parent, "spark-tests-old", 2 * DAY)
        (old / "ro").mkdir()
        (old / "ro" / "f").write_text("x")
        (old / "ro").chmod(0o555)
        (old / "deep").mkdir()
        (old / "deep" / "x").mkdir()
        (old / "deep" / "x" / "f").write_text("x")
        (old / "deep").chmod(0)
        os.utime(old, (time.time() - 2 * DAY,) * 2)  # the setup above touched it
        self.assertEqual(self.sweep(), ["spark-tests-old"])
        self.assertFalse(old.exists())

    @unittest.skipIf(os.geteuid() == 0, "root can remove from a read-only folder")
    def test_a_name_is_listed_only_when_the_folder_is_gone(self):
        locked = Path(tempfile.mkdtemp())
        folder = planted(locked, "spark-tests-old", 2 * DAY)
        locked.chmod(0o555)
        try:
            self.assertEqual(scratch.remove_old_folders(str(locked), "spark-tests-", time.time()), [])
            self.assertTrue(folder.exists())
        finally:
            locked.chmod(0o755)

    def test_a_missing_parent_removes_nothing(self):
        self.assertEqual(scratch.remove_old_folders(self.parent + "/none", "spark-tests-", time.time()), [])


if __name__ == "__main__":
    unittest.main()
