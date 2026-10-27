"""P219 step 2 (#201): board_look.py reads a board on USB and compares it with its record, and changes nothing on it."""

import json
import os
import shutil
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

import board_facts  # noqa: E402
from fakes import pin_time_zone  # noqa: E402
import board_look  # noqa: E402
import project_image  # noqa: E402
import outcomes  # noqa: E402
import image_evidence  # noqa: E402
import tools  # noqa: E402
from test_deploy import FOUND, ProjectCase, found  # noqa: E402

#: The C6 and the mpremote lines are P228's bench outputs, trimmed. The S3, classic ESP32, KB and CH340 files are
#: written by hand, as tests/data/board_look/README.md says: no such board was on the bench.
DATA = Path(__file__).resolve().parent / "data" / "board_look"
C6_PORT = "/dev/cu.usbmodem101"
C6_MAC = "8c:bf:ea:xx:xx:xx"
#: What the look says when the store holds no deploy of the board (P401).
NONE_RECORDED_LINE = "spark's last deploy here: none in its store record (it keeps only its own deploys)"
#: What the passed run of test_deploy's scenario (one wait-serial step, no input, no pin) says before the gate question (P345).
NO_CONTROL_NO_PIN = ("the passed run's scenario has no set-control step (the step that presses a button or sets a sensor) "
                     "and no expect-pin step (the step that reads a pin)")
#: A scenario that presses a button and reads a pin: its passed run has no caveat.
CONTROLLED_SCENARIO = ("name: s\nversion: 1\nsteps:\n  - set-control: { part-id: b, name: pressed, value: 1 }\n"
                       "  - expect-pin: { part-id: led, pin: A, value: 1 }\n")


def data(name):
    return (DATA / name).read_text()


def done(text, code=0):
    return subprocess.CompletedProcess([], code, text, "")


class LookCase(ProjectCase):
    """A project on the C6 whose image passed, and a fake `run` that answers mpremote devs and esptool from fixtures."""

    def setUp(self):
        super().setUp()
        home = Path(tempfile.mkdtemp())  # a store of its own: the suite's one scratch store holds what other tests recorded (P401)
        env = mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})
        env.start()
        self.addCleanup(env.stop)
        self.addCleanup(shutil.rmtree, home, True)
        pin_time_zone(self)  # a stored time is said in the machine's zone: one zone on every machine
        self.board("xiao-esp32-c6")
        self.ran = []

    def record_a_deploy(self, project="blink-c6", verdict="ready seen"):
        """A deploy of this look's board in the store, as record_deploy writes it."""
        board_facts.record_deploy({"mac": C6_MAC, "project": project, "board": "xiao-esp32-c6", "image_sha256": "0",
                                   "simulation": "passed", "deployed": "2026-10-19T09:24:50+02:00"}, verdict, "a test")

    def board(self, name):
        (self.project / "requirements.json").write_text(json.dumps({"board": name, "parts": []}))

    def look(self, devs="mpremote-devs-one.txt", esptool="c6-flash-id.txt", port=None, flasher=None, esptool_code=0,
             text=None, ignore_older_runs=False, evidence=None):
        """The LookReport of LookService.run with fake tools. `text` is what esptool prints, in place of the file. LookStop propagates."""
        def run(argv, **kw):
            self.ran.append(argv)
            if "devs" in argv:
                return done(data(devs))
            return done(text or data(esptool), esptool_code)

        flasher = flasher or FOUND["flasher"]
        with mock.patch.object(tools, "find", side_effect=lambda name, *a, **k: flasher if name == "flasher" else found(name)):
            return board_look.looker(self.project, run).run(self.project, port, evidence or image_evidence.PassedRunEvidence(ignore_older_runs))


class PortFinderTest(LookCase):
    def test_one_board(self):
        report = self.look()
        self.assertEqual(report.port, C6_PORT)

    def test_bluetooth_and_debug_console_rows_are_dropped(self):
        shell = FOUND["board-shell"]
        ports = board_look.PortFinder(shell, lambda argv, **kw: done(data("mpremote-devs-with-bluetooth.txt"))).nodes()
        self.assertEqual([p.device for p in ports], [C6_PORT])
        self.assertEqual(ports[0].usb, "303a:1001")

    def test_a_ch340_board_is_kept_and_its_product_has_spaces(self):
        ports = board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: done(data("mpremote-devs-two.txt"))).nodes()
        self.assertEqual([(p.device, p.serial, p.product) for p in ports],
                         [(C6_PORT, "8c:bf:ea:xx:xx:xx", "Espressif USB JTAG/serial debug unit"),
                          ("/dev/cu.usbserial-1410", "None", "USB Serial")])

    def test_a_failed_mpremote_stops_with_the_last_line_of_its_stderr(self):
        failed = subprocess.CompletedProcess([], 1, "", "Traceback\nmpremote: no such command\n")
        with self.assertRaises(board_look.LookStop) as stop:
            board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: failed).nodes()
        self.assertEqual(str(stop.exception), "could not list the boards on USB: mpremote: no such command")
        self.assertEqual(stop.exception.reason, "list_failed")

    def test_an_mpremote_that_cannot_start_stops_the_listing_and_an_unlisted_port_stops_the_look(self):
        def cannot_start(argv, **kw):
            raise OSError("no such file")
        with self.assertRaises(board_look.LookStop) as stop:
            board_look.PortFinder(FOUND["board-shell"], cannot_start).nodes()
        self.assertEqual(stop.exception.reason, "list_failed")
        listing = board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: done(data("mpremote-devs-one.txt")))
        with self.assertRaises(board_look.LookStop) as stop:
            listing.require_one_board("look.py", "/dev/cu.not-listed")
        self.assertEqual((str(stop.exception), stop.exception.reason),
                         ("no board on /dev/cu.not-listed: mpremote devs does not list it.", "port_not_listed"))

    def test_one_port_is_required_and_the_stop_names_the_script_that_asked(self):
        none = board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: done(""))
        with self.assertRaises(board_look.LookStop) as stop:
            none.require_one_port("reach.py")
        self.assertTrue(str(stop.exception).startswith("no board found."))
        self.assertEqual(stop.exception.reason, "no_port")
        two = board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: done(data("mpremote-devs-two.txt")))
        with self.assertRaises(board_look.LookStop) as stop:
            two.require_one_port("reach.py")
        self.assertIn("2 boards on USB:", str(stop.exception))
        self.assertEqual(stop.exception.reason, "two_boards")
        self.assertIn("reach.py --port %s  (unplug one" % C6_PORT, str(stop.exception))
        one = board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: done(data("mpremote-devs-with-bluetooth.txt")))
        self.assertEqual(one.require_one_port("reach.py"), C6_PORT)

    def test_both_commands_have_a_timeout_and_a_timeout_stops_with_the_boot_hint(self):
        seen = []
        self.look()
        board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: seen.append(kw["timeout"]) or done("")).nodes()
        board_look.EsptoolReader(FOUND["flasher"], lambda argv, **kw: seen.append(kw["timeout"]) or done(data("c6-flash-id.txt"))).read(C6_PORT)
        self.assertEqual(seen, [15, 60])

        def stalled(argv, **kw):
            raise subprocess.TimeoutExpired(argv, kw["timeout"])
        for call, reason in ((lambda: board_look.PortFinder(FOUND["board-shell"], stalled).nodes(), "list_timeout"),
                             (lambda: board_look.EsptoolReader(FOUND["flasher"], stalled).read(C6_PORT), "read_timeout")):
            with self.assertRaises(board_look.LookStop) as stop:
                call()
            self.assertEqual(stop.exception.reason, reason)
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
        self.assertIn("If the plug is USB-C, turn it around, or use a USB-A to USB-C cable.", str(stop.exception))

    def test_one_board_on_two_ports_is_one_board_on_the_port_that_holds_its_serial(self):
        report = self.look(devs="mpremote-devs-one-board-two-ports.txt")
        self.assertEqual((report.port, report.also_on), ("/dev/cu.usbserial-01A2B3C4", ("/dev/cu.SLAB_USBtoUART",)))

    def test_a_grouped_board_listed_second_by_its_serial_is_used_on_that_node_and_the_stop_lists_the_other(self):
        finder = board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: done(data("mpremote-devs-grouped-and-two-without-serial.txt")))
        with self.assertRaises(board_look.LookStop) as stop:
            finder.require_one_port("look.py")
        said = str(stop.exception)
        self.assertIn("3 boards on USB:", said)
        self.assertIn("  /dev/cu.usbserial-01A2B3C4  01A2B3C4  Silicon Labs CP2104 USB to UART Bridge Controller  (also /dev/cu.SLAB_USBtoUART)", said)
        self.assertIn("  /dev/cu.usbserial-1410  None  USB Serial\n  /dev/cu.usbserial-1420  None  USB Serial", said)
        self.assertIn("look.py --port /dev/cu.usbserial-01A2B3C4  (unplug one", said)

    def test_two_ports_with_no_serial_stay_two_boards(self):
        for serial in ("None", ""):
            with self.subTest(serial=serial):
                ports = [board_look.Port(device, serial, "1a86:7523", "USB Serial") for device in ("/dev/cu.a", "/dev/cu.usbserial-None")]
                self.assertEqual([[port.device for port in board] for board in board_look.boards_of(ports)],
                                 [["/dev/cu.a"], ["/dev/cu.usbserial-None"]])

    def test_a_port_named_by_the_person_is_found_on_either_node_of_a_grouped_board(self):
        finder = board_look.PortFinder(FOUND["board-shell"], lambda argv, **kw: done(data("mpremote-devs-one-board-two-ports.txt")))
        named = finder.require_one_board("look.py", "/dev/cu.SLAB_USBtoUART")
        self.assertEqual((named.device, named.also_on), ("/dev/cu.SLAB_USBtoUART", ()))
        report = self.look(devs="mpremote-devs-one-board-two-ports.txt", port="/dev/cu.SLAB_USBtoUART")
        self.assertIsNone(report.to_dict()["also_on"])

    def test_two_clones_with_one_serial_and_no_node_named_by_it_stay_two_boards(self):
        clones = [board_look.Port(device, "0001", "10c4:ea60", "Silicon Labs CP2102 USB to UART Bridge Controller")
                  for device in ("/dev/ttyUSB0", "/dev/ttyUSB1")]
        self.assertEqual([[port.device for port in board] for board in board_look.boards_of(clones)],
                         [["/dev/ttyUSB0"], ["/dev/ttyUSB1"]])

    def test_one_serial_with_another_usb_id_or_product_or_a_name_that_only_holds_it_stays_two_boards(self):
        slab = board_look.Port("/dev/cu.SLAB_USBtoUART", "01A2B3C4", "10c4:ea60", "Silicon Labs CP2104 USB to UART Bridge Controller")
        for other in (slab._replace(device="/dev/cu.usbserial-01A2B3C4", usb="1a86:7523"),
                      slab._replace(device="/dev/cu.usbserial-01A2B3C4", product="Silicon Labs CP2102 USB to UART Bridge Controller"),
                      slab._replace(device="/dev/cu.usbserial-01A2B3C40")):
            with self.subTest(other=other):
                self.assertEqual(len(board_look.boards_of([slab, other])), 2)

    def test_the_look_says_the_other_node_and_to_unplug_one_if_they_are_two_boards(self):
        lines = board_look.report_lines(self.look(devs="mpremote-devs-one-board-two-ports.txt"))
        self.assertIn("  port   /dev/cu.usbserial-01A2B3C4  (one board on more nodes, also /dev/cu.SLAB_USBtoUART: the same USB "
                      "serial. If these are two boards, unplug one)", lines)

    def test_nothing_ever_runs_code_on_the_board(self):
        self.look()
        self.assertTrue(self.ran)
        self.assertFalse([a for a in self.ran if "exec" in a or "run" in a or "repl" in a])


class EsptoolReaderTest(unittest.TestCase):
    def read(self, name, code=0):
        return board_look.EsptoolReader(FOUND["flasher"], lambda argv, **kw: done(data(name), code)).read(C6_PORT)

    def test_the_c6_reading_with_its_six_byte_base_mac(self):
        self.assertEqual(self.read("c6-flash-id.txt"), board_look.BoardReading("esp32c6", 4, "8c:bf:ea:xx:xx:xx"))

    def test_a_classic_esp32_has_two_detecting_lines_and_the_last_one_counts(self):
        reading = self.read("esp32-classic-flash-id.txt")
        self.assertEqual((reading.chip, reading.mac), ("esp32", "24:6f:28:xx:xx:xx"))

    def test_the_s3(self):
        self.assertEqual(self.read("s3-flash-id-16mb.txt"), board_look.BoardReading("esp32s3", 16, "dc:da:0c:xx:xx:xx"))

    def test_a_flash_size_in_kb(self):
        self.assertEqual(self.read("c6-flash-id-kb.txt").flash_mb, 4)

    def test_a_field_it_cannot_parse_is_none(self):
        self.assertEqual(self.read("c6-flash-id-garbled.txt"), board_look.BoardReading("esp32c6", None, "8c:bf:ea:xx:xx:xx"))
        self.assertIsNone(self.read("c6-flash-id-no-mac.txt").mac)

    def test_any_non_zero_exit_raises(self):
        with self.assertRaises(board_look.LookStop) as stop:
            self.read("wrong-chip.txt", code=2)
        self.assertIn("could not read the board on %s" % C6_PORT, str(stop.exception))
        self.assertIn("BOOT", str(stop.exception))
        self.assertEqual(stop.exception.reason, "board_not_read")

    def test_an_esptool_that_cannot_start_stops_the_read(self):
        def cannot_start(argv, **kw):
            raise OSError("no such file")
        with self.assertRaises(board_look.LookStop) as stop:
            board_look.EsptoolReader(FOUND["flasher"], cannot_start).read(C6_PORT)
        self.assertEqual((stop.exception.port, stop.exception.reason), (C6_PORT, "board_not_read"))

    def test_a_failed_read_keeps_the_port_and_esptool_s_own_line_not_its_url(self):
        stderr = ("ERROR: A fatal error occurred: Failed to connect to Espressif device: No serial data received.\n"
                  "For troubleshooting steps visit: https://docs.espressif.com/projects/esptool/en/latest/troubleshooting.html\n")
        def failed(argv, **kw):
            return subprocess.CompletedProcess([], 2, "Connecting......\n", stderr)

        with self.assertRaises(board_look.LookStop) as stop:
            board_look.EsptoolReader(FOUND["flasher"], failed).read(C6_PORT)
        self.assertEqual((stop.exception.port, stop.exception.tool_said), (C6_PORT, (
            "ERROR: A fatal error occurred: Failed to connect to Espressif device: No serial data received.")))

    def test_esptool_s_line_is_the_first_error_line_stripped_and_none_without_one(self):
        stderr = "ERROR: the first\nERROR: the second\nFor troubleshooting steps visit: https://docs.espressif.com\n"
        self.assertEqual(board_look.esptool_said(stderr), "ERROR: the first")
        self.assertIsNone(board_look.esptool_said(None))
        self.assertIsNone(board_look.esptool_said("Connecting......\nHint: check the port\n"))

    def test_a_failed_read_with_no_error_line_says_nothing_for_esptool(self):
        with self.assertRaises(board_look.LookStop) as stop:
            self.read("wrong-chip.txt", code=2)
        self.assertIsNone(stop.exception.tool_said)

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
        self.assertEqual(stop.exception.reason, "flasher_not_esptool")


class CompareTest(unittest.TestCase):
    RECORD = {"chip": "esp32s3", "flash_mb": [16, 4]}

    def test_each_field_is_same_differs_or_unknown(self):
        compare = board_look.compare
        self.assertEqual(compare(board_look.BoardReading("esp32s3", 4, "m"), self.RECORD), {"chip": "same", "flash": "same"})
        self.assertEqual(compare(board_look.BoardReading("esp32c6", 8, "m"), self.RECORD), {"chip": "differs", "flash": "differs"})
        self.assertEqual(compare(board_look.BoardReading(None, None, None), self.RECORD), {"chip": "unknown", "flash": "unknown"})

    def test_a_record_without_flash_is_unknown_and_a_single_number_works(self):
        self.assertEqual(board_look.compare(board_look.BoardReading("esp32c6", 4, "m"), {"chip": "esp32c6"})["flash"], "unknown")
        self.assertEqual(board_look.compare(board_look.BoardReading("esp32c6", 4, "m"), {"chip": "esp32c6", "flash_mb": 4})["flash"], "same")


class LookNamesTheButtonsTest(LookCase):
    PLACES = "hold the board's BOOT button (B, top right, beside the USB-C), press and release RESET (R, top left, beside the USB-C)"

    def test_a_failed_read_on_the_xiao_names_where_the_buttons_are(self):
        with self.assertRaises(board_look.LookStop) as stop:
            self.look(esptool_code=2)
        self.assertIn(self.PLACES, str(stop.exception))
        self.assertTrue(str(stop.exception).endswith("Left and right as seen with the metal shield facing you, USB-C at the top"))

    def test_a_failed_read_on_a_record_without_buttons_says_the_plain_words(self):
        self.board("firebeetle2-esp32s3")
        with self.assertRaises(board_look.LookStop) as stop:
            self.look(esptool_code=2)
        self.assertIn("hold the board's BOOT button, press and release RESET, release BOOT", str(stop.exception))
        self.assertNotIn("Left and right", str(stop.exception))


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
        self.assertEqual(report.stops, [board_look.Stop("chip_differs", "this board is an esp32c6, the project is for an esp32s3")])
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
        self.assertEqual(report.stops, [board_look.Stop("flash_too_small", "the flash is 2 MB, the image needs 4 MB")])
        self.assertIsNone(report.token())

    def fit(self, record, megabytes, extra):
        """The LookReport for a 4 MB image plus `extra` bytes on a board that says `megabytes` MB."""
        self.run_the_scenario()
        self.board(record)
        self.image.write_bytes(self.image.read_bytes() + b"x" * extra)
        text = data("s3-flash-id-16mb.txt").replace("16MB", "%dMB" % megabytes)
        return self.look(text=text)

    def test_the_fit_check_runs_when_the_flash_is_in_the_records_list(self):
        report = self.fit("firebeetle2-esp32s3", 4, 1)  # the record says [16, 4], the board 4: same, yet too small
        self.assertEqual((report.fields["flash"], report.stops), ("same", [board_look.Stop("flash_too_small", "the flash is 4 MB, the image needs 5 MB")]))
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
        self.assertEqual(report.stops, [board_look.Stop("flash_too_small", "the flash is 1 MB, the image needs 2 MB")])

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
        with mock.patch.object(project_image.run_scenario, "run_record", side_effect=OSError("denied")):
            report = self.look()
        self.assertEqual(report.stops, [board_look.Stop("flash_too_small", "the flash is 4 MB, the image needs 5 MB")])
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
            self.assertEqual((str(stop.exception), stop.exception.reason), ("requirements.json names no board", "no_board_named"))
            (self.project / "requirements.json").unlink(missing_ok=True)

    def test_a_board_with_no_record_stops_and_points_to_p230(self):
        self.board("no-such-board")
        with self.assertRaises(board_look.LookStop) as stop:
            self.look()
        self.assertIn("no board record for no-such-board: P230 will research one.", str(stop.exception))
        self.assertEqual(stop.exception.reason, "no_board_record")

    def test_a_tool_that_cannot_be_used_stops_the_look_with_its_sentence(self):
        with mock.patch.object(tools, "find", side_effect=tools.ToolProblem("mpremote is not installed")), \
                self.assertRaises(board_look.LookStop) as stop:
            board_look.looker(self.project)
        self.assertEqual((str(stop.exception), stop.exception.reason), ("mpremote is not installed", "tool_missing"))

    def test_another_flasher_stops_the_look(self):
        other = tools.Tool("probe-rs", "flasher", {"kind": "binary"}, ["/opt/probe-rs"])
        with self.assertRaises(board_look.LookStop) as stop:
            self.look(flasher=other)
        self.assertIn("the look reads only esptool", str(stop.exception))


class LookReportToDictTest(LookCase):
    """P239 PR 6: the facts of a look as plain values, for the --json of P213. Nothing prints them yet."""

    def test_a_match_with_a_token(self):
        self.run_the_scenario()
        report = self.look()
        as_dict = report.to_dict()
        self.assertEqual(as_dict, {
            "port": C6_PORT, "also_on": [], "chip": "esp32c6", "flash_mb": 4, "mac": C6_MAC, "board": "xiao-esp32-c6",
            "fields": {"chip": "same", "flash": "same"}, "stops": [], "warnings": [], "unknown": {},
            "verdict": "match", "status": outcomes.OK, "token": report.token(), "no_token_reason": None,
            # LookCase's scenario only waits for text (the P345 caveat), so the passed run did not press anything
            "simulation": "passed", "caveats": [NO_CONTROL_NO_PIN],
            "last_deploy": {"state": "none-recorded", "why": None, "project": None, "verdict": None, "deployed": None}})
        self.assertIsNotNone(as_dict["token"])
        json.dumps(as_dict)

    def test_a_stop_has_no_token_and_says_why(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        as_dict = self.look().to_dict()
        self.assertEqual((as_dict["verdict"], as_dict["status"], as_dict["token"], as_dict["no_token_reason"]),
                         ("stop", outcomes.PROBLEMS, None, "the look found a stop"))
        self.assertEqual(as_dict["stops"], ["this board is an esp32c6, the project is for an esp32s3"])  # sentences only
        json.dumps(as_dict)

    def test_changing_the_dict_leaves_the_report_alone(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        report = self.look()
        as_dict = report.to_dict()
        as_dict["stops"].clear()
        as_dict["fields"].clear()
        self.assertEqual((len(report.stops), len(report.fields)), (1, 2))

    def test_an_unknown_field_with_no_scenario_run(self):
        report = self.look(esptool="c6-flash-id-garbled.txt")
        as_dict = report.to_dict()
        self.assertEqual((as_dict["flash_mb"], as_dict["fields"]["flash"], as_dict["unknown"], as_dict["status"]),
                         (None, "unknown", {"flash": "the board did not say"}, outcomes.COULD_NOT_RUN))
        self.assertIn("run a scenario first", as_dict["no_token_reason"])
        json.dumps(as_dict)


class TheLookStatesTheSimulationTest(LookCase):
    """P345: the look says what tested the image and what that test did not do, only when the evidence passes the image."""

    def test_a_passed_run_that_pressed_and_read_nothing_is_simulation_passed_with_its_caveat(self):
        self.run_the_scenario()
        report = self.look()
        self.assertEqual((report.simulation, report.caveats), ("passed", [NO_CONTROL_NO_PIN]))

    def test_a_passed_run_with_a_control_and_a_pin_has_no_caveat(self):
        self.scenario.write_text(CONTROLLED_SCENARIO)
        self.run_the_scenario()
        report = self.look()
        self.assertEqual((report.simulation, report.caveats), ("passed", []))
        lines = board_look.report_lines(report)
        self.assertIn("  simulation: passed", lines)
        self.assertEqual(lines.index("  simulation: passed") + 1, lines.index("  all fields match the board record xiao-esp32-c6."))

    def test_the_caveats_are_printed_in_order_after_the_fields_stops_and_warnings_and_before_the_match_and_the_token(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        lines = board_look.report_lines(self.look(esptool="s3-flash-id-8mb.txt"))
        warning = "  the flash differs: 8 MB, the record says 16 or 4. deploy.py will ask you to accept it."
        self.assertEqual(lines[lines.index(warning):lines.index(warning) + 3],
                         [warning, "  simulation: passed", "  " + NO_CONTROL_NO_PIN])
        self.assertTrue(lines[-1].startswith("  token  "))

    def test_two_caveats_are_two_lines_in_the_evidence_s_order(self):
        self.run_the_scenario()
        evidence = mock.Mock(simulation="passed", why_not_ready=mock.Mock(return_value=None))
        evidence.caveats.return_value = ["first", "second"]
        lines = board_look.report_lines(self.look(evidence=evidence), token=False)
        self.assertEqual(lines[-4:-1], ["  simulation: passed", "  first", "  second"])

    def test_an_image_the_evidence_refuses_has_no_simulation_and_no_caveat(self):
        report = self.look()  # no scenario has run: no image
        self.assertEqual((report.simulation, report.caveats), (None, []))
        self.assertFalse([line for line in board_look.report_lines(report) if "simulation" in line])

    def test_a_refused_image_is_not_asked_for_its_caveats(self):
        evidence = mock.Mock(simulation="passed", why_not_ready=mock.Mock(return_value="no"))
        report = self.look(evidence=evidence)
        evidence.caveats.assert_not_called()
        self.assertEqual((report.simulation, report.caveats), (None, []))

    def test_a_log_that_cannot_be_read_gives_no_simulation_and_no_caveat(self):
        self.run_the_scenario()
        with mock.patch.object(project_image.ProjectImage, "read_run_logs", side_effect=project_image.DeployError("cannot read")):
            report = self.look()
        self.assertEqual((report.simulation, report.caveats), (None, []))

    def test_no_simulation_says_none_with_its_caveat(self):
        report = self.look(evidence=image_evidence.NoSimulationEvidence(self.project))
        self.assertEqual((report.simulation, report.caveats), (None, []))  # no image yet: refused
        self.run_the_scenario()
        with mock.patch.object(image_evidence.NoSimulationEvidence, "why_not_ready", return_value=None):
            report = self.look(evidence=image_evidence.NoSimulationEvidence(self.project))
        self.assertEqual((report.simulation, report.caveats), ("none", ["no simulation tested this image"]))
        self.assertEqual(board_look.report_lines(report, token=False)[-3:-1],
                         ["  simulation: none", "  no simulation tested this image"])

    def test_the_last_deploy_is_there_also_when_the_evidence_refuses_the_image(self):
        self.record_a_deploy()
        report = self.look()  # no scenario has run: no image
        self.assertIsNotNone(report.image_why)
        self.assertEqual((report.last_deploy.state, report.last_deploy.project), ("recorded", "blink-c6"))
        evidence = mock.Mock(simulation="passed", why_not_ready=mock.Mock(return_value="no"))
        self.assertEqual(self.look(evidence=evidence).last_deploy.project, "blink-c6")

    def test_the_json_carries_the_last_deploy(self):
        self.record_a_deploy()
        self.assertEqual(self.look().to_dict()["last_deploy"], {"state": "recorded", "why": None, "project": "blink-c6",
                         "verdict": "ready seen", "deployed": "2026-10-19T09:24:50+02:00"})

    def test_the_json_carries_both(self):
        self.run_the_scenario()
        as_dict = self.look().to_dict()
        self.assertEqual((as_dict["simulation"], as_dict["caveats"]), ("passed", [NO_CONTROL_NO_PIN]))
        as_dict["caveats"].clear()
        self.assertEqual(len(self.look().caveats), 1)


class ReportLinesTest(LookCase):
    """P239 PR 6: the lines a person reads live in board_look, so deploy.py need not import look.py."""

    def test_the_last_deploy_is_the_line_right_after_the_mac(self):
        self.run_the_scenario()
        lines = board_look.report_lines(self.look(), token=False)
        self.assertEqual(lines[lines.index("  mac    " + C6_MAC) + 1], "  " + NONE_RECORDED_LINE)
        self.record_a_deploy()
        lines = board_look.report_lines(self.look(), token=False)
        self.assertEqual(lines[lines.index("  mac    " + C6_MAC) + 1], "  spark's last deploy here: blink-c6, ready seen, "
                         "2026-10-19T09:24:50+02:00 (its store record, not read from the board)")

    def test_a_last_deploy_that_cannot_be_read_says_so_and_what_to_do(self):
        self.run_the_scenario()
        record = board_facts.record_path(C6_MAC)
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text("{not json")
        lines = board_look.report_lines(self.look(), token=False)
        self.assertIn("  last deploy not checked: spark's record of it cannot be read: repair or remove %s, then run "
                      "look.py again." % record, lines)

    def test_a_look_is_could_not_run_when_its_last_deploy_was_not_checked_and_ok_when_none_was_recorded(self):
        self.run_the_scenario()
        report = self.look()
        self.assertEqual(report.status, outcomes.OK)
        report.last_deploy = board_facts.LastDeploy("not-checked", why="spark's record of it cannot be read")
        self.assertEqual(report.status, outcomes.COULD_NOT_RUN)

    def test_a_board_whose_mac_was_not_read_is_not_checked_and_never_no_deploy(self):
        self.run_the_scenario()
        self.record_a_deploy()
        lines = board_look.report_lines(self.look(esptool="c6-flash-id-no-mac.txt"), token=False)
        self.assertEqual(lines[lines.index("  mac    not read") + 1], "  spark's last deploy here: not checked: the board's MAC was not read")

    def test_the_last_deploy_is_read_for_the_mac_of_this_board_only(self):
        self.run_the_scenario()
        self.record_a_deploy()
        other = "aa:bb:cc:dd:ee:ff"
        board_facts.record_deploy({"mac": other, "project": "other", "board": "b", "image_sha256": "0", "simulation": "passed",
                                   "deployed": "2026-10-20T09:24:50+02:00"}, "ready seen", "a test")
        self.assertEqual(self.look().last_deploy.project, "blink-c6")

    def test_the_token_line_is_there_unless_asked_not_to(self):
        self.run_the_scenario()
        report = self.look()
        with_token, without = board_look.report_lines(report), board_look.report_lines(report, token=False)
        self.assertEqual(with_token[:-1], without)
        self.assertTrue(with_token[-1].startswith("  token  %s  for deploy.py --token" % report.token()))

    def test_two_unknown_fields_are_said_in_the_plural(self):
        with mock.patch.object(board_look.boards, "load", return_value={"id": "x"}):
            lines = board_look.report_lines(self.look(), token=False)
        self.assertIn("  2 fields unknown (chip: the record does not hold it, flash: the record does not hold it): "
                      "deploy.py will ask you to accept it.", lines)

    def test_a_stop_is_said(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        lines = board_look.report_lines(self.look(esptool="s3-flash-id-2mb.txt"), token=False)
        self.assertIn("  the flash is 2 MB, the image needs 4 MB: deploy.py will refuse.", lines)

    def test_a_match_and_one_unknown_field_are_said(self):
        self.run_the_scenario()
        self.assertIn("  all fields match the board record xiao-esp32-c6.", board_look.report_lines(self.look(), token=False))
        lines = board_look.report_lines(self.look(esptool="c6-flash-id-garbled.txt"), token=False)
        self.assertIn("  1 field unknown (flash: the board did not say): deploy.py will ask you to accept it.", lines)

    def test_a_flash_of_zero_is_read_and_none_is_not_read(self):
        self.run_the_scenario()
        report = self.look()
        report.reading = report.reading._replace(flash_mb=0)
        self.assertIn("  flash  same      0 MB", board_look.report_lines(report, token=False))
        report.reading = report.reading._replace(flash_mb=None)
        self.assertIn("  flash  same      not read", board_look.report_lines(report, token=False))

    def test_a_warning_is_said(self):
        self.run_the_scenario()
        self.board("firebeetle2-esp32s3")
        lines = board_look.report_lines(self.look(esptool="s3-flash-id-8mb.txt"), token=False)
        self.assertIn("  the flash differs: 8 MB, the record says 16 or 4. deploy.py will ask you to accept it.", lines)


class RenamesTest(unittest.TestCase):
    """P239 PR 6: the old class names are gone, and deploy.py no longer imports look.py."""

    def test_old_names_are_gone(self):
        import ast
        old = {"Report", "Look", "Reading"}
        for each in sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "tests").glob("*.py")):
            for node in ast.walk(ast.parse(each.read_text())):
                named = node.name if isinstance(node, ast.ClassDef) else node.attr if isinstance(node, ast.Attribute) else \
                    node.id if isinstance(node, ast.Name) else None
                # check_physics.py has a local variable named Reading, no class
                if named in old and not (isinstance(node, ast.Name) and each.name == "check_physics.py"):
                    self.fail("%s:%d still names %s" % (each.name, node.lineno, named))
        self.assertFalse(hasattr(board_look, "Report") or hasattr(board_look, "Look") or hasattr(board_look, "Reading"))

    def test_deploy_does_not_import_look(self):
        import ast
        imported = set()
        for node in ast.walk(ast.parse((ROOT / "scripts" / "deploy.py").read_text())):
            if isinstance(node, ast.Import):
                imported |= {alias.name for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module)
        self.assertNotIn("look", imported)


class TheRecordsTest(unittest.TestCase):
    def test_both_library_records_carry_their_flash(self):
        import boards
        self.assertEqual(boards.load(ROOT, "xiao-esp32-c6")["flash_mb"], 4)
        self.assertEqual(boards.load(ROOT, "firebeetle2-esp32s3")["flash_mb"], [16, 4])


if __name__ == "__main__":
    unittest.main()
