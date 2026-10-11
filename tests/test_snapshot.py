"""
P184: tools/snapshot.py records what spark answers in the projects that use it, on copies, never the originals.

Every later change in P158's plan (#94) is measured as a diff against a snapshot, so the snapshot must be honest: it
never writes into a project or the store it reads, two snapshots of unchanged spark are equal, every difference is
shown under the command that printed it (moved, repeated and vanished lines included), a difference that may not be
spark's says so, and anything it could not run is said with its reason, never passed over.

    python3 -m unittest tests.test_snapshot
"""

import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import snapshot  # noqa: E402

#: A stand-in for a spark script. It writes where it runs and into $SPARK_HOME (both copies), prints what it was given,
#: and makes a tempfile folder the way check_spine does.
FAKE_SCRIPT = """import os, sys, tempfile, time
from pathlib import Path
Path("written-by-the-command.txt").write_text("x")
Path(os.environ["SPARK_HOME"], "written-into-the-store.txt").write_text("x")
print("started", flush=True)
time.sleep(float(os.environ.get("FAKE_SLEEP", "0")))
print("args:", " ".join(sys.argv[1:]))
print("cwd:", os.getcwd())
for line in os.environ.get("FAKE_LINES", "note: same").split("|"):
    print(line)
print("wrote", tempfile.mkdtemp(prefix="spark-spine-") + "/Board.tsx")
print("kept <tmp>/validation_output")
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
        (self.spark / "scripts" / "boards.py").write_text("print('the spark under test is here')\n")
        self.store = Path(tempfile.mkdtemp()); (self.store / "drawer").mkdir()
        (self.store / "drawer" / "a.json").write_text("{}")
        self.project = Path(tempfile.mkdtemp()); (self.project / "requirements.json").write_text("{}")
        self.out = Path(tempfile.mkdtemp())

    def spec(self, needs_tsci=False, extra=None, name="proj", source=None):
        commands = [{"label": "fake.py one", "argv": ["{spark}/scripts/fake.py", "one"], "needs_tsci": needs_tsci}]
        return [{"name": name, "source": str(source or self.project), "commands": commands + (extra or []),
                 "left_out": {"fake.py live": "it reaches the network"}}]

    def take(self, where, **kw):
        return snapshot.take(kw.pop("spec", None) or self.spec(), self.out / where, self.spark, self.store, **kw)


def first(record, project="proj"):
    return record["projects"][project]["commands"][0]


class TheSnapshotOnlyReads(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def test_it_writes_nothing_inside_the_project_or_the_store(self):
        project_before, store_before = digest(self.f.project), digest(self.f.store)
        taken = self.f.take("one")
        self.assertEqual(digest(self.f.project), project_before, "the project is read, never written")
        self.assertEqual(digest(self.f.store), store_before, "the command wrote into the store's copy, not the store")
        self.assertEqual(first(taken)["exit"], 0)
        self.assertIn("args: one", first(taken)["stdout"])

    def test_reading_a_git_project_leaves_its_index_alone(self):
        git = ["git", "-C", str(self.f.project), "-c", "user.email=t@example.com", "-c", "user.name=t"]
        subprocess.run(["git", "init", "-q", str(self.f.project)], check=True)
        subprocess.run(git + ["add", "."], check=True)
        subprocess.run(git + ["commit", "-qm", "x"], check=True)
        index = self.f.project / ".git" / "index"
        os.utime(index, (1000, 1000))  # the index is old, and a tracked file's time is new:
        os.utime(self.f.project / "requirements.json", None)  # plain `git status` would refresh and rewrite the index
        before = index.stat().st_mtime_ns
        self.f.take("one")
        self.assertEqual(index.stat().st_mtime_ns, before, "git status without optional locks writes nothing")

    def test_a_source_outside_git_is_pinned_by_its_digest(self):
        taken = self.f.take("one")
        self.assertTrue(taken["projects"]["proj"]["pin"].startswith("not a git repository: sha256 "))


class TwoSnapshotsCompare(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def test_two_snapshots_of_unchanged_spark_are_equal(self):
        self.assertEqual(snapshot.report(self.f.take("1"), self.f.take("2")), [])

    def test_the_scratch_folders_and_tempfiles_random_part_are_placeholders(self):
        out = first(self.f.take("1"))["stdout"]
        self.assertIn("cwd: <copy>", out)
        self.assertIn("wrote <tmp>/spark-spine-<random>/Board.tsx", out)
        self.assertIn("kept <tmp>/validation_output", out, "a fixed name is never masked")

    def test_a_changed_line_is_reported_once_with_its_command_and_stream(self):
        lines = snapshot.report(self.f.take("old"), self.f.take("new", env={"FAKE_LINES": "note: changed"}))
        self.assertEqual([l for l in lines if l.startswith("    - ")], ["    - note: same"])
        self.assertEqual([l for l in lines if l.startswith("    + ")], ["    + note: changed"])
        self.assertEqual(sum(1 for l in lines if l.startswith("proj: fake.py one")), 1)
        self.assertIn("  stdout:", lines)

    def test_a_repeated_or_moved_line_is_a_difference(self):
        old = self.f.take("old", env={"FAKE_LINES": "a|b"})
        self.assertIn("    + a", snapshot.report(old, self.f.take("rep", env={"FAKE_LINES": "a|b|a"})))
        self.assertNotEqual(snapshot.report(old, self.f.take("mov", env={"FAKE_LINES": "b|a"})), [])

    def test_a_changed_exit_is_reported(self):
        self.assertIn("  exit 0 → 1", snapshot.report(self.f.take("old"), self.f.take("new", env={"FAKE_EXIT": "1"})))

    def test_a_changed_reason_for_a_skip_is_a_difference(self):
        def record(why):
            command = {"label": "c", "exit": None, "stdout": "", "stderr": "", "skipped": why}
            return {"store": {"sha256": "s"}, "spark": {"pin": "p"}, "projects": {"proj": {"pin": "a", "commands": [command]}}}
        self.assertIn("  exit skipped: one reason → skipped: another", snapshot.report(record("one reason"), record("another")))

    def test_a_command_or_a_project_gone_from_the_new_snapshot_is_reported(self):
        extra = [{"label": "fake.py two", "argv": ["{spark}/scripts/fake.py", "two"], "needs_tsci": False}]
        old = self.f.take("old", spec=self.f.spec(extra=extra) + self.f.spec(name="gone"))
        lines = snapshot.report(old, self.f.take("new"))
        self.assertIn("proj: fake.py two — missing from this snapshot", lines)
        self.assertIn("gone — missing from this snapshot", lines)

    def test_a_changed_store_or_pin_is_context_not_a_difference(self):
        old = self.f.take("old")
        (self.f.store / "drawer" / "b.json").write_text("{}")
        new = self.f.take("new")
        self.assertTrue(snapshot.context(old, new)[0].startswith("the store differs"), snapshot.context(old, new))
        self.assertEqual(snapshot.report(old, new), [])


class WhatItCouldNotRunIsSaid(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def test_a_step_needing_tsci_without_node_modules_is_recorded_as_skipped(self):
        command = first(self.f.take("one", spec=self.f.spec(needs_tsci=True)))
        self.assertIsNone(command["exit"])
        self.assertEqual(command["skipped"], snapshot.NO_TSCI)

    def test_a_command_that_times_out_is_recorded_and_the_rest_still_runs(self):
        extra = [{"label": "fake.py two", "argv": ["{spark}/scripts/fake.py", "two"], "needs_tsci": False}]
        with mock.patch.object(snapshot, "TIMEOUT", 0.5):
            taken = self.f.take("one", spec=self.f.spec(extra=extra), env={"FAKE_SLEEP": "2"})
        commands = taken["projects"]["proj"]["commands"]
        self.assertEqual([c.get("skipped") for c in commands], ["timed out after 0.5 s"] * 2)

    def test_a_timed_out_command_keeps_what_it_printed(self):
        with mock.patch.object(snapshot, "TIMEOUT", 0.5):
            command = first(self.f.take("one", env={"FAKE_SLEEP": "2"}))
        self.assertIn("started", command["stdout"])

    def test_an_earlier_command_that_failed_skips_the_command_that_needs_its_output(self):
        extra = [{"label": "needs it", "argv": ["{spark}/scripts/fake.py", "{fake.py one}"], "needs_tsci": False}]
        taken = self.f.take("one", spec=self.f.spec(extra=extra), env={"FAKE_EXIT": "1"})
        self.assertEqual(taken["projects"]["proj"]["commands"][1]["skipped"],
                         "needs the output of `fake.py one`, which exited 1")

    def test_an_earlier_output_that_is_missing_skips_the_command_that_needs_it(self):
        extra = [{"label": "needs it", "argv": ["{spark}/scripts/fake.py", "{boards.py --paths}"], "needs_tsci": False}]
        command = self.f.take("one", spec=self.f.spec(extra=extra))["projects"]["proj"]["commands"][1]
        self.assertEqual(command["skipped"], "needs the output of `boards.py --paths`, which this project did not run")

    def test_a_missing_project_is_skipped_with_its_reason_and_the_rest_runs(self):
        spec = self.f.spec(name="absent", source=self.f.project / "nowhere") + self.f.spec()
        taken = self.f.take("one", spec=spec)
        self.assertEqual(taken["projects"]["absent"]["skipped"], "its folder is not there")
        self.assertEqual(first(taken)["exit"], 0)

    def test_what_it_leaves_out_is_said(self):
        self.assertEqual(self.f.take("one")["projects"]["proj"]["left_out"], {"fake.py live": "it reaches the network"})

    def test_the_store_copy_is_digested(self):
        self.assertEqual(self.f.take("one")["store"]["sha256"], digest(self.f.store))


class TheCommandLine(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def run_main(self, *argv):
        out = io.StringIO()
        with mock.patch.object(snapshot, "projects", return_value=self.f.spec()), \
                mock.patch.object(snapshot, "STORE", self.f.store), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = snapshot.main(list(argv))
        return code, out.getvalue()

    def test_spark_names_the_tree_whose_answers_are_recorded(self):
        code, _ = self.run_main("--out", str(self.f.out), "--spark", str(self.f.spark))
        self.assertEqual(code, 0)
        taken = json.loads((self.f.out / "snapshot.json").read_text())
        self.assertIn("args: one", first(taken)["stdout"])

    def test_relative_paths_are_resolved(self):
        here = os.getcwd(); self.addCleanup(os.chdir, here)
        os.chdir(self.f.spark.parent)
        code, _ = self.run_main("--out", os.path.relpath(self.f.out), "--spark", self.f.spark.name)
        self.assertEqual(code, 0)
        self.assertEqual(first(json.loads((self.f.out / "snapshot.json").read_text()))["exit"], 0)

    def test_a_spark_tree_without_its_scripts_could_not_run(self):
        code, said = self.run_main("--out", str(self.f.out), "--spark", str(self.f.project))
        self.assertEqual(code, 2)
        self.assertIn("is not a spark tree", said)

    def test_a_bad_against_could_not_run_before_any_work(self):
        not_json = self.f.project / "not.json"; not_json.write_text("no")
        for bad in (str(self.f.out / "missing.json"), str(not_json)):
            with self.subTest(against=bad), mock.patch.object(snapshot, "take", side_effect=AssertionError("ran")):
                code, said = self.run_main("--out", str(self.f.out / "x"), "--spark", str(self.f.spark), "--against", bad)
                self.assertEqual(code, 2)
                self.assertIn("could not run", said)

    def test_against_the_snapshot_it_would_write_is_refused(self):
        code, said = self.run_main("--out", str(self.f.out), "--spark", str(self.f.spark),
                                   "--against", str(self.f.out / "snapshot.json"))
        self.assertEqual(code, 2)
        self.assertIn("is the snapshot this run would write", said)

    def test_equal_runs_exit_0_and_say_so(self):
        self.run_main("--out", str(self.f.out / "a"), "--spark", str(self.f.spark))
        code, said = self.run_main("--out", str(self.f.out / "b"), "--spark", str(self.f.spark),
                                   "--against", str(self.f.out / "a" / "snapshot.json"))
        self.assertEqual(code, 0)
        self.assertIn("nothing differs", said)

    def test_a_moved_pin_with_equal_answers_exits_0_and_names_the_pin(self):
        self.run_main("--out", str(self.f.out / "a"), "--spark", str(self.f.spark))
        (self.f.spark / "scripts" / "later.py").write_text("")  # spark moved on; its answers did not
        code, said = self.run_main("--out", str(self.f.out / "b"), "--spark", str(self.f.spark),
                                   "--against", str(self.f.out / "a" / "snapshot.json"))
        self.assertEqual(code, 0, said)
        self.assertIn("spark: not a git repository", said)
        self.assertIn("nothing differs", said)

    def test_an_out_inside_spark_could_not_run_before_any_work(self):
        for inside in (snapshot.FIXTURES / "would-become-a-fixture", self.f.spark / "out"):
            with self.subTest(out=inside), mock.patch.object(snapshot, "take", side_effect=AssertionError("ran")):
                code, said = self.run_main("--out", str(inside), "--spark", str(self.f.spark))
                self.assertEqual(code, 2)
                self.assertIn("inside spark's tree", said)
                self.assertFalse(inside.exists())

    def test_help_shows_the_exit_codes_and_what_it_needs(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            snapshot.main(["--help"])
        text = out.getvalue()
        for words in ("Exit 0:", "1: some lines differ", "2: it could not run", "Needs:"):
            with self.subTest(words=words):
                self.assertIn(words, text)


class TheProjectsItKnows(unittest.TestCase):
    def test_every_fixture_project_is_in_the_list_with_a_relative_source(self):
        found = {p["name"]: p for p in snapshot.projects()}
        for fixture in (ROOT / "tests" / "data" / "snapshot").iterdir():
            if fixture.is_dir():
                with self.subTest(fixture=fixture.name):
                    self.assertIn(fixture.name, found)
                    self.assertEqual(snapshot.shown(found[fixture.name]["source"]), "tests/data/snapshot/" + fixture.name)

    def test_a_fixture_is_pinned_by_its_own_content_not_the_whole_repository(self):
        fixture = sorted(p for p in (ROOT / "tests" / "data" / "snapshot").iterdir() if p.is_dir())[0]
        self.assertTrue(snapshot._pin(fixture).startswith("in this repository: sha256 "), snapshot._pin(fixture))

    def test_a_fixture_pin_follows_what_spark_reads_not_its_readme(self):
        fixtures = Path(tempfile.mkdtemp()).resolve()
        case = fixtures / "case"; (case / "boards").mkdir(parents=True)
        (case / "boards" / "a.json").write_text("{}")
        with mock.patch.object(snapshot, "FIXTURES", fixtures):
            before = snapshot._pin(case)
            (case / "README.md").write_text("what the case is")
            self.assertEqual(snapshot._pin(case), before)
            (case / "boards" / "a.json").write_text('{"id": "a"}')
            self.assertNotEqual(snapshot._pin(case), before)

    def test_a_spark_tree_inside_this_repository_is_pinned_as_spark_not_as_a_fixture(self):
        fake_root = Path(tempfile.mkdtemp()).resolve()  # as ROOT is: /var is a link on macOS
        nested = fake_root / ".worktrees" / "a-card"; nested.mkdir(parents=True)
        with mock.patch.object(snapshot, "ROOT", fake_root), \
                mock.patch.object(snapshot, "FIXTURES", fake_root / "tests" / "data" / "snapshot"):
            self.assertTrue(snapshot._pin(nested).startswith("not a git repository"), snapshot._pin(nested))

    def test_the_live_vendor_check_is_left_out_and_said(self):
        bin_ = next(p for p in snapshot.projects() if p["name"] == "smartbin-local")
        self.assertIn("check_vendor_pins.py (live)", bin_["left_out"])


if __name__ == "__main__":
    unittest.main()
