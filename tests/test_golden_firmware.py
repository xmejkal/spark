"""P683 (#920, W6-F1): what run_scenario.py, flash_image.py and import_firmware.py print today stays what they print, so
no move breaks it. No golden run spends a Wokwi minute: ShimGuardTest proves the guard, and FirmwareGoldenTest runs
no Case unless the simulator found is the shim."""

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

import golden_bench  # noqa: E402
import golden_firmware  # noqa: E402
from spark.records import tool_finder  # noqa: E402


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
                              capture_output=True, text=True, timeout=golden_bench.RUN_TIMEOUT_S)

    def test_the_simulator_found_is_the_shim(self):
        self.assertEqual(tool_finder.find("simulator", self.project).command, [str(self.shim)])

    def test_the_project_names_no_other_place_for_the_simulator(self):
        entry = tool_finder.merged(self.project)["tools"]["wokwi-cli"]
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


class FirmwareOpTest(unittest.TestCase):
    """The op an accept run names is the script's name with dashes, for the firmware Cases and the bench's alike."""

    def test_the_op_of_a_firmware_case_is_its_script(self):
        self.assertEqual({golden_bench.op_of(case) for case in golden_firmware.CASES},
                         {"run-scenario", "flash-image", "import-firmware"})

    def test_the_op_of_a_bench_case_is_still_the_first_word_of_its_golden(self):
        self.assertEqual([golden_bench.op_of(case) for case in golden_bench.CASES],
                         [case.golden.split("-")[0] for case in golden_bench.CASES])

    def test_a_missing_golden_names_its_op(self):
        case = golden_firmware.CASES[0]
        why = golden_bench.check_golden(case, "printed", golden_dir=Path(tempfile.mkdtemp()))
        self.assertEqual(why, "%s does not exist: write it with SPARK_ACCEPT=run-scenario" % case.golden)


@needs_littlefs
class FirmwareGoldenTest(unittest.TestCase):
    """Each Case of golden_firmware.CASES is one test, named after its golden, run in its own copy of one project built
    for the class: the bench's golden project, with the shim named as its simulator."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp())
        cls.project = golden_bench.build_project(cls.folder)
        cls.shim = golden_firmware.name_the_shim(cls.project, cls.folder)
        # The guard holds before any child runs: no Case starts unless the simulator found is the shim. A raise, not an
        # assert, which python -O strips.
        if tool_finder.find("simulator", cls.project).command != [str(cls.shim)]:
            raise RuntimeError("the simulator found is not the shim, so no firmware golden runs")

    def run_case(self, case):
        work = Path(tempfile.mkdtemp(dir=self.folder))
        project, store = work / self.project.name, work / "store"
        shutil.copytree(self.project, project)
        code, text = golden_firmware.run_script(case, project, store)
        self.assertEqual(code, case.exit_code, text)
        scrubbed = golden_bench.scrub(text, golden_bench.replacements_of(project, store))
        self.assertIsNone(golden_bench.check_golden(case, scrubbed, golden_dir=golden_firmware.GOLDEN_DIR))

    def test_no_golden_holds_a_path_of_this_machine(self):
        for golden in sorted(golden_firmware.GOLDEN_DIR.iterdir()):
            text = golden.read_text()
            for path in (str(Path.home()), "/Users/", tempfile.gettempdir(), str(golden_bench.ROOT)):
                self.assertNotIn(path, text, golden.name)

    def test_every_golden_has_its_case(self):
        written = {golden.name for golden in golden_firmware.GOLDEN_DIR.iterdir()}
        self.assertEqual(written, {case.golden for case in golden_firmware.CASES})


for _case in golden_firmware.CASES:
    setattr(FirmwareGoldenTest, "test_" + _case.golden.replace("-", "_").replace(".", "_"),
            lambda self, case=_case: self.run_case(case))


if __name__ == "__main__":
    unittest.main()
