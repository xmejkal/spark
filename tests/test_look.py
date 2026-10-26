"""P219 step 3 (#201): look.py prints what the look found, in the lines a person reads, and changes nothing on the board."""

import contextlib
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_doctor  # noqa: E402
import flash_image  # noqa: E402
import look  # noqa: E402
import tools  # noqa: E402
from test_board_look import FOUND, LookCase, data, done, found  # noqa: E402

RESTART = "  the board restarts while it is read: a running program stops and starts again. Nothing is erased or written."
MAC = "8c:bf:ea:xx:xx:xx"
#: LookCase's scenario only waits for text, so its passed run presses nothing and reads no pin (P345): the look says so.
SIMULATION = "  simulation: passed"
CAVEAT = ("  the passed run's scenario has no set-control step (the step that presses a button or sets a sensor) and no "
          "expect-pin step (the step that reads a pin)")
NO_BOARD = ("no board found. Plug it straight into the computer with a data cable, not a hub that gives power only. "
            "If the plug is USB-C, turn it around, or use a USB-A to USB-C cable.")


class LookScriptCase(LookCase):
    def go(self, *argv, devs="mpremote-devs-one.txt", esptool="c6-flash-id.txt", text=None, fail=False):
        """(exit code, stdout lines, stderr) of look.py with fake tools. The fakes answer from the fixtures."""
        def run(command, **kw):
            self.ran.append(command)
            return done(data(devs)) if "devs" in command else done(text or data(esptool), 1 if fail else 0)

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(tools, "find", side_effect=lambda name, *a, **k: FOUND["flasher"] if name == "flasher" else found(name)), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = look.main(["--project", str(self.project), *argv], run=run)
        return code, out.getvalue().splitlines(), err.getvalue()

    def build_from_firmware(self):
        """The image of firmware/ with no run, as flash_image.py writes it."""
        patcher = mock.patch.object(flash_image, "interpreter_for",
                                    side_effect=lambda given, project=None: flash_image.Interpreter(self.micropython, 0))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.image.write_bytes(flash_image.image(self.micropython.read_bytes(), flash_image.files_under(self.project / "firmware")))

    def token(self):
        return "%s-%s" % (hashlib.sha256(MAC.encode()).hexdigest()[:4], hashlib.sha256(self.image.read_bytes()).hexdigest()[:4])


class WhatThePersonSeesTest(LookScriptCase):
    def test_a_matching_board(self):
        self.run_the_scenario()
        code, said, problems = self.go()
        self.assertEqual((code, problems), (0, ""))
        self.assertEqual(said, [
            RESTART,
            "  port   /dev/cu.usbmodem101",
            "  mac    " + MAC,
            "  spark's last deploy here: none in its store record (it keeps only its own deploys)",
            "  chip   same      esp32c6",
            "  flash  same      4 MB",
            SIMULATION, CAVEAT,
            "  all fields match the board record xiao-esp32-c6.",
            "  token  %s  for deploy.py --token. It is not your yes: deploy.py asks for that." % self.token()])

    def test_a_flash_that_differs_but_holds_the_image_is_a_warning_with_its_token(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go(esptool="s3-flash-id-8mb.txt")
        self.assertEqual(code, 1)
        self.assertEqual(said[4:7], ["  chip   same      esp32s3", "  flash  differs   8 MB",
                                     "  the flash differs: 8 MB, the record says 16 or 4. deploy.py will ask you to accept it."])
        self.assertEqual(said[7:9], [SIMULATION, CAVEAT])
        self.assertTrue(said[9].startswith("  token  "))

    def test_a_field_the_board_did_not_say_is_unknown_and_the_look_could_not_check_it(self):
        self.run_the_scenario()
        code, said, _ = self.go(esptool="c6-flash-id-garbled.txt")
        self.assertEqual(code, 2)
        self.assertIn("  flash  unknown   not read", said)
        self.assertIn("  1 field unknown (flash: the board did not say): deploy.py will ask you to accept it.", said)
        self.assertTrue(said[-1].startswith("  token  "))

    def test_a_port_with_a_newline_and_a_right_to_left_override_shows_as_one_line_with_question_marks(self):
        # P423: the report's items are guarded one by one, so a newline in a value cannot fake a line of the look
        self.run_the_scenario()
        port = "/dev/cu.usb\u202emodem\n  token  FAKE"
        code, said, _ = self.go("--port", port)
        self.assertEqual(said[1], "  port   /dev/cu.usb?modem?  token  FAKE")
        self.assertEqual(len([line for line in said if line.startswith("  token  ")]), 1)
        self.assertEqual(json.loads(self.go("--port", port, "--json")[1][-1])["data"]["port"], port)  # --json keeps it raw

    def test_a_port_with_an_override_shows_as_a_question_mark_in_the_stop_on_stderr(self):
        # P423: the failed read's lines go through guard_lines too
        self.run_the_scenario()
        with mock.patch.object(board_doctor, "after_esptool", return_value=None):
            code, _, problems = self.go("--port", "/dev/cu.usb\u202emodem", fail=True)
        self.assertEqual(code, 2)
        self.assertTrue(problems.startswith("look.py: could not read the board on /dev/cu.usb?modem."), problems)

    def test_another_chip_is_a_stop_with_no_token(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go()
        self.assertEqual(code, 1)
        self.assertEqual(said[4], "  chip   differs   esp32c6")
        self.assertEqual(said[-4:], ["  this board is an esp32c6, the project is for an esp32s3: deploy.py will refuse.",
                                     SIMULATION, CAVEAT, "  no token: the look found a stop"])

    def test_a_flash_too_small_for_the_image_is_a_stop_even_when_the_record_lists_it(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go(esptool="s3-flash-id-2mb.txt")
        self.assertEqual(code, 1)
        self.assertIn("  the flash is 2 MB, the image needs 4 MB: deploy.py will refuse.", said)
        self.assertEqual(said[-1], "  no token: the look found a stop")

    def test_a_flash_in_the_records_list_that_is_too_small_exits_1_not_0(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        self.image.write_bytes(self.image.read_bytes() + b"x")
        code, said, _ = self.go(text=data("s3-flash-id-16mb.txt").replace("16MB", "4MB"))
        self.assertEqual(code, 1)
        self.assertIn("  flash  same      4 MB", said)

    def test_no_image_prints_the_fields_and_says_why_there_is_no_token(self):
        code, said, _ = self.go()
        self.assertEqual(code, 2)
        self.assertEqual(said[4:6], ["  chip   same      esp32c6", "  flash  same      4 MB"])
        self.assertEqual(said[-2], "  all fields match the board record xiao-esp32-c6.")
        self.assertRegex(said[-1], r"^  no token: .*run a scenario first")

    def test_ignore_older_runs_gives_a_token_where_an_older_log_tested_another_image(self):
        self.run_the_scenario()
        (self.project / "firmware" / "main.py").write_text("print('ready')\nprint(2)\n")
        other = self.scenario.with_name("t.scenario.yaml")
        other.write_text(self.scenario.read_text().replace("name: s", "name: t"))
        self.run_the_scenario(scenario=other)
        code, said, _ = self.go()
        self.assertEqual(code, 2)
        self.assertRegex(said[-1], r"^  no token: .*tested another image")
        code, said, _ = self.go("--ignore-older-runs")
        self.assertEqual(code, 0)
        self.assertEqual(said[-1], "  token  %s  for deploy.py --token. It is not your yes: deploy.py asks for that." % self.token())

    def test_no_simulation_gives_a_token_for_firmware_as_it_is_with_no_run_log(self):
        self.build_from_firmware()
        code, said, _ = self.go()
        self.assertEqual(code, 2)
        self.assertRegex(said[-1], r"^  no token: .*no run in sim/runs/ tested")
        code, said, _ = self.go("--no-simulation")
        self.assertEqual(code, 0)
        self.assertEqual(said[-1], "  token  %s  for deploy.py --token. It is not your yes: deploy.py asks for that." % self.token())

    def test_no_simulation_with_firmware_changed_after_the_image_gives_no_token_and_the_build_command(self):
        self.build_from_firmware()
        (self.project / "firmware" / "main.py").write_text("print('ready')\nprint(3)\n")
        code, said, _ = self.go("--no-simulation")
        self.assertEqual(code, 2)
        self.assertRegex(said[-1], r"^  no token: .*flash_image\.py --project .* --files firmware -o ")

    def test_the_json_look_says_none_and_its_deploy_step_carries_the_flag(self):
        self.build_from_firmware()
        code, said, _ = self.go("--no-simulation", "--json")
        envelope = json.loads(said[-1])
        self.assertEqual((code, envelope["data"]["simulation"]), (0, "none"))
        self.assertIn("--no-simulation", envelope["next"][0]["argv"])

    def test_the_json_look_carries_the_simulation_and_the_caveats_of_the_passed_run(self):
        self.run_the_scenario()
        data_ = json.loads(self.go("--json")[1][-1])["data"]
        self.assertEqual((data_["simulation"], len(data_["caveats"])), ("passed", 1))
        self.assertTrue(data_["caveats"][0].startswith("the passed run's scenario has no set-control step"))

    def test_the_json_look_carries_the_last_deploy_flat(self):
        self.run_the_scenario()
        data_ = json.loads(self.go("--json")[1][-1])["data"]
        self.assertEqual(data_["last_deploy"], {"state": "none-recorded", "why": None, "project": None, "verdict": None,
                                                "deployed": None})

    def test_the_json_look_of_an_image_no_run_tested_says_null_and_no_caveat(self):
        self.build_from_firmware()
        data_ = json.loads(self.go("--json")[1][-1])["data"]
        self.assertEqual((data_["simulation"], data_["caveats"]), (None, []))

    def test_the_text_look_says_none_and_its_caveat_with_the_flag(self):
        self.build_from_firmware()
        said = self.go("--no-simulation")[1]
        self.assertEqual(said[said.index("  simulation: none"):][:2], ["  simulation: none", "  no simulation tested this image"])

    def test_the_next_step_names_a_deploy_grant_only_where_a_grant_may_answer(self):
        self.build_from_firmware()
        none = json.loads(self.go("--no-simulation", "--json")[1][-1])["next"][0]["why"]
        self.assertIn("types yes in their own terminal;", none)
        self.assertNotIn("grant", none)
        self.run_the_scenario()
        passed = json.loads(self.go("--json")[1][-1])["next"][0]["why"]
        self.assertIn("or a deploy grant stands", passed)

    def test_both_flags_are_an_argument_error(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            self.go("--no-simulation", "--ignore-older-runs")

    def test_no_mac_is_no_token(self):
        self.run_the_scenario()
        code, said, _ = self.go(esptool="c6-flash-id-no-mac.txt")
        self.assertEqual(code, 2)
        self.assertIn("  mac    not read", said)
        self.assertEqual(said[-1], "  no token: the board's MAC could not be read")


class WhatStopsTheLookTest(LookScriptCase):
    def stops(self, *argv, expected=2, **kw):
        code, said, problems = self.go(*argv, **kw)
        self.assertEqual((code, said), (expected, []))
        return problems

    def test_no_board_on_usb(self):
        self.assertEqual(self.stops(devs="mpremote-devs-none.txt"), "look.py: %s\n" % NO_BOARD)

    def test_two_boards_list_port_serial_product_and_the_command_to_copy(self):
        self.assertEqual(self.stops(devs="mpremote-devs-two.txt").splitlines(), [
            "look.py: 2 boards on USB:",
            "  /dev/cu.usbmodem101  8c:bf:ea:xx:xx:xx  Espressif USB JTAG/serial debug unit",
            "  /dev/cu.usbserial-1410  None  USB Serial",
            "look.py --port /dev/cu.usbmodem101  (unplug one to tell them apart)"])
        self.assertFalse([each for each in self.ran if "flash_id" in each])  # none was read: each read restarts a board

    def test_two_boards_with_a_port_reads_that_one(self):
        self.run_the_scenario()
        code, said, _ = self.go("--port", "/dev/cu.usbserial-1410", devs="mpremote-devs-two.txt")
        self.assertEqual(code, 0)
        self.assertEqual(said[1], "  port   /dev/cu.usbserial-1410")

    def test_no_record_for_the_board(self):
        self.board("no-such-board")
        self.assertEqual(self.stops(), "look.py: no board record for no-such-board: P230 will research one.\n")

    def test_requirements_naming_no_board(self):
        (self.project / "requirements.json").write_text("{}")
        self.assertEqual(self.stops(), "look.py: requirements.json names no board\n")

    def test_a_tool_that_is_missing(self):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(tools, "find", side_effect=tools.ToolProblem("no esptool")), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = look.main(["--project", str(self.project)])
        self.assertEqual((code, out.getvalue(), err.getvalue()), (2, "", "look.py: no esptool\n"))


class TheHelpTest(unittest.TestCase):
    def test_help_says_what_it_reads_what_it_changes_the_restart_the_token_and_the_exit_codes(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            look.main(["--help"])
        said = " ".join(out.getvalue().split())
        for words in ("--project", "--port", "writes nothing", "erases nothing", "restarts", "token", "Exit codes", "0 ", "1 ", "2 "):
            self.assertIn(words, said)


if __name__ == "__main__":
    unittest.main()
