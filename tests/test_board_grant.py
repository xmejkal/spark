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
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
#: The whole path a person runs grant.py by (P283).
GRANT_SCRIPT = str(ROOT / "scripts" / "grant.py")
sys.path.insert(0, str(ROOT / "scripts"))

import board_console  # noqa: E402
import board_doctor  # noqa: E402
import board_grant  # noqa: E402
import store  # noqa: E402
import board_look  # noqa: E402
import boards  # noqa: E402
import deploy_gate  # noqa: E402
import grant  # noqa: E402
import image_evidence  # noqa: E402
import tools  # noqa: E402
from fakes import FakeClock, FakeConsent, FakeProbePlatform, line_made_at_import, pin_time_zone  # noqa: E402
from test_board_look import data, done  # noqa: E402
from test_deploy import found  # noqa: E402


UTC = datetime.timezone.utc
#: The moment the fake clock starts, and the MAC of P228's bench C6 as the fixtures write it.
START = datetime.datetime(2026, 10, 17, 9, 0, tzinfo=UTC)
MAC = "8c:bf:ea:xx:xx:xx"
OTHER = "/dev/cu.usbmodem202 aa:bb:cc:dd:ee:ff 303a:1001 Espressif USB JTAG/serial debug unit\n"


def a_grant(scope="deploy", mac=MAC, minutes=30, since=START, **changes):
    """A Grant of `scope` for `mac` that starts at `since` and lasts `minutes`, with `changes` to its fields."""
    fields = dict(mac=mac, board_token=board_look.board_token(mac), granted_by="ada", granted_at=since.isoformat(),
                  expires_at=(since + datetime.timedelta(minutes=minutes)).isoformat(), scope=scope)
    return board_grant.Grant(**dict(fields, **changes))


def a_report(verdict="match", mac=MAC, last_deploy_not_checked=False):
    """What consent_for_deploy reads of a look: its verdict, the board's MAC and whether its last deploy was checked."""
    return mock.Mock(verdict=verdict, reading=board_look.BoardReading("esp32c6", 4, mac),
                     **{"last_deploy_not_checked.return_value": last_deploy_not_checked})


class GrantScopeTest(unittest.TestCase):
    """The store keeps a live and a deploy grant side by side, and each reads only its own file."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.grants = board_grant.GrantStore()

    def test_a_grant_with_no_scope_in_its_file_reads_as_a_live_grant(self):
        old = {key: value for key, value in a_grant("live")._asdict().items() if key != "scope"}
        (self.home / "grants").mkdir()
        (self.home / "grants" / "8c-bf-ea-xx-xx-xx.json").write_text(json.dumps(old))
        self.assertEqual(self.grants.find(MAC), a_grant("live"))
        self.assertEqual(self.grants.find(MAC).scope, "live")

    def test_a_file_whose_scope_differs_from_its_name_is_refused(self):
        for scope, wanted, name in (("deploy", "live", "8c-bf-ea-xx-xx-xx"), ("live", "deploy", "8c-bf-ea-xx-xx-xx-deploy"),
                                    ("x", "deploy", "8c-bf-ea-xx-xx-xx-deploy")):
            (self.home / "grants").mkdir(exist_ok=True)
            (self.home / "grants" / (name + ".json")).write_text(json.dumps(a_grant(scope)._asdict()))
            with self.assertRaises(board_grant.GrantRefusedError) as refused:
                self.grants.find(MAC, wanted)
            self.assertEqual(refused.exception.why, "not a grant", (scope, wanted))

    def test_a_deploy_grant_alone_opens_no_live_grant(self):
        self.grants.save(a_grant("deploy"))
        self.assertIsNone(self.grants.find(MAC))
        finder = mock.Mock(require_one_board=lambda *a: board_look.Port("/dev/x", MAC, "303a:1001", "p"))
        service = board_grant.GrantService(finder, now=FakeClock(START).now)
        self.assertEqual(service.check().why, "no grant")

    def test_a_live_grant_alone_opens_no_deploy_grant(self):
        self.grants.save(a_grant("live"))
        self.assertIsNone(self.grants.find(MAC, "deploy"))

    def test_the_unsafe_times_of_a_grant_are_not_trusted(self):
        for changes, why in (({"expires_at": "garbage"}, "not a grant"),
                             ({"granted_at": "garbage"}, "not a grant"),
                             ({"expires_at": None}, "not a grant"),
                             ({"expires_at": "2099-01-01T00:00:00"}, "no zone"),
                             ({"granted_at": "2026-10-17T08:00:00"}, "no zone"),
                             ({"expires_at": "2027-10-17T09:30:00+00:00"}, "not a grant"),
                             ({"granted_at": "2026-10-17T09:05:00+00:00"}, "not a grant"),
                             ({"expires_at": "2026-10-17T09:00:00+00:00"}, "expired")):
            self.assertEqual(a_grant(**changes).why_not_valid(START), why, changes)
        self.assertIsNone(a_grant().why_not_valid(START))

    def test_the_longest_grant_counts_from_the_yes_not_from_now(self):
        two_hours_ago = START - datetime.timedelta(hours=2)
        self.assertEqual(a_grant(since=two_hours_ago, minutes=25 * 60).why_not_valid(START), "not a grant")
        self.assertIsNone(a_grant(since=two_hours_ago, minutes=24 * 60).why_not_valid(START))

    def test_a_clock_with_no_zone_is_no_valid_time(self):
        self.assertEqual(a_grant().why_not_valid(datetime.datetime(2026, 10, 17, 9, 0)),
                         "no zone")


class ConsentForDeployTest(unittest.TestCase):
    """consent_for_deploy: the standing yes for a look that matched and a valid deploy grant, else the terminal."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        pin_time_zone(self)
        self.clock, self.terminal = FakeClock(START), FakeConsent(False)
        self.service = board_grant.GrantService(now=self.clock.now)

    def choose(self, report=None, ignore_older_runs=False, evidence=None):
        return self.service.consent_for_deploy(report or a_report(), evidence or image_evidence.PassedRunEvidence(ignore_older_runs), self.terminal)

    def assertTerminal(self, why, **kw):
        chosen = self.choose(**kw)
        self.assertIs(chosen.consent, self.terminal)
        self.assertEqual(chosen.why, why)

    def test_a_look_whose_last_deploy_was_not_checked_asks_in_the_terminal(self):
        board_grant.GrantStore().save(a_grant())
        chosen = self.choose(report=a_report(last_deploy_not_checked=True))
        self.assertEqual((chosen.consent, chosen.why), (self.terminal, "last deploy not checked"))

    def test_a_valid_deploy_grant_and_a_matching_look_give_the_standing_yes(self):
        board_grant.GrantStore().save(a_grant())
        chosen = self.choose()
        self.assertIsInstance(chosen.consent, board_grant.StandingConsentStrategy)
        self.assertIsNone(chosen.why)
        self.assertTrue(chosen.consent.ask("erase ALL?"))
        self.assertEqual(chosen.consent.who,
                         "standing yes typed by ada at 2026-10-17T11:00:00+02:00, until 2026-10-17T11:30:00+02:00")

    def test_a_grant_kept_in_utc_says_its_times_in_the_machines_zone(self):
        board_grant.GrantStore().save(a_grant())  # a_grant keeps START as UTC, as a grant written before P291 did
        self.assertIn("at 2026-10-17T11:00:00+02:00, until 2026-10-17T11:30:00+02:00", self.choose().consent.who)

    def test_a_mac_in_capitals_finds_the_grant(self):
        board_grant.GrantStore().save(a_grant())
        self.assertIsNone(self.choose(a_report(mac=MAC.upper())).why)

    def test_no_deploy_grant_asks_in_the_terminal(self):
        self.assertTerminal("no grant")

    def test_an_ended_deploy_grant_asks_in_the_terminal(self):
        board_grant.GrantStore().save(a_grant())
        self.clock.advance(minutes=30)
        self.assertTerminal("expired")

    def test_only_a_live_grant_asks_in_the_terminal(self):
        board_grant.GrantStore().save(a_grant("live"))
        self.assertTerminal("no grant")

    def test_a_deploy_grant_of_another_board_asks_in_the_terminal(self):
        board_grant.GrantStore().save(a_grant(mac="aa:bb:cc:dd:ee:ff"))
        self.assertTerminal("no grant")

    def test_a_deploy_file_whose_scope_differs_asks_in_the_terminal(self):
        board_grant.GrantStore().save(a_grant())
        (self.home / "grants" / "8c-bf-ea-xx-xx-xx-deploy.json").write_text(
            json.dumps(a_grant("live")._asdict()))
        self.assertTerminal("not a grant")

    def test_a_file_that_is_no_grant_asks_in_the_terminal_and_never_crashes(self):
        (self.home / "grants").mkdir()
        (self.home / "grants" / "8c-bf-ea-xx-xx-xx-deploy.json").write_text("not json")
        self.assertTerminal("not a grant")

    def test_a_mac_that_is_no_text_asks_in_the_terminal_and_never_crashes(self):
        (self.home / "grants").mkdir()
        for mac in (12, ["8c"], None):
            (self.home / "grants" / "8c-bf-ea-xx-xx-xx-deploy.json").write_text(
                json.dumps(dict(a_grant()._asdict(), mac=mac)))
            self.assertTerminal("not a grant")

    def test_a_look_with_a_warning_and_no_deploy_grant_says_there_is_no_grant(self):
        self.assertTerminal("no grant", report=a_report("warning"))
        self.assertTerminal("no grant", ignore_older_runs=True)

    def test_a_time_that_cannot_be_trusted_asks_in_the_terminal(self):
        for changes, why in (({"expires_at": "2099-01-01T00:00:00"}, "no zone"),
                             ({"expires_at": "2027-10-17T09:30:00+00:00"}, "not a grant"),
                             ({"expires_at": "garbage"}, "not a grant")):
            board_grant.GrantStore().save(a_grant(**changes))
            self.assertTerminal(why)

    def test_a_look_that_is_no_match_asks_in_the_terminal(self):
        board_grant.GrantStore().save(a_grant())
        for verdict in ("warning", "stop"):
            self.assertTerminal("look not a match", report=a_report(verdict))

    def test_ignore_older_runs_asks_in_the_terminal(self):
        board_grant.GrantStore().save(a_grant())
        self.assertTerminal("ignore older runs", ignore_older_runs=True)

    def test_no_simulation_asks_in_the_terminal(self):
        board_grant.GrantStore().save(a_grant())
        self.assertTerminal("no simulation", evidence=image_evidence.NoSimulationEvidence(self.home))

    def test_the_standing_yes_stops_when_the_grant_ends_before_the_erase(self):
        board_grant.GrantStore().save(a_grant())
        consent = self.choose().consent
        self.clock.advance(minutes=31)
        for step in (consent.require_ready, lambda: consent.ask("erase ALL?")):
            with self.assertRaises(deploy_gate.GateClosedError) as shut:
                step()
            self.assertIn("deploy grant ended before the erase", str(shut.exception))
            self.assertEqual(shut.exception.code, 2)

    def test_the_standing_yes_works_with_the_real_clock(self):
        board_grant.GrantStore().save(a_grant(since=board_console.SystemClock().now().replace(microsecond=0)))
        chosen = board_grant.GrantService().consent_for_deploy(a_report(), image_evidence.PassedRunEvidence(), self.terminal)
        self.assertIsNone(chosen.why)
        self.assertTrue(chosen.consent.ask("x"))


class LocalTimeTest(unittest.TestCase):
    """P291, P315: spark writes and says a time in the machine's zone, with the zone."""

    def setUp(self):
        pin_time_zone(self)

    def test_now_has_the_machines_zone(self):
        self.assertIn(board_console.SystemClock().now().utcoffset(),
                      (datetime.timedelta(hours=1), datetime.timedelta(hours=2)))  # Prague: winter or summer

    def test_a_kept_time_has_no_fraction_of_a_second(self):
        moment = datetime.datetime(2026, 10, 18, 10, 0, 0, 123456, tzinfo=UTC)
        self.assertEqual(board_grant.stamp(moment), "2026-10-18T12:00:00+02:00")

    def test_a_stored_utc_time_is_said_in_the_machines_zone(self):
        self.assertEqual(board_grant.say_in_local_zone("2026-10-18T04:30:19+00:00"), "2026-10-18T06:30:19+02:00")

    def test_a_grant_over_the_change_to_winter_time_ends_in_winter_time(self):
        clock = FakeClock(datetime.datetime(2026, 10, 25, 0, 30, tzinfo=UTC))
        finder = mock.Mock()
        finder.require_one_board.return_value = mock.Mock(device="/dev/cu.usbmodem101", serial=MAC)
        reader = mock.Mock()
        reader.read.return_value = mock.Mock(mac=MAC)
        grants = mock.Mock()
        grant = board_grant.GrantService(finder, reader, grants, now=clock.now).issue(
            None, 60, FakeConsent(True), scope="deploy")
        self.assertEqual((grant.granted_at, grant.expires_at), ("2026-10-25T02:30:00+02:00", "2026-10-25T02:30:00+01:00"))


class ANewlineInTheStorePathTest(unittest.TestCase):
    """P444 (#592): the store's path is in the sentence of a broken tools.json, and a newline in it cannot start a line that
    looks like spark's own, from any of the three scripts that read the tools list."""

    def test_no_stderr_line_of_grant_live_or_look_starts_with_the_fake_word(self):
        home = Path(tempfile.mkdtemp()) / "a\nGRANTED (deploy): board ok"
        home.mkdir()
        (home / "tools.json").write_text("{nope")
        project = Path(tempfile.mkdtemp())
        for script, extra in (("grant.py", ["--check"]), ("live.py", ["--code", "x"]), ("look.py", [])):
            with self.subTest(script=script):
                run = subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--project", str(project)] + extra,
                                     env=dict(os.environ, SPARK_HOME=str(home)), capture_output=True, text=True)
                self.assertEqual(run.returncode, 2)
                self.assertEqual([line for line in run.stderr.splitlines() if line.startswith("GRANTED")], [])
                self.assertEqual(len(run.stderr.splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
