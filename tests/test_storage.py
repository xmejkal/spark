"""P1036 (#1519): one Storage under the Stores. The bytes that the two moved Stores write stay those of main, the contract
runs on FileStorage and on MemoryStorage, and the namespaces behind the seam are the only ones served."""

import hashlib
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.records import store  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
