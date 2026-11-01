"""P475 (W4-1): the platform hands each board tool its role's tool, and a Fake platform stands in for it without a patch."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_look  # noqa: E402
import firmware_platform  # noqa: E402
import tools  # noqa: E402
from fakes import FakeBoardReader, FakeFirmwarePlatform  # noqa: E402

from test_deploy import FOUND  # noqa: E402

ESPTOOL, MPREMOTE = FOUND["flasher"], FOUND["board-shell"]
find = FOUND.__getitem__


class MicroPythonPlatformTest(unittest.TestCase):
    def setUp(self):
        self.project = Path(tempfile.mkdtemp())
        (self.project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": []}))
        self.platform = firmware_platform.MicroPythonPlatform(self.project, find)

    def test_the_flasher_is_esptool_for_the_records_chip(self):
        made = self.platform.make_flasher()
        self.assertEqual((made.tool, made.chip), (ESPTOOL, "esp32c6"))

    def test_the_shell_command_is_the_board_shell_s(self):
        self.assertEqual(self.platform.make_shell_command(), tools.command_for(MPREMOTE))

    def test_the_port_finder_lists_with_the_board_shell_and_the_reader_reads_with_the_flasher(self):
        ran = []
        run = lambda command, **kw: ran.append(command)  # noqa: E731
        self.assertEqual(self.platform.make_port_finder(run).command, tools.command_for(MPREMOTE) + ["devs"])
        reader = self.platform.make_board_reader(run, "try the button")
        self.assertEqual((reader.flasher_tool, reader.boot_hint), (ESPTOOL, "try the button"))

    def test_the_console_probe_is_for_the_board_shell_and_the_port(self):
        probe = self.platform.make_console_probe("/dev/cu.usbmodem101", None)
        self.assertEqual((probe.python, probe.port), (MPREMOTE.command, "/dev/cu.usbmodem101"))

    def test_a_missing_tool_shows_when_a_step_asks_for_it_not_before(self):
        def missing(role):
            raise tools.ToolProblem("%s is not installed" % role)
        platform = firmware_platform.MicroPythonPlatform(self.project, missing)  # builds
        with self.assertRaises(tools.ToolProblem):
            platform.make_port_finder(None)


class LookerTest(unittest.TestCase):
    def test_the_reader_gets_the_hint_that_names_the_project_s_buttons(self):
        project = Path(tempfile.mkdtemp())
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": []}))
        platform = FakeFirmwarePlatform(project, port_finder=object(), board_reader=FakeBoardReader())
        board_look.looker(platform)
        self.assertEqual(len(platform.hints), 1)
        self.assertIn("hold the board's BOOT button (B, top right", platform.hints[0])


class FakeFirmwarePlatformTest(unittest.TestCase):
    def test_a_part_the_test_gave_is_handed_out_and_one_it_did_not_give_fails_loudly(self):
        platform = FakeFirmwarePlatform(console_probe="probe")
        self.assertEqual(platform.make_console_probe("/dev/x", None), "probe")
        with self.assertRaises(AssertionError):
            platform.make_flasher()

    def test_a_part_that_is_an_exception_is_raised(self):
        with self.assertRaises(tools.ToolProblem):
            FakeFirmwarePlatform(port_finder=tools.ToolProblem("no mpremote")).make_port_finder(None)

    def test_a_fake_board_reader_gives_its_readings_in_turn_and_keeps_the_ports(self):
        stop = board_look.LookStop("could not read", reason="board_not_read")
        reader = FakeBoardReader("first", stop)
        self.assertEqual(reader.read("/dev/a"), "first")
        with self.assertRaises(board_look.LookStop):
            reader.read("/dev/b")
        self.assertEqual(reader.read_ports, ["/dev/a", "/dev/b"])


if __name__ == "__main__":
    unittest.main()
