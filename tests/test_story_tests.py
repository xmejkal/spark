"""
P714 (#963): which test modules a push runs, chosen from the files its branch changed.

The PO, 2026-11-08: "you test the story. Maybe a few integration or some end-to-end tests, but just that part you
worked on". Each doubt about a file runs more, never less: the whole quick run, with the sentence that says why.

    python3 -m unittest tests.test_story_tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_commit  # noqa: E402
import story_tests  # noqa: E402

TESTS = {"test_widget": "import widget\n", "test_other": "import other  # and its __init__\n", "test_uses_widget_tests": "import test_widget\n",
         "test_golden_firmware": "", "test_golden_design": "", "test_golden_records": "", "test_golden_bench": "",
         "test_converter": "", "test_build_page": "reads commands/build.md\n", "test_docs": "walks past only_the_always_list\n"}


def chosen(*changed, tests=TESTS, goldens=()):
    return story_tests.select(list(changed), tests, dict(goldens))


class TheChangedFilesChooseTheTestsTest(unittest.TestCase):
    def assert_runs(self, story, *modules):
        self.assertEqual((story.state, story.why), ("chosen", None))
        self.assertEqual(set(story.modules) - {"test_docs"}, set(modules))

    def test_a_test_that_names_the_changed_file_runs_and_others_do_not(self):
        self.assert_runs(chosen("tools/widget.py"), "test_widget")

    def test_only_the_whole_word_names_a_file(self):
        self.assertEqual(chosen("tools/widge.py").state, "quick_run")

    def test_a_changed_test_runs_itself_though_it_never_names_itself(self):
        self.assert_runs(chosen("tests/test_other.py"), "test_other")

    def test_a_changed_test_also_runs_the_tests_that_import_it(self):
        self.assert_runs(chosen("tests/test_widget.py"), "test_widget", "test_uses_widget_tests")

    def test_a_helper_of_the_tests_runs_the_tests_that_name_it(self):
        self.assert_runs(chosen("tests/widget.py"), "test_widget")

    def test_a_script_named_only_by_a_golden_helper_runs_that_net(self):
        self.assert_runs(chosen("scripts/emit_board.py", goldens={"golden_design": 'Case("emit_board.py")\n'}.items()),
                         "test_golden_design")

    def test_a_module_of_an_area_also_runs_the_area_s_net(self):
        self.assert_runs(chosen("scripts/spark/firmware/widget.py"), "test_widget", "test_golden_firmware")

    def test_build_uses_the_design_net_and_idea_and_sourcing_the_records_net(self):
        self.assert_runs(chosen("scripts/spark/build/widget.py"), "test_widget", "test_golden_design")
        self.assert_runs(chosen("scripts/spark/idea/widget.py"), "test_widget", "test_golden_records")
        self.assert_runs(chosen("scripts/spark/sourcing/widget.py"), "test_widget", "test_golden_records")

    def test_an_area_with_no_net_runs_only_its_named_tests(self):
        # a made-up area: every real one has a net (the test below)
        self.assert_runs(chosen("scripts/spark/gadget/widget.py"), "test_widget")

    def test_every_area_of_the_tree_has_a_golden_net_that_exists(self):
        # P802: idea named test_golden_idea, which does not exist, and the story run dropped it without a word
        areas = sorted(folder.name for folder in (ROOT / "scripts" / "spark").iterdir()
                       if (folder / "__init__.py").is_file() and folder.name != "core")
        self.assertIn("idea", areas)
        nets = {area: story_tests.GOLDEN_NET % story_tests.GOLDEN_NET_ELSEWHERE.get(area, area) for area in areas}
        self.assertEqual({area: net for area, net in nets.items() if not (ROOT / "tests" / (net + ".py")).is_file()}, {})

    def test_a_command_page_runs_the_tests_that_name_the_page_and_not_the_word(self):
        tests = dict(TESTS, test_the_word="a build of the board\n")
        self.assert_runs(chosen("commands/build.md", tests=tests), "test_build_page")

    def test_a_saved_output_runs_its_net(self):
        self.assert_runs(chosen("tests/golden/look-ok.txt"), "test_golden_bench")
        self.assert_runs(chosen("tests/golden-firmware/a/run.txt"), "test_golden_firmware")

    def test_the_converter_s_files_run_the_converter_s_test(self):
        self.assert_runs(chosen("tools/circuit-to-wokwi/lib/geometry.ts"), "test_converter")

    def test_a_document_and_a_mutation_table_need_only_the_always_list(self):
        for name in ("docs/guide/agents.md", "scrum/README.md", "README.md", "tests/mutations/p1-a.json"):
            self.assert_runs(chosen(name))

    def test_the_tests_of_several_files_add_up_sorted_without_repeats(self):
        story = chosen("tools/widget.py", "tests/widget.py", "tools/other.py")
        self.assertEqual(story.modules, ("test_docs", "test_other", "test_widget"))


class ADoubtRunsTheQuickRunTest(unittest.TestCase):
    def assert_quick(self, story, word):
        self.assertEqual((story.state, story.modules, story.scope()), ("quick_run", (), None))
        self.assertIn(word, story.why)

    def test_the_core_runs_the_quick_run(self):
        self.assert_quick(chosen("scripts/spark/core/widget.py"), "every area depends on scripts/spark/core/widget.py")

    def test_a_package_file_runs_the_quick_run(self):
        self.assert_quick(chosen("scripts/spark/firmware/__init__.py"), "every area depends on scripts/spark/firmware/__init__.py")

    def test_a_file_only_an_always_run_test_names_runs_the_quick_run(self):
        self.assert_quick(chosen("tools/only_the_always_list.py"), "no test names tools/only_the_always_list.py")

    def test_a_file_nothing_names_runs_the_quick_run_and_is_named(self):
        self.assert_quick(chosen("tools/nothing_names_me.py"), "tools/nothing_names_me.py")

    def test_a_deleted_module_that_no_test_names_runs_the_quick_run(self):
        self.assert_quick(chosen("scripts/spark/firmware/gone.py"), "scripts/spark/firmware/gone.py")

    def test_a_document_outside_the_document_folders_is_not_a_document(self):
        self.assert_quick(chosen("skills/widget/PAGE.md"), "skills/widget/PAGE.md")

    def test_one_doubt_among_many_files_runs_the_quick_run(self):
        self.assertEqual(chosen("tools/widget.py", "tools/nothing_names_me.py", "README.md").state, "quick_run")

    def test_changes_that_could_not_be_read_run_the_quick_run(self):
        self.assert_quick(story_tests.select(None, TESTS, {}), "could not")

    def test_no_change_runs_the_quick_run_because_the_gate_measures_head(self):
        self.assert_quick(chosen(), "P106")

    def test_no_test_left_to_run_is_the_quick_run_and_never_an_empty_command(self):
        self.assert_quick(chosen("README.md", tests={"test_widget": ""}), "no test")


class WhatTheChoiceRemovesTest(unittest.TestCase):
    def test_a_named_test_that_no_longer_exists_is_left_out(self):
        story = chosen("tests/golden-gone/a.txt", "tools/widget.py")
        self.assertEqual(story.modules, ("test_docs", "test_widget"))

    def test_the_story_says_how_much_it_chose(self):
        self.assertEqual(chosen("tools/widget.py", "README.md").scope(), "2 of 10 test files")

    def test_every_always_run_test_exists_in_this_repository(self):
        texts = {found.stem: "" for found in (ROOT / "tests").glob("test_*.py")}
        self.assertEqual(len(story_tests.select(["README.md"], texts, {}).modules), 19)


#: P1017: a small tree of scripts/. top imports mid, mid imports low, and the package file of b imports its neighbour.
SCRIPTS = {"scripts/spark/a/top.py": "from spark.a import mid\n", "scripts/spark/a/mid.py": "import spark.a.low\n",
           "scripts/spark/a/low.py": "import json\n", "scripts/spark/a/other.py": "from spark.a.low import THING\n",
           "scripts/spark/b/__init__.py": "from spark.b import neighbour\n", "scripts/spark/b/page.py": "",
           "scripts/spark/b/neighbour.py": "", "scripts/flow.py": "from spark.flow import page\n",
           "scripts/spark/flow/page.py": "import spark.a.top\n",
           "scripts/spark/flow/__init__.py": "from spark.flow import page\n"}


def walked(*changed, tests):
    return story_tests.select(list(changed), tests, {}, SCRIPTS)


class TheImportsThroughScriptsChooseTheTestsTest(unittest.TestCase):
    """
    P1017: a test runs the modules its imports reach through scripts/, so a change to one of them runs it. The walk only
    adds tests to a story run that the name rule started. It never ends a doubt, so no change runs fewer tests than on main.
    """

    def assert_runs(self, story, *modules):
        self.assertEqual((story.state, story.why), ("chosen", None))
        self.assertEqual(set(story.modules) - {"test_docs"}, set(modules))

    def test_a_test_runs_for_a_module_that_its_imports_reach_through_two_modules(self):
        tests = {"test_x": "import spark.a.top\n", "test_names_it": "low\n", "test_apart": "import json\n"}
        self.assert_runs(walked("scripts/spark/a/low.py", tests=tests), "test_x", "test_names_it")

    def test_a_file_that_only_the_walk_finds_stays_the_quick_run_as_on_main(self):
        # the PR review of #1493: a walk that ended the doubt dropped tests that reach a file through a child process
        story = walked("scripts/spark/a/low.py", tests={"test_x": "import spark.a.top\n"})
        self.assertEqual((story.state, story.modules), ("quick_run", ()))
        self.assertIn("no test names scripts/spark/a/low.py", story.why)

    def test_from_a_package_import_names_each_module(self):
        tests = {"test_x": "from spark.a import other, top\n", "test_y": "from spark.a import other\n", "test_names_it": "mid\n"}
        self.assert_runs(walked("scripts/spark/a/mid.py", tests=tests), "test_x", "test_names_it")

    def test_each_form_of_import_reaches_its_file(self):
        forms = {"test_plain": "import flow\n", "test_dotted": "import spark.flow.page\n", "test_from_spark": "from spark import flow\n",
                 "test_from_module": "from spark.flow.page import Page\n", "test_late": "def late():\n    import spark.flow.page\n",
                 "test_stdlib": "import json\n"}
        story = walked("scripts/spark/a/top.py", tests=dict(forms, test_names_it="top\n"))
        self.assertEqual(set(story.modules), {"test_plain", "test_dotted", "test_from_spark", "test_from_module", "test_late",
                                              "test_names_it"})

    def test_a_package_file_on_the_way_is_run_and_so_reaches_its_imports(self):
        tests = {"test_x": "from spark.b.page import draw\n", "test_golden_b": "", "test_names_it": "neighbour\n"}
        self.assert_runs(walked("scripts/spark/b/neighbour.py", tests=tests), "test_x", "test_golden_b", "test_names_it")

    def test_a_text_that_does_not_parse_imports_nothing(self):
        tests = {"test_broken": "def broken(:\nimport spark.a.top\n", "test_names_it": "low\n"}
        self.assert_runs(walked("scripts/spark/a/low.py", tests=tests), "test_names_it")

    def test_a_whole_tree_test_that_the_walk_finds_does_not_remove_the_doubt(self):
        story = walked("scripts/spark/a/low.py", tests={"test_docs": "import spark.a.top\n"})
        self.assertEqual(story.state, "quick_run")

    def test_an_area_whose_modules_reach_the_change_runs_its_net(self):
        tests = {"test_golden_design": "", "test_golden_a": "", "test_names_it": "low\n"}
        self.assert_runs(walked("scripts/spark/a/low.py", tests=tests), "test_names_it", "test_golden_a", "test_golden_design")

    def test_without_the_scripts_texts_the_choice_is_today_s(self):
        tests = {"test_x": "import spark.a.top\n", "test_names_it": "low\n", "test_golden_a": "", "test_golden_design": ""}
        story = story_tests.select(["scripts/spark/a/low.py"], tests, {})
        self.assert_runs(story, "test_names_it", "test_golden_a")


class TheBreadboardChangeOfP953Test(unittest.TestCase):
    """
    P1017's value: #1374 (P953 PR 3) changed these seven modules, merged green, and main went red in test_flow_page and
    test_golden_design, which import none of them by name. A renamed module fails this loudly: update the list.
    """

    CHANGED = ("bench_changes", "drawing", "kept_moves", "rails", "spacing", "wire_routing", "wiring_steps")

    @classmethod
    def setUpClass(cls):
        cls.texts = check_commit.story_texts(ROOT)

    def test_each_breadboard_module_of_p953_pr3_runs_the_flow_page_and_the_design_net(self):
        for module in self.CHANGED:
            name = "scripts/spark/breadboard/%s.py" % module
            with self.subTest(name):
                self.assertTrue((ROOT / name).is_file(), "renamed? update CHANGED")
                story = story_tests.select([name], *self.texts)
                self.assertEqual(story.state, "chosen", story.why)
                self.assertTrue({"test_flow_page", "test_golden_design"} <= set(story.modules), story.modules)


if __name__ == "__main__":
    unittest.main()
