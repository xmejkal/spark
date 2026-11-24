"""P816 (#1168): a `check_spine.py --keep .` build that did not finish keeps the earlier `dist/`, which every check
reads, and names it: one `left alone` entry in text and in --json, `dist_written: false` in `.spark/build.json`, and a
`circuit` line in check_all's `resolved`. A build that ends `problems` writes its own `dist/` and names nothing. Each
test runs check_spine.py (and check_all.py) as a child in golden_design's project (the button-light fixture, which
holds an earlier dist/board/), with the fake tsci, as the goldens check-spine-ok-keep, -problems-build,
-could-not-run-no-tsci and -could-not-run-requirements set it up.

P1088 (#1598): a work `dist/` is kept only when it holds `dist/board/circuit.json`, the file the build stage itself tests,
and then it replaces the earlier `dist/` whole, staged beside it: a copy that fails leaves the earlier `dist/` as it was,
with one `not kept` entry that the record and check_all agree with."""

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
#: A tsci that makes dist/board/ and no circuit.json in it (its cp finds no such file): a build that stopped midway.
PARTIAL = {"FAKE_TSCI_CIRCUIT": golden_design.FAKES_TOKEN + "/no-such-circuit.json"}
#: A tsci whose dist/ holds its circuit.json and a link to nothing, so the copy of dist/ fails midway.
DANGLING = {"FAKE_TSCI_DANGLING": "1"}
#: A file of the person's at the name the staged copy would take.
IN_THE_WAY = (("dist.new", "mine\n"),)


def files_of(folder):
    """Every file under `folder`, by its path relative to it, with its bytes."""
    return {str(each.relative_to(folder)): each.read_bytes() for each in sorted(Path(folder).rglob("*")) if each.is_file()}


def plant_an_old_board(project):
    """A board of an earlier layout in the earlier dist/, which no entry names."""
    (project / "dist" / "old").mkdir()
    (project / "dist" / "old" / "circuit.json").write_text("[]")


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
        code, project, report = self.run_build(NO_TSCI, before=draw)
        self.assertEqual(code, 2)
        for name in PICTURES:
            self.assertEqual((project / "dist" / "board" / name).read_text(), "<svg>" + name + "</svg>")
        self.assertEqual(len(self.dist_entries(report)), 1)
        self.assertEqual(self.dist_entries(report)[0]["did"], "left alone")

    def test_check_all_names_an_earlier_dist(self):
        _, project, _ = self.run_build(NO_TSCI)
        line = "circuit      the last build, %s, did not write dist/: build again with check_spine.py --keep before you rely on this circuit" % self.record(project)["at"]
        _, report = self.check_all(project)
        self.assertIn(line, report["resolved"])
        _, text = self.check_all(project, json_out=False)
        self.assertIn(line, [one.strip() for one in text.splitlines()])

    def test_check_all_names_nothing_after_a_build_that_wrote_dist(self):
        _, project, _ = self.run_build()
        self.assertIs(self.record(project)["dist_written"], True)
        _, report = self.check_all(project)
        self.assertEqual([one for one in report["resolved"] if "did not write dist/" in one], [])


    def test_a_work_dist_without_a_circuit_keeps_the_earlier_dist_and_names_it(self):
        before = {}

        def remember(project):
            before["circuit"] = (project / "dist" / "board" / "circuit.json").read_bytes()
        code, project, report = self.run_build(env=PARTIAL, before=remember)
        self.assertEqual(code, 2)
        self.assertEqual(next(stage["code"] for stage in report["stages"] if stage["name"] == "build"), "tool_cannot_build")
        self.assertEqual((project / "dist" / "board" / "circuit.json").read_bytes(), before["circuit"])
        self.assertEqual([(entry["did"], entry["why"]) for entry in self.dist_entries(report)], [("left alone", WHY)])
        self.assertIs(self.record(project)["dist_written"], False)
        line = "circuit      the last build, %s, did not write dist/: build again with check_spine.py --keep before you rely on this circuit" % self.record(project)["at"]
        _, checked = self.check_all(project)
        self.assertIn(line, checked["resolved"])
        code, _, text = self.run_build(env=PARTIAL, json_out=False)
        self.assertEqual(code, 2)
        self.assertIn("left alone: dist (%s)" % WHY, [one.strip() for one in text.splitlines()])

    def test_a_work_dist_without_a_circuit_and_no_earlier_dist_makes_none(self):
        code, project, report = self.run_build(env=PARTIAL, without_dist=True)
        self.assertEqual(code, 2)
        self.assertFalse((project / "dist").exists())
        self.assertEqual(self.dist_entries(report), [])
        self.assertIs(self.record(project)["dist_written"], False)

    def test_a_build_with_problems_replaces_the_earlier_dist_whole(self):
        code, project, report = self.run_build(env=ERRORED, before=plant_an_old_board)
        self.assertEqual(code, 1)
        self.assertEqual([entry["did"] for entry in self.dist_entries(report)], ["wrote"])
        self.assertFalse((project / "dist" / "board" / "built-from.json").exists())
        self.assertFalse((project / "dist" / "old").exists())
        built = json.loads((self.folder / golden_design.ERRORED_CIRCUIT).read_text())
        self.assertEqual(json.loads((project / "dist" / "board" / "circuit.json").read_text()), built)
        self.assertIs(self.record(project)["dist_written"], True)
        self.assertEqual(sorted(each.name for each in project.iterdir() if each.name.startswith("dist")), ["dist"])

    def test_a_finished_build_replaces_the_earlier_dist_whole(self):
        code, project, report = self.run_build(before=plant_an_old_board)
        self.assertEqual(code, 0)
        self.assertEqual([entry["did"] for entry in self.dist_entries(report)], ["wrote"])
        self.assertFalse((project / "dist" / "old").exists())
        self.assertTrue((project / "dist" / "board" / "built-from.json").is_file())
        self.assertEqual(sorted(each.name for each in project.iterdir() if each.name.startswith("dist")), ["dist"])

    def test_a_finished_build_whose_dist_cannot_be_copied_says_not_kept_once(self):
        code, project, report = self.run_build(env=DANGLING)
        entries = self.dist_entries(report)
        self.assertEqual([entry["did"] for entry in entries], ["not kept"], entries)
        self.assertIs(self.record(project)["dist_written"], False)
        line = "circuit      the last build, %s, did not write dist/: build again with check_spine.py --keep before you rely on this circuit" % self.record(project)["at"]
        _, checked = self.check_all(project)
        self.assertIn(line, checked["resolved"])

    def test_an_unfinished_build_whose_dist_cannot_be_copied_says_not_kept_once(self):
        code, project, report = self.run_build(env=dict(ERRORED, **DANGLING))
        self.assertEqual(code, 1)
        self.assertEqual([entry["did"] for entry in self.dist_entries(report)], ["not kept"])
        self.assertIs(self.record(project)["dist_written"], False)

    def test_a_copy_that_fails_leaves_the_earlier_dist_whole(self):
        # the council's condition: the copy is staged beside dist/, so a failed one never touches the earlier board
        before = {}

        def remember(project):
            before["dist"] = files_of(project / "dist")
        code, project, report = self.run_build(env=dict(ERRORED, **DANGLING), before=remember)
        self.assertEqual(code, 1)
        self.assertIn("dist/board/built-from.json", ["dist/" + name for name in before["dist"]])
        self.assertEqual(files_of(project / "dist"), before["dist"])
        self.assertEqual(sorted(each.name for each in project.iterdir() if each.name.startswith("dist")), ["dist"])

    def test_a_file_at_the_stage_name_is_left_and_named(self):
        code, project, report = self.run_build(IN_THE_WAY)
        entries = self.dist_entries(report)
        self.assertEqual([entry["did"] for entry in entries], ["not kept"])
        self.assertIn("dist.new is in the way: delete it if it is not yours", entries[0]["why"])
        self.assertEqual((project / "dist.new").read_text(), "mine\n")
        self.assertIs(self.record(project)["dist_written"], False)


if __name__ == "__main__":
    unittest.main()
