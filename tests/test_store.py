"""P88: where the store is — read on every call, and never the person's while the suite runs (docs/2026-10-04-store-design.md §6.1)."""

import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import store  # noqa: E402

#: Where the person's store is when nothing says otherwise.
PERSONS = Path.home() / ".local" / "share" / "spark"


def home_in(env):
    """What `store.home()` answers in a fresh process with exactly this environment — a process with no unittest in it."""
    done = subprocess.run([sys.executable, "-c", "import store; print(store.home())"], cwd=SCRIPTS, env=env,
                          capture_output=True, text=True, timeout=30)
    return Path(done.stdout.strip())


class TheHomeTest(unittest.TestCase):
    def test_spark_home_wins(self):
        scratch = tempfile.mkdtemp()
        self.assertEqual(home_in({"HOME": "/nowhere", "XDG_DATA_HOME": "/xdg", "SPARK_HOME": scratch}), Path(scratch))

    def test_then_the_xdg_data_home(self):
        self.assertEqual(home_in({"HOME": "/nowhere", "XDG_DATA_HOME": "/xdg"}), Path("/xdg/spark"))

    def test_then_the_home_folder(self):
        self.assertEqual(home_in({"HOME": "/nowhere"}), Path("/nowhere/.local/share/spark"))

    def test_it_is_read_on_every_call(self):
        first, second = tempfile.mkdtemp(), tempfile.mkdtemp()
        with mock.patch.dict(os.environ, {"SPARK_HOME": first}):
            self.assertEqual(store.place("catalog"), Path(first) / "catalog")
        with mock.patch.dict(os.environ, {"SPARK_HOME": second}):
            self.assertEqual(store.place("catalog"), Path(second) / "catalog")
            self.assertEqual(store.place("tools"), Path(second) / "tools.json")


class TheSuiteStaysOutOfThePersonsStoreTest(unittest.TestCase):
    def test_the_suite_runs_on_a_scratch_store(self):
        self.assertNotEqual(store.home(), PERSONS)
        self.assertTrue(os.environ.get("SPARK_HOME"), "store.py gives a process running unittest a scratch store")

    def test_a_script_the_suite_starts_gets_the_same_scratch_store(self):
        self.assertEqual(home_in(dict(os.environ)), store.home())

    def test_no_script_imports_unittest_so_a_real_run_never_gets_a_scratch_store(self):
        importing = [path.name for path in sorted(SCRIPTS.glob("*.py"))
                     if re.search(r"^\s*(import|from)\s+(unittest|doctest)\b", path.read_text(), re.M)]
        self.assertEqual(importing, [])

    def test_only_the_store_says_where_the_store_is(self):
        spelled = [path.name for path in sorted(SCRIPTS.glob("*.py"))
                   if '".local"' in path.read_text() and path.name != "store.py"]
        self.assertEqual(spelled, [], "every path into the person's store comes from store.place()")


class TheLayersTest(unittest.TestCase):
    """§5.5: one walk over every layer, nearest first — the project, the shelf, spark's library, the catalog."""

    def setUp(self):
        self.home, self.project, self.library = (Path(tempfile.mkdtemp()) for _ in range(3))
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def put(self, folder, name):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text("{}")

    def test_the_order_is_project_shelf_library_catalog(self):
        self.assertEqual([name for name, _ in store.layers("parts", self.library, self.project, drafts=True)],
                         ["project", "shelf", "library", "catalog"])
        self.assertEqual([name for name, _ in store.layers("parts", self.library)], ["shelf", "library"])
        self.assertEqual([name for name, _ in store.layers("boards", self.library, self.project, drafts=True)],
                         ["project", "library"], "boards have no shelf and no catalog")

    def test_the_nearest_layer_wins(self):
        self.put(self.library, "a.json")
        self.put(self.home / "shelf", "a.json")
        self.put(self.home / "shelf", "b.json")
        self.put(self.project / "parts", "b.json")
        self.put(self.home / "catalog", "c.json")
        found = store.records("parts", self.library, self.project, drafts=True)
        self.assertEqual({key: layer for key, (layer, _) in found.items()}, {"a": "shelf", "b": "project", "c": "catalog"})
        self.assertNotIn("c", store.records("parts", self.library, self.project), "the catalog is read only for drafts")

    def test_a_skipped_name_is_not_a_record(self):
        self.put(self.project / "boards", "active.json")
        self.put(self.project / "boards", "x-board.json")
        self.assertEqual(sorted(store.records("boards", self.library, self.project, skip={"active.json"})), ["x-board"])

    def test_a_project_s_board_choice_is_not_a_board(self):
        import boards
        self.put(self.project / "boards", "active.json")
        self.assertNotIn("active", boards.available(self.project))


class ContainedWritesTest(unittest.TestCase):
    """§5.1, §5.8: a write lands inside its place, whole or not at all, private, and never in a git work tree."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_write_is_whole_and_a_retried_one_changes_nothing(self):
        self.assertTrue(store.write_json("drawer", "x", {"a": "Kč"}))
        self.assertFalse(store.write_json("drawer", "x", {"a": "Kč"}))
        self.assertEqual(json.loads((self.home / "drawer" / "x.json").read_text()), {"a": "Kč"})
        self.assertEqual(list((self.home / "drawer").glob("*.part")), [])

    def test_a_private_place_is_0600_in_0700(self):
        store.write_json("drawer", "x", {})
        self.assertEqual(stat.S_IMODE((self.home / "drawer" / "x.json").stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE((self.home / "drawer").stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(self.home.stat().st_mode), 0o700)

    def test_a_key_that_is_not_plain_is_refused(self):
        for key in ("../x", "a/b", "X", "", ".hidden", "a.json"):
            with self.subTest(key=key), self.assertRaises(store.StoreProblem):
                store.write_json("drawer", key, {})
        self.assertFalse((self.home / "drawer").exists())

    def test_a_private_place_inside_git_is_refused(self):
        repo = Path(tempfile.mkdtemp())
        (repo / ".git").mkdir()
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(repo / "store")}):
            with self.assertRaises(store.StoreProblem) as refused:
                store.write_json("drawer", "x", {})
        self.assertIn(str(repo.resolve()), str(refused.exception))
        self.assertFalse((repo / "store").exists())

    def test_a_slug_is_plain_words_never_the_raw_text(self):
        self.assertEqual(store.slug('Gravity: I2S 3W "Class D" $amp'), "gravity-i2s-3w-class-d-amp")
        self.assertEqual(store.slug("dfrobot-MYST01-Raspberry Pi"), "dfrobot-myst01-raspberry-pi")
        self.assertEqual(len(store.slug("x" * 100)), 60)
        self.assertEqual(store.slug("!!!"), "entry")


class TheProjectsListTest(unittest.TestCase):
    """§5.5: the projects list tells spark where the person's projects are."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_project_is_listed_once_under_its_folder_s_name(self):
        folder = Path(tempfile.mkdtemp()) / "plant-alarm"
        folder.mkdir()
        self.assertEqual(store.add_project(folder), "plant-alarm")
        self.assertEqual(store.add_project(folder), "plant-alarm")
        self.assertEqual(store.projects(), {"plant-alarm": folder.resolve()})

    def test_a_second_live_folder_with_the_same_name_gets_a_number(self):
        first, second = (Path(tempfile.mkdtemp()) / "bin" for _ in range(2))
        first.mkdir()
        second.mkdir()
        self.assertEqual((store.add_project(first), store.add_project(second)), ("bin", "bin-2"))

    def test_a_list_that_is_not_json_is_named(self):
        (self.home / "projects.json").write_text("{")
        with self.assertRaises(store.StoreProblem) as broken:
            store.projects()
        self.assertIn("projects.json", str(broken.exception))


if __name__ == "__main__":
    unittest.main()
