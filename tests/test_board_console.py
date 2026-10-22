"""P243 (#252), P251 (#264): the board's console, read so that the open does not choose the boot mode: download mode
found, a press of R seen."""

import contextlib
import io
import subprocess
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_console  # noqa: E402
import download_mode  # noqa: E402
import tools  # noqa: E402
from fakes import FakeClock  # noqa: E402
from unittest import mock  # noqa: E402

PORT = "/dev/cu.usbmodem101"
ROM = "ESP-ROM:esp32c6-20220919\nboot:0x4 (DOWNLOAD(USB/UART0/SDIO_FEI_FEO))\nwaiting for download\n"


def printing(text, ran):
    """A fake subprocess.run whose command prints `text`, keeping each command in `ran`."""
    def run(command, **kw):
        ran.append(command)
        return subprocess.CompletedProcess(command, 0, text, "")
    return run


class TheConsoleTest(unittest.TestCase):
    def test_the_rom_s_download_line_is_download_mode_and_its_words_are_kept(self):
        ran = []
        waits, said = board_console.ConsoleProbe(["/opt/python3"], PORT, printing(ROM, ran)).waits_in_download_mode()
        self.assertEqual((waits, said), (True, ROM))
        self.assertEqual(ran[0][:2] + ran[0][3:], ["/opt/python3", "-c", PORT, "2"])
        self.assertIn("s.dtr, s.rts, s.exclusive = sys.argv[1], 115200, 0.1, False, False, True", ran[0][2])

    def test_the_console_script_opens_the_port_with_dtr_and_rts_off_and_prints_what_it_read(self):
        opened = []

        class Serial:
            def __init__(self):
                self.chunks = [ROM.encode(), b"\xff"]

            def open(self):
                opened.append((self.port, self.baudrate, self.dtr, self.rts))

            def read(self, size):
                return self.chunks.pop(0) if self.chunks else b""

            def close(self):
                opened.append("closed")

        out = io.StringIO()
        with mock.patch.dict(sys.modules, {"serial": types.SimpleNamespace(Serial=Serial)}), \
                mock.patch.object(sys, "argv", ["-c", PORT, "0.01"]), contextlib.redirect_stdout(out):
            exec(board_console.READ_CONSOLE, {})
        self.assertEqual(opened, [(PORT, 115200, False, False), "closed"])
        self.assertEqual(out.getvalue(), ROM + "\ufffd")

    def test_the_console_script_takes_the_port_s_lock_and_exits_3_when_another_program_holds_it(self):
        import errno

        class SerialException(OSError):
            pass

        def opening(error):
            class Serial:
                def open(self):
                    self.seen = self.exclusive
                    raise SerialException(error, "Could not exclusively lock port")
            return Serial

        for error, code in ((errno.EAGAIN, 3), (errno.ENOENT, 1)):
            serial = types.SimpleNamespace(Serial=opening(error), SerialException=SerialException)
            with mock.patch.dict(sys.modules, {"serial": serial}), mock.patch.object(sys, "argv", ["-c", PORT, "1"]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stopped:
                exec(board_console.READ_CONSOLE, {})
            self.assertEqual(stopped.exception.code, code)

    def test_a_port_another_program_holds_is_read_as_busy_and_never_as_download_mode(self):
        def busy(command, **kw):
            raise subprocess.CalledProcessError(3, command, "", "Could not exclusively lock port /dev/cu.usbmodem101")
        probe = board_console.ConsoleProbe(["/opt/python3"], PORT, busy)
        self.assertEqual(probe.console().kind, "busy")
        self.assertFalse(probe.waits_in_download_mode()[0])

    def test_a_line_that_is_ready_is_a_boot_and_a_word_inside_a_line_is_not(self):
        self.assertTrue(download_mode.booted("entry 0x4086b910\r\nready\r\n"))
        self.assertFalse(download_mode.booted("not ready yet\n"))
        self.assertFalse(download_mode.booted(""))
        self.assertTrue(download_mode.booted(" ready \n"))

    def test_a_firmware_s_lines_are_not_download_mode(self):
        probe = board_console.ConsoleProbe(["/opt/python3"], PORT, printing("ready\n", []))
        self.assertFalse(probe.waits_in_download_mode()[0])

    def test_a_console_script_that_fails_is_not_download_mode_whatever_it_printed(self):
        def run(command, check=False, **kw):
            if check:
                raise subprocess.CalledProcessError(1, command, ROM, "no module named serial")
            return subprocess.CompletedProcess(command, 1, ROM, "no module named serial")
        self.assertEqual(board_console.ConsoleProbe(["/opt/python3"], PORT, run).waits_in_download_mode(),
                         (False, "could not read the port: no module named serial"))

    def test_a_port_that_cannot_be_read_is_not_download_mode(self):
        def fails(command, **kw):
            raise subprocess.CalledProcessError(1, command, "", "could not open port")
        self.assertEqual(board_console.ConsoleProbe(["/opt/python3"], PORT, fails).waits_in_download_mode(),
                         (False, "could not read the port: could not open port"))

    def test_a_probe_needs_mpremote_as_a_python_package_and_a_port(self):
        python = tools.Tool("mpremote", "board-shell", {"kind": "python", "module": "mpremote"}, ["/opt/python3"])
        command = tools.Tool("mpremote", "board-shell", {"kind": "command"}, ["/usr/local/bin/mpremote"])
        self.assertEqual(board_console.ConsoleProbe.for_tool(python, PORT).python, ["/opt/python3"])
        self.assertIsNone(board_console.ConsoleProbe.for_tool(command, PORT))
        self.assertIsNone(board_console.ConsoleProbe.for_tool(python, None))


class TheResetTest(unittest.TestCase):
    def probe(self, *here):
        """A probe whose port is there or not at each look, in turn, then there for good."""
        looks = list(here)
        self.clock = FakeClock()
        return board_console.ConsoleProbe(["/opt/python3"], PORT, clock=self.clock,
                                               port_exists=lambda port: looks.pop(0) if looks else True)

    def test_a_port_that_goes_and_comes_back_is_the_reset(self):
        self.assertTrue(self.probe(True, True, False, False, True).wait_for_reset())
        self.assertEqual(len(self.clock.slept), 4)

    def test_a_port_that_never_goes_is_no_reset_after_the_wait(self):
        self.assertFalse(self.probe().wait_for_reset(timeout_s=1))
        self.assertGreaterEqual(self.clock.now, 1)

    def test_a_port_that_goes_and_never_comes_back_is_no_reset(self):
        probe = self.probe()
        probe.port_exists = lambda port: False
        self.assertFalse(probe.wait_for_reset(timeout_s=1))


class TheCureTest(unittest.TestCase):
    """P251: the open with DTR and RTS off is the cure. It keeps what the restart printed, then waits for the port."""

    def probe(self, run, *here):
        looks = list(here)
        self.clock = FakeClock()
        return board_console.ConsoleProbe(["/opt/python3"], PORT, run, clock=self.clock,
                                          port_exists=lambda port: looks.pop(0) if looks else True)

    def test_a_restart_heard_on_the_open_is_kept_and_the_cure_settles_2_s(self):
        heard = "ESP-ROM:esp32c6-20220919\nrst:0x15 (USB_UART_HPSYS),boot:0x1e\nready\n"
        self.assertEqual(self.probe(printing(heard, [])).cure(), board_console.Cure(heard, None, True, True, True))
        self.assertEqual(self.clock.slept, [2])

    def test_an_open_that_printed_no_restart_is_no_restart(self):
        self.assertEqual(self.probe(printing("first: 1\n", [])).cure(), board_console.Cure("first: 1\n", None, False, True))

    def test_a_read_that_failed_mid_restart_keeps_what_it_heard_and_its_reason(self):
        def fails(command, **kw):
            raise subprocess.CalledProcessError(1, command, "rst:0x15 (USB_UART_HPSYS)\n", "serial.SerialException: device disconnected")
        self.assertEqual(self.probe(fails).cure(), board_console.Cure(
            "rst:0x15 (USB_UART_HPSYS)\n", "serial.SerialException: device disconnected", True, True, True))

    def test_a_read_that_timed_out_keeps_its_reason(self):
        def stalls(command, **kw):
            raise subprocess.TimeoutExpired(command, kw["timeout"])
        cure = self.probe(stalls).cure()
        self.assertEqual((cure.heard, cure.restart_heard), ("", False))
        self.assertIn("timed out", cure.why)

    def test_the_cure_waits_until_the_port_is_there_again(self):
        self.probe(printing("", []), False, False, True).cure()
        self.assertEqual(self.clock.slept, [0.1, 0.1, 2])

    def test_a_port_not_back_after_10_s_is_said_and_not_settled(self):
        probe = self.probe(printing("", []))
        probe.port_exists = lambda port: False
        cure = probe.cure()
        self.assertFalse(cure.port_back)
        self.assertGreaterEqual(self.clock.now, 10)
        self.assertLess(self.clock.now, 11)
        self.assertNotIn(2, self.clock.slept)

    def test_a_restart_is_the_rom_s_rst_line_and_not_a_word_that_ends_in_rst(self):
        self.assertTrue(board_console.shows_restart("rst:0x15 (USB_UART_HPSYS),boot:0x1e"))
        self.assertTrue(board_console.shows_restart("ESP-ROM\nrst:0xc (SW_CPU),boot:0x8"))
        self.assertFalse(board_console.shows_restart("first: 1\nworst:0x\n"))
        self.assertFalse(board_console.shows_restart("ready\n"))

    def test_a_boot_heard_from_its_middle_is_a_boot_tail_not_a_restart(self):
        tail = "mode:DIO, clock div:2\r\nload:0x40875730,len:0xdbc\r\nentry 0x4086b910\r\nready\r\n"
        self.assertTrue(board_console.shows_boot(tail))
        self.assertFalse(board_console.shows_restart(tail))
        self.assertTrue(board_console.shows_boot("rst:0x15 (USB_UART_HPSYS),boot:0x1e\n"))
        self.assertFalse(board_console.shows_boot("my entry 0x10 point\n"))
        self.assertFalse(board_console.shows_boot("entry 0x10 point\n"))

    def test_the_cure_keeps_a_boot_tail_apart_from_a_restart(self):
        tail = "mode:DIO, clock div:2\nentry 0x4086b910\nready\n"
        self.assertEqual(self.probe(printing(tail, [])).cure(), board_console.Cure(tail, None, False, True, True))

    def test_the_console_script_prints_what_it_read_when_the_port_drops(self):
        class Serial:
            def __init__(self):
                self.chunks = [b"rst:0x15\n"]

            def open(self):
                pass

            def read(self, size):
                if self.chunks:
                    return self.chunks.pop(0)
                raise OSError("device disconnected")

            def close(self):
                pass

        out = io.StringIO()
        with mock.patch.dict(sys.modules, {"serial": types.SimpleNamespace(Serial=Serial)}), \
                mock.patch.object(sys, "argv", ["-c", PORT, "5"]), contextlib.redirect_stdout(out), \
                self.assertRaises(OSError):
            exec(board_console.READ_CONSOLE, {})
        self.assertEqual(out.getvalue(), "rst:0x15\n")


class ResetSentenceTest(unittest.TestCase):
    """P213 b2: the download-mode sentences name RESET, with its place only when a board record gives one."""

    def test_a_board_with_no_places_gets_the_plain_words(self):
        self.assertEqual(download_mode.press_reset(), "the board waits in download mode: press the board's RESET once")
        self.assertIn("in 60 s: press its RESET. If", download_mode.no_reset())

    def test_a_board_with_places_names_where_reset_is(self):
        record = {"physical": {"buttons": {"seen_from": "USB-C at the top", "boot": {"silkscreen": "B", "place": "top right"},
                                           "reset": {"silkscreen": "R", "place": "top left"}}}}
        places = download_mode.boards.ButtonPlaces.from_record(record)
        self.assertEqual(download_mode.press_reset(places), "the board waits in download mode: press the board's RESET (R, top left) once. Left and right as seen "
                         "with USB-C at the top")
        self.assertIn("press its RESET (R, top left). Left and right as seen with USB-C at the top. If",
                      download_mode.no_reset(places))

if __name__ == "__main__":
    unittest.main()
