"""
The flow's reading of a check record (P1209, #1758): `spark.flow.checks_reading` says the free checks' state in one line,
from `.spark/check-firmware.json` alone, and whether the page draws it grey: only where nothing more runs. It runs nothing.

    python3 -m unittest tests.test_checks_reading
"""

import ast
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
from spark.flow import checks_reading, flow_codes  # noqa: E402
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
        self.assertEqual(flow_codes.NO_SIMULATION_NOW, NO_MODEL)

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
        said = simulation(with_record(a_project(), "problems", ["imports: 5 of 6 imported", "tests: 35 of 35 passed (tests/)"]))
        self.assertIn("imports: 5 of 6 imported", said["line"])
        self.assertFalse(said["grey"])

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


if __name__ == "__main__":
    unittest.main()
