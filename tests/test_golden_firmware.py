"""P683 (#920, W6-F1): what run_scenario.py, flash_image.py and import_firmware.py print today stays what they print, so
no move breaks it. No golden run spends a Wokwi minute: the guard tests come first."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from suite_runs import needs_littlefs  # noqa: E402

import golden_firmware  # noqa: E402
import tools  # noqa: E402


class ShimGuardTest(unittest.TestCase):
    """The guard (the PO, 2026-10-31: no paid Wokwi run): the simulator a golden child finds is the shim, every child
    carries the fake token, and the shim runs the fake tool with that token alone."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp())
        cls.project = cls.folder / "project"
        (cls.project / "sim").mkdir(parents=True)
        cls.shim = golden_firmware.name_the_shim(cls.project, cls.folder)

    def run_shim(self, token):
        env = dict(os.environ, WOKWI_CLI_TOKEN=token, FAKE_WOKWI_SERIAL="ready\n")
        log = self.folder / "serial.log"
        return subprocess.run([str(self.shim), "sim", "--serial-log-file", str(log)], env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=golden_firmware.golden_bench.RUN_TIMEOUT_S)

    def test_the_simulator_found_is_the_shim(self):
        self.assertEqual(tools.find("simulator", self.project).command, [str(self.shim)])

    def test_the_project_names_no_other_place_for_the_simulator(self):
        entry = tools.merged(self.project)["tools"]["wokwi-cli"]
        self.assertEqual((entry["also"], entry["fetch"]), ([], None))

    def test_every_child_carries_the_fake_token(self):
        env = golden_firmware.child_env(self.folder / "store")
        self.assertEqual(env["WOKWI_CLI_TOKEN"], golden_firmware.FAKE_TOKEN)

    def test_the_shim_refuses_any_other_token(self):
        for token in ("", "wok_a-real-looking-token", golden_firmware.FAKE_TOKEN + "x"):
            done = self.run_shim(token)
            self.assertEqual(done.returncode, golden_firmware.REFUSED_EXIT, token)
            self.assertNotIn("Wokwi CLI", done.stdout, token)

    def test_the_shim_runs_the_fake_tool_with_the_fake_token(self):
        done = self.run_shim(golden_firmware.FAKE_TOKEN)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("Wokwi CLI v0.0.0 (fake)", done.stdout)


if __name__ == "__main__":
    unittest.main()
