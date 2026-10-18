"""P239 PR 7: flasher.py holds how an image goes onto a board, and deploy.py holds none of esptool's words."""

import ast
import subprocess
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_look  # noqa: E402
import flasher  # noqa: E402
import tools  # noqa: E402

PYTHON = "/opt/python3"
ESPTOOL = tools.Tool("esptool", "flasher", {"kind": "python", "module": "esptool"}, [PYTHON])
PORT = "/dev/cu.usbmodem1101"
BASE = [PYTHON, "-m", "esptool"]


class SecondFlasher(flasher.Flasher):
    """A flasher a caller swaps in: one command, no hint."""

    def build_commands(self, image, port=None):
        return [["probe", str(image)] + (["on", port] if port else [])]


class TheEsptoolFlasherTest(unittest.TestCase):
    def test_it_erases_then_writes_the_image_at_zero_on_the_port(self):
        commands = flasher.EsptoolFlasher(ESPTOOL, "esp32s3").build_commands("/p/my image.bin", PORT)
        self.assertEqual(commands, [BASE + ["--chip", "esp32s3", "--port", PORT, "erase_flash"],
                                    BASE + ["--chip", "esp32s3", "--port", PORT, "write_flash", "0x0", "/p/my image.bin"]])

    def test_without_a_port_esptool_finds_the_board(self):
        commands = flasher.EsptoolFlasher(ESPTOOL, "esp32c6").build_commands("/p/i.bin")
        self.assertEqual(commands, [BASE + ["--chip", "esp32c6", "erase_flash"],
                                    BASE + ["--chip", "esp32c6", "write_flash", "0x0", "/p/i.bin"]])

    def test_its_names_are_the_ones_esptool_3_and_4_know(self):
        self.assertEqual((flasher.EsptoolFlasher.ERASE, flasher.EsptoolFlasher.WRITE, flasher.EsptoolFlasher.IMAGE_OFFSET),
                         ("erase_flash", "write_flash", "0x0"))

    def test_the_boot_hint_is_the_one_the_look_prints_too(self):
        steps = ["hold the board's BOOT button", "press and release RESET", "release BOOT", "run it again"]
        hint = flasher.EsptoolFlasher.BOOT_HINT
        self.assertEqual([hint.index(step) for step in steps], sorted(hint.index(step) for step in steps))
        failed = types.SimpleNamespace(returncode=1, stdout="", stderr="")
        with self.assertRaises(board_look.LookStop) as stop:
            board_look.EsptoolReader(ESPTOOL, lambda argv, **kw: failed).read(PORT)
        self.assertIn(flasher.EsptoolFlasher.BOOT_HINT, str(stop.exception))

    def test_the_port_finder_prints_the_same_hint_when_mpremote_times_out(self):
        def timed_out(argv, **kw):
            raise subprocess.TimeoutExpired(argv, 15)
        with self.assertRaises(board_look.LookStop) as stop:
            board_look.PortFinder(ESPTOOL, timed_out).boards()
        self.assertIn(flasher.EsptoolFlasher.BOOT_HINT, str(stop.exception))

    def test_the_prefix_puts_chip_before_port_and_both_are_optional(self):
        self.assertEqual(flasher.build_esptool_prefix(ESPTOOL, PORT, "esp32s3"), BASE + ["--chip", "esp32s3", "--port", PORT])
        self.assertEqual(flasher.build_esptool_prefix(ESPTOOL, PORT), BASE + ["--port", PORT])
        self.assertEqual(flasher.build_esptool_prefix(ESPTOOL), BASE)


class TheBaseTest(unittest.TestCase):
    def test_the_base_supplies_no_commands(self):
        with self.assertRaises(NotImplementedError):
            flasher.Flasher().build_commands("i")

    def test_the_base_has_no_hint_and_a_caller_can_swap_a_subclass_in(self):
        other = SecondFlasher()
        self.assertEqual(flasher.Flasher.BOOT_HINT, "")
        self.assertEqual(other.build_commands("i", PORT), [["probe", "i", "on", PORT]])
        self.assertEqual(other.BOOT_HINT, "")


class DeployHoldsNoEsptoolWordTest(unittest.TestCase):
    #: String constants esptool defines. Exact equality: prose that mentions a word is the person's text.
    WORDS = {"erase_flash", "write_flash", "flash_id", "--chip", "0x0"}
    #: Module-level names whose value is text for the person.
    PROSE = {"EPILOG", "WATCH"}

    def test_deploy_holds_no_esptool_constant(self):
        tree = ast.parse((ROOT / "scripts" / "deploy.py").read_text())
        prose = {id(node.value) for node in tree.body if isinstance(node, ast.Assign)
                 and any(isinstance(each, ast.Name) and each.id in self.PROSE for each in node.targets)}
        found = [(node.lineno, node.value) for node in ast.walk(tree)
                 if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in self.WORDS
                 and id(node) not in prose]
        self.assertEqual(found, [])

    def test_deploy_reads_the_hint_from_its_plan_and_names_no_flash_constant(self):
        tree = ast.parse((ROOT / "scripts" / "deploy.py").read_text())
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        self.assertFalse(names & {"ERASE", "WRITE", "IMAGE_OFFSET", "BOOT_HINT"})
        owners = {node.value.id for node in ast.walk(tree) if isinstance(node, ast.Attribute) and node.attr == "BOOT_HINT"
                  and isinstance(node.value, ast.Name)}
        self.assertEqual(owners, set())  # planned.flasher.BOOT_HINT, not board_look.BOOT_HINT


if __name__ == "__main__":
    unittest.main()
