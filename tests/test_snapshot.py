"""
P184: tools/snapshot.py records what spark answers in the projects that use it, on copies, never the originals.

Every later change in P158's plan is measured as a diff against a snapshot (the design §10.1, §12.3 H0a), so the
snapshot must be honest in four ways: it never writes into the project or the store it reads, two snapshots of
unchanged spark are equal line for line, a changed line is reported once under the command that printed it, and a
step it could not run is recorded as skipped with its reason, never as a pass.

    python3 -m unittest tests.test_snapshot
"""

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import snapshot  # noqa: E402

#: A stand-in for a spark script: prints its arguments, writes a file where it runs, and reads one optional env var.
FAKE_SCRIPT = """import os, sys
from pathlib import Path
Path("written-by-the-command.txt").write_text("x")
print("args:", " ".join(sys.argv[1:]))
print("cwd:", os.getcwd())
print("note:", os.environ.get("FAKE_NOTE", "same"))
import tempfile
print("wrote", tempfile.mkdtemp(prefix="spark-spine-") + "/Board.tsx")
sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
"""


def digest(folder: Path) -> str:
    """Every file under `folder`, path and bytes, as one sha256: a change anywhere changes it."""
    h = hashlib.sha256()
    for p in sorted(folder.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(folder)).encode()); h.update(p.read_bytes())
    return h.hexdigest()


class Fixture:
    """A fake spark, a fake store and a fake project, in temporary folders."""

    def __init__(self):
        self.spark = Path(tempfile.mkdtemp()); (self.spark / "scripts").mkdir()
        (self.spark / "scripts" / "fake.py").write_text(FAKE_SCRIPT)
        self.store = Path(tempfile.mkdtemp()); (self.store / "drawer").mkdir()
        (self.store / "drawer" / "a.json").write_text("{}")
        self.project = Path(tempfile.mkdtemp()); (self.project / "requirements.json").write_text("{}")
        self.out = Path(tempfile.mkdtemp())

    def spec(self, needs_tsci=False):
        return [{"name": "proj", "source": str(self.project),
                 "commands": [{"label": "fake.py one", "argv": ["{spark}/scripts/fake.py", "one"], "needs_tsci": needs_tsci}],
                 "left_out": {"fake.py live": "it reaches the network"}}]


class TheSnapshotIsHonest(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def test_it_writes_nothing_inside_the_project(self):
        project_before, store_before = digest(self.f.project), digest(self.f.store)
        taken = snapshot.take(self.f.spec(), self.f.out, self.f.spark, self.f.store)
        self.assertEqual(digest(self.f.project), project_before, "the project is read, never written")
        self.assertEqual(digest(self.f.store), store_before, "the store is copied, never written")
        command = taken["projects"]["proj"]["commands"][0]
        self.assertEqual(command["exit"], 0)
        self.assertIn("args: one", command["stdout"])

    def test_two_snapshots_of_unchanged_spark_are_equal(self):
        first = snapshot.take(self.f.spec(), self.f.out / "1", self.f.spark, self.f.store)
        second = snapshot.take(self.f.spec(), self.f.out / "2", self.f.spark, self.f.store)
        self.assertEqual(snapshot.report(first, second), [], "the scratch paths are written as placeholders")
        self.assertIn("cwd: <copy>", first["projects"]["proj"]["commands"][0]["stdout"])

    def test_a_random_temp_folder_name_is_not_a_difference(self):
        # The first real snapshot (2026-10-11): check_spine writes into tempfile's random folder, and three commands
        # differed between two runs of unchanged spark until the random part was written as a placeholder.
        first = snapshot.take(self.f.spec(), self.f.out / "1", self.f.spark, self.f.store)
        second = snapshot.take(self.f.spec(), self.f.out / "2", self.f.spark, self.f.store)
        self.assertEqual(snapshot.report(first, second), [])
        self.assertIn("wrote <tmp>/spark-spine-<random>/Board.tsx", first["projects"]["proj"]["commands"][0]["stdout"])

    def test_a_changed_line_is_reported_once_with_its_command(self):
        old = snapshot.take(self.f.spec(), self.f.out / "old", self.f.spark, self.f.store)
        new = snapshot.take(self.f.spec(), self.f.out / "new", self.f.spark, self.f.store, env={"FAKE_NOTE": "changed"})
        lines = snapshot.report(old, new)
        self.assertEqual([l for l in lines if l.startswith("  - ")], ["  - note: same"])
        self.assertEqual([l for l in lines if l.startswith("  + ")], ["  + note: changed"])
        self.assertEqual(sum(1 for l in lines if l.startswith("proj: fake.py one")), 1, "named once, with its command")

    def test_a_changed_exit_is_reported(self):
        old = snapshot.take(self.f.spec(), self.f.out / "old", self.f.spark, self.f.store)
        new = snapshot.take(self.f.spec(), self.f.out / "new", self.f.spark, self.f.store, env={"FAKE_EXIT": "1"})
        self.assertIn("  exit 0 → 1", snapshot.report(old, new))

    def test_a_step_needing_tsci_without_node_modules_is_recorded_as_skipped(self):
        taken = snapshot.take(self.f.spec(needs_tsci=True), self.f.out, self.f.spark, self.f.store)
        command = taken["projects"]["proj"]["commands"][0]
        self.assertIsNone(command["exit"])
        self.assertEqual(command["skipped"], "no node_modules in the copy (tsci needed); copy it, never link it")

    def test_what_it_leaves_out_is_said(self):
        taken = snapshot.take(self.f.spec(), self.f.out, self.f.spark, self.f.store)
        self.assertEqual(taken["projects"]["proj"]["left_out"], {"fake.py live": "it reaches the network"})

    def test_the_store_copy_is_dated_and_digested(self):
        taken = snapshot.take(self.f.spec(), self.f.out, self.f.spark, self.f.store)
        self.assertEqual(taken["store"]["sha256"], digest(self.f.store))


class TheSparkUnderTest(unittest.TestCase):
    def test_spark_names_the_tree_whose_answers_are_recorded(self):
        # The bin's Makefile reads spark from a fixed path (the targeted refuter's fix 1); a snapshot names its own.
        f = Fixture()
        from unittest import mock
        with mock.patch.object(snapshot, "projects", return_value=f.spec()), \
                mock.patch.object(snapshot, "STORE", f.store), \
                mock.patch("sys.stdout", new_callable=__import__("io").StringIO):
            code = snapshot.main(["--out", str(f.out), "--spark", str(f.spark)])
        taken = __import__("json").loads((f.out / "snapshot.json").read_text())
        self.assertEqual(code, 0)
        self.assertIn("args: one", taken["projects"]["proj"]["commands"][0]["stdout"])


class TheProjectsItKnows(unittest.TestCase):
    def test_every_fixture_project_is_in_the_list(self):
        names = {p["name"] for p in snapshot.projects()}
        for fixture in (ROOT / "tests" / "data" / "snapshot").iterdir():
            if fixture.is_dir():
                with self.subTest(fixture=fixture.name):
                    self.assertIn(fixture.name, names)

    def test_the_live_vendor_check_is_left_out_and_said(self):
        bin_ = next(p for p in snapshot.projects() if p["name"] == "smartbin-local")
        self.assertIn("check_vendor_pins.py (live)", bin_["left_out"])


if __name__ == "__main__":
    unittest.main()
