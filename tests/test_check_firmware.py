"""
check-firmware, the free checks in one Operation (P1208, #1757): the import check and the project's own tests, with no sim/
and no board. `spark.firmware.firmware_check.CheckFirmware` is the Operation, and `scripts/check_firmware.py` its CLI.

    python3 -m unittest tests.test_check_firmware

Each test builds a small project in the suite's temp folder and runs real children, because the counts are what is tested.
"""

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
from spark.core import outcomes  # noqa: E402
from spark.core.operation import READS, RUNS  # noqa: E402
from spark.firmware import own_tests  # noqa: E402
from spark.firmware.firmware_check import CheckFirmware  # noqa: E402

LIGHT = "from machine import Pin\nLED = Pin(2, Pin.OUT)\n"
TWO_PASSING = "import unittest\n\nclass A(unittest.TestCase):\n    def test_one(self):\n        pass\n\n    def test_two(self):\n        pass\n"
ONE_FAILING = "import unittest\n\nclass A(unittest.TestCase):\n    def test_fine(self):\n        pass\n\n    def test_bad(self):\n        self.assertEqual(1, 2)\n"


def a_project(firmware=None, tests=None):
    """A project with firmware/ holding one file per entry of `firmware` ({"light": source}) and tests/ one per entry of
    `tests`; None for either leaves its folder out. Returns the project."""
    project = Path(tempfile.mkdtemp()) / "project"
    project.mkdir()
    for folder, files in (("firmware", firmware), ("tests", tests)):
        if files is not None:
            (project / folder).mkdir()
            for name, source in files.items():
                (project / folder / (name + ".py")).write_text(source)
    return project


def check(project, **keywords):
    """The OperationResult of CheckFirmware over `project`, its children real."""
    return CheckFirmware(**keywords).run(project, outside=FakeOutsideWorld(run=subprocess.run))


def files_of(project):
    return sorted(str(path.relative_to(project)) for path in project.rglob("*"))


class TheFreeChecksTogetherTest(unittest.TestCase):
    def test_a_project_whose_firmware_imports_and_tests_pass_is_ok(self):
        result = check(a_project({"light": LIGHT}, {"test_a": TWO_PASSING}))
        self.assertEqual(result.status(), outcomes.OK, result.findings)
        self.assertEqual(result.data["imports"], {"imported": 1, "total": 1})
        self.assertEqual(result.data["tests"], {"state": "recorded", "passed": 2, "total": 2, "failed": [], "skipped": 0})
        self.assertEqual([entry["module"] for entry in result.data["modules"]], ["light"])
        self.assertIn("imports: 1 of 1 imported", result.lines)
        self.assertIn("tests: 2 of 2 passed (tests/)", result.lines)

    def test_a_failed_own_test_is_a_problem_with_its_code(self):
        result = check(a_project({"light": LIGHT}, {"test_a": ONE_FAILING}))
        self.assertEqual(result.status(), outcomes.PROBLEMS)
        problems = [found for found in result.findings if found.severity == outcomes.PROBLEMS]
        self.assertEqual([(found.subject, found.code) for found in problems], [("test_a.A.test_bad", "own_test_failed")])
        self.assertIn("AssertionError: 1 != 2", problems[0].sentence)
        self.assertEqual(result.data["tests"]["failed"], ["test_a.A.test_bad"])
        self.assertEqual((result.data["tests"]["passed"], result.data["tests"]["total"]), (1, 2))
        self.assertIn("tests: 1 of 2 passed (tests/)", result.lines)

    def test_a_module_that_does_not_import_is_a_problem_with_its_code_and_its_name(self):
        result = check(a_project({"light": LIGHT, "sensor": "import missing_driver\n"}, {"test_a": TWO_PASSING}))
        self.assertEqual(result.status(), outcomes.PROBLEMS)
        self.assertEqual([(found.subject, found.code) for found in result.findings], [("sensor", "import_failed")])
        self.assertEqual(result.data["imports"], {"imported": 1, "total": 2})

    def test_no_tests_folder_is_a_note_and_no_finding(self):
        result = check(a_project({"light": LIGHT}))
        self.assertEqual((result.status(), result.findings), (outcomes.OK, []))
        self.assertEqual(result.data["tests"], {"state": "none-recorded"})
        self.assertEqual(result.notes, ["no tests/ folder: this project has no own tests"])
        self.assertIn("tests: none (no tests/ folder)", result.lines)

    def test_no_firmware_folder_still_runs_the_tests(self):
        result = check(a_project(tests={"test_a": TWO_PASSING}))
        self.assertEqual(result.status(), outcomes.COULD_NOT_RUN)
        self.assertEqual([(found.severity, found.code) for found in result.findings],
                         [(outcomes.COULD_NOT_RUN, "no_firmware_folder")])
        self.assertEqual(result.data["tests"]["state"], "recorded")
        self.assertEqual(result.data["imports"], {})
        self.assertIn("imports: not checked (no firmware/ folder)", result.lines)

    def test_a_test_run_that_cannot_count_is_could_not_run_never_ok(self):
        project = a_project({"light": LIGHT}, {"test_a": "import unittest\n\nclass A(unittest.TestCase):\n    def test_loops(self):\n        while True:\n            pass\n"})
        result = check(project, tests_timeout_s=0.5)
        self.assertEqual(result.status(), outcomes.COULD_NOT_RUN)
        self.assertEqual([(found.severity, found.code) for found in result.findings],
                         [(outcomes.COULD_NOT_RUN, "own_tests_not_run")])
        self.assertEqual(result.data["tests"]["state"], "not-checked")
        self.assertNotIn("passed", result.data["tests"])
        self.assertTrue(result.lines[-1].startswith("tests: not checked ("), result.lines)

    def test_the_import_timeout_is_a_keyword_of_the_operation(self):
        result = check(a_project({"spin": "while True:\n    pass\n"}), import_timeout_s=0.5)
        self.assertEqual([found.code for found in result.findings], ["import_timeout"])

    def test_a_runner_given_to_the_operation_is_the_one_that_reads(self):
        class GivenReader:
            def read(self, project, run):
                return own_tests.OwnTests("recorded", 5, 5, [], 0)

        result = check(a_project({"light": LIGHT}), own_tests_reader=GivenReader())
        self.assertEqual(result.data["tests"]["total"], 5)


class WhatItDeclaresTest(unittest.TestCase):
    def test_it_declares_reads_and_runs_and_writes_nothing(self):
        self.assertEqual(CheckFirmware.effects, (READS, RUNS))
        project = a_project({"light": LIGHT}, {"test_a": TWO_PASSING})
        before = files_of(project)
        check(project)
        self.assertEqual(files_of(project), before)

    def test_its_data_keys_are_the_keys_of_its_answer(self):
        result = check(a_project({"light": LIGHT}, {"test_a": TWO_PASSING}))
        self.assertEqual(sorted(CheckFirmware.data_keys), sorted(result.data))

    def test_the_project_argument_is_the_only_one_but_json(self):
        self.assertEqual([argument.dest for argument in CheckFirmware.arguments], ["project", "json"])

    def test_it_has_a_summary_and_the_op_named_for_the_script(self):
        self.assertEqual(CheckFirmware.name, "check-firmware")
        self.assertIn("own tests", CheckFirmware.summary)


if __name__ == "__main__":
    unittest.main()
