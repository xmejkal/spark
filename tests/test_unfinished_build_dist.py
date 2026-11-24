"""P816 (#1168): a `check_spine.py --keep .` build that did not finish leaves no earlier `dist/` behind, since every
check reads it, and says so in text and in --json. A build that ends `problems` keeps the `dist/` it made. Each test
runs check_spine.py as a child in golden_design's project (the button-light fixture, which holds an earlier
dist/board/), with the fake tsci, as the goldens check-spine-ok-keep, -problems-build, -could-not-run-no-tsci and
-could-not-run-requirements set it up."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

import golden_design  # noqa: E402
from golden_design import Case  # noqa: E402
from golden_firmware import STDERR_MARK  # noqa: E402

KEEP = [golden_design.REQUIREMENTS, "--keep", "."]
NO_TSCI = ((".spark/tools.json", json.dumps({"tscircuit": {"kind": "path", "exe": "tsci", "also": [], "needs": []}})),)
REFUSED = ((golden_design.REQUIREMENTS, "{not json"),)
ERRORED = {"FAKE_TSCI_CIRCUIT": golden_design.FAKES_TOKEN + "/" + golden_design.ERRORED_CIRCUIT}
WHY = "the build did not finish in this run, and it described an earlier build"


class UnfinishedBuildDistTest(unittest.TestCase):
    """What an earlier build's `dist/` becomes after a `--keep .` build in the project, by how the build ended."""

    @classmethod
    def setUpClass(cls):
        cls.folder = Path(tempfile.mkdtemp())
        cls.shims = golden_design.make_fakes(cls.folder)
        cls.project = golden_design.build_project(cls.folder, cls.shims)

    def run_build(self, plant=(), env=None, json_out=True, without_dist=False, before=None):
        """check_spine.py --keep . in a copy of the project: its exit code, the project, and its --json report (None
        without --json, then the whole text)."""
        case = Case("check-spine", "check_spine.py", KEEP + (["--json"] if json_out else []), None, plant, env or {})
        work = Path(tempfile.mkdtemp(dir=self.folder))
        project = golden_design.copy_project(case, self.project, work)
        if without_dist:
            shutil.rmtree(project / "dist")
        if before:
            before(project)
        code, text = golden_design.run_case(case, project, work / "store", self.shims)
        return code, project, json.loads(text.split(STDERR_MARK)[0]) if json_out else text

    def dist_entries(self, report):
        return [entry for entry in report["kept"] if entry["file"] == "dist"]

    def test_a_build_that_did_not_finish_removes_the_earlier_dist_and_says_so(self):
        code, project, report = self.run_build(NO_TSCI)
        self.assertEqual(code, 2)
        self.assertFalse((project / "dist").exists())
        self.assertEqual([(entry["did"], entry["why"]) for entry in self.dist_entries(report)], [("removed", WHY)])
        code, _, text = self.run_build(NO_TSCI, json_out=False)
        self.assertEqual(code, 2)
        self.assertIn("removed dist: " + WHY, [line.strip() for line in text.splitlines()])

    def test_a_refused_requirements_file_removes_the_earlier_dist(self):
        code, project, report = self.run_build(REFUSED)
        self.assertEqual(code, 2)
        self.assertFalse((project / "dist").exists())
        refused = next(stage["detail"] for stage in report["stages"] if stage["name"] == "requirements")
        self.assertEqual([(entry["did"], entry["why"]) for entry in self.dist_entries(report)],
                         [("removed", refused + ", and it described an earlier build")])

    def test_a_build_with_problems_keeps_the_dist_it_made(self):
        code, project, report = self.run_build(env=ERRORED)
        self.assertEqual(code, 1)
        self.assertEqual([entry["did"] for entry in self.dist_entries(report)], ["wrote"])
        built = json.loads((self.folder / golden_design.ERRORED_CIRCUIT).read_text())
        self.assertEqual(json.loads((project / "dist" / "board" / "circuit.json").read_text()), built)

    def test_no_earlier_dist_no_entry(self):
        code, project, report = self.run_build(NO_TSCI, without_dist=True)
        self.assertEqual(code, 2)
        self.assertEqual(self.dist_entries(report), [])
        self.assertFalse((project / "dist").exists())

    @unittest.skipIf(os.geteuid() == 0, "root removes a read-only folder's files")
    def test_a_dist_that_cannot_be_removed_is_not_kept_and_the_rest_is_written(self):
        # Council C: a read-only dist/board stops the removal; the build still writes the pin map and its record.
        def read_only(project):
            (project / "dist" / "board").chmod(0o555)
            self.addCleanup((project / "dist" / "board").chmod, 0o755)
        code, project, report = self.run_build(NO_TSCI, before=read_only)
        self.assertEqual(code, 2)
        self.assertEqual([entry["did"] for entry in self.dist_entries(report)], ["not kept"])
        self.assertTrue((project / "dist" / "board" / "circuit.json").exists())
        did = {entry["file"]: entry["did"] for entry in report["kept"]}
        self.assertEqual((did.get("firmware/pins.py"), did.get(".spark/build.json")), ("wrote", "wrote"))


if __name__ == "__main__":
    unittest.main()
