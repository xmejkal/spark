"""P816 (#1168): a `check_spine.py --keep .` build that did not finish keeps the earlier `dist/`, which every check
reads, and names it: one `left alone` entry in text and in --json, `dist_written: false` in `.spark/build.json`, and a
`circuit` line in check_all's `resolved`. A build that ends `problems` writes its own `dist/` and names nothing. Each
test runs check_spine.py (and check_all.py) as a child in golden_design's project (the button-light fixture, which
holds an earlier dist/board/), with the fake tsci, as the goldens check-spine-ok-keep, -problems-build,
-could-not-run-no-tsci and -could-not-run-requirements set it up.

P1088 (#1598): a work `dist/` is kept only when it holds `dist/board/circuit.json`, the file the build stage itself tests,
and then it replaces the earlier `dist/` whole, staged beside it: a copy that fails leaves the earlier `dist/` as it was,
with one `not kept` entry that the record and check_all agree with, and the earlier pictures stay. A name the stage or
the aside needs that is taken, or a `dist/` that is a link, stops the copy and is named; an earlier `dist/` set aside
that cannot be removed is named too. `ReplaceWholeTest` runs `replace_whole` itself for an error or a Ctrl-C midway.

P1093 (#1608) and P1095 (#1613): a build that kept no `dist/` of its own (it did not finish, or its copy failed) leaves
the earlier `breadboard.md` as one `left alone` entry, an earlier build's, so P1044's witness stays and `flow.py show`
and `flow.py page` still warn; a copy that failed writes no `built-from.json` or sheet beside the earlier circuit. The
reference design (no requirements file) records its build too, with `requirements: null`, and names an earlier `dist/`
it did not replace."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import golden_design  # noqa: E402
from spark.build.build_record import replace_whole  # noqa: E402
from golden_design import Case  # noqa: E402
from golden_firmware import STDERR_MARK  # noqa: E402
from spark.flow.flow_codes import WIRED_BUILD_MESSAGE, WIRED_SHEET_MESSAGE  # noqa: E402
from spark.flow.wired_board import day_of  # noqa: E402

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
#: What an earlier dist/ set aside that cannot be removed says (P1088).
ASIDE_LEFT = "dist.old is spark's own earlier dist/, set aside for the new one, and it could not be removed: delete it before the next build"
#: The reference design built into the project (P1095): no requirements file, and what the fake tsci builds for it.
REFERENCE = ["--keep", "."]
REFERENCE_ENV = {"FAKE_TSCI_CIRCUIT": golden_design.FAKES_TOKEN + "/" + golden_design.REFERENCE_CIRCUIT}
#: An earlier build's wiring sheet, and its last change (18 Nov 2026), which P1044 reads as the witness.
SHEET, SHEET_TIME = "# an earlier build's sheet\n", 1795000000
#: The earlier build's mark in dist/board/built-from.json, which a copy that failed must not overwrite (P1095 comment 1).
MARKED = '{"requirements": "an earlier build"}\n'


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

    def run_build(self, plant=(), env=None, json_out=True, without_dist=False, before=None, args=KEEP):
        """check_spine.py `args` (--keep . with the requirements file) in a copy of the project: its exit code, the
        project, and its --json report (None without --json, then the whole text)."""
        case = Case("check-spine", "check_spine.py", args + (["--json"] if json_out else []), None, plant, env or {})
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

    def entry_of(self, report, name):
        """The one kept entry for the file `name`."""
        entries = [entry for entry in report["kept"] if entry["file"] == name]
        self.assertEqual(len(entries), 1, entries)
        return entries[0]

    def flow(self, project, *argv):
        """flow.py `argv` --project . in `project`, with the store the build used: its exit code and its stdout."""
        case = Case("flow", "flow.py", list(argv) + ["--project", golden_design.golden_checks.PROJECT], None)
        code, text = golden_design.run_case(case, project, project.parent / "store", self.shims)
        return code, text.split(STDERR_MARK)[0]

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
            for name in PICTURES:
                (project / "dist" / "board" / name).write_text("<svg>" + name + "</svg>")
            before["dist"] = files_of(project / "dist")
        code, project, report = self.run_build(env=dict(ERRORED, **DANGLING), before=remember)
        self.assertEqual(code, 1)
        self.assertIn("dist/board/built-from.json", ["dist/" + name for name in before["dist"]])
        for name in PICTURES:
            self.assertEqual((project / "dist" / "board" / name).read_text(), "<svg>" + name + "</svg>")
        self.assertEqual(files_of(project / "dist"), before["dist"])
        self.assertEqual(sorted(each.name for each in project.iterdir() if each.name.startswith("dist")), ["dist"])

    def test_a_file_at_the_stage_name_is_left_and_named(self):
        code, project, report = self.run_build(IN_THE_WAY)
        entries = self.dist_entries(report)
        self.assertEqual([entry["did"] for entry in entries], ["not kept"])
        self.assertIn("dist.new is in the way: delete it if it is not yours", entries[0]["why"])
        self.assertEqual((project / "dist.new").read_text(), "mine\n")
        self.assertIs(self.record(project)["dist_written"], False)

    def test_a_file_at_the_aside_name_is_left_and_named(self):
        code, project, report = self.run_build((("dist.old", "mine\n"),))
        entries = self.dist_entries(report)
        self.assertEqual([entry["did"] for entry in entries], ["not kept"])
        self.assertIn("dist.old is in the way: delete it if it is not yours", entries[0]["why"])
        self.assertEqual((project / "dist.old").read_text(), "mine\n")
        self.assertTrue((project / "dist" / "board" / "circuit.json").is_file())
        self.assertIs(self.record(project)["dist_written"], False)

    def test_a_dist_that_is_a_link_is_not_kept_and_untouched(self):
        before = {}

        def link(project):
            elsewhere = project.parent / "elsewhere"
            (project / "dist").rename(elsewhere)
            (project / "dist").symlink_to(elsewhere, target_is_directory=True)
            before["files"] = files_of(elsewhere)
        code, project, report = self.run_build(env=ERRORED, before=link)
        entries = self.dist_entries(report)
        self.assertEqual([entry["did"] for entry in entries], ["not kept"])
        self.assertIn("is a link, so spark does not replace it", entries[0]["why"])
        self.assertTrue((project / "dist").is_symlink())
        self.assertEqual(files_of(project.parent / "elsewhere"), before["files"])
        self.assertIs(self.record(project)["dist_written"], False)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root removes a read-only folder")
    def test_an_earlier_dist_that_cannot_be_removed_is_named(self):
        def lock(project):
            locked = project / "dist" / "locked"
            locked.mkdir()
            (locked / "x.json").write_text("[]")
            locked.chmod(0o555)
            for each in (locked, project / "dist.old" / "locked"):
                self.addCleanup(lambda folder=each: folder.is_dir() and folder.chmod(0o755))
        code, project, report = self.run_build(before=lock)
        self.assertEqual(code, 0)
        self.assertEqual([entry["did"] for entry in self.dist_entries(report)], ["wrote"])
        self.assertEqual([(entry["did"], entry["why"]) for entry in report["kept"] if entry["file"] == "dist.old"],
                         [("not kept", ASIDE_LEFT)])
        self.assertTrue((project / "dist.old" / "locked" / "x.json").is_file())
        self.assertFalse((project / "dist" / "locked").exists())
        self.assertIs(self.record(project)["dist_written"], True)

    # --- P1093 (#1608), P1095 (#1613) ---
    def plant_sheet(self, project):
        (project / "breadboard.md").write_text(SHEET)
        os.utime(project / "breadboard.md", (SHEET_TIME, SHEET_TIME))

    def test_a_failed_build_keeps_the_earlier_sheet_and_flow_still_warns(self):
        code, project, report = self.run_build(NO_TSCI, before=self.plant_sheet)
        self.assertEqual(code, 2)
        self.assertEqual((project / "breadboard.md").read_text(), SHEET)
        self.assertEqual((project / "breadboard.md").stat().st_mtime, SHEET_TIME)
        entry = self.entry_of(report, "breadboard.md")
        self.assertEqual(entry["did"], "left alone")
        self.assertTrue(entry["why"].endswith(", so it is an earlier build's"), entry["why"])
        _, text = self.flow(project, "show", "--json")
        shown = json.loads(text)
        sheet_at = shown["data"]["guide"]["wired"]["sheet_at"]
        self.assertIsNotNone(sheet_at)
        build = next(offer for phase in shown["data"]["phases"] for offer in phase["offers"] if offer["key"] == "build")
        self.assertTrue(build["effect"].startswith(WIRED_BUILD_MESSAGE), build["effect"])
        parts = next(phase for phase in shown["data"]["phases"] if phase["phase"] == "parts")
        self.assertTrue(parts["says"][0].startswith(WIRED_SHEET_MESSAGE % day_of(sheet_at)), parts["says"])
        code, _ = self.flow(project, "page")
        self.assertEqual(code, 0)
        page = (project / "page.html").read_text()
        self.assertIn(WIRED_SHEET_MESSAGE % day_of(sheet_at), page)
        self.assertIn(WIRED_BUILD_MESSAGE, page)

    def test_a_finished_build_whose_dist_copy_fails_writes_no_sheet_or_built_from(self):
        def mark(project):
            self.plant_sheet(project)
            (project / "dist" / "board" / "built-from.json").write_text(MARKED)
        code, project, report = self.run_build(env=DANGLING, before=mark)
        self.assertEqual([entry["did"] for entry in self.dist_entries(report)], ["not kept"])
        self.assertEqual((project / "dist" / "board" / "built-from.json").read_text(), MARKED)
        self.assertEqual((project / "breadboard.md").read_text(), SHEET)
        entry = self.entry_of(report, "breadboard.md")
        self.assertEqual(entry["did"], "left alone")
        self.assertIn("the build was not kept in this run", entry["why"])

    def test_a_build_with_problems_leaves_an_earlier_sheet_named_and_the_breadboard_stale(self):
        # the refuter's fix 1: a build that ends `problems` replaces dist/ but writes no sheet, so the earlier sheet stays
        # beside the new circuit, named, and the breadboard phase reads it as stale
        code, project, report = self.run_build(env=ERRORED, before=self.plant_sheet)
        self.assertEqual(code, 1)
        self.assertEqual([entry["did"] for entry in self.dist_entries(report)], ["wrote"])
        self.assertEqual((project / "breadboard.md").read_text(), SHEET)
        entry = self.entry_of(report, "breadboard.md")
        self.assertEqual(entry["did"], "left alone")
        self.assertTrue(entry["why"].endswith(", so it is an earlier build's"), entry["why"])
        _, text = self.flow(project, "show", "--json")
        breadboard = next(phase for phase in json.loads(text)["data"]["phases"] if phase["phase"] == "breadboard")
        self.assertEqual(breadboard["status"], "stale")

    def test_a_reference_design_build_records_that_it_wrote_dist(self):
        def earlier(project):
            (project / ".spark" / "build.json").write_text(json.dumps({"schema": 1, "status": "could-not-run", "stages": [],
                                                                       "missing_facts": [], "requirements": "requirements.json",
                                                                       "dist_written": False, "at": "2026-01-01T00:00:00+01:00"}))
        code, project, report = self.run_build(env=REFERENCE_ENV, before=earlier, args=REFERENCE)
        self.assertEqual([entry["did"] for entry in self.dist_entries(report)], ["wrote"])
        record = self.record(project)
        self.assertIs(record["dist_written"], True)
        self.assertIsNone(record["requirements"])
        self.assertNotEqual(record["at"], "2026-01-01T00:00:00+01:00")
        _, checked = self.check_all(project)
        self.assertEqual([one for one in checked["resolved"] if "did not write dist/" in one], [])

    def test_a_reference_design_build_without_a_circuit_names_the_earlier_dist(self):
        code, project, report = self.run_build(env=PARTIAL, args=REFERENCE)
        self.assertEqual([(entry["did"], entry["why"]) for entry in self.dist_entries(report)], [("left alone", WHY)])
        self.assertIs(self.record(project)["dist_written"], False)
        line = "circuit      the last build, %s, did not write dist/: build again with check_spine.py --keep before you rely on this circuit" % self.record(project)["at"]
        _, checked = self.check_all(project)
        self.assertIn(line, checked["resolved"])
    # --- end P1093, P1095 ---


class ReplaceWholeTest(unittest.TestCase):
    """`replace_whole` itself, when the rename that puts the copy in place fails or is stopped midway."""

    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder, True)
        for name, text in (("new", "new"), ("dist", "earlier")):
            (self.folder / name / "board").mkdir(parents=True)
            (self.folder / name / "board" / "circuit.json").write_text(text)

    def replace_with_a_stop(self, stop):
        """replace_whole with a rename that raises `stop` for the staged copy."""
        def rename(source, target):
            if Path(source).name == "dist.new":
                raise stop
            os.rename(source, target)
        replace_whole(self.folder / "new", self.folder / "dist", rename)

    def assert_earlier_whole(self):
        self.assertEqual(files_of(self.folder / "dist"), {"board/circuit.json": b"earlier"})
        self.assertEqual(sorted(each.name for each in self.folder.iterdir()), ["dist", "new"])

    def test_a_rename_that_fails_puts_the_earlier_dist_back(self):
        with self.assertRaises(OSError):
            self.replace_with_a_stop(OSError("full"))
        self.assert_earlier_whole()

    def test_a_ctrl_c_midway_puts_the_earlier_dist_back_and_removes_the_copy(self):
        with self.assertRaises(KeyboardInterrupt):
            self.replace_with_a_stop(KeyboardInterrupt())
        self.assert_earlier_whole()


if __name__ == "__main__":
    unittest.main()
