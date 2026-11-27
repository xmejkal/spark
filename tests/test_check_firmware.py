"""
check-firmware, the free checks in one Operation (P1208, #1757): the import check and the project's own tests, with no sim/
and no board. `spark.firmware.firmware_check.CheckFirmware` is the Operation, and `scripts/check_firmware.py` its CLI.

    python3 -m unittest tests.test_check_firmware

Each test builds a small project in the suite's temp folder and runs real children, because the counts are what is tested.
"""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_firmware  # noqa: E402
from fakes import FakeOutsideWorld  # noqa: E402
from spark.core import outcomes  # noqa: E402
from spark.core.codes import Code  # noqa: E402
from spark.core.result import Refusal  # noqa: E402
from spark.core.operation import READS, RUNS, WRITES  # noqa: E402
from spark.core.zone_time import stamp  # noqa: E402
from spark.firmware import own_tests  # noqa: E402
from spark.firmware.firmware_check import CheckFirmware  # noqa: E402
from spark.records.check_record import CheckRecordStore  # noqa: E402
from fakes import FakeClock  # noqa: E402

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
        self.assertEqual(result.notes, [{"subject": "tests", "sentence": "no tests/ folder: this project has no own tests"}])
        self.assertIn("tests: none (no tests/ folder)", result.lines)

    def test_no_firmware_folder_still_runs_the_tests(self):
        result = check(a_project(tests={"test_a": TWO_PASSING}))
        self.assertEqual(result.status(), outcomes.COULD_NOT_RUN)
        self.assertEqual([(found.severity, found.code) for found in result.findings],
                         [(outcomes.COULD_NOT_RUN, "no_firmware_folder")])
        self.assertEqual(result.data["tests"]["state"], "recorded")
        self.assertEqual(result.data["imports"], {"state": "not-checked"})
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
            def read(self, project, outside):
                return own_tests.OwnTests("recorded", 5, 5, [], 0)

        result = check(a_project({"light": LIGHT}), own_tests_reader=GivenReader())
        self.assertEqual(result.data["tests"]["total"], 5)

    def test_the_reader_gets_the_whole_outside_world_so_a_runner_can_find_its_tool(self):
        # P1208 review A4: `read(project, outside)`, so a MicroPython host runner can use outside.find_tool
        given = []

        class GivenReader:
            def read(self, project, outside):
                given.append(outside)
                return own_tests.OwnTests("none-recorded")

        outside = FakeOutsideWorld(run=subprocess.run)
        CheckFirmware(own_tests_reader=GivenReader()).run(a_project({"light": LIGHT}), outside=outside)
        self.assertEqual(given, [outside])

    def test_the_tests_timeout_goes_to_the_default_reader_and_a_reader_with_it_is_refused(self):
        self.assertEqual(CheckFirmware(tests_timeout_s=7).reader.timeout_s, 7)
        with self.assertRaises(ValueError):
            CheckFirmware(tests_timeout_s=7, own_tests_reader=object())

    def test_every_test_skipped_is_could_not_run_never_ok(self):
        # P1208 review R3 (delegated: the council decided in the PO's night auto mode, his to change)
        result = check(a_project({"light": LIGHT}, {"test_a": "import unittest\n\nclass A(unittest.TestCase):\n    @unittest.skip('x')\n    def test_a(self):\n        pass\n"}))
        self.assertEqual(result.status(), outcomes.COULD_NOT_RUN)
        self.assertEqual([found.code for found in result.findings], ["own_tests_not_run"])

    def test_an_import_finding_is_built_from_its_module_entry_whatever_the_list_of_problems(self):
        # P1208 review A3: no pairing by position: the entry holds its module, code and detail
        entries = [{"module": "a", "status": "imported", "detail": ""},
                   {"module": "b", "status": "raised", "detail": "KeyError: 'k'", "code": Code("import_failed", "m", "fix one")},
                   {"module": "c", "status": "timed out", "detail": "5 s", "code": Code("import_timeout", "m", "fix two")}]
        found = CheckFirmware.import_findings(entries, [], [])
        self.assertEqual([(each.subject, each.code, each.sentence) for each in found],
                         [("b", "import_failed", "b raised: KeyError: 'k'"), ("c", "import_timeout", "c timed out: 5 s")])
        self.assertTrue(all(each.fix for each in found))

    def test_a_problem_with_no_module_is_one_finding_named_firmware(self):
        nothing = Refusal("nothing to import", Code("nothing_to_import", "m", "fix three"))
        found = CheckFirmware.import_findings([{"module": "pins", "status": "imported", "detail": ""}], [nothing], [])
        self.assertEqual([(each.subject, each.code) for each in found], [("firmware", "nothing_to_import")])


class TheCheckRecordTest(unittest.TestCase):
    """P1209 (D1, D3): every run that read firmware/ keeps its answer in `.spark/check-firmware.json`, which the flow reads."""

    def test_a_run_keeps_its_answer_in_the_check_record(self):
        project = a_project({"light": LIGHT}, {"test_a": TWO_PASSING})
        result = check(project)
        read = CheckRecordStore(project, "check-firmware").read()
        self.assertEqual((read.state, read.current, read.status), (outcomes.RECORDED, True, outcomes.OK))
        self.assertEqual(read.data, {"imports": result.data["imports"], "tests": result.data["tests"]})
        self.assertEqual(read.lines, ["imports: 1 of 1 imported", "tests: 2 of 2 passed (tests/)"])
        self.assertEqual(read.at, stamp(FakeClock().now()))  # the time with its zone
        self.assertIs(result.data["written"], True)

    def test_a_failed_check_is_kept_with_its_status(self):
        project = a_project({"light": LIGHT}, {"test_a": ONE_FAILING})
        check(project)
        read = CheckRecordStore(project, "check-firmware").read()
        self.assertEqual((read.status, read.data["tests"]["failed"]), (outcomes.PROBLEMS, ["test_a.A.test_bad"]))

    def test_a_record_that_cannot_be_written_is_a_note_and_the_result_stands(self):
        project = a_project({"light": LIGHT}, {"test_a": TWO_PASSING})
        (project / ".spark").write_text("a file where the folder goes")
        result = check(project)
        self.assertEqual((result.status(), result.findings, result.data["written"]), (outcomes.OK, [], False))
        self.assertEqual(result.notes, [{"subject": ".spark/check-firmware.json",
                                         "sentence": "did not keep the check record: FileExistsError"}])
        self.assertEqual(result.lines[-1], "did not keep the check record: FileExistsError")  # the text view shows it (v2-7)

    def test_no_firmware_folder_keeps_no_record(self):
        """v2-5: a mistyped --project is never made into a project with a .spark/."""
        project = a_project(tests={"test_a": TWO_PASSING})
        result = check(project)
        self.assertEqual((result.data["written"], (project / ".spark").exists()), (False, False))

    def test_the_record_keeps_no_module_detail(self):
        """v3-2: no `modules`, no module detail and no traceback text, only the counts and the failed tests' ids."""
        project = a_project({"light": LIGHT, "sensor": "raise KeyError('a-detail-text')\n"}, {"test_a": ONE_FAILING})
        check(project)
        text = (project / ".spark" / "check-firmware.json").read_text()
        self.assertNotIn('"modules"', text)
        for gone in ("a-detail-text", "KeyError", "AssertionError", "1 != 2"):
            self.assertNotIn(gone, text)
        self.assertIn("test_a.A.test_bad", text)

    def test_the_record_names_no_secrets_file(self):
        """v2-12, v3-2: the secrets file is in the record with neither its path nor its sha256."""
        import hashlib
        project = a_project({"light": LIGHT, "wifi_secrets": 'PASSWORD = "hunter2-hunter2"\n'}, {"test_a": TWO_PASSING})
        check(project)
        text = (project / ".spark" / "check-firmware.json").read_text()
        self.assertNotIn("wifi_secrets", text)
        self.assertNotIn(hashlib.sha256((project / "firmware" / "wifi_secrets.py").read_bytes()).hexdigest(), text)
        self.assertIn("firmware/light.py", text)

    def test_the_page_is_written_again_after_a_check(self):
        project = a_project({"light": LIGHT}, {"test_a": TWO_PASSING})
        (project / "page.html").write_text("an older page\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_firmware.main(["--project", str(project), "--json"])
        said = json.loads(out.getvalue())
        self.assertEqual(code, outcomes.EXIT_OK, said)
        self.assertEqual([note["subject"] for note in said["notes"]], ["page.html"])
        self.assertNotEqual((project / "page.html").read_text(), "an older page\n")


class WhatItDeclaresTest(unittest.TestCase):
    def test_it_declares_writes_and_writes_only_its_check_record(self):
        self.assertEqual(CheckFirmware.effects, (READS, RUNS, WRITES))
        project = a_project({"light": LIGHT}, {"test_a": TWO_PASSING})
        before = files_of(project)
        check(project)
        self.assertEqual(files_of(project), sorted(before + [".spark", ".spark/check-firmware.json"]))

    def test_its_data_keys_are_the_keys_of_its_answer(self):
        result = check(a_project({"light": LIGHT}, {"test_a": TWO_PASSING}))
        self.assertEqual(sorted(CheckFirmware.data_keys), sorted(result.data))

    def test_the_project_argument_is_the_only_one_but_json(self):
        self.assertEqual([argument.dest for argument in CheckFirmware.arguments], ["project", "json"])

    def test_it_has_a_summary_and_the_op_named_for_the_script(self):
        self.assertEqual(CheckFirmware.name, "check-firmware")
        self.assertIn("own tests", CheckFirmware.summary)


class TheCommandTest(unittest.TestCase):
    """The CLI, `scripts/check_firmware.py`: one run_cli call over the Operation."""

    def run_main(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_firmware.main([str(each) for each in argv])
        return code, out.getvalue()

    def test_the_text_says_n_of_m(self):
        code, out = self.run_main("--project", a_project({"light": LIGHT}, {"test_a": TWO_PASSING}))
        self.assertEqual(code, outcomes.EXIT_OK, out)
        self.assertIn("imports: 1 of 1 imported", out)
        self.assertIn("tests: 2 of 2 passed", out)

    def test_a_failed_own_test_exits_1_and_the_json_names_its_code(self):
        code, out = self.run_main("--project", a_project({"light": LIGHT}, {"test_a": ONE_FAILING}), "--json")
        said = json.loads(out)
        self.assertEqual((code, said["status"], said["problems"][0]["code"]), (outcomes.EXIT_PROBLEMS, "problems", "own_test_failed"))
        self.assertEqual(said["data"]["tests"]["failed"], ["test_a.A.test_bad"])

    def test_tests_that_gave_no_count_exit_2(self):
        project = a_project({"light": LIGHT}, {"test_a": "import unittest\n\nclass A(unittest.TestCase):\n    def test_loops(self):\n        while True:\n            pass\n"})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_firmware.main(["--project", str(project), "--json"], operation=CheckFirmware(tests_timeout_s=0.5))
        self.assertEqual((code, json.loads(out.getvalue())["unchecked"][0]["code"]), (outcomes.EXIT_COULD_NOT_RUN, "own_tests_not_run"))


if __name__ == "__main__":
    unittest.main()
