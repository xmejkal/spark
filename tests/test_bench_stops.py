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

from spark.bench import board_look  # noqa: E402
from spark.records import tool_finder  # noqa: E402
from fakes import FakeOutsideWorld  # noqa: E402
from spark.bench.check_grant import CheckGrant  # noqa: E402
from spark.bench import stops  # noqa: E402
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
        said = stop_result(tool_finder.ToolError("no board on %s" % port, code="tool_missing"), "live.py",
                           self.project, port)
        self.assertEqual((said.diagnostics, self.faked_lines(said)), (["live.py: no board on /dev/x?GRANTED"], []))

    def test_a_newline_in_the_project_of_a_tool_problem_fakes_no_line(self):
        project = self.project / "a\nGRANTED: board ok"
        said = stop_result(tool_finder.ToolError("no tools list in %s" % project, code="tool_missing"), "reach.py",
                           project, None)
        self.assertEqual(len(said.diagnostics), 1, said.diagnostics)
        self.assertEqual(self.faked_lines(said), [])

    def test_a_newline_in_the_port_of_the_doctor_s_lines_fakes_no_line(self):
        port = "/dev/x\nGRANTED"
        stop = board_look.LookStopError("esptool could not read the board", reason="esptool_failed")
        doctor_for = lambda cannot: (["grant.py: esptool could not read the board on %s" % port], None)  # noqa: E731
        said = stop_result(stop, "grant.py", self.project, port, doctor_for)
        self.assertEqual((said.diagnostics, self.faked_lines(said)),
                         (["grant.py: esptool could not read the board on /dev/x?GRANTED"], []))


#: board_look's no_port stop, word for word.
NO_BOARD = ("no board found. Plug it straight into the computer with a data cable, not a hub that gives power only. "
            "If the plug is USB-C, turn it around, or use a USB-A to USB-C cable.")


class AStopOfAFirmwareThatSleepsSaysTheAsleepFixTest(unittest.TestCase):
    """P1049: a stop_result with `doctor_for` (grant.py, bench.py record) says a no_port or port_not_listed stop as look.py
    does when firmware/ calls deepsleep: its sentence, then slice 3's asleep fix, which is the Finding's fix too."""

    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        (self.project / "firmware").mkdir()
        (self.project / "firmware" / "main.py").write_text("import machine\nmachine.deepsleep(1)\n")
        self.no_port = board_look.LookStopError(NO_BOARD, reason="no_port")

    def test_no_port_gives_no_board_found_then_the_asleep_fix(self):
        said = stop_result(self.no_port, "grant.py", self.project, None, stops.undoctored("grant.py"))
        self.assertEqual(len(said.diagnostics), 2, said.diagnostics)
        self.assertEqual(said.diagnostics[0], "grant.py: no board found.")
        fix = said.diagnostics[1]
        self.assertTrue(fix.startswith("What spark knows: no board is on USB, and the project's firmware calls deepsleep "
                                       "(firmware/main.py:2)."), fix)
        (found,) = said.findings
        self.assertEqual((found.code, found.sentence, found.fix), ("no_port", "no board found.", fix))

    def test_a_named_port_not_listed_keeps_its_sentence_and_the_fix_opens_with_that_port(self):
        stop = board_look.LookStopError("no board on %s: mpremote devs does not list it.", "/dev/cu.usbmodem9", reason="port_not_listed")
        said = stop_result(stop, "grant.py", self.project, "/dev/cu.usbmodem9", stops.undoctored("grant.py"))
        self.assertEqual(len(said.diagnostics), 2, said.diagnostics)
        self.assertEqual(said.diagnostics[0], "grant.py: no board on /dev/cu.usbmodem9: mpremote devs does not list it.")
        self.assertTrue(said.diagnostics[1].startswith("What spark knows: the port you named is not on USB, and"), said.diagnostics[1])
        (found,) = said.findings
        self.assertEqual((found.code, found.sentence, found.fix),
                         ("port_not_listed", "no board on /dev/cu.usbmodem9: mpremote devs does not list it.", said.diagnostics[1]))

    def test_without_a_deepsleep_call_and_without_doctor_for_the_stop_is_as_before(self):
        # live.py and reach.py give no doctor_for: their stops keep today's words until P1057
        said = stop_result(self.no_port, "live.py", self.project, None)
        self.assertEqual((said.diagnostics, said.findings[0].sentence, said.findings[0].fix), (["live.py: " + NO_BOARD], NO_BOARD, ""))
        (self.project / "firmware" / "main.py").write_text("import machine\nmachine.lightsleep(1)\n")
        said = stop_result(self.no_port, "grant.py", self.project, None, stops.undoctored("grant.py"))
        self.assertEqual((said.diagnostics, said.findings[0].sentence, said.findings[0].fix), (["grant.py: " + NO_BOARD], NO_BOARD, ""))

    def test_a_file_that_does_not_parse_keeps_the_stop_s_own_words_and_no_fix(self):
        # the review of #1569, refuter 1: UNPARSED is a fact with no step, so it never takes the place of the script's fix
        (self.project / "firmware" / "main.py").write_text("import machine\nmachine.deepsleep(1\n")
        said = stop_result(self.no_port, "grant.py", self.project, None, stops.undoctored("grant.py"))
        self.assertEqual((said.diagnostics, said.findings[0].sentence, said.findings[0].fix), (["grant.py: " + NO_BOARD], NO_BOARD, ""))

    def test_the_asleep_fix_comes_with_the_look_step_and_no_other_stop_does(self):
        # P1048: the fix's step 1 names look.py, so `next` names it, for the person to run after their hands
        (step,) = stop_result(self.no_port, "grant.py", self.project, None, stops.undoctored("grant.py")).next
        self.assertEqual((step.op, step.argv, step.needs_person, step.needs_yes), ("look", ["--project", str(self.project)], True, False))
        self.assertEqual(stop_result(self.no_port, "live.py", self.project, None).next, [])  # no doctor_for (P1057)
        for main in ("import machine\nmachine.lightsleep(1)\n", "import machine\nmachine.deepsleep(1\n"):
            with self.subTest(main=main):
                (self.project / "firmware" / "main.py").write_text(main)
                self.assertEqual(stop_result(self.no_port, "grant.py", self.project, None, stops.undoctored("grant.py")).next, [])


class AStopsDataIsItsOwnTest(unittest.TestCase):
    """A frontend may add to a result's data, and the next stop's data stays as it was."""

    def test_a_change_to_one_stop_s_data_leaves_the_next_stop_s_data(self):
        class NoMpremote:
            def __init__(self, project, find_tool):
                pass

            def make_port_finder(self, run):
                raise tool_finder.ToolError("no mpremote", code="tool_missing")
        project = Path(tempfile.mkdtemp())
        check = CheckGrant(platform_for=NoMpremote)
        first = check.run(project, None, outside=FakeOutsideWorld())
        first.data["granted"] = True
        second = check.run(project, None, outside=FakeOutsideWorld())
        self.assertEqual(second.data, {"granted": False, "why": "could not run", "grant": None})
# --- end MVP ---


if __name__ == "__main__":
    unittest.main()
