"""P324: tools/factcheck.py checks a plan's file:line references, lists the names it proposes and the counts it states."""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import factcheck  # noqa: E402


def fixture():
    """A small tree: two files named util.py, one module with a class, a guide, and a plan in its own folder."""
    root = Path(tempfile.mkdtemp())
    (root / "a").mkdir()
    (root / "b").mkdir()
    (root / "plan").mkdir()
    (root / "a" / "util.py").write_text("x = 1\n")
    (root / "b" / "util.py").write_text("y = 2\n")
    (root / "core.py").write_text("class FlashTool:\n    pass\n\n\ndef run_flash():\n    return 1\n")
    (root / "guide.md").write_text("The `needs_yes` key says a person must answer.\n")
    plan = root / "plan" / "design.md"
    plan.write_text("A `BrandNewThing` and `run_flash` and `needs_yes` and `only_here`.\n")
    (root / "plan" / "notes.md").write_text("`only_here` is defined in the plan's own folder.\n")
    files = [p for p in root.rglob("*") if p.is_file()]
    return root, plan, factcheck.PlanCheck(root, files)


class ReferenceTest(unittest.TestCase):
    def setUp(self):
        self.root, self.plan, self.check = fixture()

    def verdicts(self, text):
        return {reference: verdict for reference, verdict, _ in self.check.references(text)}

    def test_each_reference_gets_its_verdict(self):
        said = self.verdicts("core.py:1 core.py:99 gone.py:3 util.py:1 a/util.py:1")
        self.assertEqual(said, {"core.py:1": "ok", "core.py:99": "past end", "gone.py:3": "missing",
                                "util.py:1": "ambiguous", "a/util.py:1": "ok"})

    def test_an_ok_reference_shows_its_line(self):
        self.assertEqual(self.check.references("core.py:5"), [("core.py:5", "ok", "def run_flash():")])


class NameAndCountTest(unittest.TestCase):
    def setUp(self):
        self.root, self.plan, self.check = fixture()

    def test_only_a_name_found_nowhere_outside_the_plan_folder_is_listed(self):
        names = self.check.unknown_names(self.plan.read_text(), self.plan.parent)
        self.assertEqual(names, ["BrandNewThing", "only_here"])

    def test_a_sentence_with_a_count_is_listed_and_a_plain_number_is_not(self):
        said = factcheck.PlanCheck.counts("It touches 34 importers. Slice 2 is next. Version 10 ships.")
        self.assertEqual(said, ["It touches 34 importers."])


class NoGitTest(unittest.TestCase):
    def test_without_git_it_lists_the_files_itself_and_skips_caches(self):
        root = Path(tempfile.mkdtemp())
        (root / "__pycache__").mkdir()
        (root / "__pycache__" / "x.pyc").write_text("")
        (root / "kept.py").write_text("z = 3\n")
        check = factcheck.PlanCheck.for_repository(root)
        self.assertEqual([p.name for p in check.files], ["kept.py"])


class MainTest(unittest.TestCase):
    def run_main(self, text):
        plan = Path(tempfile.mkdtemp()) / "plan.md"
        plan.write_text(text)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = factcheck.main([str(plan)])
        return code, out.getvalue()

    def test_a_good_reference_exits_0_and_a_broken_one_exits_1(self):
        self.assertEqual(self.run_main("See tools/journey.py:1.")[0], 0)
        code, out = self.run_main("See tools/no_such_tool.py:1.")
        self.assertEqual(code, 1)
        self.assertIn("1 broken reference(s)", out)


if __name__ == "__main__":
    unittest.main()
