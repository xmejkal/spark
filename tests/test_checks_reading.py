"""
The flow's reading of a check record (P1209, #1758): `spark.flow.checks_reading` says the free checks' state in one line,
from `.spark/check-firmware.json` alone, and whether the page draws it grey: only where nothing more runs. It runs nothing.

    python3 -m unittest tests.test_checks_reading
"""

import ast
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.core.zone_time import day_and_time  # noqa: E402
from spark.firmware.firmware_check import INPUTS  # noqa: E402
from spark.flow import checks_reading  # noqa: E402
from spark.records.check_record import CheckRecordStore  # noqa: E402

AT = "2026-11-27T02:10:00+01:00"
OK_LINES = ["imports: 6 of 6 imported", "tests: 35 of 35 passed (tests/)"]
NO_MODEL = "No simulation: Wokwi has no model of this board. You test it on the real board."


def a_project(firmware=True):
    """A project with firmware/main.py and tests/, or an empty one."""
    project = Path(tempfile.mkdtemp()) / "clock"
    project.mkdir()
    if firmware:
        (project / "firmware").mkdir()
        (project / "firmware" / "main.py").write_text("import clock\n")
        (project / "tests").mkdir()
        (project / "tests" / "test_clock.py").write_text("import unittest\n")
    return project


def with_record(project, status="ok", lines=OK_LINES, inputs=INPUTS):
    """`project` with a check record of check-firmware saved now, as the Operation saves it."""
    CheckRecordStore(project, "check-firmware").save(inputs, AT, {"status": status, "data": {}, "lines": lines})
    return project


def simulation(project, no_model=True, firmware_written=True):
    return checks_reading.simulation_of(project, firmware_written, no_model)


class TheSimulationLineTest(unittest.TestCase):
    def test_no_record_and_no_firmware_with_no_model_is_today_s_line_in_grey(self):
        said = simulation(a_project(firmware=False), firmware_written=False)
        self.assertEqual((said["line"], said["grey"], said["check"]["state"]), (NO_MODEL, True, "none-recorded"))

    def test_no_record_and_no_firmware_on_a_covered_board_is_no_line(self):
        said = simulation(a_project(firmware=False), no_model=False, firmware_written=False)
        self.assertEqual((said["line"], said["grey"]), (None, False))

    def test_firmware_and_no_record_says_not_run_yet_and_is_not_grey(self):
        said = simulation(a_project())
        self.assertEqual((said["line"], said["grey"]), ("Free checks: not run yet. Ask Claude to run them, for free. " + NO_MODEL, False))

    def test_a_current_ok_record_with_no_model_is_grey_and_names_the_counts(self):
        said = simulation(with_record(a_project()))
        self.assertEqual(said["line"], "Free checks, %s: imports: 6 of 6 imported; tests: 35 of 35 passed (tests/). %s"
                         % (day_and_time(AT), NO_MODEL))
        self.assertEqual((said["grey"], said["check"]["state"], said["check"]["current"]), (True, "recorded", True))

    def test_a_failed_check_is_never_grey(self):
        said = simulation(with_record(a_project(), "problems", ["imports: 0 of 0 imported", "tests: none (no tests/ folder)"]))
        self.assertFalse(said["grey"])
        # the card's page-check step 7: a run that answered problems says so, though its lines show no failure
        self.assertEqual(said["line"], "Free checks, %s, problems: imports: 0 of 0 imported; tests: none (no tests/ folder). "
                         "Ask Claude to go through them with you. %s" % (day_and_time(AT), NO_MODEL))

    def test_a_record_of_older_firmware_says_run_again_and_shows_no_counts(self):
        project = with_record(a_project())
        (project / "firmware" / "main.py").write_text("import clock  # changed\n")
        said = simulation(project)
        self.assertEqual(said["line"], "Free checks, %s, on older firmware/ or tests/: ask Claude to run them again. %s"
                         % (day_and_time(AT), NO_MODEL))
        self.assertNotIn("6 of 6", said["line"])
        self.assertFalse(said["grey"])

    def test_an_older_record_names_its_own_inputs(self):
        """v3-4: the folder or file names come from the record's `inputs`, so check-design (P1255) reuses the reader."""
        project = a_project()
        (project / "board.tsx").write_text("<board />\n")
        CheckRecordStore(project, "check-design").save(("board.tsx",), AT, {"status": "ok", "data": {}, "lines": ["x"]})
        (project / "board.tsx").write_text("<board/>\n")
        said = checks_reading.said_of(checks_reading.read_check(project, "check-design"), "Board checks")
        self.assertEqual(said, "Board checks, %s, on older board.tsx: ask Claude to run them again." % day_and_time(AT))

    def test_an_unreadable_record_says_so_and_is_not_grey(self):
        project = a_project()
        (project / ".spark").mkdir()
        (project / ".spark" / "check-firmware.json").write_text("{not json")
        said = simulation(project)
        self.assertEqual(said["line"], "Free checks: the check record is no JSON. Ask Claude to run them again. " + NO_MODEL)
        self.assertEqual((said["grey"], said["check"]["state"]), (False, "not-checked"))

    def test_a_board_wokwi_covers_has_the_free_checks_part_alone_and_is_not_grey(self):
        """v2-8: on a board Wokwi covers, the simulate step's words stay in guide.now and the stations."""
        said = simulation(with_record(a_project()), no_model=False)
        self.assertEqual(said["line"], "Free checks, %s: imports: 6 of 6 imported; tests: 35 of 35 passed (tests/)." % day_and_time(AT))
        self.assertFalse(said["grey"])

    def test_a_secrets_file_never_makes_the_record_older(self):
        """v3-1: the reader leaves the secrets files out as the Operation does."""
        project = a_project()
        (project / "firmware" / "wifi_secrets.py").write_text('PASSWORD = "one-password"\n')
        from spark.firmware.project_secrets import is_secret_path
        CheckRecordStore(project, "check-firmware", leave_out=is_secret_path).save(INPUTS, AT, {"status": "ok", "data": {}, "lines": OK_LINES})
        (project / "firmware" / "wifi_secrets.py").write_text('PASSWORD = "another-password"\n')
        self.assertTrue(simulation(project)["grey"])

    def test_the_reader_runs_nothing(self):
        tree = ast.parse((ROOT / "scripts" / "spark" / "flow" / "checks_reading.py").read_text())
        imported = {alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names}
        imported |= {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertFalse(imported & {"subprocess", "os"}, imported)
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)} | {node.arg for node in ast.walk(tree) if isinstance(node, ast.arg)}
        self.assertNotIn("outside", names)


class ThePinLineTest(unittest.TestCase):
    """P882: `missing_pin_line` is the line of a current record that names a pin name the pin map lacks, else None."""

    LINE = "pin map: 0 of 1 uses found in firmware/pins.py, not found: JOY_SW (firmware/main.py:3)"
    MISSING = {"state": "recorded", "used": 1, "missing": [{"name": "JOY_SW", "file": "firmware/main.py", "line": 3}], "not_compared": []}

    def with_pin_map(self, pin_map, project=None, **keywords):
        project = project or a_project()
        CheckRecordStore(project, "check-firmware").save(INPUTS, AT, dict({"status": "problems", "lines": OK_LINES,
                                                                           "data": {"pin_map": pin_map}}, **keywords))
        return project

    def test_a_current_record_that_names_a_missing_name_gives_the_line(self):
        self.assertEqual(checks_reading.missing_pin_line(self.with_pin_map(self.MISSING)), self.LINE)

    def test_a_record_of_older_firmware_gives_none(self):
        project = self.with_pin_map(self.MISSING)
        (project / "firmware" / "main.py").write_text("import clock  # changed\n")
        self.assertIsNone(checks_reading.missing_pin_line(project))

    def test_a_record_with_no_pin_map_gives_none(self):
        self.assertIsNone(checks_reading.missing_pin_line(with_record(a_project())))  # P1209's records hold data {}

    def test_no_record_and_a_record_that_cannot_be_read_give_none(self):
        project = a_project()
        self.assertIsNone(checks_reading.missing_pin_line(project))
        (project / ".spark").mkdir()
        (project / ".spark" / "check-firmware.json").write_text("{not json")
        self.assertIsNone(checks_reading.missing_pin_line(project))

    def test_a_pin_map_that_lacks_nothing_or_was_not_read_gives_none(self):
        for pin_map in (dict(self.MISSING, missing=[]), {"state": "not-checked", "why": "x"}):
            with self.subTest(pin_map=pin_map):
                self.assertIsNone(checks_reading.missing_pin_line(self.with_pin_map(pin_map)))

    def test_a_pin_map_of_another_shape_gives_none_and_never_raises(self):
        for pin_map in ([], "x", None, dict(self.MISSING, missing="JOY_SW"), dict(self.MISSING, missing=[{"name": "A"}]),
                        dict(self.MISSING, used="1")):
            with self.subTest(pin_map=pin_map):
                self.assertIsNone(checks_reading.missing_pin_line(self.with_pin_map(pin_map)))


class TheDesignLineTest(unittest.TestCase):
    """P1255: the Design checks' line, `design_line`, says the check-design record in one sentence from the record alone
    (`said_of`), and runs nothing (`test_the_reader_runs_nothing` reads this module)."""

    INPUTS = ["requirements.json"]

    def a_project(self):
        project = Path(tempfile.mkdtemp()) / "lamp"
        project.mkdir()
        (project / "requirements.json").write_text('{"board": "xiao-esp32-c6"}\n')
        return project

    def kept(self, project, status, lines):
        CheckRecordStore(project, "check-design").save(self.INPUTS, AT, {"status": status, "data": {}, "lines": lines})
        return project

    def test_no_build_and_no_record_is_no_line(self):
        self.assertIsNone(checks_reading.design_line(self.a_project(), False))

    def test_a_build_and_no_record_says_not_run_yet(self):
        self.assertEqual(checks_reading.design_line(self.a_project(), True), "Design checks: not run yet. Ask Claude to run them, for free.")

    def test_a_record_is_said_with_no_build_too(self):
        project = self.kept(self.a_project(), "ok", ["2 check(s) found nothing"])
        self.assertEqual(checks_reading.design_line(project, False), "Design checks, %s: 2 check(s) found nothing." % day_and_time(AT))

    def test_a_current_record_of_problems_names_its_status_and_its_lines(self):
        project = self.kept(self.a_project(), "problems", ["rules-vs-netlist found 1 problem(s)", "2 check(s) found nothing"])
        self.assertEqual(checks_reading.design_line(project, True),
                         "Design checks, %s, problems: rules-vs-netlist found 1 problem(s); 2 check(s) found nothing. "
                         "Ask Claude to go through them with you." % day_and_time(AT))

    def test_a_could_not_run_record_says_could_not_look_and_never_ok(self):
        project = self.kept(self.a_project(), "could-not-run", ["physics could not look", "3 check(s) found nothing"])
        line = checks_reading.design_line(project, True)
        self.assertEqual(line, "Design checks, %s, could-not-run: physics could not look; 3 check(s) found nothing. "
                               "Ask Claude to go through them with you." % day_and_time(AT))
        self.assertNotIn("ok", line.split(":")[0])

    def test_an_older_record_names_its_inputs(self):
        project = self.kept(self.a_project(), "ok", ["2 check(s) found nothing"])
        (project / "requirements.json").write_text('{"board": "firebeetle2-esp32s3"}\n')
        self.assertEqual(checks_reading.design_line(project, True),
                         "Design checks, %s, on older requirements.json: ask Claude to run them again." % day_and_time(AT))

    def test_an_unreadable_record_says_why(self):
        project = self.a_project()
        (project / ".spark").mkdir()
        (project / ".spark" / "check-design.json").write_text("{not json")
        self.assertEqual(checks_reading.design_line(project, False), "Design checks: the check record is no JSON. Ask Claude to run them again.")

    def test_the_line_reads_check_design_s_record_not_check_firmware_s(self):
        project = with_record(a_project())
        self.assertEqual(checks_reading.design_line(project, True), "Design checks: not run yet. Ask Claude to run them, for free.")


class TheDesignNowLineTest(unittest.TestCase):
    """P1341: `design_now_line` is NOW's text of the design checks while no check-design record is current: a head by the
    record's state, the gloss and one ask. A current record says nothing here, at any status: the build row says it."""

    INPUTS, a_project, kept = TheDesignLineTest.INPUTS, TheDesignLineTest.a_project, TheDesignLineTest.kept
    NOT_RUN = ("The design checks have not run yet. They compare the circuit with the facts of the board and its parts. "
               "Ask Claude to run the design checks.")
    OLDER = ("The design checks ran before their files changed. They compare the circuit with the facts of the board and "
             "its parts. Ask Claude to run the design checks.")
    UNREAD = ("Design checks: the check record is no JSON. They compare the circuit with the facts of the board and its "
              "parts. Ask Claude to run the design checks.")

    def unreadable(self):
        project = self.a_project()
        (project / ".spark").mkdir()
        (project / ".spark" / "check-design.json").write_text("{not json")
        return project

    def older(self):
        project = self.kept(self.a_project(), "ok", ["2 check(s) found nothing"])
        (project / "requirements.json").write_text('{"board": "firebeetle2-esp32s3"}\n')
        return project

    def test_a_build_and_no_record_says_the_design_checks_have_not_run(self):
        self.assertEqual(checks_reading.design_now_line(self.a_project(), True), self.NOT_RUN)

    def test_no_build_is_no_text(self):
        self.assertIsNone(checks_reading.design_now_line(self.a_project(), False))
        self.assertIsNone(checks_reading.design_now_line(self.unreadable(), False))

    def test_a_current_record_is_no_text_at_any_status(self):
        for status in ("ok", "problems", "could-not-run"):
            with self.subTest(status=status):
                self.assertIsNone(checks_reading.design_now_line(self.kept(self.a_project(), status, ["1 line"]), True))

    def test_an_older_record_says_so_and_names_no_input(self):
        said = checks_reading.design_now_line(self.older(), True)
        self.assertEqual(said, self.OLDER)
        self.assertNotIn("requirements.json", said)

    def test_a_record_that_cannot_be_read_says_why(self):
        self.assertEqual(checks_reading.design_now_line(self.unreadable(), True), self.UNREAD)

    def test_no_text_says_them_or_free(self):
        for project in (self.a_project(), self.older(), self.unreadable()):
            said = checks_reading.design_now_line(project, True)
            with self.subTest(said=said):
                self.assertTrue(said)
                self.assertEqual(re.findall(r"\b(them|free)\b", said.lower()), [])

    def test_the_text_reads_check_design_s_record_not_check_firmware_s(self):
        self.assertEqual(checks_reading.design_now_line(with_record(a_project()), True), self.NOT_RUN)


if __name__ == "__main__":
    unittest.main()
