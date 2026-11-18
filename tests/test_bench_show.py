"""P919 (#1301): bench.py show lists each board on USB with its deploys, its kept projects and its grants, and opens no port.
The stores' new reads first, then the flow and the Operation."""

import datetime
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.bench import board_codes  # noqa: E402
from spark.bench import bench_service  # noqa: E402
from spark.bench import board_grant  # noqa: E402
from spark.bench import board_look  # noqa: E402
from spark.bench import known_board  # noqa: E402
from spark.bench.board_look import Port  # noqa: E402
from spark.core import outcomes  # noqa: E402
from spark.records import store  # noqa: E402
from spark.records.deploy_record_store import DeployRecordStore  # noqa: E402
from fakes import FakePortFinder  # noqa: E402

#: Invented MACs, never a real board's: board A and board B.
MAC_A, MAC_B = "aa:bb:cc:dd:ee:ff", "aa:bb:cc:dd:12:34"
#: mpremote devs rows: a native S3 whose serial is its MAC with no colon, as the game box's is, a C6 whose serial is its
#: MAC with colons, a bridge chip, a native board whose firmware set its serial, and a CH340 with no serial.
S3 = Port("/dev/cu.usbmodem1101", "aabbccddeeff", "303a:1001", "Espressif USB JTAG/serial debug unit")
C6 = Port("/dev/cu.usbmodem101", MAC_B, "303a:1001", "Espressif USB JTAG/serial debug unit")
BRIDGE = Port("/dev/cu.usbserial-01A2B3C4", "01A2B3C4", "10c4:ea60", "Silicon Labs CP2104 USB to UART Bridge Controller")
FIRMWARE_SERIAL = Port("/dev/cu.usbmodem1101", "SPARK-S3LCD", "303a:4001", "Espressif Device")
NO_SERIAL = Port("/dev/cu.usbserial-1410", "None", "1a86:7523", "USB Serial")


class StoreCase(unittest.TestCase):
    """A scratch store of its own."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        patcher = mock.patch.dict(os.environ, {"SPARK_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def keep(self, project, mac, usb_key, at="2026-11-17T18:00:00+01:00"):
        """The store keeps the board `mac` for `project`, as a yes on a look keeps it."""
        known_board.KnownBoardStore().write(known_board.KnownBoard(str(Path(project).resolve()), mac, usb_key,
                                                                   "firebeetle2-esp32s3", "a test", at))

    def deploys(self, mac, entries, board="firebeetle2-esp32s3"):
        """The store's record of the board `mac` with these deploy entries, as write_deploy appends them."""
        place = store.place("boards")
        place.mkdir(parents=True, exist_ok=True)
        (place / (store.slug(mac) + ".json")).write_text(json.dumps({"mac": mac, "board": board, "deploys": entries}))


def entry(project, deployed, verdict="ready seen"):
    return {"project": project, "image_sha256": "0" * 64, "deployed": deployed, "verdict": verdict, "simulation": None,
            "yes": "typed by a test", "micropython_banner": None}


class TheMacPartOfASerialTest(unittest.TestCase):
    def test_a_serial_of_12_hex_digits_with_no_colon_gives_the_mac_with_colons(self):
        self.assertEqual(known_board.mac_part_of(S3), MAC_A)

    def test_a_serial_with_colons_gives_the_same_form(self):
        self.assertEqual(known_board.mac_part_of(C6), MAC_B)

    def test_upper_case_hex_and_a_longer_serial_give_the_first_six_bytes_in_lower_case(self):
        self.assertEqual(known_board.mac_part_of(S3._replace(serial="AABBCCDDEEFF-01")), MAC_A)

    def test_a_bridge_a_firmware_serial_and_no_serial_give_none(self):
        for row in (BRIDGE, FIRMWARE_SERIAL, NO_SERIAL, BRIDGE._replace(serial="aabbccddeeff")):
            self.assertIsNone(known_board.mac_part_of(row), row)


class TheKeptBoardsTest(StoreCase):
    def test_no_place_gives_no_record_and_nothing_unreadable(self):
        self.assertEqual(known_board.KnownBoardStore().read_all(), known_board.KeptBoards([], []))

    def test_every_kept_board_of_every_folder_comes_back(self):
        self.keep("/tmp/one", MAC_A, "aabbccddeeff")
        self.keep("/tmp/two", MAC_B, None)
        kept = known_board.KnownBoardStore().read_all()
        self.assertEqual(sorted(known.mac for known in kept.records), sorted([MAC_A, MAC_B]))
        self.assertEqual(kept.unreadable, [])

    def test_a_file_that_cannot_be_used_is_named_and_the_others_still_come_back(self):
        self.keep("/tmp/one", MAC_A, "aabbccddeeff")
        bad = store.place("known-boards") / "0123456789abcdef.json"
        bad.write_text("{not json")
        kept = known_board.KnownBoardStore().read_all()
        self.assertEqual(([known.mac for known in kept.records], kept.unreadable), ([MAC_A], [bad]))

    def test_read_still_refuses_the_same_file(self):
        self.keep("/tmp/one", MAC_A, "aabbccddeeff")
        known_board.KnownBoardStore.find_path("/tmp/one").write_text('{"mac": 1}')
        with self.assertRaises(known_board.SparkError) as refused:
            known_board.KnownBoardStore().read("/tmp/one")
        self.assertEqual(refused.exception.code, "known_board_unreadable")


class TheDeploysTest(StoreCase):
    def test_no_record_is_none_recorded(self):
        self.assertEqual(DeployRecordStore().read_deploys(MAC_A).state, outcomes.NONE_RECORDED)

    def test_every_entry_comes_back_in_the_order_written_with_the_board(self):
        entries = [entry("blink", "2026-11-02T10:00:00+01:00"), entry("walk4", "2026-11-17T08:04:00")]
        self.deploys(MAC_A, entries)
        read = DeployRecordStore().read_deploys(MAC_A)
        self.assertEqual((read.state, list(read.entries), read.board, read.why), (outcomes.RECORDED, entries, "firebeetle2-esp32s3", None))

    def test_one_entry_without_a_project_or_a_time_makes_the_record_not_checked(self):
        for broken in ({"deployed": "2026-11-02"}, entry("walk4", ""), "not an entry", entry(7, "2026-11-02")):
            self.deploys(MAC_A, [entry("blink", "2026-11-02"), broken, entry("walk4", "2026-11-17")])
            read = DeployRecordStore().read_deploys(MAC_A)
            self.assertEqual((read.state, read.entries), (outcomes.NOT_CHECKED, ()), broken)

    def test_a_record_that_is_no_json_or_too_deep_is_not_checked(self):
        place = store.place("boards")
        place.mkdir(parents=True)
        for text in ("{not json", "[" * 100000 + "]" * 100000, '{"deploys": []}', '["no record"]'):
            (place / (store.slug(MAC_A) + ".json")).write_text(text)
            self.assertEqual(DeployRecordStore().read_deploys(MAC_A).state, outcomes.NOT_CHECKED, text[:20])

    def test_no_mac_is_not_checked(self):
        self.assertEqual(DeployRecordStore().read_deploys(None).state, outcomes.NOT_CHECKED)


class TheDeepGrantFileTest(StoreCase):
    def test_a_deeply_nested_grant_file_is_refused_and_does_not_crash(self):
        place = store.place("grants")
        place.mkdir(parents=True)
        (place / (board_grant.GrantStore.key(MAC_A) + ".json")).write_text("[" * 100000 + "]" * 100000)
        with self.assertRaises(board_grant.GrantRefusedError) as refused:
            board_grant.GrantStore().find(MAC_A)
        self.assertEqual(refused.exception.why, "not a grant")


class TheNewCodeTest(unittest.TestCase):
    def test_cannot_tell_board_has_its_own_sentence(self):
        self.assertIn("USB serial", board_codes.CODES["cannot_tell_board"])


#: The fake clock's now, and a grant given an hour before it that ended half an hour before it.
NOW = datetime.datetime(2026, 11, 18, 12, 0, tzinfo=datetime.timezone.utc)
ENDED = ("2026-11-18T11:00:00+00:00", "2026-11-18T11:30:00+00:00")


class ServiceCase(StoreCase):
    """BenchService on a fake list of boards and the real stores in a scratch store."""

    def give_grant(self, key, scope, times=ENDED):
        board_grant.GrantStore().save(board_grant.Grant(key, board_look.board_token(board_grant.mac_key(key)), "tester", *times, scope))

    def show(self, *rows):
        return bench_service.BenchService(FakePortFinder(list(rows)), now=lambda: NOW).show()

    def one(self, row):
        result = self.show(row)
        self.assertEqual(len(result.boards), 1)
        return result.boards[0]


class IdentifyTest(StoreCase):
    def kept(self, *records, unreadable=()):
        return known_board.KeptBoards(list(records), list(unreadable))

    def record(self, project, mac, usb_key):
        return known_board.KnownBoard(project, mac, usb_key, "esp32-devkit", "a test", "2026-11-17T18:00:00+01:00")

    def test_a_native_board_is_named_by_its_serial_and_kept_for_none(self):
        self.assertEqual(bench_service.identify(S3, self.kept()), (MAC_A, "usb_serial", None, []))

    def test_a_kept_bridge_board_is_named_by_the_kept_record(self):
        kept = self.record("/p/one", MAC_B, "01a2b3c4")
        self.assertEqual(bench_service.identify(BRIDGE, self.kept(kept)), (MAC_B, "kept_board", "esp32-devkit", [kept]))

    def test_a_bridge_board_that_none_keeps_is_not_named_and_kept_for_nothing(self):
        self.assertEqual(bench_service.identify(BRIDGE, self.kept(self.record("/p/one", MAC_B, "99999999"))), (None, None, None, []))

    def test_two_kept_records_of_one_serial_and_two_macs_name_no_mac_and_list_both(self):
        one, two = self.record("/p/one", MAC_A, "01a2b3c4"), self.record("/p/two", MAC_B, "01a2b3c4")
        self.assertEqual(bench_service.identify(BRIDGE, self.kept(one, two)), (None, None, None, [one, two]))

    def test_two_kept_records_of_one_board_name_it(self):
        one, two = self.record("/p/one", MAC_A, "aabbccddeeff"), self.record("/p/two", MAC_A, None)
        self.assertEqual(bench_service.identify(S3, self.kept(one, two))[:2], (MAC_A, "kept_board"))

    def test_no_serial_or_a_firmware_serial_is_not_known_when_the_store_keeps_boards_and_none_when_it_keeps_none(self):
        for row in (NO_SERIAL, FIRMWARE_SERIAL):
            self.assertEqual(bench_service.identify(row, self.kept(self.record("/p/one", MAC_A, None))), (None, None, None, None), row)
            self.assertEqual(bench_service.identify(row, self.kept()), (None, None, None, []), row)

    def test_an_unreadable_kept_file_makes_kept_for_not_known_and_still_names_the_board(self):
        self.assertEqual(bench_service.identify(S3, self.kept(unreadable=[Path("x.json")])), (MAC_A, "usb_serial", None, None))


class TheBenchServiceTest(ServiceCase):
    def test_no_board_is_an_empty_list(self):
        self.assertEqual(self.show(), bench_service.BenchResult([], []))

    def test_a_native_board_with_deploys_from_three_names_and_an_ended_grant(self):
        self.deploys(MAC_A, [entry("blink", "2026-11-02T10:00:00+01:00"), entry("walk4", "2026-11-10T09:00:00+01:00"),
                             entry("bench", "2026-11-10T11:00:00+01:00"), entry("walk4", "2026-11-17T08:04:00+01:00")])
        self.give_grant(MAC_A, "deploy")
        board = self.one(S3)
        said = board.to_dict()
        self.assertEqual(said["deploys_from"], [{"project": "walk4", "deploys": 2, "last": "2026-11-17T08:04:00+01:00"},
                                                {"project": "bench", "deploys": 1, "last": "2026-11-10T11:00:00+01:00"},
                                                {"project": "blink", "deploys": 1, "last": "2026-11-02T10:00:00+01:00"}])
        self.assertEqual((said["mac"], said["mac_from"], said["board"], said["kept_for"], said["unchecked"]),
                         (MAC_A, "usb_serial", "firebeetle2-esp32s3", [], []))
        self.assertEqual((said["last_deploy"]["state"], said["last_deploy"]["project"]), ("recorded", "walk4"))
        self.assertEqual(said["grants"], [{"scope": "deploy", "state": "ended", "granted_by": "tester", "granted_at": ENDED[0],
                                           "expires_at": ENDED[1]},
                                          {"scope": "live", "state": "none", "granted_by": None, "granted_at": None, "expires_at": None}])
        self.assertEqual((said["device"], said["also_on"], said["usb_serial"], said["usb_id"], said["product"]),
                         (S3.device, [], S3.serial, S3.usb, S3.product))

    def test_a_live_grant_is_asked_by_the_serial_and_a_deploy_grant_by_the_mac(self):
        self.give_grant(MAC_B, "live", ("2026-11-18T11:00:00+00:00", "2026-11-18T13:00:00+00:00"))
        self.give_grant("aabbccddeeff", "live")  # keyed by the serial with no colon: the S3's live grant
        self.assertEqual([row["state"] for row in self.one(C6).to_dict()["grants"]], ["none", "live"])
        self.assertEqual([row["state"] for row in self.one(S3).to_dict()["grants"]], ["none", "ended"])

    def test_two_boards_come_in_the_order_listed(self):
        self.assertEqual([board.device for board in self.show(C6, BRIDGE._replace(device="/dev/cu.usbserial-9")).boards],
                         [C6.device, "/dev/cu.usbserial-9"])

    def test_a_bridge_board_that_a_project_keeps_is_named_by_the_kept_record(self):
        self.keep("/tmp/one", MAC_B, "01a2b3c4")
        self.deploys(MAC_B, [entry("one", "2026-11-17T08:04:00+01:00")])
        said = self.one(BRIDGE).to_dict()
        self.assertEqual((said["mac"], said["mac_from"], [kept["project"] for kept in said["kept_for"]]),
                         (MAC_B, "kept_board", [str(Path("/tmp/one").resolve())]))
        self.assertEqual((said["deploys_from"][0]["project"], said["unchecked"]), ("one", []))

    def test_a_board_spark_cannot_tell_has_its_store_parts_unchecked(self):
        for row in (BRIDGE, NO_SERIAL, FIRMWARE_SERIAL):
            board = self.one(row)
            said = board.to_dict()
            self.assertEqual((said["mac"], said["deploys_from"], said["kept_for"], said["last_deploy"]["state"]),
                             (None, None, [], "not-checked"), row)
            self.assertEqual(said["unchecked"], ["last_deploy", "deploys_from", "grants"], row)
            self.assertEqual({item.code for item in board.unchecked}, {"cannot_tell_board"}, row)
            self.assertEqual(said["grants"][0]["state"], "not_checked", row)

    def test_an_unreadable_kept_file_makes_kept_for_unchecked_for_every_board(self):
        place = store.place("known-boards")
        place.mkdir(parents=True)
        (place / "0123456789abcdef.json").write_text("{not json")
        result = self.show(S3, C6)
        self.assertEqual(result.kept_unreadable, [place / "0123456789abcdef.json"])
        for board in result.boards:
            self.assertIsNone(board.to_dict()["kept_for"])
            self.assertEqual([(item.part, item.code) for item in board.unchecked], [("kept_for", "known_board_unreadable")])

    def test_an_unreadable_deploy_record_makes_both_deploy_parts_unchecked(self):
        place = store.place("boards")
        place.mkdir(parents=True)
        (place / (store.slug(MAC_A) + ".json")).write_text("{not json")
        board = self.one(S3)
        self.assertEqual([(item.part, item.code) for item in board.unchecked],
                         [("last_deploy", "last_deploy_not_checked"), ("deploys_from", "last_deploy_not_checked")])
        self.assertIsNone(board.to_dict()["deploys_from"])

    def test_a_bad_entry_in_the_middle_makes_deploys_from_unchecked_and_drops_none(self):
        self.deploys(MAC_A, [entry("blink", "2026-11-02"), {"project": "walk4"}, entry("walk4", "2026-11-17")])
        board = self.one(S3)
        self.assertIsNone(board.to_dict()["deploys_from"])
        self.assertIn(("deploys_from", "last_deploy_not_checked"), [(item.part, item.code) for item in board.unchecked])

    def test_an_unusable_grant_file_is_not_a_grant_and_unchecked(self):
        place = store.place("grants")
        place.mkdir(parents=True)
        (place / (board_grant.GrantStore.key(MAC_A, "deploy") + ".json")).write_text("[" * 100000 + "]" * 100000)
        board = self.one(S3)
        self.assertEqual(board.to_dict()["grants"][0]["state"], "not_a_grant")
        self.assertEqual([(item.part, item.code) for item in board.unchecked], [("grants", "not_a_grant")])

    def test_two_kept_records_of_one_serial_and_two_macs_leave_the_store_parts_unchecked(self):
        self.keep("/tmp/one", MAC_A, "01a2b3c4")
        self.keep("/tmp/two", MAC_B, "01a2b3c4")
        said = self.one(BRIDGE).to_dict()
        self.assertEqual((said["mac"], len(said["kept_for"]), said["unchecked"]), (None, 2, ["last_deploy", "deploys_from", "grants"]))

    def test_times_with_and_without_a_zone_under_one_name_give_the_last_entry_as_stored(self):
        self.deploys(MAC_A, [entry("walk4", "2026-11-17T08:04:00+01:00"), entry("walk4", "2026-11-10T09:00:00")])
        self.assertEqual(self.one(S3).to_dict()["deploys_from"], [{"project": "walk4", "deploys": 2, "last": "2026-11-10T09:00:00"}])


if __name__ == "__main__":
    unittest.main()
