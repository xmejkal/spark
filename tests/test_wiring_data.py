"""
The wiring of one build as data (P826, #1184): the numbered steps and what must be true before power is applied, which a
page reads, equal to what breadboard.md prints. The expected sheets of the fixtures are the reference, never a
renderer's output.

    python3 -m unittest tests.test_wiring_data
"""

import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard import before_power  # noqa: E402
from spark.breadboard import breadboard_codes  # noqa: E402
from spark.breadboard import sheet  # noqa: E402

FIXTURES = ROOT / "tests" / "data" / "breadboard"


def in_store(home):
    return mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})


def a_copy(name):
    """A fixture project in a folder of its own."""
    project = Path(tempfile.mkdtemp()) / name
    shutil.copytree(FIXTURES / name, project)
    return project


def expected_steps(text):
    """[(number, words)] of the numbered lines under "### Steps" of a sheet."""
    section = text.split("### Steps", 1)[1].split("### Diagram", 1)[0]
    return [(int(found.group(1)), found.group(2)) for found in re.finditer(r"^(\d+)\. (.*)$", section, re.MULTILINE)]


def expected_before_power(text):
    """The lines of a sheet's "Before you power it" section, after its heading's blank line."""
    return text.split("## Before you power it\n\n", 1)[1].rstrip("\n").split("\n")


class TheDataReadsAsTheSheetTest(unittest.TestCase):
    """On both fixtures: the steps and the before-power lines equal the expected sheet's, line for line."""

    def test_the_steps_and_the_before_power_lines_equal_the_sheet_s(self):
        for name in ("motor", "button-light"):
            with self.subTest(fixture=name):
                project = a_copy(name)
                with in_store(Path(tempfile.mkdtemp())):
                    data = sheet.wiring_data(project / "requirements.json")
                expected = (FIXTURES / name / "breadboard.expected.md").read_text()
                self.assertEqual([(step.number, step.words) for step in data.steps], expected_steps(expected))
                self.assertEqual(before_power.BeforePowerList().render(data.before_power), expected_before_power(expected))


class TheMotorDataTest(unittest.TestCase):
    """The motor fixture holds every kind, and the tactile button twice, so its host requirements are said once."""

    @classmethod
    def setUpClass(cls):
        with in_store(Path(tempfile.mkdtemp())):
            cls.data = sheet.wiring_data(a_copy("motor") / "requirements.json")
        cls.items = cls.data.before_power.items

    def test_each_item_reads_as_the_expected_section(self):
        # Written from the "Before you power it" section of motor/breadboard.expected.md.
        l9110s, inlet, button = "L9110S dual motor driver module", "JST PH 2-pin power inlet", "6x6 mm tactile push button"
        self.assertEqual([(item.kind, item.subject, item.pin, item.record) for item in self.items], [
            (before_power.OFF_BOARD_SUPPLY, "MOTOR6V", None, None),
            (before_power.CONFLICT, "L9110sModule", "AIA", "l9110s-module"),
            (before_power.CONFLICT, "L9110sModule", "AIB", "l9110s-module"),
            (before_power.UNUSED_PIN, "L9110sModule", "BIA", "l9110s-module"),
            (before_power.UNUSED_PIN, "L9110sModule", "BIB", "l9110s-module"),
            (before_power.HOST_REQUIREMENT, l9110s, None, "l9110s-module"),
            (before_power.HOST_REQUIREMENT, l9110s, None, "l9110s-module"),
            (before_power.HOST_REQUIREMENT, inlet, None, "jst-ph-2-power-inlet"),
            (before_power.HOST_REQUIREMENT, inlet, None, "jst-ph-2-power-inlet"),
            (before_power.HOST_REQUIREMENT, inlet, None, "jst-ph-2-power-inlet"),
            (before_power.HOST_REQUIREMENT, inlet, None, "jst-ph-2-power-inlet"),
            (before_power.FIRMWARE_PULL, "BtnOpen", "A", "tactile-button"),
            (before_power.HOST_REQUIREMENT, button, None, "tactile-button"),
            (before_power.HOST_REQUIREMENT, button, None, "tactile-button"),
            (before_power.FIRMWARE_PULL, "BtnMode", "A", "tactile-button"),
        ])

    def test_a_supply_names_its_users_sorted_and_says_nothing_of_its_own(self):
        supply = self.items[0]
        self.assertEqual(supply.users, ("JstPh2PowerInlet", "L9110sModule"))
        self.assertIsNone(supply.said)
        self.assertEqual({item.users for item in self.items[1:]}, {()})

    def test_each_kind_says_the_record_s_own_words(self):
        said = {item.kind: item.said for item in reversed(self.items)}  # the first item of each kind
        self.assertTrue(said[before_power.CONFLICT].startswith("AIA: the board's 10000 ohm pull-down"), said)
        self.assertEqual(said[before_power.UNUSED_PIN],
                         "channel B is unused in a one-motor design and must not float — tie it to the driver's own ground")
        self.assertTrue(said[before_power.HOST_REQUIREMENT].startswith("Pull both inputs down in HARDWARE."), said)
        self.assertIsNone(said[before_power.FIRMWARE_PULL])

    def test_the_records_are_the_ids_of_the_line_that_names_each_record_whole(self):
        self.assertEqual(self.data.before_power.records, ["jst-ph-2-power-inlet", "l9110s-module", "tactile-button"])

    def test_the_supply_s_step_has_its_edge_and_a_placing_step_has_none(self):
        self.assertEqual(self.data.steps[19].number, 20)
        self.assertEqual(self.data.steps[19].edge, ("MOTOR6V supply", "JstPh2PowerInlet VCC"))
        self.assertIsNone(self.data.steps[0].edge)


class NoBuildIsRefusedTest(unittest.TestCase):
    def test_a_project_with_no_build_is_refused_as_the_sheet_refuses_it(self):
        project = a_copy("motor")
        shutil.rmtree(project / "dist")
        with in_store(Path(tempfile.mkdtemp())), self.assertRaises(sheet.NotBuiltError) as said:
            sheet.wiring_data(project / "requirements.json")
        self.assertEqual(said.exception.code, breadboard_codes.NOT_BUILT)


if __name__ == "__main__":
    unittest.main()
