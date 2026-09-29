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

import boards  # noqa: E402  - for the role vocabulary, so the test cannot drift from it either
import check_design  # noqa: E402

BOARD = json.loads(
    (ROOT / "boards" / "xiao-esp32-c6.json").read_text())

#: The board that brings one GPIO out under two silkscreen names, which is where the
#: label-keyed exclusivity check quietly stopped working.
FIREBEETLE = json.loads(
    (ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())


def design(*parts):
    return {"parts": list(parts)}


class PinCapabilityTest(unittest.TestCase):
    def test_a_wake_source_on_a_pin_that_cannot_wake_is_caught(self):
        # D7 is GPIO17. Only GPIO0-7 can wake an ESP32-C6, so this is the mistake that the bin's
        # whole pin map exists to avoid.
        problems = check_design.check_pin_capability(
            design({"ref": "OpenButton", "pins": [{"signal": "A", "pin": "D7", "needs": ["wake"]}]}),
            BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("cannot do that", problems[0].detail)
        self.assertIn("D0", problems[0].fix)  # tells you which pins can

    def test_an_analogue_input_on_a_digital_only_pin_is_caught(self):
        problems = check_design.check_pin_capability(
            design({"ref": "StallSense", "pins": [{"signal": "SENSE", "pin": "D3", "needs": ["adc"]}]}),
            BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("adc", problems[0].detail)

    def test_a_pin_the_board_does_not_have_is_caught(self):
        problems = check_design.check_pin_capability(
            design({"ref": "Ghost", "pins": [{"signal": "X", "pin": "D42"}]}), BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("does not bring out", problems[0].detail)

    def test_two_parts_on_one_pin_are_caught(self):
        problems = check_design.check_pin_capability(
            design(
                {"ref": "OpenButton", "pins": [{"signal": "A", "pin": "D1"}]},
                {"ref": "ModeButton", "pins": [{"signal": "A", "pin": "D1"}]}),
            BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("already taken by OpenButton", problems[0].detail)

    def test_a_serial_module_on_the_boot_log_pin_is_caught(self):
        # D6 is GPIO16 = U0TXD. A button there is fine; anything parsing serial is not, because
        # the ROM bootloader prints its log into that module on every reset.
        problems = check_design.check_pin_capability(
            design({"ref": "Mp3Player", "reads_serial": True,
                    "pins": [{"signal": "RXD", "pin": "D6"}]}),
            BOARD)
        self.assertEqual(len(problems), 1)
        self.assertIn("serial console", problems[0].detail)

    def test_two_devices_sharing_a_declared_bus_are_not_a_collision(self):
        # The commonest wiring pattern in the domain, reported as two errors on a stranger's
        # first design. Both parts declare the same bus; the design file already carried it and
        # nothing read it.
        oled = {"ref": "Oled", "i2c": {"bus": "i2c0"},
                "pins": [{"signal": "SDA", "pin": "SDA"}, {"signal": "SCL", "pin": "SCL"}]}
        sensor = dict(oled, ref="Sensor")
        self.assertEqual(
            check_design.check_pin_capability(design(oled, sensor), FIREBEETLE), [])

    def test_two_devices_on_the_same_pin_but_different_buses_are_still_a_collision(self):
        # The exemption is "you both said you share this bus", not "you are both I2C".
        oled = {"ref": "Oled", "i2c": {"bus": "i2c0"},
                "pins": [{"signal": "SDA", "pin": "SDA"}]}
        other = {"ref": "Other", "i2c": {"bus": "i2c1"},
                 "pins": [{"signal": "SDA", "pin": "SDA"}]}
        self.assertEqual(len(check_design.check_pin_capability(design(oled, other), FIREBEETLE)), 1)

    def test_one_pin_brought_out_under_two_names_is_caught(self):
        """
        The mirror-image defect, and the reason both live in one fix.

        This board brings GPIO10 out twice, silkscreened `SS` and `A4`. Two parts on those two
        labels are on ONE pin and short each other. Keyed on the label, that read as clean —
        "two parts on one pin" is a headline check, missed on the plugin's own default board.
        """
        aliases = [label for label, gpio in FIREBEETLE["pins"].items() if gpio == 10]
        self.assertEqual(len(aliases), 2, "this board no longer has an aliased pin to test with")
        first, second = aliases
        problems = check_design.check_pin_capability(
            design({"ref": "Flash", "pins": [{"signal": "CS", "pin": first}]},
                   {"ref": "Analog", "pins": [{"signal": "IN", "pin": second}]}), FIREBEETLE)
        self.assertEqual(len(problems), 1)
        self.assertIn("same pin", problems[0].detail)
        self.assertIn("GPIO10", problems[0].detail)

    def test_a_plain_collision_on_one_label_is_still_caught(self):
        problems = check_design.check_pin_capability(
            design({"ref": "BtnA", "pins": [{"signal": "A", "pin": "D6"}]},
                   {"ref": "BtnB", "pins": [{"signal": "B", "pin": "D6"}]}), FIREBEETLE)
        self.assertEqual(len(problems), 1)
        self.assertIn("already taken by BtnA", problems[0].detail)

    def test_the_same_hazard_is_caught_on_every_board_the_plugin_ships(self):
        """
        The defect that made this necessary: the two shipped boards named the console
        differently — `boot_log_tx` and `console_uart` — and this check knew only the first. So a
        serial-parsing part on the console UART was caught on the XIAO and passed without a word
        on the FireBeetle. The same hazard, one board checked, and 216 tests green, because the
        fixture here only ever used one board.

        `boards.PIN_ROLES` is now a closed vocabulary so the names cannot drift again. This
        proves the check actually reaches both, and will fail for any board added without it.
        """
        exercised = 0
        for path in sorted((ROOT / "boards").glob("*.json")):
            if path.name == "active.json":
                continue
            board = json.loads(path.read_text())
            console = (board.get("pin_roles") or {}).get(boards.CONSOLE_UART)
            self.assertIsNotNone(console, "%s names no console UART" % path.stem)
            label = next(l for l, g in board["pins"].items() if g == console["gpio"][0])
            with self.subTest(board=path.stem):
                problems = check_design.check_pin_capability(
                    design({"ref": "Gps", "reads_serial": True,
                            "pins": [{"signal": "TXD", "pin": label}]}), board)
                self.assertEqual(len(problems), 1,
                                 "%s: a serial part on %s was not caught" % (path.stem, label))
            exercised += 1
        self.assertGreater(exercised, 1, "this passed by exercising no board, or only one")

    def test_a_button_on_the_boot_log_pin_is_fine(self):
        # The caveat is real but conditional. A check that forbade this outright would be wrong,
        # and the bin would fail its own regression fixture.
        problems = check_design.check_pin_capability(
            design({"ref": "ModeButton", "pins": [{"signal": "A", "pin": "D6"}]}), BOARD)
        self.assertEqual(problems, [])

    def test_chip_capability_is_intersected_with_what_the_board_exposes(self):
        # The C6 can wake on GPIO0-7; the XIAO brings out only 0, 1 and 2 of them. Checking the
        # chip alone would approve four pins that are not on the header.
        pins = check_design.usable_pins(BOARD)
        # Compared by GPIO, not by label. The XIAO file now records the vendor's function names
        # as second labels for GPIOs it already carried — A0/A1/A2 on 0/1/2, the way the
        # FireBeetle has SS and A4 on GPIO10 — and a label list would grow while the fact under
        # test, "only three of the chip's wake pins are on this header", stays exactly true.
        can_wake = sorted({pin["gpio"] for pin in pins.values() if "wake" in pin["capabilities"]})
        self.assertEqual(can_wake, [0, 1, 2])
        self.assertEqual({name for name, pin in pins.items() if pin["gpio"] in (0, 1, 2)},
                         {"D0", "D1", "D2", "A0", "A1", "A2"})


class BoardResolutionTest(unittest.TestCase):
    """A design should name a board the way a person would, not by where it sits on this disk."""

    def test_a_board_id_resolves_to_a_shipped_definition(self):
        found = check_design.resolve_board("xiao-esp32-c6", Path("/nowhere/design.json"))
        self.assertTrue(found.exists())
        self.assertEqual(json.loads(found.read_text())["id"], "xiao-esp32-c6")

    def test_an_unknown_board_says_which_ones_exist(self):
        with self.assertRaises(SystemExit) as raised:
            check_design.resolve_board("firebeetle2-s3", Path("/nowhere/design.json"))
        self.assertIn("xiao-esp32-c6", str(raised.exception))

    def test_a_path_beside_the_design_still_wins(self):
        found = check_design.resolve_board(
            "boards/xiao-esp32-c6.json", ROOT / "design.json")
        self.assertEqual(found, (ROOT / "boards" / "xiao-esp32-c6.json").resolve())


class I2cAddressTest(unittest.TestCase):
    def test_two_devices_at_one_address_are_caught(self):
        problems = check_design.check_i2c_addresses(design(
            {"ref": "Rangefinder", "i2c": {"bus": "i2c0", "address": "0x29"}},
            {"ref": "SecondSensor", "i2c": {"bus": "i2c0", "address": "0x29"}}))
        self.assertEqual(len(problems), 1)
        self.assertIn("0x29", problems[0].detail)
        self.assertIn("Rangefinder", problems[0].detail)

    def test_the_same_address_on_a_different_bus_is_fine(self):
        problems = check_design.check_i2c_addresses(design(
            {"ref": "Rangefinder", "i2c": {"bus": "i2c0", "address": "0x29"}},
            {"ref": "SecondSensor", "i2c": {"bus": "i2c1", "address": "0x29"}}))
        self.assertEqual(problems, [])


class RealDesignTest(unittest.TestCase):
    def test_the_smart_bin_passes(self):
        """The regression fixture: a known-good design must stay clean."""
        real = json.loads((ROOT / "examples" / "smartbin.design.json").read_text())
        self.assertEqual(check_design.run(real, BOARD), [])


if __name__ == "__main__":
    unittest.main()
