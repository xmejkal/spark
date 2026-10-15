"""P219 step 2 (#201): board_look.py reads a board on USB and compares it with its record, and changes nothing on it."""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_look  # noqa: E402
import image_check  # noqa: E402
import outcomes  # noqa: E402
import tools  # noqa: E402
from test_deploy import FOUND, PORT, ProjectCase, found  # noqa: E402

#: The C6 and the mpremote lines are P228's bench outputs, trimmed. The S3, classic ESP32, KB and CH340 files are
#: written by hand, as tests/data/board_look/README.md says: no such board was on the bench.
DATA = Path(__file__).resolve().parent / "data" / "board_look"
C6_PORT = "/dev/cu.usbmodem101"


def data(name):
    return (DATA / name).read_text()


def done(text, code=0):
    return subprocess.CompletedProcess([], code, text, "")


class LookCase(ProjectCase):
    """A project on the C6 whose image passed, and a fake `run` that answers mpremote devs and esptool from fixtures."""

    def setUp(self):
        super().setUp()
        self.board("xiao-esp32-c6")
        self.ran = []

    def board(self, name):
        (self.project / "requirements.json").write_text(json.dumps({"board": name, "parts": []}))

    def look(self, devs="mpremote-devs-one.txt", esptool="c6-flash-id.txt", port=None, flasher=None, esptool_code=0,
             text=None, **kwargs):
        """The Report of Look.run with fake tools. `text` is what esptool prints, in place of the file. LookStop propagates."""
        def run(argv, **kw):
            self.ran.append(argv)
            if "devs" in argv:
                return done(data(devs))
            return done(text or data(esptool), esptool_code)

        flasher = flasher or FOUND["flasher"]
        with mock.patch.object(tools, "find", side_effect=lambda name, *a, **k: flasher if name == "flasher" else found(name)):
            return board_look.looker(self.project, run).run(self.project, port, **kwargs)


class PortFinderTest(LookCase):
    def test_one_board(self):
        report = self.look()
        self.assertEqual(report.port, C6_PORT)

    def test_bluetooth_and_debug_console_rows_are_dropped(self):
        shell = FOUND["board-shell"]
        ports = board_look.PortFinder(shell, lambda argv, **kw: done(data("mpremote-devs-with-bluetooth.txt"))).boards()
        self.assertEqual([p.device for p in ports], [C6_PORT])
        self.assertEqual(ports[0].usb, "303a:1001")

    def test_a_ch340_board_is_kept_and_its_product_has_spaces(self):
        ports = board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: done(data("mpremote-devs-two.txt"))).boards()
        self.assertEqual([(p.device, p.serial, p.product) for p in ports],
                         [(C6_PORT, "8c:bf:ea:xx:xx:xx", "Espressif USB JTAG/serial debug unit"),
                          ("/dev/cu.usbserial-1410", "None", "USB Serial")])

    def test_a_failed_mpremote_stops_with_the_last_line_of_its_stderr(self):
        failed = subprocess.CompletedProcess([], 1, "", "Traceback\nmpremote: no such command\n")
        with self.assertRaises(board_look.LookStop) as stop:
            board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: failed).boards()
        self.assertEqual(str(stop.exception), "could not list the boards on USB: mpremote: no such command")

    def test_one_port_is_required_and_the_stop_names_the_script_that_asked(self):
        none = board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: done(""))
        with self.assertRaises(board_look.LookStop) as stop:
            none.require_one_port("reach.py")
        self.assertTrue(str(stop.exception).startswith("no board found."))
        two = board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: done(data("mpremote-devs-two.txt")))
        with self.assertRaises(board_look.LookStop) as stop:
            two.require_one_port("reach.py")
        self.assertIn("2 boards on USB:", str(stop.exception))
        self.assertIn("reach.py --port %s  (unplug one" % C6_PORT, str(stop.exception))
        one = board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: done(data("mpremote-devs-with-bluetooth.txt")))
        self.assertEqual(one.require_one_port("reach.py"), C6_PORT)

    def test_both_commands_have_a_timeout_and_a_timeout_stops_with_the_boot_hint(self):
        seen = []
        self.look()
        board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: seen.append(kw["timeout"]) or done("")).boards()
        board_look.EsptoolReader(FOUND["flasher"], lambda argv, **kw: seen.append(kw["timeout"]) or done(data("c6-flash-id.txt"))).read(C6_PORT)
        self.assertEqual(seen, [15, 60])

        def stalled(argv, **kw):
            raise subprocess.TimeoutExpired(argv, kw["timeout"])
        for call in (lambda: board_look.PortFinder(FOUND["board-shell"], stalled).boards(),
                     lambda: board_look.EsptoolReader(FOUND["flasher"], stalled).read(C6_PORT)):
            with self.assertRaises(board_look.LookStop) as stop:
                call()
            self.assertIn("took more than", str(stop.exception))
            self.assertIn("BOOT", str(stop.exception))

    def test_two_boards_and_no_port_stops_listing_both_and_reads_neither(self):
        with self.assertRaises(board_look.LookStop) as stop:
            self.look(devs="mpremote-devs-two.txt")
        said = str(stop.exception)
        for part in (C6_PORT, "8c:bf:ea:xx:xx:xx", "/dev/cu.usbserial-1410", "look.py --port", "unplug one",
                     "Espressif USB JTAG/serial debug unit", "USB Serial"):
            self.assertIn(part, said)
        self.assertFalse([a for a in self.ran if "flash_id" in a])

    def test_two_boards_with_a_port_reads_that_one_without_listing(self):
        report = self.look(devs="mpremote-devs-two.txt", port="/dev/cu.usbserial-1410")
        self.assertEqual(report.port, "/dev/cu.usbserial-1410")
        self.assertFalse([a for a in self.ran if "devs" in a])

    def test_no_board(self):
        with self.assertRaises(board_look.LookStop) as stop:
            self.look(devs="mpremote-devs-none.txt")
        self.assertIn("no board found", str(stop.exception))

    def test_nothing_ever_runs_code_on_the_board(self):
        self.look()
        self.assertTrue(self.ran)
        self.assertFalse([a for a in self.ran if "exec" in a or "run" in a or "repl" in a])


class EsptoolReaderTest(unittest.TestCase):
    def read(self, name, code=0):
        return board_look.EsptoolReader(FOUND["flasher"], lambda argv, **kw: done(data(name), code)).read(C6_PORT)

    def test_the_c6_reading_with_its_six_byte_base_mac(self):
        self.assertEqual(self.read("c6-flash-id.txt"), board_look.Reading("esp32c6", 4, "8c:bf:ea:xx:xx:xx"))

    def test_a_classic_esp32_has_two_detecting_lines_and_the_last_one_counts(self):
        reading = self.read("esp32-classic-flash-id.txt")
        self.assertEqual((reading.chip, reading.mac), ("esp32", "24:6f:28:xx:xx:xx"))

    def test_the_s3(self):
        self.assertEqual(self.read("s3-flash-id-16mb.txt"), board_look.Reading("esp32s3", 16, "dc:da:0c:xx:xx:xx"))

    def test_a_flash_size_in_kb(self):
        self.assertEqual(self.read("c6-flash-id-kb.txt").flash_mb, 4)

    def test_a_field_it_cannot_parse_is_none(self):
        self.assertEqual(self.read("c6-flash-id-garbled.txt"), board_look.Reading("esp32c6", None, "8c:bf:ea:xx:xx:xx"))
        self.assertIsNone(self.read("c6-flash-id-no-mac.txt").mac)

    def test_any_non_zero_exit_raises(self):
        with self.assertRaises(board_look.LookStop) as stop:
            self.read("wrong-chip.txt", code=2)
        self.assertIn("could not read the board on %s" % C6_PORT, str(stop.exception))
        self.assertIn("BOOT", str(stop.exception))

    def test_two_different_detecting_lines_and_the_last_wins(self):
        for first in ("Autodetection failed, trying again...", "ESP32"):
            text = "Detecting chip type... %s\nDetecting chip type... ESP32-S3\nBASE MAC: aa:bb:cc:dd:ee:ff\n" % first
            reading = board_look.EsptoolReader(FOUND["flasher"], lambda argv, **kw: done(text)).read(C6_PORT)
            self.assertEqual(reading.chip, "esp32s3", first)

    def test_it_runs_flash_id_with_the_underscore_on_the_port(self):
        ran = []
        board_look.EsptoolReader(FOUND["flasher"], lambda argv, **kw: ran.append(argv) or done(data("c6-flash-id.txt"))).read(C6_PORT)
        self.assertEqual(ran, [["/opt/python3", "-m", "esptool", "--port", C6_PORT, "flash_id"]])

    def test_another_flasher_than_esptool_is_not_read(self):
        other = tools.Tool("probe-rs", "flasher", {"kind": "binary"}, ["/opt/probe-rs"])
        with self.assertRaises(board_look.LookStop) as stop:
            board_look.EsptoolReader(other, lambda argv, **kw: done("")).read(C6_PORT)
        self.assertIn("the look reads only esptool", str(stop.exception))


class CompareTest(unittest.TestCase):
    RECORD = {"chip": "esp32s3", "flash_mb": [16, 4]}

    def test_each_field_is_same_differs_or_unknown(self):
        compare = board_look.compare
        self.assertEqual(compare(board_look.Reading("esp32s3", 4, "m"), self.RECORD), {"chip": "same", "flash": "same"})
        self.assertEqual(compare(board_look.Reading("esp32c6", 8, "m"), self.RECORD), {"chip": "differs", "flash": "differs"})
        self.assertEqual(compare(board_look.Reading(None, None, None), self.RECORD), {"chip": "unknown", "flash": "unknown"})

    def test_a_record_without_flash_is_unknown_and_a_single_number_works(self):
        self.assertEqual(board_look.compare(board_look.Reading("esp32c6", 4, "m"), {"chip": "esp32c6"})["flash"], "unknown")
        self.assertEqual(board_look.compare(board_look.Reading("esp32c6", 4, "m"), {"chip": "esp32c6", "flash_mb": 4})["flash"], "same")


class LookTest(LookCase):
    def test_a_matching_board_passes_with_a_token(self):
        self.run_the_scenario()
        report = self.look()
        self.assertEqual((report.verdict, report.status), ("match", outcomes.OK))
        self.assertEqual(report.fields, {"chip": "same", "flash": "same"})
        self.assertRegex(report.token(), r"^[0-9a-f]{4}-[0-9a-f]{4}$")

    def test_the_token_is_the_mac_half_and_the_image_half_not_the_port(self):
        import hashlib
        self.run_the_scenario()
        token = self.look().token()
        self.assertEqual(token, "%s-%s" % (hashlib.sha256(b"8c:bf:ea:xx:xx:xx").hexdigest()[:4],
                                           hashlib.sha256(self.image.read_bytes()).hexdigest()[:4]))
        self.assertEqual(self.look(port="/dev/cu.usbmodem999").token(), token)

    def test_another_image_changes_only_the_second_half(self):
        self.run_the_scenario()
        first = self.look().token()
        (self.project / "firmware" / "main.py").write_text("print('ready')\nprint(2)\n")
        self.run_the_scenario()
        second = self.look().token()
        self.assertEqual(first.split("-")[0], second.split("-")[0])
        self.assertNotEqual(first.split("-")[1], second.split("-")[1])

    def test_another_chip_is_a_stop_with_no_token(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        report = self.look()
        self.assertEqual((report.verdict, report.status), ("stop", outcomes.PROBLEMS))
        self.assertIn("this board is an esp32c6, the project is for an esp32s3", report.stops[0])
        self.assertIsNone(report.token())

    def test_a_flash_that_differs_but_holds_the_image_is_a_warning_and_keeps_its_token(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        report = self.look(esptool="s3-flash-id-8mb.txt")
        self.assertEqual((report.verdict, report.status, report.fields["flash"]), ("warning", outcomes.PROBLEMS, "differs"))
        self.assertIn("the flash differs: 8 MB, the record says 16 or 4", report.warnings[0])
        self.assertIsNotNone(report.token())

    def test_a_flash_smaller_than_the_image_is_a_stop(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        report = self.look(esptool="s3-flash-id-2mb.txt")
        self.assertEqual(report.verdict, "stop")
        self.assertEqual(report.stops, ["the flash is 2 MB, the image needs 4 MB"])
        self.assertIsNone(report.token())

    def fit(self, record, megabytes, extra):
        """The Report for a 4 MB image plus `extra` bytes on a board that says `megabytes` MB."""
        self.run_the_scenario()
        self.board(record)
        self.image.write_bytes(self.image.read_bytes() + b"x" * extra)
        text = data("s3-flash-id-16mb.txt").replace("16MB", "%dMB" % megabytes)
        return self.look(text=text)

    def test_the_fit_check_runs_when_the_flash_is_in_the_records_list(self):
        report = self.fit("firebeetle2-esp32s3", 4, 1)  # the record says [16, 4], the board 4: same, yet too small
        self.assertEqual((report.fields["flash"], report.stops), ("same", ["the flash is 4 MB, the image needs 5 MB"]))
        self.assertIsNone(report.token())
        self.assertEqual((report.status, report.exit_code()), (outcomes.PROBLEMS, outcomes.EXIT_PROBLEMS))

    def test_a_match_with_no_token_went_unchecked(self):
        report = self.look()  # no scenario run, so no passed run names the image
        self.assertEqual((report.verdict, report.token()), ("match", None))
        self.assertEqual((report.status, report.exit_code()), (outcomes.COULD_NOT_RUN, outcomes.EXIT_COULD_NOT_RUN))

    def test_an_image_of_exactly_the_flash_read_fits(self):
        report = self.fit("firebeetle2-esp32s3", 4, 0)
        self.assertEqual((report.verdict, report.stops), ("match", []))

    def test_one_byte_over_one_megabyte_does_not_fit_a_one_megabyte_flash(self):
        self.run_the_scenario()
        self.image.write_bytes(b"x" * (1024 * 1024 + 1))
        report = self.look(text=data("c6-flash-id.txt").replace("4MB", "1MB"))
        self.assertEqual(report.stops, ["the flash is 1 MB, the image needs 2 MB"])

    def test_a_field_it_cannot_read_is_a_warning_and_unchecked(self):
        self.run_the_scenario()
        report = self.look(esptool="c6-flash-id-garbled.txt")
        self.assertEqual((report.verdict, report.status, report.fields["flash"]), ("warning", outcomes.COULD_NOT_RUN, "unknown"))
        self.assertEqual((report.unknown, report.warnings), ({"flash": "the board did not say"}, []))

    def test_no_mac_means_no_token_and_says_why(self):
        self.run_the_scenario()
        report = self.look(esptool="c6-flash-id-no-mac.txt")
        self.assertIsNone(report.token())
        self.assertIn("MAC", report.no_token_reason())

    def test_no_image_means_no_token_and_says_why(self):
        report = self.look()
        self.assertIsNone(report.token())
        self.assertIn("run a scenario first", report.no_token_reason())
        self.assertEqual(report.fields, {"chip": "same", "flash": "same"})

    def test_an_image_no_passed_run_names_means_no_token(self):
        self.run_the_scenario()
        self.image.write_bytes(b"x" + self.image.read_bytes()[1:])  # the same size: the fit check is not in play
        report = self.look()
        self.assertIsNone(report.token())
        self.assertIn("no run in sim/runs/ tested", report.no_token_reason())

    def test_a_log_that_tested_another_image_means_no_token_unless_told_to_ignore_it(self):
        self.run_the_scenario()
        runs = self.project / "sim" / "runs"
        (runs / "old.log").write_text("# old.scenario.yaml, run 2026-10-01\nverdict: passed\nimage sha256: 0\n\nbody\n")
        report = self.look()
        self.assertIsNone(report.token())
        self.assertIn("old.log tested another image", report.no_token_reason())
        self.assertIsNotNone(self.look(ignore_older_runs=True).token())

    def test_a_log_that_cannot_be_read_still_lets_the_fit_check_run(self):
        self.run_the_scenario()
        self.image.write_bytes(self.image.read_bytes() + b"x")  # 4 MB + 1 byte on a 4 MB flash
        with mock.patch.object(image_check.run_scenario, "run_record", side_effect=OSError("denied")):
            report = self.look()
        self.assertEqual(report.stops, ["the flash is 4 MB, the image needs 5 MB"])
        self.assertIn("cannot read", report.image_why)

    def test_a_record_without_flash_says_the_record_does_not_hold_it_and_a_silent_board_says_so(self):
        self.run_the_scenario()
        with mock.patch.object(board_look.boards, "load", return_value={"chip": "esp32c6"}):
            self.assertEqual(self.look().unknown, {"flash": "the record does not hold it"})
        self.assertEqual(self.look(esptool="c6-flash-id-garbled.txt").unknown, {"flash": "the board did not say"})

    def test_requirements_missing_or_naming_no_board_stops_without_a_name_of_none(self):
        (self.project / "requirements.json").write_text(json.dumps({"parts": []}))
        for _ in range(2):
            with self.assertRaises(board_look.LookStop) as stop:
                self.look()
            self.assertEqual(str(stop.exception), "requirements.json names no board")
            (self.project / "requirements.json").unlink(missing_ok=True)

    def test_a_board_with_no_record_stops_and_points_to_p230(self):
        self.board("no-such-board")
        with self.assertRaises(board_look.LookStop) as stop:
            self.look()
        self.assertIn("no board record for no-such-board: P230 will research one.", str(stop.exception))

    def test_another_flasher_stops_the_look(self):
        other = tools.Tool("probe-rs", "flasher", {"kind": "binary"}, ["/opt/probe-rs"])
        with self.assertRaises(board_look.LookStop) as stop:
            self.look(flasher=other)
        self.assertIn("the look reads only esptool", str(stop.exception))


class TheRecordsTest(unittest.TestCase):
    def test_both_library_records_carry_their_flash(self):
        import boards
        self.assertEqual(boards.load(ROOT, "xiao-esp32-c6")["flash_mb"], 4)
        self.assertEqual(boards.load(ROOT, "firebeetle2-esp32s3")["flash_mb"], [16, 4])


if __name__ == "__main__":
    unittest.main()
