"""P380 (#487): what look, deploy, grant --check, live and reach print today stays what they print, so no move breaks it."""

import hashlib
import json
import os
import shlex
import site
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from suite_runs import needs_littlefs  # noqa: E402

import golden_bench  # noqa: E402
import boards  # noqa: E402
import tools  # noqa: E402
from micropython_fakes import fake_interpreter  # noqa: E402
import board_codes  # noqa: E402
from spark.core import codes  # noqa: E402


@needs_littlefs
class BenchGoldenTest(unittest.TestCase):
    """Each Case of golden_bench.CASES is one test, named after its golden, run in one project built for the class."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp())
        cls.project = golden_bench.build_project(cls.folder)
        look_ok = next(case for case in golden_bench.CASES if case.golden == "look-ok.json")
        code, out = golden_bench.run_script(look_ok, cls.project, Path(tempfile.mkdtemp(dir=cls.folder)))
        cls.token = (json.loads(out)["data"] or {}).get("token") if code == 0 else None
        assert cls.token, "look-ok gave no token, so no deploy Case can run: %s" % out

    def run_case(self, case):
        store = Path(tempfile.mkdtemp(dir=self.folder))  # each Case its own store, so that no grant leaks
        code, out = golden_bench.run_script(case, self.project, store, self.token)
        self.assertEqual(code, case.exit_code, out)
        why = golden_bench.check_golden(case, golden_bench.scrub(out, golden_bench.replacements_of(self.project, store)))
        self.assertIsNone(why, why)

    def test_no_golden_holds_a_path_of_this_machine(self):
        for golden in sorted(golden_bench.GOLDEN_DIR.iterdir()):
            text = golden.read_text()
            for path in (str(Path.home()), "/Users/", tempfile.gettempdir(), str(golden_bench.ROOT)):
                self.assertNotIn(path, text, golden.name)

    def test_every_golden_has_its_case(self):
        written = {golden.name for golden in golden_bench.GOLDEN_DIR.iterdir()}
        self.assertEqual(written, {case.golden for case in golden_bench.CASES})

    def test_every_item_in_every_golden_has_a_listed_code(self):
        # P433: look.py and deploy.py write a code in each problem and each unchecked item (look-ok and the dry run have none)
        items = [(golden.name, item) for pattern in ("look-*.json", "deploy-*.json")
                 for golden in sorted(golden_bench.GOLDEN_DIR.glob(pattern))
                 for key in ("problems", "unchecked") for item in json.loads(golden.read_text())[key]]
        self.assertTrue(items, "no golden holds an item, so the test would pass for nothing")
        self.assertEqual([name for name, item in items if item.get("code") not in {**board_codes.CODES, **codes.CODES}], [])

    def test_the_token_ends_in_the_image_hash(self):
        # The goldens print the image half as <image>, so this pins it: the first 4 hex of the image's sha256.
        image = next(self.project.glob("sim/*.bin"))
        self.assertTrue(self.token.endswith("-" + hashlib.sha256(image.read_bytes()).hexdigest()[:4]), self.token)


@needs_littlefs
class ThePrintedDeployLineTest(unittest.TestCase):
    """P463: with no simulation, the line deploy.py prints, run in a new shell with no SPARK_HOME, reaches the same
    gate. The store's MicroPython build is all it needs, and only the line's own SPARK_HOME gives it."""

    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.project = golden_bench.build_project(self.folder)
        self.store = self.folder / "the store"
        (self.store / "downloads").mkdir(parents=True)
        lists = tools.merged(self.project)["tools"]
        build = boards.get(self.project, "micropython_port", golden_bench.BOARD_ID)
        entry = next(entry for entry in lists.values() if entry.get("micropython_port") == build)
        (self.store / "downloads" / entry["file"]).write_bytes(fake_interpreter())
        for image in self.project.glob("sim/*.bin"):
            image.unlink()

    def child(self, script, *argv, env=None):
        env = env or golden_bench.child_env(self.store, "s3-flash-id-16mb.txt", "mpremote-devs-one.txt")
        return subprocess.run([sys.executable, str(golden_bench.ROOT / "scripts" / script), *argv], cwd=str(self.project),
                              env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=golden_bench.RUN_TIMEOUT_S)

    def printed_line(self):
        self.assertEqual(self.child("flash_image.py", "--project", str(self.project), "--files", "firmware", "-o",
                                    "sim/flash-with-firmware.bin").returncode, 0)
        looked = self.child("look.py", "--project", str(self.project), "--no-simulation", "--json")
        token = json.loads(looked.stdout)["data"]["token"]
        self.assertTrue(token, looked.stdout)
        deployed = self.child("deploy.py", "--project", str(self.project), "--no-simulation", "--json", "--token", token)
        self.assertEqual(deployed.returncode, 2, deployed.stdout)
        return json.loads(deployed.stdout)["data"]["run_in_terminal"]

    def prefix(self):
        return "SPARK_HOME=%s " % shlex.quote(str(self.store.resolve()))

    def run_in_a_new_shell(self, line):
        """(exit code, stderr) of `line` in sh with no SPARK_HOME and an empty home, as a person's new terminal window has."""
        env = golden_bench.child_env(self.store, "s3-flash-id-16mb.txt", "mpremote-devs-one.txt")
        del env["SPARK_HOME"]
        env["HOME"] = tempfile.mkdtemp(dir=self.folder)
        env["PYTHONUSERBASE"] = site.getuserbase()  # pip --user packages live under the real home, which this shell has not
        env["PATH"] = os.pathsep.join([str(Path(sys.executable).parent), env.get("PATH", "")])
        done = subprocess.run(["sh", "-c", line], cwd=self.folder, env=env, stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, timeout=golden_bench.RUN_TIMEOUT_S)
        return done.returncode, done.stderr

    def test_the_line_starts_with_the_store_and_reaches_the_gate_in_a_new_shell(self):
        line = self.printed_line()
        self.assertTrue(line.startswith(self.prefix()), line)
        code, said = self.run_in_a_new_shell(line)
        self.assertEqual(code, 2, said)
        self.assertIn("no terminal to ask you in", said)

    def test_the_same_line_without_its_store_stops_at_the_missing_build(self):
        line = self.printed_line()
        code, said = self.run_in_a_new_shell(line[len(self.prefix()):])
        self.assertEqual(code, 2, said)
        self.assertIn("not installed", said)
        self.assertNotIn("no terminal to ask you in", said)


for _case in golden_bench.CASES:
    setattr(BenchGoldenTest, "test_" + _case.golden.replace("-", "_").replace(".", "_"),
            lambda self, case=_case: self.run_case(case))


if __name__ == "__main__":
    unittest.main()
