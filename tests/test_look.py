"""P219 step 3 (#201): look.py prints what the look found, in the lines a person reads, and changes nothing on the board."""

import ast
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_doctor  # noqa: E402
import deploy_gate  # noqa: E402
import boards  # noqa: E402
import flash_image  # noqa: E402
import look  # noqa: E402
import sim_project  # noqa: E402
import tools  # noqa: E402
from fakes import FakeConsent, FakeOutsideWorld  # noqa: E402
from spark.core import outcomes  # noqa: E402
from test_board_look import LookCase, data, done, found  # noqa: E402

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

        return self.go_with(FakeOutsideWorld(run=run, find_tool=found), *argv)

    def go_with(self, outside, *argv):
        """(exit code, stdout lines, stderr) of look.py on `outside`, a FakeOutsideWorld, so no test patches tools.find (P442)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = look.main(["--project", str(self.project), *argv], outside=outside)
        return code, out.getvalue().splitlines(), err.getvalue()

    def build_from_firmware(self):
        """The image of firmware/ with no run, as flash_image.py writes it."""
        patcher = mock.patch.object(flash_image, "interpreter_for",
                                    side_effect=lambda given, project=None, find_tool=None: flash_image.Interpreter(self.micropython, 0))
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

    def run_the_scenario_with_a_note(self):
        (self.project / "sim" / "WHAT-THIS-CANNOT-SHOW.md").write_text(
            sim_project.limits_note([("ONBOARD_DISPLAY", "no part for the display. Test it on the board.")]))
        self.run_the_scenario()

    def test_the_text_look_lists_the_limits_of_the_passed_run_after_the_caveat(self):
        self.run_the_scenario_with_a_note()
        code, said, _ = self.go()
        self.assertEqual(code, 0)
        self.assertEqual(said[6:10], [
            SIMULATION, CAVEAT, "  what this simulation cannot show, so test it on the board:",
            "  - ONBOARD_DISPLAY — no part for the display. Test it on the board."])

    def test_the_json_look_carries_the_limits_of_the_passed_run(self):
        self.run_the_scenario_with_a_note()
        data = json.loads(self.go("--json")[1][-1])["data"]
        self.assertEqual(data["limits"], [{"component": "ONBOARD_DISPLAY", "sentence": "no part for the display. Test it on the board."}])

    def test_a_passed_run_of_a_project_with_no_note_has_no_limits_and_no_heading(self):
        self.run_the_scenario()
        code, said, _ = self.go()
        self.assertFalse([line for line in said if "cannot show" in line])
        self.assertEqual(json.loads(self.go("--json")[1][-1])["data"]["limits"], [])

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

    def test_a_newline_in_the_port_cannot_fake_a_line_of_the_stop_and_json_keeps_the_port_raw(self):
        # P430: the port goes into the stop's first line, so it is put on one line before the stop is guarded
        self.run_the_scenario()
        port = "/dev/x\nGRANTED"
        code, _, problems = self.go("--port", port, fail=True)
        self.assertEqual(code, 2)
        self.assertTrue(problems.startswith("look.py: could not read the board on /dev/x?GRANTED"), problems)
        self.assertEqual([line for line in problems.splitlines() if line.startswith("GRANTED")], [])
        said = self.go("--port", port, "--json", fail=True)[1][-1]
        self.assertIn(json.dumps(port)[1:-1], said)  # the envelope's text holds the port as typed, JSON-escaped
        self.assertIn("/dev/x?GRANTED", problems)

    def test_a_newline_in_a_button_word_of_the_board_record_cannot_fake_a_line_of_the_stop(self):
        # P430: the doctor's step holds the record's button words, which `guard_lines` would let break the line
        self.run_the_scenario()
        record = {"physical": {"buttons": {"seen_from": "the shield", "boot": {"silkscreen": "B\nGRANTED: fake", "place": "top"},
                                           "reset": {"silkscreen": "R", "place": "left"}}}}
        with mock.patch.object(boards.ButtonPlaces, "of_project", return_value=boards.ButtonPlaces.from_record(record)):
            code, _, problems = self.go(fail=True, text="Connecting......\nA fatal error occurred: No serial data received.\n")
        self.assertEqual(code, 2)
        self.assertIn("BOOT button (B?GRANTED: fake, top)", problems)
        self.assertEqual([line for line in problems.splitlines() if line.startswith("GRANTED")], [])

    def test_a_newline_in_the_project_path_cannot_fake_a_line_of_a_tool_problem_stop(self):
        # P430: looker turns a ToolProblem into a stop whose text holds the project's tools file path
        project = Path(tempfile.mkdtemp()) / "a\nGRANTED (deploy): board ok"
        (project / ".spark").mkdir(parents=True)
        (project / ".spark" / "tools.json").write_text("not json")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = look.main(["--project", str(project)])
        self.assertEqual(code, 2)
        self.assertIn("a?GRANTED (deploy): board ok", err.getvalue())
        self.assertEqual([line for line in err.getvalue().splitlines() if line.startswith("GRANTED")], [])

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

    def test_a_firmware_line_that_is_no_string_stops_the_token_with_one_sentence_and_no_traceback(self):
        # P429: `firmware = 3` raised a TypeError out of the look
        (self.project / "sim" / "wokwi.toml").write_text("[wokwi]\nversion = 1\nfirmware = 3\n")
        code, said, problems = self.go()
        self.assertEqual((code, problems), (2, ""))
        self.assertEqual(said[-1], "  no token: sim/wokwi.toml line 3 names the firmware in a form spark cannot read. "
                         'To fix it, write it as firmware = "name.bin".')

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

    def test_no_simulation_with_a_finder_that_lacks_littlefs_gives_no_token_and_the_install_line(self):
        # P442: the image check asks the finder the look was given, not tools.find, so the fake decides what is installed
        self.build_from_firmware()

        def without_littlefs(name):
            return found(name) if name != "littlefs" else found("not-installed")
        code, said, _ = self.go_with(FakeOutsideWorld(run=lambda command, **kw: done(data("mpremote-devs-one.txt")) if "devs" in command
                                                      else done(data("c6-flash-id.txt")), find_tool=without_littlefs), "--no-simulation", "--json")
        self.assertEqual(code, 2)
        no_token = [item for item in json.loads(said[-1])["unchecked"] if item["sentence"].startswith("no token: ")]
        self.assertEqual([item["code"] for item in no_token], ["tool_missing"])
        self.assertIn("not-installed is not installed", no_token[0]["sentence"])

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

    def brief_with_must(self, *must):
        (self.project / ".spark").mkdir(exist_ok=True)
        (self.project / ".spark" / "project.json").write_text(json.dumps({"must": list(must)}))

    def run_without_step_names(self):
        """A passed run whose log is from before step names: its header holds no names marker and no name line."""
        self.run_the_scenario()
        log = next((self.project / "sim" / "runs").glob("*.log"))
        log.write_text("".join(line for line in log.read_text().splitlines(True) if not line.startswith(("step names: ", "step name: "))))

    def not_checked(self, data_):
        return [each for each in data_["caveats"] if each.startswith(outcomes.NOT_CHECKED_MESSAGE.split("%s")[0])]

    def test_the_look_exits_0_and_lists_the_unnamed_must_lines_in_text_and_json(self):
        self.brief_with_must("the LED lights", "the LED goes off")
        self.run_the_scenario()
        code, said, _ = self.go()
        self.assertEqual(code, 0)
        self.assertEqual(said[said.index("  no scenario named these must lines, so test them on the board:") + 1:][:2], ["  - the LED lights", "  - the LED goes off"])
        code, lines, _ = self.go("--json")
        data_ = json.loads(lines[-1])["data"]
        self.assertEqual((code, data_["unnamed_must"], self.not_checked(data_)), (0, ["the LED lights", "the LED goes off"], []))

    def test_the_caveats_hold_not_checked_exactly_when_a_log_could_not_say(self):
        self.brief_with_must("the LED lights")
        self.run_without_step_names()
        code, lines, _ = self.go("--json")
        data_ = json.loads(lines[-1])["data"]
        self.assertEqual((code, data_["unnamed_must"], len(self.not_checked(data_))), (0, [], 1))
        self.assertEqual(json.loads(lines[-1])["status"], "ok")

    def test_an_older_log_and_no_must_line_say_nothing(self):
        self.brief_with_must()
        self.run_without_step_names()
        code, lines, _ = self.go("--json")
        data_ = json.loads(lines[-1])["data"]
        self.assertEqual((code, data_["unnamed_must"], self.not_checked(data_)), (0, [], []))

    def test_a_scenario_that_names_every_must_line_says_nothing(self):
        self.brief_with_must("the LED lights")
        self.scenario.write_text("name: s\nversion: 1\nsteps:\n  - name: the LED lights\n    wait-serial: on\n")
        self.run_the_scenario()
        data_ = json.loads(self.go("--json")[1][-1])["data"]
        self.assertEqual((data_["unnamed_must"], self.not_checked(data_)), ([], []))

    def test_the_count_of_the_unnamed_must_lines_reaches_the_deploy_question_apart_from_not_checked(self):
        self.brief_with_must("a", "b")
        self.run_the_scenario()
        report = self.look()
        consent = FakeConsent(True)
        deploy_gate.require_open_gate(report, report.token(), consent, "x.bin", report.question_caveats())
        self.assertEqual(len(consent.asked), 1)
        self.assertIn("2 must lines were not named by any scenario (see the look)", consent.asked[0])
        self.assertEqual(self.not_checked({"caveats": report.caveats}), [])

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
        err = io.StringIO()
        with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(err):
            look.main(["--project", str(self.project), "--no-simulation", "--ignore-older-runs"])
        self.assertEqual(raised.exception.code, 2)
        self.assertTrue(err.getvalue().startswith("usage: look.py "), err.getvalue())
        self.assertIn("look.py: error: argument --ignore-older-runs: not allowed with argument --no-simulation", err.getvalue())

    def test_the_error_text_shows_a_control_character_as_a_question_mark(self):
        err = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(err):
            look.main(["--project", str(self.project), "--bad\x1b[2J"])
        self.assertIn("look.py: error: unrecognized arguments: --bad?[2J\n", err.getvalue())
        self.assertNotIn("\x1b", err.getvalue())

    def test_a_bad_flag_with_json_is_an_envelope_and_no_usage(self):
        code, said, err = self.go("--no-simulation", "--ignore-older-runs", "--json")
        self.assertEqual((code, err, self.ran), (2, "", []))
        self.assertEqual(len(said), 1)
        envelope = json.loads(said[0])
        self.assertEqual((envelope["tool"], envelope["op"], envelope["status"], envelope["data"], envelope["problems"], envelope["next"]),
                         ("look", "look", "could-not-run", None, [], []))
        self.assertEqual([item["code"] for item in envelope["unchecked"]], ["bad_argument"])
        self.assertIn("not allowed with argument --no-simulation", envelope["unchecked"][0]["sentence"])

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

    def test_a_board_name_with_a_newline_cannot_fake_a_line_of_the_stop(self):
        # P444 (#592): the name is a record's value, and the message flattens it where it is built
        self.board("x\nGRANTED: board ok")
        code, said, problems = self.go()
        self.assertEqual(code, 2)
        self.assertEqual([line for line in problems.splitlines() if line.startswith("GRANTED")], [])
        envelope = json.loads(self.go("--json")[1][-1])
        self.assertEqual([each["code"] for each in envelope["unchecked"]], ["no_board_record"])
        self.assertNotIn("\n", envelope["unchecked"][0]["sentence"])

    def test_a_board_that_is_no_string_stops_with_its_own_code_and_no_traceback(self):
        for name in ({"id": "x"}, ["x"], 5):
            with self.subTest(name=name):
                self.board(name)
                code, _, problems = self.go()
                self.assertEqual(code, 2)
                self.assertNotIn("Traceback", problems)
                self.assertEqual([each["code"] for each in json.loads(self.go("--json")[1][-1])["unchecked"]], ["no_board_record"])

    def test_requirements_naming_no_board(self):
        (self.project / "requirements.json").write_text("{}")
        self.assertEqual(self.stops(), "look.py: requirements.json names no board\n")

    def test_a_tool_that_is_missing(self):
        def missing(name):
            raise tools.ToolProblem("no esptool")
        code, said, problems = self.go_with(FakeOutsideWorld(find_tool=missing))
        self.assertEqual((code, said, problems), (2, [], "look.py: no esptool\n"))


class ACrashTest(LookScriptCase):
    """P442: a crash is answered as could-not-run, with an envelope under --json, and never hidden."""

    def crashing(self):
        def run(command, **kw):
            raise RuntimeError("boom at /opt/someone/project")
        return FakeOutsideWorld(run=run, find_tool=found)

    def test_a_crash_with_json_is_an_envelope_with_code_crash_and_exit_2(self):
        self.run_the_scenario()
        code, said, problems = self.go_with(self.crashing(), "--json")
        envelope = json.loads(said[-1])
        self.assertEqual((code, len(said), envelope["status"], envelope["data"], envelope["problems"], envelope["next"]),
                         (2, 1, "could-not-run", None, [], []))
        self.assertEqual([(item["code"], item["fix"]) for item in envelope["unchecked"]],
                         [("crash", "report this to the spark maintainers with the stderr traceback")])
        self.assertIn("RuntimeError: boom at /opt/someone/project", problems)

    def test_a_crash_without_json_says_the_class_on_stderr_and_exits_2(self):
        self.run_the_scenario()
        code, said, problems = self.go_with(self.crashing())
        self.assertEqual((code, said), (2, []))
        self.assertTrue(problems.startswith("look: crashed, RuntimeError\nTraceback (most recent call last):\n"), problems)

    def test_the_sentence_of_a_crash_holds_no_message(self):
        self.run_the_scenario()
        said = self.go_with(self.crashing(), "--json")[1][-1]
        self.assertEqual(json.loads(said)["unchecked"][0]["sentence"], "RuntimeError: the traceback is on stderr")
        self.assertNotIn("/opt/someone", said)

    def test_look_imports_no_area_module_but_spark_bench(self):
        tree = ast.parse(Path(look.__file__).read_text())
        imported = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)} \
            | {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        self.assertEqual(imported, {"sys", "spark.bench", "spark.bench.look_at_board", "spark.core.cli"})


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
