"""
A project's firmware imports on the Mac without running (P59, #7): the `machine` stand-in, and the one command that
imports each firmware module with it.

    python3 -m unittest tests.test_import_firmware

The stand-in is loaded under a name of its own, never as `machine`, so this process's sys.modules stays clean. The command
runs in a subprocess per module, as it does for a person; a looping module is given half a second to loop in.
"""

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


STAND_IN = ROOT / "scripts" / "stand_in" / "machine.py"
SCRIPT = ROOT / "scripts" / "import_firmware.py"
#: Long enough to see a loop is a loop, short enough for the suite.
LOOP_TIMEOUT_S = "0.5"


def a_stand_in():
    """A fresh copy of the stand-in, with a level table of its own."""
    spec = importlib.util.spec_from_file_location("stand_in_machine_under_test", STAND_IN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ThePinsRememberTheirLevelsTest(unittest.TestCase):
    def setUp(self):
        self.machine = a_stand_in()
        self.Pin = self.machine.Pin

    def test_a_pin_reads_back_what_was_written(self):
        led = self.Pin(7, self.Pin.OUT)
        led.value(1)
        self.assertEqual(led.value(), 1)
        led.value(0)
        self.assertEqual(led.value(), 0)

    def test_on_and_off_write_one_and_zero(self):
        led = self.Pin(7, self.Pin.OUT)
        led.on()
        self.assertEqual(led.value(), 1)
        led.off()
        self.assertEqual(led.value(), 0)

    def test_two_objects_for_one_gpio_share_a_level(self):
        self.Pin(5, self.Pin.OUT).value(1)
        self.assertEqual(self.Pin(5, self.Pin.IN).value(), 1)

    def test_a_different_gpio_has_a_level_of_its_own(self):
        self.Pin(5, self.Pin.OUT).value(1)
        self.assertEqual(self.Pin(6, self.Pin.OUT).value(), 0)

    def test_a_value_given_at_construction_is_the_level(self):
        self.assertEqual(self.Pin(5, self.Pin.OUT, value=1).value(), 1)

    def test_an_input_nothing_set_reads_one_with_a_pull_up_and_zero_without(self):
        self.assertEqual(self.Pin(1, self.Pin.IN, self.Pin.PULL_UP).value(), 1)
        self.assertEqual(self.Pin(2, self.Pin.IN, self.Pin.PULL_DOWN).value(), 0)
        self.assertEqual(self.Pin(3, self.Pin.IN).value(), 0)

    def test_the_outside_world_drives_an_input(self):
        button = self.Pin(4, self.Pin.IN, self.Pin.PULL_UP)
        self.machine.set_level(4, 0)
        self.assertEqual(button.value(), 0)
        self.machine.set_level(4, 1)
        self.assertEqual(button.value(), 1)

    def test_level_says_what_the_firmware_last_wrote(self):
        self.Pin(9, self.Pin.OUT).value(1)
        self.assertEqual(self.machine.level(9), 1)
        self.Pin(9, self.Pin.OUT).value(0)
        self.assertEqual(self.machine.level(9), 0)

    def test_level_is_none_while_nothing_wrote_or_set_the_pin(self):
        self.Pin(9, self.Pin.OUT)
        self.assertIsNone(self.machine.level(9))

    def test_an_irq_handler_is_remembered_and_never_called(self):
        calls = []
        button = self.Pin(4, self.Pin.IN)
        button.irq(handler=lambda pin: calls.append(pin), trigger=self.Pin.IRQ_FALLING)
        self.machine.set_level(4, 1)
        self.assertEqual(calls, [])

    def test_init_reconfigures_the_pin(self):
        button = self.Pin(4)
        button.init(self.Pin.IN, self.Pin.PULL_UP)
        self.assertEqual(button.value(), 1)

    def test_what_the_stand_in_lacks_is_an_import_error_that_names_it(self):
        for statement in ("from machine import PWM", "import machine; machine.I2C"):
            with self.subTest(statement=statement):
                done = subprocess.run([sys.executable, "-c", statement], capture_output=True, text=True,
                                      env={"PYTHONPATH": str(STAND_IN.parent)})
                self.assertNotEqual(done.returncode, 0)
                self.assertIn("ImportError", done.stderr)
                self.assertIn("stand-in", done.stderr)
                self.assertIn("Pin only", done.stderr)


if __name__ == "__main__":
    unittest.main()
