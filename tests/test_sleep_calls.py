"""P1022 slice 3: the deepsleep calls of a project's firmware/, read from its files and never from the board."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from spark.firmware import sleep_calls  # noqa: E402

#: The shape of the firmware of the 13:58 deploy on the FireBeetle 2 C6 (p934-display2, 2026-11-23): two deepsleep calls.
WALK_MAIN = """import machine
import time

def nap(seconds):
    print('deep sleep for %d s' % seconds)
    machine.deepsleep(seconds * 1000)

print('ready, cpu 80 MHz, deep sleep, power-up')
if time.time() > 10:
    machine.deepsleep(1000)
nap(67)
"""


def project_with(**files):
    """A project folder whose firmware/ holds `files`, each name with `__` for `.` and `_slash_` for `/` (lib_slash_a__py)."""
    project = Path(tempfile.mkdtemp())
    for name, text in files.items():
        path = project / "firmware" / name.replace("__", ".").replace("_slash_", "/")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return project


class DeepSleepCallsTest(unittest.TestCase):
    def test_the_walk_s_firmware_gives_both_places_in_line_order(self):
        found = sleep_calls.deep_sleep_calls(project_with(main__py=WALK_MAIN))
        self.assertEqual(found, sleep_calls.SleepCalls(("firmware/main.py:6", "firmware/main.py:10"), ()))

    def test_each_name_bound_to_machine_or_its_deepsleep_counts(self):
        for text in ("import machine as m\nm.deepsleep(1)\n", "from machine import deepsleep as ds\nds(1)\n",
                     "import machine\nds = machine.deepsleep\nds(1)\n", "from machine import deepsleep\ndeepsleep(1)\n"):
            with self.subTest(text=text):
                found = sleep_calls.deep_sleep_calls(project_with(main__py=text))
                self.assertEqual(found.places, ("firmware/main.py:%d" % len(text.splitlines()),))

    def test_a_driver_s_own_deepsleep_a_comment_a_docstring_and_lightsleep_do_not_count(self):
        for text in ("import machine\nEpd().deepsleep()\n", "import machine\nself.epd.deepsleep()\n",
                     "import machine\n# machine.deepsleep(1)\n", '"""machine.deepsleep(1)"""\nimport machine\n',
                     "import machine\nmachine.lightsleep(1)\n", "import machine\ndef f(machine):\n    machine.deepsleep(1)\n",
                     "from machine import deepsleep\ndef deepsleep(ms):\n    pass\ndeepsleep(1)\n"):
            with self.subTest(text=text):
                self.assertEqual(sleep_calls.deep_sleep_calls(project_with(main__py=text)), sleep_calls.SleepCalls((), ()))

    def test_places_sort_by_file_then_by_the_line_as_a_number(self):
        calls = "import machine\n" + "\n" * 8 + "machine.deepsleep(1)\n" + "machine.deepsleep(2)\n"
        found = sleep_calls.deep_sleep_calls(project_with(main__py=calls, lib_slash_a__py="import machine\nmachine.deepsleep(1)\n"))
        self.assertEqual(found.places, ("firmware/lib/a.py:2", "firmware/main.py:10", "firmware/main.py:11"))

    def test_a_file_that_does_not_parse_is_named_and_the_others_still_count(self):
        project = project_with(main__py="import machine\nmachine.deepsleep(1\n", app__py="import machine\nmachine.deepsleep(1)\n",
                               nul__py="x = 1\x00\n")
        self.assertEqual(sleep_calls.deep_sleep_calls(project),
                         sleep_calls.SleepCalls(("firmware/app.py:2",), ("firmware/main.py", "firmware/nul.py")))

    def test_no_firmware_folder_gives_no_call(self):
        self.assertEqual(sleep_calls.deep_sleep_calls(Path(tempfile.mkdtemp())), sleep_calls.SleepCalls((), ()))


if __name__ == "__main__":
    unittest.main()
