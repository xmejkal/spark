"""
The project's own tests, counted (P1208, #1757): `own_tests.UnittestReader` runs PROJECT/tests with unittest in a child of
its own (`own_tests_child.py`) and reads the one line of JSON that the child prints last.

    python3 -m unittest tests.test_own_tests

Each test builds a small project in the suite's temp folder and runs the real child, because the count is what is tested.
"""

import ast
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from fakes import FakeOutsideWorld  # noqa: E402
from spark.firmware import own_tests  # noqa: E402
from spark.firmware.isolated_python import IsolatedPython  # noqa: E402

CHILD = ROOT / "scripts" / "spark" / "firmware" / "own_tests_child.py"
TWO_PASSING = "import unittest\n\nclass A(unittest.TestCase):\n    def test_one(self):\n        pass\n\n    def test_two(self):\n        self.assertTrue(True)\n"


def a_project(**tests):
    """A project whose tests/ holds one file per keyword (`test_a="..."` is tests/test_a.py); with no keyword there is no
    tests/ folder. Returns the project."""
    project = Path(tempfile.mkdtemp()) / "project"
    project.mkdir()
    for name, source in tests.items():
        (project / "tests").mkdir(exist_ok=True)
        (project / "tests" / (name + ".py")).write_text(source)
    return project


def read(project, timeout_s=30):
    return own_tests.UnittestReader(timeout_s).read(project, FakeOutsideWorld(run=subprocess.run))


class CountingTest(unittest.TestCase):
    def test_a_project_with_passing_tests_counts_them(self):
        found = read(a_project(test_a=TWO_PASSING))
        self.assertEqual((found.state, found.passed, found.total, found.failed, found.skipped, found.why),
                         ("recorded", 2, 2, [], 0, None))

    def test_a_failing_test_is_named_by_its_id(self):
        found = read(a_project(test_a=(
            "import unittest\n\nclass A(unittest.TestCase):\n    def test_fails(self):\n        self.assertEqual(1, 2)\n\n"
            "    def test_raises(self):\n        raise KeyError('k')\n")))
        self.assertEqual((found.state, found.passed, found.total), ("recorded", 0, 2))
        self.assertEqual(sorted(found.failed), ["test_a.A.test_fails", "test_a.A.test_raises"])
        self.assertEqual(found.reasons["test_a.A.test_fails"], "AssertionError: 1 != 2")
        self.assertEqual(found.reasons["test_a.A.test_raises"], "KeyError: 'k'")

    def test_a_skipped_test_is_neither_passed_nor_failed(self):
        found = read(a_project(test_a=TWO_PASSING + "\n    @unittest.skip('later')\n    def test_three(self):\n        pass\n"))
        self.assertEqual((found.passed, found.total, found.failed, found.skipped), (2, 3, [], 1))

    def test_a_test_with_three_failing_subtests_is_one_failure(self):
        found = read(a_project(test_a=(
            "import unittest\n\nclass A(unittest.TestCase):\n    def test_many(self):\n        for n in range(3):\n"
            "            with self.subTest(n=n):\n                self.fail('n')\n\n    def test_fine(self):\n        pass\n")))
        self.assertEqual((found.passed, found.total, found.failed), (1, 2, ["test_a.A.test_many"]))

    def test_a_test_with_three_skipped_subtests_is_one_skipped_test(self):
        # P1208 review R1: skipped is counted by test, as the failures are, so passed is never below the tests that passed
        found = read(a_project(test_a=(
            "import unittest\n\nclass A(unittest.TestCase):\n    def test_many(self):\n        for n in range(3):\n"
            "            with self.subTest(n=n):\n                self.skipTest('later')\n\n    def test_fine(self):\n        pass\n")))
        self.assertEqual((found.state, found.passed, found.total, found.failed, found.skipped), ("recorded", 1, 2, [], 1))

    def test_an_expected_failure_that_fails_as_expected_counts_as_passed(self):
        found = read(a_project(test_a=(
            "import unittest\n\nclass A(unittest.TestCase):\n    @unittest.expectedFailure\n    def test_known(self):\n        self.fail('known')\n\n"
            "    def test_fine(self):\n        pass\n")))
        self.assertEqual((found.state, found.passed, found.total, found.failed, found.skipped), ("recorded", 2, 2, [], 0))

    def test_an_unexpected_success_is_a_failed_test(self):
        found = read(a_project(test_a=(
            "import unittest\n\nclass A(unittest.TestCase):\n    @unittest.expectedFailure\n    def test_now_works(self):\n        pass\n")))
        self.assertEqual((found.passed, found.total, found.failed), (0, 1, ["test_a.A.test_now_works"]))

    def test_a_module_that_cannot_be_imported_is_a_failed_test(self):
        found = read(a_project(test_a=TWO_PASSING, test_b="import not_a_module_anywhere\n"))
        self.assertEqual((found.passed, found.total), (2, 3))
        self.assertEqual(len(found.failed), 1)
        self.assertIn("test_b", found.failed[0])

    def test_a_class_that_cannot_set_up_is_counted_and_never_goes_below_zero(self):
        found = read(a_project(test_a=(
            "import unittest\n\nclass A(unittest.TestCase):\n    @classmethod\n    def setUpClass(cls):\n        raise OSError('no')\n\n"
            "    def test_one(self):\n        pass\n")))
        self.assertEqual(found.state, "recorded")
        self.assertEqual(len(found.failed), 1)
        self.assertGreaterEqual(found.passed, 0)
        self.assertGreaterEqual(found.total, len(found.failed))


class WhenThereIsNothingToCountTest(unittest.TestCase):
    def test_no_tests_folder_is_none_recorded(self):
        found = read(a_project())
        self.assertEqual((found.state, found.passed, found.total, found.failed, found.skipped, found.why),
                         ("none-recorded", None, None, None, None, None))

    def test_a_tests_folder_with_no_test_is_not_checked_never_zero_of_zero(self):
        found = read(a_project(helper="X = 1\n"))
        self.assertEqual(found.state, "not-checked")
        self.assertIn("no test", found.why)
        self.assertEqual((found.passed, found.total), (None, None))

    def test_a_run_where_every_test_is_skipped_is_not_checked_never_ok(self):
        # P1208 review R3 (delegated: the council decided in the PO's night auto mode, his to change): nothing passed, nothing failed
        found = read(a_project(test_a="import unittest\n\nclass A(unittest.TestCase):\n    @unittest.skip('later')\n    def test_a(self):\n        pass\n"))
        self.assertEqual(found.state, "not-checked")
        self.assertIn("was skipped: nothing passed", found.why)
        self.assertEqual((found.passed, found.total), (None, None))

    def test_a_run_past_the_timeout_is_not_checked(self):
        found = read(a_project(test_a="import unittest\n\nclass A(unittest.TestCase):\n    def test_loops(self):\n        while True:\n            pass\n"),
                     timeout_s=0.5)
        self.assertEqual(found.state, "not-checked")
        self.assertIn("did not finish within 0.5 s", found.why)
        self.assertEqual((found.passed, found.total, found.failed), (None, None, None))

    def test_a_run_that_gives_no_line_of_json_is_not_checked(self):
        def silent(command, **options):
            return subprocess.CompletedProcess(command, 3, "", "")

        found = own_tests.UnittestReader(5).read(a_project(test_a=TWO_PASSING), FakeOutsideWorld(run=silent))
        self.assertEqual(found.state, "not-checked")
        self.assertIn("no count", found.why)

    def test_a_line_that_is_not_the_count_is_not_checked(self):
        def odd(command, **options):
            return subprocess.CompletedProcess(command, 0, "\n[1, 2]\n", "")

        self.assertEqual(own_tests.UnittestReader(5).read(a_project(test_a=TWO_PASSING), FakeOutsideWorld(run=odd)).state, "not-checked")

    def test_the_reader_never_raises_for_a_tests_that_is_a_file(self):
        project = a_project()
        (project / "tests").write_text("not a folder\n")
        self.assertEqual(read(project).state, "none-recorded")


class WhatTheTestsDoDoesNotBreakTheCountTest(unittest.TestCase):
    def test_a_test_that_prints_does_not_break_the_count(self):
        found = read(a_project(test_a=(
            "import os, sys, unittest\n\nclass A(unittest.TestCase):\n    def test_prints(self):\n"
            "        print('{\"total\": 99, \"failed\": [], \"skipped\": 0}')\n"
            "        os.write(1, b'{\"total\": 98, \"failed\": [], \"skipped\": 0}\\n')\n\n"
            "    def test_prints_no_newline(self):\n        sys.stdout.write('{\"total\": 97')\n")))
        self.assertEqual((found.state, found.passed, found.total), ("recorded", 2, 2))

    def test_a_test_that_prints_with_no_newline_at_the_end_still_counts(self):
        done = subprocess.run([sys.executable, "-I", "-B", str(CHILD), str(a_project(test_a=(
            "import sys, unittest\n\nclass A(unittest.TestCase):\n    def test_a(self):\n        sys.stdout.write('partial')\n"
            "        sys.stdout.flush()\n"))), "tests"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertNotIn("partial", done.stdout)
        self.assertEqual(done.stdout.strip().splitlines()[-1], '{"total": 1, "failed": [], "skipped": 0}')

    def test_a_test_file_s_atexit_that_writes_a_line_cannot_replace_the_count(self):
        # P1208 review R4: the child ends right after its count, so nothing registered by a test runs after it
        found = read(a_project(test_a=(
            "import atexit, os, unittest\n\natexit.register(lambda: os.write(1, b'{\"total\": 99, \"failed\": [], \"skipped\": 0}\\n'))\n\n"
            "class A(unittest.TestCase):\n    def test_a(self):\n        pass\n")))
        self.assertEqual((found.state, found.passed, found.total), ("recorded", 1, 1))

    def test_tests_in_a_package_import_relative_and_from_the_firmware_folder(self):
        project = a_project(__init__="", helper="VALUE = 41\n", test_a=(
            "import unittest\nfrom . import helper\nfrom firmware import light\n\nclass A(unittest.TestCase):\n"
            "    def test_both(self):\n        self.assertEqual(helper.VALUE + 1, light.ANSWER)\n"))
        (project / "firmware").mkdir()
        (project / "firmware" / "light.py").write_text("ANSWER = 42\n")
        found = read(project)
        self.assertEqual((found.state, found.passed, found.total, found.failed), ("recorded", 1, 1, []))

    def test_the_tests_run_in_the_project_folder_and_leave_no_bytecode(self):
        project = a_project(test_a=(
            "import os, unittest\n\nclass A(unittest.TestCase):\n    def test_cwd(self):\n"
            "        self.assertTrue(os.path.isdir('tests'))\n"))
        self.assertEqual(read(project).passed, 1)
        self.assertEqual([path.name for path in project.rglob("__pycache__")], [])


class TheChildIsAFileOfItsOwnTest(unittest.TestCase):
    def test_the_child_imports_nothing_of_spark(self):
        tree = ast.parse(CHILD.read_text())
        names = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        names += [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        self.assertTrue(names)
        self.assertEqual([name for name in names if name.split(".")[0] == "spark"], [])


class TheIsolatedChildTest(unittest.TestCase):
    """P1208: the one Adapter that starts the import check's children and the own tests' child."""

    def test_the_child_starts_isolated_with_no_bytecode_and_its_cwd(self):
        calls = []

        def recording_run(command, **options):
            calls.append((command, options))
            return subprocess.CompletedProcess(command, 7, "out", "err")

        done = IsolatedPython(recording_run).call("child.py", ["a", 1], Path("/somewhere"), 3)
        self.assertEqual((done.timed_out, done.returncode, done.stdout, done.stderr), (False, 7, "out", "err"))
        command, options = calls[0]
        self.assertEqual(command, [sys.executable, "-I", "-B", "child.py", "a", "1"])
        self.assertEqual((options["cwd"], options["timeout"], options["stdin"]), ("/somewhere", 3, subprocess.DEVNULL))

    def test_a_child_past_its_time_is_timed_out_with_no_output(self):
        def too_slow(command, **options):
            raise subprocess.TimeoutExpired(command, options["timeout"])

        done = IsolatedPython(too_slow).call("child.py", [], Path("."), 1)
        self.assertEqual((done.timed_out, done.returncode, done.stdout, done.stderr), (True, None, "", ""))


if __name__ == "__main__":
    unittest.main()
