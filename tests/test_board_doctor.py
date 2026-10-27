"""P282 (#326): the board doctor says what is true and one next step, from codes, never from a tool's words."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_doctor  # noqa: E402
import boards  # noqa: E402
import tools  # noqa: E402
from board_console import ConsoleReadResult  # noqa: E402
from board_look import LookStop, Port  # noqa: E402

PORT = "/dev/cu.usbmodem1101"
C6 = Port(PORT, "8C:BF:EA:CC:97:70", "303a:1001", "Espressif USB JTAG/serial debug unit")
DEFAULTS = json.loads((ROOT / "data" / "tools.json").read_text())
ESPTOOL = tools.Tool("esptool", "flasher", DEFAULTS["esptool"], ["/opt/python3", "-m", "esptool"])
MPREMOTE = tools.Tool("mpremote", "board-shell", DEFAULTS["mpremote"], ["/opt/python3", "-m", "mpremote"])
SAID = "ERROR: A fatal error occurred: Failed to connect to Espressif device: No serial data received."


class FakeFinder:
    def __init__(self, *boards, raises=None):
        self.listed, self.raises = list(boards), raises

    def nodes(self):
        if self.raises:
            raise self.raises
        return self.listed


class FakeProbe:
    """A ConsoleProbe that reads `read` once and counts the reads."""

    def __init__(self, read):
        self.read, self.reads = read, 0

    def console(self):
        self.reads += 1
        return self.read


def examine(read, tool=ESPTOOL, finder=None, said=SAID):
    probe = None if read is None else FakeProbe(read)
    doctor = board_doctor.BoardDoctorService.for_board(finder or FakeFinder(C6), probe)
    return doctor.examine(PORT, tool, said), probe


class StepTest(unittest.TestCase):
    def test_a_silent_board_after_esptool_is_hold_boot_and_esptool_s_words_are_kept(self):
        result, probe = examine(ConsoleReadResult("read", "", None))
        self.assertEqual((result.next_step, result.if_not_helped, result.tool_said), ("hold_boot", None, SAID))
        self.assertEqual([check.name for check in result.checks], ["port-listed", "console"])
        self.assertIn("USB serial 8C:BF:EA:CC:97:70", result.checks[0].fact)
        self.assertEqual(probe.reads, 1)

    def test_a_silent_board_after_mpremote_is_press_reset_then_replug(self):
        result, _ = examine(ConsoleReadResult("read", "", None), tool=MPREMOTE)
        self.assertEqual((result.next_step, result.if_not_helped), ("press_reset", "replug"))

    def test_a_port_not_listed_is_plug_in_and_the_console_is_not_opened(self):
        result, probe = examine(ConsoleReadResult("read", "", None), finder=FakeFinder())
        self.assertEqual(result.next_step, "plug_in")
        self.assertEqual(probe.reads, 0)

    def test_a_port_another_program_holds_is_close_other(self):
        result, _ = examine(ConsoleReadResult("busy", "", "Could not exclusively lock port"))
        self.assertEqual(result.next_step, "close_other")
        self.assertEqual(board_doctor.step_sentence(result.next_step),  # P354: the console that walk 1 left open
                         "another program holds the port, often mpremote's console: leave mpremote's console with "
                         "Ctrl-X, or close the other program, and run it again")

    def test_download_mode_is_press_reset_for_mpremote_and_run_again_for_esptool(self):
        rom = "ESP-ROM:esp32c6-20220919\nboot:0x4 (DOWNLOAD(USB/UART0/SDIO_FEI_FEO))\nwaiting for download\n"
        after_mpremote, _ = examine(ConsoleReadResult("read", rom, None), tool=MPREMOTE)
        after_esptool, _ = examine(ConsoleReadResult("read", rom, None))
        self.assertEqual((after_mpremote.next_step, after_esptool.next_step), ("press_reset", "run_again"))

    def test_a_boot_heard_on_the_doctor_s_open_is_run_again(self):
        result, _ = examine(ConsoleReadResult("read", "rst:0x15 (USB_UART_HPSYS),boot:0x1e\nready\n", None))
        self.assertEqual(result.next_step, "run_again")

    def test_firmware_text_with_no_boot_is_the_tool_s_silent_step_with_the_text_as_fact(self):
        result, _ = examine(ConsoleReadResult("read", "LED on\nLED off\n", None))
        self.assertEqual((result.next_step, result.checks[-1].fact), ("hold_boot", "the console printed: LED off"))

    def test_a_console_it_could_not_read_names_no_step_and_says_so(self):
        result, _ = examine(ConsoleReadResult("unread", "", "no module named serial"))
        self.assertIsNone(result.next_step)
        self.assertIn("next    no step: the doctor could not look", board_doctor.describe(result))

    def test_no_probe_gives_the_silent_step_and_says_the_console_was_not_read(self):
        result, _ = examine(None, tool=MPREMOTE)
        self.assertEqual(result.next_step, "press_reset")
        self.assertIn("not read", result.checks[-1].fact)

    def test_a_list_that_fails_keeps_its_error_and_the_console_still_looks(self):
        result, _ = examine(ConsoleReadResult("read", "", None), finder=FakeFinder(raises=LookStop("mpremote took too long", reason="list_timeout")))
        self.assertIn("mpremote took too long", result.checks[0].fact)
        self.assertEqual(result.next_step, "hold_boot")


class ConfigurationTest(unittest.TestCase):
    def test_a_layer_that_changes_the_silent_step_changes_the_step(self):
        mine = tools.Tool("esptool", "flasher", dict(DEFAULTS["esptool"], silent_step="press_reset"), [])
        result, _ = examine(ConsoleReadResult("read", "", None), tool=mine)
        self.assertEqual(result.next_step, "press_reset")

    def test_an_unknown_silent_step_is_an_error_that_names_the_tool(self):
        with self.assertRaises(board_doctor.UnknownStepError) as stop:
            examine(ConsoleReadResult("read", "", None),
                    tool=tools.Tool("esptool", "flasher", dict(DEFAULTS["esptool"], silent_step="erase"), []))
        self.assertIn("esptool", str(stop.exception))

    def test_a_tool_of_the_person_s_own_with_no_silent_step_still_gets_the_checks(self):
        own = tools.Tool("my-shell", "board-shell", {"kind": "path"}, [])
        busy, _ = examine(ConsoleReadResult("busy", "", "locked"), tool=own)
        silent, _ = examine(ConsoleReadResult("read", "", None), tool=own)
        self.assertEqual((busy.next_step, silent.next_step), ("close_other", None))


class EsptoolStopTest(unittest.TestCase):
    def test_a_stop_with_no_port_prints_only_the_stop(self):
        self.assertEqual(board_doctor.stop_lines("look.py", LookStop("requirements.json names no board", reason="no_board_named"), ".", None),
                         ["look.py: requirements.json names no board"])

    def test_a_tools_list_it_cannot_use_keeps_the_stop_and_says_no_doctor(self):
        from unittest import mock
        stop = LookStop("could not read the board on %s" % PORT, PORT, SAID, reason="board_not_read")
        with mock.patch.object(tools, "find", side_effect=tools.ToolProblem("mpremote is not installed")):
            lines = board_doctor.stop_lines("grant.py", stop, ".", None)
        self.assertEqual(lines, ["grant.py: could not read the board on %s (no doctor: mpremote is not installed)" % PORT])


class OutputTest(unittest.TestCase):
    def test_the_lines_say_the_tool_s_words_each_check_and_the_steps(self):
        result, _ = examine(ConsoleReadResult("read", "", None), tool=MPREMOTE, said="could not enter raw repl")
        self.assertEqual(board_doctor.describe(result), [
            "said    could not enter raw repl",
            "check   port-listed: mpremote devs lists /dev/cu.usbmodem1101, USB serial 8C:BF:EA:CC:97:70",
            "check   console: the console was silent for 2 s",
            "next    press the board's RESET once and run it again",
            "if not  unplug the board, plug it in again, and run it again"])

    def test_the_two_button_steps_name_the_places_when_given_them(self):
        places = boards.ButtonPlaces.from_record({"physical": {"buttons": {
            "seen_from": "the shield facing you", "boot": {"silkscreen": "B", "place": "top right"},
            "reset": {"silkscreen": "R", "place": "top left"}}}})
        self.assertEqual(board_doctor.step_sentence("press_reset", places),
                         "press the board's RESET (R, top left) once and run it again. Left and right as seen with the shield facing you")
        self.assertEqual(board_doctor.step_sentence("hold_boot", places),
                         "hold the board's BOOT button (B, top right), press and release RESET (R, top left), release BOOT, "
                         "and run it again. After it, press RESET once so the firmware starts. Left and right as seen "
                         "with the shield facing you")
        result, _ = examine(ConsoleReadResult("read", "", None), tool=MPREMOTE)
        self.assertIn("next    press the board's RESET (R, top left) once and run it again. Left and right as seen with the shield "
                      "facing you", board_doctor.describe(result, places))
        self.assertIn("press the board's RESET once and run it again", board_doctor.step_sentence("press_reset"))

    def test_a_step_without_a_button_is_the_same_with_or_without_places(self):
        self.assertEqual(board_doctor.step_sentence("replug"),
                         "unplug the board, plug it in again, and run it again")

    def test_the_json_holds_codes_and_never_a_pass(self):
        result, _ = examine(ConsoleReadResult("read", "", None))
        line = json.loads(json.dumps(board_doctor.as_dict(result)))
        self.assertEqual(sorted(line), ["checks", "if_not_helped", "next_step", "tool_said"])
        self.assertFalse(line["checks"][-1]["passed"])


if __name__ == "__main__":
    unittest.main()
