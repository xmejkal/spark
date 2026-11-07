"""P253 (#265), P242 (#249), P657: grant.py gives and checks a grant through the core. The yes comes through the outside's
`make_consent`, the clock is the outside's, and the board answers from P228's fixtures."""

import contextlib
import datetime
import hashlib
import io
import json
import os
import shlex
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_console  # noqa: E402
import board_doctor  # noqa: E402
import board_grant  # noqa: E402
import boards  # noqa: E402
import deploy_gate  # noqa: E402
import grant  # noqa: E402
import store  # noqa: E402
import tools  # noqa: E402
from fakes import FakeClock, FakeConsent, FakeOutsideWorld, FakeProbePlatform, line_made_at_import, pin_time_zone  # noqa: E402
from spark.bench.check_grant import CheckGrant  # noqa: E402
from spark.bench.deploy_image import DeployImage  # noqa: E402
from spark.bench.issue_grant import IssueGrant  # noqa: E402
from spark.core.cli import run_operation  # noqa: E402
from spark.core.events import BEGIN, LINE, TerminalReporter  # noqa: E402
from spark.core.outside import build_outside_world  # noqa: E402
from test_board_look import data, done  # noqa: E402
from test_deploy import found  # noqa: E402

UTC = datetime.timezone.utc
#: The moment the fake clock starts, and the MAC of P228's bench C6 as the fixtures write it.
START = datetime.datetime(2026, 10, 17, 9, 0, tzinfo=UTC)
MAC = "8c:bf:ea:xx:xx:xx"
OTHER = "/dev/cu.usbmodem202 aa:bb:cc:dd:ee:ff 303a:1001 Espressif USB JTAG/serial debug unit\n"
GRANT_SCRIPT = str(ROOT / "scripts" / "grant.py")


class NoTerminal(io.StringIO):
    """A stdin that is a pipe, not a terminal: the terminal consent then gives the line to run in one."""

    def isatty(self):
        return False


class GrantCase(unittest.TestCase):
    """A scratch store, a fake clock, and fake mpremote and esptool that answer from P228's fixtures."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        pin_time_zone(self)
        self.now, self.ran = START, []
        self.clock = FakeClock()
        self.clock.now = lambda: self.now  # a test moves the time by setting self.now
        self.devs, self.esptool = data("mpremote-devs-one.txt"), data("c6-flash-id.txt")

    def run_tool(self, argv, **kw):
        self.ran.append(argv)
        return done(self.devs if "devs" in argv else self.esptool)

    def grant(self, *argv, consent=None, platform=None, find_tool=found):
        """(exit code, stdout, stderr) of grant.py with the fakes. `consent` is the yes (None: a real terminal's), `platform` the
        FirmwarePlatform of the run (None: MicroPythonPlatform over `find_tool`)."""
        out, err = io.StringIO(), io.StringIO()
        make_consent = (lambda line: consent) if consent else (lambda line: deploy_gate.TerminalConsentStrategy(line, stdin=NoTerminal(), stdout=out))
        outside = FakeOutsideWorld(run=self.run_tool, find_tool=find_tool, reporter=TerminalReporter(out), clock=self.clock,
                                   make_consent=make_consent)
        operation = grant.operation_for(argv)(platform_for=(lambda project, find: platform) if platform else None)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = grant.main(list(argv), outside=outside, operation=operation)
        return code, out.getvalue(), err.getvalue()

    def project_with_buttons(self, buttons):
        """A project whose board record is the XIAO C6's with `buttons` as its physical.buttons: the restart notice names them."""
        project = Path(tempfile.mkdtemp())
        (project / "boards").mkdir()
        (project / "requirements.json").write_text(json.dumps({"board": "xiao-esp32-c6", "parts": []}))
        record = dict(boards.load(Path("."), "xiao-esp32-c6"), physical={"buttons": buttons})
        (project / "boards" / "xiao-esp32-c6.json").write_text(json.dumps(record))
        return str(project)

    def kept(self):
        return json.loads((self.home / "grants" / "8c-bf-ea-xx-xx-xx.json").read_text())

    def check(self, *argv):
        code, out, _ = self.grant("--check", "--json", *argv)
        return code, json.loads(out)


class DoctorTest(GrantCase):
    """P282: a read that esptool could not make ends with the board doctor's facts and one next step."""

    def run_tool(self, argv, **kw):
        self.ran.append(argv)
        if "devs" in argv:
            return done(self.devs)
        if "flash-id" in argv:
            return subprocess.CompletedProcess(argv, 2, "Connecting......\n", "ERROR: A fatal error occurred: Failed "
                                               "to connect to Espressif device: No serial data received.\nFor "
                                               "troubleshooting steps visit: https://docs.espressif.com\n")
        return done("")  # the doctor's console read: silent

    def test_the_doctor_reads_the_console_with_the_probe_of_the_platform_grant_was_given(self):
        def locked(command, **kw):  # the console script exits as it does when another program holds the port's lock
            raise subprocess.CalledProcessError(3, command, "", "serial.SerialException: Could not exclusively lock port")
        probe = board_console.ConsoleProbe(["/opt/python3"], "/dev/cu.usbmodem101", locked)
        platform = FakeProbePlatform(Path("."), probe, lambda role: found(role))
        code, _, err = self.grant("--minutes", "30", consent=FakeConsent(True), platform=platform)
        self.assertEqual(code, 2)
        self.assertEqual(err.strip().splitlines()[-1].strip(), "next    " + board_doctor.step_sentence("close_other"))

    def test_a_silent_board_names_esptool_s_words_the_port_and_hold_boot_last(self):
        code, _, err = self.grant("--minutes", "30", consent=FakeConsent(True))
        self.assertEqual(code, 2)
        lines = err.strip().splitlines()
        self.assertEqual(lines[0], "grant.py: could not read the board on /dev/cu.usbmodem101")
        self.assertIn("  said    ERROR: A fatal error occurred: Failed to connect to Espressif device: No serial data "
                      "received.", lines)
        self.assertIn("  check   console: the console was silent for 2 s", lines)
        self.assertTrue(lines[-1].startswith("  next    hold the board's BOOT button"))
        self.assertFalse((self.home / "grants").exists())


class IssueTest(GrantCase):
    def test_the_yes_keeps_a_grant_for_this_board_until_the_limit(self):
        consent = FakeConsent(True)
        code, out, _ = self.grant("--minutes", "30", consent=consent)
        self.assertEqual(code, 0)
        self.assertEqual(consent.asked, ["let Claude run code on the board 8c:bf:ea:xx:xx:xx (token %s) for 30 minutes "
                                         "from your yes?" % self.kept()["board_token"]])
        kept = self.kept()
        self.assertEqual((kept["mac"], kept["granted_at"], kept["expires_at"]),
                         (MAC, "2026-10-17T11:00:00+02:00", "2026-10-17T11:30:00+02:00"))
        self.assertEqual(len(kept["board_token"]), 4)
        self.assertIn("the board restarts while it is read", out)
        self.assertIn("If it then waits in download mode, press its RESET", out)
        self.assertEqual(stat.S_IMODE((self.home / "grants" / "8c-bf-ea-xx-xx-xx.json").stat().st_mode), 0o600)

    def test_a_store_that_refuses_the_grant_is_a_line_with_the_way_out_not_a_traceback(self):
        # P499 (#684): a SPARK_HOME that names a file; the patched environment is restored with the case
        (self.home / "afile").write_text("")
        os.environ["SPARK_HOME"] = str(self.home / "afile")
        code, _, err = self.grant("--minutes", "30", consent=FakeConsent(True))
        self.assertEqual(code, 2)
        self.assertIn("grant.py: cannot make", err)
        self.assertIn("point SPARK_HOME at a folder you can write", err)
        self.assertNotIn("Traceback", err)

    def test_the_grant_names_who_typed_the_yes_by_the_user_name_it_is_given(self):
        finder = mock.Mock()
        finder.require_one_board.return_value = mock.Mock(device="/dev/cu.usbmodem101", serial=MAC)
        reader = mock.Mock()
        reader.read.return_value = mock.Mock(mac=MAC)
        service = board_grant.GrantService(finder, reader, mock.Mock(), now=lambda: START, user_name=lambda: "grace")
        self.assertEqual(service.issue(None, 30, FakeConsent(True)).granted_by, "grace")

    def test_a_relayed_yes_makes_a_live_grant_that_names_the_person_and_the_program(self):
        # P675 (W4-4): the login is never asked for, because getpass can raise
        asked = []
        relayed = deploy_gate.RelayedConsentStrategy("ada", "test-ui", lambda question: asked.append(question) or True)
        with mock.patch("getpass.getuser", side_effect=OSError("no user")):
            code, _, err = self.grant("--minutes", "30", consent=relayed)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.kept()["granted_by"], "relayed by ada through test-ui")
        self.assertIn("8c:bf:ea:xx:xx:xx (token %s) for 30 minutes" % self.kept()["board_token"], asked[0])
        code, checked = self.check()
        self.assertEqual((code, checked["granted"], checked["grant"]["granted_by"]), (0, True, "relayed by ada through test-ui"))

    def test_a_relayed_yes_makes_no_deploy_grant_and_never_touches_the_board(self):
        relayed = deploy_gate.RelayedConsentStrategy("ada", "test-ui", lambda question: True)
        code, _, err = self.grant("--minutes", "30", "--scope", "deploy", consent=relayed)
        self.assertEqual((code, self.ran), (1, []))
        self.assertIn("a yes another program relayed makes a live grant only", err)
        self.assertFalse((self.home / "grants").exists())

    def test_a_relayed_answer_that_is_not_true_is_no(self):
        relayed = deploy_gate.RelayedConsentStrategy("ada", "test-ui", lambda question: "yes")
        code, _, err = self.grant("--minutes", "30", consent=relayed)
        self.assertEqual(code, 1)
        self.assertIn("no grant: the person answered no", err)

    def test_a_relayed_yes_names_its_person_and_program_in_one_printable_line(self):
        for person, program in (("", "ui"), (" \n", "ui"), ("ada", ""), (None, "ui"), ("ada", 7)):
            with self.assertRaises(ValueError, msg=(person, program)):
                deploy_gate.RelayedConsentStrategy(person, program, lambda question: True)
        relayed = deploy_gate.RelayedConsentStrategy("ada\nyes", "ui", lambda question: True)
        self.assertEqual(len(relayed.who.splitlines()), 1)

    def test_no_operation_takes_a_relayed_yes_from_the_command_line(self):
        for operation in (IssueGrant, CheckGrant, DeployImage):
            for argument in operation.arguments:
                self.assertNotIn("relay", " ".join(argument.flags) + argument.dest, operation.name)

    def test_the_token_is_the_first_half_of_the_looks_token(self):
        self.grant("--minutes", "5", consent=FakeConsent(True))
        self.assertEqual(self.kept()["board_token"], hashlib.sha256(MAC.encode()).hexdigest()[:4])

    def test_no_saves_nothing(self):
        code, _, err = self.grant("--minutes", "30", consent=FakeConsent(False))
        self.assertEqual(code, 1)
        self.assertIn("no grant: the person answered no", err)
        self.assertFalse((self.home / "grants").exists())

    def test_no_terminal_names_the_line_to_run_and_saves_nothing(self):
        code, _, err = self.grant("--minutes", "30")
        self.assertEqual(code, 2)
        # P283: the bare `grant.py` was "command not found" in the PO's terminal; the line names the script's whole path.
        self.assertIn("\n  %s\n" % store.prefix_home(shlex.join([GRANT_SCRIPT, "--minutes", "30", "--project", str(Path(".").resolve())])),
                      err + "\n")
        self.assertFalse((self.home / "grants").exists())
        self.assertEqual([argv[-1] for argv in self.ran], ["devs"], "the board restarted for nothing")

    def test_no_terminal_keeps_the_port_the_person_named(self):
        _, _, err = self.grant("--minutes", "30", "--port", "/dev/cu.usbmodem101")
        self.assertIn(" --port /dev/cu.usbmodem101", err)

    def test_minutes_out_of_range_are_refused_before_the_board_is_touched(self):
        for minutes in ("0", "1441", "99999999999"):
            code, out, err = self.grant("--minutes", minutes, consent=FakeConsent(True))
            self.assertEqual(code, 2, minutes)
            self.assertIn("--minutes must be a whole number from 1 to 1440", err)
            self.assertNotIn("restarts", out)
        self.assertEqual(self.ran, [])
        self.assertEqual(self.grant("--minutes", "1440", consent=FakeConsent(True))[0], 0)

    def test_the_limit_counts_from_the_yes(self):
        test = self

        class Slow(FakeConsent):
            def ask(self, question):
                test.now = START + datetime.timedelta(minutes=10)
                return super().ask(question)

        self.grant("--minutes", "30", consent=Slow(True))
        self.assertEqual(self.kept()["expires_at"], "2026-10-17T11:40:00+02:00")

    def test_json_goes_with_check_only(self):
        with self.assertRaises(SystemExit):
            self.grant("--minutes", "30", "--json", consent=FakeConsent(True))

    def test_a_serial_that_is_not_the_mac_gets_no_grant(self):
        self.devs = "/dev/cu.usbserial-1410 None 1a86:7523 USB Serial\n"
        consent = FakeConsent(True)
        code, _, err = self.grant("--minutes", "30", consent=consent)
        self.assertEqual(code, 1)
        self.assertIn("the board's USB serial is not its MAC", err)
        self.assertEqual(consent.asked, [])
        self.assertFalse((self.home / "grants").exists())

    def test_no_mac_read_gets_no_grant(self):
        self.esptool = data("c6-flash-id-no-mac.txt")
        code, _, err = self.grant("--minutes", "30", consent=FakeConsent(True))
        self.assertEqual(code, 2)
        self.assertIn("the board's MAC could not be read", err)
        self.assertFalse((self.home / "grants").exists())

    def test_two_boards_need_the_port_and_the_port_picks_one(self):
        self.devs = data("mpremote-devs-one.txt") + OTHER
        code, _, err = self.grant("--minutes", "30", consent=FakeConsent(True))
        self.assertEqual(code, 2)
        self.assertIn("2 boards on USB", err)
        code, _, _ = self.grant("--minutes", "30", "--port", "/dev/cu.usbmodem101", consent=FakeConsent(True))
        self.assertEqual(code, 0)
        self.assertEqual(self.ran[-1][-3:], ["--port", "/dev/cu.usbmodem101", "flash-id"])

    def test_a_port_mpremote_does_not_list_is_refused(self):
        code, _, err = self.grant("--minutes", "30", "--port", "/dev/cu.nothing", consent=FakeConsent(True))
        self.assertEqual(code, 2)
        self.assertIn("no board on /dev/cu.nothing: mpremote devs does not list it.", err)


class CheckTest(GrantCase):
    def setUp(self):
        super().setUp()
        self.grant("--minutes", "30", consent=FakeConsent(True))
        self.ran = []

    def test_a_call_inside_the_limit_finds_it_without_touching_the_board(self):
        code, said = self.check()
        self.assertEqual((code, said["granted"], said["why"], said["grant"]["mac"]), (0, True, None, MAC))
        self.assertEqual([argv[-1] for argv in self.ran], ["devs"])

    def test_the_grant_ends_at_its_limit(self):
        self.now = START + datetime.timedelta(minutes=30)
        self.assertEqual(self.check(), (1, {"granted": False, "why": "expired", "grant": self.kept()}))

    def test_another_board_has_no_grant(self):
        self.devs = OTHER
        self.assertEqual(self.check(), (1, {"granted": False, "why": "no grant", "grant": None}))

    def test_no_grant_at_all(self):
        (self.home / "grants" / "8c-bf-ea-xx-xx-xx.json").unlink()
        code, out, _ = self.grant("--check")
        self.assertEqual(code, 1)
        self.assertIn("no grant for this board: the person runs %s --minutes N in their own terminal" % line_made_at_import(GRANT_SCRIPT), out)

    def test_an_ended_or_untrusted_grant_names_grant_py_by_its_whole_path(self):
        # P283: the ended and no-zone sentences ask for the grant again, as the no-grant one does.
        self.now = START + datetime.timedelta(hours=1)
        self.assertIn("ended: the person runs %s --minutes N again" % line_made_at_import(GRANT_SCRIPT), self.grant("--check")[1])
        self.now = START
        path = self.home / "grants" / "8c-bf-ea-xx-xx-xx.json"
        path.write_text(json.dumps(dict(self.kept(), expires_at="2099-01-01T00:00:00")))
        self.assertIn("not trusted: the person runs %s --minutes N again" % line_made_at_import(GRANT_SCRIPT), self.grant("--check")[1])

    def test_a_time_with_no_zone_is_not_trusted(self):
        path = self.home / "grants" / "8c-bf-ea-xx-xx-xx.json"
        path.write_text(json.dumps(dict(self.kept(), expires_at="2099-01-01T00:00:00")))
        self.assertEqual(self.check()[1]["why"], "no zone")

    def test_a_file_that_is_no_grant_is_not_trusted(self):
        (self.home / "grants" / "8c-bf-ea-xx-xx-xx.json").write_text("{}")
        self.assertEqual(self.check(), (1, {"granted": False, "why": "not a grant", "grant": None}))

    def test_another_boards_grant_copied_under_this_name_is_not_trusted(self):
        path = self.home / "grants" / "8c-bf-ea-xx-xx-xx.json"
        path.write_text(json.dumps(dict(self.kept(), mac="aa:bb:cc:dd:ee:ff")))
        self.assertEqual(self.check()[1]["why"], "not a grant")
        path.write_text(json.dumps(dict(self.kept(), board_token="0000")))
        self.assertEqual(self.check()[1]["why"], "not a grant")

    def test_a_grant_longer_than_a_day_is_not_trusted(self):
        path = self.home / "grants" / "8c-bf-ea-xx-xx-xx.json"
        path.write_text(json.dumps(dict(self.kept(), expires_at="2099-01-01T00:00:00+00:00")))
        self.assertEqual(self.check()[1]["why"], "not a grant")

    def test_no_board_still_gives_json(self):
        self.devs = ""
        self.assertEqual(self.check(), (2, {"granted": False, "why": "could not run", "grant": None}))

    def test_an_empty_serial_never_reads_a_stray_file(self):
        (self.home / "grants" / "entry.json").write_text(json.dumps(dict(self.kept(), mac="")))
        self.assertIsNone(board_grant.GrantStore().find(" "))

    def test_the_mac_compares_in_any_case(self):
        self.esptool = self.esptool.replace("8c:bf:ea:xx:xx:xx", "8C:BF:EA:XX:XX:XX")
        (self.home / "grants" / "8c-bf-ea-xx-xx-xx.json").unlink()
        self.assertEqual(self.grant("--minutes", "30", consent=FakeConsent(True))[0], 0)
        self.assertEqual(self.kept()["mac"], MAC)
        self.devs = self.devs.replace("8c:bf:ea:xx:xx:xx", "8C:BF:EA:XX:XX:XX")
        self.assertEqual(self.check()[0], 0)

    def test_a_new_grant_replaces_the_old_one(self):
        self.now = START + datetime.timedelta(minutes=40)
        self.assertEqual(self.check()[0], 1)
        self.grant("--minutes", "5", consent=FakeConsent(True))
        self.assertEqual(self.check()[0], 0)
        self.assertEqual(self.kept()["expires_at"], "2026-10-17T11:45:00+02:00")

    def test_the_text_says_until_when(self):
        code, out, _ = self.grant("--check")
        self.assertEqual((code, out.strip()), (0, "granted: board 8c:bf:ea:xx:xx:xx until 2026-10-17T11:30:00+02:00"))

    def test_a_grant_kept_in_utc_says_until_when_in_the_machines_zone(self):
        path = self.home / "grants" / "8c-bf-ea-xx-xx-xx.json"
        path.write_text(json.dumps(dict(self.kept(), expires_at="2026-10-17T09:30:00+00:00")))
        self.assertEqual(self.grant("--check")[1].strip(), "granted: board 8c:bf:ea:xx:xx:xx until 2026-10-17T11:30:00+02:00")


class DeployGrantTest(GrantCase):
    """P242 (#249): `grant.py --scope deploy` keeps a second file per board, with its own question."""

    def kept_deploy(self):
        return json.loads((self.home / "grants" / "8c-bf-ea-xx-xx-xx-deploy.json").read_text())

    def test_a_deploy_grant_keeps_its_own_file_and_leaves_the_live_one(self):
        self.grant("--minutes", "30", consent=FakeConsent(True))
        code, out, _ = self.grant("--scope", "deploy", "--minutes", "60", consent=FakeConsent(True))
        self.assertEqual(code, 0)
        self.assertIn("granted (deploy): board %s" % MAC, out)
        self.assertEqual((self.kept_deploy()["scope"], self.kept_deploy()["expires_at"]),
                         ("deploy", "2026-10-17T12:00:00+02:00"))
        self.assertEqual((self.kept()["scope"], self.kept()["expires_at"]), ("live", "2026-10-17T11:30:00+02:00"))
        self.assertEqual(stat.S_IMODE((self.home / "grants" / "8c-bf-ea-xx-xx-xx-deploy.json").stat().st_mode), 0o600)

    def test_a_new_live_grant_leaves_the_deploy_one(self):
        self.grant("--scope", "deploy", "--minutes", "60", consent=FakeConsent(True))
        self.grant("--minutes", "5", consent=FakeConsent(True))
        self.assertEqual(self.kept_deploy()["expires_at"], "2026-10-17T12:00:00+02:00")

    def test_the_question_says_it_erases_all_the_flash_and_asks_no_yes_for_each_deploy(self):
        consent = FakeConsent(True)
        self.grant("--scope", "deploy", "--minutes", "60", consent=consent)
        self.assertEqual(len(consent.asked), 1)
        for words in ("erase ALL of the flash", "8c:bf:ea:xx:xx:xx", "any passed image of any project",
                      "no yes from you for each deploy", "for 60 minutes"):
            self.assertIn(words, consent.asked[0])

    def test_no_saves_nothing(self):
        code, _, _ = self.grant("--scope", "deploy", "--minutes", "60", consent=FakeConsent(False))
        self.assertEqual(code, 1)
        self.assertFalse((self.home / "grants").exists())

    def test_a_board_whose_serial_is_not_its_mac_gets_a_deploy_grant_but_no_live_one(self):
        self.devs = "/dev/cu.usbserial-1410 None 1a86:7523 USB Serial\n"
        self.assertEqual(self.grant("--minutes", "30", consent=FakeConsent(True))[0], 1)
        self.assertEqual(self.grant("--scope", "deploy", "--minutes", "30", consent=FakeConsent(True))[0], 0)

    def test_minutes_out_of_range_are_refused_for_a_deploy_grant_too(self):
        for minutes in ("0", "1441"):
            self.assertEqual(self.grant("--scope", "deploy", "--minutes", minutes, consent=FakeConsent(True))[0], 2)
        self.assertEqual(self.ran, [])

    def test_scope_goes_with_minutes_only_and_must_be_known(self):
        for argv in (("--check", "--scope", "deploy"), ("--minutes", "5", "--scope", "everything")):
            with self.assertRaises(SystemExit):
                self.grant(*argv)
        with self.assertRaises(SystemExit):
            self.grant("--check", "--scope", "live")

    def test_grant_py_says_what_a_deploy_grant_allows_and_how_to_end_it(self):
        _, out, _ = self.grant("--scope", "deploy", "--minutes", "60", consent=FakeConsent(True))
        path = self.home / "grants" / "8c-bf-ea-xx-xx-xx-deploy.json"
        self.assertIn("Claude can now run deploy.py on this board with no yes from you", out)
        self.assertIn("erases ALL of the board's flash each time", out)
        self.assertIn("rm %s" % shlex.quote(str(path)), out)
        _, out, _ = self.grant("--minutes", "60", consent=FakeConsent(True))
        self.assertNotIn("rm ", out)

    def test_an_unknown_scope_given_to_the_service_is_refused_and_saves_nothing(self):
        service = board_grant.GrantService(mock.Mock(), mock.Mock(), now=FakeClock(START).now)
        with self.assertRaises(board_grant.GrantRefusedError) as refused:
            service.issue(None, 5, FakeConsent(True), scope="bogus")
        self.assertEqual(refused.exception.why, "bad scope")
        self.assertEqual(refused.exception.code, 2)
        self.assertFalse((self.home / "grants").exists())

    def test_no_terminal_gives_the_deploy_line_with_its_scope(self):
        _, _, err = self.grant("--scope", "deploy", "--minutes", "30")
        line = store.prefix_home(shlex.join([GRANT_SCRIPT, "--scope", "deploy", "--minutes", "30", "--project", str(Path(".").resolve())]))
        self.assertIn("\n  %s\n" % line, err + "\n")


class GuardedPrintsTest(GrantCase):
    """P430 (#569): grant.py prints through the text guard, and its --json keeps the raw text."""

    BIDI_MAC = "8c:bf:ea:\u202exx:xx:xx"

    def with_bidi_mac(self):
        self.esptool = data("c6-flash-id.txt").replace("8c:bf:ea:xx:xx:xx", self.BIDI_MAC)
        self.devs = data("mpremote-devs-one.txt").replace("8c:bf:ea:xx:xx:xx", self.BIDI_MAC)

    def test_the_granted_line_shows_a_mac_with_a_bidi_character_guarded_and_the_file_keeps_it_raw(self):
        self.with_bidi_mac()
        code, out, _ = self.grant("--scope", "deploy", "--minutes", "30", consent=FakeConsent(True))
        self.assertEqual(code, 0)
        self.assertIn("  granted (deploy): board 8c:bf:ea:?xx:xx:xx (token ", out)
        self.assertNotIn("\u202e", out)
        self.assertEqual(json.loads(next((self.home / "grants").glob("*-deploy.json")).read_text())["mac"], self.BIDI_MAC)

    def test_the_rm_line_shows_a_store_path_with_a_bidi_character_guarded(self):
        self.home = self.home / "a\u202eb"
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)}):
            _, out, _ = self.grant("--scope", "deploy", "--minutes", "30", consent=FakeConsent(True))
        self.assertIn("rm ", out)
        self.assertIn("a?b", out)
        self.assertNotIn("\u202e", out)

    def test_the_restart_notice_shows_a_button_word_with_a_bidi_character_guarded(self):
        project = self.project_with_buttons({"seen_from": "the shield \u202efacing you", "boot": {"silkscreen": "B\u202e", "place": "top"},
                                             "reset": {"silkscreen": "R", "place": "left"}})
        _, out, _ = self.grant("--minutes", "30", "--project", project, consent=FakeConsent(True))
        self.assertIn("press its RESET (R, left) once. Left and right as seen with the shield ?facing you.", out)
        self.assertNotIn("\u202e", out)

    def test_the_check_shows_a_serial_with_a_bidi_character_guarded_and_json_keeps_it_raw(self):
        self.with_bidi_mac()
        self.grant("--minutes", "30", consent=FakeConsent(True))
        code, out, _ = self.grant("--check")
        self.assertEqual((code, out.startswith("  granted: board 8c:bf:ea:?xx:xx:xx until ")), (0, True))
        self.assertEqual(self.check()[1]["grant"]["mac"], self.BIDI_MAC)

    def test_a_port_with_a_bidi_character_is_told_guarded_and_the_json_is_could_not_run(self):
        code, out, err = self.grant("--check", "--json", "--port", "/dev/x\u202ey")
        self.assertEqual((code, json.loads(out)["why"]), (2, "could not run"))
        self.assertIn("no board on /dev/x?y", err)
        self.assertNotIn("\u202e", err)

    def test_a_newline_in_the_port_cannot_fake_a_line_of_the_stop(self):
        code, _, err = self.grant("--check", "--port", "/dev/x\nGRANTED")
        self.assertEqual(code, 2)
        self.assertIn("no board on /dev/x?GRANTED", err)
        self.assertEqual([line for line in err.splitlines() if line.startswith("GRANTED")], [])

    def test_a_tool_problem_with_a_bidi_character_is_told_guarded(self):
        def missing(name, **where):
            raise tools.ToolProblem("no \u202e mpremote")
        code, _, err = self.grant("--check", find_tool=missing)
        self.assertEqual((code, err), (2, "grant.py: no ? mpremote\n"))

    # --- MVP --- a newline in a value (P430): guard_lines keeps a newline, so each value that can hold one is put on one line first
    FAKE_BUTTONS = {"seen_from": "the shield", "boot": {"silkscreen": "B", "place": "top"},
                    "reset": {"silkscreen": "R\nGRANTED (deploy): fake", "place": "left"}}

    def test_a_newline_in_a_button_word_cannot_fake_a_line_of_the_restart_notice(self):
        _, out, _ = self.grant("--minutes", "30", "--project", self.project_with_buttons(self.FAKE_BUTTONS), consent=FakeConsent(True))
        self.assertIn("press its RESET (R?GRANTED (deploy): fake, left) once", out)
        self.assertEqual([line for line in out.splitlines() if line.startswith("GRANTED")], [])

    def test_a_newline_in_a_button_word_cannot_fake_a_line_of_the_stop(self):
        self.run_tool = lambda argv, **kw: (done(self.devs) if "devs" in argv else subprocess.CompletedProcess(
            argv, 2, "Connecting......\n", "ERROR: A fatal error occurred: Failed to connect: No serial data received.\n"))
        code, _, err = self.grant("--minutes", "30", "--project", self.project_with_buttons(self.FAKE_BUTTONS), consent=FakeConsent(True))
        self.assertEqual(code, 2)
        self.assertIn("RESET (R?GRANTED (deploy): fake, left)", err)
        self.assertEqual([line for line in err.splitlines() if line.startswith("GRANTED")], [])

    def test_a_newline_in_the_project_path_cannot_fake_a_line_of_a_tool_problem(self):
        project = Path(tempfile.mkdtemp()) / "a\nGRANTED: board ok"
        (project / ".spark").mkdir(parents=True)
        (project / ".spark" / "tools.json").write_text("not json")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = grant.main(["--check", "--project", str(project)])
        self.assertEqual(code, 2)
        self.assertEqual(len(err.getvalue().splitlines()), 1, err.getvalue())
        self.assertIn("a?GRANTED: board ok", err.getvalue())

    def test_a_newline_in_the_store_path_cannot_fake_a_line_of_the_rm_line(self):
        self.home = self.home / "a\nGRANTED: board ok"
        with mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)}):
            _, out, _ = self.grant("--scope", "deploy", "--minutes", "30", consent=FakeConsent(True))
        self.assertIn("rm ", out)
        self.assertIn("a?GRANTED: board ok", out)
        self.assertEqual([line for line in out.splitlines() if line.startswith("GRANTED")], [])

    def test_the_closed_gate_s_rerun_line_shows_the_project_path_and_the_port_guarded(self):
        self.devs = self.devs.replace("/dev/cu.usbmodem101", "/dev/cu.usb\u202emodem101")
        code, _, err = self.grant("--minutes", "30", "--project", "/tmp/a\u202eb\x1b[31m\nGRANTED", "--port", "/dev/cu.usb\u202emodem101")
        self.assertEqual(code, 2)
        self.assertIn("/a?b?[31m?GRANTED'", err)
        self.assertIn("--port '/dev/cu.usb?modem101'", err)
        self.assertEqual([line for line in err.splitlines() if line.startswith("GRANTED")], [])
        self.assertNotIn("\u202e", err)


class GrantModesTest(GrantCase):
    """P657: two Operations behind one script. `operation_for` picks by --check, and each mode has its own parser and help."""

    def issued(self, consent=None, minutes=30, find_tool=found):
        """The OperationResult of IssueGrant run on the fakes (no CLI), the yes `consent` (default: yes)."""
        outside = FakeOutsideWorld(run=self.run_tool, find_tool=find_tool, clock=self.clock,
                                   make_consent=lambda line: consent or FakeConsent(True))
        return IssueGrant().run(minutes=minutes, scope="live", project=Path("."), port=None, outside=outside)

    def checked(self):
        outside = FakeOutsideWorld(run=self.run_tool, find_tool=found, clock=self.clock)
        return CheckGrant().run(check=True, project=Path("."), port=None, outside=outside)

    def refused(self, usage_argv):
        out, err = io.StringIO(), io.StringIO()
        with self.assertRaises(SystemExit) as raised, contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            grant.main(usage_argv, outside=FakeOutsideWorld())
        self.assertEqual((raised.exception.code, out.getvalue()), (2, ""))
        return err.getvalue()

    def test_the_check_flag_or_a_prefix_of_it_picks_the_check(self):
        for argv in (["--check"], ["--check", "--json"], ["--che"], ["--ch", "--json"], ["--c"]):
            self.assertIs(grant.operation_for(argv), CheckGrant, argv)
        for argv in ([], ["--"], ["--minutes", "5"], ["--minutes", "5", "--scope", "deploy", "--port", "/dev/x"]):
            self.assertIs(grant.operation_for(argv), IssueGrant, argv)
        self.assertEqual(self.grant("--che")[0], 1, "an abbreviation runs the check, as argparse took it before")

    def test_the_help_of_each_mode_names_both_flags(self):
        for argv in (["--help"], ["--check", "--help"]):
            out = io.StringIO()
            with self.assertRaises(SystemExit) as raised, contextlib.redirect_stdout(out):
                grant.main(argv, outside=FakeOutsideWorld())
            self.assertEqual(raised.exception.code, 0)
            self.assertIn("--check", out.getvalue())
            self.assertIn("--minutes", out.getvalue())
        out = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(out):
            grant.main(["--help"], outside=FakeOutsideWorld())
        self.assertIn("--scope {live,deploy}", out.getvalue())

    def test_a_flag_of_the_other_mode_and_no_mode_are_refused_with_the_usage(self):
        self.assertIn("unrecognized arguments: --json", self.refused(["--minutes", "5", "--json"]))
        self.assertIn("unrecognized arguments: --minutes 5", self.refused(["--check", "--minutes", "5"]))
        self.assertIn("unrecognized arguments: --scope live", self.refused(["--check", "--scope", "live"]))
        self.assertIn("the following arguments are required: --minutes", self.refused([]))
        self.assertTrue(self.refused(["--check", "--json", "--bogus"]).startswith("usage: grant.py "))

    def test_issue_grants_input_schema_has_minutes_as_a_required_integer_and_scope_as_a_choice(self):
        schema = IssueGrant().input_schema()
        self.assertEqual((schema["required"], schema["properties"]["minutes"]["type"]), (["minutes"], "integer"))
        self.assertEqual((schema["properties"]["scope"]["enum"], schema["properties"]["scope"]["default"]), (["live", "deploy"], "live"))
        self.assertNotIn("json", schema["properties"])
        self.assertNotIn("required", CheckGrant().input_schema())

    def test_a_crash_with_json_prints_no_line(self):
        def boom(name, **where):
            raise RuntimeError("boom")
        code, out, err = self.grant("--check", "--json", find_tool=boom)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("Traceback (most recent call last):", err)

    def test_the_restart_notice_the_question_and_the_granted_line_come_in_that_order(self):
        out = io.StringIO()

        class Asking(FakeConsent):
            def ask(self, question):
                out.write("asked: %s\n" % question[:12])
                return True
        outside = FakeOutsideWorld(run=self.run_tool, find_tool=found, reporter=TerminalReporter(out), clock=self.clock,
                                   make_consent=lambda line: Asking(True))
        with contextlib.redirect_stdout(out):
            self.assertEqual(grant.main(["--minutes", "30"], outside=outside), 0)
        lines = out.getvalue().splitlines()
        self.assertTrue(lines[0].startswith("  the board restarts while it is read"), lines)
        self.assertEqual(lines[1], "asked: let Claude r")
        self.assertTrue(lines[2].startswith("  granted (live): board 8c:bf:ea:xx:xx:xx"), lines)
        self.assertEqual(len(lines), 3)

    def test_the_restart_notice_is_an_event_of_the_look(self):
        outside = FakeOutsideWorld(run=self.run_tool, find_tool=found, clock=self.clock, make_consent=lambda line: FakeConsent(True))
        result = IssueGrant().run(minutes=30, scope="live", project=Path("."), port=None, outside=outside)
        events = outside.reporter.events
        self.assertEqual([(event.kind, event.code) for event in events], [(BEGIN, "look"), (LINE, "look")])
        self.assertTrue(events[1].text.startswith("the board restarts while it is read"), events[1].text)
        self.assertEqual((result.data["mac"], result.findings, result.status()), (MAC, (), "ok"))

    def test_a_stop_of_the_issue_is_one_finding_of_the_status_of_its_exit_code(self):
        def missing(name, **where):
            raise tools.ToolProblem("no mpremote")
        for result, status, code in ((self.issued(FakeConsent(False)), "problems", "answered_no"),
                                     (self.issued(minutes=0), "could-not-run", "bad_minutes"),
                                     (self.issued(find_tool=missing), "could-not-run", "tool_missing")):
            self.assertEqual((result.status(), [finding.code for finding in result.findings], result.data), (status, [code], None))
        self.devs = data("mpremote-devs-one.txt") + OTHER
        self.assertEqual([finding.code for finding in self.issued().findings], ["two_boards"])
        self.devs = "/dev/cu.usbserial-1410 None 1a86:7523 USB Serial\n"
        self.assertEqual([(finding.severity, finding.code) for finding in self.issued().findings], [("problems", "serial_not_mac")])
        (self.home / "afile").write_text("")
        os.environ["SPARK_HOME"] = str(self.home / "afile")
        self.devs = data("mpremote-devs-one.txt")
        self.assertEqual([(finding.severity, finding.code) for finding in self.issued().findings], [("could-not-run", "store_problem")])

    def test_an_issue_without_the_asks_effect_is_refused_before_the_board_is_touched(self):
        from spark.core.operation import BOARD, READS, RUNS
        outside = build_outside_world((READS, RUNS, BOARD), TerminalReporter(io.StringIO()), find_tool=found, clock=self.clock,
                                      make_consent=lambda line: FakeConsent(True))
        result = run_operation(IssueGrant(), dict(minutes=30, scope="live", project=Path("."), port=None), outside)
        self.assertEqual(([finding.code for finding in result.findings], self.ran), (["undeclared_effect"], []))
        self.assertIn("declares no `asks` effect", result.findings[0].sentence)

    def test_the_check_is_one_problem_per_refusal_and_one_unchecked_item_when_it_could_not_look(self):
        self.grant("--minutes", "30", consent=FakeConsent(True))
        granted = self.checked()
        self.assertEqual((granted.status(), granted.findings, granted.data["granted"]), ("ok", [], True))
        self.now = START + datetime.timedelta(minutes=30)
        self.assertEqual([(finding.severity, finding.code) for finding in self.checked().findings], [("problems", "grant_expired")])
        self.now = START
        path = self.home / "grants" / "8c-bf-ea-xx-xx-xx.json"
        path.write_text(json.dumps(dict(self.kept(), expires_at="2099-01-01T00:00:00")))
        self.assertEqual([finding.code for finding in self.checked().findings], ["grant_no_zone"])
        path.write_text("{}")
        self.assertEqual([finding.code for finding in self.checked().findings], ["not_a_grant"])
        path.unlink()
        self.assertEqual([finding.code for finding in self.checked().findings], ["no_grant"])
        self.devs = data("mpremote-devs-two.txt")
        stopped = self.checked()
        self.assertEqual(([(finding.severity, finding.code) for finding in stopped.findings], stopped.data),
                         ([("could-not-run", "two_boards")], {"granted": False, "why": "could not run", "grant": None}))


if __name__ == "__main__":
    unittest.main()
