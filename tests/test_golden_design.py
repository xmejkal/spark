"""P699 (#946, W6-D1): what the five design and build CLIs print today, and what `check_spine.py --keep` writes, stays
what they print and write, so the design codes and moves break nothing. No golden runs a real tool: DesignGuardTest
proves the guard, and DesignGoldenTest runs no Case unless the board engine and the converter a child finds are the
fakes, and no real tool can be found on its PATH."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

import golden_bench  # noqa: E402
import golden_checks  # noqa: E402
import golden_design  # noqa: E402
import tools  # noqa: E402

#: The real tools a design or build CLI could reach, none of which a golden child may find.
REAL_TOOLS = ("tsci", "bun", "node", "npm", "wokwi-cli", "gh")
ROLES = {"board-engine": golden_design.TSCI, "diagram-converter": golden_design.CONVERTER}


def guard_holds(project, shims):
    """None when a child of `project` finds the two fakes in `shims` and none of REAL_TOOLS, else what it found."""
    path = golden_checks.child_env(Path(shims).parent / "guard-store", shims)["PATH"]
    try:
        with mock.patch.dict(os.environ, {"PATH": path}):
            found = {role: tools.find(role, project, personal=Path(shims) / "no-tools.json").command for role in ROLES}
    except tools.ToolProblem as refused:
        return "a fake is not found: %s" % refused
    if found != {role: [str(Path(shims) / exe)] for role, exe in ROLES.items()}:
        return "the tools found are not the fakes: %r" % found
    real = [name for name in REAL_TOOLS if shutil.which(name, path=path)]
    return "a real tool is on a child's PATH: %s" % real if real else None


class DesignGuardTest(unittest.TestCase):
    """The guard: a child's PATH is the fakes' folder alone, the project's tools list names the two fakes and nothing
    else to look for, and no real tool is found."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp())
        cls.shims = golden_design.make_fakes(cls.folder)
        cls.project = cls.folder / "project"
        (cls.project / ".spark").mkdir(parents=True)
        (cls.project / ".spark" / "tools.json").write_text(json.dumps(golden_design.fakes_named(cls.shims)))

    def env(self):
        return golden_checks.child_env(self.folder / "store", self.shims)

    def test_the_child_path_is_the_fakes_folder_alone_with_no_token(self):
        with mock.patch.dict(os.environ, {"WOKWI_CLI_TOKEN": "wok_a-pretend-token"}):
            env = self.env()
        self.assertEqual(env["PATH"], str(self.shims))
        self.assertNotIn("WOKWI_CLI_TOKEN", env)
        self.assertEqual({name: env[name] for name in golden_checks.PROXIES},
                         dict.fromkeys(golden_checks.PROXIES, golden_checks.CLOSED_PROXY))

    def test_the_board_engine_and_the_converter_found_are_the_fakes(self):
        self.assertIsNone(guard_holds(self.project, self.shims))

    def test_no_real_tool_is_found(self):
        with mock.patch.dict(os.environ, {"PATH": self.env()["PATH"]}):
            for role in ("ts-runtime", "js-runtime", "simulator"):
                with self.assertRaises(tools.ToolProblem, msg=role):
                    tools.find(role, self.project, personal=self.folder / "no-tools.json")
        self.assertEqual([name for name in REAL_TOOLS if shutil.which(name, path=self.env()["PATH"])], [])

    def test_without_needs_the_fakes_are_refused(self):
        # tools.find looks for bun and node first: the reason the project's list says "needs": [] (P698 row 2).
        project = self.folder / "needs"
        named = golden_design.fakes_named(self.shims)
        for entry in named.values():
            entry.pop("needs", None)
        (project / ".spark").mkdir(parents=True)
        (project / ".spark" / "tools.json").write_text(json.dumps(named))
        self.assertIn("needs bun", guard_holds(project, self.shims))

    def test_the_fake_tsci_answers_version_and_refuses_export(self):
        tsci = str(self.shims / golden_design.TSCI)
        version = subprocess.run([tsci, "--version"], env=self.env(), capture_output=True, text=True)
        self.assertEqual(version.stdout, "0.0.0-fake\n")
        export = subprocess.run([tsci, "export", "circuit.json"], env=self.env(), capture_output=True, text=True)
        self.assertEqual(export.returncode, 1)

    def test_the_fake_converter_writes_its_diagram(self):
        out = self.folder / "diagram.json"
        done = subprocess.run([str(self.shims / golden_design.CONVERTER), "--circuit", "c.json", "--out", str(out)],
                              env=self.env(), capture_output=True, text=True, timeout=golden_bench.RUN_TIMEOUT_S)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue(json.loads(out.read_text())["connections"])


class DesignOpTest(unittest.TestCase):
    """Each golden's name starts with its op, the script's name with dashes, so an accept run names it."""

    def test_each_golden_starts_with_its_op(self):
        for case in golden_design.CASES:
            self.assertTrue(case.golden.startswith(golden_bench.op_of(case) + "-"), case.golden)


class DesignGoldenTest(unittest.TestCase):
    """Each Case of golden_design.CASES is one test, named after its golden, run in its own copy of one project built
    for the class: the button-light fixture after init_project.py, whose tools list names the fakes."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp())
        cls.shims = golden_design.make_fakes(cls.folder)
        cls.project = golden_design.build_project(cls.folder, cls.shims)
        # The guard holds before any child runs. A raise, not an assert, which python -O strips.
        broken = guard_holds(cls.project, cls.shims)
        if broken:
            raise RuntimeError("%s, so no design golden runs" % broken)

    def run_case(self, case):
        work = Path(tempfile.mkdtemp(dir=self.folder))
        store = work / "store"
        project = golden_design.copy_project(case, self.project, work)
        code, text = golden_design.run_case(case, project, store, self.shims)
        self.assertEqual(code, case.exit_code, text)
        scrubbed = golden_bench.scrub(text, golden_design.places(project, store, self.shims))
        self.assertIsNone(golden_bench.check_golden(case, scrubbed, golden_dir=golden_design.GOLDEN_DIR))

    def test_the_fake_tsci_built_the_board(self):
        # A Case passes on the fake's build alone: the marker it touches is there after the run, and was not before.
        marker = self.folder / golden_design.BUILT_MARKER
        marker.unlink(missing_ok=True)
        self.run_case(next(case for case in golden_design.CASES if case.golden == "check-spine-ok.json"))
        self.assertTrue(marker.is_file())

    def test_no_golden_holds_a_path_of_this_machine(self):
        for golden in sorted(golden_design.GOLDEN_DIR.iterdir()):
            text = golden.read_text()
            for path in (str(Path.home()), "/Users/", tempfile.gettempdir(), str(golden_bench.ROOT)):
                self.assertNotIn(path, text, golden.name)

    def test_every_golden_has_its_case(self):
        written = {golden.name for golden in golden_design.GOLDEN_DIR.iterdir()}
        self.assertEqual(written, {case.golden for case in golden_design.CASES})


for _case in golden_design.CASES:
    setattr(DesignGoldenTest, "test_" + _case.golden.replace("-", "_").replace(".", "_"),
            lambda self, case=_case: self.run_case(case))


if __name__ == "__main__":
    unittest.main()
