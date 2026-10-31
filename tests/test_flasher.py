"""P239 PR 7: flasher.py holds how an image goes onto a board, and deploy.py holds none of esptool's words."""

import ast
import subprocess
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import board_look  # noqa: E402
import boards  # noqa: E402
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
        self.assertEqual(commands, [BASE + ["--chip", "esp32s3", "--port", PORT, "erase-flash"],
                                    BASE + ["--chip", "esp32s3", "--port", PORT, "write-flash", "0x0", "/p/my image.bin"]])

    def test_without_a_port_esptool_finds_the_board(self):
        commands = flasher.EsptoolFlasher(ESPTOOL, "esp32c6").build_commands("/p/i.bin")
        self.assertEqual(commands, [BASE + ["--chip", "esp32c6", "erase-flash"],
                                    BASE + ["--chip", "esp32c6", "write-flash", "0x0", "/p/i.bin"]])

    def test_its_names_are_the_ones_esptool_3_and_4_know(self):
        self.assertEqual((flasher.EsptoolFlasher.ERASE, flasher.EsptoolFlasher.WRITE, flasher.EsptoolFlasher.IMAGE_OFFSET),
                         ("erase-flash", "write-flash", "0x0"))

    def test_it_retries_its_erase_on_exit_2_after_5_s_and_the_base_flasher_never_retries(self):
        self.assertEqual((flasher.EsptoolFlasher.RETRY_EXIT_CODE, flasher.EsptoolFlasher.RETRY_WAIT_S), (2, 5))
        self.assertEqual((flasher.Flasher.RETRY_EXIT_CODE, flasher.Flasher.RETRY_WAIT_S), (None, 0))

    PLACES = boards.ButtonPlaces.from_record({"physical": {"buttons": {
        "seen_from": "the shield facing you", "boot": {"silkscreen": "B", "place": "top right"},
        "reset": {"silkscreen": "R", "place": "top left"}}}})

    def test_the_plain_boot_hint_is_the_sentence_the_flasher_always_had(self):
        self.assertEqual(flasher.EsptoolFlasher(ESPTOOL, "esp32s3").boot_hint,
                         "if esptool could not connect, hold the board's BOOT button, press and release RESET, "
                         "release BOOT, and run it again")

    def test_the_boot_hint_names_the_places_in_the_order_of_the_steps(self):
        hint = flasher.EsptoolFlasher(ESPTOOL, "esp32c6", self.PLACES).boot_hint
        self.assertEqual(hint, "if esptool could not connect, hold the board's BOOT button (B, top right), press and "
                               "release RESET (R, top left), release BOOT, and run it again. Left and right as seen "
                               "with the shield facing you")
        steps = ["hold the board's BOOT", "press and release RESET", "release BOOT", "run it again"]
        self.assertEqual([hint.index(step) for step in steps], sorted(hint.index(step) for step in steps))

    def test_the_look_prints_the_hint_it_is_given(self):
        failed = types.SimpleNamespace(returncode=1, stdout="", stderr="")
        hint = flasher.EsptoolFlasher.boot_hint_for(self.PLACES)
        with self.assertRaises(board_look.LookStop) as stop:
            board_look.EsptoolReader(ESPTOOL, lambda argv, **kw: failed, boot_hint=hint).read(PORT)
        self.assertTrue(str(stop.exception).endswith(hint), str(stop.exception))
        with self.assertRaises(board_look.LookStop) as stop:
            board_look.EsptoolReader(ESPTOOL, lambda argv, **kw: failed).read(PORT)
        self.assertIn(flasher.EsptoolFlasher(ESPTOOL, "esp32s3").boot_hint, str(stop.exception))

    def test_the_port_finder_prints_the_plain_hint_when_mpremote_times_out(self):
        def timed_out(argv, **kw):
            raise subprocess.TimeoutExpired(argv, 15)
        with self.assertRaises(board_look.LookStop) as stop:
            board_look.PortFinder(ESPTOOL, timed_out).nodes()
        self.assertIn(flasher.EsptoolFlasher(ESPTOOL, "esp32s3").boot_hint, str(stop.exception))

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
        self.assertEqual(flasher.Flasher.boot_hint, "")
        self.assertEqual(other.build_commands("i", PORT), [["probe", "i", "on", PORT]])
        self.assertEqual(other.boot_hint, "")


class DeployHoldsNoEsptoolWordTest(unittest.TestCase):
    #: String constants esptool defines. Exact equality: prose that mentions a word is the person's text.
    WORDS = {"erase-flash", "write-flash", "flash-id", "--chip", "0x0"}
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
        self.assertFalse(names & {"ERASE", "WRITE", "IMAGE_OFFSET", "BOOT_HINT_TEMPLATE"})
        owners = {node.value.id for node in ast.walk(tree) if isinstance(node, ast.Attribute) and node.attr == "boot_hint_for"
                  and isinstance(node.value, ast.Name)}
        self.assertEqual(owners, set())  # planned.flasher.boot_hint, not a builder of its own


if __name__ == "__main__":
    unittest.main()
