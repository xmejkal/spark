"""P219 step 3 (#201): look.py prints what the look found, in the lines a person reads, and changes nothing on the board."""

import ast
import contextlib
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.bench import board_doctor  # noqa: E402
from spark.bench import board_envelope  # noqa: E402
from spark.bench import board_look  # noqa: E402
from spark.bench import deploy_gate  # noqa: E402
from spark.bench import known_board  # noqa: E402
from spark.records import board_records  # noqa: E402
from spark.firmware import image_builder  # noqa: E402
import look  # noqa: E402
from spark.bench import look_at_board  # noqa: E402
from spark.core.cli import run_operation  # noqa: E402
from spark.firmware import sim_project  # noqa: E402
from spark.records import deploy_record_store  # noqa: E402
from spark.records import store  # noqa: E402
from spark.records import tool_finder  # noqa: E402
from spark.bench import image_evidence  # noqa: E402
from fakes import FakeConsent, FakeDeployRecordStore, FakeOutsideWorld, FakeReporter, FakeToolFinder, RealChildRun, Stream  # noqa: E402
from spark.core import outcomes  # noqa: E402
from spark.core.events import Event  # noqa: E402
from spark.core.operation import Argument  # noqa: E402
from spark.core.operation_help_table import OperationHelpTable  # noqa: E402
from suite_runs import needs_littlefs, needs_rich  # noqa: E402
from test_board_look import FOUND, LookCase, data, done, found  # noqa: E402
from test_deploy import real_littlefs  # noqa: E402

RESTART = "    the board restarts while it is read: a running program stops and starts again. Nothing is erased or written."
MAC = "8c:bf:ea:xx:xx:xx"
#: LookCase's scenario only waits for text, so its passed run presses nothing and reads no pin (P345): the look says so.
SIMULATION = "    simulation   passed"
CAVEAT = ("    the passed run's scenario has no set-control step (the step that presses a button or sets a sensor) and no "
          "expect-pin step (the step that reads a pin)")
NO_BOARD = ("no board found. Plug it straight into the computer with a data cable, not a hub that gives power only. "
            "If the plug is USB-C, turn it around, or use a USB-A to USB-C cable.")

#: The words of the asleep fix (P1022 slice 3), literals so that a change of the code's text fails here.
OWN_USB_SLEEP = "In deep sleep the chip's own USB is off, so the board leaves USB with the cable in, until it wakes."
MAYBE_OWN_USB_SLEEP = ("If the board's USB is the chip's own (USB-Serial/JTAG), it is off in deep sleep, and the board "
                       "leaves USB with the cable in until it wakes.")
UNPARSED_MAIN = "These files of firmware/ did not parse, so spark does not know whether they call deepsleep: firmware/main.py."


@contextlib.contextmanager
def plain_environ(**set_):
    """P1032: os.environ without FORCE_COLOR and NO_COLOR, so a shell that sets them changes no text, with `set_` added."""
    with mock.patch.dict(os.environ, set_):
        for name in ("FORCE_COLOR", "NO_COLOR"):
            if name not in set_:
                os.environ.pop(name, None)
        yield


class LookScriptCase(LookCase):
    def go(self, *argv, devs="mpremote-devs-one.txt", esptool="c6-flash-id.txt", text=None, fail=False, **shown):
        """(exit code, stdout lines, stderr) of look.py with fake tools. The fakes answer from the fixtures."""
        def run(command, **kw):
            self.ran.append(command)
            return done(data(devs)) if "devs" in command else done(text or data(esptool), 1 if fail else 0)

        if self.KNOWS_THE_BOARD:  # P865: the store keeps the board this call reads, by the serial of the first row listed
            rows = data(devs).split()
            self.know_the_board(board_look.EsptoolReader.parse(text or data(esptool)).mac or MAC, known_board.comparable_key(rows[1]) if rows else None)
        return self.go_with(FakeOutsideWorld(run=RealChildRun(run), find_tool=found), *argv, **shown)  # P458: the compile child is real

    def no_token(self, said, under="Not checked"):
        """P1032: the one Not checked item of a text look that says why there is no token; Next points `under` a section."""
        (item,) = [line for line in said if line.startswith("    - no token: ")]
        self.assertEqual(said[-2:], ["  Next:", "    No command: the first item under %s above says why." % under])
        return item

    def command(self, said):
        """P1032: the deploy command, the text look's last line, after its why."""
        self.assertTrue(said[-2].startswith("    why: erases ALL of the flash"), said[-2])
        self.assertIn("deploy.py --project ", said[-1])
        return said[-1]

    def go_with(self, outside, *argv, stdout=None, environ=None):
        """(exit code, stdout lines, stderr) of look.py on `outside`, a FakeOutsideWorld, so no test patches
        tool_finder.find (P442). `stdout` is the stream it prints on (None: a pipe) and `environ` the variables set for
        the run (P1032)."""
        out, err = stdout or io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), plain_environ(**(environ or {})):
            code = look.main(["--project", str(self.project), *argv], outside=outside)
        return code, out.getvalue().splitlines(), err.getvalue()

    def build_from_firmware(self):
        """The image of firmware/ with no run, as flash_image.py writes it."""
        patcher = mock.patch.object(image_builder, "interpreter_for",
                                    side_effect=lambda given, project=None, find_tool=None: image_builder.Interpreter(self.micropython, 0))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.image.write_bytes(image_builder.image(self.micropython.read_bytes(), image_builder.files_under(self.project / "firmware")))

    def token(self):
        return "%s-%s" % (hashlib.sha256(MAC.encode()).hexdigest()[:4], hashlib.sha256(self.image.read_bytes()).hexdigest()[:4])

    @staticmethod
    def store_disallows_direct_flashing():
        """P1029: the person's file that disallows direct flashing, in this test's store."""
        store.place("grants").mkdir(exist_ok=True)
        (store.place("grants") / "direct_flashing_disallowed").write_text("")


class WhatThePersonSeesTest(LookScriptCase):
    @needs_littlefs
    def test_a_matching_board(self):
        self.run_the_scenario()
        code, said, problems = self.go()
        self.assertEqual((code, problems), (0, ""))
        self.assertEqual(said[:-2], [
            "✓ look: ok. The chip and the flash match the board record xiao-esp32-c6.",
            "",
            "  Board",
            "    port         /dev/cu.usbmodem101",
            "    mac          " + MAC,
            "    chip         esp32c6    same",
            "    flash        4 MB       same",
            "    spark's last deploy here: none in its store record (it keeps its own deploys and those that a registered project recorded)",
            "  Image",
            "    micropython  no banner in the image",
            SIMULATION, CAVEAT,
            "",
            "  Note",
            RESTART,
            "",
            "  Next: you, in your own terminal. deploy.py asks for your yes."])
        self.assertTrue(self.command(said).endswith(" --token %s --port /dev/cu.usbmodem101" % self.token()))

    def run_the_scenario_with_a_note(self):
        (self.project / "sim" / "WHAT-THIS-CANNOT-SHOW.md").write_text(
            sim_project.limits_note([("ONBOARD_DISPLAY", "no part for the display. Test it on the board.")]))
        self.run_the_scenario()

    @needs_littlefs
    def test_the_text_look_lists_the_limits_of_the_passed_run_after_the_caveat(self):
        self.run_the_scenario_with_a_note()
        code, said, _ = self.go()
        self.assertEqual(code, 0)
        self.assertEqual(said[10:14], [
            SIMULATION, CAVEAT, "    what this simulation cannot show, so test it on the board:",
            "    - ONBOARD_DISPLAY — no part for the display. Test it on the board."])

    @needs_littlefs
    def test_the_json_look_carries_the_limits_of_the_passed_run(self):
        self.run_the_scenario_with_a_note()
        data = json.loads(self.go("--json")[1][-1])["data"]
        self.assertEqual(data["limits"], [{"component": "ONBOARD_DISPLAY", "sentence": "no part for the display. Test it on the board."}])

    def test_a_passed_run_of_a_project_with_no_note_has_no_limits_and_no_heading(self):
        self.run_the_scenario()
        code, said, _ = self.go()
        self.assertFalse([line for line in said if "cannot show" in line])
        self.assertEqual(json.loads(self.go("--json")[1][-1])["data"]["limits"], [])

    @needs_littlefs
    def test_a_flash_that_differs_but_holds_the_image_is_a_warning_with_its_token(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go(esptool="s3-flash-id-8mb.txt")
        self.assertEqual(code, 1)
        self.assertEqual(said[5:7], ["    chip         esp32s3    same", "    flash        8 MB       differs"])
        self.assertIn("    - the flash differs: 8 MB, the record says 16 or 4", said)
        self.assertEqual(said[10:12], [SIMULATION, CAVEAT])
        self.assertRegex(self.command(said), r" --token [0-9a-f]{4}-[0-9a-f]{4} ")

    @needs_littlefs
    def test_a_field_the_board_did_not_say_is_unknown_and_the_look_could_not_check_it(self):
        self.run_the_scenario()
        code, said, _ = self.go(esptool="c6-flash-id-garbled.txt")
        self.assertEqual(code, 2)
        self.assertIn("    flash        not read   unknown", said)
        self.assertEqual(said[0], "? look: could-not-run. Unknown against the board record xiao-esp32-c6: the flash: the board did "
                                  "not say it. deploy.py will ask you to accept it.")
        self.assertIn("    - flash unknown: the board did not say", said)
        self.assertIn(" --token %s " % self.token(), self.command(said))

    @needs_littlefs
    def test_a_port_with_a_newline_and_a_right_to_left_override_shows_as_one_line_with_question_marks(self):
        # P423: the report's items are guarded one by one, so a newline in a value cannot fake a line of the look
        self.run_the_scenario()
        port = "/dev/cu.usb\u202emodem\n  token  FAKE"
        code, said, _ = self.go("--port", port)
        self.assertEqual(said[3], "    port         /dev/cu.usb?modem?  token  FAKE")
        self.assertEqual([line for line in said if line.lstrip().startswith("token")], [])
        self.assertIn(" --token %s " % self.token(), self.command(said))
        self.assertEqual(json.loads(self.go("--port", port, "--json")[1][-1])["data"]["port"], port)  # --json keeps it raw

    def test_a_port_with_an_override_shows_as_a_question_mark_in_the_stop_on_stderr(self):
        # P423: the failed read's lines go through guard_lines too
        self.run_the_scenario()
        code, _, problems = self.go("--port", "/dev/cu.usb\u202emodem", fail=True)
        self.assertEqual(code, 2)
        self.assertEqual(problems.splitlines()[0], "look.py: could not read the board on /dev/cu.usb?modem")
        self.assertNotIn("\u202e", problems)

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
        with mock.patch.object(board_records.ButtonPlaces, "of_project",
                               return_value=board_records.ButtonPlaces.from_record(record)):
            code, _, problems = self.go(fail=True, text="Connecting......\nA fatal error occurred: No serial data received.\n")
        self.assertEqual(code, 2)
        self.assertIn("BOOT button (B?GRANTED: fake, top)", problems)
        self.assertEqual([line for line in problems.splitlines() if line.startswith("GRANTED")], [])

    def test_a_newline_in_the_project_path_cannot_fake_a_line_of_a_tool_problem_stop(self):
        # P430: looker turns a ToolError into a stop whose text holds the project's tools file path
        project = Path(tempfile.mkdtemp()) / "a\nGRANTED (deploy): board ok"
        (project / ".spark").mkdir(parents=True)
        (project / ".spark" / "tools.json").write_text("not json")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = look.main(["--project", str(project)])
        self.assertEqual(code, 2)
        self.assertIn("a?GRANTED (deploy): board ok", err.getvalue())
        self.assertEqual([line for line in err.getvalue().splitlines() if line.startswith("GRANTED")], [])

    @needs_littlefs
    def test_another_chip_is_a_stop_with_no_token(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go()
        self.assertEqual(code, 1)
        self.assertEqual(said[5], "    chip         esp32c6    differs")
        self.assertEqual(said[0], "✗ look: problems. Stop: this board is an esp32c6, the project is for an esp32s3. deploy.py will refuse.")
        self.assertIn("    - this board is an esp32c6, the project is for an esp32s3", said)
        self.assertEqual(said[said.index(SIMULATION) + 1], CAVEAT)
        self.assertEqual(self.no_token(said, under="Problems"), "    - no token: the look found a stop")

    @needs_littlefs
    def test_a_flash_too_small_for_the_image_is_a_stop_even_when_the_record_lists_it(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go(esptool="s3-flash-id-2mb.txt")
        self.assertEqual(code, 1)
        self.assertIn("    - the flash is 2 MB, the image needs 4 MB", said)
        self.assertEqual(self.no_token(said, under="Problems"), "    - no token: the look found a stop")

    @needs_littlefs
    def test_a_flash_in_the_records_list_that_is_too_small_exits_1_not_0(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        self.image.write_bytes(self.image.read_bytes() + b"x")
        code, said, _ = self.go(text=data("s3-flash-id-16mb.txt").replace("16MB", "4MB"))
        self.assertEqual(code, 1)
        self.assertIn("    flash        4 MB       same", said)

    def test_no_image_prints_the_fields_and_says_why_there_is_no_token(self):
        code, said, _ = self.go()
        self.assertEqual(code, 2)
        self.assertEqual(said[5:7], ["    chip         esp32c6    same", "    flash        4 MB       same"])
        self.assertEqual(said[0], "? look: could-not-run. The chip and the flash match the board record xiao-esp32-c6.")
        self.assertRegex(self.no_token(said), r"^    - no token: .*run a scenario first")

    def test_a_firmware_line_that_is_no_string_stops_the_token_with_one_sentence_and_no_traceback(self):
        # P429: `firmware = 3` raised a TypeError out of the look
        (self.project / "sim" / "wokwi.toml").write_text("[wokwi]\nversion = 1\nfirmware = 3\n")
        code, said, problems = self.go()
        self.assertEqual((code, problems), (2, ""))
        self.assertEqual(self.no_token(said), "    - no token: sim/wokwi.toml line 3 names the firmware in a form spark cannot read. "
                         'To fix it, write it as firmware = "name.bin".')

    @needs_littlefs
    def test_ignore_older_runs_gives_a_token_where_an_older_log_tested_another_image(self):
        self.run_the_scenario()
        (self.project / "firmware" / "main.py").write_text("print('ready')\nprint(2)\n")
        other = self.scenario.with_name("t.scenario.yaml")
        other.write_text(self.scenario.read_text().replace("name: s", "name: t"))
        self.run_the_scenario(scenario=other)
        code, said, _ = self.go()
        self.assertEqual(code, 2)
        self.assertRegex(self.no_token(said), r"^    - no token: .*tested another image")
        code, said, _ = self.go("--ignore-older-runs")
        self.assertEqual(code, 0)
        self.assertIn(" --token %s " % self.token(), self.command(said))

    @needs_littlefs
    def test_no_simulation_gives_a_token_for_firmware_as_it_is_with_no_run_log(self):
        self.build_from_firmware()
        code, said, _ = self.go()
        self.assertEqual(code, 2)
        self.assertRegex(self.no_token(said), r"^    - no token: .*no run in sim/runs/ tested")
        flag = self.no_token(said).rsplit("run look.py ", 1)[1]  # P463: the sentence names the way, and the way works
        self.assertEqual(flag, "--no-simulation")
        code, said, _ = self.go(flag)
        self.assertEqual(code, 0)
        self.assertIn(" --token %s " % self.token(), self.command(said))

    @needs_littlefs
    def test_no_simulation_with_firmware_changed_after_the_image_gives_no_token_and_the_build_command(self):
        self.build_from_firmware()
        (self.project / "firmware" / "main.py").write_text("print('ready')\nprint(3)\n")
        code, said, _ = self.go("--no-simulation")
        self.assertEqual(code, 2)
        self.assertRegex(self.no_token(said), r"^    - no token: .*flash_image\.py --project .* --files .*/firmware'? -o ")

    def test_littlefs_turned_off_in_the_project_is_named_by_the_look(self):
        # P457: the image check asks the finder with the project, so the sentence names the file that turned it off
        (self.project / ".spark").mkdir(exist_ok=True)
        (self.project / ".spark" / "tools.json").write_text(json.dumps({"littlefs-python": {"on": False}}))
        self.image.write_bytes(b"x")
        code, said, _ = self.go_with(FakeOutsideWorld(run=RealChildRun(lambda command, **kw: done(data("mpremote-devs-one.txt")) if "devs" in command
                                                                       else done(data("c6-flash-id.txt"))), find_tool=real_littlefs(self.project)), "--no-simulation")
        self.assertEqual(code, 2)
        self.assertIn("littlefs-python is turned off in this project's .spark/tools.json", self.no_token(said))

    def test_no_simulation_with_a_finder_that_lacks_littlefs_gives_no_token_and_the_install_line(self):
        # P442: the image check asks the finder the look was given, not tool_finder.find, so the fake decides what is
        # installed
        self.image.write_bytes(b"x")  # P452: the finder answers before the image is read, so no littlefs is needed to build one

        not_installed = tool_finder.ToolError("not-installed is not installed — install: /spark:setup add not-installed", code="tool_missing")
        finder = FakeToolFinder({**FOUND, "littlefs": not_installed})
        code, said, _ = self.go_with(FakeOutsideWorld(run=RealChildRun(lambda command, **kw: done(data("mpremote-devs-one.txt")) if "devs" in command
                                                                       else done(data("c6-flash-id.txt"))), find_tool=finder.find), "--no-simulation", "--json")
        self.assertEqual(code, 2)
        # P457, P725: by name alone; the finder the world holds is the project's, so a tools file that turns littlefs off is named
        self.assertIn(("littlefs", None), finder.asked)
        self.assertEqual({project for name, project in finder.asked}, {None})
        no_token = [item for item in json.loads(said[-1])["unchecked"] if item["sentence"].startswith("no token: ")]
        self.assertEqual([item["code"] for item in no_token], ["tool_missing"])
        self.assertIn("not-installed is not installed", no_token[0]["sentence"])

    @needs_littlefs
    def test_the_json_look_says_none_and_its_deploy_step_carries_the_flag(self):
        self.build_from_firmware()
        code, said, _ = self.go("--no-simulation", "--json")
        envelope = json.loads(said[-1])
        self.assertEqual((code, envelope["data"]["simulation"]), (0, "none"))
        self.assertIn("--no-simulation", envelope["next"][0]["argv"])

    @needs_littlefs
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

    @needs_littlefs
    def test_the_look_exits_0_and_lists_the_unnamed_must_lines_in_text_and_json(self):
        self.brief_with_must("the LED lights", "the LED goes off")
        self.run_the_scenario()
        code, said, _ = self.go()
        self.assertEqual(code, 0)
        self.assertEqual(said[said.index("    no scenario named these must lines, so test them on the board:") + 1:][:2], ["    - the LED lights", "    - the LED goes off"])
        code, lines, _ = self.go("--json")
        data_ = json.loads(lines[-1])["data"]
        self.assertEqual((code, data_["unnamed_must"], self.not_checked(data_)), (0, ["the LED lights", "the LED goes off"], []))

    @needs_littlefs
    def test_the_caveats_hold_not_checked_exactly_when_a_log_could_not_say(self):
        self.brief_with_must("the LED lights")
        self.run_without_step_names()
        code, lines, _ = self.go("--json")
        data_ = json.loads(lines[-1])["data"]
        self.assertEqual((code, data_["unnamed_must"], len(self.not_checked(data_))), (0, [], 1))
        self.assertEqual(json.loads(lines[-1])["status"], "ok")

    @needs_littlefs
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

    @needs_littlefs
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
                                                "deployed": None, "micropython_banner": None, "made_by": None})

    @needs_littlefs
    def test_the_json_look_of_an_image_no_run_tested_says_null_and_no_caveat(self):
        self.build_from_firmware()
        data_ = json.loads(self.go("--json")[1][-1])["data"]
        self.assertEqual((data_["simulation"], data_["caveats"]), (None, []))

    @needs_littlefs
    def test_the_text_look_says_none_and_its_caveat_with_the_flag(self):
        self.build_from_firmware()
        said = self.go("--no-simulation")[1]
        self.assertEqual(said[said.index("    simulation   none"):][:2], ["    simulation   none", "    no simulation tested this image"])

    @needs_littlefs
    def test_the_next_step_names_a_deploy_grant_only_where_a_grant_may_answer(self):
        self.build_from_firmware()
        none = json.loads(self.go("--no-simulation", "--json")[1][-1])["next"][0]["why"]
        self.assertIn("types yes in their own terminal (or a deploy grant given with --no-simulation stands);", none)
        self.store_disallows_direct_flashing()  # P1029
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
        self.assertIn("    mac          not read", said)
        self.assertEqual(self.no_token(said), "    - no token: the board's MAC could not be read")


#: An SGR code, the only escape code the coloured text view adds (P1032).
SGR = re.compile(r"\x1b\[[0-9;]*m")


class TheTextViewTest(LookScriptCase):
    """P1032: without --json the look prints a status line, its facts, the findings with their fix, a Note and Next."""

    @needs_littlefs
    def test_the_text_view_starts_with_the_status_line_and_ends_with_the_command(self):
        self.run_the_scenario()
        code, said, _ = self.go()
        self.assertEqual(code, 0)
        self.assertEqual(said[0], "✓ look: ok. The chip and the flash match the board record xiao-esp32-c6.")
        self.assertTrue(said[-1].startswith("    SPARK_HOME="), said[-1])
        self.assertIn("deploy.py --project ", said[-1])
        self.assertTrue(said[-1].endswith(" --token %s --port /dev/cu.usbmodem101" % self.token()), said[-1])
        self.assertEqual([line for line in said if line.lstrip().startswith("token")], [])

    @needs_littlefs
    def test_a_warning_has_its_mark_its_field_and_a_problem_with_its_fix(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        code, said, _ = self.go(esptool="s3-flash-id-8mb.txt")
        self.assertEqual(code, 1)
        self.assertEqual(said[0], "! look: problems. Warning: the flash differs from the board record firebeetle2-esp32s3. "
                                  "deploy.py will ask you to accept it.")
        item = said.index("    - the flash differs: 8 MB, the record says 16 or 4")
        self.assertFalse(said[item + 1].startswith("      fix: "), "the review of #1549, SF1: a fix that restates the verdict")
        self.assertEqual([line for line in said[1:] if "deploy.py will ask you" in line], [])
        problem = json.loads(self.go("--json", esptool="s3-flash-id-8mb.txt")[1][-1])["problems"][0]
        self.assertEqual(problem["fix"], "deploy.py asks the person to accept it", "the JSON keeps the fix")

    @needs_littlefs
    def test_every_stop_headline_has_a_problem_after_it(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        for esptool, stop in (("c6-flash-id.txt", "this board is an esp32c6, the project is for an esp32s3"),
                              ("s3-flash-id-2mb.txt", "the flash is 2 MB, the image needs 4 MB")):
            with self.subTest(esptool=esptool):
                code, said, _ = self.go(esptool=esptool)
                self.assertEqual(code, 1)
                self.assertEqual(said[0], "✗ look: problems. Stop: %s. deploy.py will refuse." % stop)
                problems = said.index("  Problems")
                self.assertEqual(said[problems + 1], "    - " + stop)
                self.assertFalse(said[problems + 2].startswith("      fix: "), "deploy.py will refuse restates the verdict")
                self.assertEqual(said[-1], "    No command: the first item under Problems above says why.")

    def test_an_unknown_field_with_no_token_points_next_at_the_missing_token(self):
        # the review of #1549, refuter 1: no image, so no token; the status line does not promise deploy.py's question
        code, said, _ = self.go(esptool="c6-flash-id-garbled.txt")
        self.assertEqual(code, 2)
        self.assertEqual(said[0], "? look: could-not-run. Unknown against the board record xiao-esp32-c6: the flash: the board did not say it.")
        unchecked = said.index("  Not checked")
        self.assertTrue(said[unchecked + 1].startswith("    - no token: "), said[unchecked + 1])
        self.assertIn("    - flash unknown: the board did not say", said[unchecked:])
        self.no_token(said)
        envelope = json.loads(self.go("--json", esptool="c6-flash-id-garbled.txt")[1][-1])
        self.assertEqual(envelope["unchecked"][0]["code"], "field_unknown", "the JSON keeps its order")

    def test_a_stop_and_the_question_print_as_before(self):
        # D1: a stop before the read prints on stderr only, and the board question keeps its lines
        code, said, problems = self.go(devs="mpremote-devs-none.txt")
        self.assertEqual((code, said, problems), (2, [], "look.py: %s\n" % NO_BOARD))

    @needs_rich
    @needs_littlefs
    def test_on_a_terminal_the_look_is_coloured_and_in_a_pipe_it_is_plain(self):
        self.run_the_scenario()
        terminal = Stream(tty=True)
        code, said, _ = self.go(stdout=terminal, environ={"TERM": "xterm"})
        self.assertEqual(code, 0)
        self.assertTrue(SGR.search("\n".join(said)), said)
        self.assertEqual([SGR.sub("", line) for line in said], self.go()[1])
        self.assertFalse(SGR.search("\n".join(self.go(environ={"TERM": "xterm"})[1])), "a pipe gets no code")

    @needs_rich
    @needs_littlefs
    def test_force_color_on_a_pipe_gives_codes(self):
        self.run_the_scenario()
        self.assertTrue(SGR.search("\n".join(self.go(environ={"FORCE_COLOR": "1"})[1])))
        self.assertFalse(SGR.search("\n".join(self.go(environ={"FORCE_COLOR": "1", "NO_COLOR": "1"})[1])))
        self.assertFalse(SGR.search(self.go("--json", environ={"FORCE_COLOR": "1"})[1][-1]), "--json never gets a code")

    @needs_littlefs
    def test_the_look_s_view_and_deploy_s_lines_show_the_same_facts(self):
        (self.project / "sim" / "WHAT-THIS-CANNOT-SHOW.md").write_text(
            sim_project.limits_note([("ONBOARD_DISPLAY", "no part for the display. Test it on the board.")]))
        self.run_the_scenario()
        report = self.look()
        facts, deploy_s = "\n".join(look_at_board.look_facts(report)), "\n".join(board_look.report_lines(report, token=False))
        values = [report.port, report.reading.mac, report.reading.chip, "%s MB" % report.reading.flash_mb,
                  board_look.say_last_deploy(report.last_deploy), board_look.say_image_banner(report), report.simulation]
        values += report.caveats + [board_look.say_limit(limit) for limit in report.limits]
        self.assertEqual(len(report.limits), 1)
        for value in values:
            with self.subTest(value=value):
                self.assertIn(value, facts)
                self.assertIn(value, deploy_s)


class TheMaskedTextTest(LookScriptCase):
    """P677: look's text keeps raw the store record a person must repair, the fix of a pasted Finding."""

    @needs_littlefs
    def test_the_text_line_of_a_last_deploy_that_cannot_be_read_keeps_the_record_to_repair(self):
        self.run_the_scenario()
        record = store.place("boards") / (store.slug(MAC) + ".json")
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text("{not json")
        _, said, _ = self.go()
        self.assertIn("fix: repair or remove %s, then run look.py again" % record, "\n".join(said))


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
        self.assertFalse([each for each in self.ran if "flash-id" in each])  # none was read: each read restarts a board

    @needs_littlefs
    def test_two_boards_with_a_port_reads_that_one(self):
        self.run_the_scenario()
        code, said, _ = self.go("--port", "/dev/cu.usbserial-1410", devs="mpremote-devs-two.txt")
        self.assertEqual(code, 0)
        self.assertEqual(said[3], "    port         /dev/cu.usbserial-1410")

    def test_no_board_with_a_deepsleep_call_names_deep_sleep_and_keeps_the_cable_check_last(self):
        # P1022 slice 3, 2026-11-23 14:05 CET: the FireBeetle 2 C6 in deep sleep was off USB, and the look blamed the cable
        self.sleeper("import machine\nprint('ready')\nmachine.deepsleep(60000)\n")
        problems = self.stops(devs="mpremote-devs-none.txt").splitlines()
        self.assertEqual(problems[0], "look.py: no board found.")
        fix = problems[1]
        for words in ("What spark knows: no board is on USB, and the project's firmware calls deepsleep (firmware/main.py:3).",
                      OWN_USB_SLEEP, "Hold the board's BOOT button (B, top right, beside the USB-C), press and "
                      "release RESET (R, top left, beside the USB-C), then release BOOT. Left and right as seen with the metal shield",
                      "press RESET (R, top left, beside the USB-C) once, with BOOT not held"):
            self.assertIn(words, fix)
        self.assertLess(fix.index("1. Hold"), fix.index("2. Or wait"))
        self.assertLess(fix.index("2. Or wait"), fix.index("3. If the board still does not show, check the cable"))
        self.assertEqual(len(problems), 2)
        unchecked = self.unchecked(devs="mpremote-devs-none.txt")
        self.assertEqual((unchecked["code"], unchecked["sentence"], unchecked["fix"]), ("no_port", "no board found.", fix))

    #: ASLEEP_LOOK_WHY, copied: the order of the person's hands and the one look after them (P1048).
    ASLEEP_LOOK_WHY = ("first the person does step 1 or 2 of the fix: the board in download mode with BOOT and RESET, or "
                       "awake. Run it once after the person says so: the look then finds the board and names its port. The "
                       "board restarts while it is read")

    def next_of(self, *argv, **kw):
        """The `next` of look.py --json, after a stop (exit 2)."""
        code, said, _ = self.go("--json", *argv, **kw)
        self.assertEqual(code, 2)
        return json.loads(said[-1])["next"]

    def test_no_board_with_a_deepsleep_call_names_the_look_that_needs_the_person(self):
        # P1048: the fix's step 1 says "run look.py again"; `next` names that look, which the person's hands come before
        self.sleeper("import machine\nmachine.deepsleep(1)\n")
        problems = self.stops(devs="mpremote-devs-none.txt").splitlines()
        (step,) = self.next_of(devs="mpremote-devs-none.txt")
        self.assertEqual((step["op"], step["argv"], step["needs_person"], step["needs_yes"], step["why"]),
                         ("look", ["--project", str(self.project.resolve())], True, False, self.ASLEEP_LOOK_WHY))
        self.assertEqual((len(problems), problems[0]), (2, "look.py: no board found."))  # the text gains no line

    def test_a_named_port_off_usb_names_the_look_with_no_port_and_the_same_flags(self):
        # P1048 D5: the named port was not on USB, so the look picks the port; the run's evidence flags stay
        self.sleeper("import machine\nmachine.deepsleep(1)\n")
        (step,) = self.next_of("--port", "/dev/cu.usbmodem101", "--ignore-older-runs", devs="mpremote-devs-none.txt", fail=True)
        self.assertEqual((step["argv"], step["needs_person"]), (["--project", str(self.project.resolve()), "--ignore-older-runs"], True))

    def test_a_stop_with_no_asleep_fix_names_no_step(self):
        # P1048 D6: the cable sentence, UNPARSED and the doctor's own step give no look step
        for main, argv, kw in (("import machine\nmachine.lightsleep(1)\n", (), {}),
                               ("import machine\nmachine.deepsleep(1\n", (), {}),
                               ("import machine\nmachine.lightsleep(1)\n", ("--port", "/dev/cu.usbmodem101"), {"fail": True})):
            with self.subTest(main=main, argv=argv):
                self.sleeper(main)
                self.assertEqual(self.next_of(*argv, devs="mpremote-devs-none.txt", **kw), [])
        self.sleeper("import machine\nmachine.deepsleep(1)\n")
        stop = board_look.LookStopError("no board on %s: mpremote devs does not list it.", "/dev/x", reason="port_not_listed")
        _, _, fix = board_envelope.stop_said("look.py", stop, (["look.py: " + str(stop)], None), None, self.project)
        self.assertEqual(board_envelope.asleep_next(fix, self.project), [])  # a port_not_listed the person did not name

    def test_a_board_whose_usb_may_be_a_bridge_gets_the_words_with_a_condition(self):
        self.board("firebeetle2-esp32s3")
        self.sleeper("import machine\nmachine.deepsleep(1)\n")
        fix = self.stops(devs="mpremote-devs-none.txt").splitlines()[1]
        self.assertIn(MAYBE_OWN_USB_SLEEP, fix)
        self.assertNotIn(OWN_USB_SLEEP, fix)
        self.assertIn("Hold the board's BOOT button, press and release RESET, then release BOOT. The board", fix)

    def test_only_the_first_two_call_places_are_shown(self):
        self.sleeper("import machine\nmachine.deepsleep(1)\nmachine.deepsleep(2)\nmachine.deepsleep(3)\n")
        self.assertIn("(firmware/main.py:2, firmware/main.py:3).", self.unchecked(devs="mpremote-devs-none.txt")["fix"])

    def test_a_named_port_that_is_not_on_usb_opens_with_that_port_never_with_no_board(self):
        # look.py and deploy.py read a --port the list does not hold, and reach.py asks the board question for it (P892),
        # so only grant.py, live.py and bench.py record stop with port_not_listed: the fix is asked for that code directly
        self.sleeper("import machine\nmachine.deepsleep(1)\n")
        places = board_records.ButtonPlaces.of_project(self.project)
        fix = board_envelope.asleep_fix(self.project, "port_not_listed", places)
        self.assertTrue(fix.startswith("What spark knows: the port you named is not on USB, and"), fix)
        self.assertNotIn("no board is on USB", fix)
        stop = board_look.LookStopError("no board on %s: mpremote devs does not list it.", "/dev/x", reason="port_not_listed")
        self.assertEqual(board_envelope.asleep_stop(stop, self.project, places), ("no board on /dev/x: mpremote devs does not list it.", fix))
        self.assertEqual(board_envelope.asleep_fix(self.project, "two_boards", places), "")

    def test_after_the_doctor_only_a_plug_in_step_on_a_named_port_with_a_deepsleep_call_gets_the_asleep_fix(self):
        # P1049, D2 and D3: a port spark picked, another step, no doctor, no call and a file that does not parse give ""
        places = board_records.ButtonPlaces.of_project(self.project)
        plug_in, close_other = (board_doctor.DoctorProbeResult((), None, step, None) for step in ("plug_in", "close_other"))
        self.assertEqual(board_envelope.asleep_after_doctor(plug_in, "/dev/cu.usbmodem101", self.project, places), "")
        self.sleeper("import machine\nmachine.deepsleep(1\n")
        self.assertEqual(board_envelope.asleep_after_doctor(plug_in, "/dev/cu.usbmodem101", self.project, places), "")
        self.sleeper("import machine\nmachine.deepsleep(1)\n")
        fix = board_envelope.asleep_after_doctor(plug_in, "/dev/cu.usbmodem101", self.project, places)
        self.assertTrue(fix.startswith("What spark knows: the port you named is not on USB, and the project's firmware calls "
                                       "deepsleep (firmware/main.py:2)."), fix)
        self.assertEqual(board_envelope.asleep_after_doctor(plug_in, None, self.project, places), "")
        self.assertEqual(board_envelope.asleep_after_doctor(close_other, "/dev/cu.usbmodem101", self.project, places), "")
        self.assertEqual(board_envelope.asleep_after_doctor(None, "/dev/cu.usbmodem101", self.project, places), "")

    #: look.py --port on a port the list does not hold, esptool failing: the doctor's lines (the refuter's find of P1049).
    NAMED_NOT_LISTED = ["look.py: could not read the board on /dev/cu.usbmodem101",
                        "  check   port-listed: mpremote devs does not list /dev/cu.usbmodem101 (it lists: none)",
                        "  next    plug the board straight into the computer with a data cable, not a hub that gives power only, "
                        "and run it again"]

    def named_not_listed(self, *argv):
        """(stderr lines, the one unchecked item of --json) of look.py --port on a port that mpremote devs does not list."""
        go = dict(devs="mpremote-devs-none.txt", fail=True)
        return self.stops("--port", "/dev/cu.usbmodem101", **go).splitlines(), self.unchecked("--port", "/dev/cu.usbmodem101", **go)

    def test_a_named_port_off_usb_with_a_deepsleep_call_gets_the_asleep_fix_as_the_doctor_s_next_step(self):
        # P1049: the doctor's plug_in step was the cable advice of the 14:05 sighting again
        self.sleeper("import machine\nmachine.deepsleep(1)\n")
        problems, unchecked = self.named_not_listed()
        self.assertEqual(problems[:2], self.NAMED_NOT_LISTED[:2])
        self.assertEqual(len(problems), 3)
        self.assertTrue(problems[2].startswith("  next    What spark knows: the port you named is not on USB, and the project's "
                                               "firmware calls deepsleep (firmware/main.py:2). " + OWN_USB_SLEEP), problems[2])
        self.assertFalse([line for line in problems if "plug the board straight" in line])
        self.assertEqual((unchecked["code"], unchecked["fix"]), ("board_not_read", problems[2][len("  next    "):]))
        self.assertNotEqual(unchecked["fix"], self.NAMED_NOT_LISTED[2][len("  next    "):])
        code, said, _ = self.go("--json", "--port", "/dev/cu.usbmodem101", devs="mpremote-devs-none.txt", fail=True)
        self.assertEqual(json.loads(said[-1])["data"]["doctor"]["next_step"], "plug_in", "D4: the data is what the doctor saw")

    def test_a_named_port_off_usb_without_a_deepsleep_call_keeps_the_doctor_s_step(self):
        self.sleeper("import machine\nmachine.lightsleep(1)\n")
        problems, unchecked = self.named_not_listed()
        self.assertEqual(problems, self.NAMED_NOT_LISTED)
        self.assertEqual((unchecked["code"], unchecked["fix"]), ("board_not_read", self.NAMED_NOT_LISTED[2][len("  next    "):]))

    def test_a_named_port_off_usb_with_a_file_that_does_not_parse_keeps_the_doctor_s_step(self):
        # D3: after the doctor, only a found deepsleep call replaces the cable step
        self.sleeper("import machine\nmachine.deepsleep(1\n")
        problems, unchecked = self.named_not_listed()
        self.assertEqual(problems, self.NAMED_NOT_LISTED)
        self.assertEqual(unchecked["fix"], self.NAMED_NOT_LISTED[2][len("  next    "):])

    def test_a_port_not_listed_that_the_person_did_not_name_never_gets_the_port_you_named(self):
        # P1049 (Round 1 C, Round 2 H): stop_said says "the port you named" only of the port the person named
        self.sleeper("import machine\nmachine.deepsleep(1)\n")
        stop = board_look.LookStopError("no board on %s: mpremote devs does not list it.", "/dev/x", reason="port_not_listed")
        answer = (["look.py: no board on /dev/x: mpremote devs does not list it."], None)
        self.assertEqual(board_envelope.stop_said("look.py", stop, answer, None, self.project), (answer[0], str(stop), ""))
        lines, sentence, fix = board_envelope.stop_said("look.py", stop, answer, "/dev/x", self.project)
        self.assertTrue(fix.startswith("What spark knows: the port you named is not on USB"), fix)
        self.assertEqual((lines, sentence), (["look.py: " + str(stop), fix], str(stop)))

    def test_a_firmware_file_that_does_not_parse_is_named_and_the_cable_sentence_stays(self):
        self.sleeper("import machine\nmachine.deepsleep(1\n")
        self.assertEqual(self.stops(devs="mpremote-devs-none.txt").splitlines(), [
            "look.py: %s" % NO_BOARD, UNPARSED_MAIN])
        self.assertEqual(self.unchecked(devs="mpremote-devs-none.txt")["fix"], UNPARSED_MAIN)

    def test_no_board_without_a_deepsleep_call_stays_as_it_was(self):
        self.sleeper("import machine\nmachine.lightsleep(1)\n")
        self.assertEqual(self.stops(devs="mpremote-devs-none.txt"), "look.py: %s\n" % NO_BOARD)
        self.assertEqual(self.unchecked(devs="mpremote-devs-none.txt")["fix"], "")

    def sleeper(self, main):
        (self.project / "firmware").mkdir(exist_ok=True)
        (self.project / "firmware" / "main.py").write_text(main)

    def unchecked(self, *argv, **kw):
        """The one unchecked item of look.py --json."""
        code, said, _ = self.go("--json", *argv, **kw)
        self.assertEqual(code, 2)
        (item,) = json.loads(said[-1])["unchecked"]
        return item

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
            raise tool_finder.ToolError("no esptool", code="tool_missing")
        code, said, problems = self.go_with(FakeOutsideWorld(find_tool=missing))
        self.assertEqual((code, said, problems), (2, [], "look.py: no esptool\n"))


class TheOperationTest(LookScriptCase):
    """P442: the look runs without a CLI: run_operation over LookAtBoard gives the result, and nothing is printed."""

    def test_the_look_reports_one_begin_before_the_read(self):
        # P507: the setup of the test without littlefs above, so the test runs on every machine; the terminal adds no line
        self.image.write_bytes(b"x")
        def without_littlefs(name, **where):
            return found(name) if name != "littlefs" else found("not-installed")
        ran_at_the_begin = []

        class Watching(FakeReporter):
            """Fake Reporter that also keeps what the outside had run when each event came."""

            def report(self, event):
                super().report(event)
                ran_at_the_begin.append(list(outside.ran))
        outside = FakeOutsideWorld(run=RealChildRun(lambda command, **kw: done(data("mpremote-devs-one.txt")) if "devs" in command
                                                    else done(data("c6-flash-id.txt"))), find_tool=without_littlefs, reporter=Watching())
        self.go_with(outside, "--no-simulation", "--json")
        self.assertEqual(outside.reporter.events, [Event.begin("look")])
        self.assertEqual(ran_at_the_begin, [[]], "the BEGIN comes before the look runs anything")
        self.assertTrue(outside.ran, "the look ran its read after the BEGIN")

    def test_the_input_schema_names_each_value_that_run_takes(self):
        # P605: an MCP tool or a LangGraph node (P417) builds the values from this schema, so its names are run's keywords
        import inspect
        schema = look_at_board.LookAtBoard().input_schema()
        keywords = [name for name, kind in inspect.signature(look_at_board.LookAtBoard.run).parameters.items()
                    if kind.kind == kind.POSITIONAL_OR_KEYWORD and name != "self"] + ["ignore_older_runs", "no_simulation"]  # P865: **evidence
        self.assertEqual(list(schema["properties"]), keywords)
        self.assertEqual([schema["properties"][name].get("default") for name in keywords], [".", None, None, False, False])

    @needs_littlefs
    def test_run_operation_gives_the_lines_the_findings_and_the_deploy_step_with_no_stdout(self):
        self.run_the_scenario()
        values = {"project": self.project, "port": None, "ignore_older_runs": False, "no_simulation": False}
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            result = run_operation(look_at_board.LookAtBoard(), values, FakeOutsideWorld(
                run=lambda command, **kw: done(data("mpremote-devs-one.txt")) if "devs" in command else done(data("c6-flash-id.txt")),
                find_tool=found))
        self.assertEqual((out.getvalue(), err.getvalue(), result.status(), result.findings, result.diagnostics), ("", "", "ok", [], ()))
        self.assertEqual(result.lines[1:3], ["    port         /dev/cu.usbmodem101", "    mac          " + MAC])
        self.assertEqual(result.headline.sentence, "The chip and the flash match the board record xiao-esp32-c6.")
        self.assertEqual([line for line in result.lines if self.token() in line], [])
        self.assertEqual([(step.op, step.needs_yes, step.argv[3]) for step in result.next], [("deploy", True, self.token())])
        self.assertEqual(result.data["token"], self.token())

    @needs_littlefs
    def test_run_operation_on_an_unknown_field_gives_the_unchecked_finding(self):
        self.run_the_scenario()
        values = {"project": self.project, "port": None, "ignore_older_runs": False, "no_simulation": False}
        result = run_operation(look_at_board.LookAtBoard(), values, FakeOutsideWorld(
            run=lambda command, **kw: done(data("mpremote-devs-one.txt")) if "devs" in command else done(data("c6-flash-id-garbled.txt")),
            find_tool=found))
        self.assertEqual((result.status(), [(f.severity, f.subject, f.code) for f in result.findings]),
                         ("could-not-run", [("could-not-run", None, "field_unknown")]))

    def values(self, no_simulation=False):
        return {"project": self.project, "port": None, "ignore_older_runs": False, "no_simulation": no_simulation}

    @staticmethod
    def fake_tools(child=None):
        """A `run` for a FakeOutsideWorld: mpremote devs and esptool from the fixtures, and the compile child answered with
        `child` (its stdout), so no real child starts (P458)."""
        def run(command, **options):
            if image_evidence.COMPILE_CHILD in command:
                return done(child)
            return done(data("mpremote-devs-one.txt")) if "devs" in command else done(data("c6-flash-id.txt"))
        return run

    @needs_littlefs
    def test_no_simulation_starts_the_compile_child_through_the_world_and_reads_the_store_it_was_given(self):
        # P458, the card's done-when: no child process and no store read bypasses what the Operation was given
        self.build_from_firmware()
        child_options = []

        def run(command, **options):
            if image_evidence.COMPILE_CHILD in command:
                child_options.append(options)
            return self.fake_tools('{"ok": true}\n')(command, **options)
        records = FakeDeployRecordStore()
        outside = FakeOutsideWorld(run=run, find_tool=found)
        result = run_operation(look_at_board.LookAtBoard(records=records), self.values(no_simulation=True), outside)
        self.assertEqual((result.status(), result.data["token"]), ("ok", self.token()))
        self.assertEqual(len(outside.ran), 3)
        self.assertIn("devs", outside.ran[0])
        self.assertIn("flash-id", outside.ran[1])
        self.assertEqual(outside.ran[2], [sys.executable, "-I", "-B", "-c", image_evidence.COMPILE_CHILD])
        self.assertEqual([json.loads(options["input"]) for options in child_options],
                         [[["firmware/main.py", str(self.project / "firmware" / "main.py")]]])
        self.assertEqual(records.asked, [MAC])

    def test_a_fake_child_that_names_a_syntax_error_is_the_no_token_sentence_and_no_real_child_runs(self):
        # P458: the parent reads what the world's `run` answers; firmware/main.py itself compiles, so the sentence is the fake's
        self.image.write_bytes(b"x")
        broken = '{"checking": "firmware/main.py"}\n{"name": "firmware/main.py", "kind": "syntax", "line": 3, "msg": "invalid syntax"}\n'
        result = run_operation(look_at_board.LookAtBoard(records=FakeDeployRecordStore()), self.values(no_simulation=True),
                               FakeOutsideWorld(run=self.fake_tools(broken), find_tool=found))
        self.assertEqual([(finding.code, finding.sentence) for finding in result.findings],
                         [("evidence_refuses", "no token: firmware/main.py, line 3 does not compile: invalid syntax")])
        self.assertEqual([line for line in result.lines if "no token" in line], [])

    def test_the_last_deploy_line_and_its_fix_come_from_the_store_the_look_was_given(self):
        # P458: the look reads `records`, never a store of its own, and the fix line names the path the LastDeploy carries
        self.image.write_bytes(b"x")
        recorded = deploy_record_store.LastDeploy(outcomes.RECORDED, "p", "ready", "2026-10-17T09:00:00+02:00")
        unreadable = deploy_record_store.LastDeploy(outcomes.NOT_CHECKED, why="spark's record of it cannot be read",
                                                    record_path=Path("/the/store/boards/record.json"))
        results = []
        for last in (recorded, unreadable):
            records = FakeDeployRecordStore(last=last)
            result = run_operation(look_at_board.LookAtBoard(records=records), self.values(),
                                   FakeOutsideWorld(run=self.fake_tools(), find_tool=found))
            self.assertEqual(records.asked, [MAC])
            results.append(result)
        self.assertIn("    spark's last deploy here: p, ready, 2026-10-17T09:00:00+02:00 (its store record, not read from the board)", results[0].lines)
        self.assertIn(("last deploy not checked: spark's record of it cannot be read", "repair or remove /the/store/boards/record.json, "
                      "then run look.py again"), [(found.sentence, found.fix) for found in results[1].findings])


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
        self.assertEqual(problems.splitlines()[:3], ["look: crashed, RuntimeError", "report this to the spark maintainers with the stderr traceback",
                                                     "Traceback (most recent call last):"])

    def test_the_sentence_of_a_crash_holds_no_message(self):
        self.run_the_scenario()
        said = self.go_with(self.crashing(), "--json")[1][-1]
        self.assertEqual(json.loads(said)["unchecked"][0]["sentence"], "RuntimeError: the traceback is on stderr")
        self.assertNotIn("/opt/someone", said)

    def test_the_bench_lists_the_look_for_the_frontends(self):
        from spark import bench
        self.assertEqual(sorted(bench.OPERATIONS), ["check-grant", "deploy", "issue-grant", "live", "look", "reach", "record-deploy",
                                                    "register-project", "show-bench"])
        self.assertIs(bench.OPERATIONS["look"], bench.look_at_board.LookAtBoard)
        self.assertIs(bench.OPERATIONS["deploy"], bench.deploy_image.DeployImage)

    def test_look_imports_no_area_module_but_spark_bench(self):
        tree = ast.parse(Path(look.__file__).read_text())
        imported = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)} \
            | {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        self.assertEqual(imported, {"sys", "pathlib", "spark.bench", "spark.bench.look_at_board", "spark.core.cli"})


class Retold(look_at_board.LookAtBoard):
    """The look told anew, to show that every interface reads the one class (P481)."""

    summary = "A sentence that only this test gives the look."
    details = "A paragraph that only this test gives the look."
    arguments = look_at_board.LookAtBoard.arguments + (Argument(("--retold",), "retold", bool, "a flag that only this test adds"),)


class HelpCase(unittest.TestCase):
    def help_of(self, operation=None):
        """What look.py --help prints, for `operation` (None: LookAtBoard)."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            look.main(["--help"], operation=operation)
        return out.getvalue()


class TheHelpTest(HelpCase):
    def test_help_says_what_it_reads_what_it_changes_the_restart_the_token_and_the_exit_codes(self):
        said = " ".join(self.help_of().split())
        for words in ("--project", "--port", "writes nothing", "erases nothing", "restarts", "token", "Exit codes", "0 ", "1 ", "2 "):
            self.assertIn(words, said)

    def test_the_sentence_and_the_paragraphs_are_the_operations_word_for_word(self):
        # P481: argparse prints a raw description and epilog as they are, so the moved texts appear unwrapped
        said = self.help_of()
        self.assertIn("\n" + look_at_board.LookAtBoard.summary + "\n", said)
        self.assertIn(look_at_board.LookAtBoard.details, said)

    def test_a_blank_line_stands_between_the_operations_paragraphs_and_the_clis_own(self):
        self.assertIn(look_at_board.LookAtBoard.details + "\n\n--json prints one envelope on stdout", self.help_of())


class TheOneSourceTest(HelpCase):
    """P481: the summary, the details and the Arguments are written once, on the Operation, and every interface reads them."""

    def test_help_shows_the_new_sentence_the_new_paragraph_and_the_new_flag(self):
        said = self.help_of(Retold())
        for words in (Retold.summary, Retold.details, "--retold", "a flag that only this test adds"):
            self.assertIn(words, said)
        self.assertNotIn(look_at_board.LookAtBoard.summary, said)

    def test_the_input_schema_holds_the_new_flag(self):
        self.assertEqual(Retold().input_schema()["properties"]["retold"]["description"], "a flag that only this test adds")

    def test_the_page_block_shows_the_new_sentence_and_the_new_flag(self):
        block = OperationHelpTable.render(Retold)
        self.assertTrue(block.startswith(Retold.summary + "\n"))
        self.assertIn("| `--retold` |  | a flag that only this test adds |", block)


if __name__ == "__main__":
    unittest.main()
