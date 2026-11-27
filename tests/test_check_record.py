"""
The check record (P1209, #1758): what a check Operation keeps of its last answer, `<project>/.spark/<op>.json`, written and
read through one Store, `spark.records.check_record.CheckRecordStore`. A record whose input files changed since reads as
older, never as current.

    python3 -m unittest tests.test_check_record
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.core import outcomes  # noqa: E402
from spark.firmware.project_secrets import is_secret_path  # noqa: E402
from spark.records.check_record import CheckRecordStore, is_plain_input  # noqa: E402

AT = "2026-11-27T02:10:00+01:00"
ANSWER = {"status": "ok", "data": {"imports": {"imported": 1, "total": 1}, "tests": {"state": "none-recorded"}},
          "lines": ["imports: 1 of 1 imported", "tests: none (no tests/ folder)"]}
INPUTS = ("firmware", "tests")


def a_project(tests=True):
    """A project with firmware/ holding main.py and light.py, and tests/ holding one test unless `tests` is False."""
    project = Path(tempfile.mkdtemp()) / "project"
    (project / "firmware").mkdir(parents=True)
    (project / "firmware" / "main.py").write_text("import light\n")
    (project / "firmware" / "light.py").write_text("LED = 2\n")
    if tests:
        (project / "tests").mkdir()
        (project / "tests" / "test_light.py").write_text("import unittest\n")
    return project


def saved(project, inputs=INPUTS, **keywords):
    """The Store of `check-firmware` over `project`, with a record saved of ANSWER over `inputs`."""
    records = CheckRecordStore(project, "check-firmware", **keywords)
    records.save(inputs, AT, ANSWER)
    return records


class TheCheckRecordTest(unittest.TestCase):
    def test_no_file_is_none_recorded(self):
        read = CheckRecordStore(a_project(), "check-firmware").read()
        self.assertEqual((read.state, read.why, read.current), (outcomes.NONE_RECORDED, None, None))

    def test_a_saved_record_reads_back_current_with_its_status_data_and_lines(self):
        project = a_project()
        read = saved(project).read()
        self.assertEqual((read.name, read.state, read.why, read.current), ("check-firmware", outcomes.RECORDED, None, True))
        self.assertEqual((read.at, read.status, read.data, read.lines), (AT, "ok", ANSWER["data"], ANSWER["lines"]))
        self.assertTrue((project / ".spark" / "check-firmware.json").is_file())
        self.assertEqual(read.inputs, list(INPUTS))

    def test_a_changed_file_reads_as_not_current(self):
        project = a_project()
        records = saved(project)
        (project / "firmware" / "light.py").write_text("LED = 4\n")  # same name, other bytes
        self.assertEqual((records.read().state, records.read().current), (outcomes.RECORDED, False))

    def test_a_new_file_in_an_input_reads_as_not_current(self):
        project = a_project()
        records = saved(project)
        (project / "tests" / "test_more.py").write_text("")
        self.assertFalse(records.read().current)

    def test_a_missing_input_folder_is_hashed_not_skipped(self):
        project = a_project(tests=False)
        records = saved(project)
        self.assertTrue(records.read().current)
        (project / "tests").mkdir()  # an empty tests/ is not the missing one
        self.assertFalse(records.read().current)

    def test_a_pycache_does_not_make_the_record_older(self):
        project = a_project()
        records = saved(project)
        (project / "firmware" / "__pycache__").mkdir()
        (project / "firmware" / "__pycache__" / "light.cpython-310.pyc").write_bytes(b"\x00")
        self.assertTrue(records.read().current)

    def test_a_file_input_is_hashed_as_itself(self):
        """v2-1: an input is a path in the project, a file or a folder, so check-design (P1255) keeps `board.tsx`."""
        project = a_project()
        (project / "board.tsx").write_text("<board />\n")
        records = saved(project, inputs=("board.tsx",))
        self.assertTrue(records.read().current)
        (project / "board.tsx").write_text("<board/>\n")
        self.assertFalse(records.read().current)

    def test_a_record_of_another_shape_is_not_checked(self):
        project = a_project()
        path = saved(project).path
        good = json.loads(path.read_text())
        for case, text in (("no JSON", "{not json"), ("schema 2", json.dumps(dict(good, schema=2))),
                           ("a key missing", json.dumps({key: value for key, value in good.items() if key != "lines"})),
                           ("an input outside", json.dumps(dict(good, inputs=["../x"]))),
                           ("an absolute input", json.dumps(dict(good, inputs=["/etc"]))),
                           ("another op", json.dumps(dict(good, op="check-design"))),
                           ("a list", "[]")):
            with self.subTest(case=case):
                path.write_text(text)
                read = CheckRecordStore(project, "check-firmware").read()
                self.assertEqual((read.state, read.current), (outcomes.NOT_CHECKED, None))
                self.assertTrue(isinstance(read.why, str) and read.why)

    def test_a_record_reader_never_raises_on_an_input_of_dot_or_a_line_that_is_no_text(self):
        """The review (A1, R12): `.`, `./` and an empty path are no plain input, and every line is a str."""
        project = a_project()
        path = saved(project).path
        good = json.loads(path.read_text())
        self.assertEqual([is_plain_input(text) for text in (".", "./", "", "firmware/", "board.tsx")],
                         [False, False, False, True, True])
        for case, text in (("input .", json.dumps(dict(good, inputs=["."]))),
                           ("input ./", json.dumps(dict(good, inputs=["./"]))),
                           ("a line that is no text", json.dumps(dict(good, lines=[1])))):
            with self.subTest(case=case):
                path.write_text(text)
                read = CheckRecordStore(project, "check-firmware").read()
                self.assertEqual((read.state, read.current), (outcomes.NOT_CHECKED, None))
                self.assertTrue(isinstance(read.why, str) and read.why)

    def test_schema_true_is_not_schema_1(self):
        """The review (A8, R13): JSON's true equals 1 in Python, and is no schema."""
        project = a_project()
        path = saved(project).path
        path.write_text(json.dumps(dict(json.loads(path.read_text()), schema=True)))
        read = CheckRecordStore(project, "check-firmware").read()
        self.assertEqual((read.state, read.why), (outcomes.NOT_CHECKED, "the check record is of another shape (schema True, op 'check-firmware')"))

    def test_a_record_with_no_inputs_is_not_checked(self):
        """The review (A8, R13): a record over no inputs proves nothing, so it never reads as current."""
        project = a_project()
        path = saved(project).path
        path.write_text(json.dumps(dict(json.loads(path.read_text()), inputs=[], inputs_sha256={})))
        read = CheckRecordStore(project, "check-firmware").read()
        self.assertEqual((read.state, read.why), (outcomes.NOT_CHECKED, "the check record names no input"))

    def test_a_record_that_cannot_be_read_is_not_checked_with_its_own_reason(self):
        """The review (A8, R13): an OSError on the record is not "no JSON"."""
        project = a_project()
        path = saved(project).path
        path.chmod(0)
        try:
            read = CheckRecordStore(project, "check-firmware").read()
        finally:
            path.chmod(0o644)
        self.assertEqual((read.state, read.why), (outcomes.NOT_CHECKED, "the check record cannot be read (PermissionError)"))

    def test_a_spark_folder_that_cannot_be_searched_is_not_checked_with_its_own_reason(self):
        """The review (A8, R13): `exists()` raises under a `.spark/` with no search right; the reader does not."""
        project = a_project()
        saved(project)
        (project / ".spark").chmod(0)
        try:
            read = CheckRecordStore(project, "check-firmware").read()
        finally:
            (project / ".spark").chmod(0o755)
        self.assertEqual((read.state, read.why), (outcomes.NOT_CHECKED, "the check record cannot be read (PermissionError)"))

    def test_save_refuses_an_input_that_is_not_plain(self):
        """The review (A4): an input outside the project is a programmer's error, as a name that is no plain id is."""
        for inputs in ((".",), ("../x",), ("/etc",), ("",), ()):
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                CheckRecordStore(a_project(), "check-firmware").save(inputs, AT, ANSWER)

    def test_an_input_that_cannot_be_read_is_not_checked(self):
        """v2-3: an OSError while hashing is no crash and no current record."""
        project = a_project()
        records = saved(project)
        (project / "firmware" / "light.py").chmod(0)
        try:
            read = records.read()
        finally:
            (project / "firmware" / "light.py").chmod(0o644)
        self.assertEqual((read.state, read.current), (outcomes.NOT_CHECKED, None))
        self.assertIn("PermissionError", read.why)

    def test_a_name_that_is_no_plain_id_is_refused(self):
        for name in ("../build", "Check", "", "check.firmware"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                CheckRecordStore(a_project(), name)

    def test_the_store_never_makes_the_project_folder(self):
        """v2-5: a mistyped project folder is never made, nor its .spark/."""
        nowhere = Path(tempfile.mkdtemp()) / "no-such-project"
        with self.assertRaises(OSError):
            CheckRecordStore(nowhere, "check-firmware").save(INPUTS, AT, ANSWER)
        self.assertFalse(nowhere.exists())


class TheSecretsTest(unittest.TestCase):
    """v3-1, v3-2: the secrets files are left out of the record on both sides: neither their path nor their sha256."""

    def a_secret_project(self):
        project = a_project()
        (project / "firmware" / "wifi_secrets.py").write_text('PASSWORD = "hunter2-hunter2"\n')
        return project

    def test_a_secrets_file_is_left_out_and_the_record_reads_as_current(self):
        project = self.a_secret_project()
        records = saved(project, leave_out=is_secret_path)
        self.assertTrue(records.read().current)
        (project / "firmware" / "wifi_secrets.py").write_text('PASSWORD = "another-password"\n')
        self.assertTrue(records.read().current)  # a new password asks for no new check

    def test_the_saved_text_holds_no_secrets_file_name_and_no_secret_hash(self):
        import hashlib
        project = self.a_secret_project()
        text = saved(project, leave_out=is_secret_path).path.read_text()
        secret_hash = hashlib.sha256((project / "firmware" / "wifi_secrets.py").read_bytes()).hexdigest()
        self.assertNotIn("wifi_secrets", text)
        self.assertNotIn(secret_hash, text)
        self.assertIn("firmware/light.py", text)

    def test_the_rule_names_only_a_secrets_file_directly_in_firmware(self):
        self.assertEqual([is_secret_path(name) for name in ("firmware/wifi_secrets.py", "firmware/lib/x_secret.py",
                                                            "tests/test_secrets.py", "firmware/light.py")],
                         [True, False, False, False])


if __name__ == "__main__":
    unittest.main()
