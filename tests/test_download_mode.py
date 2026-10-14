"""P243 (#252): after a flash, a board that waits in download mode is found, and a press of its R button is seen."""

import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import download_mode  # noqa: E402
import tools  # noqa: E402
from fakes import FakeClock  # noqa: E402

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
        waits, said = download_mode.DownloadModeProbe(["/opt/python3"], PORT, printing(ROM, ran)).waits_in_download_mode()
        self.assertEqual((waits, said), (True, ROM))
        self.assertEqual(ran[0][:2] + ran[0][3:], ["/opt/python3", "-c", PORT, "2"])
        self.assertIn("s.dtr, s.rts = sys.argv[1], 115200, 0.1, False, False", ran[0][2])

    def test_a_firmware_s_lines_are_not_download_mode(self):
        probe = download_mode.DownloadModeProbe(["/opt/python3"], PORT, printing("ready\n", []))
        self.assertFalse(probe.waits_in_download_mode()[0])

    def test_a_port_that_cannot_be_read_is_not_download_mode(self):
        def fails(command, **kw):
            raise subprocess.CalledProcessError(1, command, "", "could not open port")
        self.assertEqual(download_mode.DownloadModeProbe(["/opt/python3"], PORT, fails).waits_in_download_mode(),
                         (False, ""))

    def test_a_probe_needs_mpremote_as_a_python_package_and_a_port(self):
        python = tools.Tool("mpremote", "board-shell", {"kind": "python", "module": "mpremote"}, ["/opt/python3"])
        command = tools.Tool("mpremote", "board-shell", {"kind": "command"}, ["/usr/local/bin/mpremote"])
        self.assertEqual(download_mode.DownloadModeProbe.for_tool(python, PORT).python, ["/opt/python3"])
        self.assertIsNone(download_mode.DownloadModeProbe.for_tool(command, PORT))
        self.assertIsNone(download_mode.DownloadModeProbe.for_tool(python, None))


class TheResetTest(unittest.TestCase):
    def probe(self, *here):
        """A probe whose port is there or not at each look, in turn, then there for good."""
        looks = list(here)
        self.clock = FakeClock()
        return download_mode.DownloadModeProbe(["/opt/python3"], PORT, clock=self.clock,
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


if __name__ == "__main__":
    unittest.main()
