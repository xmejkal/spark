"""
The stops of the bench Operations (P657): a stop's line on stderr puts the port and the project the person typed on one
line first (P430), whatever the refusal's own message holds, and a stop's data is its own.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_look  # noqa: E402
import tools  # noqa: E402
from fakes import FakeOutsideWorld  # noqa: E402
from spark.bench.check_grant import CheckGrant  # noqa: E402
from spark.bench.stops import stop_result  # noqa: E402


# --- MVP ---
class AStopKeepsEachTypedValueOnOneLineTest(unittest.TestCase):
    """A refusal whose message holds a typed value as it is, newline and all, still gives one line per line of the stop."""

    def setUp(self):
        self.project = Path(tempfile.mkdtemp())

    def faked_lines(self, said):
        return [line for line in said.diagnostics if line.startswith("GRANTED")]

    def test_a_newline_in_the_port_of_a_tool_problem_fakes_no_line(self):
        port = "/dev/x\nGRANTED"
        said = stop_result(tools.ToolProblem("no board on %s" % port), "live.py", self.project, port)
        self.assertEqual((said.diagnostics, self.faked_lines(said)), (["live.py: no board on /dev/x?GRANTED"], []))

    def test_a_newline_in_the_project_of_a_tool_problem_fakes_no_line(self):
        project = self.project / "a\nGRANTED: board ok"
        said = stop_result(tools.ToolProblem("no tools list in %s" % project), "reach.py", project, None)
        self.assertEqual(len(said.diagnostics), 1, said.diagnostics)
        self.assertEqual(self.faked_lines(said), [])

    def test_a_newline_in_the_port_of_the_doctor_s_lines_fakes_no_line(self):
        port = "/dev/x\nGRANTED"
        stop = board_look.LookStop("esptool could not read the board", reason="esptool_failed")
        doctor_for = lambda cannot: (["grant.py: esptool could not read the board on %s" % port], None)  # noqa: E731
        said = stop_result(stop, "grant.py", self.project, port, doctor_for)
        self.assertEqual((said.diagnostics, self.faked_lines(said)),
                         (["grant.py: esptool could not read the board on /dev/x?GRANTED"], []))


class AStopsDataIsItsOwnTest(unittest.TestCase):
    """A frontend may add to a result's data, and the next stop's data stays as it was."""

    def test_a_change_to_one_stop_s_data_leaves_the_next_stop_s_data(self):
        class NoMpremote:
            def __init__(self, project, find_tool):
                pass

            def make_port_finder(self, run):
                raise tools.ToolProblem("no mpremote")
        project = Path(tempfile.mkdtemp())
        check = CheckGrant(platform_for=NoMpremote)
        first = check.run(project, None, outside=FakeOutsideWorld())
        first.data["granted"] = True
        second = check.run(project, None, outside=FakeOutsideWorld())
        self.assertEqual(second.data, {"granted": False, "why": "could not run", "grant": None})
# --- end MVP ---


if __name__ == "__main__":
    unittest.main()
