"""P254 (#266): the XIAO C6's USB and flash pins are recorded with their sources, and code for a live try that writes
one of their numbers is refused with the pin, its role and its source."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import boards  # noqa: E402
from restricted_pins import RestrictedPins, whole_numbers_in  # noqa: E402

C6 = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())


class TheRecordTest(unittest.TestCase):
    def test_the_c6_records_its_usb_and_flash_pins(self):
        roles = C6["pin_roles"]
        self.assertEqual((roles["usb"]["gpio"], roles["flash"]["gpio"]), ([12, 13], [24, 25, 26, 27, 28, 29, 30]))

    def test_both_roles_are_in_the_vocabulary_and_the_record_is_valid(self):
        self.assertLessEqual({"usb", "flash"}, set(boards.PIN_ROLES))
        self.assertEqual(boards.validate(C6, ROOT / "boards" / "xiao-esp32-c6.json"), [])


class RefusalTest(unittest.TestCase):
    def setUp(self):
        self.pins = RestrictedPins.from_board(C6)

    def refused(self, code):
        return self.pins.why_refused(code)

    def test_a_usb_pin_is_refused_with_its_role_and_source(self):
        why = self.refused("from machine import Pin\nPin(12, Pin.OUT).value(1)")
        self.assertIn("it writes the number 12 (any number, not only a pin), and GPIO12 is this board's usb pin", why)
        self.assertIn("v1.5", why)
        self.assertIn("page 23", why)

    def test_the_flash_pins_are_refused(self):
        for gpio in (24, 30):
            self.assertIn("GPIO%d is this board's flash pin" % gpio, self.refused("Pin(%d)" % gpio))
        self.assertIn("page 32", self.refused("Pin(24)"))

    def test_every_way_to_write_the_number_is_refused(self):
        for code in ("USB = 12\nPin(USB)", "from machine import Pin as P\nP(12)", "Pin(0x0C)", "UART(1, tx=13)",
                     "Pin(-12)", "from micropython import const\nLED = const(12)", "machine.Pin(id=13)"):
            self.assertIsNotNone(self.refused(code), code)

    def test_the_lowest_restricted_number_is_named(self):
        self.assertIn("GPIO13", self.refused("Pin(30)\nPin(13)"))

    def test_other_pins_and_numbers_pass(self):
        for code in ("Pin(15, Pin.OUT)", "Pin(2)", "Pin(1)", "Pin(120)", "print('GPIO12')", "x = True"):
            self.assertIsNone(self.refused(code), code)

    def test_it_refuses_too_much_on_purpose(self):
        self.assertIsNotNone(self.refused("import time\ntime.sleep(12)"))
        self.assertIsNotNone(self.refused("i2c.readfrom(0x1C, 1)"))

    def test_a_number_computed_at_run_time_passes(self):
        self.assertIsNone(self.refused("Pin(6 * 2)"))

    def test_code_that_does_not_parse_is_refused(self):
        self.assertEqual(self.refused("Pin(12"), "the code does not parse as Python, so spark cannot tell which pins it names")

    def test_code_too_deep_to_parse_is_refused_not_a_crash(self):
        self.assertIn("does not parse", self.refused("x = " + "[" * 100000 + "]" * 100000))

    def test_a_viper_function_parses(self):
        self.assertIsNone(self.refused("import micropython\n@micropython.viper\ndef f(x: int) -> int:\n    return x"))


class NoRolesTest(unittest.TestCase):
    def test_a_record_with_no_restricted_pins_refuses_nothing_and_says_so(self):
        pins = RestrictedPins.from_board({"pin_roles": {"strapping": {"gpio": [12], "note": "x"}}})
        self.assertTrue(pins.has_none())
        self.assertIsNone(pins.why_refused("Pin(12)"))
        self.assertFalse(RestrictedPins.from_board(C6).has_none())

    def test_a_broken_record_is_an_error_not_a_pass(self):
        for spec in ({"gpio": "12", "note": "x"}, {"gpio": 12, "note": "x"}, {"gpio": [12], "note": ""},
                     {"gpio": [12]}, ["12"], {"gpio": [12.0], "note": "x"}):
            with self.assertRaises(ValueError, msg=repr(spec)):
                RestrictedPins.from_board({"id": "b", "pin_roles": {"usb": spec}})

    def test_the_flash_note_names_the_page_that_maps_the_gpios(self):
        self.assertIn("page 20, Table 2-4", C6["pin_roles"]["flash"]["note"])

    def test_whole_numbers_in(self):
        self.assertEqual(whole_numbers_in("a = 3\nb = -4\nc = 'x5'\nd = False"), {3, 4})
        self.assertIsNone(whole_numbers_in("def"))


if __name__ == "__main__":
    unittest.main()
