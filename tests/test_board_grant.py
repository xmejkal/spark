"""P253 (#265): the live grant. The person's one yes for one board and a time limit is kept in the store, a later call
finds it with `mpremote devs` only, and one after the limit, on another board or with no grant is refused."""

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
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
#: The whole path a person runs grant.py by (P283).
GRANT_SCRIPT = str(ROOT / "scripts" / "grant.py")
sys.path.insert(0, str(ROOT / "scripts"))

import board_grant  # noqa: E402
import grant  # noqa: E402
import tools  # noqa: E402
from fakes import FakeConsent  # noqa: E402
from test_board_look import data, done  # noqa: E402
from test_deploy import found  # noqa: E402

UTC = datetime.timezone.utc
#: The moment the fake clock starts, and the MAC of P228's bench C6 as the fixtures write it.
START = datetime.datetime(2026, 10, 17, 9, 0, tzinfo=UTC)
MAC = "8c:bf:ea:xx:xx:xx"
OTHER = "/dev/cu.usbmodem202 aa:bb:cc:dd:ee:ff 303a:1001 Espressif USB JTAG/serial debug unit\n"


class GrantCase(unittest.TestCase):
    """A scratch store, a fake clock, and fake mpremote and esptool that answer from P228's fixtures."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.now, self.ran = START, []
        self.devs, self.esptool = data("mpremote-devs-one.txt"), data("c6-flash-id.txt")

    def run_tool(self, argv, **kw):
        self.ran.append(argv)
        return done(self.devs if "devs" in argv else self.esptool)

    def grant(self, *argv, consent=None):
        """(exit code, stdout, stderr) of grant.py with the fakes."""
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(tools, "find", side_effect=found), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = grant.main(list(argv), run=self.run_tool, consent=consent, now=lambda: self.now)
        return code, out.getvalue(), err.getvalue()

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
        if "flash_id" in argv:
            return subprocess.CompletedProcess(argv, 2, "Connecting......\n", "ERROR: A fatal error occurred: Failed "
                                               "to connect to Espressif device: No serial data received.\nFor "
                                               "troubleshooting steps visit: https://docs.espressif.com\n")
        return done("")  # the doctor's console read: silent

    def test_a_silent_board_names_esptool_s_words_the_port_and_hold_boot_last(self):
        code, _, err = self.grant("--minutes", "30", consent=FakeConsent(True))
        self.assertEqual(code, 2)
        lines = err.strip().splitlines()
        self.assertEqual(lines[0], "grant.py: could not read the board on /dev/cu.usbmodem101")
        self.assertIn("  said    ERROR: A fatal error occurred: Failed to connect to Espressif device: No serial data "
                      "received.", lines)
        self.assertIn("  check   console: the console was silent for 2 s", lines)
        self.assertTrue(lines[-1].startswith("  next    hold the board's BOOT (B) button"))
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
                         (MAC, "2026-10-17T09:00:00+00:00", "2026-10-17T09:30:00+00:00"))
        self.assertEqual(len(kept["board_token"]), 4)
        self.assertIn("the board restarts while it is read", out)
        self.assertEqual(stat.S_IMODE((self.home / "grants" / "8c-bf-ea-xx-xx-xx.json").stat().st_mode), 0o600)

    def test_the_token_is_the_first_half_of_the_looks_token(self):
        self.grant("--minutes", "5", consent=FakeConsent(True))
        self.assertEqual(self.kept()["board_token"], hashlib.sha256(MAC.encode()).hexdigest()[:4])

    def test_no_saves_nothing(self):
        code, _, err = self.grant("--minutes", "30", consent=FakeConsent(False))
        self.assertEqual(code, 1)
        self.assertIn("no grant: the person answered no", err)
        self.assertFalse((self.home / "grants").exists())

    def test_no_terminal_names_the_line_to_run_and_saves_nothing(self):
        class Pipe(io.StringIO):
            def isatty(self):
                return False

        with mock.patch.object(sys, "stdin", Pipe()):
            code, _, err = self.grant("--minutes", "30")
        self.assertEqual(code, 2)
        # P283: the bare `grant.py` was "command not found" in the PO's terminal; the line names the script's whole path.
        self.assertIn("\n  %s\n" % shlex.join([GRANT_SCRIPT, "--minutes", "30", "--project", str(Path(".").resolve())]),
                      err + "\n")
        self.assertFalse((self.home / "grants").exists())
        self.assertEqual([argv[-1] for argv in self.ran], ["devs"], "the board restarted for nothing")

    def test_no_terminal_keeps_the_port_the_person_named(self):
        class Pipe(io.StringIO):
            def isatty(self):
                return False

        with mock.patch.object(sys, "stdin", Pipe()):
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
        self.assertEqual(self.kept()["expires_at"], "2026-10-17T09:40:00+00:00")

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
        self.assertEqual(self.ran[-1][-3:], ["--port", "/dev/cu.usbmodem101", "flash_id"])

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
        self.assertIn("no grant for this board: the person runs %s --minutes N in their own terminal" % GRANT_SCRIPT, out)

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
        self.assertEqual(self.kept()["expires_at"], "2026-10-17T09:45:00+00:00")

    def test_the_text_says_until_when(self):
        code, out, _ = self.grant("--check")
        self.assertEqual((code, out.strip()), (0, "granted: board 8c:bf:ea:xx:xx:xx until 2026-10-17T09:30:00+00:00"))


if __name__ == "__main__":
    unittest.main()
