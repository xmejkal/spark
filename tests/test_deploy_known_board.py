"""P892 (#1266): the deploy asks the board question before its read, as the look does, and stops before any read for
another board or for a project that keeps no board."""

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit
from suite_runs import needs_littlefs  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.bench import bench_privacy  # noqa: E402
from spark.bench import board_doctor  # noqa: E402
from spark.bench import known_board  # noqa: E402
from spark.core.events import TerminalReporter  # noqa: E402
from spark.core.privacy import MaskingReporter  # noqa: E402
from spark.core.replies import ReplyStrategy, reply_strategy_for  # noqa: E402
from fakes import FakeConsent, FakeConsoleProbe, FakeOutsideWorld  # noqa: E402
from test_board_look import C6_MAC, C6_PORT, data  # noqa: E402
from test_deploy_gate import GateCase  # noqa: E402

#: An invented MAC, never a real board's: another board.
OTHER_MAC = "aa:bb:cc:dd:12:34"
#: mpremote devs rows: another native USB board on the C6's port, a native USB board whose firmware set its serial, and a
#: CH340 with no serial.
OTHER_ROW = "%s %s 303a:1001 Espressif USB JTAG/serial debug unit" % (C6_PORT, OTHER_MAC)
FIRMWARE_ROW = "%s SPARK-S3LCD 303a:4001 Espressif Device" % C6_PORT
NO_SERIAL_PORT = "/dev/cu.usbserial-1410"
NO_SERIAL_ROW = "%s None 1a86:7523 USB Serial" % NO_SERIAL_PORT
#: What the look says that is untrue in the deploy (P892, test 12).
LOOK_WORDS = ("Nothing is erased or written", "run look.py again when you want to read it", "say yes to read this board",
              "except for a port the list does not hold")


class RecordingReplies(ReplyStrategy):
    """Fake ReplyStrategy: keeps each Question it is asked in `asked`, and answers as the replies file at `path` does (None:
    nothing now)."""

    def __init__(self, path=None):
        self.asked, self.given = [], reply_strategy_for(path)

    def reply(self, question):
        self.asked.append(question)
        return self.given.reply(question)


class DeployKnownBoardCase(GateCase):
    """The deploy on fake tools, with the C6 kept as the project's board, and the replies of the agent's own file."""

    def setUp(self):
        super().setUp()
        self.yes_file = Path(tempfile.mkdtemp()) / "replies.json"  # the agent's own file, outside the project
        self.replies = RecordingReplies()

    def outside_world(self, run, consent, reporter, clock=None):
        world = super().outside_world(run, consent, reporter, clock)
        return FakeOutsideWorld(run, find_tool=self.find_tool, reporter=world.reporter, clock=world.clock,
                                make_consent=world._make_consent, replies=self.replies)

    def forget(self):
        """The store keeps no board for this project."""
        known_board.KnownBoardStore.find_path(self.project).unlink()

    def answer(self, value, key=None):
        """The agent's file with `value` for the open key of the last question asked (or `key`), read by the next deploy."""
        self.yes_file.write_text(json.dumps({"replies": {key or self.replies.asked[-1].key: value}}))
        self.replies = RecordingReplies(self.yes_file)

    def go(self, rows=None, *argv, mac=None, consent=None):
        """(exit code, the envelope, stderr, the flash-id commands it ran) of `deploy.py --json --token`, with the agent's
        file once it exists: mpremote lists `rows` (None: the C6), esptool reads `mac` (None: the C6's)."""
        token = self.token()  # the token's look reads the board too: counted before `before`
        before = len(self.ran)
        given = ["--replies", str(self.yes_file)] if self.yes_file.exists() else []
        code, said, err = self.deploy("--json", "--token", token, *argv, *given, consent=consent or FakeConsent(True),
                                      devs_text=rows, text=data("c6-flash-id.txt").replace(C6_MAC, mac) if mac else None)
        return code, json.loads(said.splitlines()[-1]), err, [each for each in self.ran[before:] if "flash-id" in each]

    def codes(self, envelope):
        return [item["code"] for item in envelope["unchecked"] + envelope["problems"]]

    def all_argv(self, envelope):
        return [arg for step in envelope["next"] for arg in step["argv"]]


@needs_littlefs
class TheDeployAsksTheBoardQuestionTest(DeployKnownBoardCase):
    """The plan's tests 1 to 11, 13 and 14."""

    def setUp(self):
        super().setUp()
        self.run_the_scenario()

    def test_1_the_kept_board_is_read_with_no_question_and_the_deploy_goes_on(self):
        code, envelope, _, read = self.go()
        self.assertEqual((code, len(read), self.replies.asked), (0, 1, []))
        self.assertEqual(self.flashed()[0], "erase-flash")

    def test_2_another_board_stops_before_any_read_and_names_the_look_with_its_reason(self):
        code, envelope, _, read = self.go(OTHER_ROW, mac=OTHER_MAC)
        self.assertEqual((code, self.codes(envelope), read, self.replies.asked, self.flashed()), (2, ["other_board"], [], [], []))
        self.assertIn("did not restart", envelope["unchecked"][0]["sentence"])
        step = envelope["next"][0]
        self.assertEqual((step["op"], step["needs_person"]), ("look", True))
        self.assertIn("not this project's", step["why"])
        self.assertNotIn(None, self.all_argv(envelope))
        self.assertNotIn("None", self.all_argv(envelope))

    def test_3_no_kept_board_and_a_serial_stops_before_any_read_and_names_not_kept(self):
        self.forget()
        code, envelope, _, read = self.go()
        self.assertEqual((code, self.codes(envelope), read, self.replies.asked), (2, ["no_known_board"], [], []))
        self.assertIn("not kept", envelope["unchecked"][0]["fix"])
        self.assertEqual((envelope["next"][0]["op"], envelope["next"][0]["needs_person"]), ("look", True))

    def test_4_a_firmware_serial_with_no_reply_is_asked_and_the_next_step_is_the_same_deploy_with_replies(self):
        self.know_the_board(C6_MAC, None)  # kept while a firmware set the serial: spark cannot tell this board
        code, envelope, _, read = self.go(FIRMWARE_ROW)
        self.assertEqual((code, self.codes(envelope), read), (2, ["needs_reply"], []))
        question = envelope["data"]["open"][0]
        self.assertTrue(question["key"].startswith("deploy.read_board."), question)
        self.assertEqual((envelope["data"]["port"], envelope["data"]["product"]), (C6_PORT, "Espressif Device"))
        step = envelope["next"][0]
        self.assertEqual((step["op"], step["needs_person"], step["needs_yes"]), ("deploy", True, False))
        self.assertEqual(step["argv"][-2:], ["--replies", "<your replies file>"])
        self.assertIn("--token", step["argv"])

    def test_5_a_yes_in_the_file_reads_the_board_once_and_the_deploy_goes_on_and_the_yes_is_used(self):
        self.know_the_board(C6_MAC, None)
        self.go(FIRMWARE_ROW)
        self.answer(True)
        code, envelope, _, read = self.go(FIRMWARE_ROW)
        self.assertEqual((code, len(read), self.flashed()[0]), (0, 1, "erase-flash"))
        self.assertEqual(list(json.loads(self.yes_file.read_text())["replies"].values()), [None])

    def test_6_a_no_reads_nothing_and_names_deploy_and_a_value_that_is_no_boolean_leaves_it_open(self):
        self.know_the_board(C6_MAC, None)
        self.go(FIRMWARE_ROW)
        key = self.replies.asked[-1].key
        self.answer(False)
        code, envelope, _, read = self.go(FIRMWARE_ROW)
        self.assertEqual((code, self.codes(envelope), read, envelope["next"]), (2, ["answered_no"], [], []))
        self.assertIn("deploy.py", envelope["unchecked"][0]["fix"])
        self.answer("yes", key)
        code, envelope, _, read = self.go(FIRMWARE_ROW)
        self.assertEqual((code, self.codes(envelope), read), (2, ["needs_reply"], []))

    def test_7_a_yes_under_the_looks_key_does_not_answer_the_deploy(self):
        self.know_the_board(C6_MAC, None)
        self.go(FIRMWARE_ROW)
        key = self.replies.asked[-1].key
        self.answer(True, "look." + key[len("deploy."):])
        code, envelope, _, read = self.go(FIRMWARE_ROW)
        self.assertEqual((code, self.codes(envelope), read), (2, ["needs_reply"], []))

    def test_8_a_named_port_with_no_serial_and_a_port_the_list_does_not_hold_are_both_asked(self):
        code, envelope, _, read = self.go(NO_SERIAL_ROW, "--port", NO_SERIAL_PORT)
        self.assertEqual((code, self.codes(envelope), read), (2, ["needs_reply"], []))
        code, envelope, _, read = self.go(None, "--port", "/dev/cu.nowhere")
        self.assertEqual((code, self.codes(envelope), read), (2, ["needs_reply"], []))
        question = envelope["data"]["open"][0]
        self.assertIn("/dev/cu.nowhere", question["text"])
        self.assertNotIn("reports no USB serial", question["text"] + question["why"])
        self.assertIsNone(envelope["data"]["product"])

    def test_9_another_mac_after_the_read_stops_before_the_erase_also_after_a_yes(self):
        consent = FakeConsent(True)
        code, envelope, _, read = self.go(mac=OTHER_MAC, consent=consent)  # the kept board's serial, another MAC
        self.assertEqual((code, self.codes(envelope), len(read), self.flashed(), consent.asked), (2, ["other_board"], 1, [], []))
        self.assertIn("did restart", envelope["unchecked"][0]["sentence"])
        self.know_the_board(C6_MAC, None)
        self.go(FIRMWARE_ROW)
        self.answer(True)
        code, envelope, _, read = self.go(FIRMWARE_ROW, mac=OTHER_MAC, consent=consent)
        self.assertEqual((code, self.codes(envelope), len(read), self.flashed(), consent.asked), (2, ["other_board"], 1, [], []))
        self.assertEqual(known_board.KnownBoardStore().read(self.project).mac, C6_MAC)  # nothing was kept

    def test_10_a_kept_record_and_a_replies_file_that_cannot_be_read_are_one_finding_each(self):
        path = known_board.KnownBoardStore.find_path(self.project)
        path.write_text("{not json")
        code, envelope, _, read = self.go()
        self.assertEqual((code, self.codes(envelope), read), (2, ["known_board_unreadable"], []))
        self.know_the_board(C6_MAC, known_board.comparable_key(C6_MAC))
        self.yes_file.write_text("{not json")
        code, envelope, _, read = self.go()
        self.assertEqual((code, self.codes(envelope), read), (2, ["bad_argument"], []))

    def test_11_a_dry_run_asks_nothing_and_leaves_the_replies_file_as_it_is(self):
        self.yes_file.write_text(json.dumps({"replies": {"deploy.read_board.abcd": True}}))
        before = self.yes_file.read_text()
        code, _, _ = self.deploy("--dry-run", "--replies", str(self.yes_file))
        self.assertEqual((code, self.replies.asked, self.yes_file.read_text()), (0, [], before))
        self.assertFalse([each for each in self.ran if "devs" in each])

    def test_13_a_yes_with_no_terminal_and_no_grant_reads_once_and_ends_at_the_closed_gate(self):
        self.know_the_board(C6_MAC, None)
        self.go(FIRMWARE_ROW)
        self.answer(True)
        token = self.token()
        before = len(self.ran)
        code, said, _ = self.deploy("--json", "--token", token, "--replies", str(self.yes_file), devs_text=FIRMWARE_ROW)
        envelope = json.loads(said.splitlines()[-1])
        self.assertEqual((code, self.codes(envelope), self.flashed()), (2, ["no_terminal"], []))
        self.assertEqual(len([each for each in self.ran[before:] if "flash-id" in each]), 1)
        self.assertIn("--token %s" % token, envelope["data"]["run_in_terminal"])
        self.assertNotIn("--replies", envelope["data"]["run_in_terminal"])

    def test_14_the_stops_lines_show_the_key_and_the_store_path_whole(self):
        self.know_the_board(C6_MAC, None)
        stream = io.StringIO()
        reporter = MaskingReporter(TerminalReporter(stream), bench_privacy.privacy_for(self.project))
        self.deploy("--json", "--token", self.token(), consent=FakeConsent(True), devs_text=FIRMWARE_ROW, reporter=reporter)
        key = self.replies.asked[-1].key
        self.assertIn('{"replies": {"%s": true}}' % key, stream.getvalue())
        path = known_board.KnownBoardStore.find_path(self.project)
        path.write_text("{not json")
        code, _, err = self.deploy("--json", "--token", self.token(), consent=FakeConsent(True), reporter=reporter)
        self.assertIn(str(path), err)


class TheNamedPortOffUsbTest(DeployKnownBoardCase):
    """P1049: deploy.py --port on a port the list does not hold, the board question answered yes and esptool failing: the
    doctor's plug_in step becomes the asleep fix when firmware/ calls deepsleep, as look.py --port says it."""

    def off_usb(self, *argv):
        """(exit code, stdout, stderr) of the deploy after the person's yes to the board question."""
        go = dict(consent=FakeConsent(True), devs="mpremote-devs-none.txt", look_fails=True, probe=FakeConsoleProbe(""))
        named = ("--token", "aaaa-bbbb", "--port", "/dev/cu.usbmodem101")
        if not self.yes_file.exists():
            self.deploy(*named, **go)
            self.answer(True)
        return self.deploy(*argv, *named, "--replies", str(self.yes_file), **go)

    def test_a_deepsleep_call_gives_the_asleep_fix_as_the_doctor_s_next_step(self):
        self.run_the_scenario()
        (self.project / "firmware" / "main.py").write_text("import machine\nmachine.deepsleep(1)\n")
        code, _, problems = self.off_usb()
        self.assertEqual((code, self.flashed()), (2, []))
        self.assertIn("deploy.py: could not read the board on /dev/cu.usbmodem101", problems)
        last = problems.strip().splitlines()[-1]
        self.assertTrue(last.startswith("  next    What spark knows: the port you named is not on USB, and the project's firmware "
                                        "calls deepsleep (firmware/main.py:2)."), last)
        self.assertNotIn("plug the board straight", problems)
        envelope = json.loads(self.off_usb("--json")[1].splitlines()[-1])
        (item,) = envelope["unchecked"]
        self.assertEqual((item["code"], item["fix"]), ("board_not_read", last[len("  next    "):]))
        (step,) = envelope["next"]  # P1048: the look of the fix's step 1, with no --port
        self.assertEqual((step["op"], step["argv"], step["needs_person"]), ("look", ["--project", str(self.project.resolve())], True))

    def test_without_a_deepsleep_call_the_doctor_s_plug_in_step_stays(self):
        self.run_the_scenario()
        code, _, problems = self.off_usb()
        self.assertEqual(code, 2)
        self.assertEqual(problems.strip().splitlines()[-1], "  next    " + board_doctor.step_sentence("plug_in"))
        envelope = json.loads(self.off_usb("--json")[1].splitlines()[-1])
        (item,) = envelope["unchecked"]
        self.assertEqual((item["code"], item["fix"]), ("board_not_read", board_doctor.step_sentence("plug_in")))
        self.assertEqual(envelope["next"], [])  # P1048 D6: the doctor's own step gives no look step


if __name__ == "__main__":
    unittest.main()
