"""
Proof that firmware and board are compared on what is physically true, not on naming.

Firmware and board are written in different languages, by different tools, at different times,
and nothing compiles them together. So they drift silently: the code runs, the board builds, the
lid does not move.

The design decision worth testing is what gets compared. A previous tool decided which firmware
constants needed a wake-capable pin by running a regex over their NAMES — a naming convention
pretending to be a requirement. Rename a constant and the check quietly stopped applying; a
project whose constants were called something else got no checking at all. Here the requirement
comes from the assignment, which came from the part that asked for it, and what is compared is
the GPIO number.

    python3 -m unittest discover -s tests
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_firmware  # noqa: E402

BOARD = {
    "schema": 1, "id": "test", "name": "Test Board",
    "pins": {"P0": 0, "W0": 2, "A0": 4, "S0": 5},
    "wake_capable_gpio": [2, 4],
    "adc_gpio": [4],
    "pin_roles": {"strapping": {"gpio": [5], "note": "sampled at reset"}},
}


def assignment(*entries):
    return [dict({"signal": s, "pin": p, "gpio": g, "needs": n}) for s, p, g, n in entries]


class ReadingTheFirmwareTest(unittest.TestCase):
    def test_it_reads_a_plain_constant(self):
        self.assertEqual(check_firmware.read_pin_constants("PIN_MOTOR_IA = 14"),
                         {"PIN_MOTOR_IA": 14})

    def test_it_reads_one_with_a_trailing_comment(self):
        self.assertEqual(check_firmware.read_pin_constants("PIN_LED = 9   # D7"),
                         {"PIN_LED": 9})

    def test_it_ignores_anything_that_is_not_a_plain_number(self):
        # A computed or conditional assignment is not something to guess at, and a check that
        # guesses is worse than one that says it could not tell.
        source = "PIN_A = BASE + 1\nPIN_B = 3\n# PIN_C = 9\n"
        self.assertEqual(check_firmware.read_pin_constants(source), {"PIN_B": 3})

    def test_it_ignores_constants_that_are_not_pins(self):
        self.assertEqual(check_firmware.read_pin_constants("VOLUME = 22"), {})


class AgainstTheBoardTest(unittest.TestCase):
    """True regardless of what the design intended."""

    def test_a_pin_the_board_does_not_bring_out_is_caught(self):
        problems = check_firmware.check_against_board({"PIN_X": 99}, BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("does not bring out", problems[0])

    def test_a_strapping_pin_is_caught_and_the_reason_is_carried(self):
        problems = check_firmware.check_against_board({"PIN_X": 5}, BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("strapping", problems[0])
        # The board file explained why; repeating it here saves a lookup at the worst moment.
        self.assertIn("sampled at reset", problems[0])

    def test_an_ordinary_pin_says_nothing(self):
        self.assertEqual(check_firmware.check_against_board({"PIN_X": 0}, BOARD), [])


class AgainstTheAgreedPinMapTest(unittest.TestCase):
    """Both directions, because each failure is silent in its own way."""

    def test_a_pin_the_design_wired_but_the_firmware_ignores_is_caught(self):
        problems = check_firmware.check_against_assignment(
            {}, assignment(("LED", "P0", 0, [])), BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("no firmware constant uses that pin", problems[0])

    def test_a_pin_the_firmware_drives_but_the_design_ignores_is_caught(self):
        problems = check_firmware.check_against_assignment({"PIN_LED": 0}, [], BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("does not connect to anything", problems[0])

    def test_agreement_says_nothing(self):
        self.assertEqual(check_firmware.check_against_assignment(
            {"PIN_LED": 0}, assignment(("LED", "P0", 0, [])), BOARD), [])

    def test_the_names_do_not_have_to_match(self):
        # Matched on GPIO, which is what is physically true. A firmware that calls its constant
        # PIN_STATUS while the design calls the signal LED is not a defect.
        self.assertEqual(check_firmware.check_against_assignment(
            {"PIN_STATUS_INDICATOR": 0}, assignment(("LED", "P0", 0, [])), BOARD), [])

    def test_a_capability_the_design_asked_for_is_re_checked(self):
        # The assigner honoured it, so this normally holds — but a hand-edited pin map is exactly
        # where it stops holding, and that edit leaves no other trace.
        problems = check_firmware.check_against_assignment(
            {"PIN_INT": 0}, assignment(("INT", "P0", 0, ["wake"])), BOARD)
        self.assertTrue(any("cannot do" in p for p in problems))

    def test_a_capability_that_still_holds_says_nothing(self):
        self.assertEqual(check_firmware.check_against_assignment(
            {"PIN_INT": 2}, assignment(("INT", "W0", 2, ["wake"])), BOARD), [])


class NothingToCompareIsNotAgreementTest(unittest.TestCase):
    def test_a_firmware_with_no_pin_constants_is_could_not_run(self):
        # Silence here would read as "the firmware agrees", which is the one thing it must never
        # be mistaken for.
        path = Path(tempfile.mkdtemp()) / "config.py"
        path.write_text("VOLUME = 22\n")
        self.assertEqual(check_firmware.main([str(path), "--project", str(path.parent)]),
                         check_firmware.EXIT_COULD_NOT_RUN)

    def test_a_missing_file_is_could_not_run(self):
        self.assertEqual(check_firmware.main(["/nonexistent/config.py"]),
                         check_firmware.EXIT_COULD_NOT_RUN)

    def test_could_not_run_is_a_different_answer_from_clean(self):
        self.assertNotEqual(check_firmware.EXIT_COULD_NOT_RUN, check_firmware.EXIT_OK)


class AgainstARealFirmwareTest(unittest.TestCase):
    def test_the_real_board_and_its_firmware_agree(self):
        config = ROOT.parent / "smartbin-local" / "firmware" / "micropython" / "config.py"
        if not config.is_file():
            self.skipTest("no real firmware available to read")
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        firmware = check_firmware.read_pin_constants(config.read_text())
        self.assertTrue(firmware, "read no pin constants from a real firmware")
        self.assertEqual(check_firmware.check_against_board(firmware, board), [])


if __name__ == "__main__":
    unittest.main()
