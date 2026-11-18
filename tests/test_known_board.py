"""P865 (#1231): the look names the board it will read, asks once, and remembers it in the person's store."""

import contextlib
import io
import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import look  # noqa: E402
from spark.bench import build_project_outside_world  # noqa: E402
from spark.bench import known_board  # noqa: E402
from spark.bench import look_at_board  # noqa: E402
from spark.bench.board_look import Port  # noqa: E402
from spark.records import store  # noqa: E402
from suite_runs import needs_littlefs  # noqa: E402
from spark.core.events import Event  # noqa: E402
from spark.core.operation import ASKS  # noqa: E402
from spark.core.errors import SparkError  # noqa: E402
from spark.core.replies import PERSON, YES_NO, Question, Reply, reply_strategy_for  # noqa: E402
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


class KnownBoardCase(LookScriptCase):
    """The look on fake tools, with no board kept at the start: no port is opened and no board is read."""

    KNOWS_THE_BOARD = False

    def setUp(self):
        super().setUp()
        self.yes_file = Path(tempfile.mkdtemp()) / "replies.json"  # the agent's own file, outside the project

    def look_at(self, rows, *argv, mac=MAC_A, replies_file=None, ask=True, as_json=True, fail=False):
        """(exit code, stdout lines, stderr, the flash-id commands it ran) of look.py on fake tools: mpremote lists `rows`,
        esptool reads `mac` (None: no MAC). `replies_file` answers as the bench's builder would; `ask=False` fails the test
        when the look asks anything."""
        text = data("c6-flash-id.txt").replace(C6_MAC, mac) if mac else data("c6-flash-id-no-mac.txt")
        before = len(self.ran)

        def run(command, **kw):
            self.ran.append(command)
            return done(rows + "\n") if "devs" in command else done(text, 1 if fail else 0)
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

    def keep(self, rows, mac=MAC_A):
        """The board on `rows`, read as `mac`, kept after a yes, as a person's first look keeps it."""
        self.envelope(rows, mac=mac, replies_file=self.say_yes(self.envelope(rows, mac=mac)[1]))
        self.assertEqual(self.kept().mac, mac)

    def write_record(self, **changes):
        """The kept record of NATIVE_A with `changes`, written by hand."""
        self.keep(NATIVE_A)
        path = known_board.KnownBoardStore.find_path(self.project)
        path.write_text(json.dumps(dict(json.loads(path.read_text()), **changes)))

    def codes(self, envelope):
        return [item["code"] for item in envelope["unchecked"] + envelope["problems"]]



class TheLookAsksOnceTest(KnownBoardCase):
    """The Done-when lines of P865."""

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

    def test_the_kept_board_under_micropython_is_known_by_the_mac_part_of_its_serial(self):
        # the P472 bench: the same S3 shows its MAC in ROM download mode and the MAC plus two bytes under MicroPython
        self.envelope(NATIVE_A, replies_file=self.say_yes(self.envelope(NATIVE_A)[1]))
        micropython = "%s aabbccddeeff0001 303a:4001 Espressif Device" % PORT
        self.assertEqual(len(self.envelope(micropython, ask=False)[2]), 1)

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


class TheReviewOfPullRequest1264Test(KnownBoardCase):
    """P865's review round: each test pins one finding of the lens or the refuter (H1 to H5, T1 to T9)."""

    def test_h1_a_yes_to_another_board_with_a_firmware_serial_makes_it_the_projects_board(self):
        self.keep(FIRMWARE_SERIAL)
        code, envelope, read = self.envelope(FIRMWARE_SERIAL, mac=MAC_B)
        self.assertEqual(read, [])
        self.assertIn("in place of the old one", envelope["data"]["open"][0]["why"])
        code, envelope, read = self.envelope(FIRMWARE_SERIAL, mac=MAC_B, replies_file=self.say_yes(envelope))
        self.assertEqual((len(read), "other_board" in self.codes(envelope), self.kept().mac), (1, False, MAC_B))
        self.assertIn("in place of the old one", " ".join(envelope["notes"]))

    @needs_littlefs
    def test_h1_the_replaced_board_gets_a_token_as_any_kept_board(self):
        self.run_the_scenario()
        self.keep(FIRMWARE_SERIAL)
        yes = self.say_yes(self.envelope(FIRMWARE_SERIAL, mac=MAC_B)[1])
        code, envelope, read = self.envelope(FIRMWARE_SERIAL, mac=MAC_B, replies_file=yes)
        self.assertTrue(envelope["data"]["token"], envelope)
        self.assertEqual([step["op"] for step in envelope["next"]], ["deploy"])

    def test_h1_a_named_port_with_no_serial_reads_with_no_yes_and_then_stops_as_another_board_and_names_the_way_out(self):
        self.keep(NATIVE_A)
        code, envelope, read = self.envelope(NO_SERIAL, "--port", "/dev/cu.usbserial-1410", mac=MAC_B, ask=False)
        other = [item for item in envelope["unchecked"] if item["code"] == "other_board"]
        self.assertEqual((code, len(read), self.kept().mac), (2, 1, MAC_A))
        self.assertIn("without --port", other[0]["fix"])

    def test_n1_a_named_port_of_another_box_with_the_same_firmware_serial_is_asked(self):
        self.keep(FIRMWARE_SERIAL)
        code, envelope, read = self.envelope(FIRMWARE_SERIAL, "--port", PORT, mac=MAC_B)
        self.assertEqual((code, read, self.codes(envelope)), (2, [], ["needs_reply"]))

    def test_n1_a_named_port_of_a_firmware_serial_with_no_kept_board_is_asked(self):
        code, envelope, read = self.envelope(FIRMWARE_SERIAL, "--port", PORT)
        self.assertEqual((code, read, self.codes(envelope)), (2, [], ["needs_reply"]))

    def test_h3_the_next_step_keeps_the_port_and_the_evidence_flag(self):
        argv = self.envelope(NATIVE_A, "--port", PORT, "--no-simulation")[1]["next"][0]["argv"]
        self.assertEqual(argv[argv.index("--port") + 1], PORT)
        self.assertIn("--no-simulation", argv)

    def test_h4_a_replies_file_that_cannot_be_written_stops_with_a_sentence_and_reads_nothing(self):
        yes = self.say_yes(self.envelope(NATIVE_A)[1])
        yes.chmod(0o444)
        self.addCleanup(yes.chmod, 0o644)
        code, envelope, read = self.envelope(NATIVE_A, replies_file=yes)
        self.assertEqual((code, read, self.codes(envelope)), (2, [], ["bad_argument"]))

    def test_h4_a_record_with_no_time_is_unreadable(self):
        self.write_record(at=None)
        code, envelope, read = self.envelope(NATIVE_B, mac=MAC_B, ask=False)
        self.assertEqual((code, read, self.codes(envelope)), (2, [], ["known_board_unreadable"]))

    def test_h5_a_yes_given_to_a_look_that_stops_before_the_gate_is_used_all_the_same(self):
        yes = self.say_yes(self.envelope(NATIVE_A)[1])
        self.assertIn("two_boards", self.codes(self.envelope(NATIVE_A + "\n" + NO_SERIAL, replies_file=yes)[1]))
        code, envelope, read = self.envelope(NATIVE_A, replies_file=yes)
        self.assertEqual((code, read, self.codes(envelope)), (2, [], ["needs_reply"]))

    def test_t1_only_the_json_value_true_is_a_yes(self):
        key = self.envelope(NATIVE_A)[1]["data"]["open"][0]["key"]
        for value in ("yes", 1, "true"):
            with self.subTest(value=value):
                self.yes_file.write_text(json.dumps({"replies": {key: value}}))
                code, envelope, read = self.envelope(NATIVE_A, replies_file=self.yes_file)
                self.assertEqual((read, self.codes(envelope)), ([], ["needs_reply"]))

    def test_t2_every_look_key_of_the_file_is_cleared_and_no_other_key(self):
        key = self.envelope(NATIVE_A)[1]["data"]["open"][0]["key"]
        self.yes_file.write_text(json.dumps({"replies": {key: True, "look.switch_board.ffff": True, "physical.mounting_holes": 4}}))
        self.envelope(NATIVE_A, replies_file=self.yes_file)
        self.assertEqual(json.loads(self.yes_file.read_text())["replies"],
                         {key: None, "look.switch_board.ffff": None, "physical.mounting_holes": 4})

    def test_t3_a_read_that_fails_has_used_the_yes(self):
        yes = self.say_yes(self.envelope(NATIVE_A)[1])
        self.assertEqual(len(self.envelope(NATIVE_A, replies_file=yes, fail=True)[2]), 1)
        code, envelope, read = self.envelope(NATIVE_A, replies_file=yes)
        self.assertEqual((read, self.codes(envelope)), ([], ["needs_reply"]))

    def test_t4_a_record_with_an_empty_mac_is_unreadable(self):
        self.write_record(mac="")
        self.assertEqual(self.codes(self.envelope(NATIVE_A, ask=False)[1]), ["known_board_unreadable"])

    def test_t4_an_empty_serial_never_matches_an_empty_usb_key(self):
        row = Port("/dev/cu.usbserial-1410", "None", "1a86:7523", "USB Serial")
        known = known_board.KnownBoard("/p", MAC_A, "", "xiao-esp32-c6", "a test", "2026-11-17T18:00:00+01:00")
        self.assertEqual(known_board.tell(row, known), "cannot_tell")

    def test_t5_a_yes_to_switch_board_replaces_the_record(self):
        self.keep(NATIVE_A)
        yes = self.say_yes(self.envelope(NATIVE_B, mac=MAC_B)[1])
        code, envelope, read = self.envelope(NATIVE_B, mac=MAC_B, replies_file=yes)
        self.assertEqual((len(read), self.kept().mac, self.kept().usb_key), (1, MAC_B, "aabbccdd1234"))

    def test_t6_a_store_that_refuses_the_write_leaves_the_look_standing_with_a_note(self):
        class RefusingStore(known_board.KnownBoardStore):
            """Fake KnownBoardStore: reads as the store does, and refuses every write."""

            def write(self, known):
                raise store.StoreError("the store refuses the write", code="store_not_writable")
        yes = self.say_yes(self.envelope(NATIVE_A)[1])
        outside = FakeOutsideWorld(run=lambda command, **kw: done(NATIVE_A + "\n") if "devs" in command
                                   else done(data("c6-flash-id.txt").replace(C6_MAC, MAC_A)), find_tool=found, replies=reply_strategy_for(yes))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            look.main(["--project", str(self.project), "--json", "--replies", str(yes)], outside=outside,
                      operation=look_at_board.LookAtBoard(known=RefusingStore()))
        envelope = json.loads(out.getvalue().splitlines()[-1])
        self.assertEqual(envelope["notes"], ["not kept: the store refuses the write"])
        self.assertNotIn("crash", self.codes(envelope))

    @needs_littlefs
    def test_t7_another_board_after_the_read_gives_no_token_and_no_deploy_step(self):
        self.run_the_scenario()
        self.keep(BRIDGE)
        self.assertEqual([step["op"] for step in self.envelope(BRIDGE, ask=False)[1]["next"]], ["deploy"])  # the kept board has one
        envelope = self.envelope(BRIDGE, mac=MAC_B, ask=False)[1]
        self.assertEqual((envelope["data"]["token"], envelope["next"]), (None, []))

    def test_t8_a_project_with_no_board_record_stops_before_any_question(self):
        self.board("no-such-board")
        code, envelope, read = self.envelope(NATIVE_A, ask=False)
        self.assertEqual((code, read, self.codes(envelope)), (2, [], ["no_board_record"]))

    def test_t9_the_kept_record_is_private(self):
        self.keep(NATIVE_A)
        path = known_board.KnownBoardStore.find_path(self.project)
        self.assertEqual((stat.S_IMODE(path.stat().st_mode), stat.S_IMODE(path.parent.stat().st_mode)), (0o600, 0o700))


class TheLastReviewRoundTest(KnownBoardCase):
    """P865's last review round: a true `why` (R1), a tty alias of a listed port (R2), a true fix (R3), and six pins (E1 to E6)."""

    def test_r1_a_board_with_a_mac_shaped_serial_is_not_told_that_its_firmware_set_it(self):
        self.write_record(usb_key=None)
        question = self.envelope(NATIVE_B, mac=MAC_B)[1]["data"]["open"][0]
        self.assertIn("MAC ends 12:34", question["text"])
        self.assertNotIn("This board's USB serial is set by its firmware", question["why"])
        self.assertNotIn("asks every time", question["why"])

    def test_r2_a_tty_alias_of_a_listed_port_is_asked(self):
        code, envelope, read = self.envelope(NATIVE_A, "--port", "/dev/tty.usbmodem101")
        self.assertEqual((code, read, self.codes(envelope)), (2, [], ["needs_reply"]))

    def test_r3_another_board_on_an_unlisted_port_is_not_sent_to_a_look_without_port(self):
        self.keep(NATIVE_A)
        envelope = self.envelope(NATIVE_A, "--port", "/dev/cu.nowhere", mac=MAC_B, ask=False)[1]
        other = [item for item in envelope["unchecked"] if item["code"] == "other_board"]
        self.assertNotIn("without --port", other[0]["fix"])

    def test_e1_the_yes_is_used_also_by_a_look_with_port(self):
        yes = self.say_yes(self.envelope(NATIVE_A, "--port", PORT)[1])
        self.assertEqual(len(self.envelope(NATIVE_A, "--port", PORT, replies_file=yes)[2]), 1)
        self.assertEqual(list(json.loads(yes.read_text())["replies"].values()), [None])

    def test_e2_a_bridge_serial_of_twelve_characters_or_more_is_no_mac(self):
        row = Port("/dev/cu.usbserial-0123", "0123456789ABCDEF", "10c4:ea60", "CP2102N USB to UART Bridge Controller")
        self.assertEqual(known_board.named(row), "USB serial ends CDEF")

    def test_e3_the_next_step_keeps_ignore_older_runs(self):
        self.assertIn("--ignore-older-runs", self.envelope(NATIVE_A, "--ignore-older-runs")[1]["next"][0]["argv"])

    def test_e4_no_replace_sentence_when_no_board_is_kept(self):
        self.assertNotIn("in place of", self.envelope(NO_SERIAL)[1]["data"]["open"][0]["why"])

    def test_e5_no_replace_sentence_on_a_first_question_or_a_kept_board(self):
        row = Port(PORT, MAC_A, "303a:1001", "Espressif USB JTAG/serial debug unit")
        known = known_board.KnownBoard("/p", MAC_A, None, "xiao-esp32-c6", "a test", "2026-11-17T18:00:00+01:00")
        for state, kept in (("none", None), ("same", known)):
            with self.subTest(state=state):
                self.assertNotIn("in place of", known_board.question_for(state, row, PORT, kept).why)

    def test_e6_the_envelope_names_the_kept_board_by_its_last_two_bytes(self):
        self.keep(NATIVE_A)
        self.assertEqual(self.envelope(NATIVE_B, mac=MAC_B)[1]["data"]["known_board"], {"state": "other", "mac_ends": "ee:ff"})


class FakeKnownStore:
    """Fake KnownBoardStore: `read` gives the KnownBoard it was given, for every project."""

    def __init__(self, known):
        self.known = known

    def read(self, project):
        return self.known


class TheBoardQuestionTest(unittest.TestCase):
    """P892 (#1266): one class judges the board before a touch that restarts it, by `tell`'s state and the touch."""

    KEPT = known_board.KnownBoard("/p", MAC_A, "aabbccddeeff", "xiao-esp32-c6", "a test", "2026-11-17T18:00:00+01:00")

    def judge(self, touch, row, known, port=None, value=None):
        """(the KnownBoardResult, the questions asked) of KnownBoardService.judge, the replies answering `value` (None: not now)."""
        asked = []

        def replies(question):
            asked.append(question)
            return None if value is None else Reply(question.key, value, "a test")
        row = Port(*row.split(None, 3)) if row else None
        return known_board.KnownBoardService(FakeKnownStore(known), touch).judge(Path("/p"), port, row, replies), asked

    def test_15_judge_by_state_and_touch(self):
        look, deploy, kept = known_board.LOOK, known_board.DEPLOY, self.KEPT
        table = (  # touch, the row listed, the board kept, --port, the reply: the code, and whether it asked
            (look, NATIVE_A, kept, None, None, None, False), (deploy, NATIVE_A, kept, None, None, None, False),
            (look, NATIVE_B, kept, None, None, "needs_reply", True), (deploy, NATIVE_B, kept, None, True, "other_board", False),
            (look, NATIVE_A, None, None, None, "needs_reply", True), (deploy, NATIVE_A, None, None, True, "no_known_board", False),
            (look, NO_SERIAL, kept, "/dev/cu.usbserial-1410", None, None, False),
            (deploy, NO_SERIAL, kept, "/dev/cu.usbserial-1410", None, "needs_reply", True),
            (look, None, kept, "/dev/cu.nowhere", None, None, False), (deploy, None, kept, "/dev/cu.nowhere", True, None, True),
            (look, NO_SERIAL, kept, None, False, "answered_no", True), (deploy, NO_SERIAL, None, None, False, "answered_no", True),
            (deploy, NO_SERIAL, kept, None, "yes", "needs_reply", True), (deploy, NO_SERIAL, kept, None, True, None, True),
        ) + tuple(row for touch in (known_board.GRANT, known_board.REACH, known_board.LIVE) for row in (  # P892 part 2, test 18
            (touch, NATIVE_A, kept, None, None, None, False), (touch, NATIVE_B, kept, None, True, "other_board", False),
            (touch, NATIVE_A, None, None, True, "no_known_board", False),
            (touch, NO_SERIAL, kept, "/dev/cu.usbserial-1410", None, "needs_reply", True),
            (touch, None, kept, "/dev/cu.nowhere", True, None, True), (touch, NO_SERIAL, None, None, False, "answered_no", True)))
        for touch, row, known, port, value, code, asks in table:
            with self.subTest(touch=touch.name, row=row, known=bool(known), port=port, value=value):
                judged, asked = self.judge(touch, row, known, port, value)
                self.assertEqual((judged.code, bool(asked)), (code, asks))
                self.assertTrue(all(question.key.startswith(touch.name + ".") for question in asked), asked)

    def test_15_a_yes_lets_the_read_go_on_with_the_reply_and_the_row(self):
        judged, asked = self.judge(known_board.DEPLOY, NO_SERIAL, self.KEPT, value=True)
        self.assertEqual((judged.code, judged.reply.value, judged.row.device, judged.known), (None, True, "/dev/cu.usbserial-1410", self.KEPT))

    def test_15_a_record_that_cannot_be_read_passes_up(self):
        class Unreadable(FakeKnownStore):
            def read(self, project):
                raise SparkError("cannot be read", code="known_board_unreadable", fix="repair it")
        with self.assertRaises(SparkError):
            known_board.KnownBoardService(Unreadable(None), known_board.DEPLOY).judge(Path("/p"), None, Port(*NATIVE_A.split(None, 3)), None)

    def test_15_the_deploy_stop_names_the_port_and_a_null_product_with_no_row(self):
        judged, _ = self.judge(known_board.DEPLOY, None, self.KEPT, "/dev/cu.nowhere")
        data = judged.data("/dev/cu.nowhere")
        self.assertEqual((data["port"], data["product"], data["known_board"]), ("/dev/cu.nowhere", None, {"state": "cannot_tell", "mac_ends": "ee:ff"}))
        self.assertEqual([found.code for found in judged.findings(known_board.DEPLOY)], ["needs_reply"])

    def test_12_the_deploys_sentences_say_nothing_of_the_looks(self):
        deploy = known_board.DEPLOY
        said = [deploy.question, deploy.no_fix, deploy.other_fix, deploy.answer_fix]
        for row in (NO_SERIAL, FIRMWARE_SERIAL, None):
            question = known_board.question_for("cannot_tell", Port(*row.split(None, 3)) if row else None, PORT, self.KEPT, deploy)
            said += [question.text, question.why]
        for each in said:
            for words in ("Nothing is erased or written", "run look.py again when you want to read it", "say yes to read this board",
                          "except for a port the list does not hold"):
                with self.subTest(sentence=each, words=words):
                    self.assertNotIn(words, each)

    def test_12_the_deploys_question_on_a_port_the_list_does_not_hold_names_the_port_alone(self):
        question = known_board.question_for("cannot_tell", None, "/dev/cu.nowhere", self.KEPT, known_board.DEPLOY)
        self.assertTrue(question.text.startswith("Read the board on /dev/cu.nowhere? "), question.text)
        self.assertNotIn("reports no USB serial", question.why)
        self.assertNotIn("in place of", question.why)
        self.assertTrue(question.key.startswith("deploy.read_board."))


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
