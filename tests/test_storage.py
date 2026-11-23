"""P1036 (#1519): one Storage under the Stores. The bytes that the two moved Stores write stay those of main, the contract
runs on FileStorage and on MemoryStorage, and the namespaces behind the seam are the only ones served."""

import ast
import hashlib
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.records import store  # noqa: E402
from spark.records import storage  # noqa: E402
from spark.records.deploy_record_store import DeployRecordStore, outside_deploy  # noqa: E402
from spark.records.registered_project_store import RegisteredProjectStore  # noqa: E402

MAC = "a0:b1:c2:d3:e4:f5"
#: The sha256 of each file that the calls of `write_the_files` write, measured on main e521db8f (P1036's plan, section 5).
REGISTERED_SHA256 = "a1701105e93dd4f3c8fb788c95062e4a88f9c7a57fd83e0466115208081174e8"
BOARD_SHA256 = "b90fca2f8e4473839ffb330d0550e634e4d041ffcc0563f1c58d97b521ecc029"


class ScratchStoreCase(unittest.TestCase):
    """A scratch store of its own, in `self.home`."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp()) / "store"
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(shutil.rmtree, self.home.parent, True)


def write_the_files(registered, deploys):
    """The calls of the plan's section 5 on the two Stores `registered` and `deploys`."""
    registered.register("pixel-games", "https://example.org/someone/pixel-games.git", "box.py", "2026-11-18T20:13:42+01:00")
    registered.register("rc-car", "https://example.org/another/rc-car.git", "flash.sh", "2026-11-19T07:05:09+01:00")
    facts = {"mac": MAC, "project": "blink-c6", "board": "xiao-esp32-c6", "image_sha256": "0",
             "simulation": "passed", "deployed": "2026-10-19T09:24:50+02:00",
             "micropython_banner": "MicroPython v1.24.1 on 2024-11-29; ESP32C6 module with ESP32C6"}
    deploys.write_deploy(facts, "ready seen", "typed by a test")
    deploys.append_deploy(MAC, outside_deploy("pixel-games", "box.py", "2026-11-18T21:40:17+01:00", "ready not read"))


class TheBytesStayTest(ScratchStoreCase):
    """The files of the two Stores keep the bytes, the modes and the unchanged write that main gives them."""

    def test_the_files_keep_main_s_bytes_and_modes(self):
        write_the_files(RegisteredProjectStore(), DeployRecordStore())
        registered, board = store.place("registered-projects"), store.place("boards") / "a0-b1-c2-d3-e4-f5.json"
        self.assertEqual([hashlib.sha256(each.read_bytes()).hexdigest() for each in (registered, board)],
                         [REGISTERED_SHA256, BOARD_SHA256])
        self.assertEqual([each.stat().st_mode & 0o777 for each in (registered, board, board.parent, self.home)],
                         [0o600, 0o600, 0o700, 0o700])

    def test_the_same_registration_again_changes_nothing(self):
        write_the_files(RegisteredProjectStore(), DeployRecordStore())
        registered = store.place("registered-projects")
        before = registered.stat().st_mtime_ns
        again = RegisteredProjectStore().register("pixel-games", "https://example.org/someone/pixel-games.git", "box.py",
                                                  "2026-11-20T10:00:00+01:00")
        self.assertEqual((again[1], registered.stat().st_mtime_ns), (False, before))


class TheMemoryBytesTest(ScratchStoreCase):
    """The calls of `write_the_files` on MemoryStorage keep the objects of the files that TheBytesStayTest pins (test 23).
    The scratch store is for `register`, which still reads the projects list from the file store."""

    def test_memory_keeps_the_registrations_of_the_pinned_file(self):
        write_the_files(RegisteredProjectStore(), DeployRecordStore())
        memory = storage.MemoryStorage()
        write_the_files(RegisteredProjectStore(memory), DeployRecordStore())
        self.assertEqual(sha256_of(store.place("registered-projects")), REGISTERED_SHA256)
        self.assertEqual(memory.get("registered-projects"), json.loads(store.place("registered-projects").read_bytes()))

    def test_memory_keeps_the_board_record_of_the_pinned_file(self):
        write_the_files(RegisteredProjectStore(), DeployRecordStore())
        memory = storage.MemoryStorage()
        write_the_files(RegisteredProjectStore(), DeployRecordStore(memory))
        board = store.place("boards") / "a0-b1-c2-d3-e4-f5.json"
        self.assertEqual(sha256_of(board), BOARD_SHA256)
        self.assertEqual(memory.get("boards", "a0-b1-c2-d3-e4-f5"), json.loads(board.read_bytes()))


class TheRecordPathIsNeverOpenedTest(unittest.TestCase):
    """P1036 (test 24, R2.3): `DeployRecordStore.find_path` names a place for words and for tests on FileStorage, and a
    MemoryStorage never backs it, so no script opens, reads or writes what it gives. A rule about the code, so it reads
    the code: every call of a `find_path` that is not KnownBoardStore's (known_board.py, and `self.known` elsewhere)."""

    USES = ("open", "read_text", "read_bytes", "write_text", "write_bytes")

    @staticmethod
    def calls_of_find_path(tree, source):
        """The Call nodes of DeployRecordStore's `find_path` in one module's `tree`."""
        return [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "find_path" and ast.get_source_segment(source, node.func.value) != "self.known"]

    def opened(self, tree, source):
        """Each line where a result of `find_path`, or a name given one, is opened, read or written."""
        calls = self.calls_of_find_path(tree, source)
        names = {target.id for node in ast.walk(tree) if isinstance(node, ast.Assign) and node.value in calls
                 for target in node.targets if isinstance(target, ast.Name)}

        def is_result(node):
            return node in calls or (isinstance(node, ast.Name) and node.id in names)
        lines = [node.lineno for node in ast.walk(tree) if isinstance(node, ast.Attribute) and node.attr in self.USES
                 and is_result(node.value)]
        return lines + [node.lineno for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                        and node.func.id == "open" and any(is_result(arg) for arg in node.args)]

    def test_no_script_opens_what_find_path_gives(self):
        found, opened = set(), {}
        for module in sorted((ROOT / "scripts").rglob("*.py")):
            if module.name == "known_board.py":
                continue
            source = module.read_text(encoding="utf-8")
            tree = ast.parse(source)
            if self.calls_of_find_path(tree, source):
                found.add(module.name)
            if self.opened(tree, source):
                opened[module.name] = self.opened(tree, source)
        self.assertEqual(opened, {})
        self.assertTrue({"deploy_record_store.py", "bench_service.py"} <= found, found)


class StorageContract:
    """The contract that every Storage keeps (P1036, tests 1 to 11). A class that runs it gives `make()`, `plant(made,
    namespace, key, data)` (a text, bytes, or storage.UNREADABLE) and `kept(made)`: what the Storage holds, as a list."""

    NOT_PLAIN = ("../x", "X", "", "-x")
    OUTSIDE = ("grants", "launcher", "history", "nope")

    def test_nothing_there_is_none(self):
        made = self.make()
        self.assertEqual([made.get("registered-projects"), made.get("boards", "a0-b1")], [None, None])

    def test_a_put_says_whether_it_changed(self):
        made = self.make()
        said = [made.put("boards", "a0-b1", {"mac": "a0:b1"})]
        said.append(made.get("boards", "a0-b1"))
        said.append(made.put("boards", "a0-b1", {"mac": "a0:b1"}))
        said.append(made.put("boards", "a0-b1", {"mac": "a0:b1", "deploys": []}))
        said.append(made.put("registered-projects", None, {"pixel-games": {}}))
        self.assertEqual(said, [True, {"mac": "a0:b1"}, False, True, True])

    def test_a_change_to_what_get_gave_never_reaches_the_storage(self):
        made = self.make()
        made.put("boards", "a0-b1", {"deploys": []})
        made.get("boards", "a0-b1")["deploys"].append("changed")
        self.assertEqual(made.get("boards", "a0-b1"), {"deploys": []})

    def test_the_keys_of_a_folder_are_sorted_and_a_file_has_none(self):
        made = self.make()
        before = made.keys("boards")
        for key in ("c3", "a0-b1", "b2"):
            made.put("boards", key, {})
        self.assertEqual((before, made.keys("boards")), ([], ["a0-b1", "b2", "c3"]))
        with self.assertRaises(ValueError):
            made.keys("registered-projects")

    def test_what_is_no_json_object_is_broken_and_what_cannot_be_read_is_refused(self):
        made = self.make()
        for data in ("{not json", "[1]", "", "[" * 100000, b"\xff"):
            with self.subTest(data=data[:10]):
                self.plant(made, "boards", "a0-b1", data)
                with self.assertRaises(store.StoreError) as refused:
                    made.get("boards", "a0-b1")
                self.assertEqual(refused.exception.code, "record_file_broken")
        self.plant(made, "boards", "c3", storage.UNREADABLE)
        with self.assertRaises(store.StoreError) as refused:
            made.get("boards", "c3")
        self.assertEqual(refused.exception.code, "file_refused")

    def test_a_key_that_is_not_plain_is_refused_and_nothing_is_kept(self):
        made = self.make()
        for key in self.NOT_PLAIN:
            for call in (lambda: made.get("boards", key), lambda: made.put("boards", key, {}), lambda: made.where("boards", key)):
                with self.subTest(key=key), self.assertRaises(store.StoreError) as refused:
                    call()
                self.assertEqual(refused.exception.code, "key_not_plain")
        self.assertEqual(self.kept(made), [])

    def test_a_namespace_outside_the_seam_or_a_key_that_does_not_fit_is_a_bug(self):
        made = self.make()
        for namespace in self.OUTSIDE:
            for call in (lambda: made.get(namespace, "a0"), lambda: made.put(namespace, "a0", {}), lambda: made.keys(namespace),
                         lambda: made.where(namespace, "a0"), lambda: made.get(namespace), lambda: made.put(namespace, None, {})):
                with self.subTest(namespace=namespace), self.assertRaises(ValueError):
                    call()
        for namespace, key in (("registered-projects", "a0"), ("boards", None)):
            for call in (lambda: made.get(namespace, key), lambda: made.put(namespace, key, {}), lambda: made.where(namespace, key)):
                with self.subTest(namespace=namespace, key=key), self.assertRaises(ValueError):
                    call()
        self.assertEqual(self.kept(made), [])

    def test_a_value_that_is_no_object_is_refused(self):
        made = self.make()
        with self.assertRaises(TypeError):
            made.put("boards", "a0-b1", [1])
        self.assertEqual(self.kept(made), [])

    def test_where_names_the_namespace_and_the_key(self):
        made = self.make()
        said = [made.where("boards", "a0-b1"), made.where("registered-projects")]
        self.assertEqual([type(each) for each in said], [str, str])
        self.assertTrue("boards" in said[0] and "a0-b1" in said[0] and "registered-projects" in said[1], said)

    def test_a_lock_inside_its_own_lock_in_one_thread_passes(self):
        made, said = self.make(), []

        def nested():
            with made.locked():
                with made.locked():
                    said.append(made.put("boards", "a0-b1", {}))
        runner = threading.Thread(target=nested, daemon=True)
        runner.start()
        runner.join(5)
        self.assertEqual((runner.is_alive(), said, made.get("boards", "a0-b1")), (False, [True], {}))

    def test_a_put_under_the_lock_waits_while_another_thread_holds_it(self):
        made = self.make()
        held, release = threading.Event(), threading.Event()

        def hold():
            with made.locked():
                held.set()
                release.wait(10)

        def write():
            with made.locked():
                made.put("boards", "a0-b1", {})
        holder = threading.Thread(target=hold, daemon=True)
        holder.start()
        held.wait(10)
        writer = threading.Thread(target=write, daemon=True)
        writer.start()
        writer.join(0.5)
        written_while_held = made.get("boards", "a0-b1")
        release.set()
        holder.join(10)
        writer.join(10)
        self.assertEqual((written_while_held, made.get("boards", "a0-b1")), (None, {}))


class FileStorageContractTest(StorageContract, ScratchStoreCase):
    """The contract on FileStorage, in a scratch store."""

    def make(self):
        return storage.FileStorage()

    def plant(self, made, namespace, key, data):
        path = store.find_file(namespace, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        if data is storage.UNREADABLE:
            path.mkdir()
        elif isinstance(data, bytes):
            path.write_bytes(data)
        else:
            path.write_text(data, encoding="utf-8")

    def kept(self, made):
        return sorted(str(each.relative_to(self.home)) for each in self.home.rglob("*")) if self.home.exists() else []


class MemoryStorageContractTest(StorageContract, unittest.TestCase):
    """The contract on MemoryStorage."""

    def make(self):
        return storage.MemoryStorage()

    def plant(self, made, namespace, key, data):
        made.plant(namespace, key, data)

    def kept(self, made):
        return made.keys("boards") + ([] if made.get("registered-projects") is None else ["registered-projects"])


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class FileStorageTest(ScratchStoreCase):
    """What only FileStorage keeps: the store's modes, its refusals, its one lock and no root of its own (tests 12 to 20)."""

    def test_a_put_makes_private_files_in_private_folders(self):
        storage.FileStorage().put("boards", "a0-b1", {})
        storage.FileStorage().put("registered-projects", None, {})
        modes = [each.stat().st_mode & 0o777 for each in (store.find_file("boards", "a0-b1"), store.place("registered-projects"),
                                                         store.place("boards"), self.home)]
        self.assertEqual(modes, [0o600, 0o600, 0o700, 0o700])

    def test_a_broken_link_is_refused_and_not_nothing(self):
        path = store.find_file("boards", "a0-b1")
        path.parent.mkdir(parents=True)
        path.symlink_to(self.home / "gone.json")
        with self.assertRaises(store.StoreError) as refused:
            storage.FileStorage().get("boards", "a0-b1")
        self.assertEqual(refused.exception.code, "file_refused")

    def test_a_record_spark_may_not_read_is_refused(self):
        storage.FileStorage().put("boards", "a0-b1", {})
        path = store.find_file("boards", "a0-b1")
        path.chmod(0)
        self.addCleanup(path.chmod, 0o600)
        with self.assertRaises(store.StoreError) as refused:
            storage.FileStorage().get("boards", "a0-b1")
        self.assertEqual(refused.exception.code, "file_refused")

    def test_a_store_inside_a_git_work_tree_is_refused_and_nothing_is_written(self):
        (self.home.parent / ".git").mkdir()
        with self.assertRaises(store.StoreError) as refused:
            storage.FileStorage().put("boards", "a0-b1", {})
        self.assertEqual(refused.exception.code, "store_in_repository")
        self.assertFalse(store.find_file("boards", "a0-b1").exists())

    def test_it_keeps_no_root_and_follows_the_store_of_each_call(self):
        made = storage.FileStorage()
        self.assertEqual(vars(made), {})
        other = self.home.parent / "other"
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(other)}):
            made.put("boards", "a0-b1", {})
        self.assertEqual(((other / "boards" / "a0-b1.json").is_file(), store.find_file("boards", "a0-b1").exists()), (True, False))

    def test_a_put_writes_the_bytes_that_write_json_writes(self):
        value = {"mac": "a0:b1", "name": "Žluťoučký kůň", "deploys": [{"n": 1}]}
        storage.FileStorage().put("boards", "a0-b1", value)
        other = self.home.parent / "other"
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(other)}):
            store.write_json("boards", "a0-b1", value)
        self.assertEqual(sha256_of(store.find_file("boards", "a0-b1")), sha256_of(other / "boards" / "a0-b1.json"))

    def test_a_file_that_is_not_plain_is_no_key_and_a_link_to_a_record_is_read(self):
        storage.FileStorage().put("boards", "a0-b1", {})
        (store.place("boards") / "Notes.json").write_text("{}")
        elsewhere = self.home.parent / "elsewhere.json"
        elsewhere.write_text(json.dumps({"mac": "c3"}))
        (store.place("boards") / "c3.json").symlink_to(elsewhere)
        made = storage.FileStorage()
        self.assertEqual((made.keys("boards"), made.get("boards", "c3")), (["a0-b1", "c3"], {"mac": "c3"}))

    def test_where_is_the_path_of_the_file(self):
        made = storage.FileStorage()
        self.assertEqual([made.where("boards", "a0-b1"), made.where("registered-projects")],
                         [str(store.find_file("boards", "a0-b1")), str(store.find_file("registered-projects", None))])

    def test_its_lock_is_the_store_s_one_lock(self):
        said = []

        def nested():
            with store.locked():
                with storage.FileStorage().locked():
                    said.append(storage.FileStorage().put("boards", "a0-b1", {}))
        runner = threading.Thread(target=nested, daemon=True)
        runner.start()
        runner.join(5)
        self.assertEqual((runner.is_alive(), said), (False, [True]))


class TheNamespacesTest(unittest.TestCase):
    """Every place of the store is classified: served by the seam or outside it (tests 21 and 22)."""

    def test_every_place_is_served_or_outside_and_never_both(self):
        self.assertEqual(set(storage.NAMESPACES) & set(storage.OUTSIDE), set())
        self.assertEqual(sorted(storage.NAMESPACES + storage.OUTSIDE), sorted(store.PLACES))
        self.assertEqual([name for name in storage.NAMESPACES if not store.PLAIN.fullmatch(name)], [])

    def test_the_class_of_a_namespace_is_the_store_s(self):
        self.assertEqual([storage.privacy_of(name) for name in storage.NAMESPACES], [storage.PRIVATE, storage.PRIVATE])
        with self.assertRaises(ValueError):
            storage.privacy_of("grants")
        self.assertEqual([name in storage.OUTSIDE for name in ("grants", "launcher")], [True, True])


if __name__ == "__main__":
    unittest.main()
