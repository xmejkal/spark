"""P88: where the store is — read on every call, and never the person's while the suite runs (docs/2026-10-04-store-design.md §6.1)."""

import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import threading
import time
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

    def test_an_unchanged_write_still_tightens_a_loosened_private_file(self):
        store.write_json("drawer", "x", {"a": 1})
        target = self.home / "drawer" / "x.json"
        os.chmod(target, 0o644)
        os.chmod(self.home / "drawer", 0o755)
        self.assertFalse(store.write_json("drawer", "x", {"a": 1}))
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE((self.home / "drawer").stat().st_mode), 0o700)

    def test_a_private_part_file_is_0600_before_it_holds_a_byte(self):
        real_write_text = Path.write_text
        seen = []

        def look_at_the_part_first(path, text, *args, **kwargs):
            if path.name.endswith(".part"):
                seen.append((stat.S_IMODE(path.stat().st_mode), path.stat().st_size))
            return real_write_text(path, text, *args, **kwargs)

        for stale in (False, True):
            with self.subTest(stale=stale):
                target = Path(tempfile.mkdtemp()) / "entry.json"
                if stale:  # what an older, failed write left behind: looser than 0600, and not empty
                    left_behind = target.with_name("entry.json.part")
                    left_behind.write_text("half of an old write")
                    os.chmod(left_behind, 0o644)
                seen.clear()
                with mock.patch.object(Path, "write_text", autospec=True, side_effect=look_at_the_part_first):
                    store.write_file(target, "secret\n", private=True)
                self.assertEqual(seen, [(0o600, 0)])
                self.assertEqual((target.read_text(), stat.S_IMODE(target.stat().st_mode)), ("secret\n", 0o600))

    def test_a_copied_folder_is_private_all_the_way_down(self):
        source = Path(tempfile.mkdtemp()) / "chip"
        (source / "sub").mkdir(parents=True)
        (source / "sub" / "f.txt").write_text("x")
        os.chmod(source / "sub" / "f.txt", 0o644)
        os.chmod(source / "sub", 0o755)
        store.copy_folder("shelf", source, "chip")
        copied = self.home / "shelf" / "chip"
        self.assertEqual(stat.S_IMODE((copied / "sub" / "f.txt").stat().st_mode), 0o600)
        for folder in (copied, copied / "sub", self.home / "shelf"):
            self.assertEqual(stat.S_IMODE(folder.stat().st_mode), 0o700)
        with self.assertRaises(store.StoreProblem):
            store.copy_folder("shelf", source, "../x")

    def test_a_copied_folder_inside_git_is_refused(self):
        repo = Path(tempfile.mkdtemp())
        (repo / ".git").mkdir()
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(repo / "store")}):
            with self.assertRaises(store.StoreProblem):
                store.copy_folder("shelf", repo, "chip")
        self.assertFalse((repo / "store").exists())

    def test_a_slug_is_plain_words_never_the_raw_text(self):
        self.assertEqual(store.slug('Gravity: I2S 3W "Class D" $amp'), "gravity-i2s-3w-class-d-amp")
        self.assertEqual(store.slug("dfrobot-MYST01-Raspberry Pi"), "dfrobot-myst01-raspberry-pi")
        self.assertEqual(len(store.slug("x" * 100)), 60)
        self.assertEqual(store.slug("!!!"), "entry")


class OneWriterAtATimeTest(unittest.TestCase):
    """P97 (§6.1): a write is whole or not at all, and a second writer waits for the first."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_write_that_fails_halfway_leaves_the_old_file_whole(self):
        target = Path(tempfile.mkdtemp()) / "record.json"
        target.write_text("old\n")
        with mock.patch.object(Path, "replace", side_effect=OSError("the disk is full")), self.assertRaises(OSError):
            store.write_file(target, "new\n")
        self.assertEqual(target.read_text(), "old\n")

    def test_a_write_that_fails_leaves_no_part_file_behind(self):
        real_write_text = Path.write_text

        def runs_out_of_room_on_the_part(path, text, *args, **kwargs):
            if path.name.endswith(".part"):
                real_write_text(path, text[:2], *args, **kwargs)  # half of it lands first
                raise OSError("the disk is full")
            return real_write_text(path, text, *args, **kwargs)

        for private in (False, True):
            with self.subTest(private=private):
                target = Path(tempfile.mkdtemp()) / "record.json"
                target.write_text("old\n")
                with mock.patch.object(Path, "write_text", autospec=True, side_effect=runs_out_of_room_on_the_part):
                    with self.assertRaises(OSError):
                        store.write_file(target, "new\n", private=private)
                self.assertEqual(sorted(found.name for found in target.parent.iterdir()), ["record.json"])
                self.assertEqual(target.read_text(), "old\n")

    def test_a_write_waits_while_another_holds_the_store(self):
        given = Path(tempfile.mkdtemp()) / "entries.json"
        given.write_text(json.dumps([{"label": "a probe", "count": 1}]))
        with store.locked():
            writer = subprocess.Popen([sys.executable, str(SCRIPTS / "parts.py"), "--drawer-set", str(given)],
                                      env=dict(os.environ), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.5)
            self.assertFalse((self.home / "drawer" / "a-probe.json").exists(), "it wrote while another held the store")
        self.assertEqual(writer.wait(timeout=60), 0)
        self.assertTrue((self.home / "drawer" / "a-probe.json").exists())

    def test_a_writer_on_another_store_does_not_wait(self):
        elsewhere = Path(tempfile.mkdtemp())
        given = Path(tempfile.mkdtemp()) / "entries.json"
        given.write_text(json.dumps([{"label": "a probe", "count": 1}]))
        with store.locked():
            writer = subprocess.run([sys.executable, str(SCRIPTS / "parts.py"), "--drawer-set", str(given)],
                                    env=dict(os.environ, SPARK_HOME=str(elsewhere)), capture_output=True, timeout=30)
        self.assertEqual(writer.returncode, 0, writer.stderr)
        self.assertTrue((elsewhere / "drawer" / "a-probe.json").exists())

    def test_a_read_does_not_wait_for_a_writer(self):
        with store.locked():
            reader = subprocess.run([sys.executable, str(SCRIPTS / "parts.py"), "--drawer"], env=dict(os.environ),
                                    capture_output=True, timeout=30)
        self.assertEqual(reader.returncode, 0, reader.stderr)

    def test_a_lock_taken_inside_a_lock_does_not_wait_for_itself(self):
        nesting = "import store\nwith store.locked():\n    with store.locked():\n        print('twice')"
        try:
            nested = subprocess.run([sys.executable, "-c", nesting], cwd=SCRIPTS, env=dict(os.environ),
                                    capture_output=True, text=True, timeout=20)
        except subprocess.TimeoutExpired:
            self.fail("a lock taken inside a lock waited for itself, and would have waited for ever")
        self.assertEqual((nested.returncode, nested.stdout.strip()), (0, "twice"), nested.stderr)

    def test_another_thread_waits_for_a_store_taken_a_second_time(self):
        entered = threading.Event()

        def take_the_store():
            with store.locked():
                entered.set()

        other = threading.Thread(target=take_the_store, daemon=True)
        with store.locked():
            pass
        with store.locked():
            other.start()
            self.assertFalse(entered.wait(timeout=0.5), "another thread got in while this one held the store")
        other.join(timeout=20)
        self.assertTrue(entered.is_set())


class TheHistoryTest(unittest.TestCase):
    """P97 (§5.7): one event per line, appended, a repeat of a key not written, private."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_an_event_is_written_once(self):
        reused = {"event": "reused", "project": "plant-alarm", "need": "soil", "part": "sen0193-soil-moisture"}
        self.assertEqual((store.append_event(reused), store.append_event(dict(reused))), (True, False))
        self.assertEqual([json.loads(line) for line in (self.home / "history.jsonl").read_text().splitlines()], [reused])

    def test_a_reason_given_again_is_the_same_event(self):
        first = {"event": "passed_over", "project": "plant-alarm", "need": "soil", "part": "x", "why": "too big", "by": "person"}
        store.append_event(first)
        self.assertFalse(store.append_event(dict(first, why="too dear")), "keyed by project, need and part")

    def test_a_step_started_again_is_another_event(self):
        step = {"event": "step", "project": "plant-alarm", "step": "C", "session": "s1", "start": "2026-10-06T10:00:00+00:00"}
        store.append_event(step)
        self.assertTrue(store.append_event(dict(step, start="2026-10-06T11:00:00+00:00")))
        self.assertEqual(len(store.events()), 2)

    def test_the_history_is_private_and_never_inside_git(self):
        store.append_event({"event": "reused", "project": "p", "need": "n", "part": "x"})
        self.assertEqual(stat.S_IMODE((self.home / "history.jsonl").stat().st_mode), 0o600)
        repo = Path(tempfile.mkdtemp())
        (repo / ".git").mkdir()
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(repo / "store")}), self.assertRaises(store.StoreProblem):
            store.append_event({"event": "reused", "project": "p", "need": "n", "part": "x"})
        self.assertFalse((repo / "store" / "history.jsonl").exists())

    def test_a_line_that_is_not_an_event_is_named(self):
        (self.home / "history.jsonl").write_text('{"event":"reused"}\nnot json\n')
        with self.assertRaises(store.StoreProblem) as broken:
            store.events()
        self.assertIn("line 2", str(broken.exception))

    def test_a_reason_with_a_line_separator_in_it_is_still_one_line_and_one_event(self):
        said = "příliš velké\u2028a drahé\u0085také"  # json.dumps(ensure_ascii=False) leaves U+2028 and U+0085 as they are
        passed = {"event": "passed_over", "project": "plant-alarm", "need": "soil", "part": "x", "why": said, "by": "person"}
        self.assertTrue(store.append_event(passed))
        self.assertEqual(store.events(), [passed])
        self.assertIn("příliš velké", (self.home / "history.jsonl").read_text(encoding="utf-8"), "kept readable, not escaped")
        self.assertFalse(store.append_event(dict(passed, why="again")), "the file still reads as the one event it holds")

    def test_the_events_come_back_in_the_order_they_were_written(self):
        reused = {"event": "reused", "project": "p", "need": "n", "part": "x"}
        step = {"event": "step", "project": "p", "step": "C", "session": "s1", "start": "2026-10-06T10:00:00+00:00"}
        store.append_event(reused)
        store.append_event(step)
        self.assertEqual(store.events(), [reused, step])

    def test_a_repeat_of_any_earlier_event_is_refused_not_only_of_the_last(self):
        first = {"event": "reused", "project": "p", "need": "n", "part": "x"}
        second = {"event": "reused", "project": "p", "need": "n", "part": "y"}
        store.append_event(first)
        store.append_event(second)
        self.assertFalse(store.append_event(dict(first)))
        self.assertEqual(store.events(), [first, second])

    def test_a_part_passed_over_and_picked_later_is_two_events(self):
        passed = {"event": "passed_over", "project": "plant-alarm", "need": "soil", "part": "x", "why": "too big", "by": "person"}
        picked = {"event": "reused", "project": "plant-alarm", "need": "soil", "part": "x"}
        self.assertEqual((store.append_event(passed), store.append_event(picked)), (True, True))
        self.assertEqual([event["event"] for event in store.events()], ["passed_over", "reused"])

    def test_events_that_differ_in_one_field_of_their_key_are_each_written(self):
        # §5.7's keys, written out: a step by (project, step, session, start); a reuse and a pass-over by (project, need,
        # and the pick's part, board or entry); a build by (project, board, parts).
        step = {"event": "step", "project": "p", "step": "C", "session": "s1", "start": "t1"}
        reuse = {"event": "reused", "project": "p", "need": "n", "part": "x"}
        passing = {"event": "passed_over", "project": "p", "need": "n", "part": "x"}
        build = {"event": "built", "project": "p", "board": {"id": "b", "digest": "d1"}, "parts": [{"id": "x", "digest": "d2"}]}
        another_pick = {"project": "q", "need": "m", "part": "y", "board": "b", "entry": "e"}
        differences = [(step, {"project": "q", "step": "D", "session": "s2", "start": "t2"}),
                       (reuse, another_pick), (passing, another_pick),
                       (build, {"project": "q", "board": {"id": "b", "digest": "d3"}, "parts": [{"id": "x", "digest": "d4"}]})]
        for event, changes in differences:
            for field, other in changes.items():
                with self.subTest(event=event["event"], field=field):
                    (self.home / "history.jsonl").unlink(missing_ok=True)
                    store.append_event(event)
                    self.assertTrue(store.append_event(dict(event, **{field: other})), "%s is part of the key" % field)

    def test_every_kind_of_line_that_is_not_an_event_is_named_with_its_file_and_line(self):
        not_events = [b"[1]", b'"reused"', b"5", b"null", b'{"project":"p"}', b'{"event":5}', b'{"event":null}',
                      b"", b"\xff\xfe not utf-8"]
        for line in not_events:
            with self.subTest(line=line):
                (self.home / "history.jsonl").write_bytes(b'{"event":"reused"}\n' + line + b"\n")
                with self.assertRaises(store.StoreProblem) as broken:
                    store.events()
                self.assertIn("history.jsonl line 2 ", str(broken.exception))

    def test_a_history_someone_loosened_is_private_again_after_the_next_event(self):
        store.append_event({"event": "reused", "project": "p", "need": "n", "part": "x"})
        target = self.home / "history.jsonl"
        os.chmod(target, 0o644)
        os.chmod(self.home, 0o755)
        store.append_event({"event": "reused", "project": "p", "need": "n", "part": "y"})
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.home.stat().st_mode), 0o700)

    def test_a_last_line_left_without_its_newline_does_not_swallow_the_next_event(self):
        left_open = {"event": "reused", "project": "p", "need": "n", "part": "x"}
        (self.home / "history.jsonl").write_text(json.dumps(left_open))  # a hand edit that did not end its line
        after = {"event": "reused", "project": "p", "need": "n", "part": "y"}
        self.assertTrue(store.append_event(after))
        self.assertEqual(store.events(), [left_open, after])

    def test_an_empty_history_file_takes_its_first_event(self):
        (self.home / "history.jsonl").write_text("")
        first = {"event": "reused", "project": "p", "need": "n", "part": "x"}
        self.assertEqual(store.events(), [])
        self.assertTrue(store.append_event(first))
        self.assertEqual(store.events(), [first])


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
