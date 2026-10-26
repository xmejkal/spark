"""P401 (#518): board_facts.read_last_deploy reads what spark's store says of the board on USB, and says what it cannot read."""

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

import board_facts  # noqa: E402
import text_guards  # noqa: E402
import store  # noqa: E402

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
                last = board_facts.LastDeploy("recorded", "p", "ready seen", stored)
                self.assertIn(stored, last.line())
                self.assertIn(stored, last.in_question())

    def test_a_utc_z_time_is_said_in_the_machine_zone(self):
        last = board_facts.LastDeploy("recorded", "p", "ready seen", "2026-10-23T04:55:29Z")
        self.assertIn("2026-10-23T06:55:29+02:00", last.line())

    def test_a_folder_or_a_broken_link_in_the_record_place_is_not_checked_never_none(self):
        target = store.place("boards") / (store.slug(MAC) + ".json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.mkdir()
        self.assertEqual(board_facts.read_last_deploy(MAC).state, "not-checked")
        target.rmdir()
        target.symlink_to(target.parent / "gone.json")
        self.assertEqual(board_facts.read_last_deploy(MAC).state, "not-checked")

    def test_an_empty_time_is_not_checked(self):
        self.write_deploys([{"project": "p", "verdict": "ready seen", "deployed": " "}])
        self.assertEqual(board_facts.read_last_deploy(MAC).state, "not-checked")

    def test_a_project_name_cannot_add_a_line(self):
        last = board_facts.LastDeploy("recorded", "a\nmac    ff", "ready seen", "2026-10-19T09:24:50+02:00")
        self.assertNotIn("\n", last.line())
        self.assertNotIn("\n", last.in_question())



class ReadLastDeployTest(LastDeployCase):
    def test_the_state_words_are_outcomes_and_board_facts_keeps_none(self):
        for name in ("RECORDED", "NONE_RECORDED", "NOT_CHECKED"):
            self.assertFalse(hasattr(board_facts, name), name)

    def test_a_round_trip_gives_the_project_verdict_and_time_that_record_deploy_wrote(self):
        board_facts.record_deploy(said(), "ready seen", "a test")
        last = board_facts.read_last_deploy(MAC)
        self.assertEqual((last.state, last.project, last.verdict, last.deployed),
                         ("recorded", "blink-c6", "ready seen", "2026-10-19T09:24:50+02:00"))

    def test_two_deploys_the_last_one_wins(self):
        board_facts.record_deploy(said("blink-c6"), "ready seen", "a test")
        board_facts.record_deploy(said("reaction-game", "2026-10-23T06:55:29+02:00"), "ready not seen", "a test")
        last = board_facts.read_last_deploy(MAC)
        self.assertEqual((last.project, last.verdict), ("reaction-game", "ready not seen"))

    def test_another_board_s_record_is_not_this_board_s(self):
        board_facts.record_deploy(said(mac="aa:bb:cc:dd:ee:01"), "ready seen", "a test")
        self.assertEqual(board_facts.read_last_deploy("aa:bb:cc:dd:ee:011").state, "none-recorded")
        self.assertEqual(board_facts.read_last_deploy(MAC).state, "none-recorded")

    def test_no_mac_is_not_checked_and_says_so(self):
        for mac in (None, ""):
            last = board_facts.read_last_deploy(mac)
            self.assertEqual((last.state, last.why), ("not-checked", "the board's MAC was not read"))

    def test_no_file_is_none_recorded(self):
        last = board_facts.read_last_deploy(MAC)
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
                last = board_facts.read_last_deploy(MAC)
                self.assertEqual((last.state, last.why, last.project), ("not-checked", CANNOT_READ, None))

    def test_a_record_that_cannot_be_opened_is_not_checked(self):
        self.write_deploys([])
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("no")):
            self.assertEqual(board_facts.read_last_deploy(MAC).why, CANNOT_READ)

    def test_an_older_bad_entry_does_not_matter_when_the_newest_is_good(self):
        self.write_deploys([5, {"project": "p", "verdict": "v", "deployed": "d"}])
        self.assertEqual(board_facts.read_last_deploy(MAC).project, "p")


class LastDeployWordsTest(LastDeployCase):
    def recorded(self, deployed):
        self.write_deploys([{"project": "blink-c6", "verdict": "ready seen", "deployed": deployed}])
        return board_facts.read_last_deploy(MAC)

    def test_recorded_with_a_zone(self):
        last = self.recorded("2026-10-19T09:24:50+02:00")
        self.assertEqual(last.line(), "spark's last deploy here: blink-c6, ready seen, 2026-10-19T09:24:50+02:00 "
                                      "(its store record, not read from the board)")
        self.assertEqual(last.in_question(), "spark's store record names blink-c6 as its last deploy here, "
                                             "2026-10-19T09:24:50+02:00, ready seen")
        self.assertEqual(last.to_dict(), {"state": "recorded", "why": None, "project": "blink-c6", "verdict": "ready seen",
                                          "deployed": "2026-10-19T09:24:50+02:00"})

    def test_a_time_in_another_zone_is_said_in_the_machine_s_zone(self):
        self.assertIn(", 2026-10-19T09:24:50+02:00 (", self.recorded("2026-10-19T07:24:50+00:00").line())

    def test_a_time_with_no_zone_is_not_given_one(self):
        last = self.recorded("2026-10-19T09:24:50")
        self.assertIn("blink-c6, ready seen, 2026-10-19T09:24:50 (zone not stored) (its store record", last.line())
        self.assertIn("last deploy here, 2026-10-19T09:24:50 (zone not stored), ready seen", last.in_question())
        self.assertEqual(last.to_dict()["deployed"], "2026-10-19T09:24:50")

    def test_a_time_that_does_not_parse_is_as_stored(self):
        last = self.recorded("last tuesday")
        self.assertIn("blink-c6, ready seen, last tuesday (its store record", last.line())
        self.assertIn("last deploy here, last tuesday, ready seen", last.in_question())

    def test_none_recorded(self):
        last = board_facts.read_last_deploy(MAC)
        self.assertEqual(last.line(), "spark's last deploy here: none in its store record (it keeps only its own deploys)")
        self.assertEqual(last.in_question(), "spark's store record names no deploy here")
        self.assertEqual(last.to_dict(), {"state": "none-recorded", "why": None, "project": None, "verdict": None, "deployed": None})

    def test_not_checked(self):
        last = board_facts.read_last_deploy(None)
        self.assertEqual(last.line(), "spark's last deploy here: not checked: the board's MAC was not read")
        self.assertEqual(last.in_question(), "spark did not read its record of this board: the board's MAC was not read")
        self.assertEqual(last.to_dict(), {"state": "not-checked", "why": "the board's MAC was not read", "project": None,
                                          "verdict": None, "deployed": None})
        json.dumps(last.to_dict())


# --- MVP --- P403: every field of the line passes the print guard
class PrintableFieldsTest(LastDeployCase):
    def test_a_verdict_and_a_time_with_a_newline_show_a_question_mark_in_both_sentences(self):
        last = board_facts.LastDeploy("recorded", "blink\nc6", "ready\nseen", "not a time\nat all")
        for said in (last.line(), last.in_question()):
            with self.subTest(said=said):
                self.assertIn("blink?c6", said)
                self.assertIn("ready?seen", said)
                self.assertIn("not a time?at all", said)
                self.assertNotIn("\n", said)

    def test_a_time_with_a_zone_is_said_without_the_question_mark(self):
        last = board_facts.LastDeploy("recorded", "p", "ready seen", "2026-10-23T04:55:29Z")
        self.assertNotIn("?", last.line())

    def test_printable_shows_what_a_terminal_does_not_print_as_a_question_mark(self):
        self.assertEqual(text_guards.printable("a\nb\u202ec ok"), "a?b?c ok")


if __name__ == "__main__":
    unittest.main()
