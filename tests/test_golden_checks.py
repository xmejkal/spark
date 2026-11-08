"""P687 (#925, W6-C1): what the six check CLIs print today stays what they print, so the checks move breaks nothing. No
child reaches the network: GhShimGuardTest proves the guard, and ChecksGoldenTest runs no Case unless the gh a child
finds is the shim."""

import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

import golden_bench  # noqa: E402
import golden_checks  # noqa: E402
import golden_firmware  # noqa: E402


def spark_cache():
    """{name: bytes} of spark's own kept headers, which no golden run may write."""
    return {path.name: path.read_bytes() for path in sorted(golden_checks.SPARK_CACHE.iterdir())}


def restore(name, value):
    """Put `name` back in this process's environment as it was: `value`, or gone when None."""
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


class GhShimGuardTest(unittest.TestCase):
    """The guard: a child's PATH is the shim's folder alone, its gh is the fake, its proxies are a closed port, and it
    carries no Wokwi token."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp())
        cls.bin = golden_checks.name_the_gh(cls.folder)

    def env(self):
        return golden_checks.child_env(self.folder / "store", self.bin)

    def in_parent(self, **values):
        """Set `values` in this process's environment, which a child's is made from, until the test ends."""
        for name, value in values.items():
            self.addCleanup(restore, name, os.environ.get(name))
            os.environ[name] = value

    def run_gh(self, **told):
        return subprocess.run(["gh", "api", "repos/x/y/contents/z", "--jq", ".content"], env=dict(self.env(), **told),
                              stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              timeout=golden_bench.RUN_TIMEOUT_S)

    def test_the_child_path_is_the_shims_folder_alone(self):
        self.assertEqual(self.env()["PATH"], str(self.bin))

    def test_the_gh_found_is_the_shim(self):
        self.assertEqual(shutil.which("gh", path=self.env()["PATH"]), str(self.bin / "gh"))

    def test_every_proxy_is_a_closed_port_and_nothing_bypasses_it(self):
        self.in_parent(no_proxy="*", NO_PROXY="*")  # a parent that lets every host bypass the proxy
        env = self.env()
        self.assertEqual({name: env.get(name) for name in golden_checks.PROXIES},
                         dict.fromkeys(golden_checks.PROXIES, golden_checks.CLOSED_PROXY))
        self.assertFalse({"no_proxy", "NO_PROXY"} & set(env))

    def test_no_child_carries_a_wokwi_token(self):
        self.in_parent(WOKWI_CLI_TOKEN="wok_a-pretend-token")
        self.assertNotIn("WOKWI_CLI_TOKEN", self.env())

    def test_the_shim_runs_the_fake_gh(self):
        done = self.run_gh()
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(base64.b64decode(done.stdout).decode(), golden_checks.FAKE_GH_HEADER.read_text())

    def test_the_fake_gh_changes_a_pin_when_told(self):
        done = self.run_gh(FAKE_GH_FIND="A0 = 4;", FAKE_GH_REPLACE="A0 = 5;")
        self.assertIn("A0 = 5;", base64.b64decode(done.stdout).decode())

    def test_run_script_gives_the_child_the_env_it_is_given(self):
        # A dropped env would give a live Case the parent's PATH, and the real gh. The marker is the fake's exit code.
        project = Path(tempfile.mkdtemp(dir=self.folder))
        case = golden_firmware.Case("marker.txt", "../tests/fake_gh.py", [], 3)
        code, text = golden_firmware.run_script(case, project, self.folder / "store", dict(self.env(), FAKE_GH_EXIT="3"))
        self.assertEqual(code, 3, text)

    def test_the_fake_gh_fails_when_told(self):
        done = self.run_gh(FAKE_GH_EXIT="1")
        self.assertEqual((done.returncode, done.stdout), (1, ""))
        self.assertIn("HTTP 404", done.stderr)


class ChecksOpTest(unittest.TestCase):
    """Each golden's name starts with its op, the script's name with dashes, so an accept run names it."""

    def test_each_golden_starts_with_its_op(self):
        for case in golden_checks.CASES:
            self.assertTrue(case.golden.startswith(golden_bench.op_of(case) + "-"), case.golden)


class ChecksGoldenTest(unittest.TestCase):
    """Each Case of golden_checks.CASES is one test, named after its golden, run in its own copy of one project built
    for the class: the button-light fixture after init_project.py."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp())
        cls.bin = golden_checks.name_the_gh(cls.folder)
        # The guard holds before any child runs. A raise, not an assert, which python -O strips.
        if shutil.which("gh", path=golden_checks.child_env(cls.folder / "store", cls.bin)["PATH"]) != str(cls.bin / "gh"):
            raise RuntimeError("the gh a child finds is not the shim, so no checks golden runs")
        cls.project = golden_checks.build_project(cls.folder, cls.bin)
        cls.cache = spark_cache()

    def run_case(self, case):
        work = Path(tempfile.mkdtemp(dir=self.folder))
        project, store = work / self.project.name, work / "store"
        shutil.copytree(self.project, project)
        code, text = golden_firmware.run_script(case, project, store, golden_checks.child_env(store, self.bin))
        self.assertEqual(code, case.exit_code, text)
        self.assertEqual(spark_cache(), self.cache, "a golden run wrote into spark's own cache")
        scrubbed = golden_bench.scrub(text, golden_bench.replacements_of(project, store))
        self.assertIsNone(golden_bench.check_golden(case, scrubbed, golden_dir=golden_checks.GOLDEN_DIR))

    def test_the_floating_rules_drop_only_the_firmware_pull_up(self):
        rules = json.loads((self.project / ".spark" / "rules.json").read_text())
        floating = json.loads((self.project / golden_checks.FLOATING_RULES).read_text())
        self.assertTrue(rules["pulled_by_firmware"])
        self.assertEqual(floating, dict(rules, pulled_by_firmware=[]))

    def test_no_golden_holds_a_path_of_this_machine(self):
        for golden in sorted(golden_checks.GOLDEN_DIR.iterdir()):
            text = golden.read_text()
            for path in (str(Path.home()), "/Users/", tempfile.gettempdir(), str(golden_bench.ROOT)):
                self.assertNotIn(path, text, golden.name)

    def test_every_golden_has_its_case(self):
        written = {golden.name for golden in golden_checks.GOLDEN_DIR.iterdir()}
        self.assertEqual(written, {case.golden for case in golden_checks.CASES})


for _case in golden_checks.CASES:
    setattr(ChecksGoldenTest, "test_" + _case.golden.replace("-", "_").replace(".", "_"),
            lambda self, case=_case: self.run_case(case))


if __name__ == "__main__":
    unittest.main()
