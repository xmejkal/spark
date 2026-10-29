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
import os
import subprocess
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import import_child  # noqa: E402
import import_firmware  # noqa: E402
import outcomes  # noqa: E402


STAND_IN = ROOT / "scripts" / "stand_in" / "machine.py"
#: framebuf.py and micropython.py live here: the check puts this folder after the firmware's own.
FALLBACK = STAND_IN.parent / "fallback"
SCRIPT = ROOT / "scripts" / "import_firmware.py"
#: Long enough to see a loop is a loop, short enough for the suite.
LOOP_TIMEOUT_S = "0.5"


def a_stand_in(name="machine"):
    """A fresh copy of one stand-in (machine, micropython or framebuf), with a level table of its own."""
    folder = STAND_IN.parent if name == "machine" else FALLBACK
    spec = importlib.util.spec_from_file_location("stand_in_%s_under_test" % name, folder / (name + ".py"))
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

    def test_any_true_value_is_the_level_one(self):
        led = self.Pin(7, self.Pin.OUT)
        led.value(True)
        self.assertEqual(led.value(), 1)
        led.value(2)
        self.assertEqual(self.machine.level(7), 1)

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

    def test_what_the_stand_in_lacks_is_an_attribute_error_that_names_it(self):
        done = subprocess.run([sys.executable, "-c", "import machine; machine.Timer"], capture_output=True, text=True,
                              env={"PYTHONPATH": str(STAND_IN.parent)})
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("AttributeError", done.stderr)
        self.assertIn("stand-in", done.stderr)
        self.assertIn("move the rest into a function that main.py calls", done.stderr)
        self.assertNotIn("Pin and PWM only", done.stderr)

    def test_a_from_import_of_what_it_lacks_is_an_import_error_through_the_child(self):
        _, answer = answer_for(a_project(light="from machine import UART\n"))
        detail = module_named(answer, "light")["detail"]
        self.assertEqual(module_named(answer, "light")["status"], "raised", answer)
        self.assertTrue(detail.startswith("ImportError: "), detail)
        self.assertIn("scripts/stand_in/machine.py", detail)
        self.assertIn("not UART", detail)
        self.assertIn("move the rest into a function that main.py calls", detail)

    def test_hasattr_and_getattr_with_a_default_see_nothing_for_what_it_lacks(self):
        self.assertFalse(hasattr(self.machine, "UART"))
        self.assertIsNone(getattr(self.machine, "UART", None))

    def test_the_error_lists_the_classes_sorted_and_not_the_helpers(self):
        with self.assertRaises(AttributeError) as caught:
            self.machine.UART
        self.assertIn("has ADC, I2C, I2S, PWM, Pin, SPI, SoftI2C and SoftSPI only, not UART", str(caught.exception))
        self.assertNotIn("set_level", str(caught.exception))


class APwmKeepsWhatWasLastSetTest(unittest.TestCase):
    """P352: walk 1's dimmed LED (`effects.py`) used PWM, and the import check refused it."""

    def setUp(self):
        self.machine = a_stand_in()
        self.PWM, self.Pin = self.machine.PWM, self.machine.Pin

    def test_the_walks_effects_pattern_runs(self):
        led = self.PWM(self.Pin(15), freq=1000, duty_u16=0)
        led.duty_u16(32768)
        self.assertEqual(led.duty_u16(), 32768)
        self.assertEqual(led.freq(), 1000)

    def test_each_setter_keeps_its_value_for_the_getter(self):
        led = self.PWM(self.Pin(15))
        led.freq(500)
        led.duty(512)
        led.duty_ns(1000)
        self.assertEqual((led.freq(), led.duty(), led.duty_ns()), (500, 512, 1000))

    def test_init_sets_what_it_is_given_and_keeps_the_rest(self):
        led = self.PWM(self.Pin(15), freq=1000, duty_u16=100)
        led.init(duty_u16=200)
        self.assertEqual((led.freq(), led.duty_u16()), (1000, 200))

    def test_nothing_set_reads_none(self):
        self.assertIsNone(self.PWM(self.Pin(15)).duty_u16())

    def test_deinit_is_remembered(self):
        led = self.PWM(self.Pin(15))
        self.assertFalse(led.deinited)
        led.deinit()
        self.assertTrue(led.deinited)

    def test_init_after_deinit_turns_it_on_again(self):
        led = self.PWM(self.Pin(15))
        led.deinit()
        led.init(freq=1000)
        self.assertFalse(led.deinited)

    def test_the_frequency_can_be_given_by_position_as_on_the_esp32(self):
        led = self.PWM(self.Pin(15), 1000)
        self.assertEqual(led.freq(), 1000)
        led.init(500)
        self.assertEqual(led.freq(), 500)

    def test_duty_ns_and_invert_are_kept_from_the_constructor(self):
        led = self.PWM(self.Pin(15), freq=1, duty_ns=2, invert=True)
        self.assertEqual(led.duty_ns(), 2)
        led.init(invert=False)
        self.assertEqual(led.settings["invert"], False)

    def test_a_pwm_takes_a_pin_number_too(self):
        self.assertEqual(self.PWM(15, freq=50).freq(), 50)


class TheNewStandInsKeepTheirArgumentsAndReturnFixedValuesTest(unittest.TestCase):
    """P421: no device is modelled; a stand-in never reports one as present."""

    def setUp(self):
        self.machine = a_stand_in()

    def test_an_adc_reads_zero_in_each_form(self):
        pot = self.machine.ADC(self.machine.Pin(34), atten=self.machine.ADC.ATTN_11DB)
        self.assertEqual((pot.read_u16(), pot.read(), pot.read_uv()), (0, 0, 0))
        self.assertIsNone(pot.atten(self.machine.ADC.ATTN_6DB))
        self.assertIsNone(pot.width(self.machine.ADC.WIDTH_12BIT))

    def test_an_spi_read_is_zero_bytes_of_the_length_asked(self):
        for bus in (self.machine.SPI(1, 1000000, sck=1, mosi=2, miso=3), self.machine.SoftSPI(baudrate=1000000)):
            with self.subTest(bus=type(bus).__name__):
                self.assertEqual(bus.read(3), b"\x00\x00\x00")
                self.assertIsNone(bus.write(b"x"))
                self.assertIsNone(bus.write_readinto(b"x", bytearray(1)))

    def test_an_spi_readinto_leaves_the_buffer_as_it_is(self):
        buf = bytearray(b"\x07\x07")
        self.assertIsNone(self.machine.SPI(1).readinto(buf))
        self.assertEqual(buf, bytearray(b"\x07\x07"))

    def test_the_spi_bit_orders_differ(self):
        self.assertNotEqual(self.machine.SPI.MSB, self.machine.SPI.LSB)

    def test_an_i2c_bus_finds_no_device_and_writing_does_not_make_one(self):
        for bus in (self.machine.I2C(0, scl=self.machine.Pin(22), sda=self.machine.Pin(21), freq=400000),
                    self.machine.SoftI2C(scl=self.machine.Pin(22), sda=self.machine.Pin(21))):
            with self.subTest(bus=type(bus).__name__):
                self.assertEqual(bus.scan(), [])
                self.assertEqual(bus.writeto(60, b"ab"), 2)
                self.assertEqual(bus.writeto(60, b"ab", False), 2)
                self.assertEqual(bus.scan(), [])

    def test_an_i2c_read_is_zero_bytes_of_the_length_asked(self):
        bus = self.machine.I2C(0)
        self.assertEqual(bus.readfrom(60, 3), b"\x00\x00\x00")
        self.assertEqual(bus.readfrom_mem(60, 1, 2), b"\x00\x00")
        buf = bytearray(b"\x09")
        self.assertIsNone(bus.readfrom_into(60, buf))
        self.assertIsNone(bus.readfrom_mem_into(60, 1, buf))
        self.assertIsNone(bus.writeto_mem(60, 1, b"x"))
        self.assertEqual(buf, bytearray(b"\x09"))

    def test_an_i2s_write_is_taken_whole_and_a_read_leaves_the_buffer(self):
        speaker = self.machine.I2S(0, sck=1, ws=2, sd=3, mode=self.machine.I2S.TX, bits=16,
                                   format=self.machine.I2S.MONO, rate=22050, ibuf=2000)
        self.assertEqual(speaker.write(bytes(8)), 8)
        buf = bytearray(4)
        self.assertEqual(speaker.readinto(buf), 4)
        self.assertEqual(buf, bytearray(4))

    def test_an_i2s_handler_is_kept_and_never_called(self):
        calls = []
        speaker = self.machine.I2S(0)
        speaker.irq(lambda bus: calls.append(bus))
        speaker.write(b"x")
        self.assertEqual(calls, [])
        self.assertIsNotNone(speaker.handler)

    def test_a_constructor_given_a_keyword_it_does_not_know_does_not_raise(self):
        for cls in (self.machine.ADC, self.machine.SPI, self.machine.I2C, self.machine.I2S):
            with self.subTest(cls=cls.__name__):
                cls(1, nothing_like_this=2)

    def test_deinit_is_remembered_and_init_turns_it_on_again(self):
        for cls in (self.machine.ADC, self.machine.SPI, self.machine.I2C, self.machine.I2S):
            with self.subTest(cls=cls.__name__):
                bus = cls(1)
                self.assertFalse(bus.deinited)
                bus.deinit()
                self.assertTrue(bus.deinited)
                bus.init(1)
                self.assertFalse(bus.deinited)

    def test_a_software_bus_is_the_same_kind_of_stand_in(self):
        self.assertTrue(issubclass(self.machine.SoftSPI, self.machine.SPI))
        self.assertTrue(issubclass(self.machine.SoftI2C, self.machine.I2C))

    def test_an_i2c_vector_write_counts_every_byte_and_the_rest_of_the_bus_calls_run(self):
        for bus in (self.machine.I2C(0), self.machine.SoftI2C(scl=1, sda=2)):
            with self.subTest(bus=type(bus).__name__):
                self.assertEqual(bus.writevto(60, [b"ab", bytearray(3)]), 5)
                self.assertEqual(bus.write(b"abc"), 3)
                buf = bytearray(b"\x05\x05")
                self.assertIsNone(bus.readinto(buf))
                self.assertEqual(buf, bytearray(b"\x05\x05"))
                self.assertIsNone(bus.start())
                self.assertIsNone(bus.stop())

    def test_a_pin_is_called_to_write_and_to_read(self):
        chip_select = self.machine.Pin(5, self.machine.Pin.OUT)
        chip_select(1)
        self.assertEqual(chip_select(), 1)
        chip_select(0)
        self.assertEqual(chip_select.value(), 0)

    def test_a_subclass_may_give_init_other_arguments(self):
        machine = self.machine

        class Sensor(machine.I2C):
            def init(self):
                self.ready = True

        sensor = Sensor(0, scl=1)
        self.assertEqual((sensor.args, sensor.settings), ((0,), {"scl": 1}))
        sensor.init()
        self.assertTrue(sensor.ready)

    def test_each_new_name_imports_on_its_own(self):
        for name in ("ADC", "SPI", "SoftSPI", "I2C", "SoftI2C", "I2S"):
            with self.subTest(name=name):
                done = subprocess.run([sys.executable, "-c", "from machine import " + name], capture_output=True,
                                      text=True, env={"PYTHONPATH": str(STAND_IN.parent)})
                self.assertEqual(done.returncode, 0, done.stderr)


class TheDisplayDriverStandInsTest(unittest.TestCase):
    """P421: `micropython` and `framebuf`, the two a display driver imports besides `machine`."""

    def setUp(self):
        self.framebuf = a_stand_in("framebuf")
        self.micropython = a_stand_in("micropython")

    def test_const_gives_back_its_argument(self):
        self.assertEqual(self.micropython.const(5), 5)

    def test_a_decorator_gives_back_the_function_it_was_given(self):
        def blink():
            pass
        for decorator in (self.micropython.native, self.micropython.viper, self.micropython.bytecode):
            with self.subTest(decorator=decorator.__name__):
                self.assertIs(decorator(blink), blink)

    def test_a_picture_reads_zero_and_draws_nothing(self):
        buf = bytearray(8)
        screen = self.framebuf.FrameBuffer(buf, 8, 8, self.framebuf.MONO_VLSB)
        self.assertEqual(screen.pixel(1, 1), 0)
        self.assertIsNone(screen.pixel(1, 1, 1))
        self.assertEqual(screen.pixel(1, 1), 0)
        for call in (lambda: screen.fill(1), lambda: screen.fill_rect(0, 0, 4, 4, 1), lambda: screen.hline(0, 0, 4, 1),
                     lambda: screen.vline(0, 0, 4, 1), lambda: screen.line(0, 0, 4, 4, 1),
                     lambda: screen.rect(0, 0, 4, 4, 1), lambda: screen.text("hi", 0, 0, c=1),
                     lambda: screen.scroll(1, 0), lambda: screen.blit(screen, 0, 0, 0),
                     lambda: screen.ellipse(4, 4, 2, 2, 1), lambda: screen.poly(0, 0, bytearray(4), 1)):
            self.assertIsNone(call())
        self.assertEqual(buf, bytearray(8))

    MICROPYTHON_HAS = "has alloc_emergency_exception_buf, bytecode, const, native and viper only"
    FRAMEBUF_HAS = "has FrameBuffer, GS2_HMSB, GS4_HMSB, GS8, MONO_HLSB, MONO_HMSB, MONO_VLSB and RGB565 only"

    def test_a_name_the_stand_in_lacks_is_an_attribute_error_with_its_own_file_names_and_action(self):
        for module, statement, have in (
                ("micropython", "import micropython; micropython.opt_level", self.MICROPYTHON_HAS),
                ("framebuf", "import framebuf; framebuf.Nothing", self.FRAMEBUF_HAS)):
            with self.subTest(module=module):
                done = subprocess.run([sys.executable, "-c", statement], capture_output=True, text=True,
                                      env={"PYTHONPATH": str(FALLBACK)})
                self.assertNotEqual(done.returncode, 0)
                self.assertIn("AttributeError", done.stderr)
                self.assertIn("scripts/stand_in/fallback/%s.py" % module, done.stderr)
                self.assertIn(have, done.stderr)
                self.assertIn("move the rest into a function that main.py calls", done.stderr)

    def test_a_from_import_of_what_a_stand_in_lacks_is_an_import_error_through_the_child(self):
        for module, have in (("micropython", self.MICROPYTHON_HAS), ("framebuf", self.FRAMEBUF_HAS)):
            with self.subTest(module=module):
                _, answer = answer_for(a_project(light="from %s import Nothing\n" % module))
                detail = module_named(answer, "light")["detail"]
                self.assertEqual(module_named(answer, "light")["status"], "raised", answer)
                self.assertTrue(detail.startswith("ImportError: "), detail)
                self.assertIn("scripts/stand_in/fallback/%s.py" % module, detail)
                self.assertIn(have, detail)
                self.assertIn("not Nothing", detail)

    def test_hasattr_and_getattr_with_a_default_see_nothing_for_what_they_lack(self):
        for module in (self.framebuf, self.micropython):
            with self.subTest(module=module.__name__):
                self.assertFalse(hasattr(module, "Nothing"))
                self.assertIsNone(getattr(module, "Nothing", None))

    def test_alloc_emergency_exception_buf_keeps_nothing(self):
        self.assertIsNone(self.micropython.alloc_emergency_exception_buf(100))

    def test_a_subclass_may_define_width_as_a_property(self):
        framebuf = self.framebuf

        class Screen(framebuf.FrameBuffer):
            def __init__(self):
                super().__init__(bytearray(8), 8, 8, framebuf.MONO_VLSB)

            @property
            def width(self):
                return 8

        self.assertEqual(Screen().width, 8)

    def test_a_driver_shaped_module_imports(self):
        project = a_project(screen=(
            "from machine import I2C, Pin\nfrom micropython import const\nimport framebuf\n"
            "WIDTH = const(128)\n"
            "class Screen(framebuf.FrameBuffer):\n"
            "    def __init__(self, i2c):\n"
            "        self.i2c, self.buffer = i2c, bytearray(128 * 8)\n"
            "        super().__init__(self.buffer, WIDTH, 64, framebuf.MONO_VLSB)\n"
            "    def show(self):\n"
            "        self.fill(0)\n        self.i2c.writeto(0x3C, self.buffer)\n"
            "Screen(I2C(0, scl=Pin(22), sda=Pin(21))).show()\n"))
        code, answer = answer_for(project)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_OK, outcomes.OK), answer)

    def test_the_ssd1306_shapes_import_when_the_module_builds_the_screen(self):
        """micropython-lib's ssd1306.py: `writevto` on an I2C, `self.cs(1)` and `spi.write` on an SPI, built at once."""
        project = a_project(screen=(
            "from machine import Pin, SoftI2C, SoftSPI\nimport framebuf\n"
            "class Screen(framebuf.FrameBuffer):\n"
            "    def __init__(self, bus, cs):\n"
            "        self.bus, self.cs, self.buffer = bus, cs, bytearray(128 * 8)\n"
            "        self.write_list = [b'\\x40', self.buffer]\n"
            "        super().__init__(self.buffer, 128, 64, framebuf.MONO_VLSB)\n"
            "        self.show()\n"
            "class OnI2C(Screen):\n"
            "    def show(self):\n"
            "        assert self.bus.writevto(0x3C, self.write_list) == 1025\n"
            "class OnSPI(Screen):\n"
            "    def show(self):\n"
            "        self.cs(1)\n        self.cs(0)\n        self.bus.write(self.buffer)\n        self.cs(1)\n"
            "        assert self.cs() == 1\n"
            "OnI2C(SoftI2C(scl=Pin(22), sda=Pin(21)), Pin(5, Pin.OUT))\n"
            "OnSPI(SoftSPI(baudrate=1000000), Pin(6, Pin.OUT))\n"))
        code, answer = answer_for(project)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_OK, outcomes.OK), answer)

    def test_a_driver_of_the_firmware_s_own_framebuf_wins_in_the_firmware_folder_and_in_lib(self):
        for where in ("", "lib"):
            with self.subTest(where=where or "firmware"):
                project = a_project(screen="import framebuf\nassert framebuf.MINE == 1\n")
                folder = project / "firmware" / where
                folder.mkdir(exist_ok=True)
                (folder / "framebuf.py").write_text("MINE = 1\n")
                (folder / "micropython.py").write_text("MINE = 1\n")
                (project / "firmware" / "uses.py").write_text("import micropython\nassert micropython.MINE == 1\n")
                _, answer = answer_for(project)
                self.assertEqual(module_named(answer, "screen")["status"], "imported", answer)
                self.assertEqual(module_named(answer, "uses")["status"], "imported", answer)

    def test_without_a_framebuf_of_its_own_the_firmware_gets_the_stand_in(self):
        project = a_project(screen="import framebuf\nassert 'MINE' not in dir(framebuf)\nframebuf.FrameBuffer\n")
        _, answer = answer_for(project)
        self.assertEqual(module_named(answer, "screen")["status"], "imported", answer)


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
    def test_a_firmware_that_builds_one_of_each_new_class_imports(self):
        project = a_project(parts=(
            "from machine import ADC, I2C, I2S, Pin, SPI, SoftI2C, SoftSPI\n"
            "pot = ADC(Pin(34), atten=ADC.ATTN_11DB)\n"
            "pot.read_u16()\n"
            "spi = SPI(1, baudrate=1000000, sck=Pin(1), mosi=Pin(2), miso=Pin(3))\n"
            "soft = SoftSPI(baudrate=1000000, sck=Pin(1), mosi=Pin(2), miso=Pin(3))\n"
            "spi.write(b'x')\nsoft.read(3)\n"
            "i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)\n"
            "soft_i2c = SoftI2C(scl=Pin(22), sda=Pin(21))\n"
            "i2c.scan()\ni2c.writeto(0x3C, b'x')\nsoft_i2c.scan()\n"
            "speaker = I2S(0, sck=Pin(1), ws=Pin(2), sd=Pin(3), mode=I2S.TX, bits=16, format=I2S.MONO,\n"
            "              rate=22050, ibuf=2000)\n"
            "speaker.write(b'x')\nspeaker.readinto(bytearray(4))\n"
            "for part in (pot, spi, soft, i2c, soft_i2c, speaker):\n"
            "    part.deinit()\n"))
        code, answer = answer_for(project)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_OK, outcomes.OK), answer)

    def test_a_firmware_file_named_like_a_standard_module_does_not_break_the_machine_import(self):
        project = a_project(token="x = 1\n", ast="x = 1\n", tokenize="x = 1\n", linecache="x = 1\n", dis="x = 1\n",
                            light="from machine import ADC, Pin\nADC(Pin(34))\n")
        code, answer = answer_for(project)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_OK, outcomes.OK), answer)

    def test_a_module_that_asks_the_bus_for_a_device_at_module_level_does_not_import(self):
        project = a_project(screen="from machine import I2C\ni2c = I2C(0)\nassert 0x3C in i2c.scan()\n")
        _, answer = answer_for(project)
        self.assertEqual(module_named(answer, "screen")["status"], "raised")
        self.assertIn("AssertionError", module_named(answer, "screen")["detail"])

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

    def test_a_driver_kept_in_firmware_lib_is_found_as_on_the_board(self):
        # F5: MicroPython looks in /lib after the root, and the project's firmware/ is uploaded as the root.
        project = a_project(light="import driver\nlevel = driver.LEVEL\n")
        (project / "firmware" / "lib").mkdir()
        (project / "firmware" / "lib" / "driver.py").write_text("LEVEL = 1\n")
        code, answer = answer_for(project)
        self.assertEqual(code, outcomes.EXIT_OK, answer)
        self.assertEqual([entry["module"] for entry in answer["modules"]], ["light"], "a driver is not firmware to import")

    def test_main_py_is_left_unrun(self):
        project = a_project(main="open('main-ran', 'w').close()\n", light="x = 1\n")
        code, answer = answer_for(project)
        self.assertEqual(code, outcomes.EXIT_OK, answer)
        self.assertEqual([entry["module"] for entry in answer["modules"]], ["light"])
        self.assertFalse(list(project.rglob("main-ran")), "main.py ran")

    def test_boot_py_is_left_unrun_too(self):
        project = a_project(boot="open('boot-ran', 'w').close()\n", light="x = 1\n")
        code, answer = answer_for(project)
        self.assertEqual(code, outcomes.EXIT_OK, answer)
        self.assertEqual([entry["module"] for entry in answer["modules"]], ["light"])
        self.assertFalse(list(project.rglob("boot-ran")), "boot.py ran")

    def test_importing_leaves_no_bytecode_in_the_person_s_folder(self):
        project = a_project(light="x = 1\n")
        with mock.patch.dict(os.environ):  # the suite may run with bytecode off already; the command must not rely on it
            for variable in ("PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX"):
                os.environ.pop(variable, None)
            answer_for(project)
        self.assertFalse((project / "firmware" / "__pycache__").exists())

    def test_a_module_opens_its_files_from_the_firmware_folder_as_on_the_board(self):
        project = a_project(light="settings = open('config.json').read()\n")
        (project / "firmware" / "config.json").write_text("{}")
        code, answer = answer_for(project)
        self.assertEqual(code, outcomes.EXIT_OK, answer)

    def test_the_project_defaults_to_the_folder_it_runs_in(self):
        project = a_project(light="x = 1\n")
        done = subprocess.run([sys.executable, str(SCRIPT), "--json"], cwd=str(project), capture_output=True, text=True)
        self.assertEqual((done.returncode, json.loads(done.stdout)["status"]), (outcomes.EXIT_OK, outcomes.OK), done.stderr)


class TheCommandRunsFromWhereTheyAreTest(unittest.TestCase):
    def test_the_default_project_puts_the_firmware_folder_on_the_path_by_its_whole_name(self):
        # F2: with `.` the folder was a relative path and the child ran inside it, so the entry named nothing. Imports
        # worked only because `-c` adds '' to the path, and PYTHONSAFEPATH=1 (Python 3.11 and later) takes that away.
        project = a_project(light="import os, sys\nassert os.getcwd() in sys.path, sys.path\n")
        done = subprocess.run([sys.executable, str(SCRIPT), "--json"], cwd=str(project), capture_output=True, text=True,
                              env=dict(os.environ, PYTHONSAFEPATH="1"))
        self.assertEqual(done.returncode, outcomes.EXIT_OK, done.stdout + done.stderr)

    def test_a_module_that_asks_for_input_does_not_read_the_callers_pipe(self):
        # F6: an input() at module level took the line the caller piped in. On the board nobody types at import.
        project = a_project(light="answer = input()\n")
        done = subprocess.run([sys.executable, str(SCRIPT), "--json"], cwd=str(project), input="typed\n",
                              capture_output=True, text=True)
        answer = json.loads(done.stdout)
        self.assertEqual(done.returncode, outcomes.EXIT_PROBLEMS, answer)
        self.assertEqual(module_named(answer, "light")["detail"], "EOFError: EOF when reading a line")


class TheChildIsAFileOfItsOwnTest(unittest.TestCase):
    """P443: the child that imports one module is scripts/import_child.py, run with -I."""

    def test_a_firmware_cannot_import_the_child_file(self):
        project = a_project(light="import import_child\n")
        _, answer = answer_for(project)
        self.assertEqual(module_named(answer, "light")["status"], "raised", answer)
        self.assertIn("No module named 'import_child'", module_named(answer, "light")["detail"])

    def test_the_child_imports_the_module_from_the_folders_given(self):
        project = a_project(light="import sys\nassert sys.path[0].endswith('first'), sys.path\n")
        done = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "scripts" / "import_child.py"), "light",
                               str(project / "first"), str(project / "firmware")], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)


class TheChildGivesTimeMicroPythonsNamesTest(unittest.TestCase):
    """P443: micropython-lib's SSD1306_SPI sleeps in its constructor, and a driver builds it at module level."""

    def test_the_six_names_are_set_with_their_fixed_values(self):
        fake = types.ModuleType("fake_time")
        import_child.add_micropython_time(fake)
        self.assertIsNone(fake.sleep_ms(10_000))
        self.assertIsNone(fake.sleep_us(10_000_000))
        self.assertEqual((fake.ticks_ms(), fake.ticks_us()), (0, 0))
        self.assertEqual(fake.ticks_add(5, 3), 8)
        self.assertEqual(fake.ticks_diff(8, 5), 3)
        self.assertEqual(fake.ticks_diff(5, 8), -3)

    def test_this_process_s_own_time_is_left_alone(self):
        """Importing the child file, as the top of this file did, patches nothing."""
        import_child.add_micropython_time(types.ModuleType("fake_time"))
        self.assertFalse(hasattr(time, "sleep_ms"))

    def test_the_ssd1306_spi_shape_built_at_module_level_imports(self):
        """micropython-lib's ssd1306.py: a reset pin, `time.sleep_ms(1)` and `sleep_ms(10)`, a FrameBuffer subclass."""
        project = a_project(screen=(
            "import time\nfrom machine import Pin, SoftSPI\nimport framebuf\n"
            "class SSD1306_SPI(framebuf.FrameBuffer):\n"
            "    def __init__(self, spi, dc, res, cs):\n"
            "        dc.init(dc.OUT, value=0)\n        res.init(res.OUT, value=0)\n        cs.init(cs.OUT, value=1)\n"
            "        self.spi, self.buffer = spi, bytearray(128 * 8)\n"
            "        super().__init__(self.buffer, 128, 64, framebuf.MONO_VLSB)\n"
            "        self.reset(res)\n"
            "    def reset(self, res):\n"
            "        res(1)\n        time.sleep_ms(1)\n        res(0)\n        time.sleep_ms(10)\n        res(1)\n"
            "screen = SSD1306_SPI(SoftSPI(baudrate=1000000), Pin(1), Pin(2), Pin(3))\n"))
        code, answer = answer_for(project)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_OK, outcomes.OK), answer)

    def test_a_long_sleep_at_import_does_not_wait(self):
        project = a_project(slow="import time\ntime.sleep_ms(10_000)\ntime.sleep_us(10_000_000)\n")
        _, answer = answer_for(project, "--timeout", LOOP_TIMEOUT_S)
        self.assertEqual(module_named(answer, "slow")["status"], "imported", answer)

    def test_a_wait_on_ticks_ms_times_out_because_it_is_always_zero(self):
        project = a_project(wait=("import time\nstart = time.ticks_ms()\n"
                                  "while time.ticks_diff(time.ticks_ms(), start) < 100:\n    pass\n"))
        _, answer = answer_for(project, "--timeout", LOOP_TIMEOUT_S)
        self.assertEqual(module_named(answer, "wait")["status"], "timed out", answer)

    def test_real_time_stays_real(self):
        project = a_project(clock="import time\nassert time.time() > 1e9\ntime.sleep(0.01)\n")
        _, answer = answer_for(project)
        self.assertEqual(module_named(answer, "clock")["status"], "imported", answer)


class TheChildGivesBackAStandInsWordsTest(unittest.TestCase):
    """P443: `hasattr` sees an AttributeError, and `from X import name` still says why in an ImportError."""

    def detail_of(self, source):
        _, answer = answer_for(a_project(light=source))
        return module_named(answer, "light")["status"], module_named(answer, "light")["detail"]

    def test_the_ssd1306_spi_shape_with_its_exception_buffer_imports(self):
        project = a_project(screen=(
            "import micropython\nimport time\nfrom machine import Pin, SoftSPI\nimport framebuf\n"
            "micropython.alloc_emergency_exception_buf(100)\n"
            "class SSD1306_SPI(framebuf.FrameBuffer):\n"
            "    def __init__(self, spi, res):\n"
            "        self.spi, self.buffer = spi, bytearray(128 * 8)\n"
            "        super().__init__(self.buffer, 128, 64, framebuf.MONO_VLSB)\n"
            "        res(1)\n        time.sleep_ms(1)\n        res(0)\n        time.sleep_ms(10)\n        res(1)\n"
            "screen = SSD1306_SPI(SoftSPI(baudrate=1000000), Pin(1, Pin.OUT))\n"))
        code, answer = answer_for(project)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_OK, outcomes.OK), answer)

    def test_a_probe_for_a_name_a_stand_in_lacks_imports_for_all_three_stand_ins(self):
        source = ("import framebuf, machine, micropython\n"
                  "for module in (framebuf, machine, micropython):\n"
                  "    assert not hasattr(module, 'Nothing')\n"
                  "    assert getattr(module, 'Nothing', None) is None\n")
        self.assertEqual(self.detail_of(source), ("imported", ""))

    def test_a_probe_and_then_a_from_import_names_the_name_of_the_from_import(self):
        status, detail = self.detail_of("import machine\nhasattr(machine, 'Timer')\nfrom machine import UART\n")
        self.assertEqual(status, "raised")
        self.assertIn("not UART", detail)
        self.assertNotIn("Timer", detail)

    def test_a_dunder_miss_clears_the_name_remembered_so_it_gives_the_plain_error(self):
        status, detail = self.detail_of("import machine\nhasattr(machine, 'UART')\nfrom machine import __version__\n")
        self.assertEqual(status, "raised")
        self.assertIn("cannot import name '__version__'", detail)
        self.assertNotIn("stand-in", detail)

    def test_a_from_import_of_a_good_name_and_a_missing_one_still_gets_the_words(self):
        status, detail = self.detail_of("from machine import Pin, UART\n")
        self.assertEqual(status, "raised")
        self.assertIn("not UART", detail)

    def test_a_firmware_module_with_a_missed_of_its_own_keeps_the_plain_error(self):
        for own in ("0", "[]", "'ab'", "('x', 'y')"):
            with self.subTest(own=own):
                project = a_project(fw="_missed = %s\n" % own, light="from fw import nope\n")
                _, answer = answer_for(project)
                self.assertEqual(module_named(answer, "light")["status"], "raised", answer)
                self.assertIn("cannot import name 'nope'", module_named(answer, "light")["detail"])

    def test_an_import_error_of_the_firmware_s_own_keeps_its_words(self):
        for source, said in (("from nothere import x\n", "No module named 'nothere'"),
                             ("raise ImportError('plain')\n", "ImportError: plain"),
                             ("import machine\nraise ImportError('plain', name='machine')\n", "ImportError: plain")):
            with self.subTest(source=source):
                status, detail = self.detail_of(source)
                self.assertEqual(status, "raised")
                self.assertIn(said, detail)

    def test_one_miss_is_handed_back_once(self):
        module = a_stand_in("machine")
        sys.modules["stand_in_machine_under_test"] = module
        try:
            error = ImportError("cannot import name", name="stand_in_machine_under_test")
            self.assertIsNone(import_child.words_of_stand_in(error))
            getattr(module, "Nothing", None)
            self.assertIn("not Nothing", import_child.words_of_stand_in(error))
            self.assertIsNone(import_child.words_of_stand_in(error))
        finally:
            del sys.modules["stand_in_machine_under_test"]

    def test_an_error_with_no_name_or_a_module_that_is_not_loaded_has_no_words(self):
        self.assertIsNone(import_child.words_of_stand_in(ImportError("plain")))
        self.assertIsNone(import_child.words_of_stand_in(ImportError("plain", name="not_loaded_anywhere")))

    def test_each_stand_in_remembers_a_miss_and_a_dunder_clears_it(self):
        for name in ("machine", "framebuf", "micropython"):
            with self.subTest(stand_in=name):
                module = a_stand_in(name)
                self.assertIsNone(module._missed)
                self.assertIsNone(getattr(module, "__spark__", None))
                self.assertIsNone(module._missed)
                self.assertIsNone(getattr(module, "Nothing", None))
                self.assertEqual(module._missed[0], "Nothing")
                self.assertIn("not Nothing", module._missed[1])
                self.assertIsNone(getattr(module, "__spark__", None))
                self.assertIsNone(module._missed)


class AModuleThatFailsIsAProblemTest(unittest.TestCase):
    def test_a_module_that_raises_says_the_exception_s_last_line(self):
        project = a_project(light="raise ValueError('no such pin')\n", pins="BUTTON = 4\n")
        code, answer = answer_for(project)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_PROBLEMS, outcomes.PROBLEMS), answer)
        self.assertEqual(module_named(answer, "light")["status"], "raised")
        self.assertEqual(module_named(answer, "light")["detail"], "ValueError: no such pin")
        self.assertEqual(module_named(answer, "pins")["status"], "imported", "one bad module hid the other")

    def test_the_timeout_is_the_one_asked_for(self):
        project = a_project(slow="import time\ntime.sleep(3)\n")
        _, answer = answer_for(project, "--timeout", LOOP_TIMEOUT_S)
        self.assertEqual(module_named(answer, "slow")["status"], "timed out")
        self.assertIn("within 0.5 s", module_named(answer, "slow")["detail"])

    def test_a_name_the_stand_in_lacks_names_the_stand_in(self):
        project = a_project(light="from machine import UART\n")
        _, answer = answer_for(project)
        self.assertIn("stand-in", module_named(answer, "light")["detail"])

    def test_a_module_that_dims_an_led_with_pwm_imports(self):
        project = a_project(effects="from machine import Pin, PWM\n"
                                    "led = PWM(Pin(15), freq=1000)\nled.duty_u16(32768)\n")
        _, answer = answer_for(project)
        self.assertEqual(module_named(answer, "effects")["status"], "imported")

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

    def test_a_comment_only_boot_py_does_not_make_a_main_py_with_the_loop_importable(self):
        # F4, irrigation's exact case: the stock boot.py is comments, and the loop is still in main.py.
        project = a_project(boot="# boot.py -- run on boot-up\n", pins="BUTTON = 4\n", main="while True:\n    pass\n")
        code, answer = answer_for(project)
        self.assertEqual(code, outcomes.EXIT_PROBLEMS, answer)
        self.assertIn("move the code out of main.py", answer["problems"][0])
        self.assertEqual([entry["module"] for entry in answer["modules"]], ["pins"])

    def test_an_empty_firmware_folder_is_the_same_problem(self):
        code, answer = answer_for(a_project())
        self.assertEqual(code, outcomes.EXIT_PROBLEMS, answer)


def with_package(project, name, init="x = 1\n"):
    """firmware/NAME/__init__.py: the shape of the bin's firmware, a two-line main.py over a package."""
    (project / "firmware" / name).mkdir()
    (project / "firmware" / name / "__init__.py").write_text(init)
    return project


class APackageIsFirmwareToo(unittest.TestCase):
    def test_a_package_is_imported_by_its_folder_name(self):
        project = with_package(a_project(main="import smartbin\n", pins="BUTTON = 4\n"), "smartbin")
        code, answer = answer_for(project)
        self.assertEqual((code, answer["status"]), (outcomes.EXIT_OK, outcomes.OK), answer)
        self.assertEqual(module_named(answer, "smartbin")["status"], "imported")

    def test_a_package_that_raises_is_a_problem_beside_flat_modules_that_import(self):
        project = with_package(a_project(light="x = 1\n"), "smartbin", init="raise OSError('no bus')\n")
        code, answer = answer_for(project)
        self.assertEqual(code, outcomes.EXIT_PROBLEMS, answer)
        self.assertEqual(module_named(answer, "smartbin")["detail"], "OSError: no bus")
        self.assertEqual(module_named(answer, "light")["status"], "imported")

    def test_a_folder_with_no_init_is_not_firmware(self):
        project = a_project(light="x = 1\n")
        (project / "firmware" / "data").mkdir()
        (project / "firmware" / "data" / "table.py").write_text("raise ValueError\n")
        _, answer = answer_for(project)
        self.assertEqual([entry["module"] for entry in answer["modules"]], ["light"])


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
        for said in ("usage:", "main.py", "stand-in", "--timeout", "--json", "ADC", "I2S", "framebuf",
                     "sleep_ms", "proves that the names exist and the module-level calls ran"):
            self.assertIn(said, done.stdout)
        self.assertNotIn("nothing else", done.stdout)


if __name__ == "__main__":
    unittest.main()
