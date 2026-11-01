"""P462 (#630): after the write, deploy counts a restart only when mpremote answers after it, and finds the port by the MAC."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import board_look  # noqa: E402
import board_start  # noqa: E402
import boards  # noqa: E402
from fakes import FakeClock, FakePortFinder  # noqa: E402

MAC = "8c:bf:ea:00:00:03"
#: The port as the ROM lists it (the serial is the MAC), as MicroPython lists it (hex of 8 bytes, the MAC first), and a bridge's.
ROM = board_look.Port("/dev/cu.usbmodem1101", MAC, "303a:1001", "ESP32-S3")
MICROPYTHON = board_look.Port("/dev/cu.usbmodem2101", "8CBFEA00000300FF", "303a:4001", "MicroPython")
BRIDGE = board_look.Port("/dev/cu.usbserial-1410", "01A2B3C4", "10c4:ea60", "CP2102")
OTHER = board_look.Port("/dev/cu.usbmodem3301", "8c:bf:ea:00:00:04", "303a:1001", "ESP32-S3")


def name(row):
    return row and row.device


class BoardStartTest(unittest.TestCase):
    def service(self, *looks, mac=MAC):
        """The service over a finder that lists `looks` (each a list of Ports) call by call, then the last one for good."""
        self.clock, self.finder = FakeClock(), FakePortFinder(*looks)
        self.lines = []
        return board_start.BoardStartService(self.finder, mac, self.clock, boards.ButtonPlaces.EMPTY)

    def answers_after(self, calls):
        """A read that says no `calls` times, then yes; it keeps the ports it was asked for."""
        self.asked = []

        def read(port):
            self.asked.append(port)
            return len(self.asked) > calls
        return read

    def test_the_port_is_found_by_the_mac_when_the_name_changed(self):
        service = self.service([OTHER], [MICROPYTHON])
        self.assertEqual(name(service.find_port(ROM.device)), MICROPYTHON.device)

    def test_another_board_on_the_old_name_does_not_hide_the_board_on_a_new_one(self):
        other_here = board_look.Port(ROM.device, "8c:bf:ea:00:00:04", "303a:1001", "ESP32-S3")
        self.assertEqual(name(self.service([other_here, MICROPYTHON]).find_port(ROM.device)), MICROPYTHON.device)

    def test_a_micropython_serial_of_8_bytes_matches_a_mac_with_colons(self):
        self.assertEqual(name(self.service([MICROPYTHON]).find_port("/dev/none")), MICROPYTHON.device)

    def test_a_redacted_serial_matches_by_lower_case_and_no_colons(self):
        redacted = board_look.Port("/dev/cu.usbmodem101", "8C:BF:EA:xx:xx:xx", "303a:1001", "x")
        self.assertEqual(name(self.service([redacted], mac="8c:bf:ea:xx:xx:xx").find_port("/dev/none")), redacted.device)

    def test_a_bridge_serial_is_no_mac_so_the_look_s_port_name_stays(self):
        self.assertEqual(name(self.service([BRIDGE]).find_port(BRIDGE.device)), BRIDGE.device)

    def test_no_mac_means_the_port_name_alone(self):
        self.assertEqual(name(self.service([ROM, OTHER], mac=None).find_port(OTHER.device)), OTHER.device)

    def test_a_port_that_is_not_listed_in_the_wait_is_none_after_it(self):
        service = self.service([])
        self.assertIsNone(name(service.find_port(ROM.device)))
        self.assertGreaterEqual(self.clock.elapsed, 7)

    def test_a_port_that_comes_back_in_the_wait_is_found_and_the_log_says_when(self):
        service = self.service([], [], [ROM])
        self.assertEqual(name(service.find_port(ROM.device)), ROM.device)
        self.assertIn("port back on %s after 1 s" % ROM.device, "".join(service.heard))

    def test_a_tool_restart_that_left_download_mode_is_not_counted(self):
        # P472 bench: esptool's restart dropped the port and brought it back, and the ROM still waited
        service = self.service([ROM], [], [ROM])
        read = self.answers_after(99)
        start = service.wait_for_start(ROM.device, read, self.lines.append, timeout_s=10)
        self.assertEqual((start.code, start.port), ("download_mode_stayed", ROM.device))
        self.assertEqual(self.asked, [ROM.device])
        self.assertEqual(len(self.lines), 1)
        self.assertIn("a restart in download mode, not counted", "".join(service.heard))

    def test_a_press_of_reset_counts_when_mpremote_answers_after_it(self):
        service = self.service([ROM], [ROM], [], [MICROPYTHON])
        start = service.wait_for_start(ROM.device, self.answers_after(0), self.lines.append, timeout_s=10)
        self.assertEqual((start.code, start.port), (None, MICROPYTHON.device))
        self.assertEqual((self.asked, self.lines), ([MICROPYTHON.device], []))
        self.assertIn("reset seen: the firmware answered", "".join(service.heard))

    def test_a_restart_that_did_not_count_and_a_press_that_did(self):
        service = self.service([ROM], [], [ROM], [], [ROM])
        start = service.wait_for_start(ROM.device, self.answers_after(1), self.lines.append, timeout_s=10)
        self.assertEqual((start.code, len(self.asked), len(self.lines)), (None, 2, 1))

    def test_a_port_that_never_comes_back_is_port_gone_and_no_read_was_made(self):
        service = self.service([ROM], [])
        start = service.wait_for_start(ROM.device, self.answers_after(0), self.lines.append, timeout_s=3)
        self.assertEqual((start.code, start.port, self.asked), ("port_gone", None, []))
        self.assertIn("unplug", start.sentence)

    def test_a_port_that_never_goes_is_download_mode_stayed(self):
        service = self.service([ROM])
        start = service.wait_for_start(ROM.device, self.answers_after(0), self.lines.append, timeout_s=3)
        self.assertEqual((start.code, start.port, self.asked), ("download_mode_stayed", ROM.device, []))

    def test_a_failed_list_between_two_listings_is_no_restart(self):
        failed = board_look.LookStop("could not list", reason="list_failed")
        service = self.service([ROM], failed, [ROM])
        read = self.answers_after(99)
        start = service.wait_for_start(ROM.device, read, self.lines.append, timeout_s=3, usb=ROM.usb)
        self.assertEqual((start.code, self.asked, self.lines), ("download_mode_stayed", [], []))

    def test_a_row_whose_usb_id_changed_is_a_restart_even_with_no_gap_seen(self):
        service = self.service([ROM], [MICROPYTHON])
        start = service.wait_for_start(ROM.device, self.answers_after(0), self.lines.append, timeout_s=3, usb=ROM.usb)
        self.assertEqual((start.code, start.port, self.asked), (None, MICROPYTHON.device, [MICROPYTHON.device]))

    def test_the_port_that_the_wait_gave_up_on_is_the_one_listed_by_the_mac(self):
        service = self.service([MICROPYTHON])  # no usb id given: the first listing is not a change
        start = service.wait_for_start(ROM.device, self.answers_after(99), self.lines.append, timeout_s=2)
        self.assertEqual((start.code, start.port, self.asked), ("download_mode_stayed", MICROPYTHON.device, []))


if __name__ == "__main__":
    unittest.main()
