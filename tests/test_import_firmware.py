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

import import_firmware  # noqa: E402
import outcomes  # noqa: E402


STAND_IN = ROOT / "scripts" / "stand_in" / "machine.py"
SCRIPT = ROOT / "scripts" / "import_firmware.py"
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


def a_project(**modules):
    """A project whose firmware/ holds one file per keyword (`light="..."` is firmware/light.py); returns the project."""
    project = Path(tempfile.mkdtemp()) / "project"
    (project / "firmware").mkdir(parents=True)
    for name, source in modules.items():
        (project / "firmware" / (name + ".py")).write_text(source)
    return project


def run_command(*argv):
    """import_firmware.main in this process, as (exit code, stdout); each module still imports in a process of its own."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = import_firmware.main([str(argument) for argument in argv])
    return code, out.getvalue()


def answer_for(project, *flags):
    code, out = run_command(project, "--json", *flags)
    return code, json.loads(out)


def module_named(answer, name):
    return next(entry for entry in answer["modules"] if entry["module"] == name)


class AModuleThatImportsIsOkTest(unittest.TestCase):
    def test_a_module_that_uses_the_stand_in_imports(self):
        project = a_project(light="import machine\nled = machine.Pin(3, machine.Pin.OUT)\n")
        code, answer = answer_for(project)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_OK, outcomes.OK), answer)
        self.assertEqual(module_named(answer, "light")["status"], "imported")

    def test_a_module_may_import_its_neighbour_in_firmware(self):
        project = a_project(pins="BUTTON = 4\n", light="import pins\nBUTTON = pins.BUTTON\n")
        code, answer = answer_for(project)
        self.assertEqual(code, outcomes.EXIT_OK, answer)
        self.assertEqual(sorted(entry["module"] for entry in answer["modules"]), ["light", "pins"])

    def test_main_py_is_left_unrun(self):
        project = a_project(main="open('main-ran', 'w').close()\n", light="x = 1\n")
        code, answer = answer_for(project)
        self.assertEqual(code, outcomes.EXIT_OK, answer)
        self.assertEqual([entry["module"] for entry in answer["modules"]], ["light"])
        self.assertFalse(list(project.rglob("main-ran")), "main.py ran")

    def test_importing_leaves_no_bytecode_in_the_person_s_folder(self):
        project = a_project(light="x = 1\n")
        answer_for(project)
        self.assertFalse((project / "firmware" / "__pycache__").exists())

    def test_the_project_defaults_to_the_folder_it_runs_in(self):
        project = a_project(light="x = 1\n")
        done = subprocess.run([sys.executable, str(SCRIPT), "--json"], cwd=str(project), capture_output=True, text=True)
        self.assertEqual((done.returncode, json.loads(done.stdout)["status"]), (outcomes.EXIT_OK, outcomes.OK), done.stderr)


class AModuleThatFailsIsAProblemTest(unittest.TestCase):
    def test_a_module_that_raises_says_the_exception_s_last_line(self):
        project = a_project(light="raise ValueError('no such pin')\n", pins="BUTTON = 4\n")
        code, answer = answer_for(project)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_PROBLEMS, outcomes.PROBLEMS), answer)
        self.assertEqual(module_named(answer, "light")["status"], "raised")
        self.assertEqual(module_named(answer, "light")["detail"], "ValueError: no such pin")
        self.assertEqual(module_named(answer, "pins")["status"], "imported", "one bad module hid the other")

    def test_a_module_that_needs_more_than_pin_is_named_as_the_stand_in_s_limit(self):
        project = a_project(light="from machine import PWM\n")
        _, answer = answer_for(project)
        self.assertIn("stand-in", module_named(answer, "light")["detail"])

    def test_a_module_that_loops_at_import_is_cut_off_and_told_to_use_a_function(self):
        project = a_project(spin="while True:\n    pass\n", pins="BUTTON = 4\n")
        code, answer = answer_for(project, "--timeout", LOOP_TIMEOUT_S)
        self.assertEqual(code, outcomes.EXIT_PROBLEMS, answer)
        self.assertEqual(module_named(answer, "spin")["status"], "timed out")
        self.assertIn("function that main.py calls", module_named(answer, "spin")["detail"])
        self.assertEqual(module_named(answer, "pins")["status"], "imported")

    def test_a_folder_with_only_main_py_cannot_be_imported(self):
        project = a_project(main="while True:\n    pass\n")
        code, answer = answer_for(project)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_PROBLEMS, outcomes.PROBLEMS), answer)
        self.assertIn("main.py", answer["problems"][0])
        self.assertIn("move the code out of main.py", answer["problems"][0])

    def test_main_py_and_the_pin_map_alone_are_the_same_problem(self):
        project = a_project(main="while True:\n    pass\n", pins="BUTTON = 4\n")
        code, answer = answer_for(project)
        self.assertEqual(code, outcomes.EXIT_PROBLEMS, answer)
        self.assertIn("move the code out of main.py", answer["problems"][0])

    def test_an_empty_firmware_folder_is_the_same_problem(self):
        code, answer = answer_for(a_project())
        self.assertEqual(code, outcomes.EXIT_PROBLEMS, answer)


class WhenItCannotLookTest(unittest.TestCase):
    def test_no_firmware_folder_is_could_not_run_not_a_pass(self):
        empty = Path(tempfile.mkdtemp())
        code, answer = answer_for(empty)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_COULD_NOT_RUN, outcomes.COULD_NOT_RUN), answer)
        self.assertIn("firmware", answer["unchecked"][0])

    def test_the_text_answer_names_each_module_and_the_verdict(self):
        project = a_project(light="x = 1\n", broken="raise KeyError('k')\n")
        code, out = run_command(project)
        self.assertEqual(code, outcomes.EXIT_PROBLEMS, out)
        self.assertRegex(out, r"imported\s+light")
        self.assertRegex(out, r"raised\s+broken")

    def test_the_json_keeps_its_shape(self):
        _, answer = answer_for(a_project(light="x = 1\n"))
        self.assertEqual(sorted(answer), ["modules", "problems", "status", "tool", "unchecked"])
        self.assertEqual(sorted(answer["modules"][0]), ["detail", "module", "status"])

    def test_help_says_what_it_does_and_leaves_alone(self):
        done = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        for said in ("usage:", "main.py", "stand-in", "--timeout", "--json"):
            self.assertIn(said, done.stdout)


if __name__ == "__main__":
    unittest.main()
