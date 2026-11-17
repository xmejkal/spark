"""P865 (#1231): the look names the board it will read, asks once, and remembers it in the person's store."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.bench import build_project_outside_world  # noqa: E402
from spark.bench import known_board  # noqa: E402
from spark.core.events import Event  # noqa: E402
from spark.core.operation import ASKS  # noqa: E402
from spark.core.replies import PERSON, YES_NO, Question, reply_strategy_for  # noqa: E402
from fakes import FakeOutsideWorld, FakeReporter  # noqa: E402
from test_board_look import C6_MAC, data, done, found  # noqa: E402
from test_look import LookScriptCase  # noqa: E402

#: Invented MACs, never a real board's: board A and board B.
MAC_A, MAC_B = "aa:bb:cc:dd:ee:ff", "aa:bb:cc:dd:12:34"
PORT = "/dev/cu.usbmodem101"
#: mpremote devs rows: a native USB board whose serial is its MAC, a bridge chip's 8-character serial, a native USB board
#: whose firmware set its serial (a custom build), and a CH340 with no serial.
NATIVE_A = "%s %s 303a:1001 Espressif USB JTAG/serial debug unit" % (PORT, MAC_A)
NATIVE_B = "%s %s 303a:1001 Espressif USB JTAG/serial debug unit" % (PORT, MAC_B)
BRIDGE = "/dev/cu.usbserial-01A2B3C4 01A2B3C4 10c4:ea60 Silicon Labs CP2104 USB to UART Bridge Controller"
FIRMWARE_SERIAL = "%s SPARK-S3LCD 303a:4001 Espressif Device" % PORT
NO_SERIAL = "/dev/cu.usbserial-1410 None 1a86:7523 USB Serial"


class TheLookAsksOnceTest(LookScriptCase):
    """The Done-when lines of P865, each on fake tools: no port is opened and no board is read."""

    KNOWS_THE_BOARD = False

    def setUp(self):
        super().setUp()
        self.yes_file = Path(tempfile.mkdtemp()) / "replies.json"  # the agent's own file, outside the project

    def look_at(self, rows, *argv, mac=MAC_A, replies_file=None, ask=True, as_json=True):
        """(exit code, stdout lines, stderr, the flash-id commands it ran) of look.py on fake tools: mpremote lists `rows`,
        esptool reads `mac` (None: no MAC). `replies_file` answers as the bench's builder would; `ask=False` fails the test
        when the look asks anything."""
        text = data("c6-flash-id.txt").replace(C6_MAC, mac) if mac else data("c6-flash-id-no-mac.txt")
        before = len(self.ran)

        def run(command, **kw):
            self.ran.append(command)
            return done(rows + "\n") if "devs" in command else done(text)
        outside = FakeOutsideWorld(run=run, find_tool=found, replies=reply_strategy_for(replies_file) if ask else None)
        given = (["--json"] if as_json else []) + (["--replies", str(replies_file)] if replies_file else [])
        code, said, err = self.go_with(outside, *argv, *given)
        return code, said, err, [each for each in self.ran[before:] if "flash-id" in each]

    def envelope(self, rows, *argv, **kw):
        code, said, _, read = self.look_at(rows, *argv, **kw)
        return code, json.loads(said[-1]), read

    def say_yes(self, envelope):
        """The agent's file after the person's yes to the open question of `envelope`."""
        self.yes_file.write_text(json.dumps({"replies": {envelope["data"]["open"][0]["key"]: True}}))
        return self.yes_file

    def kept(self):
        return known_board.KnownBoardStore().read(self.project)

    def test_1_no_known_board_asks_one_question_that_names_the_port_and_the_restart_and_reads_nothing(self):
        code, envelope, read = self.envelope(NATIVE_A)
        self.assertEqual((code, [item["code"] for item in envelope["unchecked"]], read), (2, ["needs_reply"], []))
        question = envelope["data"]["open"][0]
        self.assertEqual((question["kind"], question["asked_of"]), (YES_NO, PERSON))
        self.assertIn(PORT, question["text"])
        self.assertIn("restart", question["text"])

    def test_2_a_yes_reads_once_and_keeps_the_board_in_the_store_and_no_file_in_the_project(self):
        files = sorted(self.project.rglob("*"))
        yes = self.say_yes(self.envelope(NATIVE_A)[1])
        code, envelope, read = self.envelope(NATIVE_A, replies_file=yes)
        self.assertEqual((len(read), [item["code"] for item in envelope["unchecked"] if item["code"] == "needs_reply"]), (1, []))
        self.assertEqual((self.kept().mac, self.kept().usb_key), (MAC_A, "aabbccddeeff"))
        self.assertEqual(sorted(self.project.rglob("*")), files)

    def test_3_a_later_look_reads_the_kept_board_with_no_question(self):
        self.envelope(NATIVE_A, replies_file=self.say_yes(self.envelope(NATIVE_A)[1]))
        code, envelope, read = self.envelope(NATIVE_A, ask=False)
        self.assertEqual((len(read), envelope["data"].get("open")), (1, None))

    def test_4_another_board_stops_before_the_read_and_names_both_and_so_does_its_listed_port(self):
        self.envelope(NATIVE_A, replies_file=self.say_yes(self.envelope(NATIVE_A)[1]))
        for argv in ((), ("--port", PORT)):
            with self.subTest(argv=argv):
                code, envelope, read = self.envelope(NATIVE_B, *argv, mac=MAC_B)
                said = json.dumps(envelope["unchecked"])
                self.assertEqual((code, read), (2, []))
                self.assertIn("other_board", [item["code"] for item in envelope["unchecked"]])
                self.assertIn("MAC ends 12:34", said)
                self.assertIn("MAC ends ee:ff", said)
        self.assertEqual(self.kept().mac, MAC_A)

    def test_4_the_same_trusted_serial_with_another_mac_after_the_read_says_it_restarted_and_keeps_the_record(self):
        self.envelope(BRIDGE, replies_file=self.say_yes(self.envelope(BRIDGE)[1]))
        code, envelope, read = self.envelope(BRIDGE, mac=MAC_B, ask=False)
        other = [item for item in envelope["unchecked"] if item["code"] == "other_board"]
        self.assertEqual((code, len(read), len(other), envelope["next"]), (2, 1, 1, []))
        self.assertIn("did restart", other[0]["sentence"])
        self.assertEqual(self.kept().mac, MAC_A)

    def test_5_a_yes_that_one_look_used_does_not_answer_the_next(self):
        yes = self.say_yes(self.envelope(NO_SERIAL)[1])
        self.assertEqual(len(self.envelope(NO_SERIAL, replies_file=yes)[2]), 1)
        self.assertEqual([value for value in json.loads(yes.read_text())["replies"].values()], [None])
        code, envelope, read = self.envelope(NO_SERIAL, replies_file=yes)
        self.assertEqual((code, read, [item["code"] for item in envelope["unchecked"]]), (2, [], ["needs_reply"]))

    def test_6_a_bridge_board_is_asked_once(self):
        self.envelope(BRIDGE, replies_file=self.say_yes(self.envelope(BRIDGE)[1]))
        self.assertEqual(len(self.envelope(BRIDGE, ask=False)[2]), 1)

    def test_6_a_native_board_whose_firmware_set_its_serial_is_asked_on_every_look(self):
        self.envelope(FIRMWARE_SERIAL, replies_file=self.say_yes(self.envelope(FIRMWARE_SERIAL)[1]))
        self.assertEqual((self.kept().mac, self.kept().usb_key), (MAC_A, None))
        code, envelope, read = self.envelope(FIRMWARE_SERIAL)
        self.assertEqual((code, read), (2, []))
        self.assertIn("firmware", envelope["data"]["open"][0]["why"])

    def test_7_no_new_line_holds_the_full_mac(self):
        runs = [self.look_at(NATIVE_A, as_json=as_json) for as_json in (True, False)]  # the open question
        self.yes_file.write_text(json.dumps({"replies": {json.loads(runs[0][1][-1])["data"]["open"][0]["key"]: False}}))
        runs.append(self.look_at(NATIVE_A, replies_file=self.yes_file))  # a no
        self.envelope(NATIVE_A, replies_file=self.say_yes(self.envelope(NATIVE_A)[1]))  # kept
        runs += [self.look_at(NATIVE_B, mac=MAC_B, as_json=as_json) for as_json in (True, False)]  # another board
        for code, said, err, _ in runs:
            for mac in (MAC_A, MAC_B):
                self.assertNotIn(mac, "\n".join(said) + err)
        self.envelope(BRIDGE, replies_file=self.say_yes(self.envelope(BRIDGE)[1]))  # the kept note, then a board read that is not it
        for envelope in (self.envelope(BRIDGE, mac=MAC_B, ask=False)[1],):
            new = [item for item in envelope["unchecked"] if item["code"] == "other_board"] + [envelope.get("notes")]
            self.assertNotIn(MAC_B, json.dumps(new))
            self.assertNotIn(MAC_A, json.dumps(new))

    def test_7_the_kept_note_holds_no_full_mac(self):
        code, said, err, _ = self.look_at(BRIDGE, replies_file=self.say_yes(self.envelope(BRIDGE)[1]), as_json=False)
        new = [line for line in said if "kept" in line]
        self.assertTrue(new, said)
        self.assertNotIn(MAC_A, "\n".join(new))

    def test_8_no_mac_read_after_a_yes_keeps_nothing_and_says_so(self):
        code, envelope, read = self.envelope(NATIVE_A, mac=None, replies_file=self.say_yes(self.envelope(NATIVE_A)[1]))
        self.assertEqual((len(read), self.kept()), (1, None))
        self.assertIn("not kept: the board's MAC could not be read", envelope["notes"])

    def test_9_an_unlisted_port_reads_with_no_question_and_keeps_nothing(self):
        code, envelope, read = self.envelope(NATIVE_A, "--port", "/dev/cu.nowhere", ask=False)
        self.assertEqual((len(read), self.kept()), (1, None))

    def test_10_the_begin_comes_before_the_list(self):
        at_the_begin = []

        class Watching(FakeReporter):
            """Fake Reporter that also keeps what the outside had run when each event came."""

            def report(self, event):
                super().report(event)
                at_the_begin.append(list(outside.ran))
        outside = FakeOutsideWorld(run=lambda command, **kw: done(NATIVE_A + "\n"), find_tool=found, reporter=Watching(),
                                   replies=reply_strategy_for(None))
        self.go_with(outside, "--json")
        self.assertEqual((outside.reporter.events, at_the_begin), ([Event.begin("look")], [[]]))
        self.assertIn("devs", outside.ran[0])

    def test_a_no_reads_nothing_and_keeps_nothing(self):
        key = self.envelope(NATIVE_A)[1]["data"]["open"][0]["key"]
        self.yes_file.write_text(json.dumps({"replies": {key: False}}))
        code, envelope, read = self.envelope(NATIVE_A, replies_file=self.yes_file)
        self.assertEqual((code, read, [item["code"] for item in envelope["unchecked"]], self.kept()), (2, [], ["answered_no"], None))

    def test_a_record_of_another_folder_counts_as_none(self):
        self.envelope(NATIVE_A, replies_file=self.say_yes(self.envelope(NATIVE_A)[1]))
        path = known_board.KnownBoardStore.find_path(self.project)
        path.write_text(json.dumps(dict(json.loads(path.read_text()), project="/somewhere/else")))
        self.assertEqual(self.envelope(NATIVE_A)[1]["data"]["open"][0]["asked_of"], PERSON)

    def test_a_record_that_cannot_be_read_stops_before_the_read(self):
        path = known_board.KnownBoardStore.find_path(self.project)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{not json")
        code, envelope, read = self.envelope(NATIVE_A, ask=False)
        self.assertEqual((code, read, [item["code"] for item in envelope["unchecked"]]), (2, [], ["known_board_unreadable"]))


class TheBenchBuilderTest(unittest.TestCase):
    """The bench's builder answers from the --replies file, as research's does (P865)."""

    def test_the_replies_file_answers_the_look(self):
        file = Path(tempfile.mkdtemp()) / "replies.json"
        file.write_text(json.dumps({"replies": {"look.read_board.abcd": True}}))
        outside = build_project_outside_world(Path(tempfile.mkdtemp()), (ASKS,), FakeReporter(), {"replies": file, "json": True})
        question = Question("look.read_board.abcd", "Read?", YES_NO, PERSON)
        self.assertIs(outside.replies(question).value, True)


if __name__ == "__main__":
    unittest.main()
