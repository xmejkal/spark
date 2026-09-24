"""
Proof that each check bites.

A check that cannot fail is worse than no check, because it is believed. So every check here has
a design that violates it and an assertion that it is caught — and the passing case is the real
smart bin, so a change that breaks working designs is caught too.

    python3 -m unittest discover -s tests
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_pins  # noqa: E402

BOARD = json.loads(
    (ROOT.parent / "smartbin-local" / "boards" / "xiao-esp32-c6.json").read_text())


def design(*parts):
    return {"parts": list(parts)}


class PinCapabilityTest(unittest.TestCase):
    def test_a_wake_source_on_a_pin_that_cannot_wake_is_caught(self):
        # D7 is GPIO17. Only GPIO0-7 can wake an ESP32-C6, so this is the mistake that the bin's
        # whole pin map exists to avoid.
        problems = check_pins.check_pin_capability(
            design({"ref": "OpenButton", "pins": [{"signal": "A", "pin": "D7", "needs": ["wake"]}]}),
            BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("cannot do that", problems[0].detail)
        self.assertIn("D0", problems[0].fix)  # tells you which pins can

    def test_an_analogue_input_on_a_digital_only_pin_is_caught(self):
        problems = check_pins.check_pin_capability(
            design({"ref": "StallSense", "pins": [{"signal": "SENSE", "pin": "D3", "needs": ["adc"]}]}),
            BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("adc", problems[0].detail)

    def test_a_pin_the_board_does_not_have_is_caught(self):
        problems = check_pins.check_pin_capability(
            design({"ref": "Ghost", "pins": [{"signal": "X", "pin": "D42"}]}), BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("does not bring out", problems[0].detail)

    def test_two_parts_on_one_pin_are_caught(self):
        problems = check_pins.check_pin_capability(
            design(
                {"ref": "OpenButton", "pins": [{"signal": "A", "pin": "D1"}]},
                {"ref": "ModeButton", "pins": [{"signal": "A", "pin": "D1"}]}),
            BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("already taken by OpenButton", problems[0].detail)

    def test_a_serial_module_on_the_boot_log_pin_is_caught(self):
        # D6 is GPIO16 = U0TXD. A button there is fine; anything parsing serial is not, because
        # the ROM bootloader prints its log into that module on every reset.
        problems = check_pins.check_pin_capability(
            design({"ref": "Mp3Player", "reads_serial": True,
                    "pins": [{"signal": "RXD", "pin": "D6"}]}),
            BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("boot-log UART", problems[0].detail)

    def test_a_button_on_the_boot_log_pin_is_fine(self):
        # The caveat is real but conditional. A check that forbade this outright would be wrong,
        # and the bin would fail its own regression fixture.
        problems = check_pins.check_pin_capability(
            design({"ref": "ModeButton", "pins": [{"signal": "A", "pin": "D6"}]}), BOARD)
        self.assertEqual(problems, [])

    def test_chip_capability_is_intersected_with_what_the_board_exposes(self):
        # The C6 can wake on GPIO0-7; the XIAO brings out only 0, 1 and 2 of them. Checking the
        # chip alone would approve four pins that are not on the header.
        pins = check_pins.usable_pins(BOARD)
        can_wake = sorted(name for name, pin in pins.items() if "wake" in pin["capabilities"])
        self.assertEqual(can_wake, ["D0", "D1", "D2"])


class I2cAddressTest(unittest.TestCase):
    def test_two_devices_at_one_address_are_caught(self):
        problems = check_pins.check_i2c_addresses(design(
            {"ref": "Rangefinder", "i2c": {"bus": "i2c0", "address": "0x29"}},
            {"ref": "SecondSensor", "i2c": {"bus": "i2c0", "address": "0x29"}}))
        self.assertEqual(len(problems), 1)
        self.assertIn("0x29", problems[0].detail)
        self.assertIn("Rangefinder", problems[0].detail)

    def test_the_same_address_on_a_different_bus_is_fine(self):
        problems = check_pins.check_i2c_addresses(design(
            {"ref": "Rangefinder", "i2c": {"bus": "i2c0", "address": "0x29"}},
            {"ref": "SecondSensor", "i2c": {"bus": "i2c1", "address": "0x29"}}))
        self.assertEqual(problems, [])


class RealDesignTest(unittest.TestCase):
    def test_the_smart_bin_passes(self):
        """The regression fixture: a known-good design must stay clean."""
        real = json.loads((ROOT / "examples" / "smartbin.design.json").read_text())
        self.assertEqual(check_pins.run(real, BOARD), [])


if __name__ == "__main__":
    unittest.main()
