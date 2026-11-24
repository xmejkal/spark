"""P816 (#1168): a `check_spine.py --keep .` build that did not finish keeps the earlier `dist/`, which every check
reads, and names it: one `left alone` entry in text and in --json, `dist_written: false` in `.spark/build.json`, and a
`circuit` line in check_all's `resolved`. A build that ends `problems` writes its own `dist/` and names nothing. Each
test runs check_spine.py (and check_all.py) as a child in golden_design's project (the button-light fixture, which
holds an earlier dist/board/), with the fake tsci, as the goldens check-spine-ok-keep, -problems-build,
-could-not-run-no-tsci and -could-not-run-requirements set it up."""

import json
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
EARLIER = ", so it is an earlier build's, which every check reads"
WHY = "the build did not finish in this run" + EARLIER
PICTURES = ("schematic.svg", "pcb.svg")


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

    def record(self, project):
        return json.loads((project / ".spark" / "build.json").read_text())

    def check_all(self, project, json_out=True):
        """check_all.py --project . in `project`, with the store the build used: its exit code and its --json report (the
        text without --json)."""
        case = Case("check-all", "check_all.py", ["--project", golden_design.golden_checks.PROJECT] + (["--json"] if json_out else []), None)
        code, text = golden_design.run_case(case, project, project.parent / "store", self.shims)
        return code, json.loads(text.split(STDERR_MARK)[0]) if json_out else text

    def test_a_build_that_did_not_finish_keeps_the_earlier_dist_and_names_it(self):
        before = {}

        def remember(project):
            before["circuit"] = (project / "dist" / "board" / "circuit.json").read_bytes()
        code, project, report = self.run_build(NO_TSCI, before=remember)
        self.assertEqual(code, 2)
        self.assertEqual((project / "dist" / "board" / "circuit.json").read_bytes(), before["circuit"])
        self.assertEqual([(entry["did"], entry["why"]) for entry in self.dist_entries(report)], [("left alone", WHY)])
        self.assertIs(self.record(project)["dist_written"], False)
        code, _, text = self.run_build(NO_TSCI, json_out=False)
        self.assertEqual(code, 2)
        self.assertIn("left alone: dist (%s)" % WHY, [line.strip() for line in text.splitlines()])

    def test_a_refused_requirements_file_keeps_the_earlier_dist_and_names_it(self):
        code, project, report = self.run_build(REFUSED)
        self.assertEqual(code, 2)
        self.assertTrue((project / "dist" / "board" / "circuit.json").exists())
        refused = next(stage["detail"] for stage in report["stages"] if stage["name"] == "requirements")
        self.assertEqual([(entry["did"], entry["why"]) for entry in self.dist_entries(report)],
                         [("left alone", refused + EARLIER)])

    def test_a_build_with_problems_writes_its_dist_and_names_nothing(self):
        code, project, report = self.run_build(env=ERRORED)
        self.assertEqual(code, 1)
        self.assertEqual([entry["did"] for entry in self.dist_entries(report)], ["wrote"])
        built = json.loads((self.folder / golden_design.ERRORED_CIRCUIT).read_text())
        self.assertEqual(json.loads((project / "dist" / "board" / "circuit.json").read_text()), built)
        self.assertIs(self.record(project)["dist_written"], True)

    def test_no_earlier_dist_no_entry(self):
        code, project, report = self.run_build(NO_TSCI, without_dist=True)
        self.assertEqual(code, 2)
        self.assertEqual(self.dist_entries(report), [])
        self.assertFalse((project / "dist").exists())
        self.assertIs(self.record(project)["dist_written"], False)

    def test_an_unfinished_build_keeps_the_pictures_of_the_earlier_dist(self):
        # Council 2: the pictures show the same earlier board, and nothing is deleted
        def draw(project):
            for name in PICTURES:
                (project / "dist" / "board" / name).write_text("<svg>" + name + "</svg>")
        code, project, _ = self.run_build(NO_TSCI, before=draw)
        self.assertEqual(code, 2)
        for name in PICTURES:
            self.assertEqual((project / "dist" / "board" / name).read_text(), "<svg>" + name + "</svg>")

    def test_check_all_names_an_earlier_dist(self):
        _, project, _ = self.run_build(NO_TSCI)
        line = "circuit      the last build, %s, did not write dist/" % self.record(project)["at"]
        _, report = self.check_all(project)
        self.assertIn(line, report["resolved"])
        _, text = self.check_all(project, json_out=False)
        self.assertIn(line, [one.strip() for one in text.splitlines()])

    def test_check_all_names_nothing_after_a_build_that_wrote_dist(self):
        _, project, _ = self.run_build()
        self.assertIs(self.record(project)["dist_written"], True)
        _, report = self.check_all(project)
        self.assertEqual([one for one in report["resolved"] if "did not write dist/" in one], [])


if __name__ == "__main__":
    unittest.main()
