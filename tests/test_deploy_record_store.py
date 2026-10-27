"""P401 (#518), P431 (OC5): DeployRecordStore writes spark's record of a board and reads what it says of the board on USB, and says what it cannot read."""

import json
import os
import shutil
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import deploy_record_store  # noqa: E402
import store  # noqa: E402

STORE = deploy_record_store.DeployRecordStore()
MAC = "8c:bf:ea:cc:97:70"
CANNOT_READ = "spark's record of it cannot be read"


def said(project="blink-c6", deployed="2026-10-19T09:24:50+02:00", mac=MAC):
    return {"mac": mac, "project": project, "board": "xiao-esp32-c6", "image_sha256": "0", "simulation": "passed",
            "deployed": deployed}


class LastDeployCase(unittest.TestCase):
    """An empty store of its own, and the machine's zone set to Prague for the test."""

    def setUp(self):
        home = Path(suite_temp.ROOT) / ("home-%d" % id(self))
        env = mock.patch.dict(os.environ, {"SPARK_HOME": str(home), "TZ": "Europe/Prague"})
        env.start()
        self.addCleanup(env.stop)
        time.tzset()
        self.addCleanup(time.tzset)
        self.addCleanup(shutil.rmtree, home, True)

    def write(self, text, mac=MAC):
        folder = store.place("boards")
        folder.mkdir(parents=True, exist_ok=True)
        (folder / (store.slug(mac) + ".json")).write_text(text)

    def write_deploys(self, deploys):
        self.write(json.dumps({"mac": MAC, "deploys": deploys}))

    def test_a_time_the_machine_zone_cannot_hold_is_said_as_stored(self):
        for stored in ("0001-01-01T00:30:00+14:00", "9999-12-31T23:59:59-14:00"):
            with self.subTest(stored=stored):
                self.assertEqual(deploy_record_store.LastDeploy("recorded", "p", "ready seen", stored).time_said(), stored)

    def test_a_utc_z_time_is_said_in_the_machine_zone(self):
        last = deploy_record_store.LastDeploy("recorded", "p", "ready seen", "2026-10-23T04:55:29Z")
        self.assertEqual(last.time_said(), "2026-10-23T06:55:29+02:00")

    def test_a_time_in_another_zone_is_said_in_the_machine_s_zone(self):
        last = deploy_record_store.LastDeploy("recorded", "p", "ready seen", "2026-10-19T07:24:50+00:00")
        self.assertEqual(last.time_said(), "2026-10-19T09:24:50+02:00")

    def test_a_time_with_no_zone_is_not_given_one(self):
        last = deploy_record_store.LastDeploy("recorded", "p", "ready seen", "2026-10-19T09:24:50")
        self.assertEqual(last.time_said(), "2026-10-19T09:24:50 (zone not stored)")

    def test_a_time_that_does_not_parse_is_as_stored(self):
        self.assertEqual(deploy_record_store.LastDeploy("recorded", "p", "ready seen", "last tuesday").time_said(), "last tuesday")

    def test_a_folder_or_a_broken_link_in_the_record_place_is_not_checked_never_none(self):
        target = store.place("boards") / (store.slug(MAC) + ".json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.mkdir()
        self.assertEqual(STORE.read_last_deploy(MAC).state, "not-checked")
        target.rmdir()
        target.symlink_to(target.parent / "gone.json")
        self.assertEqual(STORE.read_last_deploy(MAC).state, "not-checked")

    def test_an_empty_time_is_not_checked(self):
        self.write_deploys([{"project": "p", "verdict": "ready seen", "deployed": " "}])
        self.assertEqual(STORE.read_last_deploy(MAC).state, "not-checked")


class ReadLastDeployTest(LastDeployCase):
    def test_the_state_words_are_outcomes_and_the_store_keeps_none(self):
        for name in ("RECORDED", "NONE_RECORDED", "NOT_CHECKED"):
            self.assertFalse(hasattr(deploy_record_store, name), name)

    def test_a_round_trip_gives_the_project_verdict_and_time_that_write_deploy_wrote(self):
        STORE.write_deploy(said(), "ready seen", "a test")
        last = STORE.read_last_deploy(MAC)
        self.assertEqual((last.state, last.project, last.verdict, last.deployed),
                         ("recorded", "blink-c6", "ready seen", "2026-10-19T09:24:50+02:00"))

    def test_the_store_reads_what_it_wrote(self):
        path = STORE.write_deploy(said(), "ready seen", "a test")
        self.assertEqual(path, STORE.find_path(MAC))
        record = json.loads(path.read_text())
        self.assertEqual((record["mac"], record["board"]), (MAC, "xiao-esp32-c6"))
        self.assertEqual(record["deploys"], [{"project": "blink-c6", "image_sha256": "0", "deployed": "2026-10-19T09:24:50+02:00",
                                              "verdict": "ready seen", "simulation": "passed", "yes": "a test"}])
        last = STORE.read_last_deploy(MAC)
        self.assertEqual(last.to_dict(), {"state": "recorded", "why": None, "project": "blink-c6", "verdict": "ready seen",
                                          "deployed": "2026-10-19T09:24:50+02:00"})

    def test_a_record_that_is_no_board_record_is_left_as_it_is(self):
        self.write("[1, 2]")
        with self.assertRaises(store.StoreProblem):
            STORE.write_deploy(said(), "ready seen", "a test")
        self.assertEqual(STORE.find_path(MAC).read_text(), "[1, 2]")

    def test_none_recorded_and_not_checked_give_their_dicts(self):
        self.assertEqual(STORE.read_last_deploy(MAC).to_dict(), {"state": "none-recorded", "why": None, "project": None,
                                                                 "verdict": None, "deployed": None})
        self.assertEqual(STORE.read_last_deploy(None).to_dict(), {"state": "not-checked", "why": "the board's MAC was not read",
                                                                  "project": None, "verdict": None, "deployed": None})

    def test_two_deploys_the_last_one_wins(self):
        STORE.write_deploy(said("blink-c6"), "ready seen", "a test")
        STORE.write_deploy(said("reaction-game", "2026-10-23T06:55:29+02:00"), "ready not seen", "a test")
        last = STORE.read_last_deploy(MAC)
        self.assertEqual((last.project, last.verdict), ("reaction-game", "ready not seen"))

    def test_another_board_s_record_is_not_this_board_s(self):
        STORE.write_deploy(said(mac="aa:bb:cc:dd:ee:01"), "ready seen", "a test")
        self.assertEqual(STORE.read_last_deploy("aa:bb:cc:dd:ee:011").state, "none-recorded")
        self.assertEqual(STORE.read_last_deploy(MAC).state, "none-recorded")

    def test_no_mac_is_not_checked_and_says_so(self):
        for mac in (None, ""):
            last = STORE.read_last_deploy(mac)
            self.assertEqual((last.state, last.why), ("not-checked", "the board's MAC was not read"))

    def test_no_file_is_none_recorded(self):
        last = STORE.read_last_deploy(MAC)
        self.assertEqual((last.state, last.why, last.project), ("none-recorded", None, None))

    def test_every_shape_that_is_not_a_record_is_not_checked_with_the_same_why(self):
        shapes = {"unparsable": "{not json", "empty file": "", "a list": "[1, 2]", "a string": '"x"', "no deploys": '{"mac": "m"}',
                  "deploys a dict": '{"deploys": {}}', "empty deploys": '{"deploys": []}',
                  "newest not a dict": '{"deploys": [{"project": "p"}, 5]}',
                  "newest has no verdict": '{"deploys": [{"project": "p", "deployed": "d"}]}',
                  "newest project not a string": '{"deploys": [{"project": 3, "verdict": "v", "deployed": "d"}]}',
                  "too deep": "[" * 100000}
        for name, text in shapes.items():
            with self.subTest(name):
                self.write(text)
                last = STORE.read_last_deploy(MAC)
                self.assertEqual((last.state, last.why, last.project), ("not-checked", CANNOT_READ, None))

    def test_a_record_that_cannot_be_opened_is_not_checked(self):
        self.write_deploys([])
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("no")):
            self.assertEqual(STORE.read_last_deploy(MAC).why, CANNOT_READ)

    def test_an_older_bad_entry_does_not_matter_when_the_newest_is_good(self):
        self.write_deploys([5, {"project": "p", "verdict": "v", "deployed": "d"}])
        self.assertEqual(STORE.read_last_deploy(MAC).project, "p")
