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
        self.assertEqual(len(story_tests.select(["README.md"], texts, {}).modules), 17)


if __name__ == "__main__":
    unittest.main()
