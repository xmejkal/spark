"""P919 (#1301): bench.py show lists each board on USB with its deploys, its kept projects and its grants, and opens no port.
The stores' new reads first, then the flow and the Operation."""

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
from spark.bench import board_grant  # noqa: E402
from spark.bench import known_board  # noqa: E402
from spark.bench.board_look import Port  # noqa: E402
from spark.core import outcomes  # noqa: E402
from spark.records import store  # noqa: E402
from spark.records.deploy_record_store import DeployRecordStore  # noqa: E402

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
        bad = store.place(known_board.PLACE) / "0123456789abcdef.json"
        bad.write_text("{not json")
        kept = known_board.KnownBoardStore().read_all()
        self.assertEqual(([known.mac for known in kept.records], kept.unreadable), ([MAC_A], [bad]))

    def test_read_still_refuses_the_same_file(self):
        self.keep("/tmp/one", MAC_A, "aabbccddeeff")
        known_board.KnownBoardStore.find_path("/tmp/one").write_text('{"mac": 1}')
        with self.assertRaises(known_board.SparkError) as refused:
            known_board.KnownBoardStore().read("/tmp/one")
        self.assertEqual(refused.exception.code, board_codes.KNOWN_BOARD_UNREADABLE)


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
        self.assertEqual(refused.exception.why, board_grant.WHY_NOT_A_GRANT)


class TheNewCodeTest(unittest.TestCase):
    def test_cannot_tell_board_has_its_own_sentence(self):
        self.assertEqual(board_codes.CANNOT_TELL_BOARD, "cannot_tell_board")
        self.assertIn("USB serial", board_codes.CODES[board_codes.CANNOT_TELL_BOARD])


if __name__ == "__main__":
    unittest.main()
