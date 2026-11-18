"""P892 (#1266), part 2: grant.py, reach.py and live.py ask the board question before they touch the board on USB, as the
deploy does, and a macOS /dev/tty. port is judged as its /dev/cu. port. "No touch" means no esptool `flash-id` and no
mpremote `exec` ran, and the console probe (the board doctor's read) was never called."""

import contextlib
import datetime
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

import grant  # noqa: E402
import live  # noqa: E402
import reach  # noqa: E402
from spark.bench import board_doctor  # noqa: E402
from spark.bench import board_grant  # noqa: E402
from spark.bench import board_look  # noqa: E402
from spark.bench import board_start  # noqa: E402
from spark.bench import deploy_gate  # noqa: E402
from spark.bench import known_board  # noqa: E402
from spark.bench.board_console import Cure  # noqa: E402
from spark.bench.board_look import Port  # noqa: E402
from spark.bench.check_grant import CheckGrant  # noqa: E402
from spark.bench.issue_grant import IssueGrant  # noqa: E402
from spark.bench.reach_board import ReachBoard  # noqa: E402
from spark.bench.run_live_code import RunLiveCode  # noqa: E402
from spark.records import board_records  # noqa: E402
from fakes import FakeClock, FakeConsent, FakeConsoleProbe, FakeOutsideWorld, FakeProbePlatform  # noqa: E402
from test_board_look import C6_MAC, C6_PORT, data, done, found  # noqa: E402
from test_deploy_known_board import RecordingReplies  # noqa: E402
from test_grant import NoTerminal  # noqa: E402

GRANT, REACH, LIVE = "grant.py", "reach.py", "live.py"
#: The grant's two scopes, as a person types them after --scope.
LIVE_SCOPE, DEPLOY_SCOPE = "live", "deploy"
SCRIPTS = (GRANT, REACH, LIVE)
NOW = datetime.datetime(2026, 10, 17, 9, 0, tzinfo=datetime.timezone.utc)
RESTART = Cure("rst:0x15 (USB_UART_HPSYS),boot:0x1e\n", None, True, True)
#: mpremote devs rows: the kept C6, another native USB board on its port (an invented MAC), a native USB board whose
#: firmware set its serial, and a CH340 with no serial.
KEPT_ROW = data("mpremote-devs-one.txt")
OTHER_MAC = "aa:bb:cc:dd:12:34"
OTHER_ROW = "%s %s 303a:1001 Espressif USB JTAG/serial debug unit\n" % (C6_PORT, OTHER_MAC)
FIRMWARE_SERIAL = "SPARK-S3LCD"
FIRMWARE_ROW = "%s %s 303a:4001 Espressif Device\n" % (C6_PORT, FIRMWARE_SERIAL)
NO_SERIAL_PORT = "/dev/cu.usbserial-1410"
NO_SERIAL_ROW = "%s None 1a86:7523 USB Serial\n" % NO_SERIAL_PORT
#: The words of the other touches: a script's name, and the erase of the deploy.
SCRIPT_NAMES = ("look.py", "deploy.py", GRANT, REACH, LIVE)


class BoardQuestionCase(unittest.TestCase):
    """A store of its own that keeps the C6 as the project's board and holds a live grant for it, a project whose board is
    the XIAO ESP32-C6, fake mpremote and esptool, and the agent's replies file once a test writes it."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.project = Path(tempfile.mkdtemp())
        (self.project / "boards").mkdir()
        (self.project / "boards" / "active.json").write_text(json.dumps({"schema": 1, "board": "xiao-esp32-c6"}))
        self.devs, self.esptool, self.ran = KEPT_ROW, data("c6-flash-id.txt"), []
        self.yes_file = Path(tempfile.mkdtemp()) / "replies.json"  # the agent's own file, outside the project
        self.probe, self.consent = FakeConsoleProbe(cured=RESTART), FakeConsent(True)
        self.make_consent = lambda line: self.consent
        self.replies = RecordingReplies()
        self.keep(C6_MAC, known_board.comparable_key(C6_MAC))
        self.give_live_grant(C6_MAC)

    def keep(self, mac, usb_key):
        """The store keeps the board `mac` for this project, as a yes on an earlier look keeps it."""
        known_board.KnownBoardStore().write(known_board.KnownBoard(str(self.project.resolve()), mac, usb_key, "xiao-esp32-c6",
                                                                   "a test", "2026-11-17T18:00:00+01:00"))

    def forget(self):
        known_board.KnownBoardStore.find_path(self.project).unlink()

    def give_live_grant(self, serial):
        """A live grant for the board whose USB serial is `serial`, valid at NOW for 30 minutes."""
        board_grant.GrantStore().save(board_grant.Grant(serial, board_look.board_token(board_grant.mac_key(serial)), "a test",
                                                        NOW.isoformat(), (NOW + datetime.timedelta(minutes=30)).isoformat()))

    def cannot_tell(self, script):
        """The board on USB is one that spark cannot tell: a CH340 with no serial for the grant (a deploy grant), and a serial
        that its firmware set for reach and live, with a live grant for it and the kept board's serial not trusted."""
        if script == GRANT:
            self.devs = NO_SERIAL_ROW
        else:
            self.keep(C6_MAC, None)
            self.devs = FIRMWARE_ROW
            self.give_live_grant(FIRMWARE_SERIAL)

    def run_tool(self, command, **kw):
        self.ran.append(command)
        if "devs" in command:
            return done("", 1) if self.devs is None else done(self.devs)
        if "flash-id" in command:
            return done(self.esptool)
        return done("reached\n" if "exec" in command else "")  # the exec, then live's reset

    def outside(self):
        self.replies = RecordingReplies(self.yes_file if self.yes_file.exists() else None)
        return FakeOutsideWorld(run=self.run_tool, find_tool=found, clock=FakeClock(NOW), make_consent=self.make_consent,
                                replies=self.replies)

    def operation(self, script):
        platform_for = lambda project, find_tool: FakeProbePlatform(project, self.probe, find_tool)  # noqa: E731
        return {GRANT: IssueGrant, REACH: ReachBoard, LIVE: RunLiveCode}[script](platform_for=platform_for)

    def result(self, script, port=None, scope=DEPLOY_SCOPE):
        """The OperationResult of the script's Operation, with the agent's file once it exists. `scope` is the grant's."""
        values = {GRANT: dict(minutes=30, scope=scope), REACH: dict(cure_first=False), LIVE: dict(code="print(1)")}[script]
        replies = self.yes_file if self.yes_file.exists() else None
        return self.operation(script).run(project=self.project, port=port, replies=replies, outside=self.outside(), **values)

    def main(self, script, *argv):
        """(exit code, stdout, stderr) of the script's main, with the agent's file once it exists."""
        module, first = {GRANT: (grant, ["--minutes", "30"]), REACH: (reach, []), LIVE: (live, ["--code", "print(1)"])}[script]
        given = ["--replies", str(self.yes_file)] if self.yes_file.exists() else []
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = module.main(first + ["--project", str(self.project)] + list(argv) + given, outside=self.outside(),
                               operation=self.operation(script))
        return code, out.getvalue(), err.getvalue()

    def answer(self, value, key=None):
        """The agent's file with `value` for the key of the last question asked (or `key`), read by the next run."""
        self.yes_file.write_text(json.dumps({"replies": {key or self.replies.asked[-1].key: value}}))

    def touched(self):
        """Each esptool read and mpremote exec that ran, and each call of the console probe."""
        return [command for command in self.ran if "flash-id" in command or "exec" in command] + self.probe.asked

    @staticmethod
    def codes(result):
        return [found.code for found in result.findings]


class TheThreeAskTest(BoardQuestionCase):
    """The plan's tests 1 to 8 and 13, for each of the three scripts."""

    def test_1_the_kept_board_is_touched_with_no_question_with_and_without_a_replies_file(self):
        for script in SCRIPTS:
            for given in (False, True):
                with self.subTest(script=script, replies_file=given):
                    if given:
                        self.yes_file.write_text(json.dumps({"replies": {"other.key": True}}))
                    self.ran = []
                    result = self.result(script, scope=LIVE_SCOPE)
                    self.assertEqual((result.status(), self.codes(result), self.replies.asked), ("ok", [], []))
                    self.assertTrue(self.touched())

    def test_2_another_board_stops_with_no_touch_and_names_the_look(self):
        self.devs = OTHER_ROW
        self.give_live_grant(OTHER_MAC)
        for script in SCRIPTS:
            with self.subTest(script=script):
                result = self.result(script, scope=LIVE_SCOPE)
                self.assertEqual((self.codes(result), result.status(), self.touched(), self.replies.asked),
                                 (["other_board"], "could-not-run", [], []))
                self.assertIn("look.py", result.findings[0].fix)

    def test_3_no_kept_board_and_a_serial_stops_with_no_touch(self):
        self.forget()
        for script in SCRIPTS:
            with self.subTest(script=script):
                result = self.result(script, scope=LIVE_SCOPE)
                self.assertEqual((self.codes(result), self.touched(), self.replies.asked), (["no_known_board"], [], []))
                self.assertIn("look.py", result.findings[0].fix)

    def test_4_a_board_spark_cannot_tell_with_no_reply_is_asked_under_the_touchs_key(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                self.cannot_tell(script)
                result = self.result(script)
                self.assertEqual((self.codes(result), result.status(), self.touched()), (["needs_reply"], "could-not-run", []))
                name, word = script[:-len(".py")], "read_board" if script == GRANT else "run_on_board"
                self.assertTrue(re.fullmatch(r"%s\.%s\.[0-9a-f]{4}" % (name, word), self.replies.asked[0].key), self.replies.asked[0].key)

    def test_5_a_yes_in_the_file_lets_the_touch_run_and_is_used(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                self.cannot_tell(script)
                self.result(script)
                self.answer(True)
                result = self.result(script)
                self.assertEqual((result.status(), self.codes(result)), ("ok", []))
                self.assertTrue(self.touched())
                self.assertEqual(list(json.loads(self.yes_file.read_text())["replies"].values()), [None])
                self.yes_file.unlink()

    def test_6_a_no_touches_nothing_and_a_value_that_is_no_boolean_leaves_it_open(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                self.cannot_tell(script)
                self.result(script)
                key = self.replies.asked[-1].key
                self.answer(False)
                result = self.result(script)
                self.assertEqual((self.codes(result), self.touched()), (["answered_no"], []))
                self.assertIn(script, result.findings[0].fix)
                self.answer("yes", key)
                self.assertEqual(self.codes(self.result(script)), ["needs_reply"])
                self.yes_file.unlink()

    def test_7_a_yes_under_another_touchs_key_does_not_answer(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                self.cannot_tell(script)
                self.result(script)
                rest = self.replies.asked[-1].key.split(".", 1)[1]
                self.yes_file.write_text(json.dumps({"replies": {"look." + rest: True, "deploy." + rest: True}}))
                result = self.result(script)
                self.assertEqual((self.codes(result), self.touched()), (["needs_reply"], []))
                self.yes_file.unlink()

    def test_8_a_named_port_is_asked_and_a_port_the_list_does_not_hold_is_asked_by_reach_alone(self):
        for script, row, port in ((GRANT, NO_SERIAL_ROW, NO_SERIAL_PORT), (REACH, NO_SERIAL_ROW, NO_SERIAL_PORT),
                                  (LIVE, FIRMWARE_ROW, C6_PORT)):  # a board with no serial has no live grant: live asks first for this one
            with self.subTest(script=script, port=port):
                self.cannot_tell(script)
                self.devs = row
                self.assertEqual((self.codes(self.result(script, port)), self.touched()), (["needs_reply"], []))
        self.devs = KEPT_ROW
        for script, code in ((GRANT, "port_not_listed"), (REACH, "needs_reply"), (LIVE, "port_not_listed")):
            with self.subTest(script=script, port="/dev/cu.nowhere"):
                result = self.result(script, "/dev/cu.nowhere")
                self.assertEqual((self.codes(result), self.touched()), ([code], []))
                self.assertEqual(len(self.replies.asked), 1 if script == REACH else 0)
        self.devs = None  # the list fails
        for script in SCRIPTS:
            with self.subTest(script=script, listed=False):
                result = self.result(script)
                self.assertEqual((self.codes(result), self.touched(), self.replies.asked), (["list_failed"], [], []))

    def test_8_reach_refuses_cure_first_with_no_probe_before_the_question(self):
        self.cannot_tell(REACH)
        self.probe = None  # mpremote is no Python package: there is no console probe
        result = self.operation(REACH).run(project=self.project, port=None, cure_first=True, replies=None, outside=self.outside())
        self.assertEqual((self.codes(result), self.replies.asked, [command for command in self.ran if "exec" in command]), (["no_probe"], [], []))

    def test_17_a_named_tty_port_is_the_kept_board_on_its_cu_port_and_the_touch_uses_the_named_port(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                self.ran = []
                result = self.result(script, "/dev/tty.usbmodem101", scope=LIVE_SCOPE)
                self.assertEqual((result.status(), self.replies.asked), ("ok", []))
                self.assertTrue(all("/dev/tty.usbmodem101" in command for command in self.touched()), self.touched())

    def test_13_no_stop_of_the_board_question_calls_the_doctors_console_probe(self):
        for script in SCRIPTS:
            for state in ("other", "none", "cannot_tell", "no"):
                with self.subTest(script=script, state=state):
                    self.setUp()
                    if state == "other":
                        self.devs = OTHER_ROW
                        self.give_live_grant(OTHER_MAC)
                    elif state == "none":
                        self.forget()
                    else:
                        self.cannot_tell(script)
                    if state == "no":
                        self.yes_file.write_text(json.dumps({"replies": {}}))
                        self.result(script)
                        self.answer(False)
                    result = self.result(script, scope=LIVE_SCOPE if state in ("other", "none") else DEPLOY_SCOPE)
                    self.assertEqual(result.status(), "could-not-run")
                    self.assertEqual(self.probe.asked, [])


class TheLiveAndTheGrantTest(BoardQuestionCase):
    """The plan's tests 9 to 12: live's order, the grant's check after its read, its early refusal and --check."""

    def test_9_live_refuses_a_board_with_no_grant_before_any_question_and_stops_another_board_with_one(self):
        self.devs = OTHER_ROW
        result = self.result(LIVE)
        self.assertEqual((self.codes(result), result.data["answer"], self.replies.asked, self.touched()), (["refused_no_grant"], "refused_no_grant", [], []))
        self.give_live_grant(OTHER_MAC)
        self.assertEqual(self.codes(self.result(LIVE)), ["other_board"])

    def test_10_another_mac_after_the_grants_read_stops_before_its_own_yes(self):
        (self.home / "grants" / "8c-bf-ea-xx-xx-xx.json").unlink()
        self.esptool = data("c6-flash-id.txt").replace(C6_MAC, OTHER_MAC)
        result = self.result(GRANT, scope=LIVE_SCOPE)  # on the kept board's serial
        self.assertEqual((self.codes(result), self.consent.asked, list((self.home / "grants").iterdir())), (["other_board"], [], []))
        self.assertIn("did restart", result.findings[0].sentence)
        self.devs = NO_SERIAL_ROW
        self.result(GRANT)
        self.answer(True)
        result = self.result(GRANT)  # after a yes
        self.assertEqual((self.codes(result), self.consent.asked, list((self.home / "grants").iterdir())), (["other_board"], [], []))
        self.esptool = data("c6-flash-id.txt")
        self.answer(True)
        result = self.result(GRANT)
        self.assertEqual((self.codes(result), len(self.consent.asked)), ([], 1), "a yes in the file is no yes to the grant")
        self.make_consent = lambda line: deploy_gate.TerminalConsentStrategy(line, stdin=NoTerminal(), stdout=io.StringIO())
        self.answer(True)
        self.ran = []
        result = self.result(GRANT)
        self.assertEqual((self.codes(result), self.replies.asked, self.touched()), (["no_terminal"], [], []))

    def test_11_a_live_grant_on_a_serial_that_cannot_be_the_mac_is_refused_from_the_list_alone(self):
        for row in (NO_SERIAL_ROW, FIRMWARE_ROW):
            with self.subTest(row=row):
                self.keep(C6_MAC, None)
                self.devs, self.ran = row, []
                result = self.result(GRANT, scope=LIVE_SCOPE)
                self.assertEqual((self.codes(result), result.status(), self.touched(), self.replies.asked), (["serial_not_mac"], "problems", [], []))
                result = self.result(GRANT, scope=DEPLOY_SCOPE)
                self.assertEqual((self.codes(result), self.touched(), len(self.replies.asked)), (["needs_reply"], [], 1))

    def test_12_the_check_asks_nothing_and_opens_no_port(self):
        for state in ("same", "other", "cannot_tell", "none"):
            with self.subTest(state=state):
                self.ran = []
                self.devs = {"same": KEPT_ROW, "other": OTHER_ROW, "cannot_tell": FIRMWARE_ROW, "none": KEPT_ROW}[state]
                if state == "none":
                    self.forget()
                CheckGrant().run(check=True, project=self.project, port=None, outside=self.outside())
                self.assertEqual((self.replies.asked, [command[-1] for command in self.ran]), ([], ["devs"]))


class TheStopsTest(BoardQuestionCase):
    """The plan's tests 14 to 16 and 19: a kept record that cannot be read, the words of each touch, the --json lines, and
    the deploy's finding after a read of another board."""

    def test_14_a_kept_record_that_cannot_be_read_is_one_finding_and_its_line(self):
        known_board.KnownBoardStore.find_path(self.project).write_text("{not json")
        for script in SCRIPTS:
            with self.subTest(script=script):
                result = self.result(script, scope=LIVE_SCOPE)
                self.assertEqual((self.codes(result), self.touched()), (["known_board_unreadable"], []))
                code, _, err = self.main(script)
                self.assertEqual(code, 2)
                self.assertIn("spark's record of this project's board cannot be read", err)
                self.assertNotIn("Traceback", err)

    def test_15_each_touchs_question_no_and_reasons_hold_no_words_of_another_touch(self):
        kept = known_board.KnownBoard("/p", C6_MAC, None, "xiao-esp32-c6", "a test", "2026-11-17T18:00:00+01:00")
        rows = [Port(*row.split(None, 3)) for row in (NO_SERIAL_ROW.strip(), FIRMWARE_ROW.strip(), OTHER_ROW.strip())] + [None]
        for touch, script in ((known_board.GRANT, GRANT), (known_board.REACH, REACH), (known_board.LIVE, LIVE)):
            said = [touch.no_message]
            for row in rows:
                question = known_board.question_for("cannot_tell", row, C6_PORT, kept, touch)
                said += [question.text, question.why]
            for each in said:
                with self.subTest(touch=touch.name, sentence=each):
                    self.assertFalse([name for name in SCRIPT_NAMES if name != script and name in each])
                    self.assertNotIn("erase", each)
                    if touch is not known_board.GRANT:
                        self.assertIsNone(re.search(r"\bread", each))

    def test_16_reach_json_prints_its_line_for_an_open_question_only_and_live_names_the_question_in_its_stop_line(self):
        self.cannot_tell(REACH)
        code, said, _ = self.main(REACH, "--json")
        line = json.loads(said)
        self.assertEqual((code, sorted(line), line["reached"], line["port"]), (2, ["known_board", "open", "port", "product", "reached"], False, C6_PORT))
        self.answer(False)
        self.assertEqual(self.main(REACH, "--json")[1], "")
        self.yes_file.unlink()
        self.keep(C6_MAC, known_board.comparable_key(C6_MAC))
        self.devs = OTHER_ROW
        self.assertEqual(self.main(REACH, "--json")[1], "")
        self.forget()
        self.devs = KEPT_ROW
        self.assertEqual(self.main(REACH, "--json")[1], "")
        self.assertEqual(self.main(REACH, "--json", "--port", "/dev/cu.nowhere")[1].count('"open"'), 1)
        self.keep(C6_MAC, known_board.comparable_key(C6_MAC))
        self.devs = OTHER_ROW
        self.give_live_grant(OTHER_MAC)
        line = json.loads(self.main(LIVE, "--json")[1])
        self.assertEqual((line["answer"], line["open"], line["product"], line["known_board"]),
                         ("could-not-run", [], "Espressif USB JTAG/serial debug unit", {"state": "other", "mac_ends": "xx:xx"}))
        self.devs = data("mpremote-devs-two.txt")
        line = json.loads(self.main(LIVE, "--json")[1])
        self.assertEqual([key for key in ("open", "product", "known_board") if key in line], [])

    def test_16_the_paste_line_on_stderr_shows_the_key_whole(self):
        self.cannot_tell(REACH)
        _, _, err = self.main(REACH)
        self.assertIn('{"replies": {"%s": true}}' % self.replies.asked[-1].key, err)

    def test_19_the_deploys_finding_after_a_read_of_another_board_is_as_before(self):
        known = known_board.KnownBoard("/p", "aa:bb:cc:dd:ee:ff", None, "xiao-esp32-c6", "a test", "2026-11-17T18:00:00+01:00")
        found = known_board.other_after(known, C6_PORT, OTHER_MAC, known_board.DEPLOY.after_fix)
        self.assertEqual(tuple(found), ("could-not-run", "board", "other_board",
                                        "The board on /dev/cu.usbmodem101 (MAC ends 12:34) is not the kept board (its MAC ends ee:ff, "
                                        "kept since 2026-11-17). It did restart: a read restarts the board.",
                                        "plug in this project's board, then run look.py again"))
        self.assertIsNone(known_board.other_after(known, C6_PORT, "AA:BB:CC:DD:EE:FF", known_board.DEPLOY.after_fix))
        self.assertIsNone(known_board.other_after(None, C6_PORT, OTHER_MAC, known_board.DEPLOY.after_fix))


class TheTtyAliasTest(unittest.TestCase):
    """The plan's test 17: a /dev/tty. port is its /dev/cu. port in the list, the doctor's port check, the console check
    after a deploy and the key of a board with no serial."""

    def finder(self, devs=KEPT_ROW):
        return board_look.PortFinder(found("board-shell"), run=lambda command, **kw: done(devs) if devs is not None else done("", 1))

    def test_17_the_tty_name_of_a_port_is_its_cu_name(self):
        tty = "/dev/tty.usbmodem101"
        self.assertEqual(self.finder().require_one_board("x", tty).device, C6_PORT)
        self.assertEqual(self.finder().find_listed("x", tty).device, C6_PORT)
        self.assertIsNone(self.finder().find_listed("x", "/dev/cu.nowhere"))
        with self.assertRaises(board_look.LookStopError):
            self.finder(None).find_listed("x", tty)
        self.assertTrue(board_doctor.PortListedDoctorProbe(self.finder()).run(tty, None).passed)
        self.assertTrue(board_start.console_may_be_read(Port(*KEPT_ROW.split(None, 3)), tty))
        starts = board_start.BoardStartService(self.finder(NO_SERIAL_ROW), C6_MAC, FakeClock(), board_records.ButtonPlaces.EMPTY)
        self.assertEqual(starts.find_port("/dev/tty.usbserial-1410").device, NO_SERIAL_PORT)  # a bridge's port, found by its name
        row = Port(*NO_SERIAL_ROW.split(None, 3))
        keys = {known_board.question_for("cannot_tell", row, port, None, known_board.REACH).key
                for port in (NO_SERIAL_PORT, "/dev/tty.usbserial-1410")}
        self.assertEqual(len(keys), 1, keys)


if __name__ == "__main__":
    unittest.main()
